#!/usr/bin/env python3
"""Amendment 2 (revised): rerun the locked scan with neighbours for people of data type "other".

    .venv/bin/python analysis/corrected_run.py          # run from questions/strangers; writes results/corrected/

Uses the locked scan.py unchanged. Only the people list (people_amended.tsv: the locked list plus the missing
neighbour pools) and the output folders differ.
"""
import csv
import pathlib
import subprocess
import sys

import amend2
import scan

HERE = pathlib.Path(__file__).resolve().parent
Q = HERE.parent
CACHE2 = Q / "data" / "cache" / "strangers_real_corrected"


def write_people():
    people = scan.load_people()
    extra = amend2.pools(people)
    rows = list(csv.DictReader(open(HERE / "people.tsv"), delimiter="\t"))
    cols = list(rows[0].keys())
    with open(HERE / "people_amended.tsv", "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            if int(r["row"]) in extra:
                assert not r["pool"]
                r["pool"] = ",".join(map(str, extra[int(r["row"])]))
            f.write("\t".join(r[c] for c in cols) + "\n")
    return len(extra)


def patch():
    def load_people():
        people = []
        with open(HERE / "people_amended.tsv") as f:
            for p in csv.DictReader(f, delimiter="\t"):
                p["row"], p["nsnp"], p["date"] = int(p["row"]), int(p["nsnp"]), float(p["date"])
                p["date_sd"] = float(p["date_sd"]) if p["date_sd"] not in ("", "None") else None
                p["pool"] = [int(x) for x in p["pool"].split(",")] if p["pool"] else []
                people.append(p)
        return people
    scan.load_people = load_people
    CACHE2.mkdir(parents=True, exist_ok=True)
    for name in ("geno.u8", "refs.npz", "meta.json"):
        if not (CACHE2 / name).exists():
            (CACHE2 / name).symlink_to(scan.CACHE / name)
    scan.CACHE = CACHE2
    scan.OUT = Q / "results" / "corrected"


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "work":
        patch()
        scan.work(int(sys.argv[2]), int(sys.argv[3]))
        return
    print("people given neighbours by the amendment:", write_people())
    patch()
    n = 12
    procs = [subprocess.Popen([sys.executable, __file__, "work", str(i), str(n)], stdout=subprocess.DEVNULL) for i in range(n)]
    assert all(p.wait() == 0 for p in procs), "a worker failed"
    scan.final()


if __name__ == "__main__":
    main()
