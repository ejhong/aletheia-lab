<!-- {"vendor": "openai", "model": "gpt-6.2-astra", "utc": "2026-11-23T07:47:45.024716+00:00", "input_tokens": 6004, "output_tokens": 9374, "cost_usd_list_price": 0.423} -->

### (a) Errors of sign, algebra or logic

- **“In three Greenland ice cores, is the largest ammonium spike within 150 years of the Younger Dryas onset exceptional against every other 300-year stretch of the same record, or one of many like it?”**  
  The comparison is with usable, grid-aligned, non-overlapping windows, not every 300-year stretch. The target is ±150 years from the chosen centre: 12,900 rather than 12,896 b2k in NGRIP and NEEM, and a depth-based anchor rather than an independently dated onset in GISP2.

- **“The paper predates the NGRIP and NEEM data used here, so those two cores are a test on data its authors did not have.”**  
  The paper predates the cited *release*, which does not establish what measurements its authors had. The plan itself cites a 2015 analysis of NGRIP ammonium.

- **“The realised fractions (rank/N) are reported beside every verdict.”**  
  If `q` other windows tie the target, the fraction matching or beating it is `(rank + q)/N`, not `rank/N`. Under the stated rule, even a target matched by every window ranks first and counts as top 1%.

- **“In a series, *top 1%* means rank ≤ max(1, floor(0.01·N)) and *top 5%* means rank ≤ floor(0.05·N).”**  
  For `N < 20`, rank 1 is top 1% but not top 5%; G10 has at most 15 windows. To make the categories nested under the stated minimum-one convention, the 5% cutoff also needs `max(1, …)`.

- **“When NGRIP and NEEM are the two passing cores, or two of three, their winning bins must start within 60 years of each other; both are on GICC05.”**  
  A window can have multiple bins tied for maximum E. If one tied bin meets the timing rule and another does not, the verdict is undefined without a within-window tie rule; reporting ties *between* windows does not resolve it.

- **“No tier passes; the target is in the top 1% in some single series of a tier.”**  
  This does not imply **“One core only.”** Two cores can both rank first but fail the timing rule, or qualify in different tiers. The condition means “at least one top-1% series, no passing pair.”

- **“In two cores, measured alike, the spike near the onset would be among the one to three largest of roughly 40,000 or 100,000 years.”**  
  It is the **window maximum** that ranks first to third among usable window maxima. A single higher-ranked window can contain several spikes larger than the target spike.

- **“In GISP2 it adds `A / duration` to the sample that holds `t + 0.5`, and the bins are remade; if no sample holds it, the pulse is lost.”**  
  This implements an instantaneous midpoint impulse, not the stated pulse over `[t, t+1)`. Each intersected sample should receive `(A / duration) × (fraction of the pulse year overlapping that sample)`; only the fraction in gaps is lost.

- **“It is read together with the recovery test below, which says what size of fire the criterion could have seen.”**  
  Recovery measures **per-series threshold attainment for an added ammonium pulse**, not fire size or recovery by the multi-core timing criterion. A placement also counts if its window was already above threshold and the injected pulse changes nothing.

- **“Ranks on E with `a0` moved by half a bin (`T/2`; for T = 10 from the 10-yr files this cannot be done and is skipped).”**  
  Because `a0` defines both grids, this moves the target and comparison windows as well as the bins. It is a joint bin-and-window shift, not a bin-phase-only change.

- **“The rank correlation of E across windows between N10 and E10, N20 and G20, and E20 and G20.”**  
  For the GISP2 pairs, matching by `k` correlates E at equal offsets from separately dated anchors. Unlike N10–E10, it is not a correlation between windows established to cover the same dates.

### (b) Factual statements that are wrong

- **“None of the tiers includes the Holocene, which NGRIP lacks.”**  
  The Holocene began about 11,700 yr b2k. All three tiers include early Holocene ice, as does the specified NGRIP record extending to 10,270 yr b2k.

- **“Within NGRIP the onset is known to a few years, so ±150 years is far wider than any dating error there.”**  
  The 150-year allowance is far wider than the ±4-year uncertainty in locating the onset **on the adopted chronology**, not than the quoted 138-year maximum counting error in its absolute age.

- **“Within a tier all windows are diluted alike, but a pulse can sink into the noise, and the coarse tiers favour sustained rises over sharp spikes.”**  
  Only the nominal bin width is alike. In GISP2, different sample durations, bin-boundary overlaps and gaps can give the same pulse different binned amplitudes within one tier.

### (c) Contradictory instructions

- **“None of the above.” / “In two or more of the three cores, the target window has no E in any tier series.”**  
  **Not testable** is listed *below* **Not met**, so both can apply; if the sole measurable core ranks first, **One core only** and **Not testable** both apply instead. Evaluate **Not testable** first and the other verdicts only otherwise.

- **“Every GISP2 sample between 1711.5 and 1713.0 m: depths, ages, ammonium.” / “the target window `k = 0` is removed from every table”**  
  The fixed-depth instruction includes real-target samples even when a decoy window stands in for `k = 0`. In the decoy run, the exclusion must override “every GISP2 sample” for those sample rows.
