"""
Independent replication of the Global Consciousness Project (GCP) 500-event audit.
Usage: python replicate.py OUTDIR   (run from questions/gcp-audit/)

Choices made where the protocol could be ambiguous:
1. Reference pool 183-day window: "events in the test that begin within 183 days of this
   event (before or after)" is evaluated as exact elapsed Unix seconds between event begin
   times: abs(other.begin_unix - event.begin_unix) <= 183 * 86400.
2. Duplicate seconds and cleaning order: when a Unix second appears more than once in a day
   file, the later line overwrites every field it fills before cleaning rule 1 is applied;
   thus a later out-of-range value replaces an earlier valid value and is then removed.
3. Egg check constant and boundaries: the literal 7.0711 from the protocol is used in the
   mean check (rather than sqrt(50)); failure is strictly > 5 (<= 5 passes); window count
   requirement is n >= L / 2.0 (exact division for odd L).
4. Day-file header/record validation: trailing CR/LF is stripped; the single `12,` line
   must have integer egg IDs in fields 4+ with no duplicates; `13,` lines with missing
   trailing fields treat them as empty, while any non-empty field beyond the header's egg
   count stops the program.
5. Non-evaluable windows in OUTDIR/windows.tsv: `_z` and `_seconds_used` are left empty,
   while `_eggs_usable` is always reported as the integer count of usable eggs.
6. Verdicts scope and thresholds: `reproduction` and `verdicts.reproduction` are computed
   over all evaluable events (slope = OLS slope of ours on published); `verdicts.events`,
   `verdicts.controls`, and `verdicts.overall` are computed on pairs where both windows are
   evaluable; `sd_controls` fails calibration when < 0.85 or > 1.2.
7. Sign-flip test comparison: flipped sums are compared with `>= obs_sum` in float64 via
   `signs @ diffs` with pairs in registry order.
"""

from collections import OrderedDict
from concurrent.futures import ProcessPoolExecutor
import csv
from datetime import datetime, timezone
import gzip
import json
import math
import os
from pathlib import Path
import sys
import warnings

import numpy as np

MISSING = np.int8(-128)
SENTINEL = -999999999
SENTINEL_B = b",-999999999,"
MEAN_SD_CONST = 7.0711


def parse_utc(text: str) -> int:
    dt = datetime.strptime(text.strip(), "%Y-%m-%d %H:%M:%S")
    return int(dt.replace(tzinfo=timezone.utc).timestamp())


def day_to_str(day_num: int) -> str:
    return datetime.fromtimestamp(day_num * 86400, tz=timezone.utc).strftime("%Y-%m-%d")


