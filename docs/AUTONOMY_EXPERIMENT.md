# Can another AI pass improve the publication?

This experiment tests the founder's continuing-conversation model: read the
question and earlier work, investigate, update the record, and produce a better
illustrated account. It does not test whether an operator can make a good article
by choosing findings and rewriting model outputs interactively.

## Starting point

Use Deep Memory at Lab commit `d9d350e94fb838c77c505ac910026ef9e12e9a59`.
Keep its weak incumbent, all existing records and decisions, and the complete
Birdmen homepage and founding brief. These are development-era inputs, not a
blind holdout. The earlier Gemini report and the later interactive corrections
are part of its known history. Do not call either an autonomous first pass.

The question spans Pillar 43 and proposed bird-human parallels, handled forms,
boar and reptile motifs, culture-bringer traditions, and flood traditions.
Orientation across those strands is necessary; equal attention or one shared
explanation is not. Founding inputs always travel with the complete current
case. Linked pages and image pixels require actual retrieval.

## Fixed process

1. Save the complete input, case snapshot, source-code and prompt fingerprints.
2. Commission a broad Gemini Deep Research Max investigation using the common
   research prompt. Preserve the provider response, original input and every
   citation together. One provider task per round; polling resumes that task.
3. Give Astra the complete handoff to plan source verification and reconcile
   concrete additions, corrections, arguments and research opportunities.
   Retrieve the selected sources and check the consequential readings against
   those documents. Missing material is explicitly deferred.
4. Prepare the checked record changes in an isolated working copy. Use the
   existing edition drafter and independent comparison against the incumbent.
   The article, selected claims and assessment are considered together.
5. Keep the incumbent if the candidate is worse, unchanged or fails review.
   Preserve useful research and the reasons for every failed or deferred step.
   Nothing in the experiment bypasses publication review or grants standing.
6. Run exactly the same process a second time on the resulting experimental
   state, with the first round's report, changes and decisions as memory.

The second round is explicitly commissioned to measure continued value even
when the ordinary scheduler would rest. It is not permission for endless
reconsideration. Transport, validation and budget failures are not saturation.
Do not change prompts between rounds or quietly repair content. Any intervention
ends the uninterrupted experiment; preserve that attempt and start a separately
identified revision of the protocol. Automated recovery must be specified in
advance and every attempt retained.

## What we judge

Compare each candidate with the incumbent and retain the actual reasons:

- **Evidence:** consequential assertions have checked provenance; corrections
  survive; uncertainty and shared ancestry are handled honestly.
- **Understanding:** substantive competing arguments and replies are recognizable;
  the account distinguishes local observations from stronger historical claims.
- **Coverage:** the ledger gains useful depth across the founding question;
  unresolved strands remain visible. Count records for orientation, not success.
- **Reading:** a coherent, interesting illustrated essay, clear selection and
  routes into the evidence; clarity does not come from dropping a serious objection.
- **Memory:** the second round uses prior decisions, avoids pointless rediscovery,
  and can reconsider them for a reason. A sound decision to retain an edition counts.
- **Autonomy and cost:** exact paid calls, reservations, failures, source-check
  outcomes and operator interventions. No hidden editorial rescue.

Independent comparison is a useful filter, not proof of truth or a statistically
validated improvement score. Inspect source-specific reasons and the rendered
articles. Two rounds can reveal a working cycle or a failure; they cannot prove
indefinite improvement or establish the best provider.

After Deep Memory, repeat the unchanged process on megalithic-casting as the
mature-case test. A fresh report without the case's memory can later serve as a
control if the first two rounds warrant the additional expense. Do not buy a
provider tournament before establishing a useful complete update.

## Spending and publication

Recurring workers remain disabled. On 2026-09-07 the founder approved the
specific two-round spending request: “spending rtequrests approved”. This
authorizes temporarily resuming Lab API calls and raising the daily allowance
to $100 while retaining the $150 monthly limit and $30 review reserve. Restore
the paused state and $25 daily limit when the experiment finishes or stops.
Existing unresolved reservations stay in the allowance. The previous report accounted
for about $15.07, and two Astra editing calls for about $1.36. Those are observed
development costs, not a promise about the next requests.

Approved estimate for this experiment: approximately **$40–60** for two research
reports, editing, source checks and comparison, within the existing $150 monthly
allowance. Gemini's managed agent has no documented hard dollar ceiling; research
reservations are estimates and an overrun must remain visible. Launch the second
round only after the first has a complete usage receipt and enough allowance
remains. Keep recurring schedules off. Publication remains a separate, gated
decision. The original Aletheia repository remains frozen.

Provider references: [Gemini agent execution and limitations](https://ai.google.dev/gemini-api/docs/deep-research),
[Gemini tariffs](https://ai.google.dev/gemini-api/docs/pricing), and
[OpenAI research handoff guidance](https://developers.openai.com/api/docs/guides/deep-research).

## Status

Prepared protocol; no new paid experimental round has started. Infrastructure
tests and a valid prepared input must never be reported as a successful research
experiment. The completion record must link the two real rounds and their
rendered candidates, or state precisely where execution stopped.

Prepare with `node scripts/experiment-case.ts prepare deep-memory <experiment-id>`.
Run each round with `node scripts/experiment-case.ts run <experiment-id> <1|2>
<authorization-file>`, using the existing private authentication loader. The
command never changes the allowance or publishes. It saves the baseline,
complete input, exact model requests and responses, source captures, costs and
candidate case snapshots under the ignored `.research-runs/` directory. Publish
an inspectable, appropriately licensed receipt after evaluating the experiment.

Each round prioritizes up to twelve original-source retrievals for verification;
the research agent itself has no imposed search-count target. Additional readings
remain deferred. Reconciliation can emit up to six existing twenty-record
proposal bundles. These are processing limits, not research quotas or a claim
of exhaustive coverage. Oversized or unreadable documents remain explicit gaps.

This first protocol has no automatic content repair. Malformed proposals and
failed source checks remain recorded; independent valid bundles can advance.
An interrupted paid editing call stops the attempt. A research task can resume
only by polling its recorded provider ID; an ambiguous start cannot be retried.
Changed code, prompts or intervening case edits stop the fixed experiment.
