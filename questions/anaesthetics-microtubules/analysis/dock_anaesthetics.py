#!/usr/bin/env python3
"""
Locked molecular docking and statistical evaluation pipeline for Issue #48:
"Do anaesthetics pick out microtubules?" (questions/anaesthetics-microtubules).

Uses version-pinned open-source tools:
  - AutoDock Vina v1.2.5 (vina & vinardo scoring functions)
  - Open Babel 3.1.1 (deterministic receptor/ligand PDBQT preparation)
  - Pure NumPy statistical routines (deterministic seed 20261123)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

SEED = 20261123
BOX_SIZE = 18.0
EXHAUSTIVENESS = 4  # Amendment 1 (2026-11-23): reduced from 16 to 4 after verifying <=0.011 kcal/mol convergence on redocking controls
RT_310K = 0.00198720425864083 * 310.0  # 0.616033 kcal/mol
N_PERM = 10000
N_BOOT = 5000
SCORING_FUNCTIONS = ("vina", "vinardo")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PDB_DIR = DATA_DIR / "pdb"
WORK_DIR = DATA_DIR / "dock_work"
RESULTS_DIR = ROOT / "results"


@dataclass(frozen=True)
class Molecule:
    mol_id: str
    name: str
    mol_class: str  # "anaesthetic", "non_immobilizer", "convulsant"
    subset: str     # "clinical", "fang1996", "non_imm", "annotated"
    cid: int
    smiles: str
    mac_atm: Optional[float]
    oil_gas: Optional[float]
    n_heavy: int
    mw: float
    xlogp: float
    source: str


MOLECULES: List[Molecule] = [
    # Subset A: Clinical volatile anaesthetics (n = 9)
    Molecule("methoxyflurane", "Methoxyflurane", "anaesthetic", "clinical", 4116, "COC(C(Cl)Cl)(F)F", 0.00160, 960.0, 8, 164.96, 2.2, "Craddock 2017 S1"),
    Molecule("trichloroethylene", "Trichloroethylene", "anaesthetic", "clinical", 6575, "C(=C(Cl)Cl)Cl", 0.00170, 960.0, 5, 131.38, 2.6, "BJA 1986 / UiA"),
    Molecule("halothane", "Halothane", "anaesthetic", "clinical", 3562, "C(C(F)(F)F)(Cl)Br", 0.00770, 224.0, 7, 197.38, 2.3, "Craddock 2017 S1"),
    Molecule("isoflurane", "Isoflurane", "anaesthetic", "clinical", 3763, "C(C(F)(F)F)(OC(F)F)Cl", 0.01200, 96.0, 10, 184.49, 2.1, "Craddock 2017 S1"),
    Molecule("enflurane", "Enflurane", "anaesthetic", "clinical", 3226, "C(C(OC(F)F)(F)F)(F)Cl", 0.01700, 98.0, 10, 184.49, 2.1, "Craddock 2017 S1"),
    Molecule("diethyl_ether", "Diethyl ether", "anaesthetic", "clinical", 3283, "CCOCC", 0.01900, 65.0, 5, 74.12, 0.9, "Craddock 2017 S1"),
    Molecule("sevoflurane", "Sevoflurane", "anaesthetic", "clinical", 5206, "C(OC(C(F)(F)F)C(F)(F)F)F", 0.02000, 53.0, 12, 200.05, 2.8, "Craddock 2017 S1"),
    Molecule("desflurane", "Desflurane", "anaesthetic", "clinical", 42113, "C(C(F)(F)F)(OC(F)F)F", 0.06000, 19.0, 10, 168.04, 2.6, "Craddock 2017 S1"),
    Molecule("nitrous_oxide", "Nitrous oxide", "anaesthetic", "clinical", 948, "[N-]=[N+]=O", 1.01000, 0.39, 3, 44.01, 0.5, "Craddock 2017 S1"),
    # Subset B: Experimental aromatic & cycloalkane volatile anaesthetics (Fang et al. 1996 / Liu et al. 1994, n = 18)
    Molecule("o_xylene", "o-Xylene", "anaesthetic", "fang1996", 7237, "CC1=CC=CC=C1C", 0.00118, 10800.0, 8, 106.16, 3.1, "Fang 1996 T4-T5"),
    Molecule("ethylbenzene", "Ethylbenzene", "anaesthetic", "fang1996", 7500, "CCC1=CC=CC=C1", 0.00121, 5450.0, 8, 106.16, 3.1, "Fang 1996 T4-T5"),
    Molecule("m_xylene", "m-Xylene", "anaesthetic", "fang1996", 7929, "CC1=CC(=CC=C1)C", 0.00139, 7780.0, 8, 106.16, 3.2, "Fang 1996 T4-T5"),
    Molecule("p_xylene", "p-Xylene", "anaesthetic", "fang1996", 7809, "CC1=CC=C(C=C1)C", 0.00151, 6300.0, 8, 106.16, 3.2, "Fang 1996 T4-T5"),
    Molecule("toluene", "Toluene", "anaesthetic", "fang1996", 1140, "CC1=CC=CC=C1", 0.00450, 2170.0, 7, 92.14, 2.7, "Fang 1996 T4-T5"),
    Molecule("o_difluorobenzene", "o-Difluorobenzene", "anaesthetic", "fang1996", 9706, "C1=CC=C(C(=C1)F)F", 0.00610, 853.0, 8, 114.09, 2.4, "Fang 1996 T4-T5"),
    Molecule("p_difluorobenzene", "p-Difluorobenzene", "anaesthetic", "fang1996", 10892, "C1=CC(=CC=C1F)F", 0.00640, 654.0, 8, 114.09, 2.2, "Fang 1996 T4-T5"),
    Molecule("methylpentafluorobenzene", "Methylpentafluorobenzene", "anaesthetic", "fang1996", 69869, "CC1=C(C(=C(C(=C1F)F)F)F)F", 0.00640, 1470.0, 12, 182.09, 2.8, "Fang 1996 T4-T5"),
    Molecule("124_trifluorobenzene", "1,2,4-Trifluorobenzene", "anaesthetic", "fang1996", 67773, "C1=CC(=C(C=C1F)F)F", 0.00970, 621.0, 9, 132.08, 2.4, "Fang 1996 T4-T5"),
    Molecule("benzene", "Benzene", "anaesthetic", "fang1996", 241, "C1=CC=CC=C1", 0.01010, 565.0, 6, 78.11, 2.1, "Fang 1996 T4-T5"),
    Molecule("fluorobenzene", "Fluorobenzene", "anaesthetic", "fang1996", 10008, "C1=CC=C(C=C1)F", 0.01120, 661.0, 7, 96.10, 2.3, "Fang 1996 T4-T5"),
    Molecule("pentafluorobenzene", "Pentafluorobenzene", "anaesthetic", "fang1996", 9696, "C1=C(C(=C(C(=C1F)F)F)F)F", 0.01250, 393.0, 11, 168.06, 2.5, "Fang 1996 T4-T5"),
    Molecule("cycloheptane", "Cycloheptane", "anaesthetic", "fang1996", 9265, "C1CCCCCC1", 0.01370, 2780.0, 7, 98.19, 4.0, "Fang 1996 T4-T5"),
    Molecule("hexafluorobenzene", "Hexafluorobenzene", "anaesthetic", "fang1996", 9805, "C1(=C(C(=C(C(=C1F)F)F)F)F)F", 0.01610, 251.0, 12, 186.05, 2.5, "Fang 1996 T4-T5"),
    Molecule("135_trifluorobenzene", "1,3,5-Trifluorobenzene", "anaesthetic", "fang1996", 9745, "C1=C(C=C(C=C1F)F)F", 0.02220, 335.0, 9, 132.08, 2.2, "Fang 1996 T4-T5"),
    Molecule("n_hexane", "n-Hexane", "anaesthetic", "fang1996", 8058, "CCCCCC", 0.03500, 148.0, 6, 86.18, 3.9, "Liu 1994 / Fang 1996 T5"),
    Molecule("cyclohexane", "Cyclohexane", "anaesthetic", "fang1996", 8078, "C1CCCCC1", 0.04200, 385.0, 6, 84.16, 3.4, "Fang 1996 T4-T5"),
    Molecule("cyclopentane", "Cyclopentane", "anaesthetic", "fang1996", 9253, "C1CCCC1", 0.05300, 139.0, 5, 70.13, 3.0, "Fang 1996 T4-T5"),
    # Confirmed Meyer-Overton Non-Immobilizers (n = 7)
    Molecule("F6", "F6 (1,2-dichlorohexafluorocyclobutane)", "non_immobilizer", "non_imm", 9643, "C1(C(C(C1(F)Cl)(F)Cl)(F)F)(F)F", None, 43.5, 12, 232.94, 3.2, "Koblin 1994 / Steffey 1998"),
    Molecule("F8", "F8 (2,3-dichlorooctafluorobutane)", "non_immobilizer", "non_imm", 78982, "C(C(C(F)(F)F)(F)Cl)(C(F)(F)F)(F)Cl", None, 25.0, 14, 270.93, 4.3, "Koblin 1994 / Steffey 1998"),
    Molecule("TFMB", "TFMB (1,3,5-tris(trifluoromethyl)benzene)", "non_immobilizer", "non_imm", 123085, "C1=C(C=C(C=C1C(F)(F)F)C(F)(F)F)C(F)(F)F", None, 264.0, 18, 282.10, 4.6, "Fang 1996 T2, T5"),
    Molecule("cyclooctane", "Cyclooctane", "non_immobilizer", "non_imm", 9266, "C1CCCCCCC1", None, 7010.0, 8, 112.21, 4.5, "Fang 1996 T2, T5"),
    Molecule("perfluoropentane", "Perfluoropentane", "non_immobilizer", "non_imm", 12675, "C(C(C(F)(F)F)(F)F)(C(C(F)(F)F)(F)F)(F)F", None, 0.662, 17, 288.03, 4.5, "Liu 1994 / Steffey 1998"),
    Molecule("perfluorocyclobutane", "Perfluorocyclobutane", "non_immobilizer", "non_imm", 8263, "C1(C(C(C1(F)F)(F)F)(F)F)(F)F", None, None, 12, 200.03, 1.6, "Koblin 1994"),
    Molecule("CF3CClFCF3", "2-Chloroheptafluoropropane", "non_immobilizer", "non_imm", 66156, "C(C(F)(F)F)(C(F)(F)F)(F)Cl", None, None, 11, 204.47, 3.4, "Koblin 1994"),
    # Annotated convulsant / transitional (n = 1)
    Molecule("flurothyl", "Flurothyl", "convulsant", "annotated", 9528, "C(C(F)(F)F)OCC(F)(F)F", None, 47.0, 11, 182.06, 2.3, "Craddock 2017 S1"),
]


@dataclass(frozen=True)
class SiteSpec:
    target_id: str
    target_label: str
    role: str
    pdb_id: str
    chains: Tuple[str, ...]
    site_id: str
    center: Tuple[float, float, float]
    is_primary_single: bool


SITES: List[SiteSpec] = [
    # Primary Orch OR target: bovine alpha/beta-tubulin 1JFF (Craddock 2012/2017 8 persistent single-dimer sites)
    SiteSpec("tubulin_1jff", "Tubulin (1JFF)", "test_primary", "1JFF", ("A", "B"), "site_1", (-13.09, -4.81, -0.86), False),
    SiteSpec("tubulin_1jff", "Tubulin (1JFF)", "test_primary", "1JFF", ("A", "B"), "site_4", (11.44, -11.78, -1.97), False),
    SiteSpec("tubulin_1jff", "Tubulin (1JFF)", "test_primary", "1JFF", ("A", "B"), "site_5", (25.52, -5.34, 3.59), False),
    SiteSpec("tubulin_1jff", "Tubulin (1JFF)", "test_primary", "1JFF", ("A", "B"), "site_7", (15.60, -5.03, 9.23), True),
    SiteSpec("tubulin_1jff", "Tubulin (1JFF)", "test_primary", "1JFF", ("A", "B"), "site_21", (-9.66, -9.13, 3.69), False),
    SiteSpec("tubulin_1jff", "Tubulin (1JFF)", "test_primary", "1JFF", ("A", "B"), "site_23", (26.45, -1.00, 9.18), False),
    SiteSpec("tubulin_1jff", "Tubulin (1JFF)", "test_primary", "1JFF", ("A", "B"), "site_37", (14.01, 0.64, -8.89), False),
    SiteSpec("tubulin_1jff", "Tubulin (1JFF)", "test_primary", "1JFF", ("A", "B"), "site_38", (15.80, -0.07, -2.17), False),
    # High-res replication tubulin: 4I4T (1.80 A X-ray)
    SiteSpec("tubulin_4i4t", "Tubulin (4I4T, 1.8 Å)", "test_replication", "4I4T", ("A", "B"), "site_1", (12.86, 47.46, 23.42), False),
    SiteSpec("tubulin_4i4t", "Tubulin (4I4T, 1.8 Å)", "test_replication", "4I4T", ("A", "B"), "site_4", (7.52, 60.88, 44.05), False),
    SiteSpec("tubulin_4i4t", "Tubulin (4I4T, 1.8 Å)", "test_replication", "4I4T", ("A", "B"), "site_5", (19.26, 75.92, 50.13), False),
    SiteSpec("tubulin_4i4t", "Tubulin (4I4T, 1.8 Å)", "test_replication", "4I4T", ("A", "B"), "site_7", (13.07, 69.85, 40.09), True),
    SiteSpec("tubulin_4i4t", "Tubulin (4I4T, 1.8 Å)", "test_replication", "4I4T", ("A", "B"), "site_21", (8.71, 51.05, 24.30), False),
    SiteSpec("tubulin_4i4t", "Tubulin (4I4T, 1.8 Å)", "test_replication", "4I4T", ("A", "B"), "site_23", (22.91, 79.83, 48.48), False),
    SiteSpec("tubulin_4i4t", "Tubulin (4I4T, 1.8 Å)", "test_replication", "4I4T", ("A", "B"), "site_37", (21.29, 57.31, 48.74), False),
    SiteSpec("tubulin_4i4t", "Tubulin (4I4T, 1.8 Å)", "test_replication", "4I4T", ("A", "B"), "site_38", (21.87, 64.63, 45.84), False),
    # Rival synaptic receptor: Human GABA_A alpha1-beta2-gamma2 (6X3T, 2.55 A cryo-EM)
    SiteSpec("gabaa_6x3t", "GABA_A (6X3T)", "rival_channel", "6X3T", ("A", "B", "C", "D", "E"), "site_B601", (134.05, 120.75, 156.36), True),
    SiteSpec("gabaa_6x3t", "GABA_A (6X3T)", "rival_channel", "6X3T", ("A", "B", "C", "D", "E"), "site_D601", (110.13, 136.34, 141.96), False),
    # Rival pentameric ion channel: GLIC + desflurane (3P4W, 3.20 A X-ray)
    SiteSpec("glic_3p4w", "GLIC (3P4W)", "rival_channel", "3P4W", ("A", "B", "C", "D", "E"), "site_A319", (46.87, -8.76, 45.36), True),
    # Positive non-conscious soluble control 1: Human Serum Albumin + halothane (1E7B, 2.38 A X-ray)
    SiteSpec("hsa_1e7b", "Albumin (1E7B)", "positive_control", "1E7B", ("A",), "site_4003", (10.88, 3.29, -12.49), True),
    SiteSpec("hsa_1e7b", "Albumin (1E7B)", "positive_control", "1E7B", ("A",), "site_4001_4002", (0.25, -20.40, -6.97), False),
    # Positive non-conscious soluble control 2: Firefly Luciferase + bromoform (1BA3, 2.20 A X-ray)
    SiteSpec("luciferase_1ba3", "Luciferase (1BA3)", "positive_control", "1BA3", ("A",), "site_991", (16.58, 82.65, 48.82), True),
    # Negative globular control 1: Hen Egg-White Lysozyme (1DPX, 1.65 A X-ray)
    SiteSpec("lysozyme_1dpx", "Lysozyme (1DPX)", "negative_control", "1DPX", ("A",), "site_cleft", (2.99, 20.60, 25.68), True),
    # Negative globular control 2: Human Ubiquitin (1UBQ, 1.80 A X-ray)
    SiteSpec("ubiquitin_1ubq", "Ubiquitin (1UBQ)", "negative_control", "1UBQ", ("A",), "site_patch", (27.09, 35.30, 20.28), True),
]

TARGET_ORDER = [
    "tubulin_1jff",
    "tubulin_4i4t",
    "gabaa_6x3t",
    "glic_3p4w",
    "hsa_1e7b",
    "luciferase_1ba3",
    "lysozyme_1dpx",
    "ubiquitin_1ubq",
]

# Craddock et al. (2017) Supplementary Table S2 MOE scores (kJ/mol -> converted to kcal/mol via /4.184)
# Best (most negative) score across the 8 single-dimer sites (1, 4, 5, 7, 21, 23, 37, 38)
CRADDOCK_2017_MOE_KJ: Dict[str, Dict[str, Optional[float]]] = {
    "desflurane": {"site_1": -7.83, "site_4": -7.94, "site_5": -9.16, "site_7": -8.96, "site_21": -5.94, "site_23": -7.29, "site_37": -6.69, "site_38": -7.31},
    "diethyl_ether": {"site_1": -5.87, "site_4": -7.30, "site_5": -7.15, "site_7": -7.20, "site_21": -5.02, "site_23": -5.70, "site_37": -5.58, "site_38": -7.55},
    "enflurane": {"site_1": -7.71, "site_4": -8.24, "site_5": -8.73, "site_7": -8.48, "site_21": -6.33, "site_23": -7.19, "site_37": -7.38, "site_38": -9.19},
    "halothane": {"site_1": -7.48, "site_4": -6.29, "site_5": -6.72, "site_7": -7.91, "site_21": -5.30, "site_23": -6.36, "site_37": -6.36, "site_38": -7.40},
    "isoflurane": {"site_1": -7.67, "site_4": -8.28, "site_5": -8.46, "site_7": -8.90, "site_21": -5.97, "site_23": -7.41, "site_37": -7.19, "site_38": -8.92},
    "methoxyflurane": {"site_1": -7.25, "site_4": -8.24, "site_5": -8.18, "site_7": -7.84, "site_21": -5.80, "site_23": -6.52, "site_37": -6.42, "site_38": -6.82},
    "nitrous_oxide": {"site_1": -4.55, "site_4": -4.41, "site_5": -6.16, "site_7": -5.46, "site_21": -4.95, "site_23": -4.97, "site_37": -4.97, "site_38": -6.07},
    "sevoflurane": {"site_1": -8.51, "site_4": -9.10, "site_5": -7.46, "site_7": -8.53, "site_21": -6.23, "site_23": -7.87, "site_37": -7.61, "site_38": -8.36},
    "F6": {"site_1": -7.88, "site_4": -7.73, "site_5": None, "site_7": -8.60, "site_21": -6.12, "site_23": -6.59, "site_37": -7.83, "site_38": -8.37},
    "TFMB": {"site_1": -10.72, "site_4": -9.32, "site_5": -8.32, "site_7": None, "site_21": -6.82, "site_23": -8.99, "site_37": -9.36, "site_38": -11.06},
    "flurothyl": {"site_1": -8.22, "site_4": -9.74, "site_5": -9.64, "site_7": -9.51, "site_21": -6.17, "site_23": -7.49, "site_37": -7.70, "site_38": -7.89},
}


# ---------------------------------------------------------------------------
# Pure-NumPy Statistics (deterministic, zero external stats library)
# ---------------------------------------------------------------------------

def average_ranks(x: np.ndarray) -> np.ndarray:
    """Compute midranks (average ranks for ties), 1-indexed."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(n, dtype=float)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and x[order[j + 1]] == x[order[i]]:
            j += 1
        avg_r = 0.5 * (i + j) + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg_r
        i = j + 1
    return ranks


