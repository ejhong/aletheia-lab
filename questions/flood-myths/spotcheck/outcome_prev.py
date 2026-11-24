import sys, json, pandas as pd, numpy as np
D, J = sys.argv[1:3]
rr = pd.read_stata(f'{D}/Berezkin_groups_Regressions_Ready.dta'); mot = pd.read_stata(f'{D}/Motifs_Berezkin_groups.dta', convert_categoricals=False)
need = ["latitude_forgeo","longitude_forgeo","motifs_total","lnnmbr_title","lnyear_firstpub","lnriver_dist_bere","lnbdisttoquake1000","avtemp200_bere"]
df = rr[['oid','group_Berezkin','flood_related','continent_bere']+need].merge(mot[['oid']+[k for k in mot.columns if k not in rr.columns]], on='oid').dropna(subset=need).reset_index(drop=True)
c = np.array(pd.DataFrame(json.load(open(J))['map_points']).c)
NB = ["c2","c4","c7","c9a","c10","c10a","c12a","c12b","c13","c14","b7b","b7d","b52a","g9a","i81a","k38d","l28a"]
FLOOD = ["c4","c7","c9a","c10","c10a","c12a","g9a","b7d","l28a"]          # flood is the core of title/description
for x in NB + ['c3','c5a','c5b','c6','k52c']: df[x] = pd.to_numeric(df[x], errors='coerce').fillna(0)
def prev(cols, lab):
    a = (df[cols].sum(axis=1) > 0)
    print(f'{lab:55s} global {100*a.mean():5.1f}%  coastal {100*a[c==1].mean():5.1f}%  inland {100*a[c==0].mean():5.1f}%')
prev(NB, 'study list (17)')
prev(FLOOD, 'flood-centred 9 (no c2)')
prev(FLOOD+['c2'], 'flood-centred 9 + c2 (deluge or conflagration)')
prev([x for x in NB if x not in FLOOD+['c2']], 'the 7 ambiguous/non-flood (c12b,c13,c14,b7b,b52a,i81a,k38d)')
amb = [x for x in NB if x not in FLOOD+['c2']]
only = (df[amb].sum(axis=1) > 0) & (df[FLOOD+['c2']].sum(axis=1) == 0)
print('societies counted as having a flood motif ONLY via the 7 ambiguous motifs: %d of %d with any (%.0f%%)' % (only.sum(), (df[NB].sum(axis=1)>0).sum(), 100*only.sum()/(df[NB].sum(axis=1)>0).sum()))
print('c5a groups by continent', df[df.c5a>0].continent_bere.value_counts().to_dict(), ' c5a total', int((df.c5a>0).sum()))
print('flood_related>0 share %.3f' % (df.flood_related>0).mean())
