#!/usr/bin/env python3
"""Compare an independent implementation's output with ours.

    python3 replication/compare.py THEIR_OUTDIR [corrected]
"""
import csv
import pathlib
import sys

Q = pathlib.Path(__file__).resolve().parent.parent
T = pathlib.Path(sys.argv[1])


def read(path):
    return list(csv.DictReader(open(path), delimiter="\t"))


RUN = sys.argv[2] if len(sys.argv) > 2 else "locked"
PEOPLE = "people_amended.tsv" if RUN == "corrected" else "people.tsv"
RES = Q / "results" / ("corrected" if RUN == "corrected" else "")
ours_p = {r["gid"]: r for r in read(Q / "analysis" / PEOPLE)}
row2gid = {r["row"]: g for g, r in ours_p.items()}
theirs_p = {r["genetic_id"]: r for r in read(T / "people.tsv")}
print(f"PEOPLE: ours {len(ours_p)}, theirs {len(theirs_p)}, in both {len(set(ours_p) & set(theirs_p))}")
both = sorted(set(ours_p) & set(theirs_p))
side = sum(ours_p[g]["side"] == theirs_p[g]["side"] for g in both)
typ = sum(ours_p[g]["type"] == theirs_p[g]["type"] for g in both)
print(f"  same side: {side} of {len(both)}; same data type: {typ} of {len(both)}")
same_pool = diff_pool = ours_only = theirs_only = 0
for g in both:
    a = {row2gid[x] for x in ours_p[g]["pool"].split(",")} if ours_p[g]["pool"] else set()
    b = set(theirs_p[g]["neighbours"].split(",")) if theirs_p[g]["neighbours"] else set()
    if a == b:
        same_pool += 1
    elif a and b:
        diff_pool += 1
    elif a:
        ours_only += 1
    else:
        theirs_only += 1
print(f"  neighbours identical: {same_pool}; different sets: {diff_pool}; only we give neighbours: {ours_only}; only they do: {theirs_only}")

ours_s = {r["genetic_id"]: r for r in read(RES / "scan.tsv")}
theirs_s = {r["genetic_id"]: r for r in read(T / "scan.tsv")}
print("\nSTATISTICS (people in both; a statistic counts where both give a value)")
print(f"{'statistic':10s} {'compared':>8s} {'agree':>6s} {'f4 differs':>10s} {'Z differs':>9s} {'only ours':>9s} {'only theirs':>11s}")
tot = agree_tot = 0
for name in ["S", "D1", "D2"] + [f"{t}_{r}" for t in ("E", "G") for r in ("French", "Yoruba", "Han", "Papuan")]:
    n = ok = fd = zd = oo = ot = 0
    for g in both:
        a, b = ours_s[g].get(f"{name}_f4", ""), theirs_s.get(g, {}).get(f"{name}_f4", "")
        if a and not b:
            oo += 1
        elif b and not a:
            ot += 1
        elif a and b:
            n += 1
            fa, fb = float(a), float(b)
            za, zb = float(ours_s[g][f"{name}_Z"]), float(theirs_s[g][f"{name}_Z"])
            f_ok = abs(fa - fb) <= max(0.01 * abs(fa), 1e-7)
            z_ok = abs(za - zb) <= 0.1
            ok += f_ok and z_ok
            fd += not f_ok
            zd += not z_ok
    tot += n
    agree_tot += ok
    print(f"{name:10s} {n:8d} {ok:6d} {fd:10d} {zd:9d} {oo:9d} {ot:11d}")
print(f"all statistics: {agree_tot} agree of {tot} compared")

fit = {r["control"]: float(r["coefficient"]) for r in read(T / "fit.tsv")}
import json
mine = json.loads((RES / "summary.json").read_text())["fit_coefficients"]
print("\nFIT  ours:", mine, "\n     theirs:", {k: round(v, 4) for k, v in fit.items()})
oh = {(r["genetic_id"], r["test"], r["toward"]) for r in read(RES / "hits.tsv")}
th = {(r["genetic_id"], r["test"], r["toward"]) for r in read(T / "hits.tsv")}
print(f"\nHITS  ours {len(oh)}, theirs {len(th)}, in both {len(oh & th)}")
for label, s in (("only ours", oh - th), ("only theirs", th - oh)):
    for h in sorted(s)[:12]:
        g = h[0]
        print(f"   {label}: {h}  our S_Z {ours_s.get(g, {}).get('S_Z', '')} their S_Z {theirs_s.get(g, {}).get('S_Z', '')}")
