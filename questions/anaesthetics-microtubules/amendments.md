# Amendments — `anaesthetics-microtubules`

## Amendment 1 — 2026-11-23 (pre-results operational runtime adjustment)

- **What changed:** Reduced AutoDock Vina search `--exhaustiveness` from `16` to `4` in `analysis/dock_anaesthetics.py`. All 8 protein structures, all 24 binding-site boxes (`18 × 18 × 18 Å`), all 35 ligands, both scoring functions (`vina` and `vinardo`), fixed seed (`20261123`), and all statistical tests and verdict criteria remain **100% unchanged**.
- **Why:** On the 2-CPU virtual machine, the first batch (`tubulin_1jff:site_1`, 35 ligands at `exhaustiveness = 16`) took ~155 s per pocket-scoring run, projecting >2 hours for all 48 batches (`1,680` dockings). Convergence benchmarking strictly on the pre-lock crystallographic positive controls showed identical or near-identical top-mode affinities across `exhaustiveness = 4, 8, 16` because the panel consists of small, low-rotamer volatile molecules (`3–18` heavy atoms):
  - `1E7B + halothane`: `−4.456` (`ex=4`), `−4.456` (`ex=8`), `−4.456 kcal/mol` (`ex=16`) — `0.000 kcal/mol` difference.
  - `3P4W + desflurane`: `−5.503` (`ex=4`), `−5.486` (`ex=8`), `−5.492 kcal/mol` (`ex=16`) — `0.011 kcal/mol` difference.
- **Blinding confirmation:** The initial `exhaustiveness = 16` run was cancelled during the first pocket and its partial output directory (`data/dock_work/out/`) was deleted without inspecting any affinities or computing any correlations or comparisons. This amendment was written and committed *before* running the amended docking.
