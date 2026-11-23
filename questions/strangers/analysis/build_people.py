#!/usr/bin/env python3
"""Build the list of ancient people, their sides, data types and neighbour pools, from AADR metadata only.

    python3 analysis/build_people.py        # run from questions/strangers; writes analysis/people.tsv and refs.tsv

Reads the .anno and .ind files, never the genotypes. Rules are those of protocol.md. Needs numpy.
"""
import csv
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
D = HERE.parent / "data" / "aadr_v66.p1"
ANNO = D / "v66.p1_1240K.aadr.PUB.anno"
IND = D / "v66.p1_1240K.aadr.patch.PUB.ind"

PASS = {"Pass", "PROVISIONAL_PASS", "MERGE_PASS"}
AMERICAS = {"USA", "Canada", "Greenland", "Mexico", "Belize", "Guatemala", "Honduras", "El Salvador", "Nicaragua",
            "Costa Rica", "Panama", "Colombia", "Venezuela", "Ecuador", "Peru", "Bolivia", "Brazil", "Chile",
            "Argentina", "Uruguay", "Paraguay", "Guyana", "Suriname", "French Guiana", "Cuba", "Dominican Republic",
            "Puerto Rico", "Bahamas", "Haiti", "Jamaica", "Curacao", "Guadeloupe", "Saint Lucia", "Barbados",
            "Sint Maarten", "Trinidad and Tobago"}
EUROPE = {"United Kingdom", "Hungary", "Italy", "Austria", "Spain", "Germany", "Denmark", "France", "Poland", "Czechia"}
REF_LABELS = {"Mbuti": ["Mbuti"], "Yoruba": ["Yoruba"], "French": ["French"], "Sardinian": ["Sardinian"], "Han": ["Han"],
              "Papuan": ["Papuan"], "NA": ["Karitiana", "Surui", "Mixe", "Pima", "Piapoco", "Quechua"],
              "Mandenka": ["Mandenka"], "Japanese": ["Japanese"], "Australian": ["Australian"]}
K, MAX_KM, MAX_YEARS = 20, 1500.0, 1500.0
C = {"gid": 0, "iid": 2, "pub": 6, "method": 9, "date": 10, "date_sd": 11, "group": 14, "entity": 16, "lat": 17,
     "lon": 18, "nsnp": 26, "sex": 30, "y_hg": 35, "mt_hg": 38, "mt": 39, "angsd": 42, "hapconx": 43, "library": 44,
     "assess": 47, "warn": 48}
EHG_LABELS = {"Russia_Karelia_Mesolithic", "Russia_Karelia_Mesolithic_HG"}   # a reference, not tested


def fl(x):
    try:
        return float(x)
    except ValueError:
        return None


def kind(gid):
    if gid.endswith(".AG"):
        return "AG"
    if gid.endswith(".SG") and ".AG" not in gid:
        return "SG"
    if gid.endswith(".TW") and ".AG" not in gid:
        return "TW"
    return "other"


def side(entity, lat, lon):
    if entity not in AMERICAS:
        return "elsewhere"
    if lat is not None and lat >= 50 and entity in ("USA", "Canada", "Greenland"):
        return "american"                      # the Arctic, including the Aleutians and east Greenland
    if lon is None or lat is None:
        return "american"                      # no coordinates: by political entity
    if not (-170 <= lon <= -30):
        return "elsewhere"                     # e.g. Guam and the Marianas, recorded under USA
    if (entity == "Chile" and lon < -80) or (entity == "Ecuador" and lon < -85) or (lat < 30 and lon < -130):
        return "elsewhere"                     # Pacific islands: Rapa Nui, Galapagos, Hawaii
    return "american"


