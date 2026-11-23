<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T07:36:01.553640+00:00", "input_tokens": 4921, "output_tokens": 30950, "cost_usd_list_price": 0.479} -->

### 1. Flaws That Could Produce a False Positive or False Negative

1. **Severe dilution of an acute fire spike in `G60` (and `N10`/`E10`) — False Negative [must fix]**
   - The primary decision rule uses 60-year bins (`G60`) for GISP2 on `H` and `E`, and 10-year bins (`N10`, `E10`) for NGRIP and NEEM. A 1–2 year wildfire/impact smoke pulse is diluted by **30×–60×** in a 60-year bin (a huge +200 µg/kg 1-year spike adds only +3.3 µg/kg to a 60-year mean), making it nearly invisible against multi-decadal climate shifts in biogenic/soil ammonium.
   - The plan's claim that *"all windows are diluted alike, so the ranking stays fair"* is wrong: heavy averaging penalizes brief, intense spikes far more than sustained warm-period elevations or clusters of smaller fires. Because `G60` is virtually blind to a 1–2 year peak, the primary rule effectively fails to test the GISP2 peak that the literature debates, and forces both `N10` and `E10` to pass.

2. **No cross-core synchrony check inside the 300-year target window — False Positive [must fix]**
   - The target window `[12,750, 13,050)` b2k contains ~154 years of the warm Bølling-Allerød (GI-1) and ~146 years of the cold Younger Dryas (GS-1). Because the rule takes the maximum anywhere in the 300-year window independently in each core, a large Allerød fire at 13,030 b2k in NGRIP and a completely unrelated YD fire at 12,760 b2k in NEEM (270 years apart!) would both fall inside the window and trigger an **"Exceptional"** verdict for the YD onset.
   - A ±150-year window also confuses *absolute* GICC05 counting uncertainty (138 yr MCE from 2000 CE) with *relative* stratigraphic uncertainty inside a core (which is ~0–5 yr relative to the GS-1 onset at 1526.52 m in NGRIP).

3. **Running background and MAD straddle the abrupt BA–YD climate transition — False Negative on `Z`, biased `E` [must fix]**
   - A centered 300-year running window right at the GS-1 onset puts half its bins in the warm, higher-NH4 Bølling-Allerød and half in the cold, lower-NH4 Younger Dryas.
   - A step change inside the background window **inflates `MAD(ln x)`**, shrinking the denominator of `z_j` and systematically depressing `Z` right at the YD onset (false negative) relative to spikes inside climatically stable periods.
   - For `E`, a spike on the cold (YD) side has its background pulled up by the warm Allerød (false negative), while a spike on the warm (Allerød) side has its background pulled down by the cold YD (false positive).
   - For `G60`, `2n+1 = 5` bins (and as few as 3 valid bins are permitted!), including `x_j` itself—computing a running median from 3–5 60-year bins across a climate transition is extremely noisy.

4. **Dropping `x ≤ 0` before taking `ln x`, and near-zero `MAD(ln x)` explosions — False Positive or False Negative on `Z` [must fix]**
   - CFA ammonium baselines frequently drift slightly below zero in clean glacial ice, and discrete GISP2 data can hit detection limits near zero. Dropping `x ≤ 0` bins truncates the left tail of the background distribution, biasing `median(ln x)` upward and distorting `MAD(ln x)`. Conversely, a single near-zero positive value (e.g. `0.01 µg/kg` from baseline noise) produces an extreme negative log that blows up `MAD(ln x)`.
   - Conversely, in quiet cold stadials (especially in `G20` with only 15 background bins), quantized or nearly flat low values can yield a tiny nonzero `MAD(ln x)`, producing spurious astronomical `z_j` values that outrank real fire spikes (false negative) or falsely inflate the target (false positive).

5. **Span mismatch across the three primary cores (Holocene missing in `N10`, folded Eemian included in `E10`) — Asymmetry / Bias [should fix]**
   - `N10` starts at 10,300 b2k (missing ~88% of the Holocene, when boreal forests recolonized North America and fire/biogenic NH4 was high), whereas `E10`, `G60`, and `G20` include the entire Holocene (`0–10,300` yr). In `G20` (0–50 ka), the Holocene makes up nearly a quarter of the record. Thus `H` and `E` are much harder to pass in `E10`/`G60`/`G20` than in `N10`.
   - Furthermore, `E10` extends to 121,440 b2k, which includes NEEM's **stratigraphically folded and disturbed Eemian ice** (>~108 ka), plus the Holocene brittle-ice zone with elevated missingness.

