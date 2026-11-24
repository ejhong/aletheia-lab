"""Shared helpers for the spot-check scripts (not run directly).

Written independently of analysis/megafauna_timing.py: its own .xlsx reader (zipfile + XML, no
openpyxl/pandas), IntCal20 loader and calibration. Data files are the ones in ../MANIFEST.md, kept
git-ignored in questions/yd-megafauna-timing/data/ (the default); pass another folder as the first
argument to any script.
"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE.parent / "data"
RESULTS = HERE.parent / "results"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def data_dir() -> Path:
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA
    for f in ("intcal20.14c", "broughton2018_s1.xlsx"):
        if not (d / f).is_file():
            sys.exit(f"missing {d / f}; download it as described in MANIFEST.md")
    return d


def read_xlsx_first_sheet(path: Path) -> list[list[str]]:
    """Return the first worksheet as a list of rows of strings (shared strings resolved)."""
    z = zipfile.ZipFile(path)
    names = z.namelist()
    shared = []
    if "xl/sharedStrings.xml" in names:
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    sheet = sorted(n for n in names if n.startswith("xl/worksheets/sheet"))[0]
    rows = []
    for r in ET.fromstring(z.read(sheet)).iter("{%s}row" % NS["m"]):
        cells = {}
        for c in r.findall("m:c", NS):
            col = re.match(r"[A-Z]+", c.get("r")).group()
            idx = 0
            for ch in col:
                idx = idx * 26 + ord(ch) - 64
            v, t = c.find("m:v", NS), c.get("t")
            if t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
            elif v is None:
                val = ""
            elif t == "s":
                val = shared[int(v.text)]
            else:
                val = v.text
            cells[idx - 1] = val
        rows.append([cells.get(i, "") for i in range(max(cells) + 1)] if cells else [])
    return rows


def load_broughton(d: Path) -> list[dict]:
    """Rows of Broughton & Weitzel (2018) Supplementary Data 1 with a numeric RCYBP and Error."""
    out = []
    for r in read_xlsx_first_sheet(d / "broughton2018_s1.xlsx")[2:]:
        try:
            rc, err = float(r[4]), float(r[5])
        except (ValueError, IndexError):
            continue
        out.append({
            "taxon": r[0].strip(), "state": r[1].strip(), "site": r[2].strip(), "lab": r[3].strip(),
            "rc": rc, "err": err, "material": r[9].strip(), "method": r[10].strip().upper(),
            "score": r[11].strip(),
        })
    return out


def load_intcal(d: Path) -> np.ndarray:
    ic = np.loadtxt(d / "intcal20.14c")
    return ic[np.argsort(ic[:, 0])]


def calibrate(rc, err, mu, sg, full_likelihood=True):
    """Calibrated posteriors on a calendar grid, one row per date, each row summing to 1.

    full_likelihood=True keeps the Gaussian's 1/sqrt(var) term (standard calibration);
    False drops it, as in the study's protocol formula and code.
    """
    rc = np.atleast_1d(np.asarray(rc, float))[:, None]
    err = np.atleast_1d(np.asarray(err, float))[:, None]
    var = err ** 2 + sg[None, :] ** 2
    lp = -0.5 * (rc - mu[None, :]) ** 2 / var
    if full_likelihood:
        lp = lp - 0.5 * np.log(var)
    lp -= lp.max(axis=1, keepdims=True)
    p = np.exp(lp)
    return p / p.sum(axis=1, keepdims=True)
