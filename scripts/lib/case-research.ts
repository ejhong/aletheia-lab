import fs from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { z } from "zod";
import { loadCase, displayAssessment } from "../../src/domain/load.ts";
import { readCaseSnapshot, evidencePacket, resolveCaseDirectory } from "./case-snapshot.mjs";
import { readIntakeDecisions, writeIntakeDecisions } from "./intake-store.mjs";
import { fingerprint } from "./review-state.mjs";
import { openaiResearch } from "./openai-response.mjs";
import type { ResearchProposal } from "../../src/domain/researchProposal.ts";

export const CASE_RESEARCH_PROTOCOL = "case-research-report-v3";
const KIND = "case-research-report";
const INSTRUCTIONS = fs.readFileSync(new URL("../prompts/case-research.md", import.meta.url), "utf8");
const MAX_PACKET_BYTES = 800000;
const LEDGER_SECTIONS = ["sources", "claims", "evidence", "research", "studies"] as const;
const RecordList = z.array(z.object({ id: z.string() }).passthrough());
const PreviousPacket = z.object({
  ledger: z.object({ sources: RecordList, claims: RecordList, evidence: RecordList,
    research: RecordList, studies: RecordList }).passthrough(),
}).passthrough();

/** Compare recorded inputs, not a model's claim of novelty. Missing historical
 * packets are unknown coverage, never an empty ledger or a no-change finding. */
function changesSinceReport(previousInput: unknown, packet: z.infer<typeof PreviousPacket>) {
  if (typeof previousInput !== "string")
    return { available: false, reason: "No comparable input packet for the previous completed report." };
  let parsed: unknown;
  try { parsed = JSON.parse(previousInput); } catch {
    return { available: false, reason: "The previous report input is not a readable JSON packet." };
  }
  const previous = PreviousPacket.safeParse(parsed);
  if (!previous.success)
    return { available: false, reason: "The previous report used a different packet format; consult its report and history." };
  const ledger = Object.fromEntries(LEDGER_SECTIONS.map(kind => {
    const before = new Map(previous.data.ledger[kind].map(record => [record.id, record]));
    const after = new Map(packet.ledger[kind].map(record => [record.id, record]));
    return [kind, {
      added: [...after.keys()].filter(id => !before.has(id)).sort(),
      updated: [...after.keys()].filter(id => before.has(id) && fingerprint(before.get(id)) !== fingerprint(after.get(id))).sort(),
      removed: [...before.keys()].filter(id => !after.has(id)).sort(),
    }];
  }));
  const sections = ["case", "foundingInputs", "currentArticle", "currentAssessment", "retiredClaims", "conjectures", "plates"]
    .filter(key => fingerprint(previous.data[key] ?? null) !== fingerprint(packet[key] ?? null));
  return { available: true, ledger, sections,
    meaning: "Recorded changes since the previous completed report's inputs. A navigation aid, not a measure of importance or a search boundary." };
}

export function caseResearchInput(root: string, key: string) {
  const dir = path.join(root, "content/cases", resolveCaseDirectory(root, key));
  const loaded = loadCase(dir);
  const snapshot = readCaseSnapshot(dir);
  const history = readIntakeDecisions(root).filter(e => e.case === loaded.record.slug || e.case === path.basename(dir));
  const reports = history.filter(e => e.details?.kind === KIND);
  const constitution = fs.readFileSync(path.join(root, "AGENTS.md"), "utf8");
  const foundingInputs = loaded.narrativeInputs.map(i => ({ ...i, text: fs.readFileSync(
    i.file.startsWith("inputs/") ? path.join(dir, i.file) : path.resolve(root, i.file), "utf8") }));
  // A report cannot make its own unchanged case due for another paid report.
  const basis = fingerprint({ content: snapshot.contentHash, constitution, foundingInputs,
    memory: history.filter(e => e.details?.kind !== KIND).map(e => e.id), protocol: INSTRUCTIONS });
  const previous = reports.filter(e => e.decision === "completed").at(-1);
  const previousRequest = previous && reports.find(e => e.runId === previous.runId && e.details?.request)?.details?.request;
  const packet = { constitution, case: loaded.record, ledger: evidencePacket(snapshot.files),
    retiredClaims: loaded.claims.filter(c => c.reviewState === "rejected")
      .map(c => ({ id: c.id, statement: c.statement, reason: c.rejectionReason })),
    conjectures: loaded.conjectures,
    currentArticle: snapshot.edition?.article ?? snapshot.files["overview.md"],
    currentAssessment: displayAssessment(loaded)?.run ?? null,
    plates: loaded.images, foundingInputs, caseHistory: loaded.history,
    memory: history.map(e => ({ id: e.id, date: e.date, stage: e.stage, outcome: e.decision, reason: e.reason,
      source: e.source, question: e.discovery?.plan?.question,
      requestedReading: e.stage === "source-request" ? e.details?.context : undefined,
      researchOutcomes: e.details?.outcomes,
      coverage: e.details?.coverage, deferred: e.details?.deferred,
      changes: e.research?.changes.map((c: ResearchProposal["changes"][number]) => ({ kind: c.kind, recordId: c.recordId, rationale: c.rationale })),
    })),
    previousReport: previous ? { runId: previous.runId, caseBasis: previous.caseBasis, date: previous.date,
      verification: "unverified working report", text: previous.details?.report, citations: previous.details?.citations } : null,
  };
  return { case: loaded.record.slug, basis, packet: { ...packet,
    changesSincePreviousReport: { runId: previous?.runId ?? null,
      ...changesSinceReport(previousRequest?.input, packet) } }, prior: reports.at(-1) };
}

