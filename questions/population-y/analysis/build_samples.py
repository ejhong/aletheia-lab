#!/usr/bin/env python3
"""Build the sample sets for questions/population-y from AADR metadata only.

Reads the .anno and .ind files (never the genotypes) and the Natural Earth coastline, and writes:
  analysis/sets.tsv          one row per (set, individual): which individuals make up each population set
  analysis/ancient_cells.tsv one row per ancient region-by-period cell, with counts
The rules are the ones stated in protocol.md, "Sample sets". Standard library only.

    python3 analysis/build_samples.py            # run from questions/population-y
"""
import collections
import csv
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE.parent / "data"
ANNO = DATA / "aadr_v66.p1" / "v66.p1_1240K.aadr.PUB.anno"
IND = DATA / "aadr_v66.p1" / "v66.p1_1240K.aadr.patch.PUB.ind"
COAST = DATA / "naturalearth" / "ne_50m_coastline.geojson"

# Column numbers in the .anno file (0-based), checked against the header below.
C_GID, C_IID, C_PUB, C_DATE, C_GROUP, C_ENTITY, C_LAT, C_LON, C_DTYPE, C_NSNP, C_ASSESS = 0, 2, 6, 10, 14, 16, 17, 18, 21, 26, 47
HEADER_CHECK = {C_GID: "Genetic ID", C_IID: "Individual ID", C_PUB: "Publication abbreviation", C_DATE: "Date mean in BP",
                C_GROUP: "Group ID", C_ENTITY: "Political Entity", C_LAT: "Latitude", C_LON: "Longitude",
                C_DTYPE: "Data type", C_NSNP: "SNPs hit on autosomal targets (Computed using easystats on 1240k snpset)",
                C_ASSESS: "ASSESSMENT"}

PASS = {"Pass", "PROVISIONAL_PASS", "MERGE_PASS"}
AMERICAS = {"USA", "Canada", "Greenland", "Mexico", "Belize", "Guatemala", "Honduras", "El Salvador", "Nicaragua",
            "Costa Rica", "Panama", "Colombia", "Venezuela", "Ecuador", "Peru", "Bolivia", "Brazil", "Chile",
            "Argentina", "Uruguay", "Paraguay", "Guyana", "Suriname", "French Guiana", "Cuba", "Dominican Republic",
            "Puerto Rico", "Bahamas", "Haiti", "Jamaica", "Curacao", "Guadeloupe", "Saint Lucia", "St. Lucia",
            "Barbados", "Sint Maarten", "Trinidad and Tobago"}
MESO = {"Mexico", "Belize", "Guatemala", "Honduras", "El Salvador", "Nicaragua"}
CARIB = {"Cuba", "Dominican Republic", "Puerto Rico", "Bahamas", "Haiti", "Jamaica", "Curacao", "Guadeloupe",
         "Saint Lucia", "St. Lucia", "Barbados", "Sint Maarten", "Trinidad and Tobago"}
ISTHMO = {"Costa Rica", "Panama", "Colombia", "Venezuela", "Guyana", "Suriname", "French Guiana"}
EAST_SA = {"Brazil", "Paraguay", "Uruguay"}
COAST_KM = 75.0
BAD_LABEL = ("-o", "Ignore", "QCremove", "Discovery", "_o", "outlier")


def fl(x):
    try:
        return float(x)
    except ValueError:
        return None


def load():
    csv.field_size_limit(10 ** 9)
    with open(ANNO, encoding="utf-8", errors="replace", newline="") as f:
        r = csv.reader(f, delimiter="\t")
        header = next(r)
        for col, want in HEADER_CHECK.items():
            assert header[col].startswith(want), (col, header[col][:60])
        rows = list(r)
    ind = [line.split() for line in open(IND)]
    assert len(ind) == len(rows)
    out = []
    for i, (x, ir) in enumerate(zip(rows, ind)):
        assert x[C_GID] == ir[0], (i, x[C_GID], ir[0])
        out.append({"row": i, "gid": x[C_GID], "iid": x[C_IID], "pub": x[C_PUB], "date": fl(x[C_DATE]),
                    "group": ir[2],  # the label in the .ind file is the one the genotype file goes with
                    "entity": x[C_ENTITY], "lat": fl(x[C_LAT]), "lon": fl(x[C_LON]), "dtype": x[C_DTYPE],
                    "nsnp": int(fl(x[C_NSNP]) or 0), "assess": x[C_ASSESS]})
    return out


def pipeline(s):
    """Which present-day sequencing pipeline a genome comes from, by its Genetic ID."""
    g = s["gid"]
    if g.endswith(".DG") and (g.startswith("S_") or g.startswith("B_")):
        return "SGDP"
    if g.endswith(".DG") and g.startswith("HGDP"):
        return "NYGC"
    return None


