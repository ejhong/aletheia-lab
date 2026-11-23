#!/usr/bin/env python3
"""Rank the Younger Dryas onset window against every other window of each ice-core record (protocol.md).

    python analysis/fire.py --decoy     # before the lock: the target window is removed and a decoy stands in for it
    python analysis/fire.py             # the locked run; writes results/

Run from questions/ice-core-fire. Needs numpy (the shared venv has numpy 2.3.5 on Python 3.12).
"""
import json
import pathlib
import sys
import warnings

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

Q = pathlib.Path(__file__).resolve().parent.parent
D = Q / "data"
CENTRE = {"gicc05": 12900.0, "gisp2": 12885.0}
ONSET_B2K = 12896.0
# name: (core, source, timescale, bin length T, span start, span end)
SERIES = {"N10": ("NGRIP", "ngrip10", "gicc05", 10, 10300, 107620), "E10": ("NEEM", "neem10", "gicc05", 10, 10300, 107620),
          "N20": ("NGRIP", "ngrip10", "gicc05", 20, 10300, 50000), "E20": ("NEEM", "neem10", "gicc05", 20, 10300, 50000),
          "G20": ("GISP2", "gisp2", "gisp2", 20, 10300, 50000),
          "N60": ("NGRIP", "ngrip10", "gicc05", 60, 10300, 107620), "E60": ("NEEM", "neem10", "gicc05", 60, 10300, 107620),
          "G60": ("GISP2", "gisp2", "gisp2", 60, 10300, 107620),
          "N3": ("NGRIP", "ngrip_mm", "gicc05", 3, 10300, 60000), "N1": ("NGRIP", "ngrip_mm", "gicc05", 1, 10300, 20000),
          "G10": ("GISP2", "gisp2", "gisp2", 10, 10300, 15000), "E10h": ("NEEM", "neem10", "gicc05", 10, 0, 107620),
          "G20h": ("GISP2", "gisp2", "gisp2", 20, 0, 50000), "G60h": ("GISP2", "gisp2", "gisp2", 60, 0, 110000)}
TIERS = {"T10": ["N10", "E10"], "T20": ["N20", "E20", "G20"], "T60": ["N60", "E60", "G60"]}
TIER_SERIES = [s for t in TIERS.values() for s in t]
PULSE_SERIES = TIER_SERIES + ["N3", "N1"]
PULSE_SIZES = (20, 50, 100, 200, 500, 1000, 2000, 5000)
WIDTH = 300


# ---------- reading the files ----------

def read_pangaea(path, ncol=6):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("*/"):
                break
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t") + [""] * ncol
            rows.append([float(x) if x else np.nan for x in p[:ncol]])
    return np.array(rows)


def read_gicc05():
    out = []
    for line in open(D / "noaa" / "gicc05-60ka-20yr.txt", encoding="latin-1"):
        p = line.split()
        if len(p) == 4:
            try:
                out.append([float(x) for x in p])
            except ValueError:
                pass
    a = np.array(out)
    assert len(a) == 3000 and np.all(np.diff(a[:, 0]) > 0) and np.all(np.diff(a[:, 1]) > 0)
    return a[:, 0], a[:, 1]          # age b2k, NGRIP depth m


def read_ngrip_mm():
    cache = D / "cache" / "ngrip_mm.npy"
    if cache.exists():
        return np.load(cache)
    a = read_pangaea(D / "pangaea" / "935818.tab")[:, [0, 4]]
    cache.parent.mkdir(exist_ok=True)
    np.save(cache, a)
    return a


def read_gisp2():
    rows, started = [], False
    for line in open(D / "noaa" / "iond.txt", encoding="latin-1"):
        p = line.rstrip("\n").split("\t")
        if p[0] == "Top":
            started = True
            continue
        if started and len(p) >= 12:
            try:
                rows.append([float(x) if x.strip() else np.nan for x in p[:12]])
            except ValueError:
                pass
    g = np.array(rows)
    g = g[(g[:, 10] < 999999) & (g[:, 11] < 999999) & (g[:, 11] > g[:, 10])]
    assert not np.isnan(g[:, [3, 8]]).any() and np.all(g[1:, 10] >= g[:-1, 11] - 1e-9)
    return g


