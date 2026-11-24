# Independent parse of SI Table S6 (p.16 pdftotext -layout) and comparison with study CSV
import sys, re, csv
txt=open(sys.argv[1]).read()
study=list(csv.DictReader(open(sys.argv[2])))
rows=[]; pending_a=False
for line in txt.splitlines():
    s=line.strip()
    if s=='a': pending_a=True; continue
    m=re.match(r'^(a\s+)?(83023-052|2013029-064|2008029-067|2013029-077)\s+(\d+)-(\d+)\s+([\d.]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$',s)
    if m:
        rows.append(dict(a=bool(m.group(1)) or pending_a, core=m.group(2)[-2:], lo=float(m.group(3)), hi=float(m.group(4)), g=float(m.group(5)), n=int(m.group(6)), nkg=int(m.group(7)), c=int(m.group(8)), ckg=int(m.group(9))))
        pending_a=False
print("rows parsed:",len(rows))
# compare with study csv
mism=0
for r,s in zip(rows,study):
    for k1,k2 in (('lo','depth_lo_cm'),('hi','depth_hi_cm'),('g','sample_mass_g'),('n','msp_n'),('nkg','msp_kg'),('c','cdp_n'),('ckg','cdp_kg')):
        if float(r[k1])!=float(s[k2]): mism+=1; print("MISMATCH",r,k1,s[k2])
    if r['a']!=(s['marked_peak_a']=='True'): mism+=1; print("A-flag mismatch",r,s['marked_peak_a'])
print("cell mismatches vs study CSV:",mism)
print("\nRow-by-row count/mass check (per kg):")
print(f"{'core':4} {'depth':8} {'mass_g':>7} {'n':>3} {'tab/kg':>7} {'n/mass':>9} {'c':>3} {'tabC/kg':>7} {'c/mass':>9} {'mass implied by n':>8} {'by c':>8}")
for r in rows:
    nm = r['n']/(r['g']/1000); cm = r['c']/(r['g']/1000)
    im_n = r['n']/r['nkg']*1000 if r['nkg'] else float('nan')
    im_c = r['c']/r['ckg']*1000 if r['ckg'] else float('nan')
    print(f"{r['core']:4} {int(r['lo'])}-{int(r['hi']):<4} {r['g']:7.2f} {r['n']:3d} {r['nkg']:7d} {nm:9.1f} {r['c']:3d} {r['ckg']:7d} {cm:9.1f} {im_n:8.2f} {im_c:8.2f} {'a' if r['a'] else ''}")
# coverage
L={'52':875.0,'64':713.0,'67':519.0,'77':649.5}
print("\nCoverage:")
tot_span=tot_thick=0
for c in L:
    rr=[r for r in rows if r['core']==c]
    mids=[(r['lo']+r['hi'])/2 for r in rr]
    span=max(mids)-min(mids); edge=max(r['hi'] for r in rr)-min(r['lo'] for r in rr)
    thick=sum(r['hi']-r['lo'] for r in rr)
    tot_span+=span; tot_thick+=thick
    print(f"core {c}: n={len(rr)} midpoint span={span:.1f} cm ({100*span/L[c]:.2f}%), edge span={edge:.1f}, summed thickness={thick:.1f} cm ({100*thick/L[c]:.2f}% of {L[c]} cm)")
T=sum(L.values())
print(f"total length {T}; midpoint-span coverage {tot_span:.1f} cm = {100*tot_span/T:.2f}%; summed sample thickness {tot_thick:.1f} cm = {100*tot_thick/T:.2f}%")
# Core 64 vs Core 67
def get(c,lo,hi): return [r for r in rows if r['core']==c and r['lo']==lo and r['hi']==hi][0]
print("\nCore 64 vs Core 67:")
c64=[r for r in rows if r['core']=='64']; c67=[r for r in rows if r['core']=='67']
c64out=[r for r in c64 if not (r['lo']==312)]
for unit,k in (('spherules/kg','nkg'),('CDPs/kg','ckg')):
    o=max(c64out,key=lambda r:r[k]); 
    print(f" {unit}: C64 max outside 312-318 = {o[k]} at {int(o['lo'])}-{int(o['hi'])}; C64 312-318 = {get('64',312,318)[k]}")
    for lo,hi in ((32,35),(30,32),(28,30)):
        v=get('67',lo,hi)[k]; print(f"    C67 {lo}-{hi} = {v}; ratio C64out/C67 = {o[k]/v if v else float('nan'):.3f}")
    m=max(c67,key=lambda r:r[k]); print(f"    C67 max anywhere = {m[k]} at {int(m['lo'])}-{int(m['hi'])}; ratio {o[k]/m[k]:.3f}")