def main():
    csv.field_size_limit(10 ** 9)
    with open(ANNO, encoding="utf-8", errors="replace", newline="") as f:
        r = csv.reader(f, delimiter="\t")
        header = next(r)
        assert header[C["iid"]].startswith("Individual ID") and header[C["assess"]].startswith("ASSESSMENT")
        assert header[C["nsnp"]].startswith("SNPs hit on autosomal targets (Computed using easystats on 1240k snpset)")
        rows = list(r)
    ind = [line.split() for line in open(IND)]
    assert len(ind) == len(rows)

    # Present-day references: the two pipelines of #31, each person once, panel-A version preferred.
    refs = {}
    for name, labels in REF_LABELS.items():
        best = {}
        for i, (x, ir) in enumerate(zip(rows, ind)):
            g = ir[0]
            a = g.endswith(".DG") and (g.startswith("S_") or g.startswith("B_"))
            b = g.endswith(".DG") and g.startswith("HGDP")
            if ir[2] in labels and (a or b) and x[C["assess"]] in PASS:
                if x[C["iid"]] not in best or (a and not best[x[C["iid"]]][1]):
                    best[x[C["iid"]]] = (i, a)
        refs[name] = sorted(i for i, _ in best.values())
    refs["MA1"] = [i for i, ir in enumerate(ind) if ir[0] == "MA1.SG"]

    # The universe of ancient people.
    best = {}
    for i, (x, ir) in enumerate(zip(rows, ind)):
        d, n = fl(x[C["date"]]), int(fl(x[C["nsnp"]]) or 0)
        if d is None or d < 500 or x[C["assess"]] not in PASS or n < 100000:
            continue
        if x[C["iid"]] not in best or n > best[x[C["iid"]]]["nsnp"]:
            lat, lon = fl(x[C["lat"]]), fl(x[C["lon"]])
            best[x[C["iid"]]] = {"row": i, "gid": ir[0], "iid": x[C["iid"]], "group": ir[2], "entity": x[C["entity"]],
                                 "lat": lat, "lon": lon, "date": d, "nsnp": n, "type": kind(ir[0]),
                                 "side": side(x[C["entity"]], lat, lon), "pub": x[C["pub"]], "method": x[C["method"]][:40],
                                 "mt": x[C["mt"]], "angsd": x[C["angsd"]], "hapconx": x[C["hapconx"]],
                                 "date_sd": fl(x[C["date_sd"]]), "sex": x[C["sex"]], "y_hg": x[C["y_hg"]][:30],
                                 "mt_hg": x[C["mt_hg"]][:30], "library": x[C["library"]][:60],
                                 "assess": x[C["assess"]], "warn": x[C["warn"]][:200]}
    people = sorted(best.values(), key=lambda p: p["row"])
    refs["EHG"] = [p["row"] for p in people if p["group"] in EHG_LABELS]
    people = [p for p in people if p["group"] not in EHG_LABELS]
    for p in people:
        p["site"] = "" if p["lat"] is None or p["lon"] is None else f"{p['lat']:.2f},{p['lon']:.2f}"
    # Clean ancient American baselines, one per data type: American side, south of 50 degrees, not labelled Norse.
    clean = lambda p: p["side"] == "american" and p["lat"] is not None and p["lat"] < 50 and "Norse" not in p["group"]
    for t in ("AG", "SG", "TW"):
        refs[f"BASE_AM.{t}"] = [p["row"] for p in people if clean(p) and p["type"] == t]
    refs["ANCIENT_AMERICAN"] = [p["row"] for p in people if clean(p) and p["type"] == "AG" and p["nsnp"] >= 500000]
    for p in people:
        own = [r for r in refs.get(f"BASE_AM.{p['type']}", []) if r != p["row"]]
        p["baseline"] = (p["type"] if len(own) >= 20 else "AG") if p["side"] == "american" else ""

    # Neighbour pools: the 20 nearest people of the same side and data type, in kilometres plus years.
    for p in people:
        p["pool"] = []
    for s in ("american", "elsewhere"):
        for t in ("AG", "SG", "TW"):
            grp = [p for p in people if p["side"] == s and p["type"] == t and p["lat"] is not None and p["lon"] is not None]
            if len(grp) <= K:
                continue
            la = np.radians(np.array([p["lat"] for p in grp]))
            lo = np.radians(np.array([p["lon"] for p in grp]))
            dt = np.array([p["date"] for p in grp])
            for i, p in enumerate(grp):
                a = np.sin((la - la[i]) / 2) ** 2 + np.cos(la) * np.cos(la[i]) * np.sin((lo - lo[i]) / 2) ** 2
                km = 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
                yrs = np.abs(dt - dt[i])
                d = km + yrs
                same_site = np.array([q["site"] == p["site"] for q in grp])
                d[same_site] = np.inf              # neighbours come from other sites (and never include the person)
                order = np.argsort(d, kind="stable")[:K]   # ties go to the earlier line of the file
                if not np.all(np.isfinite(d[order])):
                    continue
                if np.all(km[order] <= MAX_KM) and np.all(yrs[order] <= MAX_YEARS):
                    p["pool"] = [grp[j]["row"] for j in order]

    cols = ["row", "gid", "iid", "group", "entity", "lat", "lon", "date", "date_sd", "nsnp", "type", "side", "site",
            "baseline", "sex", "y_hg", "mt_hg", "library", "pub", "method", "mt", "angsd", "hapconx", "assess", "warn", "pool"]
    with open(HERE / "people.tsv", "w") as f:
        f.write("\t".join(cols) + "\n")
        for p in people:
            f.write("\t".join(("" if p[c] is None else ",".join(map(str, p[c])) if c == "pool" else str(p[c]).replace("\t", " "))
                              for c in cols) + "\n")
    with open(HERE / "refs.tsv", "w") as f:
        f.write("set\trow\tgenetic_id\n")
        for name, rws in refs.items():
            for i in rws:
                f.write(f"{name}\t{i}\t{ind[i][0]}\n")

    n = len(people)
    by = lambda key: {k: sum(1 for p in people if key(p) == k) for k in sorted({key(p) for p in people})}
    print(f"{n} ancient people; side {by(lambda p: p['side'])}; type {by(lambda p: p['type'])}")
    print("with a pool:", by(lambda p: (p["side"], bool(p["pool"]))))
    print("references:", {k: len(v) for k, v in refs.items()})
    print("American-side baseline used:", by(lambda p: p["baseline"]))
    edge = [p for p in people if p["entity"] in AMERICAS and (p["lon"] is None or not (-165 <= p["lon"] <= -35) or p["side"] == "elsewhere")]
    for p in edge:
        print("  boundary case:", p["gid"], p["group"], p["entity"], p["lat"], p["lon"], "->", p["side"])
    europe = sum(1 for p in people if p["entity"] in EUROPE and p["side"] == "elsewhere" and p["nsnp"] >= 500000)
    print("European donors available:", europe)


if __name__ == "__main__":
    main()
