"""Independent spot check of anaesthetics-terahertz (#115), written by Claude without using the study's solver.

It needs no docked poses. It rebuilds the ring network from the public structure files, then asks three things:
1. Does the empty-protein spectrum match the study's (468.0-695.5 THz for 1JFF, 16 modes in 605-621 THz)?
2. Is the direction of the shift near 613 THz set by the added molecule alone? A featureless probe of adjustable
   size is put next to rings in tubulin, in lysozyme and in a random cloud of rings.
3. Does the answer change when the whole structure is turned in space, under two readings of the published method?

Readings of "the induced dipole direction is defined by the vector (a'xx, a'yy, a'zz) in the protein frame":
  T  the tensor is turned into the protein frame and its diagonal is kept      (the study's Model A)
  V  the three principal values are treated as an arrow fixed to the ring and that arrow is turned
"""
import math, sys, pathlib
import numpy as np

E, ME, EPS0 = 1.602176634e-19, 9.1093837015e-31, 8.8541878128e-12
AU = 1.64877727436e-41
A3_PER_AU = 0.529177210903 ** 3
DIP = E * E / (4 * math.pi * EPS0 * ME)
DIAG = E * E / (ME * AU)
ALPHA = {"TRP": (119.5, 91.6, 29.4), "TYR": (89.5, 43.0, 82.9), "PHE": (79.0, 79.0, 38.6)}   # Kurian 2018, Table III
LO, HI = 605.0, 621.0


def unit(v):
    return v / np.linalg.norm(v)


def rings(path, chains):
    res = {}
    for line in open(path):
        if line.startswith("ENDMDL"):
            break
        if not line.startswith("ATOM"):
            continue
        name, alt, rn, ch = line[12:16].strip(), line[16], line[17:20], line[21]
        if rn not in ALPHA or ch not in chains or alt not in " A":
            continue
        key = (ch, int(line[22:26]), line[26], rn)
        res.setdefault(key, {})[name] = np.array([float(line[30:38]), float(line[38:46]), float(line[46:54])])
    out = []
    for key, a in res.items():
        rn = key[3]
        try:
            if rn == "TRP":
                c = (a["CD2"] + a["CE2"]) / 2
                x = unit(a["NE1"] - c)
                z = unit(np.cross(x, a["CZ2"] - a["CG"]))
                y = np.cross(z, x)
            else:
                six = [a[n] for n in ("CG", "CD1", "CD2", "CE1", "CE2", "CZ")]
                c = np.mean(six, axis=0)
                if rn == "TYR":
                    y = unit(a["CG"] - a["CZ"])
                    z = unit(np.cross((a["CD1"] + a["CE1"]) - (a["CD2"] + a["CE2"]), y))
                else:
                    y = unit(a["CZ"] - a["CG"])
                    z = unit(np.cross((a["CD2"] + a["CE2"]) - (a["CD1"] + a["CE1"]), y))
                x = np.cross(y, z)
        except KeyError:
            continue
        out.append({"kind": rn, "pos": c, "frame": np.column_stack([x, y, z]), "alpha": np.array(ALPHA[rn])})
    return out


def probe(pos, alpha_a3, frame=None):
    return {"kind": "GAS", "pos": np.asarray(pos, float), "frame": np.eye(3) if frame is None else frame,
            "alpha": np.full(3, alpha_a3 / A3_PER_AU)}


def oscillator(node, reading):
    R, a = node["frame"], node["alpha"]
    if reading == "T":
        d = np.diag(R @ np.diag(a) @ R.T)
    else:
        d = R @ a
    n = np.linalg.norm(d)
    return n, d / n


def matrix(nodes, reading):
    n = len(nodes)
    abar, u = zip(*(oscillator(x, reading) for x in nodes))
    M = np.zeros((n, n))
    for s in range(n):
        M[s, s] = DIAG / abar[s]
        for t in range(s + 1, n):
            d = (nodes[t]["pos"] - nodes[s]["pos"]) * 1e-10
            r = np.linalg.norm(d)
            rh = d / r
            M[s, t] = M[t, s] = DIP / r ** 3 * (u[s] @ u[t] - 3 * (u[s] @ rh) * (u[t] @ rh))
    return M


def modes(M):
    w, v = np.linalg.eigh(M)
    return np.sqrt(np.clip(w, 0, None)) / (2 * math.pi * 1e12), v


def f_alone(alpha_a3):
    return math.sqrt(DIAG / (math.sqrt(3) * alpha_a3 / A3_PER_AU)) / (2 * math.pi * 1e12)


def band_shift(prot, f0, v0, gas, reading):
    """Largest shift (GHz) of an empty-protein mode in 605-621 THz when the gas is added. Plus = pushed down."""
    f1, v1 = modes(matrix(prot + [gas], reading))
    gas_mode = int(np.argmax(v1[-1] ** 2))
    keep = [j for j in range(len(f1)) if j != gas_mode]
    ov = (v0.T @ v1[:-1][:, keep]) ** 2
    best = 0.0
    used = set()
    order = np.dstack(np.unravel_index(np.argsort(-ov, axis=None), ov.shape))[0]
    match = {}
    for i, j in order:
        if i in match or j in used:
            continue
        match[i] = j
        used.add(j)
    for i in range(len(f0)):
        if LO <= f0[i] <= HI:
            df = (f1[keep[match[i]]] - f0[i]) * 1000
            if abs(df) > abs(best):
                best = df
    return -best


