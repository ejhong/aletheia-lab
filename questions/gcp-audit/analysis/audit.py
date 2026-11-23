#!/usr/bin/env python3
"""Audit of the Global Consciousness Project's formal series: score every event in windows.tsv and its control
window with the project's standard statistic (protocol.md).

    python analysis/audit.py                 # the locked run; writes results/

Run from questions/gcp-audit with the repository's .venv (Python 3.12, numpy 2.3.5).
"""
import csv
import datetime
import gzip
import json
import math
import pathlib

import numpy as np

Q = pathlib.Path(__file__).resolve().parent.parent
DATA = Q / "data"
DAY = 86400
SD = math.sqrt(50.0)
WILD, MIN_FRACTION, MIN_EGGS, REF_TRIALS, CHECK = 45, 0.8, 2, 86400, 5.0
POOL_SPAN, POOL_DAY_MIN, MIN_PAIRS = 183 * DAY, 3600, 300
UTC = datetime.timezone.utc
FMT = "%Y-%m-%d %H:%M:%S"


def ts(text):
    return int(datetime.datetime.strptime(text, FMT).replace(tzinfo=UTC).timestamp())


def day_name(t):
    return datetime.datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%d")


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
                x = np.full((DAY, len(eggs)), np.nan, dtype=np.float32)
            elif line.startswith("13,"):
                p = line.rstrip("\n").split(",")
                i = int(p[1]) - t0
                assert 0 <= i < DAY, f"{day}: a second outside the day"
                assert len(p) <= 3 + len(eggs), f"{day}: more fields than eggs"
                for k, v in enumerate(p[3:3 + len(eggs)]):
                    if v:
                        x[i, k] = float(v)
    assert eggs is not None, f"{day}: no line of egg numbers"
    cache.parent.mkdir(exist_ok=True)
    np.savez_compressed(cache, t0=t0, eggs=np.array(eggs), x=x)
    return t0, eggs, x


def clean(x):
    """Remove trial sums that differ from 100 by 45 or more."""
    x = x.copy()
    with np.errstate(invalid="ignore"):
        x[np.abs(x - 100) >= WILD] = np.nan
    return x


def window(start, seconds, reader=read_day):
    """The `seconds` seconds from Unix time `start`: (egg numbers, array [seconds, eggs]), cleaned of wild trials."""
    days = sorted({day_name(start + k) for k in range(0, seconds, DAY)} | {day_name(start + seconds - 1)})
    parts = [reader(d) for d in days]
    eggs = sorted({e for _, es, _ in parts for e in es})
    col = {e: k for k, e in enumerate(eggs)}
    out = np.full((seconds, len(eggs)), np.nan, dtype=np.float32)
    for t0, es, x in parts:
        lo, hi = max(start, t0), min(start + seconds, t0 + DAY)
        if hi > lo:
            out[lo - start:hi - start, [col[e] for e in es]] = x[lo - t0:hi - t0]
    return eggs, clean(out)


def sums(x):
    """Per egg: number of trials, their sum, and their sum of squares about 100."""
    n = (~np.isnan(x)).sum(axis=0)
    d = x.astype(np.float64) - 100
    return n, np.nansum(d, axis=0), np.nansum(d ** 2, axis=0)


def passes(n, total, ss, seconds):
    """The egg check for one window."""
    with np.errstate(invalid="ignore", divide="ignore"):
        mean_dev = total / n
        return (n >= seconds / 2) & (np.abs(mean_dev) / (SD / np.sqrt(n)) <= CHECK) & (np.abs(ss / n / 50 - 1) * np.sqrt(n / 2) <= CHECK)


def wilson_hilferty(chi2, df):
    k = 2 / (9 * df)
    return ((chi2 / df) ** (1 / 3) - (1 - k)) / math.sqrt(k)


def score(x, s, seconds):
    """The window's score from trial sums x [seconds, eggs] and each egg's standard deviation s. None if too few seconds."""
    z = (x.astype(np.float64) - 100) / s
    n = (~np.isnan(z)).sum(axis=1)
    use = n >= 1
    df = int(use.sum())
    if df < MIN_FRACTION * seconds or df < 2:
        return None
    Z = np.nansum(z[use], axis=1) / np.sqrt(n[use])
    chi2 = float(np.sum(Z ** 2))
    return {"z": wilson_hilferty(chi2, df), "chi2": chi2, "df": df, "eggs_median": float(np.median(n[use]))}


