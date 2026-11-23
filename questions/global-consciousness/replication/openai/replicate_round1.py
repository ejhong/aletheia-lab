#!/usr/bin/env python3
# Usage: python replicate.py OUTDIR
#
# Interpretive choices:
# - "Cleaned trials" for the scale pool means trials surviving the per-trial
#   cutoff, including those from control eggs/windows that fail a scoring
#   check. The egg check applies locally to the window being scored.
# - Pool by numeric egg ID and the paired event's UTC start year. Weight each
#   trial equally, not each control equally. A zero scale is unusable.
# - Align days by egg ID, not column position. A duplicate record replaces
#   the whole second, including any missing trailing fields. Empty extra
#   trailing data fields are harmless; nonempty extras, invalid integers,
#   and empty/duplicate egg identifiers are errors.
# - Count usable eggs after both egg and scale checks, and report actual
#   seconds meeting N >= 5 even for an unevaluable window.
# - Use sample SD for control scores. Undefined numeric summaries are null;
#   only defined calibration statistics can trigger their cutoffs. With no
#   evaluable events both verdicts are "not testable" per the protocol.
# - Preserve TSV order for output and sign-flip columns. Use the same NumPy
#   sum reduction for observed and flipped sums, counting ties without a
#   tolerance. With no evaluable pairs the mean and p-value are undefined.
# - Report the nominal event p-value and mean-score interval on stdout to
#   keep the two output file schemas exactly as specified.

import csv
import gzip
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import numpy as np


DAY = 86400
EPOCH = date(1970, 1, 1)


def clean(x):
    return x if 55 < x < 145 else 0  # zero encodes missing, never a kept sum


class TrialCodes(dict):
    def __missing__(self, token):
        return clean(int(token))


CODES = TrialCodes((str(x), clean(x)) for x in range(201))
CODES[""] = 0
DELTA = np.arange(145, dtype=np.int64) - 100
DELTA[0] = 0
SQUARE = DELTA * DELTA


def read_day(day):
    path = Path("data") / f"basketdata-{EPOCH + timedelta(days=day)}.csv.gz"
    ids = None
    records = []
    # Buffer just the records of one day: no assumption about header position.
    with gzip.open(path, "rt", encoding="latin-1", newline="") as f:
        for line in f:
            if line.startswith("13,"):
                records.append(line)
            elif line.startswith("12,"):
                if ids is not None:
                    raise ValueError(f"{path}: repeated 12 line")
                fields = next(csv.reader([line], strict=True))
                ids = tuple(map(int, fields[3:]))
                if not ids or len(set(ids)) != len(ids):
                    raise ValueError(f"{path}: empty or duplicate egg list")
    if ids is None:
        raise ValueError(f"{path}: missing 12 line")

    width = len(ids)
    buf = bytearray(DAY * width)
    encode = CODES.__getitem__
    midnight = day * DAY
    for row in csv.reader(records, strict=True):
        t = int(row[1]) - midnight
        if not 0 <= t < DAY:
            raise ValueError(f"{path}: timestamp outside day: {row[1]}")
        if len(row) > width + 3 and any(row[width + 3:]):
            raise ValueError(f"{path}: extra trial sums at {row[1]}")
        values = bytes(map(encode, row[3:3 + width]))
        pos = t * width
        buf[pos:pos + width] = values.ljust(width, b"\0")
    return ids, np.frombuffer(buf, dtype=np.uint8).reshape(DAY, width)


def segments(start):
    day, off = divmod(start, DAY)
    yield day, off, DAY
    if off:
        yield day + 1, 0, off


class Window:
    def __init__(self, parts):
        self.ids = sorted({egg for ids, _ in parts for egg in ids})
        index = {egg: i for i, egg in enumerate(self.ids)}
        self.raw = np.zeros((len(index), DAY), dtype=np.uint8)
        pos = 0
        for ids, data in parts:
            end = pos + len(data)
            self.raw[[index[e] for e in ids], pos:end] = data.T
            pos = end

        # Exact integer sufficient statistics: n, sum(x-100), sum((x-100)^2).
        self.stats = {}
        for egg, row in zip(self.ids, self.raw):
            hist = np.bincount(row, minlength=len(DELTA))
            self.stats[egg] = (DAY - int(hist[0]), int(hist @ DELTA),
                               int(hist @ SQUARE))


def make_reader(starts):
    remaining = Counter(d for start in starts for d, _, _ in segments(start))
    cache = {}

    def window(start):
        parts = []
        for d, lo, hi in segments(start):
            if d not in cache:
                cache[d] = read_day(d)
            ids, raw = cache[d]
            parts.append((ids, raw[lo:hi]))
            remaining[d] -= 1
            if not remaining[d]:
                del cache[d]
        return Window(parts)

    return window


