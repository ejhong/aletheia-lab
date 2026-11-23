#!/usr/bin/env python3
"""
Pre-registered collective aromatic dipole-oscillation solver for Issue #115
(`anaesthetics-terahertz`).

Implements:
  - Model A: Exact Kurian (2018) / Craddock (2017) N x N coupled scalar dipole
    Hamiltonian using Kurian Table III aromatic polarizabilities and Fig. 4 ring axes.
  - Model A_phys: Same N x N formalism with physical plane-aligned Tyr tensor
    (out-of-plane 43.0 a.u. on ring normal z).
  - Model B: Rotationally invariant 3N x 3N full 3D tensor coupled Drude oscillator
    Hamiltonian (exact dipole-dipole tensor T_ij = (I - 3 r_hat r_hat^T) / r^3).
  - Thole (1981) / van Duijnen & Swart (1998) Table 5 exponential-damped interacting
    atomic dipole polarizability tensors for all 35 volatile ligands in their exact
    docked 3D orientations from Issue #48 (plus exact Craddock Table S1 calibration
    check on the 11 reference gases).

Usage:
  python3 questions/anaesthetics-terahertz/analysis/terahertz_modes.py
"""
from __future__ import annotations

import csv
import json
import math
import pathlib
import subprocess
import time
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial.transform import Rotation
from scipy.stats import rankdata

# ---------------------------------------------------------------------------
# Paths & Constants
# ---------------------------------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
Q48 = REPO / "questions" / "anaesthetics-microtubules"
PDB_DIR = Q48 / "data" / "pdb"
DOCK_OUT_DIR = Q48 / "data" / "dock_work" / "out"
Q48_SUMMARY = Q48 / "results" / "summary.json"
RESULTS_DIR = ROOT / "results"

SEED = 20261123
N_PERM = 10000
N_BOOT = 5000
N_SO3 = 20

# CODATA 2018 physical constants
E_CHG = 1.602176634e-19
M_E = 9.1093837015e-31
EPS0 = 8.8541878128e-12
BOHR_ANG = 0.529177210903
AU_TO_ANG3 = BOHR_ANG ** 3
AU_POL_SI = 1.64877727436e-41  # 4 * pi * eps0 * a0^3  [C^2 m^2 / J]
ANG_TO_M = 1e-10
PREF_DIP = (E_CHG ** 2) / (4.0 * math.pi * EPS0 * M_E)  # [m^3 / s^2]
PREF_DIAG = (E_CHG ** 2) / (M_E * AU_POL_SI)            # [a.u. * (rad/s)^2]

BAND_LO_THZ = 605.0  # 613 - 8 THz (Craddock et al. 2017 Fig. 4)
BAND_HI_THZ = 621.0  # 613 + 8 THz

# Kurian et al. (2018) Table III polarizability tensors in a.u.
AROM_ALPHA_KURIAN = {
    "TRP": np.array([119.5, 91.6, 29.4], dtype=float),
    "TYR": np.array([89.5, 43.0, 82.9], dtype=float),
    "PHE": np.array([79.0, 79.0, 38.6], dtype=float),
}
AROM_ALPHA_PHYS = {
    "TRP": np.array([119.5, 91.6, 29.4], dtype=float),
    "TYR": np.array([89.5, 82.9, 43.0], dtype=float),
    "PHE": np.array([79.0, 79.0, 38.6], dtype=float),
}

# van Duijnen & Swart (1998) J. Phys. Chem. A 102:2399, Table 5 ("exp" model, a = 2.089)
THOLE_A = 2.089
THOLE_ALPHA_AU = {
    "H": 2.7927,
    "C": 8.6959,
    "N": 6.5406,
    "O": 5.7494,
    "F": 3.0013,
    "Cl": 16.1979,
    "Br": 23.5714,
}

# Craddock et al. (2017) Table S1 CAM-B3LYP/PolX mean polarizabilities (in Angstrom^3)
CRADDOCK_S1_ALPHA_A3 = {
    "nitrous_oxide": 2.86,
    "desflurane": 7.22,
    "diethyl_ether": 8.45,
    "flurothyl": 8.83,
    "sevoflurane": 8.95,
    "enflurane": 9.04,
    "isoflurane": 9.10,
    "halothane": 9.38,
    "methoxyflurane": 10.70,
    "F6": 11.50,
    "TFMB": 16.37,
}
CRADDOCK_ORIG_ANAES = [
    "desflurane", "diethyl_ether", "enflurane", "halothane",
    "isoflurane", "methoxyflurane", "nitrous_oxide", "sevoflurane",
]
CRADDOCK_ORIG_NON = ["F6", "TFMB"]

TARGETS = [
    {
        "target_id": "tubulin_1jff",
        "label": "Tubulin (1JFF)",
        "pdb_id": "1JFF",
        "chains": {"A", "B"},
        "role": "test_primary",
        "pockets": ["site_1", "site_4", "site_5", "site_7", "site_21", "site_23", "site_37", "site_38"],
    },
    {
        "target_id": "tubulin_4i4t",
        "label": "Tubulin (4I4T, 1.8 Å)",
        "pdb_id": "4I4T",
        "chains": {"A", "B"},
        "role": "test_replication",
        "pockets": ["site_1", "site_4", "site_5", "site_7", "site_21", "site_23", "site_37", "site_38"],
    },
    {
        "target_id": "gabaa_6x3t",
        "label": "GABA_A (6X3T)",
        "pdb_id": "6X3T",
        "chains": {"A", "B", "C", "D", "E"},
        "role": "rival_channel",
        "pockets": ["site_B601", "site_D601"],
    },
    {
        "target_id": "glic_3p4w",
        "label": "GLIC (3P4W)",
        "pdb_id": "3P4W",
        "chains": {"A", "B", "C", "D", "E"},
        "role": "rival_channel",
        "pockets": ["site_A319"],
    },
    {
        "target_id": "hsa_1e7b",
        "label": "Albumin (1E7B)",
        "pdb_id": "1E7B",
        "chains": {"A"},
        "role": "positive_control",
        "pockets": ["site_4001_4002", "site_4003"],
    },
    {
        "target_id": "luciferase_1ba3",
        "label": "Luciferase (1BA3)",
        "pdb_id": "1BA3",
        "chains": {"A"},
        "role": "positive_control",
        "pockets": ["site_991"],
    },
    {
        "target_id": "lysozyme_1dpx",
        "label": "Lysozyme (1DPX)",
        "pdb_id": "1DPX",
        "chains": {"A"},
        "role": "negative_control",
        "pockets": ["site_cleft"],
    },
    {
        "target_id": "ubiquitin_1ubq",
        "label": "Ubiquitin (1UBQ)",
        "pdb_id": "1UBQ",
        "chains": {"A"},
        "role": "negative_control",
        "pockets": ["site_patch"],
    },
]


# ---------------------------------------------------------------------------
# Molecular Polarizability (Thole / van Duijnen & Swart 1998)
# ---------------------------------------------------------------------------
def thole_polarizability_tensor(coords_ang: np.ndarray, elems: List[str]) -> np.ndarray:
    """Compute exact 3x3 molecular polarizability tensor in a.u. (Bohr^3)."""
    n = len(elems)
    R = np.asarray(coords_ang, dtype=float) / BOHR_ANG
    alphas = np.array([THOLE_ALPHA_AU[e] for e in elems], dtype=float)
    A = np.zeros((3 * n, 3 * n), dtype=float)
    for i in range(n):
        A[3 * i:3 * i + 3, 3 * i:3 * i + 3] = np.eye(3) / alphas[i]
    for i in range(n):
        for j in range(i + 1, n):
            rij = R[j] - R[i]
            d = float(np.linalg.norm(rij))
            if d < 1e-6:
                continue
            s = (alphas[i] * alphas[j]) ** (1.0 / 6.0)
            au = THOLE_A * (d / s)
            e_au = math.exp(-au)
            fe = 1.0 - (0.5 * au * au + au + 1.0) * e_au
            ft = fe - (au ** 3 / 6.0) * e_au
            rhat = rij / d
            T = (fe * np.eye(3) - 3.0 * ft * np.outer(rhat, rhat)) / (d ** 3)
            A[3 * i:3 * i + 3, 3 * j:3 * j + 3] = T
            A[3 * j:3 * j + 3, 3 * i:3 * i + 3] = T
    B = np.linalg.inv(A)
    # Sum over all 3x3 blocks
    B_blocks = B.reshape(n, 3, n, 3)
    pol = B_blocks.sum(axis=(0, 2))
    return 0.5 * (pol + pol.T)


