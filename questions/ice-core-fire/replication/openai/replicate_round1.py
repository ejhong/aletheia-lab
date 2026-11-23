# replicate.py -- Python 3.12, numpy
#
# Conventions where interpretation is needed:
# - Use float64, with no tolerance, snapping, or intermediate rounding other
#   than rounding the published ka labels to years. Out-of-file bins are
#   missing; neither bin construction nor background estimation stops at a
#   series' comparison-span boundary.
# - The background coverage test counts all present x, including nonpositives.
#   The log median and unscaled log MAD use just the positives, without a
#   second coverage test. A usable window needs only one defined z for Z;
#   the additional 80% test applies only to E.
# - All peak ages (including H and Z) use the youngest maximizer. Ties are
#   exact ties of the computed values. q counts OTHER windows equal to the
#   target, so rank + q is the last position in the tie.
# - A missing target measure is a null series entry for that measure in JSON.
#   Keep the file schemas as specified; print target tie/fraction diagnostics
#   and timing notes to stdout. Signed offsets are bin start minus 12896
#   (positive = older); no offset is calculated on the GISP2 clock.
# - Check timing pair by pair, reporting both checked and uncheckable pairs
#   if both support a tier pass. Testability counts distinct cores with a
#   target E in at least one decision series, not distinct passing tiers.

import csv
import json
import math
import sys
import warnings
from itertools import combinations
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


PANGAEA = Path("data/pangaea")
NOAA = Path("data/noaa")
SERIES = (
    # name, T, span start, span end
    ("N10", 10, 10300, 107620), ("E10", 10, 10300, 107620),
    ("N20", 20, 10300, 50000), ("E20", 20, 10300, 50000),
    ("G20", 20, 10300, 50000), ("N60", 60, 10300, 107620),
    ("E60", 60, 10300, 107620), ("G60", 60, 10300, 107620),
    ("N3", 3, 10300, 60000), ("N1", 1, 10300, 20000),
    ("G10", 10, 10300, 15000), ("E10h", 10, 0, 107620),
    ("G20h", 20, 0, 50000), ("G60h", 60, 0, 110000),
)
TIERS = (("N10", "E10"), ("N20", "E20", "G20"), ("N60", "E60", "G60"))
COLUMNS = "k start end bins with_value E E_age H H_age Z Z_age mean".split()


def pangaea(number):
    path = PANGAEA / f"{number}.tab"
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.startswith("*/"):
                break
        else:
            raise ValueError(f"No end of metadata in {path}")
        next(f)  # column names

        def pairs():
            for line in f:
                fields = line.rstrip("\r\n").split("\t", 5)
                if len(fields) == 1 and not fields[0].strip():
                    continue
                nh4 = fields[4].strip() if len(fields) > 4 else ""
                yield float(fields[0]), float(nh4) if nh4 else math.nan

        return np.fromiter(pairs(), dtype=np.dtype((np.float64, (2,)))).T


def gicc05():
    rows = []
    with (NOAA / "gicc05-60ka-20yr.txt").open(encoding="latin-1") as f:
        for line in f:
            fields = line.split()
            if len(fields) != 4:
                continue
            try:
                age, depth, _, _ = map(float, fields)
            except ValueError:
                continue
            rows.append((age, depth))
    age, depth = np.asarray(rows, dtype=float).T
    if not (np.all(np.diff(age) > 0) and np.all(np.diff(depth) > 0)):
        raise ValueError("Non-increasing GICC05 coordinates")
    return age, depth


def gisp2():
    rows = []
    with (NOAA / "iond.txt").open(encoding="latin-1") as f:
        for line in f:
            if line.split("\t", 1)[0].strip() == "Top":
                break
        else:
            raise ValueError("No GISP2 header")
        for line in f:
            fields = line.rstrip("\r\n").split("\t")
            if len(fields) < 12:
                continue  # blank or lacking the final age
            top, bot = (float(s.strip() or "nan") for s in fields[10:12])
            if top < bot < 999999:
                rows.append((top, bot, float(fields[3])))
    return np.asarray(rows, dtype=float).T


