<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T06:34:44.531700+00:00", "input_tokens": 3273, "output_tokens": 53518, "cost_usd_list_price": 0.8126} -->

Here is a critical review of the pre-registration across the five requested areas, with severity ratings (`must fix`, `should fix`, `minor`) and the three highest-priority changes at the end.

---

### 1. Flaws that could produce a false positive or a false negative

* **Greenland Norse (and any real colony/group of strangers) will populate each other's neighbour pools and mask themselves — while creating false positives in their neighbours (`must fix`).**
  * In AADR, there are roughly 15–20+ medieval Greenland Norse `.SG` genomes within ~400 km and ~300 years of one another. Because Step B selects the 20 nearest same-side, same-data-type neighbours within 1,500 km and 1,500 years, Greenland Norse will make up most or all of each other's pools `P`, driving `E_French ≈ 0` and causing the scan to fail its own headline positive-control check.
  * Conversely, any Greenland Inuit/Thule `.SG` individual whose 20 nearest neighbours include Greenland Norse gets an artificially European-shifted pool `P`, causing innocent Inuit genomes to fire as false-positive `E_Han` hits (since Inuit share more alleles with Han than Europeans do).
  * The exact same mechanism hides any genuine cluster, family, or settlement of 10–20+ transoceanic migrants buried at the same site or region.

