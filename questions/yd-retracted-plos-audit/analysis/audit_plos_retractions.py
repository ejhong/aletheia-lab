#!/usr/bin/env python3
"""
Pre-registered audit of the two February 11, 2026 PLOS One Younger Dryas retractions:
  Paper A: Moore et al. (2025) Baffin Bay marine cores (e0328347, retracted e0342613)
  Paper B: Kennett et al. (2025) Shocked quartz at 3 US sites (e0319840, retracted e0342620)

Standard library + numpy + scipy + pypdf only. Zero network calls.
Locked protocol: questions/yd-retracted-plos-audit/protocol.md (Issue #127).
"""
from __future__ import annotations

import csv
import json
import math
import pathlib
import re
import statistics
import xml.etree.ElementTree as ET
import zipfile
from typing import Any

import numpy as np
from pypdf import PdfReader
from scipy.stats import chi2

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"

# Reference geochemical compositions (ppm unless noted)
# Upper Continental Crust (Rudnick & Gao 2003, Treatise on Geochemistry):
# FeO_T = 5.04 wt% -> Fe = 39,180 ppm (~39,200 ppm); Cr = 92 ppm; Ni = 47 ppm; Co = 17.3 ppm;
# Pt = 0.5 ppb; Ir = 0.022 ppb; Pd = 0.52 ppb.
UCC_REF = {
    "Fe_ppm": 39200.0,
    "Cr_ppm": 92.0,
    "Ni_ppm": 47.0,
    "Co_ppm": 17.3,
    "Pt_ppb": 0.5,
    "Ir_ppb": 0.022,
    "Pd_ppb": 0.52,
}
# USGS Basalt Glass standard BIR-1G (GeoReM preferred values, Jochum et al. 2005):
# FeO_T = 10.4 wt% -> Fe = 80,800 ppm (or ~79,000); Cr = 391 ppm; Ni = 166 ppm; Co = 52 ppm.
BIR1G_REF = {
    "Fe_ppm": 79000.0,
    "Cr_ppm": 391.0,
    "Ni_ppm": 166.0,
    "Co_ppm": 52.0,
}
# CI Chondrite (Lodders 2003 / Wasson & Kallemeyn 1988):
CI_REF = {
    "Fe_ppm": 185000.0,
    "Cr_ppm": 2650.0,
    "Ni_ppm": 10800.0,
    "Co_ppm": 506.0,
    "Pt_ppb": 990.0,
    "Ir_ppb": 465.0,
    "Pd_ppb": 560.0,
}

# Pre-registered Baffin Bay core metadata (from Moore et al. 2025 Table 1 & Fig. 2)
BAFFIN_CORES = {
    "52": {"name": "83023-052", "length_cm": 875.0, "water_depth_m": 512, "ydb_cm": (625.0, 630.0), "dr_holocene": 71.0, "dr_err": 50.0},
    "64": {"name": "2013029-064", "length_cm": 713.0, "water_depth_m": 875, "ydb_cm": (312.0, 318.0), "dr_holocene": 218.0, "dr_err": 50.0},
    "67": {"name": "2008029-067", "length_cm": 519.0, "water_depth_m": 2357, "ydb_cm": (32.0, 35.0), "dr_holocene": 218.0, "dr_err": 50.0},
    "77": {"name": "2013029-077", "length_cm": 649.5, "water_depth_m": 1153, "ydb_cm": (161.0, 162.0), "dr_holocene": 103.0, "dr_err": 50.0},
}

