"""Independent single-date radiocarbon calibrator (written for this spot check; does not reuse the study's code).

Likelihood on a 1-yr calendar grid: N(c14 - dR ; curve_mu(t), sqrt(err^2 + curve_sig(t)^2 + dR_err^2)),
with the 1/sigma normalisation, as OxCal does for R_Date with a Delta_R(mean, sd) offset.
Outputs mean and sd (OxCal's mu/sigma), median, outer bounds of the 68.3 / 95.4 % HPD region.
"""
import csv, pathlib
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent.parent

def read_curve(path):
    rows = []
    for line in open(path, encoding='utf-8', errors='replace'):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        parts = s.replace(',', ' ').split()
        try:
            rows.append([float(parts[0]), float(parts[1]), float(parts[2])])
        except (ValueError, IndexError):
            continue
    a = np.array(rows)
    a = a[np.argsort(a[:, 0])]
    return a[:, 0], a[:, 1], a[:, 2]

CURVES = {
    'Marine20': read_curve(HERE / 'curves/marine20.14c'),
    'IntCal20': read_curve(HERE / 'curves/intcal20.14c'),
    'Marine13': read_curve(HERE / 'curves/marine13.14c'),
    'IntCal13': read_curve(HERE / 'curves/intcal13.14c'),
}

def calibrate(c14, err, curve, dR=0.0, dR_err=0.0, step=1.0):
    t, mu, sg = CURVES[curve] if isinstance(curve, str) else curve
    lo = max(t[0], 0.0); hi = t[-1]
    g = np.arange(lo, hi + step, step)
    m = np.interp(g, t, mu); s = np.interp(g, t, sg)
    v = err**2 + s**2 + dR_err**2
    lp = -0.5 * (c14 - dR - m)**2 / v - 0.5 * np.log(v)
    p = np.exp(lp - lp.max()); p /= p.sum()
    mean = float((p * g).sum()); sd = float(np.sqrt((p * (g - mean)**2).sum()))
    cdf = np.cumsum(p); med = float(np.interp(0.5, cdf, g))
    order = np.argsort(p)[::-1]; cs = np.cumsum(p[order])
    def hpd(level):
        k = int(np.searchsorted(cs, level)) + 1
        sel = g[order[:k]]
        return float(sel.min()), float(sel.max())
    def prob(a, b):
        return float(p[(g >= a) & (g <= b)].sum())
    return dict(mean=mean, sd=sd, median=med, h68=hpd(0.6827), h95=hpd(0.9545),
                p_12900_12700=prob(12700, 12900), p_yd=prob(11700, 12900), p_lt11700=float(p[g < 11700].sum()))

def table_s1():
    return list(csv.DictReader(open(HERE / 'scripts/table_s1_mine.csv')))
