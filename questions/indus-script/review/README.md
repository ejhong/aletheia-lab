# Review of the plan before it was locked

Google's `gemini-4-neon` read `protocol.md` twice on 27 November 2026 (UTC 28 November), before any new list
existed. Its replies are in `round1/` and `round2/`, each with the text it saw (`protocol_as_reviewed.md`; the
name of the lab's director is taken out before sending). To run a round: `python3 review/run_review.py <round>`
from `questions/indus-script` (add `--narrow` for an errors-only round). The key comes from `GEMINI_API_KEY`.
Cost: $0.75.

Between the two rounds the plan changed for a second reason as well: a report on the public dispute showed that
both sides had by then run control languages themselves, and that what they still disputed was whether Tamil
stands out when its list is built like the others. The question and the rules were rewritten around that.

## Round 1

| Point | Done |
|---|---|
| "Standard error" over 100 rounds that reuse the same seals and names is not a standard error | The significance test is gone. A pass now needs 80 of 100 rounds and a mean of at least a quarter of the preprint's Tamil list's. The plan says what the spread of rounds does and does not measure. |
| Drawing 600 from about 650 names against 600 from 1,125 gives unlike overlaps; a list could fall under 600 | New lists are used whole at 550 to 600 names; the preprint's longer lists are sampled to 600 a round; the difference is stated as a limit. Short lists are rebuilt once. |
| "Cannot verify" was uncapped in the check | A sample now fails with fewer than 40 of 50 ok, as well as with more than 5 wrong. |
| Web access could lead a session to the preprint or the rebuttal | Sessions list what they consulted; a session that consulted either is discarded. Stated as a limit. |
| Letter maps distort sounds; Old Irish spelling is far from its sounds | Old Irish replaced by Finnish, whose spelling is close to its sounds. Maps apply digraphs in order. A rule is given for a letter the map misses. The rest is a stated limit. |
| How finely names are split is uncontrolled; categories were designed on Tamil | Left to the sessions, as in the preprint's own controls; share of one-part names reported; both stated as limits. |
| One fresh Tamil list is too few | Two, each from its own sessions. |
| Sumerian is not unconnected with the Indus | Wording corrected: Sumerian was spoken by trading partners, as Akkadian was, which the preprint used as a control on that ground. Kept, because both sides of the dispute ran it. |
| The calibration verdict cannot fail | Kept as a guard against a fault in the run, and described as that. |
| No floor on the size of a pass; one and two passing controls treated inconsistently; fresh Tamil ignored in some branches; controls compared with the preprint's list and not with fresh Tamil | Rules rewritten: two answers (do controls pass; does fresh Tamil stand out from the controls by rank and by mean) and one overall reading that uses both. |
| The contest was not specified well enough to program independently | `analysis/METHOD.md` gives every step, table and seed, and is part of the plan. |
| Report full distributions and a comparison across lists | Median, standard deviation and quartiles are reported, with the ranking of the ten lists. |
| Diagnostics of each list before the contest | Reported for every list: size, mix, one-part names, candidates a sign, checker counts. |
| Shuffle the pictures | Added for every list, 20 shuffles. |
| Leave the top sign out for every passing list | Added. |
| A fresh Sanskrit list | Not done. The question is about Tamil against unrelated languages; left for a follow-up. |
| Replace Sumerian with a language with no contact | Not done, for the reason above. |

## Round 2 (errors only)

Three inconsistencies of wording, all corrected: the summary of what counts for and against did not match the
rule; list sizes were described as both "600" and "550 or more"; and the preprint's Akkadian run used rounds 20
to 29, not 0 to 9. No factual error was reported.
