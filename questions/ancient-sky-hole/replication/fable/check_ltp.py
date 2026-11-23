"""Cross-check of ltp.py against pyerfa (run in the scratch venv with pyerfa==2.0.1.5)."""
import numpy as np, erfa
from ltp import ltpequ
ep = np.linspace(-200000, 200000, 4001)
mine = ltpequ(ep)
ref = np.array([erfa.ltpequ(e) for e in ep])
d = np.degrees(np.arccos(np.clip((mine*ref).sum(1), -1, 1)))*3600
print("max angular difference vs erfa.ltpequ over +-200000 yr (arcsec):", d.max())
def radec(v):
    return np.degrees(np.arctan2(v[1], v[0])) % 360, np.degrees(np.arcsin(v[2]))
def sep(ra1, de1, ra2, de2):
    r = np.radians
    return np.degrees(np.arccos(np.sin(r(de1))*np.sin(r(de2)) + np.cos(r(de1))*np.cos(r(de2))*np.cos(r(ra1-ra2))))
# J2000 positions (approx., proper motion ignored): Thuban alpha Dra, Vega alpha Lyr
thuban = (211.0973, 64.3758); vega = (279.2347, 38.7837)
for lab, t in [("J2000", 2000.0), ("2750 BCE", -2749.0), ("12000 BCE", -11999.0), ("3000 BCE", -2999.0)]:
    ra, de = radec(ltpequ(t))
    print(lab, "NCP ra,dec = %.3f %.3f" % (ra, de), " sep Thuban %.2f deg, sep Vega %.2f deg" % (sep(ra, de, *thuban), sep(ra, de, *vega)))
for t in [2000.0, -2999.0]:
    pe = erfa.ltpecl(t); pq = erfa.ltpequ(t)
    print("obliquity at", t, np.degrees(np.arccos(np.dot(pe, pq))))
