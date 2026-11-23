"""Independent replication of questions/ancient-sky-hole/protocol.md (written from protocol.md and
MANIFEST.md only). Usage:

    python -I skyrep.py <ptolemy_verbunt2012.tsv> <hipparcos_v70.tsv> <output.json> [--boot B] [--no-m4]

Interpretive choices that the protocol leaves open are marked "CHOICE" and listed in README.md.
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ltp import ltpequ  # noqa: E402

D2R = np.pi / 180.0
EPS = 0.002
EPS0 = 84381.406 / 3600.0 * D2R  # J2000 mean obliquity (IAU 2006), for ecliptic coordinates
T_LO, T_HI = -10000.0, 1000.0
PHI_LO, PHI_HI = 15.0, 50.0
T_3000BCE = -2999.0


# ----------------------------------------------------------------------------- reading
def read_tsv(path):
    rows, header, skip = [], None, 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split("\t")
            if header is None:
                header = [p.strip() for p in parts]
                skip = 2  # units line and dashes line
                continue
            if skip:
                skip -= 1
                continue
            rows.append([p.strip() for p in parts] + [""] * (len(header) - len(parts)))
    return header, rows


def fnum(s):
    try:
        return float(s)
    except ValueError:
        return np.nan


def load_hip(path):
    h, rows = read_tsv(path)
    ix = {k: h.index(k) for k in ["HIP", "RAICRS", "DEICRS", "Vmag", "pmRA", "pmDE"]}
    hip = np.array([int(r[ix["HIP"]]) for r in rows])
    ra = np.array([fnum(r[ix["RAICRS"]]) for r in rows])
    de = np.array([fnum(r[ix["DEICRS"]]) for r in rows])
    v = np.array([fnum(r[ix["Vmag"]]) for r in rows])
    pma = np.nan_to_num(np.array([fnum(r[ix["pmRA"]]) for r in rows]), nan=0.0)
    pmd = np.nan_to_num(np.array([fnum(r[ix["pmDE"]]) for r in rows]), nan=0.0)
    return dict(n_rows=len(rows), hip=hip, ra=ra, de=de, v=v, pma=pma, pmd=pmd)


def load_ptolemy(path):
    h, rows = read_tsv(path)
    ix = {k: h.index(k) for k in ["P", "cst", "f_N", "HIP", "I"]}
    out = []
    for r in rows:
        hip = r[ix["HIP"]]
        q = r[ix["I"]]
        out.append(dict(P=int(r[ix["P"]]), cst=r[ix["cst"]], fN=r[ix["f_N"]],
                        HIP=int(hip) if hip else None, I=int(q) if q else None))
    return out


# ----------------------------------------------------------------------------- geometry
def unit(ra, de):
    a, d = ra * D2R, de * D2R
    return np.stack([np.cos(d) * np.cos(a), np.cos(d) * np.sin(a), np.sin(d)], -1)


def pm_velocity(ra, de, pma, pmd):
    a, d = ra * D2R, de * D2R
    ea = np.stack([-np.sin(a), np.cos(a), np.zeros_like(a)], -1)
    ed = np.stack([-np.sin(d) * np.cos(a), -np.sin(d) * np.sin(a), np.cos(d)], -1)
    k = np.pi / (180.0 * 3.6e6)
    return k * (pma[:, None] * ea + pmd[:, None] * ed)


def directions(u0, vel, t):
    """u_i(t) for epochs t (array) -> (nT, N, 3)."""
    t = np.atleast_1d(np.asarray(t, float))
    u = u0[None] + (t - 1991.25)[:, None, None] * vel[None]
    return u / np.linalg.norm(u, axis=-1, keepdims=True)


def declinations(u0, vel, t):
    t = np.atleast_1d(np.asarray(t, float))
    u = directions(u0, vel, t)
    p = ltpequ(t)  # (nT, 3)
    return np.degrees(np.arcsin(np.clip(np.einsum("tni,ti->tn", u, p), -1, 1)))


def to_ecliptic(u):
    x, y, z = u[..., 0], u[..., 1], u[..., 2]
    ye = y * np.cos(EPS0) + z * np.sin(EPS0)
    ze = -y * np.sin(EPS0) + z * np.cos(EPS0)
    return np.degrees(np.arctan2(ye, x)) % 360.0, np.degrees(np.arcsin(np.clip(ze, -1, 1)))


def from_ecliptic(lam, bet):
    l, b = lam * D2R, bet * D2R
    xe, ye, ze = np.cos(b) * np.cos(l), np.cos(b) * np.sin(l), np.sin(b)
    y = ye * np.cos(EPS0) - ze * np.sin(EPS0)
    z = ye * np.sin(EPS0) + ze * np.cos(EPS0)
    return np.stack([xe, y, z], -1)


# ----------------------------------------------------------------------------- models
def fit_logistic(v, y):
    """ML fit of p = 1/(1+exp((V-V50)/sV)) by Newton-Raphson (IRLS)."""
    X = np.stack([np.ones_like(v), v], 1)
    w = np.zeros(2)
    for _ in range(100):
        eta = X @ w
        p = 1 / (1 + np.exp(-eta))
        g = X.T @ (y - p)
        H = (X * (p * (1 - p))[:, None]).T @ X
        step = np.linalg.solve(H, g)
        w += step
        if np.abs(step).max() < 1e-12:
            break
    a, b = w
    p = 1 / (1 + np.exp(-(X @ w)))
    ll = float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))
    return dict(V50=float(-a / b), sV=float(-1 / b), loglik=ll, n=int(len(v)), n_cat=int(y.sum()))


def p_base(v, cal):
    return 1.0 / (1.0 + np.exp((v - cal["V50"]) / cal["sV"]))


def apparent_altitude(h):
    """Bennett (1982) refraction applied to the geometric altitude for h > -0.6 deg (the protocol's
    stated behaviour: h=0 -> h_app ~ +0.57)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 1.0 / np.tan((h + 7.31 / (h + 4.4)) * D2R) / 60.0
    return np.where(h > -0.6, h + r, h)


