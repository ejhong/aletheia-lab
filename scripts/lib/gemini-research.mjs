import fs from "node:fs";
import path from "node:path";
import { fingerprint } from "./review-state.mjs";
import { sharedBudget } from "./ai-budget.mjs";
import { BudgetStopped } from "./ai-policy.mjs";

export const GEMINI_RESEARCH_AGENT = "deep-research-max-preview-04-2026";
const API = "https://generativelanguage.googleapis.com/v1beta/interactions";
const PRICING = "https://ai.google.dev/gemini-api/docs/pricing";

/** Preserve provider annotations in their original shape and location. The
 * complete response remains attached; prose alone is never the editor handoff. */
export function geminiReport(body) {
  if (body.status !== "completed" || body.agent !== GEMINI_RESEARCH_AGENT || !body.id)
    throw new Error("No completed report from the commissioned Gemini agent");
  const text = (body.steps ?? []).filter(step => step.type === "model_output")
    .flatMap(step => step.content ?? []).filter(item => item.type === "text")
    .map(item => item.text).join("\n\n");
  if (!text.trim()) throw new Error("Completed Gemini task has no report text");
  const citations = [];
  function walk(value, location) {
    if (!value || typeof value !== "object") return;
    for (const [key, child] of Object.entries(value)) {
      const here = `${location}/${key}`;
      if (["annotations", "citations"].includes(key) && Array.isArray(child))
        child.forEach((annotation, i) => citations.push({ location: `${here}/${i}`, annotation }));
      else if (Array.isArray(child)) child.forEach((item, i) => walk(item, `${here}/${i}`));
      else walk(child, here);
    }
  }
  walk(body.steps, "steps");
  return { text, model: body.agent, responseId: body.id, output: body.steps,
    usage: body.usage, citations, raw: body };
}

/** The same conservative tariff estimate used for the original trial. It is
 * not a vendor invoice or an advance dollar cap on a managed research agent. */
export function geminiResearchCost(usage) {
  const fields = ["total_input_tokens", "total_tool_use_tokens", "total_output_tokens", "total_thought_tokens"];
  if (!usage || fields.some(key => !Number.isSafeInteger(usage[key]) || usage[key] < 0) ||
      fields.reduce((total, key) => total + usage[key], 0) !== usage.total_tokens ||
      !Array.isArray(usage.grounding_tool_count) || usage.grounding_tool_count.some(tool =>
        tool.type !== "google_search" || !Number.isSafeInteger(tool.count) || tool.count < 0))
    throw new BudgetStopped("Unknown Gemini usage; retain the reservation and inspect the full receipt.");
  const queries = usage.grounding_tool_count.reduce((total, tool) => total + tool.count, 0);
  const amount = (usage.total_input_tokens + usage.total_tool_use_tokens) * 4 +
    (usage.total_output_tokens + usage.total_thought_tokens) * 18 + queries * 14000;
  return { amount, receipt: { responseAccounting: "Conservative tariff estimate, not invoice",
    input: usage.total_input_tokens, toolInput: usage.total_tool_use_tokens,
    output: usage.total_output_tokens, thought: usage.total_thought_tokens, queries,
    inputRate: 4, outputRate: 18, searchUsdPerQuery: 0.014, rateDate: "2026-09-07", source: PRICING,
    assumptions: "Declared Gemini 3.1 Pro foundation; long-context rates for every step; no cache or free-search credit; per-step model details unavailable" } };
}

/** A repeatable manual-experiment transport. Its authorization must come from
 * the operator; this module never resumes an allowance or changes a limit.
 * Exactly one POST may start a task. Subsequent invocations poll that same ID.
 * An ambiguous start needs inspection, never an automatic second purchase.
 * @param {string} directory
 * @param {{authorization: string, estimatedReservationUsd?: number,
 * apiKey?: string, budget?: ReturnType<typeof sharedBudget>, fetchImpl?: typeof fetch,
 * pause?: (ms: number) => Promise<void>, progress?: (message: string) => void}} options */
