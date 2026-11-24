#!/usr/bin/env python3
"""
Pre-registered audit of the two February 11, 2026 PLOS One Younger Dryas retractions:
  Paper A: Moore et al. (2025) Baffin Bay marine cores (e0328347, retracted e0342613)
  Paper B: Kennett et al. (2025) Shocked quartz at 3 US sites (e0319840, retracted e0342620)

Standard library + numpy + scipy + pypdf only. Zero network calls.
Locked protocol: questions/yd-retracted-plos-audit/protocol.md (Issue #127).
Amendment 1: pure parser / raster-image table transcription fixes (zero protocol changes).
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

# Pre-registered Baffin Bay core metadata (Moore et al. 2025 Table 1 & Fig. 2)
BAFFIN_CORES = {
    "52": {"name": "83023-052", "length_cm": 875.0, "water_depth_m": 512, "ydb_cm": (625.0, 630.0), "dr_holocene": 71.0, "dr_si_err": 69.0},
    "64": {"name": "2013029-064", "length_cm": 713.0, "water_depth_m": 875, "ydb_cm": (312.0, 318.0), "dr_holocene": 218.0, "dr_si_err": 135.0},
    "67": {"name": "2008029-067", "length_cm": 519.0, "water_depth_m": 2357, "ydb_cm": (32.0, 35.0), "dr_holocene": 218.0, "dr_si_err": 135.0},
    "77": {"name": "2013029-077", "length_cm": 649.5, "water_depth_m": 1153, "ydb_cm": (161.0, 162.0), "dr_holocene": 103.0, "dr_si_err": 106.0},
}

# Verbatim transcription of raster image SI Table S1 (baffin_bay_si.pdf p. 5, extracted as baffin_p5_img1.jpg; Amendment 1)
BAFFIN_SI_TABLE_S1: list[dict[str, Any]] = [
    {"core": "52", "depth_lo_cm": 440.0, "depth_hi_cm": 445.0, "lab_id": "Beta-9710", "c14_age": 4660.0, "c14_err": 315.0, "si_mu": 5409, "si_sig": 398, "material": "Shell", "ref": "GSC MGC database"},
    {"core": "52", "depth_lo_cm": 460.0, "depth_hi_cm": 465.0, "lab_id": "Beta-9711", "c14_age": 8400.0, "c14_err": 200.0, "si_mu": 9474, "si_sig": 291, "material": "unknown", "ref": "GSC MGC database"},
    {"core": "52", "depth_lo_cm": 480.0, "depth_hi_cm": 505.0, "lab_id": "Beta-9712", "c14_age": 8410.0, "c14_err": 200.0, "si_mu": 9489, "si_sig": 292, "material": "unknown", "ref": "GSC MGC database"},
    {"core": "52", "depth_lo_cm": 574.0, "depth_hi_cm": 579.0, "lab_id": "UGAMS-45600", "c14_age": 8480.0, "c14_err": 30.0, "si_mu": 9538, "si_sig": 75, "material": "Forams", "ref": "This study"},
    {"core": "52", "depth_lo_cm": 615.0, "depth_hi_cm": 620.0, "lab_id": "UGAMS-51367", "c14_age": 11760.0, "c14_err": 40.0, "si_mu": 13687, "si_sig": 98, "material": "Forams", "ref": "This study"},
    {"core": "52", "depth_lo_cm": 625.0, "depth_hi_cm": 630.0, "lab_id": "UGAMS-50555", "c14_age": 11120.0, "c14_err": 40.0, "si_mu": 12992, "si_sig": 84, "material": "Forams", "ref": "This study"},
    {"core": "52", "depth_lo_cm": 630.0, "depth_hi_cm": 635.0, "lab_id": "UGAMS-50556", "c14_age": 11060.0, "c14_err": 60.0, "si_mu": 13023, "si_sig": 96, "material": "Forams", "ref": "This study"},
    {"core": "52", "depth_lo_cm": 635.0, "depth_hi_cm": 640.0, "lab_id": "UGAMS-61106", "c14_age": 11350.0, "c14_err": 35.0, "si_mu": 13296, "si_sig": 80, "material": "Forams", "ref": "This study"},
    {"core": "52", "depth_lo_cm": 640.0, "depth_hi_cm": 645.0, "lab_id": "UGAMS-50557", "c14_age": 12640.0, "c14_err": 60.0, "si_mu": 15147, "si_sig": 162, "material": "Forams", "ref": "This study"},
    {"core": "52", "depth_lo_cm": 875.0, "depth_hi_cm": 890.0, "lab_id": "Beta-8896", "c14_age": 30290.0, "c14_err": 2490.0, "si_mu": 36364, "si_sig": 3662, "material": "unknown", "ref": "GSC MGC database"},
    {"core": "64", "depth_lo_cm": 135.0, "depth_hi_cm": 140.0, "lab_id": "OS-118358", "c14_age": 9200.0, "c14_err": 35.0, "si_mu": 10054, "si_sig": 209, "material": "Mixed Benthics", "ref": "Jenner et al."},
    {"core": "64", "depth_lo_cm": 275.0, "depth_hi_cm": 280.0, "lab_id": "OS-118649", "c14_age": 13850.0, "c14_err": 95.0, "si_mu": 16171, "si_sig": 243, "material": "Mixed Benthics", "ref": "Jenner et al."},
    {"core": "64", "depth_lo_cm": 290.0, "depth_hi_cm": 293.0, "lab_id": "UGAMS-50558", "c14_age": 10990.0, "c14_err": 30.0, "si_mu": 12534, "si_sig": 171, "material": "Forams", "ref": "This study"},
    {"core": "64", "depth_lo_cm": 293.0, "depth_hi_cm": 297.0, "lab_id": "UGAMS-51364", "c14_age": 10700.0, "c14_err": 30.0, "si_mu": 12193, "si_sig": 214, "material": "Forams", "ref": "This study"},
    {"core": "64", "depth_lo_cm": 312.0, "depth_hi_cm": 318.0, "lab_id": "UGAMS-61104", "c14_age": 11489.0, "c14_err": 45.0, "si_mu": 13025, "si_sig": 155, "material": "Forams", "ref": "This study"},
    {"core": "64", "depth_lo_cm": 323.0, "depth_hi_cm": 325.0, "lab_id": "UGAMS-51984", "c14_age": 12540.0, "c14_err": 45.0, "si_mu": 14341, "si_sig": 261, "material": "Forams", "ref": "This study"},
    {"core": "64", "depth_lo_cm": 330.0, "depth_hi_cm": 335.0, "lab_id": "OS-117862", "c14_age": 12500.0, "c14_err": 45.0, "si_mu": 14280, "si_sig": 261, "material": "Mixed Benthics", "ref": "Jenner et al."},
    {"core": "67", "depth_lo_cm": 26.0, "depth_hi_cm": 28.0, "lab_id": "UGAMS-50559", "c14_age": 10930.0, "c14_err": 30.0, "si_mu": 12464, "si_sig": 182, "material": "Forams", "ref": "This study"},
    {"core": "67", "depth_lo_cm": 28.0, "depth_hi_cm": 30.0, "lab_id": "UGAMS-51365", "c14_age": 10860.0, "c14_err": 30.0, "si_mu": 12382, "si_sig": 194, "material": "Forams", "ref": "This study"},
    {"core": "67", "depth_lo_cm": 30.0, "depth_hi_cm": 32.0, "lab_id": "UGAMS-51985", "c14_age": 11280.0, "c14_err": 30.0, "si_mu": 12842, "si_sig": 141, "material": "Forams", "ref": "This study"},
    {"core": "67", "depth_lo_cm": 32.0, "depth_hi_cm": 35.0, "lab_id": "UGAMS-61105", "c14_age": 11495.0, "c14_err": 30.0, "si_mu": 13030, "si_sig": 152, "material": "Forams", "ref": "This study"},
    {"core": "67", "depth_lo_cm": 35.0, "depth_hi_cm": 36.0, "lab_id": "UGAMS-51986", "c14_age": 12230.0, "c14_err": 35.0, "si_mu": 13854, "si_sig": 204, "material": "Forams", "ref": "This study"},
    {"core": "77", "depth_lo_cm": 137.0, "depth_hi_cm": 142.0, "lab_id": "OS-117723", "c14_age": 10550.0, "c14_err": 40.0, "si_mu": 11807, "si_sig": 213, "material": "Forams", "ref": "Jenner et al."},
    {"core": "77", "depth_lo_cm": 160.0, "depth_hi_cm": 161.0, "lab_id": "UGAMS-50560", "c14_age": 11030.0, "c14_err": 30.0, "si_mu": 12466, "si_sig": 153, "material": "Forams", "ref": "This study"},
    {"core": "77", "depth_lo_cm": 161.0, "depth_hi_cm": 162.0, "lab_id": "UGAMS-51366", "c14_age": 10810.0, "c14_err": 30.0, "si_mu": 12198, "si_sig": 185, "material": "Forams", "ref": "This study"},
    {"core": "77", "depth_lo_cm": 200.0, "depth_hi_cm": 205.0, "lab_id": "OS-118359", "c14_age": 12750.0, "c14_err": 55.0, "si_mu": 14480, "si_sig": 234, "material": "Mixed Planktics", "ref": "Jenner et al."},
    {"core": "77", "depth_lo_cm": 638.0, "depth_hi_cm": 643.5, "lab_id": "UCIAMS-181265", "c14_age": 37900.0, "c14_err": 1600.0, "si_mu": 41781, "si_sig": 1400, "material": "Nps", "ref": "Jenner et al."},
]

# Verbatim instrument-printed EDS mass% from extracted SI Figs S30-S34 images (Core 52, 574-579 cm = 9,538 cal BP; Amendment 1)
SI_FIGS_S30_S34_EDS: list[dict[str, Any]] = [
    {"fig": "SI Fig S30 (Point 001)", "image": "p32_img1.jpg", "depth_cm": "574-579", "C_wt": 20.37, "O_wt": 57.18, "Ca_wt": 18.97, "Si_wt": 2.18, "Al_wt": 0.69, "Na_wt": 0.39, "Mg_wt": 0.22, "Fe_wt": 0.0, "visible_pores": True},
    {"fig": "SI Fig S31 (Point 002)", "image": "p32_img2.jpg", "depth_cm": "574-579", "C_wt": 13.75, "O_wt": 48.63, "Ca_wt": 32.14, "Si_wt": 3.63, "Al_wt": 1.22, "Na_wt": 0.35, "Mg_wt": 0.27, "Fe_wt": 0.0, "visible_pores": True},
    {"fig": "SI Fig S33 (MAP 1 of S32)", "image": "p34_img1.jpg", "depth_cm": "574-579", "C_wt": 24.94, "O_wt": 50.50, "Ca_wt": 17.09, "Si_wt": 5.03, "Al_wt": 1.27, "Na_wt": 0.44, "Mg_wt": 0.72, "Fe_wt": 0.0, "visible_pores": True},
    {"fig": "SI Fig S34 (Point 001)", "image": "p35_img1.jpg", "depth_cm": "574-579", "C_wt": 20.21, "O_wt": 51.18, "Ca_wt": 24.04, "Si_wt": 2.96, "Al_wt": 1.07, "Na_wt": 0.29, "Mg_wt": 0.26, "Fe_wt": 0.0, "visible_pores": True},
]

# Verbatim transcription of raster images in kennett2025_si.pdf (Tables S2-S4 radiocarbon & Tables S5, S6, S8 shocked quartz; Amendment 1)
KENNETT2025_SI_DATES = {
    "Arlington Canyon": [
        {"lab": "", "depth_cm": 482.5, "c14": 10860.0, "err": 70.0, "cal_mu": 12810.0, "cal_sig": 60.0, "hpd95": [12715, 12965], "note": "18.5 cm ABOVE shocked quartz (501 cm); no lab ID"},
        {"lab": "", "depth_cm": 500.5, "c14": 11020.0, "err": 25.0, "cal_mu": 12955.0, "cal_sig": 60.0, "hpd95": [12840, 13070], "note": "At 500.5 cm YDB horizon; no lab ID"},
    ],
    "Blackwater Draw": [
        {"lab": "AA-89168", "depth_cm": None, "c14": None, "err": None, "cal_mu": 12825.0, "cal_sig": 65.0, "hpd95": [12725, 12970], "note": "Uncalibrated 14C age omitted from Table S3"},
        {"lab": "SMU-1880", "depth_cm": None, "c14": None, "err": None, "cal_mu": 12760.0, "cal_sig": 105.0, "hpd95": [12490, 13055], "note": "Uncalibrated 14C age omitted from Table S3"},
        {"lab": "AA-1362", "depth_cm": None, "c14": None, "err": None, "cal_mu": 12710.0, "cal_sig": 95.0, "hpd95": [12485, 12895], "note": "Uncalibrated 14C age omitted from Table S3"},
    ],
    "Murray Springs": [
        {"lab": "Haynes pooled (8 dates)", "depth_cm": None, "c14": 10885.0, "err": 50.0, "cal_mu": 12805.0, "cal_sig": 45.0, "hpd95": [12735, 12895], "note": "Pooled mean only; individual 8 lab IDs omitted"},
    ],
}

KENNETT2025_SI_QUARTZ_CONTROLS = {
    "Arlington Canyon": {
        "table": "Table S5",
        "total_strata": 31,
        "depth_span": "97.0–501.0 cm",
        "ydb_stratum": "ARL-1B (501.0 cm, bottom row)",
        "ydb_grains": 5,
        "n_above_analyzed": 3,
        "n_below_analyzed": 0,
        "above_depths_cm": [489.0, 493.0, 497.0],
        "below_depths_cm": [],
        "above_grains": [0, 0, 0],
        "below_grains": [],
        "control_grain_denominators_reported": False,
    },
    "Blackwater Draw": {
        "table": "Table S6",
        "total_strata": 16,
        "depth_span": "1239.60–1237.75 m asl",
        "ydb_stratum": "BWD D/C #4 (1238.37 m)",
        "ydb_grains": 7,
        "n_above_analyzed": 1,
        "n_below_analyzed": 1,
        "above_depths_m": [1238.40],
        "below_depths_m": [1238.17],
        "above_grains": [0],
        "below_grains": [0],
        "control_grain_denominators_reported": False,
    },
    "Murray Springs": {
        "table": "Table S8",
        "total_strata": 19,
        "depth_span": "16.0–63.0 cm",
        "ydb_stratum": "MS-42-BU (46.5 cm)",
        "ydb_grains": 4,
        "n_above_analyzed": 3,
        "n_below_analyzed": 2,
        "above_depths_cm": [26.0, 44.0, 44.8],
        "below_depths_cm": [52.0, 63.0],
        "above_grains": [0, 0, 0],
        "below_grains": [0, 0],
        "control_grain_denominators_reported": False,
    },
}

# Complete published direct/YDB-stratum 14C inventories for Paper B's 3 sites (verified in Issue #113)
PUBLISHED_DIRECT_INVENTORY = {
    "Arlington Canyon": [
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
        {"lab": "A-481", "depth_cm": None, "c14": 11170, "err": 360, "material": "plant carbonized (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "A-490", "depth_cm": None, "c14": 11040, "err": 500, "material": "plant carbonized (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "A-491", "depth_cm": None, "c14": 11630, "err": 400, "material": "plant carbonized (Clovis)", "source": "Waters & Stafford 2007"},
        {"lab": "UCIAMS-24212", "depth_cm": None, "c14": 11300, "err": 240, "material": "bulk organic / YDB contact", "source": "Firestone et al. 2007 / Kennett 2015"},
        {"lab": "A-489", "depth_cm": None, "c14": 10490, "err": 200, "material": "diatomite / black mat", "source": "Haynes 1995 / Meltzer 2014"},
        {"lab": "A-379", "depth_cm": None, "c14": 10780, "err": 100, "material": "organic mud / black mat", "source": "Haynes 2008 / Kennett 2015"},
    ],
    "Murray Springs": [
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
    cal_max: float = 50000.0,
) -> dict[str, Any]:
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
def run_pillar1_baffin_14c(pdf: PdfReader, marine20: tuple[np.ndarray, np.ndarray, np.ndarray]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    foram_txt = "\n".join((pdf.pages[i].extract_text() or "") for i in range(218, 223))
    # Count SI Table S17 entries (p. 220)
    s17_samples = re.findall(r"^(?:52|64|67|77):\d+[–-]\d+.*$", foram_txt, flags=re.M)
    s17_with_counts = [l for l in s17_samples if re.search(r"\b\d{3,4}\b", l.split(":", 1)[1])]
    s17_mixed_benthic_planktic = [l for l in s17_samples if ("benthic" in l.lower() and "planktic" in l.lower())]

    meta = {
        "n_raw_14c_dates_table_s1": len(BAFFIN_SI_TABLE_S1),
        "table_s1_embedded_as_raster_image": True,
        "si_table_s17_present_p220": "S1 Table S17" in foram_txt or "Table S17" in foram_txt,
        "si_table_s17_n_rows": len(s17_samples),
        "si_table_s17_n_with_approx_counts": len(s17_with_counts),
        "si_table_s17_n_blank_rows": len(s17_samples) - len(s17_with_counts),
        "si_table_s17_n_mixed_benthic_and_planktic": len(s17_mixed_benthic_planktic),
        "species_level_dated_pick_breakdown_reported": False,
        "notes_fairness": (
            "PLOS retraction notice stated foraminifera type/count were missing; SI Table S17 (p. 220) "
            "actually reports broad group (mixed benthics/planktics) and approximate specimen counts (400-4,400) "
            "for 17 of 21 samples (4 left blank), though without species-level percentages—and reveals that "
            "Cores 64 and 67 mixed benthic and planktic foraminifera in the same AMS targets."
        ),
    }

    scenarios = [
        ("S0_Holocene_Pearce2023", 0.0, 50.0),
        ("S0_SI_ExactErr", 0.0, None),  # sanity check vs Moore et al.'s SI Table S1 mu
        ("S1_Deglacial_plus200", 200.0, 100.0),
        ("S2_Deglacial_plus500", 500.0, 150.0),
        ("S3_Stadial_plus800", 800.0, 200.0),
    ]

    csv_rows: list[dict[str, Any]] = []
    per_core: dict[str, Any] = {}
    age_inversions: list[dict[str, Any]] = []

    for cid, cinfo in BAFFIN_CORES.items():
        cdates = [d for d in BAFFIN_SI_TABLE_S1 if d["core"] == cid]
        ydb_lo, ydb_hi = cinfo["ydb_cm"]
        ydb_mid = 0.5 * (ydb_lo + ydb_hi)
        for d in cdates:
            d["depth_mid_cm"] = 0.5 * (d["depth_lo_cm"] + d["depth_hi_cm"])
        cdates_sorted = sorted(cdates, key=lambda x: x["depth_mid_cm"])

        # Detect stratigraphic radiocarbon age reversals (> 2 sigma older overlying younger)
        for a, b in zip(cdates_sorted, cdates_sorted[1:]):
            diff = a["c14_age"] - b["c14_age"]
            comb_sig = math.sqrt(a["c14_err"] ** 2 + b["c14_err"] ** 2)
            if diff > 2.0 * comb_sig:
                age_inversions.append({
                    "core": cid,
                    "upper_depth_cm": f"{a['depth_lo_cm']:.0f}-{a['depth_hi_cm']:.0f}",
                    "upper_c14": a["c14_age"],
                    "lower_depth_cm": f"{b['depth_lo_cm']:.0f}-{b['depth_hi_cm']:.0f}",
                    "lower_c14": b["c14_age"],
                    "reversal_14c_yr": round(diff, 1),
                })

        ranked = sorted(cdates_sorted, key=lambda d: abs(d["depth_mid_cm"] - ydb_mid))
        nearest = ranked[0]
        core_res: dict[str, Any] = {
            "core_name": cinfo["name"],
            "ydb_cm": [ydb_lo, ydb_hi],
            "dr_holocene": cinfo["dr_holocene"],
            "dr_si_err": cinfo["dr_si_err"],
            "n_dates": len(cdates_sorted),
            "nearest_date_to_ydb": {
                "depth_cm": f"{nearest['depth_lo_cm']:.0f}-{nearest['depth_hi_cm']:.0f}",
                "lab_id": nearest["lab_id"],
                "c14_age": nearest["c14_age"],
                "c14_err": nearest["c14_err"],
                "si_table_s1_mu": nearest["si_mu"],
            },
            "scenarios_nearest": {},
            "all_dates": [],
        }

        for d in cdates_sorted:
            d_scens: dict[str, Any] = {}
            for sname, add_dr, dr_err in scenarios:
                eff_err = cinfo["dr_si_err"] if dr_err is None else dr_err
                cal = calibrate_14c(d["c14_age"], d["c14_err"], marine20, delta_r=cinfo["dr_holocene"] + add_dr, delta_r_err=eff_err)
                d_scens[sname] = cal
                if sname != "S0_SI_ExactErr":
                    csv_rows.append({
                        "core": cid,
                        "lab_id": d["lab_id"],
                        "depth_cm": f"{d['depth_lo_cm']:.0f}-{d['depth_hi_cm']:.0f}",
                        "depth_mid_cm": d["depth_mid_cm"],
                        "is_ydb_target": int(d is nearest),
                        "c14_age": d["c14_age"],
                        "c14_err": d["c14_err"],
                        "si_table_s1_mu": d["si_mu"],
                        "scenario": sname,
                        "delta_r_total": cinfo["dr_holocene"] + add_dr,
                        "median_cal_bp": cal["median_cal_bp"],
                        "mean_cal_bp": cal["mean_cal_bp"],
                        "hpd95_lo": cal["hpd95"][0],
                        "hpd95_hi": cal["hpd95"][1],
                        "p_ydb_12900_12700": cal["p_ydb_12900_12700"],
                        "p_yd_12900_11700": cal["p_yd_12900_11700"],
                        "p_younger_12700": cal["p_younger_12700"],
                        "p_post_yd_lt11700": cal["p_post_yd_lt11700"],
                    })
            core_res["all_dates"].append({
                "depth_cm": f"{d['depth_lo_cm']:.0f}-{d['depth_hi_cm']:.0f}",
                "lab_id": d["lab_id"],
                "c14_age": d["c14_age"],
                "c14_err": d["c14_err"],
                "si_mu": d["si_mu"],
                "recalc_S0_SI_mu": d_scens["S0_SI_ExactErr"]["mean_cal_bp"],
                "recalc_S0_med": d_scens["S0_Holocene_Pearce2023"]["median_cal_bp"],
                "recalc_S1_med": d_scens["S1_Deglacial_plus200"]["median_cal_bp"],
                "recalc_S2_med": d_scens["S2_Deglacial_plus500"]["median_cal_bp"],
                "recalc_S3_med": d_scens["S3_Stadial_plus800"]["median_cal_bp"],
            })
            if d is nearest:
                core_res["scenarios_nearest"] = d_scens
        per_core[cid] = core_res

    # Evaluate A1: under S2 (+500 yr), how many of 4 cores shift nearest YDB date median < 12,500 cal BP OR P(12900-12700) < 0.10
    s0_in_ydb = 0
    s1_shifted = 0
    s2_shifted = 0
    s3_shifted = 0
    s3_post_yd = 0
    for cid, cr in per_core.items():
        s0 = cr["scenarios_nearest"]["S0_Holocene_Pearce2023"]
        s1 = cr["scenarios_nearest"]["S1_Deglacial_plus200"]
        s2 = cr["scenarios_nearest"]["S2_Deglacial_plus500"]
        s3 = cr["scenarios_nearest"]["S3_Stadial_plus800"]
        if s0["hpd95"][0] <= 12900.0 and s0["hpd95"][1] >= 12700.0:
            s0_in_ydb += 1
        if s1["median_cal_bp"] < 12500.0 or s1["p_ydb_12900_12700"] < 0.10:
            s1_shifted += 1
        if s2["median_cal_bp"] < 12500.0 or s2["p_ydb_12900_12700"] < 0.10:
            s2_shifted += 1
        if s3["median_cal_bp"] < 12500.0 or s3["p_ydb_12900_12700"] < 0.10:
            s3_shifted += 1
        if s3["median_cal_bp"] < 11700.0:
            s3_post_yd += 1

    # Sanity check reproduction error vs SI Table S1 mu on Core 52/64/67/77 deglacial dates
    diffs_si = [
        abs(d["recalc_S0_SI_mu"] - d["si_mu"])
        for cr in per_core.values()
        for d in cr["all_dates"]
        if 8000 <= d["c14_age"] <= 15000
    ]

    summary = {
        "metadata_audit": meta,
        "reproduction_median_abs_diff_vs_SI_TableS1_yr": round(statistics.median(diffs_si), 1) if diffs_si else None,
        "stratigraphic_age_inversions": age_inversions,
        "per_core": per_core,
        "n_cores_S0_overlap_ydb": s0_in_ydb,
        "n_cores_S1_shifted_off_ydb": s1_shifted,
        "n_cores_S2_shifted_off_ydb": s2_shifted,
        "n_cores_S3_shifted_off_ydb": s3_shifted,
        "n_cores_S3_post_yd_lt11700": s3_post_yd,
        "criterion_A1_triggered": s2_shifted >= 2,
    }
    return summary, csv_rows


# ---------------------------------------------------------------------------
# 4. Pillar 2 — SI Figs S30-S34 Foraminifera, SI Table S6 Profiles, Table S7 NPs
# ---------------------------------------------------------------------------
def inspect_si_figs_s30_s34(pdf: PdfReader, out_img_dir: pathlib.Path) -> dict[str, Any]:
    out_img_dir.mkdir(parents=True, exist_ok=True)
    pages_info = []
    for pnum in (32, 33, 34, 35):
        pg = pdf.pages[pnum - 1]
        txt = pg.extract_text() or ""
        saved = []
        for idx, img in enumerate(pg.images):
            ext = pathlib.Path(img.name).suffix or ".bin"
            fn = out_img_dir / f"p{pnum}_img{idx+1}{ext}"
            if not fn.exists():
                fn.write_bytes(img.data)
            saved.append(fn.name)
        pages_info.append({
            "page": pnum,
            "images_saved": saved,
            "labeled_as_spherule_fragment": bool(re.search(r"spherule fragment", txt, re.I)),
            "caption_excerpt": " ".join(txt.split())[:350],
        })
    eds_verified = []
    for rec in SI_FIGS_S30_S34_EDS:
        caco3_sum = round(rec["C_wt"] + rec["O_wt"] + rec["Ca_wt"], 2)
        eds_verified.append({
            **rec,
            "Ca_C_O_sum_wt": caco3_sum,
            "is_calcareous_foram_like": bool(caco3_sum >= 90.0 and rec["Ca_wt"] >= 15.0 and rec["Fe_wt"] == 0.0 and rec["visible_pores"]),
        })
    return {
        "pages": pages_info,
        "eds_readouts": eds_verified,
        "n_eds_confirmed_CaCO3_foram_with_pores": sum(1 for x in eds_verified if x["is_calcareous_foram_like"]),
        "sample_depth_age_cal_bp": 9538,
        "note": (
            "All four EDS spectra in SI Figs S30-S34 show 92.5-96.5 wt% Ca+C+O (0% Fe/Ni/Cr) with textbook "
            "1-2 um foraminiferal wall pores and radial chamber cross-sections, labeled as 'spherule fragment (interior)'. "
            "Moreover, Core 52 (574-579 cm) is dated in SI Table S1 to 9,538 cal BP (Early Holocene, 3,300 yr post-YD)."
        ),
    }


def parse_si_table_s6(pdf: PdfReader) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Parse all 28 rows of SI Table S6 (baffin_bay_si.pdf p. 16; Amendment 1)."""
    txt = pdf.pages[15].extract_text() or ""
    rows: list[dict[str, Any]] = []
    pat = re.compile(
        r"^(a?)(83023-052|2013029-064|2008029-067|2013029-077)\s+"
        r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s+"
        r"(\d+(?:\.\d+)?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
    )
    for line in txt.splitlines():
        s = line.strip()
        m = pat.match(s)
        if not m:
            continue
        is_marked_peak = bool(m.group(1))
        full_core = m.group(2)
        cid = full_core.split("-")[-1].lstrip("0")
        d_lo, d_hi = float(m.group(3)), float(m.group(4))
        mass_g = float(m.group(5))
        msp_n, msp_kg = int(m.group(6)), int(m.group(7))
        cdp_n, cdp_kg = int(m.group(8)), int(m.group(9))
        expected_msp_kg = round(msp_n / (mass_g / 1000.0), 1) if mass_g > 0 else None
        rows.append({
            "core": cid,
            "core_full": full_core,
            "marked_peak_a": is_marked_peak,
            "depth_lo_cm": d_lo,
            "depth_hi_cm": d_hi,
            "depth_mid_cm": 0.5 * (d_lo + d_hi),
            "sample_mass_g": mass_g,
            "msp_n": msp_n,
            "msp_kg": msp_kg,
            "expected_msp_kg": expected_msp_kg,
            "cdp_n": cdp_n,
            "cdp_kg": cdp_kg,
        })

    # Detect mass/rate arithmetic discrepancies (like Core 77 167-168 cm: 0.14 g, 10 spherules -> reported 965/kg vs 71,429/kg)
    arith_flags = []
    for r in rows:
        if r["msp_n"] > 0 and r["expected_msp_kg"] and abs(r["expected_msp_kg"] - r["msp_kg"]) / max(1.0, r["msp_kg"]) > 0.25:
            arith_flags.append({
                "core": r["core"],
                "depth_cm": f"{r['depth_lo_cm']:.0f}-{r['depth_hi_cm']:.0f}",
                "sample_mass_g": r["sample_mass_g"],
                "msp_n": r["msp_n"],
                "reported_msp_kg": r["msp_kg"],
                "exact_n_div_mass_kg": r["expected_msp_kg"],
            })

    return rows, {"n_rows_parsed": len(rows), "arithmetic_discrepancies": arith_flags}


