"""Independent replication of the Global Consciousness Project post-2015 test.

Ambiguities in protocol.md and choices made:
1. Control-window trials entering s^2: Cleaning step 1 (|x - 100| < 45) is
   applied to all control-window trials pooled for s^2; Cleaning step 2 (the
   egg check) is applied only to decide whether an egg is usable in the window
   being scored, not as a pre-filter on control windows contributing to s^2.
2. Standard deviation of control scores (sd_controls): sample standard
   deviation with ddof=1.
3. Calibration check boundaries: calibration_in_doubt is True if
   abs(z_controls) >= 2.58, or sd_controls < 0.75, or sd_controls > 1.3, or
   fewer than 2 controls are evaluable.
4. Egg-check mean constant: literal 7.0711 as written in the protocol (rather
   than sqrt(50)).
5. Degenerate s^2 == 0: an egg whose pooled control trials have s^2 == 0 is
   treated as not usable rather than dividing by zero.
6. CSV edge cases: a '13,' line before the '12,' line stops the program;
   trailing fields beyond the egg count on '13,' lines are ignored if empty
   and stop the program if non-empty; day files are decoded as latin-1 so
   non-UTF-8 bytes in ignored lines do not abort parsing.
7. seconds_used for non-evaluable windows: reported as 0 if fewer than 5 eggs
   are usable, and as df (the count of seconds with N >= 5) if eggs_usable >= 5
   but df < 69,120; z is left empty in both cases.
8. Pair order in the sign-flip test: pairs are ordered as in events.tsv.
"""

from collections import defaultdict
import csv
from datetime import date, datetime, timedelta, timezone
import gzip
import json
import math
from pathlib import Path
import sys
import numpy as np

SECONDS_PER_DAY = 86400
MIN_EGG_TRIALS = 43200
MIN_CONTROL_TRIALS = 86400
MIN_EGGS = 5
MIN_SECONDS = 69120
THEORETICAL_SD = 7.0711


class TrialParser(dict):
    """Fast lookup/parser for trial sums applying Cleaning step 1."""

    def __init__(self) -> None:
        super().__init__()
        self[""] = math.nan
        for i in range(201):
            self[str(i)] = float(i) if abs(i - 100) < 45 else math.nan

    def __missing__(self, key: str) -> float:
        s = key.strip()
        if not s:
            val = math.nan
        else:
            x = float(s)
            val = x if abs(x - 100.0) < 45.0 else math.nan
        if len(self) < 2048:
            self[key] = val
        return val


def parse_utc(text: str) -> datetime:
    return datetime.strptime(text.strip(), "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=timezone.utc
    )


def day_start_ts(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())


def load_day(d: date, parser: TrialParser) -> tuple[list[int], np.ndarray]:
    path = Path("data") / f"basketdata-{d.isoformat()}.csv.gz"
    start_ts = day_start_ts(d)
    get_val = parser.__getitem__
    egg_ids: list[int] | None = None
    n_eggs = 0
    rows: list[list[float]] = []

    with gzip.open(path, "rt", encoding="latin-1") as f:
        for line in f:
            if line.startswith("13,"):
                if egg_ids is None:
                    raise ValueError(f"'13,' line before '12,' line in {path}")
                parts = line.rstrip("\r\n").split(",")
                offset = int(parts[1]) - start_ts
                if not (0 <= offset < SECONDS_PER_DAY):
                    raise ValueError(f"Timestamp out of UTC day {d} in {path}")
                vals = parts[3:]
                m = len(vals)
                if m == n_eggs:
                    rows[offset] = list(map(get_val, vals))
                elif m < n_eggs:
                    row = list(map(get_val, vals))
                    row.extend([math.nan] * (n_eggs - m))
                    rows[offset] = row
                else:
                    if any(v.strip() for v in vals[n_eggs:]):
                        raise ValueError(f"Extra fields on '13,' line in {path}")
                    rows[offset] = list(map(get_val, vals[:n_eggs]))
            elif line.startswith("12,"):
                if egg_ids is not None:
                    raise ValueError(f"Multiple '12,' lines in {path}")
                raw_ids = line.rstrip("\r\n").split(",")[3:]
                if not raw_ids:
                    raise ValueError(f"No egg numbers on '12,' line in {path}")
                egg_ids = [int(x.strip()) for x in raw_ids]
                if len(egg_ids) != len(set(egg_ids)):
                    raise ValueError(f"Duplicate egg numbers in {path}")
                n_eggs = len(egg_ids)
                empty_row = [math.nan] * n_eggs
                rows = [empty_row] * SECONDS_PER_DAY

    if egg_ids is None:
        raise ValueError(f"Missing '12,' line in {path}")

    return egg_ids, np.asarray(rows, dtype=np.float64)


