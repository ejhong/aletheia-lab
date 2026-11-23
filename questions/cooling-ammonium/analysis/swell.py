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
COLUMN = {"ammonium": 4, "calcium": 3}
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
    """P = ln(largest 20-year mean after / median 20-year mean before); R = ln(mean after / mean before). None if too little data."""
    a, b = bins(series, t, after, before)
    a2, b2 = [x for x in a if x is not None], [x for x in b if x is not None]
    if 5 * len(a2) < 4 * len(a) or 5 * len(b2) < 4 * len(b) or min(a2 + b2) <= 0:
        return None
    return {"P": math.log(max(a2) / float(np.median(b2))), "R": math.log((sum(a2) / len(a2)) / (sum(b2) / len(b2))),
            "peak": max(a2), "peak_years_after": 20 * a.index(max(a2)) + 10, "before_median": float(np.median(b2)),
            "after_mean": sum(a2) / len(a2), "before_mean": sum(b2) / len(b2)}


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


def binom_tail(k, n, p=0.25):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def analyse(core, ion, events, after=AFTER):
    series = read_series(core, ion)
    null = [m for m in (measures(series, t, after) for t in quiet_times(events, after)) if m]
    rows = []
    for e in coolings(events):
        if after > AFTER and any(e["age"] - after < a < e["age"] for a in (x["age"] for x in events)):
            continue
        m = measures(series, e["t"], after)
        if m:
            for key in ("P", "R"):
                m[key + "_pct"] = float(np.mean([n[key] < m[key] for n in null]))
            rows.append({"event": e["event"], "age": e["age"], "unc": e["unc"], **m})
    return rows, null


def verdicts(per_core, key="P"):
    """Q1: is a rise general among the other coolings? Q2: where does GS-1 rank among all of them?"""
    q1, q2 = {}, {}
    for core, rows in per_core.items():
        others = [r for r in rows if r["event"] != "GS-1"]
        k = sum(1 for r in others if r[key + "_pct"] >= 0.75)
        q1[core] = {"others": len(others), "in_top_quarter": k, "share": k / len(others), "binomial_p": binom_tail(k, len(others)),
                    "median_percentile": float(np.median([r[key + "_pct"] for r in others]))}
        yd = next((r for r in rows if r["event"] == "GS-1"), None)
        if yd:
            q2[core] = {"rank": 1 + sum(1 for r in rows if r[key] > yd[key]), "of": len(rows), "value": yd[key], "percentile_vs_quiet": yd[key + "_pct"]}
    if all(v["share"] >= 2 / 3 for v in q1.values()):
        general = "general"
    elif all(v["binomial_p"] < 0.05 for v in q1.values()):
        general = "often"
    else:
        general = "not seen"
    if len(q2) < len(per_core):
        special = "not testable"
    elif all(v["rank"] == 1 for v in q2.values()):
        special = "stands out"
    elif all(v["rank"] <= math.ceil(v["of"] / 4) for v in q2.values()):
        special = "among the largest"
    else:
        special = "ordinary among coolings"
    return {"general": general, "younger_dryas": special, "q1": q1, "q2": q2}


def main():
    events = read_events()
    assert len(events) == 111 and sum(1 for e in events if e["kind"] == "stadial onset") == 35
    control = sys.argv[1:] == ["control"]
    ions = ["calcium"] if control else ["ammonium", "calcium"]
    out = {"coolings": [e["event"] for e in coolings(events)], "quiet_times": len(quiet_times(events))}
    print(len(out["coolings"]), "coolings:", " ".join(out["coolings"]))
    print(out["quiet_times"], "quiet times")
    for ion in ions:
        per_core, nulls = {}, {}
        for core in FILES:
            per_core[core], null = analyse(core, ion, events)
            nulls[core] = {k: [float(np.percentile([n[k] for n in null], q)) for q in (5, 25, 50, 75, 95)] for k in ("P", "R")} | {"n": len(null)}
        out[ion] = {"events": per_core, "quiet": nulls, "P": verdicts(per_core, "P"), "R": verdicts(per_core, "R")}
        v = out[ion]["P"]
        print(f"{ion}: rise after cooling is '{v['general']}'; Younger Dryas '{v['younger_dryas']}'")
        for core in FILES:
            print(f"  {core}: quiet times {nulls[core]['n']}; others in top quarter {v['q1'][core]['in_top_quarter']}/{v['q1'][core]['others']} "
                  f"(p {v['q1'][core]['binomial_p']:.2g}), median percentile {v['q1'][core]['median_percentile']:.2f}; GS-1 rank {v['q2'].get(core, {}).get('rank')}/{v['q2'].get(core, {}).get('of')}")
    if control:
        return
    wide = {}
    for ion in ions:
        per_core = {core: analyse(core, ion, events, 300)[0] for core in FILES}
        wide[ion] = {"events": per_core, "P": verdicts(per_core, "P"), "R": verdicts(per_core, "R")}
    out["after_300_years"] = wide
    extra = [e for e in events if e["event"] in ("GI-1d", "GI-1b", "Start of 11.4 ka BP event") or (e["kind"] == "stadial onset" and e["event"] not in out["coolings"])]
    out["other_coolings_not_in_the_test"] = {}
    for core in FILES:
        series = read_series(core, "ammonium")
        null = [m for m in (measures(series, t) for t in quiet_times(events)) if m]
        rows = []
        for e in extra:
            m = measures(series, int(round(e["age"] / 10.0)) * 10)
            if m:
                rows.append({"event": e["event"], "age": e["age"], "unc": e["unc"], "P": m["P"], "R": m["R"],
                             "P_pct": float(np.mean([n["P"] < m["P"] for n in null])), "R_pct": float(np.mean([n["R"] < m["R"] for n in null]))})
        out["other_coolings_not_in_the_test"][core] = rows
    (Q / "results").mkdir(exist_ok=True)
    json.dump(out, open(Q / "results" / "summary.json", "w"), indent=1)
    with open(Q / "results" / "events.tsv", "w") as f:
        cols = ["ion", "core", "event", "age", "unc", "P", "P_pct", "R", "R_pct", "peak", "peak_years_after", "before_median", "after_mean", "before_mean"]
        f.write("\t".join(cols) + "\n")
        for ion in ions:
            for core in FILES:
                for r in out[ion]["events"][core]:
                    f.write("\t".join(f"{r[c]:.4f}" if isinstance(r.get(c), float) else str({"ion": ion, "core": core, **r}[c]) for c in cols) + "\n")


if __name__ == "__main__":
    main()