def score(win, pool, is_control):
    count = np.zeros(DAY, dtype=np.int32)
    total = np.zeros(DAY, dtype=np.float64)
    usable = 0
    for egg, row in zip(win.ids, win.raw):
        n, offset, sq = win.stats[egg]
        if n < 43200 or abs(offset / n) / (7.0711 / math.sqrt(n)) > 5:
            continue
        if abs(sq / (50 * n) - 1) * math.sqrt(n / 2) > 5:
            continue
        nc, qc = pool.get(egg, (0, 0))
        if is_control:
            nc -= n
            qc -= sq
        if nc < DAY or qc <= 0:
            continue
        usable += 1
        count += row != 0
        # DELTA[0] is zero, so a missing observation adds no numerator.
        total += DELTA[row] / math.sqrt(qc / nc)

    good = count >= 5
    df = int(np.count_nonzero(good))
    if df < 69120 or usable < 5:
        return None, df, usable
    chi = float(np.sum(total[good] ** 2 / count[good]))
    a = 2 / (9 * df)
    return ((chi / df) ** (1 / 3) - (1 - a)) / math.sqrt(a), df, usable


def analyse(rows):
    groups = defaultdict(list)
    starts = []
    for i, r in enumerate(rows):
        e, c = (datetime.strptime(r[k], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
                for k in ("start_utc", "control_start_utc"))
        t, u = int(e.timestamp()), int(c.timestamp())
        groups[e.year].append((i, t, u))
        starts.extend((t, u))

    window = make_reader(starts)
    results = [None] * len(rows)
    for group in groups.values():
        controls = [window(u) for _, _, u in group]
        pool = defaultdict(lambda: [0, 0])
        for ctrl in controls:
            for egg, (n, _, sq) in ctrl.stats.items():
                pool[egg][0] += n
                pool[egg][1] += sq
        for (i, t, _), ctrl in zip(group, controls):
            results[i] = score(window(t), pool, False), score(ctrl, pool, True)
    return results


def paired_check(results):
    d = np.array([e[0] - c[0] for e, c in results
                  if e[0] is not None and c[0] is not None], dtype=np.float64)
    mean = p = None
    if len(d):
        observed = d.sum()
        mean = float(observed / len(d))
        rng = np.random.default_rng(47)
        hits = 0
        for _ in range(20):
            signs = rng.integers(0, 2, (10000, len(d))) * 2 - 1
            hits += int(np.count_nonzero((signs * d).sum(axis=1) >= observed))
        p = (hits + 1) / 200001
    return dict(pairs=len(d), mean_difference=mean, p_one_sided_sign_flip=p)


def combined(values):
    return math.fsum(values) / math.sqrt(len(values)) if values else None


def summarize(results):
    events = [e[0] for e, _ in results if e[0] is not None]
    controls = [c[0] for _, c in results if c[0] is not None]
    n = len(events)
    z, zc = combined(events), combined(controls)
    sd = float(np.std(controls, ddof=1)) if len(controls) >= 2 else None
    departure = size = "not testable"
    if n:
        departure = ("departure" if z >= 3.09 else "suggestive" if z >= 1.645
                     else "no positive excess detected")
        size = ("smaller than the benchmark" if z <= 0.33 * math.sqrt(n) - 1.645
                else "not shown smaller than the benchmark")
        mean = math.fsum(events) / n
        half = 1.96 / math.sqrt(n)
        print(f"Mean event score: {mean:.8g} (95% interval "
              f"{mean-half:.8g} to {mean+half:.8g}); nominal one-sided "
              f"p = {0.5 * math.erfc(z / math.sqrt(2)):.8g}")
    doubt = ((zc is not None and abs(zc) >= 2.58) or
             (sd is not None and not 0.75 <= sd <= 1.3))
    return dict(n_events=n, z_all=z, n_controls=len(controls), z_controls=zc,
                sd_controls=sd, departure=departure, size=size,
                calibration_in_doubt=doubt, paired=paired_check(results))


def main(out):
    with open("events.tsv", encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t") if r["in_test"] == "yes"]
    results = analyse(rows)
    summary = summarize(results)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "windows.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(("event", "start_utc", "z", "seconds_used", "eggs_usable",
                    "control_start_utc", "control_z", "control_seconds_used",
                    "control_eggs_usable"))
        for r, (e, c) in zip(rows, results):
            w.writerow((r["event"], r["start_utc"], *e, r["control_start_utc"], *c))
    (out / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)
                                      + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python replicate.py OUTDIR")
    main(Path(sys.argv[1]))