def extract_window(
    start_dt: datetime,
    day_cache: dict[date, tuple[list[int], np.ndarray]],
    parser: TrialParser,
) -> tuple[list[int], np.ndarray]:
    d1 = start_dt.date()
    offset = int(start_dt.timestamp()) - day_start_ts(d1)
    if d1 not in day_cache:
        day_cache[d1] = load_day(d1, parser)
    eggs1, arr1 = day_cache[d1]
    if offset == 0:
        return eggs1, arr1

    d2 = d1 + timedelta(days=1)
    if d2 not in day_cache:
        day_cache[d2] = load_day(d2, parser)
    eggs2, arr2 = day_cache[d2]

    idx1 = {e: i for i, e in enumerate(eggs1)}
    idx2 = {e: i for i, e in enumerate(eggs2)}
    all_eggs = sorted(idx1.keys() | idx2.keys())
    n1 = SECONDS_PER_DAY - offset
    out = np.full((SECONDS_PER_DAY, len(all_eggs)), np.nan, dtype=np.float64)
    for j, e in enumerate(all_eggs):
        if e in idx1:
            out[:n1, j] = arr1[offset:, idx1[e]]
        if e in idx2:
            out[n1:, j] = arr2[:offset, idx2[e]]
    return all_eggs, out


def score_window(
    eggs: list[int],
    arr: np.ndarray,
    ref_s: dict[int, float],
) -> tuple[float | None, int, int]:
    d = arr - 100.0
    valid = ~np.isnan(d)
    counts = valid.sum(axis=0)

    usable_cols: list[int] = []
    usable_s: list[float] = []
    for j, e in enumerate(eggs):
        nj = int(counts[j])
        if nj < MIN_EGG_TRIALS:
            continue
        col = d[valid[:, j], j]
        if abs(float(np.mean(col))) / (THEORETICAL_SD / math.sqrt(nj)) > 5.0:
            continue
        ms = float(np.mean(col * col))
        if abs(ms / 50.0 - 1.0) * math.sqrt(nj / 2.0) > 5.0:
            continue
        s = ref_s.get(e)
        if s is None or s <= 0.0:
            continue
        usable_cols.append(j)
        usable_s.append(s)

    eggs_usable = len(usable_cols)
    if eggs_usable < MIN_EGGS:
        return None, 0, eggs_usable

    z_mat = d[:, usable_cols] / np.asarray(usable_s, dtype=np.float64)
    n_sec = np.sum(~np.isnan(z_mat), axis=1)
    used = n_sec >= MIN_EGGS
    df = int(np.sum(used))
    if df < MIN_SECONDS:
        return None, df, eggs_usable

    z_sec = np.nansum(z_mat[used], axis=1) / np.sqrt(n_sec[used])
    chi2 = float(np.sum(z_sec * z_sec))
    a = 2.0 / (9.0 * df)
    z_win = ((chi2 / df) ** (1.0 / 3.0) - (1.0 - a)) / math.sqrt(a)
    return float(z_win), df, eggs_usable


