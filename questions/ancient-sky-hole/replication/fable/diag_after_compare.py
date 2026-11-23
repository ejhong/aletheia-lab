"""POST-COMPARISON diagnostic (written after reading results/summary.json and analysis/skyhole.py).
Checks that the original log-likelihoods are reproduced with the 4-decimal rounded calibration, and that the
original M3 result is reproduced with a 0.2-deg refined R grid. Usage: python -I diag_after_compare.py <ptolemy.tsv> <hip.tsv> <this folder>"""
import sys, numpy as np
sys.path.insert(0, sys.argv[3])
import skyrep as s
hd = s.load_hip(sys.argv[2]); pt = s.load_ptolemy(sys.argv[1])
ok = np.isfinite(hd['ra'])&np.isfinite(hd['de'])
u0 = s.unit(hd['ra'],hd['de']); vel = s.pm_velocity(hd['ra'],hd['de'],hd['pma'],hd['pmd'])
u2k = s.directions(u0,vel,[2000.])[0]; lam,bet = s.to_ecliptic(u2k)
y = np.isin(hd['hip'], [r['HIP'] for r in pt if r['I'] in (1,2,3)]).astype(float)
m = ok&(hd['v']<=5.5)&(bet<=30)
S = dict(u0=u0[m],vel=vel[m],v=hd['v'][m],y=y[m],w=np.ones(m.sum()))
for cal in [dict(V50=4.415490932649737,sV=0.3089437760579218), dict(V50=4.4155,sV=0.3089)]:
    L = s.tile_ll_m1(S, cal, 0.25, [910.], [25.8], S['w'][:,None]).sum()
    print(cal, L)
# M3 with their R refinement (0.2 step around best)
cal = dict(V50=4.4155,sV=0.3089)
Rs = np.arange(37.5, 45.5+1e-9, 0.2)
best=(-1e9,)
for t in np.arange(-400, 401, 10.):
    dec = s.declinations(S['u0'],S['vel'],[t])[0]
    L = s.m3_ll(90+dec[None,:], Rs[:,None], S['v'], S['y'], cal) @ S['w']
    j=int(np.argmax(L))
    if L[j]>best[0]: best=(L[j],t,Rs[j])
print('M3 with R step 0.2 and rounded cal:', best)
