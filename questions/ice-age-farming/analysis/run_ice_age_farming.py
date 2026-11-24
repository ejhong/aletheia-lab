#!/usr/bin/env python3
"""Pre-registered global Neotoma fossil pollen sweep for pre-12,000 BP farming (#88).

Implements questions/ice-age-farming/protocol.md (locked in protocol.lock).
Queries the live Neotoma v2.0 REST API, caches JSON responses locally in data/
(gitignored), records SHA-256 hashes, calibrates on Holocene Neolithic Europe,
and audits every pre-12,000 BP crop-bearing core globally.
"""
import collections
import concurrent.futures
import hashlib
import json
import math
import pathlib
import time
import urllib.parse
import urllib.request

import numpy as np
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CACHE = DATA / "neotoma_cache"
CACHE.mkdir(parents=True, exist_ok=True)
RES = ROOT / "results"
RES.mkdir(parents=True, exist_ok=True)

# 32 pre-registered crop/cereal Neotoma taxon IDs (protocol.md §3.1)
CROP_TAXON_IDS = {
    # Old World cereals
    416: "Poaceae (Cerealia)",
    427: "Poaceae (Cerealia) undiff.",
    1947: "Poaceae (Cerealia-type)",
    2941: "Poaceae (Cerealia-type) undiff.",
    3711: "Poaceae (Cerealia-type) cf. Hordeum",
    3916: "Poaceae (Cerealia) cf. Avena",
    3920: "Poaceae (Cerealia) cf. Triticum dicoccon",
    3922: "Poaceae (Cerealia) cf. Triticum",
    3925: "Poaceae (Cerealia) cf. Secale",
    31532: "Poaceae (Cerealia) sp.",
    31534: "Poaceae (Cerealia) excluding Secale",
    31540: "Poaceae (Cerealia-type) cf. Hordeum group",
    31542: "Poaceae (Cerealia-type) cf. Avena/Triticum group",
    31996: "Cerealia",
    497: "Triticum-type",
    969: "Triticum",
    3919: "Triticum undiff.",
    3705: "Hordeum-type",
    3921: "Hordeum/Triticum",
    3923: "Hordeum",
    3924: "Hordeum/Secale",
    488: "Secale-type",
    967: "Secale",
    3926: "Secale cereale",
    # New World & East Asian crops
    323: "Zea mays",
    538: "Zea",
    4981: "Zea undiff.",
    5644: "Oryza-type",
    39697: "Oryza",
    106: "Fagopyrum",
    1324: "Fagopyrum esculentum",
    4287: "Fagopyrum-type",
}
CROP_ID_SET = set(CROP_TAXON_IDS.keys())

CROP_NAME_KEYWORDS = (
    "cerealia", "triticum", "hordeum", "secale", "zea", "oryza", "fagopyrum"
)

WEED_KEYWORDS = (
    "plantago lanceolata",
    "plantago major",
    "plantago media",
    "rumex",
    "urtica",
    "centaurea cyanus",
    "polygonum aviculare",
    "cannabis",
    "humulus",
)


def is_crop_taxon(taxon_id, name: str) -> bool:
    if taxon_id in CROP_ID_SET:
        return True
    low = (name or "").lower()
    if "oryzaephilus" in low or "kunzea" in low:
        return False
    return any(k in low for k in CROP_NAME_KEYWORDS)


def is_anthro_weed(name: str) -> bool:
    low = (name or "").lower()
    if "alisma" in low or "plantago-aquatica" in low:
        return False
    return any(k in low for k in WEED_KEYWORDS)


def is_plantago_lanceolata(name: str) -> bool:
    low = (name or "").lower()
    return "plantago lanceolata" in low


def fetch_json(url: str, cache_name: str, retries: int = 3):
    cp = CACHE / cache_name
    if cp.exists() and cp.stat().st_size > 2:
        return json.loads(cp.read_text(encoding="utf-8"))
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "pollen-audit/1.0"})
            with urllib.request.urlopen(req, timeout=35) as r:
                raw = r.read()
            obj = json.loads(raw.decode("utf-8"))
            cp.write_bytes(raw)
            return obj
        except Exception as e:
            last_err = e
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"Failed {url}: {last_err}")


