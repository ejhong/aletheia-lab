#!/usr/bin/env python3
"""Pre-registered geochemical fingerprinting & blind peak-uniqueness analysis for Issue #120.

Implements every statistical test specified in questions/yd-platinum-fingerprint/protocol.md:
  - Pillar 1A: Full 6-HSE (Os, Ir, Ru, Pt, Pd, Re) CI-normalized Centered Log-Ratio (CLR)
               compositional classification + two-component HSE & 187Os/188Os mixing RMSE
               across Hall's Cave TX (Sun et al. 2020) and Page-Ladson FL (Nana Yobo et al. 2026),
               validated against a mandatory positive control of confirmed Chicxulub K-Pg
               impact samples (kpg2025_MOESM4.xlsx).
  - Pillar 1B: Diagnostic ratio comparison (Pt/Ir, Pt/Pd, Os/Ir, Re/Os, 187Os/188Os) and
               cross-site geochemical coherence across YDB sites (Hall's Cave, Page-Ladson,
               Moore 2017, White Pond 2019, Wonderkrater 2026, GISP2 Petaev 2013) vs.
               confirmed Chicxulub K-Pg, volcanic gas condensates, Laacher See Tephra,
               CI chondrites, iron meteorites, and Upper Continental Crust (UCC).
  - Pillar 2:  Blind stratigraphic peak-uniqueness audit (no author boundary labels used
               during peak detection) with exact Poisson-binomial permutation p-values.

Usage:
    python3 questions/yd-platinum-fingerprint/analysis/pt_fingerprint.py
"""

from __future__ import annotations

import csv
import json
import math
import os
import pathlib
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from typing import Any

import numpy as np
from pypdf import PdfReader
from scipy import stats

HERE = pathlib.Path(__file__).resolve().parent
QDIR = HERE.parent
DATA = QDIR / "data"
RESULTS = QDIR / "results"

HSE_ORDER = ["Os", "Ir", "Ru", "Pt", "Pd", "Re"]

# ---------------------------------------------------------------------------
# Reference End-Members (all units in ppt = pg/g; primary citations in MANIFEST.md)
# ---------------------------------------------------------------------------
# CI Chondrite (Wasson & Kallemeyn 1988; Horan et al. 2003; 1 ppb = 1000 ppt)
CI_CHONDRITE_PPT = {
    "Os": 490_000.0,
    "Ir": 460_000.0,
    "Ru": 710_000.0,
    "Pt": 990_000.0,
    "Pd": 560_000.0,
    "Re": 37_000.0,
}
CI_187OS_188OS = 0.126  # Walker et al. (2002)

# Upper Continental Crust (Peucker-Ehrenbrink & Jahn 2001; Park et al. 2012; Sun et al. 2020 Table S2)
UCC_PPT = {
    "Os": 31.0,
    "Ir": 22.0,
    "Ru": 30.0,
    "Pt": 510.0,
    "Pd": 520.0,
    "Re": 198.0,
}
UCC_187OS_188OS = 1.26

# Niuatahi-Motutahi submarine volcanic sulfur condensates (Park et al. 2016 GCA 174, Table 1 midpoints; ppt)
# Note: Os not reported in Table 1; used in Pillar 1B (Pt/Ir, Pt/Pd, Re/Ir)
NIUATAHI_VOLCANIC_PPT = {
    "Ir": 0.5,       # <0.0003-0.0007 ppb
    "Ru": 26.5,      # 0.012-0.041 ppb
    "Pt": 597.0,     # 0.414-0.780 ppb
    "Pd": 545.0,     # 0.379-0.710 ppb
    "Re": 13_400.0,  # 10.8-16.0 ppb
}

# Published GISP2 Pt anomaly summary (Petaev et al. 2013 PNAS; verified in Green et al. 2025 & Wolbach et al. 2018)
# Used ONLY in Pillar 1B cross-site Pt/Ir comparison (not in full 6-HSE Pillar 1A)
GISP2_PETAEV_2013 = {
    "site": "GISP2 (Greenland ice)",
    "source": "Petaev et al. (2013) PNAS; Green et al. (2025)",
    "pt_peak_ppt": 82.2,
    "pt_ir_low": 100.0,
    "pt_ir_high": 1264.0,
    "pt_ir_mid": math.sqrt(100.0 * 1264.0),  # geometric midpoint ~355.5
}

# Fallback Iron Meteorite (low-Ir differentiated iron, e.g., IIIAB/IIAB/IVB range from Cook et al. 2004 / Petaev & Jacobsen 2004)
# Overridden/augmented programmatically when Sun et al. 2020 Table S3 is parsed.
FALLBACK_LOW_IR_IRON_PPT = {
    "Os": 120_000.0,
    "Ir": 250_000.0,
    "Ru": 2_500_000.0,
    "Pt": 5_000_000.0,
    "Pd": 4_500_000.0,
    "Re": 15_000.0,
}

# ===========================================================================
# Core Mathematical & Statistical Engine (tested independently on synthetic data)
# ===========================================================================

def hse_vec(d: dict[str, float]) -> np.ndarray:
    """Return 6-element numpy vector [Os, Ir, Ru, Pt, Pd, Re] in ppt."""
    return np.array([float(d[e]) for e in HSE_ORDER], dtype=float)


def ci_clr(vec_ppt: np.ndarray) -> np.ndarray:
    """CI-chondrite-normalized centered log10-ratio vector (length 6)."""
    ci = hse_vec(CI_CHONDRITE_PPT)
    if np.any(vec_ppt <= 0) or np.any(~np.isfinite(vec_ppt)):
        raise ValueError("All 6 HSE concentrations must be strictly positive and finite.")
    z = np.log10(vec_ppt / ci)
    return z - np.mean(z)


