"""Independent replication of the Indus preprint language contest (REP-1).

Usage:
    python replicate.py SETTINGS.json CORPUS.csv FIRST_SEED LAST_SEED OUT.json

Ambiguity resolution choices (per analysis/METHOD.md and replication/FORMAT.md):
1. norm(s): applies unicodedata.normalize("NFC", s).lower() and deletes characters
   matching the exact regex [\\s\\-’'’;:,.()\\[\\]?/*0-9] given in Section 2.
2. Settings defaults/normalisation: drop_parts and keep_noninitial are normalised
   with norm(); punmax defaults to 0.5; weights defaults to "once" (missing name
   weight defaults to 1); loan_category defaults to "sanskrit_loan" and is
   disabled if explicitly null.
3. Empty strings after norm(): dropped from name morphemes and sign word sets;
   signs present in the words file with empty word sets remain in words and top.
4. Corpus CSV parsing: opened with encoding="utf-8-sig" to tolerate an optional
   UTF-8 BOM; dir. and type fields are stripped of surrounding whitespace along
   with text.
5. Repeated adjacent sign in slots[s]: when a bigram in half 1 has a == b and
   a in signs, (a, a) is incremented once in slots[a] (not twice), so gain(s, m)
   equals the exact log-likelihood change of half 1 when switching s from GAP to m.
6. Rounding: each run's heldout is rounded to 2 decimals; difference is
   round(real - null, 2) from the rounded heldout values; mean_difference is
   round(mean(differences), 2).
"""

from collections import Counter, defaultdict
import csv
from functools import lru_cache
import json
import math
from pathlib import Path
import random
import re
import sys
import unicodedata

NORM_RE = re.compile(r"[\s\-’'’;:,.()\[\]?/*0-9]")
DIGITS3_RE = re.compile(r"\d{3}")

TWO_CHAR_PHONEMES = frozenset("kh gh ch jh ṭh ḍh th dh ph bh ai au".split())
ONE_CHAR_PHONEMES = frozenset(
    "ā ī ū ē ō ṛ ṝ ṅ ñ ṇ ṉ ṟ ḻ ḷ ṭ ḍ ṃ ḥ ś ṣ "
    "a i u e o k g c j t d p b n m y r l v h s".split()
)
VOWELS = frozenset("a ā i ī u ū e ē o ō ai au ṛ ṝ".split())
STEM_ENDINGS = (
    "am", "aḥ", "as", "ai", "au",
    "a", "ā", "i", "ī", "u", "ū", "e", "ē", "o", "ō", "ṛ",
)
NUM_SIGN_VALUES = (
    ("032", "2"), ("033", "3"), ("031", "1"), ("001", "1"),
    ("003", "3"), ("017", "7"), ("004", "4"), ("055", "12"),
    ("005", "5"), ("013", "3"), ("016", "6"),
)
STAB_ALPHA = {3: 0.9, 2: 0.7, 1: 0.3}
LOG_BREAK = math.log(0.3)

_SUB_ROWS = (
    (0.35, "l-ḷ ḷ-ḻ r-ṟ"),
    (0.5,  "l-ḻ"),
    (0.2,  "n-ṇ n-ṉ ṇ-ṉ n-ñ m-ṃ n-ṃ n-ṅ"),
    (0.3,  "a-ā i-ī u-ū e-ē o-ō ṛ-ṝ"),
    (0.6,  "t-ṭ ṭ-ṟ r-l d-ḍ"),
    (0.5,  "e-i o-u a-ai a-au ai-e au-o"),
    (0.3,  "k-g c-j ṭ-ḍ t-d p-b"),
    (0.2,  "k-kh g-gh c-ch j-jh ṭ-ṭh ḍ-ḍh t-th d-dh p-ph b-bh"),
    (0.45, "k-gh g-kh c-jh j-ch ṭ-ḍh ḍ-ṭh t-dh d-th p-bh b-ph"),
    (0.3,  "kh-gh ch-jh ṭh-ḍh th-dh ph-bh"),
    (0.3,  "s-ś s-ṣ ś-ṣ"),
    (0.5,  "c-s c-ś"),
    (0.4,  "ṛ-r ṛ-i ṛ-u"),
    (0.5,  "ṛ-a"),
    (0.2,  "h-ḥ"),
    (0.6,  "v-b"),
)
SUB_COST: dict[tuple[str, str], float] = {}
for _cost, _pairs in _SUB_ROWS:
    for _pair in _pairs.split():
        _a, _b = _pair.split("-")
        SUB_COST[(_a, _b)] = _cost
        SUB_COST[(_b, _a)] = _cost


