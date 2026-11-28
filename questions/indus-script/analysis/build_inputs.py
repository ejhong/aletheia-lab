#!/usr/bin/env python3
"""Turn the list-builders' files into the contest's input files. Mechanical; no judgement.

usage:
  build_inputs.py parts   LANG     write lists/LANG/parts.jsonl, the file the labeler is given
  build_inputs.py samples LANG     write lists/LANG/samples.json, the 50 + 50 items the checker is given
  build_inputs.py verdicts LANG    read lists/LANG/verdicts.json and apply the plan's check
  build_inputs.py inputs  LANG     write inputs/LANG/{names.jsonl, parts.jsonl, words.json, cfg.json}
                                   (add --accept-size for a list that is still short after one rebuild)

Reads lists/LANG/names.jsonl, words.json, numbers.json (and labels.jsonl for "inputs") and
prompts/languages.json. Spelling: each language's fixed letter map (prompts/languages.json) is applied to
name parts, picture words and number words alike, so that every letter is one the contest's sound table knows.
"inputs" stops with an error if any letter is still outside the table.
"""
import collections
import json
import os
import random
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import contest  # noqa: E402

# Stability value by category, as the preprint set it for REP-1 (inputs/category_stability.json in its archive).
STABILITY = {"occupation_group": 2, "grammar_suffix": 3, "place_name": 2, "dynasty_clan": 2, "quality_size": 2,
             "landscape": 3, "celestial": 1, "kinship": 3, "honorific": 3, "animal": 2, "title_rank": 3,
             "verb_deed": 2, "deity": 1, "personal_name": 1, "place_word": 3, "artefact": 2, "body_part": 2,
             "direction": 3, "plant": 2, "other": 1, "colour": 2, "number": 3}
SAMPLE_SEED = 20261127
NAMES_USED = 600   # a new list longer than this is cut to this many names, once, at random
MIN_NAMES = 550    # a new list shorter than this is built again


def settings(lang):
    with open(os.path.join(ROOT, "prompts", "languages.json"), encoding="utf-8") as f:
        return json.load(f)[lang]


def respell(word, rules):
    """Lowercase, NFC, then the language's letter map in order."""
    w = unicodedata.normalize("NFC", word.lower())
    for old, new in rules:
        w = w.replace(old, new)
    return w


def unknown_letters(word):
    """Letters of a normalised word that the contest's sound table would drop."""
    s, i, out = contest.norm(word), 0, []
    while i < len(s):
        for p in contest.PHONEMES:
            if s.startswith(p, i):
                i += len(p)
                break
        else:
            out.append(s[i])
            i += 1
    return out


def read_names(lang):
    rows, seen = [], set()
    for r in contest.read_jsonl(os.path.join(ROOT, "lists", lang, "names.jsonl")):
        parts = r.get("morphemes", [])
        if isinstance(parts, str):  # amendment 2: members written as one string joined by " + "
            parts = parts.split(" + ")
        parts = [m.strip() for m in parts if m and m.strip()]
        key = tuple(m.lower() for m in parts)
        if not parts or key in seen:
            continue
        seen.add(key)
        glosses = [g.strip() for g in str(r.get("gloss", "")).split(" + ")]
        if len(glosses) != len(parts):
            glosses = glosses + [""] * len(parts)
        rows.append({"name": r.get("name", ""), "type": r.get("type", ""), "morphemes": parts,
                     "glosses": glosses[:len(parts)], "source": r.get("source", "")})
    return rows


