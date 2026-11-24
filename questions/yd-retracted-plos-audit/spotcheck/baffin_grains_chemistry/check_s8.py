# Independent recomputation of the x100 / Fe-Ni-Cr checks from Tables S8a and S8b
import sys, openpyxl, statistics
a=openpyxl.load_workbook(sys.argv[1],data_only=True,read_only=True).worksheets[0]
b=openpyxl.load_workbook(sys.argv[2],data_only=True,read_only=True).worksheets[0]
ra=list(a.iter_rows(values_only=True)); rb=list(b.iter_rows(values_only=True))
ha={str(v).strip():i for i,v in enumerate(ra[0]) if v is not None}
hb={}
for i,v in enumerate(rb[0]):
    if v is not None and str(v).strip() not in hb: hb[str(v).strip()]=i
print("S8b header units row:", [ (rb[0][i],rb[1][i]) for i in range(len(rb[0])) if rb[0][i] in ('Cr','Fe2O3','Ni','Ir','Pt','CaO')])
sph=[]
for r in ra[1:]:
    if r[0] and 'Baffin' in str(r[0]):
        sph.append(dict(t='S8a',s=r[0],Fe=r[ha['Fe']],Cr=r[ha['Cr53(LR)']],Ni=r[ha['Ni60(LR)']],CaO=r[ha['Cao wt%']],Ir=r[ha['Ir(ppb)']],Pt=r[ha['Pt195(ppb)']],IrLR=r[ha['Ir193(LR)']]))
for r in rb[2:]:
    if r[0] and str(r[0]).lower().startswith('spot'):
        sph.append(dict(t='S8b',s=r[0],Fe=r[hb['Fe2O3']]*6994.0,Cr=r[hb['Cr']],Ni=r[hb['Ni']],CaO=r[hb['CaO']],Ir=r[hb['Ir']],Pt=r[hb['Pt']],IrLR=None))
print("n S8a",sum(1 for x in sph if x['t']=='S8a'),"n S8b",sum(1 for x in sph if x['t']=='S8b'))
# all rows in S8a with a name (to see if any dropped)
print("S8a named rows:", [r[0] for r in ra[1:] if r[0]])
print("S8b rows:", [r[0] for r in rb[2:] if r[0]])
UCC=dict(Fe=39200.,Cr=92.,Ni=47.)
for x in sph:
    x['FeCr']=x['Fe']/x['Cr']; x['FeNi']=x['Fe']/x['Ni']
    x['FeCr100']=x['FeCr']/100; x['FeNi100']=x['FeNi']/100
    x['box_raw']= x['FeCr']<=150 and x['FeNi']<=80
    x['box100']= x['FeCr100']<=150 and x['FeNi100']<=80
    x['Ni_ex_ucc']=x['Ni']-0.99*UCC['Ni']; x['Cr_ex_ucc']=x['Cr']-0.99*UCC['Cr']
    f=x['Fe']/UCC['Fe']; x['Ni_ex_fe']=x['Ni']-0.99*f*UCC['Ni']; x['Cr_ex_fe']=x['Cr']-0.99*f*UCC['Cr']
    print(f"{x['t']} {str(x['s']):22s} Fe={x['Fe']:9.0f} Cr={x['Cr']:7.1f} Ni={x['Ni']:7.1f} CaO={x['CaO']:5.2f} Fe/Cr={x['FeCr']:8.1f} Fe/Ni={x['FeNi']:9.1f} x100: {x['FeCr100']:6.2f} {x['FeNi100']:7.2f} box100={x['box100']} Ir={x['Ir']} Pt={x['Pt']}")
n=len(sph)
print(f"\nn={n}; Fe/Ni>200: {sum(x['FeNi']>200 for x in sph)}; Fe/Cr>200: {sum(x['FeCr']>200 for x in sph)}; raw in box: {sum(x['box_raw'] for x in sph)}; x100 in box: {sum(x['box100'] for x in sph)}")
print("x100 NOT in box:",[ (x['s'],round(x['FeCr100'],1),round(x['FeNi100'],1)) for x in sph if not x['box100']])
print(f"median Fe/Cr={statistics.median(x['FeCr'] for x in sph):.1f}; median Fe/Ni={statistics.median(x['FeNi'] for x in sph):.1f}")
print("CaO>15:",sum(x['CaO']>15 for x in sph))
c1=sum(1 for x in sph if x['Ni_ex_ucc']>=108 and x['Cr_ex_ucc']>=26.5); c2=sum(1 for x in sph if x['Ni_ex_fe']>=108 and x['Cr_ex_fe']>=26.5)
print(f"excess >=1wt% CI (Ni>=108, Cr>=26.5 ppm) vs unscaled 0.99*UCC: {c1}/{n} = {100*c1/n:.1f}%;  vs Fe-scaled 0.99*UCC: {c2}/{n}")
print("  unscaled-UCC passers:",[x['s'] for x in sph if x['Ni_ex_ucc']>=108 and x['Cr_ex_ucc']>=26.5])
print("  Fe-scale factors:",[round(x['Fe']/UCC['Fe'],2) for x in sph])
# UCC control
print(f"UCC: Fe/Cr={UCC['Fe']/UCC['Cr']:.1f} Fe/Ni={UCC['Fe']/UCC['Ni']:.1f} -> x100 {UCC['Fe']/UCC['Cr']/100:.2f} {UCC['Fe']/UCC['Ni']/100:.2f}")
print("Pure CI chondrite for reference (Fe 185000, Cr 2650, Ni 10800 ppm; Lodders 2003 approx): Fe/Cr=%.1f Fe/Ni=%.1f"%(185000/2650,185000/10800))
# Pt/Ir
pi=[(x['t'],x['s'],x['Pt'],x['Ir'],x['IrLR']) for x in sph if x['Pt'] and x['Ir'] and x['Pt']>0 and x['Ir']>0]
for p in pi: print("Pt/Ir",p, round(p[2]/p[3],2))
s8a=[p[2]/p[3] for p in pi if p[0]=='S8a']; s8b=[p[2]/p[3] for p in pi if p[0]=='S8b']
print(f"S8a Pt/Ir n={len(s8a)} median={statistics.median(s8a):.1f}; S8b Pt/Ir n={len(s8b)} median={statistics.median(s8b) if s8b else None}")
print("S8a Ir(LR) values incl. negatives:",[ (x['s'],x['IrLR']) for x in sph if x['t']=='S8a'])
# duplicate check Spot 8 vs Spot 9
r8=[r for r in rb if r[0]=='Spot 8'][0]; r9=[r for r in rb if r[0]=='Spot 9'][0]
rat=[r9[i]/r8[i] for i in range(1,len(r8)) if isinstance(r8[i],(int,float)) and isinstance(r9[i],(int,float)) and r8[i] not in (0,) ]
print(f"Spot9/Spot8 ratio over {len(rat)} numeric cells: min {min(rat):.6f} max {max(rat):.6f}; SiO2 {r8[hb['SiO2']]} vs {r9[hb['SiO2']]} (34.5/34.4={34.5/34.4:.6f})")