def airmass_ky(happ):
    hh = np.where(happ > 0, happ, 1.0)
    return 1.0 / (np.sin(hh * D2R) + 0.50572 * (hh + 6.07995) ** -1.6364)


def star_ll_m1(dec, phi, v, y, cal, kv):
    """dec (..., N) deg, phi broadcastable -> per-star log-likelihood (..., N)."""
    h = 90.0 - np.abs(phi - dec)
    ha = apparent_altitude(h)
    X = airmass_ky(ha)
    veff = v + kv * (X - 1.0)
    P = np.where(ha > 0, (1 - 2 * EPS) * p_base(veff, cal) + EPS, EPS)
    return np.where(y > 0, np.log(P), np.log1p(-P))


def tile_ll_m1(S, cal, kv, ts, phis, W, chunk=8):
    """Per-tile summed log-likelihood on the grid ts x phis -> (nT, nPhi, nTiles)."""
    ts = np.asarray(ts, float)
    phis = np.asarray(phis, float)
    out = np.empty((len(ts), len(phis), W.shape[1]))
    for i in range(0, len(ts), chunk):
        dec = declinations(S["u0"], S["vel"], ts[i:i + chunk])  # (c, N)
        ll = star_ll_m1(dec[:, None, :], phis[None, :, None], S["v"], S["y"], cal, kv)
        out[i:i + chunk] = (ll.reshape(-1, ll.shape[-1]) @ W).reshape(len(dec), len(phis), -1)
    return out


def grid_coarse():
    return np.arange(T_LO, T_HI + 0.1, 50.0), np.round(np.arange(PHI_LO, PHI_HI + 1e-9, 0.5), 6)


def grid_refined(tc, pc):
    ts = tc + np.arange(-600, 601, 10.0)
    ps = np.round(pc + np.arange(-20, 21) * 0.2, 6)
    # CHOICE: the refined window is clipped to the coarse search domain.
    return ts[(ts >= T_LO) & (ts <= T_HI)], ps[(ps >= PHI_LO - 1e-9) & (ps <= PHI_HI + 1e-9)]


def argmax2(L):
    i, j = np.unravel_index(np.argmax(L), L.shape)
    return int(i), int(j)


def fit_m1(S, cal, kv, W=None):
    if W is None:
        W = S["w"][:, None]  # single "tile" = straight sum
    ts, ps = grid_coarse()
    L = tile_ll_m1(S, cal, kv, ts, ps, W).sum(-1)
    i, j = argmax2(L)
    tr, pr = grid_refined(ts[i], ps[j])
    Lr = tile_ll_m1(S, cal, kv, tr, pr, W).sum(-1)
    a, b = argmax2(Lr)
    return dict(t=float(tr[a]), phi=float(pr[b]), loglik=float(Lr[a, b]),
                coarse_t=float(ts[i]), coarse_phi=float(ps[j]), coarse_loglik=float(L[i, j]))


