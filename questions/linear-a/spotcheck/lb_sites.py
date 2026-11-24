import json,sys,importlib.util,pathlib,re,collections
W=pathlib.Path(sys.argv[1])
spec=importlib.util.spec_from_file_location("rla",W/"analysis/run_linear_a.py"); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
txt=(W/"data/linearb_xyz_inscriptions.js").read_text(encoding="utf-8",errors="ignore")
blocks=re.split(r'\n    \[\n        "',txt)
site_types=collections.defaultdict(set); tok=collections.Counter()
for b in blocks[1:]:
    name=b.split('"',1)[0]; site=name[:2]
    mm=re.search(r'"transliteratedWords"\s*:\s*\[([^\]]*)\]',b)
    if not mm: continue
    for w in re.findall(r'"([^"]+)"',mm.group(1)):
        ws=w.strip(); parts=ws.split("-")
        if "[" in ws or "]" in ws or "?" in ws or " " in ws or "/" in ws: continue
        if len(parts)>=3 and all(re.fullmatch(r"[a-z]{1,3}[0-9₂₃₄]*",p) for p in parts):
            site_types[site].add(ws.lower()); tok[site]+=1
allw=set().union(*site_types.values())
print("types",len(allw),{k:len(v) for k,v in sorted(site_types.items(),key=lambda x:-len(x[1]))})
kn=site_types["Kn"]; others=set().union(*[v for k,v in site_types.items() if k!="Kn"])
print("Knossos-only types",len(kn-others),f"{len(kn-others)/len(allw):.1%}","tokens by site",tok.most_common(5))
