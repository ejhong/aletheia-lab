"""Free scan: for each core and curve, which single offset dR (step 2 yr, -1000..+1000) and dR_err best reproduce the
published mu column? Excludes the two >30 ka dates (Beta-8896, UCIAMS-181265). Reports max and median |mu diff| and
max |sd diff| at the best dR, so one can see whether the sign-flip / IntCal recipe is unique."""
import sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import mycal

rows = [r for r in mycal.table_s1() if float(r['c14']) < 20000]
TAB = {'52': 69, '64': 135, '67': 135, '77': 106}
for core in ('52', '64', '67', '77'):
    cr = [r for r in rows if r['core'] == core]
    print(f'\n=== Core {core}: {len(cr)} dates (<20 ka 14C)')
    for curve in ('Marine20', 'IntCal20', 'Marine13', 'IntCal13'):
        best = None
        for ee in sorted({TAB[core], 0, 50, 100}):
            # coarse then fine
            for dR in np.arange(-1000, 1001, 10):
                diffs = [mycal.calibrate(float(r['c14']), float(r['err']), curve, dR, ee, step=2)['mean'] - float(r['mu']) for r in cr]
                score = max(abs(x) for x in diffs)
                if best is None or score < best[0]:
                    best = (score, dR, ee)
        _, dR0, ee0 = best
        fine = None
        for dR in np.arange(dR0 - 12, dR0 + 13, 1):
            cals = [mycal.calibrate(float(r['c14']), float(r['err']), curve, dR, ee0) for r in cr]
            d = [c['mean'] - float(r['mu']) for c, r in zip(cals, cr)]
            s = [c['sd'] - float(r['sigma']) for c, r in zip(cals, cr)]
            score = max(abs(x) for x in d)
            if fine is None or score < fine[0]:
                fine = (score, dR, d, s)
        score, dR, d, s = fine
        print(f'  {curve:9s} best dR={dR:+6.0f} dR_err={ee0:4.0f}: max|dmu|={score:7.1f} median|dmu|={np.median(np.abs(d)):6.1f} max|dsd|={max(abs(x) for x in s):6.1f}  per-date dmu={[round(x,1) for x in d]}')
