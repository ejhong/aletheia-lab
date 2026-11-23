"""Independent recomputation of Archive B (charcoal, Tier C1, 13.5 kyr span) of question #69 from its protocol.md alone."""
import collections, csv, json, math, statistics, sys
import numpy as np
D = sys.argv[1] + "/data/gcd_csv/"
num = lambda s: float(s) if s not in ("", None) else float("nan")
rows = lambda t: csv.DictReader(open(D + t + ".csv", encoding="utf-8", errors="replace"))
pref = {r["ID_SITE"]: r["PREF_UNITS"] for r in rows("SITE")}
age = {r["ID_SAMPLE"]: num(r["EST_AGE"]) for r in rows("SAMPLE")}
by_site = collections.defaultdict(list)
for r in rows("CHARCOAL"):
    q, a = num(r["QUANTITY"]), age.get(r["ID_SAMPLE"], float("nan"))
    if math.isfinite(q) and q >= 0 and math.isfinite(a):
        by_site[r["ID_SITE"]].append((r["ID_SAMPLE"], r["ID_UNITS"], q, a))
dates = collections.defaultdict(list)
for r in rows("DATE_INFO"):
    d = num(r["AGE_CALIB"])
    if not math.isfinite(d):
        d = num(r["AGE_C14"])
    if math.isfinite(d):
        dates[r["ID_SITE"]].append(d)
A0, W, LO, HI = 12650.0, 300.0, 1250.0, 14750.0
KS = list(range(int((LO - A0) / W), int((HI - A0) / W)))
sites = {}
for s, v in by_site.items():
    counts = collections.Counter(u for _, u, _, _ in v)
    if len(counts) > 1:
        unit = pref.get(s) if counts.get(pref.get(s), 0) >= 0.5 * len(v) else sorted(counts, key=lambda u: (-counts[u], u))[0]
    else:
        unit = next(iter(counts))
    samp = collections.defaultdict(list)
    for sid, u, q, a in v:
        if u == unit:
            samp[(sid, a)].append(q)
    pts = sorted((a, sum(q) / len(q)) for (sid, a), q in samp.items())
    ages = np.array([p[0] for p in pts]); qs = np.array([p[1] for p in pts])
    lg = ages[(ages >= 10000) & (ages <= 15000)]
    if len(lg) < 15 or ages.min() > 1250 or ages.max() < 14750:
        continue
    if statistics.median(np.diff(np.sort(lg))) > 100:
        continue
    if sum(1 for d in dates.get(s, []) if 9500 <= d <= 15500) < 2:
        continue
    m = (ages >= LO) & (ages < HI)
    pos = qs[m][qs[m] > 0]
    if not len(pos):
        continue
    y = np.log10(qs[m] + pos.min() / 2)
    if y.std() == 0:
        continue
    z = (y - y.mean()) / y.std()
    k = np.floor((ages[m] - A0) / W).astype(int)
    sites[s] = {int(kk): float(z[k == kk].mean()) for kk in np.unique(k)}
print("Tier C1 sites:", len(sites))
M, F, present = {}, {}, {}
for k in KS:
    v = [w[k] for w in sites.values() if k in w]
    if len(v) >= 0.5 * len(sites):
        M[k], F[k], present[k] = sum(v) / len(v), sum(1 for x in v if x >= 1.0) / len(v), len(v)
E = {}
for k in M:
    nb = [M[j] for j in range(k - 2, k + 3) if j in M]
    if len(nb) >= 3:
        E[k] = M[k] - statistics.median(nb)
rank = lambda w: (1 + sum(1 for k, v in w.items() if k and v > w[0]), len(w), round(w[0], 3))
print("E_mean rank, N, value:", rank(E)); print("F_peak rank, N, value:", rank(F), "sites at or above +1.0:", round(F[0] * present[0]), "of", present[0])
print("top windows by F_peak:", [(int(A0 + W * k), round(v, 3)) for k, v in sorted(F.items(), key=lambda kv: -kv[1])[:4]])
