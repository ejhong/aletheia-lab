# Extract Appendix Table A1 from JATS XML and recompute means; also a mixing sensitivity estimate
import sys, re, statistics
import xml.etree.ElementTree as ET
r=ET.parse(sys.argv[1]).getroot()
for tw in r.iter('table-wrap'):
    t=' '.join(tw.itertext())
    if 'Oxygen isotope results' in t or 'Obsidian' in t:
        rows=[]
        for tr in tw.iter('tr'):
            cells=[re.sub(r'\s+',' ',''.join(td.itertext())).strip() for td in tr if td.tag in('td','th')]
            rows.append(cells); print(cells)
        foot=tw.find('.//table-wrap-foot')
        if foot is not None: print("FOOT:",re.sub(r'\s+',' ',' '.join(foot.itertext())))
        cores=[c for c in rows if c and c[0].startswith('Core')]
        f=lambda s: float(s.replace('−','-'))
        vals={c[0]:f(c[5]) for c in cores}
        ydb=[v for k,v in vals.items() if any(x in k for x in ('312–318','30–32','32–35'))]
        ydb2=[v for k,v in vals.items() if any(x in k for x in ('312–318','28–30','30–32'))]
        ydb3=[v for k,v in vals.items() if any(x in k for x in ('312–318','32–35'))]
        bg=[v for k,v in vals.items() if not any(x in k for x in ('312–318','30–32','32–35'))]
        print("n core samples",len(vals)); print("all", vals)
        print("study YDB set (312-318, 30-32, 32-35): n=%d mean=%.4f"%(len(ydb),statistics.mean(ydb)))
        print("background (rest): n=%d mean=%.4f"%(len(bg),statistics.mean(bg)))
        print("alt YDB = Fig2 levels only (312-318, 32-35): mean=%.4f"%statistics.mean(ydb3))
        print("max |D17O| =",max(abs(v) for v in vals.values()), "; n with |D17O|>0.06:",sum(abs(v)>0.06 for v in vals.values()), [k for k,v in vals.items() if abs(v)>0.06])
        break
# mixing sensitivity: Delta17O shift for x wt% admixture (O-weighted; approximate, linear)
# Bulk sediment O ~ 47-50 wt%; CI chondrite O ~46 wt%; CM ~ 43 wt%; CO ~ 37 wt% (approx literature values, unverified here)
cases={'CI (D17O ~ +0.39 permil; cometary/CI-like)':(0.39,0.46),'CM (~ -2.9 permil)':(-2.9,0.43),'CO Kainsaz (-5.25 permil, value cited by authors)':(-5.25,0.37),'ordinary chondrite H/L (~ +0.7 to +1.1 permil)':(0.9,0.36)}
sedO=0.48
for name,(d,o) in cases.items():
    for x in (0.01,0.02):
        fO=x*o/(x*o+(1-x)*sedO)
        print(f"{name}: {x*100:.0f} wt% admixture -> O fraction {fO:.4f} -> shift {fO*d:+.3f} permil (threshold 0.06)")
