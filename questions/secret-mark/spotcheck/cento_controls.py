import sys, json
import numpy as np
from collections import Counter
sys.path.insert(0, sys.argv[3])
from cento_lib import *
D = sys.argv[1]; L = json.load(open(sys.argv[2])); OUT = sys.argv[4]
G = {k: load_gospel(f'{D}/gospel_{k}.txt') for k in ['mark', 'matthew', 'luke', 'john']}
T = {k: [w for _, w in v] for k, v in G.items()}
stop = set(w for w, _ in Counter(sum(T.values(), [])).most_common(50))
mk, mkT, jnT = G['mark'], T['mark'], T['john']
SM = L['secret_mark_quotes']
# locate end of Mark 16:8 proper (before the shorter ending): last 'γαρ' before 16:9 following 'εφοβουντο'
le0, _ = span(mk, (16, 9), (16, 20))
s8, e8 = span(mk, (16, 8), (16, 8))
v8 = mkT[s8:e8]; k = v8.index('εφοβουντο') + 2; short_end_start = s8 + k
print('Mark 16:8 shorter ending tokens:', ' '.join(mkT[short_end_start:e8])[:120], '...', e8 - short_end_start)
def R(toks, runs):
    rb, rt = ref_sets(runs); return rates(toks, rb, rt, stop)
rows = []
def add(label, toks, runs_mark, runs_mj, note=''):
    a = R(toks, runs_mark); b = R(toks, runs_mj)
    rows.append(dict(label=label, n_tok=len(toks), cont_bi_mark=a['cont_bi'], cont_tri_mark=a['cont_tri'],
                     cont_bi_mj=b['cont_bi'], cont_tri_mj=b['cont_tri'], all_bi_mark=a['all_bi'], note=note))
add('Secret Mark quotes (study text)', SM, [mkT], [mkT, jnT])
add('Secret Mark Bethany only', L['secret_mark_bethany'], [mkT], [mkT, jnT])
# Markan passages, leave-passage-out
mark_ctrl = {
 'Mark 10:46-52 Bartimaeus': ((10,46),(10,52)), 'Mark 5:35-43 Jairus raising': ((5,35),(5,43)),
 'Mark 5:21-43 Jairus+woman': ((5,21),(5,43)), 'Mark 8:1-10 feeding 4000': ((8,1),(8,10)),
 'Mark 6:35-44 feeding 5000': ((6,35),(6,44)), 'Mark 10:17-31 rich man': ((10,17),(10,31)),
 'Mark 16:1-8 empty tomb': ((16,1),(16,7)), 'Mark 14:43-52 arrest/naked youth': ((14,43),(14,52)),
 'Mark 1:21-28 exorcism': ((1,21),(1,28)), 'Mark 1:29-39': ((1,29),(1,39)), 'Mark 2:1-12 paralytic': ((2,1),(2,12)),
 'Mark 4:35-41 storm': ((4,35),(4,41)), 'Mark 5:1-20 Gerasene': ((5,1),(5,20)), 'Mark 6:45-52 walking on water': ((6,45),(6,52)),
 'Mark 7:24-30 Syrophoenician': ((7,24),(7,30)), 'Mark 7:31-37 deaf man': ((7,31),(7,37)), 'Mark 8:22-26 blind man': ((8,22),(8,26)),
 'Mark 9:14-29 epileptic boy': ((9,14),(9,29)), 'Mark 8:27-9:1 confession/prediction': ((8,27),(9,1)),
 'Mark 9:30-37 2nd prediction': ((9,30),(9,37)), 'Mark 10:32-45 3rd prediction+James/John': ((10,32),(10,45)),
 'Mark 3:1-6 withered hand': ((3,1),(3,6)), 'Mark 1:40-45 leper': ((1,40),(1,45)),
}
for lab, (a, b) in mark_ctrl.items():
    s, e = span(mk, a, b)
    if (a, b) == ((16,1),(16,7)): e = span(mk, (16,1),(16,8))[1] - (e8 - short_end_start)  # 16:1-8 without shorter ending
    toks = mkT[s:e]
    add(lab, toks, [mkT[:s], mkT[e:]], [mkT[:s], mkT[e:], jnT], 'leave-passage-out vs rest of Mark')
