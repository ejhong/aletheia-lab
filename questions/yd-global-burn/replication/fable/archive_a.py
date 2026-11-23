"""Independent recomputation of Archive A of question #69 from its protocol.md alone (not from its code)."""
import math, sys
import numpy as np
D = sys.argv[1] + "/data/noaa/"
A0, W = 12650.0, 300.0

def table(path, cols):
    rows, seen_header = [], False
    for line in open(path, encoding="latin-1"):
        if line.startswith("#") or not line.strip():
            continue
        if not seen_header:
            seen_header = True
            continue
        p = line.rstrip("\n").split("\t")
        try:
            v = [float(p[c]) for c in cols]
        except (ValueError, IndexError):
            continue
        if all(math.isfinite(x) for x in v):
            rows.append(v)
    a = np.array(rows)
    ages = np.unique(a[:, 0])
    return np.array([[t] + [a[a[:, 0] == t, k].mean() for k in range(1, a.shape[1])] for t in ages])

def interp(age, val, t, gap):
    out = np.full(len(t), np.nan)
    for i, x in enumerate(t):
        j = np.searchsorted(age, x)
        if j < len(age) and age[j] == x:
            out[i] = val[j]
        elif 0 < j < len(age) and age[j] - age[j - 1] <= gap:
            out[i] = val[j - 1] + (val[j] - val[j - 1]) * (x - age[j - 1]) / (age[j] - age[j - 1])
    return out

def windows(score_at, spans):
    """score_at: {grid index j: score}; returns {k: max over the window's 3 grid points} where at least 2 are finite."""
    out = {}
    for lo, hi in spans:
        k = math.ceil((lo - A0) / W)
        while A0 + W * (k + 1) <= hi:
            v = [score_at.get(3 * k + i, np.nan) for i in range(3)]
            if sum(np.isfinite(v)) >= 2:
                out[k] = np.nanmax(v)
            k += 1
    return out

def rank(w):
    t = w[0]
    return 1 + sum(1 for k, v in w.items() if k and v > t), len(w), sum(1 for k, v in w.items() if k and v == t), t

def grid_scores(x, fn):
    """x: {j: value}; score at j = max over h in (1, 2) of fn(x_j, x_{j+h}) where both exist."""
    out = {}
    for j in x:
        v = [fn(j, h) for h in (1, 2) if np.isfinite(x.get(j, np.nan)) and np.isfinite(x.get(j + h, np.nan))]
        if v:
            out[j] = max(v)
    return out

# WAIS: 100-year bin means, forward rise
wa = table(D + "antarctica2015co2wais-noaa.txt", [1, 2])
jw = np.floor((wa[:, 0] - A0) / 100).astype(int)
xw = {int(j): wa[jw == j, 1].mean() for j in np.unique(jw)}
sw = grid_scores(xw, lambda j, h: xw[j] - xw[j + h])
print("WAIS_CO2 rank, N, ties, value:", rank(windows(sw, [(10250, 21950)])))

# Taylor Glacier: interpolate, BURN = max(0, dCO2) x max(0, d13C drop)
tg = table(D + "taylor2018d13co2.txt", [1, 2, 4])
js = np.arange(-40, 400)
t = A0 + 100 * js
seg = ((t >= tg[:, 0].min()) & (t <= tg[:, 0].max()))
co2, d13 = interp(tg[:, 0], tg[:, 1], t, 500), interp(tg[:, 0], tg[:, 2], t, 500)
xc, xd = {int(j): c for j, c in zip(js, co2)}, {int(j): d for j, d in zip(js, d13)}
ok = lambda j, h: all(np.isfinite(v) for v in (xc.get(j, np.nan), xc.get(j + h, np.nan), xd.get(j, np.nan), xd.get(j + h, np.nan)))
burn, drop = {}, {}
for j in js:
    v = [max(0, xc[j] - xc[j + h]) * max(0, xd[j + h] - xd[j]) for h in (1, 2) if ok(int(j), h)]
    u = [xd[j + h] - xd[j] for h in (1, 2) if ok(int(j), h)]
    if v:
        burn[int(j)], drop[int(j)] = max(v), max(u)
spans = [(11150, 22250), (35150, 46250)]
print("TG_BURN  rank, N, ties, value:", rank(windows(burn, spans)))
print("TG_D13C  rank, N, ties, value:", rank(windows(drop, spans)))
top = sorted(windows(burn, spans).items(), key=lambda kv: -kv[1])[:7]
print("TG_BURN top windows:", [(int(A0 + W * k), round(v, 3)) for k, v in top])

# Eggleston composite: d13C drop
eg = table(D + "eggleston2016d13co2-noaa.txt", [0, 1])
js = np.arange(-125, 1500)
d = interp(eg[:, 0], eg[:, 1], A0 + 100 * js, 300)
xe = {int(j): v for j, v in zip(js, d)}
se = grid_scores(xe, lambda j, h: xe[j + h] - xe[j])
we = {k: round(float(v), 6) for k, v in windows(se, [(950, 154850)]).items()}
print("EGG_D13C rank, N, ties, value:", rank(we))
print("EGG top windows:", [(int(A0 + W * k), v) for k, v in sorted(we.items(), key=lambda kv: -kv[1])[:8]])
