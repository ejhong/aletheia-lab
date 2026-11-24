#!/usr/bin/env python3
"""Pre-registered Greek stylometry & pastiche audit for #15 (Secret Mark).

Implements Tests 0-5 from questions/secret-mark/protocol.md exactly as locked.
"""
from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
from pypdf import PdfReader
from scipy.optimize import minimize
from scipy.special import log_softmax, softmax

from fetch_data import (
    DATA_DIR,
    SOURCES,
    extract_greek_tokens,
    parse_morphgnt,
    parse_tei_xml,
    strip_diacritics_greek,
)

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
SEED = 20261124


def load_mar_saba_texts() -> dict[str, list[str]]:
    """Extract and segment the Mar Saba Letter Greek text directly from akma_SecretMark.pdf."""
    pdf_path = DATA_DIR / "akma_SecretMark.pdf"
    reader = PdfReader(str(pdf_path))
    pages = []
    for idx in [5, 7, 9, 11]:
        t = reader.pages[idx].extract_text()
        t = re.split(r"\na\.\s", t)[0]
        t = re.sub(r"LETTER OF CLEMENT TO THEODORE.*", "", t, flags=re.S)
        t = t.replace("Kαλῶς", "Καλῶς").replace("µ", "μ").replace("m", "γγ").replace("v", "λλ")
        t = re.sub(r"<[IVX]+>", " ", t)
        t = re.sub(r"[0-9]+", " ", t)
        t = re.sub(r"[a-zA-Z]+", " ", t)
        pages.append(t)
    full_tokens = extract_greek_tokens(" ".join(pages))

    def find_subseq(seq: list[str], sub: list[str], start: int = 0) -> int:
        n, m = len(seq), len(sub)
        for i in range(start, n - m + 1):
            if seq[i : i + m] == sub:
                return i
        raise ValueError(f"Subsequence not found: {' '.join(sub)}")

    # Heading: Folio I.1 (9 tokens)
    head_end = find_subseq(full_tokens, ["καλωσ", "εποιησασ"])
    heading = full_tokens[:head_end]
    body = full_tokens[head_end:]

    # Canonical Mark anchor 1a: ησαν δε εν τη οδω αναβαινοντεσ εισ ιεροσολυμα
    a1a_s = find_subseq(body, ["ησαν", "δε", "εν", "τη", "οδω"])
    a1a_e = find_subseq(body, ["ιεροσολυμα"], a1a_s) + 1
    # Canonical Mark anchor 1b: μετα τρεισ ημερασ αναστησεται
    a1b_s = find_subseq(body, ["μετα", "τρεισ", "ημερασ", "αναστησεται"], a1a_e)
    a1b_e = a1b_s + 4
    # Secret Mark Passage 1 (Bethany)
    sm1_s = find_subseq(body, ["και", "ερχονται", "εισ", "βηθανιαν"], a1b_e)
    sm1_e = find_subseq(body, ["περαν", "του", "ιορδανου"], sm1_s) + 3
    # Canonical Mark anchor 2: και προσεπορευοντο αυτω ιακωβοσ και ιωαννησ
    a2_s = find_subseq(body, ["και", "προσεπορευοντο", "αυτω"], sm1_e)
    a2_e = find_subseq(body, ["ιωαννησ"], a2_s) + 1
    # Canonical Mark anchor 3: και ερχεται εισ ιεριχω
    a3_s = find_subseq(body, ["και", "ερχεται", "εισ", "ιεριχω"], a2_e)
    a3_e = a3_s + 4
    # Secret Mark Passage 2 (Jericho)
    sm2_s = find_subseq(body, ["και", "ησαν", "εκει", "η", "αδελφη"], a3_e)
    sm2_e = find_subseq(body, ["απεδεξατο", "αυτασ", "ο", "ιησουσ"], sm2_s) + 4

    clement_frame = (
        body[:a1a_s]
        + body[a1a_e:a1b_s]
        + body[a1b_e:sm1_s]
        + body[sm1_e:a2_s]
        + body[a2_e:a3_s]
        + body[a3_e:sm2_s]
        + body[sm2_e:]
    )
    sm_bethany = body[sm1_s:sm1_e]
    sm_jericho = body[sm2_s:sm2_e]
    sm_quotes = sm_bethany + sm_jericho

    # Normalize primary MS/PV reading (AKMA main text has MS/PV except λεγουσιν [AT] -> λεγουσι [MS/PV]
    # and προσεπορευοντο [AT] -> προσπορευοντο [MS/PV], which is in anchor 2)
    clement_ms = ["λεγουσι" if w == "λεγουσιν" else w for w in clement_frame]

    # Tselikas (AT) sensitivity reading from Adam's apparatus
    clement_at = list(clement_frame)
    # Apply AT variants documented in Adam apparatus
    def replace_first(toks, old, new):
        out = list(toks)
        for i, w in enumerate(out):
            if w == old:
                out[i] = new
                break
        return out

    clement_at = replace_first(clement_at, "επιστομισασ", "επιστομισαι")
    clement_at = replace_first(clement_at, "τι", "το")
    # ταταυτου -> τα, ταυτου
    idx_t = clement_at.index("ταταυτου")
    clement_at = clement_at[:idx_t] + ["τα", "ταυτου"] + clement_at[idx_t + 1 :]
    clement_at = replace_first(clement_at, "δοξαν", "δοξα")
    clement_at = replace_first(clement_at, "γυμνοσ", "γυμνοι")

    return {
        "heading": heading,
        "full_no_heading": body,
        "clement_frame": clement_ms,
        "clement_frame_AT": clement_at,
        "secret_mark_bethany": sm_bethany,
        "secret_mark_jericho": sm_jericho,
        "secret_mark_quotes": sm_quotes,
    }


def load_corpora() -> dict[str, list[str]]:
    texts: dict[str, list[str]] = {}
    for src in SOURCES:
        ext = ".xml" if src["fmt"] == "tei" else ".txt"
        path = DATA_DIR / f"{src['id']}{ext}"
        raw_text = parse_tei_xml(path) if src["fmt"] == "tei" else parse_morphgnt(path)
        texts[src["id"]] = extract_greek_tokens(raw_text)
    return texts


def make_chunks(tokens: list[str], chunk_len: int) -> list[list[str]]:
    n = len(tokens) // chunk_len
    return [tokens[i * chunk_len : (i + 1) * chunk_len] for i in range(n)]


def sample_evenly(items: list, max_n: int) -> list:
    if len(items) <= max_n:
        return list(items)
    idx = np.linspace(0, len(items) - 1, max_n, dtype=int)
    return [items[i] for i in idx]


def char_ngrams_from_tokens(tokens: list[str], ns=(3, 4)) -> Counter:
    s = " " + " ".join(tokens) + " "
    c: Counter = Counter()
    for n in ns:
        for i in range(len(s) - n + 1):
            c[s[i : i + n]] += 1
    return c


def build_feature_vocab(
    chunks_by_author: dict[str, list[list[str]]],
    n_mfw: int = 150,
    n_char: int = 500,
    char_ns=(3, 4),
) -> tuple[list[str], list[str]]:
    """Build balanced MFW and char-ngram vocabularies across authors (mean relative frequency)."""
    word_rel_sum: Counter = Counter()
    char_rel_sum: Counter = Counter()
    n_authors = len(chunks_by_author)
    for author, chunks in chunks_by_author.items():
        wc = Counter()
        cc = Counter()
        for ch in chunks:
            wc.update(ch)
            cc.update(char_ngrams_from_tokens(ch, char_ns))
        wt = sum(wc.values()) or 1
        ct = sum(cc.values()) or 1
        for k, v in wc.items():
            word_rel_sum[k] += v / wt / n_authors
        for k, v in cc.items():
            char_rel_sum[k] += v / ct / n_authors
    mfw = [w for w, _ in word_rel_sum.most_common(n_mfw)]
    cng = [g for g, _ in char_rel_sum.most_common(n_char)]
    return mfw, cng