def profile_phi_at(S, cal, kv, t):
    ps = np.round(np.arange(PHI_LO, PHI_HI + 1e-9, 0.05), 6)
    L = tile_ll_m1(S, cal, kv, [t], ps, S["w"][:, None]).sum(-1)[0]
    j = int(np.argmax(L))
    return float(ps[j]), float(L[j])


def star_level_ci(S, cal, kv, best):
    ts = np.arange(best["t"] - 2500, best["t"] + 2501, 10.0)
    ts = ts[(ts >= T_LO) & (ts <= T_HI)]
    ps = np.round(np.arange(max(PHI_LO, best["phi"] - 8), min(PHI_HI, best["phi"] + 8) + 1e-9, 0.1), 6)
    L = tile_ll_m1(S, cal, kv, ts, ps, S["w"][:, None]).sum(-1)
    ok = 2 * (L.max() - L) <= 5.99
    ii, jj = np.nonzero(ok)
    return dict(t=[float(ts[ii].min()), float(ts[ii].max())], phi=[float(ps[jj].min()), float(ps[jj].max())],
                grid_max_loglik=float(L.max()), note="2 dlnL <= 5.99 region on a 10 yr x 0.1 deg grid within +-2500 yr, +-8 deg")


def m3_ll(theta, R, v, y, cal, w=2.0):
    """theta (..., N) distance from the south pole (deg); R broadcastable."""
    z = (theta - R) / w
    sig = 1.0 / (1.0 + np.exp(-z))
    P = (1 - 2 * EPS) * p_base(v, cal) * sig + EPS
    return np.where(y > 0, np.log(P), np.log1p(-P))


def fit_m3(S, cal):
    Rs = np.round(np.arange(20.0, 65.0 + 1e-9, 0.5), 6)
    wsum = S["w"]

    def L_for(ts):
        out = np.empty((len(ts), len(Rs)))
        for i in range(0, len(ts), 8):
            dec = declinations(S["u0"], S["vel"], ts[i:i + 8])
            ll = m3_ll(90.0 + dec[:, None, :], Rs[None, :, None], S["v"], S["y"], cal)
            out[i:i + 8] = ll @ wsum
        return out

    ts = np.arange(T_LO, T_HI + 0.1, 50.0)
    L = L_for(ts)
    i, j = argmax2(L)
    # CHOICE: M3 has no stated refined grid; refine the epoch to 10 yr (+-600 yr), keep R on its 0.5 deg grid.
    tr = ts[i] + np.arange(-600, 601, 10.0)
    tr = tr[(tr >= T_LO) & (tr <= T_HI)]
    Lr = L_for(tr)
    a, b = argmax2(Lr)
    return dict(t=float(tr[a]), R_cap=float(Rs[b]), loglik=float(Lr[a, b]), coarse_t=float(ts[i]))


# ----------------------------------------------------------------------------- M4 free pole
def pole_grid(step=2.0):
    poles, eclc = [], []
    for b in np.arange(-90.0, -40.0 + 1e-9, step):
        n = 1 if b <= -89.999 else max(1, int(round(360.0 * np.cos(b * D2R) / step)))
        for l in np.arange(n) * 360.0 / n:
            poles.append(from_ecliptic(np.array(l), np.array(b)))
            eclc.append((l, b))
    return np.array(poles), np.array(eclc)