def sources():
    data = {}
    for core, number in (("N", 935814), ("E", 935831)):
        ka, value = pangaea(number)
        data[core] = (np.rint(ka * 1000).astype(np.int64), value)
    age, depth = gicc05()
    mm_depth, value = pangaea(935818)
    mm_age = np.interp(mm_depth, depth, age, left=np.nan, right=np.nan)
    keep = np.isfinite(mm_age)
    data["mm"] = (mm_age[keep], value[keep])
    data["G"] = gisp2()
    return data


def row_bins(age, value, a0, T, mm):
    j = np.floor_divide(age - a0, T).astype(np.int64) if not mm else (
        np.floor((age - a0) / T).astype(np.int64)
    )
    base = int(j.min())
    j -= base
    size = int(j.max()) + 1
    nominal = np.bincount(j, minlength=size) if mm else T // 10
    ok = np.isfinite(value)
    idx = j[ok]
    count = np.bincount(idx, minlength=size)
    total = np.bincount(idx, weights=value[ok], minlength=size)
    x = np.full(size, np.nan)
    np.divide(total, count, out=x, where=(count > 0) & (2 * count >= nominal))
    return base, x


def sample_bins(top, bot, value, a0, T):
    first = np.floor((top - a0) / T).astype(np.int64)
    stop = np.ceil((bot - a0) / T).astype(np.int64)
    counts = stop - first
    # Flatten the ragged ranges [first[i], stop[i]) of intersected bins.
    i = np.repeat(np.arange(top.size), counts)
    offsets = np.cumsum(counts) - counts
    j = np.arange(i.size) + (first - offsets)[i]
    left = a0 + j * T
    weight = np.minimum(left + T, bot[i]) - np.maximum(left, top[i])
    base = int(j.min())
    j -= base
    coverage = np.bincount(j, weights=weight)
    total = np.bincount(j, weights=weight * value[i])
    x = np.full(coverage.size, np.nan)
    np.divide(total, coverage, out=x, where=coverage >= T / 2)
    return base, x


def local_stats(x, T):
    n = 150 // T
    width = 2 * n + 1

    def neighborhoods(a):
        return sliding_window_view(np.pad(a, n, constant_values=np.nan), width)

    raw = neighborhoods(x)
    bg, z, numer, mad = (np.full(x.size, np.nan) for _ in range(4))
    if T != 60:
        logx = np.full(x.size, np.nan)
        np.log(x, out=logx, where=x > 0)
        logs = neighborhoods(logx)

    # Blocks limit median/MAD workspace even at annual resolution.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="All-NaN slice encountered",
                                category=RuntimeWarning)
        for i in range(0, x.size, 1024):
            s = slice(i, i + 1024)
            v = raw[s]
            enough = 2 * np.count_nonzero(np.isfinite(v), axis=1) >= width
            bg[s] = np.where(enough, np.nanmedian(v, axis=1), np.nan)
            if T == 60:
                continue
            lv = logs[s]
            lm = np.nanmedian(lv, axis=1)
            numer[s] = logx[s] - lm
            mad[s] = np.nanmedian(np.abs(lv - lm[:, None]), axis=1)
            good = enough & np.isfinite(numer[s]) & (mad[s] > 0)
            np.divide(numer[s], 1.4826 * mad[s], where=good, out=z[s])
    return bg, z, numer, mad


