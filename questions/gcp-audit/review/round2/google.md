<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T20:31:20.341998+00:00", "input_tokens": 6324, "output_tokens": 37428, "cost_usd_list_price": 0.5804} -->

### (a) Errors of sign, algebra or logic

1. > **For an artefact of the devices or the method:** "the excess is not specific to the events", or a calibration failure together with a paired difference whose interval includes zero.

   No confidence interval is defined for the paired difference (`Events against their own controls` specifies only the mean, SE, and a one-sided sign-flip `p`), and because the clause is not conditioned on `Z_events ≥ 1.645` or `≥ 300` pairs, it classifies a null result with miscalibrated controls (e.g., `Z_events ≈ 0`, `Z_controls ≈ 0`, control SD `> 1.2`) as an artefact. Define the paired-difference interval explicitly (or replace it with `paired p > 0.05`) and gate this clause on `≥ 300` pairs and `Z_events ≥ 1.645`.

2. > 4. Everything above for: events that do not overlap an earlier event in the test; pairs with the control earlier, and later; the test without the five events already scored in #47; each year; and each window length (under 1 hour; 1 to 6 hours; over 6 hours and under a day; a day or more).

   Because 1999 has only one event (`By year: 1 (1999)`), dividing by `n − 1` for standard deviations—and computing paired SE, Pearson `r`, and regression slope—is undefined (`0/0`) for that year. Restrict dispersion, correlation, and slope statistics to subsets with `n ≥ 2` (and clarify that "Everything above" does not include the `Overall` label, whose `≥ 300`-pair rule forces every year and window-length subset to **Insufficient coverage**).

### (b) Factual statements you are confident are wrong

None found. (The mathematical claims checked—including the `2.4%` full-day variance threshold, the cross-egg variance denominator `2(N − 1)/N`, and the Wilson–Hilferty error `< 0.002` at `df ≥ 600` out to `±4σ`—all check out.)

### (c) Instructions that contradict each other

1. > The label is given twice: for our main scores, and for the scores with theoretical standardising (item 1 below), since the project's table may have been built with either.
   >
   > ### Reported alongside, not part of the labels
   > 1. **Theoretical standardising** (`s = 7.0711` for every egg), for events and controls, with the same eggs.

   Theoretical standardising is placed under "not part of the labels," yet it receives a reproduction label and enters `What would count` ("under either standardising" / "under both standardisings"). Move its definition out of that section or change the heading to note that only its event/control comparisons, not its reproduction label, are outside the labels.

2. > **For an artefact of the devices or the method:** "the excess is not specific to the events", or a calibration failure together with a paired difference whose interval includes zero.
   >
   > **Mixed** and **insufficient coverage** are reported as they are. *(and in `Overall`: `**Mixed** | anything else; reported with the numbers and no further label`)*

   A calibration failure with `Z_controls < 2.58` (e.g., control SD outside `0.85`–`1.2` or `Z_controls ≤ −2.58`) and a paired-difference interval including zero—or any such case with `< 300` pairs—receives the `Overall` label **Mixed** or **Insufficient coverage**, yet `What would count` simultaneously classifies it as evidence for an artefact rather than reporting it as is. Either drop the second clause from `What would count` or promote it into the `Overall` table above **Mixed** (and below **Insufficient coverage** and **No excess found**).
