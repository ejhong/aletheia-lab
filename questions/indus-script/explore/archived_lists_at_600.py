#!/usr/bin/env python3
"""EXPLORATORY. The preprint's own archived lists at the list size and number of rounds the lab's plan uses.

Run before the lock, on the preprint's lists only, to check that the planned design (600 names a round,
100 rounds) still sees the preprint's Tamil result. No control language built by the lab is touched.

usage: archived_lists_at_600.py ARCHIVE_UNZIPPED_DIR CORPUS_CSV OUT.json [processes]
"""
import json
import multiprocessing
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis"))
import contest  # noqa: E402

ARCH, CORPUS, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3]
PROCS = int(sys.argv[4]) if len(sys.argv) > 4 else 6
LISTS = {"tamil (preprint's list)": ("REP-1_tamil_vs_sanskrit/inputs", "cfg_headline_tamil.json"),
         "sanskrit (preprint's list)": ("REP-1_tamil_vs_sanskrit/inputs", "cfg_headline_sanskrit.json"),
         "akkadian (preprint's list)": ("REP-3_akkadian/inputs", "cfg_akkadian.json")}


def one(job):
    name, base, cfg, seed, drop = job
    real = contest.run(cfg, base, seed, "real", corpus_csv=CORPUS, drop_signs=drop)
    null = contest.run(cfg, base, seed, "null", corpus_csv=CORPUS, drop_signs=drop)
    return name, drop, real["heldout"] - null["heldout"], real["read"], real["pic_mean_opts"]


def main():
    jobs = []
    for name, (sub, cfg_name) in LISTS.items():
        base = os.path.join(ARCH, sub)
        with open(os.path.join(base, cfg_name), encoding="utf-8") as f:
            cfg = json.load(f)
        cfg["sample_n"] = 600
        for drop in ((), ("740",)):
            jobs += [(name, base, cfg, seed, drop) for seed in range(100)]
    with multiprocessing.Pool(PROCS) as pool:
        done = pool.map(one, jobs, chunksize=5)
    out = {"note": "EXPLORATORY, before the lock; the preprint's archived lists sampled to 600 names, rounds 0 to 99"}
    for name in LISTS:
        for drop in ((), ("740",)):
            d = [x[2] for x in done if x[0] == name and x[1] == drop]
            key = name + (" with sign 740 left unread" if drop else "")
            out[key] = {"mean": round(statistics.mean(d), 1), "sd": round(statistics.stdev(d), 1),
                        "standard_error": round(statistics.stdev(d) / len(d) ** 0.5, 1),
                        "rounds_above_control": sum(x > 0 for x in d), "rounds": len(d),
                        "first_ten_rounds_above_control": sum(x > 0 for x in d[:10]),
                        "signs_read_mean": round(statistics.mean(x[3] for x in done if x[0] == name and x[1] == drop), 1)}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
