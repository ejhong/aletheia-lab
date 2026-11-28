#!/usr/bin/env python3
"""The preprint's language contest, written out again by the lab.

Source of the method: Siva Raj with Claude, "Indus Script Read as Early Dravidian, with AI
Assistance", v0.7 (doi:10.5281/zenodo.24383779, CC BY 4.0), test REP-1, files contest.py,
decoder.py and nphon.py in tests_archive.zip. The lab does not run downloaded programs, so the
procedure is written out here from a line-by-line reading of those files. It follows them step
for step, including the random seeds and the tables of sound costs, so that its output can be
compared number for number with the per-seed outputs the preprint archived. Any difference from
the archive is a fault in this file.

What one run does (one language, one seed, one mode):
  1. Seal texts are read from the public corpus file and reduced to the common picture signs.
  2. The seals are split in two halves at random, and so are the names.
  3. On seal half 1 with name half A, each sign may take a name part that sounds like one of
     its picture words; the choice that most raises the fit to names is kept.
  4. The chosen readings are scored on seal half 2 with name half B.
  mode "real" uses the names as they are; mode "null" first shuffles the name parts among the
  names. The preprint's score for a language is real minus null.

usage: contest.py CONFIG.json SEED real|null OUTDIR
       (or import run() from another program)
"""
import collections
import csv
import json
import math
import os
import random
import re
import statistics
import sys
import unicodedata
from functools import lru_cache

# ---------------------------------------------------------------- spelling and sound costs
# (the preprint's nphon.py: one neutral spelling and one cost table for every language)


def norm(s):
    s = unicodedata.normalize("NFC", s.lower())
    return re.sub(r"[\s\-’'’;:,.()\[\]?/*0-9]", "", s)


PHONEMES = ["kh", "gh", "ch", "jh", "ṭh", "ḍh", "th", "dh", "ph", "bh", "ai", "au",
            "ā", "ī", "ū", "ē", "ō", "ṛ", "ṝ", "ṅ", "ñ", "ṇ", "ṉ", "ṟ", "ḻ", "ḷ", "ṭ", "ḍ", "ṃ", "ḥ", "ś", "ṣ",
            "a", "i", "u", "e", "o", "k", "g", "c", "j", "t", "d", "p", "b", "n", "m", "y", "r", "l", "v", "h", "s"]
VOWELS = {"a", "ā", "i", "ī", "u", "ū", "e", "ē", "o", "ō", "ai", "au", "ṛ", "ṝ"}


def phonemes(s):
    """Split a normalised word into the sounds of the table; a character not in the table is dropped."""
    s = norm(s)
    out, i = [], 0
    while i < len(s):
        for p in PHONEMES:
            if s.startswith(p, i):
                out.append(p)
                i += len(p)
                break
        else:
            i += 1
    return out


NEAR = {}


def _near(pairs, cost):
    for a, b in pairs:
        NEAR[(a, b)] = cost
        NEAR[(b, a)] = cost


_near([("l", "ḷ"), ("ḷ", "ḻ"), ("r", "ṟ")], 0.35)
_near([("l", "ḻ")], 0.5)
_near([("n", "ṇ"), ("n", "ṉ"), ("ṇ", "ṉ"), ("n", "ñ"), ("m", "ṃ"), ("n", "ṃ"), ("n", "ṅ")], 0.2)
_near([("a", "ā"), ("i", "ī"), ("u", "ū"), ("e", "ē"), ("o", "ō"), ("ṛ", "ṝ")], 0.3)
_near([("t", "ṭ"), ("ṭ", "ṟ"), ("r", "l"), ("d", "ḍ")], 0.6)
_near([("e", "i"), ("o", "u"), ("a", "ai"), ("a", "au"), ("ai", "e"), ("au", "o")], 0.5)
_near([("k", "g"), ("c", "j"), ("ṭ", "ḍ"), ("t", "d"), ("p", "b")], 0.3)
_near([(a, a + "h") for a in ["k", "g", "c", "j", "ṭ", "ḍ", "t", "d", "p", "b"]], 0.2)
_near([("k", "gh"), ("g", "kh"), ("c", "jh"), ("j", "ch"), ("ṭ", "ḍh"), ("ḍ", "ṭh"), ("t", "dh"), ("d", "th"),
       ("p", "bh"), ("b", "ph")], 0.45)
