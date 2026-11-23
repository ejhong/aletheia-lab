#!/usr/bin/env python3
"""Does ammonium rise after every abrupt cooling in Greenland ice, or only after the Younger Dryas onset? (protocol.md)

    python analysis/swell.py control      # before the lock: calcium (dust) only, to test the program on the real files
    python analysis/swell.py              # the locked run; writes results/

Run from questions/cooling-ammonium. Needs numpy (the shared venv: numpy 2.3.5, Python 3.12).
"""
import csv
import json
import math
import pathlib
import sys

import numpy as np

Q = pathlib.Path(__file__).resolve().parent.parent
FILES = {"NGRIP": Q / "data" / "pangaea" / "935814.tab", "NEEM": Q / "data" / "pangaea" / "935831.tab"}
COLUMN = {"ammonium": 4, "calcium": 3, "nitrate": 5, "sodium": 2}
SPAN = (10300, 107620)            # ages compared, years b2k
AFTER, BEFORE = 200, 100          # years after and before an onset


def read_series(core, ion):
    """{age in years b2k (a multiple of 10): value} for one core and ion. A row labelled a covers [a, a+10)."""
    out = {}
    with open(FILES[core], encoding="utf-8") as f:
        for line in f:
            if line.startswith("*/"):
                break
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t") + [""] * 6
            if p[COLUMN[ion]]:
                out[int(round(float(p[0]) * 1000))] = float(p[COLUMN[ion]])
    return out


def read_events():
    return [{"event": r["event"], "age": int(r["age_b2k"]), "kind": r["kind"], "unc": r["definition_uncertainty"]}
            for r in csv.DictReader(open(Q / "events.tsv"), delimiter="\t")]


def coolings(events):
    """The stadial onsets that enter the test, oldest last."""
    ages = [e["age"] for e in events]
    out = []
    for e in events:
        t = e["age"]
        if e["kind"] != "stadial onset" or e["unc"] not in ("4yr", "a", "b"):
            continue
        if any(t < a < t + BEFORE for a in ages) or any(t - AFTER < a < t for a in ages):
            continue
        tr = int(round(t / 10.0)) * 10
        if tr - AFTER < SPAN[0] or tr + BEFORE > SPAN[1]:
            continue
        out.append({**e, "t": tr})
    return out


