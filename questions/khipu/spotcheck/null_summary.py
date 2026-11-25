import json, sys, math
for f in sys.argv[1:]:
    R = json.load(open(f))
    n = len(R); A = sum(r['A'] for r in R); B = sum(r['B'] for r in R); gA = sum(r['gA'] for r in R); gB = sum(r['gB'] for r in R)
    pairs = sum(r['pairs'] for r in R)
    hits = [h for r in R for h in r['A_hits']]
    L8 = [h for h in hits if h[3] >= 8]
    print(f"{f}: scans={n} pendant pair tests={pairs} TierA={A} (per scan {A/n:.2f}; per pair {A/pairs:.2e}) TierB={B} (per scan {B/n:.2f}) | cluster-sum TierA={gA} TierB={gB}")
    print(f"   TierA hits with L>=8: {len(L8)}; max value in any null TierA window: {max((max(h[5]) for h in hits), default=None)}; L values: {sorted(h[3] for h in hits)}")
    print(f"   expected false TierA per real scan = {A/n:.2f}; vs 10 real TierA (9 pendant+1 cluster) -> FDR approx {A/n/10:.3f}")
    for h in hits: print('     ', h)
