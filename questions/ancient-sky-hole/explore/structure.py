#!/usr/bin/env python3
"""Blind structural inspection of downloaded primary star catalogs.

EXPLORATORY ONLY — never computes southern-sky coordinates, hole centers,
or (epoch, latitude) estimates. Inspects only headers, counts, quality flags,
Hipparcos cross-match coverage, constellation lists, and the NORTHERN sky
(dec_J2000 > +20 deg) magnitude completeness curve.
"""
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def parse_vizier_tsv(path: Path):
    rows = []
    headers = None
    sep_seen = False
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = [p.strip() for p in line.rstrip("\n").split("\t")]
            if headers is None:
                headers = parts
                continue
            if not sep_seen:
                if all(set(p) <= {"-", " "} and "-" in p for p in parts if p):
                    sep_seen = True
                continue
            if len(parts) < len(headers):
                parts += [""] * (len(headers) - len(parts))
            rows.append(dict(zip(headers, parts)))
    return headers, rows


def main():
    p_hdr, p_rows = parse_vizier_tsv(DATA / "ptolemy_verbunt2012.tsv")
    h_hdr, h_rows = parse_vizier_tsv(DATA / "hipparcos_v70.tsv")
    b_hdr, b_rows = parse_vizier_tsv(DATA / "bsc5.tsv")

    print(f"Ptolemy rows:   {len(p_rows)}  cols={p_hdr}")
    print(f"Hipparcos rows: {len(h_rows)}  cols={h_hdr}")
    print(f"BSC5 rows:      {len(b_rows)}  cols={b_hdr}")

    hip_map = {}
    missing_pos = 0
    for r in h_rows:
        try:
            hid = int(r["HIP"])
            ra = float(r["RAICRS"])
            de = float(r["DEICRS"])
            vmag = float(r["Vmag"])
            pmra = float(r["pmRA"]) if r["pmRA"] else 0.0
            pmde = float(r["pmDE"]) if r["pmDE"] else 0.0
            hd = int(r["HD"]) if r["HD"] else None
            hip_map[hid] = (ra, de, vmag, pmra, pmde, hd)
        except ValueError:
            missing_pos += 1
    print(f"Valid Hipparcos V<=7.0 stars: {len(hip_map)} (skipped {missing_pos})")

    # Ptolemy quality flags and constellation list
    q_counts = Counter(r["I"] for r in p_rows)
    fn_counts = Counter(r["f_N"] for r in p_rows)
    csts = []
    seen = set()
    cst_counts = Counter()
    ptol_hips_all = set()
    ptol_hips_q13 = set()
    unmatched_in_h70 = 0
    for r in p_rows:
        c = (int(r["C"]), r["cst"])
        if c not in seen:
            seen.add(c)
            csts.append(c)
        cst_counts[r["cst"]] += 1
        if r["HIP"]:
            hid = int(r["HIP"])
            ptol_hips_all.add(hid)
            if r["I"] in {"1", "2", "3"}:
                ptol_hips_q13.add(hid)
            if hid not in hip_map:
                unmatched_in_h70 += 1

    print(f"Ptolemy ID quality flags I: {dict(sorted(q_counts.items()))}")
    print(f"Ptolemy f_N (informes 'a'): {dict(fn_counts)}")
    print(f"Unique HIP in Ptolemy (all): {len(ptol_hips_all)}, (I<=3): {len(ptol_hips_q13)}")
    print(f"Ptolemy HIPs missing from Hipparcos V<=7.0: {unmatched_in_h70}")
    print(f"Constellations ({len(csts)}):")
    for num, abbr in sorted(csts):
        print(f"  {num:2d}. {abbr:6s} ({cst_counts[abbr]:2d} stars)")

    # Blind northern-sky completeness curve (dec_J2000 > +20 deg ONLY!)
    print("\nBLIND NORTHERN-SKY (dec_J2000 > +20 deg) completeness by Vmag:")
    bins = [(-2.0, 2.0), (2.0, 3.0), (3.0, 3.5), (3.5, 4.0), (4.0, 4.5),
            (4.5, 5.0), (5.0, 5.5), (5.5, 6.0), (6.0, 6.5)]
    for lo, hi in bins:
        tot = 0
        hit = 0
        for hid, (ra, de, vmag, *_rest) in hip_map.items():
            if de > 20.0 and lo <= vmag < hi:
                tot += 1
                if hid in ptol_hips_q13:
                    hit += 1
        frac = hit / tot if tot else 0.0
        print(f"  Vmag [{lo:4.1f}, {hi:4.1f}): {hit:4d} / {tot:4d}  ({100*frac:5.1f}%)")

    # BSC5 HD cross-match coverage
    hd_to_name = {}
    for r in b_rows:
        if r["HD"] and r["Name"]:
            hd_to_name[int(r["HD"])] = r["Name"]
    matched_names = sum(1 for v in hip_map.values() if v[5] in hd_to_name and v[2] <= 5.5)
    tot_v55 = sum(1 for v in hip_map.values() if v[2] <= 5.5)
    print(f"\nBSC5 Bayer/Flamsteed name coverage for V<=5.5: {matched_names}/{tot_v55}")


if __name__ == "__main__":
    main()
