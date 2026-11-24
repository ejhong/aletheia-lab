"""Extra probes of the cento statistic (spot check). Uses cento_lib (independent of study code).
1. Is the 'John' part special? Gain in content-bigram overlap when John (or Matthew, or Luke) is
   added to the Mark reference: Secret Mark vs each of the 62 LOO Mark chunks.
2. Concentration: what share of a passage's Mark-matched content bigrams can be found inside the
   single best 400-token stretch of Mark? (high = parallel rewriting of one source passage,
   low = matches scattered across Mark, as in a cento OR in ordinary Markan idiom)
3. Longer ending 16:9-20 vs Matthew+Luke+John, against Mark LOO chunks on the same reference.
Usage: python -I cento_extra.py <data dir> <layers.json> <scripts dir> <out.json>
"""
import sys, json
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, sys.argv[3])
from cento_lib import *
D = sys.argv[1]; L = json.load(open(sys.argv[2])); OUT = sys.argv[4]
G = {k: load_gospel(f'{D}/gospel_{k}.txt') for k in ['mark', 'matthew', 'luke', 'john']}
T = {k: [w for _, w in v] for k, v in G.items()}
stop = set(w for w, _ in Counter(sum(T.values(), [])).most_common(50))
mk, mkT = G['mark'], T['mark']
SM = L['secret_mark_quotes']; N = len(SM)
res = {}
def cb(toks, runs):
    rb, rt = ref_sets(runs); return rates(toks, rb, rt, stop)['cont_bi']
# 1. increments
chunks = [(i * N, (i + 1) * N) for i in range(len(mkT) // N)]
for g in ['john', 'matthew', 'luke']:
    sm0 = cb(SM, [mkT]); sm1 = cb(SM, [mkT, T[g]]); inc_sm = sm1 - sm0
    incs = []
    for s, e in chunks:
        runs = [mkT[:s], mkT[e:]]
        incs.append(cb(mkT[s:e], runs + [T[g]]) - cb(mkT[s:e], runs))
    a = np.array(incs)
    res[f'increment_add_{g}'] = dict(SM_increment=inc_sm, chunk_mean=float(a.mean()), chunk_sd=float(a.std(ddof=1)),
                                     n_chunks_ge_SM=int((a >= inc_sm).sum()), n=len(a))
# 2. concentration
def bigram_positions(tokens):
    pos = defaultdict(list)
    for i in range(len(tokens) - 1):
        pos[(tokens[i], tokens[i + 1])].append(i)
    return pos
def concentration(toks, ref_tokens, excl=None, W=400):
    pos = bigram_positions(ref_tokens)
    bgs = [g for g in ngrams(toks, 2) if not all(w in stop for w in g)]
    matched = []
    for g in set(bgs):
        p = [i for i in pos.get(g, []) if excl is None or not (excl[0] <= i < excl[1])]
        if p: matched.append(p)
    if not matched: return 0.0, 0
    # best window: slide start over all candidate positions
    import bisect
    matched = [sorted(p) for p in matched]
    starts = sorted(set(i for p in matched for i in p))
    best = 0
    for s0 in starts:
        c = 0
        for p in matched:
            j = bisect.bisect_left(p, s0)
            if j < len(p) and p[j] < s0 + W: c += 1
        best = max(best, c)
    return best / len(matched), len(matched)
conc = {}
conc['Secret Mark quotes'] = concentration(SM, mkT)
conc['Secret Mark Bethany'] = concentration(L['secret_mark_bethany'], mkT)
vals = [concentration(mkT[s:e], mkT, excl=(s - 1, e))[0] for s, e in chunks]
conc['Mark LOO chunks (mean, max)'] = (float(np.mean(vals)), float(np.max(vals)))
for lab, (g, a, b) in {'Matt 15:32-39': ('matthew', (15, 32), (15, 39)), 'Matt 14:15-21': ('matthew', (14, 15), (14, 21)),
                       'Matt 16:13-28': ('matthew', (16, 13), (16, 28)), 'Luke 18:18-23': ('luke', (18, 18), (18, 23)),
                       'Matt 9:18-26': ('matthew', (9, 18), (9, 26)), 'Luke 18:35-43': ('luke', (18, 35), (18, 43)),
                       'John 11:1-44': ('john', (11, 1), (11, 44))}.items():
    s, e = span(G[g], a, b); conc[lab] = concentration(T[g][s:e], mkT)
res['concentration_best400_share_of_matched_content_bigram_types'] = conc
# 3. longer ending vs other gospels
le0, _ = span(mk, (16, 9), (16, 20)); LE = mkT[le0:]
ref = [T['matthew'], T['luke'], T['john']]
le = cb(LE, ref)
v = np.array([cb(mkT[s:e], ref) for s, e in chunks if e <= le0])
res['longer_ending_vs_Mt_Lk_Jn'] = dict(LE=le, mark_chunks_mean=float(v.mean()), max=float(v.max()), n_ge=int((v >= le).sum()), n=len(v))
sm_other = cb(SM, ref)
res['secret_mark_vs_Mt_Lk_Jn'] = dict(SM=sm_other, n_mark_chunks_ge=int((v >= sm_other).sum()), n=len(v))
json.dump(res, open(OUT, 'w'), indent=1, default=str)
for k, x in res.items(): print(k, json.dumps(x, default=str))
