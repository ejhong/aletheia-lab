#!/usr/bin/env python3
"""Amendment 2: the neighbours test for the people of data type "other", which the locked code left out.

    .venv/bin/python analysis/amend2.py        # run from questions/strangers; writes results/amended/other_type.*
"""
import csv
import json
import pathlib
import statistics

import numpy as np

import scan

Q = pathlib.Path(__file__).resolve().parent.parent
OUT = Q / "results" / "amended"
K, MAX_KM, MAX_YEARS = 20, 1500.0, 1500.0
SIB_LABELS = {"Russia_AltaiKrai_N", "Russia_AltaiKrai_Eneolithic"}


def pools(people):
    """Neighbours for people of type "other": the protocol's rule, as in build_people.py."""
    out = {}
    for side in ("american", "elsewhere"):
        grp = [p for p in people if p["side"] == side and p["type"] == "other" and p["lat"] not in ("", "None") and p["lon"] not in ("", "None")]
        if len(grp) <= K:
            continue
        la = np.radians(np.array([float(p["lat"]) for p in grp]))
        lo = np.radians(np.array([float(p["lon"]) for p in grp]))
        dt = np.array([p["date"] for p in grp])
        for i, p in enumerate(grp):
            a = np.sin((la - la[i]) / 2) ** 2 + np.cos(la) * np.cos(la[i]) * np.sin((lo - lo[i]) / 2) ** 2
            km = 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
            yrs = np.abs(dt - dt[i])
            d = km + yrs
            d[np.array([q["site"] == p["site"] for q in grp])] = np.inf
            order = np.argsort(d, kind="stable")[:K]
            if np.all(np.isfinite(d[order])) and np.all(km[order] <= MAX_KM) and np.all(yrs[order] <= MAX_YEARS):
                out[p["row"]] = [grp[j]["row"] for j in order]
    return out


def main():
    store, people, refs = scan.Store(), scan.load_people(), scan.load_refs()
    summary = json.loads((Q / "results" / "summary.json").read_text())
    blocks = {}
    for f in sorted((scan.CACHE / "parts").glob("part*.npz")):
        z = np.load(f)
        for k in z.files:
            if k.endswith(".b"):
                blocks[k] = z[k]
    kE = 1 + len(scan.CONTROLS)
    else_b = [p for p in people if p["side"] == "elsewhere" and f"{p['row']}.b" in blocks]
    est = np.array([[scan.one(blocks[f"{p['row']}.b"], k, kE)["f4"] for k in range(kE)] for p in else_b])
    u, _ = scan.robust_fit(est[:, 0], est[:, 1:])

    pool = pools(people)
    by_row = {p["row"]: p for p in people}
    n_else = sum(1 for r in pool if by_row[r]["side"] == "elsewhere")
    n_am = len(pool) - n_else
    family = summary["tests_in_family"] + n_else + len(scan.FOREIGN) * n_am
    zstar = statistics.NormalDist().inv_cdf(1 - 0.05 / family)
    LE, vE = scan.left_sides(store, ["NA"] + scan.CONTROLS)
    LA, vA = scan.left_sides(store, scan.FOREIGN)
    sib = [p for p in people if p["group"] in SIB_LABELS]
    na = store.freq["NA"]
    rows, hits = [], []
    for r, nb in sorted(pool.items()):
        p = by_row[r]
        x, pl = store.x(r), store.pool(nb)
        if p["side"] == "elsewhere":
            j = scan.residual(scan.contrast_sums(store, LE, vE, x, pl), u)
            rec = {"genetic_id": p["gid"], "group": p["group"], "entity": p["entity"], "side": p["side"], "date_bp": int(p["date"]),
                   "statistic": "S", "f4": j["f4"], "Z": round(j["z"], 3), "centred_Z": round(j["c_z"], 3), "hit": scan.passes(j, zstar)}
            if rec["hit"]:
                Lt, vt = scan.left_sides(store, ["NA"] + scan.CONTROLS)
                tv = scan.residual(scan.contrast_sums(store, Lt, vt, x, pl, store.tv), u)
                L2, v2 = scan.left_sides(store, ["ANCIENT_AMERICAN"] + scan.CONTROLS)
                alt = scan.residual(scan.contrast_sums(store, L2, v2, x, pl), u)
                s = store.pool([q["row"] for q in sib if q["row"] != r and not (p["site"] and q["site"] == p["site"])])
                ok = ~np.isnan(s) & ~np.isnan(na) & ~np.isnan(x) & ~np.isnan(pl)
                left, right = np.where(ok, s - na, 0).astype(np.float32), np.where(ok, pl - x, 0).astype(np.float32)
                t = scan.jack(store.sums(ok.astype(np.float32)).astype(float), store.sums(left * right).astype(float),
                              store.sums(left).astype(float), store.sums(right).astype(float))
                rec.update(tv_ratio=round(tv["f4"] / j["f4"], 2), tv_Z=round(tv["z"], 2), second_ratio=round(alt["f4"] / j["f4"], 2),
                           robust=bool(tv["f4"] >= 0.5 * j["f4"] and tv["z"] >= 2 and alt["f4"] >= 0.5 * j["f4"]),
                           T_Z=round(t["z"], 2), T_centred_Z=round(t["c_z"], 2), sex=p["sex"], mt=p["mt_hg"], y=p["y_hg"],
                           library=p["library"], publication=p["pub"], lat=p["lat"], lon=p["lon"],
                           neighbours="; ".join(sorted({by_row[q]["group"] for q in nb}))[:300])
                hits.append(rec)
            rows.append(rec)
        else:
            blk = scan.contrast_sums(store, LA, vA, x, pl)
            for k, name in enumerate(scan.FOREIGN):
                j = scan.one(blk, k, len(scan.FOREIGN))
                rec = {"genetic_id": p["gid"], "group": p["group"], "entity": p["entity"], "side": p["side"], "date_bp": int(p["date"]),
                       "statistic": f"E_{name}", "f4": j["f4"], "Z": round(j["z"], 3), "centred_Z": round(j["c_z"], 3),
                       "hit": scan.passes(j, zstar)}
                rows.append(rec)
                if rec["hit"]:
                    hits.append(rec)
    cols = ["genetic_id", "group", "entity", "side", "date_bp", "statistic", "f4", "Z", "centred_Z", "hit"]
    with open(OUT / "other_type.tsv", "w") as f:
        f.write("\t".join(cols) + "\n")
        for rec in rows:
            f.write("\t".join(str(rec[c]) for c in cols) + "\n")
    # Original hits that would fall below the recomputed threshold.
    lost = []
    for h in csv.DictReader(open(Q / "results" / "hits.tsv"), delimiter="\t"):
        zs = [float(v) for v in h["Z"].split(";")]
        if min(zs) < zstar:
            lost.append((h["genetic_id"], h["test"], h["toward"], h["Z"]))
    out = {"people_newly_tested": len(pool), "elsewhere": n_else, "american_side": n_am, "family": family,
           "threshold": round(zstar, 4), "locked_threshold": summary["threshold"], "new_hits": hits,
           "original_hits_below_new_threshold": lost}
    (OUT / "other_type.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
