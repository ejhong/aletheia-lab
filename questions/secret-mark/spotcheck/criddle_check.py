"""Spot check: does the study's R_criddle = C1/(C1+C2+) test what Criddle tested?

Criddle (1995), as summarised in secondary sources, compared words of the letter that Clement
never uses elsewhere (new words) with words Clement uses only once elsewhere, using Stahlin's
lemma index of all of Clement. His claim: too many once-used words relative to new words.
So the matching statistic is C1/(C0+C1) (high = suspicious), not C1/(C1+C2+).

Here: same tokens, same MFW-150 exclusion, same Clement reference as the study, computed
(a) on inflected forms (as the study), (b) on a crude lemma proxy (first 5 letters of the
form; labelled crude), each with leave-one-chunk-out for Clement's own chunks.
Usage: python -I criddle_check.py <study analysis dir> <layers.json> <out.json>
"""
import sys, json
from collections import Counter
import numpy as np
sys.path.insert(0, sys.argv[1])
import run_stylometry as rs

L = json.load(open(sys.argv[2]))
frame = L['clement_frame']
LA = len(frame)
corp = rs.load_corpora()
auth = {}
for s in rs.SOURCES:
    if s['role'] in ('target_author', 'comparison'):
        auth.setdefault(s['author'], []).extend(corp[s['id']])
chunks = {a: rs.make_chunks(t, LA) for a, t in auth.items()}
bal = {a: rs.sample_evenly(c, 40) for a, c in chunks.items()}
mfw, _ = rs.build_feature_vocab(bal, n_mfw=150, n_char=10)
mfw = set(mfw)
clem = auth['Clement of Alexandria']
print('Clement training tokens', len(clem), 'chunks', len(chunks['Clement of Alexandria']), 'LA', LA)

def stats(chunk, ref, key):
    types = set(key(w) for w in chunk if w not in mfw)
    c0 = sum(1 for w in types if ref.get(w, 0) == 0)
    c1 = sum(1 for w in types if ref.get(w, 0) == 1)
    c2 = sum(1 for w in types if ref.get(w, 0) >= 2)
    return dict(n=len(types), c0=c0, c1=c1, c2p=c2,
                crid=c1 / max(1, c0 + c1),          # Criddle direction: once-used vs new
                study=c1 / max(1, c1 + c2))         # study's R_criddle

out = {}
for kname, key in [('forms', lambda w: w), ('prefix5_crude_lemma', lambda w: w[:5])]:
    ref = Counter(key(w) for w in clem if w not in mfw)
    ms = stats(frame, ref, key)
    vals = []
    for ch in chunks['Clement of Alexandria']:
        r = ref.copy()
        for w in ch:
            if w not in mfw:
                r[key(w)] -= 1
        vals.append(stats(ch, r, key))
    held = [stats(ch, ref, key) for nm in ('clement_quis_dives', 'clement_eclogae') for ch in rs.make_chunks(corp[nm], LA)]
    res = {'mar_saba': ms}
    for lab, V in [('clement_LOO', vals), ('heldout_QD_Ecl', held), ('all', vals + held)]:
        for st in ('crid', 'study'):
            a = np.array([v[st] for v in V])
            x = ms[st]
            res[f'{lab}_{st}'] = dict(n=len(a), mean=float(a.mean()), sd=float(a.std(ddof=1)),
                                      n_ge=int((a >= x).sum()), n_le=int((a <= x).sum()),
                                      upper_tail_p=(int((a >= x).sum()) + 1) / (len(a) + 1))
    out[kname] = res
    print('==', kname, 'letter', ms)
    for k, v in res.items():
        if k != 'mar_saba':
            print('  ', k, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()})
json.dump(out, open(sys.argv[3], 'w'), indent=1)
