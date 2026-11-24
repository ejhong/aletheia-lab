"""Item 2: which three ages reproduce the paper's chi2 = 0.057, weighted mean 12,801.6 cal BP?"""
import itertools
import numpy as np
from scipy.stats import chi2

def ww(a, s):
    a = np.asarray(a, float); s = np.asarray(s, float); w = 1/s**2
    m = (w*a).sum()/w.sum(); T = (w*(a-m)**2).sum(); df = len(a)-1
    return m, T, 1-chi2.cdf(T, df)

# Kennett 2025 SI Tables S2-S4 (unmodelled IntCal20 mu, sigma) as read from the images
AC = {"AC 482.5 cm (S2)": (12810, 60), "AC 500.5 cm (S2)": (12955, 60)}
BW = {"BW AA-89168 (S3)": (12825, 65), "BW SMU-1880 (S3)": (12760, 105), "BW AA-1362 (S3)": (12710, 95)}
MS = {"MS Haynes 10885+-50 (S4)": (12805, 45)}
# Kennett 2015 PNAS Bayesian modelled YDB ages (68%), quoted in Kennett 2025 'Radiocarbon dating' section
K15 = {"AC K2015 modelled": (12805, 55), "BW K2015 modelled": (12775, 365), "MS K2015 modelled": (12750, 235)}

print("Paper reports: weighted mean 12,801.6 cal BP; chi2 = 0.057, df 2, p = 0.972\n")
print("One SI row per site:")
for a, b, c in itertools.product(AC.items(), BW.items(), MS.items()):
    m, T, p = ww([a[1][0], b[1][0], c[1][0]], [a[1][1], b[1][1], c[1][1]])
    print(f"  {a[0]:18s} | {b[0]:18s} | {c[0]:24s}  mean {m:8.1f}  chi2 {T:6.3f}  p {p:.3f}")
m, T, p = ww([v[0] for v in K15.values()], [v[1] for v in K15.values()])
print(f"\nKennett 2015 modelled ages (12805+-55, 12775+-365, 12750+-235): mean {m:.1f} chi2 {T:.3f} p {p:.3f}")
# search any 3 of all 6 SI rows + 3 modelled
pool = {**AC, **BW, **MS, **K15}
print("\nAll triples from SI rows + K2015 modelled with |mean-12801.6|<1.5 or |chi2-0.057|<0.01:")
for trip in itertools.combinations(pool.items(), 3):
    m, T, p = ww([t[1][0] for t in trip], [t[1][1] for t in trip])
    if abs(m-12801.6) < 1.5 or abs(T-0.057) < 0.01:
        print("  ", [t[0] for t in trip], f"mean {m:.2f} chi2 {T:.4f} p {p:.4f}")
# Study's numbers
print("\nStudy's reconstructions:")
for lab, a, s in [("482.5 + AA-89168 + MS", [12810,12825,12805],[60,65,45]),
                  ("500.5 + AA-89168 + MS", [12955,12825,12805],[60,65,45]),
                  ("all 6 SI rows", [12810,12955,12825,12760,12710,12805],[60,60,65,105,95,45])]:
    m, T, p = ww(a, s); print(f"  {lab:24s} mean {m:.2f} chi2 {T:.3f} p {p:.3f}")
print("  ratio 4.209/0.064 =", round(4.209/0.064, 1), "; ratio vs paper's 0.057:", round(4.209/0.057, 1))