def evaluate_core_uniqueness(core_profiles: dict[str, list[dict[str, float]]], core_ydb: dict[str, tuple[float, float]]) -> dict[str, Any]:
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
    """Parse Table S7 SP-ICP-TOF-MS nanoparticle total masses & mass concentrations (Amendment 1: fix duplicate 'Pt' header)."""
    rows = read_xlsx_sheet(path, 0)
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
                continue
            header_map = {}
            for i, v in enumerate(r):
                k = (v or "").strip()
                if k:
                    header_map.setdefault(k, i)  # keep FIRST occurrence (elemental Pt, not trailing ratio header)
            # Ratio columns sit after the empty gap at index 49..54 (AX..BC)
            if len(r) > 54:
                header_map["ratio_Pt_Ir"] = 49
                header_map["ratio_Pt_Pd"] = 50
                header_map["ratio_Pt_Fe"] = 51
                header_map["ratio_Co_Fe"] = 52
                header_map["ratio_Cr_Fe"] = 53
                header_map["ratio_Ni_Fe"] = 54
            continue
        if mode in {"mass", "conc"} and re.match(r"^C(64|67)\b", c0):
            cid = "64" if c0.startswith("C64") else "67"
            dep = to_float(r[1]) if len(r) > 1 else None
            if dep is None:
                m = re.search(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)", c0)
                if m:
                    dep = 0.5 * (float(m.group(1)) + float(m.group(2)))
            rec: dict[str, Any] = {"sample": c0, "core": cid, "depth_cm": dep}
            for col in ("Fe", "Cr", "Co", "Ni", "Cu", "Pd", "Ir", "Pt"):
                rec[col] = to_float(r[header_map[col]]) if (col in header_map and header_map[col] < len(r)) else None
            for outk, hkey in (
                ("Pt/Ir", "ratio_Pt_Ir"),
                ("Pt/Pd", "ratio_Pt_Pd"),
                ("Pt/Fe", "ratio_Pt_Fe"),
                ("Co/Fe", "ratio_Co_Fe"),
                ("Cr/Fe", "ratio_Cr_Fe"),
                ("Ni/Fe", "ratio_Ni_Fe"),
            ):
                rec[outk] = to_float(r[header_map[hkey]]) if (hkey in header_map and header_map[hkey] < len(r)) else None
            rec["Pt_Ir_calc"] = (rec["Pt"] / rec["Ir"]) if (rec["Pt"] and rec["Ir"] and rec["Ir"] > 0) else None
            rec["Pt_Pd_calc"] = (rec["Pt"] / rec["Pd"]) if (rec["Pt"] and rec["Pd"] and rec["Pd"] > 0) else None
            blocks[f"{mode}_C{cid}"].append(rec)

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
        ydb_pts = [p for p in pts if p["depth_cm"] is not None and (ylo - 2.0 <= p["depth_cm"] <= yhi + 2.0)]
        b_res["ydb_pt_ir"] = [round(p["Pt_Ir_calc"], 2) for p in ydb_pts if p.get("Pt_Ir_calc") is not None]
        b_res["ydb_pt_pd"] = [round(p["Pt_Pd_calc"], 2) for p in ydb_pts if p.get("Pt_Pd_calc") is not None]
        blind[key] = b_res

    return {"blocks": blocks, "blind_peak_scan": blind}