def smiles_expected_formula(smiles: str) -> Dict[str, int]:
    xyz = subprocess.check_output(
        ["obabel", f"-:{smiles}", "-oxyz", "--gen3d"],
        stderr=subprocess.DEVNULL, text=True,
    )
    elems = [ln.split()[0] for ln in xyz.splitlines()[2:] if len(ln.split()) == 4]
    return {e: elems.count(e) for e in sorted(set(elems))}


def pdbqt_model1_all_atom(pdbqt_path: pathlib.Path, expected_formula: Dict[str, int]) -> Tuple[List[str], np.ndarray]:
    """Read MODEL 1 heavy atoms from docked PDBQT, reconstruct H if needed, assert exact formula."""
    pdb_lines = []
    idx = 1
    for ln in pdbqt_path.read_text().splitlines():
        if ln.startswith("ENDMDL"):
            break
        if ln.startswith(("ATOM  ", "HETATM")):
            x = float(ln[30:38]); y = float(ln[38:46]); z = float(ln[46:54])
            ad = ln[77:79].strip()
            if ad in ("Cl", "CL", "Br", "BR"):
                elem = ad.capitalize()
            elif ad in ("A", "C"):
                elem = "C"
            elif ad in ("OA", "O"):
                elem = "O"
            elif ad in ("NA", "NS", "N"):
                elem = "N"
            elif ad == "F":
                elem = "F"
            elif ad in ("H", "HD"):
                elem = "H"
            else:
                elem = "".join(c for c in ln[12:16] if c.isalpha())[:2].capitalize()
            pdb_lines.append(
                f"HETATM{idx:5d} {elem:<4s} LIG A   1    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00          {elem:>2s}"
            )
            idx += 1
    pdb_lines.append("END")
    expect_h = expected_formula.get("H", 0)
    cmd = ["obabel", "-ipdb", "-oxyz"] + (["-h"] if expect_h > 0 else [])
    xyz = subprocess.check_output(
        cmd, input="\n".join(pdb_lines) + "\n", stderr=subprocess.DEVNULL, text=True
    )
    elems, coords = [], []
    for ln in xyz.splitlines()[2:]:
        p = ln.split()
        if len(p) == 4:
            elems.append(p[0])
            coords.append([float(p[1]), float(p[2]), float(p[3])])
    got = {e: elems.count(e) for e in sorted(set(elems))}
    if got != expected_formula:
        raise ValueError(f"Formula mismatch on {pdbqt_path}: got {got}, expected {expected_formula}")
    return elems, np.asarray(coords, dtype=float)


# ---------------------------------------------------------------------------
# Aromatic Ring Extraction & Synthetic Shuffled Control
# ---------------------------------------------------------------------------
def extract_aromatics(pdb_path: pathlib.Path, chains: set) -> List[Dict]:
    residues: Dict[Tuple[str, str, str], Dict[str, np.ndarray]] = {}
    for ln in pdb_path.read_text().splitlines():
        if ln.startswith("ATOM  "):
            res = ln[17:20].strip()
            ch = ln[21]
            if ch not in chains or res not in ("TRP", "TYR", "PHE"):
                continue
            alt = ln[16]
            if alt not in (" ", "A"):
                continue
            rnum = ln[22:26].strip()
            aname = ln[12:16].strip()
            xyz = np.array([float(ln[30:38]), float(ln[38:46]), float(ln[46:54])], dtype=float)
            residues.setdefault((ch, rnum, res), {})[aname] = xyz
    out = []
    for (ch, rnum, res), atoms in sorted(residues.items(), key=lambda kv: (kv[0][0], int(kv[0][1]))):
        if res == "TRP":
            req = ("CD2", "CE2", "NE1", "CZ2", "CG")
            if not all(k in atoms for k in req):
                continue
            center = 0.5 * (atoms["CD2"] + atoms["CE2"])
            vx = atoms["NE1"] - center
            vx /= np.linalg.norm(vx)
            vy_tmp = atoms["CZ2"] - atoms["CG"]
            vz = np.cross(vx, vy_tmp); vz /= np.linalg.norm(vz)
            vy = np.cross(vz, vx)
            R = np.column_stack([vx, vy, vz])
        elif res == "TYR":
            req = ("CG", "CD1", "CD2", "CE1", "CE2", "CZ")
            if not all(k in atoms for k in req):
                continue
            center = np.mean([atoms[k] for k in req], axis=0)
            vy = atoms["CG"] - atoms["CZ"]; vy /= np.linalg.norm(vy)
            vx_tmp = (atoms["CD1"] + atoms["CE1"]) - (atoms["CD2"] + atoms["CE2"])
            vz = np.cross(vx_tmp, vy); vz /= np.linalg.norm(vz)
            vx = np.cross(vy, vz)
            R = np.column_stack([vx, vy, vz])
        else:
            req = ("CG", "CD1", "CD2", "CE1", "CE2", "CZ")
            if not all(k in atoms for k in req):
                continue
            center = np.mean([atoms[k] for k in req], axis=0)
            vy = atoms["CZ"] - atoms["CG"]; vy /= np.linalg.norm(vy)
            vx_tmp = (atoms["CD2"] + atoms["CE2"]) - (atoms["CD1"] + atoms["CE1"])
            vz = np.cross(vx_tmp, vy); vz /= np.linalg.norm(vz)
            vx = np.cross(vy, vz)
            R = np.column_stack([vx, vy, vz])
        out.append({"id": f"{ch}:{rnum}:{res}", "res": res, "center": center, "R": R})
    return out


def make_shuffled_tubulin(aroms_1jff: List[Dict], seed: int = SEED) -> Tuple[List[Dict], List[np.ndarray]]:
    """Create 81 random aromatic dipoles inside 1JFF's ellipsoid with min spacing >= 4.5 A + 8 random pockets."""
    rng = np.random.default_rng(seed)
    pts = np.array([a["center"] for a in aroms_1jff])
    mu = pts.mean(axis=0)
    radii = pts.std(axis=0) * 1.9
    placed: List[np.ndarray] = []
    res_types = [a["res"] for a in aroms_1jff]
    nodes = []
    for idx, res in enumerate(res_types):
        while True:
            # Uniform inside unit ball
            u = rng.normal(size=3)
            u /= np.linalg.norm(u)
            r = rng.uniform(0.0, 1.0) ** (1.0 / 3.0)
            pos = mu + r * u * radii
            if all(np.linalg.norm(pos - q) >= 4.5 for q in placed):
                placed.append(pos)
                break
        R = Rotation.random(random_state=rng).as_matrix()
        nodes.append({"id": f"SHUF:{idx+1}:{res}", "res": res, "center": pos, "R": R})
    # 8 random pockets placed 4.5-7.5 A from randomly selected aromatic rings (with >= 4.2 A clearance from all rings)
    pockets = []
    for k in range(8):
        while True:
            anchor = placed[int(rng.integers(0, len(placed)))]
            dvec = rng.normal(size=3); dvec /= np.linalg.norm(dvec)
            dist = float(rng.uniform(4.8, 7.2))
            ppos = anchor + dist * dvec
            if all(np.linalg.norm(ppos - q) >= 4.2 for q in placed):
                pockets.append(ppos)
                break
    return nodes, pockets


