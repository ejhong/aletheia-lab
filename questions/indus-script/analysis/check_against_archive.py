#!/usr/bin/env python3
"""Compare the lab's contest program with the per-seed outputs archived by the preprint.

usage: check_against_archive.py ARCHIVE_TEST_DIR CORPUS_CSV OUT.json
  ARCHIVE_TEST_DIR: the unpacked REP-1_tamil_vs_sanskrit folder of tests_archive.zip (read as data only)
  CORPUS_CSV:       inscriptions.csv from yajnadevam/lipi at the pinned commit

For every archived output file of the headline run (Tamil and Sanskrit, real and null, seeds 0 to 9)
the same run is made here and every field is compared.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contest  # noqa: E402

arch, corpus, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
rows, bad = [], 0
for lang in ("tamil", "sanskrit"):
    cfg_path = os.path.join(arch, "inputs", f"cfg_headline_{lang}.json")
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    for mode in ("real", "null"):
        for seed in range(10):
            with open(os.path.join(arch, "outputs", "headline", f"{lang}_{mode}_{seed}.json"), encoding="utf-8") as f:
                theirs = json.load(f)
            ours = contest.run(cfg, os.path.dirname(cfg_path), seed, mode, corpus_csv=corpus)
            diffs = [k for k in ours if ours[k] != theirs.get(k)]
            bad += bool(diffs)
            rows.append({"lang": lang, "mode": mode, "seed": seed, "ours": ours["heldout"],
                         "archive": theirs["heldout"], "fields_that_differ": diffs})
            print(lang, mode, seed, ours["heldout"], theirs["heldout"], "SAME" if not diffs else f"DIFFERS {diffs}")
summary = {}
for lang in ("tamil", "sanskrit"):
    real = {r["seed"]: r["ours"] for r in rows if r["lang"] == lang and r["mode"] == "real"}
    null = {r["seed"]: r["ours"] for r in rows if r["lang"] == lang and r["mode"] == "null"}
    d = [real[s] - null[s] for s in range(10)]
    summary[lang] = {"real_minus_null_by_seed": [round(x, 2) for x in d], "mean": round(sum(d) / 10, 1),
                     "seeds_above_control": sum(x > 0 for x in d)}
print(json.dumps(summary, indent=1))
print(f"{len(rows) - bad} of {len(rows)} runs identical to the archive")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"runs": rows, "summary": summary, "identical": len(rows) - bad, "total": len(rows)}, f, indent=1)
