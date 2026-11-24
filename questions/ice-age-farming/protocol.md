# Protocol — Farming Before the Ice Age Ended (#88)

- **Issue:** #88 (`lane:data`)
- **Date:** 2026-11-24
- **Budget:** $0 (open Neotoma v2.0 REST API + PANGAEA metadata; local Python computation)

## 1. Exact Question

Across the global **Neotoma Paleoecology Database** of dated lake and bog fossil pollen cores, do any well-dated sediment layers older than **12,000 cal BP** (`12,000–50,000 BP`) preserve a sustained, multi-proxy **farming package**—crop/cereal-type pollen co-occurring with anthropogenic field weeds and canopy clearance—above the wild-grass false-positive rate observed in glacial negative controls, after first calibrating the exact same detector on the known Holocene spread of Neolithic farming across Europe?

## 2. Why Un-Lumped Neotoma Data Are Required

Pre-protocol inspection of `LegacyPollen 2.0`'s taxonomic harmonization table (`harmonization_table_new.tab`) confirmed that harmonized biome syntheses lump `Cerealia`, `Triticum`, `Hordeum`, `Secale`, `Oryza`, and `Avena` into family-level `Poaceae`, and `Plantago lanceolata` into `Plantaginaceae`. Detecting ancient crops therefore requires querying **un-lumped fossil pollen counts** directly from the **Neotoma Paleoecology Database v2.0 API** (`https://api.neotomadb.org/v2.0/`, CC-BY 4.0), which preserves exact taxon identifications, `TRSH` (arboreal) vs. `UPHE` (upland herb) ecological groups, and radiocarbon chronologies.

## 3. Pre-Registered Taxa, Farming Signature, and Controls

### 3.1 Crop / Cereal Taxa (Fixed Neotoma Taxon IDs)
- **Old World cereals:** `Poaceae (Cerealia)` (`416`), `Poaceae (Cerealia) undiff.` (`427`), `Poaceae (Cerealia-type)` (`1947`), `Poaceae (Cerealia-type) undiff.` (`2941`), `Poaceae (Cerealia-type) cf. Hordeum` (`3711`), `Poaceae (Cerealia) cf. Avena` (`3916`), `Poaceae (Cerealia) cf. Triticum dicoccon` (`3920`), `Poaceae (Cerealia) cf. Triticum` (`3922`), `Poaceae (Cerealia) cf. Secale` (`3925`), `Poaceae (Cerealia) sp.` (`31532`), `Poaceae (Cerealia) excluding Secale` (`31534`), `Poaceae (Cerealia-type) cf. Hordeum group` (`31540`), `Poaceae (Cerealia-type) cf. Avena/Triticum group` (`31542`), `Cerealia` (`31996`), `Triticum-type` (`497`), `Triticum` (`969`), `Triticum undiff.` (`3919`), `Hordeum-type` (`3705`), `Hordeum/Triticum` (`3921`), `Hordeum` (`3923`), `Hordeum/Secale` (`3924`), `Secale-type` (`488`), `Secale` (`967`), `Secale cereale` (`3926`).
- **New World & East Asian crops:** `Zea mays` (`323`), `Zea` (`538`), `Zea undiff.` (`4981`), `Oryza-type` (`5644`), `Oryza` (`39697`), `Fagopyrum` (`106`), `Fagopyrum esculentum` (`1324`), `Fagopyrum-type` (`4287`).

### 3.2 Anthropogenic Field/Pasture Weeds (Excluding Natural Ice-Age Steppe Taxa)
Because *Artemisia* and *Chenopodiaceae/Amaranthaceae* naturally dominate cold Pleistocene steppe-tundra, our pre-registered anthropogenic weed index **`anthro_weed_pct`** sums strictly:
- `Plantago lanceolata` / `Plantago lanceolata-type` (tracked separately as `plantago_lan_pct`),
- `Rumex` / `Rumex acetosa` / `Rumex acetosella`,
- `Urtica` / `Urtica dioica`,
- `Centaurea cyanus`,
- `Polygonum aviculare` / `Polygonum aviculare-type`,
- `Cannabis` / `Cannabis-type` / `Cannabis/Humulus`.

### 3.3 Sample-Level Metrics & Multi-Proxy Farming Package Rules
For every sample `i` with terrestrial pollen sum `S_i = TRSH + UPHE ≥ 100` grains (`NISP` counts, or `present/absent` normalized if percentage units):
- `crop_pct = 100 * crop_grains / S_i`
- `anthro_weed_pct = 100 * weed_grains / S_i`
- `ap_pct = 100 * TRSH / S_i` (arboreal pollen percentage)