def pearson_r(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    xm = x - x.mean()
    ym = y - y.mean()
    denom = float(np.sqrt(np.sum(xm * xm) * np.sum(ym * ym)))
    if denom == 0.0:
        return 0.0
    return float(np.sum(xm * ym) / denom)


def spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
    return pearson_r(average_ranks(x), average_ranks(y))


def partial_spearman(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    """Partial Spearman rank correlation between x and y controlling for z."""
    rx = average_ranks(x)
    ry = average_ranks(y)
    rz = average_ranks(z)
    rxy = pearson_r(rx, ry)
    rxz = pearson_r(rx, rz)
    ryz = pearson_r(ry, rz)
    denom = math.sqrt(max(0.0, (1.0 - rxz * rxz) * (1.0 - ryz * ryz)))
    if denom < 1e-12:
        return 0.0
    return float((rxy - rxz * ryz) / denom)


def roc_auc_pos_vs_neg(pos: np.ndarray, neg: np.ndarray) -> float:
    """P(pos > neg) + 0.5 * P(pos == neg)."""
    pos = np.asarray(pos, dtype=float)
    neg = np.asarray(neg, dtype=float)
    diff = pos[:, None] - neg[None, :]
    wins = np.sum(diff > 0.0) + 0.5 * np.sum(diff == 0.0)
    return float(wins / (len(pos) * len(neg)))


def ols_fit_and_residuals(x_train: np.ndarray, y_train: np.ndarray, x_all: np.ndarray, y_all: np.ndarray) -> Tuple[float, float, np.ndarray]:
    """Fit y = a + b*x on training subset, return (a, b, y_all - y_hat)."""
    x_tr = np.asarray(x_train, dtype=float)
    y_tr = np.asarray(y_train, dtype=float)
    xm = x_tr.mean()
    ym = y_tr.mean()
    vx = float(np.sum((x_tr - xm) ** 2))
    slope = float(np.sum((x_tr - xm) * (y_tr - ym)) / vx) if vx > 1e-12 else 0.0
    intercept = float(ym - slope * xm)
    resid = np.asarray(y_all, dtype=float) - (intercept + slope * np.asarray(x_all, dtype=float))
    return intercept, slope, resid


def perm_test_corr(x: np.ndarray, y: np.ndarray, stat_fn, n_perm: int, rng: np.random.Generator) -> Tuple[float, float]:
    if stat_fn is spearman_rho:
        ux = average_ranks(x)
        uy = average_ranks(y)
    else:
        ux = np.asarray(x, dtype=float)
        uy = np.asarray(y, dtype=float)
    ux = ux - ux.mean()
    uy = uy - uy.mean()
    nx = float(np.sqrt(np.sum(ux * ux)))
    ny = float(np.sqrt(np.sum(uy * uy)))
    if nx == 0.0 or ny == 0.0:
        return 0.0, 1.0
    ux = ux / nx
    uy = uy / ny
    obs = float(np.dot(ux, uy))
    # Vectorized permutations
    idx = np.argsort(rng.random((n_perm, len(uy))), axis=1)
    y_perm = uy[idx]
    rs = y_perm @ ux
    count = int(np.sum(np.abs(rs) >= abs(obs) - 1e-12))
    return obs, float((count + 1) / (n_perm + 1))


def perm_test_partial(x: np.ndarray, y: np.ndarray, z: np.ndarray, n_perm: int, rng: np.random.Generator) -> Tuple[float, float]:
    """Freedman-Lane / residual permutation test for partial Spearman correlation."""
    rx = average_ranks(x)
    ry = average_ranks(y)
    rz = average_ranks(z)
    _, _, ex = ols_fit_and_residuals(rz, rx, rz, rx)
    _, _, ey = ols_fit_and_residuals(rz, ry, rz, ry)
    return perm_test_corr(ex, ey, pearson_r, n_perm, rng)


def perm_test_auc(pos: np.ndarray, neg: np.ndarray, n_perm: int, rng: np.random.Generator) -> Tuple[float, float]:
    obs = roc_auc_pos_vs_neg(pos, neg)
    pooled = np.concatenate([pos, neg])
    ranks = average_ranks(pooled)
    n_pos = len(pos)
    n_neg = len(neg)
    idx = np.argsort(rng.random((n_perm, len(pooled))), axis=1)
    r_pos_sum = np.sum(ranks[idx[:, :n_pos]], axis=1)
    aucs = (r_pos_sum - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    dev_obs = abs(obs - 0.5)
    count = int(np.sum(np.abs(aucs - 0.5) >= dev_obs - 1e-12))
    return float(obs), float((count + 1) / (n_perm + 1))


def perm_test_mean_diff(group_a: np.ndarray, group_b: np.ndarray, n_perm: int, rng: np.random.Generator) -> Tuple[float, float]:
    """Two-sided permutation test of mean(group_a) - mean(group_b)."""
    obs = float(np.mean(group_a) - np.mean(group_b))
    pooled = np.concatenate([group_a, group_b])
    n_a = len(group_a)
    total = float(np.sum(pooled))
    n_b = len(group_b)
    idx = np.argsort(rng.random((n_perm, len(pooled))), axis=1)
    sum_a = np.sum(pooled[idx[:, :n_a]], axis=1)
    diffs = (sum_a / n_a) - ((total - sum_a) / n_b)
    count = int(np.sum(np.abs(diffs) >= abs(obs) - 1e-12))
    return obs, float((count + 1) / (n_perm + 1))


def bootstrap_corr_ci(x: np.ndarray, y: np.ndarray, stat_fn, n_boot: int, rng: np.random.Generator) -> Tuple[float, float]:
    n = len(x)
    if stat_fn is pearson_r:
        idx = rng.integers(0, n, size=(n_boot, n))
        xb = x[idx]; yb = y[idx]
        xm = xb - xb.mean(axis=1, keepdims=True)
        ym = yb - yb.mean(axis=1, keepdims=True)
        den = np.sqrt(np.sum(xm * xm, axis=1) * np.sum(ym * ym, axis=1))
        vals = np.where(den > 0, np.sum(xm * ym, axis=1) / np.where(den > 0, den, 1.0), 0.0)
        lo, hi = np.percentile(vals, [2.5, 97.5])
        return float(lo), float(hi)
    vals = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        vals[i] = stat_fn(x[idx], y[idx])
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def boltzmann_affinity(energies_kcal: Sequence[float], rt: float = RT_310K) -> float:
    """Boltzmann-averaged binding strength B_ens = RT * ln(mean(exp(-dG / RT)))."""
    b_vals = np.array([-e for e in energies_kcal], dtype=float)
    m = float(np.max(b_vals))
    return float(m + rt * math.log(float(np.mean(np.exp((b_vals - m) / rt)))))


# ---------------------------------------------------------------------------
# Structure & Docking Preparation
# ---------------------------------------------------------------------------

def prep_receptor(pdb_in: Path, chains: Sequence[str], pdbqt_out: Path) -> Path:
    clean_pdb = pdbqt_out.with_suffix(".clean.pdb")
    chain_set = set(chains)
    with open(pdb_in) as fin, open(clean_pdb, "w") as fout:
        for line in fin:
            if line.startswith("ATOM  ") and line[21] in chain_set and line[16] in (" ", "A"):
                fout.write(line[:16] + " " + line[17:])
        fout.write("END\n")
    subprocess.run(
        ["obabel", str(clean_pdb), "-O", str(pdbqt_out), "-xr", "-p", "7.4"],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return clean_pdb


def prep_ligand(mol: Molecule, lig_dir: Path) -> Path:
    sdf = lig_dir / f"{mol.mol_id}.sdf"
    pdbqt = lig_dir / f"{mol.mol_id}.pdbqt"
    subprocess.run(
        ["obabel", f"-:{mol.smiles}", "-O", str(sdf), "--gen3d", "--best"],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["obabel", str(sdf), "-O", str(pdbqt)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return pdbqt


def parse_vina_model1(pdbqt_path: Path) -> Tuple[float, List[Dict[str, object]]]:
    """Parse best-mode ΔG (kcal/mol) and MODEL 1 heavy-atom coordinates from Vina PDBQT."""
    affinity: Optional[float] = None
    atoms: List[Dict[str, object]] = []
    in_m1 = False
    with open(pdbqt_path) as f:
        for line in f:
            if line.startswith("MODEL 1"):
                in_m1 = True
            elif line.startswith("ENDMDL") and in_m1:
                break
            elif in_m1 and line.startswith("REMARK VINA RESULT:"):
                parts = line.split()
                affinity = float(parts[3])
            elif in_m1 and (line.startswith("ATOM") or line.startswith("HETATM")):
                atype = line[77:79].strip()
                aname = line[12:16].strip()
                if atype.upper().startswith("H"):
                    continue
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                atoms.append({"name": aname, "elem": atype, "x": round(x, 3), "y": round(y, 3), "z": round(z, 3)})
    if affinity is None:
        raise ValueError(f"Could not parse REMARK VINA RESULT from {pdbqt_path}")
    return affinity, atoms


def extract_pocket_context(clean_pdb: Path, center: Tuple[float, float, float], radius: float = 8.5) -> List[Dict[str, object]]:
    """Extract residue centroids and CA/sidechain markers within `radius` Å of pocket center for 3D visualization."""
    res_atoms: Dict[Tuple[str, int, str], List[Tuple[str, float, float, float]]] = {}
    cx, cy, cz = center
    r2 = radius * radius
    with open(clean_pdb) as f:
        for line in f:
            if not line.startswith("ATOM  "):
                continue
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            if (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2 <= r2:
                ch = line[21]
                resi = int(line[22:26].strip())
                resn = line[17:20].strip()
                aname = line[12:16].strip()
                res_atoms.setdefault((ch, resi, resn), []).append((aname, x, y, z))
    aromatic = {"PHE", "TYR", "TRP", "HIS"}
    hydrophobic = {"ALA", "VAL", "LEU", "ILE", "MET", "PRO", "CYS"}
    polar = {"SER", "THR", "ASN", "GLN"}
    charged = {"ASP", "GLU", "LYS", "ARG"}
    out = []
    for (ch, resi, resn), pts in sorted(res_atoms.items()):
        mx = sum(p[1] for p in pts) / len(pts)
        my = sum(p[2] for p in pts) / len(pts)
        mz = sum(p[3] for p in pts) / len(pts)
        kind = "aromatic" if resn in aromatic else ("hydrophobic" if resn in hydrophobic else ("charged" if resn in charged else "polar"))
        out.append({
            "chain": ch,
            "resi": resi,
            "resn": resn,
            "kind": kind,
            "x": round(mx, 2),
            "y": round(my, 2),
            "z": round(mz, 2),
        })
    return out


def run_batch_docking(rec_pdbqt: Path, lig_paths: Sequence[Path], site: SiteSpec, scoring: str, out_dir: Path, cpu: int = 2) -> Dict[str, Tuple[float, List[Dict[str, object]]]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    all_present = all(
        (out_dir / f"{lp.stem}_out.pdbqt").exists() or (out_dir / f"{lp.stem}.pdbqt").exists()
        for lp in lig_paths
    )
    if not all_present:
        cmd = [
            "vina",
            "--receptor", str(rec_pdbqt),
            "--batch", *[str(p) for p in lig_paths],
            "--dir", str(out_dir),
            "--center_x", f"{site.center[0]:.3f}",
            "--center_y", f"{site.center[1]:.3f}",
            "--center_z", f"{site.center[2]:.3f}",
            "--size_x", f"{BOX_SIZE:.1f}",
            "--size_y", f"{BOX_SIZE:.1f}",
            "--size_z", f"{BOX_SIZE:.1f}",
            "--scoring", scoring,
            "--exhaustiveness", str(EXHAUSTIVENESS),
            "--seed", str(SEED),
            "--cpu", str(cpu),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    parsed: Dict[str, Tuple[float, List[Dict[str, object]]]] = {}
    for lp in lig_paths:
        mol_id = lp.stem
        out_file = out_dir / f"{mol_id}_out.pdbqt"
        if not out_file.exists():
            # Vina sometimes names batch outputs identically to input stem
            alt = out_dir / f"{mol_id}.pdbqt"
            if alt.exists():
                out_file = alt
            else:
                raise FileNotFoundError(f"Expected Vina output missing: {out_file}")
        parsed[mol_id] = parse_vina_model1(out_file)
    return parsed


# ---------------------------------------------------------------------------
# Statistical Evaluation Engine (reusable in unit tests & locked run)
# ---------------------------------------------------------------------------

def evaluate_target_vector(
    b_by_mol: Dict[str, float],
    molecules: Sequence[Molecule],
    rng: np.random.Generator,
    subset_filter: Optional[str] = None,
) -> Dict[str, object]:
    """Compute all pre-registered potency tracking and non-immobilizer separation metrics."""
    anaes = [m for m in molecules if m.mol_class == "anaesthetic" and (subset_filter is None or m.subset == subset_filter)]
    non_imm = [m for m in molecules if m.mol_class == "non_immobilizer"]

    b_an = np.array([b_by_mol[m.mol_id] for m in anaes], dtype=float)
    p_an = np.array([-math.log10(m.mac_atm) for m in anaes], dtype=float)
    hvy_an = np.array([m.n_heavy for m in anaes], dtype=float)
    mw_an = np.array([m.mw for m in anaes], dtype=float)
    oil_an = np.array([math.log10(m.oil_gas) for m in anaes], dtype=float)
    xlp_an = np.array([m.xlogp for m in anaes], dtype=float)

    rho_pot, p_rho_pot = perm_test_corr(b_an, p_an, spearman_rho, N_PERM, rng)
    r_pot, p_r_pot = perm_test_corr(b_an, p_an, pearson_r, N_PERM, rng)
    rho_ci = bootstrap_corr_ci(b_an, p_an, spearman_rho, N_BOOT, rng)
    r_ci = bootstrap_corr_ci(b_an, p_an, pearson_r, N_BOOT, rng)

    rho_part_hvy, p_part_hvy = perm_test_partial(b_an, p_an, hvy_an, N_PERM, rng)
    rho_part_oil, p_part_oil = perm_test_partial(b_an, p_an, oil_an, N_PERM, rng)
    rho_part_xlp, p_part_xlp = perm_test_partial(b_an, p_an, xlp_an, N_PERM, rng)

    # Size / lipophilicity diagnostics
    rho_hvy = spearman_rho(b_an, hvy_an)
    rho_mw = spearman_rho(b_an, mw_an)
    rho_oil = spearman_rho(b_an, oil_an)
    rho_xlp = spearman_rho(b_an, xlp_an)

    # Non-immobilizer separation
    b_non = np.array([b_by_mol[m.mol_id] for m in non_imm], dtype=float)
    auc_sep, p_auc = perm_test_auc(b_an, b_non, N_PERM, rng)
    delta_b_raw = float(np.median(b_an) - np.median(b_non))

    # Lipophilicity-adjusted residual (all anaes vs n=5 non_imm with measured oil_gas)
    non_oil_mols = [m for m in non_imm if m.oil_gas is not None]
    x_oil_all = np.concatenate([oil_an, np.array([math.log10(m.oil_gas) for m in non_oil_mols])])
    y_oil_all = np.concatenate([b_an, np.array([b_by_mol[m.mol_id] for m in non_oil_mols])])
    a_oil, b_oil, resid_oil = ols_fit_and_residuals(oil_an, b_an, x_oil_all, y_oil_all)
    e_an_oil = resid_oil[: len(anaes)]
    e_non_oil = resid_oil[len(anaes) :]
    r_non_oil, p_non_oil = perm_test_mean_diff(e_non_oil, e_an_oil, N_PERM, rng)

    # Size-adjusted residual (all anaes vs all n=7 non_imm)
    x_hvy_all = np.concatenate([hvy_an, np.array([m.n_heavy for m in non_imm], dtype=float)])
    y_hvy_all = np.concatenate([b_an, b_non])
    a_hvy, b_hvy, resid_hvy = ols_fit_and_residuals(hvy_an, b_an, x_hvy_all, y_hvy_all)
    e_an_hvy = resid_hvy[: len(anaes)]
    e_non_hvy = resid_hvy[len(anaes) :]
    r_non_hvy, p_non_hvy = perm_test_mean_diff(e_non_hvy, e_an_hvy, N_PERM, rng)

    # XLogP-adjusted residual (all anaes vs all n=7 non_imm)
    x_xlp_all = np.concatenate([xlp_an, np.array([m.xlogp for m in non_imm], dtype=float)])
    a_xlp, b_xlp, resid_xlp = ols_fit_and_residuals(xlp_an, b_an, x_xlp_all, y_hvy_all)
    e_an_xlp = resid_xlp[: len(anaes)]
    e_non_xlp = resid_xlp[len(anaes) :]
    r_non_xlp, p_non_xlp = perm_test_mean_diff(e_non_xlp, e_an_xlp, N_PERM, rng)

    return {
        "n_anaesthetic": len(anaes),
        "n_non_immobilizer": len(non_imm),
        "n_non_immobilizer_oil": len(non_oil_mols),
        "mean_B_anaes": round(float(np.mean(b_an)), 4),
        "median_B_anaes": round(float(np.median(b_an)), 4),
        "mean_B_non": round(float(np.mean(b_non)), 4),
        "median_B_non": round(float(np.median(b_non)), 4),
        "rho_pot": round(rho_pot, 4),
        "p_rho_pot": round(p_rho_pot, 5),
        "rho_pot_ci95": [round(rho_ci[0], 4), round(rho_ci[1], 4)],
        "r_pot": round(r_pot, 4),
        "p_r_pot": round(p_r_pot, 5),
        "r_pot_ci95": [round(r_ci[0], 4), round(r_ci[1], 4)],
        "rho_partial_heavy": round(rho_part_hvy, 4),
        "p_partial_heavy": round(p_part_hvy, 5),
        "rho_partial_oil": round(rho_part_oil, 4),
        "p_partial_oil": round(p_part_oil, 5),
        "rho_partial_xlogp": round(rho_part_xlp, 4),
        "p_partial_xlogp": round(p_part_xlp, 5),
        "diag_rho_heavy": round(rho_hvy, 4),
        "diag_rho_mw": round(rho_mw, 4),
        "diag_rho_oil": round(rho_oil, 4),
        "diag_rho_xlogp": round(rho_xlp, 4),
        "auc_sep": round(auc_sep, 4),
        "p_auc_sep": round(p_auc, 5),
        "delta_B_raw": round(delta_b_raw, 4),
        "r_non_oil": round(r_non_oil, 4),
        "p_non_oil": round(p_non_oil, 5),
        "ols_oil_intercept": round(a_oil, 4),
        "ols_oil_slope": round(b_oil, 4),
        "r_non_heavy": round(r_non_hvy, 4),
        "p_non_heavy": round(p_non_hvy, 5),
        "ols_heavy_intercept": round(a_hvy, 4),
        "ols_heavy_slope": round(b_hvy, 4),
        "r_non_xlogp": round(r_non_xlp, 4),
        "p_non_xlogp": round(p_non_xlp, 5),
    }


def paired_target_comparison(
    b1: Dict[str, float],
    b2: Dict[str, float],
    molecules: Sequence[Molecule],
    rng: np.random.Generator,
) -> Dict[str, object]:
    """Paired stratified bootstrap comparing target 1 minus target 2."""
    anaes = [m for m in molecules if m.mol_class == "anaesthetic"]
    non_imm = [m for m in molecules if m.mol_class == "non_immobilizer"]
    non_oil = [m for m in non_imm if m.oil_gas is not None]

    b1_an = np.array([b1[m.mol_id] for m in anaes], dtype=float)
    b2_an = np.array([b2[m.mol_id] for m in anaes], dtype=float)
    p_an = np.array([-math.log10(m.mac_atm) for m in anaes], dtype=float)
    oil_an = np.array([math.log10(m.oil_gas) for m in anaes], dtype=float)
    hvy_an = np.array([m.n_heavy for m in anaes], dtype=float)

    b1_non = np.array([b1[m.mol_id] for m in non_imm], dtype=float)
    b2_non = np.array([b2[m.mol_id] for m in non_imm], dtype=float)
    hvy_non = np.array([m.n_heavy for m in non_imm], dtype=float)

    b1_noil = np.array([b1[m.mol_id] for m in non_oil], dtype=float)
    b2_noil = np.array([b2[m.mol_id] for m in non_oil], dtype=float)
    oil_noil = np.array([math.log10(m.oil_gas) for m in non_oil], dtype=float)

    def calc_metrics(ia, inon, inoil):
        drho = spearman_rho(b1_an[ia], p_an[ia]) - spearman_rho(b2_an[ia], p_an[ia])
        dauc = roc_auc_pos_vs_neg(b1_an[ia], b1_non[inon]) - roc_auc_pos_vs_neg(b2_an[ia], b2_non[inon])
        _, _, r1_oil = ols_fit_and_residuals(oil_an[ia], b1_an[ia], oil_noil[inoil], b1_noil[inoil])
        _, _, r2_oil = ols_fit_and_residuals(oil_an[ia], b2_an[ia], oil_noil[inoil], b2_noil[inoil])
        # positive = target 1 rejects non-immobilizers more strongly (more negative residual)
        d_rej_oil = float((-np.mean(r1_oil)) - (-np.mean(r2_oil)))
        _, _, r1_hvy = ols_fit_and_residuals(hvy_an[ia], b1_an[ia], hvy_non[inon], b1_non[inon])
        _, _, r2_hvy = ols_fit_and_residuals(hvy_an[ia], b2_an[ia], hvy_non[inon], b2_non[inon])
        d_rej_hvy = float((-np.mean(r1_hvy)) - (-np.mean(r2_hvy)))
        return drho, dauc, d_rej_oil, d_rej_hvy

    n_a, n_n, n_no = len(anaes), len(non_imm), len(non_oil)
    obs = calc_metrics(np.arange(n_a), np.arange(n_n), np.arange(n_no))
    arr = np.empty((N_BOOT, 4), dtype=float)
    for k in range(N_BOOT):
        ia = rng.integers(0, n_a, size=n_a)
        inon = rng.integers(0, n_n, size=n_n)
        inoil = rng.integers(0, n_no, size=n_no)
        arr[k] = calc_metrics(ia, inon, inoil)

    names = ["delta_rho_pot", "delta_auc_sep", "delta_reject_oil", "delta_reject_heavy"]
    out: Dict[str, object] = {}
    for j, nm in enumerate(names):
        lo, hi = np.percentile(arr[:, j], [2.5, 97.5])
        out[nm] = round(float(obs[j]), 4)
        out[f"{nm}_ci95"] = [round(float(lo), 4), round(float(hi), 4)]
    return out


def decide_verdict(summary_vina: Dict[str, object], summary_vinardo: Dict[str, object]) -> Dict[str, object]:
    """Evaluate the pre-registered verdict rule from protocol.md Section 7."""
    t1 = summary_vina["targets_best"]["tubulin_1jff"]
    t2 = summary_vina["targets_best"]["tubulin_4i4t"]
    t1_vdo = summary_vinardo["targets_best"]["tubulin_1jff"]
    comps = summary_vina["paired_vs_tubulin_1jff_best"]

    pot_1jff = (t1["rho_pot"] > 0) and (t1["p_rho_pot"] < 0.05)
    pot_4i4t = (t2["rho_pot"] > 0) and (t2["p_rho_pot"] < 0.05)
    pot_vdo = (t1_vdo["rho_pot"] > 0) and (t1_vdo["p_rho_pot"] < 0.05)

    rej_1jff = ((t1["auc_sep"] > 0.65) and (t1["p_auc_sep"] < 0.05)) or ((t1["r_non_oil"] < 0) and (t1["p_non_oil"] < 0.05))
    rej_4i4t = ((t2["auc_sep"] > 0.65) and (t2["p_auc_sep"] < 0.05)) or ((t2["r_non_oil"] < 0) and (t2["p_non_oil"] < 0.05))

    controls = ["hsa_1e7b", "luciferase_1ba3", "lysozyme_1dpx", "ubiquitin_1ubq"]
    rivals = ["gabaa_6x3t", "glic_3p4w"]

    beats_all_controls = all(
        (comps[c]["delta_rho_pot_ci95"][0] > 0.0) or (comps[c]["delta_auc_sep_ci95"][0] > 0.0)
        for c in controls
    )
    matches_or_beats_rivals = all(
        (comps[r]["delta_rho_pot_ci95"][1] >= 0.0) and (comps[r]["delta_auc_sep_ci95"][1] >= 0.0)
        for r in rivals
    )
    fails_non_imm_1jff = (t1["auc_sep"] <= 0.55) and ((t1["r_non_oil"] >= 0.0) or (t1["p_non_oil"] >= 0.05))

    if pot_1jff and pot_4i4t and rej_1jff and rej_4i4t and beats_all_controls and matches_or_beats_rivals:
        code = "tubulin_selective"
        reason = "Tubulin tracks potency, rejects non-immobilizers, and beats all non-conscious and negative controls."
    elif (not pot_1jff) and fails_non_imm_1jff:
        code = "no_potency_or_selectivity"
        reason = "Tubulin docking fails to track clinical/experimental anaesthetic potency and fails to reject non-immobilizers."
    elif pot_1jff and ((not beats_all_controls) or fails_non_imm_1jff):
        if pot_1jff != pot_4i4t or pot_1jff != pot_vdo:
            code = "mixed_or_scoring_dependent"
            reason = "Potency tracking splits across tubulin structures (1JFF vs 4I4T) or scoring functions (vina vs vinardo)."
        else:
            code = "generic_hydrophobic_binding"
            reason = "Predicted binding on tubulin tracks potency no better than non-conscious/negative control proteins and/or fails to reject non-immobilizers."
    else:
        code = "mixed_or_scoring_dependent"
        reason = "Results split across potency tracking, non-immobilizer separation, structure replication, or scoring functions."

    return {
        "verdict_code": code,
        "reason": reason,
        "checks": {
            "pot_1jff_vina": pot_1jff,
            "pot_4i4t_vina": pot_4i4t,
            "pot_1jff_vinardo": pot_vdo,
            "rej_1jff_vina": rej_1jff,
            "rej_4i4t_vina": rej_4i4t,
            "beats_all_4_controls": beats_all_controls,
            "matches_or_beats_rivals": matches_or_beats_rivals,
        },
    }


def check_inputs() -> None:
    print("Checking PDB inputs and SMILES...")
    seen_pdbs = sorted({s.pdb_id for s in SITES})
    for pdb in seen_pdbs:
        p = PDB_DIR / f"{pdb}.pdb"
        if not p.exists():
            raise FileNotFoundError(f"Missing PDB file: {p}")
        h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        print(f"  OK {pdb}.pdb ({p.stat().st_size} bytes, sha256={h}...)")
    assert len(MOLECULES) == 35, f"Expected 35 molecules, got {len(MOLECULES)}"
    assert sum(1 for m in MOLECULES if m.mol_class == "anaesthetic") == 27
    assert sum(1 for m in MOLECULES if m.mol_class == "non_immobilizer") == 7
    assert sum(1 for m in MOLECULES if m.mol_class == "convulsant") == 1
    assert len(SITES) == 24
    print(f"  OK {len(MOLECULES)} molecules (27 anaesthetics, 7 non-immobilizers, 1 convulsant), {len(SITES)} fixed sites across {len(TARGET_ORDER)} proteins.")


def run_full_analysis(cpu: int = 2, max_new_pockets: Optional[int] = None) -> None:
    check_inputs()
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rec_dir = WORK_DIR / "receptors"
    lig_dir = WORK_DIR / "ligands"
    rec_dir.mkdir(exist_ok=True)
    lig_dir.mkdir(exist_ok=True)

    t_start = time.time()
    print("[1/4] Preparing deterministic 3D ligand PDBQTs with Open Babel 3.1.1...", flush=True)
    lig_paths: List[Path] = []
    for mol in MOLECULES:
        lp = lig_dir / f"{mol.mol_id}.pdbqt"
        if not lp.exists():
            lp = prep_ligand(mol, lig_dir)
        lig_paths.append(lp)
    print(f"  Ready: {len(lig_paths)} ligands ({time.time() - t_start:.1f}s).", flush=True)

    print("[2/4] Preparing clean receptor PDBQTs for 8 proteins...", flush=True)
    rec_paths: Dict[str, Path] = {}
    clean_pdbs: Dict[str, Path] = {}
    for tid in TARGET_ORDER:
        site0 = next(s for s in SITES if s.target_id == tid)
        pdb_in = PDB_DIR / f"{site0.pdb_id}.pdb"
        rec_out = rec_dir / f"{tid}.pdbqt"
        clean_p = rec_out.with_suffix(".clean.pdb")
        if not (rec_out.exists() and clean_p.exists()):
            clean_p = prep_receptor(pdb_in, site0.chains, rec_out)
        rec_paths[tid] = rec_out
        clean_pdbs[tid] = clean_p
    print(f"  Ready: {len(rec_paths)} receptors ({time.time() - t_start:.1f}s total).", flush=True)

    print(f"[3/4] Running AutoDock Vina v1.2.5 batch docking ({len(SITES)} pockets × {len(MOLECULES)} ligands × {len(SCORING_FUNCTIONS)} scoring functions)...", flush=True)
    # raw_scores[scoring][target_id][site_id][mol_id] = dG (kcal/mol)
    raw_scores: Dict[str, Dict[str, Dict[str, Dict[str, float]]]] = {sf: {} for sf in SCORING_FUNCTIONS}
    # Save representative 3D docked poses on primary single pocket of each target (vina)
    pose_ligands = {"methoxyflurane", "halothane", "isoflurane", "o_xylene", "desflurane", "F6", "TFMB", "cyclooctane"}
    poses_3d: Dict[str, object] = {"targets": {}}

    new_pockets_done = 0
    for idx, site in enumerate(SITES, 1):
        site_had_new = False
        for sf in SCORING_FUNCTIONS:
            t0 = time.time()
            out_dir = WORK_DIR / "out" / sf / f"{site.target_id}__{site.site_id}"
            was_cached = all(
                (out_dir / f"{lp.stem}_out.pdbqt").exists() or (out_dir / f"{lp.stem}.pdbqt").exists()
                for lp in lig_paths
            )
            if not was_cached:
                site_had_new = True
            parsed = run_batch_docking(rec_paths[site.target_id], lig_paths, site, sf, out_dir, cpu=cpu)
            raw_scores[sf].setdefault(site.target_id, {})[site.site_id] = {m: parsed[m][0] for m in parsed}
            if sf == "vina" and site.is_primary_single:
                pocket_res = extract_pocket_context(clean_pdbs[site.target_id], site.center, radius=8.5)
                poses_3d["targets"][site.target_id] = {
                    "label": site.target_label,
                    "pdb_id": site.pdb_id,
                    "role": site.role,
                    "site_id": site.site_id,
                    "center": list(site.center),
                    "pocket_residues": pocket_res,
                    "ligands": {
                        mid: {"dG": parsed[mid][0], "atoms": parsed[mid][1]}
                        for mid in sorted(pose_ligands)
                    },
                }
            tag = "cached" if was_cached else f"{time.time() - t0:5.1f}s"
            print(f"  [{idx:2d}/{len(SITES)}] {site.target_id:16s} {site.site_id:14s} [{sf:7s}] {tag}", flush=True)
        if site_had_new:
            new_pockets_done += 1
            if max_new_pockets is not None and new_pockets_done >= max_new_pockets and idx < len(SITES):
                print(f"Chunk checkpoint reached ({idx}/{len(SITES)} pockets completed). Re-run to continue.", flush=True)
                return

    # Export full affinity matrix TSV
    tsv_path = RESULTS_DIR / "affinities.tsv"
    with open(tsv_path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["scoring", "target_id", "pdb_id", "role", "site_id", "is_primary_single", "mol_id", "mol_class", "subset", "mac_atm", "oil_gas", "n_heavy", "mw", "xlogp", "dG_kcal_mol", "B_neg_dG"])
        for sf in SCORING_FUNCTIONS:
            for site in SITES:
                for mol in MOLECULES:
                    dg = raw_scores[sf][site.target_id][site.site_id][mol.mol_id]
                    w.writerow([
                        sf, site.target_id, site.pdb_id, site.role, site.site_id, int(site.is_primary_single),
                        mol.mol_id, mol.mol_class, mol.subset,
                        "" if mol.mac_atm is None else f"{mol.mac_atm}",
                        "" if mol.oil_gas is None else f"{mol.oil_gas}",
                        mol.n_heavy, mol.mw, mol.xlogp, f"{dg:.3f}", f"{-dg:.3f}",
                    ])

    with open(RESULTS_DIR / "poses_3d.json", "w") as f:
        json.dump(poses_3d, f)

    print("[4/4] Computing locked statistics, partial correlations, non-immobilizer residuals, and paired bootstraps...")
    rng = np.random.default_rng(SEED)
    summary: Dict[str, object] = {
        "meta": {
            "seed": SEED,
            "box_size_A": BOX_SIZE,
            "exhaustiveness": EXHAUSTIVENESS,
            "n_perm": N_PERM,
            "n_boot": N_BOOT,
            "rt_310k": round(RT_310K, 6),
            "vina_version": subprocess.check_output(["vina", "--version"], text=True).strip(),
            "obabel_version": subprocess.check_output(["obabel", "-V"], text=True).strip(),
            "elapsed_sec": round(time.time() - t_start, 2),
        },
        "molecules": [asdict(m) for m in MOLECULES],
        "target_meta": {
            tid: {
                "label": next(s.target_label for s in SITES if s.target_id == tid),
                "pdb_id": next(s.pdb_id for s in SITES if s.target_id == tid),
                "role": next(s.role for s in SITES if s.target_id == tid),
                "n_sites": sum(1 for s in SITES if s.target_id == tid),
                "primary_single_site": next(s.site_id for s in SITES if s.target_id == tid and s.is_primary_single),
            }
            for tid in TARGET_ORDER
        },
        "scoring": {},
    }

    for sf in SCORING_FUNCTIONS:
        sf_out: Dict[str, object] = {
            "targets_best": {},
            "targets_single": {},
            "targets_boltzmann": {},
            "targets_best_clinical": {},
            "targets_best_fang1996": {},
            "per_site": {},
            "b_best_matrix": {},
            "b_single_matrix": {},
            "paired_vs_tubulin_1jff_best": {},
            "paired_vs_tubulin_1jff_single": {},
            "paired_vs_tubulin_4i4t_best": {},
        }

        b_best_all: Dict[str, Dict[str, float]] = {}
        b_single_all: Dict[str, Dict[str, float]] = {}
        b_ens_all: Dict[str, Dict[str, float]] = {}

        for tid in TARGET_ORDER:
            site_dict = raw_scores[sf][tid]
            prim_site = next(s.site_id for s in SITES if s.target_id == tid and s.is_primary_single)
            b_best_all[tid] = {m.mol_id: round(max(-site_dict[sid][m.mol_id] for sid in site_dict), 4) for m in MOLECULES}
            b_single_all[tid] = {m.mol_id: round(-site_dict[prim_site][m.mol_id], 4) for m in MOLECULES}
            b_ens_all[tid] = {m.mol_id: round(boltzmann_affinity([site_dict[sid][m.mol_id] for sid in site_dict]), 4) for m in MOLECULES}

            sf_out["b_best_matrix"][tid] = b_best_all[tid]
            sf_out["b_single_matrix"][tid] = b_single_all[tid]
            sf_out["targets_best"][tid] = evaluate_target_vector(b_best_all[tid], MOLECULES, rng)
            sf_out["targets_single"][tid] = evaluate_target_vector(b_single_all[tid], MOLECULES, rng)
            sf_out["targets_boltzmann"][tid] = evaluate_target_vector(b_ens_all[tid], MOLECULES, rng)
            sf_out["targets_best_clinical"][tid] = evaluate_target_vector(b_best_all[tid], MOLECULES, rng, subset_filter="clinical")
            sf_out["targets_best_fang1996"][tid] = evaluate_target_vector(b_best_all[tid], MOLECULES, rng, subset_filter="fang1996")

            sf_out["per_site"][tid] = {}
            for sid in site_dict:
                b_site = {m.mol_id: -site_dict[sid][m.mol_id] for m in MOLECULES}
                sf_out["per_site"][tid][sid] = evaluate_target_vector(b_site, MOLECULES, rng)

        for tid in TARGET_ORDER:
            if tid != "tubulin_1jff":
                sf_out["paired_vs_tubulin_1jff_best"][tid] = paired_target_comparison(b_best_all["tubulin_1jff"], b_best_all[tid], MOLECULES, rng)
                sf_out["paired_vs_tubulin_1jff_single"][tid] = paired_target_comparison(b_single_all["tubulin_1jff"], b_single_all[tid], MOLECULES, rng)
            if tid != "tubulin_4i4t":
                sf_out["paired_vs_tubulin_4i4t_best"][tid] = paired_target_comparison(b_best_all["tubulin_4i4t"], b_best_all[tid], MOLECULES, rng)

        summary["scoring"][sf] = sf_out

    # Diagnostic comparison with Craddock et al. (2017) Table S2 MOE scores on 1JFF
    crad_best_b: Dict[str, float] = {}
    for mid, sdict in CRADDOCK_2017_MOE_KJ.items():
        vals = [v for v in sdict.values() if v is not None]
        crad_best_b[mid] = round(max(-v / 4.184 for v in vals), 4)
    crad_anaes = [m for m in MOLECULES if m.mol_id in crad_best_b and m.mol_class == "anaesthetic"]
    crad_non = [m for m in MOLECULES if m.mol_id in crad_best_b and m.mol_class == "non_immobilizer"]
    c_b_an = np.array([crad_best_b[m.mol_id] for m in crad_anaes])
    c_p_an = np.array([-math.log10(m.mac_atm) for m in crad_anaes])
    c_b_non = np.array([crad_best_b[m.mol_id] for m in crad_non])
    vina_1jff_crad = np.array([summary["scoring"]["vina"]["b_best_matrix"]["tubulin_1jff"][m.mol_id] for m in crad_anaes + crad_non])
    moe_crad_all = np.array([crad_best_b[m.mol_id] for m in crad_anaes + crad_non])
    summary["craddock2017_moe_comparison"] = {
        "n_anaesthetics": len(crad_anaes),
        "n_non_immobilizers": len(crad_non),
        "moe_best_kcal": crad_best_b,
        "moe_rho_pot_8_anaes": round(spearman_rho(c_b_an, c_p_an), 4),
        "moe_auc_sep_8_vs_2": round(roc_auc_pos_vs_neg(c_b_an, c_b_non), 4),
        "vina_vs_moe_spearman_10_mols": round(spearman_rho(vina_1jff_crad, moe_crad_all), 4),
    }

    summary["verdict"] = decide_verdict(summary["scoring"]["vina"], summary["scoring"]["vinardo"])

    with open(RESULTS_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n=== LOCKED SUMMARY (VINA, BEST-POCKET, N=27 ANAESTHETICS / 7 NON-IMMOBILIZERS) ===")
    for tid in TARGET_ORDER:
        m = summary["scoring"]["vina"]["targets_best"][tid]
        print(
            f"  {tid:16s} | rho_pot={m['rho_pot']:+.3f} (p={m['p_rho_pot']:.4f}) | "
            f"part_hvy={m['rho_partial_heavy']:+.3f} | part_oil={m['rho_partial_oil']:+.3f} | "
            f"AUC_sep={m['auc_sep']:.3f} (p={m['p_auc_sep']:.4f}) | r_non_oil={m['r_non_oil']:+.3f} (p={m['p_non_oil']:.4f})"
        )
    print(f"VERDICT: {summary['verdict']['verdict_code']} — {summary['verdict']['reason']}")
    print(f"Done in {time.time() - t_start:.1f}s. Wrote {tsv_path} and {RESULTS_DIR / 'summary.json'}.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Locked docking analysis for Issue #48 (anaesthetics-microtubules)")
    ap.add_argument("--check-inputs", action="store_true", help="Verify PDB files and protocol tables without docking")
    ap.add_argument("--cpu", type=int, default=2, help="CPU threads per AutoDock Vina call")
    ap.add_argument("--max-new-pockets", type=int, default=None, help="Checkpoint after running N uncached pockets")
    args = ap.parse_args()
    if args.check_inputs:
        check_inputs()
    else:
        run_full_analysis(cpu=args.cpu, max_new_pockets=args.max_new_pockets)


if __name__ == "__main__":
    main()