# Complete published direct/YDB-stratum 14C inventories for Paper B's 3 sites
# Verified from primary sources in Issue #113 (ydb-site-synchrony/MANIFEST.md):
# - Arlington Canyon AC-003 (Kennett et al. 2008 QSR Table 4, depths 482-502 cm around YDB)
# - Blackwater Draw (Waters & Stafford 2007 Science Table 1 + Haynes / Kennett 2015)
# - Murray Springs (Waters & Stafford 2007 Science Table 1 + Haynes / Kennett 2015)
PUBLISHED_DIRECT_INVENTORY = {
    "Arlington Canyon": [
        # Kennett et al. (2008) QSR Table 4, AC-003 direct charcoal/wood dates in 482-505 cm YDB zone
        {"lab": "UCIAMS-36305", "depth_cm": 482.5, "c14": 10960, "err": 50, "material": "charcoal", "source": "Kennett et al. 2008 Table 4"},
        {"lab": "UCIAMS-36306", "depth_cm": 495.5, "c14": 11185, "err": 30, "material": "charcoal", "source": "Kennett et al. 2008 Table 4"},
        {"lab": "UCIAMS-36307", "depth_cm": 495.5, "c14": 11075, "err": 30, "material": "charcoal", "source": "Kennett et al. 2008 Table 4"},
        {"lab": "UCIAMS-36308", "depth_cm": 500.5, "c14": 11110, "err": 35, "material": "charcoal", "source": "Kennett et al. 2008 Table 4"},
        {"lab": "UCIAMS-36309", "depth_cm": 500.5, "c14": 11440, "err": 90, "material": "wood/charcoal", "source": "Kennett et al. 2008 Table 4"},
        {"lab": "UCIAMS-36960", "depth_cm": 500.5, "c14": 11070, "err": 25, "material": "charcoal", "source": "Kennett et al. 2008 Table 4"},
        {"lab": "UCIAMS-36961", "depth_cm": 500.5, "c14": 11105, "err": 30, "material": "charcoal", "source": "Kennett et al. 2008 Table 4"},
        {"lab": "UCIAMS-36962", "depth_cm": 500.5, "c14": 11105, "err": 30, "material": "charcoal", "source": "Kennett et al. 2008 Table 4"},
        {"lab": "UCIAMS-42817", "depth_cm": 500.5, "c14": 11100, "err": 30, "material": "charcoal", "source": "Kennett et al. 2008 Table 4"},
        {"lab": "UCIAMS-42818", "depth_cm": 500.5, "c14": 11095, "err": 25, "material": "charcoal", "source": "Kennett et al. 2008 Table 4"},
        {"lab": "UCIAMS-42819", "depth_cm": 500.5, "c14": 11050, "err": 30, "material": "charcoal", "source": "Kennett et al. 2008 Table 4"},
    ],
    "Blackwater Draw": [
        # Waters & Stafford (2007) Table 1 Clovis/YDB contact + Haynes black mat dates
        {"lab": "A-481", "depth_cm": None, "c14": 11170, "err": 360, "material": "plant carbonized (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "A-490", "depth_cm": None, "c14": 11040, "err": 500, "material": "plant carbonized (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "A-491", "depth_cm": None, "c14": 11630, "err": 400, "material": "plant carbonized (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "UCIAMS-24212", "depth_cm": None, "c14": 11300, "err": 240, "material": "bulk organic / YDB contact", "source": "Firestone et al. 2007 / Kennett 2015"},
        {"lab": "A-489", "depth_cm": None, "c14": 10490, "err": 200, "material": "diatomite / black mat", "source": "Haynes 1995 / Meltzer 2014"},
        {"lab": "A-379", "depth_cm": None, "c14": 10780, "err": 100, "material": "organic mud / black mat", "source": "Haynes 2008 / Kennett 2015"},
    ],
    "Murray Springs": [
        # Waters & Stafford (2007) Table 1 (8 Haynes dates on Clovis/YDB black-mat contact)
        {"lab": "A-805", "depth_cm": None, "c14": 11150, "err": 450, "material": "charcoal (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "A-805A", "depth_cm": None, "c14": 11230, "err": 340, "material": "charcoal (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "A-805B", "depth_cm": None, "c14": 10930, "err": 170, "material": "charcoal (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "A-805C", "depth_cm": None, "c14": 10890, "err": 180, "material": "charcoal (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "A-805D", "depth_cm": None, "c14": 10840, "err": 70, "material": "charcoal (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "A-805E", "depth_cm": None, "c14": 10840, "err": 140, "material": "charcoal (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "A-805F", "depth_cm": None, "c14": 10710, "err": 160, "material": "charcoal (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "Tx-1413", "depth_cm": None, "c14": 10760, "err": 100, "material": "charcoal (Clovis)", "source": "Waters & Stafford 2007"},
    ],
}


# ---------------------------------------------------------------------------
# 1. Radiocarbon Calibration Engine (Marine20 & IntCal20) + Ward-Wilson T
# ---------------------------------------------------------------------------
def load_cal_curve(path: pathlib.Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load a .14c calibration curve sorted ascending by cal BP."""
    cal, c14, sig = [], [], []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = [p for p in re.split(r"[,\s]+", s) if p]
            if len(parts) < 3:
                continue
            try:
                cal.append(float(parts[0]))
                c14.append(float(parts[1]))
                sig.append(float(parts[2]))
            except ValueError:
                continue
    order = np.argsort(cal)
    return np.array(cal)[order], np.array(c14)[order], np.array(sig)[order]


def calibrate_14c(
    c14_age: float,
    c14_err: float,
    curve: tuple[np.ndarray, np.ndarray, np.ndarray],
    delta_r: float = 0.0,
    delta_r_err: float = 0.0,
    grid_step: float = 5.0,
    cal_min: float = 0.0,
    cal_max: float = 30000.0,
) -> dict[str, Any]:
    """
    Exact numerical radiocarbon calibration with flat calendar prior.
    Subtracts delta_r from measured marine 14C age before matching curve,
    propagating lab + curve + delta_r variance.
    """
    cal_c, c14_c, sig_c = curve
    grid = np.arange(cal_min, cal_max + grid_step, grid_step)
    mu = np.interp(grid, cal_c, c14_c)
    s_curve = np.interp(grid, cal_c, sig_c)
    adj_age = c14_age - delta_r
    var_tot = (c14_err ** 2) + (s_curve ** 2) + (delta_r_err ** 2)
    log_p = -0.5 * ((adj_age - mu) ** 2) / var_tot - 0.5 * np.log(var_tot)
    log_p -= np.max(log_p)
    p = np.exp(log_p)
    total = float(np.sum(p))
    if total <= 0:
        raise ValueError("Calibration likelihood collapsed to zero.")
    p /= total

    cdf = np.cumsum(p)
    median = float(np.interp(0.5, cdf, grid))
    mean = float(np.sum(p * grid))
    sd = float(math.sqrt(max(0.0, float(np.sum(p * ((grid - mean) ** 2))))))

    def hpd_bounds(level: float) -> tuple[float, float]:
        idx = np.argsort(p)[::-1]
        acc = 0.0
        chosen = []
        for i in idx:
            chosen.append(grid[i])
            acc += p[i]
            if acc >= level:
                break
        return (float(min(chosen)), float(max(chosen)))

    hpd68 = hpd_bounds(0.6827)
    hpd95 = hpd_bounds(0.9545)

    p_ydb_narrow = float(np.sum(p[(grid >= 12700.0) & (grid <= 12900.0)]))
    p_yd_full = float(np.sum(p[(grid >= 11700.0) & (grid <= 12900.0)]))
    p_younger_12700 = float(np.sum(p[grid < 12700.0]))
    p_post_yd = float(np.sum(p[grid < 11700.0]))

    return {
        "c14_age": round(float(c14_age), 1),
        "c14_err": round(float(c14_err), 1),
        "delta_r": round(float(delta_r), 1),
        "delta_r_err": round(float(delta_r_err), 1),
        "median_cal_bp": round(median, 1),
        "mean_cal_bp": round(mean, 1),
        "sd_cal_yr": round(sd, 1),
        "hpd68": [round(hpd68[0], 1), round(hpd68[1], 1)],
        "hpd95": [round(hpd95[0], 1), round(hpd95[1], 1)],
        "p_ydb_12900_12700": round(p_ydb_narrow, 4),
        "p_yd_12900_11700": round(p_yd_full, 4),
        "p_younger_12700": round(p_younger_12700, 4),
        "p_post_yd_lt11700": round(p_post_yd, 4),
        "prob_sum": round(float(np.sum(p)), 6),
    }


def ward_wilson_t(ages: list[float], errs: list[float]) -> dict[str, float]:
    """Ward & Wilson (1978) chi-square homogeneity test T on uncalibrated 14C ages."""
    a = np.asarray(ages, dtype=float)
    s = np.asarray(errs, dtype=float)
    if len(a) < 2:
        return {"n": len(a), "weighted_mean": float(a[0]) if len(a) else math.nan, "T": 0.0, "df": 0, "p_value": 1.0}
    w = 1.0 / (s ** 2)
    wm = float(np.sum(w * a) / np.sum(w))
    T = float(np.sum(w * ((a - wm) ** 2)))
    df = len(a) - 1
    pval = float(1.0 - chi2.cdf(T, df))
    return {"n": len(a), "weighted_mean": round(wm, 2), "T": round(T, 3), "df": df, "p_value": round(pval, 6)}


# ---------------------------------------------------------------------------
# 2. Pure-stdlib XLSX Reader
# ---------------------------------------------------------------------------
def _col_idx(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch.upper()) - ord("A") + 1)
    return idx - 1


def read_xlsx_sheet(path: pathlib.Path, sheet_index: int = 0) -> list[list[str]]:
    ns = {
        "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    with zipfile.ZipFile(path) as z:
        sst: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", ns):
                sst.append("".join(t.text or "" for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")))
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rmap = {r.attrib["Id"]: r.attrib["Target"] for r in rels}
        sheets = wb.findall(".//m:sheet", ns)
        sh = sheets[sheet_index]
        rid = sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        tgt = "xl/" + rmap[rid].lstrip("/")
        if tgt not in z.namelist():
            tgt = rmap[rid].lstrip("/")
        sroot = ET.fromstring(z.read(tgt))
        out: list[list[str]] = []
        for row in sroot.findall(".//m:sheetData/m:row", ns):
            cells = row.findall("m:c", ns)
            if not cells:
                out.append([])
                continue
            max_c = max(_col_idx(c.attrib.get("r", "A1")) for c in cells)
            vals = [""] * (max_c + 1)
            for c in cells:
                ci = _col_idx(c.attrib.get("r", "A1"))
                t = c.attrib.get("t")
                v = c.find("m:v", ns)
                if v is not None and v.text is not None:
                    vals[ci] = sst[int(v.text)] if t == "s" else v.text
                else:
                    is_el = c.find("m:is", ns)
                    if is_el is not None:
                        vals[ci] = "".join(x.text or "" for x in is_el.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
            out.append(vals)
        return out


def to_float(s: str) -> float | None:
    if s is None:
        return None
    t = str(s).strip().replace(",", "").replace("−", "-")
    if not t or t in {"--", "-", "ND", "nd", "n/a", "N/A", "BDL", "<LOD"}:
        return None
    try:
        v = float(t)
        return v if math.isfinite(v) else None
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# 3. Pillar 1 — Baffin Bay Radiocarbon & Polar Reservoir Sensitivity
# ---------------------------------------------------------------------------
def parse_baffin_radiocarbon(pdf: PdfReader) -> tuple[list[dict[str, Any]], dict[str, Any], str]:
    """Parse SI Table S1 (p5) and Foraminifera dating section (pp219-222)."""
    p5_txt = pdf.pages[4].extract_text() or ""
    p6_13_txt = "\n".join((pdf.pages[i].extract_text() or "") for i in range(5, 13))
    foram_txt = "\n".join((pdf.pages[i].extract_text() or "") for i in range(218, 223))

    # Extract raw 14C rows from p5 (and fallback p6-13 if any wrapped)
    rows: list[dict[str, Any]] = []
    cur_core = None
    for line in p5_txt.splitlines():
        s = line.strip()
        if not s:
            continue
        # Detect core label
        m_core = re.search(r"\b(?:Core\s*)?(?:83023[-–]?0?|2013029[-–]?0?|2008029[-–]?0?)?(52|64|67|77)\b", s)
        # Look for depth + 14C age + +/- err patterns: e.g. "625-630" or "627.5" and "11,340 ± 40" or "11340 40"
        m_age = re.search(r"(\d{1,2},?\d{3})\s*(?:±|\+/-|\s+)\s*(\d{2,3})\b", s)
        if m_core and (s.lower().startswith("core") or re.match(r"^(?:83023|2013029|2008029|52|64|67|77)\b", s)):
            cur_core = m_core.group(1)
        if m_age and cur_core:
            c14_val = float(m_age.group(1).replace(",", ""))
            err_val = float(m_age.group(2))
            if 4000 <= c14_val <= 35000 and 10 <= err_val <= 600:
                # Extract depth before the age match
                pre = s[: m_age.start()]
                # Remove core prefix like 2013029-064 or 83023-052
                pre_clean = re.sub(r"\b(?:83023|2013029|2008029)[-–]0?\d+\b", "", pre)
                pre_clean = re.sub(r"\bCore\s*\d+\b", "", pre_clean, flags=re.I)
                m_dep_rng = re.search(r"(\d{1,3}(?:\.\d+)?)\s*[-–]\s*(\d{1,3}(?:\.\d+)?)", pre_clean)
                m_dep_one = re.findall(r"\b(\d{1,3}(?:\.\d+)?)\b", pre_clean)
                if m_dep_rng:
                    d_lo, d_hi = float(m_dep_rng.group(1)), float(m_dep_rng.group(2))
                    d_mid = 0.5 * (d_lo + d_hi)
                elif m_dep_one:
                    # Pick last number before 14C age (avoiding leading core id)
                    cand = [float(x) for x in m_dep_one if float(x) not in (52, 64, 67, 77) or len(m_dep_one) == 1]
                    d_mid = cand[-1] if cand else float(m_dep_one[-1])
                    d_lo = d_hi = d_mid
                else:
                    d_lo = d_hi = d_mid = math.nan
                lab_m = re.search(r"\b(?:UCIAMS|OS|Beta|CAMS|AA|TO|UOC|NOSAMS|AAR)[-–]?\d+\b", s, re.I)
                rows.append({
                    "core": cur_core,
                    "depth_lo_cm": d_lo,
                    "depth_hi_cm": d_hi,
                    "depth_mid_cm": d_mid,
                    "c14_age": c14_val,
                    "c14_err": err_val,
                    "lab_id": lab_m.group(0) if lab_m else "",
                    "raw_line": s,
                })

    # Metadata check in p5 + pp219-222
    has_species_list = bool(re.search(r"(Cassidulina|Nonionellina|Islandiella|Elphidium|Neogloboquadrina|benthic|planktic|mollus[ck]|foraminifera)", foram_txt + "\n" + p5_txt, re.I))
    has_individual_counts = bool(re.search(r"\b\d+\s+(?:specimens|individuals|tests|forams|foraminifera)\b", foram_txt + "\n" + p5_txt, re.I))
    has_5cm_uncertainty_note = bool(re.search(r"5\s*cm", foram_txt + "\n" + p5_txt, re.I))
    meta = {
        "n_parsed_raw_14c_dates": len(rows),
        "mentions_foram_taxa_in_si": has_species_list,
        "reports_specimen_counts_per_date": has_individual_counts,
        "mentions_5cm_layer_uncertainty": has_5cm_uncertainty_note,
        "foram_section_excerpt": foram_txt[:1500],
    }
    return rows, meta, f"=== SI Table S1 (p5) ===\n{p5_txt}\n\n=== Foraminifera Section (pp219-222) ===\n{foram_txt[:4000]}\n"


def run_pillar1_baffin_14c(pdf: PdfReader, marine20: tuple[np.ndarray, np.ndarray, np.ndarray]) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    dates, meta, raw_dump = parse_baffin_radiocarbon(pdf)
    scenarios = [
        ("S0_Holocene_Pearce2023", 0.0, 50.0),
        ("S1_Deglacial_plus200", 200.0, 100.0),
        ("S2_Deglacial_plus500", 500.0, 150.0),
        ("S3_Stadial_plus800", 800.0, 200.0),
    ]
    csv_rows: list[dict[str, Any]] = []
    per_core: dict[str, Any] = {}

    for cid, cinfo in BAFFIN_CORES.items():
        cdates = [d for d in dates if d["core"] == cid]
        ydb_lo, ydb_hi = cinfo["ydb_cm"]
        ydb_mid = 0.5 * (ydb_lo + ydb_hi)
        # Identify closest date(s) to the claimed YDB depth (within +/- 35 cm, or nearest bracketing)
        ranked = sorted(cdates, key=lambda d: abs(d["depth_mid_cm"] - ydb_mid) if not math.isnan(d["depth_mid_cm"]) else 9999.0)
        nearest = ranked[0] if ranked else None
        core_res: dict[str, Any] = {
            "core_name": cinfo["name"],
            "ydb_cm": [ydb_lo, ydb_hi],
            "dr_holocene": cinfo["dr_holocene"],
            "n_dates": len(cdates),
            "nearest_date_to_ydb": None,
            "scenarios_nearest": {},
            "all_dates": [],
        }
        for d in cdates:
            dist = abs(d["depth_mid_cm"] - ydb_mid) if not math.isnan(d["depth_mid_cm"]) else None
            d_cal: dict[str, Any] = {
                "depth_cm": d["depth_mid_cm"],
                "dist_to_ydb_cm": round(dist, 1) if dist is not None else None,
                "c14_age": d["c14_age"],
                "c14_err": d["c14_err"],
                "lab_id": d["lab_id"],
                "raw_line": d["raw_line"],
                "scenarios": {},
            }
            for sname, add_dr, dr_err in scenarios:
                cal = calibrate_14c(d["c14_age"], d["c14_err"], marine20, delta_r=cinfo["dr_holocene"] + add_dr, delta_r_err=dr_err)
                d_cal["scenarios"][sname] = cal
                csv_rows.append({
                    "core": cid,
                    "depth_mid_cm": d["depth_mid_cm"],
                    "is_nearest_to_ydb": int(d is nearest),
                    "c14_age": d["c14_age"],
                    "c14_err": d["c14_err"],
                    "scenario": sname,
                    "delta_r_total": cinfo["dr_holocene"] + add_dr,
                    "median_cal_bp": cal["median_cal_bp"],
                    "hpd95_lo": cal["hpd95"][0],
                    "hpd95_hi": cal["hpd95"][1],
                    "p_ydb_12900_12700": cal["p_ydb_12900_12700"],
                    "p_yd_12900_11700": cal["p_yd_12900_11700"],
                    "p_younger_12700": cal["p_younger_12700"],
                    "p_post_yd_lt11700": cal["p_post_yd_lt11700"],
                })
            core_res["all_dates"].append(d_cal)
            if d is nearest:
                core_res["nearest_date_to_ydb"] = {
                    "depth_cm": d["depth_mid_cm"],
                    "c14_age": d["c14_age"],
                    "c14_err": d["c14_err"],
                    "lab_id": d["lab_id"],
                }
                core_res["scenarios_nearest"] = d_cal["scenarios"]
        per_core[cid] = core_res

    # Evaluate A1 criterion: under S2 (+500 yr), how many of 4 cores shift nearest YDB date median < 12,500 cal BP or P(YDB 12900-12700) < 0.10
    s2_shifted = 0
    s0_in_ydb = 0
    for cid, cr in per_core.items():
        if cr["scenarios_nearest"]:
            s0 = cr["scenarios_nearest"]["S0_Holocene_Pearce2023"]
            s2 = cr["scenarios_nearest"]["S2_Deglacial_plus500"]
            if s0["hpd95"][0] <= 12900.0 and s0["hpd95"][1] >= 12700.0:
                s0_in_ydb += 1
            if s2["median_cal_bp"] < 12500.0 or s2["p_ydb_12900_12700"] < 0.10:
                s2_shifted += 1

    summary = {
        "metadata_audit": meta,
        "per_core": per_core,
        "n_cores_S0_overlap_ydb": s0_in_ydb,
        "n_cores_S2_shifted_off_ydb": s2_shifted,
        "criterion_A1_triggered": s2_shifted >= 2,
    }
    return summary, csv_rows, raw_dump


# ---------------------------------------------------------------------------
# 4. Pillar 2 — SI Figs S30-S34 Foraminifera, SI Table S6 Profiles, Table S7 NPs
# ---------------------------------------------------------------------------
def inspect_si_figs_s30_s34(pdf: PdfReader, out_img_dir: pathlib.Path) -> tuple[dict[str, Any], str]:
    """Extract captions, EDS text, and embedded SEM images for SI Figs S30-S34 (pp 32-35)."""
    out_img_dir.mkdir(parents=True, exist_ok=True)
    pages_info = []
    raw_chunks = []
    ca_c_o_hits = 0
    for pnum in (32, 33, 34, 35):
        pg = pdf.pages[pnum - 1]
        txt = pg.extract_text() or ""
        raw_chunks.append(f"=== baffin_bay_si.pdf p{pnum} ===\n{txt}\n")
        saved = []
        for idx, img in enumerate(pg.images):
            ext = pathlib.Path(img.name).suffix or ".bin"
            fn = out_img_dir / f"p{pnum}_img{idx+1}{ext}"
            fn.write_bytes(img.data)
            saved.append(fn.name)
        has_ca_c_o = bool(re.search(r"\bCa\b", txt) and re.search(r"\bO\b", txt))
        has_spherule_claim = bool(re.search(r"spherule|impact|cosmic", txt, re.I))
        if has_ca_c_o and has_spherule_claim:
            ca_c_o_hits += 1
        pages_info.append({
            "page": pnum,
            "images_saved": saved,
            "mentions_Ca_and_O": has_ca_c_o,
            "labeled_as_spherule_or_cosmic": has_spherule_claim,
            "text_excerpt": txt[:1000],
        })
    return {
        "pages": pages_info,
        "n_pages_with_CaO_spherule_claim": ca_c_o_hits,
    }, "\n".join(raw_chunks)


def parse_si_table_s6(pdf: PdfReader) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    """Parse SI Table S6 (p16, plus p17 if continued) for microspherule & MDP counts/kg."""
    txt_p16 = pdf.pages[15].extract_text() or ""
    txt_p17 = pdf.pages[16].extract_text() or ""
    # Only include p17 if it continues Table S6 (before Fig S7/S8)
    combined = txt_p16 + ("\n" + txt_p17 if "Table S6" in txt_p17 or re.search(r"Core\s*77", txt_p17) else "")

    rows: list[dict[str, Any]] = []
    cur_core = None
    for line in combined.splitlines():
        s = line.strip()
        if not s:
            continue
        mc = re.search(r"\bCore\s*(?:83023[-–]?0?|2013029[-–]?0?|2008029[-–]?0?)?(52|64|67|77)\b", s, re.I)
        if mc:
            cur_core = mc.group(1)
        # Match depth interval (e.g., "312-318" or "315") followed by numeric counts
        md = re.match(r"^(?:(?:Core\s*)?(?:52|64|67|77)\s+)?(\d{1,3}(?:\.\d+)?)\s*[-–]\s*(\d{1,3}(?:\.\d+)?)\s+(.*)$", s)
        if not md and cur_core:
            md_single = re.match(r"^(\d{1,3}(?:\.\d+)?)\s+([\d,\.]+\s+[\d,\.]+.*)$", s)
            if md_single:
                d_lo = d_hi = float(md_single.group(1))
                rest = md_single.group(2)
            else:
                continue
        elif md:
            d_lo, d_hi = float(md.group(1)), float(md.group(2))
            rest = md.group(3)
        else:
            continue
        if not cur_core:
            continue
        nums = [to_float(x) for x in re.findall(r"[\d,]+(?:\.\d+)?", rest)]
        nums = [x for x in nums if x is not None]
        if nums:
            # First numeric count is typically MSp/kg (or age then MSp/kg; guard against 5-digit cal ages > 5000 if depth < 1000)
            rows.append({
                "core": cur_core,
                "depth_lo_cm": d_lo,
                "depth_hi_cm": d_hi,
                "depth_mid_cm": 0.5 * (d_lo + d_hi),
                "values": nums,
                "raw_line": s,
            })

    return {"n_parsed_rows": len(rows), "rows": rows}, rows, f"=== SI Table S6 (p16-17) ===\n{combined}\n"


def evaluate_core_uniqueness(core_profiles: dict[str, list[dict[str, float]]], core_ydb: dict[str, tuple[float, float]]) -> dict[str, Any]:
    """Pure function testable on synthetic and real core profiles."""
    out: dict[str, Any] = {}
    for cid, pts in core_profiles.items():
        if not pts:
            continue
        ylo, yhi = core_ydb[cid]
        in_ydb = [p["count"] for p in pts if (p["depth_mid"] >= ylo - 1.0 and p["depth_mid"] <= yhi + 1.0)]
        out_ydb = [p["count"] for p in pts if not (p["depth_mid"] >= ylo - 1.0 and p["depth_mid"] <= yhi + 1.0)]
        ydb_max = max(in_ydb) if in_ydb else 0.0
        out_max = max(out_ydb) if out_ydb else 0.0
        out_med = statistics.median(out_ydb) if out_ydb else 0.0
        span = max(p["depth_mid"] for p in pts) - min(p["depth_mid"] for p in pts)
        out[cid] = {
            "n_samples": len(pts),
            "depth_min_cm": round(min(p["depth_mid"] for p in pts), 1),
            "depth_max_cm": round(max(p["depth_mid"] for p in pts), 1),
            "sampled_span_cm": round(span, 1),
            "ydb_max": round(ydb_max, 2),
            "out_of_ydb_max": round(out_max, 2),
            "out_of_ydb_median": round(out_med, 2),
            "out_to_ydb_ratio": round(out_max / ydb_max, 3) if ydb_max > 0 else None,
        }
    return out


def parse_table_s7_nanoparticles(path: pathlib.Path) -> dict[str, Any]:
    """Parse Table S7 SP-ICP-TOF-MS nanoparticle total masses & ratios for Cores 64 & 67."""
    rows = read_xlsx_sheet(path, 0)
    # Locate the 'Total Mass of NPs' header rows (r2 = idx 1 for C64, r15 = idx 14 for C67) and 'Mass Concentration' (r57 = idx 56)
    blocks: dict[str, list[dict[str, Any]]] = {"mass_C64": [], "mass_C67": [], "conc_C64": [], "conc_C67": []}
    mode = "mass"
    header_map: dict[str, int] = {}

    for r in rows:
        c0 = (r[0] if r else "").strip()
        if c0 == "Mass Concentration":
            mode = "conc"
            continue
        if c0 in {"Mass of Single-metal NPs", "Mass of Multi-metal NPs"}:
            mode = "skip"
            continue
        if c0 == "Total Mass of NPs":
            if mode == "skip":
                # Keep skipping unless we just passed Mass Concentration
                continue
            header_map = {v.strip(): i for i, v in enumerate(r) if v and v.strip()}
            continue
        if mode in {"mass", "conc"} and re.match(r"^C(64|67)\b", c0):
            cid = "64" if c0.startswith("C64") else "67"
            dep = to_float(r[1]) if len(r) > 1 else None
            if dep is None:
                m = re.search(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)", c0)
                if m:
                    dep = 0.5 * (float(m.group(1)) + float(m.group(2)))
            rec: dict[str, Any] = {"sample": c0, "core": cid, "depth_cm": dep}
            for col in ("Fe", "Cr", "Co", "Ni", "Cu", "Pd", "Ir", "Pt", "Pt/Ir", "Pt/Pd", "Pt/Fe", "Co/Fe", "Cr/Fe", "Ni/Fe"):
                if col in header_map and header_map[col] < len(r):
                    rec[col] = to_float(r[header_map[col]])
                else:
                    rec[col] = None
            # Also recompute Pt/Ir and Pt/Pd directly from masses if both > 0
            if rec["Pt"] and rec["Ir"] and rec["Ir"] > 0:
                rec["Pt_Ir_calc"] = rec["Pt"] / rec["Ir"]
            else:
                rec["Pt_Ir_calc"] = None
            if rec["Pt"] and rec["Pd"] and rec["Pd"] > 0:
                rec["Pt_Pd_calc"] = rec["Pt"] / rec["Pd"]
            else:
                rec["Pt_Pd_calc"] = None
            blocks[f"{mode}_C{cid}"].append(rec)

    # Blind peak scan on Total Mass (and Mass Concentration) for C64 and C67
    blind: dict[str, Any] = {}
    for key in ("mass_C64", "mass_C67", "conc_C64", "conc_C67"):
        pts = blocks[key]
        cid = "64" if "C64" in key else "67"
        ylo, yhi = BAFFIN_CORES[cid]["ydb_cm"]
        b_res: dict[str, Any] = {"n_depths": len(pts), "ydb_cm": [ylo, yhi], "elements": {}}
        for el in ("Pt", "Ir", "Pd", "Ni", "Co", "Cr", "Pt/Ir", "Pt/Pd", "Pt/Fe", "Ni/Fe"):
            valid = [(p["depth_cm"], p[el], p["sample"]) for p in pts if p.get(el) is not None and p["depth_cm"] is not None]
            if not valid:
                continue
            top = max(valid, key=lambda x: x[1])
            in_ydb = (ylo - 2.0 <= top[0] <= yhi + 2.0)
            vals_all = [x[1] for x in valid]
            med = statistics.median(vals_all)
            b_res["elements"][el] = {
                "max_depth_cm": top[0],
                "max_sample": top[2],
                "max_val": top[1],
                "median_val": med,
                "max_to_median": round(top[1] / med, 2) if med > 0 else None,
                "peak_in_claimed_ydb": in_ydb,
            }
        # Summarize Pt/Ir and Pt/Pd ratios inside claimed YDB
        ydb_pts = [p for p in pts if p["depth_cm"] is not None and (ylo - 2.0 <= p["depth_cm"] <= yhi + 2.0)]
        b_res["ydb_pt_ir"] = [round(p["Pt_Ir_calc"], 2) for p in ydb_pts if p.get("Pt_Ir_calc") is not None]
        b_res["ydb_pt_pd"] = [round(p["Pt_Pd_calc"], 2) for p in ydb_pts if p.get("Pt_Pd_calc") is not None]
        blind[key] = b_res

    return {"blocks": blocks, "blind_peak_scan": blind}


# ---------------------------------------------------------------------------
# 5. Pillar 3 — x100 Mixing Math Audit (Table S8a/S8b), Bulk Δ17O, XML Citations
# ---------------------------------------------------------------------------
def evaluate_x100_mixing_artifact(fe_ppm: float, cr_ppm: float, ni_ppm: float) -> dict[str, Any]:
    """
    Reproduce Moore et al. (2025) x100 Ni & Cr scaling vs. proper 99% terrestrial subtraction.
    Moore et al. multiplied total measured Ni and Cr by 100 (without subtracting 99% terrestrial Ni/Cr),
    which reduces Fe/Cr and Fe/Ni by 100x mechanically.
    """
    raw_fe_cr = fe_ppm / cr_ppm if cr_ppm > 0 else None
    raw_fe_ni = fe_ppm / ni_ppm if ni_ppm > 0 else None
    moore_fe_cr = fe_ppm / (100.0 * cr_ppm) if cr_ppm > 0 else None
    moore_fe_ni = fe_ppm / (100.0 * ni_ppm) if ni_ppm > 0 else None

    # Proper 99% UCC subtraction:
    cr_excess_ucc = cr_ppm - 0.99 * UCC_REF["Cr_ppm"]
    ni_excess_ucc = ni_ppm - 0.99 * UCC_REF["Ni_ppm"]
    # Fe-scaled crustal baseline (appropriate for Fe-rich magnetite/crustal spherules):
    fe_scale = fe_ppm / UCC_REF["Fe_ppm"]
    cr_excess_fescale = cr_ppm - 0.99 * fe_scale * UCC_REF["Cr_ppm"]
    ni_excess_fescale = ni_ppm - 0.99 * fe_scale * UCC_REF["Ni_ppm"]

    return {
        "raw_Fe_Cr": round(raw_fe_cr, 2) if raw_fe_cr is not None else None,
        "raw_Fe_Ni": round(raw_fe_ni, 2) if raw_fe_ni is not None else None,
        "moore_x100_Fe_Cr": round(moore_fe_cr, 2) if moore_fe_cr is not None else None,
        "moore_x100_Fe_Ni": round(moore_fe_ni, 2) if moore_fe_ni is not None else None,
        "moore_x100_enters_cosmic_box": bool(
            moore_fe_cr is not None and moore_fe_ni is not None and moore_fe_cr <= 150.0 and moore_fe_ni <= 80.0
        ),
        "cr_excess_ucc_ppm": round(cr_excess_ucc, 2),
        "ni_excess_ucc_ppm": round(ni_excess_ucc, 2),
        "cr_excess_fescale_ppm": round(cr_excess_fescale, 2),
        "ni_excess_fescale_ppm": round(ni_excess_fescale, 2),
    }


def run_pillar3_chem_and_citations(
    s8a_path: pathlib.Path,
    s8b_path: pathlib.Path,
    s10_path: pathlib.Path,
    moore_xml_path: pathlib.Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    # 3a. Parse Table S8a (LA-ICP-MS microspherules)
    rows_a = read_xlsx_sheet(s8a_path, 0)
    hdr_a = {v.strip(): i for i, v in enumerate(rows_a[0]) if v and v.strip()}
    spherules: list[dict[str, Any]] = []
    for r in rows_a[1:]:
        if not r or not r[0]:
            continue
        name = r[0].strip()
        if not re.search(r"Baffin", name, re.I):
            continue
        fe = to_float(r[hdr_a["Fe"]]) if "Fe" in hdr_a and hdr_a["Fe"] < len(r) else None
        cr = to_float(r[hdr_a["Cr53(LR)"]]) if "Cr53(LR)" in hdr_a and hdr_a["Cr53(LR)"] < len(r) else None
        ni = to_float(r[hdr_a["Ni60(LR)"]]) if "Ni60(LR)" in hdr_a and hdr_a["Ni60(LR)"] < len(r) else None
        co = to_float(r[hdr_a["Co59(LR)"]]) if "Co59(LR)" in hdr_a and hdr_a["Co59(LR)"] < len(r) else None
        cao = to_float(r[hdr_a["Cao wt%"]]) if "Cao wt%" in hdr_a and hdr_a["Cao wt%"] < len(r) else None
        sio2 = to_float(r[hdr_a["SiO2 wt%"]]) if "SiO2 wt%" in hdr_a and hdr_a["SiO2 wt%"] < len(r) else None
        feo = to_float(r[hdr_a["FeO wt%"]]) if "FeO wt%" in hdr_a and hdr_a["FeO wt%"] < len(r) else None
        ir_ppb = to_float(r[hdr_a["Ir(ppb)"]]) if "Ir(ppb)" in hdr_a and hdr_a["Ir(ppb)"] < len(r) else None
        pt_ppb = to_float(r[hdr_a["Pt195(ppb)"]]) if "Pt195(ppb)" in hdr_a and hdr_a["Pt195(ppb)"] < len(r) else None
        if fe is None or fe <= 0:
            continue
        # Only include valid positive Cr/Ni rows for ratios
        mix = evaluate_x100_mixing_artifact(fe, cr if (cr and cr > 0) else 0.0, ni if (ni and ni > 0) else 0.0)
        spherules.append({
            "source_table": "S8a",
            "sample": name,
            "Fe_ppm": round(fe, 1),
            "FeO_wt": round(feo, 2) if feo is not None else None,
            "SiO2_wt": round(sio2, 2) if sio2 is not None else None,
            "CaO_wt": round(cao, 2) if cao is not None else None,
            "Cr_ppm": round(cr, 2) if cr is not None else None,
            "Ni_ppm": round(ni, 2) if ni is not None else None,
            "Co_ppm": round(co, 2) if co is not None else None,
            "Ir_ppb": round(ir_ppb, 2) if ir_ppb is not None else None,
            "Pt_ppb": round(pt_ppb, 2) if pt_ppb is not None else None,
            "Pt_Ir": round(pt_ppb / ir_ppb, 2) if (pt_ppb and ir_ppb and pt_ppb > 0 and ir_ppb > 0) else None,
            **mix,
        })

    # Parse Table S8b (Core 64 glassy spherules)
    rows_b = read_xlsx_sheet(s8b_path, 0)
    hdr_b = {v.strip(): i for i, v in enumerate(rows_b[0]) if v and v.strip()}
    for r in rows_b[2:]:
        if not r or not r[0] or not r[0].strip().lower().startswith("spot"):
            continue
        fe2o3 = to_float(r[hdr_b["Fe2O3"]]) if "Fe2O3" in hdr_b and hdr_b["Fe2O3"] < len(r) else None
        cr = to_float(r[hdr_b["Cr"]]) if "Cr" in hdr_b and hdr_b["Cr"] < len(r) else None
        ni = to_float(r[hdr_b["Ni"]]) if "Ni" in hdr_b and hdr_b["Ni"] < len(r) else None
        co = to_float(r[hdr_b["Co"]]) if "Co" in hdr_b and hdr_b["Co"] < len(r) else None
        cao = to_float(r[hdr_b["CaO"]]) if "CaO" in hdr_b and hdr_b["CaO"] < len(r) else None
        sio2 = to_float(r[hdr_b["SiO2"]]) if "SiO2" in hdr_b and hdr_b["SiO2"] < len(r) else None
        if fe2o3 is None or fe2o3 <= 0:
            continue
        # Fe2O3 wt% -> Fe ppm: wt% * 0.6994 * 10000
        fe = fe2o3 * 6994.0
        mix = evaluate_x100_mixing_artifact(fe, cr if (cr and cr > 0) else 0.0, ni if (ni and ni > 0) else 0.0)
        spherules.append({
            "source_table": "S8b",
            "sample": f"C64_glassy_{r[0].strip()}",
            "Fe_ppm": round(fe, 1),
            "FeO_wt": round(fe2o3 * 0.8998, 2),
            "SiO2_wt": round(sio2, 2) if sio2 is not None else None,
            "CaO_wt": round(cao, 2) if cao is not None else None,
            "Cr_ppm": round(cr, 2) if cr is not None else None,
            "Ni_ppm": round(ni, 2) if ni is not None else None,
            "Co_ppm": round(co, 2) if co is not None else None,
            "Ir_ppb": None,
            "Pt_ppb": None,
            "Pt_Ir": None,
            **mix,
        })

    # Check Ca-rich rows in Table S10 (MDPs) as well
    rows_10 = read_xlsx_sheet(s10_path, 0)
    hdr_10 = {v.strip(): i for i, v in enumerate(rows_10[0]) if v and v.strip()}
    s10_ca_vals = []
    for r in rows_10[1:]:
        if r and len(r) > hdr_10.get("Ca", 999):
            v = to_float(r[hdr_10["Ca"]])
            if v is not None:
                s10_ca_vals.append(v)

    valid_ni = [s for s in spherules if s["raw_Fe_Ni"] is not None]
    valid_cr = [s for s in spherules if s["raw_Fe_Cr"] is not None]
    valid_both = [s for s in spherules if s["raw_Fe_Ni"] is not None and s["raw_Fe_Cr"] is not None]

    frac_raw_feni_gt200 = sum(1 for s in valid_ni if s["raw_Fe_Ni"] > 200.0) / len(valid_ni) if valid_ni else 0.0
    frac_raw_cosmic = sum(1 for s in valid_both if s["raw_Fe_Cr"] <= 150.0 and s["raw_Fe_Ni"] <= 80.0) / len(valid_both) if valid_both else 0.0
    frac_x100_cosmic = sum(1 for s in valid_both if s["moore_x100_enters_cosmic_box"]) / len(valid_both) if valid_both else 0.0
    # Consistent with >= 1 wt% CI chondrite admixture (+108 ppm Ni, +26.5 ppm Cr above 99% UCC / Fe-scaled baseline)
    frac_pos_1pct_ci_ucc = sum(
        1 for s in valid_both if s["ni_excess_ucc_ppm"] >= 108.0 and s["cr_excess_ucc_ppm"] >= 26.5
    ) / len(valid_both) if valid_both else 0.0
    frac_pos_1pct_ci_fescale = sum(
        1 for s in valid_both if s["ni_excess_fescale_ppm"] >= 108.0 and s["cr_excess_fescale_ppm"] >= 26.5
    ) / len(valid_both) if valid_both else 0.0

    ucc_control = evaluate_x100_mixing_artifact(UCC_REF["Fe_ppm"], UCC_REF["Cr_ppm"], UCC_REF["Ni_ppm"])
    bir1g_control = evaluate_x100_mixing_artifact(BIR1G_REF["Fe_ppm"], BIR1G_REF["Cr_ppm"], BIR1G_REF["Ni_ppm"])

    # 3b. Parse Bulk Δ17O (Appendix Table A1) & 187 XML references from moore2025_baffin_bay.xml
    xml = ET.fromstring(moore_xml_path.read_bytes())
    delta17o_rows = []
    for tw in xml.findall(".//table-wrap"):
        txt_all = " ".join(tw.itertext())
        if "17O" in txt_all or "obsidian" in txt_all.lower():
            for tr in tw.findall(".//tbody/tr"):
                cells = ["".join(td.itertext()).strip() for td in tr.findall("td")]
                if cells:
                    delta17o_rows.append(cells)

    # Parse Δ17O numeric values (excluding obsidian standards)
    baffin_d17o_vals = []
    for cells in delta17o_rows:
        row_s = " ".join(cells)
        if re.search(r"obsidian|mean|std|sd|average", row_s, re.I):
            continue
        # Δ17O* is typically the last or near-last small number between -1 and +1
        nums = [to_float(c) for c in cells]
        nums = [x for x in nums if x is not None]
        if len(nums) >= 3:
            baffin_d17o_vals.append({"sample": cells[0], "d17O": nums[-3], "d18O": nums[-2], "Delta17O_star": nums[-1]})

    n_d17o_et = sum(1 for x in baffin_d17o_vals if abs(x["Delta17O_star"]) > 0.06)

    # 3c. Audit all 187 <ref> elements in moore2025_baffin_bay.xml
    refs = xml.findall(".//ref")
    doi_to_refs: dict[str, list[str]] = {}
    malformed_dois = []
    missing_dois = 0
    year_anomalies = []
    for rf in refs:
        rid = rf.attrib.get("id", "")
        mc = rf.find(".//mixed-citation")
        txt = "".join(mc.itertext()).strip() if mc is not None else "".join(rf.itertext()).strip()
        doi_el = rf.find(".//pub-id[@pub-id-type='doi']")
        doi = (doi_el.text or "").strip().lower() if doi_el is not None else ""
        if not doi:
            m_doi = re.search(r"10\.\d{4,9}/[^\s,;]+", txt)
            doi = m_doi.group(0).rstrip(".").lower() if m_doi else ""
        if not doi:
            missing_dois += 1
        else:
            if not re.match(r"^10\.\d{4,9}/\S+$", doi) or " " in doi or doi.endswith("/"):
                malformed_dois.append({"ref": rid, "doi": doi})
            doi_to_refs.setdefault(doi, []).append(f"{rid}: {txt[:90]}")
        # Check for obviously garbled years or placeholder text
        if re.search(r"\b(18\d\d|202[6-9]|xxxx|doi:\s*$|http://dx\.doi\.org/\s*$)", txt, re.I):
            year_anomalies.append({"ref": rid, "excerpt": txt[:120]})

    duplicate_dois = {d: lst for d, lst in doi_to_refs.items() if len(lst) > 1}
    total_xml_ref_flags = len(malformed_dois) + sum(len(v) - 1 for v in duplicate_dois.values()) + len(year_anomalies)

    summary = {
        "n_spherules_total": len(spherules),
        "n_s8a": sum(1 for s in spherules if s["source_table"] == "S8a"),
        "n_s8b": sum(1 for s in spherules if s["source_table"] == "S8b"),
        "n_high_CaO_gt15wt": sum(1 for s in spherules if s["CaO_wt"] is not None and s["CaO_wt"] > 15.0),
        "s10_mdp_n_ca_gt15wt": sum(1 for v in s10_ca_vals if v > 15.0),
        "s10_mdp_n_total": len(s10_ca_vals),
        "raw_median_Fe_Cr": round(statistics.median(s["raw_Fe_Cr"] for s in valid_cr), 1) if valid_cr else None,
        "raw_median_Fe_Ni": round(statistics.median(s["raw_Fe_Ni"] for s in valid_ni), 1) if valid_ni else None,
        "frac_raw_Fe_Ni_gt200_terrestrial": round(frac_raw_feni_gt200, 4),
        "frac_raw_in_cosmic_box": round(frac_raw_cosmic, 4),
        "frac_after_moore_x100_in_cosmic_box": round(frac_x100_cosmic, 4),
        "frac_ge_1pct_CI_excess_vs_UCC": round(frac_pos_1pct_ci_ucc, 4),
        "frac_ge_1pct_CI_excess_vs_Fescale_UCC": round(frac_pos_1pct_ci_fescale, 4),
        "pure_UCC_control": ucc_control,
        "pure_BIR1G_basalt_control": bir1g_control,
        "s8a_Pt_Ir_valid_n": sum(1 for s in spherules if s["Pt_Ir"] is not None),
        "s8a_Pt_Ir_median": round(statistics.median(s["Pt_Ir"] for s in spherules if s["Pt_Ir"] is not None), 2)
        if any(s["Pt_Ir"] is not None for s in spherules) else None,
        "bulk_delta17O_raw_table": delta17o_rows,
        "bulk_delta17O_baffin_samples": baffin_d17o_vals,
        "bulk_delta17O_n_ET_gt_0p06": n_d17o_et,
        "xml_citations": {
            "n_refs_total": len(refs),
            "n_missing_doi": missing_dois,
            "n_malformed_doi": len(malformed_dois),
            "malformed_dois": malformed_dois[:20],
            "n_duplicate_doi_keys": len(duplicate_dois),
            "duplicate_dois": duplicate_dois,
            "n_year_or_placeholder_anomalies": len(year_anomalies),
            "total_structural_xml_flags": total_xml_ref_flags,
        },
        "criterion_A4_x100_artifact_triggered": bool(
            ucc_control["moore_x100_enters_cosmic_box"] and frac_raw_feni_gt200 > 0.50
        ),
    }
    return summary, spherules


# ---------------------------------------------------------------------------
# 6. Pillar 4 — Shocked Quartz (Paper B: e0319840 / e0342620) Audit
# ---------------------------------------------------------------------------
def run_pillar4_shocked_quartz(
    quartz_si_pdf: PdfReader,
    quartz_xml_path: pathlib.Path,
    retraction_xml_path: pathlib.Path,
    intcal20: tuple[np.ndarray, np.ndarray, np.ndarray],
) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    # Extract SI pages 1-5 (Tables S1-S8) and Methods (pp 14-22)
    p1_5 = "\n".join(f"=== kennett2025_si p{i+1} ===\n" + (quartz_si_pdf.pages[i].extract_text() or "") for i in range(min(5, len(quartz_si_pdf.pages))))
    methods_txt = "\n".join((quartz_si_pdf.pages[i].extract_text() or "") for i in range(13, len(quartz_si_pdf.pages)))

    # Parse included 14C dates from p2 (Tables S2, S3, S4)
    p2_txt = quartz_si_pdf.pages[1].extract_text() or ""
    included_by_site: dict[str, list[dict[str, Any]]] = {"Arlington Canyon": [], "Blackwater Draw": [], "Murray Springs": []}
    cur_site = None
    for line in p2_txt.splitlines():
        s = line.strip()
        if "Table S2" in s or "Arlington Canyon" in s:
            cur_site = "Arlington Canyon"
        elif "Table S3" in s or "Blackwater Draw" in s:
            cur_site = "Blackwater Draw"
        elif "Table S4" in s or "Murray Springs" in s:
            cur_site = "Murray Springs"
        if not cur_site:
            continue
        # Match uncalibrated 14C age +/- err (9,000-12,500)
        m = re.search(r"\b(1[012],?\d{3}|9,?\d{3})\s*(?:±|\+/-)\s*(\d{2,3})\b", s)
        if m:
            age = float(m.group(1).replace(",", ""))
            err = float(m.group(2))
            if 9000 <= age <= 12500 and 10 <= err <= 600:
                lab_m = re.search(r"\b(?:UCIAMS|AA|A|Tx|Beta|CAMS|OS|GX|SMU)[-–]\d+[A-Z]?\b", s)
                included_by_site[cur_site].append({
                    "site": cur_site,
                    "c14_age": age,
                    "c14_err": err,
                    "lab_id": lab_m.group(0) if lab_m else "",
                    "raw_line": s,
                })

    # Compare included vs. complete published direct YDB-stratum inventories
    csv_rows: list[dict[str, Any]] = []
    site_comparisons: dict[str, Any] = {}
    all_pub_ages, all_pub_errs = [], []
    all_inc_ages, all_inc_errs = [], []
    total_omitted = 0

    for site, pub_list in PUBLISHED_DIRECT_INVENTORY.items():
        inc_list = included_by_site[site]
        inc_c14_set = {(int(d["c14_age"]), int(d["c14_err"])) for d in inc_list}
        inc_labs = {d["lab_id"].upper() for d in inc_list if d["lab_id"]}
        matched_pub = 0
        for p in pub_list:
            in_paper = (p["lab"].upper() in inc_labs) or ((p["c14"], p["err"]) in inc_c14_set)
            if in_paper:
                matched_pub += 1
            cal = calibrate_14c(p["c14"], p["err"], intcal20)
            all_pub_ages.append(p["c14"])
            all_pub_errs.append(p["err"])
            csv_rows.append({
                "site": site,
                "lab_id": p["lab"],
                "c14_age": p["c14"],
                "c14_err": p["err"],
                "included_in_kennett2025": int(in_paper),
                "median_cal_bp": cal["median_cal_bp"],
                "hpd95_lo": cal["hpd95"][0],
                "hpd95_hi": cal["hpd95"][1],
                "source": p["source"],
            })
        omitted = len(pub_list) - matched_pub
        total_omitted += omitted
        for d in inc_list:
            all_inc_ages.append(d["c14_age"])
            all_inc_errs.append(d["c14_err"])
        site_comparisons[site] = {
            "n_published_direct_dates": len(pub_list),
            "n_included_in_si_table": len(inc_list),
            "n_published_matched": matched_pub,
            "n_published_omitted": omitted,
            "n_included_with_lab_id": sum(1 for d in inc_list if d["lab_id"]),
            "ward_wilson_all_published": ward_wilson_t([p["c14"] for p in pub_list], [p["err"] for p in pub_list]),
            "ward_wilson_included": ward_wilson_t([d["c14_age"] for d in inc_list], [d["c14_err"] for d in inc_list]) if len(inc_list) >= 2 else None,
            "included_rows": inc_list,
        }

    ww_all_pub = ward_wilson_t(all_pub_ages, all_pub_errs)
    ww_all_inc = ward_wilson_t(all_inc_ages, all_inc_errs)

    # Check vertical control sampling & sedimentation-rate model in XML + SI
    qxml_txt = "".join(ET.fromstring(quartz_xml_path.read_bytes()).itertext())
    has_sed_rate_model = bool(re.search(r"sedimentation rate|age[- ]depth model|accumulation rate", qxml_txt + "\n" + methods_txt, re.I))
    # Extract exact mentions of "above" / "below" quartz counts in XML + SI p3-5
    quartz_control_mentions = re.findall(r".{0,80}(?:none above or below|above and below|above or below|quartz grains on a).{0,100}", qxml_txt + "\n" + p1_5, re.I)

    # Parse retraction_shocked_quartz.xml verbatim to check allegation scope
    rxml_txt = " ".join("".join(ET.fromstring(retraction_xml_path.read_bytes()).itertext()).split())
    notice_scope = {
        "cites_age_model_or_radiocarbon": bool(re.search(r"age model|radiocarbon", rxml_txt, re.I)),
        "cites_vertical_sampling_or_sed_rate": bool(re.search(r"sampling strategy|entire core|sedimentation rate|other depths", rxml_txt, re.I)),
        "alleges_microscopy_fabrication_or_misid": bool(re.search(r"fabricat|manipulat|duplicat|misidentif|microscop|TEM|EBSD|foraminifera", rxml_txt, re.I)),
        "alleges_hydrocode_error": bool(re.search(r"hydrocode|simulation|shock wave", rxml_txt, re.I)),
        "notice_text_excerpt": rxml_txt[:2000],
    }

    summary = {
        "site_chronology_audit": site_comparisons,
        "total_published_direct_dates_3sites": len(all_pub_ages),
        "total_included_dates_in_si_tables": len(all_inc_ages),
        "total_published_dates_omitted": total_omitted,
        "ward_wilson_all_25_published_direct": ww_all_pub,
        "ward_wilson_si_included_dates": ww_all_inc,
        "has_sedimentation_rate_or_agedepth_model": has_sed_rate_model,
        "quartz_control_mentions": quartz_control_mentions[:15],
        "retraction_notice_scope": notice_scope,
        "criterion_B1_chronology_overturned": bool(ww_all_pub["p_value"] < 0.01 and total_omitted >= 3),
    }
    return summary, csv_rows, p1_5


# ---------------------------------------------------------------------------
# 7. Pre-Registered Verdict Rule Engine
# ---------------------------------------------------------------------------
def evaluate_verdicts(
    paper_a_flags: dict[str, bool],
    paper_b_flags: dict[str, bool],
) -> dict[str, Any]:
    """
    Mutually exclusive pre-registered verdict rules from protocol.md Section 4.
    Paper A keys: A1_polar_14c, A2_foram_s30_s34, A3_core64_or_coverage, A4_x100_math, A5_d17O_and_refs
    Paper B keys: B1_chronology_overturned, B2_missing_controls, B_notice_challenges_microscopy
    """
    a_count = sum(1 for k in ("A1_polar_14c", "A2_foram_s30_s34", "A3_core64_or_coverage", "A4_x100_math", "A5_d17O_and_refs") if paper_a_flags.get(k))
    if a_count >= 3:
        verdict_a = "retraction_strongly_supported"
    elif a_count >= 2:
        verdict_a = "retraction_mixed_or_harsh"
    else:
        verdict_a = "retraction_unsupported"

    b1 = bool(paper_b_flags.get("B1_chronology_overturned"))
    b2 = bool(paper_b_flags.get("B2_missing_controls"))
    b_mic = bool(paper_b_flags.get("B_notice_challenges_microscopy"))
    if b1 and b2 and b_mic:
        verdict_b = "retraction_strongly_supported"
    elif b1 or b2:
        verdict_b = "retraction_mixed_or_harsh"
    else:
        verdict_b = "retraction_unsupported"

    return {
        "paper_a_baffin_bay": {
            "verdict": verdict_a,
            "checks_triggered_count": a_count,
            "checks": paper_a_flags,
        },
        "paper_b_shocked_quartz": {
            "verdict": verdict_b,
            "checks": paper_b_flags,
        },
    }


# ---------------------------------------------------------------------------
# 8. Main Pipeline
# ---------------------------------------------------------------------------
def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    marine20 = load_cal_curve(DATA / "marine20.14c")
    intcal20 = load_cal_curve(DATA / "intcal20.14c")

    baffin_pdf = PdfReader(str(DATA / "baffin_bay_si.pdf"))
    quartz_pdf = PdfReader(str(DATA / "kennett2025_si.pdf"))

    # Pillar 1
    p1_sum, p1_csv, p1_raw = run_pillar1_baffin_14c(baffin_pdf, marine20)

    # Pillar 2
    s30_34_sum, s30_34_raw = inspect_si_figs_s30_s34(baffin_pdf, RESULTS / "si_figs_s30_s34")
    s6_sum, s6_rows, s6_raw = parse_si_table_s6(baffin_pdf)
    s7_sum = parse_table_s7_nanoparticles(DATA / "table_s7_nanoparticles.xlsx")

    # Build core profiles from S6 (using first count column after depth; note raw table dumped for audit verification)
    core_profiles: dict[str, list[dict[str, float]]] = {cid: [] for cid in BAFFIN_CORES}
    for r in s6_rows:
        # In SI Table S6, identify MSp count (handle whether age precedes count)
        vals = r["values"]
        count_val = vals[0]
        if len(vals) >= 2 and vals[0] > 4000 and vals[1] < 20000:
            # Likely cal age followed by count
            count_val = vals[1]
        core_profiles[r["core"]].append({"depth_mid": r["depth_mid_cm"], "count": count_val})

    uniq = evaluate_core_uniqueness(core_profiles, {k: v["ydb_cm"] for k, v in BAFFIN_CORES.items()})
    # Compute core coverage %
    total_sampled = sum(uniq[c]["sampled_span_cm"] for c in uniq)
    total_len = sum(BAFFIN_CORES[c]["length_cm"] for c in BAFFIN_CORES)
    cov_pct = (total_sampled / total_len) * 100.0 if total_len > 0 else 0.0
    c64_out = uniq.get("64", {}).get("out_of_ydb_max", 0.0)
    c67_ydb = uniq.get("67", {}).get("ydb_max", 0.0)
    c64_vs_c67_ratio = round(c64_out / c67_ydb, 3) if c67_ydb > 0 else None

    # Pillar 3
    p3_sum, p3_csv = run_pillar3_chem_and_citations(
        DATA / "table_s8a_spherules.xlsx",
        DATA / "table_s8b_core64_glassy.xlsx",
        DATA / "table_s10_mdps.xlsx",
        DATA / "moore2025_baffin_bay.xml",
    )

    # Pillar 4
    p4_sum, p4_csv, p4_raw = run_pillar4_shocked_quartz(
        quartz_pdf,
        DATA / "kennett2025_shocked_quartz.xml",
        DATA / "retraction_shocked_quartz.xml",
        intcal20,
    )

    # Save raw extracted PDF table texts for transparent verification
    (RESULTS / "extracted_tables_raw.txt").write_text(
        p1_raw + "\n" + s6_raw + "\n" + s30_34_raw + "\n" + p4_raw,
        encoding="utf-8",
    )

    # Check A1..A5 and B1..B2 flags
    a_flags = {
        "A1_polar_14c": p1_sum["criterion_A1_triggered"],
        "A2_foram_s30_s34": s30_34_sum["n_pages_with_CaO_spherule_claim"] >= 2,
        "A3_core64_or_coverage": bool((c64_vs_c67_ratio is not None and c64_vs_c67_ratio >= 0.80) or (cov_pct < 20.0)),
        "A4_x100_math": p3_sum["criterion_A4_x100_artifact_triggered"],
        "A5_d17O_and_refs": bool(
            p3_sum["bulk_delta17O_n_ET_gt_0p06"] == 0 and p3_sum["xml_citations"]["total_structural_xml_flags"] >= 10
        ),
    }
    b_flags = {
        "B1_chronology_overturned": p4_sum["criterion_B1_chronology_overturned"],
        "B2_missing_controls": not p4_sum["has_sedimentation_rate_or_agedepth_model"],
        "B_notice_challenges_microscopy": p4_sum["retraction_notice_scope"]["alleges_microscopy_fabrication_or_misid"],
    }
    verdicts = evaluate_verdicts(a_flags, b_flags)

    # Write CSV artifacts
    if p1_csv:
        with open(RESULTS / "pillar1_baffin_14c.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(p1_csv[0].keys()))
            w.writeheader()
            w.writerows(p1_csv)
    if p3_csv:
        with open(RESULTS / "pillar3_spherules_chem.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(p3_csv[0].keys()))
            w.writeheader()
            w.writerows(p3_csv)
    if p4_csv:
        with open(RESULTS / "pillar4_quartz_audit.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(p4_csv[0].keys()))
            w.writeheader()
            w.writerows(p4_csv)

    summary = {
        "question": "yd-retracted-plos-audit",
        "issue": 127,
        "verdicts": verdicts,
        "pillar1_baffin_14c": p1_sum,
        "pillar2_baffin_microspherules_and_nps": {
            "si_figs_s30_s34": s30_34_sum,
            "si_table_s6_uniqueness": uniq,
            "total_core_coverage_pct": round(cov_pct, 2),
            "core64_out_to_core67_ydb_ratio": c64_vs_c67_ratio,
            "table_s7_blind_peak_scan": s7_sum["blind_peak_scan"],
        },
        "pillar3_baffin_chem_and_citations": p3_sum,
        "pillar4_shocked_quartz": p4_sum,
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== AUDIT COMPLETE ===")
    print("Paper A (Baffin Bay):", verdicts["paper_a_baffin_bay"]["verdict"], a_flags)
    print("Paper B (Shocked Quartz):", verdicts["paper_b_shocked_quartz"]["verdict"], b_flags)
    print(f"Pillar 1 raw 14C dates parsed: {p1_sum['metadata_audit']['n_parsed_raw_14c_dates']}, S2 shifted off YDB: {p1_sum['n_cores_S2_shifted_off_ydb']}/4")
    print(f"Pillar 2 S6 rows: {s6_sum['n_parsed_rows']}, coverage: {cov_pct:.1f}%, C64_out/C67_YDB: {c64_vs_c67_ratio}")
    print(f"Pillar 3 spherules: {p3_sum['n_spherules_total']}, raw Fe/Ni>200: {p3_sum['frac_raw_Fe_Ni_gt200_terrestrial']:.1%}, UCC x100 cosmic: {p3_sum['pure_UCC_control']['moore_x100_enters_cosmic_box']}, d17O ET: {p3_sum['bulk_delta17O_n_ET_gt_0p06']}, XML ref flags: {p3_sum['xml_citations']['total_structural_xml_flags']}")
    print(f"Pillar 4 quartz: omitted {p4_sum['total_published_dates_omitted']}/{p4_sum['total_published_direct_dates_3sites']}, WW all pub T={p4_sum['ward_wilson_all_25_published_direct']['T']} p={p4_sum['ward_wilson_all_25_published_direct']['p_value']}, sed model={p4_sum['has_sedimentation_rate_or_agedepth_model']}, notice challenges microscopy={p4_sum['retraction_notice_scope']['alleges_microscopy_fabrication_or_misid']}")


if __name__ == "__main__":
    main()
