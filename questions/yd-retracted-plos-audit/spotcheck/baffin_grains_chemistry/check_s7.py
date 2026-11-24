# Independent recomputation of Table S7 peak-location test, 12 metrics, several windows, chance expectation
import sys, openpyxl, statistics
from openpyxl.utils import column_index_from_string as ci
from math import comb
wb=openpyxl.load_workbook(sys.argv[1],data_only=True,read_only=True); ws=wb.worksheets[0]
rows=list(ws.iter_rows(values_only=True))
C={'Cr':'G','Fe':'I','Co':'J','Ni':'K','Pd':'S','Ir':'AQ','Pt':'AR','Pt/Ir':'AX','Pt/Pd':'AY','Pt/Fe':'AZ','Co/Fe':'BA','Cr/Fe':'BB','Ni/Fe':'BC'}
def block(r0,r1):
    out=[]
    for r in rows[r0-1:r1]:
        if r[0] and str(r[0]).startswith('C6'):
            d=dict(sample=r[0],depth=r[1]); 
            for k,c in C.items(): d[k]=r[ci(c)-1]
            out.append(d)
    return out
blocks={'mass_C64':block(3,8),'mass_C67':block(16,21),'conc_C64':block(58,63),'conc_C67':block(65,70)}
# sanity: ratio columns equal ratio of totals?
for b in blocks.values():
    for d in b:
        assert abs(d['Pt']/d['Ir']-d['Pt/Ir'])/d['Pt/Ir']<1e-6 and abs(d['Pt']/d['Pd']-d['Pt/Pd'])/d['Pt/Pd']<1e-6
print("ratio columns = ratio of total element masses: confirmed")
metrics12=['Pt','Ir','Pd','Ni','Co','Cr','Pt/Ir','Pt/Pd','Pt/Fe','Ni/Fe','Cr/Fe','Co/Fe']
metrics10=metrics12[:10]
windows={'64':{'protocol 312-318':(312,318),'code (+/-2 cm) 310-320':(310,320)},
         '67':{'protocol/Fig2 32-35':(32,35),'code (+/-2 cm) 30-37':(30,37),'S6 footnote-a peak samples 28-32':(28,32)}}
for key,b in blocks.items():
    core=key[-2:]
    print(f"\n== {key}: depths {[d['sample'] for d in b]}")
    peaks={}
    for m in metrics12:
        top=max(b,key=lambda d:d[m]); med=statistics.median(d[m] for d in b)
        peaks[m]=top
        print(f"  {m:6s} max at {top['sample']:12s} value {top[m]:.4g}  max/median {top[m]/med:.2f}")
    for wname,(lo,hi) in windows[core].items():
        nin_depths=sum(1 for d in b if lo<=d['depth']<=hi)
        for ms,lab in ((metrics10,'10'),(metrics12,'12')):
            k=sum(1 for m in ms if lo<=peaks[m]['depth']<=hi)
            p=nin_depths/len(b)
            # binomial tail P(X>=k) under independence (metrics are NOT independent; indicative only)
            n=len(ms); tail=sum(comb(n,j)*p**j*(1-p)**(n-j) for j in range(k,n+1))
            print(f"  window {wname}: {nin_depths}/{len(b)} depths inside; {lab} metrics peaking inside = {k}; chance expectation {n*p:.2f}; P(X>={k}) indep.binomial={tail:.3f}")
print("\nPt/Pd at claimed levels:", {key:[(d['sample'],round(d['Pt/Pd'],3)) for d in b] for key,b in blocks.items() if key.startswith('mass')})
print("Pt/Ir at claimed levels:", {key:[(d['sample'],round(d['Pt/Ir'],3)) for d in b] for key,b in blocks.items() if key.startswith('mass')})