6. **Fixed bin-edge splitting right at the target center — False Negative (and False Positive in `G20`/`G60`) [should fix]**
   - In `G10` (`a0 = 12,735`, `T = 10`), the target center `12,885` falls **directly on the bin boundary** between `[12875, 12885)` and `[12885, 12895)`. A brief peak centered at 12,885 is split across two bins and attenuated by up to 50%.
   - Even worse, in sensitivity check #1 (120-year window, `a0 = 12,825`), `G60` has only two bins `[12825, 12885)` and `[12885, 12945)`—putting the cited peak (`12,885`) directly on the boundary between them.
   - Conversely, in primary `G60` and `G20`, anchoring `a0` directly on the cited GISP2 peak depth (`1712.0–1712.3 m` → `12,885 BP`) places that peak dead-center in a single bin, whereas comparison peaks elsewhere in the core hit bin edges at random—introducing both slight data-peeking circularity and a small phase advantage for GISP2.

7. **Thinning and CFA dispersion bias across deep glacial ice vs. YD — False Positive in `N3`/`N10`/`E10`, False Negative in `N1` [should fix]**
   - Ammonium has a longer dispersion tail in CFA systems (~1.5–2 cm) than conservative ions. At 60–120 ka in NGRIP and NEEM, annual layers thin well below 1 cm/yr (down to ~0.3–0.5 cm/yr), so CFA smearing and solid-state diffusion attenuate deep-glacial peaks more strongly than YD-onset peaks (biasing `N3`, `N10`, and `E10` toward a false positive against deep ice). The plan's Known Weaknesses note only mentions thinning working *against* the YD, missing the opposite direction against older glacial ice.
   - Also, in `N1`, linearly interpolating the 20-year GICC05 table onto 1 mm depths across the abrupt ~2× accumulation drop at the YD onset distorts 1-year bin durations right at the onset.

8. **Window usability (80% threshold) can mask a gap right on the YD onset — False Negative [should fix]**
   - Up to 20% of bins (60 years of the 300-year window, or 1 of the 5 bins in `G60`) can be missing while the target window is still declared "usable." If a core break or CFA dropout coincides with the YD onset itself, the series will still enter the verdict and score ordinary on the remaining 240 years.

---

### 2. Problems With the Decision Rules

1. **Measure `H` (raw concentration) does not test for a fire *spike* and is strongly confounded by shared climate state [must fix]**
   - Allowing **"Exceptional"** on `H` alone means a warm-period rise in background biogenic/soil ammonium (or a modest fire sitting on top of a warm Bølling-Allerød baseline) can pass without any exceptional peak excess (`E`) or anomaly (`Z`).
   - Because NGRIP, NEEM, and GISP2 are **not independent**—they share the same Greenland/North American glacial-interglacial and Dansgaard-Oeschger climate cycles—the plan's benchmark *"about 2% of the time by chance"* (which assumes independent cores and exchangeable windows) severely underestimates the false-positive rate for a window overlapping a warm interstadial.

2. **Resolution mismatch inside the "2 of 3 cores" rule makes the test unfair [must fix]**
   - Grouping `G60` (60-yr bins) alongside `N10` and `E10` (10-yr bins) for `H` and `E` means GISP2 cannot realistically detect a brief fire spike, effectively turning "2 of 3 cores" into "2 of 2 cores (both from the same lab)" for short events while keeping "2 of 3" for multi-decadal climate shifts.

3. **Discontinuous `floor(0.01·N)` threshold penalizes `G20` relative to `E10` [should fix]**
   - For `E10` (`N ≈ 404`), top 1% allows **rank ≤ 4** (top 0.99%). For `G20` (`N ≈ 166`, span 0–50 ka), `floor(0.01·166) = 1`, forcing GISP2 to be **strictly rank #1** (top 0.60%) to qualify as "top 1%" on `Z`.

