#!/usr/bin/env python3
"""Pre-registered Khipu Rosetta Hunt across all 619 khipus in OKR khipu.db (#13).

Implements questions/khipu/protocol.md (locked in protocol.lock).
1. Independent knot-value decoding (knot_value_type cross-checked against Locke/Ascher base-10 rules).
2. Full audit & combinatorial/corpus false-positive calibration of the 1670 Santa Valley match.
3. Corpus-wide Internal Rosetta Hunt across all 191,271 khipu pairs (blind Puruchuco recovery gate,
   exact/near-exact copies & mirrors, unprovenanced-to-provenanced matches, and 2/3-child summation
   hierarchies), calibrated against permutation nulls.
4. Provenance-level Rosetta-readiness census across all 619 khipus.
"""
from __future__ import annotations

import collections
import itertools
import json
import math
import pathlib
import sqlite3
from typing import Any

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "khipu.db"
RES = ROOT / "results"


def decode_cord_locke_ascher(clusters: list[list[tuple[str, float, float]]]) -> int | None:
    """Independently decode a cord's base-10 value from ordered knot clusters.

    Each cluster is a list of (type_code, num_turns, start_pos) ordered from primary cord outward.
    Locke (1912) / Ascher & Ascher rules:
    - Units position (lowest/outermost): 'E' = 1, 'L' = num_turns (2..9), 'EE' = 1.
    - Higher powers of 10: 'S' knots each count 1 * 10^p.
    Returns None if non-standard knots prevent unambiguous base-10 decoding.
    """
    if not clusters:
        return 0
    # Identify if bottom cluster is units (contains E or L)
    # Process clusters from outermost (bottom) to top
    parsed = []
    for cl in clusters:
        types = [t.strip().upper() for t, _, _ in cl if t]
        if not types:
            continue
        if any(t in ("E", "EE") for t in types):
            val = sum(1 for t in types if t in ("E", "EE"))
            parsed.append(("U", val))
        elif any(t in ("L", "LL") for t in types):
            val = 0
            for t, nt, _ in cl:
                tu = (t or "").strip().upper()
                if tu in ("L", "LL"):
                    val += int(round(nt)) if nt and nt > 0 else 1
            parsed.append(("U", val))
        elif all(t == "S" for t in types):
            parsed.append(("S", len(types)))
        else:
            return None
    if not parsed:
        return 0
    # Standard decimal assignment: if last cluster is 'U', it's 10^0, preceding 'S' are 10^1, 10^2, ...
    # If all are 'S', without spatial gaps we cannot distinguish 10s vs 100s unambiguously; assign from 10^1 upward
    total = 0
    if parsed[-1][0] == "U":
        total += parsed[-1][1]
        power = 1
        for kind, val in reversed(parsed[:-1]):
            if kind != "S":
                return None
            total += val * (10 ** power)
            power += 1
        return total
    return None