# Longer ending vs Mark 1:1-16:8 (without either ending)
mk_core = mkT[:short_end_start]
add('Mark 16:9-20 longer ending (later pastiche)', mkT[le0:], [mk_core], [mk_core, jnT], 'vs Mark 1:1-16:8 only')
add('Mark shorter ending', mkT[short_end_start:e8], [mk_core], [mk_core, jnT], 'vs Mark 1:1-16:8 only')
# Other gospels vs whole Mark
others = {
 'Matt 9:18-26 Jairus': ('matthew', (9,18),(9,26)), 'Matt 20:29-34 blind men': ('matthew', (20,29),(20,34)),
 'Matt 15:32-39 feeding 4000': ('matthew', (15,32),(15,39)), 'Matt 14:15-21 feeding 5000': ('matthew', (14,15),(14,21)),
 'Matt 19:16-22 rich young man': ('matthew', (19,16),(19,22)), 'Matt 28:1-8 empty tomb': ('matthew', (28,1),(28,8)),
 'Matt 8:23-27 storm': ('matthew', (8,23),(8,27)), 'Matt 16:13-28 confession': ('matthew', (16,13),(16,28)),
 'Luke 8:40-56 Jairus': ('luke', (8,40),(8,56)), 'Luke 18:35-43 blind man': ('luke', (18,35),(18,43)),
 'Luke 18:18-23 rich ruler': ('luke', (18,18),(18,23)), 'Luke 24:1-12 tomb': ('luke', (24,1),(24,12)),
 'Luke 7:11-17 Nain widow son (L only)': ('luke', (7,11),(7,17)),
 'John 20:1-18 tomb': ('john', (20,1),(20,18)),
}
for lab, (g, a, b) in others.items():
    s, e = span(G[g], a, b); toks = T[g][s:e]
    mj = [mkT, jnT] if g != 'john' else [mkT, jnT[:s], jnT[e:]]
    add(lab, toks, [mkT], mj, 'vs whole Mark' + (' (Mk u John-minus-passage)' if g == 'john' else ''))
s, e = span(G['john'], (11,1),(11,44)); j11 = jnT[s:e]
add('John 11:1-44 Lazarus', j11, [mkT], [mkT, jnT[:s], jnT[e:]], 'vs Mark; MJ = Mark u John minus John 11')
# also 181-token windows from start of each control (length-matched)
for lab, (g, a, b) in list(others.items()) + [('John 11:1-44 Lazarus', ('john', (11,1),(11,44)))]:
    s, e = span(G[g], a, b)
    if e - s < 181: continue
# Matthew/Luke 181-token non-overlapping chunks vs Mark: distribution
for g in ['matthew', 'luke', 'john']:
    t = T[g]; vals = [R(t[i*181:(i+1)*181], [mkT])['cont_bi'] for i in range(len(t)//181)]
    a = np.array(vals); n_ge = int((a >= 0.4859).sum())
    rows.append(dict(label=f'{g} all 181-tok chunks vs Mark (cont_bi)', n_tok=len(vals), cont_bi_mark=float(np.median(a)),
                     cont_tri_mark=float(a.max()), note=f'median shown in cont_bi_mark, max in cont_tri_mark col; n>=SM: {n_ge}/{len(vals)}'))
    if g == 'matthew':
        top = np.argsort(-a)[:5]
        rows.append(dict(label='matthew top chunks', n_tok=0, note='; '.join(f'{G[g][i*181][0]}-{G[g][(i+1)*181-1][0]}:{a[i]:.3f}' for i in top)))
json.dump(rows, open(OUT, 'w'), indent=1, ensure_ascii=False)
print(f"{'passage':48s} {'ntok':>5s} {'cbiMk':>6s} {'ctriMk':>6s} {'cbiMJ':>6s} {'ctriMJ':>6s}")
for r in rows:
    f = lambda k: f"{r[k]:.3f}" if isinstance(r.get(k), float) else '   -  '
    print(f"{r['label'][:48]:48s} {r['n_tok']:5d} {f('cont_bi_mark'):>6s} {f('cont_tri_mark'):>6s} {f('cont_bi_mj'):>6s} {f('cont_tri_mj'):>6s}  {r.get('note','')}")
