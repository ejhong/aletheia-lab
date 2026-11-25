"""Classify cords where the study's Locke/Ascher decoder disagrees with knot_value_type sums."""
import sys, sqlite3, collections
sys.path.insert(0, sys.argv[1])
import run_khipu as rk
con = sqlite3.connect('file:' + sys.argv[2] + '?mode=ro', uri=True)
kc = {r[0]: (r[1] or 0, float(r[2] or 0)) for r in con.execute("select CLUSTER_ID, ORDINAL, START_POS from knot_cluster")}
kv = collections.defaultdict(int); kcl = collections.defaultdict(lambda: collections.defaultdict(list))
for cid, tc, nt, v, clid in con.execute("select CORD_ID, TYPE_CODE, NUM_TURNS, knot_value_type, CLUSTER_ID from knot"):
    try:
        iv = int(float(v)) if v not in (None, '') else 0
    except ValueError:
        iv = 0
    if iv > 0: kv[cid] += iv
    kcl[cid][clid or 0].append((str(tc or ''), float(nt or 0), kc.get(clid or 0, (0, 0.0))[1]))
cats = collections.Counter(); n = 0; ex = []
for (cid,) in con.execute("select CORD_ID from cord where CORD_LEVEL=1"):
    if cid not in kcl: continue
    ordered = sorted(kcl[cid].items(), key=lambda kv_: (kc.get(kv_[0], (0, 0.0))[0], kc.get(kv_[0], (0, 0.0))[1]))
    la = rk.decode_cord_locke_ascher([k for _, k in ordered])
    if la is None: continue
    n += 1
    t = kv.get(cid, 0)
    if la == t: cats['agree'] += 1; continue
    s = str(t)
    if t > 0 and '0' in s[1:] and str(la) == s.replace('0', ''):
        cats['decoder cannot represent an empty decimal place (e.g. 105 read as 15)'] += 1
    elif t > 0 and '0' in s[1:]:
        cats['true value has an internal/trailing zero, other disagreement'] += 1
    elif la == 0 or t == 0:
        cats['one side zero'] += 1
    else:
        cats['other'] += 1
        if len(ex) < 8: ex.append((cid, la, t, ordered))
print('checked', n); [print(f"  {v:6d}  {k}") for k, v in cats.most_common()]
for e in ex: print('  example other:', e[0], 'decoder', e[1], 'kvt', e[2], [[x[0] + str(int(x[1])) for x in k] for _, k in e[3]])
