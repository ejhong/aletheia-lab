import sys
sys.path.insert(0, sys.argv[2])
from khipu_lib import load_all, by_okr
from align_same_object import sw, meta, cords, B  # reuses own alignment (loads db from argv[1])
for spec in sys.argv[3:]:
    a, b, o = spec.split(':')
    ca, cb = cords[B[a]], cords[B[b]]
    if o == 'rev': cb = cb[::-1]
    sc, pr = sw(ca, cb)
    print('#####', a, b, o, 'score', sc)
    pi = pj = None
    for i, j in pr:
        if pi is not None and (i - pi > 1 or j - pj > 1):
            print('   ---- gap: A skips', i - pi - 1, 'B skips', j - pj - 1)
        x, y = ca[i], cb[j]
        flag = '==' if x['val'] == y['val'] else '~ ' if x['val'] and y['val'] and abs(x['val']-y['val']) <= max(1, 0.02*max(x['val'], y['val'])) else 'XX'
        print(f"{i:>3} {x['cl']:>3} {x['color'][:8]:>8} {str(x['length'])[:5]:>5} {x['val']:>6} {x['knots'][:20]:<20} {flag} {j:>3} {y['cl']:>3} {y['color'][:8]:>8} {str(y['length'])[:5]:>5} {y['val']:>6} {y['knots'][:20]}")
        pi, pj = i, j