export function geminiResearch(directory, { authorization, estimatedReservationUsd = 25,
  apiKey = process.env.GEMINI_API_KEY, budget = sharedBudget(), fetchImpl = fetch,
  pause = ms => new Promise(resolve => setTimeout(resolve, ms)), progress = () => {} } = {}) {
  if (typeof authorization !== "string" || authorization.trim().length < 20 ||
      !Number.isFinite(estimatedReservationUsd) || estimatedReservationUsd <= 0)
    throw new BudgetStopped("A managed-agent experiment needs a recorded authorization acknowledging estimated, uncapped cost.");
  const save = (name, data) => fs.writeFileSync(path.join(directory, name), JSON.stringify(data, null, 2), { flag: "wx" });
  const read = name => JSON.parse(fs.readFileSync(path.join(directory, name), "utf8"));
  async function request(suffix, body) {
    if (!apiKey) throw new Error("GEMINI_API_KEY is not configured");
    const response = await fetchImpl(API + suffix, {
      method: body ? "POST" : "GET", headers: { "content-type": "application/json", "x-goog-api-key": apiKey },
      ...(body ? { body: JSON.stringify(body) } : {}), signal: AbortSignal.timeout(60000),
    });
    const data = await response.json();
    return { at: new Date().toISOString(), httpStatus: response.status, body: data };
  }
  return async (instructions, input, { context } = {}) => {
    if (!apiKey) throw new Error("GEMINI_API_KEY is not configured");
    fs.mkdirSync(directory, { recursive: true });
    const body = { agent: GEMINI_RESEARCH_AGENT, input: `${instructions}\n\nResearch data:\n${input}`,
      background: true, tools: [{ type: "google_search" }, { type: "url_context" }],
      agent_config: { type: "deep-research", thinking_summaries: "auto", visualization: "off", collaborative_planning: false } };
    const inputHash = fingerprint(body);
    const savedRequest = path.join(directory, "gemini-request.json");
    if (fs.existsSync(savedRequest)) {
      if (read("gemini-request.json").inputHash !== inputHash) throw new Error("Cannot resume a different research commission");
    } else save("gemini-request.json", { inputHash, body, authorization, estimatedReservationUsd, guaranteedCostCap: false });
    let start;
    if (fs.existsSync(path.join(directory, "gemini-start.json"))) start = read("gemini-start.json");
    else {
      if (fs.existsSync(path.join(directory, "gemini-attempt.json")))
        throw new Error("Research start has an unknown outcome; inspect it before any further paid request");
      // Record before even reserving, so a lost reservation acknowledgement also
      // fails closed. The ordinary live allowance remains authoritative.
      save("gemini-attempt.json", { inputHash, at: new Date().toISOString() });
      const ticket = await budget.reserve({ workload: "research", model: GEMINI_RESEARCH_AGENT,
        amount: Math.ceil(estimatedReservationUsd * 1e6), terms: {
          authorization, accounting: "Authorized manual estimate; managed agent has no guaranteed dollar cap",
          estimatedReservationUsd, source: PRICING, ...(context ?? {}) } });
      save("gemini-ticket.json", ticket);
      start = await request("", body);
      save("gemini-start.json", start);
    }
    if (start.httpStatus >= 400 || !start.body.id)
      throw new Error(`Gemini start HTTP ${start.httpStatus}; inspect the preserved response and reservation`);
    let result = start.body;
    const completedFile = path.join(directory, "gemini-completed.json");
    if (fs.existsSync(completedFile)) result = read("gemini-completed.json");
    for (let poll = 0; ["in_progress", "requires_action"].includes(result.status); poll++) {
      if (result.status === "requires_action") throw new Error("Unexpected interactive planning; inspect the preserved task");
      if (poll >= 240) throw new Error("Polling paused after 60 minutes; the same provider task must be resumed or inspected");
      await pause(15000);
      const receipt = await request(`/${encodeURIComponent(start.body.id)}`);
      save(`gemini-poll-${Date.now()}-${poll}.json`, receipt);
      if (receipt.httpStatus >= 400) throw new Error(`Gemini poll HTTP ${receipt.httpStatus}; resume the same task`);
      if (receipt.body.id !== start.body.id) throw new Error("Gemini poll returned another task");
      result = receipt.body;
      progress(`Gemini ${result.status}; ${result.steps?.length ?? 0} recorded steps; task ${result.id}`);
    }
    if (!fs.existsSync(completedFile)) save("gemini-completed.json", result);
    const report = geminiReport(result);
    const cost = geminiResearchCost(result.usage);
    const ticket = read("gemini-ticket.json");
    if (!fs.existsSync(path.join(directory, "gemini-cost.json")))
      save("gemini-cost.json", { ...cost, estimateUsd: cost.amount / 1e6, reservationUsd: ticket.reserved / 1e6 });
    if (cost.amount > ticket.reserved)
      throw new BudgetStopped("Completed Gemini research exceeded its estimated reservation. The report is saved; reconcile the overrun before another paid step.");
    await budget.settle(ticket, cost.amount, { ...cost.receipt, responseId: report.responseId });
    return report;
  };
}
