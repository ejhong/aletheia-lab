import sys, re, pandas as pd, numpy as np
D=sys.argv[1]
m=pd.read_stata(f'{D}/Motif_Master.dta',convert_categoricals=False)
mot=pd.read_stata(f'{D}/Motifs_Berezkin_groups.dta',convert_categoricals=False)
NB=["c2","c4","c7","c9a","c10","c10a","c12a","c12b","c13","c14","b7b","b7d","b52a","g9a","i81a","k38d","l28a"]
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',200)
ids=set(m.motif_id)
print("missing from master:", [x for x in NB+["c3","c5a"] if x not in ids])
print("missing from incidence:", [x for x in NB+["c3","c5a"] if x not in mot.columns])
for x in NB+["c3","c5a"]:
    r=m[m.motif_id==x].iloc[0]
    n=int(pd.to_numeric(mot[x],errors='coerce').fillna(0).sum()) if x in mot.columns else -1
    print(f"\n== {x} (n_groups={n}) | {r.title_english} | RU: {r.title_russian}\n   {str(r.desc_eng)[:400]}")
# all c-section motifs
print("\n\n==== ALL c* MOTIFS ====")
for _,r in m[m.motif_id.str.match(r'^c\d')].iterrows():
    x=r.motif_id; n=int(pd.to_numeric(mot[x],errors='coerce').fillna(0).sum()) if x in mot.columns else -1
    print(f"{x:6s} n={n:4d} {'*' if x in NB else ' '} {r.title_english} | {r.title_russian}")
# keyword search outside chosen set
pat=re.compile(r'flood|deluge|inundat|submerg|drown|sea rose|water rose|rising water|water.*rise', re.I)
patru=re.compile(r'потоп|наводн|затоп|подъ[её]м вод|вода подним|вода поднял', re.I)
print("\n\n==== KEYWORD HITS (title or RU title or eng desc) NOT IN CHOSEN SET ====")
for _,r in m.iterrows():
    x=r.motif_id
    if x in NB or x in ("c3","c5a"): continue
    t=f"{r.title_english} {r.title_russian}"
    hit_t = pat.search(str(r.title_english)) or patru.search(str(r.title_russian))
    hit_d = pat.search(str(r.desc_eng)) or patru.search(str(r.desc_russian))
    if hit_t or hit_d:
        n=int(pd.to_numeric(mot[x],errors='coerce').fillna(0).sum()) if x in mot.columns else -1
        print(f"{x:7s} n={n:4d} {'T' if hit_t else 'd'} {r.title_english} | {r.title_russian}")
