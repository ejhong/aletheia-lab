import sys, json
sys.path.insert(0, sys.argv[3])
from khipu_lib import load_all, by_okr
db, summ = sys.argv[1], sys.argv[2]
meta, cords = load_all(db)
B = by_okr(meta)
hits = json.load(open(summ))['test2a_copy_mirror_hunt']['pendant_hits']
pairs = [('KH0362','KH0049'),('KH0121','KH0473'),('KH0132','KH0456'),('KH0128','KH0137'),('KH0097','KH0586'),('KH0156','KH0432'),('KH0175','KH0190'),('KH0305','KH0301'),('KH0315','KH0300'),('KH0304','KH0303')]
pad = int(sys.argv[4]) if len(sys.argv) > 4 else 2
for a, b in pairs:
    h = [x for x in hits if x['khipu_a'] == a and x['khipu_b'] == b][0]
    ca, cb = cords[B[a]], cords[B[b]]
    if h['orient'] == 'rev':
        cb = cb[::-1]
    oa, ob, L = h['offset_a'], h['offset_b'], h['L']
    print(f"\n##### {a} ({meta[B[a]]['inv']}) vs {b} ({meta[B[b]]['inv']}) orient={h['orient']} L={L} offA={oa} offB={ob} errL1={h['err_l1']}  nA={len(ca)} nB={len(cb)}")
    print(f"{'i':>3} | {'A#':>4} {'cl':>3} {'att':>3} {'col':>10} {'len':>6} {'val':>6} {'sub':>3} {'knotsA':<22}| {'B#':>4} {'cl':>3} {'att':>3} {'col':>10} {'len':>6} {'val':>6} {'sub':>3} {'knotsB':<22}")
    for i in range(-pad, L + pad):
        ia, ib = oa + i, ob + i
        def f(c, idx):
            if 0 <= idx < len(c):
                x = c[idx]
                return f"{x['ord'] or 0:>4} {x['cl']:>3} {x['att']:>3} {x['color'][:10]:>10} {str(x['length'])[:6]:>6} {x['val']:>6} {x['nsub']:>3} {x['knots'][:22]:<22}"
            return ' ' * 60
        mark = '*' if 0 <= i < L else ' '
        print(f"{mark}{i:>2} | {f(ca, ia)}| {f(cb, ib)}")
