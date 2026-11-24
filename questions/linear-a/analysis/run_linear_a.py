#!/usr/bin/env python3
"""Pre-registered computational audit of the 2026 Linear A Semitic decipherment (#12).

Implements protocol.md (locked in protocol.lock) using:
  - plasma-ai/kaphtor (pinned commit d419ccc1e79f, treated strictly as data)
  - Independent Linear A cross-check (lineara_xyz_inscriptions.js)
  - Linear B Mycenaean Greek negative control (mwenge/linearb.xyz)
  - Bronze Age Semitic positive controls (Amarna Canaanite & Akkadian)
"""
import collections
import json
import math
import pathlib
import random
import re
import unicodedata

import numpy as np
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
KAPHTOR = DATA / "kaphtor" / "data"
RES = ROOT / "results"
RES.mkdir(parents=True, exist_ok=True)

# 9-class strong consonant inventory matching sign_values.json neutralization_classes
CLASSES_9 = ("K", "P", "T", "S", "R", "M", "N", "W", "Y")
CLASSES_7 = ("K", "P", "T", "S", "R", "M", "N")

# Map individual consonant phonemes (normalized lowercase, stripped of diacritics where handled explicitly)
# to the 9-class Linear A syllabic consonant grid.
CONSONANT_MAP = {
    # K-class: velars & uvulars/labiovelars
    "k": "K", "g": "K", "q": "K", "c": "K", "ɣ": "K", "ɠ": "K",
    # P-class: labials
    "p": "P", "b": "P", "f": "P", "v": "P", "φ": "P", "β": "P",
    # T-class: dentals & interdentals
    "t": "T", "d": "T", "ṭ": "T", "ṯ": "T", "ḏ": "T", "ḍ": "T", "θ": "T", "ð": "T", "δ": "T",
    # S-class: sibilants & affricates
    "s": "S", "z": "S", "š": "S", "ṣ": "S", "ś": "S", "ŝ": "S", "ž": "S", "č": "S", "ç": "S", "č": "S",
    # R-class: liquids
    "r": "R", "l": "R", "ḷ": "R", "ṛ": "R",
    # Unmerged sonorants & glides
    "m": "M",
    "n": "N",
    "w": "W",
    "y": "Y", "j": "Y",
}
# Weak / guttural / laryngeal / vowel characters dropped from core consonant skeleton
DROPPED_CHARS = set("aeiouāēīōūăĕĭŏŭâêîôûäëïöüvʾʿʕʔʼ'hḥḫẖꜣꜥḫħʰʷʸˈˌ-–—*0123456789₂₃₄₅₆₇₈₉()[]?~./,;: ")

SEMITIC_PREFIXES = set("MTYNS")
SEMITIC_SUFFIXES = set("TNMYW")


def project_phoneme_string(text: str, drop_wy: bool = False) -> str:
    """Project a phonetic / consonantal string onto the Linear A 9-class (or 7-class) skeleton."""
    if not text:
        return ""
    # Strip uppercase 'V' (standard Proto-Semitic unspecified-vowel placeholder) before lowercasing
    s = re.sub(r"V", "", text).lower()
    # Handle digraphs before single chars
    s = s.replace("sh", "š").replace("ts", "ṣ").replace("th", "ṯ").replace("dh", "ḏ").replace("ch", "ḫ").replace("kh", "ḫ").replace("gh", "g").replace("qu", "k").replace("kw", "k").replace("gw", "k").replace("ph", "p")
    out = []
    for ch in s:
        if ch in CONSONANT_MAP:
            cls = CONSONANT_MAP[ch]
            if drop_wy and cls in ("W", "Y"):
                continue
            out.append(cls)
        else:
            # Check base character after NFD stripping if it's a diacriticized consonant
            nfd = unicodedata.normalize("NFD", ch)
            base = nfd[0] if nfd else ""
            if base in CONSONANT_MAP and base not in ("h",):
                cls = CONSONANT_MAP[base]
                if drop_wy and cls in ("W", "Y"):
                    continue
                out.append(cls)
    return "".join(out)


def parse_semitic_ps_variants(ps_str: str) -> list[str]:
    """Extract clean root forms from SED Proto-Semitic string (e.g., '*sVrw(-ay)- ~ (?) *sVran-')."""
    if not ps_str:
        return []
    parts = re.split(r"[,~;/]", ps_str)
    forms = []
    for part in parts:
        # Remove gloss numbers, question marks, asterisks
        p = re.sub(r"\(\?\)", "", part)
        p = re.sub(r"\b\d+\b", "", p)
        # Variant 1: strip parenthesized optional affixes like (-at), (V), (ʾa-)
        p_no_paren = re.sub(r"\([^)]*\)", "", p).strip()
        # Variant 2: keep parenthesized consonant content (minus V placeholder)
        p_with_paren = re.sub(r"[()]", "", p).replace("V", "").strip()
        p_no_paren = p_no_paren.replace("V", "")
        if p_no_paren:
            forms.append(p_no_paren)
        if p_with_paren and p_with_paren != p_no_paren:
            forms.append(p_with_paren)
    return forms


def build_root_skeletons(forms_by_entry: list[list[str]], drop_wy: bool = False) -> tuple[set[str], dict[str, int]]:
    """Build set of unique consonant skeletons and multiplicity count (distinct root entries per skeleton)."""
    skel_counts = collections.Counter()
    for forms in forms_by_entry:
        seen_for_entry = set()
        for f in forms:
            sk = project_phoneme_string(f, drop_wy=drop_wy)
            if len(sk) >= 2:
                seen_for_entry.add(sk)
        for sk in seen_for_entry:
            skel_counts[sk] += 1
    return set(skel_counts.keys()), dict(skel_counts)


