# Log: populations at the Younger Dryas (#40)

## 2026-11-23: start (Claude Fable 5.2)

- Eugene asked for #40 to be run after #47. Marked active.
- **Scope cut to one line of evidence:** radiocarbon dates as a head count. The genetic lines in the issue are not
  attempted; they cannot resolve centuries.
- **Data.** p3k14c release 2025.07 (173,946 dates) and IntCal20. Counted before the plan: 2,562 North American,
  4,334 European and 1,975 Asian dates with radiocarbon ages 8,500–14,000. Nothing calibrated, no curve through
  time made.
- **Program and tests** written. On made-up data a planted halving is caught where the calibration curve allows,
  and where a flat stretch of the curve hides it the program reports low power and "cannot tell".
- **Review, two rounds, two vendors** (`review/README.md`). The made-up reference records were rebuilt to match
  the real record's make-up; the reference became a parabola; "no drop" became "a halving is excluded" with a
  stricter test; an aquatic screen was added.
- **False-alarm check** of the whole procedure on 100 made-up histories with no crash, using North America's real
  bins and errors: see `explore/calibration.json`.
- Dates admitted: North America 1,803 (212 screened out as aquatic), Europe 3,527, Asia 1,447.

## 2026-11-23: locked run, replication, checks afterwards, write-up (Claude Fable 5.2)

- **Lock:** 2026-11-23T17:17:16Z, commit `a3116e2`. Results committed after it.
- **Locked run:** no drop detected at the onset in any region. North America: after ÷ before 1.35 against an
  expected 1.13; none of 500 halving records as high. Europe: a halving excluded (0.8%). Asia: cannot tell (1.4%).
  Overall: not supported.
- **Replication:** OpenAI and Google programs both ran first time; curves and steps identical; overall verdict the
  same; Asia falls either side of the 1% line.
- **Found afterwards** (`explore/later_drop.py`, `explore/error_check.py`): the summed curves of all three regions
  share a spike at 12,850–12,600 and a hollow after it, where the calibration curve goes from steep to flat. The
  made-up reference, which trusts stated errors, carries too little of this. With errors inflated 1.5 to 2 times
  the exclusion of a halving weakens in North America and disappears in Europe.
- **No amendments.** Spent $2.71 of $40.
