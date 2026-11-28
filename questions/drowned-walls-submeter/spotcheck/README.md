# Spot check of `drowned-walls-submeter`

Done on 2026-11-27 by Claude Fable 5.2 (Anthropic) with a Claude Opus 5.5 sub-agent, at Eugene's request. The
study was run by Antigravity (Google DeepMind). A spot check is not a replication. What it found is in
`../RESULTS.md` and `../amendments.md`.

Everything here beyond the rerun was done after the results were known and is exploratory. The scripts import
the study's own detector from `../analysis/run_submeter_scan.py` and do not change it. Every request to an
outside service uses the generic User-Agent `bathymetry-audit/1.0`.

## Files

- `rerun.py`: runs the committed program unchanged, with its data and results folders redirected and its
  User-Agent replaced from outside. Outputs: `out_rerun_stdout.txt`.
- `diff_json.py`: compares two JSON files leaf by leaf.
  - `out_diff_scan_summary.txt`: the rerun against `results/scan_summary.json`. One difference, the run time.
  - `out_diff_manifest_hashes.txt`: the same for `results/manifest_hashes.json`. No difference.
- `controls_seams.py`: for the three wreck controls, where the highest point is and whether any candidate is
  linked to a charted wreck; for the study's 12 planted false steps, whether each was rejected by `SEAM_STEP`,
  never detected, or passed. Output: `out_controls_seams.json`. Result: 9 rejected by `SEAM_STEP`, 2 never
  detected, 1 passed.
- `walls.py`: wall models used by the two scripts below.
  - Smooth ridges.
  - Lines of boulders.
  - The Blinkerwall as published: 1,673 stones, 52.75 m³, 971 m.
  - The same stones in single file.
  - A generous upper bound.

  Stones are half-ellipsoids, rendered on a fine grid and averaged to the grid of the data.
- `sens_huron.py`: plants each model at random places and directions in every Lake Huron tile with at least
  half data and runs the study's detector. Three seeds, four trials per tile.
  - Outputs: `out_sens_huron.json`, `out_sens_huron_stdout.txt`.
  - With a 0.5 m blur standing in for the sonar footprint: `out_sens_huron_footprint0.5m.json`,
    `out_sens_huron_footprint0.5m_stdout.txt`.
- `sens_baltic.py`: the same for the five Baltic test areas, with the study's own untrawled mask.
  - Walls are gridded at 1 m and interpolated to 0.25 m, as the data were made. Their slope is combined with
    the grid's own slope.
  - The study's own planted bump (+12°) is also placed at random.
  - Three seeds, ten trials per area. Outputs: `out_sens_baltic.json`, `out_sens_baltic_stdout.txt`.
- `baltic_geo.py`: extent and centre of each Baltic grid; distance to the Blinkerwall core L0923-07 (Geersen
  and others 2024, Methods: 54.1609° N, 11.4728° E); the munition table's coverage and the nearest pile; image
  modes of the Fehmarn grids. Output: `out_baltic_geo.json`.
- `huron_catalog.py` and `catalog_summary.py`: the NOAA source surveys under each Lake Huron tile, and the
  share of side-by-side pixels with identical values. Output: `out_huron_catalog_summary.json`. The raw
  catalogue reply (about 200 KB) is not kept; `huron_catalog.py` makes it again.
- `fetch_osm.py` and `osm_near.py`: nautical-chart objects from OpenStreetMap's seamark data in a box, and the
  ones nearest a point. Output: `out_osm_kielbay_near.txt`, for the Kiel Bay hit. It lists a charted wreck
  69 m away and foul ground 59 m away.
- `extract_gallery.py`: pulls the six pictures out of `site/figures/drowned-walls-submeter/sonar_gallery.html`.
  Not needed for any number.
- `out_unit_tests.txt`: the study's four unit tests, all passing.

## How to run

From `questions/drowned-walls-submeter/`. Use `python -I` with an environment that has numpy, scipy and
Pillow. Keep downloaded data in its own folder, outside the repository's code folders.

```
# data: Zenodo record 20554225 (Test_Areas.zip, Time_Series.zip) and PANGAEA.988426 (?format=textfile),
# saved as <data>/baltic/Test_Areas.zip, <data>/baltic/Time_Series.zip, <data>/baltic/pangaea_988426_munitions.tab
python -I spotcheck/rerun.py analysis <data> <rerun_results>          # fetches the 87 NOAA tiles itself
python -I spotcheck/diff_json.py results/scan_summary.json <rerun_results>/scan_summary.json
python -I spotcheck/controls_seams.py analysis <data> <rerun_results>/scan_summary.json out_controls_seams.json
python -I spotcheck/sens_huron.py analysis <rerun_results>/scan_summary.json <data>/huron_tiles out_sens_huron.json 3 4
python -I spotcheck/sens_huron.py analysis <rerun_results>/scan_summary.json <data>/huron_tiles out_sens_huron_footprint0.5m.json 3 4 0.5
python -I spotcheck/sens_baltic.py analysis <data>/baltic/Test_Areas.zip out_sens_baltic.json 3 10
python -I spotcheck/baltic_geo.py analysis <data>/baltic out_baltic_geo.json
python -I spotcheck/huron_catalog.py <rerun_results>/scan_summary.json <data>/huron_tiles huron_catalog.json
python -I spotcheck/catalog_summary.py huron_catalog.json <data>/huron_tiles out_huron_catalog_summary.json
python -I spotcheck/fetch_osm.py 54.50 10.15 54.60 10.33 kielbay_seamarks.json
python -I spotcheck/osm_near.py kielbay_seamarks.json 54.553115 10.237327 15
```

`rerun.py` and `sens_huron.py` take a few minutes in all. The rest take seconds.

## Not checked

- **O'Shea and others (2014)**, *PNAS* 111: 6911–6915. The full text could not be fetched. The Drop 45
  description comes from the university's press release. Its dimensions of Lake Huron features come from O'Shea
  and others (2013), *Quaternary International* 297: 36–44.
- **Exact positions.** Those of the Blinkerwall and of Drop 45 are not published, so the distances are
  approximate.
- **Charts.** No official German chart or wreck register was consulted for Kiel Bay; OpenStreetMap is a
  secondary copy of chart data.
- **Geology.** The labels in the first report were not checked against any map.
- **The visual audit** was not redone hit by hit.
- **Fehmarn.** No walls of real size were planted off Fehmarn; the grids there have no physical scale.
- **The stone models are idealised.** Read the rates as orders of magnitude.

## Read for the check

- Geersen and others (2024), *PNAS* 121(8), e2312008121.
- O'Shea and others (2013), *Quaternary International* 297: 36–44.
- University of Michigan press release on O'Shea and others (2014), as reprinted by phys.org (April 2014).
- The Zenodo record 10.5281/zenodo.20554225 (Feldens).
- The EGU26-13394 abstract (Feldens and others).
- The header of PANGAEA.988426.
- NOAA's BAG image service catalogue.
