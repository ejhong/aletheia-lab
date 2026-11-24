"""Spot check (my own, independent of the study code and of the earlier checker's 5' version):
classify every 1-arc-minute ETOPO cell with z<0 by the connected water body it belongs to (8-connectivity,
dateline wrapped), then for all 927 societies integrate -120<=z<0 area within 250 km by class, and the
distance to the nearest cell of the world ocean (+ Black Sea/Azov and Lake Maracaibo, real seas or sea-linked
lagoons cut off at this resolution). Usage: python -I sea_1min.py <data_dir> <study_json> <out_dir>"""
import sys, json, math, numpy as np, pandas as pd, h5py
from scipy import ndimage

D, J, OUT = sys.argv[1:4]
R = 6371.0088
f = h5py.File(f'{D}/ETOPO_2022_v1_60s_N90W180_bed.nc', 'r')
lat = f['lat'][:]; lon = f['lon'][:]
z = f['z'][:]
wet = z < 0
lab, n = ndimage.label(wet, structure=np.ones((3, 3), bool))
# wrap the dateline: merge labels touching across column 0 / last column
pairs = set()
H = lab.shape[0]
for r in range(H):
    u = lab[r, 0]
    if not u: continue
    for rr_ in (r - 1, r, r + 1):
        if 0 <= rr_ < H:
            v = lab[rr_, -1]
            if v and v != u: pairs.add((min(u, v), max(u, v)))
parent = np.arange(n + 1)
def find(x):
    while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
    return x
for u, v in pairs:
    ru, rv = find(u), find(v)
    if ru != rv: parent[max(ru, rv)] = min(ru, rv)
for i in range(n + 1): parent[i] = find(i)
lab = parent[lab]
sizes = np.bincount(lab.ravel()); sizes[0] = 0
ocean = sizes.argmax()
def at(la, lo): return lab[np.abs(lat - la).argmin(), np.abs(lon - lo).argmin()]
named = {'Black Sea (43,34)': at(43.0, 34.0), 'Azov (46,36.5)': at(46.0, 36.5), 'Caspian (42,50.5)': at(42.0, 50.5),
         'Maracaibo (9.8,-71.6)': at(9.8, -71.6), 'L.Superior (47.7,-87.5)': at(47.7, -87.5), 'L.Ontario (43.7,-77.9)': at(43.7, -77.9),
         'Baikal (53.5,108)': at(53.5, 108.0), 'Mediterranean (35,18)': at(35.0, 18.0), 'Baltic (57,19)': at(57.0, 19.0),
         'Hudson Bay (60,-85)': at(60.0, -85.0), 'Red Sea (20,38)': at(20.0, 38.0), 'Persian Gulf (27,51)': at(27.0, 51.0)}
print('components', n, 'world-ocean label', ocean, 'cells', sizes[ocean], 'share of wet cells', round(sizes[ocean] / wet.sum(), 4))
for k, v in named.items(): print(f'  {k:28s} label {v:8d}  in world ocean: {v == ocean}  cells {sizes[v] if v else 0}')
SEA = {ocean, named['Black Sea (43,34)'], named['Azov (46,36.5)'], named['Maracaibo (9.8,-71.6)']} - {0}
CASP = named['Caspian (42,50.5)']
cls = np.zeros(lab.shape, np.int8)       # 0 land, 1 world ocean, 2 Black Sea/Azov/Maracaibo, 3 Caspian, 4 other below-0 cells
cls[wet] = 4
cls[lab == CASP] = 3
for s in SEA - {ocean}: cls[lab == s] = 2
cls[lab == ocean] = 1
del lab, wet
dA = math.radians(1 / 60)
cosl = np.cos(np.radians(lat))

def gc(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2); dl = np.radians(lo2 - lo1)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))

