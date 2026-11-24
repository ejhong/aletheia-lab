"""Run the study's own matcher (best_contiguous_match) on specific pairs, incl. a known duplicate."""
import sys
sys.path.insert(0, sys.argv[1])  # study analysis dir (copy)
import numpy as np, pathlib
import run_khipu as rk
khipus, meta = rk.load_corpus(pathlib.Path(sys.argv[2]))
by = {k['okr_num']: k for k in khipus.values()}
def vec(o): return np.array([c['val'] for c in by[o]['pendants']], dtype=np.int64)
for a, b in [('KH0140','KH0483'), ('KH0121','KH0473'), ('KH0097','KH0586'), ('KH0192','KH0470'), ('KH0192','KH0469'), ('KH0362','KH0049')]:
    r = rk.best_contiguous_match(vec(a), vec(b))
    print(a, b, None if r is None else {k: r[k] for k in ('L','tier','err_l1','f_exact','orient','offset_a','offset_b')})
# what is the full KH0140/KH0483 window score?
va, vb = vec('KH0140')[:15], vec('KH0483')[:15]
print('KH0140/KH0483 full 15-cord window:', rk.score_aligned_window(va, vb), 'diff', (va - vb).tolist())
print('without cord 13:', rk.score_aligned_window(np.delete(va, 12), np.delete(vb, 12)))
