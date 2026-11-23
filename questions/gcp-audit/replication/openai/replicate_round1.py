# replicate.py -- Python 3.12, standard library and NumPy
#
# Conventions where interpretation matters:
# - windows.tsv fixes membership, order and controls. Use the supplied length
#   including the last second; the "600 df weight" label adds no extra weight.
# - The 183-day test compares EVENT begin instants, inclusively, in Unix
#   seconds. Deduplicate control days before subtracting all own-control days.
#   Block individual seconds, not whole event days; block endpoints are inclusive.
# - Egg identity is the integer egg number, not its position in a file.
#   Omitted trailing trials and whitespace-only trials are empty. Ignore surplus
#   empty trailing fields but reject surplus data and malformed integers.
#   On duplicates, a filled outlier replaces prior data and is then removed;
#   an empty field never replaces prior data. Reject empty/duplicate egg headers.
# - Pool mean squares are trial-weighted, not averages of daily estimates.
#   Window eligibility is separate for the event and control. Report the number
#   passing even when the whole window fails. Threshold endpoints count as
#   "within"; the comparison slope has an intercept.
# - Top-level control statistics use every evaluable control. Control verdict
#   and mean interval use complete pairs; interval is nominal mean +/- 1.96 SE.
#   Undefined summary numbers are null; an undefined statistic cannot trigger
#   a threshold. Extra comparison/uncertainty measures go to stderr only,
#   keeping the two output schemas exactly as in FORMAT.md.
# - Cache cleaned bytes (zero = missing), assuming archive files with unchanged
#   size and nanosecond mtime are unchanged. Cache files are installed atomically.

import csv
import gzip
import json
import math
import sys
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

DAY = 86400


def tsv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def timestamp(s):
    return int(datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC).timestamp())


