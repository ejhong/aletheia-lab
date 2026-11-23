<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T04:05:35.470023+00:00", "input_tokens": 7449, "output_tokens": 48888, "cost_usd_list_price": 0.7557} -->

Below is a critical review of the pre-registration protocol across all five requested dimensions.

---

## 1. Flaws that could produce a false positive or a false negative

### 1.1 Finite-sample bias in the denominator of T3 underestimates European admixture by ~2× in Panel A — **must fix**
In T3, the admixture fraction is estimated as:
$$\alpha = \frac{f_4(\text{Mbuti}, \text{French}; \text{Amazon}, \text{Reference})}{f_4(\text{Mbuti}, \text{French}; \text{Amazon}, \text{French})}$$
Because **French appears in both P2 and P4**, the naive plug-in estimator $(p_M - p_F)(p_A - p_F)$ is **not unbiased**: its expectation equals the true $f_4$ **plus** the sampling variance of $p_F$, namely $\mathbb{E}[P_F(1 - P_F) / (2 N_F)]$.
- In Panel A, `A.French` has only $N_F = 3$ diploid individuals ($2N_F = 6$). On 1240K SNPs, $\mathbb{E}[P_F(1-P_F)] \approx 0.12\text{--}0.15$, producing an upward bias of roughly **+0.020 to +0.025**.
- The true $f_4(\text{Mbuti}, \text{French}; \text{Amazon}, \text{French})$ is itself only ~0.02–0.03. Thus the denominator is inflated by ~70–100%, cutting $\alpha$ and the "share of $P$ explained by admixture" roughly **in half**, making Panel A falsely appear clean (false positive risk for `P_A`). Even in Panel B ($N_F=28$), this adds a ~10% bias.
- **Fix:** Either subtract the standard finite-sample heterozygosity bias $p_F(1-p_F)/(n_F - 1)$ when a population is repeated, or use a second disjoint European population (e.g., `Sardinian` or `English`) in P2 of both numerator and denominator.

### 1.2 Putting `CARIB` into the ancient northern baseline `BASE_t` contaminates it with South Americans — **must fix**
`BASE_t` is defined as `ANC.NCA` (`NAM_WEST + NAM_EAST + MESO + CARIB`) and described as "the nearest ancient counterpart of the Mixe."
- In AADR, the Caribbean `.AG` dataset is heavily dominated by **hundreds of Ceramic Age individuals** (e.g., Fernandes et al. 2020; Nägele et al. 2020) who descend from **South American (Orinoco/Amazonian Arawak) populations**, genetically close to present-day Amazonians/Piapoco rather than Mixe or North Americans.
- Because `CARIB` will constitute a huge fraction of `BASE_AG` (far outnumbering `NAM_WEST`/`NAM_EAST`), `BASE_AG` will carry South American/Amazonian-related ancestry. This severely attenuates `M1 = f4(A.Mbuti, A.Papuan; B, G_t)` for ancient South Americans (`ANC.SA`, `EAST_SA`, `ANDES_COAST`), creating a major **false negative** in Section N.
- **Fix:** Remove `CARIB` from `BASE_t` (use `NAM_WEST + NAM_EAST + MESO`, or `MESO` alone as a secondary check) and test `CARIB` as its own region against the northern baseline.

### 1.3 Geographic rules sweep Polynesian territories (Rapa Nui, Hawaii) into `ANDES_COAST` and `NAM_WEST` — **must fix**
- `ANDES_COAST` assigns `Peru, Ecuador and Chile north of −30°, 75 km or less from the sea`. **Rapa Nui (Easter Island)** is politically `Chile`, lies at latitude **−27.1°** (> −30°), and is 0 km from the sea. If AADR v66.p1 contains ancient Rapa Nui genomes (e.g., Moreno-Mayar et al. 2024) with `Political Entity = Chile`, they will be placed into `REGION.ANDES_COAST` and `ANC.SA`. Because Polynesians carry ~25–30% Papuan/Near-Oceanic ancestry, even one Rapa Nui individual would cause a **catastrophic false positive** supporting the Pacific-coast Population Y signal.
- Likewise, `NAM_WEST` (`the rest of the USA, longitude < −100°`) sweeps in **Hawaii** (~20°N, ~155°W) if any ancient Hawaiian samples exist under `USA`, injecting Polynesian/Papuan ancestry directly into `BASE_t` (causing massive false negatives in `M1`).
- **Fix:** Add explicit mainland longitude bounds (e.g., exclude longitude $< -85^\circ$ for South America / `ANDES_COAST`, and exclude $< -130^\circ$ for contiguous `USA` / `NAM_WEST`, plus verify `sets.tsv` manually for non-Americas islands).

