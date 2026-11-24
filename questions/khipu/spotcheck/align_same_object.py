"""Gapped local alignment of pendant sequences + cord-length agreement, to tell
'same physical khipu recorded twice' from 'two objects carrying the same numbers'."""
import sys, statistics as st
sys.path.insert(0, sys.argv[2])
from khipu_lib import load_all, by_okr
import numpy as np
meta, cords = load_all(sys.argv[1]); B = by_okr(meta)

def near(a, b):
    return abs(a - b) <= max(1, int(0.02 * max(a, b)))

def sw(ca, cb):
    va = [c['val'] for c in ca]; vb = [c['val'] for c in cb]
    n, m = len(va), len(vb)
    H = np.zeros((n + 1, m + 1)); T = np.zeros((n + 1, m + 1), dtype=int)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            a, b = va[i-1], vb[j-1]
            if a == 0 and b == 0: s = 0.5
            elif a == b: s = 3
            elif a > 0 and b > 0 and near(a, b): s = 2
            else: s = -3
            opts = (0, H[i-1, j-1] + s, H[i-1, j] - 4, H[i, j-1] - 4)
            k = int(np.argmax(opts)); H[i, j] = opts[k]; T[i, j] = k
    i, j = np.unravel_index(np.argmax(H), H.shape); score = H[i, j]
    pairs = []
    while i > 0 and j > 0 and H[i, j] > 0:
        k = T[i, j]
        if k == 1: pairs.append((i-1, j-1)); i -= 1; j -= 1
        elif k == 2: i -= 1
        elif k == 3: j -= 1
        else: break
    return score, pairs[::-1]

def report(a, b):
    best = None
    for rev in (False, True):
        ca, cb = cords[B[a]], cords[B[b]]
        if rev: cb = cb[::-1]
        sc, pr = sw(ca, cb)
        if best is None or sc > best[0]: best = (sc, pr, rev, ca, cb)
    sc, pr, rev, ca, cb = best
    ex = sum(1 for i, j in pr if ca[i]['val'] == cb[j]['val'] and ca[i]['val'] > 0)
    nz = sum(1 for i, j in pr if ca[i]['val'] > 0 or cb[j]['val'] > 0)
    span_a = (pr[0][0], pr[-1][0]) if pr else None; span_b = (pr[0][1], pr[-1][1]) if pr else None
    la = [(float(ca[i]['length']), float(cb[j]['length'])) for i, j in pr
          if ca[i]['length'] and cb[j]['length'] and float(ca[i]['length']) > 2 and float(cb[j]['length']) > 2]
    if len(la) >= 4:
        x, y = np.array(la).T
        r = float(np.corrcoef(x, y)[0, 1]); mad = float(np.median(np.abs(x - y))); bias = float(np.median(x - y))
    else:
        r = mad = bias = float('nan')
    print(f"{a}({meta[B[a]]['inv']},{len(ca)}) vs {b}({meta[B[b]]['inv']},{len(cb)}) {'rev' if rev else 'fwd'}: "
          f"aligned={len(pr)} spanA={span_a} spanB={span_b} nonzero={nz} exact_nonzero={ex} "
          f"| cord length n={len(la)} r={r:.2f} median|dA-dB|={mad:.1f}cm median(dA-dB)={bias:+.1f}")
    return dict(a=a, b=b, rev=rev, aligned=len(pr), nz=nz, exact=ex, r=r, mad=mad)

groups = {
  'eight study pairs': ['KH0362:KH0049','KH0192:KH0470','KH0121:KH0473','KH0132:KH0456','KH0128:KH0137','KH0097:KH0586','KH0156:KH0432','KH0175:KH0190'],
  'known duplicate in OKR concordance (same object, Ascher vs Urton)': ['KH0140:KH0483'],
  'Puruchuco copies (distinct objects, Urton & Brezine 2005)': ['KH0305:KH0301','KH0315:KH0300','KH0304:KH0303'],
  'extra checks': ['KH0469:KH0470','KH0192:KH0469'],
}
for g, lst in groups.items():
    print('==', g)
    for s in lst:
        report(*s.split(':'))
