#!/usr/bin/env python3
"""Does the Tunguska airburst of 30 June 1908 show in Greenland ice? Analysis for questions/tunguska-calibration.

    python analysis/tunguska.py ingest     read the downloaded files, write data/standard/<core>.tsv (one row per sample)
    python analysis/tunguska.py counts     samples per year around the target, from the age columns only
    python analysis/tunguska.py dating     the year of the largest sulphur value near known eruptions, per core
    python analysis/tunguska.py blind      everything the protocol asks for, with 1905 to 1912 removed from every series
    python analysis/tunguska.py run        the locked analysis; writes results/

Run from questions/tunguska-calibration. Needs numpy. See protocol.md for every definition used here.
"""
import csv
import io
import json
import pathlib
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

import numpy as np

Q = pathlib.Path(__file__).resolve().parent.parent
D = Q / "data"
STD = D / "standard"
SPECIES = ("nh4", "no3", "bc", "s")
TARGET = 1908                       # the target window is the two years 1908 and 1909
WIDTH = 2
FIRST, LAST = 1800, 1990            # reference windows lie wholly inside these years
HALF = 15                           # background: the 15 years before the window and the 15 after
MIN_BG = 20                         # of those 30 years, at least this many must have a value
BLIND_YEARS = range(1905, 1913)     # removed from every series in a blind run

# core: (site, file, format, age spec, {species: column})
CORES = {
    "neem_s1": ("NEEM", "neem2011s1-sigl2022/PANGAEA.940553.tab", "pangaea", ("col", 1, "ce"),
                {"nh4": "[NH4]+ [µmol/l]", "no3": "[NO3]- [µmol/l]", "bc": "BC [µg/kg]", "s": "S [µg/kg]"}),
    "tunu2013": ("Tunu", "tunu2013/Tunu13_database_120216.csv", "csv", ("col", "est_yr_Chrono_v1", "ce"),
                 {"nh4": "nh4_uM", "no3": "hno3_uM", "bc": "BCconc_ng_g", "s": "S_ng_g"}),
    "tunu2022a": ("Tunu", "tunu2022/Tunu22a_database_120624.csv", "csv", ("col", "Age_yb1950_DRI_NGRIP2_Chronology", "bp"),
                  {"nh4": "NH4_uM", "no3": "HNO3_uM", "bc": "rBC_ng/g", "s": "S_ng/g"}),
    "tunu2022b": ("Tunu", "tunu2022/Tunu22b_database_120624.csv", "csv", ("col", "Age_yb1950_DRI_NGRIP2_Chronology", "bp"),
                  {"nh4": "NH4_uM", "no3": "HNO3_uM", "bc": "rBC_ng/g", "s": "S_ng/g"}),
    "tunu_n": ("Tunu", "tunu-n/Tunu_database_031814_CADIS.xlsx", "xlsx", ("col", "est_yr", "ce"),
               {"nh4": "nh4", "no3": "hno3", "s": "S"}),
    "humboldt": ("Humboldt", "humboldt/HumbMain_database_031814_CADIS.xlsx", "xlsx", ("col", "est_yr", "ce"),
                 {"nh4": "nh4", "no3": "hno3", "bc": "BCconc", "s": "S"}),
    "act11d": ("ACT11d", "act11d/ACT11d_database_031814_CADIS.xlsx", "xlsx", ("col", "est_yr", "ce"),
               {"nh4": "nh4", "no3": "hno3", "s": "S"}),
    "ht95": ("Hans Tausen", "ht95/HT95_database_DRI.csv", "csv", ("col", "Est_year", "ce"),
             {"nh4": "NH4_uM", "no3": "HNO3_uM", "bc": "rBC_ng_g", "s": "S_ng_g"}),
    "negis": ("NEGIS", "negis2012/negis2012chem.txt", "noaa-tab",
              ("depthmap", ["depth_m"], "negis2012/negis2012age.txt", "noaa-tab", "depth_m", "age_AD", "ce"),
              {"nh4": "NH4+"}),
    "ngrip1": ("NGRIP", "ngrip-ic/PANGAEA.944172.tab", "pangaea",
               ("depthmap", ["Depth top [m]", "Depth bot [m]"], "gicc05-rasmussen2022/PANGAEA.943193.tab", "pangaea", 2, 0, "b2k"),
               {"nh4": "[NH4]+ [µEq/l]", "no3": "NO3 [µEq/l]", "s": "[SO4]2- [µEq/l]"}),
    "b20": ("B20", "ngt-b21-mieding/PANGAEA.484984.tab", "pangaea", ("col", 6, "ce"),
            {"nh4": "[NH4]+ [µg/kg]", "no3": "[NO3]- [µg/kg]", "s": "[SO4]2- [µg/kg]"}),
    "summit2010": ("Summit", "summit2010/Zoe2_database_031814_CADIS.xlsx", "xlsx", ("col", "est_yr", "ce"),
                   {"nh4": "nh4", "no3": "hno3", "bc": "BCconc", "s": "S"}),
    "summit2023": ("Summit", "summit2023/Summit2023_ChemistryData_17to142m.csv", "csv", ("col", "est_yr", "ce"),
                   {"nh4": "nh4_uM", "no3": "hno3_uM", "bc": "BCconc_ng_g", "s": "S_ng_g"}),
}
# The cores of the test: those whose dating near 1900 the sulphur check supports (protocol, "Which cores"), and NEGIS.
TEST_CORES = ("neem_s1", "tunu2013", "tunu2022a", "humboldt", "act11d", "negis", "ngrip1")
# Reported apart: Summit (its 1908 layer was seen before the plan) and four cores whose dating the check does not support.
APART_CORES = ("summit2010", "summit2023", "tunu2022b", "tunu_n", "ht95", "b20")
MIN_SITES = {"nh4": 5, "no3": 4, "bc": 3, "s": 4}
LAB = {"NEEM": "DRI", "Tunu": "DRI", "Humboldt": "DRI", "ACT11d": "DRI", "NEGIS": "Copenhagen", "NGRIP": "Copenhagen and others"}


