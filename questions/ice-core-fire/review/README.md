# Review of the plan before it was locked

Two models from other vendors read `protocol.md` before any result existed: OpenAI `gpt-6.2-astra` and Google
`gemini-4-neon`, on 2026-11-23. Their full replies are in `round1/` and `round2/`, with the text they saw
(`protocol_as_reviewed.md`). The script is `run_review.py`. Cost: $1.76 at list price.

## Round 1: the first design

The first design ranked a 300-year window on three measures and joined the cores with a "two of three" rule in
which NGRIP and NEEM were binned at 10 years and GISP2 at 60.

What the reviewers found, and what was done:

| Point (who) | Done |
|---|---|
| Two cores could "agree" on peaks centuries apart inside the window (both) | A timing rule for NGRIP and NEEM; the age of every winning bin is reported |
| GISP2 at 60 years next to the others at 10 is not like for like; spans differ, some with the Holocene and some without (Google) | Three tiers, each with one bin length and one span for all its cores |
| Raw peak height mostly tracks climate; the log score can explode in quiet ice; they are not three views of one thing (both) | Only the excess over the local background decides; the other two are reported |
| "All windows are diluted alike" is wrong; nobody measured what the test can see (both) | Made-up one-year pulses added to the real series; weakness reworded |
| The background median straddles the climate step at the onset (Google) | One-sided backgrounds reported as a variant |
| Bin edges fall differently on the target and on other windows (both) | Half-bin shift reported as a variant |
| The chance figures (2%, 9%) assume independence the cores do not have (both) | Removed |
| "One core only" and "ordinary" overstated what failing the rule shows (OpenAI) | Renamed; "not testable" added |
| Age label of the 10-year file was asserted, not checked; possible column swap (both) | Cross-check against the 1 mm file, outside 12,000–14,000 years: label and columns confirmed |
| Parsing left open: missing codes, coverage in the 1 mm file, overlap, logs of non-positive values, edge inequalities (both) | Spelled out |
| Petaev et al. put the platinum about 30 years before the ammonium; my depths were from memory (both) | Text corrected; the claim is marked unverified, as is the GISP2 anchor |
| Fischer's Younger Dryas minimum is not evidence against one big peak at the onset (OpenAI) | Reworded as context |
| The supporters' case is wider than Greenland ammonium (OpenAI) | The question now says so |

Not done, and why:

- Climate-matched controls (comparing the onset only with other abrupt coolings). It needs a list of transitions
  chosen in advance, and adds a second comparison set. Left as a limit.
- Deconvolving the instrument's smoothing, or passing made-up pulses through it. The made-up pulses are added
  after smoothing, and the plan says recovery is therefore optimistic.
- An independent pick of the GISP2 onset from its dust record. The 600-year variant is the check instead.
- Flux instead of concentration. No accumulation series was fetched.
- Context from other ions in GISP2.

## Round 2: errors only

The rebuilt plan went back with a narrower brief: errors of logic, wrong facts, contradictions. Both found real
ones, all fixed before the lock:

- "Top 5%" was impossible in a series with fewer than 20 windows (both).
- The verdict table could give two verdicts at once; "not testable" is now checked first (both).
- The timing rule did not say what happens when all three cores qualify (Google).
- "None of the tiers includes the Holocene" was wrong: they include its first 1,400 years (both).
- "Before 50,000 BP" read backwards (Google).
- The made-up pulse in GISP2 was put at a point, not spread over its year (OpenAI).
- The decoy run would have printed real GISP2 samples from the target depths if it ran every reported item; the
  plan now says it does not (both). The program never did.
- The correlation between GISP2 and the other cores compared ages across timescales; dropped (both).
- Smaller wording errors: "every 300-year stretch", "one of the three largest spikes", the tie fraction.

There was no third round. The plan as locked has not been read by another model.