def pockets(prot, rng, k=8, dist=5.0):
    """k probe sites, each 5 A from a ring along its normal, on the side away from the nearest other ring."""
    idx = [i for i, x in enumerate(prot) if x["kind"] == "TRP"][:k]
    if len(idx) < k:
        idx += list(rng.choice([i for i in range(len(prot)) if i not in idx], k - len(idx), replace=False))
    sites = []
    for i in idx:
        z = prot[i]["frame"][:, 2]
        cand = [prot[i]["pos"] + dist * z, prot[i]["pos"] - dist * z]
        gap = [min(np.linalg.norm(c - x["pos"]) for j, x in enumerate(prot) if j != i) for c in cand]
        sites.append(cand[int(np.argmax(gap))])
    return sites


def random_cloud(n, rng, radius=32.0):
    kinds = ["TRP"] * 8 + ["TYR"] * 34 + ["PHE"] * 39
    out = []
    while len(out) < n:
        p = rng.normal(size=3)
        p = unit(p) * radius * rng.random() ** (1 / 3)
        if all(np.linalg.norm(p - x["pos"]) >= 4.5 for x in out):
            q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
            if np.linalg.det(q) < 0:
                q[:, 0] *= -1
            k = kinds[len(out)]
            out.append({"kind": k, "pos": p, "frame": q, "alpha": np.array(ALPHA[k])})
    return out


def turn(nodes, Q):
    return [{**x, "pos": Q @ x["pos"], "frame": Q @ x["frame"]} for x in nodes]


def rand_rot(rng):
    q, r = np.linalg.qr(rng.normal(size=(3, 3)))
    q = q * np.sign(np.diag(r))
    if np.linalg.det(q) < 0:
        q[:, 0] *= -1
    return q


def main(pdb_dir):
    rng = np.random.default_rng(118)
    pdb_dir = pathlib.Path(pdb_dir)
    nets = {"tubulin 1JFF": rings(pdb_dir / "1JFF.pdb", "AB"), "lysozyme 1DPX": rings(pdb_dir / "1DPX.pdb", "A"),
            "81 random rings": random_cloud(81, rng)}
    print("== 1. empty-protein spectrum ==")
    for name, net in nets.items():
        c = {k: sum(x["kind"] == k for x in net) for k in ALPHA}
        for rd in "TV":
            f, _ = modes(matrix(net, rd))
            print(f"{name:16s} reading {rd}: {len(net)} rings {c}  {f.min():.1f}-{f.max():.1f} THz, "
                  f"{int(((f >= LO) & (f <= HI)).sum())} modes in 605-621")
    print("single rings, principal values: " + ", ".join(
        f"{k} {math.sqrt(DIAG / np.linalg.norm(a)) / (2 * math.pi * 1e12):.0f} THz" for k, a in ALPHA.items()))
    lit = {k: math.sqrt(sum(DIAG / x for x in a)) / (2 * math.pi * 1e12) for k, a in ALPHA.items()}
    print("single rings, formula as printed in Craddock 2017 (root of summed squares): " + ", ".join(
        f"{k} {v:.0f} THz" for k, v in lit.items()))

    print("\n== 2. direction of the 613 THz shift against the size of a featureless probe ==")
    sizes = np.arange(3.0, 20.01, 0.5)
    for name, net in nets.items():
        for rd in "TV":
            f0, v0 = modes(matrix(net, rd))
            if not ((f0 >= LO) & (f0 <= HI)).any():
                print(f"{name:16s} reading {rd}: no mode in the band")
                continue
            sites = pockets(net, rng)
            agree = total = 0
            line = []
            for a in sizes:
                shifts = [band_shift(net, f0, v0, probe(p, a), rd) for p in sites]
                d = max(shifts, key=abs)
                fa = f_alone(a)
                if abs(fa - 613) > 8:
                    total += 1
                    agree += (d > 0) == (fa > 613)
                line.append("+" if d > 0 else "-")
            print(f"{name:16s} reading {rd}: {''.join(line)}   rule holds {agree}/{total} (probes within 8 THz of 613 left out)")
    cross = min(sizes, key=lambda a: abs(f_alone(a) - 613))
    print(f"sizes 3.0 to 20.0 cubic angstroms left to right; a probe alone sits at 613 THz near {cross:.1f} "
          f"(exactly {(f_alone(1.0) / 613) ** 2:.2f})")

    print("\n== 3. turning the whole structure in space (20 random turns) ==")
    net = nets["tubulin 1JFF"]
    site = pockets(net, rng)[0]
    for rd in "TV":
        lo, sh = [], []
        for _ in range(20):
            Q = rand_rot(rng)
            tn = turn(net, Q)
            f0, v0 = modes(matrix(tn, rd))
            lo.append(f0.min())
            g = probe(Q @ site, 8.0, Q)          # the probe is turned with the protein
            sh.append(band_shift(tn, f0, v0, g, rd))
        sh = np.array(sh)
        print(f"reading {rd}: lowest mode {min(lo):.1f} to {max(lo):.1f} THz; 613 THz shift for an 8 cubic angstrom "
              f"probe at one site: {int((sh > 0).sum())} of 20 turns downward, median {np.median(sh):+.0f} GHz, "
              f"middle half {np.percentile(sh, 25):+.0f} to {np.percentile(sh, 75):+.0f} GHz")


if __name__ == "__main__":
    main(sys.argv[1])
