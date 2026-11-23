<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T03:50:45.450230+00:00", "input_tokens": 5104, "output_tokens": 48358, "cost_usd_list_price": 0.7407} -->

Here is a critical pre-registration review of the analysis plan. Each item is assigned a severity (**must fix**, **should fix**, or **minor**).

---

### 1. Flaws that could produce a false positive or a false negative

1. **`N3 = f4(A.Han, ONG; A.Mixe, G)` turns modern European contamination and reference bias into false positives — and the plan has the sign backwards.** (**must fix**)
   - Let ancient sample $G = (1 - c)\,\text{NatAm} + c\,\text{Eur}$ (modern European lab/museum contamination) and $\text{Mixe} = \text{NatAm}$. By linearity, $N3 = c \cdot f_4(\text{Han}, \text{ONG}; \text{NatAm}, \text{Eur})$.
   - Under the true tree $(\text{Outgroup}, (\text{Eur}, (\text{ONG}, (\text{Han}, \text{NatAm}))))$, the internal branch separating $\{\text{Han}, \text{NatAm}\}$ from $\{\text{ONG}, \text{Eur}\}$ makes $f_4(\text{Han}, \text{ONG}; \text{NatAm}, \text{Eur}) > 0$. Equivalently, European contamination makes $N1 = f_4(\text{Mbuti}, \text{ONG}; \text{Mixe}, G)$ slightly negative, makes $N2 = f_4(\text{Mbuti}, \text{Han}; \text{Mixe}, G)$ *strongly* negative (larger shared East Asian branch), and therefore makes $N3 = N1 - N2$ **strongly positive**.
   - The exact same sign holds for **African contamination**, for **excess ANE (West Eurasian-related) ancestry** in $G$ relative to Mixe, and for **reference bias toward GRCh37/hg19** (which is ~70% European and ~20% African, pulling $G$ away from the $\{\text{Han}, \text{NatAm}\}$ branch).
   - Under *Known weaknesses*, the plan states the opposite (*"Contamination from modern people would pull N3 down and could hide a real signal"*), which is only true for *East Asian* contamination.
   - Compounding this, `EARLY.*` includes every ancient genome *"whatever its assessment"* (including AADR-flagged contaminated/questionable samples), and the decision rule for `N` requires only $Z(N3) \ge 3.15$ without even requiring $N1 > 0$. A contaminated ancient individual with $Z(N1) = -1.5$ and $Z(N2) = -6.0$ would get $Z(N3) \approx +4.5$ and be declared to carry the Australasian signal.

2. **Sign error in `L2 = f4(ONG, Papuan; Reference, Amazon)`.** (**must fix**)
   - By the plan's definition $f_4(P_1, P_2; P_3, P_4) = (p_1 - p_2)(p_3 - p_4)$:
     - If Amazon shares an allele with **Papuan** ($p_{\text{Papuan}} = p_{\text{Amazon}} = 1$, $p_{\text{ONG}} = p_{\text{Ref}} = 0$), then $(0 - 1)(0 - 1) = +1$ (**positive**).
     - If Amazon shares an allele with **Onge** ($p_{\text{ONG}} = p_{\text{Amazon}} = 1$, $p_{\text{Papuan}} = p_{\text{Ref}} = 0$), then $(1 - 0)(0 - 1) = -1$ (**negative**).
   - The plan states the exact opposite (*"closer to Onge (positive) or to Papuans (negative)"* and *"L2 strongly negative (Papuan side)"*). Either flip the first two arguments to `f4(Papuan, ONG; Reference, Amazon)` or flip the interpretation.