_near([("kh", "gh"), ("ch", "jh"), ("ṭh", "ḍh"), ("th", "dh"), ("ph", "bh")], 0.3)
_near([("s", "ś"), ("s", "ṣ"), ("ś", "ṣ")], 0.3)
_near([("c", "s"), ("c", "ś")], 0.5)
_near([("ṛ", "r"), ("ṛ", "i"), ("ṛ", "u")], 0.4)
_near([("ṛ", "a")], 0.5)
_near([("h", "ḥ")], 0.2)
_near([("v", "b")], 0.6)


def sub_cost(a, b):
    if a == b:
        return 0.0
    if (a, b) in NEAR:
        return NEAR[(a, b)]
    return 1.0 if (a in VOWELS) == (b in VOWELS) else 1.4


def indel_cost(p):
    return 0.6 if p in VOWELS else (0.4 if p in ("ḥ", "h") else 1.0)


def distance(x, y):
    a, b = phonemes(x), phonemes(y)
    n, m = len(a), len(b)
    d = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        d[i][0] = d[i - 1][0] + indel_cost(a[i - 1])
    for j in range(1, m + 1):
        d[0][j] = d[0][j - 1] + indel_cost(b[j - 1])
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i - 1][j] + indel_cost(a[i - 1]), d[i][j - 1] + indel_cost(b[j - 1]),
                          d[i - 1][j - 1] + sub_cost(a[i - 1], b[j - 1]))
    return d[n][m]


def stem(w):
    w = norm(w)
    for suf in ("am", "aḥ", "as", "ai", "au", "a", "ā", "i", "ī", "u", "ū", "e", "ē", "o", "ō", "ṛ"):
        if len(w) > 3 and w.endswith(suf):
            return w[:-len(suf)]
    return w


@lru_cache(maxsize=None)
def pun_cost(target, picture_word):
    """How far a picture word must stretch to sound like a name part (0 = the same word)."""
    return min(distance(target, picture_word), distance(stem(target), stem(picture_word)) + 0.2)


# ---------------------------------------------------------------- the model of names
# (the preprint's decoder.NameModel: word pairs mixed with category pairs and word frequency)

START, END, GAP = "<s>", "</s>", "GAP"


class NameModel:
    def __init__(self, names, info, mix=(0.45, 0.4, 0.15), break_p=0.3):
        self.info = info
        self.l1, self.l2, self.l3 = mix
        self.break_p = break_p
        wb, wu, cb, cu = (collections.Counter() for _ in range(4))
        mc = collections.defaultdict(collections.Counter)
        for parts, weight in names:
            w = math.log1p(weight)
            seq = [START] + parts + [END]
            for a, b in zip(seq, seq[1:]):
                wb[(a, b)] += w
                wu[a] += w
                ca, cbb = self._cat_or_edge(a), self._cat_or_edge(b)
                cb[(ca, cbb)] += w
                cu[ca] += w
            for m in parts:
                mc[self.cat(m)][m] += w
        self.wb, self.wu, self.cb, self.cu, self.mc = wb, wu, cb, cu, mc
        self.mc_tot = {c: sum(v.values()) for c, v in mc.items()}
        self.vocab = set(m for c in mc.values() for m in c)
        self.uni = collections.Counter()
        for v in mc.values():
            self.uni.update(v)
        self.uni_tot = sum(self.uni.values())
        self.ncat = len(mc) + 2
        self.lp = lru_cache(maxsize=None)(self._logp)

    def cat(self, m):
        return (self.info.get(m) or {}).get("category", "other")

    def stab(self, m):
        return (self.info.get(m) or {}).get("stability", 2)

    def _cat_or_edge(self, x):
        return x if x in (START, END) else self.cat(x)

    def _p_in_cat(self, m, c):
        cnt = self.mc.get(c, {})
        tot = self.mc_tot.get(c, 0)
        n = max(1, len(cnt))
        emp = (cnt.get(m, 0) + 0.5) / (tot + 0.5 * (n + 1))
        flat = 1.0 / (n + 1)
        a = {3: 0.9, 2: 0.7, 1: 0.3}.get(self.stab(m), 0.7)
        return a * emp + (1 - a) * flat

    def _freq(self, b):
        return (self.uni.get(b, 0) + 0.5) / (self.uni_tot + 0.5 * len(self.vocab))

    def _mixed(self, a, b):
        pw = self.wb.get((a, b), 0) / self.wu[a] if self.wu.get(a) else 0.0
        ca, cbb = self._cat_or_edge(a), self._cat_or_edge(b)
        pc = (self.cb.get((ca, cbb), 0) + 0.1) / (self.cu.get(ca, 0) + 0.1 * self.ncat)
        pm = 1.0 if b == END else self._p_in_cat(b, cbb)
        pu = 1.0 / 50 if b == END else self._freq(b)
        return self.l1 * pw + self.l2 * pc * pm + self.l3 * pu

    def _logp(self, a, b):
        if b == GAP:
            return 0.0
        if a == GAP:
            return math.log(0.3) if b == END else math.log(self._freq(b))
        p = self._mixed(a, b)
        if a != START and b != END:  # a seal may hold more than one name: allow a boundary here
            p = (1 - self.break_p) * p + self.break_p * math.exp(
                math.log(self._mixed(a, END) + 1e-12) + math.log(self._mixed(START, b) + 1e-12))
        return math.log(p + 1e-12)