def parse_day_file(gz_path: Path, day_num: int) -> tuple[np.ndarray, np.ndarray]:
    day_start = day_num * 86400
    with gzip.open(gz_path, "rb") as f:
        raw = f.read()
    lines = raw.splitlines()

    header12 = [ln for ln in lines if ln.startswith(b"12,")]
    if len(header12) != 1:
        raise ValueError(f"Expected 1 '12,' line in {gz_path}, found {len(header12)}")
    h_parts = header12[0].split(b",")
    if len(h_parts) < 4:
        raise ValueError(f"No egg numbers on '12,' line in {gz_path}")
    eggs = np.array([int(x) for x in h_parts[3:]], dtype=np.int32)
    if eggs.size == 0 or np.unique(eggs).size != eggs.size:
        raise ValueError(f"Duplicate or empty egg numbers in {gz_path}")
    n_eggs = int(eggs.size)

    day_arr = np.full((86400, n_eggs), MISSING, dtype=np.int8)
    data_lines = [ln for ln in lines if ln.startswith(b"13,")]
    if not data_lines:
        return eggs, day_arr

    n_commas = n_eggs + 2
    n_cols = n_eggs + 3
    parsed_fast = False

    if b"-999999999" not in raw:
        padded = []
        ok_commas = True
        for ln in data_lines:
            c = ln.count(b",")
            if c > n_commas:
                ok_commas = False
                break
            padded.append(ln if c == n_commas else ln + b"," * (n_commas - c))
        if ok_commas:
            blob = b",".join(padded) + b","
            blob = blob.replace(b",,", SENTINEL_B).replace(b",,", SENTINEL_B)
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", DeprecationWarning)
                    flat = np.fromstring(blob[:-1].decode("ascii"), dtype=np.int64, sep=",")
            except (ValueError, UnicodeDecodeError):
                flat = np.empty(0, dtype=np.int64)
            if flat.size == len(data_lines) * n_cols:
                parsed_fast = True
                mat = flat.reshape(len(data_lines), n_cols)
                ts = mat[:, 1]
                if np.any((ts < day_start) | (ts >= day_start + 86400)):
                    raise ValueError(f"Timestamp out of UTC day in {gz_path}")
                offsets = ts - day_start
                vals = mat[:, 3:]
                counts = np.bincount(offsets, minlength=86400)
                is_uniq = counts[offsets] == 1
                if np.any(is_uniq):
                    u_vals = vals[is_uniq]
                    u_ok = (u_vals > 55) & (u_vals < 145)
                    day_arr[offsets[is_uniq]] = np.where(u_ok, u_vals - 100, MISSING).astype(np.int8)
                if not np.all(is_uniq):
                    for idx in np.flatnonzero(~is_uniq):
                        row = vals[idx]
                        filled = row != SENTINEL
                        r_ok = (row > 55) & (row < 145)
                        clean = np.where(r_ok, row - 100, MISSING).astype(np.int8)
                        day_arr[offsets[idx], filled] = clean[filled]

    if not parsed_fast:
        for ln in data_lines:
            parts = ln.decode("ascii", errors="replace").split(",")
            if len(parts) < 2:
                raise ValueError(f"Malformed '13,' line in {gz_path}")
            ts = int(parts[1].strip())
            off = ts - day_start
            if not (0 <= off < 86400):
                raise ValueError(f"Timestamp {ts} out of UTC day in {gz_path}")
            if len(parts) > 3 + n_eggs:
                for extra in parts[3 + n_eggs:]:
                    if extra.strip():
                        raise ValueError(f"Extra non-empty field in {gz_path}")
            for j, tok in enumerate(parts[3:3 + n_eggs]):
                tok = tok.strip()
                if tok:
                    val = float(tok)
                    day_arr[off, j] = np.int8(int(round(val)) - 100) if abs(val - 100.0) < 45.0 else MISSING

    return eggs, day_arr


