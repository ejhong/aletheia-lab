import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { z } from "zod";
import { loadCase, displayAssessment } from "../../src/domain/load.ts";
import { fingerprint } from "./review-state.mjs";
import { resolveResearchCase } from "./research-proposals.ts";
import { prepareCaseResearch, researchPreparedCase, caseResearchInput } from "./case-research.ts";
import { geminiResearch, GEMINI_RESEARCH_AGENT } from "./gemini-research.mjs";
import { editResearchReport, recordedModelStep } from "./report-editing.ts";
import { draftEdition } from "./edition-drafting.ts";
import { AI_POLICY } from "./ai-policy.mjs";
import { VENDORS, callVendor } from "./vendors.mjs";
import { sharedBudget } from "./ai-budget.mjs";

export const EXPERIMENT_PROTOCOL = "case-improvement-experiment-v1";
const RECONSIDER = "Pre-registered two-round experiment: measure the value of continuing research with the complete case and prior-work memory. Retaining the incumbent is a valid outcome.";
const id = z.string().regex(/^[a-zA-Z0-9][a-zA-Z0-9._-]+$/);
const Manifest = z.strictObject({ version: z.literal(1), protocol: z.literal(EXPERIMENT_PROTOCOL),
  id, case: z.string(), createdAt: z.iso.datetime(), baseCommit: z.string(),
  codeHash: z.string(), initialCaseHash: z.string(), initialInputHash: z.string(),
  rounds: z.literal(2), researcher: z.literal(GEMINI_RESEARCH_AGENT), editor: z.string(), sourceChecker: z.string(),
  sourceAllowancePerRound: z.literal(12), researchReservationUsd: z.literal(25),
  targetTotalUsd: z.literal(60), guaranteedResearchCostCap: z.literal(false),
  independentSeats: z.array(z.object({ vendor: z.string(), model: z.string() })),
  manualInterventionPolicy: z.string(),
});

function filesAt(directory: string): Record<string, string> {
  if (!fs.existsSync(directory)) return {};
  const files: Record<string, string> = {};
  function visit(dir: string, prefix: string) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      const relative = `${prefix}${entry.name}`, file = path.join(dir, entry.name);
      if (entry.isSymbolicLink()) throw new Error(`A frozen input cannot be a symlink: ${relative}`);
      if (entry.isDirectory()) visit(file, `${relative}/`);
      else files[relative] = fingerprint(fs.readFileSync(file).toString("base64"));
    }
  }
  visit(directory, ""); return files;
}

export function experimentCodeHash(root: string) {
  return fingerprint({ scripts: filesAt(path.join(root, "scripts")), domain: filesAt(path.join(root, "src/domain")),
    config: filesAt(path.join(root, "config")), constitution: fs.readFileSync(path.join(root, "AGENTS.md"), "utf8"),
    protocol: fs.readFileSync(path.join(root, "docs/AUTONOMY_EXPERIMENT.md"), "utf8") });
}
const caseHash = (root: string, key: string) => fingerprint(filesAt(resolveResearchCase(root, key)));
const directoryFor = (root: string, name: string) => path.join(root, ".research-runs", id.parse(name));
const read = (file: string) => JSON.parse(fs.readFileSync(file, "utf8"));
const save = (file: string, value: unknown) => fs.writeFileSync(file, JSON.stringify(value, null, 2), { flag: "wx" });

/** Freeze the real weak/mature incumbent and full commissioning input, with no
 * model, budget, intake or canonical content mutation. */
export function prepareCaseExperiment(root: string, key: string, name: string,
  now = new Date().toISOString()) {
  const directory = directoryFor(root, name);
  if (fs.existsSync(directory)) throw new Error("Experiment id already exists; preserve it and choose a new id");
  const prepared = prepareCaseResearch(root, key, { reconsider: RECONSIDER }, { now: () => now });
  const manifest = Manifest.parse({ version: 1, protocol: EXPERIMENT_PROTOCOL, id: name, case: prepared.request.case,
    createdAt: now, baseCommit: execFileSync("git", ["rev-parse", "HEAD"], { cwd: root, encoding: "utf8" }).trim(),
    codeHash: experimentCodeHash(root), initialCaseHash: caseHash(root, key), initialInputHash: prepared.request.inputHash,
    rounds: 2, researcher: GEMINI_RESEARCH_AGENT, editor: AI_POLICY.main.model, sourceChecker: AI_POLICY.sourceCheck,
    sourceAllowancePerRound: 12, researchReservationUsd: 25, targetTotalUsd: 60, guaranteedResearchCostCap: false,
    independentSeats: Object.entries(VENDORS).map(([vendor, seat]) => ({ vendor, model: seat.model })),
    manualInterventionPolicy: "No content rescue or prompt change. An intervention ends this protocol attempt; preserve it before revising the experiment." });
  fs.mkdirSync(directory, { recursive: true });
  fs.cpSync(resolveResearchCase(root, key), path.join(directory, "baseline-case"), { recursive: true, errorOnExist: true, force: false });
  save(path.join(directory, "manifest.json"), manifest);
  save(path.join(directory, "initial-prepared.json"), prepared);
  fs.writeFileSync(path.join(directory, "protocol.md"), fs.readFileSync(path.join(root, "docs/AUTONOMY_EXPERIMENT.md")), { flag: "wx" });
  return { directory, manifest, input: path.join(directory, "initial-prepared.json"), summary: prepared.summary };
}

