# Amendments — Pre-Bronze-Age Metallurgy Side-Channel (#82)

## Amendment 1 (2026-11-24, before executing analysis)

- **What changed:** Upon loading `legrand2024-id3_1-lead.txt` (Dome du Goûter, French Alps) against `legrand2024-id1_1-age.txt`, the archived lead sub-file spans depths `21.197–22.999 m` (`599 BCE to 766 CE`, i.e., `2,549–1,184 yr BP`), whereas the full `9,751 BP` depth range is only in the major-ion/dust file `legrand2024-id2-avg-chem.txt`. Consequently, `ddg_alps_lead.txt` contains zero samples older than `5,000 BP` and cannot compute a pre-5,000 BP empirical baseline or pre-5 ka upper bound.
- **How handled:** Dome du Goûter (`2,549–1,184 BP`) is retained as an independent **European Alpine Roman/Iron-Age positive-control benchmark** normalized to upper continental crust `(Pb/Ce)_UCC = 19/83 = 0.2289` (McConnell et al. 2018; Rudnick & Gao 2003). All pre-5,000 BP tests, cross-archive anomaly checks, and physical upper bounds are computed unmodified from the five remaining archives spanning `47,371–5,000 BP` (`RECAP`, `GISP2`, `EPICA Dome C`, `Füramoos`, and `Store Mosse`). No thresholds, binning windows, or verdict rules in `protocol.md` were altered.

## Amendment 2 — record added after the spot check (2026-11-24)

Nothing in the program or in `results/` was changed or rerun for this record.

1. **One archive is not what the plan says.** `PANGAEA.903892` is the Laphroaig peat bog on Islay, Scotland
   (55.63° N, 6.17° W; Kylander and others, *Boreas* 49:152, 2020), not Store Mosse in southern Sweden. The plan,
   the manifest, the program's names and the first report all called it Store Mosse. The manifest and the report
   are corrected; the program's variable names and the keys in the results file still say `store_mosse`.
2. **The known periods did not meet the plan's threshold.** The Null verdict (§4) requires the Roman and medieval
   controls to be detected with `p < 10⁻⁴` and `EF ≥ 2.0`. The Roman median is 1.56 in RECAP and 1.40 in Füramoos
   (published EF); in the Laphroaig bog the Roman and medieval `Pb/Ti` values are below the earlier level. The
   first report did not say so and, for that bog, reported raw lead, which the plan does not name. `RESULTS.md` no
   longer reports the plan's Null verdict as met.
3. **Füramoos enrichment.** The plan (§3) defines enrichment against the pre-5,000 BP median. The program computes
   that (`xef_renorm`) and tests the published EF instead. On the plan's definition 12 samples before 5,000 BP
   reach `EF ≥ 3`, two of them consecutive.
4. **The emission figure.** The plan's "~3.3 kt/yr" and "~40–80 kt/yr total production" are not in McConnell and
   others (2018), which gives a range of 0.3 to 3.8 and an average of 1.1 kt/a with a factor-of-two uncertainty.
5. **The plan's output for GISP2** (the Ice Age bound relative to RECAP's Roman level, §Test 4) was not reported.
   It is 124% (century maximum) and 90% (95th percentile).
6. **The first amendment and the log.** Amendment 1 says it was written before the analysis ran; it was committed
   with the results. The log entry committed before the lock described the Alpine core as "9.75 kyr"; that phrase
   was removed in the results commit without a note.
7. **Analyses added by the spot check, outside the plan:** the locked rule applied to the known periods;
   artificial signals added to the RECAP record; samples per thousand years; century-level tests. All are in
   `spotcheck/` and all are exploratory.