def match_skeleton(skel: str, root_set: set[str], regime: str = "A1") -> bool:
    """Test whether a projected word skeleton matches root_set under Regime A1, A2, or B."""
    if regime in ("A1", "A2"):
        return skel in root_set
    elif regime == "B":
        # Exact match or strip <=1 Semitic prefix OR <=1 Semitic suffix (remaining len >= 3)
        if len(skel) >= 3 and skel in root_set:
            return True
        if len(skel) >= 4 and skel[0] in SEMITIC_PREFIXES and skel[1:] in root_set:
            return True
        if len(skel) >= 4 and skel[-1] in SEMITIC_SUFFIXES and skel[:-1] in root_set:
            return True
        if len(skel) >= 5 and skel[0] in SEMITIC_PREFIXES and skel[-1] in SEMITIC_SUFFIXES and skel[1:-1] in root_set:
            return True
        return False
    raise ValueError(regime)


def apply_cons_perm(skel: str, perm_map: dict[str, str]) -> str:
    return "".join(perm_map.get(c, c) for c in skel)


def load_sign_table(sv_json: dict) -> tuple[dict[str, str], dict[str, str], set[str]]:
    """Return:
      sign_to_cons_kaphtor: sign -> single class in CLASSES_9 or '' (pure vowel/laryngeal)
      sign_to_cons_lb_only: sign -> class using standard Linear B value only
      novel_signs: set of signs whose kaphtor value differs from or is absent in Linear B
    """
    signs = sv_json["signs"]
    kaphtor_map = {}
    lb_map = {}
    novel = set()
    for sign, info in signs.items():
        p = info.get("primary") or {}
        c = p.get("consonant") or ""
        vw = p.get("vowel") or ""
        k_cls = project_phoneme_string(c, drop_wy=False)
        k_cls = k_cls[0] if k_cls else ""
        kaphtor_map[sign.upper()] = k_cls

        lb = info.get("linear_b")
        lb_val = lb.get("value") if isinstance(lb, dict) else (lb if isinstance(lb, str) else None)
        if lb_val and re.fullmatch(r"[a-z]+[0-9₂₃₄]*", lb_val.lower()):
            lb_c = re.sub(r"[aeiou0-9₂₃₄]+$", "", lb_val.lower())
            # Linear B standard phonetic values (ja/je/jo/ju -> Y, etc.)
            lb_cls = project_phoneme_string(lb_c, drop_wy=False)
            lb_cls = lb_cls[0] if lb_cls else ""
            lb_map[sign.upper()] = lb_cls
        else:
            lb_val = None

        val_str = f"{c}{vw}".lower()
        if lb_val is None or (val_str and val_str != lb_val.lower()):
            if k_cls:  # has a consonant assignment in kaphtor
                novel.add(sign.upper())
    return kaphtor_map, lb_map, novel


def is_clean_syllabic_word(w: str) -> bool:
    """Return True if word is unbroken, >=3 hyphenated syllabograms, no logograms/numerals/brackets."""
    if not w or "[" in w or "]" in w or "?" in w or "\n" in w or " " in w or "+" in w or "/" in w:
        return False
    parts = [p.strip() for p in w.split("-") if p.strip()]
    if len(parts) < 3:
        return False
    for p in parts:
        # Exclude numerals, punctuation, pure ideogram names (all lowercase or >4 letters like VIN, GRA, OLE)
        if re.fullmatch(r"[0-9]+", p):
            return False
        if not re.fullmatch(r"(\*[0-9]+[A-Z]?|[A-Z]+[0-9₂₃₄]*)", p.upper()):
            return False
        # Exclude known multi-letter logograms (length >= 4 without '*')
        if not p.startswith("*") and len(re.sub(r"[0-9₂₃₄]+$", "", p)) >= 4:
            return False
    return True


def linear_a_word_to_skeleton(word: str, sign_map: dict[str, str], drop_wy: bool = False) -> tuple[str, bool]:
    """Convert hyphenated Linear A word to consonant skeleton; second element = all signs known."""
    parts = [p.strip().upper() for p in word.split("-") if p.strip()]
    out = []
    all_known = True
    for p in parts:
        # Normalize subscript digits (RA₂ -> RA2)
        p_norm = p.replace("₂", "2").replace("₃", "3").replace("₄", "4")
        if p_norm in sign_map:
            cls = sign_map[p_norm]
        elif p in sign_map:
            cls = sign_map[p]
        else:
            # Fallback for standard CV syllabogram (e.g., QA, SA, TA) not listed separately
            m = re.fullmatch(r"([A-Z]{1,2})[AEIOU][0-9]*", p_norm)
            if m:
                cls = project_phoneme_string(m.group(1), drop_wy=False)
                cls = cls[0] if cls else ""
            elif re.fullmatch(r"[AEIOU][0-9]*", p_norm):
                cls = ""
            else:
                all_known = False
                cls = ""
        if cls:
            if drop_wy and cls in ("W", "Y"):
                continue
            out.append(cls)
    return "".join(out), all_known


