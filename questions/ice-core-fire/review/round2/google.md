<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T07:47:48.444616+00:00", "input_tokens": 6549, "output_tokens": 33225, "cost_usd_list_price": 0.518} -->

### (a) Errors of sign, algebra or logic

1. > "In a series, *top 1%* means rank ≤ max(1, floor(0.01·N)) and *top 5%* means rank ≤ floor(0.05·N)."
   - When `N < 20`—which occurs in G10 (`N = 15`), and in the 600-year variant for N1 (`N = 16`) and G10 (`N = 7`)—`floor(0.05·N) = 0`, making *top 5%* impossible while *top 1%* is `rank ≤ 1`. Change *top 5%* to `rank ≤ max(1, floor(0.05·N))`.

2. > "When NGRIP and NEEM are the two passing cores, or two of three, their winning bins must start within 60 years of each other; both are on GICC05. If they do not, the pair does not count, and the result is reported as 'high windows, different peaks'. A pair that includes GISP2 cannot be checked this way, since its timescale differs; such a pass is labelled 'timing not checkable'."
   - When all three cores pass in T20 or T60 and NGRIP and NEEM are > 60 years apart, disqualifying only the NGRIP–NEEM pair still leaves (NGRIP, GISP2) and (NEEM, GISP2) passing as "timing not checkable", whereas blocking the whole tier makes a passing (NGRIP, GISP2) pair fail when NEEM also passes. Also, if NGRIP and NEEM fail timing in T10 and no other tier passes, the verdict table produces **One core only** (or **Not met**), not "high windows, different peaks"; specify the exact 3-core precedence and how "high windows, different peaks" maps to the verdict table.

3. > "| **One core only** | No tier passes; the target is in the top 1% in some single series of a tier. | … | **Not met** | None of the above. | … | **Not testable** | In two or more of the three cores, the target window has no E in any tier series. |"
   - Whenever **Not testable** holds, no tier can pass, so the remaining core either reaches top 1% (**One core only**) or does not (**Not met**, "None of the above", which also sits above **Not testable**). Make **Not testable** the first rule checked so it takes precedence over all other verdicts.

---

### (b) Factual statements confident are wrong

1. > "None of the tiers includes the Holocene, which NGRIP lacks."
   - The Holocene began at 11,703 yr b2k (Rasmussen et al. 2014), so NGRIP (starting at 10,270 yr b2k) and all three tiers (starting at 10,300 yr b2k) include ~1,350–1,430 years of the early Holocene. Change to state that NGRIP and the tiers exclude only the Holocene younger than 10,300 (or 10,270) yr b2k.

2. > "GISP2's samples last at most 18.6 years before 50,000 BP and 57.3 years before 110,000 BP, which is why it enters at 20 and 60 years."
   - "Before 50,000 BP" means chronologically earlier (ages > 50,000 BP, where GISP2 samples are longer, up to 57.3 years), and "before 110,000 BP" lies outside the aged record. Replace "before" with "younger than" (or "at ages ≤") 50,000 BP and 110,000 BP.

---

### (c) Instructions that contradict each other

1. > "we use them as given and never compare a GISP2 age with a GICC05 age." vs. "The rank correlation of E across windows between N10 and E10, N20 and G20, and E20 and G20."
   - Pairing windows of N20/E20 (GICC05) with G20 (GISP2) directly compares GISP2 and GICC05 ages (which diverge by centuries to >1,000 years over 10.3–50 ka). Either drop N20–G20 and E20–G20 from item 8 or remove/qualify the "never compare" rule.

2. > "No concentration from 12,000 to 14,000 years ago has been printed or plotted, and the decoy run (below) leaves the target window out." / "the target window `k = 0` is removed from every table, another usable window at least ten windows away (chosen with seed 43) stands in for it, and the whole program runs, the made-up fires included." vs. "Every GISP2 sample between 1711.5 and 1713.0 m: depths, ages, ammonium."
   - Depths 1711.5–1713.0 m are inside the GISP2 target window (~12,885 yr BP), so running the whole program in `--decoy` prints real target-window concentrations. Instruct `--decoy` to omit item 7 (or apply it to the decoy window's depths).

3. > "(generator `numpy.random.default_rng(43)`, one stream per series in the order N10, E10, N20, E20, G20, N60, E60, G60, N3, N1; draw the window index, then the year as an integer offset from the window start)."
   - Giving each series its own `default_rng(43)` stream ("one stream per series") makes the series order irrelevant, whereas requiring a specific order only applies to a single shared stream. Specify either one shared `default_rng(43)` stream consumed in that order, or explicit per-series streams (e.g., via `SeedSequence.spawn` in that order).

4. > "Reported with the same statistics, outside the decision:" [N3, N1] and "**Against, within limits:** 'not met', provided the made-up fires show that a large event would have been caught." vs. "**Partly for:** 'unusual'; or rank 1 on E in N3 or N1, reported by name with its core, span and bin length."
   - Because N3 and N1 are outside the tier verdict, a run can simultaneously trigger **Partly for** (rank 1 in N3 or N1) and **Against, within limits** (verdict **Not met**) or **Not established** (verdict **One core only**, which also rejects single-core results). Either remove N3/N1 from **Partly for** or define explicit precedence between them and the tier verdicts.