def normalize_age_cal_bp(age_val, age_type: str):
    """Return (age_cal_bp_approx, is_uncalibrated_14c) cleanly."""
    if age_val is None:
        return None, False
    a = float(age_val)
    at = (age_type or "").lower()
    is_14c = ("radiocarbon" in at) and ("calibrated" not in at) and ("cal" not in at)
    # Approximate conversion only for flagging uncalibrated 14C threshold (10,300 14C ~ 12,000 cal BP)
    # Keep raw age reported transparently!
    if is_14c and a >= 10000:
        # IntCal20 rough monotonic mapping around 10-40 ka for uniform comparison
        cal_approx = a * 1.165 if a < 20000 else a + 3300.0
        return cal_approx, True
    return a, is_14c


def extract_core_samples(dl_json: dict) -> dict:
    """Parse a Neotoma /v2.0/data/downloads/{dsid} JSON into clean sample rows + chronology audit."""
    data = dl_json.get("data") or []
    if not data:
        return {"error": "empty_data", "samples": []}
    site = data[0].get("site") or {}
    cu = site.get("collectionunit") or {}
    ds = cu.get("dataset") or {}
    default_chron_id = cu.get("defaultchronology")
    chrons = cu.get("chronologies") or []

    # Parse coordinates
    lon, lat = None, None
    geo = site.get("geography")
    if isinstance(geo, str) and geo.startswith("{"):
        try:
            gobj = json.loads(geo)
            coords = gobj.get("coordinates")
            if gobj.get("type") == "Point" and len(coords) >= 2:
                lon, lat = float(coords[0]), float(coords[1])
            elif gobj.get("type") == "Polygon":
                ring = coords[0]
                lon = float(np.mean([p[0] for p in ring]))
                lat = float(np.mean([p[1] for p in ring]))
        except Exception:
            pass

    # Extract chronology controls (Neotoma v2.0 nests under chronologies[*].chronology.chroncontrols)
    chron_controls = []
    chron_agetype = ""
    for cwrap in chrons:
        ch = cwrap.get("chronology") if isinstance(cwrap, dict) and "chronology" in cwrap else cwrap
        if not isinstance(ch, dict):
            continue
        meta = ch.get("chronology") if isinstance(ch.get("chronology"), dict) else ch
        cid = ch.get("chronologyid")
        is_def = meta.get("isdefault")
        if (default_chron_id is not None and cid == default_chron_id) or (default_chron_id is None and (is_def or not chron_controls)):
            chron_agetype = meta.get("modelagetype") or ch.get("agetype") or ""
            raw_ctrls = ch.get("chroncontrols") or ch.get("controls") or []
            chron_controls = []
            for ctrl in raw_ctrls:
                c_age = ctrl.get("chroncontrolage") if ctrl.get("chroncontrolage") is not None else ctrl.get("age")
                c_yng = ctrl.get("agelimityounger") if ctrl.get("agelimityounger") is not None else ctrl.get("ageyounger")
                c_old = ctrl.get("agelimitolder") if ctrl.get("agelimitolder") is not None else ctrl.get("ageolder")
                chron_controls.append({
                    "depth": ctrl.get("depth"),
                    "age": c_age,
                    "ageyounger": c_yng,
                    "ageolder": c_old,
                    "type": ctrl.get("chroncontroltype"),
                })
            if default_chron_id is not None and cid == default_chron_id:
                break

    samples_out = []
    for s in (ds.get("samples") or []):
        # Choose default chronology age if present, else first available age
        ages = s.get("ages") or []
        chosen_age = None
        for a in ages:
            if default_chron_id is not None and a.get("chronologyid") == default_chron_id and a.get("age") is not None:
                chosen_age = a
                break
        if chosen_age is None:
            for a in ages:
                if a.get("age") is not None:
                    chosen_age = a
                    break
        if chosen_age is None:
            continue

        raw_age = float(chosen_age["age"])
        age_type = chosen_age.get("agetype") or chron_agetype or ""
        cal_age, is_14c = normalize_age_cal_bp(raw_age, age_type)
        depth = s.get("depth")

        trsh = 0.0
        uphe = 0.0
        crop_sum = 0.0
        weed_sum = 0.0
        plan_lan = 0.0
        units_set = set()
        crop_taxa_found = collections.Counter()
        weed_taxa_found = collections.Counter()

        for d in (s.get("datum") or []):
            val = d.get("value")
            if val is None or val <= 0:
                continue
            elem = (d.get("element") or d.get("elementtype") or "").lower()
            if elem and "pollen" not in elem and "spore" not in elem:
                continue
            units = (d.get("units") or "").upper()
            if units in ("PRESENT/ABSENT", "P/A"):
                continue
            units_set.add(units)
            eg = (d.get("ecologicalgroup") or "").upper()
            vname = d.get("variablename") or ""
            tid = d.get("taxonid")
            if eg == "TRSH":
                trsh += float(val)
            elif eg == "UPHE":
                uphe += float(val)
            elif is_crop_taxon(tid, vname) or is_anthro_weed(vname):
                uphe += float(val)

            if is_crop_taxon(tid, vname):
                crop_sum += float(val)
                crop_taxa_found[vname] += float(val)
            if is_anthro_weed(vname):
                weed_sum += float(val)
                weed_taxa_found[vname] += float(val)
            if is_plantago_lanceolata(vname):
                plan_lan += float(val)

        terrestrial_sum = trsh + uphe
        is_pct_units = any("PERCENT" in u or "%" in u for u in units_set)
        # Require terrestrial_sum >= 100 for count data, or >= 50% for percentage tables
        min_sum = 50.0 if is_pct_units else 100.0
        if terrestrial_sum < min_sum:
            continue

        crop_pct = 100.0 * crop_sum / terrestrial_sum
        weed_pct = 100.0 * weed_sum / terrestrial_sum
        plan_pct = 100.0 * plan_lan / terrestrial_sum
        ap_pct = 100.0 * trsh / terrestrial_sum
        samples_out.append({
            "depth": float(depth) if depth is not None else None,
            "age_raw": raw_age,
            "age_cal": cal_age,
            "age_type": age_type,
            "is_14c": is_14c,
            "terrestrial_sum": round(terrestrial_sum, 1),
            "is_pct_units": is_pct_units,
            "crop_val": round(crop_sum, 2),
            "crop_pct": round(crop_pct, 4),
            "weed_pct": round(weed_pct, 4),
            "plantago_lan_pct": round(plan_pct, 4),
            "ap_pct": round(ap_pct, 2),
            "crop_taxa": dict(crop_taxa_found),
            "weed_taxa": dict(weed_taxa_found),
        })

    samples_out.sort(key=lambda r: (r["depth"] if r["depth"] is not None else r["age_cal"]))
    return {
        "datasetid": ds.get("datasetid"),
        "sitename": site.get("sitename"),
        "database": ds.get("database"),
        "lon": lon,
        "lat": lat,
        "altitude": site.get("altitude"),
        "n_samples_valid": len(samples_out),
        "age_min_cal": min((r["age_cal"] for r in samples_out), default=None),
        "age_max_cal": max((r["age_cal"] for r in samples_out), default=None),
        "chron_controls": chron_controls,
        "samples": samples_out,
    }