def load_corpus(db_path: pathlib.Path = DB_PATH) -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()

    # Load archive names
    archive_names = {int(r[0]): r[1] for r in cur.execute("SELECT ARCHIVE_NUM, ARCHIVE_NAME FROM archive_dc")}

    # Load khipu metadata
    khipus: dict[int, dict[str, Any]] = {}
    for row in cur.execute(
        """
        SELECT KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM, PROVENANCE, REGION, ARCHIVE_NUM,
               DUPLICATE_FLAG, DUPLICATE_ID, COMPLETE, MUSEUM_NAME, MUSEUM_NUM
        FROM khipu_main
        """
    ):
        kid = int(row[0])
        arch = int(row[5]) if row[5] not in (None, "", 0, 0.0) else None
        khipus[kid] = {
            "khipu_id": kid,
            "okr_num": row[1] or "",
            "inv_num": row[2] or "",
            "provenance": (row[3] or "").strip(),
            "region": (row[4] or "").strip(),
            "archive_num": arch,
            "archive_name": archive_names.get(arch, "") if arch is not None else "",
            "duplicate_flag": row[6],
            "duplicate_id": row[7],
            "complete": row[8],
            "museum": row[9] or "",
            "pendants": [],
            "clusters": [],
        }

    # Load cord cluster ordinals
    cluster_ord: dict[int, int] = {}
    for cid, ord_val in cur.execute("SELECT CLUSTER_ID, ORDINAL FROM cord_cluster"):
        cluster_ord[int(cid)] = int(ord_val) if ord_val is not None else 0

    # Load cord primary colors
    cord_color: dict[int, str] = {}
    for cid, fcol, c1 in cur.execute("SELECT CORD_ID, FULL_COLOR, COLOR_CD_1 FROM ascher_cord_color"):
        cid_i = int(cid)
        if cid_i not in cord_color:
            cord_color[cid_i] = (fcol or c1 or "").strip()

    # Load knots per cord
    cord_kvt_sum: dict[int, int] = collections.defaultdict(int)
    cord_knot_clusters: dict[int, dict[int, list[tuple[str, float, float]]]] = collections.defaultdict(
        lambda: collections.defaultdict(list)
    )
    kc_pos: dict[int, tuple[int, float]] = {}
    for kcid, ord_v, spos in cur.execute("SELECT CLUSTER_ID, ORDINAL, START_POS FROM knot_cluster"):
        kc_pos[int(kcid)] = (int(ord_v) if ord_v is not None else 0, float(spos) if spos is not None else 0.0)

    n_knots_total = 0
    n_knots_kvt = 0
    for cid, tcode, nturns, kvt, kcid in cur.execute(
        "SELECT CORD_ID, TYPE_CODE, NUM_TURNS, knot_value_type, CLUSTER_ID FROM knot"
    ):
        n_knots_total += 1
        cid_i = int(cid)
        if kvt is not None and kvt != "":
            try:
                v = int(float(kvt))
                if v > 0:
                    cord_kvt_sum[cid_i] += v
                    n_knots_kvt += 1
            except ValueError:
                pass
        kcid_i = int(kcid) if kcid is not None else 0
        spos = kc_pos.get(kcid_i, (0, 0.0))[1]
        cord_knot_clusters[cid_i][kcid_i].append((str(tcode or ""), float(nturns or 0.0), spos))

    # Load level-1 pendant cords ordered cleanly
    pendants_by_khipu: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    locke_checked = 0
    locke_exact = 0
    for row in cur.execute(
        """
        SELECT KHIPU_ID, CORD_ID, CLUSTER_ID, CLUSTER_ORDINAL, CORD_ORDINAL,
               ATTACHMENT_TYPE, CORD_LEVEL, INVESTIGATOR_CORD_NUM
        FROM cord
        WHERE CORD_LEVEL = 1
        """
    ):
        kid = int(row[0])
        if kid not in khipus:
            continue
        cid = int(row[1])
        clid = int(row[2]) if row[2] is not None else 0
        cl_ord = cluster_ord.get(clid, 0)
        cord_cl_ord = int(row[3]) if row[3] is not None else 0
        cord_ord = int(row[4]) if row[4] is not None else 0
        att = (row[5] or "").strip().upper()
        val = int(cord_kvt_sum.get(cid, 0))

        # Cross-check Locke/Ascher decoder on cords with units-position E/L knots
        if cid in cord_knot_clusters:
            ordered_kcs = sorted(
                cord_knot_clusters[cid].items(),
                key=lambda kv: (kc_pos.get(kv[0], (0, 0.0))[0], kc_pos.get(kv[0], (0, 0.0))[1]),
            )
            la_val = decode_cord_locke_ascher([knots for _, knots in ordered_kcs])
            if la_val is not None:
                locke_checked += 1
                if la_val == val:
                    locke_exact += 1

        pendants_by_khipu[kid].append({
            "cord_id": cid,
            "cluster_id": clid,
            "cluster_ord": cl_ord,
            "cord_cl_ord": cord_cl_ord,
            "cord_ord": cord_ord,
            "att": att,
            "color": cord_color.get(cid, ""),
            "val": val,
            "inv_cord": row[7] or "",
        })

    for kid, plist in pendants_by_khipu.items():
        plist.sort(key=lambda c: (c["cord_ord"], c["cluster_ord"], c["cord_cl_ord"], c["cord_id"]))
        khipus[kid]["pendants"] = plist
        # Build cluster-sum vector
        cl_sums = []
        cur_cl = None
        cur_sum = 0
        cur_len = 0
        for c in plist:
            if cur_cl is None or c["cluster_id"] != cur_cl:
                if cur_cl is not None:
                    cl_sums.append((cur_cl, cur_len, cur_sum))
                cur_cl = c["cluster_id"]
                cur_sum = c["val"]
                cur_len = 1
            else:
                cur_sum += c["val"]
                cur_len += 1
        if cur_cl is not None:
            cl_sums.append((cur_cl, cur_len, cur_sum))
        khipus[kid]["clusters"] = cl_sums

    con.close()
    meta = {
        "n_khipus": len(khipus),
        "n_khipus_with_pendants": sum(1 for k in khipus.values() if k["pendants"]),
        "n_pendants_total": sum(len(k["pendants"]) for k in khipus.values()),
        "n_knots_total": n_knots_total,
        "n_knots_kvt_populated": n_knots_kvt,
        "locke_ascher_crosscheck_n": locke_checked,
        "locke_ascher_exact_match_n": locke_exact,
        "locke_ascher_exact_pct": round(100.0 * locke_exact / max(1, locke_checked), 2),
    }
    return khipus, meta


