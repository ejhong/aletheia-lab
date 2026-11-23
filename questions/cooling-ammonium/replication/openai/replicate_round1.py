# Interpretation and output choices:
# - Isolation and quiet-time vetoes use the published table (all event kinds).
#   For H, measure 300 years from the analysis onset (12,900 for GS-1) and
#   exclude the cooling's own row when checking for another event.
# - Weight available decades equally within bins, then available bins equally
#   within windows. An absent decade is like an empty field. Do not discard a
#   non-positive decade before binning: positivity is tested on bin means.
# - Apply the positivity rule to every present bin in each required window,
#   even for a maximum or median. P/R require 4 before bins; H requires 5
#   delayed bins. Test event measures independently (H needs no before bins).
#   For quiet times, first require D, then filter separately for each measure.
# - Use ordinary even-sample medians, natural logs, fractional percentiles,
#   and strict comparisons without rounding or a tie tolerance.
# - Preserve event-table order. Compute H_pct but omit it from the TSV per
#   FORMAT.md. Send companion comparisons and calcium checks to stdout only.
#   The cross-core pass listing includes GS-1; report incomplete coverage
#   separately rather than interpreting a missing D as a failed rise.
# - If either general-rise denominator is zero, neither directional verdict
#   is established ("mixed"). If GS-1 lacks D, use the protocol's "not testable"
#   and null for its unavailable rank. An evaluable D with no quiet reference
#   would prevent applying the rise rule; report an error in that case.

import csv
import json
import sys
from bisect import bisect_left, bisect_right
from math import isclose, isfinite, log
from pathlib import Path
from statistics import fmean, median

FILES = {"NGRIP": "data/pangaea/935814.tab", "NEEM": "data/pangaea/935831.tab"}
COL = {"ammonium": 4, "calcium": 3}
FIELDS = "ion core event D D_pct P P_pct R R_pct H".split()
YD = "GS-1"


def bin20(decades):
    groups = {}
    for age, value in decades.items():
        groups.setdefault(age - age % 20, []).append(value)
    return {age: fmean(values) for age, values in groups.items()}


def load_core(path):
    decades = {ion: {} for ion in COL}
    seen = set()
    with open(path, encoding="utf-8-sig", newline="") as f:
        for line in f:
            if line.startswith("*/"):
                break
        else:
            raise ValueError(f"{path}: missing header terminator")
        next(f)  # column names
        for row in csv.reader(f, delimiter="\t"):
            if not row or not any(s.strip() for s in row):
                continue
            row += [""] * (6 - len(row))
            age = round(float(row[0]) * 1000)
            if age % 10 or age in seen:
                raise ValueError(f"{path}: invalid or duplicate decade {age}")
            seen.add(age)
            for ion, col in COL.items():
                if s := row[col].strip():
                    value = float(s)
                    if not isfinite(value):
                        raise ValueError(f"{path}: nonfinite {ion} at {age}")
                    decades[ion][age] = value
    return {ion: bin20(values) for ion, values in decades.items()}


def load_events():
    with open("events.tsv", encoding="utf-8-sig", newline="") as f:
        return [(r["event"], int(r["age_b2k"]), r["kind"], r["definition_uncertainty"])
                for r in csv.DictReader(f, delimiter="\t")]


def select(events):
    selected = []
    for name, age, kind, unc in events:
        if kind != "stadial onset" or (unc not in ("a", "b") and name != YD):
            continue
        if age - 200 < 10300 or age + 100 > 107620:
            continue
        if any(age - 200 < a < age or age < a < age + 100 for _, a, _, _ in events):
            continue
        t = 12900 if name == YD else age
        if t % 20:
            raise ValueError(f"off-grid selected onset: {name}")
        h_ok = not any(n != name and t - 300 < a < t for n, a, _, _ in events)
        selected.append((name, t, h_ok))
    return selected


def quiet(t, sorted_ages):
    return bisect_left(sorted_ages, t - 300) == bisect_right(sorted_ages, t + 200)


def window(values, minimum):
    x = [v for v in values if v is not None]
    return x if len(x) >= minimum and min(x) > 0 else None


def ratio(x, y, numerator=fmean, denominator=fmean):
    return log(numerator(x) / denominator(y)) if x and y else None


def measures(bins, t, h_ok=True):
    before = window((bins.get(t + 20*k) for k in range(5)), 4)
    after = [bins.get(t - 20*(k+1)) for k in range(15)]
    delayed = window(after[2:8], 5)
    early = window(after[:10], 8)
    late = window(after[10:], 4) if h_ok else None
    return {"D": ratio(delayed, before), "P": ratio(early, before, max, median),
            "R": ratio(early, before), "H": ratio(delayed, late)}


def references(bins, times):
    ref = {key: [] for key in "DPRH"}
    for t in times:
        m = measures(bins, t)
        if m["D"] is not None:
            for key, v in m.items():
                if v is not None:
                    ref[key].append(v)
    for seq in ref.values():
        seq.sort()
    return ref


def percentile(v, seq):
    return bisect_left(seq, v) / len(seq) if v is not None and seq else None


def general(counts):
    if all(n and 3*h >= 2*n for h, n in counts):
        return "general"
    if all(n and 3*h <= n for h, n in counts):
        return "not seen"
    return "mixed"