3. **Unfiltered European (and minor African) admixture in `B.Pima` (and `A.MesoOther`) will cause massive false positives in `P_B` and `R`, and false negatives in `L3` and Panel B's `S`.** (**must fix**)
   - HGDP Pima (`B.Pima`) and several SGDP Mesoamerican individuals (`A.MesoOther`: Zapotec/Nahua/Mixtec) are well known to carry colonial-era European admixture (~5–15% in many HGDP Pima), whereas HGDP Suruí and Karitiana are nearly unadmixed.
   - If Reference has European admixture $\alpha$ and Amazon does not, then along the shared East Eurasian branch (Onge = NatAm = 1, Mbuti = Eur = 0), $f_4(\text{Mbuti}, \text{ONG}; \text{Ref}, \text{Amazon}) = +\alpha \cdot d_{\text{EastEur}} > 0$ (**false positive** in `P_B`, `R`, and `L1`). African admixture in Reference pushes `P_B` positive in the same direction.
   - Simultaneously, along the shared East Asian branch (Han = NatAm = 1, ONG = Eur = 0), $f_4(\text{Mbuti}, \text{Han}; \text{Ref}, \text{Amazon})$ gets an even larger positive inflation, which (a) pushes `L3 = f4(Han, ONG; B.Pima, B.Amazon)` **negative** (false negative) and (b) pushes East Asian groups *above* Australasians in Panel B's Specificity ranking `S` (false negative).
   - Right now, Panel B is virtually pre-doomed to fail `T3` and produce distorted `P_B`, `R`, `S`, and `L` results.

4. **Paired pipeline bias in `N3` and `N4`, and inaccurate claim that `P` and `R` stay within one pipeline.** (**should fix**)
   - In `N3 = f4(A.Han, ONG; A.Mixe, G)`, `A.Han` and `A.Mixe` are both modern diploid **SGDP** calls, while `ONG` (Mondal et al. 2016) and `G` (ancient pseudo-haploid capture/shotgun) are **non-SGDP**. Any systematic SGDP allele-frequency/calling shift shared by `A.Han` and `A.Mixe` produces a **positive bias** in `N3` (and a **negative bias** in `N4 = f4(A.Han, ONG; G, A.Amazon)`).
   - Neither `T1` (SGDP vs NYGC) nor `T2` (ancient capture vs ancient shotgun) tests modern diploid SGDP vs ancient pseudo-haploid data.
   - Also, the plan claims *"P and R stay within one pipeline and are unaffected"*, which is false: `ONG` and `JAR` are Mondal et al. 2016 (not SGDP or NYGC), and `Chimp.REF` is a reference sequence. While `Mixe` and `Amazon` sharing a pipeline mostly cancels symmetric Mondal-vs-SGDP bias in `P` and `R`, `W` in `S` mixes many pipelines (SGDP, NYGC, 1000G, Mondal, EGDP, etc.) with no pipeline check.

5. **1240K SNP ascertainment bias from Human Origins Panel 10 (Karitiana).** (**should fix**)
   - AADR 1240K includes Human Origins Panel 10 (~24,000 SNPs, ~2% of 1240K), ascertained as heterozygous in an HGDP **Karitiana** donor (who is very likely inside `B.Karitiana` and potentially `A.Karitiana`).
   - Conditioning on heterozygosity in Karitiana selects mostly low-frequency derived alleles ($p_{\text{Kar}} = 0.5 > E[p_{\text{Mixe}}]$). For alleles derived Out-of-Africa ($p_{\text{NonAfr}} > p_{\text{Mbuti}}$), $(p_{\text{Mbuti}} - p_{\text{NonAfr}})(p_{\text{Mixe}} - p_{\text{Kar}}) > 0$. This biases `f4(Mbuti, NonAfrican; Ref, Karitiana)` **upward** for *all* non-Africans (including Onge and Han), at a magnitude (~$10^{-4}$) comparable to a 1–2% Population Y signal.

6. **Ancient DNA damage (transitions) is not gated in `N` or `Sumidouro5`, nor checked in `L1`/`L4` (`Tianyuan`).** (**should fix**)
   - `Tianyuan.AG.BY.AA` is a single ancient capture individual and many ancient South American genomes in AADR are non-UDG or half-UDG treated. Computing transversions-only is merely noted *"as a check"* for `N3`, with no role in any decision rule for `N`, `Sumidouro5`, or `L1`/`L4`.

