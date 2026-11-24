# Results — Do flood myths cluster where land drowned? (#44)

- **Question:** #44, `lane:data`.
- **Plan locked:** 2026-11-24T17:25:14Z (`protocol.lock`, commit `8efaaf8`), before the results were committed. The plan is unchanged since.
- **Who did the work:** AI did. Antigravity (Google DeepMind) designed and ran the study on 24 November 2026. Claude Fable 5.2 (Anthropic), with Claude Opus 5.5 sub-agents, spot-checked it the same day and wrote this corrected report. Eugene Jhong directed both. No specialist has reviewed it, and it has not been replicated by a second company's model.
- **Record of departures from the plan:** `amendments.md`. The first write-up said there were none; there were five.

## Answer

**No sign of it. Flood motifs are no more common beside coasts that lost a wide shelf than beside coasts that lost almost none. But the test is weaker than the first write-up said, and by the plan's own rule it is not a clean null.**

- **The finding.** Among 396 societies within 150 km of water, 36% have at least one of the 17 chosen flood motifs beside the narrowest drowned shelves and 34% beside the widest. In the model fixed in advance (coastal M4, which compares societies within the same language family), the slope is −0.010 SD with a standard error of 0.062 (`p = 0.87`). A separately written program gives the same numbers.
- **A fault in the measure of drowned land, which does not change the answer.** The plan counted every map cell below sea level as sea. That takes in the Caspian Sea, the Great Lakes, Lake Baikal and desert basins. About a tenth of the "drowned shelf" in the study is not sea, 33 of the 396 "coastal" societies have no sea within 150 km, and 12 of the 99 societies in the widest-shelf group are peoples of the Caspian shore. Counting real sea only, the slope is −0.038 (`p = 0.61`, 368 societies).
- **The plan's check on the method partly failed.** The plan said a null would count only if two positive checks came out "decisively". Earthquake motifs do follow earthquake country (`p = 0.002`). Sea motifs follow nearness to the coast only weakly (`p = 0.07` and `0.05`, against a required `p < 0.001`). None of the plan's three verdicts covers that case. The first write-up said the null criterion was met "cleanly". It was not.
- **How much the test could have seen.** Large effects are unlikely. A modest one, up to about ten percentage points between narrow and wide shelves, is not excluded.
- **What it tested.** World-flood motifs in a catalogue, at the places where peoples lived in recent centuries. It did not test stories about particular drowned places, and it has almost nothing from Australia.

## Spot check and corrections

A spot check is not a replication. It reran the program, refitted the main model with separately written code, recomputed the drowned area for 38 societies from the full-resolution map, and read the plan against the program and the report.

What holds:

- The lock matches the plan, and the data files match their recorded checksums.
- Rerunning the program gives the same coefficients, standard errors and p-values (to seven figures). The permutation tests use a fixed seed and reproduce exactly.
- Every number in the tables below matches the results file.
- A separate fit of the main model gives β = −0.0100, cluster SE 0.0621, spatial SE 0.0513.
- The drowned areas are computed accurately for what the plan defined: the median ratio of the recomputed values to the study's is 1.01.
- The result survives every repair tried after the fact: real sea only; flood-centred motifs only (β = +0.001, `p = 0.98`); societies below 50° latitude only (β = −0.006, `p = 0.94`); dropping only the Noah's Ark motif (β = −0.006).

What does not:

1. **Water that is not sea.** Described above. The fault is in the locked plan ("nearest modern ocean grid cell, z < 0 m"), which the program followed. The plan's depth rule also counts shelves that were under ice at the glacial maximum, such as Hudson Bay and the Baltic, as land that drowned.
2. **"Meets the pre-registered Null verdict criterion cleanly."** False. The second positive check failed its threshold, and the table called that "Positive (borderline)".
3. **"On the exact same societies and model."** The earthquake check was run on all 927 societies with a lighter model. In the flood test's own sample and model it is not significant (β = +0.098, `p = 0.14`). The check also uses a hazard that is present today, while the drowning ended at least 7,000 years ago and many peoples have moved since. It shows that the catalogue can carry a trace of a living hazard. It does not show that it could carry a trace that old.
4. **"Would have been easily detectable."** An effect the size of the earthquake check's would have been found about two times in three at `p < 0.05`, and less than half the time under the plan's rule for a positive.
5. **Seven of the 17 motifs are not really about floods.** They include "descent from a dog", "objects' revolt", "monsters destroy people" and a dragon that withholds water. 138 of the 351 societies counted as having a flood myth (39%) have only those. Counting motifs built around a flood, 23% of societies have one (12.5% without the motif that covers destruction by flood or fire). "Nearly four in ten societies have a flood myth" overstated it.
6. **The "Noah" exclusion.** One of the two motifs excluded as biblical, "bird scouts", is recorded in 123 societies, 75 of them in the Americas, mostly in stories where an animal dives for earth. The "Noah-free" sample therefore drops many native American traditions for no good reason. The result is the same either way.
7. **Analyses described but not run.** The first write-up said that dropping high latitudes or looking at tropical shelves "produces the same null". No such analysis was in the program. Run now, it does give a null, with a wide interval for the tropics (±0.3 SD). It also said the unit tests check the area calculation and the distance to the coast; they do not.
8. **Australia.** The write-up said the catalogue codes "16 coastal Aboriginal Australian groups". Three of the 16 are Australian. It also said Nunn and Reid studied "21 stories"; their abstract says stories from 21 locations.
9. **Explanations that were not tested.** That flood myths are "far better explained by river floods, storms, tsunamis, storytelling traditions, and cultural diffusion", and the reason offered for the negative shelf-fraction result. Both are removed.
10. **"Zero amendments."** Five departures from the plan are now recorded in `amendments.md`. The largest: 31 societies with a missing temperature value were dropped without a word, 29 of them small islands of the Pacific and Indian Oceans.

