#!/usr/bin/env python3
"""Pre-lock unit tests and power/calibration checks for analysis/taurid.py.

Never reads real Taurid orbital alignment or fireball seasonality.
"""
import datetime
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import taurid as td


def test_circular_v_and_power():
    rng = np.random.default_rng(101)
    # 1. Calibration: uniform angles should reject at ~0.05 (allow [0.02, 0.09] over 200 trials)
    rejects = 0
    for trial in range(200):
        ang = rng.uniform(0.0, 360.0, size=60)
        res = td.circular_v_test(ang, 161.29, n_mc=500, seed=trial + 1)
        if res["p_unif"] < 0.05:
            rejects += 1
    rate = rejects / 200.0
    assert 0.015 <= rate <= 0.095, f"Uniform false positive rate out of bounds: {rate}"

    # 2. Power: 30 aligned Taurids (SD 25 deg around 161.3) + 70 uniform background (u ~ 3.85)
    hits = 0
    for trial in range(40):
        bg = rng.uniform(0.0, 360.0, size=70)
        sig = (161.29 + rng.normal(0.0, 25.0, size=30)) % 360.0
        res = td.circular_v_test(np.concatenate([bg, sig]), 161.29, n_mc=1000, seed=trial + 1000)
        if res["p_unif"] < 0.01:
            hits += 1
    assert hits >= 34, f"Insufficient power to detect 30/100 aligned cluster: {hits}/40"
    print(f"[PASS] Circular V-test calibration (null FPR={rate:.3f}) & power ({hits}/40 >= 34/40)")


def test_secular_control_rejects_shared_bias():
    rng = np.random.default_rng(202)
    # Both Box_T and Ctrl_LowE share identical strong Jupiter bias around 161 deg -> must NOT pass control!
    bias_t = (161.29 + rng.normal(0.0, 55.0, size=80)) % 360.0
    bias_c = (161.29 + rng.normal(0.0, 55.0, size=180)) % 360.0
    vt = td.circular_v_test(bias_t, 161.29, n_mc=2000, seed=11)
    assert vt["p_unif"] < 0.001, "Expected shared bias to look strongly non-uniform"
    ct = np.cos(np.deg2rad(td.ang_diff_deg(bias_t, 161.29)))
    cc = np.cos(np.deg2rad(td.ang_diff_deg(bias_c, 161.29)))
    dc, p_ctrl = td.perm_diff_mean(ct, cc, n_perm=2000, seed=12)
    assert p_ctrl > 0.05, f"Control failed to reject shared secular bias: dC={dc}, p={p_ctrl}"
    print(f"[PASS] Secular control rejects shared bias (p_unif={vt['p_unif']:.4f}, p_ctrl={p_ctrl:.3f})")


def test_calendar_and_swarm_power():
    # Verify exact day counts across leap and non-leap years
    for yr in (2023, 2024):
        d = datetime.date(yr, 1, 1)
        aut_n = 0
        day_n = 0
        while d.year == yr:
            if td.is_autumn_taurid(d.month, d.day):
                aut_n += 1
            if td.is_daytime_taurid(d.month, d.day):
                day_n += 1
            d += datetime.timedelta(days=1)
        assert aut_n == 47, f"Autumn days {aut_n} in {yr}"
        assert day_n == 31, f"Daytime days {day_n} in {yr}"

    # Verify B2 detects an injected 2.5x Autumn surge in the 6 swarm years
    rng = np.random.default_rng(303)
    syn_fb = []
    for yr in range(1994, 2026):
        n_bg = 30
        for _ in range(n_bg):
            doy = float(rng.uniform(0.0, 365.0))
            dt = datetime.datetime(yr, 1, 1) + datetime.timedelta(days=doy)
            syn_fb.append({"year": yr, "month": dt.month, "day": dt.day, "doy": doy,
                           "impact_kt": 0.2, "autumn": td.is_autumn_taurid(dt.month, dt.day),
                           "daytime": td.is_daytime_taurid(dt.month, dt.day)})
        if yr in td.SWARM_YEARS_6:
            for _ in range(8):  # injected 8 extra autumn Taurid bolides per swarm year
                doy = float(rng.uniform(288.0, 333.0))
                dt = datetime.datetime(yr, 1, 1) + datetime.timedelta(days=doy)
                syn_fb.append({"year": yr, "month": dt.month, "day": dt.day, "doy": doy,
                               "impact_kt": 0.5, "autumn": True, "daytime": False})
    res_b = td.analyze_archive_b(syn_fb, 1994, 2025)
    assert res_b["pass_b2"], f"Failed to detect injected swarm-year surge: {res_b['test_b2_swarm_years_6']}"
    print(f"[PASS] Calendar window exact (47d/31d) & B2 detects injected swarm surge (p={res_b['test_b2_swarm_years_6']['s_cnt']['p_perm']:.4f})")


if __name__ == "__main__":
    test_circular_v_and_power()
    test_secular_control_rejects_shared_bias()
    test_calendar_and_swarm_power()
    print("ALL TESTS PASSED.")