def clr_distance(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Euclidean distance between two CI-normalized CLR vectors."""
    return float(np.linalg.norm(ci_clr(vec_a) - ci_clr(vec_b)))


def clr_classify(
    sample_ppt: np.ndarray,
    prototypes_clr: dict[str, np.ndarray],
) -> tuple[str, dict[str, float]]:
    """Classify sample by nearest prototype in CI-normalized CLR space."""
    z = ci_clr(sample_ppt)
    dists = {name: float(np.linalg.norm(z - pclr)) for name, pclr in prototypes_clr.items()}
    best = min(dists, key=dists.get)
    return best, dists


def mixing_rmse(
    sample_ppt: np.ndarray,
    sample_os_iso: float | None,
    bg_ppt: np.ndarray,
    bg_os_iso: float,
    src_ppt: np.ndarray,
    src_os_iso: float,
    f_grid: np.ndarray | None = None,
) -> dict[str, float]:
    """Optimize 2-component mixing fraction f in [0, 1] minimizing log10-HSE + Os-isotope RMSE."""
    if f_grid is None:
        f_grid = np.concatenate(([0.0], np.logspace(-6, 0, 601)))
    log_obs = np.log10(sample_ppt)
    f = f_grid[:, None]  # (M, 1)
    c_mix = (1.0 - f) * bg_ppt[None, :] + f * src_ppt[None, :]
    hse_sq = np.sum((log_obs[None, :] - np.log10(c_mix)) ** 2, axis=1)

    if sample_os_iso is not None and np.isfinite(sample_os_iso):
        f1 = f_grid
        num = (1.0 - f1) * bg_ppt[0] * bg_os_iso + f1 * src_ppt[0] * src_os_iso
        den = (1.0 - f1) * bg_ppt[0] + f1 * src_ppt[0]
        r_mix = num / den
        iso_sq = ((sample_os_iso - r_mix) / 0.20) ** 2
        rmse_arr = np.sqrt((hse_sq + iso_sq) / 7.0)
    else:
        r_mix = np.full_like(f_grid, np.nan)
        rmse_arr = np.sqrt(hse_sq / 6.0)

    idx = int(np.argmin(rmse_arr))
    return {
        "rmse": float(rmse_arr[idx]),
        "best_f": float(f_grid[idx]),
        "pred_os_iso": float(r_mix[idx]) if np.isfinite(r_mix[idx]) else float("nan"),
        "hse_only_rmse": float(np.sqrt(hse_sq[idx] / 6.0)),
    }


def detect_blind_peaks(
    values: list[float] | np.ndarray,
    mode: str = "high",
    fold_threshold: float = 3.0,
    z_threshold: float = 3.5,
    iso_drop_threshold: float = 0.15,
) -> dict[str, Any]:
    """Blind stratigraphic peak detector (no boundary labels used).

    mode='high': detects x_i >= fold_threshold * median AND modified z >= z_threshold.
    mode='low_iso': detects median - x_i >= iso_drop_threshold AND modified z >= z_threshold.
    Adjacent flagged indices (gap <= 1 sample step) are merged into a single excursion event.
    """
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    if n < 6 or np.any(~np.isfinite(arr)):
        return {
            "n": n,
            "baseline": float("nan"),
            "scale": float("nan"),
            "z_scores": [],
            "flagged_indices": [],
            "events": [],
            "global_extreme_idx": None,
        }

    med = float(np.median(arr))
    mad = float(np.median(np.abs(arr - med)))
    if mad > 0:
        scale = mad
        z_factor = 0.6745
    else:
        q75, q25 = np.percentile(arr, [75, 25])
        iqr_s = float((q75 - q25) / 1.349)
        if iqr_s > 0:
            scale = iqr_s
            z_factor = 1.0
        else:
            scale = max(abs(0.1 * med), 0.05 if mode == "low_iso" else 1e-6)
            z_factor = 1.0

    if mode == "high":
        z = z_factor * (arr - med) / scale
        flagged = [i for i in range(n) if arr[i] >= fold_threshold * max(med, 1e-12) and z[i] >= z_threshold]
        global_idx = int(np.argmax(arr))
    elif mode == "low_iso":
        z = z_factor * (med - arr) / scale
        flagged = [i for i in range(n) if (med - arr[i]) >= iso_drop_threshold and z[i] >= z_threshold]
        global_idx = int(np.argmin(arr))
    else:
        raise ValueError(f"Unknown mode: {mode}")

    # Merge contiguous flagged indices separated by <= 1 step into single excursion events
    events = []
    if flagged:
        cluster = [flagged[0]]
        for idx in flagged[1:]:
            if idx - cluster[-1] <= 2:  # <= 1 intervening sample step
                cluster.append(idx)
            else:
                events.append(cluster)
                cluster = [idx]
        events.append(cluster)

    event_dicts = []
    for cl in events:
        if mode == "high":
            pk = max(cl, key=lambda i: arr[i])
        else:
            pk = min(cl, key=lambda i: arr[i])
        event_dicts.append({
            "indices": cl,
            "peak_idx": int(pk),
            "peak_value": float(arr[pk]),
            "peak_z": float(z[pk]),
            "fold_over_median": float(arr[pk] / med) if med > 0 else float("nan"),
        })

    return {
        "n": n,
        "baseline": med,
        "scale": scale,
        "z_scores": [float(v) for v in z],
        "flagged_indices": flagged,
        "events": event_dicts,
        "global_extreme_idx": global_idx,
    }


def poisson_binomial_tail(probs: list[float], k_obs: int) -> float:
    """Exact upper-tail probability P(X >= k_obs) for X = sum(Bernoulli(p_i))."""
    m = len(probs)
    if k_obs <= 0:
        return 1.0
    if k_obs > m:
        return 0.0
    dp = np.zeros(m + 1, dtype=float)
    dp[0] = 1.0
    for p in probs:
        p = float(np.clip(p, 0.0, 1.0))
        nxt = np.zeros_like(dp)
        nxt[:-1] += dp[:-1] * (1.0 - p)
        nxt[1:] += dp[:-1] * p
        dp = nxt
    return float(np.clip(np.sum(dp[k_obs:]), 0.0, 1.0))


def decide_verdict(
    kpg_clr_pass_frac: float,
    kpg_mix_pass_frac: float,
    ydb_cosmic_clr_frac: float,
    ydb_noncosmic_clr_frac: float,
    ydb_median_delta_rmse: float,
    ydb_median_pt_ir: float | None,
    indep_frac_outside: float,
    indep_perm_p: float,
) -> str:
    """Pre-registered mutually exclusive verdict rule from protocol.md Section 4."""
    if kpg_clr_pass_frac < 0.75 or kpg_mix_pass_frac < 0.75:
        return "ambiguous_or_mixed"

    if (
        ydb_cosmic_clr_frac > 0.50
        and ydb_median_delta_rmse < 0.0
        and (ydb_median_pt_ir is not None and ydb_median_pt_ir <= 6.0)
    ):
        return "cosmic_impact_fingerprint"

    if ydb_noncosmic_clr_frac >= 0.60 and ydb_median_delta_rmse > 0.0:
        if indep_frac_outside >= 0.50 or indep_perm_p >= 0.01:
            return "non_cosmic_and_non_unique"
        return "non_cosmic_with_ydb_anomaly"

    return "ambiguous_or_mixed"


# ===========================================================================
# Primary Dataset Parsers
# ===========================================================================

def _to_float(tok: str) -> float | None:
    s = tok.strip().replace(",", "").replace("^", "").replace("*", "").replace("†", "").replace("§", "")
    if not s or s.upper() in {"ND", "N.D.", "N/A", "NA", "-", "—", "BDL"}:
        return None
    if s.startswith("<"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse_sun2020_table_s1(pdf_path: pathlib.Path) -> list[dict[str, Any]]:
    """Parse Sun et al. (2020) Table S1 (Hall's Cave TX bulk HSE + 187Os/188Os, ppt)."""
    reader = PdfReader(str(pdf_path))
    text = (reader.pages[11].extract_text() or "") + "\n" + (reader.pages[12].extract_text() or "")
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or not re.match(r"^HC", line):
            continue
        # Normalize tokens; handle '±' or separate uncertainty columns
        parts = line.split()
        # Expected columns: Sample Depth Age Weight 187Os/188Os ± 2s Os Ir Ru Pt Pd Re
        # Some lines may omit ± symbol and have 2s directly, or have ND
        sample = parts[0]
        cleaned = [p for p in parts[1:] if p not in {"±", "+/-"}]
        if len(cleaned) < 11:
            continue
        depth_cm = _to_float(cleaned[0])
        age_ka = _to_float(cleaned[1])
        weight_g = _to_float(cleaned[2])
        os_iso = _to_float(cleaned[3])
        os_iso_2s = _to_float(cleaned[4])
        hse_vals = [_to_float(x) for x in cleaned[5:11]]
        if depth_cm is None or age_ka is None or os_iso is None:
            continue
        rec: dict[str, Any] = {
            "site": "Hall's Cave, TX",
            "study": "Sun et al. (2020)",
            "sample": sample,
            "depth_cm": depth_cm,
            "age_ka": age_ka,
            "weight_g": weight_g,
            "os_iso": os_iso,
            "os_iso_2s": os_iso_2s,
        }
        for el, val in zip(HSE_ORDER, hse_vals):
            rec[el] = val  # ppt
        rows.append(rec)
    rows.sort(key=lambda r: r["depth_cm"])
    return rows


def parse_sun2020_table_s2(pdf_path: pathlib.Path) -> dict[str, dict[str, float]]:
    """Parse Sun et al. (2020) Table S2 (volcanic gas condensates, Petriccio K-Pg, UCC; ppt)."""
    reader = PdfReader(str(pdf_path))
    text = reader.pages[13].extract_text() or ""
    refs: dict[str, dict[str, float]] = {}
    for line in text.splitlines():
        line = line.strip()
        # Find lines ending with 6 numeric tokens (possibly comma-formatted)
        m = re.match(
            r"^(.*?)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)$",
            line,
        )
        if not m:
            continue
        label = re.sub(r"[*§#&¤†‡]+$", "", m.group(1).strip()).strip()
        vals = [_to_float(m.group(i)) for i in range(2, 8)]
        if all(v is not None and v > 0 for v in vals):
            refs[label] = {el: float(v) for el, v in zip(HSE_ORDER, vals)}
    return refs


def parse_sun2020_table_s3_ocr(pdf_path: pathlib.Path) -> dict[str, dict[str, float]]:
    """OCR Sun et al. (2020) Table S3 (p.15 image: chondrite & iron meteorite HSEs in ppb -> ppt)."""
    reader = PdfReader(str(pdf_path))
    page = reader.pages[14]
    if not page.images:
        return {}
    im = page.images[0]
    ext = os.path.splitext(im.name)[1] or ".png"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tf:
        tf.write(im.data)
        tmp = tf.name
    try:
        out = subprocess.check_output(
            ["tesseract", tmp, "stdout", "--psm", "6"],
            stderr=subprocess.DEVNULL,
            timeout=20,
        ).decode("utf-8", errors="ignore")
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

    parsed: dict[str, dict[str, float]] = {}
    for line in out.splitlines():
        line = line.strip()
        m = re.match(
            r"^([A-Za-z][A-Za-z0-9\s\-\(\)/]+?)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)$",
            line,
        )
        if not m:
            continue
        label = m.group(1).strip()
        vals = [_to_float(m.group(i)) for i in range(2, 8)]
        if all(v is not None and v > 0 for v in vals):
            # Table S3 is in ppb -> convert to ppt (*1000)
            parsed[label] = {el: float(v) * 1000.0 for el, v in zip(HSE_ORDER, vals)}
    return parsed


def parse_nanayobo2026_table_s2(pdf_path: pathlib.Path) -> list[dict[str, Any]]:
    """Parse Nana Yobo et al. (2026) Table S2 (Page-Ladson FL bulk HSE + 187Os/188Os; ppb -> ppt)."""
    reader = PdfReader(str(pdf_path))
    text = reader.pages[8].extract_text() or ""
    rows = []
    # Page-Ladson Table S2 has: Strat Depth(cm) Sample 187Os/188Os ±2s Os Ir Ru Pt Pd Re (all ppb!)
    # Note: pypdf sometimes wraps headers or concatenates strat+depth. Match lines with depth ~820-890 cm
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        toks = [t for t in line.split() if t not in {"±", "+/-"}]
        # Look for a sample ID token like PL-... or numeric depth in [750, 950]
        # Let's parse flexibly by finding the 187Os/188Os value (0.1 to 2.5) followed by small 2s (<0.2) and 6 HSE values
        nums_idx = []
        for idx, tok in enumerate(toks):
            v = _to_float(tok)
            if v is not None:
                nums_idx.append((idx, v))
        if len(nums_idx) < 8:
            continue
        # Typically: [strat?, depth_cm, sample_id?, 187Os/188Os, 2s, Os, Ir, Ru, Pt, Pd, Re]
        # Identify depth_cm (between 700 and 1000 or 7.0 and 10.0 m)
        depth_cm = None
        depth_pos = None
        for idx, v in nums_idx[:3]:
            if 700.0 <= v <= 1000.0:
                depth_cm = v
                depth_pos = idx
                break
            if 7.0 <= v <= 10.0:
                depth_cm = v * 100.0
                depth_pos = idx
                break
        if depth_cm is None or depth_pos is None:
            continue
        # Remaining tokens after sample ID
        # Find where os_iso starts (value in [0.1, 3.0] followed by small uncertainty < 0.25)
        tail = toks[depth_pos + 1 :]
        # Sample ID is usually tail[0] if non-numeric or containing letters/dashes
        sample_id = tail[0] if tail else f"PL-{depth_cm:.1f}"
        # Find os_iso index in tail
        iso_pos = None
        for k in range(len(tail) - 7):
            v0 = _to_float(tail[k])
            v1 = _to_float(tail[k + 1])
            if v0 is not None and v1 is not None and 0.10 <= v0 <= 3.0 and 0.0 <= v1 <= 0.25:
                iso_pos = k
                break
        if iso_pos is None:
            continue
        strat = " ".join(toks[:depth_pos]).strip() or "?"
        if iso_pos > 0:
            sample_id = " ".join(tail[:iso_pos]).strip()
        os_iso = _to_float(tail[iso_pos])
        os_iso_2s = _to_float(tail[iso_pos + 1])
        hse_ppb = [_to_float(x) for x in tail[iso_pos + 2 : iso_pos + 8]]
        if os_iso is None or len(hse_ppb) < 6:
            continue
        rec: dict[str, Any] = {
            "site": "Page-Ladson, FL",
            "study": "Nana Yobo et al. (2026)",
            "strat": strat,
            "sample": sample_id,
            "depth_cm": depth_cm,
            # Linear age interpolation anchor from Nana Yobo et al. Table 1 & text:
            # 851 cm = 12.82 ka (4e/5 interface), 878 cm = ~13.45 ka, 842 cm = ~12.70 ka
            "age_ka": None,
            "os_iso": os_iso,
            "os_iso_2s": os_iso_2s,
        }
        # Convert ppb -> ppt (*1000)
        for el, val in zip(HSE_ORDER, hse_ppb):
            rec[el] = val * 1000.0 if val is not None else None
        rows.append(rec)
    rows.sort(key=lambda r: r["depth_cm"])
    return rows


def _read_xlsx_sheet_rows(xlsx_path: pathlib.Path, sheet_index: int) -> list[list[str]]:
    """Read an XLSX worksheet using stdlib zipfile + xml.etree (zero openpyxl dependency)."""
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(xlsx_path) as z:
        strings: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
            strings = ["".join(si.itertext()) for si in ss.findall(".//m:si", ns)]
        sh = ET.fromstring(z.read(f"xl/worksheets/sheet{sheet_index}.xml"))
        out_rows: list[list[str]] = []
        for r in sh.findall(".//m:row", ns):
            row_map: dict[int, str] = {}
            max_c = 0
            for c in r.findall("m:c", ns):
                ref = c.attrib.get("r", "")
                col_letters = re.sub(r"\d+", "", ref)
                col_idx = 0
                for ch in col_letters:
                    col_idx = col_idx * 26 + (ord(ch.upper()) - ord("A") + 1)
                col_idx -= 1
                max_c = max(max_c, col_idx)
                t = c.attrib.get("t", "")
                v = c.find("m:v", ns)
                if v is None or v.text is None:
                    val = ""
                elif t == "s":
                    val = strings[int(v.text)]
                else:
                    val = v.text
                row_map[col_idx] = val.strip()
            if row_map:
                out_rows.append([row_map.get(i, "") for i in range(max_c + 1)])
    return out_rows


def parse_kpg2025_benchmark(xlsx_path: pathlib.Path) -> list[dict[str, Any]]:
    """Parse confirmed Chicxulub K-Pg impact samples from kpg2025_MOESM4.xlsx (Data 2 & Data 3)."""
    records: list[dict[str, Any]] = []
    for sheet_idx, sheet_label in [(2, "Chicxulub M0077 (Data 2)"), (3, "Mexican K-Pg Sections (Data 3)")]:
        rows = _read_xlsx_sheet_rows(xlsx_path, sheet_idx)
        # Find header row containing 'Os ppb' and 'Ir ppb' and 'Pt ppb'
        hdr_row_idx = None
        col_map: dict[str, int] = {}
        for i, r in enumerate(rows[:10]):
            joined = " ".join(r).lower()
            if "os ppb" in joined and "ir ppb" in joined and "pt ppb" in joined:
                hdr_row_idx = i
                for j, cell in enumerate(r):
                    cl = cell.strip().lower()
                    if cl == "sample id":
                        col_map["sample"] = j
                    elif "os ppb" in cl:
                        col_map["Os"] = j
                    elif "ir ppb" in cl:
                        col_map["Ir"] = j
                    elif "ru ppb" in cl:
                        col_map["Ru"] = j
                    elif "pt ppb" in cl:
                        col_map["Pt"] = j
                    elif "pd ppb" in cl:
                        col_map["Pd"] = j
                    elif "re ppb" in cl:
                        col_map["Re"] = j
                    elif "initial 187os/188os" in cl or ("187os/188os" in cl and "os_iso" not in col_map):
                        col_map["os_iso"] = j
                    elif "lithology" in cl:
                        col_map["lithology"] = j
                break
        if hdr_row_idx is None:
            continue
        section_name = sheet_label
        for r in rows[hdr_row_idx + 1 :]:
            if len(r) <= max(col_map.get(e, 0) for e in HSE_ORDER):
                # Possible section subheader
                if r and r[0] and len(r[0]) > 3 and all(not c for c in r[1:4]):
                    section_name = r[0]
                continue
            vals = {}
            ok = True
            for el in HSE_ORDER:
                v = _to_float(r[col_map[el]]) if el in col_map and col_map[el] < len(r) else None
                if v is None or v <= 0:
                    ok = False
                    break
                vals[el] = v * 1000.0  # ppb -> ppt
            if not ok:
                continue
            os_iso = _to_float(r[col_map["os_iso"]]) if "os_iso" in col_map and col_map["os_iso"] < len(r) else None
            # Confirmed K-Pg impact ejecta horizon filter (pre-registered: Ir >= 0.5 ppb = 500 ppt)
            if vals["Ir"] >= 500.0:
                records.append({
                    "site": section_name,
                    "sheet": sheet_label,
                    "sample": r[col_map["sample"]] if "sample" in col_map else "",
                    "lithology": r[col_map["lithology"]] if "lithology" in col_map and col_map["lithology"] < len(r) else "",
                    "os_iso": os_iso,
                    **vals,
                })
    return records


def parse_green2025_laacher_see(docx_path: pathlib.Path) -> list[dict[str, Any]]:
    """Parse Green et al. (2025) Table 3 (Laacher See Tephra Pt, Ir in ppb -> ppt)."""
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(docx_path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    tables = root.findall(".//w:tbl", ns)
    out = []
    for tbl in tables:
        trs = tbl.findall(".//w:tr", ns)
        if not trs:
            continue
        hdr = ["".join(tc.itertext()).strip().lower() for tc in trs[0].findall(".//w:tc", ns)]
        if any("pt" in h for h in hdr) and any("ir" in h for h in hdr):
            for tr in trs[1:]:
                cells = ["".join(tc.itertext()).strip() for tc in tr.findall(".//w:tc", ns)]
                if len(cells) < 3 or not cells[0]:
                    continue
                sample = cells[0]
                pt_raw = cells[1]
                ir_raw = cells[2]
                pt_bdl = pt_raw.startswith("<")
                ir_bdl = ir_raw.startswith("<")
                pt_val = _to_float(pt_raw.lstrip("<"))
                ir_val = _to_float(ir_raw.lstrip("<"))
                out.append({
                    "sample": sample,
                    "pt_ppt": pt_val * 1000.0 if pt_val is not None else None,
                    "ir_ppt": ir_val * 1000.0 if ir_val is not None else None,
                    "pt_bdl": pt_bdl,
                    "ir_bdl": ir_bdl,
                    "is_topsoil": "topsoil" in sample.lower() or "soil" in sample.lower(),
                })
            break
    return out


def parse_wonderkrater2026(html_path: pathlib.Path) -> list[dict[str, Any]]:
    """Parse Thackeray et al. (2026) F1000Research HTML Table 1 (YDB vs Non-YDB PGE ratios)."""
    html_txt = html_path.read_text(encoding="utf-8", errors="ignore")
    tbls = re.findall(r"<table[^>]*>.*?</table>", html_txt, re.S)
    rows = []
    for t in tbls:
        if "YDB average" not in t:
            continue
        trs = re.findall(r"<tr[^>]*>.*?</tr>", t, re.S)
        for tr in trs[1:]:
            cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[hd][^>]*>.*?</t[hd]>", tr, re.S)]
            if len(cells) >= 6:
                rows.append({
                    "ratio_name": cells[0],
                    "ydb_avg": _to_float(cells[1]),
                    "non_ydb_avg": _to_float(cells[2]),
                    "enrichment": cells[3],
                    "chondritic_reported": _to_float(cells[4]),
                    "terrestrial_reported": _to_float(cells[5]),
                })
        break
    return rows


def _ocr_pdf_page_image(pdf_path: pathlib.Path, page_1idx: int) -> str:
    reader = PdfReader(str(pdf_path))
    page = reader.pages[page_1idx - 1]
    if not page.images:
        return ""
    im = page.images[0]
    ext = os.path.splitext(im.name)[1] or ".png"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tf:
        tf.write(im.data)
        tmp = tf.name
    try:
        return subprocess.check_output(
            ["tesseract", tmp, "stdout", "--psm", "6"],
            stderr=subprocess.DEVNULL,
            timeout=25,
        ).decode("utf-8", errors="ignore")
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def parse_moore2019_white_pond(pdf_path: pathlib.Path) -> list[dict[str, Any]]:
    """OCR-parse Moore et al. (2019) Table 3 (p.43: White Pond SC Au, Pt, Pd, Pt/Pd) with strict QA."""
    txt = _ocr_pdf_page_image(pdf_path, 43)
    rows = []
    for line in txt.splitlines():
        line = line.strip()
        # Table 3 rows start with relative depth interval e.g. '+44 to +46 165 20 2.2 5 0.4' or '-10 to -8 221 13 4.2 0.9 4.7'
        m = re.match(
            r"^[+-]?\d+\s*to\s*[+-]?\d+\s+(\d{3}(?:\.\d+)?)\s+(.*)$",
            line,
            re.IGNORECASE,
        )
        if not m:
            continue
        depth_cm = float(m.group(1))
        if not (150.0 <= depth_cm <= 260.0):
            continue
        toks = m.group(2).split()
        # Extract floats (allowing leading '<'); take last 3 valid floats as (Pt, Pd, Pt/Pd)
        nums = []
        for tok in toks:
            clean = tok.lstrip("<").replace(",", ".")
            try:
                nums.append((float(clean), tok.startswith("<")))
            except ValueError:
                continue
        if len(nums) < 3:
            continue
        # Last 3 tokens are Pt, Pd, Pt/Pd (handles merged Au+Pt cells via strict 15% Pt/Pd QA gate)
        pt_v, pt_bdl = nums[-3]
        pd_v, pd_bdl = nums[-2]
        rat_v, _ = nums[-1]
        if 0.0 < pt_v <= 200.0 and 0.0 < pd_v <= 200.0:
            calc = pt_v / pd_v
            if abs(calc - rat_v) / max(calc, 1e-6) <= 0.15:
                rows.append({
                    "site": "White Pond, SC",
                    "study": "Moore et al. (2019)",
                    "depth_cm": depth_cm,
                    "pt_ppb": pt_v,
                    "pd_ppb": pd_v,
                    "pt_pd": calc,
                    "pt_bdl": pt_bdl,
                    "pd_bdl": pd_bdl,
                })
    rows.sort(key=lambda r: r["depth_cm"])
    return rows


# ===========================================================================
# Main Pre-Registered Pipeline
# ===========================================================================

def run_pipeline() -> dict[str, Any]:
    RESULTS.mkdir(parents=True, exist_ok=True)

    # 1. Load reference benchmarks
    sun_s2 = parse_sun2020_table_s2(DATA / "sun2020_sm.pdf")
    sun_s3 = parse_sun2020_table_s3_ocr(DATA / "sun2020_sm.pdf")
    kpg_samples = parse_kpg2025_benchmark(DATA / "kpg2025_MOESM4.xlsx")
    laacher_see = parse_green2025_laacher_see(DATA / "green2025_s001.docx")
    wonderkrater = parse_wonderkrater2026(DATA / "wonderkrater2026.html")

    # Identify volcanic gas condensate vectors from Sun Table S2
    volc_refs: dict[str, np.ndarray] = {}
    petriccio_kpg: np.ndarray | None = None
    ucc_vec = hse_vec(UCC_PPT)
    for lbl, dvals in sun_s2.items():
        low = lbl.lower()
        if any(k in low for k in ["kudryavy", "tolbachik", "erta ale"]):
            volc_refs[lbl] = hse_vec(dvals)
        elif "petriccio" in low or "k/t" in low or "k-pg" in low:
            petriccio_kpg = hse_vec(dvals)
        elif "upper continental crust" in low or "ucc" in low:
            ucc_vec = hse_vec(dvals)

    # Build iron meteorite steelman (highest Pt/Ir iron meteorite in Table S3, else fallback)
    iron_refs: dict[str, np.ndarray] = {}
    for lbl, dvals in sun_s3.items():
        low = lbl.lower()
        if any(k in low for k in ["iron", "iiab", "iiiab", "ivb", "iab", "iva", "cape york"]):
            iron_refs[lbl] = hse_vec(dvals)
    if iron_refs:
        best_iron_name = max(iron_refs, key=lambda k: iron_refs[k][3] / iron_refs[k][1])
        iron_vec = iron_refs[best_iron_name]
    else:
        best_iron_name = "Low-Ir Iron (fallback literature)"
        iron_vec = hse_vec(FALLBACK_LOW_IR_IRON_PPT)

    ci_vec = hse_vec(CI_CHONDRITE_PPT)
    volc_mean_clr = np.mean([ci_clr(v) for v in volc_refs.values()], axis=0) if volc_refs else ci_clr(hse_vec({"Os": 586, "Ir": 16, "Ru": 5, "Pt": 174, "Pd": 219, "Re": 84640}))

    # K-Pg centroid from confirmed Chicxulub samples (+ Petriccio if present)
    kpg_clrs = [ci_clr(hse_vec(s)) for s in kpg_samples]
    if petriccio_kpg is not None:
        kpg_clrs.append(ci_clr(petriccio_kpg))
    kpg_med_clr = np.median(kpg_clrs, axis=0)

    prototypes_clr = {
        "chondrite": ci_clr(ci_vec),
        "kpg_impact": kpg_med_clr,
        "volcanic": volc_mean_clr,
        "ucc": ci_clr(ucc_vec),
    }

    # 2. Positive control: evaluate every confirmed Chicxulub K-Pg sample
    kpg_eval = []
    for s in kpg_samples:
        vec = hse_vec(s)
        cls, dists = clr_classify(vec, prototypes_clr)
        cosmic_clr_win = min(dists["chondrite"], dists["kpg_impact"]) < min(dists["volcanic"], dists["ucc"])
        # Leave-one-out check against pure chondrite vs volcanic/ucc (strictest test!)
        strict_cosmic_clr = dists["chondrite"] < min(dists["volcanic"], dists["ucc"])
        fit_ci = mixing_rmse(vec, s["os_iso"], ucc_vec, UCC_187OS_188OS, ci_vec, CI_187OS_188OS)
        fit_iron = mixing_rmse(vec, s["os_iso"], ucc_vec, UCC_187OS_188OS, iron_vec, CI_187OS_188OS)
        volc_fits = {vn: mixing_rmse(vec, s["os_iso"], ucc_vec, UCC_187OS_188OS, vv, 0.15) for vn, vv in volc_refs.items()}
        best_v_name = min(volc_fits, key=lambda k: volc_fits[k]["rmse"])
        delta_rmse = min(fit_ci["rmse"], fit_iron["rmse"]) - volc_fits[best_v_name]["rmse"]
        kpg_eval.append({
            "site": s["site"],
            "sample": s["sample"],
            "pt_ir": vec[3] / vec[1],
            "pt_pd": vec[3] / vec[4],
            "os_ir": vec[0] / vec[1],
            "re_os": vec[5] / vec[0],
            "os_iso": s["os_iso"],
            "nearest_class": cls,
            "strict_chondrite_beats_volc_ucc": strict_cosmic_clr,
            "cosmic_clr_win": cosmic_clr_win,
            "rmse_ci": fit_ci["rmse"],
            "rmse_iron": fit_iron["rmse"],
            "rmse_volc": volc_fits[best_v_name]["rmse"],
            "best_volc": best_v_name,
            "delta_rmse": delta_rmse,
        })

    kpg_clr_pass = sum(1 for r in kpg_eval if r["strict_chondrite_beats_volc_ucc"]) / max(len(kpg_eval), 1)
    kpg_mix_pass = sum(1 for r in kpg_eval if r["delta_rmse"] < 0) / max(len(kpg_eval), 1)

    # 3. Parse Hall's Cave (Sun 2020) and Page-Ladson (Nana Yobo 2026)
    halls_cave = parse_sun2020_table_s1(DATA / "sun2020_sm.pdf")
    page_ladson = parse_nanayobo2026_table_s2(DATA / "nanayobo2026_sm.pdf")

    # Classify each full-HSE sample in Hall's Cave and Page-Ladson
    def evaluate_site_column(
        rows: list[dict[str, Any]],
        site_name: str,
        ydb_predicate,
    ) -> dict[str, Any]:
        os_isos = [r["os_iso"] for r in rows if r.get("os_iso") is not None]
        site_os_med = float(np.median(os_isos)) if os_isos else UCC_187OS_188OS
        # Local radiogenic background: samples with os_iso >= site_os_med - 0.15 and complete 6-HSE
        bg_rows = [
            r for r in rows
            if r.get("os_iso") is not None
            and r["os_iso"] >= site_os_med - 0.15
            and all(r.get(e) is not None and r[e] > 0 for e in HSE_ORDER)
        ]
        if bg_rows:
            bg_vec = np.array([float(np.median([r[e] for r in bg_rows])) for e in HSE_ORDER])
            bg_iso = float(np.median([r["os_iso"] for r in bg_rows]))
        else:
            bg_vec = ucc_vec
            bg_iso = UCC_187OS_188OS

        evaluated = []
        for r in rows:
            in_ydb = bool(ydb_predicate(r))
            is_unrad = bool(r.get("os_iso") is not None and r["os_iso"] < site_os_med - 0.15)
            has_all6 = all(r.get(e) is not None and r[e] > 0 for e in HSE_ORDER)
            entry = dict(r)
            entry["in_ydb_window"] = in_ydb
            entry["is_unradiogenic"] = is_unrad
            entry["is_target"] = in_ydb or is_unrad
            entry["has_all6"] = has_all6
            if r.get("Pt") and r.get("Ir"):
                entry["pt_ir"] = r["Pt"] / r["Ir"]
            if r.get("Pt") and r.get("Pd"):
                entry["pt_pd"] = r["Pt"] / r["Pd"]
            if r.get("Os") and r.get("Ir"):
                entry["os_ir"] = r["Os"] / r["Ir"]
            if r.get("Re") and r.get("Os"):
                entry["re_os"] = r["Re"] / r["Os"]

            if has_all6:
                vec = hse_vec(r)
                cls, dists = clr_classify(vec, prototypes_clr)
                fit_ci = mixing_rmse(vec, r["os_iso"], bg_vec, bg_iso, ci_vec, CI_187OS_188OS)
                fit_iron = mixing_rmse(vec, r["os_iso"], bg_vec, bg_iso, iron_vec, CI_187OS_188OS)
                volc_fits = {vn: mixing_rmse(vec, r["os_iso"], bg_vec, bg_iso, vv, 0.15) for vn, vv in volc_refs.items()}
                best_v = min(volc_fits, key=lambda k: volc_fits[k]["rmse"])
                kud_key = next((k for k in volc_fits if "kudryavy" in k.lower()), best_v)
                delta_rmse = min(fit_ci["rmse"], fit_iron["rmse"]) - volc_fits[best_v]["rmse"]
                delta_rmse_kud = min(fit_ci["rmse"], fit_iron["rmse"]) - volc_fits[kud_key]["rmse"]
                # Sensitivity check using UCC background
                fit_ci_ucc = mixing_rmse(vec, r["os_iso"], ucc_vec, UCC_187OS_188OS, ci_vec, CI_187OS_188OS)
                fit_v_ucc = min(
                    mixing_rmse(vec, r["os_iso"], ucc_vec, UCC_187OS_188OS, vv, 0.15)["rmse"]
                    for vv in volc_refs.values()
                )
                entry.update({
                    "nearest_class": cls,
                    "clr_dists": dists,
                    "cosmic_clr_win": min(dists["chondrite"], dists["kpg_impact"]) < min(dists["volcanic"], dists["ucc"]),
                    "rmse_ci": fit_ci["rmse"],
                    "rmse_iron": fit_iron["rmse"],
                    "rmse_volc_best": volc_fits[best_v]["rmse"],
                    "best_volc_name": best_v,
                    "rmse_kudryavy": volc_fits[kud_key]["rmse"],
                    "delta_rmse": delta_rmse,
                    "delta_rmse_kudryavy": delta_rmse_kud,
                    "delta_rmse_ucc_bg": fit_ci_ucc["rmse"] - fit_v_ucc,
                    "ci_clr": [float(v) for v in ci_clr(vec)],
                })
            evaluated.append(entry)

        return {
            "site": site_name,
            "n_total": len(rows),
            "n_all6": sum(1 for e in evaluated if e["has_all6"]),
            "site_os_median": site_os_med,
            "bg_ppt": {el: float(v) for el, v in zip(HSE_ORDER, bg_vec)},
            "bg_os_iso": bg_iso,
            "samples": evaluated,
        }

    hc_eval = evaluate_site_column(
        halls_cave,
        "Hall's Cave, TX",
        lambda r: r.get("age_ka") is not None and 12.6 <= r["age_ka"] <= 13.1,
    )
    pl_eval = evaluate_site_column(
        page_ladson,
        "Page-Ladson, FL",
        lambda r: 847.0 <= r["depth_cm"] <= 860.0,
    )

    # Pool Pillar 1A target samples (full 6-HSE)
    all_targets = [
        e for col in (hc_eval, pl_eval) for e in col["samples"]
        if e["has_all6"] and e["is_target"]
    ]
    strict_ydb_targets = [
        e for col in (hc_eval, pl_eval) for e in col["samples"]
        if e["has_all6"] and e["in_ydb_window"]
    ]
    unrad_targets = [
        e for col in (hc_eval, pl_eval) for e in col["samples"]
        if e["has_all6"] and e["is_unradiogenic"]
    ]

    def summarize_targets(tlist: list[dict[str, Any]]) -> dict[str, Any]:
        if not tlist:
            return {"n": 0}
        deltas = np.array([t["delta_rmse"] for t in tlist], dtype=float)
        deltas_kud = np.array([t["delta_rmse_kudryavy"] for t in tlist], dtype=float)
        rng = np.random.default_rng(1202026)
        boot = [float(np.median(rng.choice(deltas, size=len(deltas), replace=True))) for _ in range(2000)]
        try:
            w_stat, w_p = stats.wilcoxon(deltas)
        except ValueError:
            w_stat, w_p = float("nan"), float("nan")
        counts = {k: sum(1 for t in tlist if t["nearest_class"] == k) for k in prototypes_clr}
        cosmic_clr_frac = sum(1 for t in tlist if t["cosmic_clr_win"]) / len(tlist)
        return {
            "n": len(tlist),
            "class_counts": counts,
            "cosmic_clr_frac": cosmic_clr_frac,
            "noncosmic_clr_frac": 1.0 - cosmic_clr_frac,
            "volc_mix_win_frac": float(np.mean(deltas > 0)),
            "median_delta_rmse": float(np.median(deltas)),
            "delta_rmse_ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
            "wilcoxon_p": float(w_p),
            "median_delta_rmse_kudryavy": float(np.median(deltas_kud)),
            "median_pt_ir": float(np.median([t["pt_ir"] for t in tlist if "pt_ir" in t])),
            "median_pt_pd": float(np.median([t["pt_pd"] for t in tlist if "pt_pd" in t])),
            "median_os_ir": float(np.median([t["os_ir"] for t in tlist if "os_ir" in t])),
            "median_re_os": float(np.median([t["re_os"] for t in tlist if "re_os" in t])),
        }

    p1a_all = summarize_targets(all_targets)
    p1a_strict = summarize_targets(strict_ydb_targets)
    p1a_unrad = summarize_targets(unrad_targets)

    # 4. Pillar 2 — Blind stratigraphic peak-uniqueness audit on independent full-HSE columns
    blind_audits: list[dict[str, Any]] = []

    def audit_column(
        site: str,
        study: str,
        tier: str,
        proxy: str,
        rows: list[dict[str, Any]],
        val_key: str,
        mode: str,
        ydb_pred,
    ) -> None:
        valid = [r for r in rows if r.get(val_key) is not None and np.isfinite(r[val_key])]
        if len(valid) < 6:
            return
        vals = [float(r[val_key]) for r in valid]
        res = detect_blind_peaks(vals, mode=mode)
        in_ydb_mask = [bool(ydb_pred(r)) for r in valid]
        n_ydb_levels = sum(in_ydb_mask)
        n_inside = 0
        n_outside = 0
        for ev in res["events"]:
            hit = any(in_ydb_mask[idx] for idx in ev["indices"])
            ev["in_ydb_window"] = hit
            ev["depth_cm"] = valid[ev["peak_idx"]].get("depth_cm")
            ev["age_ka"] = valid[ev["peak_idx"]].get("age_ka")
            if hit:
                n_inside += 1
            else:
                n_outside += 1
        g_idx = res["global_extreme_idx"]
        global_in_ydb = bool(in_ydb_mask[g_idx]) if g_idx is not None else False
        blind_audits.append({
            "site": site,
            "study": study,
            "tier": tier,
            "proxy": proxy,
            "mode": mode,
            "n_levels": len(valid),
            "n_ydb_levels": n_ydb_levels,
            "null_hit_prob": n_ydb_levels / len(valid),
            "baseline": res["baseline"],
            "n_events_total": len(res["events"]),
            "n_events_inside": n_inside,
            "n_events_outside": n_outside,
            "has_outside_peak": n_outside > 0,
            "global_extreme_in_ydb": global_in_ydb,
            "global_extreme_val": vals[g_idx] if g_idx is not None else None,
            "global_extreme_depth": valid[g_idx].get("depth_cm") if g_idx is not None else None,
            "global_extreme_age": valid[g_idx].get("age_ka") if g_idx is not None else None,
            "events": res["events"],
        })

    # Independent Tier-1 columns: Hall's Cave & Page-Ladson
    hc_ydb = lambda r: r.get("age_ka") is not None and 12.6 <= r["age_ka"] <= 13.0
    pl_ydb = lambda r: 848.0 <= r["depth_cm"] <= 855.0
    for proxy, mode in [("Pt", "high"), ("Os", "high"), ("Ir", "high"), ("os_iso", "low_iso")]:
        audit_column("Hall's Cave, TX", "Sun et al. (2020)", "independent", proxy, halls_cave, proxy, mode, hc_ydb)
        audit_column("Page-Ladson, FL", "Nana Yobo et al. (2026)", "independent", proxy, page_ladson, proxy, mode, pl_ydb)

    # Proponent Tier-2 column: White Pond SC (Moore et al. 2019)
    wp_rows = parse_moore2019_white_pond(DATA / "moore2019_s1.pdf")
    # Moore et al. 2019 places White Pond YDB at ~224-230 cm (12,835-12,735 cal BP)
    wp_ydb = lambda r: 222.0 <= r["depth_cm"] <= 232.0
    audit_column("White Pond, SC", "Moore et al. (2019)", "proponent", "Pt", wp_rows, "pt_ppb", "high", wp_ydb)
    audit_column("White Pond, SC", "Moore et al. (2019)", "proponent", "Pt/Pd", wp_rows, "pt_pd", "high", wp_ydb)

    # Summarize Pillar 2 for independent Tier-1 columns
    indep_audits = [a for a in blind_audits if a["tier"] == "independent"]
    indep_in = sum(a["n_events_inside"] for a in indep_audits)
    indep_out = sum(a["n_events_outside"] for a in indep_audits)
    indep_tot = indep_in + indep_out
    indep_frac_out = indep_out / indep_tot if indep_tot > 0 else 1.0
    indep_probs = [a["null_hit_prob"] for a in indep_audits]
    indep_hits = sum(1 for a in indep_audits if a["global_extreme_in_ydb"])
    indep_perm_p = poisson_binomial_tail(indep_probs, indep_hits)

    # Cross-site Pt/Ir summary (Pillar 1B)
    ydb_pt_ir_sites: list[dict[str, Any]] = []
    if p1a_strict.get("n", 0) > 0:
        hc_ydb_pt_ir = [e["pt_ir"] for e in hc_eval["samples"] if e["in_ydb_window"] and "pt_ir" in e]
        pl_ydb_pt_ir = [e["pt_ir"] for e in pl_eval["samples"] if e["in_ydb_window"] and "pt_ir" in e]
        if hc_ydb_pt_ir:
            ydb_pt_ir_sites.append({"site": "Hall's Cave, TX (YDB)", "pt_ir": float(np.median(hc_ydb_pt_ir)), "source": "Sun et al. (2020)"})
        if pl_ydb_pt_ir:
            ydb_pt_ir_sites.append({"site": "Page-Ladson, FL (YDB)", "pt_ir": float(np.median(pl_ydb_pt_ir)), "source": "Nana Yobo et al. (2026)"})
    for wk in wonderkrater:
        if "pt/ir" in wk["ratio_name"].lower() and wk["ydb_avg"] is not None:
            ydb_pt_ir_sites.append({"site": "Wonderkrater, South Africa (YDB)", "pt_ir": float(wk["ydb_avg"]), "source": "Thackeray et al. (2026)"})
    ydb_pt_ir_sites.append({"site": "GISP2, Greenland (peak)", "pt_ir": GISP2_PETAEV_2013["pt_ir_mid"], "source": GISP2_PETAEV_2013["source"]})

    ydb_pt_ir_vals = [s["pt_ir"] for s in ydb_pt_ir_sites if s["pt_ir"] > 0]
    kpg_pt_ir_vals = [r["pt_ir"] for r in kpg_eval if r["pt_ir"] > 0]

    verdict = decide_verdict(
        kpg_clr_pass_frac=kpg_clr_pass,
        kpg_mix_pass_frac=kpg_mix_pass,
        ydb_cosmic_clr_frac=p1a_all.get("cosmic_clr_frac", 0.5),
        ydb_noncosmic_clr_frac=p1a_all.get("noncosmic_clr_frac", 0.5),
        ydb_median_delta_rmse=p1a_all.get("median_delta_rmse", 0.0),
        ydb_median_pt_ir=float(np.median(ydb_pt_ir_vals)) if ydb_pt_ir_vals else None,
        indep_frac_outside=indep_frac_out,
        indep_perm_p=indep_perm_p,
    )

    # Amendment 1 transparent sensitivity checks (does NOT alter primary locked verdict or metrics)
    sens_audits: list[dict[str, Any]] = []
    hc_ydb_131 = lambda r: r.get("age_ka") is not None and 12.6 <= r["age_ka"] <= 13.1
    for proxy, mode in [("Pt", "high"), ("Os", "high"), ("Ir", "high"), ("os_iso", "low_iso")]:
        for site, study, rows, ypred in [
            ("Hall's Cave, TX", "Sun et al. (2020)", halls_cave, hc_ydb_131),
            ("Page-Ladson, FL", "Nana Yobo et al. (2026)", page_ladson, pl_ydb),
        ]:
            valid = [r for r in rows if r.get(proxy) is not None and np.isfinite(r[proxy])]
            vals = [float(r[proxy]) for r in valid]
            res = detect_blind_peaks(vals, mode=mode)
            mask = [bool(ypred(r)) for r in valid]
            n_in = sum(1 for ev in res["events"] if any(mask[i] for i in ev["indices"]))
            n_out = len(res["events"]) - n_in
            g_hit = bool(mask[res["global_extreme_idx"]]) if res["global_extreme_idx"] is not None else False
            sens_audits.append({
                "site": site,
                "proxy": proxy,
                "n_levels": len(valid),
                "n_ydb_levels": sum(mask),
                "null_hit_prob": sum(mask) / len(valid),
                "events_inside": n_in,
                "events_outside": n_out,
                "global_in_ydb": g_hit,
            })
    sens_in = sum(a["events_inside"] for a in sens_audits)
    sens_out = sum(a["events_outside"] for a in sens_audits)
    sens_hits = sum(1 for a in sens_audits if a["global_in_ydb"])
    sens_perm_p = poisson_binomial_tail([a["null_hit_prob"] for a in sens_audits], sens_hits)

    # 5-HSE sensitivity (Os, Ir, Pt, Pd, Re — dropping Ru=bdl) for Page-Ladson 36-30 (851 cm, iso=0.51)
    pl_36_30_sens = {}
    for r in page_ladson:
        if r["sample"] == "36-30" and r["os_iso"] < 0.60:
            idx5 = [0, 1, 3, 4, 5]  # Os, Ir, Pt, Pd, Re
            v5 = np.array([r[HSE_ORDER[i]] for i in idx5], dtype=float)
            ci5 = ci_vec[idx5]
            z5 = np.log10(v5 / ci5)
            z5 -= np.mean(z5)
            p5_dists = {}
            for pname, pref in [("chondrite", ci_vec), ("ucc", ucc_vec)]:
                zp = np.log10(pref[idx5] / ci5)
                zp -= np.mean(zp)
                p5_dists[pname] = float(np.linalg.norm(z5 - zp))
            v_clrs5 = []
            for vv in volc_refs.values():
                zp = np.log10(vv[idx5] / ci5)
                zp -= np.mean(zp)
                v_clrs5.append(zp)
            p5_dists["volcanic"] = float(np.linalg.norm(z5 - np.mean(v_clrs5, axis=0)))
            k_clrs5 = []
            for ks in kpg_samples:
                kv = hse_vec(ks)
                zp = np.log10(kv[idx5] / ci5)
                zp -= np.mean(zp)
                k_clrs5.append(zp)
            p5_dists["kpg_impact"] = float(np.linalg.norm(z5 - np.median(k_clrs5, axis=0)))
            pl_36_30_sens = {
                "sample": "36-30 (851 cm, Ru=bdl)",
                "os_iso": r["os_iso"],
                "pt_ir": r["Pt"] / r["Ir"],
                "re_os": r["Re"] / r["Os"],
                "nearest_class_5hse": min(p5_dists, key=p5_dists.get),
                "clr5_dists": p5_dists,
            }
            break

    summary = {
        "question": "yd-platinum-fingerprint",
        "issue": 120,
        "verdict": verdict,
        "reference_endmembers": {
            "ci_chondrite_ppt": CI_CHONDRITE_PPT,
            "ucc_ppt": {el: float(v) for el, v in zip(HSE_ORDER, ucc_vec)},
            "iron_steelman_name": best_iron_name,
            "iron_steelman_ppt": {el: float(v) for el, v in zip(HSE_ORDER, iron_vec)},
            "volcanic_condensates_ppt": {k: {el: float(v) for el, v in zip(HSE_ORDER, arr)} for k, arr in volc_refs.items()},
            "niuatahi_tonga_ppt": NIUATAHI_VOLCANIC_PPT,
            "laacher_see_n": len(laacher_see),
            "laacher_see_samples": laacher_see,
        },
        "positive_control_kpg": {
            "n_samples": len(kpg_eval),
            "strict_chondrite_clr_pass_frac": kpg_clr_pass,
            "cosmic_mix_pass_frac": kpg_mix_pass,
            "median_pt_ir": float(np.median(kpg_pt_ir_vals)) if kpg_pt_ir_vals else None,
            "log10_pt_ir_iqr": float(np.subtract(*np.percentile(np.log10(kpg_pt_ir_vals), [75, 25]))) if len(kpg_pt_ir_vals) >= 4 else None,
            "log10_pt_ir_span": float(np.log10(max(kpg_pt_ir_vals) / min(kpg_pt_ir_vals))) if len(kpg_pt_ir_vals) >= 2 else None,
            "samples": kpg_eval,
        },
        "pillar1a_full_hse": {
            "all_targets": p1a_all,
            "strict_ydb_targets": p1a_strict,
            "unradiogenic_targets": p1a_unrad,
            "halls_cave": hc_eval,
            "page_ladson": pl_eval,
        },
        "pillar1b_cross_site": {
            "ydb_pt_ir_sites": ydb_pt_ir_sites,
            "ydb_pt_ir_median": float(np.median(ydb_pt_ir_vals)) if ydb_pt_ir_vals else None,
            "ydb_log10_pt_ir_span": float(np.log10(max(ydb_pt_ir_vals) / min(ydb_pt_ir_vals))) if len(ydb_pt_ir_vals) >= 2 else None,
            "wonderkrater_table1": wonderkrater,
            "white_pond_n": len(wp_rows),
            "white_pond_samples": wp_rows,
        },
        "pillar2_blind_peaks": {
            "independent_events_inside": indep_in,
            "independent_events_outside": indep_out,
            "independent_frac_outside": indep_frac_out,
            "independent_global_hits": indep_hits,
            "independent_n_series": len(indep_audits),
            "independent_perm_p": indep_perm_p,
            "audits": blind_audits,
        },
        "sensitivity_amendment1": {
            "halls_cave_131_window": {
                "independent_events_inside": sens_in,
                "independent_events_outside": sens_out,
                "independent_frac_outside": sens_out / max(sens_in + sens_out, 1),
                "independent_global_hits": sens_hits,
                "independent_perm_p": sens_perm_p,
                "audits": sens_audits,
            },
            "page_ladson_36_30_5hse": pl_36_30_sens,
        },
    }

    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # Export clean TSVs
    with (RESULTS / "ydb_geochemistry.tsv").open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["site", "sample", "depth_cm", "age_ka", "os_iso", "Os_ppt", "Ir_ppt", "Ru_ppt", "Pt_ppt", "Pd_ppt", "Re_ppt", "Pt_Ir", "Pt_Pd", "Os_Ir", "Re_Os", "in_ydb", "is_unrad", "nearest_class", "delta_rmse"])
        for col in (hc_eval, pl_eval):
            for s in col["samples"]:
                w.writerow([
                    s["site"], s["sample"], s["depth_cm"], s.get("age_ka", ""),
                    s.get("os_iso", ""), s.get("Os", ""), s.get("Ir", ""), s.get("Ru", ""),
                    s.get("Pt", ""), s.get("Pd", ""), s.get("Re", ""),
                    f"{s['pt_ir']:.3f}" if "pt_ir" in s else "",
                    f"{s['pt_pd']:.3f}" if "pt_pd" in s else "",
                    f"{s['os_ir']:.3f}" if "os_ir" in s else "",
                    f"{s['re_os']:.3f}" if "re_os" in s else "",
                    int(s["in_ydb_window"]), int(s["is_unradiogenic"]),
                    s.get("nearest_class", ""),
                    f"{s['delta_rmse']:.4f}" if "delta_rmse" in s else "",
                ])

    with (RESULTS / "blind_peaks.tsv").open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["site", "study", "tier", "proxy", "n_levels", "n_ydb_levels", "events_total", "events_inside", "events_outside", "global_in_ydb", "global_val", "global_depth_cm"])
        for a in blind_audits:
            w.writerow([
                a["site"], a["study"], a["tier"], a["proxy"], a["n_levels"], a["n_ydb_levels"],
                a["n_events_total"], a["n_events_inside"], a["n_events_outside"],
                int(a["global_extreme_in_ydb"]), a["global_extreme_val"], a["global_extreme_depth"],
            ])

    return summary


if __name__ == "__main__":
    out = run_pipeline()
    print(f"Verdict: {out['verdict']}")
    print(f"K-Pg control: n={out['positive_control_kpg']['n_samples']}, CLR={out['positive_control_kpg']['strict_chondrite_clr_pass_frac']:.1%}, Mix={out['positive_control_kpg']['cosmic_mix_pass_frac']:.1%}")
    print(f"Pillar 1A targets: {out['pillar1a_full_hse']['all_targets']}")
    print(f"Pillar 2 independent blind peaks: inside={out['pillar2_blind_peaks']['independent_events_inside']}, outside={out['pillar2_blind_peaks']['independent_events_outside']}, perm_p={out['pillar2_blind_peaks']['independent_perm_p']:.4g}")