def norm(s: str) -> str:
    return NORM_RE.sub("", unicodedata.normalize("NFC", s).lower())


@lru_cache(maxsize=None)
def phonemes(s: str) -> tuple[str, ...]:
    t = norm(s)
    out: list[str] = []
    i = 0
    n = len(t)
    while i < n:
        if i + 2 <= n and t[i:i + 2] in TWO_CHAR_PHONEMES:
            out.append(t[i:i + 2])
            i += 2
        elif t[i] in ONE_CHAR_PHONEMES:
            out.append(t[i])
            i += 1
        else:
            i += 1
    return tuple(out)


def indel_cost(p: str) -> float:
    if p in VOWELS:
        return 0.6
    if p == "h" or p == "ḥ":
        return 0.4
    return 1.0


def sub_cost(a: str, b: str) -> float:
    if a == b:
        return 0.0
    c = SUB_COST.get((a, b))
    if c is not None:
        return c
    return 1.0 if (a in VOWELS) == (b in VOWELS) else 1.4


@lru_cache(maxsize=None)
def distance(x: str, y: str) -> float:
    px = phonemes(x)
    py = phonemes(y)
    m, n = len(px), len(py)
    prev = [0.0] * (n + 1)
    for j in range(1, n + 1):
        prev[j] = prev[j - 1] + indel_cost(py[j - 1])
    for i in range(1, m + 1):
        pi = px[i - 1]
        di = indel_cost(pi)
        curr = [prev[0] + di] + [0.0] * n
        for j in range(1, n + 1):
            pj = py[j - 1]
            c_del = prev[j] + di
            c_ins = curr[j - 1] + indel_cost(pj)
            c_sub = prev[j - 1] + sub_cost(pi, pj)
            curr[j] = min(c_del, c_ins, c_sub)
        prev = curr
    return prev[n]


@lru_cache(maxsize=None)
def stem(w: str) -> str:
    t = norm(w)
    if len(t) > 3:
        for e in STEM_ENDINGS:
            if t.endswith(e):
                return t[:-len(e)]
    return t


@lru_cache(maxsize=None)
def pun_cost(part: str, word: str) -> float:
    return min(distance(part, word), distance(stem(part), stem(word)) + 0.2)


def load_corpus(path: Path) -> list[list[str]]:
    texts: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            t = (row["text"] or "").strip()
            ss = [x for x in DIGITS3_RE.findall(t) if x != "999"]
            if (
                not ss
                or "[" in t or "]" in t or "/" in t
                or (row["dir."] or "").strip() not in ("R/L", "L/R")
                or "000" in ss
                or len(ss) < 2
                or not (row["type"] or "").strip().startswith("SEAL")
            ):
                continue
            key = tuple(ss)
            if key in seen:
                continue
            seen.add(key)
            texts.append(ss[::-1])
    return texts


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def scramble(names: list[tuple[list[str], float]], s: int) -> list[tuple[list[str], float]]:
    flat = [m for parts, _ in names for m in parts]
    random.Random(s).shuffle(flat)
    out: list[tuple[list[str], float]] = []
    idx = 0
    for parts, w in names:
        n = len(parts)
        out.append((flat[idx:idx + n], w))
        idx += n
    return out


