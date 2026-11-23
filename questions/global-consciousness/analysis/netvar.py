#!/usr/bin/env python3
"""The network-variance test of the Global Consciousness Project's data on events fixed by rule (protocol.md).

    python analysis/netvar.py                # the locked run; writes results/
    python analysis/validate.py              # before the lock: the project's own published events of 2011-2015

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
SD, WINDOW, MIN_TRIALS, MIN_EGGS, MIN_SECONDS, REF_TRIALS = math.sqrt(50.0), 86400, 43200, 5, 69120, 86400
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
                assert eggs is None, f"{day}: more than one line of egg numbers"
                eggs = [int(e) for e in line.rstrip("\n").split(",")[3:]]
                assert len(set(eggs)) == len(eggs), f"{day}: an egg number is repeated"
                x = np.full((WINDOW, len(eggs)), np.nan, dtype=np.float32)
            elif line.startswith("13,"):
                p = line.rstrip("\n").split(",")
                i = int(p[1]) - t0
                assert 0 <= i < WINDOW, f"{day}: a second outside the day"
                assert len(p) <= 3 + len(eggs), f"{day}: more fields than eggs"
                if True:
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


def cross_part(x, s):
    """The part of the window's chi-square that comes from pairs of eggs moving together, as a standard score."""
    z = ((x - 100) / s).astype(np.float64)
    n = (~np.isnan(z)).sum(axis=1)
    use = n >= MIN_EGGS
    zz, n = z[use], n[use]
    total = np.nansum(zz, axis=1) ** 2 / n - np.nansum(zz ** 2, axis=1) / n
    return float(total.sum() / math.sqrt(np.sum(2.0 * (n - 1) / n)))


def year_variances(controls, reader=read_day):
    """For every control window: each egg's number of trials and sum of squares about 100. {start: {egg: (n, sumsq)}}."""
    out = {}
    for start in controls:
        eggs, x = window(start, reader)
        n = (~np.isnan(x)).sum(axis=0)
        ss = np.nansum((x.astype(np.float64) - 100) ** 2, axis=0)
        out[start] = {e: (int(a), float(b)) for e, a, b in zip(eggs, n, ss)}
    return out


def score_window(start, pool, reader=read_day):
    """Score one window. pool: the control windows whose egg variances may be used (never the window itself)."""
    eggs, x = window(start, reader)
    n_ref = np.array([sum(p.get(e, (0, 0.0))[0] for p in pool) for e in eggs])
    ss_ref = np.array([sum(p.get(e, (0, 0.0))[1] for p in pool) for e in eggs])
    ok = passes(*egg_stats(x)) & (n_ref >= REF_TRIALS)
    out = {"eggs_passing": int(ok.sum()), "eggs_seen": len(eggs), "seconds_with_data": int((~np.isnan(x)).any(axis=1).sum())}
    if ok.sum() < MIN_EGGS:
        return {**out, "main": None, "theory": None, "cross": None}
    x = x[:, ok]
    s = np.sqrt(ss_ref[ok] / n_ref[ok])
    main = score(x, s)
    return {**out, "main": main, "theory": score(x, SD), "cross": cross_part(x, s) if main else None}


