"""Full-corpus null scans with the study's own matcher.
mode 'shuffle': permute pendant values within each khipu (the study's null, but over ALL eligible pairs).
mode 'relabel': keep each khipu's positional structure (zeros, repeated values, which cords share a value,
  number of digits of each value) but replace each distinct non-zero value by a random corpus value with the
  same number of digits (drawn from the empirical pendant-value distribution). True copies become unrelated.
Counts Tier A / Tier B hits per full scan of all eligible pairs (pendant mode) and cluster-sum mode."""
import sys, time, json, collections
sys.path.insert(0, sys.argv[1])
import numpy as np, pathlib
import run_khipu as rk
khipus, meta = rk.load_corpus(pathlib.Path(sys.argv[2]))
mode, nrep, seed = sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
rng = np.random.default_rng(seed)
ids = sorted(khipus)
def elig(v): return len(v) >= 6 and len({int(x) for x in v if x > 0}) >= 4 and int(v.sum()) >= 20
P = {k: np.array([c['val'] for c in khipus[k]['pendants']], dtype=np.int64) for k in ids}
G = {k: np.array([s for _, _, s in khipus[k]['clusters']], dtype=np.int64) for k in ids}
allvals = np.concatenate([v for v in P.values()]); allvals = allvals[allvals > 0]
pool = collections.defaultdict(list)
for x in allvals: pool[len(str(int(x)))].append(int(x))
pool = {d: np.array(v) for d, v in pool.items()}
def relabel(v):
    out = v.copy()
    for val in set(int(x) for x in v if x > 0):
        out[v == val] = int(rng.choice(pool[len(str(val))]))
    return out
def scan(vmap):
    ek = sorted(k for k in vmap if elig(vmap[k]))
    pf = {k: rk.build_pos_index(vmap[k]) for k in ek}
    pr = {k: rk.build_pos_index(vmap[k][::-1]) for k in ek}
    vs = {k: set(pf[k].keys()) for k in ek}
    vn = {k: vs[k] | {x - 1 for x in vs[k]} | {x + 1 for x in vs[k]} for k in ek}
    hits = []
    for i, ka in enumerate(ek):
        if len(vs[ka]) < 3: continue
        for kb in ek[i + 1:]:
            if len(vs[ka] & vn[kb]) < 3: continue
            r = rk.best_contiguous_match(vmap[ka], vmap[kb], True, pf[ka], pf[kb], pr[kb])
            if r is not None:
                hits.append((khipus[ka]['okr_num'], khipus[kb]['okr_num'], r['tier'], r['L'], r['err_l1'], r['sample_a'][:10], r['sample_b'][:10]))
    return len(ek) * (len(ek) - 1) // 2, hits
res = []
for rep in range(nrep):
    t = time.time()
    if mode == 'shuffle':
        Ps = {k: rng.permutation(v) for k, v in P.items()}
        Gs = {k: rng.permutation(v) for k, v in G.items()}
    elif mode == 'relabel':
        Ps = {k: relabel(v) for k, v in P.items()}
        Gs = {k: relabel(v) for k, v in G.items()}
    else:
        Ps, Gs = P, G
    npairs, hp = scan(Ps); ng, hg = scan(Gs)
    a = sum(1 for h in hp if h[2] == 'A'); b = len(hp) - a
    ga = sum(1 for h in hg if h[2] == 'A'); gb = len(hg) - ga
    res.append(dict(rep=rep, pairs=npairs, A=a, B=b, gpairs=ng, gA=ga, gB=gb,
                    A_hits=[h for h in hp if h[2] == 'A'], gA_hits=[h for h in hg if h[2] == 'A']))
    print(f"{mode} rep {rep}: pendant pairs={npairs} tierA={a} tierB={b} | cluster pairs={ng} tierA={ga} tierB={gb} ({time.time()-t:.0f}s)", flush=True)
    for h in res[-1]['A_hits'] + res[-1]['gA_hits']:
        print('    A-hit', h, flush=True)
json.dump(res, open(sys.argv[6], 'w'), default=int)
