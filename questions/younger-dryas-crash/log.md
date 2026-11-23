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
