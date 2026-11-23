#!/usr/bin/env python3
"""The network-variance test of the Global Consciousness Project's data on events fixed by rule (protocol.md).

    python analysis/netvar.py --controls     # before the lock: control windows only, theoretical standardising
    python analysis/netvar.py                # the locked run; writes results/

Run from questions/global-consciousness. Needs numpy (the shared venv: numpy 2.3.5, Python 3.12).
"""
import csv
import datetime
import gzip
import json
import math
import pathlib
import sys

import numpy as np

Q = pathlib.Path(__file__).resolve().parent.parent
DATA = Q / "data"
SD, WINDOW, MIN_TRIALS, MIN_EGGS, MIN_SECONDS = math.sqrt(50.0), 86400, 43200, 5, 43200
EFFECT = 0.33                 # the project's reported mean score per event (7.310 over 500 events)
UTC = datetime.timezone.utc


def read_day(day):
    """One day file -> (first Unix second of the day, egg numbers, array [86400, eggs] of trial sums, NaN where none)."""
    cache = DATA / "cache" / f"{day}.npz"
    if cache.exists():
        z = np.load(cache)
        return int(z["t0"]), z["eggs"].tolist(), z["x"].astype(np.float32)
    t0 = int(datetime.datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=UTC).timestamp())
    eggs, x = None, None
    with gzip.open(DATA / f"basketdata-{day}.csv.gz", "rt") as f:
        for line in f:
            if line.startswith("12,"):
                eggs = [int(e) for e in line.rstrip("\n").split(",")[3:]]
                x = np.full((WINDOW, len(eggs)), np.nan, dtype=np.float32)
            elif line.startswith("13,"):
                p = line.rstrip("\n").split(",")
                i = int(p[1]) - t0
                if 0 <= i < WINDOW:
                    for k, v in enumerate(p[3:3 + len(eggs)]):
                        if v:
                            x[i, k] = float(v)
    cache.parent.mkdir(exist_ok=True)
    np.savez_compressed(cache, t0=t0, eggs=np.array(eggs), x=x)
    return t0, eggs, x


def window(start, reader=read_day):
    """The 86,400 seconds from `start` (a UTC datetime string): (egg numbers, array [86400, eggs]), cleaned of wild trials."""
    s = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    t_start = int(s.timestamp())
    days = sorted({s.strftime("%Y-%m-%d"), (s + datetime.timedelta(seconds=WINDOW - 1)).strftime("%Y-%m-%d")})
    parts = [reader(d) for d in days]
    eggs = sorted({e for _, es, _ in parts for e in es})
    col = {e: k for k, e in enumerate(eggs)}
    out = np.full((WINDOW, len(eggs)), np.nan, dtype=np.float32)
    for t0, es, x in parts:
        lo, hi = max(t_start, t0), min(t_start + WINDOW, t0 + WINDOW)
        if hi > lo:
            out[lo - t_start:hi - t_start, [col[e] for e in es]] = x[lo - t0:hi - t0]
    out[np.abs(out - 100) >= 45] = np.nan
    return eggs, out


def egg_stats(x):
    """Per egg: trials, mean, and mean square about 100."""
    n = (~np.isnan(x)).sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = np.nansum(x, axis=0) / n
        ms = np.nansum((x - 100) ** 2, axis=0) / n
    return n, mean, ms


def passes(n, mean, ms):
    with np.errstate(invalid="ignore", divide="ignore"):
        return (n >= MIN_TRIALS) & (np.abs(mean - 100) / (SD / np.sqrt(n)) <= 5) & (np.abs(ms / 50 - 1) * np.sqrt(n / 2) <= 5)


def score(x, s):
    """The window's score from trial sums x [seconds, eggs] and each egg's standard deviation s. None if too few seconds."""
    z = (x - 100) / s
    n = (~np.isnan(z)).sum(axis=1)
    use = n >= MIN_EGGS
    df = int(use.sum())
    if df < MIN_SECONDS:
        return None
    Z = np.nansum(z[use], axis=1) / np.sqrt(n[use])
    chi2 = float(np.sum(Z.astype(np.float64) ** 2))
    k = 2 / (9 * df)
    return {"z": ((chi2 / df) ** (1 / 3) - (1 - k)) / math.sqrt(k), "chi2": chi2, "df": df, "eggs_median": float(np.median(n[use]))}


def pair(event_start, control_start, reader=read_day):
    """Scores for an event window and its control, each standardised by the other's egg variances."""
    ea, xa = window(event_start, reader)
    eb, xb = window(control_start, reader)
    common = [e for e in ea if e in eb]
    xa, xb = xa[:, [ea.index(e) for e in common]], xb[:, [eb.index(e) for e in common]]
    sa, sb = egg_stats(xa), egg_stats(xb)
    ok = passes(*sa) & passes(*sb)
    out = {"eggs_passing": int(ok.sum()), "eggs_seen": len(set(ea) | set(eb))}
    if ok.sum() < MIN_EGGS:
        return {**out, "event": None, "control": None, "event_theory": None, "control_theory": None}
    xa, xb = xa[:, ok], xb[:, ok]
    s_from_a, s_from_b = np.sqrt(sa[2][ok]), np.sqrt(sb[2][ok])
    return {**out, "event": score(xa, s_from_b), "control": score(xb, s_from_a),
            "event_theory": score(xa, SD), "control_theory": score(xb, SD)}