### 1.4 `K1` and `K3` ("falls short of the Amazonian level") violate the protocol's own ancient-vs-present-day safeguard — **must fix**
Section N begins by explaining that ancient-vs-present-day comparisons suffer from reference bias, chemical damage, and contamination, and therefore restricts `M1`/`M3`/`MF` to same-type ancient comparisons. Yet `K1 = f4(A.Mbuti, A.Papuan; G, A.Amazon)` and `K3 = f4(A.Han, A.Papuan; G, A.Amazon)` immediately compare **whole ancient sets `G` (mixing `.AG` and `.SG` together)** against **present-day `.DG` `A.Amazon`**, on **all SNPs (including transitions)**, with **no transversion check**, **no `f4(Mbuti, French; G, A.Amazon)` check**, and **no T2 unreliability flag**!
- Modern European contamination or hg19 reference bias in `G` pulls `G` toward Europeans (away from `Papuan` relative to `Mbuti`, inflating `K1`, and slightly closer to `Han` than to `Papuan`, inflating `K3`), creating **false positives** for "falls short of the Amazonian level."
- **Fix:** Separate `K1`/`K3` by data type (`.AG` vs `.SG`), require transversion confirmation (`K1_tv`, `K3_tv`), add a contamination/reference-bias screen `f4(A.Mbuti, A.French; G, A.Amazon)`, and mark `K1`/`K3` unreliable if `T2` fails (just as is done for the paper-form statistics).

### 1.5 Capture-reagent (1240K vs Twist) and UDG-treatment batch effects inside `.AG` and `.SG` — **must fix**
- In recent AADR releases (v54–v66), `.AG` pools **classic 1240K capture** and **Twist Ancient DNA capture** together. Rohland et al. (2022) demonstrated that 1240K vs Twist capture introduces systematic allele-frequency biases generating significant nonzero $f_4$ statistics (`|Z| > 3`). If `BASE_AG` is predominantly 1240K capture while newer South American sets are Twist capture (or vice versa), `M1`, `M3`, and `MF` will suffer false positives or false negatives.
- Both `.AG` and `.SG` also mix **non-UDG (damage-rich)** and **UDG-half/full** libraries, while `M1`, `M3`, and `MF` are tested on **all SNPs** (with only a sign check—not significance or magnitude—on transversion `M1`).
- Also, matching data type purely by Genetic ID suffix (`ends .AG` / `ends .SG`) will silently exclude ancient genomes with `.DG` (some high-coverage ancient shotgun genomes) or `.AG.BY.AA`-style suffixes from `M` while keeping them in `K` and `EARLY`.
- **Fix:** Inspect `.anno` capture/library metadata to stratify 1240K vs Twist (or run a Twist-vs-1240K technical check), use `.anno` data-type fields rather than suffix heuristics, and test `M1`, `M3`, and `MF` on transversions (`tv`) whenever UDG treatment is unbalanced.

### 1.6 Step 1 admixture screening: unscreened baseline `U` and re-inserting admixed donors — **must fix**
- **Unscreened `U`:** When screening individual `i` (e.g., in `Mixe`, `Pima`, or `Amazon`), `U` is that panel's *unscreened* Amazon set. If one or more Amazonians in `U` carry European/African admixture, `U` itself is pulled toward French/Yoruba, masking genuine admixture in `Mixe`/`Pima` (and in other admixed Amazonians).
- **Reverting to admixed donors:** If a set drops below 2 people, the rule keeps its *unscreened* (confirmed admixed!) members. For `A.Mixe` ($N=3$) or `A.Pima` ($N=2$) or `A.Surui` ($N=2$), putting confirmed European/African-admixed individuals back into `P_A` or `R` actively introduces bias (whereas a single high-coverage diploid genome works cleanly in $f_4$, or the set should be excluded from pass/fail rules).
- **Fix:** Screen `Amazon` iteratively first (dropping the worst outlier from `U` until clean) before using clean `U` to screen other American sets, and do not re-insert confirmed admixed donors into primary or robustness sets.

