"""Refit the study's primary model with drowned-shelf exposure restricted to real sea (1-arcmin, from sea_1min.py).
All variants beyond row 'A' are post-hoc spot-check sensitivity analyses, not the locked protocol.
Usage: python -I refit_sea.py <data_dir> <study_json> <out_dir>"""
import sys, json, math, numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import norm, t as tdist
D, J, OUT = sys.argv[1:4]; R = 6371.0088
rr = pd.read_stata(f'{D}/Berezkin_groups_Regressions_Ready.dta')
mot = pd.read_stata(f'{D}/Motifs_Berezkin_groups.dta', convert_categoricals=False)
NB = ["c2", "c4", "c7", "c9a", "c10", "c10a", "c12a", "c12b", "c13", "c14", "b7b", "b7d", "b52a", "g9a", "i81a", "k38d", "l28a"]
for c in NB + ["c3", "c5a"]: mot[c] = pd.to_numeric(mot[c], errors='coerce').fillna(0)
mot['nb'] = mot[NB].sum(axis=1); mot['noah'] = mot[['c3', 'c5a']].sum(axis=1)
need = ["latitude_forgeo", "longitude_forgeo", "motifs_total", "lnnmbr_title", "lnyear_firstpub", "lnriver_dist_bere", "lnbdisttoquake1000", "avtemp200_bere"]
df = rr.merge(mot[['oid', 'nb', 'noah']], on='oid').dropna(subset=need).reset_index(drop=True)
mp = pd.DataFrame(json.load(open(J))['map_points'])
s1 = pd.read_csv(f'{OUT}/sea_1min.csv')
s5 = pd.read_csv(f'{OUT}/exposure_sea_only.csv')   # earlier checker's 5' connected-sea distances, used only for inland distances >260 km
assert (s1.g.values == df.group_Berezkin.astype(str).values).all() and (s5.g.values == s1.g.values).all()
df['c_study'] = mp.c.values; df['d120_study'] = mp.d120.values
for c in ['d120_sea', 'd60_sea', 'ocean250_sea', 'dist_sea_km', 'dist_any_km', 'd120_c3', 'd120_c4']: df[c] = s1[c].values
df['dist_sea'] = np.where(df.dist_sea_km < 999, df.dist_sea_km, s5.dist_sea_km.values)
chk = df[(df.dist_sea_km < 999)]; print('5\' vs 1\' sea distance (where <260 km): median abs diff %.1f km' % (chk.dist_sea_km - s5.dist_sea_km.values[df.dist_sea_km < 999]).abs().median())
df['c_sea'] = (df.dist_sea <= 150).astype(int)
df['share'] = df.nb / df.motifs_total.clip(lower=1); df['anynb'] = (df.nb > 0).astype(float)
for c in ['share', 'flood_related', 'earthquake_related', 'sea_related', 'fire_related']:
    s = df[c].astype(float); df[c + '_z'] = (s - s.mean()) / s.std(ddof=0)
df['log_mt'] = np.log1p(df.motifs_total.astype(float)); df['abs_lat'] = df.latitude_forgeo.abs()
df['ld120_study'] = np.log1p(df.d120_study); df['ld120_sea'] = np.log1p(df.d120_sea); df['ld60_sea'] = np.log1p(df.d60_sea)
df['frac_sea'] = np.where(df.ocean250_sea > 0, df.d120_sea / df.ocean250_sea.clip(lower=1e-9), 0.0)
df['log_dist_sea'] = np.log1p(df.dist_sea)

def gcmat(la, lo):
    la, lo = np.radians(la), np.radians(lo); x = np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    # haversine form: no arccos round-off on the diagonal
    dla = la[:, None] - la[None, :]; dlo = lo[:, None] - lo[None, :]
    a = np.sin(dla / 2) ** 2 + np.cos(la)[:, None] * np.cos(la)[None, :] * np.sin(dlo / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))

def fit(sub, y, x, ctrl, label, fe='language1'):
    sub = sub.reset_index(drop=True)
    xv = sub[x].astype(float); X = pd.DataFrame({'x': (xv - xv.mean()) / xv.std(ddof=0)})
    for c in ctrl: X[c] = sub[c].astype(float)
    if fe: X = pd.concat([X, pd.get_dummies(sub[fe].astype(str), prefix='fe', drop_first=True, dtype=float)], axis=1)
    X = sm.add_constant(X)
    m = sm.OLS(sub[y].astype(float), X).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(sub.language1.astype(str))[0]}, use_t=True)
    Dm = gcmat(sub.latitude_forgeo.values.astype(float), sub.longitude_forgeo.values.astype(float))
    Xa = X.values; e = m.resid.values; XtXi = np.linalg.pinv(Xa.T @ Xa); Xe = Xa * e[:, None]
    W = np.maximum(0, 1 - Dm / 1000.0); sc = math.sqrt((XtXi @ (Xe.T @ W @ Xe) @ XtXi)[1, 1])
    b, se = m.params['x'], m.bse['x']; G = sub.language1.nunique()
    fam = sub.language1.value_counts()
    print(f"{label:70s} n={len(sub):3d} G={G:2d} sing={int((fam == 1).sum()):2d} b={b:+.4f} se_cl={se:.4f} p_cl={m.pvalues['x']:.3f} "
          f"95%CI_cl=[{b - tdist.ppf(.975, G - 1) * se:+.3f},{b + tdist.ppf(.975, G - 1) * se:+.3f}] se_c1k={sc:.4f} p_c1k={2 * norm.sf(abs(b / sc)):.3f} "
          f"95%CI_c1k=[{b - 1.96 * sc:+.3f},{b + 1.96 * sc:+.3f}]")
    return b, se, sc

