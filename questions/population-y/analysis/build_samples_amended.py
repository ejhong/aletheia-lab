#!/usr/bin/env python3
"""Amendment 1: rebuild the sample sets with two corrections to who counts as an ancient American.

    python3 analysis/build_samples_amended.py      # writes analysis/sets_amended.tsv and ancient_cells_amended.tsv

Uses the locked build_samples.py unchanged, and only alters its input:
  1. an ancient individual in the Americas whose coordinates are given must have a longitude between -170 and -30;
  2. an ancient individual whose group label contains "Norse" is left out.
Amendment 2 needs one more present-day group, Mandenka, in each panel; it is appended.
"""
import pathlib
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_samples as B  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
locked_load = B.load
removed = []


def amended_load():
    S = locked_load()
    for s in S:
        if s["entity"] in B.AMERICAS and s["date"] is not None and s["date"] >= 500:
            bad_lon = s["lon"] is not None and not (-170 <= s["lon"] <= -30)
            if bad_lon or "Norse" in s["group"]:
                removed.append((s["gid"], s["group"], s["entity"], s["lon"], "longitude" if bad_lon else "Norse"))
                s["entity"] = "EXCLUDED_BY_AMENDMENT_1"
    return S


def main():
    B.load = amended_load
    with tempfile.TemporaryDirectory() as t:
        B.HERE = pathlib.Path(t)
        B.main()
        shutil.copy(pathlib.Path(t) / "sets.tsv", HERE / "sets_amended.tsv")
        shutil.copy(pathlib.Path(t) / "ancient_cells.tsv", HERE / "ancient_cells_amended.tsv")
    S = locked_load()
    with open(HERE / "sets_amended.tsv", "a") as f:
        for panel, pipe in (("A", "SGDP"), ("B", "NYGC")):
            for s in S:
                if s["group"] == "Mandenka" and B.pipeline(s) == pipe and s["assess"] in B.PASS:
                    f.write("\t".join(str(v) for v in (f"{panel}.Mandenka", s["row"], s["gid"], s["iid"], s["group"], int(s["date"]),
                                                       s["entity"], s["lat"], s["lon"], "", s["dtype"], s["nsnp"], s["assess"])) + "\n")
    print("removed from the ancient sets:")
    for r in sorted(set(removed)):
        print("  ", *r)


if __name__ == "__main__":
    main()
