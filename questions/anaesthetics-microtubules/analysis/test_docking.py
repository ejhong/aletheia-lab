#!/usr/bin/env python3
"""
Pre-lock unit and synthetic-calibration tests for analysis/dock_anaesthetics.py.
Runs strictly on synthetic/decoy data and molecule-table invariants (never touches real test-panel dockings).
"""

import math
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dock_anaesthetics as da


def test_panel_invariants():
    assert len(da.MOLECULES) == 35
    ids = [m.mol_id for m in da.MOLECULES]
    assert len(set(ids)) == 35, "Duplicate mol_id"
    anaes = [m for m in da.MOLECULES if m.mol_class == "anaesthetic"]
    non_imm = [m for m in da.MOLECULES if m.mol_class == "non_immobilizer"]
    conv = [m for m in da.MOLECULES if m.mol_class == "convulsant"]
    assert len(anaes) == 27
    assert len(non_imm) == 7
    assert len(conv) == 1
    assert all(m.mac_atm is not None and m.mac_atm > 0 and m.oil_gas is not None and m.oil_gas > 0 for m in anaes)
    assert sum(1 for m in non_imm if m.oil_gas is not None) == 5
    # Verify Meyer-Overton correlation holds strongly in our locked molecule table
    p_an = np.array([-math.log10(m.mac_atm) for m in anaes])
    oil_an = np.array([math.log10(m.oil_gas) for m in anaes])
    rho_mo = da.spearman_rho(p_an, oil_an)
    assert rho_mo > 0.85, f"Meyer-Overton correlation unexpectedly low: {rho_mo}"
    assert len(da.SITES) == 24
    for tid in da.TARGET_ORDER:
        prim = [s for s in da.SITES if s.target_id == tid and s.is_primary_single]
        assert len(prim) == 1, f"Target {tid} must have exactly 1 primary single site"
    print(f"  PASS test_panel_invariants (Meyer-Overton rho={rho_mo:.3f} across n=27 anaesthetics)")


def test_rank_and_partial_stats():
    x = np.array([1.0, 2.0, 2.0, 4.0, 5.0])
    r = da.average_ranks(x)
    assert np.allclose(r, [1.0, 2.5, 2.5, 4.0, 5.0])
    # Pure size-confounded synthetic signal: B = 0.4 * N_heavy + small noise -> partial_heavy ~ 0
    rng = np.random.default_rng(42)
    z = np.arange(1, 28, dtype=float)
    x_sig = 0.5 * z + rng.normal(0, 0.05, size=27)
    y_sig = 0.8 * z + rng.normal(0, 0.05, size=27)
    raw = da.spearman_rho(x_sig, y_sig)
    part = da.partial_spearman(x_sig, y_sig, z)
    assert raw > 0.95 and abs(part) < 0.35, f"Expected raw~1, part~0; got raw={raw}, part={part}"
    print(f"  PASS test_rank_and_partial_stats (raw={raw:.3f}, partial_given_confounder={part:.3f})")


def test_synthetic_selective_vs_generic():
    """Verify verdict engine distinguishes a selective target from a size-biased generic binder."""
    rng = np.random.default_rng(12345)
    # 1) Selective synthetic target: tracks potency AND rejects non-immobilizers
    b_sel = {}
    for m in da.MOLECULES:
        if m.mol_class == "anaesthetic":
            b_sel[m.mol_id] = 3.0 + 1.2 * (-math.log10(m.mac_atm)) + float(rng.normal(0, 0.15))
        else:
            b_sel[m.mol_id] = 2.0 + float(rng.normal(0, 0.15))
    res_sel = da.evaluate_target_vector(b_sel, da.MOLECULES, rng)
    assert res_sel["rho_pot"] > 0.90 and res_sel["p_rho_pot"] < 0.001
    assert res_sel["auc_sep"] > 0.95 and res_sel["r_non_oil"] < -1.0

    # 2) Pure heavy-atom generic binder (simulating naive docking size bias):
    # non-immobilizers have high N_heavy, so AUC_sep < 0.5!
    b_hvy = {m.mol_id: 1.0 + 0.35 * m.n_heavy + float(rng.normal(0, 0.05)) for m in da.MOLECULES}
    res_hvy = da.evaluate_target_vector(b_hvy, da.MOLECULES, rng)
    assert res_hvy["auc_sep"] < 0.35, f"Expected heavy-atom bias to give AUC < 0.35, got {res_hvy['auc_sep']}"
    assert abs(res_hvy["r_non_heavy"]) < 0.2, f"Expected size-adjusted residual ~ 0, got {res_hvy['r_non_heavy']}"

    # 3) Null random binder
    b_null = {m.mol_id: float(rng.normal(4.0, 0.5)) for m in da.MOLECULES}
    res_null = da.evaluate_target_vector(b_null, da.MOLECULES, rng)
    assert abs(res_null["rho_pot"]) < 0.45

    # 4) Verify Boltzmann affinity >= mean and <= max
    ens = da.boltzmann_affinity([-4.0, -5.0, -6.0, -3.5])
    assert 4.6 < ens < 6.0, f"Unexpected Boltzmann affinity: {ens}"
    print(f"  PASS test_synthetic_selective_vs_generic (sel_AUC={res_sel['auc_sep']:.3f}, hvy_AUC={res_hvy['auc_sep']:.3f}, ens={ens:.3f})")


def main():
    print("Running pre-lock unit & synthetic-calibration tests...")
    test_panel_invariants()
    test_rank_and_partial_stats()
    test_synthetic_selective_vs_generic()
    print("ALL TESTS PASSED.")


if __name__ == "__main__":
    main()