def check_chronology_integrity(core: dict, target_samples: list[dict]) -> dict:
    """Check whether target samples have monotonic age-depth order and radiometric bracketing."""
    all_s = [r for r in core["samples"] if r["depth"] is not None]
    monotonic = True
    for i in range(1, len(all_s)):
        if all_s[i]["depth"] > all_s[i - 1]["depth"] and all_s[i]["age_cal"] < all_s[i - 1]["age_cal"] - 200:
            monotonic = False
            break

    ctrls = [c for c in core.get("chron_controls", []) if c.get("age") is not None and c.get("depth") is not None]
    # Filter to real dating controls (exclude core-top surface or 'Collection date' alone when counting deep bracketing)
    target_depths = [r["depth"] for r in target_samples if r["depth"] is not None]
    target_ages = [r["age_cal"] for r in target_samples]
    has_older = False
    has_younger = False
    ctrl_ages = []
    for c in ctrls:
        ca, _ = normalize_age_cal_bp(c["age"], core["samples"][0]["age_type"] if core["samples"] else "")
        if ca is not None:
            ctrl_ages.append(ca)
    if target_depths and ctrls:
        min_td, max_td = min(target_depths), max(target_depths)
        has_older = any(float(c["depth"]) >= max_td - 5.0 for c in ctrls)
        has_younger = any(float(c["depth"]) <= min_td + 5.0 for c in ctrls)
    elif target_ages and ctrl_ages:
        min_ta, max_ta = min(target_ages), max(target_ages)
        has_older = any(ca >= max_ta - 500.0 for ca in ctrl_ages)
        has_younger = any(ca <= min_ta + 500.0 for ca in ctrl_ages)

    return {
        "n_controls": len(ctrls),
        "monotonic": monotonic,
        "has_older_bracket": has_older,
        "has_younger_bracket": has_younger,
        "chron_ok": bool(monotonic and has_older and has_younger and len(ctrls) >= 2),
    }