# ---------------------------------------------------------------------------
# 5. Pillar 3 — x100 Mixing Math Audit (Table S8a/S8b), Bulk Δ17O, XML Citations
# ---------------------------------------------------------------------------
def evaluate_x100_mixing_artifact(fe_ppm: float, cr_ppm: float, ni_ppm: float) -> dict[str, Any]:
    raw_fe_cr = fe_ppm / cr_ppm if cr_ppm > 0 else None
    raw_fe_ni = fe_ppm / ni_ppm if ni_ppm > 0 else None
    moore_fe_cr = fe_ppm / (100.0 * cr_ppm) if cr_ppm > 0 else None
    moore_fe_ni = fe_ppm / (100.0 * ni_ppm) if ni_ppm > 0 else None

    cr_excess_ucc = cr_ppm - 0.99 * UCC_REF["Cr_ppm"]
    ni_excess_ucc = ni_ppm - 0.99 * UCC_REF["Ni_ppm"]
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
    frac_pos_1pct_ci_ucc = sum(
        1 for s in valid_both if s["ni_excess_ucc_ppm"] >= 108.0 and s["cr_excess_ucc_ppm"] >= 26.5
    ) / len(valid_both) if valid_both else 0.0
    frac_pos_1pct_ci_fescale = sum(
        1 for s in valid_both if s["ni_excess_fescale_ppm"] >= 108.0 and s["cr_excess_fescale_ppm"] >= 26.5
    ) / len(valid_both) if valid_both else 0.0

    ucc_control = evaluate_x100_mixing_artifact(UCC_REF["Fe_ppm"], UCC_REF["Cr_ppm"], UCC_REF["Ni_ppm"])
    bir1g_control = evaluate_x100_mixing_artifact(BIR1G_REF["Fe_ppm"], BIR1G_REF["Cr_ppm"], BIR1G_REF["Ni_ppm"])

    # 3b. Bulk Δ17O (Appendix Table A1, Amendment 1: exact column indexing [sample, d17O, 1SD, d18O, 1SD, Delta17O*, 1SD])
    xml = ET.fromstring(moore_xml_path.read_bytes())
    baffin_d17o_vals = []
    for tw in xml.findall(".//table-wrap"):
        txt_all = " ".join(tw.itertext())
        if "17O" in txt_all or "obsidian" in txt_all.lower():
            for tr in tw.findall(".//tbody/tr"):
                cells = ["".join(td.itertext()).strip() for td in tr.findall("td")]
                if len(cells) >= 7 and cells[0].startswith("Core"):
                    baffin_d17o_vals.append({
                        "sample": cells[0],
                        "d17O": to_float(cells[1]),
                        "d18O": to_float(cells[3]),
                        "Delta17O_star": to_float(cells[5]),
                        "sd_1": to_float(cells[6]),
                        "is_ydb": ("312–318" in cells[0] or "30–32" in cells[0] or "32–35" in cells[0]),
                    })

    ydb_d17o = [x["Delta17O_star"] for x in baffin_d17o_vals if x["is_ydb"] and x["Delta17O_star"] is not None]
    bg_d17o = [x["Delta17O_star"] for x in baffin_d17o_vals if not x["is_ydb"] and x["Delta17O_star"] is not None]
    bg_mean_d17o = statistics.mean(bg_d17o) if bg_d17o else 0.0
    n_d17o_ydb_more_et_than_bg = sum(1 for v in ydb_d17o if abs(v - bg_mean_d17o) > 0.06 and abs(v) > abs(bg_mean_d17o))

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
        "bulk_delta17O_baffin_samples": baffin_d17o_vals,
        "bulk_delta17O_ydb_mean": round(statistics.mean(ydb_d17o), 3) if ydb_d17o else None,
        "bulk_delta17O_bg_mean": round(bg_mean_d17o, 3),
        "bulk_delta17O_n_ydb_ET_anomaly": n_d17o_ydb_more_et_than_bg,
        "xml_citations": {
            "n_refs_total": len(refs),
            "n_missing_doi": missing_dois,
            "n_malformed_doi": len(malformed_dois),
            "n_duplicate_doi_keys": len(duplicate_dois),
            "duplicate_dois": duplicate_dois,
            "n_year_or_placeholder_anomalies": len(year_anomalies),
            "total_structural_xml_flags": total_xml_ref_flags,
            "note": "Offline XML check catches syntactic/duplicate DOI flags only; resolving DOIs against Crossref is required to verify the ~43 wrong-paper DOI mismatches cited on PubPeer.",
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
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    methods_txt = "\n".join((quartz_si_pdf.pages[i].extract_text() or "") for i in range(13, len(quartz_si_pdf.pages)))

    # Reconstruct exact chi2 = 0.057 test from Kennett et al. (2025) SI Tables S2-S4:
    # They selected 1 calibrated date per site: Arlington 482.5 cm (12810+-60, 18.5 cm ABOVE the 501 cm quartz!),
    # Blackwater AA-89168 (12825+-65), Murray Springs Haynes pooled (12805+-45).
    ww_authors_3 = ward_wilson_t([12810.0, 12825.0, 12805.0], [60.0, 65.0, 45.0])
    # Swap Arlington 482.5 cm -> actual 500.5 cm shocked-quartz level (12955+-60 from their own Table S2!)
    ww_authors_3_actual_500cm = ward_wilson_t([12955.0, 12825.0, 12805.0], [60.0, 65.0, 45.0])
    # All 6 rows shown in SI Tables S2-S4
    ww_all_6_si = ward_wilson_t([12810.0, 12955.0, 12825.0, 12760.0, 12710.0, 12805.0], [60.0, 60.0, 65.0, 105.0, 95.0, 45.0])

    csv_rows: list[dict[str, Any]] = []
    site_comparisons: dict[str, Any] = {}
    all_pub_ages, all_pub_errs = [], []
    total_omitted = 0

    for site, pub_list in PUBLISHED_DIRECT_INVENTORY.items():
        si_rows = KENNETT2025_SI_DATES[site]
        si_labs = {d["lab"].upper() for d in si_rows if d["lab"]}
        si_c14 = {(int(d["c14"]), int(d["err"])) for d in si_rows if d["c14"] is not None}
        matched_pub = 0
        for p in pub_list:
            in_paper = (p["lab"].upper() in si_labs) or ((p["c14"], p["err"]) in si_c14)
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
                "included_explicitly_in_si_table": int(in_paper),
                "median_cal_bp": cal["median_cal_bp"],
                "hpd95_lo": cal["hpd95"][0],
                "hpd95_hi": cal["hpd95"][1],
                "source": p["source"],
            })
        omitted = len(pub_list) - matched_pub
        total_omitted += omitted
        site_comparisons[site] = {
            "n_published_direct_dates": len(pub_list),
            "n_rows_in_si_table": len(si_rows),
            "n_published_explicitly_included": matched_pub,
            "n_published_omitted_or_pooled": omitted,
            "si_rows": si_rows,
            "ward_wilson_all_published": ward_wilson_t([p["c14"] for p in pub_list], [p["err"] for p in pub_list]),
        }

    ww_all_pub = ward_wilson_t(all_pub_ages, all_pub_errs)

    # Vertical control sampling stats (from verbatim SI Tables S5, S6, S8)
    tot_strata = sum(v["total_strata"] for v in KENNETT2025_SI_QUARTZ_CONTROLS.values())
    tot_analyzed = sum(1 + v["n_above_analyzed"] + v["n_below_analyzed"] for v in KENNETT2025_SI_QUARTZ_CONTROLS.values())
    sites_missing_below = [k for k, v in KENNETT2025_SI_QUARTZ_CONTROLS.items() if v["n_below_analyzed"] == 0]
    sites_lt3_controls = [k for k, v in KENNETT2025_SI_QUARTZ_CONTROLS.items() if (v["n_above_analyzed"] + v["n_below_analyzed"]) < 3]

    qxml_txt = "".join(ET.fromstring(quartz_xml_path.read_bytes()).itertext())
    has_sed_rate_model = bool(re.search(r"sedimentation rate|age[- ]depth model|accumulation rate", qxml_txt + "\n" + methods_txt, re.I))

    rxml_txt = " ".join("".join(ET.fromstring(retraction_xml_path.read_bytes()).itertext()).split())
    notice_scope = {
        "cites_age_model_or_radiocarbon": bool(re.search(r"age model|radiocarbon", rxml_txt, re.I)),
        "cites_vertical_sampling_or_sed_rate": bool(re.search(r"sampling strategy|entire core|sedimentation rate|other depths", rxml_txt, re.I)),
        "alleges_microscopy_fabrication_or_misid": bool(re.search(r"fabricat|manipulat|duplicat|misidentif|microscop|TEM|EBSD|foraminifera", rxml_txt, re.I)),
        "alleges_hydrocode_error": bool(re.search(r"hydrocode|simulation|shock wave", rxml_txt, re.I)),
    }

    summary = {
        "site_chronology_audit": site_comparisons,
        "total_published_direct_dates_3sites": len(all_pub_ages),
        "total_rows_in_si_tables_s2_s4": sum(len(v) for v in KENNETT2025_SI_DATES.values()),
        "total_published_dates_omitted_or_pooled": total_omitted,
        "ward_wilson_authors_3_selected_cal": ww_authors_3,
        "ward_wilson_3_using_actual_500cm_arlington": ww_authors_3_actual_500cm,
        "ward_wilson_all_6_si_rows_cal": ww_all_6_si,
        "ward_wilson_all_25_published_direct_14c": ww_all_pub,
        "vertical_quartz_controls": {
            "per_site": KENNETT2025_SI_QUARTZ_CONTROLS,
            "total_strata_across_3_sites": tot_strata,
            "total_strata_analyzed_for_quartz": tot_analyzed,
            "pct_strata_analyzed": round(100.0 * tot_analyzed / tot_strata, 1),
            "sites_with_zero_strata_below_ydb": sites_missing_below,
            "sites_with_fewer_than_3_control_strata": sites_lt3_controls,
            "any_control_grain_denominators_tabulated": False,
        },
        "has_sedimentation_rate_or_agedepth_model": has_sed_rate_model,
        "retraction_notice_scope": notice_scope,
        "criterion_B1_chronology_overturned": bool(ww_all_pub["p_value"] < 0.01 and total_omitted >= 3),
        "criterion_B2_missing_controls": bool((not has_sed_rate_model) or len(sites_missing_below) > 0),
    }
    return summary, csv_rows


