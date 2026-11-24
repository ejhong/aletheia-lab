import sys, json, random
import numpy as np
from collections import Counter
sys.path.insert(0, sys.argv[3])
from cento_lib import *
D = sys.argv[1]; L = json.load(open(sys.argv[2])); OUT = sys.argv[4]
mk = load_gospel(D + '/gospel_mark.txt'); mt = load_gospel(D + '/gospel_matthew.txt')
lk = load_gospel(D + '/gospel_luke.txt'); jn = load_gospel(D + '/gospel_john.txt')
T = lambda g: [w for _, w in g]
mkT, mtT, lkT, jnT = T(mk), T(mt), T(lk), T(jn)
print('tokens Mark/Mt/Lk/Jn', len(mkT), len(mtT), len(lkT), len(jnT))
stop = set(w for w, _ in Counter(mkT + mtT + lkT + jnT).most_common(50))
SM = L['secret_mark_quotes']; BETH = L['secret_mark_bethany']; JER = L['secret_mark_jericho']
N = len(SM)
res = {}
# --- Secret Mark: as the study did (concatenated quotes, crossing the seam)
mkB, mkTr = ref_sets([mkT]); jnB, jnTr = ref_sets([jnT])
def sm_rates(toks):
    return dict(mark=rates(toks, mkB, mkTr, stop), markjohn=rates(toks, mkB | jnB, mkTr | jnTr, stop))
res['SM_concat'] = sm_rates(SM)
# without the artificial seam: n-grams from each passage separately
def rates_runs(runs, rb, rt):
    bg = sum((ngrams(r, 2) for r in runs), []); tg = sum((ngrams(r, 3) for r in runs), [])
    cb = [g for g in bg if not all(w in stop for w in g)]; ct = [g for g in tg if not all(w in stop for w in g)]
    f = lambda L_, S: sum(g in S for g in L_) / max(1, len(L_))
    return dict(all_bi=f(bg, rb), all_tri=f(tg, rt), cont_bi=f(cb, rb), cont_tri=f(ct, rt), n_cb=len(cb), n_ct=len(ct))
res['SM_noseam'] = dict(mark=rates_runs([BETH, JER], mkB, mkTr), markjohn=rates_runs([BETH, JER], mkB | jnB, mkTr | jnTr))
# Mark without longer ending (16:9-20) and without shorter ending as reference
le0, le1 = span(mk, (16, 9), (16, 20))
mk_short = mkT[:le0]  # still contains shorter ending inside 16:8
mksB, mksTr = ref_sets([mk_short])
res['SM_vs_Mark1_16_8'] = dict(mark=rates(SM, mksB, mksTr, stop), markjohn=rates(SM, mksB | jnB, mksTr | jnTr, stop))
# Symmetry check: SM vs Mark minus a random 181-token span (all 62 chunk spans)
sym = []
for i in range(len(mkT) // N):
    s, e = i * N, (i + 1) * N
    rb, rt = ref_sets([mkT[:s], mkT[e:]])
    sym.append(rates(SM, rb, rt, stop)['cont_bi'])
res['SM_vs_Mark_minus_each_chunk_cont_bi'] = dict(min=min(sym), max=max(sym), mean=float(np.mean(sym)))

def loo_rate(gos_tokens, s, e, extra_runs=(), margin=0):
    rb, rt = ref_sets([gos_tokens[:max(0, s - margin)], gos_tokens[e + margin:]] + list(extra_runs))
    return rates(gos_tokens[s:e], rb, rt, stop)

def dist_summary(vals, x):
    a = np.array(vals); n = len(a)
    ge = int((a >= x).sum())
    return dict(n=n, mean=float(a.mean()), sd=float(a.std(ddof=1)), max=float(a.max()), p95=float(np.quantile(a, .95)),
                n_ge_SM=ge, frac_ge_SM=ge / n, rank_of_SM=ge + 1, emp_p_plus1=(ge + 1) / (n + 1))

keys = ['cont_bi', 'cont_tri', 'all_bi', 'all_tri']
# --- (1) reproduce: 62 non-overlapping chunks, LOO
chunks = [(i * N, (i + 1) * N) for i in range(len(mkT) // N)]
for refname, extra in [('mark', []), ('markjohn', [jnT])]:
    vals = [loo_rate(mkT, s, e, extra) for s, e in chunks]
    res[f'nonoverlap62_{refname}'] = {k: dist_summary([v[k] for v in vals], res['SM_concat'][refname][k]) for k in keys}
    if refname == 'mark':
        res['nonoverlap62_mark_values_cont_bi'] = [round(v['cont_bi'], 4) for v in vals]
# --- (2) all offsets: non-overlapping grids with every start offset 0..180 (=> every 181-token window), LOO
step = 1
win = [(s, s + N) for s in range(0, len(mkT) - N + 1, step)]
for refname, extra in [('mark', []), ('markjohn', [jnT])]:
    vals = [loo_rate(mkT, s, e, extra) for s, e in win]
    res[f'sliding_step1_{refname}'] = {k: dist_summary([v[k] for v in vals], res['SM_concat'][refname][k]) for k in keys}
    if refname == 'mark':
        cb = np.array([v['cont_bi'] for v in vals])
        top = np.argsort(-cb)[:15]
        res['sliding_top_windows_mark_cont_bi'] = [dict(start=mk[win[j][0]][0], end=mk[win[j][1] - 1][0], cont_bi=round(float(cb[j]), 4)) for j in top]
        # grid analysis: for each offset, how often would a 62-chunk grid have max >= SM
        sm_cb = res['SM_concat']['mark']['cont_bi']
        offs_hit = 0
        for off in range(N):
            idx = [off + k * N for k in range((len(mkT) - off) // N)]
            if max(cb[i] for i in idx) >= sm_cb: offs_hit += 1
        res['grid_offsets_where_some_chunk_ge_SM_cont_bi'] = f'{offs_hit}/{N}'
        sm_ct = res['SM_concat']['mark']['cont_tri']; ct_ = np.array([v['cont_tri'] for v in vals])
        offs_hit = sum(1 for off in range(N) if max(ct_[off + k * N] for k in range((len(mkT) - off) // N)) >= sm_ct)
        res['grid_offsets_where_some_chunk_ge_SM_cont_tri'] = f'{offs_hit}/{N}'
json.dump(res, open(OUT, 'w'), indent=1, ensure_ascii=False, default=str)
for k, v in res.items():
    if k.startswith('nonoverlap62_mark_values'): continue
    print(k, json.dumps(v, default=str)[:900])