def fmt_z(val: float | None) -> str:
    return "" if val is None else f"{val:.6f}"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python replicate.py OUTDIR")
    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)

    events: list[dict[str, str]] = []
    with open("events.tsv", "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row["in_test"].strip() == "yes":
                events.append(row)

    parsed: list[tuple[datetime, datetime]] = []
    by_year: dict[int, list[int]] = defaultdict(list)
    for idx, row in enumerate(events):
        ev_dt = parse_utc(row["start_utc"])
        ctrl_dt = parse_utc(row["control_start_utc"])
        parsed.append((ev_dt, ctrl_dt))
        by_year[ev_dt.year].append(idx)

    parser = TrialParser()
    results: list[dict[str, object]] = [{} for _ in events]

    for year in sorted(by_year):
        indices = by_year[year]
        day_cache: dict[date, tuple[list[int], np.ndarray]] = {}
        ctrl_windows: list[tuple[list[int], np.ndarray]] = []
        ctrl_stats: list[dict[int, tuple[int, float]]] = []

        for idx in indices:
            _, ctrl_dt = parsed[idx]
            c_eggs, c_arr = extract_window(ctrl_dt, day_cache, parser)
            ctrl_windows.append((c_eggs, c_arr))
            d = c_arr - 100.0
            counts = np.sum(~np.isnan(d), axis=0)
            sum_d2 = np.nansum(d * d, axis=0)
            ctrl_stats.append(
                {e: (int(counts[j]), float(sum_d2[j])) for j, e in enumerate(c_eggs)}
            )

        all_ctrl_eggs: set[int] = set().union(*ctrl_stats) if ctrl_stats else set()

        def build_ref_s(exclude_pos: int | None) -> dict[int, float]:
            ref_s: dict[int, float] = {}
            for e in all_ctrl_eggs:
                tot_n = 0
                tot_d2 = 0.0
                for k, st in enumerate(ctrl_stats):
                    if k != exclude_pos and e in st:
                        nk, d2k = st[e]
                        tot_n += nk
                        tot_d2 += d2k
                if tot_n >= MIN_CONTROL_TRIALS and tot_d2 > 0.0:
                    ref_s[e] = math.sqrt(tot_d2 / tot_n)
            return ref_s

        event_ref_s = build_ref_s(None)
        for pos, idx in enumerate(indices):
            ev_dt, _ = parsed[idx]
            e_eggs, e_arr = extract_window(ev_dt, day_cache, parser)
            ev_z, ev_sec, ev_u = score_window(e_eggs, e_arr, event_ref_s)
            c_eggs, c_arr = ctrl_windows[pos]
            c_z, c_sec, c_u = score_window(c_eggs, c_arr, build_ref_s(pos))
            row = events[idx]
            results[idx] = {
                "event": row["event"],
                "start_utc": row["start_utc"],
                "z": ev_z,
                "seconds_used": ev_sec,
                "eggs_usable": ev_u,
                "control_start_utc": row["control_start_utc"],
                "control_z": c_z,
                "control_seconds_used": c_sec,
                "control_eggs_usable": c_u,
            }

        day_cache.clear()
        ctrl_windows.clear()

    ev_zs = np.array([r["z"] for r in results if r["z"] is not None], dtype=np.float64)
    c_zs = np.array(
        [r["control_z"] for r in results if r["control_z"] is not None],
        dtype=np.float64,
    )
    n_events = int(len(ev_zs))
    n_controls = int(len(c_zs))

    if n_events == 0:
        z_all = None
        departure = "not testable"
        size = "not testable"
    else:
        z_all = float(np.sum(ev_zs) / math.sqrt(n_events))
        if z_all >= 3.09:
            departure = "departure"
        elif z_all >= 1.645:
            departure = "suggestive"
        else:
            departure = "no positive excess detected"
        if z_all <= 0.33 * math.sqrt(n_events) - 1.645:
            size = "smaller than the benchmark"
        else:
            size = "not shown smaller than the benchmark"

    if n_controls == 0:
        z_controls = None
        sd_controls = None
        calibration_in_doubt = True
    else:
        z_controls = float(np.sum(c_zs) / math.sqrt(n_controls))
        if n_controls < 2:
            sd_controls = None
            calibration_in_doubt = True
        else:
            sd_controls = float(np.std(c_zs, ddof=1))
            calibration_in_doubt = (
                abs(z_controls) >= 2.58 or sd_controls < 0.75 or sd_controls > 1.3
            )

    diffs = np.array(
        [
            r["z"] - r["control_z"]
            for r in results
            if r["z"] is not None and r["control_z"] is not None
        ],
        dtype=np.float64,
    )
    pairs = int(len(diffs))
    if pairs == 0:
        paired = {
            "pairs": 0,
            "mean_difference": None,
            "p_one_sided_sign_flip": None,
        }
    else:
        obs_sum = float(np.sum(diffs))
        rng = np.random.default_rng(47)
        hits = 0
        for _ in range(20):
            signs = rng.integers(0, 2, (10000, pairs)) * 2 - 1
            hits += int(np.sum((signs @ diffs) >= obs_sum))
        paired = {
            "pairs": pairs,
            "mean_difference": float(np.mean(diffs)),
            "p_one_sided_sign_flip": (hits + 1) / 200001,
        }

    cols = [
        "event",
        "start_utc",
        "z",
        "seconds_used",
        "eggs_usable",
        "control_start_utc",
        "control_z",
        "control_seconds_used",
        "control_eggs_usable",
    ]
    with open(outdir / "windows.tsv", "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(cols) + "\n")
        for r in results:
            f.write(
                "\t".join(
                    [
                        str(r["event"]),
                        str(r["start_utc"]),
                        fmt_z(r["z"]),
                        str(r["seconds_used"]),
                        str(r["eggs_usable"]),
                        str(r["control_start_utc"]),
                        fmt_z(r["control_z"]),
                        str(r["control_seconds_used"]),
                        str(r["control_eggs_usable"]),
                    ]
                )
                + "\n"
            )

    summary = {
        "n_events": n_events,
        "z_all": z_all,
        "n_controls": n_controls,
        "z_controls": z_controls,
        "sd_controls": sd_controls,
        "departure": departure,
        "size": size,
        "calibration_in_doubt": calibration_in_doubt,
        "paired": paired,
    }
    with open(outdir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
