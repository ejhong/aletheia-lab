import json, sys
from scipy import stats
d=json.load(open(sys.argv[1]))
F=lambda a,n1,b,n2: stats.fisher_exact([[a,n1-a],[b,n2-b]],alternative='greater')[1]
print("strict chron 2/1964 vs 2/639", F(2,1964,2,639))
print("strict unfilt 2/1964 vs 4/639", F(2,1964,4,639))
print("relaxed 47/1964 vs 18/639", F(47,1964,18,639))
print("-- with actually-searched denominators 142 / 57")
print("strict chron 2/142 vs 2/57", F(2,142,2,57))
print("strict unfilt 2/142 vs 4/57", F(2,142,4,57))
print("relaxed 47/142 vs 18/57", F(47,142,18,57))
print("-- calibration")
print("relaxed 59/100 vs 1/40", F(59,100,1,40), "ratio", (59/100)/(1/40))
print("strict 23/100 vs 0/40", F(23,100,0,40))
on=d['calibration']['neolithic_onsets']
a=[o['onset_cal_bp'] for o in on]; la=[o['lat'] for o in on]; lo=[o['lon'] for o in on]
print("n",len(on),"lat",stats.spearmanr(a,la),"lon",stats.spearmanr(a,lo))
# dedupe by site name (Lake Varna x2, Durankulak x2)
seen={}
for o in on: seen.setdefault(o['sitename'],[]).append(o)
u=[max(v,key=lambda o:o['onset_cal_bp']) for v in seen.values()]
print("unique sites",len(u),"lat",stats.spearmanr([o['onset_cal_bp'] for o in u],[o['lat'] for o in u]),"lon",stats.spearmanr([o['onset_cal_bp'] for o in u],[o['lon'] for o in u]))
# Onsets younger than plausible Neolithic arrival
for o in sorted(on,key=lambda o:o['onset_cal_bp']): print(o['onset_cal_bp'],o['sitename'],o['lat'],o['lon'])