# ---------------------------------------------------------------- one run of the contest

NUMBER_SIGNS = {"032": 2, "033": 3, "031": 1, "001": 1, "003": 3, "017": 7, "004": 4, "055": 12, "005": 5,
                "013": 3, "016": 6}


def load_seal_texts(corpus_csv):
    """Distinct seal texts of two or more signs with a recorded direction and no damage marks."""
    seen, texts = set(), []
    with open(corpus_csv, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t = r["text"].strip()
            ss = [s for s in re.findall(r"\d{3}", t) if s != "999"]
            if (not ss or "[" in t or "]" in t or "/" in t or r["dir."] not in ("R/L", "L/R") or "000" in ss
                    or len(ss) < 2 or not r["type"].startswith("SEAL") or tuple(ss) in seen):
                continue
            seen.add(tuple(ss))
            texts.append(ss[::-1])
    return texts


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def scramble(names, seed):
    """The same name parts, dealt out again at random into names of the same lengths."""
    pool = [m for parts, _ in names for m in parts]
    random.Random(seed).shuffle(pool)
    it = iter(pool)
    return [([next(it) for _ in parts], w) for parts, w in names]


def load_language(cfg, base):
    """Names, name-part labels, picture words and number words for one language."""
    def path(key):
        return os.path.join(base, cfg[key])

    info, loans = {}, set(cfg.get("drop_parts", []))
    for x in read_jsonl(path("parts")):
        if x.get("category") == cfg.get("loan_category", "sanskrit_loan"):
            loans.add(norm(x["m"]))
        info[norm(x["m"])] = x
    keep_noninitial = set(cfg.get("keep_noninitial", []))

    def clean(ms):
        ms = [norm(m) for m in ms if m]
        return [m for i, m in enumerate(ms) if m and not (m in loans and not (m in keep_noninitial and i > 0))]

    named = []
    for n in read_jsonl(path("names")):
        ms = clean(n["morphemes"])
        if ms:
            named.append((ms, n.get("weight", 1) if cfg.get("weights", "stored") == "stored" else 1))
    words = collections.defaultdict(set)
    with open(path("words"), encoding="utf-8") as f:
        for sign, by_english in json.load(f).items():
            for ws in by_english.values():
                words[sign] |= {norm(w) for w in ws}
    for s in NUMBER_SIGNS:
        words.pop(s, None)
    number_words = {int(k): v for k, v in cfg["number_words"].items()}
    return named, info, words, number_words


def run(cfg, base, seed, mode, corpus_csv=None, drop_signs=(), picture_shuffle=None):
    """One run. Returns the result as a dict.

    drop_signs: signs treated as unread throughout (used only for the lab's own side analyses).
    picture_shuffle: if a number k is given, the signs' sets of picture words are dealt out again among the
        same signs with random.Random(600000 + k), so that each sign carries another sign's pictures.
    If the settings give "sample_n" and the list has more names, the list is first sampled down to
    that many with random.Random(100 + seed), as in the preprint's REP-2 and REP-3.
    """
    texts = load_seal_texts(corpus_csv or os.path.join(base, cfg["corpus"]))
    named, info, words, number_words = load_language(cfg, base)
    for s in drop_signs:
        words.pop(s, None)
    if picture_shuffle is not None:
        keys = sorted(words)
        sets = [words[k] for k in keys]
        random.Random(600000 + picture_shuffle).shuffle(sets)
        words = collections.defaultdict(set, zip(keys, sets))
    if cfg.get("sample_n") and len(named) > cfg["sample_n"]:
        named = random.Random(100 + seed).sample(named, cfg["sample_n"])
    fixed = {s: number_words[v] for s, v in NUMBER_SIGNS.items()}
    top = set(words) | set(NUMBER_SIGNS)
    corpus = [[x if x in top else GAP for x in t] for t in texts]
    seals = [t for t in corpus if t.count(GAP) <= 1 and len(t) - t.count(GAP) >= 2]
    order = list(range(len(seals)))
    random.Random(800 + seed).shuffle(order)
    half1 = [seals[i] for i in order[:len(order) // 2]]
    half2 = [seals[i] for i in order[len(order) // 2:]]

    full = scramble(named, 7000 + seed) if mode == "null" else named
    idx = list(range(len(full)))
    random.Random(500 + seed).shuffle(idx)
    names_a = [full[i] for i in idx[:len(idx) // 2]]
    names_b = [full[i] for i in idx[len(idx) // 2:]]
    # each half's model is always judged against eight scrambled copies of the same half
    models_a = [NameModel(names_a, info)] + [NameModel(scramble(names_a, 3000 + i), info) for i in range(8)]
    models_b = [NameModel(names_b, info)] + [NameModel(scramble(names_b, 4000 + i), info) for i in range(8)]

    counts = collections.Counter(m for parts, _ in full for m in parts)
    parts_pool = sorted(m for m, c in counts.items() if len(m) >= 2 and c >= 2 and m not in fixed.values())
    signs = sorted(s for s in words if any(s in t for t in seals))
    pool_set = set(parts_pool)
    punmax = float(cfg.get("punmax", 0.5))
    options = {}
    for s in signs:
        c = set()
        for w in words[s]:
            if w in pool_set:
                c.add(w)
            for m in parts_pool:
                if abs(len(m) - len(w)) <= 3 and m[:1] == w[:1] and pun_cost(m, w) <= punmax:
                    c.add(m)
        options[s] = sorted(c)

    sign_set = set(signs)

    def neighbours(half):
        table = collections.defaultdict(collections.Counter)
        for t in half:
            seq = [START] + t + [END]
            for a, b in zip(seq, seq[1:]):
                for s in {a, b} & sign_set:
                    table[s][(a, b)] += 1
        return table

    slots1 = neighbours(half1)
    occurrences = collections.Counter(x for t in half1 for x in t)

    def value(x, assign):
        return assign.get(x) or fixed.get(x) or (GAP if x not in (START, END) else x)

    def gain(s, m, assign):
        pairs = []
        for (left, right), n in slots1[s].items():
            l1 = m if left == s else value(left, assign)
            r1 = m if right == s else value(right, assign)
            l0 = GAP if left == s else value(left, assign)
            r0 = GAP if right == s else value(right, assign)
            pairs.append((n, l1, r1, l0, r0))
        out = [sum(n * (mm.lp(l1, r1) - mm.lp(l0, r0)) for n, l1, r1, l0, r0 in pairs) for mm in models_a]
        return out[0] - statistics.mean(out[1:])

    def score(assign, half, models):
        total = 0.0
        for t in half:
            seq = [START] + [value(x, assign) for x in t] + [END]
            v = [sum(mm.lp(p, q) for p, q in zip(seq, seq[1:])) for mm in models]
            total += v[0] - statistics.mean(v[1:])
        return total

    assign = {s: GAP for s in signs}
    for _ in range(2):
        for s in sorted(signs, key=lambda s: -occurrences[s]):
            used = {v for k, v in assign.items() if k != s and v != GAP}
            best, best_m = 0.0, GAP
            for m in options.get(s, []):
                if m in used:
                    continue
                g = gain(s, m, assign)
                if g > best:
                    best, best_m = g, m
            assign[s] = best_m
    readings = {s: v for s, v in assign.items() if v != GAP}
    heldout = score(assign, half2, models_b)
    return {"lang": cfg["lang"], "seed": seed, "mode": mode, "names": len(named), "name_parts": len(parts_pool),
            "seals": len(seals), "signs": len(signs),
            "pic_mean_opts": round(statistics.mean(len(v) for v in options.values()), 2) if options else 0.0,
            "signs_with_options": sum(1 for v in options.values() if v),
            "read": len(readings), "heldout": round(heldout, 2), "readings": readings}


def main():
    if len(sys.argv) != 5 or sys.argv[3] not in ("real", "null"):
        sys.exit(__doc__)
    cfg_path, seed, mode, outdir = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    res = run(cfg, os.path.dirname(os.path.abspath(cfg_path)), seed, mode)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, f"{cfg['lang']}_{mode}_{seed}.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print({k: v for k, v in res.items() if k != "readings"})


if __name__ == "__main__":
    main()