# ---------------------------------------------------------------------------------------------------------------------
# Reading the files as downloaded
# ---------------------------------------------------------------------------------------------------------------------
def num(x):
    try:
        v = float(str(x).strip())
    except ValueError:
        return None
    return v if v == v else None


def text_of(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass


def read_table(path, fmt):
    """Column names and rows (lists of strings)."""
    if fmt == "pangaea":
        lines = text_of(path).partition("*/")[2].strip("\n").splitlines()
        return lines[0].split("\t"), [l.split("\t") for l in lines[1:] if l.strip()]
    if fmt == "csv":
        rows = list(csv.reader(io.StringIO(text_of(path))))
        return [c.strip() for c in rows[0]], [r for r in rows[1:] if any(x.strip() for x in r)]
    if fmt == "noaa-tab":
        # NOAA template: comment lines (some wrapped without a leading #), then a line of column names, then the rows.
        lines = text_of(path).splitlines()
        start = next(i for i, l in enumerate(lines) if l.split("\t")[0].strip() == "depth_m")
        return [c.strip() for c in lines[start].split("\t")], [l.split("\t") for l in lines[start + 1:] if l.strip()]
    if fmt == "xlsx":
        ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        z = zipfile.ZipFile(path)
        strings = ["".join(t.text or "" for t in si.iter(ns + "t"))
                   for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(ns + "si")] if "xl/sharedStrings.xml" in z.namelist() else []
        out = []
        for row in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).iter(ns + "row"):
            vals = {}
            for c in row.findall(ns + "c"):
                ci = 0
                for ch in re.match(r"[A-Z]+", c.get("r")).group(0):
                    ci = ci * 26 + ord(ch) - 64
                v = c.find(ns + "v")
                vals[ci - 1] = "" if v is None else (strings[int(v.text)] if c.get("t") == "s" else v.text)
            if vals:
                out.append([vals.get(i, "") for i in range(max(vals) + 1)])
        return [c.strip() for c in out[0]], out[1:]
    raise ValueError(fmt)