7. **Unmodeled close relatives in `B.Surui`, `B.Karitiana`, `B.Pima`, and ancient sites.** (**should fix**)
   - HGDP Suruí and Karitiana contain numerous 1st- and 2nd-degree relatives. While block jackknife SE handles genome-wide LD for the sampled individuals, retaining close relatives overweights specific families (amplifying family-level drift or admixture) and fails to address the exact Castro e Silva et al. 2021 finding cited in the plan.

8. **Pooling capture (`.AG`), shotgun (`.SG`), and heterogeneous ancestries inside `CELL.*`, `REGION.*`, and `ANC.*`.** (**should fix**)
   - Pooling 100k-SNP and 1.2M-SNP individuals lets a few high-coverage individuals (or one densely sampled site) dominate a region, while mixing `.AG` and `.SG` makes `T2` hard to interpret.
   - `REGION.NORTH` pools First Americans with Arctic/Inuit/Paleo-Eskimo/Athabaskan groups who carry real extra East Asian ancestry ($N2 \gg 0 \implies N3 \ll 0$ and $N4 \gg 0$), confounding `N3` and `N4`.

9. **Exact algebraic equality `N3 = N1 - N2` does not strictly hold under pairwise SNP filtering.** (**minor**)
   - Each statistic uses SNPs non-missing in its own four sets. Because `Mbuti`, `Han`, and `ONG` have slightly different missingness, `N3` is only approximately `N1 - N2` unless restricted to the common SNP intersection.

---

### 2. Decision rules that are unfair, miscalibrated, or do not test what they claim

1. **The `Headline` rule does not require Australasian specificity (`S`), `L3` (Onge > Han), or a clean `Han` control.** (**must fix**)
   - *"Real and robust in public data"* requires only: `P` replicates, `R` is robust/partly robust, and `T3` is clean *"for the panel that replicates."*
   - A completely non-specific artefact (e.g., Karitiana Panel 10 ascertainment bias, African admixture in Mixe, or weak European admixture below `|Z(T3)| = 3`) that pulls Amazon equally toward `Han` and `ONG` could pass `P`, `R`, and `T3` and earn the headline *"Real and robust in public data"* even if `S` and `L3` completely fail.
   - Also, the rule does not require `R` to be robust in the *same* `T3`-clean panel that replicated `P`.

2. **The `Primary (P)` rule allows an admixed Panel B (`B.Pima`) to declare replication even if Panel A is noise.** (**must fix**)
   - `max(Z(P_A), Z(P_B)) >= 3` with the other `> 0` gives two shots at `Z >= 3` without multiple-testing correction, and if `Z(P_B) = +8` (from Pima European admixture) while `Z(P_A) = +0.2` (noise), `P` is classified as *"For: The signal replicates."* The phrasing *"the panel that replicates"* in `Headline` is then inconsistent with `P`'s joint rule.

3. **The `Specificity (S)` rule is broken both by AADR's Oceanian/Negrito diversity and by ranking on Z-scores.** (**must fix**)
   - Requiring *"at least four of the five Australasian groups [ONG, JAR, Papuan, Nasioi, Australian] among the ten highest of the 145"* will **falsely fail** if AADR v66.p1 contains other Papuan, Melanesian, Philippine Negrito, Australian, or Eastern Indonesian shotgun groups (it does — e.g., Choin et al. 2021, Larena et al. 2021, Papuan sub-groups) that legitimately occupy top-10 ranks and crowd out `Australian` ($n = 2$) or `JAR` ($n = 4$).
   - Ranking by **Z-score** rather than `f4` heavily penalizes small-$n$ groups (`Australian`, $n = 2$; `JAR`, $n = 4$) relative to large-$n$ groups (`Han`, $n > 40$; `Japanese`, etc.), because SE shrinks with sample size. Under any slight East Asian bias (like `B.Pima` European admixture), large-$n$ East Asian groups will sweep the top 10.