def cross_part(x, s):
    """The part of the window's chi-square that comes from pairs of eggs moving together, as a standard score."""
    z = (x.astype(np.float64) - 100) / s
    n = (~np.isnan(z)).sum(axis=1)
    use = n >= 2
    if not use.any():
        return None
    zz, n = z[use], n[use]
    total = np.nansum(zz, axis=1) ** 2 / n - np.nansum(zz ** 2, axis=1) / n
    return float(total.sum() / math.sqrt(np.sum(2.0 * (n - 1) / n)))


def pool_of_day(day, blocked, reader=read_day):
    """Each egg's trials on one day, outside every blocked stretch: {egg: (n, sum of squares about 100)}.
    An egg is left out of the day if it has fewer than 3,600 such trials or fails the egg check on them."""
    t0, eggs, x = reader(day)
    x = clean(x)
    keep = np.ones(DAY, dtype=bool)
    for a, b in blocked:
        lo, hi = max(a, t0), min(b, t0 + DAY - 1)
        if hi >= lo:
            keep[lo - t0:hi - t0 + 1] = False
    n, total, ss = sums(x[keep])
    ok = passes(n, total, ss, 2 * POOL_DAY_MIN)          # an egg-day needs 3,600 trials and must pass the egg check
    return {e: (int(a), float(b)) for e, a, b, good in zip(eggs, n, ss, ok) if good}


def score_window(start, seconds, pool, own, reader=read_day):
    """Score one window. pool: {egg: (n, ss)}, the reference trials of this event-control pair. own: {egg: (n, ss)}
    to take out of the pool (empty in the audit, where the pair's pool already leaves out its control's days)."""
    eggs, x = window(start, seconds, reader)
    n, total, ss = sums(x)
    n_ref = np.array([pool.get(e, (0, 0.0))[0] - own.get(e, (0, 0.0))[0] for e in eggs])
    ss_ref = np.array([pool.get(e, (0, 0.0))[1] - own.get(e, (0, 0.0))[1] for e in eggs])
    pooled = n_ref >= REF_TRIALS
    ok = passes(n, total, ss, seconds) & pooled
    loose = (n >= seconds / 2) & pooled                  # the same without the mean and variance parts of the egg check
    out = {"eggs_passing": int(ok.sum()), "eggs_seen": len(eggs), "seconds_with_data": int((~np.isnan(x)).any(axis=1).sum())}
    with np.errstate(invalid="ignore", divide="ignore"):
        s_all = np.sqrt(ss_ref / n_ref)
    out["noveto"] = score(x[:, loose], s_all[loose], seconds) if loose.sum() >= MIN_EGGS else None
    if ok.sum() < MIN_EGGS:
        return {**out, "main": None, "theory": None, "cross": None}
    x = x[:, ok]
    s = s_all[ok]
    main = score(x, s, seconds)
    return {**out, "main": main, "theory": score(x, SD, seconds), "cross": cross_part(x, s) if main else None}


def sign_flip(d, draws=200000, seed=74):
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


def agreement(ours, published):
    """How closely our scores match the published ones."""
    a, b = np.asarray(ours, float), np.asarray(published, float)
    d = a - b
    return {"n": int(a.size), "r": float(np.corrcoef(a, b)[0, 1]) if a.size > 2 else None,
            "slope": float(np.polyfit(b, a, 1)[0]) if a.size > 2 else None,
            "mean_difference": float(d.mean()), "median_abs_difference": float(np.median(np.abs(d))),
            "share_within_0.25": float((np.abs(d) <= 0.25).mean()), "share_within_0.5": float((np.abs(d) <= 0.5).mean()),
            "combined_ours": float(a.sum() / math.sqrt(a.size)), "combined_published": float(b.sum() / math.sqrt(b.size))}


def reproduction_label(rep):
    if rep["r"] is None:
        return "not assessed"
    if rep["r"] >= 0.9 and rep["median_abs_difference"] <= 0.25:
        return "reproduces closely"
    if rep["r"] >= 0.7 and rep["median_abs_difference"] <= 0.5:
        return "reproduces roughly"
    return "does not reproduce"