def linear_b_word_to_skeleton(word: str, drop_wy: bool = False) -> str:
    """Convert hyphenated Linear B transliterated word (e.g., 'ko-no-so', 'wa-na-ka') to consonant skeleton."""
    parts = [p.strip().lower() for p in word.split("-") if p.strip()]
    out = []
    for p in parts:
        p_clean = re.sub(r"[0-9₂₃₄]+$", "", p)
        # Strip final vowel(s)
        c = re.sub(r"[aeiou]+$", "", p_clean)
        if c:
            cls = project_phoneme_string(c, drop_wy=drop_wy)
            if cls:
                out.append(cls[0])
    return "".join(out)


def extract_linear_a_words(corpus_json: dict) -> collections.Counter:
    """Extract all clean unbroken >=3-sign Linear A words and their token counts."""
    counts = collections.Counter()
    for rec in corpus_json.values():
        for w in rec.get("transliteratedWords") or []:
            w_clean = w.strip()
            if is_clean_syllabic_word(w_clean):
                # Normalize subscripts and uppercase
                w_norm = w_clean.upper().replace("₂", "2").replace("₃", "3").replace("₄", "4")
                counts[w_norm] += 1
    return counts


def extract_lineara_xyz_words(js_path: pathlib.Path) -> collections.Counter:
    """Independent cross-check extraction directly from lineara_xyz_inscriptions.js."""
    txt = js_path.read_text(encoding="utf-8", errors="ignore")
    counts = collections.Counter()
    for block in re.findall(r'"transliteratedWords"\s*:\s*\[([^\]]*)\]', txt):
        for w in re.findall(r'"([^"]+)"', block):
            w_clean = w.strip()
            if is_clean_syllabic_word(w_clean):
                w_norm = w_clean.upper().replace("₂", "2").replace("₃", "3").replace("₄", "4")
                counts[w_norm] += 1
    return counts


def extract_linear_b_words(js_path: pathlib.Path) -> collections.Counter:
    """Extract clean unbroken >=3-sign Linear B Mycenaean Greek words."""
    txt = js_path.read_text(encoding="utf-8", errors="ignore")
    counts = collections.Counter()
    for block in re.findall(r'"transliteratedWords"\s*:\s*\[([^\]]*)\]', txt):
        for w in re.findall(r'"([^"]+)"', block):
            w_clean = w.strip()
            if "[" in w_clean or "]" in w_clean or "?" in w_clean or " " in w_clean or "/" in w_clean:
                continue
            parts = w_clean.split("-")
            if len(parts) < 3:
                continue
            # Linear B syllabic words are lowercase hyphenated (e.g., 'ka-ko-de-ta', 'e-ke-qe')
            if all(re.fullmatch(r"[a-z]{1,3}[0-9₂₃₄]*", p) for p in parts):
                # Exclude metadata tokens like 'sup.', 'inf.', 'mut.' (none have hyphens anyway)
                counts[w_clean.lower()] += 1
    return counts


def consonant_permutation_test(
    skels: list[str],
    weights: list[int],
    root_set: set[str],
    regime: str,
    classes: tuple[str, ...],
    n_perm: int = 1000,
    seed: int = 42,
) -> dict:
    """Test observed match rate against n_perm random permutations of the consonant classes."""
    rng = random.Random(seed)
    n_types = len(skels)
    total_tok = sum(weights)
    if n_types == 0:
        return {"n_types": 0, "n_tokens": 0, "obs_type_rate": None, "p_perm_type": None}

    obs_hits = [match_skeleton(s, root_set, regime) for s in skels]
    obs_type = sum(obs_hits) / n_types
    obs_tok = sum(w for h, w in zip(obs_hits, weights) if h) / total_tok

    null_type = np.empty(n_perm, dtype=float)
    null_tok = np.empty(n_perm, dtype=float)
    cls_list = list(classes)
    for i in range(n_perm):
        shuffled = cls_list[:]
        rng.shuffle(shuffled)
        pmap = dict(zip(cls_list, shuffled))
        hits = [match_skeleton(apply_cons_perm(s, pmap), root_set, regime) for s in skels]
        null_type[i] = sum(hits) / n_types
        null_tok[i] = sum(w for h, w in zip(hits, weights) if h) / total_tok

    p_type = float((np.sum(null_type >= obs_type) + 1) / (n_perm + 1))
    p_tok = float((np.sum(null_tok >= obs_tok) + 1) / (n_perm + 1))
    sd_type = float(np.std(null_type, ddof=1))
    z_type = float((obs_type - np.mean(null_type)) / sd_type) if sd_type > 0 else 0.0
    return {
        "n_types": n_types,
        "n_tokens": total_tok,
        "obs_type_rate": round(obs_type, 5),
        "null_type_mean": round(float(np.mean(null_type)), 5),
        "null_type_sd": round(sd_type, 5),
        "z_type": round(z_type, 3),
        "p_perm_type": round(p_type, 5),
        "obs_tok_rate": round(obs_tok, 5),
        "null_tok_mean": round(float(np.mean(null_tok)), 5),
        "p_perm_tok": round(p_tok, 5),
    }


