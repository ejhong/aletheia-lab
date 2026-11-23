#!/usr/bin/env python3
"""EXPLORATORY (after the lock and after Amendment 1). Not a finding on its own.

For a flagged person, whom do they lean toward compared with their neighbours? Prints Z of f4(Mbuti, W; P, X) for a
panel of present-day and ancient reference groups W, plus the same for a made-up stranger: one of the person's own
neighbours with 7% of 5 cM blocks replaced by an ancient American's calls.

    .venv/bin/python explore/profile.py GENETIC_ID [GENETIC_ID ...]
"""
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "analysis"))
import scan  # noqa: E402

ANCIENT = {"WHG (Iron Gates)": lambda g: g == "Serbia_IronGates_Mesolithic", "Anatolian farmers": lambda g: g.startswith("Turkey_Marmara_Barcin_N"),
           "Iran Neolithic": lambda g: g.startswith("Iran_GanjDareh_N"), "Yamnaya (Samara)": lambda g: g.startswith("Russia_Samara_EBA_Yamnaya"),
           "Altai hunter-gatherers": lambda g: g in ("Russia_AltaiKrai_N", "Russia_AltaiKrai_Eneolithic"),
           "Chukotka (Old Bering Sea)": lambda g: "OldBeringSea" in g, "Morocco Epipaleolithic": lambda g: g.startswith("Morocco_Epipaleolithic"),
           "Varna (Bulgaria)": lambda g: g == "Bulgaria_Varna_C"}
MODERN = ["NA", "ANCIENT_AMERICAN", "EHG", "Han", "Japanese", "Papuan", "Australian", "French", "Sardinian", "Yoruba", "Mandenka"]


def main():
    store, people, refs = scan.Store(), scan.load_people(), scan.load_refs()
    by_gid = {p["gid"]: p for p in people}
    by_row = {p["row"]: p for p in people}
    for name, test in ANCIENT.items():
        store.freq[name] = store.pool([p["row"] for p in people if test(p["group"])])
    panel = MODERN + list(ANCIENT)
    rng = np.random.default_rng(7)
    lengths = np.diff(np.r_[store.starts, store.n_snp])
    donors = [r for r in refs["ANCIENT_AMERICAN"]]
    for gid in sys.argv[1:]:
        p = by_gid[gid]
        pool = store.pool(p["pool"])
        x = store.x(p["row"])
        nb = by_row[p["pool"][0]]
        y = store.x(nb["row"])
        dn = store.x(int(rng.choice(donors)))
        fake = np.where(np.repeat(rng.random(lengths.size) < 0.07, lengths) & ~np.isnan(dn), dn, y)
        fake_pool = store.pool([r for r in p["pool"] if r != nb["row"]])
        print(f"\n{gid}  {p['group']}  ({p['nsnp']} SNPs)   | made-up stranger: neighbour {nb['gid']} with 7% ancient American")
        out = []
        for w in panel:
            exclude = {p["row"]} | set(p["pool"])
            L, valid = scan.left_sides(store, [w])
            a = scan.one(scan.contrast_sums(store, L, valid, x, pool), 0, 1)
            b = scan.one(scan.contrast_sums(store, L, valid, fake, fake_pool), 0, 1)
            out.append((a["z"], w, b["z"]))
        for z, w, zf in sorted(out, reverse=True):
            print(f"   {w:28s} person Z {z:6.1f}     made-up stranger Z {zf:6.1f}")


if __name__ == "__main__":
    main()