mp = pd.DataFrame(json.load(open(J))['map_points'])
rr = pd.read_stata(f'{D}/Berezkin_groups_Regressions_Ready.dta')
need = ["latitude_forgeo", "longitude_forgeo", "motifs_total", "lnnmbr_title", "lnyear_firstpub", "lnriver_dist_bere", "lnbdisttoquake1000", "avtemp200_bere"]
rr = rr.dropna(subset=need).reset_index(drop=True)
assert len(rr) == len(mp) and (rr.group_Berezkin.astype(str).values == mp.g.values).all()
rows = []
RAD = 260.0
for la, lo in zip(rr.latitude_forgeo.astype(float).values, rr.longitude_forgeo.astype(float).values):
    dlat = RAD / 110.0 + 0.05
    i0 = max(0, np.searchsorted(lat, la - dlat)); i1 = min(len(lat), np.searchsorted(lat, la + dlat) + 1)
    dlon = min(180.0, RAD / (111.0 * max(0.02, math.cos(math.radians(min(89.95, abs(la) + dlat))))) + 0.05)
    jj = np.where(np.abs(((lon - lo + 180) % 360) - 180) <= dlon)[0]
    c = cls[i0:i1][:, jj]; zz = z[i0:i1][:, jj]
    d = gc(la, lo, lat[i0:i1][:, None], lon[jj][None, :])
    area = (R * dA) ** 2 * cosl[i0:i1][:, None] * np.ones(c.shape)
    w = d <= 250.0; dr = w & (zz >= -120) & (zz < 0)
    r = {f'd120_c{k}': float(area[dr & (c == k)].sum()) for k in (1, 2, 3, 4)}
    r['d60_sea'] = float(area[w & (zz >= -60) & (zz < 0) & ((c == 1) | (c == 2))].sum())
    r['ocean250_sea'] = float(area[w & ((c == 1) | (c == 2))].sum())
    r['d120_sea_lt'] = float(area[w & (zz >= -120) & (zz < 0) & ((c == 1) | (c == 2))].sum())
    anyw = c > 0; sea = (c == 1) | (c == 2)
    r['dist_any_km'] = float(d[anyw].min()) if anyw.any() else 999.0
    r['dist_sea_km'] = float(d[sea].min()) if sea.any() else 999.0   # 999 = beyond ~260 km
    rows.append(r)
X = pd.DataFrame(rows)
X.insert(0, 'g', mp.g.values); X.insert(1, 'lat', mp.lat.values); X.insert(2, 'lon', mp.lon.values)
X['study_c'] = mp.c.values; X['study_d120'] = mp.d120.values
X['d120_all_1min'] = X[['d120_c1', 'd120_c2', 'd120_c3', 'd120_c4']].sum(1)
X['d120_sea'] = X.d120_c1 + X.d120_c2
X.to_csv(f'{OUT}/sea_1min.csv', index=False)
co = X[X.study_c == 1]
print('\nAll 927: 1-arcmin all-below-0 d120 vs study 5-arcmin d120: Spearman %.4f, median ratio %.3f' % (
    X.d120_all_1min.corr(X.study_d120, method='spearman'), (X.d120_all_1min / X.study_d120.clip(lower=1))[X.study_d120 > 0].median()))
print('Coastal by study rule (any z<0 within 150 km, 1-arcmin): %d (study 396); by sea rule: %d' % ((X.dist_any_km <= 150).sum(), (X.dist_sea_km <= 150).sum()))
tot = co[['d120_c1', 'd120_c2', 'd120_c3', 'd120_c4']].sum()
print('Study-coastal societies (n=%d): summed -120..0 area within 250 km by class (km2):' % len(co))
for k, nm in zip(tot.index, ['world ocean', 'Black Sea/Azov/Maracaibo', 'Caspian', 'other below-0 (lakes, depressions, rivers)']):
    print(f'   {nm:44s} {tot[k]:14,.0f}  {100 * tot[k] / tot.sum():5.1f}%')
nonsea = co.d120_c3 + co.d120_c4
print('Study-coastal societies with >20%% of their d120 not sea: %d ; >50%%: %d ; with zero sea within 150 km: %d' % (
    (nonsea > 0.2 * co.d120_all_1min).sum(), (nonsea > 0.5 * co.d120_all_1min).sum(), (co.dist_sea_km > 150).sum()))
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 200)
bad = co[(nonsea > 0.2 * co.d120_all_1min) | (co.dist_sea_km > 150)].copy()
bad['pct_nonsea'] = (100 * (bad.d120_c3 + bad.d120_c4) / bad.d120_all_1min.clip(lower=1)).round(0)
print(bad[['g', 'lat', 'lon', 'study_d120', 'd120_c1', 'd120_c2', 'd120_c3', 'd120_c4', 'pct_nonsea', 'dist_any_km', 'dist_sea_km']].round(0).sort_values('pct_nonsea', ascending=False).to_string(index=False))
