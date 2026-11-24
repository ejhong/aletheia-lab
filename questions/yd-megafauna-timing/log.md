# Lab Log — `yd-megafauna-timing` (Issue #116)

## 2026-11-23 — Setup, Blinded Schema Verification, and Protocol Lock
- Branched `q/yd-megafauna-timing` from `origin/main` (`5d3b1a2`) and marked Issue `#116` `status:active`.
- Downloaded primary public datasets into git-ignored `data/`:
  - `data/intcal20.14c` (`IntCal20` reference curve via `rintcal`, SHA-256 `0e03064b...`).
  - `data/broughton2018_s1.xlsx` (Broughton & Weitzel 2018 *Nat. Commun.* 9:5441, CC-BY-4.0, `521` direct megafauna dates, SHA-256 `1cbc3096...`).
  - `data/stewart2021_s1.xlsx` (cross-check table, SHA-256 `6be3b170...`).
  - `19` North American Late-Glacial Neotoma v2 pollen JSONs containing `Sporormiella` (`data/neotoma/ds_*.json`).
- Ran strictly blinded schema/sample-count checks (zero spore curves, decline dates, or calibrated fossil ages inspected):
  - Verified uniform Neotoma schema (`variablename='Sporormiella'`, `units='NISP'`, `elementtype='spore'`) and selected the `11` qualifying calibrated cores (`≥ 10` samples and `≥ 4` nonzero *Sporormiella* in `17–10 ka`).
  - Verified Broughton & Weitzel (2018) spreadsheet footnotes: all rows are Barnosky & Lindsey `Score 11` (`178` conventional `ST`) or `Score 12` (`343` AMS `MS`/`AMS`), aligned `protocol.md` subsets accordingly before locking.
- Wrote `analysis/megafauna_timing.py` and `analysis/test_megafauna.py`; all 4 pre-lock synthetic recovery tests passed (`IntCal20` recovery, synthetic step/ramp *Sporormiella*, `H_impact` forward self-consistency, and Signor–Lipps `OLE`/`GRIWM` unbiasedness).
- Committed pre-lock files (`e521f1d`), ran `python3 scripts/lock.py questions/yd-megafauna-timing` (`protocol.lock` SHA-256 `fd7ae0a9bfae`, `2026-11-24T01:56:12Z`), committed `protocol.lock` on its own (`1fb4220`), passed `scripts/check.py`, and pushed `q/yd-megafauna-timing`.

## 2026-11-23 — Locked Execution, Interactive Figures, and Site Integration
- Executed `python3 questions/yd-megafauna-timing/analysis/megafauna_timing.py` (`seed = 20261123`) with zero amendments.
- Pre-registered verdict: **`staggered_spanning_yd`**:
  - Pillar 1 (*Sporormiella*, 11 cores): `9/9` cores peak before YD (`14,950 BP`, `p = 0.0039`), `9/11` reach half-drop before YD (`14,669 BP`, `+1,773 yr` lead, Wilcoxon `p = 0.0137`), `7/10` step-drop before YD (`13,940 BP`), `6/9` cross `2%` before YD (`14,107 BP`), while `3` cores (CO, TX, IN) linger above `2%` into the Younger Dryas.
  - Pillar 2 (Direct `¹⁴C` on `IntCal20`): direct bone dates surge in `13.5–12.9 ka` (`R_pre = 1.92`) and drop ~10× across `12.8–12.6 ka`, yet `M_yd` (`12.7–11.7 ka`) is `4.95%` on `Score 12` AMS vs `0.73%` `H_impact` 99th-percentile leakage (`6.8×` higher, `0/2,000` sims, `p < 0.0005` across all 6 subsets and Surovell taphonomic correction). `10` gold-standard `Score 12` AMS collagen/dentin dates (5 mammoths, 3 mastodons, 1 giant beaver, 1 short-faced bear) each have `P(< 12,750 BP) > 0.993` (`12,644`–`10,953 cal BP`). On `Score 12` AMS alone, `Equus` (`OLE 13,061`) disappears near/before onset while `Mammuthus` (`OLE 11,852`), `Mammut` (`OLE 11,867`), and `Oreamnos harringtoni` (`OLE 10,333`) persist centuries into the Younger Dryas.
- Generated 5 zero-dependency interactive HTML figures in `site/figures/yd-megafauna-timing/` (`tiles.html`, `verdict.html`, `sporormiella.html`, `radiocarbon.html`, `taxa.html`), all passing `node --check`.
- Wrote `RESULTS.md`, `site/content/yd-megafauna-timing.md`, and updated `site/topics/younger-dryas.md` and `scripts/make_topic_figures.py` to incorporate Issue `#116` into the Younger Dryas topic page.

- **2026-11-24, spot check.** Claude Fable 5.2 (Anthropic), with Claude Opus 5.5 sub-agents, reran this study after it was published and checked its write-up. Findings and corrections are in `RESULTS.md` under "Spot check"; the scripts are in `spotcheck/`. Not replicated by a second vendor; Eugene decided not to for now.