def to_ce(v, unit):
    return {"ce": v, "bp": 1950 - v, "b2k": 2000 - v}[unit]


def samples(core):
    """One row per sample: decimal year CE, then the species (NaN where missing or not positive)."""
    site, rel, fmt, age, colmap = CORES[core]
    cols, rows = read_table(D / rel, fmt)
    ix = lambda c: c if isinstance(c, int) else cols.index(c)
    get = lambda r, i: num(r[i]) if len(r) > i else None
    if age[0] == "col":
        ai = ix(age[1])
        years = [to_ce(get(r, ai), age[2]) if get(r, ai) is not None else None for r in rows]
    else:
        _, dcols, afile, afmt, adc, aac, unit = age
        acols, arows = read_table(D / afile, afmt)
        di = adc if isinstance(adc, int) else acols.index(adc)
        yi = aac if isinstance(aac, int) else acols.index(aac)
        pts = sorted((num(r[di]), to_ce(num(r[yi]), unit)) for r in arows
                     if len(r) > max(di, yi) and num(r[di]) is not None and num(r[yi]) is not None)
        pd, py = np.array([p[0] for p in pts]), np.array([p[1] for p in pts])
        dix = [ix(c) for c in dcols]
        years = []
        for r in rows:
            d = [get(r, i) for i in dix]
            if any(x is None for x in d) or not (pd[0] <= sum(d) / len(d) <= pd[-1]):
                years.append(None)
            else:
                years.append(float(np.interp(sum(d) / len(d), pd, py)))
    out = []
    for r, y in zip(rows, years):
        if y is None or not (-3000 < y < 2100) or y in (-1.0, -0.999, -999.0):      # the last three are missing-age codes
            continue
        vals = []
        for sp in SPECIES:
            v = get(r, ix(colmap[sp])) if sp in colmap else None
            vals.append(v if v is not None and v > 0 else float("nan"))
        out.append([y] + vals)
    return np.array(sorted(out))


def ingest():
    STD.mkdir(parents=True, exist_ok=True)
    for core in CORES:
        a = samples(core)
        with open(STD / f"{core}.tsv", "w") as f:
            f.write("year\t" + "\t".join(SPECIES) + "\n")
            for row in a:
                f.write("%.4f\t" % row[0] + "\t".join("" if v != v else "%.6g" % v for v in row[1:]) + "\n")
        print(core, len(a), "samples", "%.1f to %.1f" % (a[0, 0], a[-1, 0]))


# ---------------------------------------------------------------------------------------------------------------------
# From the standard tables to the statistics
# ---------------------------------------------------------------------------------------------------------------------
def load(core):
    rows = [l.rstrip("\n").split("\t") for l in open(STD / f"{core}.tsv")][1:]
    return np.array([[float(x) if x else np.nan for x in r] for r in rows])


def annual(core, species, blind=False, peak=False):
    """{year: mean (or, with peak, the largest) of the samples dated in that calendar year}.

    A year counts if at least one of its samples has a value and at least half of them do.
    """
    a = load(core)
    yr = np.floor(a[:, 0]).astype(int)
    v = a[:, 1 + SPECIES.index(species)]
    out = {}
    for y in range(FIRST - HALF - 1, LAST + HALF + 2):
        m = yr == y
        ok = m & np.isfinite(v)
        if ok.sum() >= 1 and 2 * ok.sum() >= m.sum() and not (blind and y in BLIND_YEARS):
            out[y] = float(v[ok].max() if peak else v[ok].mean())
    return out


