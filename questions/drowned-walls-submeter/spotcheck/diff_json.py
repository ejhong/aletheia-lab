"""Compare two JSON files leaf by leaf, ignoring listed top-level keys. usage: diff_json.py a.json b.json [ignore,...]"""
import json, sys
a, b = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
ign = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else set()
diffs = []
def walk(x, y, p):
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y)):
            if p == "" and k in ign: continue
            if k not in x or k not in y: diffs.append((p + "/" + str(k), x.get(k, "<missing>"), y.get(k, "<missing>"))); continue
            walk(x[k], y[k], p + "/" + str(k))
    elif isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y): diffs.append((p + " (len)", len(x), len(y)))
        for i, (u, v) in enumerate(zip(x, y)): walk(u, v, f"{p}[{i}]")
    elif x != y: diffs.append((p, x, y))
walk(a, b, "")
for d in diffs: print(*d, sep="  |  ")
print(f"{len(diffs)} differences")
