"""Sensitivity checks for the linear-a study (spot check, not part of the locked study).

Question: would the study's own pipeline have detected a TRUE Semitic language written in Linear A?

1. Test 3 (headline): push known Semitic word sets through the same skeleton matcher and compare them with
   Linear B exactly as the study compared Linear A (length bins L=2, L=3, L>=4, Fisher two-sided, type level).
   Sets: (a) Amarna Canaanite forms projected exactly as the study's calibration did;
         (b) Amarna Canaanite forms 'written in Linear A': de-geminated, Linear B spelling rules
             (final consonants and pre-consonantal r/l/m/n/s omitted), then spelled with kaphtor's own sign
             values and projected with the study's linear_a_word_to_skeleton;
         (c) Akkadian normalized lemmas, written the same way;
         (d) Proto-Semitic stems from semitic_roots.json (V -> a), written the same way (ideal case: words are bare stems);
         (e) Hebrew lexicon consonantal forms, study projection (upper bound, no orthographic loss).
2. Power of the L=3 comparison (246 vs 1,064 types; 28 held-out) by normal approximation.
3. Test 2 (27-sign shuffle): run the study's novel_sign_permutation_test on synthetic Linear A written from
   true Semitic words with kaphtor's sign values (so the proposal's values are TRUE by construction), on the full
   synthetic set and on random subsets of n=124 and n=25 affected words; report detection rates.
4. Test 2 under A2: re-score the null counting only words whose skeleton still has >=3 consonants, to test the
   study's 'artifact' explanation for p=0.001.
5. Composition (Simpson) check for the unstratified 58.6% vs 48.9% gap.
Run: python -I sensitivity.py <work/questions/linear-a> <outdir>
"""
import collections
import importlib.util
import json
import math
import pathlib
import random
import re
import sys
import unicodedata

import numpy as np
from scipy import stats

