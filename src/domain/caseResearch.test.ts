import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, expect, it, vi } from "vitest";
import { stringify } from "yaml";
import { topicSeed } from "../../scripts/lib/topic-seed.mjs";
import { caseResearchInput, prepareCaseResearch, researchCase } from "../../scripts/lib/case-research";
import { readIntakeDecisions, writeIntakeDecisions } from "../../scripts/lib/intake-store.mjs";
import { queueSources } from "../../scripts/lib/source-queue";
import { loadCase } from "./load";

const roots: string[] = [];
afterEach(() => roots.splice(0).forEach(root => fs.rmSync(root, { recursive: true, force: true })));
function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "aletheia-case-research-")); roots.push(root);
  const dir = path.join(root, "content/cases/synthetic"); fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(root, "AGENTS.md"), "Synthetic constitution: never fabricate evidence.");
  for (const [file, body] of Object.entries(topicSeed({ id: "TST-001", slug: "synthetic", title: "Synthetic topic",
    question: "Does the synthetic mark distinguish two explanations?", domain: "Tests only", date: "2026-09-06" })))
    fs.writeFileSync(path.join(dir, file), body);
  return { root, dir };
}
const reply = { model: "synthetic researcher", responseId: "synthetic-response", text: "Synthetic unverified report.",
  output: [], usage: {}, citations: [{ type: "url_citation", url: "https://example.org/source", title: "Synthetic source" }] };

function foundingInput(dir: string, text: string) {
  fs.mkdirSync(path.join(dir, "inputs"), { recursive: true });
  fs.writeFileSync(path.join(dir, "inputs/founding.html"), text);
  fs.writeFileSync(path.join(dir, "inputs/manifest.yaml"), stringify([{ id: "TST-IN001", title: "Synthetic complete founding page",
    role: "founding_research", file: "inputs/founding.html", origin: "Synthetic test fixture, not a real source.",
    license: "Synthetic text authored for this test." }]));
}

it("records the question and memory before browsing, saves a report without altering the case, and rests unchanged work", async () => {
  const { root, dir } = fixture();
  const before = loadCase(dir).contentHash;
  const respond = vi.fn(async (_instructions: string, input: string) => {
    expect(readIntakeDecisions(root).find(e => e.decision === "partial")?.details?.request).toBeDefined();
    const packet = JSON.parse(input);
    expect(packet.ledger.claims).toEqual([]);
    expect(packet.case.whatIsClaimed).toContain("synthetic mark");
    return reply;
  });
  expect((await researchCase(root, "synthetic", {}, { respond })).outcome).toBe("completed");
  expect(loadCase(dir).contentHash).toBe(before);
  expect((await researchCase(root, "synthetic", {}, { respond })).outcome).toBe("rested");
  expect(respond).toHaveBeenCalledTimes(1);
  const state = caseResearchInput(root, "synthetic");
  expect(state.packet.previousReport).toMatchObject({ text: reply.text, verification: "unverified working report", citations: reply.citations });
  expect(state.packet.memory).toHaveLength(2);
});

it("new inbox context can reopen research, and earlier reports remain in the packet as unverified memory", async () => {
  const { root } = fixture();
  await researchCase(root, "synthetic", {}, { respond: async () => reply });
  const before = caseResearchInput(root, "synthetic").basis;
  queueSources(root, { case: "synthetic", urls: ["https://example.org/new-reading"], ref: "Synthetic inbox",
    text: "Investigate this synthetic competing account.", runId: "fixture-inbox", generatedAt: "2026-09-07T12:00:00.000Z" });
  const state = caseResearchInput(root, "synthetic");
  expect(state.basis).not.toBe(before);
  expect(state.packet.memory.some(e => e.requestedReading === "Investigate this synthetic competing account.")).toBe(true);
  expect(state.packet.previousReport).toMatchObject({ text: reply.text, verification: "unverified working report" });
});

it("preserves failure without automatic repayment; explicit reconsideration must give a reason", async () => {
  const { root } = fixture();
  const respond = vi.fn(async () => { throw new Error("Synthetic transport interruption"); });
  expect((await researchCase(root, "synthetic", {}, { respond })).outcome).toBe("failed");
  expect((await researchCase(root, "synthetic", {}, { respond })).outcome).toBe("rested");
  expect(respond).toHaveBeenCalledTimes(1);
  await expect(researchCase(root, "synthetic", { reconsider: "again" }, { respond })).rejects.toThrow(/reason/);
  expect(readIntakeDecisions(root).some(e => e.reason === "Synthetic transport interruption")).toBe(true);
});

