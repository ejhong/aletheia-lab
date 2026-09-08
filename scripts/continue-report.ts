#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { execFileSync } from "node:child_process";
import { ResearchHandoffSchema, researchHandoffForModels } from "./lib/case-research.ts";
import { editResearchReport, recordedModelStep, replayCompletedModelStep } from "./lib/report-editing.ts";
import { openaiResponse } from "./lib/openai-response.mjs";
import { draftEdition } from "./lib/edition-drafting.ts";
import { AI_POLICY } from "./lib/ai-policy.mjs";
import { VENDORS, callVendor } from "./lib/vendors.mjs";
import { fingerprint } from "./lib/review-state.mjs";

// Development recovery is deliberately distinct from the frozen two-round
// experiment. It reuses a purchased report, never starts a research task,
// changes the allowance, repairs content, commits or publishes.
const [key, handoffFile, flag, replayFrom, ...extra] = process.argv.slice(2);
if (!key || !handoffFile || extra.length || (flag && (flag !== "--reuse-completed" || !replayFrom)))
  throw new Error("Usage: continue-report.ts <case> <handoff.json> [--reuse-completed <editing-directory>]");
const root = process.cwd(), at = new Date().toISOString();
const runId = `report-continuation-${at.slice(0, 10)}-${randomUUID()}`;
const directory = path.join(root, ".research-runs", runId);
const handoff = ResearchHandoffSchema.parse(JSON.parse(fs.readFileSync(handoffFile, "utf8")));
fs.mkdirSync(directory, { recursive: true });
const save = (name: string, value: unknown) => fs.writeFileSync(path.join(directory, name), JSON.stringify(value, null, 2), { flag: "wx" });
save("continuation.json", { runId, at, handoffFile, handoffHash: fingerprint(handoff), replayFrom,
  codeCommit: execFileSync("git", ["rev-parse", "HEAD"], { cwd: root, encoding: "utf8" }).trim(),
  interpretation: "Explicit development continuation after an interrupted attempt; not an uninterrupted experimental round." });
const editing = path.join(directory, "editing");
fs.mkdirSync(editing);
if (replayFrom) {
  const manifest = JSON.parse(fs.readFileSync(path.resolve(replayFrom, "../../manifest.json"), "utf8"));
  if (!/^[0-9a-f]{40}$/.test(manifest.baseCommit)) throw new Error("Invalid original experiment commit");
  const originalPolicy = execFileSync("git", ["show", `${manifest.baseCommit}:config/ai.json`], { cwd: root, encoding: "utf8" });
  if (fingerprint(JSON.parse(originalPolicy)) !== fingerprint(JSON.parse(fs.readFileSync(path.join(root, "config/ai.json"), "utf8"))))
    throw new Error("Model configuration changed since the original calls; do not reuse them as equivalent");
  // Retain the exact readings, including failures; no manual source substitution.
  for (const file of fs.readdirSync(replayFrom).filter(file => /^source-\d+\.json$/.test(file)))
    fs.copyFileSync(path.join(replayFrom, file), path.join(editing, file), fs.constants.COPYFILE_EXCL);
}
try {
  const editor = await editResearchReport(root, key, handoff,
    { directory: editing, runId, generatedAt: at, maxSources: 12 }, {
      progress: console.error,
      complete: async (system, input, options) => {
        if (replayFrom && ["commission", "reconcile"].includes(options.context.phase)) {
          console.error(`Reusing completed ${options.context.phase}; no replacement model call.`);
          return replayCompletedModelStep(replayFrom, options.context.phase, system, input, options);
        }
        return openaiResponse(system, input, options);
      },
    });
  const editionDirectory = path.join(directory, "edition");
  fs.mkdirSync(editionDirectory);
  let author = 0, interrupted = false;
  const edition = await draftEdition(root, key, { prepare: true,
    reconsider: "Continue the saved investigation after correcting duplicated provider envelopes; inspect an honest candidate without buying another report.",
    researchContext: { handoff: researchHandoffForModels(handoff), editing: editor } }, {
    progress: console.error,
    draft: async (system, user) => {
      if (interrupted) throw new Error("Earlier author call interrupted; no further paid author call");
      try {
        return await recordedModelStep(editionDirectory, `author-${++author}`, system, JSON.parse(user),
          { model: AI_POLICY.main.model, context: { case: key, runId, phase: "edition" } });
      } catch (error) { interrupted = true; throw error; }
    },
    judge: async (vendor, system, user) => {
      const config = Object.entries(VENDORS).find(([name]) => name === vendor)?.[1];
      if (!config) throw new Error("Unknown comparison vendor");
      save(`judge-${vendor}-request.json`, { system, user, model: config.model, effort: config.effort });
      const text = await callVendor(vendor, { system, user, maxTokens: 16000 });
      save(`judge-${vendor}-response.json`, { text, model: config.model });
      return text;
    },
  });
  save("result.json", { editor, edition });
  console.log(JSON.stringify({ directory, editor, edition }, null, 2));
} catch (error) {
  save("failure.json", { at: new Date().toISOString(), reason: error instanceof Error ? error.message : "Continuation interrupted" });
  throw error;
}
