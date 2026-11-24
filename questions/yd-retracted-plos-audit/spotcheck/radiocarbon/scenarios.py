"""Item 6: recompute RESULTS 1.2 table (S0-S3 as locked: dR_hol + 0/200/500/800, err 50/100/150/200) with my own
calibrator for the YDB-target date in each core; check locked rule A1; add Heaton et al. 2023 bracket
(low = Holocene dR with Pearce error; high = Holocene dR + latitude GS boost interpolated from Table A2)."""
import sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import mycal

TARGET = {'52': ('UGAMS-50555', 11120, 40), '64': ('UGAMS-61104', 11489, 45), '67': ('UGAMS-61105', 11495, 30), '77': ('UGAMS-51366', 10810, 30)}
DRH = {'52': 71, '64': 218, '67': 218, '77': 103}
PEARCE_ERR = {'52': 69, '64': 135, '67': 135, '77': 106}
LAT = {'52': 75.58667, '64': 72.426113, '67': 72.434431, '77': 68.308682}
# Heaton et al. 2023 Table A2, GS scenario, northern latitudes (deg N -> 14C yr)
A2_LAT = [88.75, 86.25, 83.75, 81.25, 78.75, 76.25, 73.75, 71.25, 68.75, 66.25, 63.75]
A2_GS = [730, 720, 730, 740, 790, 870, 960, 1110, 1400, 1370, 1190]
SC = [('S0', 0, 50), ('S1', 200, 100), ('S2', 500, 150), ('S3', 800, 200)]
RESULTS_TABLE = {  # RESULTS.md 1.2 medians as printed
    '52': (12404, 12116, 11642, 11222), '64': (12627, 12411, 11993, 11543),
    '67': (12633, 12422, 12003, 11551), '77': (11889, 11570, 11155, 10742)}

a1 = 0
for core, (lab, c14, err) in TARGET.items():
    print(f'\nCore {core} {lab} {c14}+-{err}')
    for i, (s, add, ee) in enumerate(SC):
        c = mycal.calibrate(c14, err, 'Marine20', DRH[core] + add, ee)
        flag = c['median'] < 12500 or c['p_12900_12700'] < 0.10
        if s == 'S2':
            a1 += flag
        print(f"  {s}: dR={DRH[core]+add}+-{ee}  median={c['median']:.0f} (RESULTS {RESULTS_TABLE[core][i]})  h95={c['h95']}  "
              f"P(12900-12700)={c['p_12900_12700']:.3f}  P(<11700)={c['p_lt11700']:.2f}  A1-condition={flag}")
    boost = float(np.interp(LAT[core], A2_LAT[::-1], A2_GS[::-1]))
    lo = mycal.calibrate(c14, err, 'Marine20', DRH[core], PEARCE_ERR[core])
    hi = mycal.calibrate(c14, err, 'Marine20', DRH[core] + boost, PEARCE_ERR[core])
    print(f"  Heaton2023 bracket (lat {LAT[core]:.2f}N, GS boost {boost:.0f}): low median={lo['median']:.0f} h95={lo['h95']} P(YDB)={lo['p_12900_12700']:.3f};"
          f" high median={hi['median']:.0f} h95={hi['h95']} P(YDB)={hi['p_12900_12700']:.3f}")
print(f'\nA1 (locked rule: under S2, >=2 of 4 cores with median <12500 or P(12900-12700)<0.10): {a1}/4 -> {"PASS (triggered)" if a1 >= 2 else "not triggered"}')
# A1 already under S0?
n0 = sum((lambda c: c['median'] < 12500 or c['p_12900_12700'] < 0.10)(mycal.calibrate(t[1], t[2], 'Marine20', DRH[k], 50)) for k, t in TARGET.items())
print(f'Same condition under S0 (no deglacial boost): {n0}/4')
# Sensitivity: 625-630 if its 14C age were 11020 (the value that reproduces the published 12992+-84 under the IntCal20 recipe)
for s, add, ee in SC:
    c = mycal.calibrate(11020, 40, 'Marine20', 71 + add, ee)
    print(f'Core 52 625-630 if 14C=11020: {s} median={c["median"]:.0f} P(YDB)={c["p_12900_12700"]:.3f}')
# Core 67 30-32 cm (UGAMS-51985 11280+-30)
for s, add, ee in SC[:1]:
    c = mycal.calibrate(11280, 30, 'Marine20', 218 + add, ee)
    print(f'Core 67 30-32 (11280+-30) S0 (err 50): median={c["median"]:.0f} mean={c["mean"]:.0f}')
c = mycal.calibrate(11280, 30, 'Marine20', 218, 135)
print(f'Core 67 30-32 (11280+-30) dR=218+-135: median={c["median"]:.0f} mean={c["mean"]:.0f}')
