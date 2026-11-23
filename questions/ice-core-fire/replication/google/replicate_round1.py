"""Independent replication of Issue #43 (ice-core-fire) ammonium analysis.

Ambiguities resolved / implementation choices:
1. Window-level Z completeness: The protocol states an 80% bin threshold for
   usable windows (5 * present >= 4 * bins) and for E (5 * valid_e >= 4 * bins),
   and defines per-bin z_j missingness, without explicitly repeating a window
   completeness threshold for Z. Choice: apply the same 80% threshold
   (5 * valid_z >= 4 * bins) to window-level Z (when T != 60) so Z is not
   reported from a small subset of bins in windows with incomplete backgrounds.
2. Per-bin Z positive-bin count: The protocol states that median(ln x) and
   MAD(ln x) are taken over bins in j-n..j+n with x > 0 and that z_j is missing
   if bin j has no background (fewer than n+1 present values), x_j <= 0, or
   MAD == 0. Choice: follow this condition literally without adding a separate
   minimum count on strictly positive bins.
3. MAD definition: Standard median absolute deviation from the median,
   MAD(y) = median(|y - median(y)|) over the bins in j-n..j+n with x > 0, using
   the mean of the two middle values when the count is even.
4. Tie-breaking for H_age and Z_age: Apply the same youngest-bin tie-break
   (smallest start age, matching first index in ascending-age order) specified
   for E_age.
5. GICC05 depth range endpoints: Linear interpolation treats the endpoints
   [min(gicc_depth), max(gicc_depth)] as inside the GICC05 depth range.
6. GISP2 overlap threshold and header parsing: Compare float64 overlap sum
   against T / 2 literally (missing if sum < T / 2); locate the header line as
   the first tab-separated line of >= 12 fields whose first field strips to
   'Top', and skip blank or non-numeric lines after it.
7. Timing rule boundary: "within 60 years of each other" / "more than 60 years
   apart" is implemented as abs(E_age_NGRIP - E_age_NEEM) <= 60 passing.
8. Output formatting: Bin start ages (E_age, H_age, Z_age) are exact integers
   and formatted as integers (or 'nan' when missing); floating-point values use
   full float64 precision (repr) and 'nan' when missing; rows in
   windows_<series>.tsv are ordered by ascending k.
"""

from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

# (name, source_key, T, a0, span_start, span_end)
SERIES_SPECS: list[tuple[str, str, int, int, int, int]] = [
    ("N10", "ngrip10", 10, 12750, 10300, 107620),
    ("E10", "neem10", 10, 12750, 10300, 107620),
    ("N20", "ngrip10", 20, 12750, 10300, 50000),
    ("E20", "neem10", 20, 12750, 10300, 50000),
    ("G20", "gisp2", 20, 12735, 10300, 50000),
    ("N60", "ngrip10", 60, 12750, 10300, 107620),
    ("E60", "neem10", 60, 12750, 10300, 107620),
    ("G60", "gisp2", 60, 12735, 10300, 107620),
    ("N3", "ngrip1mm", 3, 12750, 10300, 60000),
    ("N1", "ngrip1mm", 1, 12750, 10300, 20000),
    ("G10", "gisp2", 10, 12735, 10300, 15000),
    ("E10h", "neem10", 10, 12750, 0, 107620),
    ("G20h", "gisp2", 20, 12735, 0, 50000),
    ("G60h", "gisp2", 60, 12735, 0, 110000),
]

TIERS: dict[str, list[tuple[str, str]]] = {
    "T10": [("N10", "NGRIP"), ("E10", "NEEM")],
    "T20": [("N20", "NGRIP"), ("E20", "NEEM"), ("G20", "GISP2")],
    "T60": [("N60", "NGRIP"), ("E60", "NEEM"), ("G60", "GISP2")],
}

CORE_TIER_SERIES: dict[str, list[str]] = {
    "NGRIP": ["N10", "N20", "N60"],
    "NEEM": ["E10", "E20", "E60"],
    "GISP2": ["G20", "G60"],
}


