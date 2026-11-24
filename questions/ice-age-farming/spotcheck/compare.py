import json, sys
a = json.load(open(sys.argv[1])); b = json.load(open(sys.argv[2]))
def walk(x, y, path=""):
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y)):
            if k not in x or k not in y: print("KEY ONLY IN ONE:", path + "/" + k); continue
            walk(x[k], y[k], path + "/" + k)
    elif isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y): print("LEN DIFF", path, len(x), len(y))
        for i, (u, v) in enumerate(zip(x, y)): walk(u, v, f"{path}[{i}]")
    elif x != y:
        print("DIFF", path, x, "->", y)
walk(a, b)
print("done")