### 1.7 No pooled African-admixture check in T3 — **should fix**
Step 1 screens individuals for African admixture at $Z(a_i) \ge 3$, but small amounts of sub-Saharan African admixture (e.g., 0.5–1% across multiple `B.Pima` or `A.Mixe` individuals) can pass individual screening while producing a large pooled effect in `P = f4(Mbuti, Papuan; Reference, Amazon)`—because `f4(Mbuti, Papuan; Yoruba, Amazon)` is the entire Out-of-Africa drift, far larger than `f4(Mbuti, Papuan; French, Amazon)`.
- **Fix:** Add a pooled African check `f4(Chimp, Yoruba; Reference, Amazon)` (and its induced fraction of `P`) to T3 alongside the European check.

### 1.8 Karitiana ascertainment bias in 1240K SNPs is not controlled in `P_A` or `P_B` — **should fix**
The 1240K SNP set incorporates Human Origins Panel 5, which was ascertained as heterozygous in a **Karitiana** individual, and Karitiana accounts for 60% of `A.Amazon` and `B.Amazon`. Because derived alleles shared on the Out-of-Africa/Papuan branch have mean frequency $q < 0.5$, conditioning on Karitiana heterozygosity ($p_{\text{Karitiana}} = 0.5$) creates $\mathbb{E}[p_{\text{Karitiana}} - p_{\text{Reference}}] > 0$ at sites where $p_{\text{Papuan}} > p_{\text{Mbuti}}$, biasing $f_4(\text{Mbuti}, \text{Papuan}; \text{Reference}, \text{Karitiana})$ **upward** on `all` SNPs. Although `Surui`-only and `yri` cells appear in `R`, `P_A` itself is unprotected, and `R` can pass (`90% positive, median Z >= 2`) even if `Surui + yri` fails.
- **Fix:** Report and explicitly gate on `Surui`-only on `yri` (and/or San-polymorphic) SNPs, and directly test `f4(Mbuti, Papuan; Surui, Karitiana)` on `all` vs `yri` SNPs.

### 1.9 Tianyuan (`L1`, `L4`) is an ancient capture genome tested on all SNPs without transversion or reference-bias checks — **should fix**
`Tianyuan.AG.BY.AA` is a 40,000-year-old capture genome with pseudo-haploid calls and ancient-DNA reference bias. In `L4 = f4(Tianyuan, Papuan; Reference, Amazon)`, even modest European ancestry in `Reference` shares hg19 reference bias with `Tianyuan`, biasing `L4` **upward** (falsely favoring Papuans over Tianyuan) and `L1` **downward** (hiding a Tianyuan signal). Neither `L1` nor `L4` is checked on transversions (`tv`).

---

## 2. Flaws in decision rules