4. **The `Sumidouro5` rule uses the very statistic (`N1`) the plan rejects as biased, with two unadjusted bites at the apple.** (**must fix**)
   - Declaring replication if $Z(N1) \ge 3$ in *"either of its two versions"* ignores reference bias, ignores ancient DNA damage (no transversions requirement), ignores `N2`/`N3`, and picks the better of two versions (or four tests if counting both `ONG` and `A.Papuan`) without correction. This repeats the exact vulnerability at the heart of the Moreno-Mayar vs. Campelo dos Santos dispute.

5. **`Early presence` can be triggered by a single unassessed, contaminated genome.** (**must fix**)
   - Because `EARLY.*` includes samples regardless of AADR assessment and `N3` turns European contamination into a positive Z-score, *"supported if any EARLY cell or early individual carries the signal"* has a high false-positive risk.

6. **The `L` rules confuse absence of evidence with evidence of absence, leave `L4` and the `Han` control without rules, and ignore low power for `Tianyuan`.** (**should fix**)
   - Treating `|Z(L2)| < 3` as *"near zero"* (equidistant to Onge and Papuan) conflates low statistical power with true equality; `L2` needs an effect-size/CI bound (or ratio to `P`).
   - `Tianyuan` is a single ancient capture genome ($n = 1$), so `L1` has far less power than `P_A`/`P_B`.
   - `L4` and the `f4(Mbuti, Han; Reference, Amazon)` control have no thresholds and no downstream consequences if violated.

7. **The `Technical (T)` gating rule does not actually rescue `N` when `T2` fails, and leaves `T3` out of `R`, `S`, `L`, and `N`.** (**should fix**)
   - *"unless N2 is near zero"* has no threshold and is logically invalid: capture-vs-shotgun bias in `f4(A.Han, ONG; VER.AG, VER.SG)` (`T2`) is not ruled out by `N2 ≈ 0`, and `N2` can legitimately be non-zero in northern/Arctic groups.
   - `T3` only flags `P`, leaving `R`, `S`, `L`, and `N` ungated even when Reference admixture severely distorts them.

8. **The `Robustness (R)` grid has heavily correlated cells, and its median `Z >= 2` criterion is pulled in conflicting directions.** (**minor**)
   - Splitting `A.Amazon` into `A.Surui` ($n=2$) and `A.Karitiana` ($n=3$) and halving cells to transversions reduces Z-scores mechanically, while half of Panel A's cells use admixed `A.MesoOther` and all of Panel B's use admixed `B.Pima` (inflating Z-scores). Meanwhile, the 96/48 cells are tightly correlated, so "90% positive" is easy to pass once the mean is positive.

---

### 3. Ambiguities that could cause an independent programmer to compute something different

Given the strict replication criteria (**exact set membership identity** and **Z within 0.1**), the following ambiguities will almost certainly break replication:

1. **Exact `.ind` group labels and selection criteria for Panels A and B are not specified.** (**must fix**)
   - Only `A.MesoOther`, `Chimp.REF`, and `Tianyuan.AG.BY.AA` are given exact strings (and even for `A.MesoOther`, it is unclear whether `.DG` suffixes appear in `.ind`).
   - An independent programmer cannot determine exact `.ind` labels for `A.Papuan` vs `B.Papuan` (e.g., `Papuan.DG` vs `Papuan_Highlands.DG` / `Papuan_Sepik.DG`), `B.Nasioi` (HGDP uses `Bougainville.DG` in many AADR releases), `A.Mbuti` vs `MbutiPygmy`, or how to isolate Mondal `ONG (6)` and `JAR (4)` without pulling in SGDP `S_Onge-1`/`S_Onge-2`.
   - It is also unspecified whether Panels A and B filter by `Pass` assessment or exclude `_rel`/`_o`/`Ignore` labels, or how to handle SGDP individuals who have *both* `S_` and `B_` entries.