# ---------------------------------------------------------------------------
# Dipole Hamiltonians & Exact Eigenvector-Overlap Mode Matching
# ---------------------------------------------------------------------------
def build_matrix_model_a(nodes: List[Dict], use_kurian_tyr: bool = True) -> np.ndarray:
    """Exact Kurian (2018) / Craddock (2017) N x N matrix M = V / m_e in (rad/s)^2."""
    n = len(nodes)
    M = np.zeros((n, n), dtype=float)
    u_vecs = np.zeros((n, 3), dtype=float)
    centers = np.zeros((n, 3), dtype=float)
    alpha_table = AROM_ALPHA_KURIAN if use_kurian_tyr else AROM_ALPHA_PHYS
    for i, nd in enumerate(nodes):
        if "alpha_lab" in nd:
            A_lab = nd["alpha_lab"]
        else:
            A_lab = nd["R"] @ np.diag(alpha_table[nd["res"]]) @ nd["R"].T
        d_vec = np.diag(A_lab)
        a_bar = float(np.linalg.norm(d_vec))
        u_vecs[i] = d_vec / a_bar
        centers[i] = nd["center"]
        M[i, i] = PREF_DIAG / a_bar
    # Vectorized pairwise dipole-dipole coupling
    diff = (centers[None, :, :] - centers[:, None, :]) * ANG_TO_M  # (n, n, 3)
    dist = np.linalg.norm(diff, axis=2)
    np.fill_diagonal(dist, 1.0)
    rhat = diff / dist[:, :, None]
    u_dot_u = u_vecs @ u_vecs.T
    u_dot_r_i = np.einsum("ik,ijk->ij", u_vecs, rhat)
    u_dot_r_j = np.einsum("jk,ijk->ij", u_vecs, rhat)
    kappa = u_dot_u - 3.0 * u_dot_r_i * u_dot_r_j
    off = PREF_DIP * kappa / (dist ** 3)
    np.fill_diagonal(off, 0.0)
    M += off
    return 0.5 * (M + M.T)


def build_matrix_model_b(nodes: List[Dict]) -> np.ndarray:
    """Rotationally invariant full 3N x 3N coupled 3D Drude oscillator matrix M = V / m_e."""
    n = len(nodes)
    M = np.zeros((3 * n, 3 * n), dtype=float)
    centers = np.array([nd["center"] for nd in nodes], dtype=float) * ANG_TO_M
    for i, nd in enumerate(nodes):
        if "alpha_lab" in nd:
            A_lab = nd["alpha_lab"]
        else:
            A_lab = nd["R"] @ np.diag(AROM_ALPHA_PHYS[nd["res"]]) @ nd["R"].T
        M[3 * i:3 * i + 3, 3 * i:3 * i + 3] = PREF_DIAG * np.linalg.inv(A_lab)
    eye3 = np.eye(3)
    for i in range(n):
        for j in range(i + 1, n):
            rij = centers[j] - centers[i]
            d = float(np.linalg.norm(rij))
            rhat = rij / d
            T = PREF_DIP * (eye3 - 3.0 * np.outer(rhat, rhat)) / (d ** 3)
            M[3 * i:3 * i + 3, 3 * j:3 * j + 3] = T
            M[3 * j:3 * j + 3, 3 * i:3 * i + 3] = T
    return 0.5 * (M + M.T)


def eigh_freqs(M: np.ndarray) -> Tuple[np.ndarray, np.ndarray, int]:
    """Return sorted frequencies (THz), eigenvectors (columns), and count of non-positive eigenvalues."""
    w2, vecs = np.linalg.eigh(M)
    n_neg = int(np.sum(w2 <= 0.0))
    freqs_thz = np.sqrt(np.maximum(w2, 0.0)) / (2.0 * math.pi) / 1e12
    return freqs_thz, vecs, n_neg


def isolated_drude_freq_thz(alpha_lab: np.ndarray) -> Tuple[float, float]:
    """Return (Kurian a_bar norm in a.u., isolated Drude linear frequency in THz)."""
    d_vec = np.diag(alpha_lab)
    a_bar = float(np.linalg.norm(d_vec))
    f_thz = math.sqrt(PREF_DIAG / a_bar) / (2.0 * math.pi) / 1e12
    return a_bar, f_thz


def match_modes_and_shifts(
    f0: np.ndarray,
    U0: np.ndarray,
    f1: np.ndarray,
    U1: np.ndarray,
    n_lig_dof: int,
) -> Dict:
    """Identify ligand-dominated new mode(s) and match protein modes by max |<v0|v1_prot>|^2."""
    n_prot = len(f0)
    lig_weight = np.sum(U1[n_prot:, :] ** 2, axis=0)
    # Pick top n_lig_dof modes with largest ligand weight
    lig_idx = np.argsort(lig_weight)[-n_lig_dof:]
    lig_mask = np.zeros(len(f1), dtype=bool)
    lig_mask[lig_idx] = True
    prot_cols = np.where(~lig_mask)[0]
    f_new = np.sort(f1[lig_idx])

    # Overlap matrix between U0 (n_prot x n_prot) and U1[:n_prot, prot_cols] (n_prot x n_prot)
    S = (U0.T @ U1[:n_prot, prot_cols]) ** 2
    row_ind, col_ind = linear_sum_assignment(-S)
    matched_f1 = f1[prot_cols[col_ind]]
    shifts_ghz = (matched_f1 - f0) * 1000.0  # THz -> GHz

    # Band 613 +- 8 THz ([605, 621] THz)
    in_band = (f0 >= BAND_LO_THZ) & (f0 <= BAND_HI_THZ)
    if np.any(in_band):
        band_shifts = shifts_ghz[in_band]
        idx_abs = int(np.argmax(np.abs(band_shifts)))
        signed_613_ghz = float(band_shifts[idx_abs])     # negative = downward shift
        down_613_ghz = float(np.max(-band_shifts))        # largest downward shift
        d_613 = -signed_613_ghz                           # positive = downward shift
    else:
        signed_613_ghz = None
        down_613_ghz = None
        d_613 = None

    idx_all = int(np.argmax(np.abs(shifts_ghz)))
    signed_all_ghz = float(shifts_ghz[idx_all])
    d_all = -signed_all_ghz
    rms_ghz = float(np.sqrt(np.mean(shifts_ghz ** 2)))
    return {
        "f_new_thz": [float(x) for x in f_new],
        "d_613_ghz": d_613,
        "d_down_613_ghz": down_613_ghz,
        "d_all_ghz": d_all,
        "rms_ghz": rms_ghz,
        "shifts_ghz": shifts_ghz,
        "lig_weight_top": float(np.max(lig_weight)),
    }


def apply_so3_rotation(nodes: List[Dict], rot_mat: np.ndarray) -> List[Dict]:
    """Rigidly rotate all positions and local frames / tensors by rot_mat in SO(3)."""
    out = []
    for nd in nodes:
        nd2 = dict(nd)
        nd2["center"] = rot_mat @ nd["center"]
        if "R" in nd:
            nd2["R"] = rot_mat @ nd["R"]
        if "alpha_lab" in nd:
            nd2["alpha_lab"] = rot_mat @ nd["alpha_lab"] @ rot_mat.T
        out.append(nd2)
    return out


# ---------------------------------------------------------------------------
# Vectorized Statistical Functions (exact permutation & bootstrap tests)
# ---------------------------------------------------------------------------
def spearman_corr(x: np.ndarray, y: np.ndarray) -> float:
    rx = rankdata(x); ry = rankdata(y)
    rx -= rx.mean(); ry -= ry.mean()
    denom = float(np.linalg.norm(rx) * np.linalg.norm(ry))
    return float(np.dot(rx, ry) / denom) if denom > 0 else 0.0


