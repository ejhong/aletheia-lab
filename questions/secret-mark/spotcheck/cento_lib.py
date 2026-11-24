"""Independent re-implementation of the 'cento' n-gram overlap test (spot check).
Written separately from the study's run_stylometry.py; reads the same SBLGNT files."""
import re, unicodedata, json
from collections import Counter

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.replace('ς', 'σ')

def load_gospel(path):
    """Return list of (ref, token) with ref = (chapter, verse)."""
    out = []
    for line in open(path, encoding='utf-8'):
        cols = line.split()
        if len(cols) < 4: continue
        bcv = cols[0]; ch, vs = int(bcv[2:4]), int(bcv[4:6])
        for t in re.findall(r'[α-ω]+', norm(cols[3])):
            out.append(((ch, vs), t))
    return out

def ngrams(toks, n):
    return [tuple(toks[i:i+n]) for i in range(len(toks)-n+1)]

def ngram_set(toks, n):
    return set(ngrams(toks, n))

def ref_sets(token_lists):
    """token_lists: list of contiguous token runs; n-grams never cross runs."""
    b, t = set(), set()
    for run in token_lists:
        b |= ngram_set(run, 2); t |= ngram_set(run, 3)
    return b, t

def rates(toks, rb, rt, stop):
    bg = ngrams(toks, 2); tg = ngrams(toks, 3)
    cb = [g for g in bg if not all(w in stop for w in g)]
    ct = [g for g in tg if not all(w in stop for w in g)]
    f = lambda L, S: sum(g in S for g in L) / max(1, len(L))
    return dict(all_bi=f(bg, rb), all_tri=f(tg, rt), cont_bi=f(cb, rb), cont_tri=f(ct, rt),
                n_cb=len(cb), n_ct=len(ct))

def span(gos, start, end):
    """indices of tokens with start <= ref <= end (refs are (ch,vs))."""
    idx = [i for i, (r, _) in enumerate(gos) if start <= r <= end]
    return idx[0], idx[-1] + 1
