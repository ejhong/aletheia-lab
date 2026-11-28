#!/usr/bin/env python3
"""EXPLORATORY. Where does the preprint's Tamil score come from?

Uses only the preprint's archived Tamil lists (REP-1 headline settings, seeds 0 to 9) and the lab's
contest program. Nothing here is evidence about any control language; it was run before the plan was
locked, to decide what the plan should test.

usage: where_score_comes_from.py ARCHIVE_REP1_DIR CORPUS_CSV OUT.json [processes]
"""
import collections
import copy
import json
import multiprocessing
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "analysis"))
import contest  # noqa: E402

ARCH, CORPUS, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3]
PROCS = int(sys.argv[4]) if len(sys.argv) > 4 else 6
BASE = os.path.join(ARCH, "inputs")
with open(os.path.join(BASE, "cfg_headline_tamil.json"), encoding="utf-8") as f:
    CFG = json.load(f)
SEEDS = range(10)


def one(job):
    name, cfg, base, drop, seed = job
    real = contest.run(cfg, base, seed, "real", corpus_csv=CORPUS, drop_signs=drop)
    null = contest.run(cfg, base, seed, "null", corpus_csv=CORPUS, drop_signs=drop)
    return name, seed, real["heldout"] - null["heldout"], real["readings"], real["read"]


def variant_dir(tmp, parts_edit=None, names_edit=None):
    """Write an edited copy of the Tamil parts or names file and return settings that point at it."""
    cfg = copy.deepcopy(CFG)
    parts = contest.read_jsonl(os.path.join(BASE, CFG["parts"]))
    names = contest.read_jsonl(os.path.join(BASE, CFG["names"]))
    if parts_edit:
        parts = [parts_edit(dict(p)) for p in parts]
    if names_edit:
        names = [n for n in (names_edit(dict(n), {contest.norm(p["m"]): p for p in parts}) for n in names) if n]
    os.makedirs(tmp, exist_ok=True)
    for key, rows in (("parts", parts), ("names", names)):
        p = os.path.join(tmp, key + ".jsonl")
        with open(p, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        cfg[key] = p
    cfg["words"] = os.path.join(BASE, CFG["words"])
    return cfg


def flat_labels(p):
    if p.get("category") != "sanskrit_loan":
        p["category"], p["stability"] = "other", 2
    return p


def no_suffix_parts(n, info):
    n["morphemes"] = [m for m in n["morphemes"]
                      if (info.get(contest.norm(m)) or {}).get("category") not in ("grammar_suffix", "honorific")]
    return n if n["morphemes"] else None


def whole_names(n, info):
    n["morphemes"] = ["".join(n["morphemes"])]
    return n


def main():
    tmp = tempfile.mkdtemp(prefix="indus_explore_")
    jobs = [("baseline", CFG, BASE, (), s) for s in SEEDS]
    probe = contest.run(CFG, BASE, 0, "real", corpus_csv=CORPUS)
    _, _, words, _ = contest.load_language(CFG, BASE)
    texts = contest.load_seal_texts(CORPUS)
    freq = collections.Counter(x for t in texts for x in t)
    signs = sorted(words, key=lambda s: -freq[s])
    for s in signs:
        jobs += [("drop " + s, CFG, BASE, (s,), seed) for seed in SEEDS]
    variants = {
        "labels flattened (every part 'other')": variant_dir(os.path.join(tmp, "flat"), parts_edit=flat_labels),
        "suffix and honorific parts removed from names": variant_dir(os.path.join(tmp, "nosuf"), names_edit=no_suffix_parts),
        "names left whole (not split into parts)": variant_dir(os.path.join(tmp, "whole"), names_edit=whole_names),
    }
    for name, cfg in variants.items():
        jobs += [(name, cfg, BASE, (), s) for s in SEEDS]
    with multiprocessing.Pool(PROCS) as pool:
        done = pool.map(one, jobs, chunksize=4)
    by = collections.defaultdict(list)
    chosen = collections.defaultdict(collections.Counter)
    for name, seed, d, readings, nread in done:
        by[name].append(d)
        if name == "baseline":
            for sign, word in readings.items():
                chosen[sign][word] += 1
    base_mean = sum(by["baseline"]) / len(by["baseline"])
    table = {}
    for name, ds in by.items():
        table[name] = {"mean": round(sum(ds) / len(ds), 1), "seeds_above_control": sum(d > 0 for d in ds),
                       "change_from_baseline": round(sum(ds) / len(ds) - base_mean, 1)}
    drops = sorted(((v["change_from_baseline"], k) for k, v in table.items() if k.startswith("drop ")))
    out = {"note": "EXPLORATORY, run before the plan was locked; the preprint's archived Tamil lists only",
           "baseline": table["baseline"], "variants": {k: table[k] for k in variants},
           "largest_falls_when_one_sign_is_left_unread": [
               {"sign": k[5:], "occurrences_in_seal_texts": freq[k[5:]], **table[k],
                "readings_chosen_in_baseline": dict(chosen[k[5:]])} for _, k in drops[:15]],
           "largest_rises": [{"sign": k[5:], **table[k]} for _, k in drops[-5:]],
           "signs_with_picture_words": len(signs), "example_run": {k: probe[k] for k in ("seals", "signs", "read")}}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
