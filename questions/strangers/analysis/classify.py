#!/usr/bin/env python3
"""Put every flagged person of the corrected run into one described class. Writes results/corrected/hits_review.tsv.

The classes follow protocol.md ("Looking at each hit") and Amendment 1. Three of them rest on judgement made after
seeing the results; the reason is written beside each person. Run from questions/strangers.
"""
import collections
import csv
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
R = Q / "results" / "corrected"
hits = list(csv.DictReader(open(R / "hits.tsv"), delimiter="\t"))
spec = {r["genetic_id"]: r for r in csv.DictReader(open(R / "amended" / "specificity.tsv"), delimiter="\t")}
scan = {r["genetic_id"]: r for r in csv.DictReader(open(R / "scan.tsv"), delimiter="\t")}

SIBERIAN_RELATIVES = {"Kolyma1.SG", "M0831.SG", "M9984.SG", "KPT002.AG.SG", "RISE554_alt.SG"}
UNLIKE = {"R2.SG": "an early farmer whose neighbours are mostly hunter-gatherers",
          "ktg005.SG": "an early farmer in Morocco whose neighbours are a mix of European hunter-gatherers and north Africans",
          "I24277.AG.TW": "an early farmer whose neighbours of the same data type are a scattered mix of hunter-gatherers and farmers"}

people = collections.OrderedDict()
for h in hits:
    people.setdefault(h["genetic_id"], []).append(h)
rows = []
for gid, hs in people.items():
    h = hs[0]
    robust = any(x["robust"] == "True" for x in hs)
    raw = scan[gid].get("A_Z", "")
    if h["side"] == "american":
        if "Norse" in h["group"]:
            cls, why = "known", "medieval Norse settler in Greenland; the label says so"
        else:
            cls, why = "known", "Arctic people (Paleo-Inuit or Aleut) with Siberian ancestry; leans toward Han, not toward Europeans or Africans"
    elif gid == "CDE003.AG":
        cls, why = "metadata error", "a Cuban individual whose longitude is recorded as +77.8 instead of -77.8; Native American, as expected"
    elif not robust:
        cls, why = "not robust", "fails the transversion or second-reference check"
    elif spec.get(gid, {}).get("specific_to_native_americans") != "True":
        cls, why = "not specific", "Amendment 1: no closer to Native Americans than to the Altai hunter-gatherers; shared north Eurasian ancestry or unlike neighbours"
    elif "OldBeringSea" in h["group"]:
        cls, why = "known", "Old Bering Sea people of Chukotka, on the Asian shore of the Bering Strait; kin of Native Americans (from memory of the literature, not re-read)"
    elif gid in SIBERIAN_RELATIVES:
        cls, why = "known", "ancient north-east or central Siberian; closer kin of Native Americans than the Altai reference is (from memory of the literature, not re-read)"
    elif gid in UNLIKE:
        cls, why = "unlike neighbours", f"{UNLIKE[gid]}; the raw lean toward Native Americans is negative (Z = {raw or 'see profile'}), which real Native American ancestry would not give"
    else:
        cls, why = "standing", "no listed explanation applies"
    rows.append({"genetic_id": gid, "group": h["group"], "entity": h["entity"], "lat": h["lat"], "lon": h["lon"], "date_bp": h["date_bp"],
                 "side": h["side"], "tests": "+".join(sorted({x["test"] + ">" + x["toward"] for x in hs})), "max_Z": max(float(z) for x in hs for z in x["Z"].split(";")),
                 "robust": robust, "specific": spec.get(gid, {}).get("specific_to_native_americans", ""), "raw_lean_Z": raw, "class": cls, "why": why})
cols = list(rows[0].keys())
with open(R / "hits_review.tsv", "w") as f:
    f.write("\t".join(cols) + "\n")
    for r in rows:
        f.write("\t".join(str(r[c]) for c in cols) + "\n")
print(len(rows), "people;", dict(collections.Counter(r["class"] for r in rows)))
print("by side:", dict(collections.Counter((r["side"], r["class"]) for r in rows)))
ns = [r for r in rows if r["class"] == "not specific"]
print("not specific by entity:", collections.Counter(r["entity"] for r in ns).most_common())
print("standing:", [(r["genetic_id"], r["group"], r["max_Z"]) for r in rows if r["class"] == "standing"])
print("not robust:", [(r["genetic_id"], r["group"]) for r in rows if r["class"] == "not robust"])