def starts(target=TARGET, width=WIDTH):
    """Window start years: the target and every window that tiles 1800 to 1990 with it, none overlapping."""
    k0 = -((target - FIRST) // width)
    return [target + width * k for k in range(k0, (LAST - target - width + 1) // width + 1)]


def window_z(series, y, width=WIDTH):
    """The largest yearly score in the window starting at y, or None. See protocol, 'The score of a window'."""
    bg = [np.log(series[t]) for t in list(range(y - HALF, y)) + list(range(y + width, y + width + HALF)) if t in series]
    if len(bg) < MIN_BG:
        return None
    med = float(np.median(bg))
    scale = 1.4826 * float(np.median(np.abs(np.array(bg) - med)))
    if scale <= 0:
        return None
    z = [(np.log(series[t]) - med) / scale for t in range(y, y + width) if t in series]
    return max(z) if z else None


def site_scores(series_by_core, target=TARGET, width=WIDTH):
    """{site: {window start: score}}: for a site with several cores, the mean of the cores' window scores."""
    out = {}
    for site in sorted({CORES[c][0] for c in series_by_core}):
        per = {}
        for y in starts(target, width):
            zs = [z for z in (window_z(series_by_core[c], y, width) for c in series_by_core if CORES[c][0] == site) if z is not None]
            if zs:
                per[y] = float(np.mean(zs))
        if per:
            out[site] = per
    return out


def network(scores, target, min_sites):
    """({window start: mean of the site scores}, the sites used).

    The sites used are those with a score in the target window. A reference window counts only if every one of
    those sites has a score there too, so every window is a mean over the same sites.
    """
    used = sorted(s for s in scores if target in scores[s])
    if len(used) < min_sites:
        return {}, used
    return {y: float(np.mean([scores[s][y] for s in used])) for y in scores[used[0]] if all(y in scores[s] for s in used)}, used


def rank_of(table, y):
    """Rank of window y among all windows in the table (1 = largest), the number of windows, and the fraction."""
    if y not in table:
        return None
    n = len(table)
    r = 1 + sum(v > table[y] for v in table.values())
    return {"value": round(table[y], 3), "rank": r, "n": n, "fraction": round(r / n, 4)}


def verdict(r):
    if r is None:
        return "not testable"
    return "exceptional" if r["fraction"] <= 0.04 else "elevated" if r["fraction"] <= 0.10 else "ordinary"


def get_series(species, cores=TEST_CORES, blind=False, peak=False):
    return {c: annual(c, species, blind, peak) for c in cores if species in CORES[c][4]}


def analyse(species, cores=TEST_CORES, blind=False, target=TARGET, width=WIDTH, peak=False, min_sites=None):
    series = get_series(species, cores, blind, peak)
    sc = site_scores(series, target, width)
    need = MIN_SITES[species] if min_sites is None else min_sites
    if blind:      # the target is hidden: use every site, and windows where all of them have a score
        used = sorted(sc)
        net = {y: float(np.mean([sc[s][y] for s in used])) for y in starts(target, width) if all(y in sc[s] for s in used)}
        return {"sites": used, "windows": len(net)}, sc, net, series
    net, used = network(sc, target, need)
    res = {"sites": used, "windows": len(net), "network": rank_of(net, target)}
    res["verdict"] = verdict(res["network"])
    res["by_site"] = {s: rank_of(sc[s], target) for s in sc}
    return res, sc, net, series


def excess(series_by_core, y=TARGET, width=WIDTH):
    """Per site: the largest target year over the median of the background years, minus one (0.5 = half a typical year more)."""
    per = {}
    for c, s in series_by_core.items():
        bg = [s[t] for t in list(range(y - HALF, y)) + list(range(y + width, y + width + HALF)) if t in s]
        now = [s[t] for t in range(y, y + width) if t in s]
        if len(bg) >= MIN_BG and now:
            per.setdefault(CORES[c][0], []).append(max(now) / float(np.median(bg)) - 1)
    return {site: round(float(np.mean(v)), 3) for site, v in per.items()}


def power(species, rng, sizes=(0.1, 0.25, 0.5, 1.0, 2.0, 4.0), share=(1.0, 0.5), trials=400, blind=True):
    """How often an added pulse of k typical years' worth, in one year of one window, is called elevated or exceptional."""
    base = get_series(species, TEST_CORES, blind)
    typical = {c: float(np.median([v for y, v in s.items() if 1880 <= y <= 1930])) for c, s in base.items()}
    sc0 = site_scores(base)
    sites = sorted(sc0)
    net0 = {y: float(np.mean([sc0[s][y] for s in sites])) for y in starts() if all(y in sc0[s] for s in sites)}
    pool = sorted(y for y in net0 if y + WIDTH - 1 < 1890 or y > 1925)
    out = {}
    for sh in share:
        for k in sizes:
            hits = {"elevated": 0, "exceptional": 0}
            for _ in range(trials):
                y0 = int(rng.choice(pool))
                t = y0 + int(rng.integers(0, WIDTH))                 # the same year at every site
                reached = [s for s in sites if rng.random() < sh]
                zs = []
                for site in sites:
                    z = []
                    for c in [c for c in base if CORES[c][0] == site]:
                        s2 = base[c]
                        if site in reached and t in s2:
                            s2 = dict(s2)
                            s2[t] = s2[t] + k * typical[c]
                        w = window_z(s2, y0)
                        if w is not None:
                            z.append(w)
                    zs.append(float(np.mean(z)))
                val = float(np.mean(zs))
                rank = 1 + sum(v > val for yy, v in net0.items() if yy != y0)
                hits["exceptional"] += rank / len(net0) <= 0.04
                hits["elevated"] += rank / len(net0) <= 0.10
            out[f"share {sh}, pulse {k}"] = {k2: round(v / trials, 3) for k2, v in hits.items()}
    return out


def counts():
    for core in CORES:
        a = load(core)
        yr = np.floor(a[:, 0]).astype(int)
        line = []
        for sp in SPECIES:
            if sp in CORES[core][4]:
                v = a[:, 1 + SPECIES.index(sp)]
                per = [int((np.isfinite(v) & (yr == y)).sum()) for y in range(1900, 1916)]
                line.append(f"{sp}: " + " ".join(map(str, per)))
        print(f"{core:11s} samples with a value in each year 1900..1915 |", " | ".join(line))


def dating():
    """Sulphur only. The year holding the largest yearly mean near each known eruption."""
    marks = {"Laki 1783": (1781, 1786), "Tambora 1815": (1814, 1819), "Krakatau 1883": (1882, 1887), "Katmai 1912": (1910, 1915)}
    for core in CORES:
        if "s" not in CORES[core][4]:
            continue
        s = annual(core, "s")
        row = []
        for name, (a, b) in marks.items():
            ys = [y for y in range(a, b + 1) if y in s]
            if ys:
                best = max(ys, key=lambda y: s[y])
                bgd = np.median([s[y] for y in range(a - 12, b + 12) if y in s])
                row.append(f"{name}: {best} (x{s[best] / bgd:.1f})")
        print(f"{core:11s}", " | ".join(row))


def blind_run():
    rng = np.random.default_rng(100)
    out = {}
    for sp in ("nh4", "no3", "bc"):
        res, sc, net, _ = analyse(sp, blind=True)
        out[sp] = {"sites": res["sites"], "windows": len(net), "first": min(net), "last": max(net),
                   "top_windows": sorted(((round(v, 2), y) for y, v in net.items()), reverse=True)[:6]}
        if sp == "nh4":
            out[sp]["power"] = power(sp, rng)
    print(json.dumps(out, indent=1))
    json.dump(out, open(Q / "explore" / "blind_run.json", "w"), indent=1)


def run():
    R = Q / "results"
    R.mkdir(exist_ok=True)
    rng = np.random.default_rng(100)
    out = {"target_window": [TARGET, TARGET + WIDTH - 1], "test_cores": list(TEST_CORES)}
    rows = []
    for sp in ("nh4", "no3", "bc", "s"):
        res, sc, net, series = analyse(sp)
        res["excess_over_typical_year"] = excess(series)
        ex = list(res["excess_over_typical_year"].values())
        res["excess_median_of_sites"] = round(float(np.median(ex)), 3) if ex else None
        res["sites_in_own_top_tenth"] = sorted(s for s, r in res["by_site"].items() if r and r["fraction"] <= 0.10)
        res["top_windows"] = sorted(((round(v, 2), y) for y, v in net.items()), reverse=True)[:10]
        res["yearly_means_1903_1913"] = {c: {y: round(s[y], 4) for y in range(1903, 1914) if y in s} for c, s in series.items()}
        short = lambda r: {"sites": r["sites"], "network": r["network"], "verdict": r["verdict"]}
        variants = {"three-year window, 1907 to 1909": short(analyse(sp, target=1907, width=3)[0]),
                    "largest sample of each year in place of its mean": short(analyse(sp, peak=True)[0])}
        for site in res["sites"]:
            variants[f"without {site}"] = short(analyse(sp, cores=tuple(c for c in TEST_CORES if CORES[c][0] != site),
                                                        min_sites=MIN_SITES[sp] - 1)[0])
        for name, lab_is_dri in (("DRI sites only", True), ("other laboratories only", False)):
            pick = tuple(c for c in TEST_CORES if (LAB[CORES[c][0]] == "DRI") == lab_is_dri)
            variants[name] = short(analyse(sp, cores=pick, min_sites=1)[0])
        variants["with the four cores of doubtful dating added"] = short(analyse(sp, cores=TEST_CORES + ("tunu2022b", "tunu_n", "ht95", "b20"))[0])
        res["variants"] = variants
        apart = {}
        for c in APART_CORES:
            if sp in CORES[c][4]:
                s1 = annual(c, sp)
                table = {y: z for y in starts() for z in [window_z(s1, y)] if z is not None}
                apart[c] = {"rank": rank_of(table, TARGET), "excess": excess({c: s1}).get(CORES[c][0]),
                            "yearly_means_1903_1913": {y: round(s1[y], 4) for y in range(1903, 1914) if y in s1}}
        res["reported_apart"] = apart
        if sp == "s":
            res["katmai_window_1912"] = rank_of(net, 1912)
        if sp == "nh4":
            res["power"] = power(sp, rng, blind=False)
        out[sp] = res
        for site, table in sc.items():
            rows += [(sp, site, y, round(z, 4)) for y, z in sorted(table.items())]
        rows += [(sp, "network", y, round(z, 4)) for y, z in sorted(net.items())]
        with open(R / f"annual_{sp}.tsv", "w") as f:
            f.write("core\tsite\tyear\tmean\n")
            for c in CORES:
                if sp in CORES[c][4]:
                    s1 = annual(c, sp)
                    for y in sorted(s1):
                        f.write(f"{c}\t{CORES[c][0]}\t{y}\t{s1[y]:.6g}\n")
    with open(R / "window_scores.tsv", "w") as f:
        f.write("species\tsite\twindow_start\tscore\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    json.dump(out, open(R / "summary.json", "w"), indent=1)
    for sp in ("nh4", "no3", "bc", "s"):
        print(sp, out[sp]["verdict"], out[sp]["network"], "| excess:", out[sp]["excess_median_of_sites"], "| sites in own top tenth:", out[sp]["sites_in_own_top_tenth"])


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    {"ingest": ingest, "counts": counts, "dating": dating, "blind": blind_run, "run": run}.get(mode, lambda: sys.exit(__doc__))()