def combine(zs):
    zs = [z for z in zs if z is not None]
    return {"n": len(zs), "z": sum(zs) / math.sqrt(len(zs)) if zs else None, "mean": sum(zs) / len(zs) if zs else None}


def verdicts(z_all, n, z_controls, z_diff):
    used, z = "the events", z_all
    if abs(z_controls) >= 2.58:
        used, z = "the difference between events and controls (calibration failed)", z_diff
    depart = "departure" if z >= 3.09 else "suggestive" if z >= 1.645 else "no departure"
    size = "smaller than reported" if z <= EFFECT * math.sqrt(n) - 1.645 else "compatible with the reported size"
    return {"departure": depart, "size": size, "based_on": used, "z_used": z, "predicted_at_reported_size": EFFECT * math.sqrt(n)}


def read_events():
    return [r for r in csv.DictReader(open(Q / "events.tsv"), delimiter="\t") if r["in_test"] == "yes"]


def main():
    events = read_events()
    if "--controls" in sys.argv:
        zs = []
        for e in events:
            eggs, x = window(e["control_start_utc"])
            ok = passes(*egg_stats(x))
            r = score(x[:, ok], SD) if ok.sum() >= MIN_EGGS else None
            zs.append(r["z"] if r else None)
            print(f"control of {e['event'][:44]:44s} eggs {int(ok.sum()):3d} of {len(eggs):3d}  score {r['z']:+.2f}  seconds {r['df']}" if r else f"control of {e['event']}: not evaluable", flush=True)
        c = combine(zs)
        print(f"CONTROLS ONLY, theoretical standardising: {c['n']} windows, combined {c['z']:+.2f}, mean {c['mean']:+.3f}, "
              f"sd {np.std([z for z in zs if z is not None], ddof=1):.2f}")
        return
    rows = []
    for e in events:
        r = pair(e["start_utc"], e["control_start_utc"])
        get = lambda k, f="z": (r[k] or {}).get(f)
        rows.append({"kind": e["kind"], "event": e["event"], "start_utc": e["start_utc"], "control_start_utc": e["control_start_utc"],
                     "eggs_passing": r["eggs_passing"], "eggs_seen": r["eggs_seen"], "seconds": get("event", "df"), "control_seconds": get("control", "df"),
                     "z": get("event"), "control_z": get("control"), "z_theory": get("event_theory"), "control_z_theory": get("control_theory")})
        print(f"{e['event'][:50]:50s} eggs {r['eggs_passing']:3d}  event {rows[-1]['z'] if rows[-1]['z'] is None else round(rows[-1]['z'], 2)}  "
              f"control {rows[-1]['control_z'] if rows[-1]['control_z'] is None else round(rows[-1]['control_z'], 2)}", flush=True)
    ok = [r for r in rows if r["z"] is not None and r["control_z"] is not None]

    def summary(sel, a="z", b="control_z"):
        ev, co = combine([r[a] for r in sel]), combine([r[b] for r in sel])
        n = ev["n"]
        diff = (sum(r[a] for r in sel) - sum(r[b] for r in sel)) / math.sqrt(2 * n) if n else None
        return {"events": ev, "controls": co, "difference_z": diff, "verdicts": verdicts(ev["z"], n, co["z"], diff) if n else None}

    big = {q["id"] for q in json.load(open(Q / "sources" / "noaa_earthquakes_2016_2025_deaths_100_or_more.json")) if q["deaths"] >= 1000}
    is_big = lambda r: r["kind"] == "earthquake" and int(r["event"].split("NOAA id ")[1].split(",")[0]) in big
    out = {"events_in_list": len(events), "evaluable": len(ok), "not_evaluable": [r["event"] for r in rows if r not in ok],
           "all": summary(ok), "calendar": summary([r for r in ok if r["kind"] == "calendar"]),
           "earthquake": summary([r for r in ok if r["kind"] == "earthquake"]),
           "earthquakes_1000_deaths": summary([r for r in ok if is_big(r)]),
           "theoretical_standardising": summary([r for r in ok if r["z_theory"] is not None], "z_theory", "control_z_theory")}
    (Q / "results").mkdir(exist_ok=True)
    json.dump(out, open(Q / "results" / "summary.json", "w"), indent=1)
    cols = list(rows[0].keys())
    with open(Q / "results" / "events.tsv", "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join("" if r[c] is None else f"{r[c]:.4f}" if isinstance(r[c], float) else str(r[c]) for c in cols) + "\n")
    v = out["all"]
    print(f"ALL: {v['events']['n']} events, combined {v['events']['z']:+.2f}; controls {v['controls']['z']:+.2f}; difference {v['difference_z']:+.2f}")
    print("VERDICTS:", v["verdicts"])


if __name__ == "__main__":
    main()