it("previews the same full brief used for research without a model call or new intake state, and carries citations to editing", async () => {
  const { root, dir } = fixture();
  const wholePage = '<h1>Synthetic motif study</h1>\n' + '<p>Full earlier context.</p>\n'.repeat(1500)
    + '<h2>Flood traditions</h2><figure><img src="flood.jpg" alt="Synthetic comparison"><figcaption>Caption at the end.</figcaption></figure>';
  foundingInput(dir, wholePage);
  const respond = vi.fn(async () => reply);
  const before = loadCase(dir).contentHash;
  const preview = await researchCase(root, "synthetic", { prepare: true }, { respond });
  expect(preview.outcome).toBe("prepared");
  expect(respond).not.toHaveBeenCalled();
  expect(readIntakeDecisions(root)).toHaveLength(0);
  const request = JSON.parse(fs.readFileSync(preview.request!, "utf8"));
  expect(JSON.parse(request.input).foundingInputs[0].text).toBe(wholePage);
  expect(JSON.parse(request.input).changesSincePreviousReport.available).toBe(false);
  const result = await researchCase(root, "synthetic", {}, { respond });
  expect(result.outcome).toBe("completed");
  const handoff = JSON.parse(fs.readFileSync(result.handoff!, "utf8"));
  expect(handoff.request.inputHash).toBe(request.inputHash);
  expect(handoff.request.instructions).toBe(request.instructions);
  expect(handoff.request.input).toBe(request.input);
  expect(handoff.response).toEqual(reply);
  expect(handoff.verification).toBe("unverified working report");
  expect(loadCase(dir).contentHash).toBe(before);
  const restedPreview = await researchCase(root, "synthetic", { prepare: true }, { respond });
  expect(restedPreview.restReason).toMatch(/unchanged/);
  expect(respond).toHaveBeenCalledTimes(1);
  expect(readIntakeDecisions(root)).toHaveLength(2);
});

it("shows added, changed and removed records relative to the previous investigation without mistaking reordered rows for changes", async () => {
  const { root, dir } = fixture();
  const source = (id: string) => ({ id, title: `Synthetic ${id}`, sourceType: "webpage", verification: "unverified", background: true });
  fs.writeFileSync(path.join(dir, "sources.yaml"), stringify([source("SRC-TST-A"), source("SRC-TST-B"), source("SRC-TST-C")]));
  foundingInput(dir, "A synthetic initial question.");
  await researchCase(root, "synthetic", {}, { respond: async () => reply });
  fs.writeFileSync(path.join(dir, "sources.yaml"), stringify([
    source("SRC-TST-C"), { ...source("SRC-TST-A"), title: "Corrected synthetic title" }, source("SRC-TST-D"),
  ]));
  foundingInput(dir, "The synthetic question with an additional neglected strand.");
  const state = prepareCaseResearch(root, "synthetic");
  const diff = JSON.parse(state.request.input).changesSincePreviousReport;
  expect(diff.available).toBe(true);
  expect(diff.ledger.sources).toEqual({ added: ["SRC-TST-D"], updated: ["SRC-TST-A"], removed: ["SRC-TST-B"] });
  expect(diff.sections).toEqual(["foundingInputs"]);
  expect(state.restReason).toBeNull();
  const input = JSON.parse(state.request.input);
  expect(input.ledger.sources).toHaveLength(3);
  expect(input.previousReport.citations).toEqual(reply.citations);
});

it("treats an unreadable prior input as unknown history while retaining the report", async () => {
  const { root } = fixture();
  const stamp = { case: "synthetic", stage: "research-run", date: "2026-09-07", runId: "legacy-provider-run",
    model: "synthetic legacy researcher", promptVersion: "synthetic-v0", caseBasis: caseResearchInput(root, "synthetic").basis };
  writeIntakeDecisions(root, [{ ...stamp, decision: "partial", generatedAt: "2026-09-07T00:00:00.000Z", reason: "Synthetic legacy request.",
    details: { kind: "case-research-report", request: { input: "Legacy non-JSON input" } } },
    { ...stamp, decision: "completed", generatedAt: "2026-09-07T00:00:01.000Z", reason: "Synthetic legacy report.",
      details: { kind: "case-research-report", report: reply.text, citations: reply.citations } }]);
  const packet = JSON.parse(prepareCaseResearch(root, "synthetic").request.input);
  expect(packet.changesSincePreviousReport.available).toBe(false);
  expect(packet.previousReport.text).toBe(reply.text);
});

it("rejects oversized complete packets before any call, receipt or local request is written", async () => {
  const { root, dir } = fixture();
  foundingInput(dir, "Synthetic founding input. ".repeat(40000));
  const respond = vi.fn(async () => reply);
  await expect(researchCase(root, "synthetic", {}, { respond })).rejects.toThrow(/no truncated memory/);
  expect(respond).not.toHaveBeenCalled();
  expect(readIntakeDecisions(root)).toHaveLength(0);
  expect(fs.existsSync(path.join(root, ".research-runs"))).toBe(false);
});