def partial_spearman(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    rx = rankdata(x); ry = rankdata(y); rz = rankdata(z)
    rx = rx - rx.mean(); ry = ry - ry.mean(); rz = rz - rz.mean()
    zz = float(np.dot(rz, rz))
    if zz > 0:
        rx = rx - (np.dot(rx, rz) / zz) * rz
        ry = ry - (np.dot(ry, rz) / zz) * rz
    denom = float(np.linalg.norm(rx) * np.linalg.norm(ry))
    return float(np.dot(rx, ry) / denom) if denom > 0 else 0.0


def perm_test_spearman(x: np.ndarray, y: np.ndarray, n_perm: int, rng: np.random.Generator) -> Tuple[float, float]:
    obs = spearman_corr(x, y)
    rx = rankdata(x); rx = (rx - rx.mean())
    nx = np.linalg.norm(rx)
    ry = rankdata(y); ry = (ry - ry.mean())
    ny = np.linalg.norm(ry)
    if nx == 0 or ny == 0:
        return 0.0, 1.0
    rx /= nx; ry /= ny
    # Generate n_perm random permutations of ry
    idx = np.argsort(rng.random((n_perm, len(y))), axis=1)
    null_corrs = ry[idx] @ rx
    p = float((1 + np.sum(np.abs(null_corrs) >= abs(obs) - 1e-12)) / (n_perm + 1))
    return obs, p


def perm_test_partial_spearman(
    x: np.ndarray, y: np.ndarray, z: np.ndarray, n_perm: int, rng: np.random.Generator
) -> Tuple[float, float]:
    obs = partial_spearman(x, y, z)
    rx = rankdata(x); ry = rankdata(y); rz = rankdata(z)
    rx -= rx.mean(); ry -= ry.mean(); rz -= rz.mean()
    zz = float(np.dot(rz, rz))
    ex = rx - (np.dot(rx, rz) / zz) * rz if zz > 0 else rx
    ey = ry - (np.dot(ry, rz) / zz) * rz if zz > 0 else ry
    nx = np.linalg.norm(ex); ny = np.linalg.norm(ey)
    if nx == 0 or ny == 0:
        return 0.0, 1.0
    ex /= nx; ey /= ny
    idx = np.argsort(rng.random((n_perm, len(y))), axis=1)
    null_corrs = ey[idx] @ ex
    p = float((1 + np.sum(np.abs(null_corrs) >= abs(obs) - 1e-12)) / (n_perm + 1))
    return obs, p


def roc_auc(pos: np.ndarray, neg: np.ndarray) -> float:
    # Fraction of (pos_i > neg_j) + 0.5 * (pos_i == neg_j)
    diff = pos[:, None] - neg[None, :]
    return float(np.mean((diff > 0) + 0.5 * (diff == 0)))


def perm_test_auc(pos: np.ndarray, neg: np.ndarray, n_perm: int, rng: np.random.Generator) -> Tuple[float, float]:
    obs = roc_auc(pos, neg)
    pooled = np.concatenate([pos, neg])
    n_pos = len(pos); n_neg = len(neg); n_tot = len(pooled)
    ranks = rankdata(pooled)
    idx = np.argsort(rng.random((n_perm, n_tot)), axis=1)
    r_pos_sum = np.sum(ranks[idx[:, :n_pos]], axis=1)
    u_null = r_pos_sum - n_pos * (n_pos + 1) / 2.0
    auc_null = u_null / (n_pos * n_neg)
    p = float((1 + np.sum(np.abs(auc_null - 0.5) >= abs(obs - 0.5) - 1e-12)) / (n_perm + 1))
    return obs, p


def bootstrap_corr_ci(x: np.ndarray, y: np.ndarray, n_boot: int, rng: np.random.Generator) -> List[float]:
    n = len(x)
    idx = rng.integers(0, n, size=(n_boot, n))
    vals = np.array([spearman_corr(x[b], y[b]) for b in idx])
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def paired_bootstrap_compare(
    x_a: np.ndarray, x_b: np.ndarray, pot: np.ndarray,
    non_a: np.ndarray, non_b: np.ndarray,
    n_boot: int, rng: np.random.Generator,
) -> Dict:
    n_an = len(pot); n_no = len(non_a)
    d_rho_obs = spearman_corr(x_a, pot) - spearman_corr(x_b, pot)
    d_auc_obs = roc_auc(x_a, non_a) - roc_auc(x_b, non_b)
    b_an = rng.integers(0, n_an, size=(n_boot, n_an))
    b_no = rng.integers(0, n_no, size=(n_boot, n_no))
    d_rhos = np.empty(n_boot)
    d_aucs = np.empty(n_boot)
    for k in range(n_boot):
        ia = b_an[k]; ino = b_no[k]
        d_rhos[k] = spearman_corr(x_a[ia], pot[ia]) - spearman_corr(x_b[ia], pot[ia])
        d_aucs[k] = roc_auc(x_a[ia], non_a[ino]) - roc_auc(x_b[ia], non_b[ino])
    return {
        "delta_rho": round(float(d_rho_obs), 4),
        "delta_rho_ci95": [round(float(np.percentile(d_rhos, 2.5)), 4), round(float(np.percentile(d_rhos, 97.5)), 4)],
        "delta_auc": round(float(d_auc_obs), 4),
        "delta_auc_ci95": [round(float(np.percentile(d_aucs, 2.5)), 4), round(float(np.percentile(d_aucs, 97.5)), 4)],
    }


def residual_non_given_x(
    an_y: np.ndarray, an_x: np.ndarray, non_y: np.ndarray, non_x: np.ndarray, n_perm: int, rng: np.random.Generator
) -> Dict:
    # OLS fit of y ~ a + b*x on anaesthetics, evaluate mean residual of non-immobilizers
    X = np.column_stack([np.ones_like(an_x), an_x])
    beta, *_ = np.linalg.lstsq(X, an_y, rcond=None)
    res_an = an_y - (beta[0] + beta[1] * an_x)
    res_non = non_y - (beta[0] + beta[1] * non_x)
    obs = float(np.mean(res_non))
    pooled = np.concatenate([res_an, res_non])
    n_non = len(res_non)
    idx = np.argsort(rng.random((n_perm, len(pooled))), axis=1)
    null_means = np.mean(pooled[idx[:, :n_non]], axis=1)
    p = float((1 + np.sum(np.abs(null_means) >= abs(obs) - 1e-12)) / (n_perm + 1))
    return {"r_mean": round(obs, 3), "p": round(p, 5)}


# ---------------------------------------------------------------------------
# Main Runner
# ---------------------------------------------------------------------------
def evaluate_target_metrics(
    scores_by_mol: Dict[str, Optional[float]],
    mols: List[Dict],
    alpha_iso_by_mol: Dict[str, float],
    rng: np.random.Generator,
) -> Optional[Dict]:
    an_mols = [m for m in mols if m["mol_class"] == "anaesthetic"]
    no_mols = [m for m in mols if m["mol_class"] == "non_immobilizer"]
    if any(scores_by_mol[m["mol_id"]] is None for m in an_mols + no_mols):
        return None
    x_an = np.array([scores_by_mol[m["mol_id"]] for m in an_mols], dtype=float)
    x_no = np.array([scores_by_mol[m["mol_id"]] for m in no_mols], dtype=float)
    pot = np.array([-math.log10(m["mac_atm"]) for m in an_mols], dtype=float)
    alp_an = np.array([alpha_iso_by_mol[m["mol_id"]] for m in an_mols], dtype=float)
    alp_no = np.array([alpha_iso_by_mol[m["mol_id"]] for m in no_mols], dtype=float)
    oil_an = np.array([math.log10(m["oil_gas"]) for m in an_mols], dtype=float)

    rho_pot, p_pot = perm_test_spearman(x_an, pot, N_PERM, rng)
    ci_pot = bootstrap_corr_ci(x_an, pot, N_BOOT, rng)
    rho_palp, p_palp = perm_test_partial_spearman(x_an, pot, alp_an, N_PERM, rng)
    rho_poil, p_poil = perm_test_partial_spearman(x_an, pot, oil_an, N_PERM, rng)
    rho_alpha, _ = perm_test_spearman(x_an, alp_an, 1000, rng)
    auc, p_auc = perm_test_auc(x_an, x_no, N_PERM, rng)
    r_alp = residual_non_given_x(x_an, alp_an, x_no, alp_no, N_PERM, rng)

    # Subsets: clinical (n=9), fang1996 (n=18), craddock original (n=8 vs 2)
    clin_idx = [i for i, m in enumerate(an_mols) if m["subset"] == "clinical"]
    fang_idx = [i for i, m in enumerate(an_mols) if m["subset"] == "fang1996"]
    rho_clin, p_clin = perm_test_spearman(x_an[clin_idx], pot[clin_idx], N_PERM, rng)
    rho_fang, p_fang = perm_test_spearman(x_an[fang_idx], pot[fang_idx], N_PERM, rng)

    orig_an = np.array([scores_by_mol[mid] for mid in CRADDOCK_ORIG_ANAES], dtype=float)
    orig_pot = np.array([-math.log10(next(m["mac_atm"] for m in an_mols if m["mol_id"] == mid)) for mid in CRADDOCK_ORIG_ANAES], dtype=float)
    orig_no = np.array([scores_by_mol[mid] for mid in CRADDOCK_ORIG_NON], dtype=float)
    rho_orig, p_orig = perm_test_spearman(orig_an, orig_pot, N_PERM, rng)
    auc_orig = roc_auc(orig_an, orig_no)

    an_down_frac = float(np.mean(x_an > 0))
    no_up_frac = float(np.mean(x_no < 0))
    orig_an_down = int(np.sum(orig_an > 0))
    orig_no_up = int(np.sum(orig_no < 0))

    return {
        "median_anaes": round(float(np.median(x_an)), 3),
        "median_non": round(float(np.median(x_no)), 3),
        "rho_pot": round(rho_pot, 4),
        "p_rho_pot": round(p_pot, 5),
        "rho_pot_ci95": [round(ci_pot[0], 4), round(ci_pot[1], 4)],
        "rho_partial_alpha": round(rho_palp, 4),
        "p_partial_alpha": round(p_palp, 5),
        "rho_partial_oil": round(rho_poil, 4),
        "p_partial_oil": round(p_poil, 5),
        "diag_rho_alpha": round(rho_alpha, 4),
        "auc_sep": round(auc, 4),
        "p_auc_sep": round(p_auc, 5),
        "r_non_alpha": r_alp,
        "an_down_count": int(np.sum(x_an > 0)),
        "an_total": len(x_an),
        "an_down_frac": round(an_down_frac, 4),
        "no_up_count": int(np.sum(x_no < 0)),
        "no_total": len(x_no),
        "no_up_frac": round(no_up_frac, 4),
        "clinical_n9_rho": round(rho_clin, 4),
        "clinical_n9_p": round(p_clin, 5),
        "fang1996_n18_rho": round(rho_fang, 4),
        "fang1996_n18_p": round(p_fang, 5),
        "craddock_8v2": {
            "rho_pot": round(rho_orig, 4),
            "p_rho_pot": round(p_orig, 5),
            "auc_sep": round(auc_orig, 4),
            "an_down_count": orig_an_down,
            "no_up_count": orig_no_up,
        },
    }


def run_all() -> None:
    t0 = time.time()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    q48 = json.loads(Q48_SUMMARY.read_text())
    mols = q48["molecules"]
    mol_by_id = {m["mol_id"]: m for m in mols}

    print("1. Computing expected all-atom formulas & reference isolated polarizabilities...", flush=True)
    expected_formulas = {m["mol_id"]: smiles_expected_formula(m["smiles"]) for m in mols}

    # Build baseline aromatic networks for all 8 PDBs + 1JFF_shuffled
    print("2. Extracting aromatic networks for 8 PDB structures + 1JFF_shuffled...", flush=True)
    target_aroms: Dict[str, List[Dict]] = {}
    target_meta: Dict[str, Dict] = {}
    for t in TARGETS:
        aroms = extract_aromatics(PDB_DIR / f"{t['pdb_id']}.pdb", t["chains"])
        target_aroms[t["target_id"]] = aroms
        target_meta[t["target_id"]] = {
            "label": t["label"],
            "pdb_id": t["pdb_id"],
            "role": t["role"],
            "n_aromatics": len(aroms),
            "n_trp": sum(1 for a in aroms if a["res"] == "TRP"),
            "n_tyr": sum(1 for a in aroms if a["res"] == "TYR"),
            "n_phe": sum(1 for a in aroms if a["res"] == "PHE"),
            "pockets": t["pockets"],
        }
    shuf_aroms, shuf_pockets = make_shuffled_tubulin(target_aroms["tubulin_1jff"], seed=SEED)
    target_aroms["tubulin_1jff_shuffled"] = shuf_aroms
    target_meta["tubulin_1jff_shuffled"] = {
        "label": "Shuffled aromatics (81 random)",
        "pdb_id": "SYNTH",
        "role": "synthetic_control",
        "n_aromatics": len(shuf_aroms),
        "n_trp": sum(1 for a in shuf_aroms if a["res"] == "TRP"),
        "n_tyr": sum(1 for a in shuf_aroms if a["res"] == "TYR"),
        "n_phe": sum(1 for a in shuf_aroms if a["res"] == "PHE"),
        "pockets": [f"rand_{k+1}" for k in range(len(shuf_pockets))],
    }

    # Precompute baseline unperturbed spectra for Model A, Model A_phys, Model B
    baselines = {}
    for tid, aroms in target_aroms.items():
        M_a = build_matrix_model_a(aroms, use_kurian_tyr=True)
        f0_a, U0_a, neg_a = eigh_freqs(M_a)
        M_ap = build_matrix_model_a(aroms, use_kurian_tyr=False)
        f0_ap, U0_ap, neg_ap = eigh_freqs(M_ap)
        M_b = build_matrix_model_b(aroms)
        f0_b, U0_b, neg_b = eigh_freqs(M_b)
        n_band = int(np.sum((f0_a >= BAND_LO_THZ) & (f0_a <= BAND_HI_THZ)))
        baselines[tid] = {
            "A": (f0_a, U0_a, neg_a),
            "A_phys": (f0_ap, U0_ap, neg_ap),
            "B": (f0_b, U0_b, neg_b),
        }
        target_meta[tid]["baseline_a_min_thz"] = round(float(f0_a.min()), 2)
        target_meta[tid]["baseline_a_max_thz"] = round(float(f0_a.max()), 2)
        target_meta[tid]["baseline_a_n_in_613_band"] = n_band
        target_meta[tid]["baseline_a_n_neg"] = neg_a
        target_meta[tid]["baseline_b_min_thz"] = round(float(f0_b.min()), 2)
        target_meta[tid]["baseline_b_max_thz"] = round(float(f0_b.max()), 2)
        target_meta[tid]["baseline_b_n_neg"] = neg_b
        print(
            f"  {tid:22s}: N={len(aroms):3d} | Model A {f0_a.min():5.1f}-{f0_a.max():5.1f} THz "
            f"(in 613±8: {n_band:2d}, neg={neg_a}) | Model B {f0_b.min():5.1f}-{f0_b.max():6.1f} THz (neg={neg_b})",
            flush=True,
        )

    # Compute ligand all-atom poses & polarizabilities once per (pose_source, target, pocket, mol)
    print("3. Solving collective dipole eigenmodes across all 8 proteins + shuffled control...", flush=True)
    # Primary storage: results_grid[pose_src][model_key][tid][mol_id] = dict of aggregated metrics
    results_grid: Dict[str, Dict[str, Dict[str, Dict[str, Dict]]]] = {
        "vina": {"A": {}, "A_phys": {}, "B": {}},
        "vinardo": {"A": {}},
        "vina_s1cal": {"A": {}},  # exact Craddock Table S1 calibration on 11 gases
    }
    tsv_rows = []
    mol_pol_summary: Dict[str, Dict] = {}
    # Store full 1JFF per-pocket & example shift spectra for interactive plotting
    spectra_1jff_example: Dict[str, Dict] = {}

    # Cache canonical molecule polarizability (from tubulin_1jff site_7 vina pose, for isotropic reporting)
    for m in mols:
        mid = m["mol_id"]
        p = DOCK_OUT_DIR / "vina" / "tubulin_1jff__site_7" / f"{mid}_out.pdbqt"
        elems, coords = pdbqt_model1_all_atom(p, expected_formulas[mid])
        pol = thole_polarizability_tensor(coords, elems)
        eig = np.linalg.eigvalsh(pol)
        a_iso_au = float(np.mean(eig))
        a_iso_a3 = a_iso_au * AU_TO_ANG3
        a_norm_au = float(np.linalg.norm(eig))
        f_iso_thz = math.sqrt(PREF_DIAG / a_norm_au) / (2.0 * math.pi) / 1e12
        # Also Table S1 isotropic-equivalent Drude freq if in Craddock S1
        s1_a3 = CRADDOCK_S1_ALPHA_A3.get(mid)
        f_s1_thz = None
        if s1_a3 is not None:
            scale = (s1_a3 / AU_TO_ANG3) / a_iso_au
            f_s1_thz = math.sqrt(PREF_DIAG / (a_norm_au * scale)) / (2.0 * math.pi) / 1e12
        mol_pol_summary[mid] = {
            "mol_id": mid,
            "name": m["name"],
            "mol_class": m["mol_class"],
            "subset": m["subset"],
            "mac_atm": m["mac_atm"],
            "oil_gas": m["oil_gas"],
            "n_heavy": m["n_heavy"],
            "alpha_iso_a3": round(a_iso_a3, 3),
            "alpha_norm_au": round(a_norm_au, 2),
            "f_iso_thz": round(f_iso_thz, 2),
            "craddock_s1_a3": s1_a3,
            "f_s1_thz": round(f_s1_thz, 2) if f_s1_thz is not None else None,
        }

    # Helper to solve one (tid, pocket_nodes_list) across molecules
    def solve_target(pose_src: str, tid: str, models_to_run: List[str], s1_calibrate: bool = False) -> None:
        aroms = target_aroms[tid]
        is_shuf = (tid == "tubulin_1jff_shuffled")
        pockets = target_meta[tid]["pockets"]
        for mk in models_to_run:
            results_grid[pose_src if not s1_calibrate else "vina_s1cal"][mk][tid] = {}

        mol_list = [m for m in mols if (not s1_calibrate or m["mol_id"] in CRADDOCK_S1_ALPHA_A3)]
        for m in mol_list:
            mid = m["mol_id"]
            per_model_pockets: Dict[str, List[Dict]] = {mk: [] for mk in models_to_run}
            for p_idx, pk in enumerate(pockets):
                if is_shuf:
                    # Reuse 1JFF's corresponding pocket ligand orientation shifted to shuffled pocket center
                    src_pk = TARGETS[0]["pockets"][p_idx]
                    pdbqt = DOCK_OUT_DIR / pose_src / f"tubulin_1jff__{src_pk}" / f"{mid}_out.pdbqt"
                    elems, coords = pdbqt_model1_all_atom(pdbqt, expected_formulas[mid])
                    pol = thole_polarizability_tensor(coords, elems)
                    center = shuf_pockets[p_idx]
                else:
                    pdbqt = DOCK_OUT_DIR / pose_src / f"{tid}__{pk}" / f"{mid}_out.pdbqt"
                    elems, coords = pdbqt_model1_all_atom(pdbqt, expected_formulas[mid])
                    pol = thole_polarizability_tensor(coords, elems)
                    center = coords.mean(axis=0)
                if s1_calibrate:
                    target_iso_au = CRADDOCK_S1_ALPHA_A3[mid] / AU_TO_ANG3
                    pol = pol * (target_iso_au / (np.trace(pol) / 3.0))
                lig_node = {"id": f"LIG:{mid}", "res": "LIG", "center": center, "alpha_lab": pol}
                nodes_plus = aroms + [lig_node]
                _, f_iso_pose = isolated_drude_freq_thz(pol)

                for mk in models_to_run:
                    f0, U0, _ = baselines[tid][mk]
                    if mk == "A":
                        M1 = build_matrix_model_a(nodes_plus, use_kurian_tyr=True)
                        f1, U1, neg1 = eigh_freqs(M1)
                        res = match_modes_and_shifts(f0, U0, f1, U1, n_lig_dof=1)
                    elif mk == "A_phys":
                        M1 = build_matrix_model_a(nodes_plus, use_kurian_tyr=False)
                        f1, U1, neg1 = eigh_freqs(M1)
                        res = match_modes_and_shifts(f0, U0, f1, U1, n_lig_dof=1)
                    else:  # Model B
                        M1 = build_matrix_model_b(nodes_plus)
                        f1, U1, neg1 = eigh_freqs(M1)
                        res = match_modes_and_shifts(f0, U0, f1, U1, n_lig_dof=3)
                    res["pocket"] = pk
                    res["n_neg"] = neg1
                    res["f_iso_pose_thz"] = round(f_iso_pose, 2)
                    per_model_pockets[mk].append(res)

            # Aggregate across pockets of target tid
            dest_src = "vina_s1cal" if s1_calibrate else pose_src
            for mk in models_to_run:
                plist = per_model_pockets[mk]
                # d_613: pocket with largest |d_613_ghz|
                valid_613 = [x for x in plist if x["d_613_ghz"] is not None]
                if valid_613:
                    best_613 = max(valid_613, key=lambda x: abs(x["d_613_ghz"]))
                    d_613 = round(best_613["d_613_ghz"], 3)
                    best_613_pk = best_613["pocket"]
                    d_down_613 = round(max(x["d_down_613_ghz"] for x in valid_613), 3)
                else:
                    d_613 = None
                    best_613_pk = None
                    d_down_613 = None
                best_all = max(plist, key=lambda x: abs(x["d_all_ghz"]))
                d_all = round(best_all["d_all_ghz"], 3)
                rms_max = round(max(x["rms_ghz"] for x in plist), 3)
                f_new_mean = round(float(np.mean([x["f_new_thz"][0] for x in plist])), 2)
                f_iso_mean = round(float(np.mean([x["f_iso_pose_thz"] for x in plist])), 2)
                n_neg_any = int(any(x["n_neg"] > 0 for x in plist))

                rec = {
                    "d_613_ghz": d_613,
                    "d_down_613_ghz": d_down_613,
                    "best_613_pocket": best_613_pk,
                    "d_all_ghz": d_all,
                    "best_all_pocket": best_all["pocket"],
                    "rms_max_ghz": rms_max,
                    "f_new_mean_thz": f_new_mean,
                    "f_iso_mean_thz": f_iso_mean,
                    "n_neg_any": n_neg_any,
                }
                results_grid[dest_src][mk][tid][mid] = rec
                tsv_rows.append({
                    "pose_source": dest_src,
                    "model": mk,
                    "target_id": tid,
                    "mol_id": mid,
                    "mol_class": m["mol_class"],
                    "subset": m["subset"],
                    "mac_atm": m["mac_atm"] if m["mac_atm"] is not None else "",
                    "alpha_iso_a3": mol_pol_summary[mid]["alpha_iso_a3"],
                    "f_iso_thz": f_iso_mean,
                    "f_new_thz": f_new_mean,
                    "d_613_ghz": d_613 if d_613 is not None else "",
                    "d_down_613_ghz": d_down_613 if d_down_613 is not None else "",
                    "best_613_pocket": best_613_pk or "",
                    "d_all_ghz": d_all,
                    "rms_max_ghz": rms_max,
                    "n_neg_any": n_neg_any,
                })

                # Save full 81-mode shift spectrum on 1JFF Model A (vina) for key showcase compounds
                if dest_src == "vina" and mk == "A" and tid == "tubulin_1jff" and mid in (
                    "nitrous_oxide", "desflurane", "isoflurane", "halothane", "methoxyflurane",
                    "o_xylene", "F6", "TFMB", "perfluorocyclobutane", "CF3CClFCF3", "flurothyl",
                ):
                    spectra_1jff_example[mid] = {
                        "best_pocket": best_613_pk,
                        "f_new_thz": round(best_613["f_new_thz"][0], 2),
                        "f_iso_thz": best_613["f_iso_pose_thz"],
                        "d_613_ghz": d_613,
                        "shifts_ghz": [round(float(x), 3) for x in best_613["shifts_ghz"]],
                    }

    all_tids = [t["target_id"] for t in TARGETS] + ["tubulin_1jff_shuffled"]
    for tid in all_tids:
        t_s = time.time()
        solve_target("vina", tid, ["A", "A_phys", "B"], s1_calibrate=False)
        solve_target("vinardo", tid, ["A"], s1_calibrate=False)
        if tid in ("tubulin_1jff", "tubulin_4i4t", "gabaa_6x3t", "hsa_1e7b", "lysozyme_1dpx", "tubulin_1jff_shuffled"):
            solve_target("vina", tid, ["A"], s1_calibrate=True)
        print(f"  Solved {tid:22s} ({time.time()-t_s:.1f}s)", flush=True)

    # -----------------------------------------------------------------------
    # Statistical Analysis (Tests 1–5)
    # -----------------------------------------------------------------------
    print("4. Running permutation tests, paired bootstraps, level-repulsion & SO(3) audits...", flush=True)
    alpha_iso_by_mol = {mid: mol_pol_summary[mid]["alpha_iso_a3"] for mid in mol_pol_summary}

    stats_out: Dict[str, Dict] = {}
    for key_label, src, mk, metric_field in [
        ("vina_A_d613", "vina", "A", "d_613_ghz"),
        ("vina_A_ddown613", "vina", "A", "d_down_613_ghz"),
        ("vina_A_dall", "vina", "A", "d_all_ghz"),
        ("vina_A_fnew", "vina", "A", "f_new_mean_thz"),
        ("vina_Aphys_d613", "vina", "A_phys", "d_613_ghz"),
        ("vina_B_dall", "vina", "B", "d_all_ghz"),
        ("vina_B_rms", "vina", "B", "rms_max_ghz"),
        ("vinardo_A_d613", "vinardo", "A", "d_613_ghz"),
    ]:
        stats_out[key_label] = {}
        for tid in all_tids:
            scores = {mid: results_grid[src][mk][tid][mid][metric_field] for mid in mol_by_id}
            # For f_new, higher potency = LOWER f_new (higher polarizability), so flip sign for potency correlation
            if metric_field == "f_new_mean_thz":
                scores = {mid: (-v if v is not None else None) for mid, v in scores.items()}
            stats_out[key_label][tid] = evaluate_target_metrics(scores, mols, alpha_iso_by_mol, rng)

    # Table S1 exact calibration check (8 vs 2)
    s1_check = {}
    for tid in ("tubulin_1jff", "tubulin_4i4t", "gabaa_6x3t", "hsa_1e7b", "lysozyme_1dpx", "tubulin_1jff_shuffled"):
        gd = results_grid["vina_s1cal"]["A"][tid]
        an_v = np.array([gd[mid]["d_613_ghz"] for mid in CRADDOCK_ORIG_ANAES], dtype=float)
        no_v = np.array([gd[mid]["d_613_ghz"] for mid in CRADDOCK_ORIG_NON], dtype=float)
        pot_v = np.array([-math.log10(mol_by_id[mid]["mac_atm"]) for mid in CRADDOCK_ORIG_ANAES], dtype=float)
        rho_o, p_o = perm_test_spearman(an_v, pot_v, N_PERM, rng)
        s1_check[tid] = {
            "rho_pot_8": round(rho_o, 4),
            "p_rho_pot_8": round(p_o, 5),
            "auc_8v2": round(roc_auc(an_v, no_v), 4),
            "an_down_of_8": int(np.sum(an_v > 0)),
            "no_up_of_2": int(np.sum(no_v < 0)),
            "values": {mid: gd[mid]["d_613_ghz"] for mid in CRADDOCK_ORIG_ANAES + CRADDOCK_ORIG_NON + ["flurothyl"]},
        }

    # Paired bootstrap comparisons (Tubulin 1JFF minus comparator) on vina_A_d613, vina_A_dall, vina_B_dall
    an_ids = [m["mol_id"] for m in mols if m["mol_class"] == "anaesthetic"]
    no_ids = [m["mol_id"] for m in mols if m["mol_class"] == "non_immobilizer"]
    pot_an = np.array([-math.log10(mol_by_id[mid]["mac_atm"]) for mid in an_ids], dtype=float)
    paired_vs_1jff = {}
    for label, src, mk, fld in [
        ("vina_A_d613", "vina", "A", "d_613_ghz"),
        ("vina_A_dall", "vina", "A", "d_all_ghz"),
        ("vina_B_dall", "vina", "B", "d_all_ghz"),
    ]:
        paired_vs_1jff[label] = {}
        ref_an = np.array([results_grid[src][mk]["tubulin_1jff"][mid][fld] for mid in an_ids], dtype=float)
        ref_no = np.array([results_grid[src][mk]["tubulin_1jff"][mid][fld] for mid in no_ids], dtype=float)
        for tid in all_tids:
            if tid == "tubulin_1jff":
                continue
            vals_an = [results_grid[src][mk][tid][mid][fld] for mid in an_ids]
            vals_no = [results_grid[src][mk][tid][mid][fld] for mid in no_ids]
            if any(v is None for v in vals_an + vals_no):
                paired_vs_1jff[label][tid] = None
                continue
            paired_vs_1jff[label][tid] = paired_bootstrap_compare(
                ref_an, np.array(vals_an, dtype=float), pot_an,
                ref_no, np.array(vals_no, dtype=float), N_BOOT, rng,
            )

    # Test 4: Level-repulsion sign predictability across all protein-molecule pairs with a 613+-8 band
    lr_total = 0; lr_match = 0
    lr_by_target = {}
    for tid in all_tids:
        t_tot = 0; t_hit = 0
        for mid in mol_by_id:
            rec = results_grid["vina"]["A"][tid][mid]
            if rec["d_613_ghz"] is None:
                continue
            pred_down = (rec["f_iso_mean_thz"] > 613.0)
            actual_down = (rec["d_613_ghz"] > 0.0)
            t_tot += 1
            if pred_down == actual_down:
                t_hit += 1
        if t_tot > 0:
            lr_total += t_tot; lr_match += t_hit
            lr_by_target[tid] = {"matches": t_hit, "total": t_tot, "frac": round(t_hit / t_tot, 4)}
    level_repulsion = {
        "overall_matches": lr_match,
        "overall_total": lr_total,
        "overall_frac": round(lr_match / lr_total, 4) if lr_total else 0.0,
        "by_target": lr_by_target,
    }

    # Test 5: Rigid SO(3) rotational invariance audit (20 random 3D rotations of 1JFF + isoflurane/TFMB)
    so3_audit = {}
    aroms_1jff = target_aroms["tubulin_1jff"]
    f0_a_base, U0_a_base, _ = baselines["tubulin_1jff"]["A"]
    f0_b_base, U0_b_base, _ = baselines["tubulin_1jff"]["B"]
    rots = [Rotation.random(random_state=rng).as_matrix() for _ in range(N_SO3)]
    for mid, pk in [("isoflurane", "site_7"), ("TFMB", "site_5")]:
        pdbqt = DOCK_OUT_DIR / "vina" / f"tubulin_1jff__{pk}" / f"{mid}_out.pdbqt"
        elems, coords = pdbqt_model1_all_atom(pdbqt, expected_formulas[mid])
        pol = thole_polarizability_tensor(coords, elems)
        lig_node = {"id": f"LIG:{mid}", "res": "LIG", "center": coords.mean(axis=0), "alpha_lab": pol}
        a_d613, a_fmin, a_fmax, b_dall = [], [], [], []
        for Rmat in rots:
            ar_r = apply_so3_rotation(aroms_1jff, Rmat)
            lg_r = apply_so3_rotation([lig_node], Rmat)[0]
            # Model A rotated
            f0r, U0r, _ = eigh_freqs(build_matrix_model_a(ar_r, True))
            f1r, U1r, _ = eigh_freqs(build_matrix_model_a(ar_r + [lg_r], True))
            mr = match_modes_and_shifts(f0r, U0r, f1r, U1r, 1)
            a_d613.append(mr["d_613_ghz"])
            a_fmin.append(float(f0r.min())); a_fmax.append(float(f0r.max()))
            # Model B rotated
            f0rb, U0rb, _ = eigh_freqs(build_matrix_model_b(ar_r))
            f1rb, U1rb, _ = eigh_freqs(build_matrix_model_b(ar_r + [lg_r]))
            mrb = match_modes_and_shifts(f0rb, U0rb, f1rb, U1rb, 3)
            b_dall.append(mrb["d_all_ghz"])
        a_arr = np.array(a_d613); b_arr = np.array(b_dall)
        so3_audit[f"{mid}_{pk}"] = {
            "n_rotations": N_SO3,
            "model_a_d613_ghz": [round(float(x), 3) for x in a_arr],
            "model_a_mean_ghz": round(float(a_arr.mean()), 3),
            "model_a_sd_ghz": round(float(a_arr.std()), 3),
            "model_a_range_ghz": [round(float(a_arr.min()), 3), round(float(a_arr.max()), 3)],
            "model_a_sign_flips": int(np.sum(a_arr > 0) > 0 and np.sum(a_arr < 0) > 0),
            "model_a_baseline_min_range_thz": [round(min(a_fmin), 2), round(max(a_fmin), 2)],
            "model_b_dall_range_ghz": [round(float(b_arr.min()), 6), round(float(b_arr.max()), 6)],
            "model_b_max_drift_ghz": round(float(b_arr.max() - b_arr.min()), 9),
        }

    # Pre-registered Verdict Classification
    s1j = stats_out["vina_A_d613"]["tubulin_1jff"]
    s4i = stats_out["vina_A_d613"]["tubulin_4i4t"]
    ctrl_ids = ("hsa_1e7b", "luciferase_1ba3", "lysozyme_1dpx", "tubulin_1jff_shuffled")
    beats_all_ctrls = all(
        (paired_vs_1jff["vina_A_d613"][c] is not None)
        and (
            paired_vs_1jff["vina_A_d613"][c]["delta_rho_ci95"][0] > 0
            or paired_vs_1jff["vina_A_d613"][c]["delta_auc_ci95"][0] > 0
        )
        for c in ctrl_ids
    )
    pot_ok = (s1j["rho_pot"] > 0 and s1j["p_rho_pot"] < 0.05)
    pot_4i_ok = (s4i["rho_pot"] > 0 and s4i["p_rho_pot"] < 0.05)
    pot_partial_ok = (s1j["rho_partial_alpha"] > 0 and s1j["p_partial_alpha"] < 0.05)
    auc_ok = (s1j["auc_sep"] > 0.70 and s1j["p_auc_sep"] < 0.05)
    orig_ok = (s1j["craddock_8v2"]["auc_sep"] >= 0.75 or s1_check["tubulin_1jff"]["auc_8v2"] >= 0.75)
    lr_strong = (level_repulsion["overall_frac"] >= 0.80)

    if pot_ok and pot_4i_ok and pot_partial_ok and auc_ok and beats_all_ctrls:
        v_code = "tubulin_selective_terahertz"
        v_reason = "Tubulin tracks potency beyond polarizability, rejects non-immobilizers, and beats every non-conscious control."
    elif pot_ok and auc_ok and not beats_all_ctrls and not lr_strong:
        v_code = "generic_across_proteins"
        v_reason = "Expanded potency tracking and non-immobilizer separation occur equally across non-conscious control proteins."
    elif orig_ok or lr_strong:
        v_code = "level_repulsion_artifact_not_tubulin_specific"
        v_reason = (
            "The 613 THz downward-vs-upward shift follows generic coupled-oscillator level repulsion from scalar molecular "
            "polarizability, fails on the expanded 27-vs-7 volatile panel, and shows no tubulin specificity over controls."
        )
    else:
        v_code = "fails_reproduction"
        v_reason = "Collective dipole shifts fail both on Craddock's original 8-vs-2 benchmark and on the expanded 27-vs-7 panel."

    # Also store compact 3D coordinates of 1JFF and Lysozyme aromatics + pocket centers for interactive 3D figure
    aroms_3d = {}
    for tid in ("tubulin_1jff", "lysozyme_1dpx", "hsa_1e7b", "gabaa_6x3t"):
        ar = target_aroms[tid]
        pts = np.array([a["center"] for a in ar])
        ctr = pts.mean(axis=0)
        aroms_3d[tid] = {
            "label": target_meta[tid]["label"],
            "residues": [
                {
                    "id": a["id"],
                    "res": a["res"],
                    "xyz": [round(float(v), 2) for v in (a["center"] - ctr)],
                    "u": [round(float(v), 3) for v in (np.diag(a["R"] @ np.diag(AROM_ALPHA_KURIAN[a["res"]]) @ a["R"].T) / np.linalg.norm(np.diag(a["R"] @ np.diag(AROM_ALPHA_KURIAN[a["res"]]) @ a["R"].T)))],
                }
                for a in ar
            ],
            "pockets": [],
        }
        for pk in target_meta[tid]["pockets"]:
            pdbqt = DOCK_OUT_DIR / "vina" / f"{tid}__{pk}" / "isoflurane_out.pdbqt"
            _, co = pdbqt_model1_all_atom(pdbqt, expected_formulas["isoflurane"])
            aroms_3d[tid]["pockets"].append({
                "pocket": pk,
                "xyz": [round(float(v), 2) for v in (co.mean(axis=0) - ctr)],
            })

    # Write TSV
    tsv_path = RESULTS_DIR / "shifts.tsv"
    with tsv_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tsv_rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(tsv_rows)

    # Write summary.json
    summary = {
        "meta": {
            "seed": SEED,
            "n_perm": N_PERM,
            "n_boot": N_BOOT,
            "n_so3": N_SO3,
            "band_thz": [BAND_LO_THZ, BAND_HI_THZ],
            "thole_a": THOLE_A,
            "elapsed_sec": round(time.time() - t0, 2),
        },
        "molecules": [mol_pol_summary[m["mol_id"]] for m in mols],
        "target_meta": target_meta,
        "baselines_thz": {
            tid: [round(float(x), 2) for x in baselines[tid]["A"][0]]
            for tid in all_tids
        },
        "spectra_1jff_examples": spectra_1jff_example,
        "matrices": {
            "vina_A_d613": {tid: {mid: results_grid["vina"]["A"][tid][mid]["d_613_ghz"] for mid in mol_by_id} for tid in all_tids},
            "vina_A_dall": {tid: {mid: results_grid["vina"]["A"][tid][mid]["d_all_ghz"] for mid in mol_by_id} for tid in all_tids},
            "vina_A_fnew": {tid: {mid: results_grid["vina"]["A"][tid][mid]["f_new_mean_thz"] for mid in mol_by_id} for tid in all_tids},
            "vina_B_dall": {tid: {mid: results_grid["vina"]["B"][tid][mid]["d_all_ghz"] for mid in mol_by_id} for tid in all_tids},
            "vinardo_A_d613": {tid: {mid: results_grid["vinardo"]["A"][tid][mid]["d_613_ghz"] for mid in mol_by_id} for tid in all_tids},
        },
        "stats": stats_out,
        "craddock_s1_calibrated": s1_check,
        "paired_vs_1jff": paired_vs_1jff,
        "level_repulsion_audit": level_repulsion,
        "so3_rotation_audit": so3_audit,
        "aromatics_3d": aroms_3d,
        "verdict": {
            "verdict_code": v_code,
            "reason": v_reason,
            "checks": {
                "orig_8v2_reproduced": orig_ok,
                "pot_1jff_expanded": pot_ok,
                "pot_4i4t_expanded": pot_4i_ok,
                "pot_1jff_partial_alpha": pot_partial_ok,
                "auc_1jff_expanded": auc_ok,
                "beats_all_controls": beats_all_ctrls,
                "level_repulsion_gt80pct": lr_strong,
            },
        },
    }
    (RESULTS_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nDONE in {time.time()-t0:.1f}s -> verdict={v_code}", flush=True)
    print(f"  Level-repulsion sign match: {lr_match}/{lr_total} ({level_repulsion['overall_frac']:.1%})", flush=True)
    print(f"  1JFF Vina Model A (D_613): rho={s1j['rho_pot']:+.3f} (p={s1j['p_rho_pot']:.4f}), "
          f"partial|alpha={s1j['rho_partial_alpha']:+.3f} (p={s1j['p_partial_alpha']:.4f}), "
          f"AUC={s1j['auc_sep']:.3f} (p={s1j['p_auc_sep']:.4f})", flush=True)


if __name__ == "__main__":
    run_all()