The plan and the 24 KB program with its results were committed eight minutes apart. Git shows the order and nothing more; it cannot show that no analysis was run before the lock. Nothing in the plan looks shaped by results, and the motif list shows no sign of it.

The spot check's scripts and outputs are in `spotcheck/`.

## The locked run in detail

The tables below are the first run's, unchanged. Sentences around them have been corrected.

### 1. The checks on the method

The plan required three checks before the flood result was read. The two positive checks were run on all 927 societies with a lighter model than the flood test (sampling controls, latitude and language-family fixed effects); the fire check was run in the flood test's own sample and model.

| Check | Outcome | Predictor | Sample (`N`, lang. families) | `β` (SD per unit) | `p` (lang. cluster) | `p` (Conley 500 km) | `p` (Conley 1,000 km) | Result |
|---|---|---|---:|---:|---:|---:|---:|---|
| Positive Control 1 | `earthquake_related` (z) | Seismic proximity (`−ln dist`) | 927 (94) | **+0.1570** | **0.0023** | **0.00038** | **0.00053** | Pass (`p < 0.01` was required) |
| Positive Control 2 | `sea_related` (z) | Coastal proximity (`−ln dist`) | 927 (94) | **+0.0875** | 0.073 | **0.045** | 0.052 | **Fail** (`p < 0.001` was required) |
| Negative Control | `fire_related` (z) | `log(1 + drowned 120 m, 250 km)` | 396 (58) | −0.0698 | 0.198 | 0.196 | 0.226 | **Pass (null)** |

The earthquake check passes as it was coded. Run in the flood test's own sample and model (396 coastal societies, model M4) it gives `β = +0.098`, `p = 0.14`, which is not significant (spot check, after the fact). The sea check fails the threshold the plan set for it. With a standard error of 0.062, an effect of 0.15 SD would have been found at `p < 0.05` about two times in three, and under the plan's own rule for a positive (`p < 0.01` on both kinds of standard error) less than half the time.

---

### 2. The coastal comparison (`dist_coast_km ≤ 150 km`)

Comparing coastal peoples directly against one another (rather than coastal against inland steppe or mountain peoples) isolates how much land actually drowned off their shore between the Last Glacial Maximum (~20 ka, −120 m sea level) and today.

#### 2.1 Raw quartiles of Drowned Continental Shelf (`−120 m` to `0 m`, within 250 km)

| Quartile | Drowned Shelf Area (km²) | Societies (`n`) | Any Non-Biblical Flood (%) | Mean Non-Biblical Share (%) | Mean MX `flood_related` (%) |
|---|---:|---:|---:|---:|---:|
| Q1 (narrowest) | 484 – 10,397 | 99 | **36.4%** | 1.07% | 1.22% |
| Q2 | 10,397 – 20,047 | 99 | **37.4%** | 1.13% | 1.41% |
| Q3 | 20,047 – 39,598 | 99 | **35.4%** | 1.05% | 1.27% |
| Q4 (widest) | 39,598 – 187,061 | 99 | **34.3%** | 0.95% | 1.04% |

There is no upward gradient anywhere across the four quartiles.

#### 2.2 The model ladder (M1 to M4)

Coefficients are per standard deviation of the logarithm of drowned shelf area (one SD is 1.04 log units) (`log_drowned_120m_250km`) on each pre-registered outcome:

| Sample & Outcome | Model | `n` (clusters) | `β` | SE (cluster) | `p` (cluster) | SE (Conley 1,000 km) | `p` (Conley 1,000 km) | `p` (within-cont. perm.) | Residual Moran's *I* |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Coastal: `nb_flood_share_z`** | M1 (sampling) | 396 (58) | +0.0213 | 0.0569 | 0.710 | 0.0521 | 0.683 | — | +0.183 |
| **Coastal: `nb_flood_share_z`** | M2 (+ geophys.) | 396 (58) | +0.0413 | 0.0539 | 0.447 | 0.0481 | 0.390 | — | +0.147 |
| **Coastal: `nb_flood_share_z`** | M3 (+ cont. FE) | 396 (58) | +0.0590 | 0.0520 | 0.262 | 0.0507 | 0.244 | 0.271 | +0.128 |
| **Coastal: `nb_flood_share_z`** | **M4 (+ lang. FE)** | **396 (58)** | **−0.0100** | **0.0621** | **0.872** | **0.0513** | **0.845** | **0.846** | **+0.127** |
| Coastal: `any_nb_flood` (prob.) | M3 (+ cont. FE) | 396 (58) | +0.0085 | 0.0214 | 0.692 | 0.0218 | 0.695 | 0.690 | +0.173 |
| Coastal: `any_nb_flood` (prob.) | **M4 (+ lang. FE)** | **396 (58)** | **−0.0138** | **0.0293** | **0.640** | **0.0213** | **0.517** | **0.560** | **+0.134** |
| Coastal: MX `flood_related_z` | M3 (+ cont. FE) | 396 (58) | +0.0446 | 0.0509 | 0.384 | 0.0482 | 0.354 | 0.363 | +0.121 |
| Coastal: MX `flood_related_z` | **M4 (+ lang. FE)** | **396 (58)** | **−0.0321** | **0.0600** | **0.594** | **0.0479** | **0.502** | **0.512** | **+0.114** |
| **Noah-free coastal: `nb_flood_share_z`** | **M4 (+ lang. FE)** | **340 (56)** | **−0.0149** | **0.0648** | **0.819** | **0.0565** | **0.792** | **0.796** | **+0.087** |
| Noah-free coastal: `any_nb_flood` | **M4 (+ lang. FE)** | **340 (56)** | **−0.0016** | **0.0291** | **0.957** | **0.0226** | **0.944** | **0.962** | **+0.161** |
| Noah-free coastal: MX `flood_related_z` | **M4 (+ lang. FE)** | **340 (56)** | **−0.0190** | **0.0647** | **0.771** | **0.0514** | **0.712** | **0.720** | **+0.085** |
| Global all: `nb_flood_share_z` | **M4 (+ lang. FE)** | **927 (94)** | **−0.0117** | **0.0866** | **0.893** | **0.0531** | **0.826** | — | **+0.134** |
| Global all: MX `flood_related_z` | **M4 (+ lang. FE)** | **927 (94)** | **−0.0617** | **0.0825** | **0.456** | **0.0494** | **0.211** | — | **+0.141** |

No specification in the ladder differs from zero, and every M4 estimate is slightly negative. The 95% interval for the primary slope is −0.11 to +0.09 SD with spatial standard errors and −0.13 to +0.11 with standard errors clustered by language family. In plain terms: from a typical narrow-shelf society (6,400 km² drowned) to a typical wide-shelf one (58,000 km²), the data do not exclude a rise of up to about ten percentage points in how often a flood motif is recorded, on a base of 36%. Large effects are unlikely; modest ones are not excluded. The residual Moran's *I* column is a diagnostic only and is not exactly reproducible: the program gives some societies a small weight on themselves, depending on rounding, and the values change by up to a fifth between machines.

---

### 3. Other measures of drowned land (coastal, M4)

Does the null depend on choosing −120 m instead of the final Holocene rise (−60 m, ~12–7 ka), or 250 km instead of 500 km, or absolute area instead of shelf fraction?

| Exposure Definition (Coastal `n = 396`, M4 lang. FE) | `nb_flood_share_z` `β` (`p_Conley_1000`) | MX `flood_related_z` `β` (`p_Conley_1000`) | `any_nb_flood` `β` (`p_Conley_1000`) |
|---|---:|---:|---:|
| Primary: `log(1 + drowned −120 m, 250 km)` | −0.0100 (`0.845`) | −0.0321 (`0.502`) | −0.0138 (`0.517`) |
| Holocene window: `log(1 + drowned −60 m, 250 km)` | −0.0170 (`0.709`) | −0.0405 (`0.343`) | −0.0162 (`0.459`) |
| Wider radius: `log(1 + drowned −120 m, 500 km)` | −0.0826 (`0.218`) | −0.1034 (`0.079`) | +0.0054 (`0.826`) |
| Shelf fraction of ocean: `drowned_frac_ocean_250km` | **−0.1626 (`0.0185`)** | **−0.1711 (`0.0048`)** | −0.0311 (`0.263`) |