def days(t, length):
    return range(t // DAY * DAY, (t + length - 1) // DAY * DAY + 1, DAY)


class TrialCodes(dict):
    def __missing__(self, token):
        x = int(token) if token.strip() else 0
        self[token] = value = x if 55 < x < 145 else 0
        return value


def cache_day(day, cache):
    date = datetime.fromtimestamp(day, UTC).date().isoformat()
    src = Path("data") / f"basketdata-{date}.csv.gz"
    st = src.stat()
    dest = cache / f"v1-{date}-{st.st_size}-{st.st_mtime_ns}.npy"
    if dest.exists():
        return dest
    with gzip.open(src, "rb") as f:
        lines = f.read().splitlines()
    headers = [s for s in lines if s.startswith(b"12,")]
    if len(headers) != 1:
        raise ValueError(f"{src}: expected one egg header, got {len(headers)}")
    eggs = [str(int(x)) for x in headers[0].split(b",")[3:]]
    k = len(eggs)
    if not k or len(set(eggs)) != k:
        raise ValueError(f"{src}: empty or duplicate egg list")
    raw, seen = bytearray(DAY * k), bytearray(DAY)
    codes = TrialCodes({b"": 0})
    lookup = codes.__getitem__
    for line in lines:
        if not line.startswith(b"13,"):
            continue
        fields = line.split(b",")
        i = int(fields[1]) - day
        if not 0 <= i < DAY:
            raise ValueError(f"{src}: timestamp {fields[1]!r} outside day")
        trials = fields[3:]
        if len(trials) > k:
            if any(v.strip() for v in trials[k:]):
                raise ValueError(f"{src}: too many trials at second {i}")
            del trials[k:]
        offset = i * k
        if seen[i]:
            for j, v in enumerate(trials):
                if v.strip():
                    raw[offset + j] = lookup(v)
        else:
            raw[offset:offset + len(trials)] = bytes(map(lookup, trials))
            seen[i] = 1
    # Packed structured records keep the egg IDs in the .npy header.
    records = np.frombuffer(raw, dtype=[(e, "u1") for e in eggs])
    with tempfile.NamedTemporaryFile(dir=cache, delete=False) as f:
        tmp = Path(f.name)
        try:
            np.save(f, records, allow_pickle=False)
        except BaseException:
            f.close()
            tmp.unlink(missing_ok=True)
            raise
    tmp.replace(dest)
    return dest


def load_day(path):
    a = np.load(path, mmap_mode="r", allow_pickle=False)
    ids = tuple(map(int, a.dtype.names))
    return ids, a.view("u1").reshape(DAY, len(ids))


def centered(x):
    v = x.astype(np.int16) - 100
    v[x == 0] = 0
    return v


def moments(x):
    v = centered(x)
    return (np.count_nonzero(x, axis=0), v.sum(axis=0, dtype=np.int64),
            (v * v).sum(axis=0, dtype=np.int64))  # |v| <= 44


def passes(n, total, squares):
    mean_ok = np.abs(total) <= 5 * 7.0711 * np.sqrt(n)
    ms_err = np.abs(squares / (50.0 * np.maximum(n, 1)) - 1)
    return (n > 0) & mean_ok & (ms_err * np.sqrt(n / 2) <= 5)


def reference_day(day, path, blocks):
    ids, x = load_day(path)
    keep = np.ones(DAY, dtype=bool)
    for a, b in blocks:
        if a < day + DAY and b >= day:
            keep[max(0, a-day):min(DAY, b-day+1)] = False
    n, total, sq = moments(x if keep.all() else x[keep])
    ok = (n >= 3600) & passes(n, total, sq)
    return [(ids[i], int(n[i]), int(sq[i])) for i in np.flatnonzero(ok)]


def weights(pool_days, daily):
    counts, squares = Counter(), Counter()
    for d in pool_days:
        for egg, n, q in daily[d]:
            counts[egg] += n
            squares[egg] += q
    return {e: math.sqrt(n / squares[e]) for e, n in counts.items() if n >= DAY}


def score(t, length, paths, w):
    parts = []
    for day in days(t, length):
        ids, a = load_day(paths[day])
        parts.append((ids, a[max(0, t-day):min(DAY, t+length-day)]))
    eggs = sorted({e for ids, _ in parts for e in ids if e in w})
    col = {e: j for j, e in enumerate(eggs)}
    x = np.zeros((length, len(eggs)), dtype=np.uint8)
    off = 0
    for ids, part in parts:
        for j, e in enumerate(ids):
            if e in col:
                x[off:off+len(part), col[e]] = part[:, j]
        off += len(part)
    n, total, sq = moments(x)
    use = (2*n >= length) & passes(n, total, sq)
    k = int(use.sum())
    if k < 2:
        return None, None, k
    x = x[:, use]
    per_sec = np.count_nonzero(x, axis=1)
    valid = per_sec > 0
    df = int(valid.sum())
    if df < 2 or 5*df < 4*length:
        return None, None, k
    sums = (centered(x) * np.array([w[e] for e in eggs])[use]).sum(axis=1)
    chi = np.sum(sums[valid] ** 2 / per_sec[valid])
    h = 2 / (9 * df)
    return float((np.cbrt(chi / df) - (1 - h)) / math.sqrt(h)), df, k


def combined(a):
    return float(a.sum() / math.sqrt(len(a))) if len(a) else None


def sd(a):
    return float(a.std(ddof=1)) if len(a) >= 2 else None


def mean(a):
    return float(a.mean()) if len(a) else None


def sign_flip(d):
    if not len(d):
        return None
    rng = np.random.default_rng(74)
    obs, hits = d.sum(), 0
    for _ in range(20):
        signs = rng.integers(0, 2, (10000, len(d))) * 2 - 1
        hits += int(np.count_nonzero((signs * d).sum(axis=1) >= obs))
    return (hits + 1) / 200001


def summarize(events, controls, published):
    e, c, p = (np.array(v, dtype=np.float64) for v in (events, controls, published))
    ev, cv = np.isfinite(e), np.isfinite(c)
    y, x = e[ev], p[ev]
    delta = np.abs(y - x)
    med = float(np.median(delta)) if len(delta) else None
    r = slope = None
    if len(x) >= 3 and np.ptp(x) > 0:
        xc, yc = x - x.mean(), y - y.mean()
        slope = float((xc @ yc) / (xc @ xc))
        if np.ptp(y) > 0:
            r = float(np.corrcoef(x, y)[0, 1])
    repro = "does not reproduce"
    if r is not None and r >= 0.9 and med <= 0.25 and 0.8 <= slope <= 1.25:
        repro = "reproduces closely"
    elif r is not None and r >= 0.7 and med <= 0.5:
        repro = "reproduces roughly"
    paired = ev & cv
    ep, cp = e[paired], c[paired]
    ze, zc, sc = combined(ep), combined(cp), sd(cp)
    d = ep - cp
    n, pflip = len(d), sign_flip(d)
    failure = ((zc is not None and abs(zc) >= 2.58) or
               (sc is not None and not 0.85 <= sc <= 1.2))
    event_label = ("departure" if n and ze >= 3.09 else
                   "suggestive" if n and ze >= 1.645 else "no positive excess detected")
    if n < 300:
        overall = "insufficient coverage"
    elif ze < 1.645:
        overall = "no excess found"
    elif event_label == "departure" and pflip <= 0.01 and not failure:
        overall = "the excess is in the event windows"
    elif zc >= 2.58 and pflip > 0.05:
        overall = "the excess is not specific to the events"
    else:
        overall = "mixed"
    cm = mean(cp)
    half = 1.96 * sc / math.sqrt(n) if n >= 2 else None
    extra = dict(slope=slope, mean_abs_difference=mean(delta), within_025=mean(delta <= .25),
                 within_05=mean(delta <= .5), control_mean_paired=cm,
                 control_mean_ci95=[cm-half, cm+half] if half is not None else None,
                 difference_se=sd(d)/math.sqrt(n) if n >= 2 else None)
    print(json.dumps(extra, allow_nan=False), file=sys.stderr)
    return dict(n_events=len(y), z_all=combined(y), n_controls=int(cv.sum()),
                z_controls=combined(c[cv]), sd_controls=sd(c[cv]),
                pairs=dict(n=n, z_events=ze, z_controls=zc, sd_controls=sc,
                           mean_difference=mean(d), p_one_sided_sign_flip=pflip),
                reproduction=dict(n=len(y), r=r, median_abs_difference=med,
                                  combined_ours=combined(y), combined_published=combined(x)),
                verdicts=dict(reproduction=repro, events=event_label, overall=overall,
                              controls=("calibration failure detected" if failure else
                                        "no calibration failure detected")))


def main(out):
    if (out / "windows.tsv").resolve() == Path("windows.tsv").resolve():
        raise SystemExit("OUTDIR must not overwrite the input windows.tsv")
    cache = out / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    rows = [r for r in tsv("windows.tsv") if r["in_test"] == "1"]
    blocks = [(int(b["begin_unix"]), int(b["end_unix"])) for b in tsv("sources/blocked.tsv")]
    windows, control_sets, needed = [], [], set()
    for r in rows:
        t, c = timestamp(r["begin_utc"]), timestamp(r["control_begin_utc"])
        length = int(r["seconds"])
        if length <= 0 or t + length - 1 != timestamp(r["end_utc"]):
            raise ValueError(f"inconsistent window length for {r['num']}")
        windows.append((t, c, length))
        control_sets.append(set(days(c, length)))
        needed.update(days(t, length))
    refs = set().union(*control_sets)
    paths = {d: cache_day(d, cache) for d in sorted(needed | refs)}
    daily = {d: reference_day(d, paths[d], blocks) for d in sorted(refs)}
    events, controls = [], []
    with (out / "windows.tsv").open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, delimiter="\t", lineterminator="\n")
        wr.writerow("num begin_utc event_z event_seconds_used event_eggs_usable control_begin_utc "
                    "control_z control_seconds_used control_eggs_usable".split())
        for r, (t, c, length), own in zip(rows, windows, control_sets):
            near = {d for (s, _, _), ds in zip(windows, control_sets)
                    if abs(t-s) <= 183*DAY for d in ds}
            w = weights(near - own, daily)
            ev, co = score(t, length, paths, w), score(c, length, paths, w)
            wr.writerow([r["num"], r["begin_utc"], *ev, r["control_begin_utc"], *co])
            events.append(ev[0])
            controls.append(co[0])
    summary = summarize(events, controls, [float(r["published_z"]) for r in rows])
    (out / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n",
                                      encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python replicate.py OUTDIR")
    main(Path(sys.argv[1]))