/** One invocation executes one full round. A second invocation uses exactly
 * the same code and prompts, with the first round's state and memory. This
 * command never changes the live allowance, enables schedules, or publishes. */
export async function runCaseExperimentRound(root: string, name: string, round: number,
  authorization: string, progress: (message: string) => void = console.error) {
  if (![1, 2].includes(round)) throw new Error("This experiment has exactly two rounds");
  if (authorization.trim().length < 20) throw new Error("Record the founder's specific authorization for this uncapped managed-agent experiment");
  const directory = directoryFor(root, name);
  const manifest = Manifest.parse(read(path.join(directory, "manifest.json")));
  if (experimentCodeHash(root) !== manifest.codeHash)
    throw new Error("Code or prompts changed after freezing the experiment; preserve this attempt and prepare a new protocol revision");
  const dir = path.join(directory, `round-${round}`);
  const resultFile = path.join(dir, "result.json");
  if (fs.existsSync(resultFile)) return read(resultFile);
  const prior = round === 2 ? read(path.join(directory, "round-1/result.json")) : null;
  if (prior && prior.status !== "completed") throw new Error("Round one did not complete; do not buy round two to hide the failure");
  const expected = prior?.afterCaseHash ?? manifest.initialCaseHash;
  if (caseHash(root, manifest.case) !== expected)
    throw new Error("Experimental case changed outside the last completed round; inspect the intervention before continuing");
  if (fs.existsSync(path.join(dir, "editing-started.json")))
    throw new Error("Editing was interrupted; preserve the attempt and inspect it, without silently repeating paid calls or rewriting content");
  const preparedFile = path.join(dir, "prepared.json");
  const prepared: ReturnType<typeof prepareCaseResearch> = fs.existsSync(preparedFile) ? read(preparedFile)
    : round === 1 ? read(path.join(directory, "initial-prepared.json"))
      : prepareCaseResearch(root, manifest.case, { reconsider: RECONSIDER });
  const researchDir = path.join(root, ".research-runs", prepared.request.runId);
  const ticketFile = path.join(researchDir, "gemini-ticket.json");
  const currentTicket = fs.existsSync(ticketFile) ? read(ticketFile) : null;
  // Polling an existing task does not buy it again. Its recorded reservation
  // already consumes the allowance, including when it is still unsettled.
  const researchNeeded = currentTicket ? 0 : manifest.researchReservationUsd;
  const required = (researchNeeded + 5) * 1e6;
  const allowance = await sharedBudget().status();
  if (!allowance.policy.enabled) throw new Error("The live allowance is paused; no experimental call was made");
  // Older holds already consume the live allowance; never erase or demand their
  // release merely to start this experiment. A NEW unresolved experimental call
  // does block the following round.
  if (round === 2) {
    const baseline = read(path.join(directory, "round-1/allowance-before.json"));
    const priorIds = new Set(baseline.entries.map((entry: { id: string }) => entry.id));
    if (allowance.entries.some((entry: { id: string; accounted?: number }) => !priorIds.has(entry.id) &&
        entry.id !== currentTicket?.id && entry.accounted === undefined))
      throw new Error("A call made after the experiment began is unsettled; inspect it before round two");
    const spent = allowance.entries.filter((entry: { id: string }) => !priorIds.has(entry.id))
      .reduce((total: number, entry: { accounted?: number; reserved: number }) => total + (entry.accounted ?? entry.reserved), 0);
    if (spent + required > manifest.targetTotalUsd * 1e6)
      throw new Error("The remaining experimental allowance cannot cover round two's estimate and editing; inspect the first result before further spending");
  }
  if (allowance.totals.day + required > allowance.policy.dailyUsd * 1e6 ||
      allowance.totals.month + required > allowance.policy.monthlyUsd * 1e6 ||
      allowance.totals.nonReview + researchNeeded * 1e6 >
        (allowance.policy.monthlyUsd - allowance.policy.reviewReserveUsd) * 1e6)
    throw new Error("Insufficient allowance for the research estimate and editorial follow-up; no experimental call was made");
  fs.mkdirSync(dir, { recursive: true });
  if (!fs.existsSync(preparedFile)) save(preparedFile, prepared);
  if (!fs.existsSync(path.join(dir, "authorization.json"))) save(path.join(dir, "authorization.json"), { authorization, at: new Date().toISOString() });
  if (!fs.existsSync(path.join(dir, "allowance-before.json"))) save(path.join(dir, "allowance-before.json"), allowance);
  const researchResult = await researchPreparedCase(root, prepared, { resume: true,
    respond: geminiResearch(researchDir, { authorization, estimatedReservationUsd: manifest.researchReservationUsd, progress }) });
  if (researchResult.outcome !== "completed") {
    const attemptFile = path.join(dir, `research-result-${fingerprint(researchResult).slice(0, 16)}.json`);
    if (!fs.existsSync(attemptFile)) save(attemptFile, researchResult);
    return { status: "stopped", phase: "research", ...researchResult };
  }
  if (!fs.existsSync(path.join(dir, "research-result.json"))) save(path.join(dir, "research-result.json"), researchResult);
  const handoff = read(researchResult.handoff!);
  save(path.join(dir, "editing-started.json"), { at: new Date().toISOString() });
  let phase = "editing";
  try {
  progress(`Research complete. Beginning the unchanged editor for round ${round}.`);
  const editor = await editResearchReport(root, manifest.case, handoff,
    { directory: path.join(dir, "editing"), runId: `${name}-round-${round}-editing`, generatedAt: new Date().toISOString(), maxSources: 12 }, { progress });
  save(path.join(dir, "before-edition.json"), caseResearchInput(root, manifest.case));
  let author = 0, authorInterrupted = false;
  const comparisonDir = path.join(dir, "edition");
  fs.mkdirSync(comparisonDir);
  phase = "edition";
  const edition = await draftEdition(root, manifest.case, { prepare: true, reconsider: RECONSIDER,
    researchContext: { handoff, editing: editor } }, {
    progress,
    draft: async (system, user) => {
      if (authorInterrupted) throw new Error("An earlier author call was interrupted; no further paid author call");
      try {
        return await recordedModelStep(comparisonDir, `author-${++author}`, system, JSON.parse(user),
          { model: manifest.editor, context: { case: manifest.case, runId: name, phase: `round-${round}-edition` } });
      } catch (error) { authorInterrupted = true; throw error; }
    },
    judge: async (vendor, system, user) => {
      const config = Object.entries(VENDORS).find(([name]) => name === vendor)?.[1];
      if (!config) throw new Error("Unknown independent comparison vendor");
      const file = path.join(comparisonDir, `judge-${vendor}`);
      save(`${file}-request.json`, { system, user, model: config.model, effort: config.effort });
      const text = await callVendor(vendor, { system, user, maxTokens: 16000 });
      save(`${file}-response.json`, { model: config.model, text, usageLocation: "shared AI allowance receipts" });
      return text;
    },
  });
  const after = loadCase(resolveResearchCase(root, manifest.case));
  fs.cpSync(resolveResearchCase(root, manifest.case), path.join(dir, "result-case"), { recursive: true, errorOnExist: true, force: false });
  const result = { status: "completed", protocol: manifest.protocol, experiment: name, round, case: manifest.case,
    beforeCaseHash: expected, afterCaseHash: caseHash(root, manifest.case), codeHash: manifest.codeHash,
    initialInputHash: prepared.request.inputHash, research: researchResult, editor, edition,
    recordCounts: { claims: after.claims.length, evidence: after.evidence.length, sources: after.sources.length, research: after.research.length },
    article: after.editions.at(-1)?.article ?? null, assessment: displayAssessment(after)?.run ?? null,
    afterAllowance: await sharedBudget().status(),
    interpretation: "A completed experimental workflow, not a claim of improvement, saturation, publication approval or independent source truth." };
  save(resultFile, result);
  return result;
  } catch (error) {
    save(path.join(dir, "failure.json"), { status: "stopped", phase, at: new Date().toISOString(),
      reason: error instanceof Error ? error.message : "Experimental round interrupted",
      interpretation: "Preserve this attempt. Do not silently repeat paid calls or repair its content." });
    throw error;
  }
}
