#!/usr/bin/env python3
"""EXPLORATORY, after the results. What is the jar sign read as when the pictures are shuffled?

The preprint's Tamil list keeps its score when each sign is given another sign's picture words. This counts,
over the same 20 shuffles of rounds 0 to 9, which name part the jar sign (740) is then given, and where that
part sits in names.

usage: jar_sign_when_shuffled.py ARCHIVE_UNZIPPED_DIR CORPUS_CSV OUT.json
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis"))
import build_inputs  # noqa: E402
import contest  # noqa: E402

arch, corpus, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3]
base = os.path.join(arch, "REP-1_tamil_vs_sanskrit", "inputs")
cfg = build_inputs.load_json(os.path.join(base, "cfg_headline_tamil.json"))
cfg["sample_n"] = 600
named = contest.load_language(cfg, base)[0]
final = collections.Counter(parts[-1] for parts, _ in named if len(parts) > 1)
total = collections.Counter(m for parts, _ in named for m in parts)
jar = collections.Counter()
runs = 0
for k in range(20):
    for seed in range(10):
        r = contest.run(cfg, base, seed, "real", corpus_csv=corpus, picture_shuffle=k)
        jar[r["readings"].get("740", "(unread)")] += 1
        runs += 1
res = {"note": "EXPLORATORY: the preprint's Tamil list, pictures shuffled; reading given to the jar sign",
       "runs": runs,
       "readings_for_jar_sign": [{"reading": w, "runs": n, "names_it_is_in": total.get(w, 0),
                                  "names_it_ends": final.get(w, 0)} for w, n in jar.most_common(12)],
       "commonest_name_endings_in_the_list": final.most_common(8)}
with open(out, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False))