_raw = {}


def raw(source):
    if source not in _raw:
        if source == "ngrip10":
            _raw[source] = read_pangaea(D / "pangaea" / "935814.tab")
        elif source == "neem10":
            _raw[source] = read_pangaea(D / "pangaea" / "935831.tab")
        elif source == "gisp2":
            _raw[source] = read_gisp2()
        else:
            a = read_ngrip_mm()
            g_age, g_depth = read_gicc05()
            _raw[source] = np.column_stack([np.interp(a[:, 0], g_depth, g_age, left=np.nan, right=np.nan), a[:, 1], a[:, 0]])
    return _raw[source]


# ---------- bins ----------

class Binned:
    """Values in equal bins: bin j covers [a0 + j*T, a0 + (j+1)*T). Missing bins are NaN."""

    def __init__(self, a0, T, j0, x, w=None):
        self.a0, self.T, self.j0, self.x, self.w = a0, T, int(j0), x, w

    def get(self, j_from, j_to, arr=None):     # values of bins j_from .. j_to-1, NaN where no bin exists
        arr = self.x if arr is None else arr
        out = np.full(j_to - j_from, np.nan)
        lo, hi = max(j_from, self.j0), min(j_to, self.j0 + len(arr))
        if hi > lo:
            out[lo - j_from:hi - j_from] = arr[lo - self.j0:hi - self.j0]
        return out