def overall_label(pairs, ev_z, co_z, co_sd, paired_p):
    """The labels fixed in protocol.md, from the pairs in which both windows are evaluable. Checked in this order."""
    if pairs < MIN_PAIRS:
        return {"events": "not assessed", "controls": "not assessed", "overall": "insufficient coverage"}
    events = "departure" if ev_z >= 3.09 else "suggestive" if ev_z >= 1.645 else "no positive excess detected"
    failure = abs(co_z) >= 2.58 or not (0.85 <= co_sd <= 1.2)
    controls = "calibration failure detected" if failure else "no calibration failure detected"
    if ev_z < 1.645:
        overall = "no excess found"
    elif ev_z >= 3.09 and paired_p <= 0.01 and not failure:
        overall = "the excess is in the event windows"
    elif co_z >= 2.58 and paired_p > 0.05:
        overall = "the excess is not specific to the events"
    else:
        overall = "mixed"
    return {"events": events, "controls": controls, "overall": overall}


def read_windows():
    rows = list(csv.DictReader(open(Q / "windows.tsv", encoding="utf-8"), delimiter="\t"))
    return [r for r in rows if r["in_test"] == "1"]


def read_blocked():
    rows = list(csv.DictReader(open(Q / "sources" / "blocked.tsv", encoding="utf-8"), delimiter="\t"))
    return [(int(r["begin_unix"]), int(r["end_unix"])) for r in rows]


def days_touched(start, seconds):
    return sorted({day_name(start + k) for k in range(0, seconds, DAY)} | {day_name(start + seconds - 1)})


def summarise(sel):
    """Everything reported for one set of event-control pairs."""
    both = [r for r in sel if r["event_z"] is not None and r["control_z"] is not None]
    d = [r["event_z"] - r["control_z"] for r in both]
    scored = [r for r in sel if r["event_z"] is not None]
    out = {"events": combine([r["event_z"] for r in sel]), "controls": combine([r["control_z"] for r in sel]),
           "events_in_pairs": combine([r["event_z"] for r in both]), "controls_in_pairs": combine([r["control_z"] for r in both]),
           "events_theory": combine([r["event_z_theory"] for r in sel]), "controls_theory": combine([r["control_z_theory"] for r in sel]),
           "events_noveto": combine([r["event_z_noveto"] for r in sel]), "controls_noveto": combine([r["control_z_noveto"] for r in sel]),
           "events_cross": combine([r["event_cross"] for r in sel]), "controls_cross": combine([r["control_cross"] for r in sel]),
           "paired": {"n": len(d), "mean_difference": float(np.mean(d)) if d else None,
                      "sd_difference": float(np.std(d, ddof=1)) if len(d) > 1 else None,
                      "z": float(np.mean(d) / (np.std(d, ddof=1) / math.sqrt(len(d)))) if len(d) > 1 else None,
                      "event_higher": int(sum(x > 0 for x in d)), "p_one_sided": sign_flip(d) if d else None},
           "reproduction": agreement([r["event_z"] for r in scored], [r["published_z"] for r in scored]) if scored else None}
    th = [r for r in sel if r["event_z_theory"] is not None]
    out["reproduction_theory"] = agreement([r["event_z_theory"] for r in th], [r["published_z"] for r in th]) if th else None
    return out