M1s = ['log_dist_coast', 'lnnmbr_title', 'lnyear_firstpub', 'log_mt']
M2s = M1s + ['lnriver_dist_bere', 'lnbdisttoquake1000', 'avtemp200_bere', 'abs_lat']
# study's dist_coast for row A: nearest any-z<0 cell at 5' (reconstructed by earlier checker, asserted equal to study coastal flag)
comp = pd.read_csv(f'{OUT}/exposure_components.csv')
df['log_dist_coast_study'] = np.nan
co_st = df[df.c_study == 1].copy()
print('\n== A. Study as published (396 coastal by any-z<0 rule; study exposure). Control = log dist to nearest any z<0 cell at 1\' (approx.) ==')
co_st['log_dist_coast'] = np.log1p(co_st.dist_any_km)
fit(co_st, 'share_z', 'ld120_study', M2s, 'A  nb share, M4, study exposure (1\' distance control)')
print('\n== B. Same 396 societies, exposure recomputed counting only connected sea (+Black Sea/Azov) ==')
fit(co_st, 'share_z', 'ld120_sea', M2s, 'B  nb share, M4, sea-only exposure, same sample')
print('\n== C. Coastal = within 150 km of real sea (1\'); exposure sea-only; control log dist to sea ==')
cs = df[df.c_sea == 1].copy(); cs['log_dist_coast'] = cs.log_dist_sea
print('   sample', len(cs), '| in study sample but not here:', int(((df.c_study == 1) & (df.c_sea == 0)).sum()), '| here but not in study:', int(((df.c_study == 0) & (df.c_sea == 1)).sum()))
r = {}
r['C_nb'] = fit(cs, 'share_z', 'ld120_sea', M2s, 'C1 nb share M4 (primary analogue)')
fit(cs, 'flood_related_z', 'ld120_sea', M2s, 'C2 flood_related M4')
fit(cs, 'anynb', 'ld120_sea', M2s, 'C3 any nb (LPM) M4')
fit(cs[cs.noah == 0], 'share_z', 'ld120_sea', M2s, 'C4 Noah-free nb share M4')
fit(cs[cs.noah == 0], 'flood_related_z', 'ld120_sea', M2s, 'C5 Noah-free flood_related M4')
fit(cs, 'share_z', 'ld120_sea', M2s + [], 'C6 nb share M3 (continent FE)', fe='continent_bere')
fit(cs, 'share_z', 'ld60_sea', M2s, 'C7 nb share M4, -60 m sea-only')
fit(cs, 'share_z', 'frac_sea', M2s, 'C8 nb share M4, shelf fraction of sea')
fit(cs, 'flood_related_z', 'frac_sea', M2s, 'C9 flood_related M4, shelf fraction of sea')
fit(cs, 'fire_related_z', 'ld120_sea', M2s, 'C10 fire negative control M4')
fit(cs[cs.abs_lat < 50], 'share_z', 'ld120_sea', M2s, 'C11 nb share M4, |lat|<50')
fit(cs[cs.abs_lat < 30], 'share_z', 'ld120_sea', M2s, 'C12 nb share M4, |lat|<30')
print('\n== Quartiles under C (sea-only exposure, sea-defined coastal) ==')
q = np.quantile(cs.d120_sea, [0, .25, .5, .75, 1])
for i in range(4):
    m = (cs.d120_sea >= q[i]) & ((cs.d120_sea <= q[i + 1]) if i == 3 else (cs.d120_sea < q[i + 1]))
    print(f'   Q{i + 1} {q[i]:8.0f}-{q[i + 1]:8.0f} km2 n={m.sum()} any NB={100 * cs[m].anynb.mean():.1f}% mean share={100 * cs[m].share.mean():.2f}%')
print('\n== Study Q4 (top 99 by study exposure): how many have no real sea within 150 km ==')
st = df[df.c_study == 1].sort_values('d120_study', ascending=False).head(99)
print('   ', int((st.c_sea == 0).sum()), 'of 99:', ', '.join(st[st.c_sea == 0].group_Berezkin.astype(str)))
print('\n== Positive control 2 (sea motifs vs proximity) with sea-only distance, as coded by the study (global, lang FE, sampling + abs lat) ==')
df['neg_ld_sea'] = -df.log_dist_sea; df['neg_ld_any'] = -np.log1p(np.where(df.dist_any_km < 999, df.dist_any_km, np.nan))
fit(df, 'sea_related_z', 'neg_ld_sea', ['lnnmbr_title', 'lnyear_firstpub', 'log_mt', 'abs_lat'], 'PC2 sea_related ~ -log(1+dist to real sea)')
# power / precision for primary
b, se, sc = r['C_nb']
