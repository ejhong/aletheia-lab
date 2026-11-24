import sys, pathlib
sys.path.insert(0, sys.argv[1])
import numpy as np, run_khipu as rk
khipus, meta = rk.load_corpus(pathlib.Path(sys.argv[2]))
inv = {k['inv_num']: k for k in khipus.values()}
for k in khipus.values():
    if k['archive_num'] == 301:
        print(k['okr_num'], k['inv_num'], k['provenance'], len(k['pendants']))
def v(i): return np.array([c['val'] for c in inv[i]['pendants']], dtype=np.int64)
for a, b in [('UR063','UR073'), ('UR064','UR068'), ('UR066','UR067'), ('UR063','UR078')]:
    r = rk.best_contiguous_match(v(a), v(b))
    print(a, inv[a]['okr_num'], b, inv[b]['okr_num'], None if r is None else {x: r[x] for x in ('L','tier','err_l1','offset_a','offset_b','orient')})
