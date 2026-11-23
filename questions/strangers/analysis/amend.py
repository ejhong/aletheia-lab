#!/usr/bin/env python3
"""Amendment 1 and the centre robustness checks (see amendments.md). Uses the locked scan.py unchanged.

    .venv/bin/python analysis/amend.py        # run from questions/strangers; writes results/amended/
"""
import csv
import json
import pathlib
import statistics
import sys

import numpy as np

import scan

Q = pathlib.Path(__file__).resolve().parent.parent
OUT = Q / "results" / "amended"
SIB_LABELS = {"Russia_AltaiKrai_N", "Russia_AltaiKrai_Eneolithic"}


def main():
    global OUT
    RES = Q / "results"
    if "corrected" in sys.argv:           # Amendment 2 (revised): work from the corrected run
        import corrected_run
        corrected_run.patch()
        RES = scan.OUT
        OUT = RES / "amended"
    OUT.mkdir(parents=True, exist_ok=True)
    store, people, refs = scan.Store(), scan.load_people(), scan.load_refs()
    by_gid = {p["gid"]: p for p in people}
    blocks = {}
    for f in sorted((scan.CACHE / "parts").glob("part*.npz")):
        z = np.load(f)
        for k in z.files:
            blocks[k] = z[k]
    kE, kA = 1 + len(scan.CONTROLS), len(scan.FOREIGN)
    else_b = [p for p in people if p["side"] == "elsewhere" and f"{p['row']}.b" in blocks]
    est = np.array([[scan.one(blocks[f"{p['row']}.b"], k, kE)["f4"] for k in range(kE)] for p in else_b])
    u, _ = scan.robust_fit(est[:, 0], est[:, 1:])
    summary = json.loads((RES / "summary.json").read_text())
    assert all(abs(float(a) - b) < 1e-4 for a, b in zip(u, summary["fit_coefficients"].values())), "fit differs from the locked run"

    # ---- Amendment 1: is each robust hit elsewhere closer to Native Americans than to their Siberian relatives? ----
    hits = [h for h in csv.DictReader(open(RES / "hits.tsv"), delimiter="\t") if h["side"] == "elsewhere" and h["robust"] == "True"]
    sib = [p for p in people if p["group"] in SIB_LABELS]
    na, m = store.freq["NA"], store.freq["Mbuti"]
    persons = sorted({h["genetic_id"] for h in hits})
    zstar = statistics.NormalDist().inv_cdf(1 - 0.05 / len(persons))
    rows = []
    for gid in persons:
        p = by_gid[gid]
        s = store.pool([q["row"] for q in sib if q["row"] != p["row"] and not (p["site"] and q["site"] == p["site"])])
        x = store.x(p["row"])
        tests = {h["test"] for h in hits if h["genetic_id"] == gid}
        rec = {"genetic_id": gid, "group": p["group"], "entity": p["entity"], "lat": p["lat"], "lon": p["lon"],
               "date_bp": int(p["date"]), "tests": "+".join(sorted(tests)), "in_SIB": p["group"] in SIB_LABELS}
        passed = False
        if "neighbours" in tests:
            pool = store.pool(p["pool"])
            ok = ~np.isnan(s) & ~np.isnan(na) & ~np.isnan(x) & ~np.isnan(pool)
            left = np.where(ok, s - na, 0).astype(np.float32)
            right = np.where(ok, pool - x, 0).astype(np.float32)
            j = scan.jack(store.sums(ok.astype(np.float32)).astype(float), store.sums(left * right).astype(float),
                          store.sums(left).astype(float), store.sums(right).astype(float))
            rec.update(T_neighbours=j["f4"], T_neighbours_Z=round(j["z"], 2), T_neighbours_centred_Z=round(j["c_z"], 2))
            passed |= scan.passes(j, zstar)
        if "absolute" in tests:
            ok = ~np.isnan(s) & ~np.isnan(na) & ~np.isnan(x) & ~np.isnan(m)
            left = np.where(ok, m - x, 0).astype(np.float32)
            right = np.where(ok, s - na, 0).astype(np.float32)
            j = scan.jack(store.sums(ok.astype(np.float32)).astype(float), store.sums(left * right).astype(float),
                          store.sums(left).astype(float), store.sums(right).astype(float))
            rec.update(T_absolute=j["f4"], T_absolute_Z=round(j["z"], 2), T_absolute_centred_Z=round(j["c_z"], 2))
            passed |= scan.passes(j, zstar)
        rec["specific_to_native_americans"] = bool(passed)
        rows.append(rec)
    cols = ["genetic_id", "group", "entity", "lat", "lon", "date_bp", "tests", "in_SIB", "T_neighbours", "T_neighbours_Z",
            "T_neighbours_centred_Z", "T_absolute", "T_absolute_Z", "T_absolute_centred_Z", "specific_to_native_americans"]
    with open(OUT / "specificity.tsv", "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in sorted(rows, key=lambda r: (not r["specific_to_native_americans"], r["entity"], r["group"])):
            f.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
    spec = [r for r in rows if r["specific_to_native_americans"]]
    print(f"Amendment 1: {len(rows)} people tested, threshold {zstar:.2f}; specific to Native Americans: {len(spec)}")
    for r in spec:
        print("  ", r["genetic_id"], r["group"], r["entity"], r.get("T_neighbours_Z", ""), r.get("T_absolute_Z", ""))

    # ---- centre robustness, as the protocol specifies ----
    thr = summary["centre_threshold"]
    out = {}
    for name, (side, test) in scan.CENTRES.items():
        members = [p for p in people if p["side"] == side and test(p) and f"{p['row']}.b" in blocks]
        if len(members) < 2:
            continue

        def summed(ref_names, mask=None, is_s=False, na_name="NA"):
            names = ([na_name] + scan.CONTROLS) if is_s else ref_names
            L, valid = scan.left_sides(store, names)
            tot = sum(scan.contrast_sums(store, L, valid, store.x(p["row"]), store.pool(p["pool"]), mask) for p in members)
            return scan.residual(tot, u) if is_s else scan.one(tot, 0, 1)

        for stat, val in summary["centres"][name]["tests"].items():
            if val["Z"] < thr:
                continue
            if stat == "S":
                main, tv, alt = summed(None, is_s=True), summed(None, store.tv, True), summed(None, None, True, "ANCIENT_AMERICAN")
            elif stat.startswith("E_"):
                ref = stat[2:]
                main, tv, alt = summed([ref]), summed([ref], store.tv), summed([scan.SECOND[ref]])
            else:
                oname = stat[len("toward_"):]
                orows = [q["row"] for q in people if q["side"] == "elsewhere" and scan.CENTRES[oname][1](q)]
                store.freq["_centre"] = store.pool(orows)
                main, tv, alt = summed(["_centre"]), summed(["_centre"], store.tv), None
            entry = {"Z": round(main["z"], 2), "passes_rule": scan.passes(main, thr),
                     "tv_ratio": round(tv["f4"] / main["f4"], 2), "tv_Z": round(tv["z"], 2),
                     "tv_ok": bool(tv["f4"] >= 0.5 * main["f4"] and tv["z"] >= 2)}
            if alt is not None:
                entry.update(second_ratio=round(alt["f4"] / main["f4"], 2), second_ok=bool(alt["f4"] >= 0.5 * main["f4"]))
            entry["robust"] = bool(entry["passes_rule"] and entry["tv_ok"] and entry.get("second_ok", True))
            out[f"{name}.{stat}"] = entry
    (OUT / "centres_robustness.json").write_text(json.dumps(out, indent=1) + "\n")
    print("centre statistics past the threshold:", json.dumps(out, indent=1))
    (OUT / "summary.json").write_text(json.dumps({"people_tested": len(rows), "threshold": round(zstar, 3),
                                                   "specific_to_native_americans": [r["genetic_id"] for r in spec],
                                                   "centres": out}, indent=1) + "\n")


if __name__ == "__main__":
    main()