def refine_poles(p0, half=2.0, step=0.25):
    p0 = p0 / np.linalg.norm(p0)
    e1 = np.cross([0, 0, 1.0], p0)
    if np.linalg.norm(e1) < 1e-8:
        e1 = np.array([1.0, 0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(p0, e1)
    offs = np.arange(-half, half + 1e-9, step) * D2R
    P = np.array([p0 + a * e1 + b * e2 for a in offs for b in offs])
    return P / np.linalg.norm(P, axis=1, keepdims=True)


def scp_track():
    t = np.arange(-24000.0, 2000.0 + 0.1, 2.0)
    return t, -ltpequ(t)


def offtrack(p):
    t, trk = scp_track()
    c = trk @ p
    k = int(np.argmax(c))
    return float(np.degrees(np.arccos(np.clip(c[k], -1, 1)))), float(t[k])


def m4_m3(S, cal, t0):
    """Free south pole replacing -p_N(t) in M3; stars at epoch t0; R free."""
    u = directions(S["u0"], S["vel"], [t0])[0]
    Rs = np.round(np.arange(20.0, 65.0 + 1e-9, 0.5), 6)

    def best_of(P):
        best = (-np.inf, None, None)
        for i in range(0, len(P), 16):
            theta = np.degrees(np.arccos(np.clip(P[i:i + 16] @ u.T, -1, 1)))  # (c, N)
            L = m3_ll(theta[:, None, :], Rs[None, :, None], S["v"], S["y"], cal) @ S["w"]
            a, b = argmax2(L)
            if L[a, b] > best[0]:
                best = (float(L[a, b]), P[i + a], float(Rs[b]))
        return best

    P, _ = pole_grid(2.0)
    L0, p0, _ = best_of(P)
    L1, p1, R1 = best_of(refine_poles(p0, 2.0, 0.25))
    return p1, R1, L1


def m4_m1(S, cal, kv, t0):
    """Free south pole replacing -p_N(t) in M1 (declination = arcsin(-u(t0).p)); phi free."""
    u = directions(S["u0"], S["vel"], [t0])[0]

    def best_of(P, ps):
        best = (-np.inf, None, None)
        for i in range(0, len(P), 16):
            dec = np.degrees(np.arcsin(np.clip(-(P[i:i + 16] @ u.T), -1, 1)))
            L = star_ll_m1(dec[:, None, :], ps[None, :, None], S["v"], S["y"], cal, kv) @ S["w"]
            a, b = argmax2(L)
            if L[a, b] > best[0]:
                best = (float(L[a, b]), P[i + a], float(ps[b]))
        return best

    ps = np.round(np.arange(PHI_LO, PHI_HI + 1e-9, 0.5), 6)
    P, _ = pole_grid(2.0)
    L0, p0, f0 = best_of(P, ps)
    ps2 = np.round(f0 + np.arange(-20, 21) * 0.2, 6)
    ps2 = ps2[(ps2 >= PHI_LO) & (ps2 <= PHI_HI)]
    L1, p1, f1 = best_of(refine_poles(p0, 2.0, 0.25), ps2)
    return p1, f1, L1


# ----------------------------------------------------------------------------- tiles
def tiles(lam, bet):
    edges = np.arange(-90.0, 30.0 + 1e-9, 15.0)
    tid = np.full(len(lam), -1)
    k = 0
    info = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        n = int(round(24 * np.cos((lo + hi) / 2 * D2R)))
        inband = (bet >= lo) & ((bet < hi) if hi < 30 else (bet <= hi))
        sec = np.minimum((lam / (360.0 / n)).astype(int), n - 1)
        tid[inband] = k + sec[inband]
        info.append((lo, hi, n))
        k += n
    return tid, k, info


# ----------------------------------------------------------------------------- main
def main():
    t_start = time.time()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    nboot = 500
    if "--boot" in sys.argv:
        nboot = int(sys.argv[sys.argv.index("--boot") + 1])
        args = [a for a in args if a != str(nboot)]
    do_m4 = "--no-m4" not in sys.argv
    f_pt, f_hip, f_out = args[:3]

    hipd = load_hip(f_hip)
    pt = load_ptolemy(f_pt)
    valid = np.isfinite(hipd["ra"]) & np.isfinite(hipd["de"]) & np.isfinite(hipd["v"])

    # Catalogue definitions -> sets of HIP numbers
    def hips(cond):
        return {r["HIP"] for r in pt if r["HIP"] is not None and r["I"] is not None and cond(r)}

    defs = {
        "all48": hips(lambda r: r["I"] in (1, 2, 3)),
        "in_figure": hips(lambda r: r["I"] in (1, 2, 3) and r["fN"] == ""),
        "aratus_core": hips(lambda r: r["I"] in (1, 2, 3) and r["fN"] == "" and r["cst"] not in ("=Equ", "=CrA")),
        "strict_id": hips(lambda r: r["I"] in (1, 2)),
    }

    u0_all = unit(hipd["ra"], hipd["de"])
    vel_all = pm_velocity(hipd["ra"], hipd["de"], hipd["pma"], hipd["pmd"])
    u2000 = directions(u0_all, vel_all, [2000.0])[0]
    lam_all, bet_all = to_ecliptic(u2000)  # CHOICE: J2000 mean ecliptic, star positions at J2000.0
    dec2000_all = np.degrees(np.arcsin(np.clip(u2000[:, 2], -1, 1)))
    tid_all, ntiles, tinfo = tiles(lam_all, bet_all)

    out = dict(replicator="Claude Opus 5.5 (Anthropic), 2026-11-23, from protocol.md + MANIFEST.md only",
               tools=dict(python=sys.version.split()[0], numpy=np.__version__,
                          precession="own implementation of Vondrak+2011 ltpequ (ltp.py), checked vs pyerfa 2.0.1.5 to 0.005 arcsec"))
    out["sizes"] = dict(hip_rows=int(hipd["n_rows"]), hip_valid=int(valid.sum()), ptolemy_rows=len(pt))
    out["sizes"]["unique_hip_per_definition_any_mag"] = {k: len(v) for k, v in defs.items()}

    def make_set(defn, vcut, region):
        m = valid & (hipd["v"] <= vcut)
        if region == "cap":
            m &= bet_all > 30.0
        elif region == "test":
            m &= bet_all <= 30.0
        y = np.isin(hipd["hip"], list(defs[defn])).astype(float)
        S = dict(idx=np.nonzero(m)[0])
        S.update(u0=u0_all[m], vel=vel_all[m], v=hipd["v"][m], y=y[m], hip=hipd["hip"][m],
                 tile=tid_all[m], w=np.ones(m.sum()))
        return S

    univ55 = valid & (hipd["v"] <= 5.5)
    out["sizes"]["universe_V<=5.5"] = int(univ55.sum())
    out["sizes"]["universe_V<=5.5_unique_HIP"] = int(len(np.unique(hipd["hip"][univ55])))
    out["sizes"]["catalogued_in_universe_V<=5.5"] = {k: int(np.isin(hipd["hip"][univ55], list(v)).sum()) for k, v in defs.items()}
    out["sizes"]["cap_beta>30_V<=5.5"] = int((univ55 & (bet_all > 30)).sum())
    out["sizes"]["test_beta<=30_V<=5.5"] = int((univ55 & (bet_all <= 30)).sum())
    out["sizes"]["tiles"] = dict(n=ntiles, bands=[list(x) for x in tinfo],
                                 nonempty_test_V55=int(len(np.unique(tid_all[univ55 & (bet_all <= 30)]))))

    # Calibrations
    cal = {}
    for d in defs:
        C = make_set(d, 5.5, "cap")
        cal[d] = fit_logistic(C["v"], C["y"])
    out["calibration"] = cal
    print("calibration", cal, flush=True)

    KV0 = 0.25
    S0 = make_set("all48", 5.5, "test")
    prim = fit_m1(S0, cal["all48"], KV0)
    phi3k, L3k = profile_phi_at(S0, cal["all48"], KV0, T_3000BCE)
    prim["at_3000BCE"] = dict(t=T_3000BCE, best_phi=phi3k, loglik=L3k, dlnL_vs_best=L3k - prim["loglik"])
    out["M1_primary"] = prim
    print("M1 primary", prim, time.time() - t_start, flush=True)
    out["M1_primary"]["star_level_CI95"] = star_level_ci(S0, cal["all48"], KV0, prim)

    # Sensitivity: kV
    out["M1_kV"] = {}
    for kv in [0.15, 0.20, 0.25, 0.30, 0.35]:
        out["M1_kV"][f"{kv:.2f}"] = prim if kv == KV0 else fit_m1(S0, cal["all48"], kv)
        print("kV", kv, out["M1_kV"][f"{kv:.2f}"]["t"], out["M1_kV"][f"{kv:.2f}"]["phi"], flush=True)
    # Catalogue definitions
    out["M1_definition"] = {}
    for d in defs:
        Sd = make_set(d, 5.5, "test")
        out["M1_definition"][d] = prim if d == "all48" else fit_m1(Sd, cal[d], KV0)
        out["M1_definition"][d]["n_catalogued_test"] = int(Sd["y"].sum())
        print("def", d, out["M1_definition"][d]["t"], out["M1_definition"][d]["phi"], flush=True)
    # Magnitude cut-offs (CHOICE: calibration stays the V<=5.5 cap fit; the cut-off applies to the test set)
    out["M1_vcut"] = {}
    out["M1_vcut_recalibrated_sidecheck"] = {}
    for vc in [4.0, 4.5, 5.0, 5.5]:
        Sv = make_set("all48", vc, "test")
        r = prim if vc == 5.5 else fit_m1(Sv, cal["all48"], KV0)
        r = dict(r)
        r["n_test"] = int(len(Sv["v"]))
        r["n_catalogued_test"] = int(Sv["y"].sum())
        out["M1_vcut"][f"{vc:.1f}"] = r
        if vc < 5.5:
            Cv = make_set("all48", vc, "cap")
            calv = fit_logistic(Cv["v"], Cv["y"])
            rr = fit_m1(Sv, calv, KV0)
            rr["calibration"] = calv
            out["M1_vcut_recalibrated_sidecheck"][f"{vc:.1f}"] = rr
        print("vcut", vc, r["t"], r["phi"], flush=True)

    # M2: joint over kV in [0.10, 0.50] step 0.02
    m2 = {}
    for kv in np.round(np.arange(0.10, 0.50 + 1e-9, 0.02), 2):
        m2[f"{kv:.2f}"] = fit_m1(S0, cal["all48"], float(kv))
    kbest = max(m2, key=lambda k: m2[k]["loglik"])
    out["M2"] = dict(best=dict(kV=float(kbest), **m2[kbest]), profile={k: dict(t=v["t"], phi=v["phi"], loglik=v["loglik"]) for k, v in m2.items()})
    print("M2", out["M2"]["best"], time.time() - t_start, flush=True)

    # M3
    out["M3"] = fit_m3(S0, cal["all48"])
    print("M3", out["M3"], flush=True)

    # LOCO
    loco = {}
    csts = sorted({r["cst"] for r in pt})
    hip2dec = dict(zip(hipd["hip"][valid], dec2000_all[valid]))
    for c in csts:
        members = {r["HIP"] for r in pt if r["cst"] == c and r["HIP"] is not None and r["I"] in (1, 2, 3)}
        decs = [hip2dec[h] for h in members if h in hip2dec]
        if not decs or min(decs) >= -15.0:
            continue
        Sx = dict(S0)
        Sx["w"] = np.where(np.isin(S0["hip"], list(members)), 0.0, 1.0)
        r = fit_m1(Sx, cal["all48"], KV0)
        loco[c] = dict(t=r["t"], phi=r["phi"], loglik=r["loglik"], n_dropped=int((Sx["w"] == 0).sum()))
        print("LOCO", c, loco[c], flush=True)
    lt = [v["t"] for v in loco.values()]
    lp = [v["phi"] for v in loco.values()]
    infl = max(loco, key=lambda k: (abs(loco[k]["t"] - prim["t"]), abs(loco[k]["phi"] - prim["phi"])))
    out["LOCO"] = dict(constellations=loco, t_range=[min(lt), max(lt)], phi_range=[min(lp), max(lp)],
                       most_influential=infl, most_influential_shift=dict(dt=loco[infl]["t"] - prim["t"], dphi=loco[infl]["phi"] - prim["phi"]))
    print("LOCO", out["LOCO"]["t_range"], out["LOCO"]["phi_range"], infl, time.time() - t_start, flush=True)

    # Spatial block bootstrap
    W1 = np.zeros((len(S0["v"]), ntiles))
    W1[np.arange(len(S0["v"])), S0["tile"]] = 1.0
    ts, ps = grid_coarse()
    Tc = tile_ll_m1(S0, cal["all48"], KV0, ts, ps, W1)
    assert abs(Tc.sum(-1).max() - prim["coarse_loglik"]) < 1e-6
    rng = np.random.default_rng(20261123)
    cache = {}
    bt, bp = [], []
    for b in range(nboot):
        cnt = np.bincount(rng.integers(0, ntiles, size=ntiles), minlength=ntiles).astype(float)
        L = Tc @ cnt
        i, j = argmax2(L)
        key = (i, j)
        if key not in cache:
            tr, pr = grid_refined(ts[i], ps[j])
            cache[key] = (tr, pr, tile_ll_m1(S0, cal["all48"], KV0, tr, pr, W1))
        tr, pr, Tr = cache[key]
        a, c2 = argmax2(Tr @ cnt)
        bt.append(tr[a])
        bp.append(pr[c2])
    bt, bp = np.array(bt), np.array(bp)
    out["bootstrap"] = dict(B=nboot, seed=20261123,
                            draw="numpy default_rng(seed).integers(0, n_tiles, n_tiles) per resample, all %d tiles" % ntiles,
                            t_CI95=[float(np.percentile(bt, 2.5)), float(np.percentile(bt, 97.5))],
                            phi_CI95=[float(np.percentile(bp, 2.5)), float(np.percentile(bp, 97.5))],
                            t_CI68=[float(np.percentile(bt, 16)), float(np.percentile(bt, 84))],
                            phi_CI68=[float(np.percentile(bp, 16)), float(np.percentile(bp, 84))],
                            t_median=float(np.median(bt)), phi_median=float(np.median(bp)),
                            frac_t_below_3000BCE=float(np.mean(bt <= T_3000BCE)),
                            n_unique_coarse_maxima=len(cache))
    print("bootstrap", out["bootstrap"], time.time() - t_start, flush=True)

    # M4
    if do_m4:
        p3, R3, L3 = m4_m3(S0, cal["all48"], out["M3"]["t"])
        off3, toff3 = offtrack(p3)
        lam3, bet3 = to_ecliptic(p3)
        p1, f1, L1 = m4_m1(S0, cal["all48"], KV0, prim["t"])
        off1, toff1 = offtrack(p1)
        lam1, bet1 = to_ecliptic(p1)
        out["M4"] = dict(
            M3_free_pole=dict(pole_ecl=[float(lam3), float(bet3)], R_cap=R3, loglik=L3, offtrack_deg=off3,
                              closest_track_epoch=toff3, two_dlnL=2 * (L3 - out["M3"]["loglik"])),
            M1_free_pole=dict(pole_ecl=[float(lam1), float(bet1)], phi=f1, loglik=L1, offtrack_deg=off1,
                              closest_track_epoch=toff1, two_dlnL=2 * (L1 - prim["loglik"])),
        )
        print("M4", out["M4"], time.time() - t_start, flush=True)

    # Systematic envelope and verdict
    var = [(f"M1 kV={k}", v["t"], v["phi"]) for k, v in out["M1_kV"].items()]
    var += [("M2", out["M2"]["best"]["t"], out["M2"]["best"]["phi"])]
    var += [("M3", out["M3"]["t"], None)]
    var += [(f"def {k}", v["t"], v["phi"]) for k, v in out["M1_definition"].items()]
    var += [(f"V<={k}", v["t"], v["phi"]) for k, v in out["M1_vcut"].items()]
    st = [x[1] for x in var]
    sp = [x[2] for x in var if x[2] is not None]
    env = dict(t=[min(st), max(st)], phi=[min(sp), max(sp)], variants=[dict(name=n, t=t, phi=p) for n, t, p in var])
    out["systematic_envelope"] = env
    bt95, bp95 = out["bootstrap"]["t_CI95"], out["bootstrap"]["phi_CI95"]
    comb_t = [min(bt95[0], env["t"][0]), max(bt95[1], env["t"][1])]
    comb_p = [min(bp95[0], env["phi"][0]), max(bp95[1], env["phi"][1])]
    out["combined"] = dict(t=comb_t, phi=comb_p, t_BCE=[1 - comb_t[0], 1 - comb_t[1]])
    off = None
    if do_m4:
        off = max(out["M4"]["M3_free_pole"]["offtrack_deg"], out["M4"]["M1_free_pole"]["offtrack_deg"])
    offok = (off is None) or off <= 6.0
    if comb_t[0] > T_3000BCE and offok:
        verdict = "1: excludes pre-3000 BCE"
    elif comb_t[1] < T_3000BCE and offok:
        verdict = "2: requires pre-3000 BCE"
    else:
        verdict = "3: undetermined / spans 3000 BCE (or off-track)"
    out["verdict"] = dict(rule=verdict, t_lo=comb_t[0], t_hi=comb_t[1], offtrack_used=off,
                          offtrack_note="max of the M3- and M1-based free-pole offsets (CHOICE)")
    out["runtime_s"] = time.time() - t_start
    print("verdict", out["verdict"], out["combined"], flush=True)
    with open(f_out, "w") as fh:
        json.dump(out, fh, indent=1, default=float)


if __name__ == "__main__":
    main()