4. **Contradiction and mislabeling around the "fine series" headline rule [should fix]**
   - The **Decision rule** section says rank 1 in `N3` or `G20` triggers the headline *"the largest peak in 50,000 to 60,000 years at fine resolution"*, whereas **What would count** says `"Partly for: 'unusual', or rank 1 in the fine series only"`—which ambiguously includes `N1` (`N ≈ 32`) and `G10` (`N ≈ 50`), where rank 1 across 3 measures happens ~9–10% of the time by chance.
   - Calling `G20` (20-year bins) *"fine resolution"* is inaccurate when `N10` and `E10` are 10-year bins (twice as fine!).

5. **Unspecified fallback if one of the three primary cores is "not testable" [minor]**
   - The plan states a series with an unusable target window is reported as "not testable," but does not state whether the verdict rule still requires 2 of the remaining 2 cores or becomes indeterminate.

---

### 3. Ambiguities for an Independent Programmer

1. **GISP2 (`iond.txt`) missing-value sentinels, header lines, units, and overlapping samples [must fix]**
   - The plan specifies a `< 999,999` filter for ages, but specifies **no missing-value representation** (blank, `-999`, `NaN`, negative values?) for `NH4` or `NO3`, nor whether a row with valid ages and a missing ion value is excluded *before* computing `total overlap` and the overlap-weighted mean (it must be filtered per-ion, since `NH4` and `NO3` can be missing independently).
   - It does not specify whether a units line follows the `Top` header line, whether GISP2 NH4 units match µg/kg (ppb vs. µeq/L—the plan labels `H` as `µg/kg` for all series), or whether `total overlap` for overlapping/duplicate samples is the sum of overlap lengths (which can exceed `T`) or the length of the union.

2. **Exact column names, comment skipping, and bin-rounding behavior in `N10`, `E10`, and `NGRIP 1 mm` [must fix]**
   - Given the noted May 2026 column mix-up in `NGRIP 10-yr`, the exact PANGAEA column headers and units for age, depth, ammonium, and nitrate must be named explicitly.
   - For `N10`/`E10`, the plan asserts a row with age `a` covers `[a, a+10)` and maps to `j = round((a - a0)/10)`. If the file reports bin *midpoints* (ending in `.005` ka = 5 yr) instead of bin starts, `(a - a0)/10` will be half-integers (`k.5`), causing Python's banker's rounding (`round`) and round-half-up implementations to disagree and map two rows into the same bin while leaving adjacent bins empty! The plan must verify `a` modulo 10 and specify what to do on collisions.
   - For `NGRIP 1 mm`, clarify whether negative 1 mm CFA readings are included in bin means or treated as missing/zero.

3. **Edge cases in `Z` (`x ≤ 0`) and window-level usability for `E` and `Z` [must fix]**
   - For `z_j`, it is ambiguous whether the *"fewer than half of those `2n+1` bins have values"* requirement is checked **before or after** excluding bins with `x ≤ 0`. (Also state explicitly that `z_j` is missing if `x_j ≤ 0`.)
   - It is ambiguous whether a window that passes the 80% usability threshold for `x_j` also requires ≥80% valid `e_j`/`z_j` to be included in `E`/`Z`, or whether even a single valid `e_j`/`z_j` in the window suffices.

4. **GICC05 row parsing ("four numeric fields") [should fix]**
   - Filtering `gicc05-60ka-20yr.txt` to rows with "four numeric fields" risks dropping valid `(age, NGRIP depth)` tie points if any row has a missing `δ18O` or `counting error` field (blank/`NaN`), or accidentally keeping a sentinel value (like `-999`). Filter specifically on valid numeric `age` and `NGRIP depth`, and state how duplicate/non-monotonic depths are handled.

