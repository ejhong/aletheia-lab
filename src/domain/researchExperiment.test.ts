import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, expect, it, vi } from "vitest";
import { topicSeed } from "../../scripts/lib/topic-seed.mjs";
import { loadCase } from "./load.ts";
import { geminiResearch, geminiReport, geminiResearchCost, GEMINI_RESEARCH_AGENT } from "../../scripts/lib/gemini-research.mjs";
import { createBudget } from "../../scripts/lib/ai-budget.mjs";
import { AI_POLICY } from "../../scripts/lib/ai-policy.mjs";
import { recordedModelStep, editResearchReport } from "../../scripts/lib/report-editing.ts";
import { prepareCaseResearch, researchPreparedCase, caseResearchInput } from "../../scripts/lib/case-research.ts";
import { sha256 } from "../../scripts/lib/source-passages.mjs";

const temporary: string[] = [];
afterEach(() => temporary.splice(0).forEach(dir => fs.rmSync(dir, { recursive: true, force: true })));
const temp = () => { const dir = fs.mkdtempSync(path.join(os.tmpdir(), "aletheia-experiment-test-")); temporary.push(dir); return dir; };
const authorization = "Synthetic test authorization only; no live provider or spending store is used.";
const usage = { total_input_tokens: 100, total_tool_use_tokens: 20, total_output_tokens: 10,
  total_thought_tokens: 5, total_tokens: 135, grounding_tool_count: [{ type: "google_search", count: 1 }] };
const completed = { id: "synthetic-interaction", agent: GEMINI_RESEARCH_AGENT, status: "completed", usage,
  steps: [{ type: "thought", content: [{ type: "text", text: "Synthetic planning, not the report." }] },
    { type: "model_output", content: [{ type: "text", text: "Synthetic report.",
      annotations: [{ type: "url_citation", url: "https://example.org/primary" }] }] }] };

function allowance(enabled = true) {
  let state: unknown = null;
  const budget = createBudget({ read: async () => ({ sha: "synthetic", value: state }),
    write: async (_month: string, _sha: string, value: unknown) => { state = value; return true; } },
  { policy: { ...AI_POLICY, enabled, dailyUsd: 100, monthlyUsd: 150 } });
  return { ...budget, reserve: vi.fn(budget.reserve), settle: vi.fn(budget.settle) };
}

it("preserves Gemini report annotations and reproduces the earlier observed tariff estimate", () => {
  const report = geminiReport(completed);
  expect(report.text).toBe("Synthetic report.");
  expect(report.citations).toEqual([{ location: "steps/1/content/0/annotations/0", annotation: { type: "url_citation", url: "https://example.org/primary" } }]);
  expect(report.raw).toEqual(completed);
  expect(geminiResearchCost({ total_input_tokens: 2650692, total_tool_use_tokens: 266913,
    total_output_tokens: 31095, total_thought_tokens: 78478, total_tokens: 3027178,
    grounding_tool_count: [{ type: "google_search", count: 102 }] }).amount).toBe(15070734);
  expect(() => geminiResearchCost({ ...usage, total_tokens: 0 })).toThrow(/Unknown Gemini usage/);
  expect(() => geminiReport({ ...completed, status: "failed" })).toThrow(/No completed report/);
});

it("resumes one Gemini task after a polling interruption without buying another report", async () => {
  const budget = allowance();
  let interrupted = false;
  const fetchImpl = vi.fn(async (_url: string | URL | Request, init?: RequestInit) => {
    if (init?.method === "POST") return Response.json({ id: completed.id, agent: completed.agent, status: "in_progress" });
    if (!interrupted) { interrupted = true; throw new Error("Synthetic lost poll"); }
    return Response.json(completed);
  });
  const respond = geminiResearch(temp(), { authorization, budget, apiKey: "synthetic-key",
    fetchImpl, pause: async () => {} });
  await expect(respond("Synthetic instructions", "Synthetic full input")).rejects.toThrow(/lost poll/);
  const report = await respond("Synthetic instructions", "Synthetic full input");
  expect(report.text).toBe("Synthetic report.");
  expect(fetchImpl.mock.calls.filter(([, init]) => init?.method === "POST")).toHaveLength(1);
  expect(budget.reserve).toHaveBeenCalledTimes(1);
  expect(budget.settle).toHaveBeenCalledTimes(1);
  expect((await budget.status()).totals.held).toBe(0);
  await expect(respond("Different instructions", "Synthetic full input")).rejects.toThrow(/different research commission/);
});