### 2.1 Literal gap in Headline rules when `P_A` is inconclusive (`2 <= Z < 3`) — **must fix**
The Headline rules cover `P_A` detected ($Z \ge 3$) and `P_A` not detected ($Z < 2$), leaving **no headline defined** if $2 \le Z(P_A) < 3$ (which is quite plausible given that 1240K has ~10× fewer SNPs than Skoglund's whole genomes, where $Z = 4.26$).

### 2.2 Headline completely ignores `T1`, `P_B`, `P_B.heldout`, and kinship — **must fix**
`P_A` uses the **exact same 8 people** as Skoglund et al. 2015 Table 1, so `P_A` passing is only a computational reproduction on the same donors. Under the current rules, the study can still declare **"Detected and robust in public genomes"** even if:
- `T1` fails (`|Z| >= 3`), demonstrating a serious pipeline artefact;
- `P_B` or `P_B.heldout` (the only non-overlapping donors in the study) is zero or negative; or
- Removing close relatives in Panel B eliminates the signal (the exact objection raised by Castro e Silva et al. 2021).
- **Fix:** Require `T1` to pass (or explicitly demote to "with caveats" if `T1` fails) and integrate `P_B.heldout` and kinship-pruned `P_B` into the top-level verdict rather than only reporting them alongside it.

### 2.3 T3 "admixture clean" rule is too permissive (50%), sign-inconsistent, and broken for `P <= 0` — **must fix**
- Calling a panel "clean" when European admixture explains **49% of `P`** is far too loose (removing 49% of a $Z=3.5$ signal drops it to $Z \approx 1.8$, below detection).
- If `Z(T3) >= +3` (Amazon has *more* European ancestry than Reference), that biases `P` *downward* (conservative), yet `|Z(T3)| < 3` fails the check.
- If `P <= 0`, dividing `induced / P` flips the sign, potentially marking a heavily admixed panel "clean."
- **Fix:** Only penalize European excess in `Reference` (`Z(T3) <= -3` or induced share > 10–20%, and/or require the admixture-corrected residual `P - induced` to remain significant at $Z \ge 2$ or $3$).

### 2.4 Specificity uses a two-sided `|Z(Han control)| < 3` that penalizes genuine Papuan admixture — **should fix**
Because Native Americans' ~65% East Asian ancestry shares ~20,000+ years of drift with `Han` after the `Papuan` split, `f4(Mbuti, Han; Mixe, Papuan)` is strongly **negative**. Therefore, genuine Papuan-like admixture in Amazonians is expected to make `Han control = f4(Mbuti, Han; Reference, Amazon)` **slightly negative**—and North-South Native American substructure (e.g., extra East Asian/Beringian affinity in `B.Pima` vs `B.Amazon`) also pushes `Han control` negative. A two-sided `|Z(Han control)| < 3` can falsely fail specificity on a real signal.
- Note that negative `Han control` *does* inflate `L3 = P - (Han control)` if `Reference` has Han-specific ancestry, so the right logic is: check `Z(Han control) < 3` (no general non-African/East-Asian pull toward Amazon) **and** require both `P > 0` (significant) and `Z(L3) >= 2`, while flagging strongly negative `Han control` as a caveat on `L3` rather than an automatic specificity failure.

### 2.5 Robustness grid (`R`) conflates biological hypotheses with technical robustness and includes doubtful/tiny-N cells — **should fix**
- Every cell in Panel A splits `A.Amazon` into `A.Surui` ($N=2$) or `A.Karitiana` ($N=3$), and crosses them with `A.Pima` ($N=2$), `A.Australian` ($N=2$), and `tv` (~30% of SNPs). Requiring `median Z >= 2` across these small-$N$, subsampled-SNP cells can easily fail a genuine signal that has $Z \approx 3.2$ in `P_A`.
- Including both `{Papuan, Australian}` and `{ONG, JAR}` in the robustness grid conflates Question 1 (is the signal real?) with Question 3 (is it closer to Papuans or Onge?). If the signal is genuinely stronger in one lineage, the grid penalizes it.
- If Step 1 marks `A.Pima` ($N=2$) "doubtful" (reverting to admixed donors), 72 of the 216 cells (33%) are still included in the pass/fail percentage and median.
- **Fix:** Exclude sets marked doubtful in Step 1 from `R`'s summary score, and separate the robustness check (outgroup/reference/SNP class/Suruí-vs-Karitiana) from the Australasian-source comparison.

### 2.6 Anchor "counts against" rule compares incomparable `D` scales across SNP sets and quartets — **should fix**
- Skoglund et al. 2015's `D = 0.0211` came from **unbiased whole-genome sequencing**, whereas `0.0072–0.0099` came from the **Human Origins array** (including quartets other than `(Yoruba, Papuan; Mixe, Surui)`). Because `D`'s denominator scales with SNP heterozygosity, 1240K ascertained SNPs will naturally yield a much smaller `D` than whole genomes (and slightly different from Human Origins) even on the exact same genomes.
- Switching from `P_A` ($N=5$ Amazonians, $f_4$) to the Anchor ($N=2$ Suruí, $D$) to decide whether the data "count against" the published effect is inconsistent—`Surui` alone has wide CIs and excludes 60% of `P_A`'s Amazonians.
- **Fix:** Clarify the WGS-vs-1240K `D`-scale difference explicitly, and if making an equivalence/ruling-out claim, base it on an empirical 1240K effect-size benchmark rather than a cross-platform array minimum from a different quartet.

### 2.7 `L1` and `L4` (Tianyuan) have no decision thresholds — **should fix**
Unlike `L2` ($|Z| \ge 3$), the protocol defines no Z-score threshold (nor whether Panel A, Panel B, or both must pass) for concluding that Tianyuan shares the excess (`L1`) or that Papuans share more of it than Tianyuan does (`L4`).

### 2.8 Ancient (`N`) `|Z(MF)| < 3` rationale is partly backward and penalizes real ANE variation; family size `m` is inflated by non-Pass versions — **should fix**
- The plan justifies `|Z(MF)| < 3` by saying "contamination by modern Europeans lowers M1"—but if contamination in `G_t` *lowers* `M1`, it causes a false negative, not a false positive! Meanwhile, genuine prehistoric differences in Ancient North Eurasian (ANE) ancestry between ancient regions (e.g., `NORTH` or `ANDES` vs `BASE_t`) can push `|Z(MF)| >= 3` in large pools with small SEs, falsely disqualifying real signals.
- Including **non-Pass `EARLY` versions** (which by rule "cannot support a conclusion") and duplicate versions of the same person in the multiple-testing family inflates $m$ and $Z^*$ unnecessarily.
- Also, the detectability simulation evaluates `f4(A.Mbuti, A.Papuan; A.Mixe, donor)` against present-day `A.Mixe` rather than against `BASE_t`, so it does not reflect the actual power of the ancient decision test `M1`.

### 2.9 Kinship removal is purely descriptive and omitted in Panel A — **should fix**
Because relatedness in HGDP/SGDP Suruí and Karitiana is a central published criticism (Castro e Silva et al. 2021), kinship should also be checked in Panel A (whose Amazonians are a subset of Panel B) and elevated from descriptive to a formal support check in Panel B.

---

## 3. Ambiguities for an independent programmer

An independent programmer given only this plan and the raw files could reasonably compute different results on the following points:

1. **Exact `.ind` column-3 group labels for Panel A and Panel B — must fix** (unless already enumerated in `replication/FORMAT.md`). Only a handful of labels (`Mexico_Zapotec`, `Nahua`, `Mixtec_1`, `Mixtec_2`, `ONG`, `JAR`, `Mbuti`, `MbutiPygmy`, `Chimp.REF`, `Tianyuan.AG.BY.AA`) are quoted. In AADR `.ind` files, group labels frequently carry `.DG`/`.SG` suffixes (e.g., `Surui.DG` vs `Surui`). It is also unstated whether `Chimp.REF` and `Tianyuan.AG.BY.AA` are matched on column 1 (Genetic ID) or column 3 (group label), and whether `ONG`/`JAR` require a `Pass` assessment.
2. **Multiple-testing correction method for `Z*` in Section N — must fix.** "The one-sided 5% level corrected for the number of tests in a family" does not specify **Bonferroni** ($\Phi^{-1}(1 - 0.05/m)$), **Šidák**, or **Benjamini-Hochberg FDR**. It is also ambiguous whether non-Pass `EARLY` versions count in $m$, and the line "That makes 60 ancient sets" immediately follows `VER.AG`/`VER.SG` even though $23 + 10 + 2 + 25 = 60$ excludes `VER.AG`/`VER.SG`.
3. **Step 1 screening execution order and nested-set fallback — must fix.**
   - Is `U = Amazon` unscreened when screening `Mixe`/`Pima`/`Other Americans`, or is `Amazon` screened first?
   - If `A.Surui` ($N=2$) drops to 1 person and reverts to unscreened members, does `A.Amazon` (still $N=4$) drop that admixed individual or keep them? Does the `< 2` fallback apply to `B.Pima.heldout`/`B.Amazon.heldout`? Does it apply to `A.MesoOther` as a pooled set of 6 or to each constituent label (`Mixtec_1`, etc.)?
4. **Exact `.anno` column names, deduplication ties, and World panel W rules — should fix.**
   - Exact `.anno` column headers are not named for `date mean`, `data type` (`Shotgun.diploid`/`Shotgun`), `political entity`, or `coordinates` (nor how missing `".."` values are handled).
   - No tie-breaker is specified when two versions of the same person share the exact same highest SNP count (or when `Individual ID` is `".."`).
   - For World panel W, "the panel-A version if there is one" is undefined for groups not in the Panel A table (presumably any `S_*` or `B_*` ending in `.DG`, with a tie-breaker if both exist).
   - Substring exclusions `-o` and `_o` (case-sensitive) could accidentally drop valid labels containing `_o` mid-word (e.g., `_old`, `_other`) unless suffix/token matching is clarified.
5. **Coastline 5 km discretization — should fix.** Sampling "points no more than 5 km apart" could be implemented by linear interpolation in lat/lon vs spherical great-circle interpolation, or exact point-to-segment distance, and on mainland-only vs all coastline polygons—potentially flipping borderline sites near 75 km and breaking exact `sets.tsv` replication.
6. **Common masks in T3 — minor.** It is not stated whether the three $f_4$ statistics in T3 use a shared SNP mask or each statistic's own 4-set mask (the latter is implied since no common mask is named, but should be explicit).
7. **KING-robust kinship and detectability RNG details — minor** (excluded from replication, but still underspecified): KING-robust has two standard estimators (within-family vs between-family / Eq. 9 vs Eq. 11 of Manichaikul et al. 2010), an unspecified SNP filter, ambiguity over whether pairs are computed within each of the 3 groups or across all 3 combined, and ambiguity over whether "Starting from all donors" means pre- or post-Step-1 screening. Detectability does not specify whether `default_rng(31)` is re-seeded per pair or the loop/SNP draw order.

---

## 4. Important missing checks (ordered by importance, all feasible in AADR v66.p1)

1. **Baseline composition & sensitivity in Section N (`BASE_t` without `CARIB`, and capture/UDG stratification) — must fix.**
   Tabulate `BASE_AG`, `BASE_SG`, and every `REGION.*`/`CELL.*` by region, capture reagent (1240K vs Twist), and UDG status. Re-run `M1`/`M3`/`MF` using `NAM_WEST + NAM_EAST + MESO` (excluding `CARIB`) and `MESO` alone, and add a **T2b check** comparing 1240K vs Twist (and UDG vs non-UDG) on matched ancient samples in AADR v66.p1.
2. **Karitiana ascertainment check (`Surui` vs `Karitiana` across SNP classes and African-ascertained SNPs) — should fix.**
   Compute `f4(Mbuti, Papuan; Surui, Karitiana)` and `f4(Mbuti, Papuan; Reference, Surui)` on `all`, `yri`, and **San-polymorphic** SNPs ($0.05 < p_{\text{San}} < 0.95$ using `Ju_hoan_North` in AADR). If 1240K Karitiana ascertainment is inflating `P_A`/`P_B`, `Karitiana` will exceed `Surui` specifically on `all` SNPs and shrink on `yri`/San-polymorphic SNPs.
3. **Reference-population symmetry check — should fix.**
   Compute `f4(Mbuti, Papuan; A.Mixe, R)` across `R` in `{A.Pima, A.MesoOther, A.Mayan}` (and `B.Pima` vs `B.Mayan`). Because Moreno-Mayar et al. (2018) found that Mixe carries a deeply divergent basal Native American component ("UPopA"), testing whether `Mixe` behaves differently from other Mesoamerican/North American references directly checks the protocol's stated "Reference choice" weakness.
4. **Leave-one-site-out / leave-one-individual-out in Section N — should fix.**
   For any ancient pool (`CELL.*`, `REGION.*`, `ANC.SA`) that "stands out" or "falls short," run leave-one-individual-out and leave-one-site-out checks to verify the result is not driven by a single contaminated genome, a single family of relatives, or one site (e.g., Sumidouro5 driving `EAST_SA_EARLY`).
5. **Archaic (Denisovan / Neanderthal) control for `L2` and `P` — should fix.**
   Compute `f4(Mbuti, Denisova; Reference, Amazon)` and `f4(Mbuti, Vindija/Altai_Neanderthal; Reference, Amazon)` (all present in AADR v66.p1). Papuans carry ~3–5% Denisovan ancestry whereas Onge carry very little; this checks whether any `L2` difference between Papuan and Onge is confounded by archaic ancestry differences.
6. **Transversion check for Tianyuan (`L1_tv`, `L4_tv`) plus ancient Eurasian controls — should fix.**
   Run `L1` and `L4` on transversions, and compute `f4(Mbuti, X; Reference, Amazon)` for `Ust'-Ishim` (ancient reference-bias/basal-Eurasian control) and ancient Southeast Asian `Hoabinhian` genomes (Onge-related) in AADR.
7. **Symmetric `T1` check using NYGC outgroups (`B.Mbuti`, `B.Papuan`) — minor.**
   `T1` currently tests `f4(A.Mbuti, A.Papuan; DUP.SGDP, DUP.NYGC)` where P1, P2, and P3 are all SGDP. Also running it with `B.Mbuti` and `B.Papuan` checks whether pipeline-specific bias changes sign when the reference panels switch from SGDP to NYGC.
8. **All remaining present-day shotgun Native American groups in AADR — minor.**
   AADR v66.p1 also includes present-day shotgun groups like HGDP `Colombian` (Panel B) and SGDP `Chane` (Panel A, Amazonian/Chaco-adjacent) that are omitted from the "Other Americans" list. Including all passing shotgun American groups (analogous to World Panel W) gives a fuller geographic picture at negligible cost.

---

## 5. Audit of the literature summary

Overall, the literature summary is accurate and commendably transparent about which papers were unread. A few corrections and material omissions:

1. **Moreno-Mayar et al. 2018 (*Science* 362:eaav2621) — important omission affecting the protocol's primary Reference (high confidence) — should fix.**
   The summary correctly notes Sumidouro5, but omits a major finding of that same paper: **Mixe** carries ~15–30% ancestry from an unsampled basal Native American lineage ("UPopA") that diverged before the main North/South American split. Because `A.Mixe` is the protocol's primary reference in `P_A`, this directly bears on reference-choice caveats.
2. **Skoglund et al. 2015 (*Nature* 525:104) — scale conflation and missing Onge context (high confidence on the scale difference; moderate confidence on exact Table 1 decimal digits) — should fix.**
   - The summary cites `D = 0.0211` (whole-genome shotgun sequencing) alongside `D = 0.0072–0.0099` (Human Origins array) without noting that `D` is strongly compressed on ascertained SNP arrays (~2–3× smaller than on WGS for the same biological effect) and that `0.0072` is not the `(Yoruba, Papuan; Mixe, Surui)` quartet. This leads directly to the flawed Anchor benchmark in "What would count."
   - Worth noting for Question 3: Skoglund et al. 2015 reported that the signal was shared roughly equally with **Onge**, **Papuans**, and **Australians** (not specifically Papuan-tilted), and Yang et al. 2017 similarly found Tianyuan statistically indistinguishable from Onge/Papuan (`L4 ≈ 0`).
3. **Campelo dos Santos et al. 2022 (*Proc. R. Soc. B* 289:20221078) — minor omission (moderate-to-high confidence) — minor.**
   In addition to Panama and Sumidouro5, this paper reported the Australasian signal in ancient individuals from **Uruguay** (Atlantic coast), which is directly relevant to `REGION.EAST_SA` here.
4. **Raghavan et al. 2015, Posth et al. 2018, Castro e Silva et al. 2021 — accurate (high confidence for Raghavan/Posth; moderate-to-high for Castro e Silva's exact relative-removal subset).**
5. **2026 *Nature* study (`doi:10.1038/s41586-026-10406-w`) — cannot verify (low confidence).** This falls outside my verifiable literature coverage, so I cannot confirm the DOI or its reported counts.

---

## Top three changes to make first

1. **Fix Section N's ancient baseline, geography, and data-type consistency:** Remove `CARIB` from `BASE_t` (`ANC.NCA`); add longitude bounds to exclude Rapa Nui (`Chile`) and Hawaii (`USA`) from `ANDES_COAST` and `NAM_WEST`; stratify `.AG` by capture reagent (1240K vs Twist) using `.anno` metadata and validate all ancient tests on transversions; and apply type-matching, transversion checks, contamination checks, and the `T2` unreliability gate to `K1`/`K3`.
2. **Fix the T3 admixture algebra, Step 1 screening, and African-admixture check:** Correct the repeated-population finite-sample bias in the denominator of $\alpha$ (by bias-correcting or using a disjoint European population in P2), replace the permissive 50% and two-sided T3 rule with a directional residual check, add a pooled African check to T3, screen `Amazon` (`U`) iteratively before screening `Reference`, and stop the `< 2` fallback from re-inserting confirmed admixed donors.
3. **Close the Headline, decision-rule, and replication specification gaps:** Define the Headline for inconclusive `P_A` ($2 \le Z < 3$), integrate `T1`, `P_B.heldout`, and kinship pruning into the Headline verdict, specify the exact multiple-testing formula for `Z*` (excluding non-Pass versions from $m$) and thresholds for `L1`/`L4`, and list exact `.ind`/`.anno` matching rules and Step 1 edge-case rules so the independent replication cannot diverge.
