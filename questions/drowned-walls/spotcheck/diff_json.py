import json, sys
a = json.load(open(sys.argv[1])); b = json.load(open(sys.argv[2]))
diffs = []
def walk(x, y, path):
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y)):
            if k not in x or k not in y: diffs.append((path + "/" + str(k), x.get(k, "<missing>"), y.get(k, "<missing>"))); continue
            walk(x[k], y[k], path + "/" + str(k))
    elif isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y): diffs.append((path + " len", len(x), len(y)))
        for i, (u, v) in enumerate(zip(x, y)): walk(u, v, f"{path}[{i}]")
    else:
        if x != y: diffs.append((path, x, y))
walk(a, b, "")
for d in diffs: print(d[0], "|", str(d[1])[:120], "|", str(d[2])[:120])
print("N diffs:", len(diffs))