**Two locked detection thresholds:**
1. **`FARM_RELAXED` (sensitive screen):** Any sample (`S_i ≥ 100`) with `crop_pct ≥ 0.5%` (and `≥ 2` grains if counts) AND `anthro_weed_pct ≥ 0.5%`.
2. **`FARM_STRICT` (primary multi-proxy farming package):** A core contains **`≥ 2` samples** within a `≤ 1,000 yr` span (`S_i ≥ 100`) satisfying ALL of:
   - `crop_pct ≥ 0.5%` (`≥ 2` grains if NISP counts),
   - `anthro_weed_pct ≥ 0.5%` (with `Plantago lanceolata` or `Rumex`/`Urtica`/`Centaurea cyanus` present),
   - **Canopy clearance OR strong dual-indicator intensity:** either `ap_pct` declines by `≥ 10` percentage points from the core's pre-event forest mean (when baseline `ap_pct ≥ 50%`), OR (in naturally open landscapes) `crop_pct ≥ 1.0%` AND `plantago_lan_pct ≥ 0.5%` in both samples,
   - **Chronological integrity (for pre-12 ka candidates):** Sample age on the default chronology is `≥ 12,000 cal BP` (or `≥ 10,300 14C yr BP` if uncalibrated), age-depth order is monotonic (no inversions around the target depth), and the depth is bracketed by radiometric/tephra/varve age controls (not unanchored deep extrapolation).

### 3.4 Calibration Gate & Global Pre-12,000 BP Sweep
1. **Calibration Cohort (Known Holocene Neolithic Spread in Europe/Mediterranean):** Download up to `100` dated European/Mediterranean Neotoma pollen cores (`lon ∈ [-10°, 45°], lat ∈ [34°, 62°]`) spanning at least `11,000–3,000 BP` with cereal records. Measure `FARM_STRICT` and `FARM_RELAXED` detection rates in:
   - **Holocene Farming Window (`8,500–2,000 cal BP`)** — must detect farming in **`≥ 50%`** of cores, with onset times tracking the known southeast-to-northwest Neolithic wave across Europe.
   - **Pre-Neolithic Mesolithic Window (`11,500–9,000 cal BP`, North/Central Europe `lat ≥ 46°`)** — negative control for wild grass false positives (`< 10%` under `FARM_STRICT`).
2. **Global Pre-12,000 BP Census & Full-Core Audit:**
   - Query Neotoma `/v2.0/data/occurrences` across **all 32 crop/cereal taxon IDs** for `age ∈ [12,000, 50,000] BP` (excluding `pollen surface sample` and non-pollen macrofossils).
   - Also determine the denominator: total global Neotoma fossil pollen datasets reaching `≥ 12,000 BP`.
   - Download the **complete pollen core and chronology** (`/v2.0/data/downloads/{dsid}`) for **every unique fossil pollen core** with `≥ 1` pre-12,000 BP crop/cereal occurrence (up to 150 cores if more exist; prioritized by count and geographic coverage, logging total count).
   - Score every core under `FARM_RELAXED` and `FARM_STRICT`, separating:
     - **Late Glacial / Terminal Pleistocene (`12,000–18,000 cal BP`)** vs.
     - **LGM / Deep Glacial Negative Control (`18,000–50,000 cal BP`)**, where wild large grasses (*Glyceria*, *Elymus*, *Leymus*) and chronology errors set the natural false-positive baseline.
   - Audit every single core that passes `FARM_STRICT` individually (site name, coordinates, taxon identity, pollen counts, chronology type, age controls, and known literature context).

## 4. Pre-Registered Verdict Criteria

- **Candidate Discovery / Flagged for Specialist Review:** Calibration gate passes (`≥ 50%` Holocene Neolithic detection, `< 10%` Northern/Central European Mesolithic `FARM_STRICT` false-positive rate), AND `≥ 1` well-dated, non-inverted pre-12,000 cal BP core passes `FARM_STRICT` at a rate significantly exceeding the `18–50 ka` glacial negative-control rate (`p < 0.01`, Fisher exact), AND survives individual chronology/wild-grass audit.
- **Null (No evidence of Ice Age farming in global pollen cores):** Calibration gate succeeds decisively on Holocene Neolithic farming, while **zero** well-dated pre-12,000 cal BP cores survive `FARM_STRICT` + chronological/wild-grass audit (or pre-12,000 BP rate does not exceed the `18–50 ka` glacial wild-grass baseline).
- **Inconclusive / Calibration failure:** `FARM_STRICT` fails to detect `< 50%` of known Holocene Neolithic European cores or triggers `≥ 15%` false positives in pre-Neolithic Mesolithic Europe or the LGM glacial control.

## 5. Verification

Synthetic unit tests (`analysis/test_ice_age_farming.py`) verifying pollen-sum calculation (`TRSH + UPHE`), `AP%` clearance detection, `FARM_RELAXED` / `FARM_STRICT` rules, uncalibrated vs. calibrated age handling, and planted Neolithic vs. wild-grass-only synthetic cores before inspecting real Neotoma results.
