# Replication of yd-platinum-volcanism by a second vendor

Claude Fable 5.2 (Anthropic), 23 November 2026, directed by Eugene. The original run was by Antigravity (Google
DeepMind).

Two programs were written from `protocol.md` alone, without using `analysis/ptvolc.py`, and run on files
downloaded afresh from the URLs in `MANIFEST.md`. Every file matched the manifest's SHA-256 hash.

    python3 -I pt_rep.py <data dir> > output_within_core.json
    python  -I volc_rep.py "<Supplementary tables.xls>" "<Bipolar supplementary tables ... .xlsx>" ../../events.tsv > output_dating_and_eruptions.json

`volc_rep.py` needs `xlrd==2.0.1` to read the `.xls` tables of Lin et al. 2022.

## Result: every number checked is reproduced

| Measure | Original | This replication |
|---|---|---|
| Platinum onset on the common timescale (Svensson 2020 tie points) | 12,869.9; 26.1 years after the cold began | 12,869.9; 26.1 |
| Platinum peak | 12,864.1; 31.9 years after | 12,864.1; 31.9 |
| Tie points either side | 1708.64 m and 1713.915 m | the same |
| Cross-check (Rasmussen 2008 table) | 17.6 and 23.2 years after | 17.6 and 23.2 |
| Largest step in GISP2 oxygen isotopes | 1710.81 m | between 1710.47 and 1711.14 m |
| Largest step in dust and in sea salt | 1709.90 m and 1710.90 m | the same |
| Depth where cooling is first clear by the rule | 1709.91 m | 1709.91 m |
| Sulphate threshold and spikes | 236.9 ppb; at 1708.65, 1713.9, 1718.7 m | the same |
| Greenland sulphate in the 150 years before | 595.9 kg/km², rank 12 of 338 | 595.9, rank 12 of 338 |
| Bipolar aerosol loading in the 150 years before | 526.6 Tg, rank 3 of 284 | 526.6, rank 3 of 284 |
| Sulphate before 19 coolings against random times | p = 0.35 (50 yr), 0.93 (150 yr) | p = 0.35, 0.92 (own random draws) |

Both locked verdicts follow: platinum timing "ambiguous / within uncertainty"; volcanism "unusually strong
volcanic cluster".

## Checks the protocol did not ask for

Exploratory, made after the result was known.

- **Against its neighbours only.** More eruptions are recorded per thousand years in the younger ice (33 against
  19 in the Greenland list; 2.8 against 1.8 in the bipolar list), whether from real change or easier detection.
  Among the 49 windows younger than 16,500 years, the Greenland sulphate total ranks 6th, which is high but not in
  the top 5%. The bipolar loading ranks 1st of 48.
- **Size, not number.** By count of Greenland eruptions the window is ordinary (4 eruptions; 74th of 338). Two
  very large ones make the total.
- **The bipolar list is sparse.** 208 of its 284 windows hold no matched eruption, and the list marks these four as
  "Onset YD 4 spikes". The years around the Younger Dryas are the most closely studied in the record, so a
  matched eruption is more likely to be found there than elsewhere.

## Review notes

1. **The dating is good to about ten years.** The two tie points used are 5.3 m and 162 years apart and straddle
   the onset, where snowfall dropped; a straight line between them is an approximation. The two routes give 26
   and 18 years. "Roughly twenty to thirty years after the defined start" is as much as the method supports.
2. **Why the timing verdict is "ambiguous".** The rule asked for the largest step in the core to lie below the
   platinum. Because this cooling began slowly (#75), its largest step lies 40 to 70 years later, above the
   platinum. So the platinum falls after the defined start and before most of the fall. The rule could hardly
   have returned "post-dates" for a cooling of this shape.
3. **No sulphate at the platinum layer** (at most 91 ppb against a threshold of 237). That does not favour an
   ordinary sulphur-rich eruption as the platinum's source. The study does not test what the source was.
4. **A heavy run of eruptions before the cold is published work** (Abbott et al. 2021, seen in abstract before the
   lock; Lin et al. 2022 is from the same group). This study confirms it by a fixed rule on their catalogue. It is
   not an independent discovery, and the 150-year window was chosen knowing of it.
5. **A coincidence is not a cause.** The study's own test finds no tendency for sulphate to run high before the
   other 18 coolings.
6. **Process.** Lock one second after the protocol commit, results four minutes later; no review by another
   vendor before the lock; `xlrd` is used but its version is not pinned in the manifest; the model is not named.