2. **Individual deduplication and pairing rules (`DUP`, `VER`, `W`, `Ancient`) never name the `.anno` key column or tie-breakers.** (**must fix**)
   - Specify whether "same person" is matched via `Master ID` (column 2 of `.anno`), how `SNP count` is measured (`.anno` autosomal 1240K column vs. counting non-missing chr 1–22 calls in `.geno`), and how ties in SNP count are broken.
   - For `DUP.SGDP`/`DUP.NYGC` (11 individuals) and `VER.AG`/`VER.SG` (8 individuals): specify the exact filters defining the eligible pool (Americas only? `Pass` only? Minimum SNPs? What if an individual has multiple `.AG` versions or `.TW` Twist capture?).
   - For `W`: specify whether "shotgun data" means Genetic ID ending `.DG`/`.SG` or a specific `.anno` `Data source` string (and whether pseudo-haploid `.SG` modern samples are included); define `"outside the Americas"` explicitly (e.g., what about `USA` non-Indigenous groups like `CEU`/`ASW`/`Hawaiian`, or `French Guiana`/`Greenland`?); specify case-sensitivity for excluded substrings (`-o`, `_o`, `Ignore`, etc.) and whether deduplication occurs *before* or *after* the `>= 2 individuals per group` filter.

3. **Exact weighted block jackknife formula is underspecified.** (**must fix**)
   - Different implementations of "weighted block jackknife (Busing et al. 1999)" disagree by >0.1 in Z-score depending on: (a) whether variance is centered on the jackknife bias-corrected estimate $\hat{\theta}_J$ (as in Busing et al. Eq. 5 / ADMIXTOOLS) or on the full-data estimate $\hat{\theta}$, (b) whether empty 5 cM blocks ($m_j = 0$) are excluded from block count $g$, and (c) whether genetic position comes from `.snp` column 3 and how any `0.0` genetic positions are handled. Write out the exact formula for SE.

4. **Relative 1% agreement tolerance in `Replication` fails for near-zero statistics.** (**must fix**)
   - `T1`, `T2`, `T3`, `L2`, and the `Han` control are expected to be near zero. Floating-point summation differences of $10^{-8}$ on a value of $10^{-7}$ produce a 10% relative discrepancy and fail the 1% rule. Add an absolute floor (e.g., `|f4_1 - f4_2| <= max(1e-6, 0.01 * |f4_1|)`).

5. **Geographic and temporal assignment rules for `Ancient Americans` have edge-case ambiguities.** (**should fix**)
   - **Boundary inclusivity:** Exact dates `8200`, `4200`, `500` BP and exact coordinates `50°`, `-100°`, `-30°`, `-21°`, `-64°` are not specified as `>=`/`>` or `<=`/`<`.
   - **Distance to coastline ("within 75 km"):** Specify WGS84 geodesic vs. Haversine (and Earth radius) and **point-to-line-segment** vs. **point-to-vertex** distance on the 1:50m shapefile (at 1:50m resolution, vertices can be 10–30 km apart).
   - **Country/entity lists and missing coordinates:** Explicitly list all `Political Entity` strings included in `"the Americas"`, `"CARIB"`, and `"the Guianas"`, and specify how missing (`..`) lat/long values are handled.

6. **Exact `W` labels for the five Australasian groups in `S`, and ambiguity in `"either of its two versions"` for `Sumidouro5`.** (**should fix**)
   - Specify the exact `.ind` labels in `W` corresponding to `ONG`, `JAR`, `Papuan`, `Nasioi`, and `Australian`.
   - Clarify whether `"either of its two versions"` for Sumidouro5 means its two AADR Genetic IDs tested with `ONG` only, or also includes `A.Papuan` (4 tests).

7. **Minor ambiguities in `transversions`, `D` SE, and `"near zero"`.** (**minor**)
   - Specify unordered allele pairs `{A, G}` and `{C, T}` (so `G/A` and `T/C` are also dropped).
   - Specify whether `D` receives a jackknife Z-score (and if so, block weights).
   - Define `"near zero"` numerically in `T` and `L2`.

