#!/usr/bin/env python3
"""
Pre-lock unit and analytical physics tests for Issue #115 (`anaesthetics-terahertz`).
Verifies exact mathematics on synthetic oscillators, SO(3) rotational invariance,
eigenvector-overlap mode matching across level crossings, and Thole polarizability
calibration — WITHOUT inspecting any real ligand-bound protein outputs.
"""
from __future__ import annotations

import math
import subprocess
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.stats import spearmanr

import terahertz_modes as tm


def test_two_oscillator_level_repulsion():
    """Exact 2-oscillator analytical eigenvalues & level-repulsion sign theorem."""
    # Protein mode at 613 THz (a_bar ~ 115.2 a.u.), placed at origin along z
    a_prot = tm.PREF_DIAG / ((2 * math.pi * 613e12) ** 2)
    prot_node = {"id": "P1", "res": "PHE", "center": np.array([0.0, 0.0, 0.0]), "alpha_lab": np.diag([a_prot, 0.0, 0.0]) + np.diag([0, 1e-9, 1e-9])}
    # Better: isotropic diagonal a_prot / sqrt(3) so ||diag|| == a_prot
    d_p = a_prot / math.sqrt(3.0)
    prot_node = {"id": "P1", "res": "PHE", "center": np.array([0.0, 0.0, 0.0]), "alpha_lab": np.diag([d_p, d_p, d_p])}
    f0, U0, n0 = tm.eigh_freqs(tm.build_matrix_model_a([prot_node]))
    assert n0 == 0 and abs(f0[0] - 613.0) < 1e-6

    # High-freq ligand (650 THz, small alpha -> like clinical anaesthetic) at ~6 A head-to-tail along (1,1,1)
    a_hi = tm.PREF_DIAG / ((2 * math.pi * 650e12) ** 2) / math.sqrt(3.0)
    lig_hi = {"id": "L_hi", "res": "LIG", "center": np.array([3.5, 3.5, 3.5]), "alpha_lab": np.diag([a_hi, a_hi, a_hi])}
    f1, U1, _ = tm.eigh_freqs(tm.build_matrix_model_a([prot_node, lig_hi]))
    m_hi = tm.match_modes_and_shifts(f0, U0, f1, U1, 1)
    assert m_hi["d_613_ghz"] > 0.0, f"Expected downward shift (D_613 > 0) for 650 THz ligand, got {m_hi['d_613_ghz']}"

    # Low-freq ligand (550 THz, large alpha -> like F6/TFMB) at ~6 A head-to-tail along (1,1,1)
    a_lo = tm.PREF_DIAG / ((2 * math.pi * 550e12) ** 2) / math.sqrt(3.0)
    lig_lo = {"id": "L_lo", "res": "LIG", "center": np.array([3.5, 3.5, 3.5]), "alpha_lab": np.diag([a_lo, a_lo, a_lo])}
    f2, U2, _ = tm.eigh_freqs(tm.build_matrix_model_a([prot_node, lig_lo]))
    m_lo = tm.match_modes_and_shifts(f0, U0, f2, U2, 1)
    assert m_lo["d_613_ghz"] < 0.0, f"Expected upward shift (D_613 < 0) for 550 THz ligand, got {m_lo['d_613_ghz']}"
    print(f"  PASS test_two_oscillator_level_repulsion (650 THz -> D_613={m_hi['d_613_ghz']:+.2f} GHz; 550 THz -> D_613={m_lo['d_613_ghz']:+.2f} GHz)")


