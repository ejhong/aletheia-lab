"""Independent replication of the cooling-ammonium analysis protocol.

Ambiguities resolved and choices made:
1. Coverage and positivity for P, R, and H: The protocol specifies >= 4 of 5
   before bins and "every bin used must be positive" under D, and only adds
   after-bin counts under P, R, and H. Here, P and R also require >= 4 of 5
   before bins, H also requires >= 5 of 6 after bins 2..7, and every non-missing
   bin in a measure's numerator and denominator windows must be strictly > 0
   (a non-positive bin invalidates that measure rather than being dropped as
   missing).
2. Evaluability of P, R, and H when D is missing: Each measure is computed
   according to its own coverage and positivity rules; an event with undefined D
   is excluded from D counts and ranks, while its P, R, and H are still reported
   if defined.
3. Quiet-time reference pool for P and R: Quiet times are first filtered to
   multiples of 20 in [10500, 107520] with no listed event in [t-300, t+200]
   inclusive and with D defined (per core and ion). Percentiles for P and R are
   computed among the subset of those quiet times where P or R is also defined.
4. Published ages for isolation checks: All event-isolation rules (cooling
   selection, quiet-time exclusion, and H's 300-year post-onset check
   t - 300 < other_age < t) use published age_b2k values from events.tsv; GS-1
   is shifted from 12,896 to 12,900 only when forming its 20-year bins. (For
   GS-1, 12,896 and 12,900 give identical isolation results.)
5. Median for P: Standard median (mean of the two middle values when 4 of 5
   before bins are present).
6. Output formatting: events.tsv uses the exact columns specified in FORMAT.md
   (omitting H_pct), ordered by ion (ammonium, calcium), core (NGRIP, NEEM),
   and events.tsv row order; summary.json nests quiet_times as {ion: {core: n}}
   and reports "not testable" (with null rank) if GS-1 is not evaluable in
   either core.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
import json
import math
from pathlib import Path
from statistics import median
import sys
from typing import NamedTuple

import numpy as np

CORE_FILES: tuple[tuple[str, Path], ...] = (
    ("NGRIP", Path("data/pangaea/935814.tab")),
    ("NEEM", Path("data/pangaea/935831.tab")),
)
IONS: tuple[str, ...] = ("ammonium", "calcium")
ION_COL: dict[str, int] = {"calcium": 3, "ammonium": 4}


class Event(NamedTuple):
    name: str
    age: int
    kind: str
    unc: str


def load_core(path: Path) -> dict[str, dict[int, float]]:
    series: dict[str, dict[int, float]] = {ion: {} for ion in IONS}
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            if line.startswith("*/"):
                break
        next(f, None)  # skip column header line
        for raw in f:
            line = raw.rstrip("\r\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 6:
                parts.extend([""] * (6 - len(parts)))
            age = round(float(parts[0]) * 1000)
            for ion, idx in ION_COL.items():
                cell = parts[idx].strip()
                if cell:
                    val = float(cell)
                    if math.isfinite(val):
                        series[ion][age] = val
    return series


def load_events(path: Path) -> list[Event]:
    events: list[Event] = []
    with path.open("r", encoding="utf-8-sig") as f:
        next(f, None)  # skip header
        for raw in f:
            line = raw.rstrip("\r\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 5:
                parts.extend([""] * (5 - len(parts)))
            events.append(
                Event(
                    name=parts[0].strip(),
                    age=int(parts[2].strip()),
                    kind=parts[3].strip(),
                    unc=parts[4].strip(),
                )
            )
    return events


def select_coolings(events: list[Event]) -> list[tuple[Event, int, bool]]:
    selected: list[tuple[Event, int, bool]] = []
    for i, ev in enumerate(events):
        if ev.kind != "stadial onset":
            continue
        if ev.unc not in ("a", "b") and ev.name != "GS-1":
            continue
        t = ev.age
        if t - 200 < 10300 or t + 100 > 107620:
            continue
        if any(j != i and (t - 200 < o.age < t + 100) for j, o in enumerate(events)):
            continue
        h_isolated = not any(j != i and (t - 300 < o.age < t) for j, o in enumerate(events))
        eval_age = 12900 if ev.name == "GS-1" else t
        selected.append((ev, eval_age, h_isolated))
    return selected


def quiet_grid(events: list[Event]) -> list[int]:
    ages = sorted(ev.age for ev in events)
    return [
        t
        for t in range(10500, 107521, 20)
        if bisect_left(ages, t - 300) == bisect_right(ages, t + 200)
    ]


def pair_mean(series: dict[int, float], a1: int, a2: int) -> float | None:
    v1 = series.get(a1)
    v2 = series.get(a2)
    if v1 is not None and v2 is not None:
        return 0.5 * (v1 + v2)
    return v1 if v1 is not None else v2


def valid_bins(bins: list[float | None], min_count: int) -> list[float] | None:
    vals = [b for b in bins if b is not None]
    if len(vals) < min_count or any(b <= 0.0 for b in vals):
        return None
    return vals


def compute_measures(
    series: dict[int, float], t: int, compute_h: bool = True
) -> dict[str, float | None]:
    after_n = 15 if compute_h else 10
    after = [pair_mean(series, t - 20 * k - 20, t - 20 * k - 10) for k in range(after_n)]
    before = [pair_mean(series, t + 20 * k, t + 20 * k + 10) for k in range(5)]

    b_ok = valid_bins(before, 4)
    a27_ok = valid_bins(after[2:8], 5)
    a09_ok = valid_bins(after[0:10], 8)

    d_val = (
        math.log((sum(a27_ok) / len(a27_ok)) / (sum(b_ok) / len(b_ok)))
        if a27_ok is not None and b_ok is not None
        else None
    )
    p_val = (
        math.log(max(a09_ok) / median(b_ok))
        if a09_ok is not None and b_ok is not None
        else None
    )
    r_val = (
        math.log((sum(a09_ok) / len(a09_ok)) / (sum(b_ok) / len(b_ok)))
        if a09_ok is not None and b_ok is not None
        else None
    )
    h_val: float | None = None
    if compute_h and a27_ok is not None:
        a1014_ok = valid_bins(after[10:15], 4)
        if a1014_ok is not None:
            h_val = math.log((sum(a27_ok) / len(a27_ok)) / (sum(a1014_ok) / len(a1014_ok)))

    return {"D": d_val, "P": p_val, "R": r_val, "H": h_val}


def percentile(val: float | None, ref: np.ndarray) -> float | None:
    if val is None or ref.size == 0:
        return None
    return float(np.sum(ref < val)) / float(ref.size)


def decide_general(amm_d: dict[str, dict[str, tuple[float, float | None]]]) -> str:
    ge_two_thirds = True
    le_one_third = True
    for core, _ in CORE_FILES:
        others = [(d, pct) for name, (d, pct) in amm_d[core].items() if name != "GS-1"]
        m = len(others)
        if m == 0:
            return "mixed"
        k = sum(1 for d, pct in others if d > 0.0 and pct is not None and pct >= 0.75)
        if 3 * k < 2 * m:
            ge_two_thirds = False
        if 3 * k > m:
            le_one_third = False
    if ge_two_thirds:
        return "general"
    if le_one_third:
        return "not seen"
    return "mixed"


def decide_younger_dryas(
    amm_d: dict[str, dict[str, tuple[float, float | None]]],
) -> tuple[str, dict[str, int | None]]:
    ranks: dict[str, int | None] = {}
    counts: dict[str, int] = {}
    for core, _ in CORE_FILES:
        ev_map = amm_d[core]
        counts[core] = len(ev_map)
        if "GS-1" not in ev_map:
            ranks[core] = None
        else:
            gs1_d = ev_map["GS-1"][0]
            ranks[core] = 1 + sum(1 for d, _ in ev_map.values() if d > gs1_d)
    if ranks["NGRIP"] is None or ranks["NEEM"] is None:
        return "not testable", ranks
    if ranks["NGRIP"] == 1 and ranks["NEEM"] == 1:
        return "the largest", ranks
    if (
        ranks["NGRIP"] <= math.ceil(counts["NGRIP"] / 4)
        and ranks["NEEM"] <= math.ceil(counts["NEEM"] / 4)
    ):
        return "among the largest", ranks
    return "not among the largest", ranks


def fmt(val: float | None) -> str:
    return "" if val is None else repr(val)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python replicate.py OUTDIR")
    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)

    events = load_events(Path("events.tsv"))
    coolings = select_coolings(events)
    q_candidates = quiet_grid(events)
    cores = {name: load_core(path) for name, path in CORE_FILES}

    rows: list[str] = ["ion\tcore\tevent\tD\tD_pct\tP\tP_pct\tR\tR_pct\tH"]
    quiet_counts: dict[str, dict[str, int]] = {ion: {} for ion in IONS}
    amm_d: dict[str, dict[str, tuple[float, float | None]]] = {c: {} for c, _ in CORE_FILES}

    for ion in IONS:
        for core, _ in CORE_FILES:
            series = cores[core][ion]
            q_pools: dict[str, list[float]] = {"D": [], "P": [], "R": []}
            for t in q_candidates:
                m = compute_measures(series, t, compute_h=False)
                if m["D"] is None:
                    continue
                q_pools["D"].append(m["D"])
                if m["P"] is not None:
                    q_pools["P"].append(m["P"])
                if m["R"] is not None:
                    q_pools["R"].append(m["R"])
            q_ref = {k: np.array(v, dtype=np.float64) for k, v in q_pools.items()}
            quiet_counts[ion][core] = len(q_pools["D"])

            for ev, eval_age, h_isolated in coolings:
                m = compute_measures(series, eval_age, compute_h=h_isolated)
                d_pct = percentile(m["D"], q_ref["D"])
                p_pct = percentile(m["P"], q_ref["P"])
                r_pct = percentile(m["R"], q_ref["R"])
                if ion == "ammonium" and m["D"] is not None:
                    amm_d[core][ev.name] = (m["D"], d_pct)
                rows.append(
                    "\t".join(
                        [
                            ion,
                            core,
                            ev.name,
                            fmt(m["D"]),
                            fmt(d_pct),
                            fmt(m["P"]),
                            fmt(p_pct),
                            fmt(m["R"]),
                            fmt(r_pct),
                            fmt(m["H"]),
                        ]
                    )
                )

    (outdir / "events.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    general_verdict = decide_general(amm_d)
    yd_verdict, ranks = decide_younger_dryas(amm_d)
    summary = {
        "coolings": [ev.name for ev, _, _ in coolings],
        "quiet_times": quiet_counts,
        "general": general_verdict,
        "younger_dryas": yd_verdict,
        "rank": ranks,
    }
    (outdir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