def coast_points():
    """Coastline vertices, densified so that consecutive points are at most ~5 km apart."""
    pts = []
    for feat in json.load(open(COAST))["features"]:
        geom = feat["geometry"]
        lines = geom["coordinates"] if geom["type"] == "MultiLineString" else [geom["coordinates"]]
        segments = [(p1, p2) for line in lines for p1, p2 in zip(line, line[1:])]
        for p1, p2 in segments:
            (lo1, la1), (lo2, la2) = p1[:2], p2[:2]
            if not (-130 <= lo1 <= -30 and -60 <= la1 <= 35):
                continue
            d = haversine(la1, lo1, la2, lo2)
            n = max(1, int(d // 5) + 1)
            for k in range(n):
                t = k / n
                pts.append((la1 + t * (la2 - la1), lo1 + t * (lo2 - lo1)))
    return pts


def haversine(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(a))


def coast_km(s, pts):
    return min(haversine(s["lat"], s["lon"], la, lo) for la, lo in pts
               if abs(la - s["lat"]) < 6 and abs(lo - s["lon"]) < 6)


def region(s, pts):
    e, la, lo = s["entity"], s["lat"], s["lon"]
    if e in ("Greenland", "Canada"):
        return "NORTH"
    if e == "USA":
        if la is None:
            return "UNASSIGNED"
        return "NORTH" if la >= 50 else ("NAM_WEST" if lo < -100 else "NAM_EAST")
    if e in MESO:
        return "MESO"
    if e in CARIB:
        return "CARIB"
    if e in ISTHMO:
        return "ISTHMO_NSA"
    if e in EAST_SA:
        return "EAST_SA"
    if e in ("Peru", "Ecuador", "Bolivia", "Chile", "Argentina"):
        if la is None:
            return "UNASSIGNED"
        if e == "Bolivia":
            return "ANDES_INLAND"
        if e == "Chile" and la <= -30:
            return "SOUTH_CONE"
        if e == "Argentina":
            return "ANDES_INLAND" if (-30 < la < -21 and lo < -64) else "SOUTH_CONE"
        s["coast_km"] = round(coast_km(s, pts), 1)
        return "ANDES_COAST" if s["coast_km"] <= COAST_KM else "ANDES_INLAND"
    return "UNASSIGNED"


def period(d):
    return "EARLY" if d >= 8200 else ("MID" if d >= 4200 else "LATE")


def main():
    S = load()
    sets = collections.OrderedDict()

    def add(name, members):
        members = sorted(members, key=lambda s: s["row"])
        assert members, name
        sets[name] = members

    def present(group, pipe):
        return [s for s in S if s["group"] == group and pipeline(s) == pipe and s["assess"] in PASS]

    # --- Panel A (SGDP pipeline) and panel B (NYGC pipeline) -------------------------------------------------
    for g in ("Mbuti", "Yoruba", "Han", "French", "Sardinian", "Papuan", "Australian", "Mixe", "Surui", "Karitiana",
              "Pima", "Mayan", "Piapoco", "Quechua"):
        add(f"A.{g}", present(g, "SGDP"))
    add("A.MesoOther", [s for g in ("Mexico_Zapotec", "Nahua", "Mixtec_1", "Mixtec_2") for s in present(g, "SGDP")])
    add("A.Amazon", sets["A.Surui"] + sets["A.Karitiana"])
    for g in ("Mbuti", "Yoruba", "Han", "French", "Sardinian", "Papuan", "Nasioi", "Pima", "Mayan", "Surui",
              "Karitiana", "Piapoco"):
        add(f"B.{g}", present(g, "NYGC"))
    add("B.Amazon", sets["B.Surui"] + sets["B.Karitiana"])
    # --- Other fixed sets -----------------------------------------------------------------------------------
    add("ONG", [s for s in S if s["group"] == "ONG"])
    add("JAR", [s for s in S if s["group"] == "JAR"])
    add("Chimp", [s for s in S if s["gid"] == "Chimp.REF"])
    add("Tianyuan", [s for s in S if s["gid"] == "Tianyuan.AG.BY.AA"])
    # --- Same person sequenced by both pipelines (batch diagnostic) -----------------------------------------
    dupA, dupB = [], []
    for g in ("Surui", "Karitiana", "Pima", "Mayan", "Piapoco"):
        a = {s["iid"]: s for s in sets[f"A.{g}"]}
        b = {s["iid"]: s for s in sets[f"B.{g}"]}
        for iid in sorted(set(a) & set(b)):
            dupA.append(a[iid])
            dupB.append(b[iid])
    add("DUP.SGDP", dupA)
    add("DUP.NYGC", dupB)
    dup_people = {s["iid"] for s in dupB}
    add("B.Amazon.heldout", [s for s in sets["B.Amazon"] if s["iid"] not in dup_people])
    add("B.Pima.heldout", [s for s in sets["B.Pima"] if s["iid"] not in dup_people])

    # --- World panel W: present-day groups outside the Americas ---------------------------------------------
    cand = collections.defaultdict(dict)
    for s in S:
        if (s["date"] == 0 and s["entity"] not in AMERICAS and s["dtype"] in ("Shotgun.diploid", "Shotgun")
                and s["nsnp"] >= 900000 and s["assess"] in PASS and not any(b in s["group"] for b in BAD_LABEL)
                and s["group"] not in ("Mbuti", "MbutiPygmy")):
            best = cand[s["group"]].get(s["iid"])
            key = (pipeline(s) == "SGDP", s["nsnp"])
            if best is None or key > (pipeline(best) == "SGDP", best["nsnp"]):
                cand[s["group"]][s["iid"]] = s
    for g in sorted(cand):
        if len(cand[g]) >= 2:
            add(f"W.{g}", list(cand[g].values()))

    # --- Ancient Americans ----------------------------------------------------------------------------------
    pts = coast_points()
    anc = [s for s in S if s["entity"] in AMERICAS and s["date"] is not None and s["date"] >= 500]
    best = {}
    for s in anc:
        if s["nsnp"] >= 100000 and s["assess"] in PASS:
            if s["iid"] not in best or s["nsnp"] > best[s["iid"]]["nsnp"]:
                best[s["iid"]] = s
    cells = collections.defaultdict(list)
    for s in best.values():
        s["region"] = region(s, pts)
        cells[f"CELL.{s['region']}.{period(s['date'])}"].append(s)
    for name in sorted(cells):
        add(name, cells[name])
    for reg in sorted({s["region"] for s in best.values()}):
        add(f"REGION.{reg}", [s for s in best.values() if s["region"] == reg])
    add("ANC.SA", [s for s in best.values()
                   if s["region"] in ("ANDES_COAST", "ANDES_INLAND", "EAST_SA", "SOUTH_CONE", "ISTHMO_NSA")])
    add("ANC.NC", [s for s in best.values() if s["region"] in ("NAM_WEST", "NAM_EAST", "MESO")])
    # Named early individuals: every version with enough data, whatever its assessment.
    for s in anc:
        if s["date"] >= 9000 and s["nsnp"] >= 250000:
            add(f"EARLY.{s['gid']}", [s])
    # Same individual as capture and as shotgun data (data-type diagnostic).
    byiid = collections.defaultdict(list)
    for s in anc:
        if s["nsnp"] >= 400000 and s["assess"] in PASS:
            byiid[s["iid"]].append(s)
    vag, vsg = [], []
    for iid, v in sorted(byiid.items()):
        ag = [s for s in v if s["gid"].endswith(".AG")]
        sg = [s for s in v if s["gid"].endswith(".SG") and ".AG" not in s["gid"]]
        if ag and sg:
            vag.append(max(ag, key=lambda s: s["nsnp"]))
            vsg.append(max(sg, key=lambda s: s["nsnp"]))
    add("VER.AG", vag)
    add("VER.SG", vsg)

    with open(HERE / "sets.tsv", "w") as f:
        f.write("set\trow\tgenetic_id\tindividual_id\tgroup_id\tdate_bp\tentity\tlat\tlon\tcoast_km\tdata_type\tsnps_1240k\tassessment\n")
        for name, members in sets.items():
            for s in members:
                f.write("\t".join(str(v) for v in (name, s["row"], s["gid"], s["iid"], s["group"],
                                                   "" if s["date"] is None else int(s["date"]), s["entity"],
                                                   "" if s["lat"] is None else s["lat"],
                                                   "" if s["lon"] is None else s["lon"], s.get("coast_km", ""),
                                                   s["dtype"], s["nsnp"], s["assess"])) + "\n")
    with open(HERE / "ancient_cells.tsv", "w") as f:
        f.write("cell\tn\tmedian_snps\tdate_min\tdate_max\tgroup_ids\n")
        for name, members in sets.items():
            if name.startswith(("CELL.", "REGION.", "ANC.")):
                ns = sorted(s["nsnp"] for s in members)
                groups = collections.Counter(s["group"] for s in members)
                f.write(f"{name}\t{len(members)}\t{ns[len(ns) // 2]}\t{int(min(s['date'] for s in members))}\t"
                        f"{int(max(s['date'] for s in members))}\t"
                        + "; ".join(f"{g} ({n})" for g, n in groups.most_common()) + "\n")
    for name, members in sets.items():
        if not name.startswith(("W.", "EARLY.")):
            print(f"{name}\t{len(members)}")
    print("W groups:", sum(1 for n in sets if n.startswith("W.")), " EARLY versions:",
          sum(1 for n in sets if n.startswith("EARLY.")))


if __name__ == "__main__":
    main()