---

### 4. Important missing checks (in order of importance, feasible with AADR v66.p1)

1. **Individual-level colonial admixture & contamination screening (European and African), plus an unadmixed Panel B reference.** (**must fix**)
   - For every present-day American individual in Panels A and B (`A.Mixe`, `A.MesoOther`, `B.Pima`, `Suruí`, `Karitiana`, etc.), compute `f4(Mbuti, French; Ancient_Ref, ind)` and `f4(Chimp, Yoruba; Ancient_Ref, ind)` using a pre-colonial unadmixed ancient reference (e.g., Anzick-1 or Spirit Cave). Pre-specify an exclusion cutoff (blinded to Australasians) to build an unadmixed `B.Pima` (or `B.Pima + B.Mayan`) reference so Panel B is actually usable.
   - For every ancient set `G` (especially `EARLY.*`), compute `f4(A.Mbuti, A.French; A.Mixe, G)` and `f4(A.Han, A.French; A.Mixe, G)`, and tabulate AADR `.anno` contamination estimates (X-chr / mtDNA) and UDG status.

2. **Ancient-vs-Ancient matched-data-type test and SGDP-matched `A.Papuan` test for `N`.** (**must fix**)
   - Add `N3_Papuan = f4(A.Han, A.Papuan; A.Mixe, G)` (all three modern sets in SGDP, removing the SGDP-vs-Mondal paired pipeline confound).
   - Add matched ancient-vs-ancient tests `f4(A.Mbuti, ONG; Ancient_Ref, G)` and `f4(A.Han, ONG; Ancient_Ref, G)` (both all-SNPs and transversions-only), using a clean ancient `.AG` capture reference for capture sets and `.SG` shotgun reference for shotgun sets, and check `REGION.*`/`CELL.*` split by `.AG` vs `.SG`.

3. **Close-relatives removal check in Suruí, Karitiana, Pima, and ancient sets.** (**should fix**)
   - Compute pairwise IBS/kinship directly from `.geno` (and check `.anno` relatedness flags), prune 1st- and 2nd-degree relatives deterministically (e.g., keep highest-SNP member per connected component), and re-run `P_A`, `P_B`, `L3`, and `R`. This directly tests the Castro e Silva et al. 2021 finding.

4. **1240K Karitiana ascertainment bias check.** (**should fix**)
   - Report individual-level `f4(Mbuti, Han; Ref, ind)` beside `f4(Mbuti, ONG; Ref, ind)` for every Karitiana and Suruí individual (to detect if a single ascertained Karitiana donor shows an excess pull to *all* non-Africans), and run `P_A`/`P_B` restricted to SNPs polymorphic in Yoruba/Mbuti (e.g., $0.05 < p_{\text{Yoruba}} < 0.95$), which suppresses OOA-derived Karitiana ascertainment bias.

5. **Modern-vs-ancient technical check (`T4`) and African-admixture technical check (`T3b`).** (**should fix**)
   - Add `f4(A.Mbuti, A.Han; A.Mixe, CELL.MESO.LATE)` and `f4(A.Han, ONG; A.Mixe, CELL.MESO.LATE)` (all-SNPs and transversions) to directly measure modern-diploid vs. ancient-pseudo-haploid bias in matched populations.
   - Add `f4(Chimp, Yoruba; Ref, Amazon)` to `T3` to detect uneven African admixture.

6. **Leave-one-out checks on `A.Mixe` ($n = 3$) and site-level breakdown of any positive ancient `REGION.*`/`CELL.*`.** (**minor**)
   - With only 3 Mixe individuals, a single slightly admixed or noisy individual shifts all of Panel A and `N`. Similarly, verify that any positive `REGION.*`/`CELL.*` signal is not driven by one outlier or contaminated site.

7. **Archaic (`Denisova`) check in `L`.** (**minor**)
   - Using the Denisova genome in AADR 1240K, report `f4(Chimp, Denisova; Ref, Amazon)` alongside `L2` (power is low for 1–2% ancestry, but it is a cheap complementary check on Oceanian vs. deep Asian ancestry).