def read_pangaea_10yr(path: str) -> tuple[np.ndarray, np.ndarray]:
    ages: list[int] = []
    nh4s: list[float] = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            if line.startswith("*/"):
                break
        next(f)  # header row
        for line in f:
            s = line.rstrip("\r\n")
            if not s:
                continue
            parts = s.split("\t")
            a_s = parts[0].strip()
            if not a_s:
                continue
            ages.append(int(round(float(a_s) * 1000.0)))
            v_s = parts[4].strip() if len(parts) > 4 else ""
            nh4s.append(float(v_s) if v_s else math.nan)
    return np.array(ages, dtype=np.int64), np.array(nh4s, dtype=np.float64)


def read_pangaea_1mm(path: str) -> tuple[np.ndarray, np.ndarray]:
    depths: list[float] = []
    nh4s: list[float] = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            if line.startswith("*/"):
                break
        next(f)  # header row
        for line in f:
            s = line.rstrip("\r\n")
            if not s:
                continue
            parts = s.split("\t")
            d_s = parts[0].strip()
            if not d_s:
                continue
            depths.append(float(d_s))
            v_s = parts[4].strip() if len(parts) > 4 else ""
            nh4s.append(float(v_s) if v_s else math.nan)
    return np.array(depths, dtype=np.float64), np.array(nh4s, dtype=np.float64)


def read_gicc05(path: str) -> tuple[np.ndarray, np.ndarray]:
    ages: list[float] = []
    depths: list[float] = []
    with open(path, "r", encoding="latin-1") as f:
        for line in f:
            parts = line.split()
            if len(parts) != 4:
                continue
            try:
                vals = [float(p) for p in parts]
            except ValueError:
                continue
            if all(math.isfinite(v) for v in vals):
                ages.append(vals[0])
                depths.append(vals[1])
    return np.array(ages, dtype=np.float64), np.array(depths, dtype=np.float64)