def novel_sign_permutation_test(
    words_and_weights: list[tuple[str, int]],
    sign_map: dict[str, str],
    novel_signs: set[str],
    root_set: set[str],
    regime: str,
    drop_wy: bool,
    min_cons: int = 3,
    n_perm: int = 1000,
    seed: int = 123,
) -> dict:
    """Hold Linear B core signs fixed; permute ONLY Di Mino's novel/revised sign assignments."""
    # Filter to words containing at least one novel sign
    affected = []
    for w, wt in words_and_weights:
        parts = [p.strip().upper().replace("₂", "2").replace("₃", "3").replace("₄", "4") for p in w.split("-")]
        if any(p in novel_signs for p in parts):
            sk, ok = linear_a_word_to_skeleton(w, sign_map, drop_wy=drop_wy)
            if ok and len(sk) >= min_cons:
                affected.append((w, wt, sk))
    if not affected:
        return {"n_affected_types": 0, "obs_type_rate": None, "p_perm_novel": None}

    obs_rate = sum(match_skeleton(sk, root_set, regime) for _, _, sk in affected) / len(affected)
    novel_list = sorted(novel_signs)
    novel_vals = [sign_map[s] for s in novel_list]
    rng = random.Random(seed)
    null_rates = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        shuf = novel_vals[:]
        rng.shuffle(shuf)
        pmap = dict(sign_map)
        for s, v in zip(novel_list, shuf):
            pmap[s] = v
        hits = 0
        for w, _, _ in affected:
            sk, _ = linear_a_word_to_skeleton(w, pmap, drop_wy=drop_wy)
            if len(sk) >= min_cons and match_skeleton(sk, root_set, regime):
                hits += 1
        null_rates[i] = hits / len(affected)
    p_val = float((np.sum(null_rates >= obs_rate) + 1) / (n_perm + 1))
    sd = float(np.std(null_rates, ddof=1))
    z = float((obs_rate - np.mean(null_rates)) / sd) if sd > 0 else 0.0
    return {
        "n_affected_types": len(affected),
        "obs_type_rate": round(obs_rate, 5),
        "null_mean": round(float(np.mean(null_rates)), 5),
        "null_sd": round(sd, 5),
        "z_novel": round(z, 3),
        "p_perm_novel": round(p_val, 5),
    }


def two_prop_fisher(k1: int, n1: int, k2: int, n2: int) -> dict:
    r1 = k1 / n1 if n1 else 0.0
    r2 = k2 / n2 if n2 else 0.0
    _, p = stats.fisher_exact([[k1, n1 - k1], [k2, n2 - k2]], alternative="two-sided")
    return {
        "rate_a": round(r1, 5),
        "rate_b": round(r2, 5),
        "diff_pp": round((r1 - r2) * 100, 2),
        "p_fisher": float(p),
        "n_a": n1,
        "n_b": n2,
    }


