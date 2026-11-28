#!/usr/bin/env python3
"""EXPLORATORY, after the results. The two fresh Old Tamil name lists with their FIRST translators' words.

Each fresh Tamil list had two translators (the first failed the word check). Of the four, only Tamil A's first
translator gave kuṭam for "pot"; the others gave kalam, tāḻi or pāṉai. The preprint's Tamil score rests on the
jar sign being read kuṭi through kuṭam. This runs the same name lists and labels with the first translators'
words, to see whether that one choice of word matters. Main analysis only (rounds 0 to 99), plus the jar sign
left unread.

usage: tamil_first_translators.py CORPUS_CSV OUT.json
"""
import json
import os
import shutil
import statistics
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
Q = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(Q, "analysis"))
import build_inputs  # noqa: E402
import contest  # noqa: E402

corpus, out_path = os.path.abspath(sys.argv[1]), sys.argv[2]
tmp = tempfile.mkdtemp(prefix="indus_first_words_")
shutil.copytree(os.path.join(Q, "prompts"), os.path.join(tmp, "prompts"))
os.makedirs(os.path.join(tmp, "inputs"))
shutil.copy(os.path.join(Q, "inputs", "sign_english_words.json"), os.path.join(tmp, "inputs"))
build_inputs.ROOT = tmp
out = {"note": "EXPLORATORY: fresh Tamil name lists with their first translators' picture words. Not the plan's answer."}
for lang in ("tamil_fresh_a", "tamil_fresh_b"):
    dst = os.path.join(tmp, "lists", lang)
    os.makedirs(dst)
    for f in ("names.jsonl", "labels.jsonl"):
        shutil.copy(os.path.join(Q, "lists", lang, f), dst)
    for f in ("words.json", "numbers.json"):
        shutil.copy(os.path.join(Q, "lists", lang, "first_build", f), dst)
    sys.argv = ["build_inputs.py", "inputs", lang]
    build_inputs.main()
    base = os.path.join(tmp, "inputs", lang)
    cfg = build_inputs.load_json(os.path.join(base, "cfg.json"))
    words = build_inputs.load_json(os.path.join(base, "words.json"))["740"]
    res = {"words_for_the_jar_sign": words}
    for label, drop in (("main", ()), ("jar sign left unread", ("740",))):
        d, jar = [], {}
        for seed in range(100):
            real = contest.run(cfg, base, seed, "real", corpus_csv=corpus, drop_signs=drop)
            null = contest.run(cfg, base, seed, "null", corpus_csv=corpus, drop_signs=drop)
            d.append(real["heldout"] - null["heldout"])
            w = real["readings"].get("740")
            if w:
                jar[w] = jar.get(w, 0) + 1
        res[label] = {"mean": round(statistics.mean(d), 1), "median": round(statistics.median(d), 1),
                      "runs_above_control": sum(x > 0 for x in d), "runs": len(d), "readings_for_jar_sign": jar}
    out[lang] = res
    print(lang, json.dumps(res, ensure_ascii=False))
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