def read_gisp2(path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    top_ages: list[float] = []
    bot_ages: list[float] = []
    nh4s: list[float] = []
    with open(path, "r", encoding="latin-1") as f:
        found = False
        for line in f:
            parts = line.rstrip("\r\n").split("\t")
            if len(parts) >= 12 and parts[0].strip() == "Top":
                found = True
                break
        if not found:
            raise ValueError(f"Header line starting with 'Top' not found in {path}")
        for line in f:
            s = line.rstrip("\r\n")
            if not s.strip():
                continue
            parts = s.split("\t")
            if len(parts) < 12:
                continue
            ta_s, ba_s, v_s = parts[10].strip(), parts[11].strip(), parts[3].strip()
            if not ta_s or not ba_s or not v_s:
                continue
            try:
                ta, ba, v = float(ta_s), float(ba_s), float(v_s)
            except ValueError:
                continue
            if ta < 999999.0 and ba < 999999.0 and ba > ta:
                top_ages.append(ta)
                bot_ages.append(ba)
                nh4s.append(v)
    return (
        np.array(top_ages, dtype=np.float64),
        np.array(bot_ages, dtype=np.float64),
        np.array(nh4s, dtype=np.float64),
    )


def bin_10yr(ages: np.ndarray, nh4: np.ndarray, a0: int, T: int) -> tuple[int, np.ndarray]:
    j_arr = (ages - a0) // T
    j_min = int(j_arr.min())
    j_max = int(j_arr.max())
    nbins = j_max - j_min + 1
    idx = j_arr - j_min
    good = ~np.isnan(nh4)
    cnt = np.bincount(idx[good], minlength=nbins)
    v_sum = np.bincount(idx[good], weights=nh4[good], minlength=nbins)
    vals = np.full(nbins, np.nan, dtype=np.float64)
    rows_per_bin = T // 10
    ok = (2 * cnt) >= rows_per_bin
    vals[ok] = v_sum[ok] / cnt[ok]
    return j_min, vals


def bin_1mm(ages: np.ndarray, nh4: np.ndarray, a0: int, T: int) -> tuple[int, np.ndarray]:
    valid_age = ~np.isnan(ages)
    j_arr = np.floor((ages[valid_age] - a0) / T).astype(np.int64)
    v_arr = nh4[valid_age]
    j_min = int(j_arr.min())
    j_max = int(j_arr.max())
    nbins = j_max - j_min + 1
    idx = j_arr - j_min
    n_total = np.bincount(idx, minlength=nbins)
    good = ~np.isnan(v_arr)
    n_valid = np.bincount(idx[good], minlength=nbins)
    v_sum = np.bincount(idx[good], weights=v_arr[good], minlength=nbins)
    vals = np.full(nbins, np.nan, dtype=np.float64)
    ok = (n_total > 0) & ((2 * n_valid) >= n_total)
    vals[ok] = v_sum[ok] / n_valid[ok]
    return j_min, vals


def bin_gisp2(
    top_ages: np.ndarray, bot_ages: np.ndarray, nh4: np.ndarray, a0: int, T: int
) -> tuple[int, np.ndarray]:
    j_min = int(math.floor((float(top_ages.min()) - a0) / T))
    j_max = int(math.floor((float(bot_ages.max()) - a0) / T))
    nbins = j_max - j_min + 1
    w_sum = np.zeros(nbins, dtype=np.float64)
    wv_sum = np.zeros(nbins, dtype=np.float64)
    for ta, ba, v in zip(top_ages.tolist(), bot_ages.tolist(), nh4.tolist()):
        j0 = int(math.floor((ta - a0) / T))
        j1 = int(math.floor((ba - a0) / T))
        for j in range(j0, j1 + 1):
            b0 = a0 + j * T
            b1 = b0 + T
            ov = (ba if ba < b1 else b1) - (ta if ta > b0 else b0)
            if ov > 0.0:
                idx = j - j_min
                w_sum[idx] += ov
                wv_sum[idx] += ov * v
    vals = np.full(nbins, np.nan, dtype=np.float64)
    ok = w_sum >= (T / 2.0)
    vals[ok] = wv_sum[ok] / w_sum[ok]
    return j_min, vals


def nanmedian_rows(arr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    s = np.sort(arr, axis=1)
    cnt = np.sum(~np.isnan(s), axis=1)
    rows = np.arange(s.shape[0])
    lo = np.maximum((cnt - 1) // 2, 0)
    hi = cnt // 2
    med = 0.5 * (s[rows, lo] + s[rows, hi])
    med[cnt == 0] = np.nan
    return med, cnt


def compute_bin_stats(
    b_min: int, bin_vals: np.ndarray, j_lo: int, j_hi: int, T: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = 150 // T
    K = 2 * n + 1
    M = j_hi - j_lo + 1
    need_lo = j_lo - n
    need_hi = j_hi + n
    x_pad = np.full(need_hi - need_lo + 1, np.nan, dtype=np.float64)
    b_max = b_min + len(bin_vals) - 1
    ov_lo = max(b_min, need_lo)
    ov_hi = min(b_max, need_hi)
    if ov_lo <= ov_hi:
        x_pad[ov_lo - need_lo : ov_hi - need_lo + 1] = bin_vals[
            ov_lo - b_min : ov_hi - b_min + 1
        ]

    x_center = x_pad[n : n + M]
    m_out = np.full(M, np.nan, dtype=np.float64)
    z_out = np.full(M, np.nan, dtype=np.float64)

    compute_z = T != 60
    if compute_z:
        lx_pad = np.full_like(x_pad, np.nan)
        pos = x_pad > 0.0
        lx_pad[pos] = np.log(x_pad[pos])
        lx_center = lx_pad[n : n + M]
        w_lx = sliding_window_view(lx_pad, K)
    else:
        lx_center = None
        w_lx = None

    w_x = sliding_window_view(x_pad, K)
    chunk = 4096
    for start in range(0, M, chunk):
        stop = min(start + chunk, M)
        med, cnt = nanmedian_rows(w_x[start:stop])
        med[2 * cnt < K] = np.nan
        m_out[start:stop] = med
        if compute_z:
            sub_lx = w_lx[start:stop]
            med_lx, _ = nanmedian_rows(sub_lx)
            dev = np.abs(sub_lx - med_lx[:, None])
            mad_lx, _ = nanmedian_rows(dev)
            xc = x_center[start:stop]
            lxc = lx_center[start:stop]
            ok = (~np.isnan(med)) & (xc > 0.0) & (mad_lx > 0.0)
            z_chunk = np.full(stop - start, np.nan, dtype=np.float64)
            z_chunk[ok] = (lxc[ok] - med_lx[ok]) / (1.4826 * mad_lx[ok])
            z_out[start:stop] = z_chunk

    e_out = x_center - m_out
    return x_center, e_out, z_out


def compute_series_windows(
    T: int, a0: int, span_start: int, span_end: int, b_min: int, bin_vals: np.ndarray
) -> list[dict[str, object]]:
    bins_per_win = 300 // T
    k_min = (span_start - a0 + 299) // 300
    k_max = (span_end - a0) // 300 - 1
    if k_max < k_min:
        return []

    j_lo = k_min * bins_per_win
    j_hi = (k_max + 1) * bins_per_win - 1
    x_arr, e_arr, z_arr = compute_bin_stats(b_min, bin_vals, j_lo, j_hi, T)

    n_wins = k_max - k_min + 1
    x_mat = x_arr.reshape(n_wins, bins_per_win)
    e_mat = e_arr.reshape(n_wins, bins_per_win)
    z_mat = z_arr.reshape(n_wins, bins_per_win)

    rows: list[dict[str, object]] = []
    for w in range(n_wins):
        xw = x_mat[w]
        with_val = int(np.sum(~np.isnan(xw)))
        if 5 * with_val < 4 * bins_per_win:
            continue

        k = k_min + w
        start = a0 + 300 * k
        end = start + 300
        mean_val = float(np.nanmean(xw))

        h_idx = int(np.nanargmax(xw))
        h_val = float(xw[h_idx])
        h_age = start + h_idx * T

        ew = e_mat[w]
        e_valid = int(np.sum(~np.isnan(ew)))
        if 5 * e_valid >= 4 * bins_per_win:
            e_idx = int(np.nanargmax(ew))
            e_val = float(ew[e_idx])
            e_age: int | None = start + e_idx * T
        else:
            e_val = math.nan
            e_age = None

        if T == 60:
            z_val = math.nan
            z_age: int | None = None
        else:
            zw = z_mat[w]
            z_valid = int(np.sum(~np.isnan(zw)))
            if 5 * z_valid >= 4 * bins_per_win:
                z_idx = int(np.nanargmax(zw))
                z_val = float(zw[z_idx])
                z_age = start + z_idx * T
            else:
                z_val = math.nan
                z_age = None

        rows.append(
            {
                "k": k,
                "start": start,
                "end": end,
                "bins": bins_per_win,
                "with_value": with_val,
                "E": e_val,
                "E_age": e_age,
                "H": h_val,
                "H_age": h_age,
                "Z": z_val,
                "Z_age": z_age,
                "mean": mean_val,
            }
        )
    return rows


def fmt_float(v: float) -> str:
    return "nan" if math.isnan(v) else repr(float(v))


def fmt_age(v: int | None) -> str:
    return "nan" if v is None else str(v)


def write_windows_tsv(path: str, rows: list[dict[str, object]]) -> None:
    cols = ["k", "start", "end", "bins", "with_value", "E", "E_age", "H", "H_age", "Z", "Z_age", "mean"]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write(
                "\t".join(
                    [
                        str(r["k"]),
                        str(r["start"]),
                        str(r["end"]),
                        str(r["bins"]),
                        str(r["with_value"]),
                        fmt_float(r["E"]),
                        fmt_age(r["E_age"]),
                        fmt_float(r["H"]),
                        fmt_age(r["H_age"]),
                        fmt_float(r["Z"]),
                        fmt_age(r["Z_age"]),
                        fmt_float(r["mean"]),
                    ]
                )
                + "\n"
            )


def compute_target_rank(rows: list[dict[str, object]], measure: str) -> dict[str, object] | None:
    target_row = None
    vals: list[float] = []
    for r in rows:
        v = r[measure]
        if not math.isnan(v):
            vals.append(v)
            if r["k"] == 0:
                target_row = r
    if target_row is None:
        return None
    tval = float(target_row[measure])
    N = len(vals)
    rank = 1 + sum(1 for v in vals if v > tval)
    return {
        "value": tval,
        "rank": rank,
        "N": N,
        "in_top1": rank <= max(1, N // 100),
        "in_top5": rank <= max(1, N // 20),
    }


def tier_passes(
    tier_members: list[tuple[str, str]],
    ranks_e: dict[str, dict[str, object] | None],
    target_e_age: dict[str, int | None],
    key: str,
) -> bool:
    qual = [
        (s, core)
        for s, core in tier_members
        if ranks_e[s] is not None and bool(ranks_e[s][key])
    ]
    for i in range(len(qual)):
        s1, c1 = qual[i]
        for j in range(i + 1, len(qual)):
            s2, c2 = qual[j]
            if {c1, c2} == {"NGRIP", "NEEM"}:
                a1, a2 = target_e_age[s1], target_e_age[s2]
                if a1 is not None and a2 is not None and abs(a1 - a2) <= 60:
                    return True
            else:
                return True
    return False


def decide_verdict(
    ranks_e: dict[str, dict[str, object] | None],
    target_e_age: dict[str, int | None],
) -> str:
    missing_cores = sum(
        1
        for series_list in CORE_TIER_SERIES.values()
        if all(ranks_e[s] is None for s in series_list)
    )
    if missing_cores >= 2:
        return "not testable"
    if any(tier_passes(members, ranks_e, target_e_age, "in_top1") for members in TIERS.values()):
        return "exceptional"
    if any(tier_passes(members, ranks_e, target_e_age, "in_top5") for members in TIERS.values()):
        return "unusual"
    tier_series = [s for members in TIERS.values() for s, _ in members]
    if any(ranks_e[s] is not None and bool(ranks_e[s]["in_top1"]) for s in tier_series):
        return "not corroborated"
    return "not met"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python replicate.py OUTDIR")
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)

    ngrip10_age, ngrip10_nh4 = read_pangaea_10yr("data/pangaea/935814.tab")
    neem10_age, neem10_nh4 = read_pangaea_10yr("data/pangaea/935831.tab")
    ngrip1mm_depth, ngrip1mm_nh4 = read_pangaea_1mm("data/pangaea/935818.tab")
    gicc_age, gicc_depth = read_gicc05("data/noaa/gicc05-60ka-20yr.txt")
    gisp2_top, gisp2_bot, gisp2_nh4 = read_gisp2("data/noaa/iond.txt")

    ngrip1mm_age = np.interp(
        ngrip1mm_depth, gicc_depth, gicc_age, left=np.nan, right=np.nan
    )

    bin_cache: dict[tuple[str, int, int], tuple[int, np.ndarray]] = {}

    def get_bins(src: str, T: int, a0: int) -> tuple[int, np.ndarray]:
        key = (src, T, a0)
        if key not in bin_cache:
            if src == "ngrip10":
                bin_cache[key] = bin_10yr(ngrip10_age, ngrip10_nh4, a0, T)
            elif src == "neem10":
                bin_cache[key] = bin_10yr(neem10_age, neem10_nh4, a0, T)
            elif src == "ngrip1mm":
                bin_cache[key] = bin_1mm(ngrip1mm_age, ngrip1mm_nh4, a0, T)
            elif src == "gisp2":
                bin_cache[key] = bin_gisp2(gisp2_top, gisp2_bot, gisp2_nh4, a0, T)
            else:
                raise ValueError(f"Unknown source: {src}")
        return bin_cache[key]

    ranks: dict[str, dict[str, dict[str, object] | None]] = {"E": {}, "H": {}, "Z": {}}
    target_e_age: dict[str, int | None] = {}

    for name, src, T, a0, span_start, span_end in SERIES_SPECS:
        b_min, bin_vals = get_bins(src, T, a0)
        rows = compute_series_windows(T, a0, span_start, span_end, b_min, bin_vals)
        write_windows_tsv(os.path.join(outdir, f"windows_{name}.tsv"), rows)
        for m in ("E", "H", "Z"):
            ranks[m][name] = compute_target_rank(rows, m)
        t_row = next((r for r in rows if r["k"] == 0), None)
        target_e_age[name] = t_row["E_age"] if t_row is not None else None

    summary = {
        "verdict": decide_verdict(ranks["E"], target_e_age),
        "ranks": ranks,
    }
    with open(os.path.join(outdir, "summary.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=2, allow_nan=False)
        f.write("\n")


if __name__ == "__main__":
    main()