class NameModel:
    def __init__(self, names: list[tuple[list[str], float]], cat_of, stab_of):
        self.cat_of = cat_of
        self.stab_of = stab_of
        wb: dict[tuple[str, str], float] = defaultdict(float)
        wu: dict[str, float] = defaultdict(float)
        cb: dict[tuple[str, str], float] = defaultdict(float)
        cu: dict[str, float] = defaultdict(float)
        mc: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        uni: dict[str, float] = defaultdict(float)
        for parts, weight in names:
            w = math.log(1.0 + weight)
            seq = ["<s>", *parts, "</s>"]
            for a, b in zip(seq, seq[1:]):
                wb[(a, b)] += w
                wu[a] += w
                ca = a if (a == "<s>" or a == "</s>") else cat_of(a)
                cb_ = b if (b == "<s>" or b == "</s>") else cat_of(b)
                cb[(ca, cb_)] += w
                cu[ca] += w
            for m in parts:
                mc[cat_of(m)][m] += w
                uni[m] += w
        self.wb = wb
        self.wu = wu
        self.cb = cb
        self.cu = cu
        self.uni = uni
        self.uni_denom = sum(uni.values()) + 0.5 * len(uni)
        self.ncat_smooth = 0.1 * (len(mc) + 2)
        self.mc_info = {
            c: (cnt, sum(cnt.values()) + 0.5 * (max(1, len(cnt)) + 1), 1.0 / (max(1, len(cnt)) + 1))
            for c, cnt in mc.items()
        }
        self._lp_cache: dict[tuple[str, str], float] = {}

    def freq(self, b: str) -> float:
        return (self.uni.get(b, 0.0) + 0.5) / self.uni_denom

    def in_cat(self, m: str, c: str) -> float:
        entry = self.mc_info.get(c)
        if entry is None:
            emp = flat = 0.5
        else:
            cnt, denom, flat = entry
            emp = (cnt.get(m, 0.0) + 0.5) / denom
        a = STAB_ALPHA.get(self.stab_of(m), 0.7)
        return a * emp + (1.0 - a) * flat

    def mixed(self, a: str, b: str) -> float:
        wua = self.wu.get(a, 0.0)
        pw = self.wb.get((a, b), 0.0) / wua if wua else 0.0
        ca = a if (a == "<s>" or a == "</s>") else self.cat_of(a)
        if b == "</s>":
            cb_ = "</s>"
            pm = 1.0
            pu = 1.0 / 50.0
        else:
            cb_ = "<s>" if b == "<s>" else self.cat_of(b)
            pm = self.in_cat(b, cb_)
            pu = self.freq(b)
        pc = (self.cb.get((ca, cb_), 0.0) + 0.1) / (self.cu.get(ca, 0.0) + self.ncat_smooth)
        return 0.45 * pw + 0.4 * pc * pm + 0.15 * pu

    def lp(self, a: str, b: str) -> float:
        key = (a, b)
        res = self._lp_cache.get(key)
        if res is not None:
            return res
        if b == "GAP":
            res = 0.0
        elif a == "GAP":
            res = LOG_BREAK if b == "</s>" else math.log(self.freq(b))
        else:
            p = self.mixed(a, b)
            if a != "<s>" and b != "</s>":
                p = 0.7 * p + 0.3 * math.exp(self.lp(a, "</s>") + self.lp("<s>", b))
            res = math.log(p + 1e-12)
        self._lp_cache[key] = res
        return res


