#!/usr/bin/env python3
"""EXPLORATORY, after the results. The same program as the locked run, with the three dropped lists put back.

The plan dropped Finnish and both fresh Old Tamil lists because their picture words failed the check twice.
This runs analysis/run_all.py unchanged on all ten new lists, so that the dropped ones can be seen beside the
rest. It was decided on after the checks failed and before any contest was run, and it is run after the locked
results exist. Nothing it prints is the plan's answer. The "answers" it computes use the plan's rules on lists
the plan excluded.

usage: with_dropped_lists.py ARCHIVE_UNZIPPED_DIR CORPUS_CSV OUT.json [processes]
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
Q = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(Q, "analysis"))
import run_all  # noqa: E402


def main():
    arch, corpus, out = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
    tmp = tempfile.mkdtemp(prefix="indus_explore_all_")
    shutil.copytree(os.path.join(Q, "inputs"), os.path.join(tmp, "inputs"))
    for name in sorted(os.listdir(os.path.join(Q, "inputs_dropped"))):
        shutil.copytree(os.path.join(Q, "inputs_dropped", name), os.path.join(tmp, "inputs", name))
    run_all.ROOT = tmp
    sys.argv = ["run_all.py", arch, corpus] + sys.argv[4:]
    run_all.main()
    with open(os.path.join(tmp, "results", "contest_summary.json"), encoding="utf-8") as f:
        d = json.load(f)
    for v in d["lists"].values():
        v.pop("readings_chosen", None)
    d["note"] = ("EXPLORATORY: the locked program run with the three dropped lists (finnish, tamil_fresh_a, "
                 "tamil_fresh_b) put back. Not the plan's answer.")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
