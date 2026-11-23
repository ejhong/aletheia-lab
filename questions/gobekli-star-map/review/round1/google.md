<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T20:56:57.620276+00:00", "input_tokens": 3476, "output_tokens": 29518, "cost_usd_list_price": 0.4532} -->

### 1. Flaws That Could Produce a False Positive or False Negative

1. **Item 3's probability formula (`2(P+1)/19,958,400`) is mathematically broken whenever `k_i > 0` for more than one figure — *must fix***
   - `P+1 = ∏(1 + k_i)` counts configurations *with replacement* (a subset of `12⁸`), not without replacement (`19,958,400`). Sweatman & Tsikritsis (S&T) only avoided a contradiction because 7 of their 8 factors were `1`. With blind judges, `P+1` will easily exceed `19,958,400` (e.g., if the claimed symbol is ranked 9th on each figure, `P+1 = 9⁸ = 43,046,721`, giving `2(P+1)/19,958,400 = 4.31`, which is not a probability).
   - Even against `12⁸`, `∏(1 + k_i)` only counts configurations that are simultaneously better at *all 8 positions* (Pareto dominance), not configurations with a better overall fit. Under pure random rankings (`Uniform{1..12}`), the median of `2(P+1)/12⁸` is roughly `0.0028` (~1 in 350), and if mean ranks regress toward 6.5 (`k_i ≈ 5`), `2(P+1)/12⁸ ≈ 0.0078` (~1 in 128). Presenting this formula unmodified beside S&T's "1 in 5 million" creates a severe **false-positive** framing hazard.
   - Using *strictly better* (`<`) for `k_i` also treats all ties in favor of the claim: if all 12 symbols tied at mean rank 6.5, `k_i = 0` everywhere, yielding `2/19,958,400` (~1 in 10 million) from completely flat data!

2. **Subset confound between Pillar 43 symbols (`S01`–`S08`) and non-Pillar-43 distractors (`S09`–`S12`) — *must fix***
   - `S01`–`S08` are mostly spindly/varied forms (3 birds, scorpion, frog, 3 mammals) cropped from Pillar 43, whereas `S09`–`S12` (aurochs, boar, lion/leopard, fox) are all four-legged mammals photographed on *other* pillars with different stone lighting, contrast, and resolution.
   - Only `8! / 19,958,400 = 1 / 495 ≈ 0.002` of assignments in Item 2 use exclusively `{S01..S08}`. If judges systematically rank `{S01..S08}` ahead of `{S09..S12}` (because spindly shapes match stick figures better than blocky quadrupeds, or due to photo artifacts), then even a *completely random* matching among `{S01..S08}` that happens to fall in the top half of the `8!` permutations will score `p ≤ 0.001` (**false positive**).
   - Conversely, if the 4 close-up distractor reliefs from other pillars look crisper than the degraded Pillar 43 crops (such as the 64 × 82 frog or the 3 white-patched photos) and are systematically ranked higher across all figures, genuine 1-to-1 matching within `{S01..S08}` can be buried under `p > 0.05` (**false negative**).