/** The same complete brief prepares a sparse or mature case. No I/O mutations,
 * API calls, intake entries or spending reservations happen here. */
export function prepareCaseResearch(root: string, key: string, options: { reconsider?: string } = {},
  dependencies: { now?: () => string } = {}) {
  if (options.reconsider !== undefined && options.reconsider.trim().length < 10)
    throw new Error("Give a specific reconsideration reason (10+ characters)");
  const state = caseResearchInput(root, key);
  const restReason = !options.reconsider && state.prior?.caseBasis === state.basis
    ? "Inspect the previous report or failure before commissioning another unchanged investigation." : null;
  const generatedAt = (dependencies.now ?? (() => new Date().toISOString()))();
  const runId = `case-research-${generatedAt.slice(0, 10)}-${randomUUID()}`;
  const input = JSON.stringify({ ...state.packet, reconsider: options.reconsider ?? null });
  const bytes = Buffer.byteLength(input + INSTRUCTIONS);
  if (bytes > MAX_PACKET_BYTES)
    throw new Error("Research packet exceeds this manual trial's bound; no truncated memory was sent");
  const inputHash = fingerprint({ instructions: INSTRUCTIONS, input });
  const request = { runId, case: state.case, caseBasis: state.basis, generatedAt, inputHash,
    promptVersion: CASE_RESEARCH_PROTOCOL, instructions: INSTRUCTIONS, input };
  const summary = { case: state.case, caseBasis: state.basis, inputHash, bytes, limitBytes: MAX_PACKET_BYTES,
    ledger: Object.fromEntries(LEDGER_SECTIONS.map(kind => [kind, state.packet.ledger[kind].length])),
    foundingInputs: state.packet.foundingInputs.map(item => ({ id: item.id, title: item.title,
      file: item.file, bytes: Buffer.byteLength(item.text), hash: fingerprint(item.text) })),
    previousReport: state.packet.previousReport?.runId ?? null,
    changesSincePreviousReport: state.packet.changesSincePreviousReport,
    restReason, scope: "Complete founding texts and current ledger; no content truncation or claim-count quota." };
  return { request, summary, restReason };
}

/** Manual experiment, using the existing intake record. It never queues every
 * citation, adopts observations, edits an edition or schedules another run. */
export type CaseResearchResult = { outcome: "rested" | "prepared" | "completed" | "failed";
  runId?: string; model?: string; report?: string; handoff?: string; intake?: string | null;
  reason?: string; request?: string; summary?: string; inputHash?: string; restReason?: string | null };
export async function researchCase(root: string, key: string, options: { reconsider?: string; prepare?: boolean } = {},
  dependencies: { respond?: typeof openaiResearch; now?: () => string } = {}): Promise<CaseResearchResult> {
  const prepared = prepareCaseResearch(root, key, options, dependencies);
  if (prepared.restReason && !options.prepare) return { outcome: "rested", reason: prepared.restReason };
  const { request, summary } = prepared;
  const { runId, inputHash } = request;
  const dir = path.join(root, ".research-runs", runId);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, "request.json"), JSON.stringify(request, null, 2), { flag: "wx" });
  fs.writeFileSync(path.join(dir, "summary.json"), JSON.stringify(summary, null, 2), { flag: "wx" });
  if (options.prepare) return { outcome: "prepared", request: path.join(dir, "request.json"),
    summary: path.join(dir, "summary.json"), inputHash, restReason: prepared.restReason };
  return researchPreparedCase(root, prepared, dependencies);
}