def main():
    print("Loading kaphtor & control corpora...")
    sv_json = json.load(open(KAPHTOR / "linear-a/sign_values.json"))
    corpus_json = json.load(open(KAPHTOR / "linear-a/corpus.json"))
    lex_json = json.load(open(KAPHTOR / "linear-a/lexicon.json"))
    semitic_json = json.load(open(KAPHTOR / "semitic-roots/semitic_roots.json"))

    sign_map, lb_sign_map, novel_signs = load_sign_table(sv_json)
    print(f"Loaded {len(sign_map)} sign values ({len(novel_signs)} novel/revised consonant assignments).")

    # Build root banks (9-class A1 and 7-class A2)
    sem_forms = [parse_semitic_ps_variants(r.get("ps", "")) for r in semitic_json["roots"]]
    sem_set_9, sem_mult_9 = build_root_skeletons(sem_forms, drop_wy=False)
    sem_set_7, sem_mult_7 = build_root_skeletons(sem_forms, drop_wy=True)

    egy_arr = json.load(open(KAPHTOR / "linear-a/egyptian_roots.json"))
    luw_arr = json.load(open(KAPHTOR / "linear-a/luwian_roots.json"))
    hat_arr = json.load(open(KAPHTOR / "linear-a/hattic_roots.json"))
    hur_arr = json.load(open(KAPHTOR / "linear-a/hurrian_roots.json"))

    egy_set_9, _ = build_root_skeletons([[x.get("Consonantal_Root", "")] for x in egy_arr], drop_wy=False)
    egy_set_7, _ = build_root_skeletons([[x.get("Consonantal_Root", "")] for x in egy_arr], drop_wy=True)
    luw_set_9, _ = build_root_skeletons([[x.get("Consonantal_Root", "")] for x in luw_arr], drop_wy=False)
    luw_set_7, _ = build_root_skeletons([[x.get("Consonantal_Root", "")] for x in luw_arr], drop_wy=True)
    hat_set_9, _ = build_root_skeletons([[x.get("Consonantal_Root", "")] for x in hat_arr], drop_wy=False)
    hur_set_9, _ = build_root_skeletons([[x.get("Consonantal_Root", "")] for x in hur_arr], drop_wy=False)

    print(
        f"Root skeletons (>=2 cons, 9-class): Semitic={len(sem_set_9)}, "
        f"Egyptian={len(egy_set_9)}, Luwian={len(luw_set_9)}, Hattic={len(hat_set_9)}, Hurrian={len(hur_set_9)}"
    )

    # Extract Linear A words (kaphtor + independent lineara.xyz cross-check)
    la_counts = extract_linear_a_words(corpus_json)
    la_xyz_counts = extract_lineara_xyz_words(DATA / "lineara_xyz_inscriptions.js")
    lb_counts = extract_linear_b_words(DATA / "linearb_xyz_inscriptions.js")
    print(f"Clean >=3-sign words: Linear A (kaphtor)={len(la_counts)} types ({sum(la_counts.values())} tok), "
          f"Linear A (lineara.xyz)={len(la_xyz_counts)} types, Linear B={len(lb_counts)} types ({sum(lb_counts.values())} tok)")

    # Build lexicon lookup (normalized word -> entry)
    lex_entries = lex_json["entries"]
    lex_by_word = {}
    for e in lex_entries:
        w = (e.get("word") or "").strip().upper().replace("₂", "2").replace("₃", "3").replace("₄", "4")
        if w:
            lex_by_word[w] = e

    # Partition Linear A clean >=3-sign words into In-Lexicon vs Held-Out
    la_all = list(la_counts.items())
    la_in_lex = [(w, c) for w, c in la_all if w in lex_by_word]
    la_held_out = [(w, c) for w, c in la_all if w not in lex_by_word]
    print(f"Linear A split: In-Lexicon={len(la_in_lex)} types, Held-Out={len(la_held_out)} types")

    # Positive controls: Amarna Canaanite & Akkadian
    amarna_rows = [json.loads(l) for l in open(KAPHTOR / "contact/amarna_canaanite.jsonl")]
    amarna_skels_9 = sorted({project_phoneme_string(r.get("form", ""), False) for r in amarna_rows if len(project_phoneme_string(r.get("form", ""), False)) >= 3})
    amarna_skels_7 = sorted({project_phoneme_string(r.get("form", ""), True) for r in amarna_rows if len(project_phoneme_string(r.get("form", ""), True)) >= 3})

    akk_rows = [json.loads(l) for l in open(KAPHTOR / "contact/akkadian_lexicon.jsonl")]
    akk_all_9 = sorted({project_phoneme_string(r.get("normalized") or r.get("form", ""), False) for r in akk_rows if " " not in (r.get("form") or "") and len(project_phoneme_string(r.get("normalized") or r.get("form", ""), False)) >= 3})
    akk_all_7 = sorted({project_phoneme_string(r.get("normalized") or r.get("form", ""), True) for r in akk_rows if " " not in (r.get("form") or "") and len(project_phoneme_string(r.get("normalized") or r.get("form", ""), True)) >= 3})
    rng_sample = random.Random(2026)
    akk_skels_9 = rng_sample.sample(akk_all_9, min(1000, len(akk_all_9)))
    akk_skels_7 = rng_sample.sample(akk_all_7, min(1000, len(akk_all_7)))

    # Linear B skeletons
    lb_skels_9_ge3 = [(linear_b_word_to_skeleton(w, False), c) for w, c in lb_counts.items()]
    lb_skels_9_ge3 = [(s, c) for s, c in lb_skels_9_ge3 if len(s) >= 3]
    lb_skels_7_ge3 = [(linear_b_word_to_skeleton(w, True), c) for w, c in lb_counts.items()]
    lb_skels_7_ge3 = [(s, c) for s, c in lb_skels_7_ge3 if len(s) >= 3]
    lb_skels_9_eq2 = [(linear_b_word_to_skeleton(w, False), c) for w, c in lb_counts.items()]
    lb_skels_9_eq2 = [(s, c) for s, c in lb_skels_9_eq2 if len(s) == 2]

    def project_la_subset(items, smap, drop_wy, min_c, exact_c=None):
        out = []
        for w, c in items:
            sk, ok = linear_a_word_to_skeleton(w, smap, drop_wy=drop_wy)
            if not ok:
                continue
            if exact_c is not None:
                if len(sk) == exact_c:
                    out.append((sk, c))
            elif len(sk) >= min_c:
                out.append((sk, c))
        return out

    # --- 1. CALIBRATION GATE ---
    print("Running Calibration Gate (Amarna Canaanite, Akkadian, Linear B)...")
    cal = {
        "amarna_A1_ge3": consonant_permutation_test(amarna_skels_9, [1] * len(amarna_skels_9), sem_set_9, "A1", CLASSES_9, 1000, 11),
        "amarna_A2_ge3": consonant_permutation_test(amarna_skels_7, [1] * len(amarna_skels_7), sem_set_7, "A2", CLASSES_7, 1000, 12),
        "amarna_B_ge3": consonant_permutation_test(amarna_skels_9, [1] * len(amarna_skels_9), sem_set_9, "B", CLASSES_9, 1000, 13),
        "akkadian_A1_ge3": consonant_permutation_test(akk_skels_9, [1] * len(akk_skels_9), sem_set_9, "A1", CLASSES_9, 1000, 14),
        "akkadian_A2_ge3": consonant_permutation_test(akk_skels_7, [1] * len(akk_skels_7), sem_set_7, "A2", CLASSES_7, 1000, 15),
        "akkadian_B_ge3": consonant_permutation_test(akk_skels_9, [1] * len(akk_skels_9), sem_set_9, "B", CLASSES_9, 1000, 16),
        "linear_b_A1_ge3": consonant_permutation_test([s for s, _ in lb_skels_9_ge3], [c for _, c in lb_skels_9_ge3], sem_set_9, "A1", CLASSES_9, 1000, 17),
        "linear_b_A2_ge3": consonant_permutation_test([s for s, _ in lb_skels_7_ge3], [c for _, c in lb_skels_7_ge3], sem_set_7, "A2", CLASSES_7, 1000, 18),
        "linear_b_B_ge3": consonant_permutation_test([s for s, _ in lb_skels_9_ge3], [c for _, c in lb_skels_9_ge3], sem_set_9, "B", CLASSES_9, 1000, 19),
        "linear_b_A1_eq2": consonant_permutation_test([s for s, _ in lb_skels_9_eq2], [c for _, c in lb_skels_9_eq2], sem_set_9, "A1", CLASSES_9, 1000, 20),
    }

    # --- 2. TEST 1: LINEAR A CONSONANT PERMUTATIONS (ALL, IN-LEXICON, HELD-OUT, LINEARA.XYZ) ---
    print("Running Test 1 (Linear A Consonant Permutations)...")
    t1 = {}
    for label, items in [("all", la_all), ("in_lexicon", la_in_lex), ("held_out", la_held_out), ("lineara_xyz", list(la_xyz_counts.items()))]:
        p9 = project_la_subset(items, sign_map, False, 3)
        p7 = project_la_subset(items, sign_map, True, 3)
        p9_eq2 = project_la_subset(items, sign_map, False, 2, exact_c=2)
        t1[label] = {
            "A1_ge3": consonant_permutation_test([s for s, _ in p9], [c for _, c in p9], sem_set_9, "A1", CLASSES_9, 1000, 31),
            "A2_ge3": consonant_permutation_test([s for s, _ in p7], [c for _, c in p7], sem_set_7, "A2", CLASSES_7, 1000, 32),
            "B_ge3": consonant_permutation_test([s for s, _ in p9], [c for _, c in p9], sem_set_9, "B", CLASSES_9, 1000, 33),
            "A1_eq2": consonant_permutation_test([s for s, _ in p9_eq2], [c for _, c in p9_eq2], sem_set_9, "A1", CLASSES_9, 1000, 34),
        }

    # --- 3. TEST 2: NOVEL SIGN-VALUE PERMUTATIONS ---
    print("Running Test 2 (Di Mino's 32 Novel Sign Assignments)...")
    t2 = {
        "all_A1_ge3": novel_sign_permutation_test(la_all, sign_map, novel_signs, sem_set_9, "A1", False, 3, 1000, 51),
        "all_A2_ge3": novel_sign_permutation_test(la_all, sign_map, novel_signs, sem_set_7, "A2", True, 3, 1000, 52),
        "all_B_ge3": novel_sign_permutation_test(la_all, sign_map, novel_signs, sem_set_9, "B", False, 3, 1000, 53),
        "in_lexicon_A1_ge3": novel_sign_permutation_test(la_in_lex, sign_map, novel_signs, sem_set_9, "A1", False, 3, 1000, 54),
        "held_out_A1_ge3": novel_sign_permutation_test(la_held_out, sign_map, novel_signs, sem_set_9, "A1", False, 3, 1000, 55),
        "held_out_A2_ge3": novel_sign_permutation_test(la_held_out, sign_map, novel_signs, sem_set_7, "A2", True, 3, 1000, 56),
        "held_out_B_ge3": novel_sign_permutation_test(la_held_out, sign_map, novel_signs, sem_set_9, "B", False, 3, 1000, 57),
    }

    # --- 4. TEST 3: LINEAR A vs LINEAR B (MYCENAEAN GREEK) HEAD-TO-HEAD ---
    print("Running Test 3 (Linear A vs Linear B Head-to-Head, length-matched)...")
    t3 = {}
    for label, items in [("all", la_all), ("in_lexicon", la_in_lex), ("held_out", la_held_out)]:
        p9 = project_la_subset(items, sign_map, False, 3)
        p7 = project_la_subset(items, sign_map, True, 3)
        # Length-stratified (exact L_c = 2, 3, 4+)
        by_len = {}
        for L_label, cond in [("L2", lambda s: len(s) == 2), ("L3", lambda s: len(s) == 3), ("L4plus", lambda s: len(s) >= 4)]:
            la_L = [s for s, _ in project_la_subset(items, sign_map, False, 2) if cond(s)]
            lb_L = [linear_b_word_to_skeleton(w, False) for w in lb_counts.keys() if cond(linear_b_word_to_skeleton(w, False))]
            k_a = sum(match_skeleton(s, sem_set_9, "A1") for s in la_L)
            k_b = sum(match_skeleton(s, sem_set_9, "A1") for s in lb_L)
            by_len[L_label] = two_prop_fisher(k_a, len(la_L), k_b, len(lb_L))
        k_a1 = sum(match_skeleton(s, sem_set_9, "A1") for s, _ in p9)
        k_b1 = sum(match_skeleton(s, sem_set_9, "A1") for s, _ in lb_skels_9_ge3)
        k_a2 = sum(match_skeleton(s, sem_set_7, "A2") for s, _ in p7)
        k_b2 = sum(match_skeleton(s, sem_set_7, "A2") for s, _ in lb_skels_7_ge3)
        k_ab = sum(match_skeleton(s, sem_set_9, "B") for s, _ in p9)
        k_bb = sum(match_skeleton(s, sem_set_9, "B") for s, _ in lb_skels_9_ge3)
        t3[label] = {
            "A1_ge3_vs_LB": two_prop_fisher(k_a1, len(p9), k_b1, len(lb_skels_9_ge3)),
            "A2_ge3_vs_LB": two_prop_fisher(k_a2, len(p7), k_b2, len(lb_skels_7_ge3)),
            "B_ge3_vs_LB": two_prop_fisher(k_ab, len(p9), k_bb, len(lb_skels_9_ge3)),
            "by_len_A1": by_len,
        }

    # --- 5. TEST 4: SIZE-MATCHED CROSS-FAMILY BAKE-OFF ---
    print("Running Test 4 (Cross-Family Size-Matched Bake-Off)...")
    # Restrict each root bank to >=3-consonant skeletons so dictionaries are compared apples-to-apples
    banks_9 = {
        "Semitic": sorted([s for s in sem_set_9 if len(s) >= 3]),
        "Egyptian": sorted([s for s in egy_set_9 if len(s) >= 3]),
        "Luwian": sorted([s for s in luw_set_9 if len(s) >= 3]),
        "Hattic": sorted([s for s in hat_set_9 if len(s) >= 3]),
        "Hurrian": sorted([s for s in hur_set_9 if len(s) >= 3]),
    }
    la_all_9 = [s for s, _ in project_la_subset(la_all, sign_map, False, 3)]
    la_ho_9 = [s for s, _ in project_la_subset(la_held_out, sign_map, False, 3)]
    lb_9 = [s for s, _ in lb_skels_9_ge3]

    min_big_n = min(len(banks_9["Semitic"]), len(banks_9["Egyptian"]), len(banks_9["Luwian"]))
    rng_bf = random.Random(777)
    t4 = {"bank_sizes_ge3": {k: len(v) for k, v in banks_9.items()}, "matched_size_N": min_big_n, "raw": {}, "size_matched": {}}
    for fam, b_list in banks_9.items():
        b_set = set(b_list)
        t4["raw"][fam] = {
            "la_all": round(sum(s in b_set for s in la_all_9) / len(la_all_9), 5),
            "la_held_out": round(sum(s in b_set for s in la_ho_9) / len(la_ho_9), 5),
            "linear_b": round(sum(s in b_set for s in lb_9) / len(lb_9), 5),
            "amarna": round(sum(s in b_set for s in amarna_skels_9) / len(amarna_skels_9), 5),
        }
        if len(b_list) >= min_big_n:
            la_draws, ho_draws, lb_draws, am_draws = [], [], [], []
            for _ in range(200):
                sub = set(rng_bf.sample(b_list, min_big_n))
                la_draws.append(sum(s in sub for s in la_all_9) / len(la_all_9))
                ho_draws.append(sum(s in sub for s in la_ho_9) / len(la_ho_9))
                lb_draws.append(sum(s in sub for s in lb_9) / len(lb_9))
                am_draws.append(sum(s in sub for s in amarna_skels_9) / len(amarna_skels_9))
            t4["size_matched"][fam] = {
                "la_all_mean": round(float(np.mean(la_draws)), 5),
                "la_held_out_mean": round(float(np.mean(ho_draws)), 5),
                "linear_b_mean": round(float(np.mean(lb_draws)), 5),
                "amarna_mean": round(float(np.mean(am_draws)), 5),
            }

    # --- 6. TEST 5: DIRECT AUDIT OF KAPHTOR LEXICON (736 ENTRIES) ---
    print("Running Test 5 (Direct Audit of kaphtor lexicon.json)...")
    tier_counts = collections.Counter()
    len_counts = collections.Counter()
    exact_match_9 = 0
    exact_match_7 = 0
    affix_match = 0
    with_root_ge3 = 0
    multiplicities = []
    tier_fidelity = collections.defaultdict(lambda: {"n": 0, "exact_A1": 0, "exact_A2": 0, "affix_B": 0})
    for e in lex_entries:
        tier = e.get("confidence") or "UNKNOWN"
        tier_counts[tier] += 1
        w = (e.get("word") or "").strip().upper().replace("₂", "2").replace("₃", "3").replace("₄", "4")
        parts = [p for p in w.split("-") if p]
        len_counts[min(len(parts), 5)] += 1
        root_str = e.get("root") or ""
        if len(parts) >= 3 and root_str and "+" not in root_str and "+" not in w:
            w_sk9, ok9 = linear_a_word_to_skeleton(w, sign_map, False)
            w_sk7, _ = linear_a_word_to_skeleton(w, sign_map, True)
            r_sk9 = project_phoneme_string(root_str, False)
            r_sk7 = project_phoneme_string(root_str, True)
            if ok9 and len(w_sk9) >= 2 and len(r_sk9) >= 2:
                with_root_ge3 += 1
                m9 = (w_sk9 == r_sk9)
                m7 = (w_sk7 == r_sk7)
                mB = (w_sk9 == r_sk9) or (len(w_sk9) >= 3 and (w_sk9[1:] == r_sk9 or w_sk9[:-1] == r_sk9 or (len(w_sk9) >= 4 and w_sk9[1:-1] == r_sk9)))
                exact_match_9 += int(m9)
                exact_match_7 += int(m7)
                affix_match += int(mB)
                tier_fidelity[tier]["n"] += 1
                tier_fidelity[tier]["exact_A1"] += int(m9)
                tier_fidelity[tier]["exact_A2"] += int(m7)
                tier_fidelity[tier]["affix_B"] += int(mB)
                multiplicities.append(sem_mult_9.get(w_sk9, 0))

    # Collision coverage of the 5,189 Semitic roots over the 9-class space:
    # Out of 9^2 = 81 possible 2-cons skeletons and 9^3 = 729 possible 3-cons skeletons, how many are occupied?
    sem_2 = [s for s in sem_set_9 if len(s) == 2]
    sem_3 = [s for s in sem_set_9 if len(s) == 3]
    sem_2_7 = [s for s in sem_set_7 if len(s) == 2]
    sem_3_7 = [s for s in sem_set_7 if len(s) == 3]

    t5 = {
        "total_lexicon_entries": len(lex_entries),
        "confidence_tiers": dict(tier_counts),
        "word_sign_lengths": {str(k): v for k, v in sorted(len_counts.items())},
        "evaluated_single_root_ge3_sign_words": with_root_ge3,
        "strict_root_match_A1_rate": round(exact_match_9 / with_root_ge3, 4) if with_root_ge3 else 0.0,
        "strict_root_match_A2_rate": round(exact_match_7 / with_root_ge3, 4) if with_root_ge3 else 0.0,
        "affix_tolerant_root_match_rate": round(affix_match / with_root_ge3, 4) if with_root_ge3 else 0.0,
        "mean_semitic_roots_per_skeleton": round(float(np.mean(multiplicities)), 2) if multiplicities else 0.0,
        "tier_fidelity": dict(tier_fidelity),
        "semitic_skeleton_space_coverage": {
            "9class_2cons_occupied": len(sem_2),
            "9class_2cons_total": 81,
            "9class_2cons_pct": round(100.0 * len(sem_2) / 81, 1),
            "9class_3cons_occupied": len(sem_3),
            "9class_3cons_total": 729,
            "9class_3cons_pct": round(100.0 * len(sem_3) / 729, 1),
            "7class_2cons_occupied": len(sem_2_7),
            "7class_2cons_total": 49,
            "7class_2cons_pct": round(100.0 * len(sem_2_7) / 49, 1),
            "7class_3cons_occupied": len(sem_3_7),
            "7class_3cons_total": 343,
            "7class_3cons_pct": round(100.0 * len(sem_3_7) / 343, 1),
        },
    }

    summary = {
        "counts": {
            "kaphtor_inscriptions": len(corpus_json),
            "sign_values_total": len(sign_map),
            "novel_or_revised_consonant_signs": len(novel_signs),
            "semitic_roots_raw": len(semitic_json["roots"]),
            "la_clean_ge3_types": len(la_counts),
            "la_clean_ge3_tokens": sum(la_counts.values()),
            "la_in_lexicon_types": len(la_in_lex),
            "la_held_out_types": len(la_held_out),
            "la_xyz_clean_ge3_types": len(la_xyz_counts),
            "lb_clean_ge3_types": len(lb_counts),
            "lb_clean_ge3_tokens": sum(lb_counts.values()),
        },
        "calibration": cal,
        "test1_consonant_permutations": t1,
        "test2_novel_sign_permutations": t2,
        "test3_linear_a_vs_linear_b": t3,
        "test4_cross_family_bakeoff": t4,
        "test5_lexicon_and_collision_audit": t5,
    }

    out_path = RES / "linear_a_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nSaved results to {out_path}")
    print("\n=== HEADLINE RESULTS ===")
    print("CALIBRATION (A1 >=3 cons):")
    for k in ["amarna_A1_ge3", "akkadian_A1_ge3", "linear_b_A1_ge3"]:
        v = cal[k]
        print(f"  {k}: obs={v['obs_type_rate']:.3f} null={v['null_type_mean']:.3f} z={v['z_type']:+.2f} p={v['p_perm_type']:.4f} (n={v['n_types']})")
    print("CALIBRATION (A2 7-class >=3 cons):")
    for k in ["amarna_A2_ge3", "akkadian_A2_ge3", "linear_b_A2_ge3"]:
        v = cal[k]
        print(f"  {k}: obs={v['obs_type_rate']:.3f} null={v['null_type_mean']:.3f} z={v['z_type']:+.2f} p={v['p_perm_type']:.4f} (n={v['n_types']})")
    print("TEST 1 LINEAR A (A1 >=3 cons):")
    for k in ["all", "in_lexicon", "held_out", "lineara_xyz"]:
        v = t1[k]["A1_ge3"]
        print(f"  {k}: obs={v['obs_type_rate']:.3f} null={v['null_type_mean']:.3f} z={v['z_type']:+.2f} p={v['p_perm_type']:.4f} (n={v['n_types']})")
    print("TEST 1 LINEAR A (A2 7-class >=3 cons):")
    for k in ["all", "in_lexicon", "held_out"]:
        v = t1[k]["A2_ge3"]
        print(f"  {k}: obs={v['obs_type_rate']:.3f} null={v['null_type_mean']:.3f} z={v['z_type']:+.2f} p={v['p_perm_type']:.4f} (n={v['n_types']})")
    print("TEST 2 NOVEL SIGNS:")
    for k, v in t2.items():
        print(f"  {k}: obs={v['obs_type_rate']} null={v.get('null_mean')} z={v.get('z_novel')} p={v['p_perm_novel']} (n={v['n_affected_types']})")
    print("TEST 3 LINEAR A vs LINEAR B (A1 >=3):")
    for k in ["all", "in_lexicon", "held_out"]:
        v = t3[k]["A1_ge3_vs_LB"]
        print(f"  {k}: LA={v['rate_a']:.3f} vs LB={v['rate_b']:.3f} diff={v['diff_pp']:+.2f}pp p={v['p_fisher']:.4g}")
    print("TEST 4 SIZE-MATCHED CROSS-FAMILY (N =", t4["matched_size_N"], "):")
    for fam, v in t4["size_matched"].items():
        print(f"  {fam}: LA_all={v['la_all_mean']:.3f} LA_ho={v['la_held_out_mean']:.3f} LB={v['linear_b_mean']:.3f} Amarna={v['amarna_mean']:.3f}")
    print("TEST 5 COLLISION COVERAGE:", t5["semitic_skeleton_space_coverage"])
    print("TEST 5 LEXICON FIDELITY:", {k: t5[k] for k in ["strict_root_match_A1_rate", "strict_root_match_A2_rate", "affix_tolerant_root_match_rate", "mean_semitic_roots_per_skeleton"]})


if __name__ == "__main__":
    main()
