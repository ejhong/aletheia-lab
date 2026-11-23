#!/usr/bin/env python3
"""Amendments 1 and 2: rerun the locked analysis on the amended sample list, and add the amended admixture check.

    .venv/bin/python analysis/amend.py            # run from questions/population-y; writes results/amended/

The locked run.py is used unchanged. Only its input list and output folder differ, and the amended admixture
check (amendments.md, Amendment 2) is added to verdicts.json under "admixture_amended".
"""
import csv
import json
import pathlib

import f4lib
import run

HERE = pathlib.Path(__file__).resolve().parent
Q = HERE.parent


def load_amended():
    import collections
    sets = collections.OrderedDict()
    with open(HERE / "sets_amended.tsv") as f:
        cols = f.readline().rstrip("\n").split("\t")
        for line in f:
            p = dict(zip(cols, line.rstrip("\n").split("\t")))
            sets.setdefault(p["set"], []).append({"row": int(p["row"]), "gid": p["genetic_id"], "iid": p["individual_id"],
                                                  "group": p["group_id"], "assess": p["assessment"]})
    return sets


def main():
    sets = load_amended()
    out = Q / "results" / "amended"
    out.mkdir(parents=True, exist_ok=True)
    E = run.Engine()
    info = run.run(E, sets, out)
    v = run.verdicts(E.res, info, sets)

    # Amendment 2: admixture check with k(S) = f4(Chimp, Mandenka; Amazon, S) in place of h.
    v["admixture_amended"] = {}
    for pn, P in run.PANELS.items():
        o, pap, ref, amz, fr, sard, yor = P["out"][0], P["aus"][0], P["ref"][0], P["amazon"], P["french"], P["sard"], P["yoruba"]
        man = f"{pn}.Mandenka"
        quartets = [(o, pap, ref, amz),
                    (o, sard, amz, ref), (o, sard, amz, fr), (o, sard, amz, yor),
                    ("Chimp", man, amz, ref), ("Chimp", man, amz, fr), ("Chimp", man, amz, yor),
                    (o, pap, fr, amz), (o, pap, yor, amz)]

        def solve(x):
            det = x[2] * x[6] - x[3] * x[5]
            return (x[1] * x[6] - x[3] * x[4]) / det, (x[2] * x[4] - x[1] * x[5]) / det

        def p_adj(x):
            ae, aa = solve(x)
            return (x[0] - ae * x[7] - aa * x[8]) / (1 - ae - aa)

        comp = {"alpha_eur": f4lib.composite(E.freq, quartets, lambda x: solve(x)[0], E.snps),
                "alpha_afr": f4lib.composite(E.freq, quartets, lambda x: solve(x)[1], E.snps),
                "P_adj": f4lib.composite(E.freq, quartets, p_adj, E.snps),
                "P_on_this_mask": f4lib.composite(E.freq, quartets, lambda x: x[0], E.snps)}
        entry = {k: {"estimate": c[0], "se": c[1], "Z": round(c[0] / c[1], 2), "n_snps": c[2]} for k, c in comp.items()}
        for name, q in (("f4(Mbuti, French; Reference, Amazon)", (o, fr, ref, amz)),
                        ("f4(Chimp, Mandenka; Reference, Amazon)", ("Chimp", man, ref, amz))):
            r = f4lib.f4(E.freq, *q, E.snps)
            entry[name] = {"f4": r["f4"], "se": r["se"], "Z": round(r["z"], 2)}
        entry["passes"] = bool(entry["P_adj"]["Z"] >= 2)
        v["admixture_amended"][pn] = entry
    checks = dict(v["checks_on_primary"])
    checks["admixture"] = v["admixture_amended"]["A"]["passes"]
    v["checks_on_primary_with_amended_admixture"] = checks
    if v["P_A"]["Z"] >= 3:
        failed = [k for k, x in checks.items() if not x]
        v["headline"]["primary_with_amended_admixture_check"] = (
            "detected and robust" if not failed else "detected, with caveats: " + "; ".join(failed))
    (out / "verdicts.json").write_text(json.dumps(v, indent=1) + "\n")

    # The present-day statistics must be identical to the locked run.
    locked = {r["id"]: r for r in csv.DictReader(open(Q / "results" / "f4.tsv"), delimiter="\t")}
    amended = {r["id"]: r for r in csv.DictReader(open(out / "f4.tsv"), delimiter="\t")}
    present = [k for k in locked if locked[k]["section"].split(".")[0] in ("P", "LOO", "R", "Rind", "Rother", "L", "S", "T1", "T1person")]
    same = sum(1 for k in present if amended[k]["f4"] == locked[k]["f4"] and amended[k]["Z"] == locked[k]["Z"])
    print(f"present-day statistics identical to the locked run: {same} of {len(present)}")
    print(json.dumps({"headline": v["headline"], "admixture_amended": v["admixture_amended"]}, indent=1))


if __name__ == "__main__":
    main()