def best_moiety_partition_error(pachaca_counts: list[int], target_v: int, target_r: int) -> tuple[int, int, tuple[int, int]]:
    """Find best 3-vs-3 partition of 6 pachacas against (target_v, target_r).

    Returns (min_L1_error, min_abs_v_diff, (sum_A, sum_B)).
    """
    n = len(pachaca_counts)
    total = sum(pachaca_counts)
    best_l1 = 10**9
    best_dv = 10**9
    best_pair = (0, 0)
    for comb in itertools.combinations(range(n), n // 2):
        s_a = sum(pachaca_counts[i] for i in comb)
        s_b = total - s_a
        for a, b in ((s_a, s_b), (s_b, s_a)):
            l1 = abs(a - target_v) + abs(b - target_r)
            dv = abs(a - target_v)
            if l1 < best_l1 or (l1 == best_l1 and dv < best_dv):
                best_l1 = l1
                best_dv = dv
                best_pair = (a, b)
    return best_l1, best_dv, best_pair


def run_santa_valley_audit(khipus: dict[int, dict[str, Any]], rng: np.random.Generator) -> dict[str, Any]:
    """Test 1: Independent Santa Valley audit + combinatorial & corpus-wide false-positive calibration."""
    santa = sorted(
        [k for k in khipus.values() if k["provenance"] == "Santa"],
        key=lambda x: x["okr_num"],
    )
    per_khipu = []
    tot_pendants = 0
    tot_clusters = 0
    tot_6cord_groups = 0
    tot_first_cord_sum = 0
    tot_all_cord_sum = 0
    group_r_count = 0
    group_v_count = 0
    group_other_count = 0
    cord_r_count = 0
    cord_v_count = 0
    verso_first_sum = 0
    recto_first_sum = 0
    verso_all_sum = 0
    recto_all_sum = 0

    for k in santa:
        p = k["pendants"]
        tot_pendants += len(p)
        tot_clusters += len(k["clusters"])
        k_r = sum(1 for c in p if c["att"] == "R")
        k_v = sum(1 for c in p if c["att"] == "V")
        cord_r_count += k_r
        cord_v_count += k_v

        # Segment into 6-cord groups (using cord clusters if size ~6, else consecutive 6-cord color bands)
        # Check actual cluster sizes first
        cl_sizes = collections.Counter(sz for _, sz, _ in k["clusters"])
        # Build groups by 6-cord color-banded runs / fixed 6-cord chunks within clusters
        groups = []
        by_cl = collections.defaultdict(list)
        for c in p:
            by_cl[c["cluster_id"]].append(c)
        for clid, _, _ in k["clusters"]:
            cords = by_cl[clid]
            # Split into chunks of 6 if cluster is a multiple of 6 (or single group if 5..7)
            if len(cords) >= 10:
                for idx in range(0, len(cords), 6):
                    grp = cords[idx:idx + 6]
                    if len(grp) >= 4:
                        groups.append(grp)
            elif len(cords) >= 4:
                groups.append(cords)

        k_first_sum = 0
        k_all_sum = sum(c["val"] for c in p)
        k_g_r = 0
        k_g_v = 0
        for g in groups:
            g_first = g[0]["val"]
            g_sum = sum(c["val"] for c in g)
            k_first_sum += g_first
            # Group attachment = majority R/V (or first cord)
            atts = [c["att"] for c in g if c["att"] in ("R", "V")]
            maj = collections.Counter(atts).most_common(1)[0][0] if atts else ""
            if maj == "V":
                k_g_v += 1
                group_v_count += 1
                verso_first_sum += g_first
                verso_all_sum += g_sum
            elif maj == "R":
                k_g_r += 1
                group_r_count += 1
                recto_first_sum += g_first
                recto_all_sum += g_sum
            else:
                group_other_count += 1

        tot_6cord_groups += len(groups)
        tot_first_cord_sum += k_first_sum
        tot_all_cord_sum += k_all_sum
        per_khipu.append({
            "okr_num": k["okr_num"],
            "inv_num": k["inv_num"],
            "n_pendants": len(p),
            "n_clusters": len(k["clusters"]),
            "cluster_size_hist": dict(cl_sizes),
            "n_groups": len(groups),
            "groups_V": k_g_v,
            "groups_R": k_g_r,
            "cords_V": k_v,
            "cords_R": k_r,
            "first_cord_sum": k_first_sum,
            "all_pendant_sum": k_all_sum,
        })

    # Published 1670 San Pedro de Corongo revisita benchmark (Zevallos Quiñones 1991; FitzPatrick 2024)
    pachacas_1670 = [18, 23, 9, 7, 41, 32]  # Namus, Corongo, Cuyuchin, Cusca, Guauyan, Ucore (sum = 130 named; 132 total)
    obs_v = group_v_count
    obs_r = group_r_count
    obs_best_l1, obs_best_dv, obs_best_pair = best_moiety_partition_error(pachacas_1670, obs_v, obs_r)

    # Combinatorial Monte Carlo calibration (N=20,000) under Dirichlet(1) and Dirichlet(0.5)
    # Test against published Medrano & Urton / FitzPatrick (70, 63) = 133 groups AND raw OKR (obs_v, obs_r)
    mc_results = {}
    for label, alpha in (("dirichlet_1.0_uniform", 1.0), ("dirichlet_0.5_overdispersed", 0.5)):
        n_draws = 20000
        probs = rng.dirichlet([alpha] * 6, size=n_draws)
        rem = 130 - 6
        hit_l1_le5_pub = 0
        hit_l1_le3_pub = 0
        hit_dv_le2 = 0
        hit_dv_le1 = 0
        for row in probs:
            raw = np.floor(row * rem).astype(int)
            diff = rem - int(raw.sum())
            if diff > 0:
                idx = np.argsort(-(row * rem - raw))[:diff]
                raw[idx] += 1
            counts = (raw + 1).tolist()
            l1_pub, dv_pub, _ = best_moiety_partition_error(counts, 70, 63)
            if l1_pub <= 5:
                hit_l1_le5_pub += 1
            if l1_pub <= 3:
                hit_l1_le3_pub += 1
            if dv_pub <= 2:
                hit_dv_le2 += 1
            if dv_pub <= 1:
                hit_dv_le1 += 1
        mc_results[label] = {
            "n_draws": n_draws,
            "target_published_VR": [70, 63],
            "p_L1_le_5_medrano_urton": round(hit_l1_le5_pub / n_draws, 4),
            "p_L1_le_3_fitzpatrick": round(hit_l1_le3_pub / n_draws, 4),
            "p_abs_v_diff_le_2": round(hit_dv_le2 / n_draws, 4),
            "p_abs_v_diff_le_1": round(hit_dv_le1 / n_draws, 4),
        }

    # Corpus-wide random 6-khipu bundle false-positive rate against (132 +/- 5% groups/cords, 367 +/- 30% sum)
    non_santa = [k for k in khipus.values() if k["provenance"] != "Santa" and len(k["pendants"]) >= 5]
    ns_n_cl = np.array([len(k["clusters"]) for k in non_santa])
    ns_n_p = np.array([len(k["pendants"]) for k in non_santa])
    ns_sum = np.array([sum(c["val"] for c in k["pendants"]) for k in non_santa])
    n_bundles = 10000
    bundle_hits_5pct_30pct = 0
    bundle_hits_10pct_30pct = 0
    single_hits_5pct_30pct = 0
    for _ in range(n_bundles):
        idxs = rng.choice(len(non_santa), size=6, replace=False)
        b_cl = int(ns_n_cl[idxs].sum())
        b_sum = int(ns_sum[idxs].sum())
        if (125 <= b_cl <= 139) and (257 <= b_sum <= 477):
            bundle_hits_5pct_30pct += 1
        if (119 <= b_cl <= 145) and (257 <= b_sum <= 477):
            bundle_hits_10pct_30pct += 1
    for i in range(len(non_santa)):
        if (125 <= ns_n_p[i] <= 139 or 125 <= ns_n_cl[i] <= 139) and (257 <= ns_sum[i] <= 477):
            single_hits_5pct_30pct += 1

    return {
        "n_khipus": len(santa),
        "per_khipu": per_khipu,
        "totals": {
            "pendants": tot_pendants,
            "clusters": tot_clusters,
            "six_cord_groups": tot_6cord_groups,
            "groups_verso": group_v_count,
            "groups_recto": group_r_count,
            "groups_other": group_other_count,
            "cords_verso": cord_v_count,
            "cords_recto": cord_r_count,
            "first_cord_sum": tot_first_cord_sum,
            "all_pendant_sum": tot_all_cord_sum,
            "verso_first_cord_sum": verso_first_sum,
            "recto_first_cord_sum": recto_first_sum,
            "verso_all_sum": verso_all_sum,
            "recto_all_sum": recto_all_sum,
            "verso_mean_first": round(verso_first_sum / max(1, group_v_count), 2),
            "recto_mean_first": round(recto_first_sum / max(1, group_r_count), 2),
        },
        "revisita_1670_benchmark": {
            "total_tributaries": 132,
            "named_tributaries": 130,
            "pachacas": pachacas_1670,
            "total_tribute_pesos": 367,
            "observed_first_cord_sum_ratio_to_367": round(tot_first_cord_sum / 367.0, 3),
            "best_3vs3_partition_for_observed_VR": list(obs_best_pair),
            "best_3vs3_L1_error": obs_best_l1,
            "best_3vs3_abs_v_diff": obs_best_dv,
        },
        "combinatorial_moiety_null": mc_results,
        "corpus_spurious_bundle_null": {
            "n_random_6khipu_bundles": n_bundles,
            "match_132_5pct_and_367_30pct_rate": round(bundle_hits_5pct_30pct / n_bundles, 4),
            "match_132_10pct_and_367_30pct_rate": round(bundle_hits_10pct_30pct / n_bundles, 4),
            "single_khipu_matches_out_of_non_santa": single_hits_5pct_30pct,
        },
    }


def score_aligned_window(a: np.ndarray, b: np.ndarray) -> dict[str, Any] | None:
    """Evaluate a contiguous aligned slice (same length L >= 6) of two integer cord vectors."""
    L = len(a)
    if L < 6:
        return None
    mx = np.maximum(a, b)
    sum_mx = int(mx.sum())
    if sum_mx < 20:
        return None
    nz_a = set(int(x) for x in a if x > 0)
    nz_b = set(int(x) for x in b if x > 0)
    if len(nz_a) < 4 or len(nz_b) < 4:
        return None
    diff = np.abs(a - b)
    tol = np.maximum(1, np.floor(0.02 * mx).astype(np.int64))
    near_mask = diff <= tol
    exact_mask = diff == 0
    f_near = float(near_mask.mean())
    if f_near < 0.85:
        return None
    err_l1 = float(diff.sum()) / float(sum_mx)
    if err_l1 > 0.05:
        return None
    f_exact = float(exact_mask.mean())
    tier = "A" if ((err_l1 <= 0.02 and L >= 8) or (err_l1 == 0.0 and L >= 6)) else "B"
    return {
        "L": L,
        "n_distinct_nz_a": len(nz_a),
        "n_distinct_nz_b": len(nz_b),
        "sum_a": int(a.sum()),
        "sum_b": int(b.sum()),
        "f_exact": round(f_exact, 4),
        "f_near": round(f_near, 4),
        "err_l1": round(err_l1, 5),
        "tier": tier,
    }


def build_pos_index(arr: np.ndarray, min_val: int = 3, max_freq: int = 16) -> dict[int, list[int]]:
    pos: dict[int, list[int]] = collections.defaultdict(list)
    for i, val in enumerate(arr):
        iv = int(val)
        if iv >= min_val:
            pos[iv].append(i)
    return {k: v for k, v in pos.items() if len(v) <= max_freq}


def best_contiguous_match(
    v1: np.ndarray,
    v2: np.ndarray,
    allow_reverse: bool = True,
    pos1: dict[int, list[int]] | None = None,
    pos2_fwd: dict[int, list[int]] | None = None,
    pos2_rev: dict[int, list[int]] | None = None,
) -> dict[str, Any] | None:
    """Find best contiguous window alignment (L >= 6, >= 4 distinct non-zero values) between v1 and v2."""
    n1, n2 = len(v1), len(v2)
    if n1 < 6 or n2 < 6:
        return None

    if pos1 is None:
        pos1 = build_pos_index(v1)
    if not pos1:
        return None

    orientations = [(v2, "fwd", pos2_fwd if pos2_fwd is not None else build_pos_index(v2))]
    if allow_reverse:
        v2r = v2[::-1]
        orientations.append((v2r, "rev", pos2_rev if pos2_rev is not None else build_pos_index(v2r)))

    best: dict[str, Any] | None = None
    for arr2, orient, p2 in orientations:
        if not p2:
            continue
        diag_votes: dict[int, int] = {}
        for iv, p1_list in pos1.items():
            for dv in (iv, iv - 1, iv + 1):
                p2_list = p2.get(dv)
                if not p2_list:
                    continue
                if len(p1_list) * len(p2_list) > 120:
                    continue
                for i in p1_list:
                    for j in p2_list:
                        d = i - j
                        diag_votes[d] = diag_votes.get(d, 0) + 1

        if not diag_votes:
            continue
        cand_diags = [d for d, v in diag_votes.items() if v >= 3]
        if not cand_diags:
            continue
        if len(cand_diags) > 12:
            cand_diags = sorted(cand_diags, key=lambda d: -diag_votes[d])[:12]

        for d in cand_diags:
            i0 = max(0, d)
            j0 = max(0, -d)
            ov = min(n1 - i0, n2 - j0)
            if ov < 6:
                continue
            a = v1[i0:i0 + ov]
            b = arr2[j0:j0 + ov]
            mx = np.maximum(a, b)
            tol = np.maximum(1, np.floor(0.02 * mx).astype(np.int64))
            near = (np.abs(a - b) <= tol)
            if int(near.sum()) < 5:
                continue
            candidates = [(0, ov)]
            run_start = None
            misses = 0
            for idx in range(ov):
                if near[idx]:
                    if run_start is None:
                        run_start = idx
                    misses = 0
                else:
                    if run_start is not None:
                        misses += 1
                        if misses > 1:
                            end = idx - misses + 1
                            if end - run_start >= 6:
                                candidates.append((run_start, end))
                            run_start = None
                            misses = 0
            if run_start is not None:
                end = ov - misses
                if end - run_start >= 6:
                    candidates.append((run_start, end))

            for s, e in candidates:
                while s < e and a[s] == 0 and b[s] == 0:
                    s += 1
                while e > s and a[e - 1] == 0 and b[e - 1] == 0:
                    e -= 1
                if e - s < 6:
                    continue
                sc = score_aligned_window(a[s:e], b[s:e])
                if sc is None:
                    continue
                sc["orient"] = orient
                sc["offset_a"] = int(i0 + s)
                sc["offset_b"] = int(j0 + s)
                sc["sample_a"] = [int(x) for x in a[s:min(e, s + 12)]]
                sc["sample_b"] = [int(x) for x in b[s:min(e, s + 12)]]
                if best is None or (sc["tier"] == "A" and best["tier"] != "A") or (
                    sc["tier"] == best["tier"] and (sc["L"], -sc["err_l1"]) > (best["L"], -best["err_l1"])
                ):
                    best = sc
    return best


def run_pairwise_copy_hunt(khipus: dict[int, dict[str, Any]], rng: np.random.Generator) -> dict[str, Any]:
    """Test 2a: All-pairs copy/mirror hunt across all 619 khipus (pendant vectors + cluster-sum vectors)."""
    ids = sorted(khipus.keys())
    p_vecs: dict[int, np.ndarray] = {}
    g_vecs: dict[int, np.ndarray] = {}
    for kid in ids:
        pv = np.array([c["val"] for c in khipus[kid]["pendants"]], dtype=np.int64)
        if len(pv) >= 6 and len({int(x) for x in pv if x > 0}) >= 4 and int(pv.sum()) >= 20:
            p_vecs[kid] = pv
        gv = np.array([s for _, _, s in khipus[kid]["clusters"]], dtype=np.int64)
        if len(gv) >= 6 and len({int(x) for x in gv if x > 0}) >= 4 and int(gv.sum()) >= 20:
            g_vecs[kid] = gv

    def scan_vec_map(vmap: dict[int, np.ndarray], mode_name: str) -> list[dict[str, Any]]:
        ekids = sorted(vmap.keys())
        pos_fwd = {kid: build_pos_index(vmap[kid]) for kid in ekids}
        pos_rev = {kid: build_pos_index(vmap[kid][::-1]) for kid in ekids}
        val_sets = {kid: set(pos_fwd[kid].keys()) for kid in ekids}
        val_sets_near = {}
        for kid, s in val_sets.items():
            ns = set(s)
            for x in s:
                ns.add(x - 1)
                ns.add(x + 1)
            val_sets_near[kid] = ns

        hits = []
        for i in range(len(ekids)):
            ka = ekids[i]
            sa = val_sets[ka]
            if len(sa) < 3:
                continue
            va = vmap[ka]
            pa_idx = pos_fwd[ka]
            for j in range(i + 1, len(ekids)):
                kb = ekids[j]
                if len(sa & val_sets_near[kb]) < 3:
                    continue
                res = best_contiguous_match(va, vmap[kb], allow_reverse=True, pos1=pa_idx, pos2_fwd=pos_fwd[kb], pos2_rev=pos_rev[kb])
                if res is not None:
                    ma, mb = khipus[ka], khipus[kb]
                    is_puru = (ma["archive_num"] == 301 and mb["archive_num"] == 301)
                    is_dup_id = (
                        (ma["duplicate_id"] not in (None, "", 0, 0.0) and ma["duplicate_id"] == mb["khipu_id"])
                        or (mb["duplicate_id"] not in (None, "", 0, 0.0) and mb["duplicate_id"] == ma["khipu_id"])
                    )
                    pa = ma["provenance"].lower()
                    pb = mb["provenance"].lower()
                    unp_a = pa in ("", "unknown", "peru")
                    unp_b = pb in ("", "unknown", "peru")
                    if is_puru:
                        cat = "known_puruchuco"
                    elif is_dup_id:
                        cat = "existing_duplicate_id"
                    elif unp_a != unp_b:
                        cat = "novel_unprovenanced_to_provenanced"
                    elif (not unp_a) and pa == pb:
                        cat = "novel_same_provenance"
                    elif (not unp_a) and (not unp_b) and pa != pb:
                        cat = "novel_cross_provenance"
                    else:
                        cat = "novel_both_unprovenanced"

                    hits.append({
                        "mode": mode_name,
                        "khipu_a": ma["okr_num"],
                        "inv_a": ma["inv_num"],
                        "prov_a": ma["provenance"] or "unknown",
                        "arch_a": ma["archive_name"],
                        "khipu_b": mb["okr_num"],
                        "inv_b": mb["inv_num"],
                        "prov_b": mb["provenance"] or "unknown",
                        "arch_b": mb["archive_name"],
                        "category": cat,
                        **res,
                    })
        hits.sort(key=lambda h: (0 if h["tier"] == "A" else 1, -h["L"], h["err_l1"]))
        return hits

    hits_p = scan_vec_map(p_vecs, "pendant")
    hits_g = scan_vec_map(g_vecs, "cluster_sum")

    ekids = sorted(p_vecs.keys())
    n_pairs_elig = len(ekids) * (len(ekids) - 1) // 2
    null_pair_tests = 100000
    null_hits_a = 0
    null_hits_b = 0

    shuf_banks = []
    for _ in range(10):
        d_s, pf, pr = {}, {}, {}
        for kid in ekids:
            arr = p_vecs[kid].copy()
            rng.shuffle(arr)
            d_s[kid] = arr
            pf[kid] = build_pos_index(arr)
            pr[kid] = build_pos_index(arr[::-1])
        shuf_banks.append((d_s, pf, pr))

    vsets = {kid: set(shuf_banks[0][1][kid].keys()) for kid in ekids}
    vsets_near = {}
    for kid, s in vsets.items():
        ns = set(s)
        for x in s:
            ns.add(x - 1)
            ns.add(x + 1)
        vsets_near[kid] = ns

    for t in range(null_pair_tests):
        d_s, pf, pr = shuf_banks[t % 10]
        ia = int(rng.integers(0, len(ekids)))
        ib = int(rng.integers(0, len(ekids) - 1))
        if ib >= ia:
            ib += 1
        ka, kb = ekids[ia], ekids[ib]
        if len(vsets[ka] & vsets_near[kb]) < 3:
            continue
        res = best_contiguous_match(d_s[ka], d_s[kb], allow_reverse=True, pos1=pf[ka], pos2_fwd=pf[kb], pos2_rev=pr[kb])
        if res is not None:
            if res["tier"] == "A":
                null_hits_a += 1
            else:
                null_hits_b += 1

    exp_fp_a = (null_hits_a / null_pair_tests) * n_pairs_elig
    exp_fp_b = ((null_hits_a + null_hits_b) / null_pair_tests) * n_pairs_elig

    obs_a = sum(1 for h in hits_p if h["tier"] == "A")
    obs_all = len(hits_p)
    fdr_a = min(1.0, exp_fp_a / max(1, obs_a))
    fdr_all = min(1.0, exp_fp_b / max(1, obs_all))

    return {
        "n_eligible_pendant_khipus": len(p_vecs),
        "n_eligible_cluster_khipus": len(g_vecs),
        "n_total_pairs_all_619": 619 * 618 // 2,
        "n_eligible_pairs_pendant": n_pairs_elig,
        "pendant_hits_total": len(hits_p),
        "pendant_hits_tier_A": obs_a,
        "cluster_hits_total": len(hits_g),
        "cluster_hits_tier_A": sum(1 for h in hits_g if h["tier"] == "A"),
        "null_calibration": {
            "null_pair_tests": null_pair_tests,
            "null_hits_tier_A": null_hits_a,
            "null_hits_tier_B": null_hits_b,
            "expected_corpus_FP_tier_A": round(exp_fp_a, 3),
            "expected_corpus_FP_all": round(exp_fp_b, 3),
            "estimated_FDR_tier_A": round(fdr_a, 5),
            "estimated_FDR_all": round(fdr_all, 5),
        },
        "pendant_hits_by_category": dict(collections.Counter(h["category"] for h in hits_p)),
        "pendant_tier_A_by_category": dict(collections.Counter(h["category"] for h in hits_p if h["tier"] == "A")),
        "pendant_hits": hits_p,
        "cluster_hits": hits_g,
    }


def find_summation_hierarchies(khipus: dict[int, dict[str, Any]], rng: np.random.Generator) -> dict[str, Any]:
    """Test 2b: Search for 2-child and 3-child element-wise parent=C1+C2(+C3) summation hierarchies.

    Scans within every provenance/archive group (including Puruchuco as positive control, Pachacamac,
    Incahuasi, Ica, Leymebamba, Huaquerones, Nazca, Armatambo, Santa, and Unknown).
    """
    # Group khipus by archive_num (if set) AND by non-empty provenance
    groups: dict[str, list[int]] = collections.defaultdict(list)
    for kid, k in khipus.items():
        pv = [c["val"] for c in k["pendants"]]
        if len(pv) < 6 or len({x for x in pv if x > 0}) < 4 or max(pv) < 10:
            continue
        if k["archive_num"] is not None:
            groups[f"archive:{k['archive_name']}"].append(kid)
        if k["provenance"]:
            groups[f"prov:{k['provenance']}"].append(kid)

    # Deduplicate group memberships and keep groups with >= 3 eligible khipus
    pvecs = {kid: np.array([c["val"] for c in k["pendants"]], dtype=np.int64) for kid, k in khipus.items()}

    def check_parent_sum(p_arr: np.ndarray, child_sum: np.ndarray, c_arrs: list[np.ndarray]) -> dict[str, Any] | None:
        L = len(p_arr)
        if L < 6:
            return None
        s_p = int(p_arr.sum())
        if s_p < 30:
            return None
        if len({int(x) for x in p_arr if x > 0}) < 4:
            return None
        # Every child must contribute >= 10% of parent sum (excluding trivial P + 0 = P)
        for ca in c_arrs:
            if int(ca.sum()) < 0.10 * s_p:
                return None
        diff = np.abs(p_arr - child_sum)
        mx = np.maximum(p_arr, child_sum)
        tol = np.maximum(1, np.floor(0.02 * mx).astype(np.int64))
        f_near = float((diff <= tol).mean())
        if f_near < 0.90:
            return None
        err_l1 = float(diff.sum()) / float(max(1, int(mx.sum())))
        if err_l1 > 0.02:
            return None
        return {
            "L": L,
            "parent_sum": s_p,
            "child_sums": [int(ca.sum()) for ca in c_arrs],
            "f_near": round(f_near, 4),
            "err_l1": round(err_l1, 5),
            "parent_sample": [int(x) for x in p_arr[:12]],
            "sum_sample": [int(x) for x in child_sum[:12]],
        }

    found_2child = []
    found_3child = []
    seen_keys = set()

    for gname, kids in sorted(groups.items()):
        if len(kids) < 3 or len(kids) > 120:
            continue
        # Pre-compute prefix vectors (and non-zero compacted vectors) for fast exact/aligned matching
        # Test aligned prefix/sliding offsets (offset 0..min(8, len-6)) for 2-child sums, and offset 0 for 3-child sums
        kids_sorted = sorted(kids)
        # 2-child search: for every parent P, test all pairs (C1, C2) whose total sums could sum to P's window
        for p_id in kids_sorted:
            vp = pvecs[p_id]
            # Test contiguous windows of length L in [6..min(24, len(vp))] starting at 0 or cluster boundaries
            # Specifically check exact full-length alignment (min length of P, C1, C2 >= 6) at start offset 0..4
            for i in range(len(kids_sorted)):
                c1_id = kids_sorted[i]
                if c1_id == p_id:
                    continue
                v1 = pvecs[c1_id]
                for j in range(i + 1, len(kids_sorted)):
                    c2_id = kids_sorted[j]
                    if c2_id == p_id:
                        continue
                    v2 = pvecs[c2_id]
                    # Check aligned prefix of length L = min(len(vp), len(v1), len(v2)) and sub-windows from start 0..3
                    L_max = min(len(vp), len(v1), len(v2))
                    if L_max < 6:
                        continue
                    for off_p in range(0, min(5, len(vp) - 5)):
                        L = min(len(vp) - off_p, len(v1), len(v2))
                        if L < 6:
                            continue
                        # Quick total-sum screen before element-wise check
                        p_seg = vp[off_p:off_p + L]
                        s1 = int(v1[:L].sum())
                        s2 = int(v2[:L].sum())
                        sp = int(p_seg.sum())
                        if sp < 30 or abs(sp - (s1 + s2)) > 0.04 * sp:
                            continue
                        res = check_parent_sum(p_seg, v1[:L] + v2[:L], [v1[:L], v2[:L]])
                        if res is not None:
                            key = (p_id, c1_id, c2_id)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                found_2child.append({
                                    "group": gname,
                                    "parent": khipus[p_id]["okr_num"],
                                    "parent_inv": khipus[p_id]["inv_num"],
                                    "children": [khipus[c1_id]["okr_num"], khipus[c2_id]["okr_num"]],
                                    "children_inv": [khipus[c1_id]["inv_num"], khipus[c2_id]["inv_num"]],
                                    "off_p": off_p,
                                    **res,
                                })
                                break

        # 3-child search (for archives with <= 40 eligible khipus, e.g. Puruchuco, Leymebamba, Huaquerones, Nazca, Santa, Armatambo, Ica)
        if len(kids_sorted) <= 45:
            for p_id in kids_sorted:
                vp = pvecs[p_id]
                # Pre-filter children whose prefix sum is between 10% and 80% of parent
                for i in range(len(kids_sorted)):
                    c1 = kids_sorted[i]
                    if c1 == p_id:
                        continue
                    v1 = pvecs[c1]
                    for j in range(i + 1, len(kids_sorted)):
                        c2 = kids_sorted[j]
                        if c2 == p_id:
                            continue
                        v2 = pvecs[c2]
                        for m in range(j + 1, len(kids_sorted)):
                            c3 = kids_sorted[m]
                            if c3 == p_id:
                                continue
                            v3 = pvecs[c3]
                            L = min(len(vp), len(v1), len(v2), len(v3))
                            if L < 6:
                                continue
                            sp = int(vp[:L].sum())
                            ss = int(v1[:L].sum() + v2[:L].sum() + v3[:L].sum())
                            if sp < 30 or abs(sp - ss) > 0.04 * sp:
                                continue
                            res = check_parent_sum(vp[:L], v1[:L] + v2[:L] + v3[:L], [v1[:L], v2[:L], v3[:L]])
                            if res is not None:
                                key = (p_id, c1, c2, c3)
                                if key not in seen_keys:
                                    seen_keys.add(key)
                                    found_3child.append({
                                        "group": gname,
                                        "parent": khipus[p_id]["okr_num"],
                                        "parent_inv": khipus[p_id]["inv_num"],
                                        "children": [khipus[c1]["okr_num"], khipus[c2]["okr_num"], khipus[c3]["okr_num"]],
                                        "children_inv": [khipus[c1]["inv_num"], khipus[c2]["inv_num"], khipus[c3]["inv_num"]],
                                        **res,
                                    })

    # Null calibration: 500 random-triple permutation trials (shuffling cord order inside each khipu)
    all_elig = [kid for kid in pvecs if len(pvecs[kid]) >= 6 and len({int(x) for x in pvecs[kid] if x > 0}) >= 4 and int(pvecs[kid].max()) >= 10]
    null_2_hits = 0
    n_null_triples = 50000
    for _ in range(n_null_triples):
        p_id, c1, c2 = rng.choice(all_elig, size=3, replace=False)
        vp = pvecs[int(p_id)].copy()
        v1 = pvecs[int(c1)].copy()
        v2 = pvecs[int(c2)].copy()
        rng.shuffle(vp)
        rng.shuffle(v1)
        rng.shuffle(v2)
        L = min(len(vp), len(v1), len(v2))
        if L < 6:
            continue
        sp = int(vp[:L].sum())
        if sp < 30 or abs(sp - int(v1[:L].sum() + v2[:L].sum())) > 0.04 * sp:
            continue
        if check_parent_sum(vp[:L], v1[:L] + v2[:L], [v1[:L], v2[:L]]) is not None:
            null_2_hits += 1

    return {
        "groups_scanned": {g: len(v) for g, v in sorted(groups.items()) if 3 <= len(v) <= 120},
        "n_2child_found": len(found_2child),
        "n_3child_found": len(found_3child),
        "hits_2child": found_2child,
        "hits_3child": found_3child,
        "null_calibration_2child": {
            "n_random_triples": n_null_triples,
            "null_hits": null_2_hits,
            "null_rate_per_triple": null_2_hits / n_null_triples,
        },
    }


def run_readiness_census(khipus: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    """Test 3: Provenance-level Rosetta-readiness census across all 619 khipus."""
    by_prov: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for k in khipus.values():
        p = k["provenance"]
        if not p or p.lower() == "unknown":
            label = "Unknown / Blank"
        elif k["archive_num"] == 301:
            label = "Puruchuco (Archive 301)"
        elif p in ("Pachacamac", "Incahuasi", "Ica", "Leymebamba", "Huaquerones", "Nazca", "Armatambo, Huaca San Pedro", "Santa"):
            label = p
        else:
            label = "Other Named Provenances"
        by_prov[label].append(k)

    rows = []
    for label, klist in sorted(by_prov.items(), key=lambda kv: -len(kv[1])):
        n_tot = len(klist)
        n_ge10 = 0
        n_banded = 0
        n_mixed_rv = 0
        n_ready = 0
        sums = []
        for k in klist:
            p = k["pendants"]
            nz = [c["val"] for c in p if c["val"] > 0]
            sums.append(sum(nz))
            ge10 = len(nz) >= 10
            # Repeated equal-size cord clusters (>= 3 clusters of same size >= 3)
            cl_hist = collections.Counter(sz for _, sz, _ in k["clusters"] if sz >= 3)
            banded = any(cnt >= 3 for cnt in cl_hist.values())
            n_r = sum(1 for c in p if c["att"] == "R")
            n_v = sum(1 for c in p if c["att"] == "V")
            rv_tot = n_r + n_v
            mixed_rv = (rv_tot >= 10) and (min(n_r, n_v) / rv_tot >= 0.10)
            if ge10:
                n_ge10 += 1
            if banded:
                n_banded += 1
            if mixed_rv:
                n_mixed_rv += 1
            if ge10 and banded and (label != "Unknown / Blank"):
                n_ready += 1
        rows.append({
            "provenance": label,
            "n_khipus": n_tot,
            "n_ge10_knotted": n_ge10,
            "n_repeated_banding": n_banded,
            "n_mixed_RV": n_mixed_rv,
            "n_rosetta_ready": n_ready,
            "median_pendant_sum": int(np.median(sums)) if sums else 0,
            "max_pendant_sum": int(max(sums)) if sums else 0,
        })
    return rows


def main() -> None:
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261124)

    print("=== LOADING OPEN KHIPU REPOSITORY (khipu.db) ===", flush=True)
    khipus, meta = load_corpus(DB_PATH)
    print(f"Loaded {meta['n_khipus']} khipus, {meta['n_pendants_total']} level-1 pendants, {meta['n_knots_total']} knots.", flush=True)
    print(f"Locke/Ascher base-10 cross-check vs knot_value_type: {meta['locke_ascher_exact_match_n']}/{meta['locke_ascher_crosscheck_n']} ({meta['locke_ascher_exact_pct']}%)", flush=True)

    print("\n=== TEST 1: SANTA VALLEY 1670 REVISITA AUDIT & CALIBRATION ===", flush=True)
    t1 = run_santa_valley_audit(khipus, rng)
    print("Santa totals:", t1["totals"], flush=True)
    print("1670 benchmark:", t1["revisita_1670_benchmark"], flush=True)
    print("Combinatorial moiety null:", t1["combinatorial_moiety_null"], flush=True)
    print("Corpus spurious 6-khipu bundle null:", t1["corpus_spurious_bundle_null"], flush=True)

    print("\n=== TEST 2A: CORPUS-WIDE PAIRWISE COPY/MIRROR HUNT (ALL 619 KHIPUS) ===", flush=True)
    t2a = run_pairwise_copy_hunt(khipus, rng)
    print(f"Eligible khipus: pendant={t2a['n_eligible_pendant_khipus']}, cluster={t2a['n_eligible_cluster_khipus']}", flush=True)
    print(f"Pendant hits: total={t2a['pendant_hits_total']}, Tier A={t2a['pendant_hits_tier_A']}", flush=True)
    print("Pendant hits by category:", t2a["pendant_hits_by_category"], flush=True)
    print("Tier A by category:", t2a["pendant_tier_A_by_category"], flush=True)
    print("Null calibration:", t2a["null_calibration"], flush=True)
    for h in t2a["pendant_hits"][:25]:
        print(
            f"  [{h['tier']}|{h['category']}] {h['khipu_a']}({h['inv_a']},{h['prov_a']}) <-> "
            f"{h['khipu_b']}({h['inv_b']},{h['prov_b']}) | L={h['L']} orient={h['orient']} "
            f"exact={h['f_exact']} near={h['f_near']} errL1={h['err_l1']} | A={h['sample_a'][:6]} B={h['sample_b'][:6]}",
            flush=True,
        )

    print("\n=== TEST 2B: CROSS-KHIPU PARENT-CHILD SUMMATION HIERARCHIES ===", flush=True)
    t2b = find_summation_hierarchies(khipus, rng)
    print(f"2-child hierarchies found: {t2b['n_2child_found']}; 3-child found: {t2b['n_3child_found']}", flush=True)
    print("2-child null calibration:", t2b["null_calibration_2child"], flush=True)
    for h in t2b["hits_2child"][:15]:
        print("  2-CHILD:", h["group"], h["parent"], "=", h["children"], f"L={h['L']} errL1={h['err_l1']} sums={h['parent_sum']}={h['child_sums']}", flush=True)
    for h in t2b["hits_3child"][:15]:
        print("  3-CHILD:", h["group"], h["parent"], "=", h["children"], f"L={h['L']} errL1={h['err_l1']} sums={h['parent_sum']}={h['child_sums']}", flush=True)

    print("\n=== TEST 3: PROVENANCE ROSETTA-READINESS CENSUS ===", flush=True)
    t3 = run_readiness_census(khipus)
    for r in t3:
        print(" ", r, flush=True)

    summary = {
        "corpus_meta": meta,
        "test1_santa_valley": t1,
        "test2a_copy_mirror_hunt": t2a,
        "test2b_summation_hierarchies": t2b,
        "test3_readiness_census": t3,
    }
    out_path = RES / "khipu_summary.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSaved results to {out_path}", flush=True)


if __name__ == "__main__":
    main()