def run_once(
    seed: int, mode: str, all_names: list[tuple[list[str], float]],
    sample_n: int | None, seals: list[list[str]], signs: list[str],
    words: dict[str, set[str]], fixed: dict[str, str], punmax: float,
    cat_of, stab_of,
) -> tuple[float, dict[str, str]]:
    names = (
        random.Random(100 + seed).sample(all_names, sample_n)
        if sample_n and len(all_names) > sample_n else all_names
    )
    order = list(range(len(seals)))
    random.Random(800 + seed).shuffle(order)
    mid_s = len(order) // 2
    half1 = [seals[i] for i in order[:mid_s]]
    half2 = [seals[i] for i in order[mid_s:]]

    full = scramble(names, 7000 + seed) if mode == "null" else names
    idx = list(range(len(full)))
    random.Random(500 + seed).shuffle(idx)
    mid_n = len(idx) // 2
    names_a = [full[i] for i in idx[:mid_n]]
    names_b = [full[i] for i in idx[mid_n:]]

    models_a = [NameModel(names_a, cat_of, stab_of)] + [
        NameModel(scramble(names_a, 3000 + i), cat_of, stab_of) for i in range(8)
    ]
    models_b = [NameModel(names_b, cat_of, stab_of)] + [
        NameModel(scramble(names_b, 4000 + i), cat_of, stab_of) for i in range(8)
    ]

    fixed_vals = set(fixed.values())
    counts = Counter(m for parts, _ in full for m in parts)
    pool = sorted(m for m, c in counts.items() if len(m) >= 2 and c >= 2 and m not in fixed_vals)
    pool_set = set(pool)
    pool_by_first: dict[str, list[str]] = defaultdict(list)
    for m in pool:
        pool_by_first[m[0]].append(m)

    candidates: dict[str, list[str]] = {}
    for s in signs:
        ws = words[s]
        cands = {w for w in ws if w in pool_set}
        for w in ws:
            lw = len(w)
            for m in pool_by_first.get(w[0], ()):
                if m not in cands and abs(len(m) - lw) <= 3 and pun_cost(m, w) <= punmax:
                    cands.add(m)
        candidates[s] = sorted(cands)

    signs_set = set(signs)
    slots: dict[str, dict[tuple[str, str], int]] = {s: defaultdict(int) for s in signs}
    occ: Counter[str] = Counter()
    for text in half1:
        occ.update(text)
        seq = ["<s>", *text, "</s>"]
        for a, b in zip(seq, seq[1:]):
            if a in signs_set:
                slots[a][(a, b)] += 1
            if b in signs_set and b != a:
                slots[b][(a, b)] += 1

    ordered_signs = sorted(signs, key=lambda s: (-occ.get(s, 0), s))
    assigned = {s: "GAP" for s in signs}

    def value(x: str) -> str:
        if x in assigned:
            return assigned[x]
        if x in fixed:
            return fixed[x]
        if x == "<s>" or x == "</s>":
            return x
        return "GAP"

    lp_a = [m.lp for m in models_a]
    for _ in range(2):
        for s in ordered_signs:
            s_slots = slots[s]
            if not s_slots:
                assigned[s] = "GAP"
                continue
            used = {v for k, v in assigned.items() if k != s and v != "GAP"}
            cands = [m for m in candidates[s] if m not in used]
            if not cands:
                assigned[s] = "GAP"
                continue
            pinfo = [
                (l == s, r == s, "GAP" if l == s else value(l), "GAP" if r == s else value(r), n)
                for (l, r), n in s_slots.items()
            ]
            lp0 = [[lp(vl, vr) for _, _, vl, vr, _ in pinfo] for lp in lp_a]
            best_m, best_g = "GAP", 0.0
            for m in cands:
                totals = [
                    sum(n * (lp(m if il else vl, m if ir else vr) - b0)
                        for (il, ir, vl, vr, n), b0 in zip(pinfo, base))
                    for lp, base in zip(lp_a, lp0)
                ]
                g = totals[0] - sum(totals[1:]) / 8.0
                if g > best_g:
                    best_g, best_m = g, m
            assigned[s] = best_m

    lp_b = [m.lp for m in models_b]
    heldout = 0.0
    for text in half2:
        seq = ["<s>", *(value(x) for x in text), "</s>"]
        pairs = list(zip(seq, seq[1:]))
        totals = [sum(lp(a, b) for a, b in pairs) for lp in lp_b]
        heldout += totals[0] - sum(totals[1:]) / 8.0

    readings = {s: assigned[s] for s in signs if assigned[s] != "GAP"}
    return round(heldout, 2), readings