def bins(series, t, after=AFTER, before=BEFORE):
    """Twenty-year means going outward from t: the lists after (younger) and before (older). None where no row has a value."""
    def mean(a):
        v = [series[x] for x in (a, a + 10) if x in series]
        return sum(v) / len(v) if v else None
    return [mean(t - 20 * k - 20) for k in range(after // 20)], [mean(t + 20 * k) for k in range(before // 20)]


def measures(series, t, after=AFTER, before=BEFORE):
    """The four contrasts at time t, each a natural log of a ratio of means of 20-year bins. None if D cannot be had.

    D: years 40-160 after (bins 2-7) over the 100 years before. The delayed century; this one decides.
    P: the largest bin of the 200 years after, over the median bin before.   R: all 200 years after, over before.
    H: years 40-160 after over years 200-300 after (bins 10-14): does the rise fall back? None unless asked for 300.
    """
    a, b = bins(series, t, max(after, AFTER), before)
    late = a[10:15] if after >= 300 else []
    a = a[:10]
    d = [x for x in a[2:8] if x is not None]
    b2 = [x for x in b if x is not None]
    if len(d) < 5 or 5 * len(b2) < 4 * len(b) or min(d + b2) <= 0:
        return None
    mean = lambda v: sum(v) / len(v)
    out = {"D": math.log(mean(d) / mean(b2)), "delayed_mean": mean(d), "before_mean": mean(b2), "P": None, "R": None, "H": None}
    a2 = [x for x in a if x is not None]
    if len(a2) >= 8 and min(a2) > 0:
        out.update(P=math.log(max(a2) / float(np.median(b2))), R=math.log(mean(a2) / mean(b2)), peak=max(a2),
                   peak_bin_starts_years_after=20 * a.index(max(a2)))
    l2 = [x for x in late if x is not None]
    if len(l2) >= 4 and min(l2) > 0:
        out["H"] = math.log(mean(d) / mean(l2))
    return out


def quiet_times(events, after=AFTER, before=BEFORE):
    """Times on a 20-year grid with no listed event from 300 years after to 200 years before."""
    ages = np.array(sorted(e["age"] for e in events))
    out = []
    for t in range(-(-(SPAN[0] + after) // 20) * 20, SPAN[1] - before + 1, 20):
        i = np.searchsorted(ages, t - 300)
        if i < len(ages) and ages[i] <= t + 200:
            continue
        out.append(t)
    return out


KEYS = ("D", "P", "R")


def analyse(core, ion, events, shift=0, local=None):
    """Every cooling in one core: the measures and their percentiles among quiet times.

    shift moves every onset but GS-1 by that many years (positive = older). local, if given, keeps only the quiet
    times within that many years of the event when working out its percentile (at least 100 are needed).
    """
    series = read_series(core, ion)
    null = [(t, m) for t, m in ((t, measures(series, t)) for t in quiet_times(events)) if m]
    rows = []
    for e in coolings(events):
        t = e["t"] + (0 if e["event"] == "GS-1" else shift)
        m = measures(series, t)
        if not m:
            rows.append({"event": e["event"], "age": e["age"], "unc": e["unc"], "D": None})
            continue
        ref = [n for tq, n in null if local is None or abs(tq - t) <= local]
        for key in KEYS:
            vals = [n[key] for n in ref if n[key] is not None]
            m[key + "_pct"] = float(np.mean([v < m[key] for v in vals])) if m[key] is not None and len(vals) >= 100 else None
        long_cold = not any(e["age"] - 300 < a < e["age"] for a in (x["age"] for x in events))
        m["H"] = measures(series, t, 300)["H"] if long_cold else None
        rows.append({"event": e["event"], "age": e["age"], "unc": e["unc"], **m})
    return rows, [n for _, n in null]


def verdicts(per_core, key="D"):
    """Q1: is a rise general among the other coolings? Q2: where does GS-1 rank among all of them?"""
    q1, q2 = {}, {}
    for core, rows in per_core.items():
        ok = [r for r in rows if r.get(key) is not None and r.get(key + "_pct") is not None]
        others = [r for r in ok if r["event"] != "GS-1"]
        rises = [r for r in others if r[key] > 0 and r[key + "_pct"] >= 0.75]
        k = len(rises)
        vals = [r[key] for r in others]
        q1[core] = {"others": len(others), "in_top_quarter": k, "share": k / len(others), "positive": sum(1 for v in vals if v > 0),
                    "median": float(np.median(vals)), "median_percentile": float(np.median([r[key + "_pct"] for r in others])),
                    "passing": sorted(r["event"] for r in rises),
                    "not_evaluable": sorted(r["event"] for r in rows if r not in ok)}
        yd = next((r for r in ok if r["event"] == "GS-1"), None)
        if yd:
            ranked = sorted((r[key] for r in ok), reverse=True)
            rank = 1 + sum(1 for v in ranked if v > yd[key])
            q2[core] = {"rank": rank, "of": len(ok), "value": yd[key], "percentile_vs_quiet": yd[key + "_pct"],
                        "largest_other": max(vals), "median_other": float(np.median(vals))}
    cores = list(per_core)
    both = set.intersection(*[set(q1[c]["passing"]) for c in cores])
    either = set.union(*[set(q1[c]["passing"]) for c in cores])
    if all(v["share"] >= 2 / 3 for v in q1.values()):
        general = "general"
    elif all(v["share"] <= 1 / 3 for v in q1.values()):
        general = "not seen"
    else:
        general = "mixed"
    if len(q2) < len(per_core):
        special = "not testable"
    elif all(v["rank"] == 1 for v in q2.values()):
        special = "the largest"
    elif all(v["rank"] <= math.ceil(v["of"] / 4) for v in q2.values()):
        special = "among the largest"
    else:
        special = "not among the largest"
    return {"general": general, "younger_dryas": special, "q1": q1, "q2": q2,
            "paired": {"both": sorted(both), "one_core_only": sorted(either - both)}}


def profiles(events):
    """Twenty-year means from 300 years before to 300 years after every cooling, for the figures and the reader."""
    out = []
    for ion in ("ammonium", "calcium"):
        for core in FILES:
            series = read_series(core, ion)
            for e in coolings(events):
                a, b = bins(series, e["t"], 300, 300)
                for k, v in enumerate(b):
                    out.append((ion, core, e["event"], -(20 * k + 20), v))
                for k, v in enumerate(a):
                    out.append((ion, core, e["event"], 20 * k, v))
    return out


def main():
    events = read_events()
    assert len(events) == 111 and sum(1 for e in events if e["kind"] == "stadial onset") == 35
    control = sys.argv[1:] == ["control"]
    ions = ["calcium"] if control else ["ammonium", "calcium", "nitrate", "sodium"]
    out = {"coolings": [e["event"] for e in coolings(events)], "quiet_times": len(quiet_times(events))}
    print(len(out["coolings"]), "coolings:", " ".join(out["coolings"]))
    print(out["quiet_times"], "quiet times")
    for ion in ions:
        per_core, nulls = {}, {}
        for core in FILES:
            per_core[core], null = analyse(core, ion, events)
            nulls[core] = {k: [float(np.percentile([n[k] for n in null if n[k] is not None], q)) for q in (5, 25, 50, 75, 95)] for k in KEYS} | {"n": len(null)}
            d = np.array([n["D"] for n in null])
            q75 = np.percentile(d, 75)
            nulls[core]["share_caught_if_raised_by"] = {str(f): float(np.mean((d + math.log(f) >= q75) & (d + math.log(f) > 0))) for f in (1.25, 1.5, 2, 3)}
        out[ion] = {"events": per_core, "quiet": nulls, **{k: verdicts(per_core, k) for k in KEYS}}
        v = out[ion]["D"]
        print(f"{ion}: delayed rise after cooling is '{v['general']}'; Younger Dryas '{v['younger_dryas']}'; in both cores {len(v['paired']['both'])}, one only {len(v['paired']['one_core_only'])}")
        for core in FILES:
            q = v["q1"][core]
            print(f"  {core}: quiet times {nulls[core]['n']}; others in top quarter {q['in_top_quarter']}/{q['others']}, positive {q['positive']}, "
                  f"median D {q['median']:+.2f}; GS-1 D {v['q2'].get(core, {}).get('value', float('nan')):+.2f}, rank {v['q2'].get(core, {}).get('rank')}/{v['q2'].get(core, {}).get('of')}")
    if control:
        return
    side = {"onset_moved": {}, "local_reference": None}
    for shift in (-40, -20, 20, 40):
        per_core = {core: analyse(core, "ammonium", events, shift)[0] for core in FILES}
        v = verdicts(per_core, "D")
        side["onset_moved"][str(shift)] = {"general": v["general"], "younger_dryas": v["younger_dryas"],
                                           "in_top_quarter": {c: [v["q1"][c]["in_top_quarter"], v["q1"][c]["others"]] for c in FILES},
                                           "rank": {c: v["q2"][c]["rank"] for c in v["q2"]}}
    per_core = {core: analyse(core, "ammonium", events, 0, 10000)[0] for core in FILES}
    v = verdicts(per_core, "D")
    side["local_reference"] = {"general": v["general"], "younger_dryas": v["younger_dryas"],
                               "in_top_quarter": {c: [v["q1"][c]["in_top_quarter"], v["q1"][c]["others"]] for c in FILES}}
    extra = [e for e in events if e["event"] in ("GI-1d", "GI-1b", "Start of 11.4 ka BP event") or (e["kind"] == "stadial onset" and e["event"] not in out["coolings"])]
    side["other_coolings_not_in_the_test"] = {}
    for core in FILES:
        series = read_series(core, "ammonium")
        null = [m["D"] for m in (measures(series, t) for t in quiet_times(events)) if m]
        rows = []
        for e in extra:
            m = measures(series, int(round(e["age"] / 10.0)) * 10)
            if m:
                rows.append({"event": e["event"], "age": e["age"], "unc": e["unc"], "D": m["D"], "D_pct": float(np.mean([n < m["D"] for n in null]))})
        side["other_coolings_not_in_the_test"][core] = rows
    out["alongside"] = side
    (Q / "results").mkdir(exist_ok=True)
    json.dump(out, open(Q / "results" / "summary.json", "w"), indent=1)
    fmt = lambda x: "" if x is None else f"{x:.4f}" if isinstance(x, float) else str(x)
    with open(Q / "results" / "events.tsv", "w") as f:
        cols = ["ion", "core", "event", "age", "unc", "D", "D_pct", "P", "P_pct", "R", "R_pct", "H", "delayed_mean", "before_mean", "peak", "peak_bin_starts_years_after"]
        f.write("\t".join(cols) + "\n")
        for ion in ions:
            for core in FILES:
                for r in out[ion]["events"][core]:
                    f.write("\t".join(fmt({"ion": ion, "core": core, **r}.get(c)) for c in cols) + "\n")
    with open(Q / "results" / "profiles.tsv", "w") as f:
        f.write("ion\tcore\tevent\tbin_starts_years_after_onset\tmean\n")
        for row in profiles(events):
            f.write("\t".join(fmt(x) for x in row) + "\n")


if __name__ == "__main__":
    main()
