#!/usr/bin/env python3
"""Download pinned open-access Ancient Greek corpora for #15 (Secret Mark).

All URLs are pinned to immutable GitHub commit SHAs (First1KGreek, PerseusDL, SBLGNT)
plus two scholarly online editions of the Mar Saba letter for cross-verification.
Writes downloaded files to questions/secret-mark/data/ (gitignored) and outputs
a JSON summary of sizes, SHA-256 hashes, and extracted Greek token counts.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FIRST1K_SHA = "ed91552c52530c8f5a3ddf2dd767e899372a804c"
PERSEUS_SHA = "dacb04909e43dc47738828d33cc3d2b0635bc54c"
SBLGNT_SHA = "aaed91e57c8e4a8dc9a2383e129ca5e75fe6393d"

def first1k_url(urn: str) -> str:
    parts = urn.split(".")
    return f"https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/{FIRST1K_SHA}/data/{parts[0]}/{parts[1]}/{urn}.xml"

def perseus_url(urn: str) -> str:
    parts = urn.split(".")
    return f"https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/{PERSEUS_SHA}/data/{parts[0]}/{parts[1]}/{urn}.xml"

def sblgnt_url(fname: str) -> str:
    return f"https://raw.githubusercontent.com/morphgnt/sblgnt/{SBLGNT_SHA}/{fname}"

# Curated corpus:
# - Clement of Alexandria (complete surviving Greek prose)
# - 13 comparison authors spanning 1st-5th c. CE (Alexandrian, Ante-Nicene, Late-Antique)
# - 4 known-forgery / mixed-voice / pseudepigrapha controls
# - 4 Canonical Gospels (SBLGNT) for Layer B (Secret Mark quotations)
SOURCES: list[dict] = [
    # --- CLEMENT OF ALEXANDRIA (Target Author) ---
    {"id": "clement_protrepticus", "author": "Clement of Alexandria", "role": "target_author", "era": "2c",
     "work": "Protrepticus", "url": first1k_url("tlg0555.tlg001.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "clement_paedagogus", "author": "Clement of Alexandria", "role": "target_author", "era": "2c",
     "work": "Paedagogus", "url": first1k_url("tlg0555.tlg002.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "clement_stromata", "author": "Clement of Alexandria", "role": "target_author", "era": "2c",
     "work": "Stromata (Books 1-8)", "url": perseus_url("tlg0555.tlg004.perseus-grc2"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "clement_quis_dives", "author": "Clement of Alexandria", "role": "positive_control", "era": "2c",
     "work": "Quis dives salvetur (held-out positive control)", "url": first1k_url("tlg0555.tlg006.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "clement_eclogae", "author": "Clement of Alexandria", "role": "positive_control", "era": "2c",
     "work": "Eclogae propheticae (held-out short work)", "url": first1k_url("tlg0555.tlg005.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "clement_excerpta_theodoto", "author": "Clement/Theodotus", "role": "mixed_control", "era": "2c",
     "work": "Excerpta ex Theodoto (known mixed-voice control)", "url": first1k_url("tlg0555.tlg007.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},

    # --- ALEXANDRIAN & ANTE-NICENE PEERS (1st-3rd c. CE) ---
    {"id": "philo_opificio", "author": "Philo of Alexandria", "role": "comparison", "era": "1c",
     "work": "De opificio mundi", "url": first1k_url("tlg0018.tlg001.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "philo_legum", "author": "Philo of Alexandria", "role": "comparison", "era": "1c",
     "work": "Legum allegoriae I-III", "url": first1k_url("tlg0018.tlg002.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "justin_apologia", "author": "Justin Martyr", "role": "comparison", "era": "2c",
     "work": "Apologia", "url": first1k_url("tlg0645.tlg001.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "justin_dialogus", "author": "Justin Martyr", "role": "comparison", "era": "2c",
     "work": "Dialogus cum Tryphone", "url": first1k_url("tlg0645.tlg003.perseus-grc2"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "athenagoras_legatio", "author": "Athenagoras", "role": "comparison", "era": "2c",
     "work": "Legatio pro Christianis", "url": first1k_url("tlg1205.tlg001.perseus-grc2"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "athenagoras_resurr", "author": "Athenagoras", "role": "comparison", "era": "2c",
     "work": "De resurrectione", "url": first1k_url("tlg1205.tlg002.perseus-grc2"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "theophilus_autolycum", "author": "Theophilus of Antioch", "role": "comparison", "era": "2c",
     "work": "Ad Autolycum", "url": first1k_url("tlg1725.tlg001.perseus-grc2"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "tatian_graecos", "author": "Tatian", "role": "comparison", "era": "2c",
     "work": "Oratio ad Graecos", "url": first1k_url("tlg1766.tlg001.perseus-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "hippolytus_refutatio", "author": "Hippolytus", "role": "comparison", "era": "3c",
     "work": "Refutatio omnium haeresium", "url": first1k_url("tlg2115.tlg060.opp-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "origen_celsum", "author": "Origen", "role": "comparison", "era": "3c",
     "work": "Contra Celsum", "url": first1k_url("tlg2042.tlg001.perseus-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "origen_joannem", "author": "Origen", "role": "comparison", "era": "3c",
     "work": "Commentarii in Joannem", "url": first1k_url("tlg2042.tlg005.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "origen_oratione", "author": "Origen", "role": "comparison", "era": "3c",
     "work": "De oratione", "url": first1k_url("tlg2042.tlg008.perseus-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},

    # --- LATE-ANTIQUE / POST-NICENE PATRISTIC CONTROLS (4th-5th c. CE) ---
    {"id": "eusebius_he", "author": "Eusebius of Caesarea", "role": "comparison", "era": "4c",
     "work": "Historia Ecclesiastica", "url": first1k_url("tlg2018.tlg002.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "eusebius_eccl_theol", "author": "Eusebius of Caesarea", "role": "comparison", "era": "4c",
     "work": "De Ecclesiastica Theologia", "url": first1k_url("tlg2018.tlg009.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "athanasius_incarn", "author": "Athanasius of Alexandria", "role": "comparison", "era": "4c",
     "work": "De Incarnatione Verbi", "url": first1k_url("tlg2035.tlg002.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "athanasius_arianos1", "author": "Athanasius of Alexandria", "role": "comparison", "era": "4c",
     "work": "Oratio I contra Arianos", "url": first1k_url("tlg2035.tlg130.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "athanasius_arianos2", "author": "Athanasius of Alexandria", "role": "comparison", "era": "4c",
     "work": "Oratio II contra Arianos", "url": first1k_url("tlg2035.tlg131.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "epiphanius_panarion", "author": "Epiphanius of Salamis", "role": "comparison", "era": "4c",
     "work": "Panarion (Adversus haereses)", "url": first1k_url("tlg2021.tlg002.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "gregory_naz_27", "author": "Gregory of Nazianzus", "role": "comparison", "era": "4c",
     "work": "Oratio 27", "url": first1k_url("tlg2022.tlg007.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "gregory_naz_29", "author": "Gregory of Nazianzus", "role": "comparison", "era": "4c",
     "work": "Oratio 29", "url": first1k_url("tlg2022.tlg009.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "gregory_naz_31", "author": "Gregory of Nazianzus", "role": "comparison", "era": "4c",
     "work": "Oratio 31", "url": first1k_url("tlg2022.tlg011.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "theodoret_he", "author": "Theodoret of Cyrus", "role": "comparison", "era": "5c",
     "work": "Historia Ecclesiastica", "url": first1k_url("tlg4089.tlg003.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "cyril_prophets", "author": "Cyril of Alexandria", "role": "comparison", "era": "5c",
     "work": "In XII Prophetas", "url": first1k_url("tlg4090.tlg001.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},

    # --- KNOWN-FORGERY / PSEUDEPIGRAPHA CONTROLS ---
    {"id": "pseudo_athanasius_or4", "author": "Pseudo-Athanasius", "role": "forgery_control", "era": "4c",
     "work": "Oratio IV contra Arianos [Sp.]", "url": first1k_url("tlg2035.tlg117.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "ignatius_genuine", "author": "Ignatius of Antioch", "role": "control_pair", "era": "2c",
     "work": "Epistulae VII genuinae", "url": first1k_url("tlg1443.tlg001.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "pseudo_ignatius", "author": "Pseudo-Ignatius", "role": "forgery_control", "era": "4c",
     "work": "Epistulae interpolatae et suppositiciae", "url": first1k_url("tlg1443.tlg002.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "clement_rome_1", "author": "Clement of Rome", "role": "control_pair", "era": "1c",
     "work": "Epistula I ad Corinthios", "url": first1k_url("tlg1271.tlg001.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},
    {"id": "pseudo_clement_rome_2", "author": "Pseudo-Clement of Rome", "role": "forgery_control", "era": "2c",
     "work": "Epistula II ad Corinthios", "url": first1k_url("tlg1271.tlg002.1st1K-grc1"), "fmt": "tei", "licence": "CC-BY-SA-4.0"},

    # --- CANONICAL GOSPELS (SBLGNT) FOR LAYER B (SECRET MARK QUOTATIONS) ---
    {"id": "gospel_matthew", "author": "Matthew", "role": "gospel", "era": "1c",
     "work": "Gospel of Matthew (SBLGNT)", "url": sblgnt_url("61-Mt-morphgnt.txt"), "fmt": "morphgnt", "licence": "CC-BY-4.0"},
    {"id": "gospel_mark", "author": "Mark", "role": "gospel", "era": "1c",
     "work": "Gospel of Mark (SBLGNT)", "url": sblgnt_url("62-Mk-morphgnt.txt"), "fmt": "morphgnt", "licence": "CC-BY-4.0"},
    {"id": "gospel_luke", "author": "Luke", "role": "gospel", "era": "1c",
     "work": "Gospel of Luke (SBLGNT)", "url": sblgnt_url("63-Lk-morphgnt.txt"), "fmt": "morphgnt", "licence": "CC-BY-4.0"},
    {"id": "gospel_john", "author": "John", "role": "gospel", "era": "1c",
     "work": "Gospel of John (SBLGNT)", "url": sblgnt_url("64-Jn-morphgnt.txt"), "fmt": "morphgnt", "licence": "CC-BY-4.0"},
]

def strip_diacritics_greek(s: str) -> str:
    nfd = unicodedata.normalize("NFD", s.lower())
    out = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
    out = out.replace("ς", "σ")
    return out

def extract_greek_tokens(text: str) -> list[str]:
    norm = strip_diacritics_greek(text)
    return re.findall(r"[α-ω]+", norm)

def parse_tei_xml(path: Path) -> str:
    tree = ET.parse(path)
    root = tree.getroot()
    # Find <body> in TEI namespace or without namespace
    body = None
    for el in root.iter():
        if el.tag.endswith("}body") or el.tag == "body":
            body = el
            break
    if body is None:
        body = root
    # Skip editorial notes, apparatus, foreign/non-Greek blocks, heads/labels if Latin
    SKIP_TAGS = {"note", "head", "label", "bibl", "ref", "pb", "lb", "milestone", "num"}
    chunks: list[str] = []
    def walk(el):
        local = el.tag.split("}")[-1]
        if local in SKIP_TAGS:
            if el.tail:
                chunks.append(el.tail)
            return
        if el.text:
            chunks.append(el.text)
        for child in el:
            walk(child)
        if el.tail:
            chunks.append(el.tail)
    walk(body)
    return " ".join(chunks)

def parse_morphgnt(path: Path) -> str:
    words = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cols = line.strip().split()
        if len(cols) >= 4:
            words.append(cols[3])  # surface text column
    return " ".join(words)

def fetch_one(src: dict) -> dict:
    ext = ".xml" if src["fmt"] == "tei" else ".txt"
    out_path = DATA_DIR / f"{src['id']}{ext}"
    if not out_path.exists():
        req = urllib.request.Request(src["url"], headers={"User-Agent": "aletheia-lab/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        out_path.write_bytes(data)
    raw = out_path.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()
    text = parse_tei_xml(out_path) if src["fmt"] == "tei" else parse_morphgnt(out_path)
    tokens = extract_greek_tokens(text)
    return {
        **src,
        "file": out_path.name,
        "bytes": len(raw),
        "sha256": sha256,
        "greek_tokens": len(tokens),
    }

def main():
    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_one, s): s for s in SOURCES}
        for fut in as_completed(futs):
            src = futs[fut]
            try:
                res = fut.result()
                results.append(res)
                print(f"OK  {res['id']:28s} {res['greek_tokens']:8d} tokens  sha256={res['sha256'][:12]}")
            except Exception as e:
                print(f"ERR {src['id']:28s} -> {e}")
                raise
    # Sort back into SOURCES order
    order = {s["id"]: i for i, s in enumerate(SOURCES)}
    results.sort(key=lambda r: order[r["id"]])
    # Also hash the two Mar Saba reference files if present
    for fname in ["akma_SecretMark.pdf", "khazarzar_secmark.htm"]:
        p = DATA_DIR / fname
        if p.exists():
            raw = p.read_bytes()
            print(f"REF {fname:28s} {len(raw):8d} bytes   sha256={hashlib.sha256(raw).hexdigest()}")
    (DATA_DIR / "corpus_manifest.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    total = sum(r["greek_tokens"] for r in results)
    print(f"\nDownloaded {len(results)} files, total {total:,} Greek tokens.")

if __name__ == "__main__":
    main()