def main():
    events, blocked = read_windows(), read_blocked()
    for e in events:
        c, n = ts(e["control_begin_utc"]), int(e["seconds"])
        assert all(c + n - 1 < a or c > b for a, b in blocked), f"control of event {e['num']} overlaps a blocked stretch"
    control_days = {e["num"]: days_touched(ts(e["control_begin_utc"]), int(e["seconds"])) for e in events}
    day_pool = {d: pool_of_day(d, blocked) for d in sorted({d for ds in control_days.values() for d in ds})}

    def pair_pool(e):
        """The reference trials of one pair: the control days of every event that begins within 183 days of this
        one, except the days this pair's own control window touches. Each day counts once."""
        a = ts(e["begin_utc"])
        days = {d for o in events if abs(ts(o["begin_utc"]) - a) <= POOL_SPAN for d in control_days[o["num"]]} - set(control_days[e["num"]])
        tot = {}
        for d in days:
            for egg, (n, ss) in day_pool[d].items():
                p, q = tot.get(egg, (0, 0.0))
                tot[egg] = (p + n, q + ss)
        return tot, len(days)

    rows, kept = [], []
    for e in events:
        a, c, n = ts(e["begin_utc"]), ts(e["control_begin_utc"]), int(e["seconds"])
        pool, pool_days = pair_pool(e)
        ev, co = score_window(a, n, pool, {}), score_window(c, n, pool, {})
        overlaps_earlier = any(a <= y and a + n - 1 >= x for x, y in kept)
        if not overlaps_earlier:
            kept.append((a, a + n - 1))
        g = lambda r, part: None if r[part] is None else (r[part] if part == "cross" else r[part]["z"])
        rows.append({"num": e["num"], "description": e["description"], "begin_utc": e["begin_utc"], "seconds": n,
                     "published_z": float(e["published_z"]), "control_begin_utc": e["control_begin_utc"],
                     "control_shift_days": int(e["control_shift_days"]), "overlaps_earlier_event": int(overlaps_earlier),
                     "event_z": g(ev, "main"), "control_z": g(co, "main"), "event_z_theory": g(ev, "theory"),
                     "control_z_theory": g(co, "theory"), "event_z_noveto": g(ev, "noveto"), "control_z_noveto": g(co, "noveto"),
                     "event_cross": g(ev, "cross"), "control_cross": g(co, "cross"),
                     "event_df": ev["main"]["df"] if ev["main"] else None, "control_df": co["main"]["df"] if co["main"] else None,
                     "event_eggs": ev["eggs_passing"], "control_eggs": co["eggs_passing"],
                     "event_eggs_seen": ev["eggs_seen"], "control_eggs_seen": co["eggs_seen"],
                     "event_eggs_median_per_second": ev["main"]["eggs_median"] if ev["main"] else None,
                     "control_eggs_median_per_second": co["main"]["eggs_median"] if co["main"] else None, "pool_days": pool_days})
        print(rows[-1]["num"], rows[-1]["event_z"], rows[-1]["control_z"], flush=True)

    (Q / "results").mkdir(exist_ok=True)
    with open(Q / "results" / "windows.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if v is None else f"{v:.6f}" if isinstance(v, float) else v) for k, v in r.items()})

    out = {"all": summarise(rows)}
    a = out["all"]
    out["verdicts"] = overall_label(a["paired"]["n"], a["events_in_pairs"]["z"], a["controls_in_pairs"]["z"], a["controls_in_pairs"]["sd"],
                                    a["paired"]["p_one_sided"])
    out["verdicts"]["reproduction"] = reproduction_label(a["reproduction"])
    out["verdicts"]["reproduction_theory"] = reproduction_label(a["reproduction_theory"])
    out["non_overlapping"] = summarise([r for r in rows if not r["overlaps_earlier_event"]])
    out["control_earlier"] = summarise([r for r in rows if r["control_shift_days"] < 0])
    out["control_later"] = summarise([r for r in rows if r["control_shift_days"] > 0])
    out["without_events_scored_in_47"] = summarise([r for r in rows if r["num"] not in ("374", "391", "447", "476", "513")])
    out["by_year"] = {y: summarise([r for r in rows if r["begin_utc"][:4] == y]) for y in sorted({r["begin_utc"][:4] for r in rows})}
    out["by_length"] = {name: summarise([r for r in rows if lo <= r["seconds"] < hi])
                        for name, lo, hi in [("under 1 hour", 0, 3600), ("1 to 6 hours", 3600, 21601), ("over 6 hours, under a day", 21601, DAY),
                                             ("a day or more", DAY, 10 ** 9)]}
    out["not_evaluable"] = {"events": [r["num"] for r in rows if r["event_z"] is None], "controls": [r["num"] for r in rows if r["control_z"] is None]}
    json.dump(out, open(Q / "results" / "summary.json", "w"), indent=1)
    print(json.dumps({"all": out["all"], "verdicts": out["verdicts"]}, indent=1))


if __name__ == "__main__":
    main()