No measure turns positive. One, the drowned shelf as a share of nearby sea, is negative at `p = 0.019` and `p = 0.005`. It is one of twelve sensitivity tests and nothing here explains it. The first write-up offered an explanation (steep coasts have more tsunamis); that was a guess, it was not tested, and the models already control for distance to earthquakes.

---

### 4. By continent

The plan asked for four macro-regions; the program used the dataset's six continents. Testing each continent separately (Coastal M2 with sampling + geophysical controls, `500 km` Conley SEs) checks whether a strong regional signal is hidden inside the global null:

| Continent (Coastal `≤ 150 km`) | `n` | Any Non-Biblical Flood | Median Drowned Shelf (km²) | M2 `β` (`nb_flood_share_z`) | `p` (Conley 500 km) | Spearman `ρ` |
|---|---:|---:|---:|---:|---:|---:|
| Africa | 33 | 15.2% | 18,718 | −0.128 | 0.054 | −0.36 |
| Asia | 130 | 34.6% | 29,059 | +0.085 | 0.066 | +0.08 |
| Europe | 37 | 24.3% | 37,261 | −0.048 | 0.493 | −0.17 |
| North America | 140 | 41.4% | 18,211 | +0.123 | 0.329 | +0.03 |
| Oceania | 25 | 24.0% | 9,235 | −0.282 | 0.053 (`flood_rel` **0.039**) | −0.38 |
| South America | 31 | 61.3% | 16,511 | +0.151 | 0.381 | +0.24 |
| *Box around Australia and its northern neighbours (see below)* | *16* | *18.8%* | *17,023* | *—* | *—* | *−0.41* |

No continent reaches `p < 0.05` in the positive direction; Asia (`p = 0.066`), North America (`p = 0.329`), and South America (`p = 0.381`) are weak and nonsignificant, while Africa, Europe, and Oceania tilt negative.

**Australia.** The program's "Australia/Sahul" box (south of 8° S, 110° to 156° E) holds 16 coastal societies, and only three of them are Australian: Kimberley Plateau, Southern Australia and Tasmania. Ten are islands of eastern Indonesia and Timor, and three are in New Guinea and the Torres Strait. The catalogue codes the whole of Australia as eight broad regions. So this study says almost nothing about Australia, which is where the best-known claim of a remembered drowning comes from: Nunn and Reid (2016) collect Aboriginal stories from 21 places around the coast that describe particular shores going under. (We read that paper's abstract only.) Stories about a named bay are also a different thing from the world-flood motifs the catalogue indexes.


## Limits

1. **Recent homes, ancient coasts.** The catalogue places each people where it lived in recent centuries. Polynesians, Bantu speakers and Inuit, among others, reached their present coasts long after the shelves there had drowned. This weakens the test: for many societies the exposure measured is one their ancestors never had.
2. **The measure of drowned land.** Besides inland water and ice-covered shelves (above), the map gives today's depth. Where the land has risen or sunk since the ice melted, depth below 120 m is a poor guide to what was dry.
3. **The outcome.** Motifs were chosen from their titles before any result was seen. Seven of the 17 are loosely connected to floods at best, and the catalogue records what collectors wrote down, which varies from place to place.
4. **Power.** See above: modest effects are not excluded.
5. **Language families.** 21 of the 58 coastal families have one society each and add nothing to the main model, which rests on 375 societies in 37 families.
6. **No replication.** A second company's model has not rerun this from the plan.
7. **Not read.** Nunn and Reid (2016) in full; Berezkin's own terms of use for the catalogue, beyond the CC0 label on the replication package.

## Spending

Nothing was paid for. The study and the spot check ran on local machines with public data.

## What this means

Flood stories are told all over the world, and one old idea is that they are a memory of the sea rising 120 metres at the end of the Ice Age. If so, they should be commoner among peoples whose coasts lost the most land. In a catalogue of the myths of 927 peoples they are not: the rate is the same beside wide drowned shelves and narrow ones, and a little higher inland. That is evidence against a worldwide memory, and it is weaker evidence than it first looked. The study put some peoples beside "drowned shelves" that are the Caspian Sea and the Great Lakes, a third of its "flood myths" are not clearly about floods, its own check on the method half failed, and it could have missed a modest effect. Mending the faults we could mend leaves the answer where it was. It says nothing about stories of particular drowned bays and islands, such as those collected in Australia, which are a different and better-founded claim.