def vectorize_words(chunks: list[list[str]], vocab: list[str]) -> np.ndarray:
    idx = {w: i for i, w in enumerate(vocab)}
    X = np.zeros((len(chunks), len(vocab)), dtype=np.float64)
    for r, ch in enumerate(chunks):
        n = len(ch) or 1
        for w, cnt in Counter(ch).items():
            j = idx.get(w)
            if j is not None:
                X[r, j] = cnt / n
    return X


def vectorize_chars(chunks: list[list[str]], vocab: list[str], char_ns=(3, 4)) -> np.ndarray:
    idx = {g: i for i, g in enumerate(vocab)}
    X = np.zeros((len(chunks), len(vocab)), dtype=np.float64)
    for r, ch in enumerate(chunks):
        c = char_ngrams_from_tokens(ch, char_ns)
        tot = sum(c.values()) or 1
        for g, cnt in c.items():
            j = idx.get(g)
            if j is not None:
                X[r, j] = cnt / tot
    return X


def cosine_distance(u: np.ndarray, v: np.ndarray) -> float:
    nu = np.linalg.norm(u)
    nv = np.linalg.norm(v)
    if nu == 0.0 or nv == 0.0:
        return 1.0
    return float(1.0 - np.dot(u, v) / (nu * nv))


def zscore_fit(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = X.mean(axis=0)
    sd = X.std(axis=0, ddof=0)
    sd[sd < 1e-12] = 1.0
    return mu, sd


def zscore_transform(X: np.ndarray, mu: np.ndarray, sd: np.ndarray) -> np.ndarray:
    return (X - mu) / sd


def general_imposters_scores(
    target_z: np.ndarray,
    author_z_dict: dict[str, np.ndarray],
    n_iter: int = 500,
    feat_frac: float = 0.5,
    rng: np.random.Generator | None = None,
) -> dict[str, float]:
    """Koppel & Winter (2014) General Imposters: fraction of iterations each author is strictly closest."""
    if rng is None:
        rng = np.random.default_rng(SEED)
    authors = list(author_z_dict.keys())
    n_feat = target_z.shape[0]
    k_feat = max(1, int(round(n_feat * feat_frac)))
    wins = Counter({a: 0 for a in authors})
    for _ in range(n_iter):
        f_idx = rng.choice(n_feat, size=k_feat, replace=False)
        t_sub = target_z[f_idx]
        tn = np.linalg.norm(t_sub)
        best_a = None
        best_d = 1e9
        for a in authors:
            mat = author_z_dict[a]
            row = mat[rng.integers(0, mat.shape[0]), f_idx]
            rn = np.linalg.norm(row)
            d = 1.0 if (tn == 0 or rn == 0) else float(1.0 - np.dot(t_sub, row) / (tn * rn))
            if d < best_d:
                best_d = d
                best_a = a
        wins[best_a] += 1
    return {a: wins[a] / n_iter for a in authors}


def monroe_log_odds(
    c_target: Counter,
    c_other: Counter,
    alpha_0: float = 500.0,
) -> dict[str, tuple[float, float]]:
    """Monroe et al. (2008) informative Dirichlet-prior log-odds and z-score."""
    vocab = set(c_target.keys()) | set(c_other.keys())
    n_t = sum(c_target.values())
    n_o = sum(c_other.values())
    n_all = n_t + n_o
    out: dict[str, tuple[float, float]] = {}
    for w in vocab:
        y_t = c_target.get(w, 0)
        y_o = c_other.get(w, 0)
        # Informative background prior proportional to pooled frequency (floor > 0)
        alpha_w = alpha_0 * (y_t + y_o) / n_all
        if alpha_w <= 0:
            continue
        p_t = (y_t + alpha_w) / (n_t + alpha_0 - (y_t + alpha_w))
        p_o = (y_o + alpha_w) / (n_o + alpha_0 - (y_o + alpha_w))
        delta = math.log(p_t) - math.log(p_o)
        var = 1.0 / (y_t + alpha_w) + 1.0 / (y_o + alpha_w)
        z = delta / math.sqrt(var)
        out[w] = (delta, z)
    return out


def ngram_overlap_rates(
    tokens: list[str],
    ref_bigrams: set[tuple[str, str]],
    ref_trigrams: set[tuple[str, str, str]],
    stopwords: set[str],
) -> dict[str, float]:
    bgs = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]
    tgs = [(tokens[i], tokens[i + 1], tokens[i + 2]) for i in range(len(tokens) - 2)]
    c_bgs = [bg for bg in bgs if not (bg[0] in stopwords and bg[1] in stopwords)]
    c_tgs = [tg for tg in tgs if not (tg[0] in stopwords and tg[1] in stopwords and tg[2] in stopwords)]
    return {
        "all_bigram_rate": sum(1 for bg in bgs if bg in ref_bigrams) / max(1, len(bgs)),
        "all_trigram_rate": sum(1 for tg in tgs if tg in ref_trigrams) / max(1, len(tgs)),
        "content_bigram_rate": sum(1 for bg in c_bgs if bg in ref_bigrams) / max(1, len(c_bgs)),
        "content_trigram_rate": sum(1 for tg in c_tgs if tg in ref_trigrams) / max(1, len(c_tgs)),
        "n_bigrams": len(bgs),
        "n_trigrams": len(tgs),
        "n_content_bigrams": len(c_bgs),
        "n_content_trigrams": len(c_tgs),
    }


def stratified_kfold_splits(y: np.ndarray, n_splits: int = 5, seed: int = SEED):
    rng = np.random.default_rng(seed)
    folds: list[list[int]] = [[] for _ in range(n_splits)]
    for cls in sorted(set(y.tolist())):
        idx = np.where(y == cls)[0].copy()
        rng.shuffle(idx)
        for i, ix in enumerate(idx):
            folds[i % n_splits].append(int(ix))
    all_idx = set(range(len(y)))
    for k in range(n_splits):
        va = np.array(sorted(folds[k]), dtype=int)
        tr = np.array(sorted(all_idx - set(folds[k])), dtype=int)
        yield tr, va


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    classes = sorted(set(y_true.tolist()))
    f1s = []
    for c in classes:
        tp = int(np.sum((y_true == c) & (y_pred == c)))
        fp = int(np.sum((y_true != c) & (y_pred == c)))
        fn = int(np.sum((y_true == c) & (y_pred != c)))
        denom = 2 * tp + fp + fn
        f1s.append((2.0 * tp / denom) if denom > 0 else 0.0)
    return float(np.mean(f1s))


