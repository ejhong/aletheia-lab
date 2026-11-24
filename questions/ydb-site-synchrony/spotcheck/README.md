# Spot-check of ydb-site-synchrony (#113)

An independent read of this study by Claude (Anthropic), Opus 5.5, on 2026-11-24, directed by Eugene. It is a sensitivity check, not a replication: it reruns no IntCal20 calibration or simulation.

- `spotcheck.py` reads only the study's committed `../results/pillar1_dates.csv` and `../results/pillar2_sites.csv`. It recomputes Ward–Wilson T for the 9-site panels under other reasonable choices: each site's share of T, leave-one-site-out, other Arlington Canyon values, pooled errors widened to their internal scatter, and only the five sites Kennett 2015 marks as dated on the proxy layer. It also gives the calibrated-median span without Blackwater Draw, the placebo-year overlap and W_50 / W_80 at 1-year steps, and a table on the four Clovis-occupation sites.
- `output.txt` is what it prints. Rerun with `.venv/bin/python questions/ydb-site-synchrony/spotcheck/spotcheck.py` from the repo root and diff.
- Every p-value is the analytic chi-square p of T (df = n − 1). None is the study's simulated p_T.
- Two values are typed in from the papers, with locators in the script:
  - Kennett et al. 2008 (*QSR* 27:2528–2543): the Fig. 4 caption gives 11,060 ± 40 ¹⁴C BP from five lowest-layer dates, and the Table 4 footnote f lists the dates excluded as old wood.
  - Waters & Stafford 2007 (*Science* 315:1122), Table 1: the section headings.
- The Kennett 2015 "date on proxies" flag is as the study parsed it from the Fig. 2 text layer. I checked it against that text, not against the rendered figure.
- The full spot-check, which reran the study pipeline on re-downloaded data (outputs byte-identical), is reported in the PR or conversation that added this folder.