5. **Boundary inclusion, exact integer thresholds, and scope of sensitivity outputs [minor]**
   - Specify exact inequalities for "wholly inside its span" (`win_start >= span_min` and `win_end <= span_max`) and exact integer counts for ≥80% (`5 * valid >= 4 * total`) and "fewer than half" (`2 * valid < total`) to prevent floating-point edge discrepancies.
   - Clarify whether **Other widths** (#1) applies to all 7 series or only the 4 long-record series; whether `window mean` excludes missing bins; how `bins with z_j ≥ 3` is handled for `G60` (where `Z` is undefined); and the exact denominator/inequality (`<` vs `≤`) for **The cited sample** (#5).

---

### 4. Missing Checks (in Order of Importance, Feasible With Named Public Data)

1. **Cross-core synchrony and onset-proximity check [must fix]**
   - Report the exact age (and depth, for `NGRIP 1 mm` and `GISP2`) of the winning bin for `H`, `E`, and `Z` inside the target window in each core, and verify whether the NGRIP and NEEM peaks are actually synchronous on GICC05 (e.g., within ±20 yr of each other and near 12,896 b2k) rather than unrelated Allerød and YD fires 200+ years apart.

2. **Matched-resolution, matched-span multi-core comparison [must fix]**
   - Using the exact same files, add:
     - `N10`, `E10`, and `G60` restricted to their **shared clean glacial span** (`10,300–107,620` yr, excluding both the Holocene and NEEM's folded Eemian >108 ka).
     - `N20`, `E20`, and `G20` (all at **20-yr resolution** over `10,300–50,000` yr) and `N10`, `E10`, `G10` (all at **10-yr resolution** over `10,300–15,000` yr). This removes both the resolution mismatch and the Holocene/Eemian span asymmetry in one step.

3. **Data-integrity and cross-file validation (runnable in `--decoy` mode without peeking at 12–14 ka) [should fix]**
   - Cross-check `NGRIP 10-yr` directly against 10-year averages computed from `NGRIP 1 mm` + `GICC05` outside 12–14 ka (e.g., 15–20 ka) to confirm units, column identities (catching any lingering column swap), and depth-age alignment.
   - Audit missingness vs. age (especially checking for gaps inside the target window, in NEEM's brittle-ice zone, and in NEEM >108 ka), the fraction of `x ≤ 0` bins, and the distribution of `MAD(ln x)` across windows (verifying that top-ranked `Z` windows are not near-zero-MAD artifacts).

4. **Bin-phase shift sensitivity (half-bin shift `T/2`) [should fix]**
   - Recompute `G60`, `G20`, `G10`, `N3`, and `N1` (and a 10-yr binning of `NGRIP 1 mm` to 60 ka) with bin boundaries shifted by `T/2`. This directly detects boundary-splitting attenuation (like `12,885` landing on the edge of `G10` and 120-yr `G60`).

5. **Climate-transition / regime-aware background check (using NGRIP δ18O already in `GICC05`) [should fix]**
   - Check whether `MAD(ln x)` in the target window is abnormally inflated compared to the rest of the record, and test a transition-robust background (e.g., shorter window, excluding `x_j` itself, or comparing the YD onset specifically against other abrupt Dansgaard-Oeschger transitions identified via the δ18O column already present in `gicc05-60ka-20yr.txt`).

6. **Local accumulation-rate (layer-thickness) check at the YD onset in NGRIP [should fix]**
   - Since `gicc05-60ka-20yr.txt` provides depth vs. age, compute local annual layer thickness `Δz/Δt` across the BA–YD transition (~12–14 ka, where ice thinning is effectively constant) and report the local flux-scaled peak (`NH4 × Δz/Δt`) to check whether an apparent concentration spike on the cold side of the onset is partly an artifact of the ~2× snowfall drop.

7. **Co-occurring GISP2 dust/ion context (`Ca`, `SO4`) and spike duration in `N1` [minor]**
   - Because `gisp2/chem/iond.txt` already contains `Ca` (dust) and `SO4`, descriptively reporting whether the GISP2 NH4 peak coincides with the YD `Ca` rise—and reporting peak duration (consecutive elevated years in `N1` and GISP2)—distinguishes a single-season smoke plume from a multi-year event without needing new data.

---

### 5. Issues in the Summary of the Literature

1. **Mischaracterization of Fischer et al. (2015)'s method — [should fix; High confidence]**
   - The plan says its `z_j` measure *"follows the fire-peak detection of Fischer et al. 2015, who flag values of log ammonium above a running median plus a multiple of the MAD."*
   - Fischer et al. (2015) applied that detector to **high-resolution (sub-annual/annual ~1 cm CFA) NGRIP ammonium** specifically to isolate brief individual wildfire plumes (days–weeks) above a seasonal/decadal biogenic background. Applying the same formula to **10-year and 20-year binned means** (`N10`, `E10`, `G20`) does not detect individual fire peaks; it detects anomalous decades/double-decades.

2. **Overstated novelty claim and omitted key prior ice-core analyses — [minor; Medium-High confidence]**
   - The statement *"We know of no published test that ranks the onset against every other stretch of the record with a rule fixed in advance"* is likely true regarding *pre-registration*, but omits that **Melott et al. (2010)** (*Geology* 38:635–638) and **Wolbach et al. (2018)** both explicitly ranked/compared the GISP2 ~12.9 ka NH4/NO3 peak against the rest of the GISP2 record, and **Legrand et al. (2016)** / **Zennaro et al. (2015)** examined Greenland (including NEEM) biomass-burning tracers across the glacial/YD/Holocene. Also note that Wolbach et al. (2018) was a two-part paper (Part 1, pp. 165–184, is the ice-core paper) and could not have used the 2022 Erhardt et al. NGRIP/NEEM datasets—making NGRIP and NEEM a genuine out-of-sample test of the GISP2 claim, which is worth stating accurately.

3. **Incomplete characterization of why supporters cite nitrate — [minor; High confidence]**
   - The plan describes nitrate solely as a poor *fire* tracer. While nitrate is indeed a poor standalone biomass-burning proxy in Greenland ice, impact-hypothesis papers (e.g., Melott et al. 2010; Wolbach et al. 2018) also cite nitrate as a tracer of **atmospheric shock ionization (NOx production from an impact/airburst)**, not purely wildfire smoke.

4. **Rasmussen et al. (2014) onset uncertainty notation — [minor; Medium-High confidence]**
   - The GS-1 onset age (`12,896 yr b2k`, MCE `138 yr`, NGRIP depth `1526.52 m`) matches Rasmussen et al. (2014, Table 2), but check the `± 4 yr` figure against Table 2 (MCE is the reported age uncertainty; the `± 4 yr` appears to conflate transition-definition precision from Steffensen et al. 2008 / earlier work with Table 2). More importantly, ensure the text does not imply that the 138 yr absolute MCE justifies a ±150 yr within-core search window.

5. **Unverified GISP2 peak depths used directly to lock `a0` — [should fix; High confidence]**
   - The plan itself flags the GISP2 ammonium depth (`1712.20–1712.30 m`) and platinum depth (`1712.0–1712.125 m`) as `unverified` (in Petaev et al. 2013, the Pt anomaly spans roughly 1712.0–1712.375 m, peaking near 1712.125 m, and is offset from the main NH4/NO3 spike). Locking the GISP2 target window center `a0` to an unverified depth from search snippets/memory—rather than to the published GISP2 climatic YD onset (δ18O / dust transition)—risks anchoring on the wrong depth or introducing peeking bias.

---

### The Three Changes I Would Make First

1. **Fix the resolution and span mismatch in the primary test:** Stop using 60-year bins (`G60`) to test an acute fire spike in the verdict rule, and stop mixing a Holocene-less `N10` with Holocene+Eemian `E10` and `G60`. Instead, align cores on matched spans and resolutions (e.g., `N10` vs. `E10` over their clean shared glacial span `10.3–108 ka`, paired with a matched all-three-core 20-yr comparison over `10.3–50 ka` and an explicit high-resolution test in `N1`/`N3`/`G10` with half-bin phase shifts).
2. **Require cross-core synchrony (or a narrower onset window) and fix the transition-straddling `Z` estimator:** Prevent unrelated Allerød and YD fires 250+ years apart from triggering "Exceptional" by narrowing the primary target window (or requiring peak synchrony across cores near the stratigraphic onset), and fix `Z` by specifying a noise floor/handling for `x ≤ 0`, guarding against near-zero `MAD`, and checking sensitivity to the BA–YD step change.
3. **Close all data-parsing and statistical edge-case ambiguities before locking the code:** Explicitly specify GISP2 missing-value sentinels, units, header skipping, and per-ion overlap filtering; verify exact PANGAEA column headers and bin-age alignment (avoiding `round()` half-integer collisions) via an `NGRIP 10-yr` vs. `NGRIP 1 mm` cross-check outside 12–14 ka; and specify exact usability/missing-value rules for `E`, `Z`, and target-window gaps.