/** Execute the exact saved commission. A resumable provider may explicitly
 * resume its one recorded task; other transports cannot retry unknown starts. */
export async function researchPreparedCase(root: string, prepared: ReturnType<typeof prepareCaseResearch>,
  dependencies: { respond?: typeof openaiResearch; now?: () => string; resume?: boolean } = {}): Promise<CaseResearchResult> {
  const { request, summary } = prepared;
  const { runId, generatedAt, inputHash, input, instructions } = request;
  if (!/^[a-zA-Z0-9][a-zA-Z0-9._-]+$/.test(runId) ||
      inputHash !== fingerprint({ instructions, input }) ||
      caseResearchInput(root, request.case).basis !== request.caseBasis)
    throw new Error("Prepared investigation changed or is stale; no call sent");
  const dir = path.join(root, ".research-runs", runId);
  fs.mkdirSync(dir, { recursive: true });
  const save = (name: string, value: unknown) => {
    const file = path.join(dir, name);
    if (fs.existsSync(file)) {
      if (fingerprint(JSON.parse(fs.readFileSync(file, "utf8"))) !== fingerprint(value))
        throw new Error(`Conflicting research receipt: ${name}`);
    } else fs.writeFileSync(file, JSON.stringify(value, null, 2), { flag: "wx" });
  };
  save("request.json", request); save("summary.json", summary);
  const prior = readIntakeDecisions(root).filter(entry => entry.runId === runId && entry.details?.kind === KIND);
  const responseFile = path.join(dir, "response.json");
  if (prior.length && !fs.existsSync(responseFile) && !dependencies.resume)
    throw new Error("An investigation was already attempted; only its resumable provider task may continue");
  // Persist before sending. A process interruption cannot silently make the same
  // request eligible again; inspection and reasoned reconsideration are explicit.
  const stamp = { case: request.case, stage: "research-run", date: generatedAt.slice(0, 10), generatedAt,
    runId, promptVersion: CASE_RESEARCH_PROTOCOL, inputHash, caseBasis: request.caseBasis };
  writeIntakeDecisions(root, [{ ...stamp, decision: "partial", model: "Research coordinator (no completed model call)",
    reason: "Investigation request recorded; no completed report yet. Inspect local/provider receipts before retrying.",
    details: { kind: KIND, request } }]);
  try {
    const response = fs.existsSync(responseFile) ? JSON.parse(fs.readFileSync(responseFile, "utf8"))
      : await (dependencies.respond ?? openaiResearch)(instructions, input,
        { context: { case: request.case, runId, phase: KIND } });
    save("response.json", response);
    if (!response.text.trim()) throw new Error("Research returned no report; inspect the saved response");
    // Carry the exact commissioning context and all provider annotations into
    // editing together. A bare prose extract lost citations in the first trial.
    const handoff = path.join(dir, "handoff.json");
    save("handoff.json", { verification: "unverified working report", request, response });
    const report = path.join(dir, "report.md");
    if (!fs.existsSync(report)) fs.writeFileSync(report, `<!-- Unverified AI research report; ${runId}; ${response.model}. -->\n\n${response.text}\n`, { flag: "wx" });
    if (prior.some(entry => entry.decision === "completed"))
      return { outcome: "completed", runId, model: response.model, report, handoff };
    const result = writeIntakeDecisions(root, [{ ...stamp, generatedAt: (dependencies.now ?? (() => new Date().toISOString()))(),
      decision: "completed", model: response.model,
      reason: "Web research report retained as working material. Its proposed findings require separate source verification and publication review.",
      candidateHash: fingerprint(response), details: { kind: KIND, report: response.text, citations: response.citations, response } }]);
    return { outcome: "completed", runId, model: response.model, report: path.join(dir, "report.md"), handoff, intake: result.file };
  } catch (error) {
    const reason = error instanceof Error ? error.message : "Research request failed";
    save(`failure-${Date.now()}.json`, { reason });
    writeIntakeDecisions(root, [{ ...stamp, generatedAt: (dependencies.now ?? (() => new Date().toISOString()))(),
      decision: "failed", model: "Research coordinator (no accepted report)", reason, details: { kind: KIND } }]);
    return { outcome: "failed", runId, reason };
  }
}