def part_table(names):
    """Each different part with its commonest gloss and the number of names it is in."""
    gloss = collections.defaultdict(collections.Counter)
    count = collections.Counter()
    for n in names:
        for m, g in zip(n["morphemes"], n["glosses"]):
            gloss[m.lower()][g] += 1
        for m in {m.lower() for m in n["morphemes"]}:
            count[m] += 1
    return [{"part": m, "gloss": gloss[m].most_common(1)[0][0], "in_names": count[m]} for m in sorted(count)]


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("parts", "samples", "verdicts", "inputs"):
        sys.exit(__doc__)
    step, lang = sys.argv[1], sys.argv[2]
    if step == "verdicts":
        v = load_json(os.path.join(ROOT, "lists", lang, "verdicts.json"))
        for key, label in (("A", "names"), ("B", "words")):
            c = collections.Counter(str(x.get("verdict", "")).strip().lower() for x in v[key])
            ok, wrong = c.get("ok", 0), c.get("wrong", 0)
            failed = wrong > 5 or ok < 40
            print(lang, label, "ok", ok, "wrong", wrong, "cannot verify", len(v[key]) - ok - wrong,
                  "of", len(v[key]), "->", "FAILS the check" if failed else "passes the check")
        return
    rules = settings(lang)["spelling_map"]
    lists = os.path.join(ROOT, "lists", lang)
    names = read_names(lang)
    if step == "parts":
        write_jsonl(os.path.join(lists, "parts.jsonl"), part_table(names))
        print(lang, "names:", len(names), "different parts:", len(part_table(names)))
        return
    words = load_json(os.path.join(lists, "words.json"))
    if step == "samples":
        rng = random.Random(SAMPLE_SEED)
        raw = contest.read_jsonl(os.path.join(lists, "names.jsonl"))
        pairs = sorted((e, w) for e, ws in words.items() for w in ws)
        out = {"A_names": rng.sample(raw, min(50, len(raw))),
               "B_words": [{"english": e, "word": w} for e, w in rng.sample(pairs, min(50, len(pairs)))]}
        with open(os.path.join(lists, "samples.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print(lang, "sampled", len(out["A_names"]), "names and", len(out["B_words"]), "word pairs")
        return
    # step == "inputs"
    people = sum(1 for n in names if n["type"] == "person") / max(1, len(names))
    if len(names) < MIN_NAMES and "--accept-size" not in sys.argv:
        sys.exit(f"{lang}: only {len(names)} different names; the plan asks for {MIN_NAMES} or more")
    if not 0.35 <= people <= 0.60:
        sys.exit(f"{lang}: people are {people:.0%} of the list; the plan asks for 35% to 60%")
    if len(names) > NAMES_USED:  # every new list enters the contest at the same size
        keep = set(random.Random(SAMPLE_SEED).sample(range(len(names)), NAMES_USED))
        names = [n for i, n in enumerate(names) if i in keep]
    labels = {r["part"].lower(): r["category"] for r in contest.read_jsonl(os.path.join(lists, "labels.jsonl"))}
    numbers = load_json(os.path.join(lists, "numbers.json"))
    by_sign = load_json(os.path.join(ROOT, "inputs", "sign_english_words.json"))
    missing = [e for ws in by_sign.values() for e in ws if e not in words]
    if missing:
        sys.exit(f"{lang}: English entries missing from words.json: {sorted(set(missing))[:10]}")
    out_dir = os.path.join(ROOT, "inputs", lang)
    parts_out, bad, unlabeled = {}, collections.Counter(), []
    for p in part_table(names):
        m = respell(p["part"], rules)
        cat = labels.get(p["part"])
        if cat not in STABILITY:
            unlabeled.append(p["part"])
            cat = "other"
        for ch in unknown_letters(m):
            bad[ch] += 1
        parts_out.setdefault(contest.norm(m), {"m": m, "category": cat, "stability": STABILITY[cat],
                                               "gloss": p["gloss"], "in_names": p["in_names"]})
    names_out = [{"name": n["name"], "type": n["type"], "morphemes": [respell(m, rules) for m in n["morphemes"]],
                  "source": n["source"], "weight": 1} for n in names]
    words_out = {sign: {e: [respell(w, rules) for w in words[e]] for e in english}
                 for sign, english in by_sign.items()}
    numbers_out = {k: respell(v, rules) for k, v in numbers.items()}
    for w in [w for d in words_out.values() for ws in d.values() for w in ws] + list(numbers_out.values()):
        for ch in unknown_letters(w):
            bad[ch] += 1
    if bad:
        sys.exit(f"{lang}: letters outside the contest's sound table after the letter map: {dict(bad)}")
    if len(unlabeled) > 0.02 * len(parts_out):
        sys.exit(f"{lang}: {len(unlabeled)} parts have no valid label, e.g. {unlabeled[:10]}")
    write_jsonl(os.path.join(out_dir, "names.jsonl"), names_out)
    write_jsonl(os.path.join(out_dir, "parts.jsonl"), list(parts_out.values()))
    with open(os.path.join(out_dir, "words.json"), "w", encoding="utf-8") as f:
        json.dump(words_out, f, ensure_ascii=False, indent=1)
    cfg = {"lang": lang, "names": "names.jsonl", "parts": "parts.jsonl", "words": "words.json",
           "number_words": numbers_out, "punmax": 0.5, "weights": "once",
           "drop_parts": [], "loan_category": "none"}
    with open(os.path.join(out_dir, "cfg.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=1)
    filled = sum(1 for e in {e for ws in by_sign.values() for e in ws} if words[e])
    single = sum(1 for n in names_out if len(n["morphemes"]) == 1) / len(names_out)
    print(lang, "names used:", len(names_out), "people:", f"{people:.0%}", "names of one part:", f"{single:.0%}",
          "parts:", len(parts_out), "parts with no valid label (set to 'other'):", len(unlabeled),
          "English picture words filled:", filled, "of 171")


if __name__ == "__main__":
    main()
