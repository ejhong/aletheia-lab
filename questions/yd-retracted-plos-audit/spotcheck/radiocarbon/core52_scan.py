"""Core 52 robust scan (vectorised over dR): for each curve, dR (1-yr steps, -800..+300) and dR_err, count how many of
the 6 UGAMS dates and of the 9 dates <20 ka are reproduced to within 3 yr on both mu and sd. Grid 0..25,000 cal BP.
Also: same scan for Cores 64/67/77 (to test uniqueness of the -dR recipe) and an inversion for 625-630."""
import sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import mycal

G = np.arange(0, 25001, 1.0)
CV = {k: (np.interp(G, *v[:2]), np.interp(G, v[0], v[2])) for k, v in mycal.CURVES.items()}
DRS = np.arange(-800, 301, 1.0)

def mean_sd(c14, err, curve, ee):
    m, s = CV[curve]
    v = err**2 + s**2 + ee**2
    out_m = np.empty(len(DRS)); out_s = np.empty(len(DRS))
    for i0 in range(0, len(DRS), 100):
        d = DRS[i0:i0+100][:, None]
        lp = -0.5 * (c14 - d - m[None, :])**2 / v[None, :] - 0.5 * np.log(v)[None, :]
        p = np.exp(lp - lp.max(axis=1, keepdims=True)); p /= p.sum(axis=1, keepdims=True)
        mu = (p * G).sum(axis=1); sd = np.sqrt((p * (G[None, :] - mu[:, None])**2).sum(axis=1))
        out_m[i0:i0+100] = mu; out_s[i0:i0+100] = sd
    return out_m, out_s

TAB = {'52': 69, '64': 135, '67': 135, '77': 106}
allrows = [r for r in mycal.table_s1() if float(r['c14']) < 20000]
for core in ('52', '64', '67', '77'):
    rows = [r for r in allrows if r['core'] == core]
    print(f'\n=== Core {core}: {len(rows)} dates <20 ka 14C; count of dates with |dmu|<=3 and |dsd|<=3')
    for curve in ('IntCal20', 'Marine20', 'IntCal13', 'Marine13'):
        res = []
        for ee in sorted({0, 50, TAB[core], 100}):
            ok = np.zeros(len(DRS), int); ok_ug = np.zeros(len(DRS), int)
            for r in rows:
                mu, sd = mean_sd(float(r['c14']), float(r['err']), curve, ee)
                hit = (np.abs(mu - float(r['mu'])) <= 3) & (np.abs(sd - float(r['sigma'])) <= 3)
                ok += hit
                if r['lab_id'].startswith('UGAMS'):
                    ok_ug += hit
            for i in np.argsort(-ok)[:3]:
                res.append((int(ok[i]), int(ok_ug[i]), int(DRS[i]), ee))
        res.sort(reverse=True)
        print(f'  {curve:9s} best (n_matched, n_UGAMS_matched, dR, dR_err): {res[:4]}')

r = [x for x in allrows if x['depth'] == '625-630'][0]
print('\n625-630 inversion (IntCal20, dR=-71, err 69): 14C age -> mean, sd, h68, h95')
for c14 in range(11000, 11141, 10):
    c = mycal.calibrate(c14, 40, 'IntCal20', -71, 69)
    print(f'  {c14}: {c["mean"]:.0f} +- {c["sd"]:.0f}  h68={c["h68"]} h95={c["h95"]}')
print('published: 12992 +- 84, h68 13093-12924, h95 13161-12830')