---

### 5. Issues in the literature summary

1. **Characterization of Posth et al. 2018 (*Cell* 175:1185) as writing that the signal *"might be a false positive."* — should fix (medium confidence, ~70%).**
   - Posth et al. 2018 came from the same senior group (Reich/Skoglund) that published Skoglund et al. 2015. They found no Australasian signal in any of the ancient South Americans they tested (notably including ~9.6 kya Lapa do Santo in Lagoa Santa, right near Sumidouro) and noted that the signal's ancient distribution and timing remained unresolved, rather than dismissing the modern Suruí/Karitiana signal as a likely false positive. Verify the exact wording in Posth et al. 2018 before locking.

2. **Omission of Yang et al. 2017 (*Current Biology* 27:3202) and Raghavan et al. 2015 (*Science* 349:aab3884). — minor (high confidence, ~95%).**
   - `L1` and `L4` test `Tianyuan`, yet the literature summary omits Yang et al. 2017, which originally reported that 40,000-year-old Tianyuan shares the excess allele sharing with Amazonians (Suruí/Karitiana). Raghavan et al. 2015 (published simultaneously with Skoglund 2015, reporting a weaker/broader signal) is also a central piece of the disagreement.

3. **Campelo dos Santos et al. 2022 (*Proc. R. Soc. B* 289:20221078) cited from preprint only. — minor (high confidence).**
   - The summary of Sumidouro5 sensitivity is broadly accurate, but the published peer-reviewed version should be checked rather than relying on the preprint.

4. **Internal slight contradiction on *"Every published reading ... Beringia"* vs. `L2`. — minor (high confidence).**
   - Most genomic papers favor a Beringian arrival, though *"every published reading"* is slightly absolute, and `L2`'s decision rule explicitly tests *"what recent contact with Pacific islanders predicts"* (which *would* imply a sea crossing, contradicting *"What this cannot show: a sea crossing"*).

5. **2026 *Nature* paper (`doi:10.1038/s41586-026-10406-w`). — cannot verify.**
   - This is at or past my knowledge cutoff, so I cannot confirm or refute the summary of its findings or EGA accession.

*(The summaries of Skoglund et al. 2015, Moreno-Mayar et al. 2018, and Castro e Silva et al. 2021 appear accurate — high confidence.)*

---

### Three changes I would make first

1. **Fix the sign error in `L2` and overhaul `N` so contamination/reference bias cannot create false positives:** flip `L2` to `f4(Papuan, ONG; Reference, Amazon)` (or correct its sign text); exclude QC-failed/contaminated samples from `EARLY.*`; require positive `N1`, transversion-confirmed `N3`, and clean European-contamination checks (`f4(Mbuti, French; Mixe, G)`) to call an ancient signal; and add both an SGDP-matched `A.Papuan` version of `N3` and a data-type-matched ancient-vs-ancient test.
2. **Fix Reference admixture, `Headline`, and `Specificity (S)`:** screen out European/African-admixed individuals from `B.Pima` (and `A.MesoOther`/`A.Mixe`) using an unadmixed ancient American reference (blinded to Australasians); require a clean `Han` control and `L3` (`f4(Han, ONG; Ref, Amazon)`) for the `Headline` claim (with `P`, `R`, and `T3` satisfied on the same clean panel); and revise `S` to rank by `f4` (not just `Z`) and test enrichment across *all* Australasian/Melanesian/Negrito groups in `W` instead of a brittle top-10 count of five groups.
3. **Remove all programmatic ambiguities before locking:** specify exact `.ind` labels (or exact `.anno` column rules) for Panels A, B, and `W`, `Master ID` deduplication and tie-breaking, period/coordinate boundary inclusivity, point-to-segment WGS84 coastline distance, the explicit Busing et al. (1999) jackknife variance equation, and an absolute tolerance floor for near-zero `f4` replication checks.