it("never retries an ambiguous start, and respects the paused shared allowance", async () => {
  const fetchImpl = vi.fn(async () => { throw new Error("Synthetic lost start"); });
  const budget = allowance();
  const respond = geminiResearch(temp(), { authorization, budget, apiKey: "synthetic-key", fetchImpl });
  await expect(respond("Synthetic instructions", "Synthetic input")).rejects.toThrow(/lost start/);
  await expect(respond("Synthetic instructions", "Synthetic input")).rejects.toThrow(/unknown outcome/);
  expect(fetchImpl).toHaveBeenCalledTimes(1);
  expect((await budget.status()).totals.held).toBe(25000000);
  const paused = geminiResearch(temp(), { authorization, budget: allowance(false), apiKey: "synthetic-key", fetchImpl });
  await expect(paused("Synthetic instructions", "Synthetic input")).rejects.toThrow(/allowance/);
  expect(fetchImpl).toHaveBeenCalledTimes(1);
});

it("retains an overrun report and blocks following work instead of pretending the estimate was a cap", async () => {
  const directory = temp(), budget = allowance();
  const respond = geminiResearch(directory, { authorization, estimatedReservationUsd: 0.01, budget,
    apiKey: "synthetic-key", fetchImpl: vi.fn(async () => Response.json(completed)) });
  await expect(respond("Synthetic instructions", "Synthetic input")).rejects.toThrow(/exceeded its estimated reservation/);
  expect(JSON.parse(fs.readFileSync(path.join(directory, "gemini-completed.json"), "utf8"))).toEqual(completed);
  expect(budget.settle).not.toHaveBeenCalled();
  expect((await budget.status()).totals.held).toBe(10000);
});

const modelReply = (value: unknown) => ({ text: JSON.stringify(value), model: "Synthetic test editor",
  responseId: "synthetic-response", output: [], usage: {}, citations: [] });
const callOptions = { model: "synthetic-model", context: { case: "synthetic", runId: "synthetic-run", phase: "test" } };

it("replays only an identical recorded editor request and preserves interrupted attempts", async () => {
  const dir = temp(), complete = vi.fn(async () => modelReply({ result: "synthetic" }));
  const packet = { report: "Synthetic", citations: [{ url: "https://example.org/primary" }], foundingInput: "The entire synthetic founding page." };
  await recordedModelStep(dir, "editor", "Synthetic instructions", packet, callOptions, complete);
  await recordedModelStep(dir, "editor", "Synthetic instructions", packet, callOptions, complete);
  expect(complete).toHaveBeenCalledTimes(1);
  await expect(recordedModelStep(dir, "editor", "Changed instructions", packet, callOptions, complete)).rejects.toThrow(/input changed/);
  const fail = vi.fn(async () => { throw new Error("Synthetic connection failure"); });
  await expect(recordedModelStep(dir, "another-editor", "Instructions", packet, callOptions, fail)).rejects.toThrow(/connection failure/);
  await expect(recordedModelStep(dir, "another-editor", "Instructions", packet, callOptions, fail)).rejects.toThrow(/outcome is unknown/);
  expect(fail).toHaveBeenCalledTimes(1);
});

function fixture() {
  const root = temp(), dir = path.join(root, "content/cases/synthetic");
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(root, "AGENTS.md"), "Synthetic test constitution: no invented sources.");
  for (const [file, body] of Object.entries(topicSeed({ id: "TST-001", slug: "synthetic", title: "Synthetic topic",
    question: "Does the synthetic mark distinguish the explanations?", domain: "Tests only", date: "2026-09-07" })))
    fs.writeFileSync(path.join(dir, file), body);
  return { root, dir };
}
const sourceText = "The synthetic record describes a red mark in the test object. This invented document is a test fixture, not a real source. It establishes no historical connection.";
const quote = "The synthetic record describes a red mark";
const capture = { url: "https://example.org/primary", requestedUrl: "https://example.org/primary", retrievedAt: "2026-09-07T18:00:00.000Z",
  responseHash: sha256(sourceText), textHash: sha256(sourceText), text: sourceText, extractor: "plain-text-v1" };
const bundle = { title: "Synthetic observation", rationale: "A synthetic local observation useful to the fixture.", intent: "add" as const,
  priorDecisionIds: [], themeAdditions: { marks: "Synthetic marks" }, changes: [
    { kind: "source" as const, recordId: "SRC-TST-A", rationale: "Synthetic retrieved document.", anchor: null,
      after: { id: "SRC-TST-A", title: "Synthetic document", sourceType: "webpage", url: capture.url, verification: "unverified" } },
    { kind: "claim" as const, recordId: "TST-C001", rationale: "A synthetic local proposition.",
      after: { id: "TST-C001", tier: "catalog", statement: "The synthetic test mark is red.", theme: "marks", rung: "observation" },
      anchor: { sourceId: "SRC-TST-A", url: capture.url, quote, pdfPage: null } },
    { kind: "evidence" as const, recordId: "TST-E001", rationale: "The synthetic document describes the test mark.",
      after: { id: "TST-E001", title: "Synthetic description", sourceId: "SRC-TST-A", claimIds: ["TST-C001"],
        direction: "supports", strength: "weak", sourceStatement: "The synthetic document describes a red mark.",
        editorInference: "This local description is consistent with the synthetic proposition, without a broader implication.",
        limitations: ["Entirely invented material used only by the test suite."] },
      anchor: { sourceId: "SRC-TST-A", url: capture.url, quote, pdfPage: null } },
  ] };

