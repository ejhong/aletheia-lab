"""Item 3: recompute the study's T on its '25 published direct YDB-stratum dates'; per site; leave-one-out;
contributions; and a corrected Arlington Canyon set read from Kennett et al. 2008 QSR Table 4 (p. 2536)."""
import numpy as np
from scipy.stats import chi2

def ww(a, s):
    a = np.asarray(a, float); s = np.asarray(s, float); w = 1/s**2
    m = (w*a).sum()/w.sum(); T = (w*(a-m)**2).sum(); df = len(a)-1
    return m, 1/np.sqrt(w.sum()), T, df, chi2.sf(T, df), w*(a-m)**2

# The study's PUBLISHED_DIRECT_INVENTORY, copied from analysis/audit_plos_retractions.py lines ~170-205
STUDY = {
 "Arlington Canyon": [("UCIAMS-36305",10960,50),("UCIAMS-36306",11185,30),("UCIAMS-36307",11075,30),("UCIAMS-36308",11110,35),
   ("UCIAMS-36309",11440,90),("UCIAMS-36960",11070,25),("UCIAMS-36961",11105,30),("UCIAMS-36962",11105,30),
   ("UCIAMS-42817",11100,30),("UCIAMS-42818",11095,25),("UCIAMS-42819",11050,30)],
 "Blackwater Draw": [("A-481",11170,360),("A-490",11040,500),("A-491",11630,400),("UCIAMS-24212",11300,240),("A-489",10490,200),("A-379",10780,100)],
 "Murray Springs": [("A-805",11150,450),("A-805A",11230,340),("A-805B",10930,170),("A-805C",10890,180),("A-805D",10840,70),
   ("A-805E",10840,140),("A-805F",10710,160),("Tx-1413",10760,100)],
}
# Kennett et al. 2008 QSR 27:2528-2543, Table 4 (p. 2536), as extracted by pdftotext from the hash-verified PDF.
# (lab, depth cm, 14C, err, material, footnote)
K08 = [("UCIAMS-47235","95-99",11040,30,"Charcoal",""),("UCIAMS-47236","179-183",12095,40,"Charcoal","e rejected"),
 ("UCIAMS-47237","215-217",10895,35,"Charcoal",""),("UCIAMS-47238","267-270",11105,30,"Charcoal",""),
 ("UCIAMS-47239","392-396",11105,30,"Charcoal",""),("UCIAMS-42816","403-406",11095,25,"Wood (log)",""),
 ("UCIAMS-36308","464-469",11095,25,"Wood",""),("UCIAMS-36307","469-475",11070,25,"Wood",""),
 ("UCIAMS-36306","485-491",11375,25,"Wood","f old wood"),("UCIAMS-36959","480-485",11075,30,"Charcoal",""),
 ("UCIAMS-36960","480-485",11185,30,"Glassy carbon","f old wood"),("UCIAMS-36961","480-485",11440,90,"Carbon sphere","f old wood"),
 ("UCIAMS-36962","480-485",11110,35,"Carbon elongate","f old wood"),("Beta-161032","480-485",10860,70,"Wood (pine)",""),
 ("UCIAMS-36305","493-498",11235,25,"Wood","f old wood"),("UCIAMS-36304","498-503",11020,25,"Wood","")]
k08 = {r[0]: r for r in K08}

def show(label, rows):
    m, e, T, df, p, c = ww([r[1] for r in rows], [r[2] for r in rows])
    print(f"{label:58s} n={len(rows):2d} mean {m:8.1f}+-{e:4.1f}  T={T:7.2f} df={df:2d} p={p:.2e}")
    return T, c

print("=== A. The study's 25 dates ===")
allrows = [r for v in STUDY.values() for r in v]
T, c = show("All 25 (study)", allrows)
for site, rows in STUDY.items():
    show(f"  {site} only", rows)
print("\nContribution of each date to T=%.2f (largest first):" % T)
for i in np.argsort(-c):
    print(f"   {allrows[i][0]:14s} {allrows[i][1]:6d}+-{allrows[i][2]:<4d} {c[i]:6.2f}")
print("\nLeave-one-out T:")
loo = []
for i in range(len(allrows)):
    rows = allrows[:i]+allrows[i+1:]
    m, e, Ti, df, p, _ = ww([r[1] for r in rows], [r[2] for r in rows]); loo.append((Ti, allrows[i][0], p))