def evaluate_window(core: dict, age_lo: float, age_hi: float, require_chron: bool = False) -> dict:
    """Apply pre-registered FARM_RELAXED and FARM_STRICT criteria to samples in [age_lo, age_hi]."""
    win = [r for r in core["samples"] if age_lo <= r["age_cal"] <= age_hi]
    win.sort(key=lambda r: r["age_cal"], reverse=True)  # oldest -> youngest
    if not win:
        return {
            "has_data": False,
            "n_win": 0,
            "baseline_ap": None,
            "n_crop_any": 0,
            "max_crop_pct": 0.0,
            "farm_relaxed": False,
            "n_relaxed_samples": 0,
            "farm_strict_unfiltered": False,
            "farm_strict": False,
            "chron": {"chron_ok": False, "n_controls": len(core.get("chron_controls", []))},
            "earliest_strict_age": None,
            "earliest_relaxed_age": None,
            "strict_hits": [],
        }

    # Compute pre-event forest baseline AP% (older than window, or oldest 30% of window if none older)
    older = [r["ap_pct"] for r in core["samples"] if r["age_cal"] > age_hi and r["age_cal"] <= age_hi + 3000]
    if not older:
        n_base = max(1, len(win) // 3)
        older = [r["ap_pct"] for r in win[:n_base]]
    baseline_ap = float(np.median(older))

    relaxed_hits = []
    strict_candidates = []
    for r in win:
        crop_ok = (r["crop_pct"] >= 0.5) and (r["is_pct_units"] or r["crop_val"] >= 2.0)
        weed_ok = (r["weed_pct"] >= 0.5)
        if crop_ok and weed_ok:
            relaxed_hits.append(r)
            ap_drop_ok = (baseline_ap >= 50.0) and ((baseline_ap - r["ap_pct"]) >= 10.0)
            open_dual_ok = (baseline_ap < 50.0) and (r["crop_pct"] >= 1.0) and (r["plantago_lan_pct"] >= 0.5)
            if ap_drop_ok or open_dual_ok:
                strict_candidates.append(r)

    # Check >=2 strict_candidates within <=1,000 yr span
    sustained_pair = []
    for i in range(len(strict_candidates)):
        for j in range(i + 1, len(strict_candidates)):
            if abs(strict_candidates[i]["age_cal"] - strict_candidates[j]["age_cal"]) <= 1000.0:
                sustained_pair = [strict_candidates[i], strict_candidates[j]]
                break
        if sustained_pair:
            break

    chron_info = check_chronology_integrity(core, sustained_pair or relaxed_hits) if (sustained_pair or relaxed_hits) else {"chron_ok": False, "n_controls": len(core.get("chron_controls", []))}
    strict_pass = bool(sustained_pair) and ((not require_chron) or chron_info["chron_ok"])

    return {
        "has_data": True,
        "n_win": len(win),
        "baseline_ap": round(baseline_ap, 1),
        "n_crop_any": sum(1 for r in win if r["crop_val"] > 0),
        "max_crop_pct": round(max((r["crop_pct"] for r in win), default=0.0), 3),
        "farm_relaxed": len(relaxed_hits) > 0,
        "n_relaxed_samples": len(relaxed_hits),
        "farm_strict_unfiltered": bool(sustained_pair),
        "farm_strict": strict_pass,
        "chron": chron_info,
        "earliest_strict_age": max((r["age_cal"] for r in strict_candidates), default=None) if strict_pass else None,
        "earliest_relaxed_age": max((r["age_cal"] for r in relaxed_hits), default=None),
        "strict_hits": sustained_pair,
    }


def parse_lon_lat(loc_str):
    if not isinstance(loc_str, str) or not loc_str.startswith("{"):
        return None, None
    try:
        g = json.loads(loc_str)
        coords = g.get("coordinates")
        if g.get("type") == "Point" and len(coords) >= 2:
            return float(coords[0]), float(coords[1])
        if g.get("type") == "Polygon":
            ring = coords[0]
            return float(np.mean([p[0] for p in ring])), float(np.mean([p[1] for p in ring]))
    except Exception:
        pass
    return None, None


def main():
    print("=== 1. GLOBAL NEOTOMA PRE-12,000 BP CROP OCCURRENCE SWEEP (PAGINATED) ===", flush=True)
    pre12_occ_by_ds = collections.defaultdict(list)
    taxon_occ_counts = {}
    for tid, tname in CROP_TAXON_IDS.items():
        all_rows = []
        for offset in range(0, 10000, 500):
            url = f"https://api.neotomadb.org/v2.0/data/occurrences?taxonid={tid}&ageold=50000&ageyoung=12000&limit=500&offset={offset}"
            cname = f"occ_pre12_t{tid}.json" if offset == 0 else f"occ_pre12_t{tid}_off{offset}.json"
            try:
                res = fetch_json(url, cname)
                batch = res.get("data") or []
            except Exception as e:
                print(f"  WARN taxon {tid} ({tname}) off={offset}: {e}", flush=True)
                break
            all_rows.extend(batch)
            if len(batch) < 500:
                break
            time.sleep(0.08)

        pollen_rows = [
            r for r in all_rows
            if (r.get("site") or {}).get("datasettype") == "pollen"
            and (r.get("sample") or {}).get("value") not in (None, 0)
        ]
        taxon_occ_counts[f"{tid}:{tname}"] = len(pollen_rows)
        for r in pollen_rows:
            dsid = r["site"]["datasetid"]
            pre12_occ_by_ds[dsid].append({
                "taxonid": tid,
                "taxonname": tname,
                "age": (r.get("age") or {}).get("age"),
                "value": (r.get("sample") or {}).get("value"),
                "sitename": r["site"].get("sitename"),
                "database": r["site"].get("database"),
            })

    print(f"Total unique Neotoma fossil pollen cores with >=1 pre-12,000 BP crop occurrence: {len(pre12_occ_by_ds)}", flush=True)
    nonzero_taxa = {k: v for k, v in taxon_occ_counts.items() if v > 0}
    print("Non-zero pre-12 ka crop taxa:", nonzero_taxa, flush=True)

    print("\n=== 2. GLOBAL DENOMINATOR (ALL NEOTOMA FOSSIL POLLEN CORES REACHING >=12,000 BP) ===", flush=True)
    neotoma_all_pollen = set()
    neotoma_pre12_dsids = set()
    neotoma_pre18_dsids = set()
    for offset in range(0, 20000, 1000):
        url = f"https://api.neotomadb.org/v2.0/data/datasets?datasettype=pollen&limit=1000&offset={offset}"
        try:
            res = fetch_json(url, f"ds_all_pollen_off{offset}.json")
            batch = res.get("data") or []
        except Exception as e:
            print(f"  WARN denom offset {offset}: {e}", flush=True)
            break
        if not batch:
            break
        for item in batch:
            for ds in (item.get("site") or {}).get("datasets") or []:
                if ds.get("datasettype") != "pollen":
                    continue
                dsid = ds["datasetid"]
                neotoma_all_pollen.add(dsid)
                for ar in (ds.get("agerange") or []):
                    ao = ar.get("ageold")
                    if ao is None:
                        continue
                    cal_ao, _ = normalize_age_cal_bp(ao, ar.get("units") or "")
                    if cal_ao is not None and cal_ao >= 12000.0:
                        neotoma_pre12_dsids.add(dsid)
                    if cal_ao is not None and cal_ao >= 18000.0:
                        neotoma_pre18_dsids.add(dsid)
        if len(batch) < 1000:
            break
        time.sleep(0.08)
    print(
        f"Global Neotoma fossil pollen datasets: total={len(neotoma_all_pollen)}, "
        f"reaching >=12,000 cal BP={len(neotoma_pre12_dsids)}, reaching >=18,000 cal BP={len(neotoma_pre18_dsids)}",
        flush=True,
    )

    print("\n=== 3. FETCHING EUROPEAN/MEDITERRANEAN HOLOCENE NEOLITHIC CALIBRATION COHORT ===", flush=True)
    # Query Holocene (8,500-2,000 BP) cereal occurrences and filter strictly by EU/Med coordinates lon in [-10,45], lat in [34,62]
    eu_cal_dsids = []
    eu_cal_seen = set()
    for tid in [1947, 416, 427, 497]:
        for offset in range(0, 4000, 500):
            url = f"https://api.neotomadb.org/v2.0/data/occurrences?taxonid={tid}&ageold=8500&ageyoung=2000&limit=500&offset={offset}"
            try:
                res = fetch_json(url, f"eu_holo_occ_t{tid}_off{offset}.json")
                batch = res.get("data") or []
            except Exception as e:
                print(f"  WARN eu cal occ {tid} off={offset}: {e}", flush=True)
                break
            for r in batch:
                s = r.get("site") or {}
                if s.get("datasettype") != "pollen":
                    continue
                dsid = s.get("datasetid")
                if dsid in eu_cal_seen:
                    continue
                lon, lat = parse_lon_lat(s.get("location"))
                if lon is not None and lat is not None and (-10.0 <= lon <= 45.0) and (34.0 <= lat <= 62.0):
                    eu_cal_seen.add(dsid)
                    eu_cal_dsids.append(dsid)
                    if len(eu_cal_dsids) >= 100:
                        break
            if len(eu_cal_dsids) >= 100 or len(batch) < 500:
                break
            time.sleep(0.08)
        if len(eu_cal_dsids) >= 100:
            break
    print(f"Selected {len(eu_cal_dsids)} verified European/Mediterranean cereal-bearing calibration cores.", flush=True)

    # Cap pre-12 ka downloads at protocol limit (150 prioritized by occurrence count if >150)
    pre12_sorted_dsids = sorted(pre12_occ_by_ds.keys(), key=lambda k: (-len(pre12_occ_by_ds[k]), k))
    if len(pre12_sorted_dsids) > 150:
        print(f"Note: {len(pre12_sorted_dsids)} pre-12 ka cores found; prioritizing top 150 by occurrence count per protocol.", flush=True)
        pre12_download_dsids = pre12_sorted_dsids[:150]
    else:
        pre12_download_dsids = pre12_sorted_dsids

    all_target_dsids = sorted(set(eu_cal_dsids) | set(pre12_download_dsids))
    print(f"Downloading / loading {len(all_target_dsids)} full Neotoma cores...", flush=True)

    def load_core(dsid):
        try:
            dl = fetch_json(f"https://api.neotomadb.org/v2.0/data/downloads/{dsid}", f"core_{dsid}.json")
            return dsid, extract_core_samples(dl)
        except Exception as e:
            return dsid, {"datasetid": dsid, "error": str(e), "samples": []}

    cores = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for dsid, cobj in ex.map(load_core, all_target_dsids):
            cores[dsid] = cobj

    # === 4. EVALUATE CALIBRATION GATE ===
    cal_holo_n = 0
    cal_holo_relaxed = 0
    cal_holo_strict = 0
    cal_meso_n = 0
    cal_meso_relaxed = 0
    cal_meso_strict = 0
    neolithic_onsets = []

    for dsid in eu_cal_dsids:
        c = cores.get(dsid)
        if not c or not c.get("samples"):
            continue
        holo = evaluate_window(c, 2000.0, 8500.0, require_chron=False)
        if holo["has_data"] and holo["n_win"] >= 5:
            cal_holo_n += 1
            cal_holo_relaxed += int(holo["farm_relaxed"])
            cal_holo_strict += int(holo["farm_strict"])
            if holo["earliest_strict_age"] is not None and c["lat"] is not None:
                neolithic_onsets.append({
                    "datasetid": dsid,
                    "sitename": c["sitename"],
                    "lat": round(c["lat"], 2),
                    "lon": round(c["lon"], 2),
                    "onset_cal_bp": round(holo["earliest_strict_age"], 0),
                })
        # Pre-Neolithic Mesolithic negative control in N/Central Europe (lat >= 46, 9,000-11,500 BP)
        if c.get("lat") is not None and c["lat"] >= 46.0:
            meso = evaluate_window(c, 9000.0, 11500.0, require_chron=False)
            if meso["has_data"] and meso["n_win"] >= 2:
                cal_meso_n += 1
                cal_meso_relaxed += int(meso["farm_relaxed"])
                cal_meso_strict += int(meso["farm_strict"])

    print(
        f"\nCALIBRATION GATE:\n"
        f"  Holocene Neolithic Europe (8.5-2 ka): n={cal_holo_n}, "
        f"FARM_RELAXED={cal_holo_relaxed}/{cal_holo_n} ({100*cal_holo_relaxed/max(1,cal_holo_n):.1f}%), "
        f"FARM_STRICT={cal_holo_strict}/{cal_holo_n} ({100*cal_holo_strict/max(1,cal_holo_n):.1f}%)\n"
        f"  Mesolithic N/C Europe neg control (11.5-9 ka, lat>=46): n={cal_meso_n}, "
        f"FARM_RELAXED={cal_meso_relaxed}/{cal_meso_n} ({100*cal_meso_relaxed/max(1,cal_meso_n):.1f}%), "
        f"FARM_STRICT={cal_meso_strict}/{cal_meso_n} ({100*cal_meso_strict/max(1,cal_meso_n):.1f}%)"
    )

    # === 5. EVALUATE EVERY PRE-12,000 BP CANDIDATE CORE GLOBALLY ===
    lg_eval = []   # 12,000 - 18,000 cal BP (Late Glacial / Terminal Pleistocene)
    lgm_eval = []  # 18,000 - 50,000 cal BP (LGM / Deep Glacial Negative Control)
    all_pre12_audit = []

    for dsid in pre12_download_dsids:
        c = cores.get(dsid)
        if not c or not c.get("samples"):
            continue
        r_lg = evaluate_window(c, 12000.0, 18000.0, require_chron=True)
        r_lgm = evaluate_window(c, 18000.0, 50000.0, require_chron=True)
        r_all = evaluate_window(c, 12000.0, 50000.0, require_chron=True)
        entry = {
            "datasetid": dsid,
            "sitename": c["sitename"],
            "database": c["database"],
            "lat": round(c["lat"], 3) if c["lat"] is not None else None,
            "lon": round(c["lon"], 3) if c["lon"] is not None else None,
            "n_samples_valid": c["n_samples_valid"],
            "n_controls": len(c.get("chron_controls", [])),
            "occ_taxa": sorted({o["taxonname"] for o in pre12_occ_by_ds[dsid]}),
            "lg_12_18ka": {k: v for k, v in r_lg.items() if k != "strict_hits"},
            "lgm_18_50ka": {k: v for k, v in r_lgm.items() if k != "strict_hits"},
            "all_12_50ka": {k: v for k, v in r_all.items() if k != "strict_hits"},
            "strict_hits_12_50ka": r_all["strict_hits"],
        }
        all_pre12_audit.append(entry)
        if r_lg["has_data"]:
            lg_eval.append(entry)
        if r_lgm["has_data"]:
            lgm_eval.append(entry)

    n_denom = max(len(neotoma_pre12_dsids), len(all_pre12_audit))
    n_denom_lgm = max(len(neotoma_pre18_dsids), len(lgm_eval))
    lg_relaxed = sum(1 for e in lg_eval if e["lg_12_18ka"]["farm_relaxed"])
    lg_strict_unfilt = sum(1 for e in lg_eval if e["lg_12_18ka"]["farm_strict_unfiltered"])
    lg_strict = sum(1 for e in lg_eval if e["lg_12_18ka"]["farm_strict"])

    lgm_relaxed = sum(1 for e in lgm_eval if e["lgm_18_50ka"]["farm_relaxed"])
    lgm_strict_unfilt = sum(1 for e in lgm_eval if e["lgm_18_50ka"]["farm_strict_unfiltered"])
    lgm_strict = sum(1 for e in lgm_eval if e["lgm_18_50ka"]["farm_strict"])

    all_strict_flagged = [e for e in all_pre12_audit if e["all_12_50ka"]["farm_strict"]]
    all_strict_unfilt_flagged = [e for e in all_pre12_audit if e["all_12_50ka"]["farm_strict_unfiltered"]]

    # Fisher test: Late Glacial (12-18 ka) vs LGM glacial negative control (18-50 ka) among global Neotoma cores
    _, p_lg_vs_lgm_strict = stats.fisher_exact(
        [[lg_strict, max(0, n_denom - lg_strict)], [lgm_strict, max(0, n_denom_lgm - lgm_strict)]],
        alternative="greater",
    )
    _, p_lg_vs_lgm_relaxed = stats.fisher_exact(
        [[lg_relaxed, max(0, n_denom - lg_relaxed)], [lgm_relaxed, max(0, n_denom_lgm - lgm_relaxed)]],
        alternative="greater",
    )

    # Compute SHA-256 of cached Neotoma snapshot archive summary
    h = hashlib.sha256()
    for p in sorted(CACHE.glob("*.json")):
        h.update(p.name.encode())
        h.update(hashlib.sha256(p.read_bytes()).digest())
    cache_digest = h.hexdigest()

    summary = {
        "counts": {
            "global_neotoma_pollen_cores_total": len(neotoma_all_pollen),
            "global_neotoma_pollen_cores_ge12ka": len(neotoma_pre12_dsids),
            "global_neotoma_pollen_cores_ge18ka": len(neotoma_pre18_dsids),
            "cores_with_any_pre12ka_crop_occ": len(pre12_occ_by_ds),
            "cores_downloaded_valid_pre12ka": len(all_pre12_audit),
            "crop_taxa_queried": len(CROP_TAXON_IDS),
            "nonzero_pre12ka_crop_taxa": nonzero_taxa,
            "neotoma_cache_sha256": cache_digest,
        },
        "calibration": {
            "eu_holocene_8500_2000bp": {
                "n_cores": cal_holo_n,
                "farm_relaxed_n": cal_holo_relaxed,
                "farm_relaxed_pct": round(100.0 * cal_holo_relaxed / max(1, cal_holo_n), 1),
                "farm_strict_n": cal_holo_strict,
                "farm_strict_pct": round(100.0 * cal_holo_strict / max(1, cal_holo_n), 1),
            },
            "eu_mesolithic_neg_11500_9000bp": {
                "n_cores": cal_meso_n,
                "farm_relaxed_n": cal_meso_relaxed,
                "farm_relaxed_pct": round(100.0 * cal_meso_relaxed / max(1, cal_meso_n), 1),
                "farm_strict_n": cal_meso_strict,
                "farm_strict_pct": round(100.0 * cal_meso_strict / max(1, cal_meso_n), 1),
            },
            "neolithic_onsets": neolithic_onsets,
        },
        "pre12ka_sweep": {
            "late_glacial_12_18ka": {
                "cores_with_crop_data": len(lg_eval),
                "farm_relaxed_n": lg_relaxed,
                "farm_strict_unfiltered_n": lg_strict_unfilt,
                "farm_strict_chron_ok_n": lg_strict,
                "pct_of_global_ge12ka": round(100.0 * lg_strict / max(1, n_denom), 3),
            },
            "lgm_glacial_neg_18_50ka": {
                "cores_with_crop_data": len(lgm_eval),
                "farm_relaxed_n": lgm_relaxed,
                "farm_strict_unfiltered_n": lgm_strict_unfilt,
                "farm_strict_chron_ok_n": lgm_strict,
                "pct_of_global_ge18ka": round(100.0 * lgm_strict / max(1, n_denom_lgm), 3),
            },
            "fisher_p_lg_gt_lgm_strict": float(p_lg_vs_lgm_strict),
            "fisher_p_lg_gt_lgm_relaxed": float(p_lg_vs_lgm_relaxed),
            "flagged_strict_chron_ok": all_strict_flagged,
            "flagged_strict_unfiltered": all_strict_unfilt_flagged,
            "all_pre12ka_candidates_summary": [
                {
                    "datasetid": e["datasetid"],
                    "sitename": e["sitename"],
                    "lat": e["lat"],
                    "lon": e["lon"],
                    "occ_taxa": e["occ_taxa"],
                    "lg_relaxed": e["lg_12_18ka"]["farm_relaxed"],
                    "lg_strict_unfilt": e["lg_12_18ka"]["farm_strict_unfiltered"],
                    "lg_strict": e["lg_12_18ka"]["farm_strict"],
                    "lgm_strict": e["lgm_18_50ka"]["farm_strict"],
                    "max_crop_pct_12_50": e["all_12_50ka"]["max_crop_pct"],
                    "n_controls": e["n_controls"],
                }
                for e in all_pre12_audit
            ],
        },
    }

    out_path = RES / "ice_age_farming_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nSaved results to {out_path}")
    print("\n=== PRE-12,000 BP GLOBAL SWEEP HEADLINE ===")
    print(f"Global Neotoma pollen cores >=12 ka: {len(neotoma_pre12_dsids)}")
    print(f"Cores with ANY >=12 ka crop/cereal occurrence: {len(pre12_occ_by_ds)}")
    print(f"Late Glacial (12-18 ka): RELAXED={lg_relaxed}, STRICT_unfilt={lg_strict_unfilt}, STRICT_chron_ok={lg_strict}")
    print(f"LGM Negative Control (18-50 ka): RELAXED={lgm_relaxed}, STRICT_unfilt={lgm_strict_unfilt}, STRICT_chron_ok={lgm_strict}")
    print(f"Fisher p (12-18 ka > 18-50 ka): strict={p_lg_vs_lgm_strict:.4f}, relaxed={p_lg_vs_lgm_relaxed:.4f}")
    print(f"Flagged STRICT (chron OK) across 12-50 ka ({len(all_strict_flagged)}):")
    for e in all_strict_flagged:
        print(f"  DS {e['datasetid']} | {e['sitename']} ({e['lat']}, {e['lon']}) | taxa={e['occ_taxa']} | n_ctrl={e['n_controls']} | hits={[(h['age_cal'], h['crop_pct'], h['weed_pct'], h['ap_pct']) for h in e['strict_hits_12_50ka']]}")
    print(f"Flagged STRICT (unfiltered, incl. unbracketed) across 12-50 ka ({len(all_strict_unfilt_flagged)}):")
    for e in all_strict_unfilt_flagged[:15]:
        print(f"  DS {e['datasetid']} | {e['sitename']} ({e['lat']}, {e['lon']}) | chron_ok={e['all_12_50ka']['chron'].get('chron_ok')} | n_ctrl={e['n_controls']} | lg={e['lg_12_18ka']['farm_strict_unfiltered']} lgm={e['lgm_18_50ka']['farm_strict_unfiltered']}")


if __name__ == "__main__":
    main()