async function handoff(root: string) {
  const prepared = prepareCaseResearch(root, "synthetic");
  const response = { ...modelReply({}), text: "Synthetic broad report for the entire fixture question." };
  const result = await researchPreparedCase(root, prepared, { respond: async () => response });
  return JSON.parse(fs.readFileSync(result.handoff!, "utf8"));
}

it("turns a complete report into source-checked records and preserves deferred coverage for the next round", async () => {
  const { root, dir } = fixture(), packet = await handoff(root);
  const seen: unknown[] = [];
  const complete = vi.fn(async (_system: string, input: string, options: { model: string; context: { phase: string } }) => {
    const data = JSON.parse(input); seen.push(data);
    if (options.context.phase === "commission") return modelReply({ rationale: "Investigate the complete synthetic question.",
      readings: [{ url: capture.url, question: "Inspect the synthetic observation.", importance: "Tests source grounding." }],
      coverage: [{ strand: "Broader synthetic connection", state: "open", reason: "No connection established by the local observation." }], deferred: [] });
    if (options.context.phase === "reconcile") return modelReply({ rationale: "Record the local fact and preserve the larger open question.",
      bundles: [bundle], deferred: [{ item: "Synthetic historical connection", reason: "No independently checked connection.", reconsiderWhen: "A dated chain can be inspected." }] });
    return modelReply({ findings: data.changes.map((change: { recordId: string }) => ({ recordId: change.recordId,
      supported: true, contextPreserved: true, inferenceSeparated: true, independenceHandled: true,
      quoteSupported: true, locatorSupported: true, reason: "Supported by the complete synthetic source text." })) });
  });
  const result = await editResearchReport(root, "synthetic", packet,
    { directory: path.join(root, "editing"), runId: "synthetic-editor", generatedAt: "2026-09-07T18:00:01.000Z" },
    { complete, retrieve: async () => capture });
  expect(result.outcomes).toEqual([expect.objectContaining({ outcome: "prepared" })]);
  const loaded = loadCase(dir);
  expect(loaded.claims).toHaveLength(1);
  expect(loaded.claims[0].origin.extractedBy).toBe("Synthetic test editor");
  expect(loaded.claims[0].reviewState).toBe("ai_extracted");
  expect(loaded.sources[0].verification).toBe("ai_verified");
  expect(loaded.evidence[0].exactLocator).toContain("characters 1–");
  expect(seen[0]).toMatchObject({ handoff: packet });
  expect(seen[1]).toMatchObject({ handoff: packet, captures: [expect.objectContaining({ text: sourceText })] });
  const next = caseResearchInput(root, "synthetic").packet;
  expect(next.memory.some(entry => entry.deferred?.some((item: { item: string }) => item.item === "Synthetic historical connection"))).toBe(true);
  expect(next.changesSincePreviousReport).toMatchObject({ available: true, ledger: { claims: { added: ["TST-C001"] } } });
  expect(next.previousReport?.text).toBe(packet.response.text);
});

it("a source check can reject an otherwise well-formed update without changing the case", async () => {
  const { root, dir } = fixture(), packet = await handoff(root), before = loadCase(dir).contentHash;
  const complete = vi.fn(async (_system: string, input: string, options: { context: { phase: string } }) => {
    if (options.context.phase === "commission") return modelReply({ rationale: "Synthetic source check.",
      readings: [{ url: capture.url, question: "Synthetic check.", importance: "Synthetic importance." }], coverage: [], deferred: [] });
    if (options.context.phase === "reconcile") return modelReply({ rationale: "Synthetic candidate.", bundles: [bundle], deferred: [] });
    return modelReply({ findings: JSON.parse(input).changes.map((change: { recordId: string }) => ({ recordId: change.recordId,
      supported: false, contextPreserved: true, inferenceSeparated: true, independenceHandled: true,
      quoteSupported: true, locatorSupported: true, reason: "Synthetic full assertion exceeds its source." })) });
  });
  const result = await editResearchReport(root, "synthetic", packet,
    { directory: path.join(root, "editing"), runId: "synthetic-rejection", generatedAt: "2026-09-07T18:00:01.000Z" },
    { complete, retrieve: async () => capture });
  expect(result.outcome).toBe("partial");
  expect(result.outcomes[0].reason).toContain("exceeds its source");
  expect(loadCase(dir).contentHash).toBe(before);
});
