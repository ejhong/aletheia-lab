# Per-site tally of the locked mixing test (delta RMSE < 0 favours cosmic, > 0 volcanic) for the Pillar 1A targets, from results/summary.json. Run: python spotcheck/mixing_tally.py [results/summary.json]
import json
import pathlib
import statistics
import sys

QDIR = pathlib.Path(__file__).resolve().parent.parent
path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else QDIR / "results" / "summary.json"
d = json.loads(path.read_text())["pillar1a_full_hse"]
for key in ("halls_cave", "page_ladson"):
    col = d[key]
    for subset, pred in (("all targets", lambda s: s["is_target"]),
                         ("strict YDB window", lambda s: s["in_ydb_window"]),
                         ("unradiogenic Os", lambda s: s["is_unradiogenic"])):
        t = [s for s in col["samples"] if s.get("has_all6") and pred(s)]
        dl = [s["delta_rmse"] for s in t]
        if not dl:
            continue
        print(f"{col['site']:16s} {subset:18s} n={len(dl):2d}  cosmic-favoured={sum(x < 0 for x in dl):2d}  "
              f"volcanic-favoured={sum(x > 0 for x in dl):2d}  tied(0)={sum(x == 0 for x in dl):2d}  "
              f"median dRMSE={statistics.median(dl):+.4f}")
    classes = {}
    for s in col["samples"]:
        if s.get("nearest_class"):
            classes[s["nearest_class"]] = classes.get(s["nearest_class"], 0) + 1
    print(f"{col['site']:16s} CLR class of every complete sample (targets and background): {classes}")