def compute_day_pool(
    eggs: np.ndarray, day_arr: np.ndarray, day_num: int, day_blocked: list[tuple[int, int]]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    day_start = day_num * 86400
    unblocked = np.ones(86400, dtype=bool)
    for b, e in day_blocked:
        lo = max(0, b - day_start)
        hi = min(86400, e - day_start + 1)
        if lo < hi:
            unblocked[lo:hi] = False

    sub = day_arr[unblocked]
    valid = sub != MISSING
    n = valid.sum(axis=0, dtype=np.int64)
    ok = n >= 3600
    if not np.any(ok):
        empty_i32 = np.empty(0, dtype=np.int32)
        empty_i64 = np.empty(0, dtype=np.int64)
        return empty_i32, empty_i64, empty_i64

    sub_ok = np.where(valid[:, ok], sub[:, ok].astype(np.int64), 0)
    n_ok = n[ok]
    s1 = sub_ok.sum(axis=0)
    s2 = (sub_ok * sub_ok).sum(axis=0)
    mean_d = s1 / n_ok
    mean_d2 = s2 / n_ok
    pass_m = np.abs(mean_d) / (MEAN_SD_CONST / np.sqrt(n_ok)) <= 5.0
    pass_v = np.abs(mean_d2 / 50.0 - 1.0) * np.sqrt(n_ok / 2.0) <= 5.0
    keep = pass_m & pass_v
    return eggs[ok][keep].astype(np.int32), n_ok[keep].astype(np.int64), s2[keep].astype(np.int64)


def prepare_day(args: tuple[int, str, str, list[tuple[int, int]]]) -> tuple[int, list[int], list[int], list[int]]:
    day_num, gz_str, npz_str, day_blocked = args
    npz_path = Path(npz_str)
    if npz_path.exists():
        with np.load(npz_path) as z:
            return day_num, z["pool_eggs"].tolist(), z["pool_n"].tolist(), z["pool_ss"].tolist()
    eggs, day_arr = parse_day_file(Path(gz_str), day_num)
    p_eggs, p_n, p_ss = compute_day_pool(eggs, day_arr, day_num, day_blocked)
    np.savez(npz_path, eggs=eggs, data=day_arr, pool_eggs=p_eggs, pool_n=p_n, pool_ss=p_ss)
    return day_num, p_eggs.tolist(), p_n.tolist(), p_ss.tolist()


class DayLoader:
    def __init__(self, cache_dir: Path, max_days: int = 16):
        self.cache_dir = cache_dir
        self.max_days = max_days
        self.cache: OrderedDict[int, tuple[np.ndarray, np.ndarray]] = OrderedDict()

    def get(self, day_num: int) -> tuple[np.ndarray, np.ndarray]:
        item = self.cache.get(day_num)
        if item is not None:
            self.cache.move_to_end(day_num)
            return item
        npz_path = self.cache_dir / f"{day_to_str(day_num)}.npz"
        with np.load(npz_path) as z:
            item = (z["eggs"], z["data"])
        self.cache[day_num] = item
        if len(self.cache) > self.max_days:
            self.cache.popitem(last=False)
        return item


def score_window(
    w_start: int, length: int, pool_s: dict[int, float], loader: DayLoader
) -> tuple[float | None, int | None, int]:
    w_end = w_start + length - 1
    d0 = w_start // 86400
    d1 = w_end // 86400

    day_objs = [(d, *loader.get(d)) for d in range(d0, d1 + 1)]
    cand_set = {eid for _, eggs, _ in day_objs for eid in eggs.tolist() if eid in pool_s}
    if not cand_set:
        return None, None, 0

    cand_eggs = sorted(cand_set)
    egg_to_col = {eid: idx for idx, eid in enumerate(cand_eggs)}
    cand_s = np.array([pool_s[eid] for eid in cand_eggs], dtype=np.float64)

    W = np.full((length, len(cand_eggs)), MISSING, dtype=np.int8)
    for d, eggs, data in day_objs:
        day_start = d * 86400
        s0 = max(0, w_start - day_start)
        s1 = min(86400, w_end - day_start + 1)
        out0 = day_start + s0 - w_start
        out1 = out0 + (s1 - s0)
        src_cols = []
        dst_cols = []
        for j, eid in enumerate(eggs.tolist()):
            col = egg_to_col.get(eid)
            if col is not None:
                src_cols.append(j)
                dst_cols.append(col)
        if src_cols:
            W[out0:out1, dst_cols] = data[s0:s1, src_cols]

    valid = W != MISSING
    n = valid.sum(axis=0, dtype=np.int64)
    ok = n >= (length / 2.0)
    if not np.any(ok):
        return None, None, 0

    W_ok = np.where(valid[:, ok], W[:, ok].astype(np.int64), 0)
    n_ok = n[ok]
    mean_d = W_ok.sum(axis=0) / n_ok
    mean_d2 = (W_ok * W_ok).sum(axis=0) / n_ok
    pass_m = np.abs(mean_d) / (MEAN_SD_CONST / np.sqrt(n_ok)) <= 5.0
    pass_v = np.abs(mean_d2 / 50.0 - 1.0) * np.sqrt(n_ok / 2.0) <= 5.0
    keep = pass_m & pass_v
    n_usable = int(keep.sum())
    if n_usable < 2:
        return None, None, n_usable

    use_idx = np.flatnonzero(ok)[keep]
    valid_u = valid[:, use_idx]
    N_sec = valid_u.sum(axis=1)
    sec_mask = N_sec >= 1
    df = int(sec_mask.sum())
    if df < 0.8 * length or df < 2:
        return None, None, n_usable

    W_u = W[sec_mask][:, use_idx].astype(np.float64)
    z_mat = np.where(valid_u[sec_mask], W_u / cand_s[use_idx], 0.0)
    Z_sec = z_mat.sum(axis=1) / np.sqrt(N_sec[sec_mask].astype(np.float64))
    chi2 = float(np.sum(Z_sec * Z_sec))
    a = 2.0 / (9.0 * df)
    z_win = ((chi2 / df) ** (1.0 / 3.0) - (1.0 - a)) / math.sqrt(a)
    return z_win, df, n_usable


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python replicate.py OUTDIR")
    outdir = Path(sys.argv[1])
    cache_dir = outdir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    events = []
    with open("windows.tsv", "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row["in_test"] != "1":
                continue
            L = int(row["seconds"])
            ev_start = parse_utc(row["begin_utc"])
            ct_start = parse_utc(row["control_begin_utc"])
            events.append({
                "num": row["num"],
                "begin_utc": row["begin_utc"],
                "control_begin_utc": row["control_begin_utc"],
                "L": L,
                "published_z": float(row["published_z"]),
                "ev_start": ev_start,
                "ct_start": ct_start,
                "ev_days": set(range(ev_start // 86400, (ev_start + L - 1) // 86400 + 1)),
                "ct_days": set(range(ct_start // 86400, (ct_start + L - 1) // 86400 + 1)),
            })

    blocked = []
    with open("sources/blocked.tsv", "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            blocked.append((int(row["begin_unix"]), int(row["end_unix"])))

    needed_days = sorted({d for ev in events for d in (ev["ev_days"] | ev["ct_days"])})
    tasks = []
    for d in needed_days:
        ds = day_to_str(d)
        day_start, day_end = d * 86400, d * 86400 + 86399
        day_blk = [(b, e) for b, e in blocked if e >= day_start and b <= day_end]
        tasks.append((d, str(Path("data") / f"basketdata-{ds}.csv.gz"), str(cache_dir / f"{ds}.npz"), day_blk))

    day_pool: dict[int, tuple[list[int], list[int], list[int]]] = {}
    workers = min(os.cpu_count() or 1, 8)
    try:
        if workers > 1:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                for d, p_eggs, p_n, p_ss in ex.map(prepare_day, tasks):
                    day_pool[d] = (p_eggs, p_n, p_ss)
        else:
            for t in tasks:
                d, p_eggs, p_n, p_ss = prepare_day(t)
                day_pool[d] = (p_eggs, p_n, p_ss)
    except (OSError, PermissionError):
        for t in tasks:
            d, p_eggs, p_n, p_ss = prepare_day(t)
            day_pool[d] = (p_eggs, p_n, p_ss)

    loader = DayLoader(cache_dir)
    results = []
    for ev in events:
        pool_days: set[int] = set()
        for other in events:
            if abs(other["ev_start"] - ev["ev_start"]) <= 183 * 86400:
                pool_days.update(other["ct_days"])
        pool_days -= ev["ct_days"]

        tot_n: dict[int, int] = {}
        tot_ss: dict[int, int] = {}
        for d in pool_days:
            p_eggs, p_n, p_ss = day_pool[d]
            for eid, cnt, ss in zip(p_eggs, p_n, p_ss):
                tot_n[eid] = tot_n.get(eid, 0) + cnt
                tot_ss[eid] = tot_ss.get(eid, 0) + ss
        pool_s = {eid: math.sqrt(tot_ss[eid] / cnt) for eid, cnt in tot_n.items() if cnt >= 86400}

        ev_z, ev_df, ev_eggs = score_window(ev["ev_start"], ev["L"], pool_s, loader)
        ct_z, ct_df, ct_eggs = score_window(ev["ct_start"], ev["L"], pool_s, loader)
        results.append({
            "num": ev["num"],
            "begin_utc": ev["begin_utc"],
            "event_z": ev_z,
            "event_seconds_used": ev_df,
            "event_eggs_usable": ev_eggs,
            "control_begin_utc": ev["control_begin_utc"],
            "control_z": ct_z,
            "control_seconds_used": ct_df,
            "control_eggs_usable": ct_eggs,
            "published_z": ev["published_z"],
        })

    cols = [
        "num", "begin_utc", "event_z", "event_seconds_used", "event_eggs_usable",
        "control_begin_utc", "control_z", "control_seconds_used", "control_eggs_usable",
    ]
    with open(outdir / "windows.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(cols)
        for r in results:
            w.writerow([
                r["num"],
                r["begin_utc"],
                "" if r["event_z"] is None else f"{r['event_z']:.6f}",
                "" if r["event_seconds_used"] is None else str(r["event_seconds_used"]),
                str(r["event_eggs_usable"]),
                r["control_begin_utc"],
                "" if r["control_z"] is None else f"{r['control_z']:.6f}",
                "" if r["control_seconds_used"] is None else str(r["control_seconds_used"]),
                str(r["control_eggs_usable"]),
            ])

    ev_eval = [(r["event_z"], r["published_z"]) for r in results if r["event_z"] is not None]
    ct_eval = [r["control_z"] for r in results if r["control_z"] is not None]
    paired = [(r["event_z"], r["control_z"]) for r in results if r["event_z"] is not None and r["control_z"] is not None]

    n_ev = len(ev_eval)
    ev_arr = np.array([x[0] for x in ev_eval], dtype=np.float64)
    pub_arr = np.array([x[1] for x in ev_eval], dtype=np.float64)
    z_all = float(ev_arr.sum() / math.sqrt(n_ev)) if n_ev > 0 else None
    comb_pub = float(pub_arr.sum() / math.sqrt(n_ev)) if n_ev > 0 else None
    med_abs = float(np.median(np.abs(ev_arr - pub_arr))) if n_ev > 0 else None

    r_val = slope_val = None
    if n_ev >= 3:
        xc = pub_arr - pub_arr.mean()
        yc = ev_arr - ev_arr.mean()
        sxx = float(np.dot(xc, xc))
        syy = float(np.dot(yc, yc))
        sxy = float(np.dot(xc, yc))
        if sxx > 0.0:
            slope_val = sxy / sxx
            if syy > 0.0:
                r_val = sxy / math.sqrt(sxx * syy)

    n_ct = len(ct_eval)
    ct_arr = np.array(ct_eval, dtype=np.float64)
    z_ct = float(ct_arr.sum() / math.sqrt(n_ct)) if n_ct > 0 else None
    sd_ct = float(np.std(ct_arr, ddof=1)) if n_ct >= 2 else None

    n_pairs = len(paired)
    p_ev = np.array([x[0] for x in paired], dtype=np.float64)
    p_ct = np.array([x[1] for x in paired], dtype=np.float64)
    p_z_ev = float(p_ev.sum() / math.sqrt(n_pairs)) if n_pairs > 0 else None
    p_z_ct = float(p_ct.sum() / math.sqrt(n_pairs)) if n_pairs > 0 else None
    p_sd_ct = float(np.std(p_ct, ddof=1)) if n_pairs >= 2 else None
    diffs = p_ev - p_ct
    mean_diff = float(diffs.mean()) if n_pairs > 0 else None

    p_flip = None
    if n_pairs > 0:
        obs_sum = float(diffs.sum())
        rng = np.random.default_rng(74)
        hits = 0
        for _ in range(20):
            signs = rng.integers(0, 2, (10000, n_pairs)) * 2 - 1
            hits += int(np.sum((signs @ diffs) >= obs_sum))
        p_flip = (hits + 1) / 200001

    if r_val is not None and slope_val is not None and med_abs is not None:
        if r_val >= 0.9 and med_abs <= 0.25 and 0.8 <= slope_val <= 1.25:
            v_repro = "reproduces closely"
        elif r_val >= 0.7 and med_abs <= 0.5:
            v_repro = "reproduces roughly"
        else:
            v_repro = "does not reproduce"
    else:
        v_repro = "does not reproduce"

    if p_z_ev is not None and p_z_ev >= 3.09:
        v_events = "departure"
    elif p_z_ev is not None and p_z_ev >= 1.645:
        v_events = "suggestive"
    else:
        v_events = "no positive excess detected"

    if (p_z_ct is not None and abs(p_z_ct) >= 2.58) or (p_sd_ct is not None and (p_sd_ct < 0.85 or p_sd_ct > 1.2)):
        v_controls = "calibration failure detected"
    else:
        v_controls = "no calibration failure detected"

    if n_pairs < 300:
        v_overall = "insufficient coverage"
    elif p_z_ev is not None and p_z_ev < 1.645:
        v_overall = "no excess found"
    elif v_events == "departure" and p_flip is not None and p_flip <= 0.01 and v_controls == "no calibration failure detected":
        v_overall = "the excess is in the event windows"
    elif p_z_ct is not None and p_z_ct >= 2.58 and p_flip is not None and p_flip > 0.05:
        v_overall = "the excess is not specific to the events"
    else:
        v_overall = "mixed"

    summary = {
        "n_events": n_ev,
        "z_all": z_all,
        "n_controls": n_ct,
        "z_controls": z_ct,
        "sd_controls": sd_ct,
        "pairs": {
            "n": n_pairs,
            "z_events": p_z_ev,
            "z_controls": p_z_ct,
            "sd_controls": p_sd_ct,
            "mean_difference": mean_diff,
            "p_one_sided_sign_flip": p_flip,
        },
        "reproduction": {
            "n": n_ev,
            "r": r_val,
            "median_abs_difference": med_abs,
            "combined_ours": z_all,
            "combined_published": comb_pub,
        },
        "verdicts": {
            "reproduction": v_repro,
            "events": v_events,
            "controls": v_controls,
            "overall": v_overall,
        },
    }
    with open(outdir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