# ---------------------------------------------------------------------------
# 7. Pre-Registered Verdict Rule Engine
# ---------------------------------------------------------------------------
def evaluate_verdicts(
    paper_a_flags: dict[str, bool],
    paper_b_flags: dict[str, bool],
) -> dict[str, Any]:
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
    p1_sum, p1_csv = run_pillar1_baffin_14c(baffin_pdf, marine20)

    # Pillar 2
    s30_34_sum = inspect_si_figs_s30_s34(baffin_pdf, RESULTS / "si_figs_s30_s34")
    s6_rows, s6_meta = parse_si_table_s6(baffin_pdf)
    s7_sum = parse_table_s7_nanoparticles(DATA / "table_s7_nanoparticles.xlsx")

    # Core uniqueness on BOTH Spherules/kg and CDPs/kg (testing Core 64 out-of-YDB vs Core 67 YDB)
    msp_profiles: dict[str, list[dict[str, float]]] = {cid: [] for cid in BAFFIN_CORES}
    cdp_profiles: dict[str, list[dict[str, float]]] = {cid: [] for cid in BAFFIN_CORES}
    for r in s6_rows:
        msp_profiles[r["core"]].append({"depth_mid": r["depth_mid_cm"], "count": float(r["msp_kg"])})
        cdp_profiles[r["core"]].append({"depth_mid": r["depth_mid_cm"], "count": float(r["cdp_kg"])})

    uniq_msp = evaluate_core_uniqueness(msp_profiles, {k: v["ydb_cm"] for k, v in BAFFIN_CORES.items()})
    uniq_cdp = evaluate_core_uniqueness(cdp_profiles, {k: v["ydb_cm"] for k, v in BAFFIN_CORES.items()})
    per_core_cov = {
        cid: round(100.0 * uniq_msp[cid]["sampled_span_cm"] / BAFFIN_CORES[cid]["length_cm"], 2)
        for cid in uniq_msp
    }
    total_sampled = sum(uniq_msp[c]["sampled_span_cm"] for c in uniq_msp)
    total_len = sum(BAFFIN_CORES[c]["length_cm"] for c in BAFFIN_CORES)
    cov_pct = (total_sampled / total_len) * 100.0 if total_len > 0 else 0.0

    c64_out_cdp = uniq_cdp["64"]["out_of_ydb_max"]
    c67_ydb_cdp = uniq_cdp["67"]["ydb_max"]
    c64_vs_c67_cdp_ratio = round(c64_out_cdp / c67_ydb_cdp, 3) if c67_ydb_cdp > 0 else None

    # Pillar 3
    p3_sum, p3_csv = run_pillar3_chem_and_citations(
        DATA / "table_s8a_spherules.xlsx",
        DATA / "table_s8b_core64_glassy.xlsx",
        DATA / "table_s10_mdps.xlsx",
        DATA / "moore2025_baffin_bay.xml",
    )

    # Pillar 4
    p4_sum, p4_csv = run_pillar4_shocked_quartz(
        quartz_pdf,
        DATA / "kennett2025_shocked_quartz.xml",
        DATA / "retraction_shocked_quartz.xml",
        intcal20,
    )

    # Evaluate pre-registered criteria A1..A5 and B1..B2
    a_flags = {
        "A1_polar_14c": p1_sum["criterion_A1_triggered"],
        "A2_foram_s30_s34": s30_34_sum["n_eds_confirmed_CaCO3_foram_with_pores"] >= 2,
        "A3_core64_or_coverage": bool((c64_vs_c67_cdp_ratio is not None and c64_vs_c67_cdp_ratio >= 0.80) or (cov_pct < 20.0)),
        "A4_x100_math": p3_sum["criterion_A4_x100_artifact_triggered"],
        "A5_d17O_and_refs": bool(
            p3_sum["bulk_delta17O_n_ydb_ET_anomaly"] == 0 and p3_sum["xml_citations"]["total_structural_xml_flags"] >= 10
        ),
    }
    b_flags = {
        "B1_chronology_overturned": p4_sum["criterion_B1_chronology_overturned"],
        "B2_missing_controls": p4_sum["criterion_B2_missing_controls"],
        "B_notice_challenges_microscopy": p4_sum["retraction_notice_scope"]["alleges_microscopy_fabrication_or_misid"],
    }
    verdicts = evaluate_verdicts(a_flags, b_flags)

    # Write CSV artifacts
    if p1_csv:
        with open(RESULTS / "pillar1_baffin_14c.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(p1_csv[0].keys()))
            w.writeheader()
            w.writerows(p1_csv)
    if s6_rows:
        with open(RESULTS / "pillar2_baffin_s6.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(s6_rows[0].keys()))
            w.writeheader()
            w.writerows(s6_rows)
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
            "si_table_s6_meta": s6_meta,
            "si_table_s6_msp_uniqueness": uniq_msp,
            "si_table_s6_cdp_uniqueness": uniq_cdp,
            "per_core_coverage_pct": per_core_cov,
            "total_core_coverage_pct": round(cov_pct, 2),
            "core64_out_to_core67_ydb_cdp_ratio": c64_vs_c67_cdp_ratio,
            "table_s7_blind_peak_scan": s7_sum["blind_peak_scan"],
        },
        "pillar3_baffin_chem_and_citations": p3_sum,
        "pillar4_shocked_quartz": p4_sum,
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== FULL AUDIT COMPLETE (WITH AMENDMENT 1 PARSER FIXES) ===")
    print("Paper A (Baffin Bay):", verdicts["paper_a_baffin_bay"]["verdict"], f"({verdicts['paper_a_baffin_bay']['checks_triggered_count']}/5)", a_flags)
    print("Paper B (Shocked Quartz):", verdicts["paper_b_shocked_quartz"]["verdict"], b_flags)
    print(f"Pillar 1: 27 raw 14C dates, repro diff vs SI Table S1 = {p1_sum['reproduction_median_abs_diff_vs_SI_TableS1_yr']} yr, S0 overlap={p1_sum['n_cores_S0_overlap_ydb']}/4, S1 shifted={p1_sum['n_cores_S1_shifted_off_ydb']}/4, S2 shifted={p1_sum['n_cores_S2_shifted_off_ydb']}/4, S3 shifted={p1_sum['n_cores_S3_shifted_off_ydb']}/4 (post-YD={p1_sum['n_cores_S3_post_yd_lt11700']}/4), inversions={len(p1_sum['stratigraphic_age_inversions'])}")
    print(f"Pillar 2: S30-S34 confirmed CaCO3 forams={s30_34_sum['n_eds_confirmed_CaCO3_foram_with_pores']}/4; S6 rows={s6_meta['n_rows_parsed']}, coverage={cov_pct:.1f}% {per_core_cov}, C64_out_CDP/C67_YDB_CDP={c64_vs_c67_cdp_ratio} ({c64_out_cdp}/{c67_ydb_cdp})")
    print(f"Pillar 3: spherules={p3_sum['n_spherules_total']}, raw Fe/Ni>200={p3_sum['frac_raw_Fe_Ni_gt200_terrestrial']:.1%}, raw cosmic={p3_sum['frac_raw_in_cosmic_box']:.1%}, x100 cosmic={p3_sum['frac_after_moore_x100_in_cosmic_box']:.1%}, UCC x100 cosmic={p3_sum['pure_UCC_control']['moore_x100_enters_cosmic_box']}, d17O YDB mean={p3_sum['bulk_delta17O_ydb_mean']} vs BG={p3_sum['bulk_delta17O_bg_mean']}")
    print(f"Pillar 4: omitted/pooled={p4_sum['total_published_dates_omitted_or_pooled']}/{p4_sum['total_published_direct_dates_3sites']}, authors 3-date chi2={p4_sum['ward_wilson_authors_3_selected_cal']['T']} (p={p4_sum['ward_wilson_authors_3_selected_cal']['p_value']}), swap 500cm chi2={p4_sum['ward_wilson_3_using_actual_500cm_arlington']['T']} (p={p4_sum['ward_wilson_3_using_actual_500cm_arlington']['p_value']}), all 25 pub T={p4_sum['ward_wilson_all_25_published_direct_14c']['T']} (p={p4_sum['ward_wilson_all_25_published_direct_14c']['p_value']}), quartz strata={p4_sum['vertical_quartz_controls']['total_strata_analyzed_for_quartz']}/{p4_sum['vertical_quartz_controls']['total_strata_across_3_sites']} ({p4_sum['vertical_quartz_controls']['pct_strata_analyzed']}%)")


if __name__ == "__main__":
    main()
