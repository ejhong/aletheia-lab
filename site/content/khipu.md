---
summary: Corpus-wide Rosetta scan across all 619 Andean khipus (191,271 pairs) in the Open Khipu Repository plus statistical audit of the 1670 Santa Valley census match; uncovers 8 zero-FDR non-Puruchuco twin pairs across museums and coastal valleys.
verdict: New internal Rosetta links found — 8 distinct twin khipu pairs at FDR = 0.000, plus statistical caution on Santa Valley
result: Scanning all 191,271 pairs across 619 khipus in the Open Khipu Repository blindly recovers the known Puruchuco accounting copies and uncovers 8 physically distinct non-Puruchuco Tier A twin pairs at 0 / 100,000 permutation null hits (FDR = 0.000)—including a 23-cord, 34,880-unit twin split between Göteborg, Sweden (KH0362) and Lima, Peru (KH0049, 0.095% error), an exact 6-cluster Pachacamac–Huacho ledger reformatted between 5-cord and 6-cord templates (KH0192 ↔ KH0470), and a reversed 17-cord copy linking an unprovenanced Berlin khipu (KH0473) to Marquez (KH0121). Meanwhile, 62–72% of random 6-pachaca splits match Santa Valley's (70, 63) moiety count as closely as published alignments, and external colonial-document matching remains blocked by the lack of digitized Andean revisitas.
dek: Can a systematic search across all 619 public Andean khipus uncover new Rosetta links—and how statistically tight is the famous 1670 Santa Valley census match?
updated: 2026-11-24
---

{{figure: khipu/tiles}}

## The hunt

In 2018, Manny Medrano and Gary Urton proposed the field's most famous external foothold: matching six khipus from the Santa Valley, Peru (`KH0323`–`KH0328`) to a 1670 Spanish colonial tribute census (*revisita*) of 132 tributaries divided into six *pachacas*. Can a systematic computational search across all **619 khipus** (`54,403` cords, `110,677` knots) in the Open Khipu Repository (`khipu.db`) find additional Rosetta matches—both **between khipus and colonial records** and **between scattered khipus themselves**?

Before running a single pair comparison, we locked a three-part protocol: (1) audit and calibrate the 1670 Santa Valley match against exact combinatorial and corpus-wide false-positive nulls; (2) scan all `191,271` khipu pairs for exact/near-exact pendant and cluster-sum copies (requiring blind recovery of Urton & Brezine's 2005 *Science* Puruchuco copies as a positive control, calibrated against `100,000` shuffled null pairs); and (3) map which provenanced archives are structurally ready for colonial *revisita* matching.

## Eight distinct Inca twin khipus discovered at zero false-discovery rate

Without using provenance labels, our matcher blindly recovered the known Puruchuco accounting copies (`KH0305 ↔ KH0301`, `L = 36`; `KH0315 ↔ KH0300`, `L = 10`; `KH0304 ↔ KH0303`, `L = 32`)—and uncovered **eight physically distinct non-Puruchuco Tier A twin pairs** (7 pendant matches + 1 exact cluster-sum match) against **`0 / 100,000` permutation null hits (`FDR = 0.000`)**. None are flagged as duplicates in `khipu.db`; every pair has distinct museum catalog numbers and distinct cord counts:

- **Göteborg, Sweden ↔ Lima, Peru (`KH0362` Nazca, 72 cords ↔ `KH0049` Costa Sur, 108 cords):** **23 consecutive 3- and 4-digit cords** (`[1146, 1590, 1615/1605, 960, 855, 3840/3848, ..., 6485, ..., 972]`) summing to **`34,875` vs. `34,888`** (`19/23` exact, `23/23` within `1%`, `0.095%` L1 error) across two museums on two continents.
- **Pachacamac ↔ Huacho (`KH0192`, 224 cords ↔ `KH0470`, 126 cords):** **6 consecutive 100% exact cluster sums** (`[173, 275, 317, 329, 23, 171]`) encoding the exact same 24 non-zero values in **two different column layouts** (5-cord clusters in `KH0192` vs. 6-cord clusters with an inserted zero-slot in `KH0470`) across two Peruvian coastal sites ~130 km apart.
- **Provenance recovery (`KH0121` Marquez ↔ `KH0473` unknown, Berlin):** **17 consecutive cords in reverse** (`16/17` exact, `1,766` vs. `1,772`, `0.34%` error), linking unprovenanced specimen `VA 66834` directly to the **Marquez** archive.
- **Five additional regional & trans-continental twins:** **Paris (`Quai Branly`) ↔ Lima (`MNAAHP`)** (`KH0097 ↔ KH0586`, `L = 8`, `0.54%` error); **Pachacamac** all-white twin (`KH0132 ↔ KH0456`, `L = 8`, `4,291` vs. `4,288`, `0.07%` error); **Ica–Pisco** 100% exact (`KH0128 ↔ KH0137`, `L = 10`, `335 = 335`; and `KH0175 ↔ KH0190`, `L = 7`, `96 = 96`); and **Nazca ↔ Ica** reversed (`KH0156 ↔ KH0432`, `L = 9`, matching color transitions).

{{figure: khipu/rosetta_twins}}

## A statistical caution on the 1670 Santa Valley match — and why external Rosetta matches are scarce

Independently decoding `KH0323`–`KH0328` reproduces both the ~133 six-cord groups (`134` raw OKR chunks: `70` verso, `64` recto) and the striking verso-over-recto tribute asymmetry (`465` vs. `291` on first cords; `15,480` vs. `5,683` across all cords).

However, exact combinatorial calibration (`20,000` Monte Carlo draws) exposes a major caveat in the moiety-ratio argument: because six *pachacas* can be split 3-vs-3 in **`10` ways**, **`72.0%`** of random 6-*pachaca* censuses summing to 130 (`52.8%` under overdispersed Dirichlet(0.5)) match Santa's `(70, 63)` verso/recto count as closely as Medrano & Urton (`71/59`, `L1 = 5`), and **`62.3%`** (`44.4%` overdispersed) match as closely as FitzPatrick's revised 2024 grouping (`68/62`, `L1 = 3`). Meanwhile, outside that single published 1670 *revisita*, no open machine-readable corpus of 16th–17th century Andean colonial censuses exists online.

{{figure: khipu/santa_and_census}}

## What this does not settle

- **Archival museum provenance of the 8 twin pairs.** Web searches found no prior published pairing for these 8 pairs (and none carry `DUPLICATE_FLAG` in `khipu.db`), but non-digitized print museum catalogs or field notes should be checked by khipu specialists—especially for `KH0362 ↔ KH0049` (Sweden ↔ Peru) and `KH0192 ↔ KH0470` (Pachacamac ↔ Huacho).
- **Non-prefix summation trees.** Our strict prefix summation scan found zero cord-0 parent–child trees (`0/50,000` null), missing Puruchuco's offset internal summations; sliding-offset summation search remains open.
- **External census matching.** Once Peruvian archival *revisitas* are digitized, our census identifies **157 Rosetta-ready provenanced khipus** led by **Pachacamac (35)**, **Incahuasi (23)**, **Ica (18)**, **Leymebamba (9)**, and **Nazca (9)**.
- **Independent replication.** Code and pinned `khipu.db` hashes are reproducible with zero amendments; second-vendor replication is pending.

Read the full pre-registered [protocol](https://github.com/ejhong/aletheia-lab/blob/main/questions/khipu/protocol.md) and [results](https://github.com/ejhong/aletheia-lab/blob/main/questions/khipu/RESULTS.md).