def yd_verdict(ranks, sizes):
    if None in ranks.values():
        return "not testable"
    if all(r == 1 for r in ranks.values()):
        return "the largest"
    if all(r <= (sizes[c] + 3)//4 for c, r in ranks.items()):
        return "among the largest"
    return "not among the largest"


def decide(scores, names):
    ranks, sizes, counts, by_core, passes = {}, {}, {}, {}, {}
    for core, rows in scores.items():
        ds = {e: d for e, (d, _) in rows.items() if d is not None}
        if any(rows[e][1] is None for e in ds):
            raise ValueError(f"{core}: no quiet reference for evaluable D")
        hits = {e for e, d in ds.items() if d > 0 and rows[e][1] >= 0.75}
        passes[core] = hits
        others = [d for e, d in ds.items() if e != YD]
        counts[core] = (len(hits - {YD}), len(others))
        sizes[core] = len(ds)
        y = ds.get(YD)
        ranks[core] = None if y is None else 1 + sum(d > y for d in others)
        by_core[core] = {"GS-1_D": y, "largest_other_D": max(others, default=None),
                         "median_other_D": median(others) if others else None,
                         "other_rises_of_evaluable": counts[core],
                         "not_evaluable": [e for e in names if e not in ds]}
    groups = {k: [] for k in ("both", "NGRIP only", "NEEM only", "neither", "incomplete")}
    for e in names:
        hit = [c for c in scores if e in passes[c]]
        if any(rows[e][0] is None for rows in scores.values()):
            key = "incomplete"
        else:
            key = ("both" if len(hit) == 2 else hit[0] + " only" if hit else "neither")
        groups[key].append(e)
    decisions = {"general": general(counts.values()), "younger_dryas": yd_verdict(ranks, sizes),
                 "rank": ranks}
    return decisions, {"by_core": by_core, "shows_rise": groups}


def checks():
    assert bin20({-10: 5, 0: 1, 10: 3, 30: 6}) == {-20: 5, 0: 2, 20: 6}
    b = {20*k: 2 for k in range(5)}
    b.update({-20*(k+1): (8 if k == 0 else 4 if k < 10 else 1) for k in range(15)})
    b[80] = 7  # baseline mean 3, median 2
    m = measures(b, 0)
    for k, r in zip("DPRH", (4/3, 4, 4.4/3, 4)):
        assert isclose(m[k], log(r))
    assert measures(b, 0, False)["H"] is None
    del b[80], b[-60], b[-220]
    assert all(v is not None for v in measures(b, 0).values())
    del b[-240]
    assert measures(b, 0)["H"] is None
    del b[-80]
    m = measures(b, 0)
    assert m["D"] is None and m["P"] is not None and m["R"] is not None
    del b[-100]
    assert measures(b, 0)["P"] is None
    assert window([1, 0, 1, 1, None], 4) is None and window([2]*3, 4) is None
    s = [("S", 20000, "stadial onset", "a"), ("A", 19800, "other", ""),
         ("B", 20100, "other", ""), ("X", 40000, "stadial onset", "f")]
    assert select(s) == [("S", 20000, False)]
    assert not select(s + [("C", 19801, "other", "")])
    assert quiet(20000, [19699, 20201])
    assert not quiet(20000, [19700]) and not quiet(20000, [20200])
    assert percentile(2, [1, 2, 2, 4]) == 0.25
    for hits, verdict in [((2, 3), "general"), ((1, 0), "not seen"), ((2, 1), "mixed")]:
        assert general([(h, 3) for h in hits]) == verdict
    for r, v in [(1, "the largest"), (2, "among the largest"),
                 (3, "not among the largest"), (None, "not testable")]:
        assert yd_verdict({"a": 1, "b": r}, {"a": 5, "b": 5}) == v


def main(out):
    checks()
    events = load_events()
    selected = select(events)
    names = [name for name, _, _ in selected]
    ages = sorted(a for _, a, _, _ in events)
    times = [t for t in range(10500, 107521, 20) if quiet(t, ages)]
    cores = {c: load_core(path) for c, path in FILES.items()}
    sizes = {ion: {} for ion in COL}
    scores = {ion: {} for ion in COL}
    out.mkdir(parents=True, exist_ok=True)
    with (out / "events.tsv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, FIELDS, delimiter="\t", lineterminator="\n",
                                extrasaction="ignore")
        writer.writeheader()
        for ion in COL:
            for core, data in cores.items():
                bins = data[ion]
                ref = references(bins, times)
                sizes[ion][core] = len(ref["D"])
                rows = scores[ion][core] = {}
                for name, t, h_ok in selected:
                    m = measures(bins, t, h_ok)
                    pct = {k + "_pct": percentile(v, ref[k]) for k, v in m.items()}
                    writer.writerow(dict(ion=ion, core=core, event=name) | m | pct)
                    rows[name] = (m["D"], pct["D_pct"])
    decisions, companion = decide(scores["ammonium"], names)
    summary = {"coolings": names, "quiet_times": sizes} | decisions
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    ca, ca_detail = decide(scores["calcium"], names)
    print(json.dumps({"ammonium": companion, "calcium_control": ca | ca_detail}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python replicate.py OUTDIR")
    main(Path(sys.argv[1]))
