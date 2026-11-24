#!/usr/bin/env python3
"""
Extraterrestrial Helium-3 (3He_ET) Cosmic Dust Analysis across the Younger Dryas Deglaciation.
Issue #121 (yd-cosmic-dust-he3) — Aletheia Lab.

Implements the pre-registered protocol in questions/yd-cosmic-dust-he3/protocol.md:
  - Pillar 0: Positive Controls (Farley et al. 2006 ODP 757B & ODP 926B — 8.2 Ma Veritas breakup & 35.5 Ma Late Eocene shower)
  - Pillar 1: 230Th_xs,0-normalized 3He_ET flux across 7 Pacific pelagic cores (Serno et al. 2015 SO202-07-6;
              Tomchovska, Pavia & Farley 2025/2026 Cocos Ridge CR01/CR02/CR03/CR05; Marcantonio et al. 2001 B18/B25)
  - Pillar 2: Mid-Atlantic Ridge bulk-MAR replication (Middleton et al. 2018 KN207-2-GGC3/GGC6) &
              Polar ice-core reference baseline (Brook et al. 2000 GISP2/Vostok)
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.stats import hypergeom

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

# Standard McGee & Mukhopadhyay (2013) endmember 3He/4He ratios (in 10^-4 units)
R_ET_1E4 = 4.0          # 4.0 x 10^-4
R_TERR_DEFAULT_1E4 = 2.0e-4   # 2.0 x 10^-8 = 0.0002 x 10^-4
R_TERR_HIGH_1E4 = 2.0e-3      # 2.0 x 10^-7 = 0.0020 x 10^-4 (sensitivity check)

RNG_SEED = 20261124
N_PERM = 10000
N_BOOT = 10000

WINDOWS = {
    "W1_YD_13.5_11.5": (11.5, 13.5),
    "W2_Deglacial_15_10": (10.0, 15.0),
    "W3_Broad_20_10": (10.0, 20.0),
}


@dataclass
class Sample:
    core: str
    region: str
    lab: str
    age_ka: float
    flux_pcc_cm2_kyr: float
    conc_pcc_g: Optional[float] = None
    mar_g_cm2_kyr: Optional[float] = None
    ratio_1e4: Optional[float] = None
    et_frac: Optional[float] = None
    depth_cm: Optional[float] = None
    source: str = ""


def deconvolve_3he_et_fraction(r_meas_1e4: float, r_terr_1e4: float = R_TERR_DEFAULT_1E4,
                               r_et_1e4: float = R_ET_1E4) -> float:
    """Two-endmember extraterrestrial 3He fraction (McGee & Mukhopadhyay 2013, Eq. 8)."""
    if r_meas_1e4 <= r_terr_1e4:
        return 0.0
    frac = (1.0 - r_terr_1e4 / r_meas_1e4) / (1.0 - r_terr_1e4 / r_et_1e4)
    return float(max(0.0, min(1.0, frac)))


def parse_pangaea_tab(path: Path) -> Tuple[List[str], List[List[str]]]:
    txt = path.read_text(encoding="utf-8", errors="replace")
    end_hdr = txt.find("*/")
    body = txt[end_hdr + 2:].strip().splitlines()
    cols = body[0].split("\t")
    rows = [r.split("\t") for r in body[1:] if r.strip()]
    return cols, rows


def _f(val: str) -> Optional[float]:
    s = str(val).strip()
    if not s or s.lower() in ("nan", "na", "nd", "n/a", "-"):
        return None
    s = s.split("±")[0].split("+/-")[0].strip()
    try:
        v = float(s)
        return v if math.isfinite(v) else None
    except ValueError:
        return None


def parse_serno2015(path: Path, r_terr_1e4: float = R_TERR_DEFAULT_1E4) -> List[Sample]:
    """Serno et al. (2015) PANGAEA.845998 — Subarctic North Pacific SO202-07-6."""
    cols, rows = parse_pangaea_tab(path)
    idx_dep = cols.index("Depth sed [m]")
    idx_age = cols.index("Age [ka BP]")
    idx_mar = cols.index("MAR [g/m**2/a]")
    idx_3he = cols.index("3He [10**-10 cm**3/g]")
    idx_rat = cols.index("3He/4He [10**-4]")

    out: List[Sample] = []
    for r in rows:
        if len(r) <= max(idx_age, idx_mar, idx_3he, idx_rat):
            continue
        age = _f(r[idx_age])
        mar_gm2a = _f(r[idx_mar])
        he3_1e10 = _f(r[idx_3he])
        rat_1e4 = _f(r[idx_rat])
        dep_m = _f(r[idx_dep])
        if None in (age, mar_gm2a, he3_1e10, rat_1e4):
            continue
        et_frac = deconvolve_3he_et_fraction(rat_1e4, r_terr_1e4=r_terr_1e4)
        conc_pcc_g = he3_1e10 * 100.0 * et_frac      # 1e-10 cm3/g = 100 pcc/g
        mar_gcm2kyr = mar_gm2a * 0.1                 # 1 g/m2/yr = 0.1 g/cm2/kyr
        flux = conc_pcc_g * mar_gcm2kyr              # = 10 * he3_et(1e-10) * mar(g/m2/a)
        out.append(Sample(
            core="SO202-07-6",
            region="Subarctic North Pacific",
            lab="Lamont-Doherty (Winckler)",
            age_ka=age,
            flux_pcc_cm2_kyr=flux,
            conc_pcc_g=conc_pcc_g,
            mar_g_cm2_kyr=mar_gcm2kyr,
            ratio_1e4=rat_1e4,
            et_frac=et_frac,
            depth_cm=dep_m * 100.0 if dep_m is not None else None,
            source="Serno et al. 2015 (PANGAEA.845998)",
        ))
    return sorted(out, key=lambda s: s.age_ka)


def _read_xlsx_sheets(path: Path) -> Dict[str, List[List[str]]]:
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    zf = zipfile.ZipFile(path)
    ss: List[str] = []
    if "xl/sharedStrings.xml" in zf.namelist():
        for si in ET.fromstring(zf.read("xl/sharedStrings.xml")).findall("m:si", ns):
            ss.append("".join(t.text or "" for t in si.findall(".//m:t", ns)))
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rmap = {r.attrib["Id"]: r.attrib["Target"] for r in rels}
    sheets: Dict[str, List[List[str]]] = {}
    for sh in wb.findall(".//m:sheet", ns):
        name = sh.attrib["name"]
        rid = sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target = rmap[rid].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        rows: List[List[str]] = []
        for row in ET.fromstring(zf.read(target)).findall(".//m:sheetData/m:row", ns):
            rvals: Dict[int, str] = {}
            for c in row.findall("m:c", ns):
                ref = re.match(r"([A-Z]+)", c.attrib.get("r", "A")).group(1)
                col_i = 0
                for ch in ref:
                    col_i = col_i * 26 + (ord(ch) - 64)
                t = c.attrib.get("t")
                v = c.find("m:v", ns)
                if t == "inlineStr":
                    val = "".join(x.text or "" for x in c.findall(".//m:t", ns))
                elif v is None or v.text is None:
                    val = ""
                elif t == "s":
                    val = ss[int(v.text)]
                else:
                    val = v.text
                rvals[col_i - 1] = val
            if rvals:
                rows.append([rvals.get(k, "") for k in range(max(rvals) + 1)])
        sheets[name] = rows
    return sheets


def parse_tomchovska2026(path: Path) -> List[Sample]:
    """Tomchovska, Pavia & Farley (2025/2026) Figshare 30340705 — Cocos Ridge CR01, CR02, CR03, CR05."""
    sheets = _read_xlsx_sheets(path)
    s1 = sheets["Table S1"]
    s2 = sheets["Table S2"]
    s5 = sheets["Table S5"]

    age_map: Dict[Tuple[str, str], float] = {}
    for r in s1[6:]:
        if len(r) >= 16 and str(r[13]).strip().startswith("CR"):
            cnum = str(int(str(r[13]).strip()[2:]))
            dep = str(r[14]).strip()
            age = _f(r[15])
            if age is not None:
                age_map[(cnum, dep)] = age

    th_map: Dict[Tuple[str, str], float] = {}
    for r in s2[2:]:
        if len(r) >= 9 and str(r[0]).strip().isdigit():
            cnum = str(int(str(r[0]).strip()))
            dep = str(r[1]).strip()
            th_mar = _f(r[8])  # Th-based MAR (g/cm^2/Kyr)
            if th_mar is not None:
                th_map[(cnum, dep)] = th_mar

    out: List[Sample] = []
    for r in s5[3:]:
        if len(r) >= 10 and str(r[0]).strip().isdigit():
            cnum = str(int(str(r[0]).strip()))
            dep = str(r[1]).strip()
            key = (cnum, dep)
            if key not in age_map or key not in th_map:
                continue
            he3_et = _f(r[9])   # [3He] ET (pcc/g)
            rat = _f(r[6])      # 3He/4He
            if he3_et is None:
                continue
            th_mar = th_map[key]
            flux = he3_et * th_mar
            m_dep = re.findall(r"[\d.]+", dep)
            mid_cm = sum(float(x) for x in m_dep[:2]) / len(m_dep[:2]) if m_dep else None
            out.append(Sample(
                core=f"CR0{cnum}",
                region="Eastern Equatorial Pacific (Cocos Ridge)",
                lab="Caltech (Farley/Pavia)",
                age_ka=age_map[key],
                flux_pcc_cm2_kyr=flux,
                conc_pcc_g=he3_et,
                mar_g_cm2_kyr=th_mar,
                ratio_1e4=rat * 1e4 if rat is not None else None,
                et_frac=None,
                depth_cm=mid_cm,
                source="Tomchovska, Pavia & Farley 2025/2026 (Figshare 30340705)",
            ))
    return sorted(out, key=lambda s: (s.core, s.age_ka))


def parse_marcantonio2001(path: Path) -> List[Sample]:
    """Marcantonio et al. (2001) PANGAEA.846689 — Central Equatorial Pacific MANOP_B18 & MANOP_B25."""
    cols, rows = parse_pangaea_tab(path)
    idx_ev = cols.index("Event")
    idx_dep = cols.index("Depth sed [m]")
    idx_age = cols.index("Age [ka BP]")
    idx_rat = cols.index("3He/4He [10**-4]")
    idx_flx = cols.index("3He flux [10**-12 cm**3/cm**2/ka]")

    out: List[Sample] = []
    for r in rows:
        if len(r) <= max(idx_ev, idx_age, idx_flx):
            continue
        ev = r[idx_ev].strip()
        age = _f(r[idx_age])
        flx = _f(r[idx_flx])
        rat = _f(r[idx_rat]) if idx_rat < len(r) else None
        dep_m = _f(r[idx_dep]) if idx_dep < len(r) else None
        if age is None or flx is None:
            continue
        out.append(Sample(
            core=ev,
            region="Central Equatorial Pacific",
            lab="Lamont-Doherty (Marcantonio)",
            age_ka=age,
            flux_pcc_cm2_kyr=flx,
            ratio_1e4=rat,
            depth_cm=dep_m * 100.0 if dep_m is not None else None,
            source="Marcantonio et al. 2001 (PANGAEA.846689)",
        ))
    return sorted(out, key=lambda s: (s.core, s.age_ka))


def parse_middleton2018(path: Path, core_name: str) -> List[Sample]:
    """Middleton et al. (2018) NOAA Study 25870 — Mid-Atlantic Ridge KN207-2-GGC3 / GGC6."""
    lines = [l for l in path.read_text(encoding="latin-1").splitlines() if l.strip() and not l.lstrip().startswith("#")]
    cols = lines[0].split("\t")
    idx_dep = cols.index("depth_cm")
    idx_age = cols.index("age")
    idx_he = cols.index("3He_ET")

    raw_pts: List[Tuple[float, float, float]] = []
    for line in lines[1:]:
        p = line.split("\t")
        if len(p) <= max(idx_dep, idx_age, idx_he):
            continue
        dep = _f(p[idx_dep])
        age = _f(p[idx_age])
        he = _f(p[idx_he])
        if None in (dep, age, he):
            continue
        raw_pts.append((dep, age, he))
    raw_pts.sort(key=lambda x: x[0])

    # Compute centered local LSR (cm/kyr) across adjacent points with distinct ages
    n = len(raw_pts)
    out: List[Sample] = []
    for i, (dep, age, he) in enumerate(raw_pts):
        lo = max(0, i - 1)
        hi = min(n - 1, i + 1)
        while hi < n - 1 and raw_pts[hi][1] <= raw_pts[lo][1]:
            hi += 1
        while lo > 0 and raw_pts[hi][1] <= raw_pts[lo][1]:
            lo -= 1
        dt = raw_pts[hi][1] - raw_pts[lo][1]
        dz = raw_pts[hi][0] - raw_pts[lo][0]
        if dt <= 0 or dz <= 0:
            continue
        lsr = dz / dt  # cm / kyr
        # Relative bulk 3He burial flux (assumes constant dry bulk density, which cancels in ratios)
        rel_burial = he * lsr
        out.append(Sample(
            core=core_name,
            region="Central North Atlantic (Mid-Atlantic Ridge)",
            lab="UC Davis / Harvard (Middleton)",
            age_ka=age,
            flux_pcc_cm2_kyr=rel_burial,
            conc_pcc_g=he,
            mar_g_cm2_kyr=lsr,
            depth_cm=dep,
            source="Middleton et al. 2018 (NOAA 25870)",
        ))
    return out


def parse_brook2000(path: Path) -> List[Sample]:
    """Brook et al. (2000) NOAA Study 2454 — GISP2 & Vostok polar ice-core 3He_ET flux."""
    lines = path.read_text(encoding="latin-1").splitlines()
    site = ""
    out: List[Sample] = []
    for line in lines[45:]:
        s = line.strip()
        if not s:
            continue
        if s.startswith("GISP2"):
            site = "GISP2 (Greenland)"
            continue
        if s.startswith("Vostok"):
            site = "Vostok (Antarctica)"
            continue
        if s.startswith("*") or s.startswith("Notes") or not site:
            continue
        parts = line.split("\t")
        if len(parts) < 8:
            continue
        age = _f(parts[1])
        flx = _f(parts[7])
        if age is None or flx is None:
            continue
        out.append(Sample(
            core=site,
            region="Polar Ice Core",
            lab="WHOI / WSU (Brook)",
            age_ka=age,
            flux_pcc_cm2_kyr=flx,
            source="Brook et al. 2000 (NOAA 2454)",
        ))
    return out


def parse_farley2006(path: Path, core_name: str, region: str) -> List[Sample]:
    """Farley et al. (2006) PANGAEA.769829 / 769830 — ODP 121-757B & ODP 154-926B positive controls."""
    cols, rows = parse_pangaea_tab(path)
    idx_age = cols.index("Age [ka BP]")
    idx_flx = cols.index("3He ET flux [fmol/cm**2/ka]")
    idx_rat = cols.index("3He/4He [10**-4]")
    out: List[Sample] = []
    for r in rows:
        if len(r) <= max(idx_age, idx_flx):
            continue
        age_ka = _f(r[idx_age])
        flx_fmol = _f(r[idx_flx])
        rat = _f(r[idx_rat]) if idx_rat < len(r) else None
        if age_ka is None or flx_fmol is None:
            continue
        # Convert fmol cm^-2 ka^-1 to pcc STP cm^-2 ka^-1 (1 fmol = 22.414e-3 pcc STP)
        flx_pcc = flx_fmol * 0.022414
        out.append(Sample(
            core=core_name,
            region=region,
            lab="Caltech (Farley)",
            age_ka=age_ka,
            flux_pcc_cm2_kyr=flx_pcc,
            ratio_1e4=rat,
            source=f"Farley et al. 2006 ({core_name})",
        ))
    return sorted(out, key=lambda s: s.age_ka)


def stratified_window_test(
    samples: List[Sample],
    t_lo: float,
    t_hi: float,
    base_lo: Optional[float] = None,
    base_hi: Optional[float] = None,
    use_conc: bool = False,
    n_perm: int = N_PERM,
    n_boot: int = N_BOOT,
    seed: int = RNG_SEED,
    min_baseline_per_core: int = 3,
) -> Dict:
    """
    Core-normalized stratified ratio test (target window [t_lo, t_hi] vs baseline).
    Normalizes each sample by its own core's baseline median, then runs stratified
    within-core permutation test (H1: target > baseline) and stratified bootstrap 95% CI.
    """
    by_core: Dict[str, List[Sample]] = {}
    for s in samples:
        by_core.setdefault(s.core, []).append(s)

    core_blocks: List[Tuple[str, np.ndarray, np.ndarray]] = []
    per_core_stats: Dict[str, Dict] = {}
    t_norm_all: List[float] = []
    b_norm_all: List[float] = []
    t_raw_all: List[float] = []
    b_raw_all: List[float] = []

    for core, cs in sorted(by_core.items()):
        vals = [(s.age_ka, s.conc_pcc_g if use_conc else s.flux_pcc_cm2_kyr) for s in cs]
        vals = [(a, v) for a, v in vals if v is not None and v > 0]
        t_vals = np.array([v for a, v in vals if t_lo <= a <= t_hi], dtype=float)
        if base_lo is not None and base_hi is not None:
            b_vals = np.array([v for a, v in vals if (base_lo <= a <= base_hi) and not (t_lo <= a <= t_hi)], dtype=float)
        else:
            b_vals = np.array([v for a, v in vals if not (t_lo <= a <= t_hi)], dtype=float)

        if len(b_vals) < min_baseline_per_core:
            continue
        b_med = float(np.median(b_vals))
        if b_med <= 0:
            continue
        t_norm = t_vals / b_med
        b_norm = b_vals / b_med

        per_core_stats[core] = {
            "n_target": int(len(t_vals)),
            "n_baseline": int(len(b_vals)),
            "target_median_raw": round(float(np.median(t_vals)), 4) if len(t_vals) else None,
            "baseline_median_raw": round(b_med, 4),
            "median_ratio": round(float(np.median(t_norm)), 4) if len(t_vals) else None,
            "mean_ratio": round(float(np.mean(t_norm) / np.mean(b_norm)), 4) if len(t_vals) else None,
        }
        if len(t_vals) > 0:
            core_blocks.append((core, t_norm, b_norm))
            t_norm_all.extend(t_norm.tolist())
            b_norm_all.extend(b_norm.tolist())
            t_raw_all.extend(t_vals.tolist())
            b_raw_all.extend(b_vals.tolist())

    if not t_norm_all or not b_norm_all:
        return {"n_cores": 0, "n_target": 0, "n_baseline": 0, "median_ratio": None}

    t_arr = np.array(t_norm_all, dtype=float)
    b_arr = np.array(b_norm_all, dtype=float)
    obs_med_ratio = float(np.median(t_arr) / np.median(b_arr))
    obs_mean_ratio = float(np.mean(t_arr) / np.mean(b_arr))

    rng = np.random.default_rng(seed)

    # Stratified within-core permutation test (preserves exact n_target, n_baseline per core)
    perm_ratios = np.empty(n_perm, dtype=float)
    for k in range(n_perm):
        pt_list = []
        pb_list = []
        for _, tn, bn in core_blocks:
            comb = np.concatenate([tn, bn])
            perm = rng.permutation(comb)
            nt = len(tn)
            pt_list.append(perm[:nt])
            pb_list.append(perm[nt:])
        pt = np.concatenate(pt_list)
        pb = np.concatenate(pb_list)
        perm_ratios[k] = np.median(pt) / np.median(pb)
    p_perm_one_sided = float((1 + np.sum(perm_ratios >= obs_med_ratio)) / (n_perm + 1))
    p_perm_two_sided = float((1 + np.sum(np.abs(np.log(perm_ratios)) >= abs(math.log(obs_med_ratio)))) / (n_perm + 1))

    # Stratified bootstrap 95% CI on median ratio
    boot_ratios = np.empty(n_boot, dtype=float)
    for k in range(n_boot):
        bt_list = []
        bb_list = []
        for _, tn, bn in core_blocks:
            bt_list.append(rng.choice(tn, size=len(tn), replace=True))
            bb_list.append(rng.choice(bn, size=len(bn), replace=True))
        bt = np.concatenate(bt_list)
        bb = np.concatenate(bb_list)
        boot_ratios[k] = np.median(bt) / np.median(bb)
    ci_lo, ci_hi = np.percentile(boot_ratios, [2.5, 97.5])

    return {
        "window_ka": [t_lo, t_hi],
        "n_cores_with_target": len(core_blocks),
        "cores_used": [c for c, _, _ in core_blocks],
        "n_target": int(len(t_arr)),
        "n_baseline": int(len(b_arr)),
        "target_median_raw": round(float(np.median(t_raw_all)), 4),
        "baseline_median_raw": round(float(np.median(b_raw_all)), 4),
        "median_ratio": round(obs_med_ratio, 4),
        "mean_ratio": round(obs_mean_ratio, 4),
        "boot_ci95": [round(float(ci_lo), 4), round(float(ci_hi), 4)],
        "p_perm_one_sided": round(p_perm_one_sided, 5),
        "p_perm_two_sided": round(p_perm_two_sided, 5),
        "per_core": per_core_stats,
    }


def blind_peak_scan(samples: List[Sample], top_frac: float = 0.10) -> Dict:
    """Blind top-10% peak scan on core-normalized 3He_ET flux (no boundary labels)."""
    by_core: Dict[str, List[Sample]] = {}
    for s in samples:
        by_core.setdefault(s.core, []).append(s)

    normed = []
    for core, cs in by_core.items():
        med = float(np.median([s.flux_pcc_cm2_kyr for s in cs if s.flux_pcc_cm2_kyr > 0]))
        for s in cs:
            if s.flux_pcc_cm2_kyr > 0:
                normed.append({
                    "core": s.core,
                    "region": s.region,
                    "age_ka": round(s.age_ka, 3),
                    "flux_raw": round(s.flux_pcc_cm2_kyr, 4),
                    "flux_norm": round(s.flux_pcc_cm2_kyr / med, 4),
                })
    normed.sort(key=lambda x: x["flux_norm"], reverse=True)
    n_tot = len(normed)
    k_top = max(1, int(round(n_tot * top_frac)))
    top_rows = normed[:k_top]

    windows_out = {}
    for wname, (lo, hi) in WINDOWS.items():
        m_in_win = sum(1 for x in normed if lo <= x["age_ka"] <= hi)
        hits = sum(1 for x in top_rows if lo <= x["age_ka"] <= hi)
        # One-sided hypergeometric enrichment P(X >= hits)
        p_enrich = float(hypergeom.sf(hits - 1, n_tot, m_in_win, k_top)) if hits > 0 else 1.0
        windows_out[wname] = {
            "n_in_window": m_in_win,
            "top_hits_in_window": hits,
            "expected_hits": round(k_top * m_in_win / n_tot, 2),
            "frac_top_outside_window": round(1.0 - hits / k_top, 4),
            "p_enrichment": round(p_enrich, 5),
        }

    return {
        "n_total": n_tot,
        "k_top_10pct": k_top,
        "threshold_norm_flux": top_rows[-1]["flux_norm"],
        "top_samples": top_rows,
        "window_overlap": windows_out,
    }


def evaluate_verdict(pos_ctrl: Dict, p1_pooled: Dict, p1_serno: Dict, p1_cocos: Dict) -> Tuple[str, str]:
    """Strictly implement protocol.md §4 mutually exclusive verdict rules."""
    pos_pass = all(
        v["median_ratio"] is not None and v["median_ratio"] >= 2.0 and v["p_perm_one_sided"] < 0.01
        for v in pos_ctrl.values()
    )
    if not pos_pass:
        return "ambiguous_or_mixed", "One or more Pillar 0 cosmic-breakup positive controls failed."

    # Rule 1: cosmic_dust_surge_detected
    for wname in WINDOWS:
        wp = p1_pooled[wname]
        ws = p1_serno[wname]
        wc = p1_cocos[wname]
        if (
            wp["median_ratio"] is not None
            and wp["median_ratio"] >= 1.50
            and wp["p_perm_one_sided"] < 0.01
            and ws["median_ratio"] is not None and ws["median_ratio"] > 1.25
            and wc["median_ratio"] is not None and wc["median_ratio"] > 1.25
        ):
            return (
                "cosmic_dust_surge_detected",
                f"{wname} shows replicated >=1.50x 3He_ET surge (pooled {wp['median_ratio']:.2f}x, p={wp['p_perm_one_sided']:.5f}) across both North & Equatorial Pacific.",
            )

    # Rule 2: no_cosmic_dust_surge
    all_flat = all(
        (p1_pooled[w]["p_perm_one_sided"] >= 0.05) or (p1_pooled[w]["median_ratio"] < 1.20)
        for w in WINDOWS
    )
    w1_ub = p1_pooled["W1_YD_13.5_11.5"]["boot_ci95"][1]
    w2_ub = p1_pooled["W2_Deglacial_15_10"]["boot_ci95"][1]
    if all_flat and w2_ub < 1.50 and w1_ub < 1.80:
        return (
            "no_cosmic_dust_surge",
            f"All 3 positive controls passed (>=2.0x, p<0.01), while all 3 Younger Dryas / deglacial windows show no elevation and tight 95% upper bounds (W1 <= {w1_ub:.2f}x, W2 <= {w2_ub:.2f}x).",
        )

    return (
        "ambiguous_or_mixed",
        f"Did not meet clean positive or negative criteria (W1={p1_pooled['W1_YD_13.5_11.5']['median_ratio']:.2f}x [CI_hi={w1_ub:.2f}], W2={p1_pooled['W2_Deglacial_15_10']['median_ratio']:.2f}x [CI_hi={w2_ub:.2f}]).",
    )


def run_all() -> Dict:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Pillar 0: Positive Controls (Farley et al. 2006)
    odp757 = parse_farley2006(DATA_DIR / "farley2006_odp757b.tab", "ODP-757B", "South Indian Ocean")
    odp926 = parse_farley2006(DATA_DIR / "farley2006_odp926b.tab", "ODP-926B", "Equatorial Atlantic")
    pos_ctrl = {
        "Veritas_8.2Ma_ODP757B": stratified_window_test(
            odp757, 7500.0, 8350.0, base_lo=6200.0, base_hi=10500.0, seed=RNG_SEED + 1
        ),
        "Veritas_8.2Ma_ODP926B": stratified_window_test(
            odp926, 7500.0, 8350.0, base_lo=6200.0, base_hi=10500.0, seed=RNG_SEED + 2
        ),
        "LateEocene_35.5Ma_ODP757B": stratified_window_test(
            odp757, 34500.0, 36500.0, base_lo=25000.0, base_hi=33500.0, seed=RNG_SEED + 3
        ),
    }

    # Pillar 1: 7 Pacific paired 230Th + 3He cores
    serno = parse_serno2015(DATA_DIR / "serno2015_so202_07_6.tab", r_terr_1e4=R_TERR_DEFAULT_1E4)
    serno_hi_terr = parse_serno2015(DATA_DIR / "serno2015_so202_07_6.tab", r_terr_1e4=R_TERR_HIGH_1E4)
    cocos = parse_tomchovska2026(DATA_DIR / "tomchovska2026_cocos_ridge.xlsx")
    marcantonio = parse_marcantonio2001(DATA_DIR / "marcantonio2001_b18_b25.tab")
    p1_all = serno + cocos + marcantonio

    p1_pooled = {}
    p1_serno = {}
    p1_serno_hi_terr = {}
    p1_cocos = {}
    p1_marcantonio = {}
    for i, (wname, (lo, hi)) in enumerate(WINDOWS.items()):
        p1_pooled[wname] = stratified_window_test(p1_all, lo, hi, seed=RNG_SEED + 10 + i)
        p1_serno[wname] = stratified_window_test(serno, lo, hi, seed=RNG_SEED + 20 + i)
        p1_serno_hi_terr[wname] = stratified_window_test(serno_hi_terr, lo, hi, seed=RNG_SEED + 30 + i)
        p1_cocos[wname] = stratified_window_test(cocos, lo, hi, seed=RNG_SEED + 40 + i)
        p1_marcantonio[wname] = stratified_window_test(marcantonio, lo, hi, seed=RNG_SEED + 50 + i)

    # Split W3 baseline comparison: 20-10 ka vs Holocene (<10 ka) ONLY, and vs Glacial (>20 ka) ONLY
    p1_w3_vs_hol = stratified_window_test(p1_all, 10.0, 20.0, base_lo=0.0, base_hi=10.0, seed=RNG_SEED + 61)
    p1_w3_vs_glac = stratified_window_test(p1_all, 10.0, 20.0, base_lo=20.0, base_hi=400.0, seed=RNG_SEED + 62)

    # Blind top-10% peak scan on Pillar 1
    p1_peaks = blind_peak_scan(p1_all, top_frac=0.10)

    # Pillar 2: Mid-Atlantic Ridge (Middleton 2018) & Polar Ice-Core Reference (Brook 2000)
    ggc3 = parse_middleton2018(DATA_DIR / "middleton2018_kn207_ggc3.txt", "KN207-2-GGC3")
    ggc6 = parse_middleton2018(DATA_DIR / "middleton2018_kn207_ggc6.txt", "KN207-2-GGC6")
    atlantic = ggc3 + ggc6
    p2_atlantic_burial = {}
    p2_atlantic_conc = {}
    for i, (wname, (lo, hi)) in enumerate(WINDOWS.items()):
        p2_atlantic_burial[wname] = stratified_window_test(atlantic, lo, hi, use_conc=False, seed=RNG_SEED + 70 + i)
        p2_atlantic_conc[wname] = stratified_window_test(atlantic, lo, hi, use_conc=True, seed=RNG_SEED + 80 + i)

    ice_ref = parse_brook2000(DATA_DIR / "brook2000_ice_helium.txt")
    ice_vals = [s.flux_pcc_cm2_kyr for s in ice_ref]
    ice_hol = [s.flux_pcc_cm2_kyr for s in ice_ref if s.age_ka < 10.0]
    ice_glac = [s.flux_pcc_cm2_kyr for s in ice_ref if s.age_ka > 20.0]
    ice_summary = {
        "n_total": len(ice_ref),
        "n_holocene_0_4ka": len(ice_hol),
        "n_deglacial_10_20ka": sum(1 for s in ice_ref if 10.0 <= s.age_ka <= 20.0),
        "n_glacial_75_97ka": len(ice_glac),
        "all_median_pcc_cm2_kyr": round(float(np.median(ice_vals)), 3),
        "all_mean_pcc_cm2_kyr": round(float(np.mean(ice_vals)), 3),
        "holocene_median_pcc_cm2_kyr": round(float(np.median(ice_hol)), 3),
        "glacial_median_pcc_cm2_kyr": round(float(np.median(ice_glac)), 3),
    }

    # Per-core absolute flux overview (for transparency & comparison with McGee & Mukhopadhyay 0.8 ± 0.3)
    core_overview = {}
    for s in p1_all:
        core_overview.setdefault(s.core, []).append(s)
    core_table = []
    for cname, cs in sorted(core_overview.items()):
        flxs = [x.flux_pcc_cm2_kyr for x in cs]
        ages = [x.age_ka for x in cs]
        core_table.append({
            "core": cname,
            "region": cs[0].region,
            "lab": cs[0].lab,
            "n_samples": len(cs),
            "age_min_ka": round(min(ages), 2),
            "age_max_ka": round(max(ages), 2),
            "n_W1_13.5_11.5": sum(11.5 <= a <= 13.5 for a in ages),
            "n_W2_15_10": sum(10.0 <= a <= 15.0 for a in ages),
            "n_W3_20_10": sum(10.0 <= a <= 20.0 for a in ages),
            "flux_median_pcc_cm2_kyr": round(float(np.median(flxs)), 3),
            "flux_iqr_pcc_cm2_kyr": round(float(np.percentile(flxs, 75) - np.percentile(flxs, 25)), 3),
        })

    verdict, reason = evaluate_verdict(pos_ctrl, p1_pooled, p1_serno, p1_cocos)

    summary = {
        "question": "yd-cosmic-dust-he3",
        "issue": 121,
        "verdict": verdict,
        "verdict_reason": reason,
        "positive_controls_pass": all(
            v["median_ratio"] >= 2.0 and v["p_perm_one_sided"] < 0.01 for v in pos_ctrl.values()
        ),
        "pillar0_positive_controls": pos_ctrl,
        "pillar1_core_overview": core_table,
        "pillar1_pooled_230Th_norm": p1_pooled,
        "pillar1_serno_SO202_07_6": p1_serno,
        "pillar1_serno_high_Rterr_sensitivity": p1_serno_hi_terr,
        "pillar1_cocos_ridge_CR01_CR05": p1_cocos,
        "pillar1_marcantonio_B18_B25": p1_marcantonio,
        "pillar1_W3_vs_Holocene_only": p1_w3_vs_hol,
        "pillar1_W3_vs_Glacial_only": p1_w3_vs_glac,
        "pillar1_blind_peak_scan": p1_peaks,
        "pillar2_atlantic_burial": p2_atlantic_burial,
        "pillar2_atlantic_conc": p2_atlantic_conc,
        "polar_ice_reference_brook2000": ice_summary,
    }

    (RESULTS_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    # Export flat CSVs for downstream plotting & audit
    with open(RESULTS_DIR / "pillar1_samples.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["core", "region", "lab", "age_ka", "depth_cm", "flux_pcc_cm2_kyr", "flux_norm_core_median", "conc_pcc_g", "mar_g_cm2_kyr", "ratio_1e4", "source"])
        by_c: Dict[str, float] = {}
        for cname, cs in core_overview.items():
            by_c[cname] = float(np.median([x.flux_pcc_cm2_kyr for x in cs]))
        for s in p1_all:
            w.writerow([
                s.core, s.region, s.lab, f"{s.age_ka:.4f}",
                "" if s.depth_cm is None else f"{s.depth_cm:.2f}",
                f"{s.flux_pcc_cm2_kyr:.5f}",
                f"{s.flux_pcc_cm2_kyr / by_c[s.core]:.5f}",
                "" if s.conc_pcc_g is None else f"{s.conc_pcc_g:.5f}",
                "" if s.mar_g_cm2_kyr is None else f"{s.mar_g_cm2_kyr:.5f}",
                "" if s.ratio_1e4 is None else f"{s.ratio_1e4:.5f}",
                s.source,
            ])

    with open(RESULTS_DIR / "pillar2_atlantic.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["core", "age_ka", "depth_cm", "conc_3He_ET_pcc_g", "lsr_cm_kyr", "rel_burial_flux"])
        for s in atlantic:
            w.writerow([s.core, f"{s.age_ka:.3f}", f"{s.depth_cm:.2f}", f"{s.conc_pcc_g:.5f}", f"{s.mar_g_cm2_kyr:.4f}", f"{s.flux_pcc_cm2_kyr:.5f}"])

    with open(RESULTS_DIR / "positive_controls.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["core", "region", "age_Ma", "flux_pcc_cm2_kyr", "ratio_1e4"])
        for s in odp757 + odp926:
            w.writerow([s.core, s.region, f"{s.age_ka / 1000.0:.5f}", f"{s.flux_pcc_cm2_kyr:.5f}", "" if s.ratio_1e4 is None else f"{s.ratio_1e4:.5f}"])

    print(f"VERDICT: {verdict}")
    print(f"REASON:  {reason}")
    for k, v in pos_ctrl.items():
        print(f"  POS CTRL {k}: ratio={v['median_ratio']:.2f}x (CI95 {v['boot_ci95']}), p={v['p_perm_one_sided']:.5f} (n={v['n_target']}/{v['n_baseline']})")
    for wname in WINDOWS:
        v = p1_pooled[wname]
        print(f"  P1 POOLED {wname}: ratio={v['median_ratio']:.3f}x (CI95 {v['boot_ci95']}), p={v['p_perm_one_sided']:.5f} (n={v['n_target']}/{v['n_baseline']})")
    return summary


if __name__ == "__main__":
    run_all()