3. **Contamination / paper recognition is measured but never handled, and Task A itself reveals Göbekli Tepe — *must fix***
   - Every Task A trial displays **all 12 Göbekli Tepe reliefs together** (including Pillar 43's famous vulture-with-disc and scorpion). Frontier VLMs trained on web data have heavily ingested articles about Pillar 43 and the Younger Dryas star-map claim; showing all 12 together maximizes recognition *during* judging (**false positive**).
   - The single post-hoc recognition prompt only runs at the end and has **no decision rule attached**: if a judge explicitly identifies Göbekli Tepe and Sweatman & Tsikritsis, the protocol still lets it produce the label `"Blind judges see the claimed matches"`.
   - Even if a model denies recognizing the paper when shown all 20 images, it may still recognize *constellations* (especially Scorpius, Sagittarius, Gemini) from the black stick figures alone, or have implicit training-data priors linking the vulture and scorpion to those outlines.

4. **13-image VLM overload and low thinking budgets risk a massive false negative — *must fix***
   - Task A asks VLMs to ingest **13 images simultaneously** (1 line drawing + 12 low-res stone photos) and output a complete, globally consistent 12-item ranking in one call, using low reasoning budgets (`reasoning effort low` on `gpt-6.2-astra`, `512` thinking tokens on `gemini-4-neon`—barely ~350 words to inspect 13 images and rank 12).
   - Multi-image VLMs frequently suffer from visual token downsampling, label-to-image binding errors (swapping F and G), and position bias when given 13 images at once. A "plumbing test" on made-up shapes does not prove the models can reliably distinguish 12 low-contrast, 64 × 82–pixel stone reliefs in a single 13-image context. If models output near-random noise, the experiment will falsely conclude `"Blind judges do not see them"`.

5. **Shared random trial orders across all judges amplify position bias — *should fix***
   - Using the *same* `trials.json` (seed 92) for every judge means that any chance imbalance across only **5 repetitions** (e.g., a claimed symbol landing in early slots A–C on 4 of 5 trials) combines with VLM primacy/recency bias in the *same direction* across all 3 judges, instead of cancelling out (**false positive or false negative**).
   - With only 5 repetitions of 12 items, pure random permutations are too few to guarantee balanced slot exposure.

6. **Stimulus artifacts: aspect-ratio leakage, white patches, and red-line extraction — *should fix***
   - **Crop aspect-ratio leakage (false positive):** Scaling photographs and stick figures into `512 × 512` white squares preserves the aspect ratio of the authors' chosen crop rectangles. If tall carvings were cropped tall and paired with tall stick figures (and wide with wide), models can match bounding-box geometry rather than carved shapes.
   - **White patches (false positive or negative):** The 3 photos with white patches have sharp artificial high-contrast boundaries. If the authors painted white patches to carve out an intended silhouette, that helps the claim; if VLMs mistake the white blob for part of the shape, it degrades matching.
   - **Red-line extraction without visual audit (false negative):** Extracting red lines by color rule can drop anti-aliased thin lines, leave gaps where blue lines crossed red lines, or pick up red stars/labels. Moreover, stripping the faint blue lines of neighboring constellations may remove *Serpens* if S&T's Ophiuchus match relied on it (see Section 5).

7. **Task wording omits orientation rules and animal context — *should fix***
   - Asking only to rank "how closely the carved shape resembles the line drawing" without specifying whether **rotation or mirroring is allowed** creates unmeasured variance: one model may enforce strict displayed orientation while another mentally rotates shapes.
   - Referring to "the carved shape" (singular) is ambiguous for multi-element crops (`S06`: bending bird *and* wriggling fish/snake; `S05`: vulture *and* disc) and crops showing adjacent pillar carvings.
   - Telling judges only "shapes carved in stone" (never "animals") avoids semantic leakage (good for blinding against constellation names like *Lupus*), but may unfairly handicap VLMs on low-res carvings (e.g., the 64 × 82 frog) where recognizing the figure's foreground vs stone background requires knowing an animal figure is depicted (**false negative**).

8. **The 80% inclusion rule allows a judge to have 0 valid trials on a figure — *should fix***
   - Because 80% is measured over all **80 trials combined** (40 Task A + 40 Task B), a judge could score 40/40 on the easier 9-image Task B and only 24/40 on Task A, passing inclusion while missing all 5 trials on one or more Task A figures (producing `NaN` rows and biased pooled averages).

9. **Averaging noisy repetitions before permutation testing shrinks null variance relative to outlier matches — *should fix***
   - Averaging 5 reps × 3 judges = 15 trials collapses pure noise in unmatched rows toward `6.5` (SD ≈ `0.89`), while a consistent match stays at `1.0` (a `-5.5` gap, >6 SD of a single noisy row's spread). As detailed in Section 2, this lets just 2–3 matched figures dominate the pooled permutation test even when the remaining 4–5 figures are pure chance.

10. **Unclear retry mechanism could introduce anchoring bias — *minor***
    - "Asked again, up to twice" does not state whether retries are fresh stateless calls or multi-turn follow-ups. Multi-turn retries retain the model's invalid output in context and behave differently from fresh trials.

---

### 2. Problems With the Decision Rules

1. **Passing `p ≤ 0.001` does not test whether judges reproduce the paper's 1-in-5-million ranking — *must fix***
   - The decision rule tests the sharp global null ("zero resemblance across all 7 non-scorpion figures"), NOT S&T's claim ("all 7 match at rank 1 or 2"). It can trigger **`"Blind judges see the claimed matches"`** (and be read as *"For the paper's statistical case"*) in three ways where S&T's statistical case actually collapses:
     1. **2–3 figures carry 4–5 failures:** Because averaging 15 trials collapses variance in noisy rows (`SD ≈ 0.89`), if just **3 of the 7** non-scorpion figures consistently rank 1st and the other **4** are pure chance (~6.5), virtually only the `1/(11 × 10 × 9) = 1/990` assignments matching those 3 can compete, giving pooled `p ≈ 0.0005 ≤ 0.001` (and individual `p < 0.01`). Yet with 4 figures at chance, S&T's 1-in-5-million evaporates.
     2. **Weak universal resemblance:** If every claimed symbol ranks 4th out of 12 (never 1st!), pooled `p` will be `< 0.0001`, passing the bar—even though S&T's probability falls by >30,000×.
     3. **Subset effect:** Preferring `{S01..S08}` over `{S09..S12}` can push `p ≤ 0.001` with mediocre 1-to-1 matching.
   - **Verdict:** Far too easy to pass as a validation of the 1-in-5-million statistical claim.

2. **No competence floor before declaring `"Blind judges do not see them"` (unfair to the paper) — *must fix***
   - If the VLMs struggle to rank 12 tiny stone reliefs simultaneously and output high-variance noise, `pooled p > 0.05` triggers **`"Blind judges do not see them"`**, interpreted as evidence *"Against the paper's statistical case"*. Without verifying that the judges have acceptable intra-judge test-retest reliability (and can at least reliably match easy shapes like `A01`–`S01` in the 13-image layout), a null result conflates "no visual resemblance" with "noisy VLM instrument."

3. **No gate for failed blinding (contamination) — *must fix***
   - The labels say **"Blind judges..."**, yet there is no rule invalidating or downgrading the label if judges identify Göbekli Tepe, Pillar 43, or S&T (2017) in the recognition check.

4. **Single-judge veto (`p ≤ 0.01 for every included judge`) is brittle without a judge-reliability filter (unfair to the paper) — *should fix***
   - If 2 vendors show strong agreement (`p < 10⁻⁵`) while the 3rd vendor handles 13-image inputs poorly (passing 80% formatting checks with mostly random outputs, yielding `p = 0.03`), that noisy judge single-handedly vetoes the positive label and drags down the pooled `p`.

5. **Task B is half the experiment but absent from the decision rules — *should fix***
   - Running 40 Task B trials per judge (8 clean stick figures per stone photo—far easier for VLMs than 12 stone photos!) without pre-registering how Task B informs interpretation invites post-hoc cherry-picking if Task A fails and Task B succeeds (or vice versa). Also, Task B lacks a "without the scorpion" (`7! = 5,040`) analysis.

6. **Misstated justification for dropping the scorpion — *minor***
   - The plan asserts "the first [8-figure test] can be carried by the scorpion alone." In fact, under the permutation null, a single rank-1 match out of 8 (with 7 pure-chance rows) only shifts `S` by `~0.7` and cannot approach `p ≤ 0.001` on its own (`p` is at best `~1/24 ≈ 0.04` even with heavy variance collapse). Dropping the scorpion is still a good idea (because it was an anchor of S&T's reading), but the rationale should be accurate—and as shown in point 1, dropping only 1 figure does not prevent 2–3 remaining figures from carrying the 7-figure test.

---

### 3. Ambiguities for an Independent Replication Programmer

Given only this plan and `results/rankings.tsv`, an independent programmer could reasonably diverge on the following:

1. **Item 4 (without the scorpion): raw ranks (`1..12`) vs re-ranked (`1..11`) — *must fix***
   - After dropping `A01` and `S01`, do you keep the original `1..12` ranks from Task A (simply removing row `A01` and column `S01`), OR re-rank the remaining 11 symbols to `1..11` within each trial before averaging, OR re-rank each row of `M`? These give different values of `S` (chance = 6.5 vs 6.0) and different exact `p`-values because removing a middle-ranked `S01` leaves a rank gap of 2 in raw scores.

2. **Item 4 applied to Item 3: unspecified denominators, factor of 2, and >1 capping — *must fix***
   - "Items 1 to 3 are repeated for the other 7 figures, with the 11 other symbols" never states the denominators for Item 3 (presumably `11! / 4! = 1,663,200` and `11⁷ = 19,487,171`), whether the factor of `2` is retained, or whether values `> 1` are capped at `1` or reported raw.

3. **Floating-point tolerance / exact arithmetic for ties in Items 2, 3, 4, and 5 — *must fix***
   - Mean ranks are rational numbers (e.g., thirds, fifths, fifteenths). In IEEE-754 floats, mathematically equal sums or means can differ by `~10⁻¹⁶`. In Item 2 (`<=`) and especially Item 3 (`<`), a single `10⁻¹⁶` rounding artifact can flip a tie and double `P+1`! The plan must require exact rational/scaled-integer arithmetic (or a specified tolerance).

4. **Handling missing figure/symbol cells when pooling judges — *should fix***
   - If an included judge (≥80% overall) has 0 valid trials for a specific figure `a`, `M[a][s]` is undefined for that judge. Should the pooled table average over the remaining judges (`nanmean`), or exclude that judge from Task A? Similarly, it is not stated whether the 80% threshold applies jointly across all 80 trials (`≥64/80`) or separately to Task A (`≥32/40`) and Task B (`≥32/40`), or whether trials rescued by retries count toward the 80%.

5. **Item 6 definitions ("ranked first" and "rank of the claimed symbol") — *should fix***
   - Does "which symbol each judge ranked first" mean the symbol with the lowest mean rank `M[a][s]` (and how are ties listed?) or the modal #1 pick across the 5 reps?
   - Does "the rank of the claimed symbol" mean its mean rank (e.g., `3.4`) or its ordinal rank among the 12 symbols (`1` to `12`, and if ordinal, which tie rule: `1,2,2,4`, `1,2,2,3`, or mid-rank `1,2.5,2.5,4`)?

6. **Task B pooling, per-judge reporting, and inequality direction — *minor***
   - Item 5 does not explicitly specify (as Item 2 does) that `p` uses `<=`, that it is computed both per judge and on the pooled Task B table, or that the pooled Task B table is the unweighted mean of judges' tables. Likewise, Item 3 does not explicitly say whether it is computed per judge as well as pooled.

7. **Schema of `results/rankings.tsv` — *minor***
   - Not specified whether `rankings.tsv` stores already-decoded IDs (`S01`–`S12`, `A01`–`A08`) or raw presentation letters (`A`–`L`, requiring `trials.json`), and whether dropped trials appear as `NA` rows (needed for the independent programmer to verify the 80% inclusion rule!) or are pre-filtered.

---

### 4. Missing Checks (In Order of Importance, Feasible Within Plan & Budget)

1. **Within-Pillar-43 (`8!` and `7!`) permutation test on Task A and Pillar-vs-distractor comparison (`$0`, pure analysis) — *must fix***
   - Restrict Task A's matrix `M` to the 8×8 submatrix of `{S01..S08}` and compute the exact `8! = 40,320` (and `7! = 5,040` without scorpion) permutation `p`-value, plus the mean rank of `{S01..S08}` vs `{S09..S12}` across all figures. Directly separates true 1-to-1 matching from the Pillar-43 vs non-Pillar-43 photo/quadruped confound.

2. **Intra-judge reliability, inter-judge agreement, and position-bias diagnostics (`$0`, pure analysis) — *must fix***
   - Compute Kendall's *W* (or mean pairwise Spearman's *ρ*) across the 5 repetitions within each judge, inter-judge correlation across the 3 vendors, and mean rank by presentation slot (`A`–`L` / `A`–`H`). Essential to verify the judges are not outputting noise or slot-biased rankings.

3. **Staged contamination probe (`<$0.50`, 3 calls per judge instead of 1) — *must fix***
   - After ranking trials, probe in three sequential (or independent) calls: (a) the 8 black stick figures alone ("what are these?"), (b) the 12 stone photos alone ("what/where are these?"), and (c) all 20 together ("do you know any hypothesis linking them?"). Separates constellation recognition from Göbekli Tepe recognition from paper recall.

4. **Breadth / leave-k-out diagnostics and exact no-repeats Pareto count (`$0`, pure analysis) — *should fix***
   - Report how many of the 7 non-scorpion figures rank the claimed symbol 1st, top-2, or top-3, and run leave-one-out / leave-two-out sensitivity on Item 2 so 2–3 easy figures cannot masquerade as all-8 support.
   - During the `19,958,400` enumeration, directly count the exact number of valid no-repeat assignments that dominate or tie (`<=`) the claimed assignment at all positions, replacing the broken `2(P+1)/19,958,400` ratio, and report what S&T's formula yields under random ranks as a baseline.

5. **1-on-1 pairwise similarity ratings (`~$1–$3`, 96 two-image calls per judge) or positive-control calibration — *should fix***
   - Rating each `(figure, symbol)` pair individually (1 rep of `8 × 12 = 96` tiny 2-image calls per judge) eliminates 13-image overload and position bias completely, providing an immediate check on whether Task A suffered from multi-image degradation.
   - Before running the full suite, verify on a positive control (e.g., degraded/noisy stone-like silhouettes of known ground truth, or checking whether each judge consistently puts `S01` at rank 1 for `A01`) that the 13-image prompt with low thinking budget actually works.

6. **Bounding-box aspect-ratio correlation and visual audit of extracted stick figures (`$0`) — *should fix***
   - Visually verify all 8 black-on-white `A01`–`A08` images against Table 1 for dropped lines or stray artifacts.
   - Compute the non-white bounding-box aspect ratio (`width/height`) of `S01`–`S12` and `A01`–`A08`, and check whether aspect-ratio similarity alone predicts the claimed pairings or judge rankings.

7. **Task B without the scorpion (`7! = 5,040`) (`$0`, pure analysis) — *minor***
   - Mirrors the Task A without-scorpion analysis and lets you compare the two directions on equal footing.

---

### 5. Possible Errors in the Plan's Account of Sweatman & Tsikritsis (2017)

1. **"So the published figures follow from the published ranks" overlooks two mathematical errors in S&T's own formula — *should fix* (Confidence: High)**
   - The plan checks the arithmetic `2 × 2 / 12⁸` and `2 × 2 / 19,958,400` and concludes the published figures follow from the published ranks. That is only arithmetically true because S&T's formula `P+1 = ∏(1 + k_i)` is flawed in two ways:
     1. It only counts permutations that are *at least as good at every single position simultaneously*, omitting trade-off configurations (e.g., rank 1 at Gemini and rank 2 at one other position) that are equally good overall.
     2. For the no-repeats denominator (`19,958,400`), `P+1 = 2` is only valid if the single symbol ranked ahead of ibex/rat for Gemini is *not* one of the other 7 Pillar 43 symbols (if it is already used elsewhere on Pillar 43, there are 0 better no-repeat permutations, making `P+1 = 1`—Wait: conversely, if lion is tied at `=2`, there is also a tie that S&T excluded from `P`).
   - Also worth noting (though minor): S&T's quoted statement *"The probability that Pillar 43 does not represent the stated date is then simply 2(P+1)/Q"* commits the prosecutor's fallacy (confusing `P(data | coincidence)` with `P(coincidence | data)`). The plan paraphrases it properly elsewhere, so this just warrants a brief note.

2. **The Gemini cell (`"=2 with lion"`) and `P+1 = 2` — *should fix* (Confidence: Medium-High)**
   - The plan notes the Gemini cell is cut off in the PDF and reads `"=2 with lion"`. If ibex/rat is tied for **2nd** with lion, then *one* symbol is ranked **1st** (strictly better) and *lion* is tied for **2nd** (equally good). S&T's `P+1 = 2` therefore counts only the 1 strictly better symbol and ignores the tie with lion (counting ties as equally good would give `P+1 = 3`, i.e., ~1 in 3.3 million instead of 1 in 5 million). Because the cell is cut off in the PDF, the plan should verify which symbol is ranked 1st for Gemini in Table 1 and confirm whether `=2` really means 1 strictly better + 1 tied.

3. **Removing "faint blue lines of neighbouring constellations" may remove *Serpens* from the Ophiuchus comparison — *should fix* (Confidence: Medium)**
   - In Stellarium, Ophiuchus ("the serpent-bearer") overlaps closely with the neighboring constellation *Serpens*. Since S&T match Ophiuchus to `S06` ("bending bird with wriggling fish/snake"), verify directly in Table 1 whether S&T's red lines for Ophiuchus include any part of Serpens, or whether the snake correspondence relied on neighboring blue lines (or on the constellation's mythological name). If blue lines carried part of the visual match, stripping them could bias Task A against S&T on `A06`.

4. **Origin of the factor of `2` and "Scorpion = Scorpius is the reading's starting point" — *minor* (Confidence: Medium)**
   - The plan reproduces `2(P+1)/Q` without explaining where S&T's factor of `2` comes from (or checking whether it stays `2` when reduced to 7 figures).
   - Describing Scorpius as the sole starting point slightly oversimplifies S&T's argument: their starting anchor was the *pair* of the scorpion (Scorpius) alongside the vulture holding the disc (interpreted as the Sun in Sagittarius) beneath the three "handbags." Excluding only Scorpius is still defensible, but the framing should reflect this accurately.

---

### Top Three Changes to Make First

1. **Fix the statistical tests and decision rules:** Add the within-Pillar-43 `8!`/`7!` permutation test (to rule out the `S01`–`S08` vs `S09`–`S12` subset confound), add a breadth/effect-size requirement and leave-top-2-out check (so 2–3 easy figures or uniform 4th-place ranks cannot pass as validating 1-in-5-million), replace Item 3's broken `2(P+1)/19,958,400` ratio with an exact no-repeats enumeration (with conservative `<=` tie handling), and gate the verdict labels on both judge reliability and non-recognition.
2. **De-risk 13-image VLM noise and position bias:** Give each judge its own position-balanced trial orders (not one shared seed), increase reasoning/thinking budgets (especially `gemini-4-neon`'s 512 tokens), specify orientation rules in the prompt, require a per-figure minimum of valid trials, and add a cheap 1-on-1 pairwise similarity check (96 two-image calls/judge) plus intra-judge reliability diagnostics so a negative result cannot be dismissed as multi-image VLM failure.
3. **Upgrade the contamination probe and lock all replication ambiguities:** Split the post-hoc recognition check into staged prompts (figures alone → reliefs alone → all 20 together) with an explicit rule if recognition occurs, and specify exact rational arithmetic for ties, raw vs re-ranked handling in Item 4, Item 4 denominators for Item 3, retry mechanics, and exact formulas for Item 6 and Task B.