def bin_decadal(age, val, a0, T):
    """age: integer years, multiples of 10; a row labelled a covers [a, a+10)."""
    assert float(a0).is_integer() and int(a0) % 10 == 0 and T % 10 == 0
    j = (age - int(a0)) // T
    ok = ~np.isnan(val)
    j0 = int(j.min())
    have = np.bincount(j[ok] - j0, minlength=int(j.max()) - j0 + 1)
    tot = np.bincount(j[ok] - j0, weights=val[ok], minlength=len(have))
    with np.errstate(invalid="ignore", divide="ignore"):
        x = np.where(2 * have >= T // 10, tot / have, np.nan)
    x[have == 0] = np.nan
    return Binned(a0, T, j0, x)


def bin_rows(age, val, a0, T):
    ok = ~np.isnan(age)
    j = np.floor((age[ok] - a0) / T).astype(int)
    v = val[ok]
    j0 = int(j.min())
    n = np.bincount(j - j0)
    have = np.bincount(j - j0, weights=(~np.isnan(v)).astype(float))
    tot = np.bincount(j - j0, weights=np.nan_to_num(v))
    with np.errstate(invalid="ignore", divide="ignore"):
        x = np.where((n > 0) & (2 * have >= n) & (have > 0), tot / have, np.nan)
    return Binned(a0, T, j0, x)


def bin_samples(top, bot, val, a0, T):
    j_lo, j_hi = int(np.floor((top.min() - a0) / T)), int(np.floor((bot.max() - a0) / T)) + 1
    w = np.zeros(j_hi - j_lo)
    s = np.zeros(j_hi - j_lo)
    for t, b, v in zip(top, bot, val):
        for j in range(int(np.floor((t - a0) / T)), int(np.floor((b - a0) / T)) + 1):
            ov = min(b, a0 + (j + 1) * T) - max(t, a0 + j * T)
            if ov > 0:
                w[j - j_lo] += ov
                s[j - j_lo] += ov * v
    with np.errstate(invalid="ignore", divide="ignore"):
        x = np.where(w >= T / 2, s / w, np.nan)
    return Binned(a0, T, j_lo, x, w)


_built = {}


def build(name, width=WIDTH, ion="NH4", shift=0.0):
    key = (name, width, ion, shift)
    if key in _built:
        return _built[key]
    core, source, scale, T, lo, hi = SERIES[name]
    a0 = CENTRE[scale] - width / 2 + shift
    r = raw(source)
    if source in ("ngrip10", "neem10"):
        b = bin_decadal(np.rint(r[:, 0] * 1000).astype(int), r[:, 4 if ion == "NH4" else 5], a0, T)
    elif source == "gisp2":
        b = bin_samples(r[:, 10], r[:, 11], r[:, 3 if ion == "NH4" else 8], a0, T)
    else:
        assert ion == "NH4"
        b = bin_rows(r[:, 0], r[:, 1], a0, T)
    _built[key] = b
    return b


# ---------- measures ----------

def _nanmedian(a, axis):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmedian(a, axis=axis)


def scores(x, T, variant="centred", want_z=True):
    """For every bin: background, excess, and (if wanted) the log score with its numerator and MAD."""
    n = int(150 // T)
    pad = np.concatenate([np.full(n, np.nan), x, np.full(n, np.nan)])
    win = sliding_window_view(pad, 2 * n + 1)
    present = (~np.isnan(win)).sum(axis=1)
    if variant == "centred":
        m = np.where(2 * present >= 2 * n + 1, _nanmedian(win, 1), np.nan)
    else:
        before, after = win[:, :n], win[:, n + 1:]
        mb = np.where(2 * (~np.isnan(before)).sum(axis=1) >= n, _nanmedian(before, 1), np.nan)
        ma = np.where(2 * (~np.isnan(after)).sum(axis=1) >= n, _nanmedian(after, 1), np.nan)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            m = np.nanmax(np.stack([mb, ma]), axis=0) if variant == "higher" else np.nanmin(np.stack([mb, ma]), axis=0)
    e = x - m
    z = num = mad = np.full(len(x), np.nan)
    if want_z and T != 60 and variant == "centred":
        with np.errstate(invalid="ignore", divide="ignore"):
            lwin = np.where(win > 0, np.log(np.where(win > 0, win, 1.0)), np.nan)
            lm = _nanmedian(lwin, 1)
            mad = _nanmedian(np.abs(lwin - lm[:, None]), 1)
            lx = np.where(x > 0, np.log(np.where(x > 0, x, 1.0)), np.nan)
            num = lx - lm
            z = np.where(~np.isnan(m) & (mad > 0), num / (1.4826 * mad), np.nan)
    return m, e, z, num, mad


def windows(name, width=WIDTH, ion="NH4", shift=0.0, variant="centred"):
    """One row per usable window of a series."""
    core, source, scale, T, lo, hi = SERIES[name]
    b = build(name, width, ion, shift)
    m, e, z, num, mad = scores(b.x, T, variant)
    per = int(round(width / T))
    assert per * T == width
    rows = []
    k = int(np.ceil((lo - b.a0) / width))
    while b.a0 + width * (k + 1) <= hi:
        j1, j2 = k * per, (k + 1) * per
        xs, es, zs = b.get(j1, j2), b.get(j1, j2, e), b.get(j1, j2, z)
        have = int((~np.isnan(xs)).sum())
        if 5 * have >= 4 * per:
            r = {"k": k, "start": b.a0 + width * k, "end": b.a0 + width * (k + 1), "bins": per, "with_value": have}
            age = lambda i: b.a0 + (j1 + int(i)) * T
            i = int(np.nanargmax(xs))
            r.update(H=float(xs[i]), H_age=age(i), mean=float(np.nanmean(xs)))
            if 5 * int((~np.isnan(es)).sum()) >= 4 * per:
                i = int(np.nanargmax(es))
                r.update(E=float(es[i]), E_age=age(i), E_value=float(xs[i]), E_background=float(b.get(j1, j2, m)[i]))
            else:
                r.update(E=np.nan, E_age=np.nan, E_value=np.nan, E_background=np.nan)
            if (~np.isnan(zs)).any():
                i = int(np.nanargmax(zs))
                r.update(Z=float(zs[i]), Z_age=age(i), Z_numerator=float(b.get(j1, j2, num)[i]), Z_mad=float(b.get(j1, j2, mad)[i]))
            else:
                r.update(Z=np.nan, Z_age=np.nan, Z_numerator=np.nan, Z_mad=np.nan)
            rows.append(r)
        k += 1
    return rows


def rank(rows, measure, k=0):
    vals = {r["k"]: r[measure] for r in rows if not np.isnan(r[measure])}
    if k not in vals:
        return None
    n = len(vals)
    rk = 1 + sum(1 for kk, v in vals.items() if kk != k and v > vals[k])
    ties = sum(1 for kk, v in vals.items() if kk != k and v == vals[k])
    v = np.sort(np.array(list(vals.values())))[::-1]
    top1, top5 = max(1, int(np.floor(0.01 * n))), max(1, int(np.floor(0.05 * n)))
    row = next(r for r in rows if r["k"] == k)
    out = {"value": vals[k], "rank": rk, "N": n, "fraction": (rk + ties) / n, "ties": ties, "top1_rank": top1, "top5_rank": top5,
           "in_top1": rk <= top1, "in_top5": rk <= top5, "value_needed_top1": float(v[top1 - 1]),
           "value_needed_top5": float(v[top5 - 1]), "median_window": float(np.median(v))}
    if measure + "_age" in row:
        out["age"] = row[measure + "_age"]
    return out


def tier_pass(tier, ranks, level):
    """Does a tier pass at 'in_top1' or 'in_top5'? Returns (passes, note)."""
    ok = [s for s in TIERS[tier] if ranks.get(s) and ranks[s][level]]
    if len(ok) < 2:
        return False, ""
    gicc = [s for s in ok if SERIES[s][2] == "gicc05"]
    timing_ok = len(gicc) == 2 and abs(ranks[gicc[0]]["age"] - ranks[gicc[1]]["age"]) <= 60
    if len(gicc) == 2 and timing_ok:
        return True, "NGRIP and NEEM peaks within 60 years"
    if len(ok) == 2 and len(gicc) == 2:
        return False, "high windows, different peaks"
    return True, "timing not checkable" + ("; NGRIP and NEEM peaks more than 60 years apart" if len(gicc) == 2 else "")


def verdict(ranks):
    """ranks[series] is the rank record on E for each tier series (None if the target has no E)."""
    testable = {core: any(ranks.get(s) for s in TIER_SERIES if SERIES[s][0] == core) for core in ("NGRIP", "NEEM", "GISP2")}
    notes = {}
    if sum(1 for v in testable.values() if not v) >= 2:
        return "not testable", notes
    for level, name in (("in_top1", "exceptional"), ("in_top5", "unusual")):
        for t in TIERS:
            ok, note = tier_pass(t, ranks, level)
            if note:
                notes[f"{t}.{level}"] = note
            if ok:
                return name, notes
    if any(ranks.get(s) and ranks[s]["in_top1"] for s in TIER_SERIES):
        return "not corroborated", notes
    return "not met", notes


# ---------- made-up fires ----------

def pulses(name, rows, rng, target_k, thresholds, n_place=300):
    """Share of placements whose window E reaches the top-1% and top-5% values, for each pulse size."""
    core, source, scale, T, lo, hi = SERIES[name]
    b = build(name)
    n, per = int(150 // T), int(round(WIDTH / T))
    eligible = sorted(r["k"] for r in rows if not np.isnan(r["E"]) and abs(r["k"] - target_k) > 1)
    g = raw("gisp2") if source == "gisp2" else None
    hits = {A: [0, 0] for A in PULSE_SIZES}
    for _ in range(n_place):
        k = eligible[int(rng.integers(len(eligible)))]
        t = b.a0 + WIDTH * k + int(rng.integers(WIDTH))
        j1, j2 = k * per, (k + 1) * per
        base = b.get(j1 - n, j2 + n)
        delta = np.zeros(len(base))
        if g is None:
            for j in {int(np.floor((t - b.a0) / T)), int(np.floor((t + 1 - 1e-9 - b.a0) / T))}:
                ov = min(t + 1, b.a0 + (j + 1) * T) - max(t, b.a0 + j * T)
                if 0 <= j - (j1 - n) < len(delta):
                    delta[j - (j1 - n)] += ov / T
        else:
            for i in np.flatnonzero((g[:, 10] < t + 1) & (g[:, 11] > t)):
                top, bot = g[i, 10], g[i, 11]
                part = min(bot, t + 1) - max(top, t)                  # the part of the pulse year inside this sample
                for j in range(int(np.floor((top - b.a0) / T)), int(np.floor((bot - b.a0) / T)) + 1):
                    ov = min(bot, b.a0 + (j + 1) * T) - max(top, b.a0 + j * T)
                    wj = b.get(j, j + 1, b.w)[0]
                    if ov > 0 and 0 <= j - (j1 - n) < len(delta) and wj >= T / 2:
                        delta[j - (j1 - n)] += part / (bot - top) * ov / wj
        for A in PULSE_SIZES:
            m, e, *_ = scores(base + A * delta, T, want_z=False)
            E = np.nanmax(e[n:n + per])
            hits[A][0] += E >= thresholds[0]
            hits[A][1] += E >= thresholds[1]
    return {A: {"top1": h[0] / n_place, "top5": h[1] / n_place} for A, h in hits.items()}


def spearman(rows_a, rows_b, measure="E"):
    a = {r["k"]: r[measure] for r in rows_a if not np.isnan(r[measure])}
    b = {r["k"]: r[measure] for r in rows_b if not np.isnan(r[measure])}
    ks = sorted(set(a) & set(b))
    ra = np.argsort(np.argsort([a[k] for k in ks]))
    rb = np.argsort(np.argsort([b[k] for k in ks]))
    return {"rho": float(np.corrcoef(ra, rb)[0, 1]), "windows": len(ks)}


COLS = ["k", "start", "end", "bins", "with_value", "E", "E_age", "E_value", "E_background", "H", "H_age", "Z", "Z_age", "Z_numerator", "Z_mad", "mean"]


def main():
    decoy = "--decoy" in sys.argv
    tables = {name: windows(name) for name in SERIES}
    target = 0
    if decoy:
        tables = {n: [r for r in rows if r["k"] != 0] for n, rows in tables.items()}
        common = set.intersection(*[{r["k"] for r in tables[n] if not np.isnan(r["E"])} for n in TIER_SERIES])
        target = int(np.random.default_rng(43).choice(sorted(k for k in common if abs(k) >= 10)))
    ranks = {m: {n: rank(tables[n], m, target) for n in SERIES} for m in ("E", "H", "Z")}
    v, notes = verdict({n: ranks["E"][n] for n in TIER_SERIES})
    rng = np.random.default_rng(43)
    recovery = {}
    for n in PULSE_SERIES:
        r = ranks["E"][n] or rank(tables[n], "E", tables[n][0]["k"])
        recovery[n] = pulses(n, tables[n], rng, target, (r["value_needed_top1"], r["value_needed_top5"]))
    if decoy:
        print(f"DECOY RUN: the real target window is left out; window k = {target} stands in for it.")
        for n in SERIES:
            print(f"  {n}: {len(tables[n])} usable windows; " + "; ".join(
                f"{m} rank {ranks[m][n]['rank']}/{ranks[m][n]['N']}" if ranks[m][n] else f"{m} n/a" for m in ("E", "H", "Z")))
        print("  verdict for the decoy:", v, notes)
        print("  made-up fires, share reaching the top 1% (sizes " + ", ".join(map(str, PULSE_SIZES)) + "):")
        for n in PULSE_SERIES:
            print(f"    {n}: " + " ".join(f"{recovery[n][A]['top1']:.2f}" for A in PULSE_SIZES))
        return
    out = Q / "results"
    out.mkdir(exist_ok=True)
    for name, rows in tables.items():
        with open(out / f"windows_{name}.tsv", "w") as f:
            f.write("\t".join(COLS) + "\n")
            for r in rows:
                f.write("\t".join(f"{r[c]:.4f}" if isinstance(r[c], float) else str(r[c]) for c in COLS) + "\n")
    summary = {"verdict": v, "verdict_notes": notes, "tiers": TIERS, "onset_b2k": ONSET_B2K,
               "series": {n: {"core": SERIES[n][0], "timescale": SERIES[n][2], "T": SERIES[n][3], "span": SERIES[n][4:], "usable_windows": len(tables[n]),
                              "target_usable": any(r["k"] == 0 for r in tables[n])} for n in SERIES},
               "ranks": ranks, "made_up_fires": {n: {str(A): x for A, x in recovery[n].items()} for n in recovery}}
    side = {"widths": {}, "bin_phase": {}, "one_sided": {}, "nitrate": {}, "winning_bins": {}, "top10": {}, "together": {}}
    for w in (120, 600):
        side["widths"][str(w)] = {n: rank(windows(n, w), "E") for n in SERIES}
    for n in SERIES:
        T, src = SERIES[n][3], SERIES[n][1]
        if not (T == 10 and src in ("ngrip10", "neem10")):
            side["bin_phase"][n] = rank(windows(n, WIDTH, "NH4", T / 2), "E")
    for variant in ("higher", "lower"):
        side["one_sided"][variant] = {n: rank(windows(n, WIDTH, "NH4", 0.0, variant), "E") for n in SERIES}
    for n in ("N10", "E10", "G60"):
        rows = windows(n, WIDTH, "NO3")
        side["nitrate"][n] = {m: rank(rows, m) for m in ("E", "H")}
    for n in TIER_SERIES:
        best = sorted((r for r in tables[n] if not np.isnan(r["E"])), key=lambda r: -r["E"])
        pick = lambda r: {c: r[c] for c in ("k", "start", "end", "E", "E_age", "E_value", "E_background")}
        side["top10"][n] = [pick(r) for r in best[:10]]
        side["winning_bins"][n] = {"target": pick(next(r for r in tables[n] if r["k"] == 0)), "five_highest": [pick(r) for r in best[:5]]}
    g_age, g_depth = read_gicc05()
    for n in ("N1", "N3"):
        t = next((r for r in tables[n] if r["k"] == 0), None)
        if t and not np.isnan(t["E"]):
            d1, d2 = np.interp([t["E_age"], t["E_age"] + SERIES[n][3]], g_age, g_depth)
            side["winning_bins"][n] = {"target": {c: t[c] for c in ("E", "E_age", "E_value", "E_background")}, "depth_m": [float(d1), float(d2)],
                                       "layer_cm_per_year": float((d2 - d1) / SERIES[n][3] * 100)}
    side["together"]["N10-E10"] = spearman(tables["N10"], tables["E10"])
    g = raw("gisp2")
    near = g[(g[:, 1] > 1711.5) & (g[:, 0] < 1713.0)]
    side["gisp2_samples_1711.5_to_1713.0_m"] = [{"top_m": r[0], "bottom_m": r[1], "top_age": r[10], "bottom_age": r[11], "NH4": r[3], "NO3": r[8]} for r in near]
    a0 = CENTRE["gisp2"] - WIDTH / 2
    inw = np.flatnonzero((g[:, 11] > a0) & (g[:, 10] < a0 + WIDTH))
    i = inw[np.argmax(g[inw, 3])]
    side["gisp2_largest_sample_in_window"] = {"top_m": g[i, 0], "bottom_m": g[i, 1], "top_age": g[i, 10], "bottom_age": g[i, 11], "NH4": g[i, 3],
                                              "share_of_aged_samples_exceeded": float(np.mean(g[:, 3] < g[i, 3])), "aged_samples": int(len(g)),
                                              "samples_at_least_as_high": int((g[:, 3] >= g[i, 3]).sum())}
    summary["alongside"] = side
    json.dump(summary, open(out / "summary.json", "w"), indent=1, default=float)
    print("verdict:", v, notes)
    for n in SERIES:
        r = ranks["E"][n]
        if r:
            print(f"  E {n}: {r['value']:.2f} at {r['age']:.0f}, rank {r['rank']} of {r['N']} (top 1% needs {r['value_needed_top1']:.2f}, top 5% {r['value_needed_top5']:.2f})")


if __name__ == "__main__":
    main()