def main() -> None:
    if len(sys.argv) != 6:
        sys.exit("Usage: python replicate.py SETTINGS.json CORPUS.csv FIRST_SEED LAST_SEED OUT.json")
    cfg_path, corpus_path = Path(sys.argv[1]), Path(sys.argv[2])
    first_seed, last_seed = int(sys.argv[3]), int(sys.argv[4])
    out_path = Path(sys.argv[5])

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base = cfg_path.resolve().parent
    parts_rows = load_jsonl(base / cfg["parts"])
    names_rows = load_jsonl(base / cfg["names"])
    raw_words = json.loads((base / cfg["words"]).read_text(encoding="utf-8"))

    info = {norm(p["m"]): p for p in parts_rows}
    loan_cat = cfg.get("loan_category", "sanskrit_loan")
    loans = {norm(x) for x in (cfg.get("drop_parts") or [])}
    if loan_cat is not None:
        loans.update(norm(p["m"]) for p in parts_rows if p.get("category") == loan_cat)
    keep_noninitial = {norm(x) for x in (cfg.get("keep_noninitial") or [])}
    use_stored = cfg.get("weights", "once") == "stored"

    all_names: list[tuple[list[str], float]] = []
    for row in names_rows:
        ms = [nm for m in row.get("morphemes", []) if (nm := norm(m))]
        kept = [m for i, m in enumerate(ms) if m not in loans or (i > 0 and m in keep_noninitial)]
        if kept:
            w = float(row.get("weight", 1)) if use_stored else 1.0
            all_names.append((kept, w))

    num_words = cfg["number_words"]
    fixed = {s: num_words[val] for s, val in NUM_SIGN_VALUES}
    words = {
        s: {nm for ws in eng.values() for w in ws if (nm := norm(w))}
        for s, eng in raw_words.items()
        if s not in fixed
    }

    top = set(words) | set(fixed)
    seals: list[list[str]] = []
    for text in load_corpus(corpus_path):
        mapped = [s if s in top else "GAP" for s in text]
        gaps = mapped.count("GAP")
        if gaps <= 1 and len(mapped) - gaps >= 2:
            seals.append(mapped)

    seal_tokens = {t for text in seals for t in text}
    signs = sorted(s for s in words if s in seal_tokens)
    cat_map = {m: p.get("category", "other") for m, p in info.items()}
    stab_map = {m: p.get("stability", 2) for m, p in info.items()}
    cat_of = lambda m: cat_map.get(m, "other")
    stab_of = lambda m: stab_map.get(m, 2)

    punmax = float(cfg.get("punmax", 0.5))
    sample_n = cfg.get("sample_n")

    runs = []
    for seed in range(first_seed, last_seed + 1):
        real_h, readings = run_once(
            seed, "real", all_names, sample_n, seals, signs, words, fixed, punmax, cat_of, stab_of
        )
        null_h, _ = run_once(
            seed, "null", all_names, sample_n, seals, signs, words, fixed, punmax, cat_of, stab_of
        )
        diff = round(real_h - null_h, 2)
        runs.append({
            "seed": seed,
            "real": real_h,
            "null": null_h,
            "difference": diff,
            "signs_read": len(readings),
            "readings": readings,
        })

    mean_diff = round(sum(r["difference"] for r in runs) / len(runs), 2) if runs else 0.0
    above_zero = sum(1 for r in runs if r["difference"] > 0)
    result = {
        "lang": cfg["lang"],
        "runs": runs,
        "mean_difference": mean_diff,
        "seeds_above_zero": above_zero,
    }
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