def windows(base, x, bg, z, a0, T, low, high):
    B = 300 // T
    measures = (("E", x - bg), ("H", x), ("Z", z))
    for k in range((low - a0 + 299) // 300, (high - a0) // 300):
        # Slice only the part in the file; all thresholds use the full B.
        left = max(0, k * B - base)
        right = min(x.size, (k + 1) * B - base)
        if right <= left:
            continue
        raw = x[left:right]
        count = int(np.count_nonzero(np.isfinite(raw)))
        if 5 * count < 4 * B:
            continue
        start = a0 + k * 300
        row = dict(k=k, start=start, end=start + 300, bins=B, with_value=count,
                   mean=float(np.nanmean(raw)))
        for name, arr in measures:
            v = arr[left:right]
            present = np.count_nonzero(np.isfinite(v))
            if present == 0 or (name == "E" and 5 * present < 4 * B):
                peak = age = math.nan
            else:
                idx = int(np.nanargmax(v))
                peak = float(v[idx])
                age = a0 + (base + left + idx) * T
            row[name] = peak
            row[name + "_age"] = age
        yield row


def rank(rows, target, name):
    if target is None or not math.isfinite(target[name]):
        return None, None
    value = target[name]
    values = [r[name] for r in rows if math.isfinite(r[name])]
    N = len(values)
    pos = 1 + sum(v > value for v in values)
    q = values.count(value) - 1
    return dict(value=value, rank=pos, N=N, in_top1=pos <= max(1, N // 100),
                in_top5=pos <= max(1, N // 20)), q


def decision(E, targets):
    cores = {s[0] for tier in TIERS for s in tier if E[s] is not None}
    passed = {1: False, 5: False}
    notes = []
    for tier in TIERS:
        for pct in (1, 5):
            qual = [s for s in tier if E[s] and E[s][f"in_top{pct}"]]
            for a, b in combinations(qual, 2):
                prefix = f"T{tier[0][1:]} at {pct}%: {a} + {b}: "
                if "G" in (a[0], b[0]):
                    note = "pass (timing not checkable)"
                elif abs(targets[a]["E_age"] - targets[b]["E_age"]) <= 60:
                    note = "pass (timing checked)"
                else:
                    notes.append(prefix + "high windows, different peaks")
                    continue
                passed[pct] = True
                notes.append(prefix + note)
    if len(cores) < 2:
        verdict = "not testable"
    elif passed[1]:
        verdict = "exceptional"
    elif passed[5]:
        verdict = "unusual"
    elif any(E[s] and E[s]["in_top1"] for tier in TIERS for s in tier):
        verdict = "not corroborated"
    else:
        verdict = "not met"
    return verdict, notes


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    data = sources()
    cache, targets, ties, z_details = {}, {}, {}, {}
    ranks = {m: {} for m in ("E", "H", "Z")}
    for s, T, low, high in SERIES:
        core = s[0]
        a0 = 12735 if core == "G" else 12750
        key = core, T
        if key not in cache:
            if core == "G":
                base, x = sample_bins(*data["G"], a0, T)
            else:
                mm = T in (1, 3)
                base, x = row_bins(*data["mm" if mm else core], a0, T, mm)
            cache[key] = (base, x, *local_stats(x, T))
        base, x, bg, z, numer, mad = cache[key]
        rows = list(windows(base, x, bg, z, a0, T, low, high))
        with (out / f"windows_{s}.tsv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, COLUMNS, delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        target = targets[s] = next((r for r in rows if r["k"] == 0), None)
        for m in ranks:
            ranks[m][s], ties[m, s] = rank(rows, target, m)
        if ranks["Z"][s]:
            idx = (target["Z_age"] - a0) // T - base
            z_details[s] = (numer[idx], mad[idx])

    verdict, notes = decision(ranks["E"], targets)
    with (out / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(dict(verdict=verdict, ranks=ranks), f, indent=2, allow_nan=False)
        f.write("\n")

    print("Verdict:", verdict)
    for m in ranks:
        for s, T, low, high in SERIES:
            r = ranks[m][s]
            if r is None:
                print(s, m, "missing")
                continue
            age = targets[s][m + "_age"]
            q = ties[m, s]
            detail = ""
            if m == "E" and s[0] != "G":
                detail = f" offset={age - 12896:+d} yr"
            if m == "E" and s in ("N1", "N3") and r["rank"] == 1:
                detail += f" (NGRIP, {low}-{high} b2k, {T}-yr bins; single core)"
            if m == "Z":
                num, d = z_details[s]
                detail = f" numerator={num} MAD={d}"
            print(f"{s} {m} rank={r['rank']}/{r['N']} q={q} "
                  f"realised={(r['rank'] + q) / r['N']:.8g} age={age}{detail}")
        if m == "E":
            for note in notes:
                print(note)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python replicate.py OUTDIR")
    main(Path(sys.argv[1]))