* **"Centred $f_4$" violates the treeness null ($f_4 = 0$) and attenuates true signals because GRCh37 is admixed (`must fix`).**
  * Because allele 1 in AADR is the GRCh37 reference allele (not randomly polarized), the mean reference allele frequency of population $k$ is $\bar{p}_k = 1 - H(G, P_k)$, where $H(G, P_k)$ is the mean pairwise mismatch rate between population $P_k$ and the reference genome $G$. Therefore, the subtracted centring term is:
    $$(\bar{p}_1 - \bar{p}_2)(\bar{p}_3 - \bar{p}_4) = \bigl[H(G, P_2) - H(G, P_1)\bigr]\bigl[H(G, P_4) - H(G, P_3)\bigr].$$
  * Because GRCh37 is an admixed European/African-American mosaic (~57% European, ~37% West African), it is closer to Yoruba than to Mbuti *and* closer to Europeans than to Native Americans or East Asians. Consequently:
    1. **False bias under the null:** Even when true $f_4 = 0$ — e.g., `E_Yoruba = f4(Mbuti, Yoruba; NA, Eur)` or `f4(Mbuti, Yoruba; EastAsian, Eur)` — both factors are non-zero, so centred $f_4$ is systematically biased away from zero (for example, biased *positive* on `E_Yoruba` if an American individual's pool contains European genomes).
    2. **Signal attenuation:** For `E_French = f4(Mbuti, French; NA, Eur)`, both factors are strongly negative, so $(\bar{p}_1-\bar{p}_2)(\bar{p}_3-\bar{p}_4) > 0$, subtracting a substantial fraction of the true signal.
    3. **Does not remove aDNA bias:** Reference bias in aDNA occurs at heterozygous sites (proportional to $2p(1-p)$), and post-mortem C→T/G→A damage changes sign depending on whether C or T is the reference allele, so its mean shift across SNPs is near zero and centring does not remove it. Since Step B already matches `P` and `X` by data type, standard uncentred $f_4$ is cleaner and unbiased under treeness.

* **Step A on the American side is completely blind to Sub-Saharan Africans (even 100% African) and misses most admixed Europeans/East Asians (`must fix`).**
  * For a 100% West African (`Yoruba`) buried in the Americas with no Step-B pool, both `D1 = f4(Mbuti, X; Han, NA)` and `D2 = f4(Mbuti, X; MA1, NA)` have `(Mbuti, Yoruba)` on one side and two Out-of-Africa groups on the other — so **both `D1 ≈ 0` and `D2 ≈ 0`**. Step A literally cannot detect a 100% African individual.
  * For a 50% European + 50% Native American individual, `D1` is strongly *positive* (both Europeans and Native Americans share ANE with `NA` relative to `Han`), and `D2` will usually remain *positive* as well because the Native American bottleneck/East Asian drift shared between `X` and `NA` (`f4(Mbuti, NA; MA1, NA)`) outweighs European–`MA1` affinity (`|f4(Mbuti, Eur; MA1, NA)|`).
  * Furthermore, in `D2`, `X` (ancient) and `MA1.SG` (ancient, ~1×, non-UDG) sit on opposite sides of the semicolon while `Mbuti` and `NA` are modern diploid. Shared C→T/G→A damage and aDNA artefacts correlate $p_X$ and $p_{\text{MA1}}$ positively, systematically biasing `D2` *negative* for non-UDG ancient genomes.

* **Using single-genome, non-UDG `MA1.SG` and an unconstrained European-dominated OLS fit in `S` introduces false positives and false negatives (`must fix`).**
  * **UDG mismatch artefact:** Within `.AG` and `.SG`, AADR mixes UDG-full, UDG-half, and non-UDG libraries. If `X` is UDG-treated and its neighbours `P` are predominantly non-UDG, `P` shares damage with non-UDG `MA1.SG`, biasing `B_MA1` negative and therefore biasing `S = A − u_MA1·B_MA1 − …` *positive* (false positive; the reverse causes false negatives).
  * **Coverage loss & attenuation bias:** `MA1.SG` is a single ~1× pseudo-haploid genome (~70% of autosomal 1240k SNPs). Intersecting with `MA1.SG` discards ~30% of SNPs for every Old World test. Worse, single-genome sampling error in `B_MA1` (plus finite-SNP noise in `B_R`) causes errors-in-variables attenuation in OLS, pulling `u_MA1` toward zero so ANE/Steppe-rich outliers leak through as positive `S`.
  * **Unconstrained weights & Out-of-Africa drift:** Because >70% of AADR ancient genomes are West Eurasian, OLS fits `u_R` primarily to European variation. Without constraining the Out-of-Africa reference weights to sum to 1 ($\sum_{R \in \text{OOA}} u_R = 1$), differences in Out-of-Africa drift between `P` and `X` do not cancel identically. In particular, for African outliers (especially non-West-African lineages like San/Mota/Hadza vs Eurasian-admixed Africans, where `B_Yoruba` does not track OOA drift), large residual OOA drift can leak into `S`.
  * **East Asian substructure:** Native Americans descend from Ancient Northeast Asian / Beringian lineages, whereas `Han` carries Southern East Asian ancestry and `NA` includes `Karitiana`/`Surui` (~1–2% Australasian "Population Y" ancestry). Weights `u_R` dominated by West Eurasia may miscalibrate East Asian/Siberian/Oceanian residuals, creating systematic regional false positives or negatives.

* **Geography (`Side`) rules misclassify Rapa Nui, the Aleutians, Eastern Greenland, and possibly overseas territories (`must fix`).**
  * **Rapa Nui (Easter Island):** Political entity in AADR is `Chile` (Americas list), latitude −27.1°, longitude −109.3°. Because −109.3° is *not* below −130°, Rapa Nui falls on the **American side**. Ancient Rapa Nui Polynesians will trigger massive `E_Han`/`E_Papuan` (or Step-A `D1`) hits.
  * **Aleutian Islands / Western Alaska:** Extend west of −170° (and across 180°). Ancient Aleuts in AADR with longitude < −170° fall into **elsewhere**, where their Native American ancestry will trigger massive false-positive `S`/`D1`+`D2` hits.
  * **Eastern Greenland:** Extends east of −30° (to ~−12°), putting any Northeast Greenland sample into **elsewhere**.
  * **Missing coordinates:** Because the rule checks `longitude, if given`, any genome from a US Pacific territory (Hawaii, Guam, American Samoa) with missing coordinates lands on the **American side**. Similarly, any Caribbean or South American sample whose political entity is `France`/`Netherlands`/`UK` (e.g. Guadeloupe, Martinique, French Guiana) lands in **elsewhere**.

* **Exclusion of `.DG` ancient genomes from Step B (`must fix`).**
  * In AADR, many of the highest-coverage, highest-value ancient genomes (e.g., Anzick-1, Spirit Cave, Kennewick, Lagoa Santa, Saqqaq, Yana, Ust-Ishim, Loschbour, Mota, and many modern high-coverage releases) carry the `.DG` suffix (diploid shotgun). The plan's parsing rule (`.AG`, `.SG`, `.TW` only) dumps all `.DG` ancient genomes into Step A (and also risks misclassifying merged `.AG.SG` or `_d`-style IDs).

* **Post-contact colonial individuals can pass the `date mean >= 500 BP` filter (`must fix`).**
  * In AADR, BP is years before 1950 CE, so 500 BP = 1450 CE. A contextual date range of 1200–1700 CE (mean = 500 BP) or a wide radiocarbon uncertainty easily includes post-1492 colonial admixed individuals. Furthermore, marine reservoir effects in coastal Americas/Greenland/Polynesia can make post-contact burials appear 200–600 years too old. Because there is no `Date` exclusion class, an unlabeled colonial Mestizo with mean date 500 BP would be classified as `Standing`.

* **Contamination screening misses nuclear contamination in females and 3–8% contamination in low-coverage males (`must fix`).**
  * Modern European lab/excavator DNA contaminating an ancient American bone is the single most likely source of a false-positive `Standing` hit on `E_French`.
  * X-chromosome contamination (ANGSD) cannot be computed for **females** (half the dataset), and mtDNA contamination (`contamMix`) frequently appears clean (or is missing) even when nuclear contamination is 5–15% due to high endogenous mtDNA-to-nuclear ratios.
  * Requiring the **lower bound** of X-contamination > 0.02 or **upper bound** of mtDNA match < 0.95 fails to flag low-coverage samples with wide CIs (e.g., 5% contamination with CI `[0.01, 0.09]`).

* **Present-day `NA` reference contains European/African admixture (`should fix`).**
  * In HGDP/SGDP/HO, present-day `Pima` and `Quechua` (and some `Mixe`/`Piapoco`) include individuals with ~5–15% European (and minor African) admixture. This distorts `u_Sardinian` in Step B and directly weakens `D2` (and biases `D1`) in Step A. Meanwhile, `Karitiana` and `Surui` carry ~1–2% Australasian ("Population Y") ancestry, which affects `Papuan` comparisons.
  * Likewise, the secondary `NA` reference (`all capture-type people on the American side with at least 500,000 SNPs`) will include Arctic/Inuit genomes (with Siberian ancestry) and any misdated/European/Rapa Nui capture genomes on the American side, and shares capture/non-UDG artefacts if `P` and `X` differ in UDG status.

* **"The centres" pool subtraction and `f4(Mbuti, O; P, centre)` invite population-structure and batch-effect false positives (`should fix`).**
  * Removing all `Peru_…` and `Bolivia_…` (<4,200 BP) from `ANDES`'s pool leaves older Holocene Andean hunter-gatherers and neighbouring Amazonian/Brazilian/Chilean populations (which differ in Population-Y and deep South American ancestry). Similarly, removing `Egypt_…` leaves Levant/Anatolia/Sudan; removing `CHINA_EARLY` leaves Steppe/Amur/Southern China. Because pooled-centre SEs are very small, normal intra-continental population structure easily produces `Z ≥ 3.5` on `E_R`, `S`, or `f4(Mbuti, O; P, centre)`.
  * In `f4(Mbuti, O; P, centre)`, `O` pools all data types/UDG batches of an Old World centre. If `centre` (e.g., a single study like `Honduras_Copan_Classic_Maya`) differs in UDG/capture chemistry from its neighbour pool `P`, shared ancient-DNA artefacts between `centre` and `O` can produce a spurious signal.
  * The Mesoamerica labels (`Mexico_LateClassic`, `Honduras_Copan_Classic_Maya`) appear to omit major published Classic Maya/Mesoamerican sets in AADR (e.g., Belize, Guatemala, Teotihuacan, Chichen Itza), while prefix matching `Peru_…` and `Egypt_…` sweeps in published `_o` outliers and non-civilization sites.

* **Power simulation ("What could have been missed") significantly overestimates detection power (`should fix`).**
  * Replacing independent SNPs with fraction `f` of donor calls puts ~`f` foreign ancestry into *every* 5 cM block, eliminating block-to-block admixture variance. A real 5–10% admixed person (e.g. 3–5 generations post-contact) carries foreign ancestry in a few contiguous 10–40 cM tracts, leaving ~90% of blocks at zero — producing a much larger block-jackknife SE and substantially lower Z-scores.
  * The simulation also: (1) skips the two robustness checks (at 5–10% admixture near `Z*`, transversions alone have ~2.2× larger SE and will drop a meaningful fraction of real hits); (2) omits Step A; (3) tests only `E_French` on the American side, ignoring East Asian (`E_Han`, which has much weaker contrast against Native Americans since Native Americans are ~2/3 East Asian) and Oceanian/African donors; and (4) draws "random ancient American" donors from the American side without excluding Greenland Norse/Arctic/Rapa Nui, risking injecting European DNA as "Native American" for `.SG` hosts.

---

### 2. Decision rules that are unfair, miscalibrated, or do not test what they claim

* **`Neighbourhood` class disqualifies genuine small colonies or families of strangers (`must fix`).**
  * Classifying a hit as `Neighbourhood` (and thus *not* `Standing`) whenever "three or more of its 20 neighbours are also hits" treats a genuine boatload, family, or small settlement of 4+ transoceanic migrants at one site as a non-discovery — directly contradicting the lost-seafaring-civilization / transoceanic-contact question being tested.
  * The clause "or it is a hit of its own pool's kind across a whole site" is also vague and subjective.

* **Missing `Date` class and overly permissive `Known` (`-o…`) class (`should fix`).**
  * Without a `Date` class for genomes whose 95% calibrated radiocarbon interval or contextual range crosses 1492 CE (or suffers severe marine reservoir uncertainty), post-contact individuals default to `Standing`.
  * Automatically assigning any outlier suffix (`_o` in AADR, not `-o`) to `Known` risks dismissing a genuine discovery if the original publication merely flagged the genome as an unexplained PCA outlier without recognizing transoceanic ancestry. `Known` should require that the publication actually documented the *cross-oceanic* (or known Arctic/Siberian) affinity.

* **Second-reference robustness check has no definition for Step A or `f4(Mbuti, O; P, centre)` and uses potentially weak/admixed references (`should fix`).**
  * No second reference is specified for `D1`/`D2` (especially what replaces `MA1`) or for Old World centres `O` in `f4(Mbuti, O; P, centre)`, making the robustness rule uncomputable for those tests.
  * Present-day `Australian` in AADR (from SGDP) consists of only ~2 individuals (and should be verified for absence of minor European admixture, which could let European signals pass `E_Australian`). `Sardinian` has much higher Basal Eurasian and lower Steppe/ANE than `French`, which is good for guarding against ANE-driven false positives, but its attenuation ratio on genuine Northern/Eastern European or Steppe-rich visitors (like Norse) should be verified in the power simulation.

* **Transversion check has no minimum significance floor (`minor`).**
  * Requiring only `estimate_tv >= 0.5 * estimate_all` (with no Z floor) allows ~16% of pure transition-damage artefacts sitting at `Z_all ≈ 4.5` to pass by chance (since `SE_tv ≈ 2.24 * SE_all`, so `0.5 * 4.5 / 2.24 ≈ 1.0 SD`). Pairing the ratio rule with a modest floor (e.g., `Z_tv >= 2.0`) and verifying its power impact in simulations is cleaner.

* **Separate 5% Bonferroni budgets for Step A and Step B (`minor`).**
  * Controlling Step B at 5% and Step A separately at 5% yields a combined scan family-wise error rate up to ~10% (and centre tests use an uncalibrated `Z ≥ 3.5`). Pooling Step A and Step B into a single Bonferroni denominator is trivial and cleaner. Also note that `S`'s jackknife treats the data-fitted `u_R` as fixed constants (ignoring estimation variance in `u_R`, though with ~10,000 genomes this is likely small if collinearity is controlled).

---

### 3. Ambiguities where an independent programmer could compute something different

* **Distance tie-breaking for the 20 nearest neighbours (`must fix`).**
  * Thousands of AADR genomes come from the same site with identical coordinates and identical contextual `date mean`, yielding exact `distance = 0` ties. Without an explicit deterministic tie-break rule (e.g., sort by `(distance, Genetic ID)`), two independent implementations will pick different pools and fail the exact-pool replication criterion.
* **Leave-one-block-out centring and block definition in the 5 cM jackknife (`must fix`).**
  * If centring is retained, the plan does not specify whether leave-block-$j$-out estimates recompute $\bar{X}_{(-j)}$ and $\bar{Y}_{(-j)}$ without block $j$ or subtract the global $\bar{X}\bar{Y}$.
  * It also does not specify whether 5 cM bins are fixed at `floor(gpos_M / 0.05)` per chromosome (1–22) or anchored to the first SNP per chromosome, nor the exact weighting formula (standard SNP-count-weighted Busing/ADMIXTOOLS delete-block jackknife).
* **SNP intersection for OLS vs SNP-by-SNP `S`, and OLS trimming mechanics (`must fix`).**
  * Are `A` and each `B_R` in the OLS fit computed on their own pairwise-valid SNP sets, or on the common intersection of all 9 populations `{Mbuti, NA, MA1, Han, Sardinian, Papuan, Yoruba, P, X}`? Only on the common intersection does `centred(S)` equal `centred(A) − Σ u_R·centred(B_R)`.
  * For "three rounds, each dropping people whose residual is more than 4 robust standard deviations from zero": is that 3 fits (2 drops) or 4 fits (3 drops)? Are dropped people excluded permanently across rounds or re-evaluated each round? And is "median absolute residual" `median(|r|)` around zero or standard `median(|r - median(r)|)`?
* **Re-fitting `u_R` for the second-reference check and for Old World centres (`must fix`).**
  * When replacing `NA` with `NA_ancient` in `S`, does the programmer reuse `u_R` from present-day `NA` or re-fit `u_R` to `NA_ancient`? And for Old World centres, are the individual-level `u_R` weights reused?
* **Population allele frequency definition and `NA` weighting (`should fix`).**
  * For `NA` (6 populations together), are all individuals pooled with equal weight per person (so larger panels like Karitiana/Pima dominate), or are the 6 population means averaged equally?
  * For pools `P`, references, and centres: is a SNP kept if only 1 person in the set has non-missing data? Confirm genotype scaling (`{0, 0.5, 1}` from EIGENSTRAT `{0, 1, 2}`).
* **Exact AADR `.anno` columns, reference group labels, and centre label matching (`should fix`).**
  * Name the exact `.anno` columns used for `Individual ID` (`Master ID`?), `1240k SNP count` (autosomal 1240k easystats column?), `date mean`, `ASSESSMENT`, and contamination bounds.
  * Exact match vs prefix for `Mexico_LateClassic`, `Honduras_Copan_Classic_Maya`, `Syria_EMBA`; whether `Egypt_…`, `Peru_…`, etc. include `_o`/`_lc` labels; case sensitivity for `CHINA_EARLY`; and what happens if subtracting centre members leaves a centre with an empty (or tiny) pool `P`.
  * Exact AADR group labels for every present-day reference (e.g., `Papuan` vs `PapuanHighlands`/`PapuanSepik`, `Han` vs `Han_NChina`) and the `European country in a fixed list` used in the simulation.
* **Great-circle radius and missing coordinates/dates (`minor`).**
  * Specify Earth radius (e.g., Haversine with $R = 6371.0$ km) to prevent boundary disagreements near 1,500 km, and explicitly state that people with missing coordinates or date mean (`..`) cannot enter pools and fall to Step A.
  * Confirm whether Step B's Bonferroni denominator counts only people *with* a Step-B pool (consistent with Step A counting those without).

---

### 4. Important missing checks (ordered by importance, feasible with AADR v66)

1. **Same-site / same-group-excluded Step-B pools (and a global-baseline check) (`must fix`).**
   * Re-run Step B (or define the primary pool) excluding individuals with the same `Group ID` or exact same site/coordinates (e.g., requiring neighbours outside the same locality or outside 10–50 km where available). This prevents Greenland Norse and genuine migrant settlements from hiding in each other's pools, and also prevents Greenland Norse from contaminating Inuit pools (using a robust/trimmed or median neighbour baseline, or excluding obvious Step-A outliers from pools `P` before running Step B, prevents the reverse contamination).
2. **Replace Step A on the American side with a global unadmixed ancient-American baseline (`must fix`).**
   * For American-side individuals without a local Step-B pool, instead of `D1`/`D2`, compute `E_R = f4(Mbuti, R; Ancient_NA_clean, X)` for `R ∈ {French, Yoruba, Han, Papuan}` using a clean, geographically broad, unadmixed pre-contact ancient Native American baseline (excluding Arctic/Greenland/Rapa Nui). This immediately catches Africans, Europeans, Oceanians, and admixed individuals with no local pool.
3. **Uniparental markers (mtDNA / Y-chr haplogroups), sex-stratified contamination audit, and radiocarbon/date-range audit for every hit (`must fix`).**
   * All are directly in AADR `.anno`. For every hit, report: (a) mtDNA and Y-chr haplogroups (distinguishing Native American A2/B2/C1/D1/X2a/Q-M3 vs Old World haplogroups); (b) point estimates and CIs of X- and mtDNA-contamination plus `Sex` (flagging females with low-level European signals as high contamination risk); and (c) full date range / `date mean − 2·SD` and coastal/marine-diet context to catch post-1492 samples.
4. **Uncentred $f_4$ vs centred $f_4$, UDG-treatment matching, and OLS/regional null diagnostics (`must fix`).**
   * Compare uncentred vs centred $f_4$ directly (especially on Greenland Norse and African/Eurasian controls) to verify the GRCh37 centring distortion.
   * For every hit, check `.anno` UDG/library treatment against its pool `P`; if mismatched, recompute restricting `P` to the same UDG category.
   * Print the fitted `u_R` weights (and their sum) and inspect QQ-plots / regional means and SDs of `Z(S)` across Europe, Near East, Africa, South Asia, East Asia, Siberia, and Oceania to verify calibration and catch attenuation or African OOA leakage.
5. **Reference purity check before running (`should fix`).**
   * Screen every present-day individual in `NA` (and `Australian`, `Mandenka`) with `f4(Mbuti, French/Yoruba; Ancient_NA_clean, indiv)` and drop admixed individuals from `NA`. Also test replacing single-genome `MA1.SG` with a multi-individual ANE pool (e.g., `MA1.SG + AG3.SG + West_Siberia_N` or `Yana_UP.SG`) to recover the ~30% lost SNPs and reduce attenuation/damage bias.
6. **Tract-level power simulations across all four ancestries, Step A, and robustness rules (`should fix`).**
   * Simulate 5–25% admixture by replacing contiguous 10–30 cM blocks (not independent SNPs), apply the full hit + transversion + second-reference pipeline, include Step A, stratify by region, and simulate European, East Asian, African, and Oceanian donors on the American side.

---

### 5. Points in the literature summary that appear wrong or incomplete

* **`"no Indus city has any"` — wrong (high confidence, ~95% on the literature; ~70% on whether it passes this plan's filter).**
  * Rakhigarhi (`I6113`, Shinde et al. 2019, *Cell*) is one of the largest Mature Harappan (Indus Valley Civilization) cities and has a published ancient genome in AADR (~130k–140k 1240k SNPs, plus 11 "Indus Periphery" genomes from Shahr-i-Sokhta and Gonur Depe in Narasimhan et al. 2019, *Science*). If `I6113` fails AADR's `Pass` or 100k-SNP filter in v66, the text should say none passes the quality filter rather than that no Indus city has any genome. (`minor`)
* **`"Egypt has two usable genomes"` — likely slightly outdated/understated (moderate confidence, ~70%).**
  * Schuenemann et al. 2017 (*Nature Communications*) published three Abusir el-Meleq nuclear genomes (`JK2911`, `JK2888`, `JK2134`, though one may fall near/below 100k autosomal SNPs or `Pass` in AADR), and Morez Jacobs et al. 2025 (*Nature*) published an Old Kingdom Egyptian genome from Nuwayrat (depending on AADR v66's cutoff date). This count should be verified from the `.anno` file after locking rather than stated as a hard fact. (`minor`)
* **Major omissions from "Known cases" of pre-1492 cross-oceanic/intercontinental ancestry (high confidence, ~95%).**
  * **Pre-1492 Polynesia–Americas contact:** Ioannidis et al. 2020 (*Nature*) and **Moreno-Mayar et al. 2024 (*Nature*)** (ancient Rapa Nui genomes) demonstrated pre-1492 Native American ancestry in Eastern Polynesia. This is directly relevant to the Pacific side of the question and directly interacts with Rapa Nui's misclassification. (`should fix`)
  * **Back-migration from the Americas into Northeast Asia:** Beyond ancient Siberians ancestral to Native Americans (like Kolyma), **Sikora et al. 2019 (*Nature*)** and **Wang et al. 2023 (*Current Biology*)** documented reverse gene flow from Native Americans back into Kamchatka and Chukotka over the past ~5,000 years. (`minor`)
  * **Australasian ("Population Y") signal in South America:** Skoglund et al. 2015 (*Nature*), Moreno-Mayar et al. 2018 (*Science*), and Castro e Silva et al. 2021 (*PNAS*) documented a small (~1–2%) Papuan/Australasian-related signal in ancient (e.g., Lagoa Santa) and present-day South Americans (including `Karitiana` and `Surui`, which are inside the plan's `NA` reference). (`should fix`)
* **`"Centring removes a uniform lean toward the reference genome, not all of it"` — incomplete/misleading (high confidence, >99% mathematically).**
  * As shown in Section 1, centring does not just leave some reference bias behind; it actively injects a non-zero demographic bias whenever the admixed GRCh37 reference genome shares drift with both sides of the $f_4$ statistic. (`must fix`)

---

### Top three changes to make first

1. **Fix pool self-masking, the `Neighbourhood` rule, and Step A on the American side:** Exclude same-site / same-group-label individuals (and obvious Step-A outliers) when building Step-B pools so Greenland Norse and real migrant groups cannot mask themselves or poison their neighbours' pools; narrow the `Neighbourhood` class so a small colony/family of strangers is not discarded; and replace Step A's American-side `D1`/`D2` with `f4(Mbuti, R; Ancient_NA_clean, X)` so Africans and admixed individuals without local pools can be detected.
2. **Drop "centred $f_4$" in favour of standard uncentred $f_4$ and clean up the `S` controls and references:** Use standard $f_4$ (paired with UDG-matched sensitivity checks and transversions), purge European/African-admixed individuals from `NA`, replace single-genome non-UDG `MA1.SG` with a multi-individual ANE reference, and constrain $\sum_{R \in \text{OOA}} u_R = 1$ so Out-of-Africa drift cancels cleanly across continents.
3. **Close the dataset/metadata loopholes and replication ambiguities:** Fix `Side` boundaries (Rapa Nui, Aleutians, Eastern Greenland, missing coordinates), include `.DG` ancient genomes in Step B, add a `Date` uncertainty class (post-1492 CIs/marine reservoir) and stricter contamination/uniparental checks (especially for females and point estimates >2%), and write down exact tie-breaking, jackknife, SNP-intersection, and second-reference rules so independent replication can actually pass.