def tfidf_l2(X_counts: np.ndarray, idf: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    if idf is None:
        df = np.sum(X_counts > 0, axis=0)
        idf = np.log((1.0 + X_counts.shape[0]) / (1.0 + df)) + 1.0
    X_tf = X_counts * idf
    norms = np.linalg.norm(X_tf, axis=1, keepdims=True)
    norms[norms < 1e-12] = 1.0
    return X_tf / norms, idf


class BalancedMultinomialLogReg:
    """Exact L2-regularized multinomial logistic regression with balanced class weights (L-BFGS-B)."""

    def __init__(self, C: float = 1.0):
        self.C = C
        self.classes_: list[str] = []
        self.W_: np.ndarray | None = None
        self.b_: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.classes_ = sorted(set(y.tolist()))
        cls_to_i = {c: i for i, c in enumerate(self.classes_)}
        yi = np.array([cls_to_i[c] for c in y], dtype=int)
        n, d = X.shape
        K = len(self.classes_)
        counts = np.bincount(yi, minlength=K).astype(float)
        # Balanced sample weights matching sklearn: n / (K * count_k)
        sw = n / (K * counts[yi])
        Y_oh = np.zeros((n, K), dtype=float)
        Y_oh[np.arange(n), yi] = 1.0
        reg = 1.0 / self.C

        def loss_and_grad(params: np.ndarray):
            W = params[: K * d].reshape(K, d)
            b = params[K * d :]
            logits = X @ W.T + b
            logp = log_softmax(logits, axis=1)
            probs = np.exp(logp)
            loss = -np.sum(sw * logp[np.arange(n), yi]) + 0.5 * reg * np.sum(W * W)
            diff = (probs - Y_oh) * sw[:, None]
            gW = diff.T @ X + reg * W
            gb = diff.sum(axis=0)
            return float(loss), np.concatenate([gW.ravel(), gb])

        res = minimize(loss_and_grad, np.zeros(K * d + K), method="L-BFGS-B", jac=True, options={"maxiter": 500})
        self.W_ = res.x[: K * d].reshape(K, d)
        self.b_ = res.x[K * d :]
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        logits = X @ self.W_.T + self.b_
        return softmax(logits, axis=1)

    def predict(self, X: np.ndarray) -> np.ndarray:
        p = self.predict_proba(X)
        return np.array([self.classes_[i] for i in np.argmax(p, axis=1)])


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    ms = load_mar_saba_texts()
    corpora = load_corpora()

    L_A = len(ms["clement_frame"])
    L_B = len(ms["secret_mark_quotes"])
    print(f"Mar Saba segmentation: heading={len(ms['heading'])}, Layer A (Clement frame)={L_A}, "
          f"Layer A (AT)={len(ms['clement_frame_AT'])}, full_no_heading={len(ms['full_no_heading'])}, "
          f"Layer B (Secret Mark)={L_B} (Bethany={len(ms['secret_mark_bethany'])}, Jericho={len(ms['secret_mark_jericho'])})")

    # Group tokens by author for the 14-author panel
    author_tokens_train: dict[str, list[list[str]]] = {}
    author_raw_tokens: dict[str, list[str]] = {}
    for src in SOURCES:
        if src["role"] in ("target_author", "comparison"):
            author_raw_tokens.setdefault(src["author"], []).extend(corpora[src["id"]])

    # Chunk each author into L_A-token non-overlapping chunks (up to 40 evenly spaced for balanced training)
    all_author_chunks: dict[str, list[list[str]]] = {}
    balanced_chunks: dict[str, list[list[str]]] = {}
    for author, toks in author_raw_tokens.items():
        chs = make_chunks(toks, L_A)
        all_author_chunks[author] = chs
        balanced_chunks[author] = sample_evenly(chs, 40)

    authors = sorted(balanced_chunks.keys())
    print(f"14-author panel: {len(authors)} authors; training chunks per author: "
          f"min={min(len(v) for v in balanced_chunks.values())}, max={max(len(v) for v in balanced_chunks.values())}")

    # Build MFW-150 and C34-500 vocabularies on balanced training set
    mfw150, c34_500 = build_feature_vocab(balanced_chunks, n_mfw=150, n_char=500)

    # Flatten balanced training matrix
    X_mfw_list, X_c34_list, y_labels = [], [], []
    for a in authors:
        chs = balanced_chunks[a]
        X_mfw_list.append(vectorize_words(chs, mfw150))
        X_c34_list.append(vectorize_chars(chs, c34_500))
        y_labels.extend([a] * len(chs))
    X_mfw_train = np.vstack(X_mfw_list)
    X_c34_train = np.vstack(X_c34_list)
    y_train = np.array(y_labels)

    mu_mfw, sd_mfw = zscore_fit(X_mfw_train)
    mu_c34, sd_c34 = zscore_fit(X_c34_train)
    Z_mfw_train = zscore_transform(X_mfw_train, mu_mfw, sd_mfw)
    Z_c34_train = zscore_transform(X_c34_train, mu_c34, sd_c34)
    Z_comb_train = np.hstack([Z_mfw_train, Z_c34_train])

    # Author centroids & chunk dicts
    centroids_mfw = {a: Z_mfw_train[y_train == a].mean(axis=0) for a in authors}
    centroids_c34 = {a: Z_c34_train[y_train == a].mean(axis=0) for a in authors}
    centroids_comb = {a: Z_comb_train[y_train == a].mean(axis=0) for a in authors}
    author_z_comb = {a: Z_comb_train[y_train == a] for a in authors}

    # --- TF-IDF + Logistic Regression (Method 4: MFW-150 + top 1000 char 3-4-grams) ---
    _, c34_1000 = build_feature_vocab(balanced_chunks, n_mfw=150, n_char=1000)
    X_c34_1000_train = np.vstack([vectorize_chars(balanced_chunks[a], c34_1000) for a in authors])
    Xw_tf_train, idf_w = tfidf_l2(X_mfw_train)
    Xc_tf_train, idf_c = tfidf_l2(X_c34_1000_train)
    X_tf_train = np.hstack([Xw_tf_train, Xc_tf_train])

    clf = BalancedMultinomialLogReg(C=1.0).fit(X_tf_train, y_train)

    # =========================================================================
    # TEST 0: CALIBRATION GATE (5-fold CV + Held-out Clement + Known Forgeries)
    # =========================================================================
    cv_preds_mfw = np.empty_like(y_train)
    cv_preds_c34 = np.empty_like(y_train)
    cv_preds_lr = np.empty_like(y_train)
    for tr, va in stratified_kfold_splits(y_train, n_splits=5, seed=SEED):
        # MFW Cosine Delta
        mu_f, sd_f = zscore_fit(X_mfw_train[tr])
        Ztr_f = zscore_transform(X_mfw_train[tr], mu_f, sd_f)
        Zva_f = zscore_transform(X_mfw_train[va], mu_f, sd_f)
        cf = {a: Ztr_f[y_train[tr] == a].mean(axis=0) for a in authors}
        for i_loc, i_gl in enumerate(va):
            cv_preds_mfw[i_gl] = min(authors, key=lambda a: cosine_distance(Zva_f[i_loc], cf[a]))
        # C34 Cosine Delta
        mu_c, sd_c = zscore_fit(X_c34_train[tr])
        Ztr_c = zscore_transform(X_c34_train[tr], mu_c, sd_c)
        Zva_c = zscore_transform(X_c34_train[va], mu_c, sd_c)
        cc = {a: Ztr_c[y_train[tr] == a].mean(axis=0) for a in authors}
        for i_loc, i_gl in enumerate(va):
            cv_preds_c34[i_gl] = min(authors, key=lambda a: cosine_distance(Zva_c[i_loc], cc[a]))
        # Logistic Regression (fit IDF strictly on training fold!)
        Xtr_w, idf_w_f = tfidf_l2(X_mfw_train[tr])
        Xva_w, _ = tfidf_l2(X_mfw_train[va], idf_w_f)
        Xtr_c, idf_c_f = tfidf_l2(X_c34_1000_train[tr])
        Xva_c, _ = tfidf_l2(X_c34_1000_train[va], idf_c_f)
        clf_cv = BalancedMultinomialLogReg(C=1.0).fit(np.hstack([Xtr_w, Xtr_c]), y_train[tr])
        cv_preds_lr[va] = clf_cv.predict(np.hstack([Xva_w, Xva_c]))

    cv_metrics = {
        "mfw150_cosine_delta_macro_f1": macro_f1(y_train, cv_preds_mfw),
        "mfw150_cosine_delta_acc": float((cv_preds_mfw == y_train).mean()),
        "c34_500_cosine_delta_macro_f1": macro_f1(y_train, cv_preds_c34),
        "c34_500_cosine_delta_acc": float((cv_preds_c34 == y_train).mean()),
        "logreg_tfidf_macro_f1": macro_f1(y_train, cv_preds_lr),
        "logreg_tfidf_acc": float((cv_preds_lr == y_train).mean()),
    }

    def evaluate_chunks_panel(chunks: list[list[str]], run_gi: bool = True) -> list[dict]:
        Xm = vectorize_words(chunks, mfw150)
        Xc = vectorize_chars(chunks, c34_500)
        Xc1000 = vectorize_chars(chunks, c34_1000)
        Zm = zscore_transform(Xm, mu_mfw, sd_mfw)
        Zc = zscore_transform(Xc, mu_c34, sd_c34)
        Zcomb = np.hstack([Zm, Zc])
        Xw_t, _ = tfidf_l2(Xm, idf_w)
        Xc_t, _ = tfidf_l2(Xc1000, idf_c)
        Xtf = np.hstack([Xw_t, Xc_t])
        probs = clf.predict_proba(Xtf)
        classes = list(clf.classes_)

        out = []
        for i in range(len(chunks)):
            d_mfw = {a: cosine_distance(Zm[i], centroids_mfw[a]) for a in authors}
            d_c34 = {a: cosine_distance(Zc[i], centroids_c34[a]) for a in authors}
            d_comb = {a: cosine_distance(Zcomb[i], centroids_comb[a]) for a in authors}
            p_lr = {classes[j]: float(probs[i, j]) for j in range(len(classes))}
            gi = general_imposters_scores(Zcomb[i], author_z_comb, n_iter=500, rng=rng) if run_gi else {}
            out.append({
                "mfw_dist": d_mfw,
                "mfw_top": min(d_mfw, key=d_mfw.get),
                "c34_dist": d_c34,
                "c34_top": min(d_c34, key=d_c34.get),
                "comb_dist": d_comb,
                "comb_top": min(d_comb, key=d_comb.get),
                "lr_prob": p_lr,
                "lr_top": max(p_lr, key=p_lr.get),
                "gi_score": gi,
                "gi_top": max(gi, key=gi.get) if gi else None,
            })
        return out

    # Held-out positive controls & mixed/forgery controls
    qd_chunks = make_chunks(corpora["clement_quis_dives"], L_A)
    ec_chunks = make_chunks(corpora["clement_eclogae"], L_A)
    ex_chunks = make_chunks(corpora["clement_excerpta_theodoto"], L_A)
    ps_ath_chunks = make_chunks(corpora["pseudo_athanasius_or4"], L_A)

    qd_eval = evaluate_chunks_panel(qd_chunks, run_gi=True)
    ec_eval = evaluate_chunks_panel(ec_chunks, run_gi=True)
    ex_eval = evaluate_chunks_panel(ex_chunks, run_gi=True)
    ps_ath_eval = evaluate_chunks_panel(ps_ath_chunks, run_gi=True)

    # Calibrate GI(Clement) 95%-specificity threshold using 130 non-Clement chunks (10 per non-Clement author)
    non_clem_gi_scores = []
    for a in authors:
        if a == "Clement of Alexandria":
            continue
        chs = sample_evenly(all_author_chunks[a], 10)
        ev = evaluate_chunks_panel(chs, run_gi=True)
        for r in ev:
            non_clem_gi_scores.append(r["gi_score"]["Clement of Alexandria"])
    gi_95_thresh = float(np.quantile(non_clem_gi_scores, 0.95))
    gi_max_nonclem = float(np.max(non_clem_gi_scores))

    # Pairwise forgery controls for Ignatius (2c) vs Pseudo-Ignatius (4c) and 1 Clement vs 2 Clement
    def pairwise_forgery_check(gen_id: str, fake_id: str, label: str) -> dict:
        gen_ch = make_chunks(corpora[gen_id], L_A)
        fake_ch = make_chunks(corpora[fake_id], L_A)
        Xm_g = zscore_transform(vectorize_words(gen_ch, mfw150), mu_mfw, sd_mfw)
        Xc_g = zscore_transform(vectorize_chars(gen_ch, c34_500), mu_c34, sd_c34)
        Zg = np.hstack([Xm_g, Xc_g])
        Xm_f = zscore_transform(vectorize_words(fake_ch, mfw150), mu_mfw, sd_mfw)
        Xc_f = zscore_transform(vectorize_chars(fake_ch, c34_500), mu_c34, sd_c34)
        Zf = np.hstack([Xm_f, Xc_f])
        # Leave-one-out self-distances for genuine
        gen_dists = []
        for i in range(len(Zg)):
            c_loo = np.delete(Zg, i, axis=0).mean(axis=0)
            gen_dists.append(cosine_distance(Zg[i], c_loo))
        c_gen = Zg.mean(axis=0)
        fake_dists = [cosine_distance(Zf[i], c_gen) for i in range(len(Zf))]
        pct_above_95 = float(np.mean([d > np.quantile(gen_dists, 0.95) for d in fake_dists]))
        return {
            "pair": label,
            "n_genuine_chunks": len(gen_ch),
            "n_forgery_chunks": len(fake_ch),
            "genuine_median_dist": float(np.median(gen_dists)),
            "genuine_p95_dist": float(np.quantile(gen_dists, 0.95)),
            "forgery_median_dist": float(np.median(fake_dists)),
            "forgery_mean_percentile_in_genuine": float(np.mean([np.mean(np.array(gen_dists) <= d) for d in fake_dists])),
            "forgery_frac_above_genuine_p95": pct_above_95,
        }

    # Pseudo-Athanasius vs Athanasius self-distance
    ath_ch = all_author_chunks["Athanasius of Alexandria"]
    ath_Zm = zscore_transform(vectorize_words(ath_ch, mfw150), mu_mfw, sd_mfw)
    ath_Zc = zscore_transform(vectorize_chars(ath_ch, c34_500), mu_c34, sd_c34)
    ath_Z = np.hstack([ath_Zm, ath_Zc])
    ath_loo_dists = [cosine_distance(ath_Z[i], np.delete(ath_Z, i, axis=0).mean(axis=0)) for i in range(len(ath_Z))]
    ath_cent = ath_Z.mean(axis=0)
    ps_ath_Z = np.hstack([
        zscore_transform(vectorize_words(ps_ath_chunks, mfw150), mu_mfw, sd_mfw),
        zscore_transform(vectorize_chars(ps_ath_chunks, c34_500), mu_c34, sd_c34),
    ])
    ps_ath_dists = [cosine_distance(ps_ath_Z[i], ath_cent) for i in range(len(ps_ath_Z))]
    forgery_controls = [
        {
            "pair": "Pseudo-Athanasius Or. IV vs. Athanasius",
            "n_genuine_chunks": len(ath_ch),
            "n_forgery_chunks": len(ps_ath_chunks),
            "genuine_median_dist": float(np.median(ath_loo_dists)),
            "genuine_p95_dist": float(np.quantile(ath_loo_dists, 0.95)),
            "forgery_median_dist": float(np.median(ps_ath_dists)),
            "forgery_mean_percentile_in_genuine": float(np.mean([np.mean(np.array(ath_loo_dists) <= d) for d in ps_ath_dists])),
            "forgery_frac_above_genuine_p95": float(np.mean([d > np.quantile(ath_loo_dists, 0.95) for d in ps_ath_dists])),
            "panel_attributed_to_athanasius_mfw": float(np.mean([r["mfw_top"] == "Athanasius of Alexandria" for r in ps_ath_eval])),
            "panel_attributed_to_athanasius_c34": float(np.mean([r["c34_top"] == "Athanasius of Alexandria" for r in ps_ath_eval])),
            "panel_attributed_to_athanasius_lr": float(np.mean([r["lr_top"] == "Athanasius of Alexandria" for r in ps_ath_eval])),
            "panel_attributed_to_athanasius_gi": float(np.mean([r["gi_top"] == "Athanasius of Alexandria" for r in ps_ath_eval])),
        },
        pairwise_forgery_check("ignatius_genuine", "pseudo_ignatius", "Pseudo-Ignatius vs. Genuine Ignatius"),
        pairwise_forgery_check("clement_rome_1", "pseudo_clement_rome_2", "2 Clement vs. 1 Clement"),
    ]

    # =========================================================================
    # TEST 1 & TEST 4: MAR SABA LAYER A ATTRIBUTION & 14-AUTHOR RANKING
    # =========================================================================
    ms_variants = {
        "clement_frame": ms["clement_frame"],
        "clement_frame_AT": ms["clement_frame_AT"],
        "full_no_heading": ms["full_no_heading"],
    }
    test1_results = {}
    for name, toks in ms_variants.items():
        res = evaluate_chunks_panel([toks], run_gi=True)[0]
        # Build clean ranked tables
        rank_mfw = sorted(res["mfw_dist"].items(), key=lambda kv: kv[1])
        rank_c34 = sorted(res["c34_dist"].items(), key=lambda kv: kv[1])
        rank_comb = sorted(res["comb_dist"].items(), key=lambda kv: kv[1])
        rank_gi = sorted(res["gi_score"].items(), key=lambda kv: -kv[1])
        rank_lr = sorted(res["lr_prob"].items(), key=lambda kv: -kv[1])
        test1_results[name] = {
            "n_tokens": len(toks),
            "mfw_top": res["mfw_top"],
            "c34_top": res["c34_top"],
            "comb_top": res["comb_top"],
            "gi_top": res["gi_top"],
            "lr_top": res["lr_top"],
            "clement_rank_mfw": [a for a, _ in rank_mfw].index("Clement of Alexandria") + 1,
            "clement_rank_c34": [a for a, _ in rank_c34].index("Clement of Alexandria") + 1,
            "clement_rank_comb": [a for a, _ in rank_comb].index("Clement of Alexandria") + 1,
            "clement_rank_gi": [a for a, _ in rank_gi].index("Clement of Alexandria") + 1,
            "clement_rank_lr": [a for a, _ in rank_lr].index("Clement of Alexandria") + 1,
            "clement_gi_score": res["gi_score"]["Clement of Alexandria"],
            "clement_lr_prob": res["lr_prob"]["Clement of Alexandria"],
            "rank_mfw": rank_mfw,
            "rank_c34": rank_c34,
            "rank_comb": rank_comb,
            "rank_gi": rank_gi,
            "rank_lr": rank_lr,
        }

    # =========================================================================
    # TEST 2: ONE-CLASS "INSIDE AUTHENTIC CLEMENT?" SELF-DISTANCE TEST
    # + Test 4b: One-class percentile inside every one of the 14 authors!
    # =========================================================================
    clem_all_train_chunks = all_author_chunks["Clement of Alexandria"]
    clem_Zm = zscore_transform(vectorize_words(clem_all_train_chunks, mfw150), mu_mfw, sd_mfw)
    clem_Zc = zscore_transform(vectorize_chars(clem_all_train_chunks, c34_500), mu_c34, sd_c34)
    clem_Zcomb = np.hstack([clem_Zm, clem_Zc])

    # Leave-one-chunk-out distances to Clement training centroid
    clem_sum_m = clem_Zm.sum(axis=0)
    clem_sum_c = clem_Zc.sum(axis=0)
    clem_sum_cb = clem_Zcomb.sum(axis=0)
    n_ct = len(clem_all_train_chunks)
    clem_loo_m = np.array([cosine_distance(clem_Zm[i], (clem_sum_m - clem_Zm[i]) / (n_ct - 1)) for i in range(n_ct)])
    clem_loo_c = np.array([cosine_distance(clem_Zc[i], (clem_sum_c - clem_Zc[i]) / (n_ct - 1)) for i in range(n_ct)])
    clem_loo_cb = np.array([cosine_distance(clem_Zcomb[i], (clem_sum_cb - clem_Zcomb[i]) / (n_ct - 1)) for i in range(n_ct)])

    clem_cent_m = clem_Zm.mean(axis=0)
    clem_cent_c = clem_Zc.mean(axis=0)
    clem_cent_cb = clem_Zcomb.mean(axis=0)

    def clem_oneclass_eval(chunks: list[list[str]]) -> dict:
        Zm = zscore_transform(vectorize_words(chunks, mfw150), mu_mfw, sd_mfw)
        Zc = zscore_transform(vectorize_chars(chunks, c34_500), mu_c34, sd_c34)
        Zcb = np.hstack([Zm, Zc])
        dm = [cosine_distance(Zm[i], clem_cent_m) for i in range(len(chunks))]
        dc = [cosine_distance(Zc[i], clem_cent_c) for i in range(len(chunks))]
        dcb = [cosine_distance(Zcb[i], clem_cent_cb) for i in range(len(chunks))]
        return {
            "n_chunks": len(chunks),
            "mfw_dist_median": float(np.median(dm)),
            "mfw_pct_median": float(np.median([np.mean(clem_loo_m <= d) for d in dm])),
            "c34_dist_median": float(np.median(dc)),
            "c34_pct_median": float(np.median([np.mean(clem_loo_c <= d) for d in dc])),
            "comb_dist_median": float(np.median(dcb)),
            "comb_pct_median": float(np.median([np.mean(clem_loo_cb <= d) for d in dcb])),
            "comb_dists": [float(x) for x in dcb],
        }

    # Test 4b: Mar Saba percentile inside EVERY author's own LOO chunk distribution
    ms_Zm = zscore_transform(vectorize_words([ms["clement_frame"]], mfw150), mu_mfw, sd_mfw)[0]
    ms_Zc = zscore_transform(vectorize_chars([ms["clement_frame"]], c34_500), mu_c34, sd_c34)[0]
    ms_Zcb = np.hstack([ms_Zm, ms_Zc])

    per_author_oneclass = []
    for a in authors:
        chs = all_author_chunks[a]
        Zm_a = zscore_transform(vectorize_words(chs, mfw150), mu_mfw, sd_mfw)
        Zc_a = zscore_transform(vectorize_chars(chs, c34_500), mu_c34, sd_c34)
        Zcb_a = np.hstack([Zm_a, Zc_a])
        na = len(chs)
        s_a = Zcb_a.sum(axis=0)
        loo_a = np.array([cosine_distance(Zcb_a[i], (s_a - Zcb_a[i]) / (na - 1)) for i in range(na)])
        d_ms = cosine_distance(ms_Zcb, Zcb_a.mean(axis=0))
        pct_ms = float(np.mean(loo_a <= d_ms))
        per_author_oneclass.append({
            "author": a,
            "n_chunks": na,
            "author_self_median_dist": float(np.median(loo_a)),
            "author_self_p95_dist": float(np.quantile(loo_a, 0.95)),
            "mar_saba_dist": d_ms,
            "mar_saba_percentile": pct_ms,
        })
    per_author_oneclass.sort(key=lambda r: r["mar_saba_percentile"])

    test2_results = {
        "clement_train_n_chunks": n_ct,
        "clement_train_mfw_quantiles": {q: float(np.quantile(clem_loo_m, q)) for q in [0.05, 0.25, 0.5, 0.75, 0.90, 0.95]},
        "clement_train_c34_quantiles": {q: float(np.quantile(clem_loo_c, q)) for q in [0.05, 0.25, 0.5, 0.75, 0.90, 0.95]},
        "clement_train_comb_quantiles": {q: float(np.quantile(clem_loo_cb, q)) for q in [0.05, 0.25, 0.5, 0.75, 0.90, 0.95]},
        "mar_saba_clement_frame": clem_oneclass_eval([ms["clement_frame"]]),
        "mar_saba_clement_frame_AT": clem_oneclass_eval([ms["clement_frame_AT"]]),
        "mar_saba_full_no_heading": clem_oneclass_eval([ms["full_no_heading"]]),
        "heldout_quis_dives": clem_oneclass_eval(qd_chunks),
        "heldout_eclogae": clem_oneclass_eval(ec_chunks),
        "mixed_excerpta_theodoto": clem_oneclass_eval(ex_chunks),
        "per_author_oneclass": per_author_oneclass,
        "clement_loo_comb_dists": [float(x) for x in clem_loo_cb],
    }

    # =========================================================================
    # TEST 3: HYPER-CLEMENTINE LEXICAL PACKING & CRIDDLE (1995) RARE-WORD RATIO
    # =========================================================================
    mfw150_set = set(mfw150)
    clem_content_counts = Counter(w for w in author_raw_tokens["Clement of Alexandria"] if w not in mfw150_set)
    other_content_counts = Counter()
    for a in authors:
        if a != "Clement of Alexandria":
            other_content_counts.update(w for w in author_raw_tokens[a] if w not in mfw150_set)

    # Full-corpus Monroe log-odds (used for held-out works and Mar Saba)
    lo_full = monroe_log_odds(clem_content_counts, other_content_counts, alpha_0=500.0)

    def lexical_metrics_for_chunk(
        chunk: list[str],
        clem_ref_counts: Counter,
        other_ref_counts: Counter,
        lo_map: dict[str, tuple[float, float]],
    ) -> dict:
        ctoks = [w for w in chunk if w not in mfw150_set]
        utypes = set(ctoks)
        n_ctok = len(ctoks)
        n_utype = len(utypes)
        # 3a. Monroe log-odds (for words in lo_map; unseen words assigned 0.0 neutral)
        lo_vals = [lo_map[w][0] if w in lo_map else 0.0 for w in ctoks]
        z_high = sum(1 for w in utypes if w in lo_map and lo_map[w][1] > 2.0)
        # 3b. Criddle rare-to-common ratio & Clement-exclusivity
        c0 = sum(1 for w in utypes if clem_ref_counts.get(w, 0) == 0)
        c1 = sum(1 for w in utypes if clem_ref_counts.get(w, 0) == 1)
        c2p = sum(1 for w in utypes if clem_ref_counts.get(w, 0) >= 2)
        c_excl = sum(1 for w in utypes if clem_ref_counts.get(w, 0) >= 1 and other_ref_counts.get(w, 0) == 0)
        c_excl_hapax = sum(1 for w in utypes if clem_ref_counts.get(w, 0) == 1 and other_ref_counts.get(w, 0) == 0)
        return {
            "n_content_tokens": n_ctok,
            "n_unique_content": n_utype,
            "mean_monroe_log_odds": float(np.mean(lo_vals)) if lo_vals else 0.0,
            "frac_high_z_types": z_high / max(1, n_utype),
            "c0": c0,
            "c1": c1,
            "c2p": c2p,
            "r_criddle": c1 / max(1, c1 + c2p),
            "f_unseen_in_clement": c0 / max(1, n_utype),
            "c_excl": c_excl,
            "f_clement_exclusive": c_excl / max(1, n_utype),
            "c_excl_hapax": c_excl_hapax,
        }

    # Evaluate authentic Clement training chunks with STRICT leave-one-chunk-out subtraction!
    clem_loo_lex = []
    for ch in clem_all_train_chunks:
        ch_counts = Counter(w for w in ch if w not in mfw150_set)
        # Subtract this chunk from clem_content_counts
        ref_minus = clem_content_counts.copy()
        for w, cnt in ch_counts.items():
            ref_minus[w] -= cnt
            if ref_minus[w] <= 0:
                del ref_minus[w]
        # Fast local Monroe log-odds only for words in this chunk (exact match to full formula!)
        n_t_m = sum(ref_minus.values())
        n_o_m = sum(other_content_counts.values())
        n_all_m = n_t_m + n_o_m
        lo_local = {}
        for w in ch_counts:
            yt = ref_minus.get(w, 0)
            yo = other_content_counts.get(w, 0)
            if yt + yo == 0:
                continue
            aw = 500.0 * (yt + yo) / n_all_m
            pt = (yt + aw) / (n_t_m + 500.0 - (yt + aw))
            po = (yo + aw) / (n_o_m + 500.0 - (yo + aw))
            delta = math.log(pt) - math.log(po)
            z = delta / math.sqrt(1.0 / (yt + aw) + 1.0 / (yo + aw))
            lo_local[w] = (delta, z)
        clem_loo_lex.append(lexical_metrics_for_chunk(ch, ref_minus, other_content_counts, lo_local))

    qd_lex = [lexical_metrics_for_chunk(ch, clem_content_counts, other_content_counts, lo_full) for ch in qd_chunks]
    ec_lex = [lexical_metrics_for_chunk(ch, clem_content_counts, other_content_counts, lo_full) for ch in ec_chunks]
    ms_lex = lexical_metrics_for_chunk(ms["clement_frame"], clem_content_counts, other_content_counts, lo_full)
    ms_lex_at = lexical_metrics_for_chunk(ms["clement_frame_AT"], clem_content_counts, other_content_counts, lo_full)

    # Also compute non-Clement comparison baseline for lexical metrics (10 chunks per non-Clement author)
    nonclem_lex = []
    for a in authors:
        if a == "Clement of Alexandria":
            continue
        for ch in sample_evenly(all_author_chunks[a], 10):
            nonclem_lex.append(lexical_metrics_for_chunk(ch, clem_content_counts, other_content_counts, lo_full))

    def summarize_against_ref(ms_val: float, ref_vals: list[float]) -> dict:
        arr = np.array(ref_vals, dtype=float)
        mu, sd = float(arr.mean()), float(arr.std(ddof=1))
        z = (ms_val - mu) / sd if sd > 0 else 0.0
        pct = float(np.mean(arr <= ms_val))
        p_two = float(2.0 * min(np.mean(arr <= ms_val), np.mean(arr >= ms_val)))
        return {
            "mar_saba": float(ms_val),
            "ref_mean": mu,
            "ref_sd": sd,
            "ref_median": float(np.median(arr)),
            "ref_p05": float(np.quantile(arr, 0.05)),
            "ref_p95": float(np.quantile(arr, 0.95)),
            "z_score": float(z),
            "percentile": pct,
            "p_two_sided": min(1.0, p_two),
        }

    # Combine all authentic Clement reference chunks (LOO training + held-out Quis dives + Eclogae)
    all_auth_clem_lex = clem_loo_lex + qd_lex + ec_lex
    lex_keys = ["mean_monroe_log_odds", "frac_high_z_types", "r_criddle", "f_unseen_in_clement", "f_clement_exclusive"]
    test3_summary = {
        "mar_saba_raw": ms_lex,
        "mar_saba_AT_raw": ms_lex_at,
        "n_ref_clement_all": len(all_auth_clem_lex),
        "n_ref_clement_heldout_qd_ec": len(qd_lex) + len(ec_lex),
        "vs_all_authentic_clement": {
            k: summarize_against_ref(ms_lex[k], [r[k] for r in all_auth_clem_lex]) for k in lex_keys
        },
        "vs_heldout_qd_ec": {
            k: summarize_against_ref(ms_lex[k], [r[k] for r in (qd_lex + ec_lex)]) for k in lex_keys
        },
        "non_clement_medians": {k: float(np.median([r[k] for r in nonclem_lex])) for k in lex_keys},
        "clement_ref_distributions": {k: [float(r[k]) for r in all_auth_clem_lex] for k in lex_keys},
    }

    # =========================================================================
    # TEST 5: LAYER B — SECRET MARK QUOTATIONS VS CANONICAL GOSPELS & CLEMENT
    # =========================================================================
    gospel_sources = {
        "Mark": corpora["gospel_mark"],
        "Matthew": corpora["gospel_matthew"],
        "Luke": corpora["gospel_luke"],
        "John": corpora["gospel_john"],
        "Clement": author_raw_tokens["Clement of Alexandria"],
    }
    g_chunks_all = {k: make_chunks(v, L_B) for k, v in gospel_sources.items()}
    g_chunks_bal = {k: sample_evenly(v, 60) for k, v in g_chunks_all.items()}
    g_authors = sorted(g_chunks_bal.keys())

    g_mfw100, g_c34_400 = build_feature_vocab(g_chunks_bal, n_mfw=100, n_char=400)
    gXm_l, gXc_l, gy_l = [], [], []
    for a in g_authors:
        gXm_l.append(vectorize_words(g_chunks_bal[a], g_mfw100))
        gXc_l.append(vectorize_chars(g_chunks_bal[a], g_c34_400))
        gy_l.extend([a] * len(g_chunks_bal[a]))
    gXm = np.vstack(gXm_l)
    gXc = np.vstack(gXc_l)
    gy = np.array(gy_l)
    g_mu_m, g_sd_m = zscore_fit(gXm)
    g_mu_c, g_sd_c = zscore_fit(gXc)
    gZm = zscore_transform(gXm, g_mu_m, g_sd_m)
    gZc = zscore_transform(gXc, g_mu_c, g_sd_c)
    gZcb = np.hstack([gZm, gZc])
    g_cent_m = {a: gZm[gy == a].mean(axis=0) for a in g_authors}
    g_cent_c = {a: gZc[gy == a].mean(axis=0) for a in g_authors}
    g_cent_cb = {a: gZcb[gy == a].mean(axis=0) for a in g_authors}
    g_z_dict = {a: gZcb[gy == a] for a in g_authors}

    # Quick CV accuracy on 5-way L_B-token chunks (Mark/Mt/Lk/Jn/Clement)
    g_cv_pred = np.empty_like(gy)
    for tr, va in stratified_kfold_splits(gy, n_splits=5, seed=SEED):
        mm, sm = zscore_fit(gXm[tr])
        mc, sc = zscore_fit(gXc[tr])
        Ztr = np.hstack([zscore_transform(gXm[tr], mm, sm), zscore_transform(gXc[tr], mc, sc)])
        Zva = np.hstack([zscore_transform(gXm[va], mm, sm), zscore_transform(gXc[va], mc, sc)])
        ct = {a: Ztr[gy[tr] == a].mean(axis=0) for a in g_authors}
        for il, ig in enumerate(va):
            g_cv_pred[ig] = min(g_authors, key=lambda a: cosine_distance(Zva[il], ct[a]))
    g_cv_f1 = macro_f1(gy, g_cv_pred)
    g_cv_acc = float((g_cv_pred == gy).mean())

    def eval_layer_b(toks: list[str]) -> dict:
        zm = zscore_transform(vectorize_words([toks], g_mfw100), g_mu_m, g_sd_m)[0]
        zc = zscore_transform(vectorize_chars([toks], g_c34_400), g_mu_c, g_sd_c)[0]
        zcb = np.hstack([zm, zc])
        dm = {a: cosine_distance(zm, g_cent_m[a]) for a in g_authors}
        dc = {a: cosine_distance(zc, g_cent_c[a]) for a in g_authors}
        dcb = {a: cosine_distance(zcb, g_cent_cb[a]) for a in g_authors}
        gi = general_imposters_scores(zcb, g_z_dict, n_iter=500, rng=rng)
        return {
            "n_tokens": len(toks),
            "rank_mfw": sorted(dm.items(), key=lambda kv: kv[1]),
            "rank_c34": sorted(dc.items(), key=lambda kv: kv[1]),
            "rank_comb": sorted(dcb.items(), key=lambda kv: kv[1]),
            "rank_gi": sorted(gi.items(), key=lambda kv: -kv[1]),
        }

    # Test 5b: Verbatim Markan Cento Test
    gospel_all_toks = corpora["gospel_mark"] + corpora["gospel_matthew"] + corpora["gospel_luke"] + corpora["gospel_john"]
    gospel_top50 = set(w for w, _ in Counter(gospel_all_toks).most_common(50))

    mark_toks = corpora["gospel_mark"]
    john_toks = corpora["gospel_john"]
    mark_bgs = {(mark_toks[i], mark_toks[i + 1]) for i in range(len(mark_toks) - 1)}
    mark_tgs = {(mark_toks[i], mark_toks[i + 1], mark_toks[i + 2]) for i in range(len(mark_toks) - 2)}
    mj_bgs = mark_bgs | {(john_toks[i], john_toks[i + 1]) for i in range(len(john_toks) - 1)}
    mj_tgs = mark_tgs | {(john_toks[i], john_toks[i + 1], john_toks[i + 2]) for i in range(len(john_toks) - 2)}

    sm_cento_mark = ngram_overlap_rates(ms["secret_mark_quotes"], mark_bgs, mark_tgs, gospel_top50)
    sm_cento_mj = ngram_overlap_rates(ms["secret_mark_quotes"], mj_bgs, mj_tgs, gospel_top50)

    # Leave-one-chunk-out baseline on all L_B-token chunks of Canonical Mark!
    mark_chunks = g_chunks_all["Mark"]
    mark_loo_cento_mark = []
    mark_loo_cento_mj = []
    for i, ch in enumerate(mark_chunks):
        # Build Mark n-grams excluding chunk i's token span [i*L_B : (i+1)*L_B]
        s_idx, e_idx = i * L_B, (i + 1) * L_B
        rem_left = mark_toks[:s_idx]
        rem_right = mark_toks[e_idx:]
        rb = ({(rem_left[j], rem_left[j + 1]) for j in range(len(rem_left) - 1)} |
              {(rem_right[j], rem_right[j + 1]) for j in range(len(rem_right) - 1)})
        rt = ({(rem_left[j], rem_left[j + 1], rem_left[j + 2]) for j in range(len(rem_left) - 2)} |
              {(rem_right[j], rem_right[j + 1], rem_right[j + 2]) for j in range(len(rem_right) - 2)})
        mark_loo_cento_mark.append(ngram_overlap_rates(ch, rb, rt, gospel_top50))
        rb_mj = rb | {(john_toks[j], john_toks[j + 1]) for j in range(len(john_toks) - 1)}
        rt_mj = rt | {(john_toks[j], john_toks[j + 1], john_toks[j + 2]) for j in range(len(john_toks) - 2)}
        mark_loo_cento_mj.append(ngram_overlap_rates(ch, rb_mj, rt_mj, gospel_top50))

    # Also evaluate Matthew, Luke, John chunks against Mark as external comparison
    other_gospel_vs_mark = {}
    for gname in ["Matthew", "Luke", "John"]:
        rates = [ngram_overlap_rates(ch, mark_bgs, mark_tgs, gospel_top50) for ch in g_chunks_all[gname]]
        other_gospel_vs_mark[gname] = {
            k: float(np.median([r[k] for r in rates]))
            for k in ["all_bigram_rate", "all_trigram_rate", "content_bigram_rate", "content_trigram_rate"]
        }

    cento_keys = ["all_bigram_rate", "all_trigram_rate", "content_bigram_rate", "content_trigram_rate"]
    test5_results = {
        "gospel_5way_cv_macro_f1": g_cv_f1,
        "gospel_5way_cv_acc": g_cv_acc,
        "n_mark_chunks": len(mark_chunks),
        "secret_mark_quotes": eval_layer_b(ms["secret_mark_quotes"]),
        "secret_mark_bethany": eval_layer_b(ms["secret_mark_bethany"]),
        "cento_vs_mark": {
            k: summarize_against_ref(sm_cento_mark[k], [r[k] for r in mark_loo_cento_mark]) for k in cento_keys
        },
        "cento_vs_mark_union_john": {
            k: summarize_against_ref(sm_cento_mj[k], [r[k] for r in mark_loo_cento_mj]) for k in cento_keys
        },
        "other_gospels_vs_mark_medians": other_gospel_vs_mark,
        "mark_loo_content_bigram_dist": [float(r["content_bigram_rate"]) for r in mark_loo_cento_mark],
        "mark_loo_content_trigram_dist": [float(r["content_trigram_rate"]) for r in mark_loo_cento_mark],
        "mark_loo_all_trigram_dist": [float(r["all_trigram_rate"]) for r in mark_loo_cento_mark],
    }

    # Also list exact matching content trigrams in Secret Mark vs Canonical Mark for transparency
    sm_toks = ms["secret_mark_quotes"]
    matched_tgs_mark = [
        " ".join(sm_toks[i : i + 3])
        for i in range(len(sm_toks) - 2)
        if (sm_toks[i], sm_toks[i + 1], sm_toks[i + 2]) in mark_tgs
    ]
    matched_tgs_john_only = [
        " ".join(sm_toks[i : i + 3])
        for i in range(len(sm_toks) - 2)
        if (sm_toks[i], sm_toks[i + 1], sm_toks[i + 2]) in mj_tgs
        and (sm_toks[i], sm_toks[i + 1], sm_toks[i + 2]) not in mark_tgs
    ]
    test5_results["matched_trigrams_in_mark"] = matched_tgs_mark
    test5_results["matched_trigrams_in_john_only"] = matched_tgs_john_only

    # Assemble full summary JSON
    summary = {
        "segmentation": {k: len(v) for k, v in ms.items()},
        "test0_calibration": {
            "cv_14_authors": cv_metrics,
            "heldout_quis_dives": {
                "n_chunks": len(qd_chunks),
                "recall_mfw": float(np.mean([r["mfw_top"] == "Clement of Alexandria" for r in qd_eval])),
                "recall_c34": float(np.mean([r["c34_top"] == "Clement of Alexandria" for r in qd_eval])),
                "recall_lr": float(np.mean([r["lr_top"] == "Clement of Alexandria" for r in qd_eval])),
                "recall_gi": float(np.mean([r["gi_top"] == "Clement of Alexandria" for r in qd_eval])),
                "median_gi_clement": float(np.median([r["gi_score"]["Clement of Alexandria"] for r in qd_eval])),
                "gi_pass_95_spec_rate": float(np.mean([r["gi_score"]["Clement of Alexandria"] > gi_95_thresh for r in qd_eval])),
            },
            "heldout_eclogae": {
                "n_chunks": len(ec_chunks),
                "recall_mfw": float(np.mean([r["mfw_top"] == "Clement of Alexandria" for r in ec_eval])),
                "recall_c34": float(np.mean([r["c34_top"] == "Clement of Alexandria" for r in ec_eval])),
                "recall_lr": float(np.mean([r["lr_top"] == "Clement of Alexandria" for r in ec_eval])),
                "recall_gi": float(np.mean([r["gi_top"] == "Clement of Alexandria" for r in ec_eval])),
                "median_gi_clement": float(np.median([r["gi_score"]["Clement of Alexandria"] for r in ec_eval])),
            },
            "mixed_excerpta_theodoto": {
                "n_chunks": len(ex_chunks),
                "attributed_clement_mfw": float(np.mean([r["mfw_top"] == "Clement of Alexandria" for r in ex_eval])),
                "attributed_clement_c34": float(np.mean([r["c34_top"] == "Clement of Alexandria" for r in ex_eval])),
                "attributed_clement_lr": float(np.mean([r["lr_top"] == "Clement of Alexandria" for r in ex_eval])),
                "attributed_clement_gi": float(np.mean([r["gi_top"] == "Clement of Alexandria" for r in ex_eval])),
                "median_gi_clement": float(np.median([r["gi_score"]["Clement of Alexandria"] for r in ex_eval])),
            },
            "gi_clement_95_specificity_threshold": gi_95_thresh,
            "gi_clement_max_non_clement": gi_max_nonclem,
            "forgery_controls": forgery_controls,
        },
        "test1_attribution": test1_results,
        "test2_oneclass": test2_results,
        "test3_lexical_criddle": test3_summary,
        "test5_layer_b_gospels": test5_results,
    }

    out_path = RESULTS_DIR / "stylometry_summary.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print("\n=== SAVED", out_path, "===")
    print("\n--- TEST 0: CALIBRATION ---")
    print(json.dumps(summary["test0_calibration"], indent=2))
    print("\n--- TEST 1: MAR SABA LAYER A ATTRIBUTION ---")
    for k, v in test1_results.items():
        print(f"Variant {k} (n={v['n_tokens']}): MFW={v['mfw_top']} (Clem #{v['clement_rank_mfw']}), "
              f"C34={v['c34_top']} (Clem #{v['clement_rank_c34']}), "
              f"GI={v['gi_top']} (Clem #{v['clement_rank_gi']}, score={v['clement_gi_score']:.3f}), "
              f"LR={v['lr_top']} (Clem #{v['clement_rank_lr']}, prob={v['clement_lr_prob']:.3f})")
    print("\n--- TEST 2: ONE-CLASS SELF-DISTANCE ---")
    print("Mar Saba Clement frame:", test2_results["mar_saba_clement_frame"])
    print("Held-out Quis dives:", {k: v for k, v in test2_results["heldout_quis_dives"].items() if k != "comb_dists"})
    print("Top 5 closest authors by one-class percentile:")
    for r in per_author_oneclass[:5]:
        print(f"  {r['author']:28s} dist={r['mar_saba_dist']:.4f} pct={r['mar_saba_percentile']:.3f}")
    print("\n--- TEST 3: HYPER-CLEMENTINE & CRIDDLE ---")
    for k in lex_keys:
        s = test3_summary["vs_all_authentic_clement"][k]
        print(f"  {k:24s}: MS={s['mar_saba']:.4f} vs Clem={s['ref_mean']:.4f}±{s['ref_sd']:.4f} "
              f"(z={s['z_score']:+.2f}, pct={s['percentile']:.3f}, p={s['p_two_sided']:.4f})")
    print("\n--- TEST 5: LAYER B (SECRET MARK QUOTATIONS) ---")
    print("5-way CV macro-F1:", g_cv_f1, "acc:", g_cv_acc)
    print("Secret Mark quotes GI:", test5_results["secret_mark_quotes"]["rank_gi"])
    print("Secret Mark quotes Comb:", test5_results["secret_mark_quotes"]["rank_comb"])
    for k in cento_keys:
        s = test5_results["cento_vs_mark"][k]
        print(f"  Cento vs Mark {k:22s}: SM={s['mar_saba']:.4f} vs Mark_LOO={s['ref_mean']:.4f}±{s['ref_sd']:.4f} "
              f"(z={s['z_score']:+.2f}, pct={s['percentile']:.3f})")
    for k in cento_keys:
        s = test5_results["cento_vs_mark_union_john"][k]
        print(f"  Cento vs Mk∪Jn {k:21s}: SM={s['mar_saba']:.4f} vs Mark_LOO={s['ref_mean']:.4f}±{s['ref_sd']:.4f} "
              f"(z={s['z_score']:+.2f}, pct={s['percentile']:.3f})")
    print("Matched trigrams in Mark:", len(matched_tgs_mark), matched_tgs_mark[:10])
    print("Matched trigrams in John only:", len(matched_tgs_john_only), matched_tgs_john_only)


if __name__ == "__main__":
    main()