def sign_flip(d, draws=200000, seed=47):
    """One-sided p for mean(d) > 0 when each difference is as likely to be negative as positive."""
    d = np.asarray(d, dtype=np.float64)
    rng = np.random.default_rng(seed)
    obs = d.sum()
    hits = 0
    for _ in range(draws // 10000):
        signs = rng.integers(0, 2, (10000, d.size)) * 2 - 1
        hits += int(((signs * d).sum(axis=1) >= obs).sum())
    return (hits + 1) / (draws + 1)


def combine(zs):
    zs = [z for z in zs if z is not None]
    if not zs:
        return {"n": 0, "z": None, "mean": None, "sd": None}
    return {"n": len(zs), "z": sum(zs) / math.sqrt(len(zs)), "mean": sum(zs) / len(zs), "sd": float(np.std(zs, ddof=1)) if len(zs) > 1 else None}


def verdicts(z_all, n):
    depart = "departure" if z_all >= 3.09 else "suggestive" if z_all >= 1.645 else "no positive excess detected"
    size = "smaller than the benchmark" if z_all <= EFFECT * math.sqrt(n) - 1.645 else "not shown smaller than the benchmark"
    return {"departure": depart, "size": size, "predicted_at_benchmark": EFFECT * math.sqrt(n),
            "mean_per_event": z_all / math.sqrt(n), "mean_interval_95": [z_all / math.sqrt(n) - 1.96 / math.sqrt(n), z_all / math.sqrt(n) + 1.96 / math.sqrt(n)]}


def read_events():
    return [r for r in csv.DictReader(open(Q / "events.tsv"), delimiter="\t") if r["in_test"] == "yes"]


def main():
    events = read_events()
    year = lambda e: e["start_utc"][:4]
    stats = year_variances([e["control_start_utc"] for e in events])
    rows = []
    for e in events:
        same_year = [f["control_start_utc"] for f in events if year(f) == year(e)]
        ev = score_window(e["start_utc"], [stats[c] for c in same_year])
        co = score_window(e["control_start_utc"], [stats[c] for c in same_year if c != e["control_start_utc"]])
        z = lambda r, k="main": (r[k] or {}).get("z") if k != "cross" else r["cross"]
        rows.append({"kind": e["kind"], "event": e["event"], "start_utc": e["start_utc"], "control_start_utc": e["control_start_utc"],
                     "eggs_passing": ev["eggs_passing"], "eggs_seen": ev["eggs_seen"], "seconds_used": (ev["main"] or {}).get("df"),
                     "eggs_median": (ev["main"] or {}).get("eggs_median"), "z": z(ev), "z_theory": z(ev, "theory"), "z_cross": z(ev, "cross"),
                     "control_eggs_passing": co["eggs_passing"], "control_seconds_used": (co["main"] or {}).get("df"),
                     "control_z": z(co), "control_z_theory": z(co, "theory"), "control_z_cross": z(co, "cross")})
        r = rows[-1]
        print(f"{e['event'][:50]:50s} eggs {r['eggs_passing']:3d}  event {'n/a' if r['z'] is None else format(r['z'], '+.2f')}  "
              f"control {'n/a' if r['control_z'] is None else format(r['control_z'], '+.2f')}", flush=True)

    def summary(sel, a="z", b="control_z"):
        ev = combine([r[a] for r in sel])
        co = combine([r[b] for r in sel])
        both = [r for r in sel if r[a] is not None and r[b] is not None]
        d = [r[a] - r[b] for r in both]
        out = {"events": ev, "controls": co, "verdicts": verdicts(ev["z"], ev["n"]) if ev["n"] else None}
        if len(d) > 1:
            out["paired"] = {"pairs": len(d), "mean_difference": float(np.mean(d)), "t": float(np.mean(d) / (np.std(d, ddof=1) / math.sqrt(len(d)))),
                             "p_one_sided_sign_flip": sign_flip(d), "events_higher": int(sum(1 for v in d if v > 0))}
        return out

    big = {q["id"] for q in json.load(open(Q / "sources" / "noaa_earthquakes_2016_2025_deaths_100_or_more.json")) if q["deaths"] >= 1000}
    is_big = lambda r: r["kind"] == "earthquake" and int(r["event"].split("NOAA id ")[1].split(",")[0]) in big
    out = {"events_in_list": len(events), "not_evaluable": [r["event"] for r in rows if r["z"] is None],
           "controls_not_evaluable": [r["event"] for r in rows if r["control_z"] is None],
           "all": summary(rows), "calendar": summary([r for r in rows if r["kind"] == "calendar"]),
           "earthquake": summary([r for r in rows if r["kind"] == "earthquake"]),
           "earthquakes_1000_deaths": summary([r for r in rows if is_big(r)]),
           "theoretical_standardising": summary(rows, "z_theory", "control_z_theory"),
           "cross_egg_part": summary(rows, "z_cross", "control_z_cross")}
    c = out["all"]["controls"]
    out["calibration_in_doubt"] = bool(abs(c["z"]) >= 2.58 or not 0.75 <= c["sd"] <= 1.3)
    (Q / "results").mkdir(exist_ok=True)
    json.dump(out, open(Q / "results" / "summary.json", "w"), indent=1)
    cols = list(rows[0].keys())
    with open(Q / "results" / "events.tsv", "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join("" if r[c] is None else f"{r[c]:.4f}" if isinstance(r[c], float) else str(r[c]) for c in cols) + "\n")
    v = out["all"]
    print(f"ALL: {v['events']['n']} events, combined {v['events']['z']:+.2f} (mean {v['events']['mean']:+.3f}); controls combined {v['controls']['z']:+.2f}, "
          f"sd {v['controls']['sd']:.2f}; paired p {v.get('paired', {}).get('p_one_sided_sign_flip')}")
    print("VERDICTS:", v["verdicts"], "| calibration in doubt:", out["calibration_in_doubt"])


if __name__ == "__main__":
    main()