def test_model_b_exact_so3_invariance():
    """Verify full 3N x 3N Drude Model B is invariant under arbitrary rigid SO(3) rotations to <1e-9 THz."""
    rng = np.random.default_rng(42)
    nodes = []
    for i, res in enumerate(("TRP", "TYR", "PHE", "TRP", "PHE")):
        nodes.append({
            "id": f"S{i}",
            "res": res,
            "center": rng.uniform(-10.0, 10.0, size=3),
            "R": Rotation.random(random_state=rng).as_matrix(),
        })
    # Ensure well-separated
    for i in range(len(nodes)):
        nodes[i]["center"] = np.array([i * 7.0, (i % 2) * 5.0, (i % 3) * 4.0])
    f_ref, _, neg0 = tm.eigh_freqs(tm.build_matrix_model_b(nodes))
    assert neg0 == 0
    max_err = 0.0
    for _ in range(10):
        Rmat = Rotation.random(random_state=rng).as_matrix()
        f_rot, _, _ = tm.eigh_freqs(tm.build_matrix_model_b(tm.apply_so3_rotation(nodes, Rmat)))
        max_err = max(max_err, float(np.max(np.abs(f_rot - f_ref))))
    assert max_err < 1e-9, f"Model B broke SO(3) invariance: max_err={max_err}"
    print(f"  PASS test_model_b_exact_so3_invariance (max_err={max_err:.2e} THz across 10 random SO(3) rotations)")


def test_thole_craddock_s1_calibration():
    """Verify Thole (van Duijnen & Swart 1998) polarizabilities match Craddock Table S1 with r > 0.99."""
    smis = {
        "nitrous_oxide": "[N-]=[N+]=O",
        "desflurane": "C(C(F)(F)F)(OC(F)F)F",
        "diethyl_ether": "CCOCC",
        "flurothyl": "C(C(F)(F)F)OCC(F)(F)F",
        "sevoflurane": "C(OC(C(F)(F)F)C(F)(F)F)F",
        "enflurane": "C(C(OC(F)F)(F)F)(F)Cl",
        "isoflurane": "C(C(F)(F)F)(OC(F)F)Cl",
        "halothane": "C(C(F)(F)F)(Cl)Br",
        "methoxyflurane": "COC(C(Cl)Cl)(F)F",
        "F6": "C1(C(C(C1(F)Cl)(F)Cl)(F)F)(F)F",
        "TFMB": "C1=C(C=C(C=C1C(F)(F)F)C(F)(F)F)C(F)(F)F",
    }
    pred, ref = [], []
    for mid, s1 in tm.CRADDOCK_S1_ALPHA_A3.items():
        xyz = subprocess.check_output(["obabel", f"-:{smis[mid]}", "-oxyz", "--gen3d"], stderr=subprocess.DEVNULL, text=True)
        el, co = [], []
        for ln in xyz.splitlines()[2:]:
            p = ln.split()
            if len(p) == 4:
                el.append(p[0]); co.append([float(p[1]), float(p[2]), float(p[3])])
        pol = tm.thole_polarizability_tensor(np.array(co), el)
        pred.append(np.trace(pol) / 3.0 * tm.AU_TO_ANG3)
        ref.append(s1)
    r = float(np.corrcoef(pred, ref)[0, 1])
    rho = float(spearmanr(pred, ref).statistic)
    assert r > 0.99, f"Thole calibration r too low: {r}"
    print(f"  PASS test_thole_craddock_s1_calibration (r={r:.4f}, rho={rho:.4f} vs Craddock Table S1 n=11)")


def test_stats_helpers():
    rng = np.random.default_rng(123)
    x = np.linspace(1, 20, 20)
    y = x * 2.0
    r, p = tm.perm_test_spearman(x, y, 1000, rng)
    assert abs(r - 1.0) < 1e-9 and p < 0.01
    # Confounder control: x and y both pure functions of z -> partial spearman == 0
    z = np.arange(20, dtype=float)
    assert abs(tm.partial_spearman(z + 1, 3 * z - 2, z)) < 1e-9
    # Perfect AUC
    auc, pauc = tm.perm_test_auc(np.array([10., 11., 12., 13., 14.]), np.array([1., 2., 3., 4., 5.]), 1000, rng)
    assert abs(auc - 1.0) < 1e-9 and pauc < 0.02
    print("  PASS test_stats_helpers")


if __name__ == "__main__":
    print("Running pre-lock physics & unit tests for anaesthetics-terahertz...")
    test_two_oscillator_level_repulsion()
    test_model_b_exact_so3_invariance()
    test_thole_craddock_s1_calibration()
    test_stats_helpers()
    print("ALL TESTS PASSED.")