for Ti, lab, p in sorted(loo):
    print(f"   drop {lab:14s} T={Ti:6.2f} p={p:.2e}")
print("\nLeave-one-site-out:")
for site in STUDY:
    rows = [r for s, v in STUDY.items() if s != site for r in v]; show(f"  without {site}", rows)

print("\n=== B. Check the study's Arlington Canyon list against Kennett 2008 Table 4 ===")
for lab, a, s in STUDY["Arlington Canyon"]:
    real = k08.get(lab)
    if real is None:
        hit = [r[0] for r in K08 if (r[2], r[3]) == (a, s)]
        print(f"   {lab:13s} study {a}+-{s:<3d}: LAB ID NOT IN TABLE 4; value matches {hit or 'nothing'}")
    else:
        ok = (real[2], real[3]) == (a, s)
        hit = [r[0] for r in K08 if (r[2], r[3]) == (a, s)]
        print(f"   {lab:13s} study {a}+-{s:<3d}: Table 4 gives {real[2]}+-{real[3]} at {real[1]} cm ({real[4]}{', '+real[5] if real[5] else ''}) -> {'MATCH' if ok else 'MISMATCH; study value belongs to '+str(hit or 'no Table 4 row')}")
print("   SI Table S2 482.5 cm 10860+-70 =", [r[0]+' '+r[1] for r in K08 if (r[2],r[3])==(10860,70)])
print("   SI Table S2 500.5 cm 11020+-25 =", [r[0]+' '+r[1] for r in K08 if (r[2],r[3])==(11020,25)])

print("\n=== C. Arlington Canyon from Kennett 2008 Table 4 directly ===")
yd = [r for r in K08 if int(r[1].split('-')[1]) >= 396 and int(r[1].split('-')[0]) >= 392]
show("AC 12 dates 392-503 cm (Kennett 2015's 'YDB interval')", [(r[0], r[2], r[3]) for r in yd])
dark = [r for r in K08 if int(r[1].split('-')[0]) >= 459]
show("AC 10 dates in the 44-cm dark layer (464-503 cm)", [(r[0], r[2], r[3]) for r in dark])
five = [r for r in dark if not r[5]]
show("AC 5 dark-layer dates not flagged old wood (K2008 avg 11,060+-40)", [(r[0], r[2], r[3]) for r in five])
print("    labs:", [r[0] for r in five])
show("AC 2 dates in SI Table S2 (Beta-161032, UCIAMS-36304)", [("B",10860,70),("U",11020,25)])

print("\n=== D. Murray Springs / Blackwater Draw: do the study's per-date lists reproduce Waters & Stafford 2007 Table 1 means? ===")
for site, target in [("Murray Springs", "10,885 +- 50 (n=8)"), ("Blackwater Draw", "11,300 +- 235 (n=3)")]:
    rows = STUDY[site]; m, e, T_, df, p, _ = ww([r[1] for r in rows], [r[2] for r in rows])
    print(f"   {site}: study's {len(rows)} dates -> weighted mean {m:.0f}+-{e:.0f}; W&S 2007 Table 1 gives {target}")
rows = STUDY["Blackwater Draw"][:3]; m, e, *_ = ww([r[1] for r in rows], [r[2] for r in rows])
print(f"   Blackwater Draw first 3 (A-481, A-490, A-491): {m:.0f}+-{e:.0f}")

print("\n=== E. Alternative 'all dates' panels ===")
ac12 = [(r[0], r[2], r[3]) for r in yd]
show("AC 12 (K2008) + BWD 6 (study) + MS 8 (study)", ac12 + STUDY["Blackwater Draw"] + STUDY["Murray Springs"])
show("AC 12 (K2008) only", ac12)
show("AC 5 non-old-wood + MS 8 + BWD 6", [(r[0], r[2], r[3]) for r in five] + STUDY["Murray Springs"] + STUDY["Blackwater Draw"])
show("BWD 6 + MS 8 (study lists, no AC)", STUDY["Blackwater Draw"] + STUDY["Murray Springs"])
show("Site means: AC K2008 11060+-40, MS W&S 10885+-50, BWD W&S 11300+-235", [("a",11060,40),("m",10885,50),("b",11300,235)])