W = pathlib.Path(sys.argv[1]).resolve()
OUT = pathlib.Path(sys.argv[2]).resolve()
spec = importlib.util.spec_from_file_location("rla", W / "analysis/run_linear_a.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
K = W / "data/kaphtor/data"

sv = json.load(open(K / "linear-a/sign_values.json"))
sign_map, lb_sign_map, novel = m.load_sign_table(sv)
semitic = json.load(open(K / "semitic-roots/semitic_roots.json"))
sem_forms = [m.parse_semitic_ps_variants(r.get("ps", "")) for r in semitic["roots"]]
SEM9, _ = m.build_root_skeletons(sem_forms, drop_wy=False)
SEM7, _ = m.build_root_skeletons(sem_forms, drop_wy=True)
corpus = json.load(open(K / "linear-a/corpus.json"))
lex = json.load(open(K / "linear-a/lexicon.json"))["entries"]
lex_words = {(e.get("word") or "").strip().upper().replace("₂", "2").replace("₃", "3").replace("₄", "4") for e in lex}
la_counts = m.extract_linear_a_words(corpus)
lb_counts = m.extract_linear_b_words(W / "data/linearb_xyz_inscriptions.js")

res = {}


def bins_from_skels(skels):
    out = {"L2": [0, 0], "L3": [0, 0], "L4plus": [0, 0]}
    for s in skels:
        L = len(s)
        key = "L2" if L == 2 else "L3" if L == 3 else "L4plus" if L >= 4 else None
        if key:
            out[key][1] += 1
            out[key][0] += int(s in SEM9)
    return out


# Linear B bins (exactly as the study's Test 3: over unique LB words)
lb_sk = [m.linear_b_word_to_skeleton(w, False) for w in lb_counts]
LB = bins_from_skels(lb_sk)
la_sk_all = []
la_sk_ho = []
for w in la_counts:
    sk, ok = m.linear_a_word_to_skeleton(w, sign_map, False)
    if ok:
        la_sk_all.append(sk)
        if w not in lex_words:
            la_sk_ho.append(sk)
LA = bins_from_skels(la_sk_all)
LAHO = bins_from_skels(la_sk_ho)


def compare(name, bins):
    if isinstance(bins, list):
        bins = bins_from_skels(bins)
    row = {}
    for k in ("L2", "L3", "L4plus"):
        ka, na = bins[k]
        kb, nb = LB[k]
        if na == 0:
            row[k] = None
            continue
        _, p = stats.fisher_exact([[ka, na - ka], [kb, nb - kb]])
        row[k] = {"k": ka, "n": na, "rate": round(ka / na, 4), "LB_rate": round(kb / nb, 4),
                  "diff_pp": round(100 * (ka / na - kb / nb), 2), "p_fisher": round(float(p), 4)}
    # unstratified >=3
    ka = bins["L3"][0] + bins["L4plus"][0]
    na = bins["L3"][1] + bins["L4plus"][1]
    kb = LB["L3"][0] + LB["L4plus"][0]
    nb = LB["L3"][1] + LB["L4plus"][1]
    _, p = stats.fisher_exact([[ka, na - ka], [kb, nb - kb]])
    row["ge3_unstratified"] = {"k": ka, "n": na, "rate": round(ka / na, 4), "LB_rate": round(kb / nb, 4),
                               "diff_pp": round(100 * (ka / na - kb / nb), 2), "p_fisher": float(f"{p:.3g}"),
                               "share_L3": round(bins["L3"][1] / na, 3)}
    res.setdefault("test3_sensitivity", {})[name] = row
    return row


compare("Linear A (all, study)", LA)
compare("Linear A (held-out, study)", LAHO)
compare("Linear B self-check", LB)

# ---------- writing Semitic words in Linear A ----------
LARYNGEAL = set("ʾʿʕʔhḥḫẖ'ʼ")
VOWELS = "aeiou"
CODA_DROP = {"R", "M", "N", "S"}


def base(ch):
    return unicodedata.normalize("NFD", ch)[0]


def tokenize(phon):
    """phoneme string -> list of ('C', class, ph) | ('H',) | ('V', v)."""
    s = phon.lower()
    s = s.replace("sh", "š").replace("ts", "ṣ")
    toks = []
    for ch in s:
        b = base(ch)
        if ch in LARYNGEAL or b in LARYNGEAL:
            toks.append(("H", "", ch))
        elif b in VOWELS:
            toks.append(("V", b))
        elif ch in m.CONSONANT_MAP:
            toks.append(("C", m.CONSONANT_MAP[ch], ch))
        elif b in m.CONSONANT_MAP:
            toks.append(("C", m.CONSONANT_MAP[b], ch))
        # everything else (digits, hyphens, marks) ignored
    # collapse geminates (same phoneme twice) and long vowels written twice
    out = []
    for t in toks:
        if out and t[0] in ("C", "H") and out[-1][0] == t[0] and out[-1][2] == t[2]:
            continue
        if out and t[0] == "V" and out[-1][0] == "V" and out[-1][1] == t[1]:
            continue
        out.append(t)
    return out


def lb_syllables(toks):
    """Apply Linear B spelling rules. Returns list of (class or '', vowel)."""
    syl = []
    i = 0
    n = len(toks)
    while i < n:
        t = toks[i]
        if t[0] == "V":
            syl.append(("", t[1]))
            i += 1
            continue
        cls = t[1]  # '' for laryngeal
        if i + 1 < n and toks[i + 1][0] == "V":
            syl.append((cls, toks[i + 1][1]))
            i += 2
            continue
        # consonant not followed by a vowel
        if i + 1 >= n:
            i += 1  # word-final consonant omitted
            continue
        if cls in CODA_DROP or cls == "":
            i += 1  # pre-consonantal r/l/m/n/s (and laryngeals) omitted
            continue
        # stop in a cluster: written with the vowel of the next syllable (dummy vowel)
        nxt = next((x[1] for x in toks[i + 1:] if x[0] == "V"), "a")
        syl.append((cls, nxt))
        i += 1
    return syl


# sign inventory from kaphtor's own sign values; weight by frequency in Linear A words
sign_freq = collections.Counter()
for rec in corpus.values():
    for w in rec.get("transliteratedWords") or []:
        for p in w.split("-"):
            p = p.strip().strip("[]").upper().replace("₂", "2").replace("₃", "3").replace("₄", "4")
            if p:
                sign_freq[p] += 1
inv = collections.defaultdict(list)  # (class, vowel) -> [(sign, weight)]
for s, info in sv["signs"].items():
    pr = info.get("primary") or {}
    v = (pr.get("vowel") or "")
    if len(v) != 1 or v not in VOWELS:
        continue
    cls = sign_map[s.upper()]
    key_s = s.upper().replace("₂", "2").replace("₃", "3").replace("₄", "4")
    wgt = sign_freq.get(key_s, 0) + sign_freq.get(s.upper(), 0) + 1
    if cls == "" and (pr.get("consonant") or "") not in ("", None):
        cls = ""  # laryngeal-valued sign (ḥa, ʿa, ha): skeleton-silent
    inv[(cls, v)].append((s.upper() if s.upper() in sign_map else s, wgt))


def pick(cls, v, rng):
    opts = inv.get((cls, v))
    if not opts:
        for v2 in "aieou":
            opts = inv.get((cls, v2))
            if opts:
                break
    if not opts:
        return None
    signs, wts = zip(*opts)
    return rng.choices(signs, weights=wts)[0]


def write_in_linear_a(phon, rng):
    syl = lb_syllables(tokenize(phon))
    out = []
    for cls, v in syl:
        s = pick(cls, v, rng)
        if s is None:
            return None
        out.append(s)
    return "-".join(out) if len(out) >= 3 else None


def amarna_phon(form):
    f = re.sub(r"\{[^}]*\}", "", form)
    f = re.sub(r"[₀-₉0-9]", "", f)
    parts = [p for p in f.split("-") if p]
    parts = [("y" + p[1:]) if p[:2] in ("ia", "iu", "ie") else p for p in parts]
    return "".join(parts)


rng = random.Random(2027)
amarna_rows = [json.loads(l) for l in open(K / "contact/amarna_canaanite.jsonl")]
akk_rows = [json.loads(l) for l in open(K / "contact/akkadian_lexicon.jsonl")]
heb_rows = [json.loads(l) for l in open(K / "contact/hebrew_lexicon.jsonl")]

# (a) Amarna exactly as the study projected (form string, no de-gemination), all lengths, unique forms
am_forms = sorted({r.get("form", "") for r in amarna_rows})
compare("Amarna Canaanite, study projection", [m.project_phoneme_string(f, False) for f in am_forms])

synthetic = {}
# (b) Amarna written in Linear A
synthetic["amarna"] = sorted({x for x in (write_in_linear_a(amarna_phon(f), rng) for f in am_forms) if x})
# (c) Akkadian normalized single-word lemmas
akk_forms = sorted({(r.get("normalized") or "") for r in akk_rows if r.get("normalized") and " " not in r["normalized"]})
synthetic["akkadian"] = sorted({x for x in (write_in_linear_a(f, rng) for f in akk_forms) if x})
# (d) Proto-Semitic stems (V -> a), first variant only
ps_forms = []
for r in semitic["roots"]:
    fs = m.parse_semitic_ps_variants(r.get("ps", ""))
    if fs:
        ps_forms.append(re.sub(r"[*\-]", "", r["ps"].split(",")[0].split("~")[0]).replace("V", "a"))
synthetic["proto_semitic_stems"] = sorted({x for x in (write_in_linear_a(f, rng) for f in ps_forms) if x})

for name, words in synthetic.items():
    sks = []
    for w in words:
        sk, ok = m.linear_a_word_to_skeleton(w, sign_map, False)
        if ok:
            sks.append(sk)
    compare(f"{name}, written in Linear A with kaphtor values", sks)
# (e) Hebrew consonantal lemmas, study projection, de-geminated
heb = sorted({r.get("normalized") or "" for r in heb_rows if r.get("normalized")})
compare("Hebrew lexicon consonantal (upper bound)", [re.sub(r"(.)\1", r"\1", m.project_phoneme_string(h, False)) for h in heb])

json.dump({k: v[:40] for k, v in synthetic.items()}, open(OUT / "synthetic_examples.json", "w"), ensure_ascii=False, indent=1)


# ---------- 2. power of the L=3 comparison ----------
def mde(n1, n2, p2, alpha, power=0.8):
    za = stats.norm.ppf(1 - alpha / 2)
    zb = stats.norm.ppf(power)
    for d in np.arange(0.001, 1 - p2, 0.001):
        p1 = p2 + d
        se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
        if d / se >= za + zb:
            return round(100 * d, 1)
    return None


pb = LB["L3"][0] / LB["L3"][1]
res["power_L3"] = {
    "LB_rate": round(pb, 4), "headroom_pp": round(100 * (1 - pb), 1),
    "mde_pp_all_n246_alpha05": mde(LA["L3"][1], LB["L3"][1], pb, 0.05),
    "mde_pp_all_n246_alpha01": mde(LA["L3"][1], LB["L3"][1], pb, 0.01),
    "mde_pp_heldout_n28_alpha05": mde(LAHO["L3"][1], LB["L3"][1], pb, 0.05),
    "mde_pp_heldout_n28_alpha01": mde(LAHO["L3"][1], LB["L3"][1], pb, 0.01),
    "L2_LB_rate": LB["L2"][0] / LB["L2"][1],
    "L4plus_LB_rate": round(LB["L4plus"][0] / LB["L4plus"][1], 4),
}

# ---------- 3. 27-sign shuffle with a planted truth ----------
def affected_list(words, regime="A1", drop_wy=False, root=SEM9):
    aff = []
    for w in words:
        parts = [p.strip().upper().replace("₂", "2").replace("₃", "3").replace("₄", "4") for p in w.split("-")]
        if any(p in novel for p in parts):
            sk, ok = m.linear_a_word_to_skeleton(w, sign_map, drop_wy=drop_wy)
            if ok and len(sk) >= 3:
                aff.append(w)
    return aff


t2 = {}
for name, words in synthetic.items():
    aff = affected_list(words)
    full = m.novel_sign_permutation_test([(w, 1) for w in aff], sign_map, novel, SEM9, "A1", False, 3, 1000, 99)
    det = {}
    r2 = random.Random(5)
    for n in (124, 25):
        if len(aff) < n:
            continue
        ps = []
        for rep in range(100):
            sub = r2.sample(aff, n)
            out = m.novel_sign_permutation_test([(w, 1) for w in sub], sign_map, novel, SEM9, "A1", False, 3, 300, 1000 + rep)
            ps.append(out["p_perm_novel"])
        ps = np.array(ps)
        det[f"n{n}"] = {"share_p_lt_0.05": float(np.mean(ps < 0.05)), "share_p_lt_0.01": float(np.mean(ps < 0.01)),
                        "median_p": float(np.median(ps))}
    # which novel signs carry the affected words?
    sc = collections.Counter()
    for w in aff:
        for p in set(w.split("-")):
            if p.upper().replace("₂", "2") in novel:
                sc[p] += 1
    t2[name] = {"n_affected": len(aff), "full": full, "subsample_detection": det, "novel_sign_use": sc.most_common(8)}
res["test2_planted_truth"] = t2

# real corpus: which novel signs drive the 124 affected words
real_aff = affected_list(list(la_counts))
sc = collections.Counter()
only_notational = 0
NOTATIONAL = {"JA", "JE", "RA2", "TA2", "PU₂", "PU2"}  # same value or same class as standard Linear B
for w in real_aff:
    ps_ = {p.upper().replace("₂", "2") for p in w.split("-")}
    nov_here = {p for p in ps_ if p in novel}
    for p in nov_here:
        sc[p] += 1
    if nov_here <= NOTATIONAL:
        only_notational += 1
res["real_affected_words"] = {"n": len(real_aff), "by_sign": sc.most_common(), "affected_only_by_JA_JE_RA2_TA2": only_notational}

# A1 test restricted to genuinely new or class-changing signs (drop JA, JE, RA2, TA2, PU2 from the shuffled set)
novel_strict = {s for s in novel if s not in NOTATIONAL and s != "PU₂"}
la_items = list(la_counts.items())
ho_items = [(w, c) for w, c in la_items if w not in lex_words]
res["test2_strict_novel_set"] = {
    "signs": sorted(novel_strict),
    "all_A1": m.novel_sign_permutation_test(la_items, sign_map, novel_strict, SEM9, "A1", False, 3, 1000, 51),
    "held_out_A1": m.novel_sign_permutation_test(ho_items, sign_map, novel_strict, SEM9, "A1", False, 3, 1000, 55),
}


# ---------- 4. A2 artifact check ----------
def a2_fair(items, n_perm=1000, seed=52):
    aff = []
    for w, _ in items:
        parts = [p.strip().upper().replace("₂", "2").replace("₃", "3").replace("₄", "4") for p in w.split("-")]
        if any(p in novel for p in parts):
            sk, ok = m.linear_a_word_to_skeleton(w, sign_map, drop_wy=True)
            if ok and len(sk) >= 3:
                aff.append(w)
    obs = np.mean([m.linear_a_word_to_skeleton(w, sign_map, True)[0] in SEM7 for w in aff])
    nl = sorted(novel)
    vals = [sign_map[s] for s in nl]
    rng = random.Random(seed)
    null_study, null_fair, null_samelen = [], [], []
    for _ in range(n_perm):
        sh = vals[:]
        rng.shuffle(sh)
        pm = dict(sign_map)
        pm.update(zip(nl, sh))
        hits = 0
        hits_f = 0
        n_f = 0
        hits_s = 0
        n_s = 0
        for w in aff:
            sk, _ = m.linear_a_word_to_skeleton(w, pm, True)
            hit = sk in SEM7
            if len(sk) >= 3:
                hits += hit
                hits_f += hit
                n_f += 1
            sk0, _ = m.linear_a_word_to_skeleton(w, sign_map, True)
            if len(sk) == len(sk0):
                hits_s += hit
                n_s += 1
        null_study.append(hits / len(aff))
        null_fair.append(hits_f / n_f if n_f else 0)
        null_samelen.append(hits_s / n_s if n_s else 0)
    out = {"n": len(aff), "obs": round(float(obs), 4)}
    for k, arr in (("null_as_study", null_study), ("null_only_words_still_ge3", null_fair), ("null_only_words_same_length", null_samelen)):
        arr = np.array(arr)
        out[k] = {"mean": round(float(arr.mean()), 4), "p": round(float((np.sum(arr >= obs) + 1) / (len(arr) + 1)), 4)}
    return out


res["test2_A2_artifact_check"] = {"all": a2_fair(la_items), "held_out": a2_fair(ho_items, seed=56)}

# ---------- 5. composition check ----------
la3 = LA["L3"]
la4 = LA["L4plus"]
lb3 = LB["L3"]
lb4 = LB["L4plus"]
share_lb3 = lb3[1] / (lb3[1] + lb4[1])
share_la3 = la3[1] / (la3[1] + la4[1])
res["composition"] = {
    "share_L3_LA": round(share_la3, 3), "share_L3_LB": round(share_lb3, 3),
    "LA_rate_standardised_to_LB_length_mix": round(share_lb3 * la3[0] / la3[1] + (1 - share_lb3) * la4[0] / la4[1], 4),
    "LB_rate": round((lb3[0] + lb4[0]) / (lb3[1] + lb4[1]), 4),
    "LA_rate": round((la3[0] + la4[0]) / (la3[1] + la4[1]), 4),
}

(OUT / "sensitivity.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
print(json.dumps(res, indent=1, ensure_ascii=False))
