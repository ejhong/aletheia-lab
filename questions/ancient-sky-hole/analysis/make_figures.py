#!/usr/bin/env python3
"""Generate the interactive HTML figures for site/figures/ancient-sky-hole/.

Reads ONLY locked results/ and primary data/ catalogs. Produces five self-contained,
zero-dependency fragments embedded into site/content/ancient-sky-hole.md:
  1. tiles.html      - Headline tiles
  2. verdict.html    - Verdict panel
  3. sky_dome.html   - The southern sky at a chosen date (Vondrak 2011 precession)
  4. contour.html    - How well each date and latitude fits
  5. rim.html        - The stars on the rim (catalogued vs. left-out stars)

Colours and type follow site/assets/site.css: the dark panels use the site's band tokens
(warm near-black), never navy. Canvas code uses the same tokens as hex values.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
RESULTS = ROOT / "results"
OUT_DIR = REPO / "site" / "figures" / "ancient-sky-hole"

sys.path.insert(0, str(ROOT / "analysis"))
import skyhole as sh

# Common proper names for iconic southern stars (for hover tooltips & dome labels)
COMMON_NAMES: Dict[int, str] = {
    30438: "Canopus",
    32349: "Sirius",
    71681: "Alpha Centauri",
    71683: "Alpha Cen A",
    68702: "Hadar (β Cen)",
    60718: "Acrux",
    62434: "Mimosa (β Cru)",
    61084: "Gacrux",
    59747: "Imai (δ Cru)",
    7588: "Achernar",
    13847: "Acamar (θ Eri)",
    45238: "Miaplacidus",
    41037: "Avior",
    45556: "Aspidiske",
    42913: "Alsephina (δ Vel)",
    45941: "Markeb (κ Vel)",
    39953: "Suhail al Muhlif (γ Vel)",
    39429: "Naos",
    109268: "Alnair (α Gru)",
    112122: "Tiaki (β Gru)",
    2081: "Ankaa (α Phe)",
    100751: "Peacock (α Pav)",
    82273: "Atria (α TrA)",
    110130: "Alpha Tucanae",
    9236: "Alpha Hydri",
    2021: "Beta Hydri",
    85267: "Gamma Arae",
    85258: "Beta Arae",
    83081: "Zeta Arae",
    85792: "Choo (α Ara)",
    80763: "Antares",
    85927: "Shaula",
    86228: "Sargas (θ Sco)",
    90185: "Kaus Australis",
    92855: "Nunki",
    113368: "Fomalhaut",
    24436: "Rigel",
    27989: "Betelgeuse",
    33579: "Adhara",
    65474: "Spica",
    71860: "Alpha Lupi",
    26634: "Phact (α Col)",
    61585: "Alpha Muscae",
    21281: "Alpha Doradus",
    77952: "Beta TrA",
    74946: "Gamma TrA",
    52419: "Theta Carinae",
    101772: "Alpha Indi",
}

CST_FULL = {
    "=Arg": "Argo Navis",
    "=Cen": "Centaurus",
    "=Ara": "Ara",
    "=Lup": "Lupus",
    "=Sco": "Scorpius",
    "=Sgr": "Sagittarius",
    "=CrA": "Corona Australis",
    "=PsA": "Piscis Austrinus",
    "=Eri": "Eridanus",
    "=CMa": "Canis Major",
    "=Ori": "Orion",
    "=Lep": "Lepus",
    "=Hya": "Hydra",
    "=Crt": "Crater",
    "=Crv": "Corvus",
    "=Cet": "Cetus",
    "=Cap": "Capricornus",
    "=Aqr": "Aquarius",
    "=Lib": "Libra",
    "=Vir": "Virgo",
    "=Oph": "Ophiuchus",
    "=Ser": "Serpens",
}

# Hand-curated iconic constellation stick-lines (pairs of HIP IDs)
# Classical Ptolemy southern constellations (warm gold)
CLASSICAL_LINES: List[Tuple[str, List[Tuple[int, int]]]] = [
    ("Argo Navis", [
        (30438, 32768), (32768, 38827), (38827, 42913), (42913, 45941),
        (45941, 46701), (42913, 39953), (39953, 39429), (39429, 35264),
        (39953, 44816), (44816, 45941), (30438, 35264),
    ]),
    ("Centaurus (+Crux)", [
        (60718, 61084), (62434, 59747),  # Southern Cross (within Ptolemy's Centaurus)
        (71681, 68702), (68702, 66657), (66657, 68002), (68002, 71352),
        (66657, 61932), (61932, 59196), (61932, 65109), (65109, 68002),
    ]),
    ("Ara", [
        (85792, 85258), (85258, 85267), (85267, 83081), (83081, 83153),
        (85792, 88714), (88714, 85258),
    ]),
    ("Lupus", [
        (71860, 73273), (73273, 75141), (75141, 76297), (76297, 74395), (74395, 71860),
    ]),
    ("Scorpius", [
        (78820, 78401), (78401, 78265), (78401, 80112), (80112, 80763),
        (80763, 81266), (81266, 82396), (82396, 82514), (82514, 82729),
        (82729, 86228), (86228, 86670), (86670, 85927),
    ]),
    ("Sagittarius", [
        (88635, 89931), (89931, 90185), (90185, 89642), (89931, 90496),
        (90496, 92041), (92041, 92855), (92855, 93506), (93506, 90185),
        (92041, 93506), (92855, 93864),
    ]),
    ("Eridanus", [
        (23875, 18543), (18543, 17378), (17378, 16537), (16537, 13701),
        (13701, 15474), (15474, 20042), (20042, 13847),
    ]),
    ("Canis Major", [
        (32349, 30324), (32349, 33977), (33977, 34444), (34444, 33579),
        (34444, 35904), (33579, 30122),
    ]),
    ("Orion", [
        (27989, 25336), (25336, 25930), (25930, 26311), (26311, 26727),
        (26727, 27989), (25930, 24436), (26727, 27366), (24436, 27366),
    ]),
    ("Piscis Austrinus", [
        (113368, 111188), (111188, 108085), (113368, 113246),
    ]),
]

# Post-1600 unmapped southern constellations inside the void (ethereal sapphire dashed)
MODERN_VOID_LINES: List[Tuple[str, List[Tuple[int, int]]]] = [
    ("Phoenix", [(2081, 5165), (5165, 6867), (6867, 7083), (7083, 5165), (2081, 6867)]),
    ("Grus", [(109268, 112122), (112122, 112623), (109268, 108085)]),
    ("Triangulum Australe", [(82273, 77952), (77952, 74946), (74946, 82273)]),
    ("Pavo", [(100751, 102395), (102395, 99240), (99240, 100751)]),
    ("Hydrus", [(9236, 2021), (2021, 17678), (17678, 9236)]),
    ("Carina (keel)", [(45238, 45556), (45556, 41037), (41037, 45238), (45238, 50099), (50099, 52419)]),
    ("Musca", [(61585, 62322)]),
]


def bv_to_hex(bv: float) -> str:
    """Subtle realistic star tint from Johnson B-V color index."""
    if bv < 0.0:
        return "#cfe4ff"
    if bv < 0.35:
        return "#eef4ff"
    if bv < 0.70:
        return "#fff7e2"
    if bv < 1.15:
        return "#ffe2ad"
    return "#ffbf80"


def fmt_year(t: float) -> str:
    """Astronomical year (0 = 1 BCE) to a plain BCE/CE label."""
    y = int(round(t))
    return f"{1 - y} BCE" if y <= 0 else f"{y} CE"


def variant_epoch(summary: Dict, vid: str) -> float:
    for v in summary["variants"]:
        if v.get("name") == vid:
            return float(v["epoch"])
    raise KeyError(vid)


# Shared panel styles for the three dark sky figures: a night-blue plate set into the warm page.
# The site's band tokens (site/assets/site.css) are re-pointed to blues on the panel only; copper,
# ochre, verdigris and the cream ink stay the site's. `.fig` prefixes beat `.prose p` / `.prose h3`.
PANEL_CSS = """
.fig .sky-panel {
  --band: #0d1421; --band-soft: #131c2c; --band-line: #2a3750;
  --band-ink: #f6f1e8; --band-ink-soft: #cdd3de; --band-faint: #8f9bb1; --band-slate: #c9daf0;
  --band-copper: #d08a5c; --band-verdigris: #7fb39d; --band-ochre: #cfa544;
  background: var(--band); color: var(--band-ink-soft);
  border: 1px solid var(--band-line); border-radius: 3px; overflow: hidden;
  font-family: var(--sans);
}
.fig .sky-head {
  display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between;
  gap: 0.5rem 1.25rem; padding: 1rem 1.25rem 0.85rem; border-bottom: 1px solid var(--band-line);
}
.fig .sky-eyebrow {
  font: 500 10.5px/1.4 var(--mono); text-transform: uppercase; letter-spacing: 0.12em;
  color: var(--band-faint); margin: 0 0 0.3rem;
}
.fig .sky-title { font: 400 1.3rem/1.25 var(--serif); color: var(--band-ink); margin: 0; letter-spacing: -0.005em; }
.fig .sky-legend {
  display: flex; flex-wrap: wrap; gap: 0.35rem 1.4rem; margin: 0;
  padding: 0.6rem 1.25rem 0.7rem; font: 400 0.84rem/1.4 var(--sans); color: var(--band-ink-soft);
}
.fig .sky-legend .key { display: inline-flex; align-items: center; gap: 0.4rem; }
.fig .sky-legend svg { flex: none; }
.fig .sky-btn {
  font: 400 0.8rem/1.25 var(--sans); padding: 0.4rem 0.7rem; border-radius: 3px; cursor: pointer;
  background: transparent; border: 1px solid var(--band-line); color: var(--band-ink-soft);
}
.fig .sky-btn:hover { border-color: var(--band-faint); color: var(--band-ink); }
.fig .sky-btn.is-active, .fig .sky-btn[aria-pressed="true"] {
  border-color: var(--band-copper); color: var(--band-ink);
  background: color-mix(in oklab, var(--band-copper) 16%, transparent);
}
.fig .sky-panel :focus-visible { outline: 2px solid var(--band-copper); outline-offset: 2px; }
.fig .sky-panel input[type="checkbox"] { accent-color: var(--band-copper); }
.fig .sky-panel strong { color: var(--band-ink); font-weight: 600; }
"""


def build_tiles_html(summary: Dict) -> str:
    earliest = summary["combined_honest_epoch_labels"][0]
    n_var = len(summary["variants"])
    n_loco = len(summary["loco_jackknife"])
    n_boot = int(summary["bootstrap_m1"]["n_boot"])
    lo = fmt_year(variant_epoch(summary, "vmag_le_4.0"))
    hi = fmt_year(summary["m2_free_extinction"]["best"]["epoch"])
    m1 = summary["primary_m1"]["epoch_label"]
    return f"""<div class="tiles">
<div class="tile"><p class="tile-value is-word">After {earliest}</p><p class="tile-label">the earliest date in any of {n_var} versions of the test, {n_loco} leave-one-out runs and {n_boot} reshufflings of the sky</p></div>
<div class="tile"><p class="tile-value is-word">{lo} to {hi}</p><p class="tile-label">where the three best-fitting versions land: the working lives of Hipparchus and Ptolemy</p></div>
<div class="tile"><p class="tile-value">{m1}</p><p class="tile-label">where the main model landed, almost eight centuries after the catalogue was written</p></div>
<div class="tile"><p class="tile-value is-word">The catalogue</p><p class="tile-label">is what the empty patch dates, not the first drawing of the constellations</p></div>
</div>
"""


def build_sky_dome_html(cat: Dict, summary: Dict, grids: Dict) -> str:
    # Select southern stars (ecl_lat <= +12 deg, Vmag <= 5.0) for crisp 60fps canvas rendering
    # Always include HIP 71681 (Alpha Cen) and skip duplicate visual companion HIP 71683 from "missing" label noise
    mask = (cat["ecl_lat"] <= 12.0) & (cat["vmag"] <= 5.0) & (cat["hip"] != 71683)
    idxs = np.where(mask)[0]

    stars_payload = []
    hip_to_idx: Dict[int, int] = {}
    for out_i, i in enumerate(idxs):
        hid = int(cat["hip"][i])
        hip_to_idx[hid] = out_i
        u = cat["u0"][i]
        v = cat["vel"][i]
        vmag = float(cat["vmag"][i])
        bv = float(cat["bv"][i])
        cat_flag = int(cat["all48"][i])
        cst = str(cat["cst"][i])
        cst_name = CST_FULL.get(cst, cst.lstrip("=")) if cst else ""
        bayer = str(cat["name"][i])
        common = COMMON_NAMES.get(hid, "")
        label = common if common else bayer
        # Compact array: [ux, uy, uz, vx*1e6, vy*1e6, vz*1e6, vmag, cat_flag, color, label, bayer, cst_name, hip]
        stars_payload.append([
            round(float(u[0]), 5),
            round(float(u[1]), 5),
            round(float(u[2]), 5),
            round(float(v[0] * 1e6), 4),
            round(float(v[1] * 1e6), 4),
            round(float(v[2] * 1e6), 4),
            round(vmag, 2),
            cat_flag,
            bv_to_hex(bv),
            label,
            bayer,
            cst_name,
            hid,
        ])

    # Convert constellation lines to index pairs
    cl_lines = []
    for cname, pairs in CLASSICAL_LINES:
        seg = [[hip_to_idx[a], hip_to_idx[b]] for a, b in pairs if a in hip_to_idx and b in hip_to_idx]
        if seg:
            cl_lines.append({"name": cname, "segs": seg})

    mv_lines = []
    for cname, pairs in MODERN_VOID_LINES:
        seg = [[hip_to_idx[a], hip_to_idx[b]] for a, b in pairs if a in hip_to_idx and b in hip_to_idx]
        if seg:
            mv_lines.append({"name": cname, "segs": seg})

    # Precompute Milky Way galactic equator points in southern ecliptic hemisphere (b = 0 deg)
    # J2000 Galactic North Pole: RA=192.85948 deg, Dec=+27.12825 deg, l_NCP=122.93192 deg
    g_ra, g_de = math.radians(192.85948), math.radians(27.12825)
    gnp = np.array([math.cos(g_de) * math.cos(g_ra), math.cos(g_de) * math.sin(g_ra), math.sin(g_de)])
    # Orthonormal basis on galactic plane
    tmp = np.array([1.0, 0.0, 0.0])
    e1 = tmp - np.dot(tmp, gnp) * gnp
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(gnp, e1)
    mw_pts = []
    for ang_deg in range(0, 360, 4):
        th = math.radians(ang_deg)
        u = math.cos(th) * e1 + math.sin(th) * e2
        mw_pts.append([round(float(u[0]), 4), round(float(u[1]), 4), round(float(u[2]), 4)])

    # Compact downsampled likelihood lookup for live HUD (clear-sky k_V=0.15 and primary k_V=0.25)
    # epochs every 200 yr from -10000 to +1000 (step 4 in 50-yr grid), lats every 1.0 deg (step 2 in 0.5-deg grid)
    ep_full = np.array(grids["epochs"])
    la_full = np.array(grids["lats"])
    ll_15 = np.array(grids["m1_all48_kv015"])[::4, ::2]
    ll_25 = np.array(grids["m1_all48_kv025"])[::4, ::2]
    hud_grid = {
        "epochs": ep_full[::4].tolist(),
        "lats": la_full[::2].tolist(),
        "ll15": np.round(ll_15, 1).tolist(),
        "ll25": np.round(ll_25, 1).tolist(),
    }

    payload = {
        "stars": stars_payload,
        "classicalLines": cl_lines,
        "modernLines": mv_lines,
        "milkyWay": mw_pts,
        "hudGrid": hud_grid,
        "freePole": [
            round(float(summary["m4_free_pole"]["free_ra_j2000_deg"]), 2),
            round(float(summary["m4_free_pole"]["free_dec_j2000_deg"]), 2),
        ],
    }

    payload_json = json.dumps(payload, separators=(",", ":"))

    return f"""<figure class="fig sky-obs-fig" id="sky-time-machine">
<style>
{PANEL_CSS}
.sky-readout {{
  display: flex; align-items: baseline; gap: 0.85rem;
  font: 400 0.9rem/1.3 var(--sans); font-variant-numeric: tabular-nums;
}}
.sky-readout-epoch {{ font-weight: 600; color: var(--band-ink); }}
.sky-readout-lat {{ color: var(--band-ink-soft); }}
.sky-stage {{ position: relative; display: flex; justify-content: center; padding: 0.9rem 1rem 0.4rem; }}
.sky-canvas-wrap {{ position: relative; width: 100%; max-width: 660px; aspect-ratio: 1 / 1; }}
.sky-canvas-wrap canvas {{ display: block; width: 100%; height: 100%; cursor: crosshair; touch-action: pan-y; }}
.sky-tip {{
  position: absolute; pointer-events: none; z-index: 12;
  min-width: 170px; max-width: 240px; padding: 0.55rem 0.7rem; border-radius: 3px;
  background: var(--band); border: 1px solid var(--band-line);
  color: var(--band-ink-soft); font: 400 12.5px/1.5 var(--sans);
  opacity: 0; transition: opacity 0.12s ease;
}}
.sky-tip.is-on {{ opacity: 1; }}
.sky-tip-name {{ font-weight: 600; color: var(--band-ink); }}
.sky-tip-name span {{ font-weight: 400; color: var(--band-faint); }}
.sky-tip-tag {{ margin: 0.1rem 0 0.25rem; }}
.sky-tip-tag.is-cat {{ color: var(--band-ochre); }}
.sky-tip-tag.is-void {{ color: var(--band-slate); }}
.sky-hud {{
  display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px;
  background: var(--band-line); border-top: 1px solid var(--band-line); border-bottom: 1px solid var(--band-line);
}}
.sky-hud-cell {{ background: var(--band-soft); padding: 0.7rem 0.9rem; text-align: center; }}
.sky-hud-val {{ font: 600 1.05rem/1.2 var(--sans); font-variant-numeric: tabular-nums; color: var(--band-ink); }}
.sky-hud-val.is-good {{ color: var(--band-verdigris); }}
.sky-hud-val.is-bad {{ color: var(--band-copper); }}
.sky-hud-lbl {{ font: 400 0.78rem/1.4 var(--sans); color: var(--band-ink-soft); margin-top: 0.25rem; }}
.sky-controls {{ padding: 1rem 1.25rem 1.15rem; }}
.sky-sliders {{ display: grid; grid-template-columns: 1.55fr 1fr auto; gap: 0.85rem 1.25rem; align-items: end; }}
.sky-slider-group label {{
  display: flex; justify-content: space-between; align-items: baseline; gap: 0.5rem;
  font: 400 0.84rem/1.3 var(--sans); color: var(--band-ink-soft); margin-bottom: 0.4rem;
}}
.sky-slider-group label strong {{ font-variant-numeric: tabular-nums; }}
.sky-range {{
  -webkit-appearance: none; appearance: none; width: 100%; height: 4px; margin: 6px 0;
  border-radius: 2px; background: var(--band-line);
}}
.sky-range::-webkit-slider-thumb {{
  -webkit-appearance: none; appearance: none; width: 16px; height: 16px; border-radius: 50%;
  background: var(--band-copper); border: 2px solid var(--band); cursor: pointer;
}}
.sky-range::-moz-range-thumb {{
  width: 16px; height: 16px; border-radius: 50%;
  background: var(--band-copper); border: 2px solid var(--band); cursor: pointer;
}}
.fig .sky-play-btn {{ white-space: nowrap; color: var(--band-ink); padding: 0.5rem 0.95rem; }}
.sky-presets {{ display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.95rem; }}
.sky-toggles {{
  display: flex; flex-wrap: wrap; gap: 0.5rem 1.2rem; margin-top: 0.85rem; padding-top: 0.75rem;
  border-top: 1px solid var(--band-line); font: 400 0.8rem/1.3 var(--sans); color: var(--band-ink-soft);
}}
.sky-toggles label {{ display: inline-flex; align-items: center; gap: 0.38rem; cursor: pointer; }}
@media (max-width: 44rem) {{
  .sky-sliders {{ grid-template-columns: 1fr; }}
  .sky-hud {{ grid-template-columns: 1fr; }}
}}
</style>
<div class="sky-panel">
  <div class="sky-head">
    <div>
      <p class="sky-eyebrow">The southern sky, wound back</p>
      <h3 class="sky-title">The southern sky at a chosen date</h3>
    </div>
    <div class="sky-readout" aria-live="polite">
      <span class="sky-readout-epoch" id="sky-epoch-out">128 BCE</span>
      <span class="sky-readout-lat" id="sky-lat-out">36.4° N</span>
    </div>
  </div>

  <div class="sky-stage">
    <div class="sky-canvas-wrap">
      <canvas id="sky-dome-canvas" role="img" aria-label="Map of the southern sky showing the stars in Ptolemy's catalogue, the bright stars he left out, the circle the sky's south pole traces over 25,772 years, and the horizon for the chosen date and latitude."></canvas>
      <div class="sky-tip" id="sky-tip"></div>
    </div>
  </div>

  <p class="sky-legend">
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="4" fill="#e9d7a8"/></svg>Stars in Ptolemy's catalogue (filled)</span>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="4" fill="none" stroke="#c9daf0" stroke-width="1.5"/></svg>Bright stars he left out (rings)</span>
    <span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="#d08a5c" stroke-width="2"/></svg>Horizon: stars inside it never rise</span>
    <span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="#8f9bb1" stroke-width="1.5" stroke-dasharray="3 3"/></svg>Path of the sky's south pole over 25,772 years</span>
  </p>

  <div class="sky-hud">
    <div class="sky-hud-cell">
      <div class="sky-hud-val" id="hud-ptol-vis">-</div>
      <div class="sky-hud-lbl">Bright catalogued stars (magnitude 4.0 or brighter) that rise</div>
    </div>
    <div class="sky-hud-cell">
      <div class="sky-hud-val" id="hud-void-hid">-</div>
      <div class="sky-hud-lbl">Bright left-out stars (magnitude 3.5 or brighter) that never rise</div>
    </div>
    <div class="sky-hud-cell">
      <div class="sky-hud-val" id="hud-dll">-</div>
      <div class="sky-hud-lbl">How much worse this date fits than the best (0 is best; light-haze version)</div>
    </div>
  </div>

  <div class="sky-controls">
    <div class="sky-sliders">
      <div class="sky-slider-group">
        <label for="sky-epoch-slider"><span>Date</span><strong id="sky-epoch-lbl">128 BCE</strong></label>
        <input class="sky-range" id="sky-epoch-slider" type="range" min="-10000" max="2000" step="10" value="-127">
      </div>
      <div class="sky-slider-group">
        <label for="sky-lat-slider"><span>Observer's latitude</span><strong id="sky-lat-lbl">36.4° N</strong></label>
        <input class="sky-range" id="sky-lat-slider" type="range" min="15" max="45" step="0.2" value="36.4">
      </div>
      <button type="button" class="sky-btn sky-play-btn" id="sky-play-btn" aria-pressed="false">&#9654; Play</button>
    </div>

    <div class="sky-presets" id="sky-presets" role="group" aria-label="Places and dates">
      <button type="button" class="sky-btn sky-preset" aria-pressed="false" data-t="-9599" data-lat="37.2">Göbekli Tepe, 9600 BCE</button>
      <button type="button" class="sky-btn sky-preset" aria-pressed="false" data-t="-2999" data-lat="31.3">Early Sumer, 3000 BCE</button>
      <button type="button" class="sky-btn sky-preset" aria-pressed="false" data-t="-2599" data-lat="35.3">Crete, 2600 BCE (Ovenden)</button>
      <button type="button" class="sky-btn sky-preset" aria-pressed="false" data-t="-1099" data-lat="32.5">Babylon, 1100 BCE (MUL.APIN)</button>
      <button type="button" class="sky-btn sky-preset is-active" aria-pressed="true" data-t="-127" data-lat="36.4">Rhodes, 128 BCE (Hipparchus)</button>
      <button type="button" class="sky-btn sky-preset" aria-pressed="false" data-t="137" data-lat="31.2">Alexandria, 137 CE (Ptolemy)</button>
      <button type="button" class="sky-btn sky-preset" aria-pressed="false" data-t="910" data-lat="25.8">Main model's answer, 910 CE</button>
      <button type="button" class="sky-btn sky-preset" aria-pressed="false" data-t="2000" data-lat="36.0">Today, 2000 CE</button>
    </div>

    <div class="sky-toggles">
      <label><input type="checkbox" id="tog-lines" checked> Constellation lines</label>
      <label><input type="checkbox" id="tog-modern" checked> Modern constellations in the empty patch</label>
      <label><input type="checkbox" id="tog-labels" checked> Star and date labels</label>
      <label><input type="checkbox" id="tog-haze" checked> Haze band just above the horizon (0° to 8°)</label>
    </div>
  </div>
</div>
<figcaption>The southern half of the sky, drawn as an equal-area map centred on the south pole of the ecliptic (more than 1,100 Hipparcos stars brighter than magnitude 5.0, matched to Ptolemy's catalogue by Verbunt and van Gent, 2012). Move the date slider or press <em>Play</em> to swing the sky's south pole around its 25,772-year circle. The copper ring is the horizon: for an observer at the chosen latitude, stars inside it never rise. Around Hipparchus (Rhodes, 128 BCE) and Ptolemy (Alexandria, 137 CE) the ring sits on the empty patch; at 3000 BCE or 9600 BCE it misses it. Hover over a star to see how high it climbs.</figcaption>
<script>
(function() {{
  const DATA = {payload_json};
  const DAS2R = Math.PI / (180 * 3600);
  const D2PI = 2 * Math.PI;
  const EPS0 = 84381.406 * DAS2R;
  const CE = Math.cos(EPS0), SE = Math.sin(EPS0);

  const XYPOL = [
    [5453.282155, 0.4252841, -0.00037173, -0.000000152],
    [-73750.930350, -0.7675452, -0.00018725, 0.000000231]
  ];
  const XYPER = [
    [256.75, -819.940624, 75004.344875, 81491.287984, 1558.515853],
    [708.15, -8444.676815, 624.033993, 787.163481, 7774.939698],
    [274.20, 2600.009459, 1251.136893, 1251.296102, -2219.534038],
    [241.45, 2755.175630, -1102.212834, -1257.950837, -2523.969396],
    [2309.00, -167.659835, -2660.664980, -2966.799730, 247.850422],
    [492.20, 871.855056, 699.291817, 639.744522, -846.485643],
    [396.10, 44.769698, 153.167220, 131.600209, -1393.124055],
    [288.90, -512.313065, -950.865637, -445.040117, 368.526116],
    [231.10, -819.415595, 499.754645, 584.522874, 749.045012],
    [1610.00, -538.071099, -145.188210, -89.756563, 444.704518],
    [620.00, -189.793622, 558.116553, 524.429630, 235.934465],
    [157.87, -402.922932, -23.923029, -13.549067, 374.049623],
    [220.30, 179.516345, -165.405086, -210.157124, -171.330180],
    [1200.00, -9.814756, 9.344131, -44.919798, -22.899655]
  ];

  function ltpequ(epj) {{
    const t = (epj - 2000.0) / 100.0;
    let x = 0, y = 0;
    const w0 = D2PI * t;
    for (let i = 0; i < XYPER.length; i++) {{
      const a = w0 / XYPER[i][0];
      const c = Math.cos(a), s = Math.sin(a);
      x += c * XYPER[i][1] + s * XYPER[i][3];
      y += c * XYPER[i][2] + s * XYPER[i][4];
    }}
    let wt = 1.0;
    for (let i = 0; i < 4; i++) {{
      x += XYPOL[0][i] * wt;
      y += XYPOL[1][i] * wt;
      wt *= t;
    }}
    x *= DAS2R; y *= DAS2R;
    const z = Math.sqrt(Math.max(0, 1 - x * x - y * y));
    const n = Math.hypot(x, y, z) || 1;
    return [x / n, y / n, z / n];
  }}

  // Lambert azimuthal equal-area projection centered on South Ecliptic Pole (beta = -90 deg)
  // Radius covers colatitude 0..100 deg (beta = -90 to +10 deg)
  const MAX_COLAT_RAD = (100 * Math.PI) / 180;
  const MAX_R_PROJ = 2 * Math.sin(MAX_COLAT_RAD / 2);

  function eqToProj(ux, uy, uz, cx, cy, R) {{
    const xe = ux;
    const ye = uy * CE + uz * SE;
    const ze = -uy * SE + uz * CE; // sin(beta); -1 at SEP
    const colat = Math.acos(Math.max(-1, Math.min(1, -ze))); // 0 at SEP, pi/2 at ecliptic
    const rNorm = (2 * Math.sin(colat / 2)) / MAX_R_PROJ;
    const ang = Math.atan2(ye, xe);
    // Rotate so Classical/Hipparchus sky sits harmoniously upright
    const rot = -Math.PI / 2;
    const x = cx + R * rNorm * Math.cos(ang + rot);
    const y = cy - R * rNorm * Math.sin(ang + rot);
    return [x, y, rNorm];
  }}

  function fmtYear(t) {{
    const y = Math.round(t);
    return y <= 0 ? (1 - y) + " BCE" : y + " CE";
  }}

  function interpHUD(t, lat) {{
    const g = DATA.hudGrid;
    const ep = g.epochs, la = g.lats;
    const tCl = Math.max(ep[0], Math.min(ep[ep.length - 1], t));
    const lCl = Math.max(la[0], Math.min(la[la.length - 1], lat));
    const ei = Math.min(ep.length - 2, Math.max(0, Math.floor((tCl - ep[0]) / (ep[1] - ep[0]))));
    const li = Math.min(la.length - 2, Math.max(0, Math.floor((lCl - la[0]) / (la[1] - la[0]))));
    const ft = (tCl - ep[ei]) / (ep[ei + 1] - ep[ei]);
    const fl = (lCl - la[li]) / (la[li + 1] - la[li]);
    const M = g.ll15;
    const v00 = M[ei][li], v10 = M[ei + 1][li], v01 = M[ei][li + 1], v11 = M[ei + 1][li + 1];
    return (1 - ft) * (1 - fl) * v00 + ft * (1 - fl) * v10 + (1 - ft) * fl * v01 + ft * fl * v11;
  }}

  // Precompute 25,772-yr precession ring points
  const precTrack = [];
  for (let yr = -23772; yr <= 2000; yr += 220) {{
    const p = ltpequ(yr);
    precTrack.push([-p[0], -p[1], -p[2], yr]);
  }}

  const milestonePoles = [
    {{ t: -9599, lbl: "9600 BCE" }},
    {{ t: -2999, lbl: "3000 BCE" }},
    {{ t: -127, lbl: "128 BCE" }},
    {{ t: 2000, lbl: "2000 CE" }}
  ].map(m => {{
    const p = ltpequ(m.t);
    return {{ t: m.t, lbl: m.lbl, u: [-p[0], -p[1], -p[2]] }};
  }});

  // Precompute star screen coordinates (J2000; tiny proper motion applied live for altitude)
  const canvas = document.getElementById("sky-dome-canvas");
  const ctx = canvas.getContext("2d");
  const tip = document.getElementById("sky-tip");
  const epSlider = document.getElementById("sky-epoch-slider");
  const latSlider = document.getElementById("sky-lat-slider");
  const epOut = document.getElementById("sky-epoch-out");
  const latOut = document.getElementById("sky-lat-out");
  const epLbl = document.getElementById("sky-epoch-lbl");
  const latLbl = document.getElementById("sky-lat-lbl");
  const playBtn = document.getElementById("sky-play-btn");
  const hudPtol = document.getElementById("hud-ptol-vis");
  const hudVoid = document.getElementById("hud-void-hid");
  const hudDll = document.getElementById("hud-dll");
  const togLines = document.getElementById("tog-lines");
  const togModern = document.getElementById("tog-modern");
  const togLabels = document.getElementById("tog-labels");
  const togHaze = document.getElementById("tog-haze");
  const presetBtns = Array.from(document.querySelectorAll("#sky-presets .sky-preset"));

  let state = {{ t: -127, lat: 36.4, playing: false, hoverIdx: -1, width: 640 }};
  let starXY = [];
  let rafId = null;

  function resize() {{
    const rect = canvas.parentElement.getBoundingClientRect();
    const w = Math.max(240, Math.round(rect.width));
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = w * dpr;
    canvas.height = w * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    state.width = w;
    render();
  }}

  function drawCircleOnSphere(centerU, angRad, cx, cy, R) {{
    // Build orthonormal basis around centerU
    const [ax, ay, az] = centerU;
    const ref = Math.abs(az) < 0.9 ? [0, 0, 1] : [1, 0, 0];
    let e1x = ref[1] * az - ref[2] * ay;
    let e1y = ref[2] * ax - ref[0] * az;
    let e1z = ref[0] * ay - ref[1] * ax;
    const n1 = Math.hypot(e1x, e1y, e1z) || 1;
    e1x /= n1; e1y /= n1; e1z /= n1;
    const e2x = ay * e1z - az * e1y;
    const e2y = az * e1x - ax * e1z;
    const e2z = ax * e1y - ay * e1x;

    const ca = Math.cos(angRad), sa = Math.sin(angRad);
    const pts = [];
    for (let k = 0; k <= 120; k++) {{
      const phi = (k / 120) * D2PI;
      const cp = Math.cos(phi), sp = Math.sin(phi);
      const ux = ca * ax + sa * (cp * e1x + sp * e2x);
      const uy = ca * ay + sa * (cp * e1y + sp * e2y);
      const uz = ca * az + sa * (cp * e1z + sp * e2z);
      const p = eqToProj(ux, uy, uz, cx, cy, R);
      pts.push(p);
    }}
    return pts;
  }}

  // Panel palette as hex for canvas (night-blue plate; copper/ochre/verdigris from site.css)
  const C = {{
    band: "#0d1421", bandSoft: "#131c2c", ink: "#f6f1e8", inkSoft: "#cdd3de", faint: "#8f9bb1",
    line: "#2a3750", copper: "#d08a5c", verdigris: "#7fb39d", ochre: "#cfa544", slate: "#c9daf0"
  }};
  const SANS = (getComputedStyle(document.documentElement).getPropertyValue("--sans") || "").trim() || "system-ui, sans-serif";
  // Catalogued stars: cream (bright) to ochre (faint)
  function catColor(vmag) {{
    const f = Math.max(0, Math.min(1, (vmag - 1.0) / 3.5));
    const a = [246, 241, 232], b = [207, 165, 68];
    return "rgb(" + a.map((x, k) => Math.round(x + f * (b[k] - x))).join(",") + ")";
  }}

  function render() {{
    const W = state.width;
    const cx = W / 2, cy = W / 2;
    const R = W * 0.455;
    const t = state.t, lat = state.lat;
    const dt = t - 1991.25;

    ctx.clearRect(0, 0, W, W);

    // Outer rim with degree ticks
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, R + 12, 0, D2PI);
    ctx.strokeStyle = C.line;
    ctx.lineWidth = 1;
    ctx.stroke();
    for (let d = 0; d < 360; d += 5) {{
      const a = (d * Math.PI) / 180;
      const major = d % 30 === 0;
      const r0 = R + 2, r1 = R + (major ? 10 : 6);
      ctx.beginPath();
      ctx.moveTo(cx + r0 * Math.cos(a), cy + r0 * Math.sin(a));
      ctx.lineTo(cx + r1 * Math.cos(a), cy + r1 * Math.sin(a));
      ctx.strokeStyle = major ? C.faint : C.line;
      ctx.lineWidth = major ? 1.1 : 0.7;
      ctx.stroke();
    }}

    // Sky disc (flat night blue) and clip
    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, D2PI);
    ctx.fillStyle = C.bandSoft;
    ctx.fill();
    ctx.clip();

    // Faint ecliptic-latitude rings (-60, -30, 0 deg) and spokes every 30 deg
    ctx.strokeStyle = "rgba(246, 241, 232, 0.07)";
    ctx.lineWidth = 0.8;
    for (const beta of [-60, -30, 0]) {{
      const colat = ((90 + beta) * Math.PI) / 180;
      const rRing = R * ((2 * Math.sin(colat / 2)) / MAX_R_PROJ);
      ctx.beginPath();
      ctx.arc(cx, cy, rRing, 0, D2PI);
      ctx.stroke();
    }}
    for (let k = 0; k < 12; k++) {{
      const a = (k * Math.PI) / 6;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + R * Math.cos(a), cy + R * Math.sin(a));
      ctx.stroke();
    }}

    // Milky Way: one broad, faint band along the galactic equator
    ctx.save();
    ctx.beginPath();
    DATA.milkyWay.forEach((m, idx) => {{
      const [mx, my] = eqToProj(m[0], m[1], m[2], cx, cy, R);
      if (idx === 0) ctx.moveTo(mx, my); else ctx.lineTo(mx, my);
    }});
    ctx.closePath();
    ctx.strokeStyle = "rgba(246, 241, 232, 0.045)";
    ctx.lineWidth = R * 0.2;
    ctx.lineJoin = "round";
    ctx.stroke();
    ctx.restore();

    // South Celestial Pole at epoch t
    const pN = ltpequ(t);
    const pS = [-pN[0], -pN[1], -pN[2]];
    const [scpX, scpY] = eqToProj(pS[0], pS[1], pS[2], cx, cy, R);

    // Haze band (lat to lat + 8 deg around the pole)
    if (togHaze.checked) {{
      const hazePts = drawCircleOnSphere(pS, ((lat + 8.0) * Math.PI) / 180, cx, cy, R);
      ctx.beginPath();
      hazePts.forEach((p, idx) => idx === 0 ? ctx.moveTo(p[0], p[1]) : ctx.lineTo(p[0], p[1]));
      ctx.closePath();
      ctx.fillStyle = "rgba(208, 138, 92, 0.07)";
      ctx.fill();
      ctx.setLineDash([3, 4]);
      ctx.strokeStyle = "rgba(208, 138, 92, 0.4)";
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.setLineDash([]);
    }}

    // Never-rising cap (angular radius = lat around the pole): darker fill, copper horizon line
    const horPts = drawCircleOnSphere(pS, (lat * Math.PI) / 180, cx, cy, R);
    ctx.beginPath();
    horPts.forEach((p, idx) => idx === 0 ? ctx.moveTo(p[0], p[1]) : ctx.lineTo(p[0], p[1]));
    ctx.closePath();
    ctx.fillStyle = "rgba(5, 9, 17, 0.55)";
    ctx.fill();
    ctx.strokeStyle = C.copper;
    ctx.lineWidth = 2;
    ctx.stroke();

    // Precession circle (25,772 yr)
    ctx.beginPath();
    precTrack.forEach((pt, idx) => {{
      const [px, py] = eqToProj(pt[0], pt[1], pt[2], cx, cy, R);
      if (idx === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }});
    ctx.closePath();
    ctx.setLineDash([3, 3]);
    ctx.strokeStyle = C.faint;
    ctx.lineWidth = 1.2;
    ctx.stroke();
    ctx.setLineDash([]);

    // Dated points on the precession circle
    if (togLabels.checked) {{
      ctx.font = "400 11px " + SANS;
      milestonePoles.forEach(m => {{
        const [mx, my] = eqToProj(m.u[0], m.u[1], m.u[2], cx, cy, R);
        ctx.beginPath();
        ctx.arc(mx, my, 2.5, 0, D2PI);
        ctx.fillStyle = C.faint;
        ctx.fill();
        ctx.fillStyle = C.inkSoft;
        ctx.fillText(m.lbl, mx + 6, my + 4);
      }});
    }}

    // Project all stars + compute live altitudes
    starXY = new Array(DATA.stars.length);
    let ptolBrightTot = 0, ptolBrightVis = 0;
    let voidBrightTot = 0, voidBrightHid = 0;

    for (let i = 0; i < DATA.stars.length; i++) {{
      const s = DATA.stars[i];
      let ux = s[0] + dt * s[3] * 1e-6;
      let uy = s[1] + dt * s[4] * 1e-6;
      let uz = s[2] + dt * s[5] * 1e-6;
      const norm = Math.hypot(ux, uy, uz) || 1;
      ux /= norm; uy /= norm; uz /= norm;
      const [sx, sy, sr] = eqToProj(ux, uy, uz, cx, cy, R);
      const dec = (Math.asin(Math.max(-1, Math.min(1, ux * pN[0] + uy * pN[1] + uz * pN[2]))) * 180) / Math.PI;
      const hMax = 90 - Math.abs(lat - dec);
      starXY[i] = [sx, sy, hMax, sr];

      const vmag = s[6], isCat = s[7] === 1;
      if (isCat && vmag <= 4.0) {{
        ptolBrightTot++;
        if (hMax > -0.5) ptolBrightVis++;
      }} else if (!isCat && vmag <= 3.5 && dec < 0) {{
        voidBrightTot++;
        if (hMax <= 0.5) voidBrightHid++;
      }}
    }}

    // Ptolemy's constellation lines (ochre)
    if (togLines.checked) {{
      ctx.strokeStyle = "rgba(207, 165, 68, 0.38)";
      ctx.lineWidth = 1;
      DATA.classicalLines.forEach(c => {{
        ctx.beginPath();
        c.segs.forEach(([a, b]) => {{
          const pa = starXY[a], pb = starXY[b];
          if (pa[3] < 1.02 && pb[3] < 1.02) {{
            ctx.moveTo(pa[0], pa[1]);
            ctx.lineTo(pb[0], pb[1]);
          }}
        }});
        ctx.stroke();
      }});
    }}

    // Constellations drawn after 1600 inside the empty patch (dashed slate)
    if (togModern.checked) {{
      ctx.save();
      ctx.setLineDash([2.5, 3.5]);
      ctx.strokeStyle = "rgba(201, 218, 240, 0.4)";
      ctx.lineWidth = 0.95;
      DATA.modernLines.forEach(c => {{
        ctx.beginPath();
        c.segs.forEach(([a, b]) => {{
          const pa = starXY[a], pb = starXY[b];
          if (pa[3] < 1.02 && pb[3] < 1.02) {{
            ctx.moveTo(pa[0], pa[1]);
            ctx.lineTo(pb[0], pb[1]);
          }}
        }});
        ctx.stroke();
      }});
      ctx.restore();
    }}

    // Stars: catalogued = filled cream-to-gold discs; left out = pale blue-white rings
    for (let i = 0; i < DATA.stars.length; i++) {{
      const s = DATA.stars[i];
      const [sx, sy, hMax, sr] = starXY[i];
      if (sr > 1.01) continue;
      const vmag = s[6], isCat = s[7] === 1;
      const rad = Math.max(0.85, Math.min(4.8, (5.5 - vmag) * 0.72));
      ctx.beginPath();
      if (isCat) {{
        ctx.fillStyle = catColor(vmag);
        ctx.globalAlpha = vmag < 3.5 ? 1 : 0.8;
        ctx.arc(sx, sy, rad, 0, D2PI);
        ctx.fill();
      }} else {{
        ctx.strokeStyle = C.slate;
        ctx.globalAlpha = vmag < 3.5 ? 1 : 0.55;
        ctx.lineWidth = vmag < 3.5 ? 1.5 : 1;
        ctx.arc(sx, sy, Math.max(1.6, rad * 0.95), 0, D2PI);
        ctx.stroke();
      }}
    }}
    ctx.globalAlpha = 1;

    // Labels for landmark stars
    if (togLabels.checked) {{
      // Fewer labels on small screens so they do not pile up
      const keyHips = new Set(W < 460
        ? [30438, 60718, 7588, 2081, 32349, 113368]
        : [30438, 60718, 71681, 7588, 13847, 109268, 2081, 45238, 100751, 82273, 85267, 80763, 32349, 113368]);
      ctx.font = "400 11px " + SANS;
      for (let i = 0; i < DATA.stars.length; i++) {{
        const s = DATA.stars[i];
        if (!keyHips.has(s[12])) continue;
        const [sx, sy, , sr] = starXY[i];
        if (sr > 0.96) continue;
        ctx.fillStyle = s[7] === 1 ? C.ink : C.slate;
        ctx.fillText(s[9].split(" (")[0], sx + 6, sy - 4);
      }}
    }}

    // The sky's south pole at this date
    ctx.save();
    ctx.strokeStyle = C.ink;
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(scpX - 7, scpY); ctx.lineTo(scpX + 7, scpY);
    ctx.moveTo(scpX, scpY - 7); ctx.lineTo(scpX, scpY + 7);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(scpX, scpY, 3.5, 0, D2PI);
    ctx.fillStyle = C.copper;
    ctx.fill();
    ctx.font = "600 11px " + SANS;
    ctx.fillStyle = C.ink;
    ctx.fillText("South pole", scpX + 9, scpY - 6);
    ctx.restore();

    // Hover marker
    if (state.hoverIdx >= 0) {{
      const [hx, hy] = starXY[state.hoverIdx];
      ctx.strokeStyle = C.copper;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(hx, hy, 8, 0, D2PI);
      ctx.stroke();
    }}

    ctx.restore(); // end clip

    // Update UI text & HUD
    const yStr = fmtYear(t);
    epOut.textContent = yStr;
    epLbl.textContent = yStr;
    latOut.textContent = lat.toFixed(1) + "° N";
    latLbl.textContent = lat.toFixed(1) + "° N";

    const pctPtol = ptolBrightTot ? Math.round((100 * ptolBrightVis) / ptolBrightTot) : 0;
    const pctVoid = voidBrightTot ? Math.round((100 * voidBrightHid) / voidBrightTot) : 0;
    const dll = interpHUD(t, lat);

    hudPtol.textContent = pctPtol + "% (" + ptolBrightVis + "/" + ptolBrightTot + ")";
    hudPtol.className = "sky-hud-val " + (pctPtol >= 97 ? "is-good" : pctPtol < 90 ? "is-bad" : "");

    hudVoid.textContent = pctVoid + "% (" + voidBrightHid + "/" + voidBrightTot + ")";
    hudVoid.className = "sky-hud-val " + (pctVoid >= 75 ? "is-good" : pctVoid < 45 ? "is-bad" : "");

    hudDll.textContent = (dll > -0.1 ? "0.0 (best)" : dll.toFixed(1));
    hudDll.className = "sky-hud-val " + (dll > -6 ? "is-good" : dll < -30 ? "is-bad" : "");
  }}

  function setEpochLat(t, lat) {{
    state.t = t;
    state.lat = lat;
    epSlider.value = String(t);
    latSlider.value = String(lat);
    presetBtns.forEach(b => {{
      const bt = Number(b.dataset.t), bl = Number(b.dataset.lat);
      const on = Math.abs(bt - t) < 35 && Math.abs(bl - lat) < 0.4;
      b.classList.toggle("is-active", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    }});
    render();
  }}

  epSlider.addEventListener("input", () => {{
    stopPlay();
    setEpochLat(Number(epSlider.value), state.lat);
  }});
  latSlider.addEventListener("input", () => {{
    setEpochLat(state.t, Number(latSlider.value));
  }});
  presetBtns.forEach(btn => {{
    btn.addEventListener("click", () => {{
      stopPlay();
      setEpochLat(Number(btn.dataset.t), Number(btn.dataset.lat));
    }});
  }});
  [togLines, togModern, togLabels, togHaze].forEach(el => el.addEventListener("change", render));

  function stopPlay() {{
    state.playing = false;
    playBtn.innerHTML = "&#9654; Play";
    playBtn.setAttribute("aria-pressed", "false");
    if (rafId) cancelAnimationFrame(rafId);
    rafId = null;
  }}

  playBtn.addEventListener("click", () => {{
    if (state.playing) {{
      stopPlay();
      return;
    }}
    state.playing = true;
    playBtn.innerHTML = "&#10073;&#10073; Pause";
    playBtn.setAttribute("aria-pressed", "true");
    if (state.t >= 1950) state.t = -10000;
    function step() {{
      if (!state.playing) return;
      state.t += 45;
      if (state.t > 2000) state.t = -10000;
      epSlider.value = String(Math.round(state.t));
      presetBtns.forEach(b => {{ b.classList.remove("is-active"); b.setAttribute("aria-pressed", "false"); }});
      render();
      rafId = requestAnimationFrame(step);
    }}
    rafId = requestAnimationFrame(step);
  }});

  // Hover star inspector
  canvas.addEventListener("mousemove", (ev) => {{
    const rect = canvas.getBoundingClientRect();
    const mx = ev.clientX - rect.left;
    const my = ev.clientY - rect.top;
    let best = -1, bestD2 = 196; // 14px radius
    for (let i = 0; i < starXY.length; i++) {{
      const dx = starXY[i][0] - mx, dy = starXY[i][1] - my;
      const d2 = dx * dx + dy * dy;
      // Slightly prefer brighter stars when overlapping
      const score = d2 + Math.max(0, DATA.stars[i][6] - 1.5) * 6;
      if (d2 < 196 && (best === -1 || score < bestD2)) {{
        best = i; bestD2 = score;
      }}
    }}
    if (best !== state.hoverIdx) {{
      state.hoverIdx = best;
      render();
    }}
    if (best >= 0) {{
      const s = DATA.stars[best];
      const hMax = starXY[best][2];
      const isCat = s[7] === 1;
      const visTxt = hMax > 0 ? ("+" + hMax.toFixed(1) + "° above the horizon") : (hMax.toFixed(1) + "°, never rises");
      tip.innerHTML =
        '<div class="sky-tip-name">' + s[9] + (s[10] && s[10] !== s[9] ? ' <span>(' + s[10] + ')</span>' : '') + '</div>' +
        '<div class="sky-tip-tag ' + (isCat ? 'is-cat' : 'is-void') + '">' + (isCat ? ("In Ptolemy's catalogue: " + s[11]) : "Not in Ptolemy's catalogue") + '</div>' +
        '<div>Magnitude ' + s[6].toFixed(2) + ', HIP ' + s[12] + '<br>Highest point: <strong>' + visTxt + '</strong></div>';
      const tx = Math.min(rect.width - 210, Math.max(10, mx + 16));
      const ty = Math.min(rect.height - 95, Math.max(10, my - 20));
      tip.style.left = tx + "px";
      tip.style.top = ty + "px";
      tip.classList.add("is-on");
    }} else {{
      tip.classList.remove("is-on");
    }}
  }});
  canvas.addEventListener("mouseleave", () => {{
    state.hoverIdx = -1;
    tip.classList.remove("is-on");
    render();
  }});

  if (typeof ResizeObserver !== "undefined") {{
    new ResizeObserver(resize).observe(canvas.parentElement);
  }} else {{
    window.addEventListener("resize", resize);
  }}
  resize();
}})();
</script>
</figure>
"""


def build_contour_html(summary: Dict, grids: Dict) -> str:
    # Downsample to 100-yr x 1.0-deg (111 x 36) for fast page load with bilinear interpolation
    ep = grids["epochs"][::2]
    la = grids["lats"][::2]

    def pack(arr):
        a = np.clip(np.array(arr, dtype=np.float64)[::2, ::2], -180.0, 0.0)
        return np.round(a, 1).tolist()

    payload = {
        "epochs": ep,
        "lats": la,
        "grids": {
            "kv025": pack(grids["m1_all48_kv025"]),
            "kv015": pack(grids["m1_all48_kv015"]),
            "aratus": pack(grids["m1_aratus_kv025"]),
            "infig": pack(grids["m1_infig_kv025"]),
        },
        "bootE": grids["boot_epochs"],
        "bootL": grids["boot_lats"],
        "variants": [
            {"id": "v40", "lbl": "Bright stars (magnitude 4.0 or brighter)", "t": -120, "lat": 31.8, "col": "#7fb39d", "shape": "diamond"},
            {"id": "v45", "lbl": "Stars of magnitude 4.5 or brighter", "t": 50, "lat": 30.3, "col": "#7fb39d", "shape": "diamond"},
            {"id": "m2", "lbl": "Haze left free (0.10)", "t": 160, "lat": 35.7, "col": "#cfa544", "shape": "square"},
            {"id": "kv15", "lbl": "Light haze (0.15)", "t": 210, "lat": 33.2, "col": "#cfa544", "shape": "square"},
            {"id": "m1", "lbl": "Main model (0.25)", "t": 910, "lat": 25.8, "col": "#d08a5c", "shape": "triangle"},
        ],
        "m3Epoch": summary["m3_geometric_cap"]["epoch"],
    }
    payload_json = json.dumps(payload, separators=(",", ":"))

    return f"""<figure class="fig sky-contour-fig" id="sky-likelihood-map">
<style>
{PANEL_CSS}
.con-tabs {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
.con-canvas-wrap {{ position: relative; padding: 0.5rem 1rem 0.4rem; }}
.con-canvas-wrap canvas {{ display: block; width: 100%; height: 390px; cursor: crosshair; }}
.con-bar {{
  display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;
  gap: 0.5rem 1.2rem; padding: 0.7rem 1.25rem 0.9rem;
  border-top: 1px solid var(--band-line); background: var(--band-soft);
  font: 400 0.8rem/1.45 var(--sans); color: var(--band-ink-soft);
}}
.con-right-tools {{ display: flex; flex-wrap: wrap; gap: 0.5rem 1rem; align-items: center; }}
.con-right-tools label {{ display: inline-flex; align-items: center; gap: 0.35rem; cursor: pointer; }}
</style>
<div class="sky-panel">
  <div class="sky-head">
    <div>
      <p class="sky-eyebrow">Fit by date and latitude</p>
      <h3 class="sky-title">How well each date and latitude fits</h3>
    </div>
    <div class="con-tabs" id="con-tabs" role="group" aria-label="Version of the test">
      <button type="button" class="sky-btn con-tab is-active" aria-pressed="true" data-grid="kv015">Light haze</button>
      <button type="button" class="sky-btn con-tab" aria-pressed="false" data-grid="kv025">Main model</button>
      <button type="button" class="sky-btn con-tab" aria-pressed="false" data-grid="aratus">Aratus's stars only</button>
      <button type="button" class="sky-btn con-tab" aria-pressed="false" data-grid="infig">Stars inside the figures only</button>
    </div>
  </div>
  <p class="sky-legend">
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><rect x="2.5" y="2.5" width="7" height="7" transform="rotate(45 6 6)" fill="#7fb39d" stroke="#0d1421"/></svg>Bright stars only (magnitude 4.0 or 4.5)</span>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><rect x="2" y="2" width="8" height="8" fill="#cfa544" stroke="#0d1421"/></svg>Haze left free, and light haze</span>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><path d="M6 1 L11 10 L1 10 Z" fill="#d08a5c" stroke="#0d1421"/></svg>Main model (910 CE)</span>
    <span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="#7fb39d" stroke-width="1.5" stroke-dasharray="2 3"/></svg>Plain empty circle (41 BCE)</span>
    <span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="#f6f1e8" stroke-width="1.5" stroke-dasharray="5 4"/></svg>3000 BCE</span>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="2.2" fill="#c9daf0"/></svg>Reshuffled skies (main model)</span>
  </p>
  <div class="con-canvas-wrap">
    <canvas id="con-canvas" role="img" aria-label="Map of how well each date and observer's latitude fits the empty patch, with the 3000 BCE line, historical sites and the best dates from each version of the test marked."></canvas>
  </div>
  <div class="con-bar">
    <div id="con-hover-out" aria-live="polite">Hover over the map to see how much worse each point fits than the best (0 is best).</div>
    <div class="con-right-tools">
      <label><input type="checkbox" id="con-deep"> Show 10,000 BCE to 1000 CE</label>
      <label><input type="checkbox" id="con-boot" checked> 500 reshuffled skies (main model)</label>
    </div>
  </div>
</div>
<figcaption>How well each date (across) and observer's latitude (up) fits the empty patch, in the test fixed in advance. Lighter means a better fit; dark blue is worse by many orders of magnitude. The light-haze version peaks at 210 CE, 33.2° N, close to Hipparchus's Rhodes and Ptolemy's Alexandria. The main model assumes thicker haze near the horizon, and that pulls its peak past 137 CE into the shaded zone after the catalogue was written (910 CE, 25.8° N). In every version and all 500 reshuffled skies, 3000 BCE (dashed line) sits deep in the dark zone, at least 96 below the best on this scale (the difference in log-likelihood, Δln L ≤ −96).</figcaption>
<script>
(function() {{
  const D = {payload_json};
  const canvas = document.getElementById("con-canvas");
  const ctx = canvas.getContext("2d");
  const hoverOut = document.getElementById("con-hover-out");
  const tabs = Array.from(document.querySelectorAll("#con-tabs .con-tab"));
  const deepBox = document.getElementById("con-deep");
  const bootBox = document.getElementById("con-boot");

  let activeKey = "kv015";
  let hoverPt = null;
  let W = 700, H = 390;

  const PAD = {{ l: 54, r: 22, t: 26, b: 44 }};

  function fmtYear(t) {{
    const y = Math.round(t);
    return y <= 0 ? (1 - y) + " BCE" : y + " CE";
  }}

  // One smooth ramp for dLL in [-140, 0]: dark night blue (poor fit) through copper to cream (best)
  const SANS = (getComputedStyle(document.documentElement).getPropertyValue("--sans") || "").trim() || "system-ui, sans-serif";
  const C = {{ band: "#0d1421", ink: "#f6f1e8", inkSoft: "#cdd3de", faint: "#8f9bb1", line: "#2a3750", copper: "#d08a5c", verdigris: "#7fb39d", slate: "#c9daf0" }};
  function colorForDLL(dll) {{
    const u = Math.max(0, Math.min(1, 1 - Math.sqrt(Math.max(0, -dll) / 140)));
    const stops = [
      [0.00, 13, 20, 33],
      [0.45, 52, 46, 62],
      [0.75, 150, 94, 64],
      [0.90, 208, 138, 92],
      [1.00, 246, 241, 232]
    ];
    for (let i = 0; i < stops.length - 1; i++) {{
      if (u >= stops[i][0] && u <= stops[i + 1][0]) {{
        const f = (u - stops[i][0]) / (stops[i + 1][0] - stops[i][0]);
        const r = Math.round(stops[i][1] + f * (stops[i + 1][1] - stops[i][1]));
        const g = Math.round(stops[i][2] + f * (stops[i + 1][2] - stops[i][2]));
        const b = Math.round(stops[i][3] + f * (stops[i + 1][3] - stops[i][3]));
        return [r, g, b];
      }}
    }}
    return [246, 241, 232];
  }}

  // Text with a thin dark outline so it stays legible over light and dark parts of the map
  function label(txt, x, y, col) {{
    ctx.lineWidth = 3;
    ctx.lineJoin = "round";
    ctx.strokeStyle = "rgba(13, 20, 33, 0.85)";
    ctx.strokeText(txt, x, y);
    ctx.fillStyle = col;
    ctx.fillText(txt, x, y);
  }}

  function interpGrid(grid, t, lat) {{
    const ep = D.epochs, la = D.lats;
    const de = ep[1] - ep[0], dl = la[1] - la[0];
    const tCl = Math.max(ep[0], Math.min(ep[ep.length - 1], t));
    const lCl = Math.max(la[0], Math.min(la[la.length - 1], lat));
    const ei = Math.min(ep.length - 2, Math.max(0, Math.floor((tCl - ep[0]) / de)));
    const li = Math.min(la.length - 2, Math.max(0, Math.floor((lCl - la[0]) / dl)));
    const ft = (tCl - ep[ei]) / de;
    const fl = (lCl - la[li]) / dl;
    return (1 - ft) * (1 - fl) * grid[ei][li] + ft * (1 - fl) * grid[ei + 1][li] +
           (1 - ft) * fl * grid[ei][li + 1] + ft * fl * grid[ei + 1][li + 1];
  }}

  function resize() {{
    const rect = canvas.parentElement.getBoundingClientRect();
    W = Math.max(240, Math.round(rect.width - 32));
    H = W < 500 ? 330 : 390;
    canvas.style.height = H + "px";
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    render();
  }}

  function render() {{
    const grid = D.grids[activeKey];
    const tMin = deepBox.checked ? -10000 : -4000;
    const tMax = 1000;
    const lMin = 15, lMax = 45;
    const pw = W - PAD.l - PAD.r;
    const ph = H - PAD.t - PAD.b;

    const xOf = t => PAD.l + ((t - tMin) / (tMax - tMin)) * pw;
    const yOf = l => PAD.t + ((lMax - l) / (lMax - lMin)) * ph;

    ctx.clearRect(0, 0, W, H);

    // Draw smooth heatmap via offscreen pixel buffer
    const nx = Math.min(260, Math.round(pw));
    const ny = Math.min(140, Math.round(ph));
    const off = document.createElement("canvas");
    off.width = nx; off.height = ny;
    const octx = off.getContext("2d");
    const img = octx.createImageData(nx, ny);
    for (let iy = 0; iy < ny; iy++) {{
      const lat = lMax - ((iy + 0.5) / ny) * (lMax - lMin);
      for (let ix = 0; ix < nx; ix++) {{
        const t = tMin + ((ix + 0.5) / nx) * (tMax - tMin);
        const dll = interpGrid(grid, t, lat);
        const [r, g, b] = colorForDLL(dll);
        const k = (iy * nx + ix) * 4;
        img.data[k] = r; img.data[k + 1] = g; img.data[k + 2] = b; img.data[k + 3] = 255;
      }}
    }}
    octx.putImageData(img, 0, 0);
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(off, PAD.l, PAD.t, pw, ph);

    // Contour outlines (Δln L = -3.0 ~ 95% star-level, -15, -50, -100)
    const levels = [
      {{ v: -3.0, col: "rgba(13, 20, 33, 0.8)", w: 1.4 }},
      {{ v: -15.0, col: "rgba(246, 241, 232, 0.45)", w: 1.0 }},
      {{ v: -50.0, col: "rgba(246, 241, 232, 0.25)", w: 0.9 }}
    ];
    levels.forEach(lv => {{
      ctx.fillStyle = lv.col;
      for (let iy = 0; iy < ny - 1; iy++) {{
        const lat = lMax - ((iy + 0.5) / ny) * (lMax - lMin);
        for (let ix = 0; ix < nx - 1; ix++) {{
          const t = tMin + ((ix + 0.5) / nx) * (tMax - tMin);
          const v0 = interpGrid(grid, t, lat);
          const v1 = interpGrid(grid, t + (tMax - tMin) / nx, lat);
          const v2 = interpGrid(grid, t, lat - (lMax - lMin) / ny);
          if ((v0 >= lv.v) !== (v1 >= lv.v) || (v0 >= lv.v) !== (v2 >= lv.v)) {{
            ctx.fillRect(PAD.l + (ix / nx) * pw, PAD.t + (iy / ny) * ph, lv.w, lv.w);
          }}
        }}
      }}
    }});

    // Shaded zone after the catalogue was written (> 137 CE)
    const x137 = xOf(137);
    ctx.fillStyle = "rgba(13, 20, 33, 0.4)";
    ctx.fillRect(x137, PAD.t, PAD.l + pw - x137, ph);
    ctx.save();
    ctx.setLineDash([3, 3]);
    ctx.strokeStyle = "rgba(246, 241, 232, 0.45)";
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(x137, PAD.t); ctx.lineTo(x137, PAD.t + ph); ctx.stroke();
    ctx.restore();
    ctx.font = "400 11px " + SANS;
    const aTxt = W < 520 ? "After 137 CE" : "After the catalogue (137 CE)";
    const aW = ctx.measureText(aTxt).width;
    label(aTxt, Math.max(PAD.l + 4, Math.min(PAD.l + pw - aW - 4, x137 + 6)), PAD.t + 14, C.inkSoft);

    // Vertical 3000 BCE threshold line
    const x3000 = xOf(-2999);
    if (x3000 > PAD.l && x3000 < PAD.l + pw) {{
      ctx.save();
      ctx.setLineDash([5, 4]);
      ctx.strokeStyle = C.ink;
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(x3000, PAD.t); ctx.lineTo(x3000, PAD.t + ph); ctx.stroke();
      ctx.restore();
      label("3000 BCE", x3000 + 6, PAD.t + 14, C.ink);
    }}

    // Plain empty circle (M3) best date, 41 BCE
    const xm3 = xOf(D.m3Epoch);
    ctx.save();
    ctx.setLineDash([2, 3]);
    ctx.strokeStyle = "rgba(127, 179, 157, 0.85)";
    ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.moveTo(xm3, PAD.t); ctx.lineTo(xm3, PAD.t + ph); ctx.stroke();
    ctx.restore();

    // 500 reshuffled skies (spatial-block bootstrap of the main model)
    if (bootBox.checked) {{
      ctx.fillStyle = "rgba(201, 218, 240, 0.55)";
      for (let i = 0; i < D.bootE.length; i++) {{
        const bx = xOf(D.bootE[i]) + (((i * 37) % 11) - 5) * 0.6;
        const by = yOf(D.bootL[i]) + (((i * 53) % 9) - 4) * 0.5;
        if (bx >= PAD.l && bx <= PAD.l + pw && by >= PAD.t && by <= PAD.t + ph) {{
          ctx.beginPath(); ctx.arc(bx, by, 2.0, 0, Math.PI * 2); ctx.fill();
        }}
      }}
    }}

    // Historical site markers
    const sites = [
      {{ lbl: "Rhodes (128 BCE)", t: -127, lat: 36.4, dx: -102, dy: -8 }},
      {{ lbl: "Alexandria (137 CE)", t: 137, lat: 31.2, dx: -115, dy: 14 }},
      {{ lbl: "Babylon (1100 BCE)", t: -1099, lat: 32.5, dx: -114, dy: -6 }},
      {{ lbl: "Crete (2600 BCE)", t: -2599, lat: 35.3, dx: -95, dy: -8 }}
    ];
    if (deepBox.checked) {{
      sites.push({{ lbl: "Göbekli Tepe (9600 BCE)", t: -9599, lat: 37.2, dx: 8, dy: -6 }});
    }}
    ctx.font = "400 11px " + SANS;
    sites.forEach(s => {{
      const sx = xOf(s.t), sy = yOf(s.lat);
      if (sx < PAD.l || sx > PAD.l + pw) return;
      ctx.beginPath(); ctx.arc(sx, sy, 4, 0, Math.PI * 2);
      ctx.fillStyle = C.band; ctx.fill();
      ctx.strokeStyle = C.ink; ctx.lineWidth = 1.6; ctx.stroke();
      const tw = ctx.measureText(s.lbl).width;
      const lx = Math.max(PAD.l + 3, Math.min(PAD.l + pw - tw - 3, sx + s.dx));
      label(s.lbl, lx, sy + s.dy, C.ink);
    }});

    // Best date in each version: diamond = bright stars only, square = haze free / light haze, triangle = main model
    D.variants.forEach(v => {{
      const vx = xOf(v.t), vy = yOf(v.lat);
      if (vx < PAD.l || vx > PAD.l + pw) return;
      ctx.save();
      ctx.translate(vx, vy);
      ctx.fillStyle = v.col;
      ctx.strokeStyle = C.band;
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      if (v.shape === "triangle") {{
        ctx.moveTo(0, -6); ctx.lineTo(5.5, 4); ctx.lineTo(-5.5, 4); ctx.closePath();
      }} else if (v.shape === "square") {{
        ctx.rect(-4.5, -4.5, 9, 9);
      }} else {{
        ctx.moveTo(0, -6); ctx.lineTo(6, 0); ctx.lineTo(0, 6); ctx.lineTo(-6, 0); ctx.closePath();
      }}
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    }});

    // Axes frame and ticks
    ctx.strokeStyle = C.line;
    ctx.lineWidth = 1;
    ctx.strokeRect(PAD.l, PAD.t, pw, ph);

    ctx.font = "400 11px " + SANS;
    ctx.fillStyle = C.inkSoft;
    ctx.textAlign = "center";
    const xTicks = deepBox.checked
      ? (W < 520 ? [-10000, -6000, -2000, 1000] : [-10000, -8000, -6000, -4000, -2000, 0, 1000])
      : (W < 520 ? [-4000, -2000, 0] : [-4000, -3000, -2000, -1000, 0, 1000]);
    xTicks.forEach(tx => {{
      const x = xOf(tx);
      ctx.beginPath(); ctx.moveTo(x, PAD.t + ph); ctx.lineTo(x, PAD.t + ph + 5); ctx.stroke();
      ctx.fillText(tx === 0 ? "1 BCE" : (tx < 0 ? (-tx) + " BCE" : tx + " CE"), x, PAD.t + ph + 18);
    }});
    ctx.fillStyle = C.faint;
    ctx.fillText("Date", PAD.l + pw / 2, H - 6);

    ctx.textAlign = "right";
    for (let ly = 15; ly <= 45; ly += 5) {{
      const y = yOf(ly);
      ctx.beginPath(); ctx.moveTo(PAD.l - 5, y); ctx.lineTo(PAD.l, y); ctx.stroke();
      ctx.fillStyle = C.inkSoft;
      ctx.fillText(ly + "° N", PAD.l - 8, y + 3.5);
    }}
    ctx.textAlign = "left";

    // Hover crosshair
    if (hoverPt) {{
      const hx = xOf(hoverPt.t), hy = yOf(hoverPt.lat);
      ctx.save();
      ctx.strokeStyle = C.copper;
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(hx, PAD.t); ctx.lineTo(hx, PAD.t + ph);
      ctx.moveTo(PAD.l, hy); ctx.lineTo(PAD.l + pw, hy);
      ctx.stroke();
      ctx.restore();
    }}
  }}

  tabs.forEach(tab => {{
    tab.addEventListener("click", () => {{
      activeKey = tab.dataset.grid;
      tabs.forEach(t => {{ t.classList.toggle("is-active", t === tab); t.setAttribute("aria-pressed", t === tab ? "true" : "false"); }});
      render();
    }});
  }});
  deepBox.addEventListener("change", render);
  bootBox.addEventListener("change", render);

  canvas.addEventListener("mousemove", ev => {{
    const rect = canvas.getBoundingClientRect();
    const mx = ev.clientX - rect.left;
    const my = ev.clientY - rect.top;
    const pw = W - PAD.l - PAD.r, ph = H - PAD.t - PAD.b;
    if (mx < PAD.l || mx > PAD.l + pw || my < PAD.t || my > PAD.t + ph) {{
      hoverPt = null;
      hoverOut.textContent = "Hover over the map to see how much worse each point fits than the best (0 is best).";
      render();
      return;
    }}
    const tMin = deepBox.checked ? -10000 : -4000;
    const t = tMin + ((mx - PAD.l) / pw) * (1000 - tMin);
    const lat = 45 - ((my - PAD.t) / ph) * 30;
    const dll = interpGrid(D.grids[activeKey], t, lat);
    const log10Odds = (-dll / Math.LN10);
    const oddsStr = log10Odds < 0.15 ? "about as good as the best" : ("about " + (log10Odds < 3 ? ("1 in " + Math.round(Math.pow(10, log10Odds)).toLocaleString()) : ("1 in 10^" + log10Odds.toFixed(1))) + " as likely as the best");
    hoverPt = {{ t, lat }};
    hoverOut.innerHTML = '<strong>' + fmtYear(t) + ', ' + lat.toFixed(1) + '° N</strong>: <strong>' + dll.toFixed(1) + '</strong> against the best (' + oddsStr + ')';
    render();
  }});
  canvas.addEventListener("mouseleave", () => {{
    hoverPt = null;
    hoverOut.textContent = "Hover over the map to see how much worse each point fits than the best (0 is best).";
    render();
  }});

  if (typeof ResizeObserver !== "undefined") {{
    new ResizeObserver(resize).observe(canvas.parentElement);
  }} else {{
    window.addEventListener("resize", resize);
  }}
  resize();
}})();
</script>
</figure>
"""


def build_rim_html(cat: Dict) -> str:
    # 12 of the southernmost bright Ptolemy stars, and the 12 brightest missing southern stars in results/rim_stars.tsv
    # (Alp1 Cen, HIP 71683, is left out of the second list: it is the close companion of the listed Alp2 Cen).
    ptol_hips = [30438, 60718, 71681, 68702, 85267, 62434, 85258, 83081, 59747, 42913, 45941, 13847]
    miss_hips = [7588, 45238, 109268, 41037, 82273, 100751, 112122, 45556, 2081, 52727, 61585, 52419]

    hip_idx = {int(h): i for i, h in enumerate(cat["hip"])}
    stars_out = []
    for grp, hlist in ((1, ptol_hips), (0, miss_hips)):
        for hid in hlist:
            i = hip_idx[hid]
            u = cat["u0"][i]
            v = cat["vel"][i]
            label = COMMON_NAMES.get(hid, str(cat["name"][i])).split(" (")[0]
            cst = CST_FULL.get(str(cat["cst"][i]), "") if grp == 1 else "Left out"
            stars_out.append({
                "hip": hid,
                "name": label,
                "bayer": str(cat["name"][i]),
                "cst": cst,
                "vmag": round(float(cat["vmag"][i]), 2),
                "ra": round(float(cat["ra"][i]), 2),
                "cat": grp,
                "u": [round(float(u[0]), 5), round(float(u[1]), 5), round(float(u[2]), 5)],
                "v": [round(float(v[0] * 1e6), 4), round(float(v[1] * 1e6), 4), round(float(v[2] * 1e6), 4)],
            })

    payload_json = json.dumps(stars_out, separators=(",", ":"))

    return f"""<figure class="fig sky-rim-fig" id="sky-horizon-rim">
<style>
{PANEL_CSS}
.rim-score {{ font: 400 0.84rem/1.4 var(--sans); color: var(--band-ink-soft); font-variant-numeric: tabular-nums; }}
.fig .rim-score strong.is-good {{ color: var(--band-verdigris); }}
.fig .rim-score strong.is-bad {{ color: var(--band-copper); }}
.rim-canvas-wrap {{ position: relative; padding: 0.4rem 1rem 0.3rem; }}
.rim-canvas-wrap canvas {{ display: block; width: 100%; height: 340px; }}
.rim-controls {{ padding: 0.8rem 1.25rem 1rem; border-top: 1px solid var(--band-line); background: var(--band-soft); }}
.rim-presets {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
</style>
<div class="sky-panel">
  <div class="sky-head">
    <div>
      <p class="sky-eyebrow">24 stars near the southern horizon</p>
      <h3 class="sky-title">The stars on the rim</h3>
    </div>
    <div class="rim-score" id="rim-score" aria-live="polite">-</div>
  </div>
  <p class="sky-legend">
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="4.5" fill="#e9d7a8"/></svg>In Ptolemy's catalogue (filled)</span>
    <span class="key"><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="4" fill="none" stroke="#c9daf0" stroke-width="2"/></svg>Bright stars he left out (rings)</span>
    <span class="key"><svg viewBox="0 0 16 12" width="16" height="12" aria-hidden="true"><line x1="0" x2="16" y1="6" y2="6" stroke="#d08a5c" stroke-width="2"/></svg>Horizon</span>
  </p>
  <div class="rim-canvas-wrap">
    <canvas id="rim-canvas" role="img" aria-label="How high the 12 southernmost stars Ptolemy listed and the 12 brightest southern stars he left out climb above or below the horizon, for a chosen place and date."></canvas>
  </div>
  <div class="rim-controls">
    <div class="rim-presets" id="rim-presets" role="group" aria-label="Places and dates">
      <button type="button" class="sky-btn rim-btn is-active" aria-pressed="true" data-t="-127" data-lat="36.4">Rhodes, 128 BCE (Hipparchus)</button>
      <button type="button" class="sky-btn rim-btn" aria-pressed="false" data-t="137" data-lat="31.2">Alexandria, 137 CE (Ptolemy)</button>
      <button type="button" class="sky-btn rim-btn" aria-pressed="false" data-t="-1099" data-lat="32.5">Babylon, 1100 BCE</button>
      <button type="button" class="sky-btn rim-btn" aria-pressed="false" data-t="-2599" data-lat="35.3">Crete, 2600 BCE</button>
      <button type="button" class="sky-btn rim-btn" aria-pressed="false" data-t="-9599" data-lat="37.2">Göbekli Tepe, 9600 BCE</button>
    </div>
  </div>
</div>
<figcaption>How high each star climbs at its highest point, in degrees above or below the sea horizon, for 12 of the southernmost bright stars Ptolemy listed (filled dots) and the 12 brightest southern stars he left out (rings), placed in order around the sky. Alpha-1 Centauri is not among the rings, because it is the close companion of a listed star. At <strong>Rhodes in 128 BCE</strong> all 12 listed stars rise and 9 of the 12 left-out stars never do. Of the other three, Avior grazes the horizon (+0.01°), Iota Carinae stands 2° up, and Mu Velorum stands 14° up, which we cannot explain. At <strong>Alexandria in 137 CE</strong> seven of the twelve left-out stars stand more than 3° up and are still not in the catalogue. At <strong>2600 BCE</strong> or <strong>9600 BCE</strong> the two groups are mixed on both sides of the horizon. Among the 30 brightest left-out stars in the results file, 23 never rose at Rhodes and 14 at Alexandria.</figcaption>
<script>
(function() {{
  const STARS = {payload_json};
  const DAS2R = Math.PI / (180 * 3600);
  const D2PI = 2 * Math.PI;
  const XYPOL = [
    [5453.282155, 0.4252841, -0.00037173, -0.000000152],
    [-73750.930350, -0.7675452, -0.00018725, 0.000000231]
  ];
  const XYPER = [
    [256.75, -819.940624, 75004.344875, 81491.287984, 1558.515853],
    [708.15, -8444.676815, 624.033993, 787.163481, 7774.939698],
    [274.20, 2600.009459, 1251.136893, 1251.296102, -2219.534038],
    [241.45, 2755.175630, -1102.212834, -1257.950837, -2523.969396],
    [2309.00, -167.659835, -2660.664980, -2966.799730, 247.850422],
    [492.20, 871.855056, 699.291817, 639.744522, -846.485643],
    [396.10, 44.769698, 153.167220, 131.600209, -1393.124055],
    [288.90, -512.313065, -950.865637, -445.040117, 368.526116],
    [231.10, -819.415595, 499.754645, 584.522874, 749.045012],
    [1610.00, -538.071099, -145.188210, -89.756563, 444.704518],
    [620.00, -189.793622, 558.116553, 524.429630, 235.934465],
    [157.87, -402.922932, -23.923029, -13.549067, 374.049623],
    [220.30, 179.516345, -165.405086, -210.157124, -171.330180],
    [1200.00, -9.814756, 9.344131, -44.919798, -22.899655]
  ];
  function ltpequ(epj) {{
    const t = (epj - 2000.0) / 100.0;
    let x = 0, y = 0;
    const w0 = D2PI * t;
    for (let i = 0; i < XYPER.length; i++) {{
      const a = w0 / XYPER[i][0];
      const c = Math.cos(a), s = Math.sin(a);
      x += c * XYPER[i][1] + s * XYPER[i][3];
      y += c * XYPER[i][2] + s * XYPER[i][4];
    }}
    let wt = 1.0;
    for (let i = 0; i < 4; i++) {{ x += XYPOL[0][i] * wt; y += XYPOL[1][i] * wt; wt *= t; }}
    x *= DAS2R; y *= DAS2R;
    const z = Math.sqrt(Math.max(0, 1 - x * x - y * y));
    const n = Math.hypot(x, y, z) || 1;
    return [x / n, y / n, z / n];
  }}

  const canvas = document.getElementById("rim-canvas");
  const ctx = canvas.getContext("2d");
  const scoreEl = document.getElementById("rim-score");
  const btns = Array.from(document.querySelectorAll("#rim-presets .rim-btn"));

  let curT = -127, curLat = 36.4, targetT = -127, targetLat = 36.4;
  let W = 700, H = 340, animId = null;
  const PAD = {{ l: 50, r: 24, t: 24, b: 38 }};

  function resize() {{
    const rect = canvas.parentElement.getBoundingClientRect();
    W = Math.max(240, Math.round(rect.width - 32));
    H = W < 500 ? 310 : 340;
    canvas.style.height = H + "px";
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    render();
  }}

  const SANS = (getComputedStyle(document.documentElement).getPropertyValue("--sans") || "").trim() || "system-ui, sans-serif";
  const C = {{ band: "#0d1421", bandSoft: "#131c2c", ink: "#f6f1e8", inkSoft: "#cdd3de", faint: "#8f9bb1", line: "#2a3750", copper: "#d08a5c", verdigris: "#7fb39d", slate: "#c9daf0" }};
  function catColor(vmag) {{
    const f = Math.max(0, Math.min(1, (vmag - 1.0) / 3.5));
    const a = [246, 241, 232], b = [207, 165, 68];
    return "rgb(" + a.map((x, k) => Math.round(x + f * (b[k] - x))).join(",") + ")";
  }}

  function render() {{
    const pw = W - PAD.l - PAD.r, ph = H - PAD.t - PAD.b;
    const yMin = -28, yMax = 32;
    const xOf = ra => PAD.l + (ra / 360) * pw;
    const yOf = h => PAD.t + ((yMax - Math.max(yMin, Math.min(yMax, h))) / (yMax - yMin)) * ph;

    ctx.clearRect(0, 0, W, H);

    // Sky above the horizon (panel blue), haze band 0 to +6 deg, darker ground below
    const y0 = yOf(0);
    ctx.fillStyle = C.bandSoft;
    ctx.fillRect(PAD.l, PAD.t, pw, y0 - PAD.t);
    const y6 = yOf(6);
    ctx.fillStyle = "rgba(208, 138, 92, 0.08)";
    ctx.fillRect(PAD.l, y6, pw, y0 - y6);
    ctx.fillStyle = "#080d16";
    ctx.fillRect(PAD.l, y0, pw, PAD.t + ph - y0);

    // Horizontal grid lines
    ctx.font = "400 11px " + SANS;
    ctx.textAlign = "right";
    for (const h of [-20, -10, 0, 10, 20, 30]) {{
      const y = yOf(h);
      ctx.beginPath(); ctx.moveTo(PAD.l, y); ctx.lineTo(PAD.l + pw, y);
      ctx.strokeStyle = h === 0 ? C.copper : "rgba(246, 241, 232, 0.07)";
      ctx.lineWidth = h === 0 ? 2 : 1;
      ctx.stroke();
      ctx.fillStyle = h === 0 ? C.copper : C.faint;
      ctx.fillText((h > 0 ? "+" : "") + h + "°", PAD.l - 7, y + 3.5);
    }}
    ctx.textAlign = "left";
    ctx.fillStyle = C.faint;
    ctx.fillText("Above the horizon: rises", PAD.l + 8, PAD.t + 15);
    ctx.fillText("Below the horizon: never rises", PAD.l + 8, PAD.t + ph - 8);
    const placed = [];  // label boxes already drawn, to avoid overlaps

    // Evaluate stars at (curT, curLat)
    const pN = ltpequ(curT);
    const dt = curT - 1991.25;
    let catUp = 0, missDown = 0;

    STARS.forEach((s, idx) => {{
      let ux = s.u[0] + dt * s.v[0] * 1e-6;
      let uy = s.u[1] + dt * s.v[1] * 1e-6;
      let uz = s.u[2] + dt * s.v[2] * 1e-6;
      const n = Math.hypot(ux, uy, uz) || 1;
      ux /= n; uy /= n; uz /= n;
      const dec = (Math.asin(Math.max(-1, Math.min(1, ux * pN[0] + uy * pN[1] + uz * pN[2]))) * 180) / Math.PI;
      const hMax = 90 - Math.abs(curLat - dec);
      if (s.cat === 1 && hMax > 0) catUp++;
      if (s.cat === 0 && hMax <= 0) missDown++;

      const sx = xOf(s.ra), sy = yOf(hMax);
      const rad = Math.max(3.5, Math.min(7.5, (4.4 - s.vmag) * 1.45));

      // Stem to the horizon
      ctx.beginPath(); ctx.moveTo(sx, y0); ctx.lineTo(sx, sy);
      ctx.strokeStyle = s.cat === 1 ? "rgba(207, 165, 68, 0.35)" : "rgba(201, 218, 240, 0.3)";
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.beginPath(); ctx.arc(sx, sy, rad, 0, D2PI);
      if (s.cat === 1) {{
        // catalogued: filled cream-to-gold disc
        ctx.fillStyle = catColor(s.vmag);
        ctx.fill();
        ctx.strokeStyle = C.band; ctx.lineWidth = 1.2; ctx.stroke();
      }} else {{
        // left out: pale blue-white ring
        ctx.fillStyle = C.band; ctx.fill();
        ctx.strokeStyle = C.slate; ctx.lineWidth = 2; ctx.stroke();
      }}

      // Labels for the brightest stars only, to avoid clutter
      const showLbl = W > 480 ? (s.vmag < 2.95 || s.hip === 85267 || s.hip === 13847) : (s.vmag < 2.2 || s.hip === 2081);
      if (showLbl) {{
        ctx.font = "400 11px " + SANS;
        const tw = ctx.measureText(s.name).width;
        const alignR = s.ra > 315;
        const first = idx % 2 === 0 ? -rad - 4 : rad + 12;
        const tries = [first, idx % 2 === 0 ? rad + 12 : -rad - 4, first + (first < 0 ? -12 : 12)];
        for (const dy of tries) {{
          const x0 = alignR ? sx - 6 - tw : sx + 6;
          const box = [x0 - 2, sy + dy - 10, x0 + tw + 2, sy + dy + 3];
          const hit = placed.some(b => !(box[2] < b[0] || box[0] > b[2] || box[3] < b[1] || box[1] > b[3]));
          if (hit) continue;
          placed.push(box);
          ctx.textAlign = "left";
          ctx.lineWidth = 3; ctx.lineJoin = "round";
          ctx.strokeStyle = "rgba(13, 20, 33, 0.85)";
          ctx.strokeText(s.name, x0, sy + dy);
          ctx.fillStyle = s.cat === 1 ? C.ink : C.slate;
          ctx.fillText(s.name, x0, sy + dy);
          break;
        }}
      }}
    }});

    // Frame and x-axis
    ctx.strokeStyle = C.line;
    ctx.lineWidth = 1;
    ctx.strokeRect(PAD.l, PAD.t, pw, ph);
    ctx.textAlign = "center";
    ctx.font = "400 11px " + SANS;
    ctx.fillStyle = C.inkSoft;
    for (let hr = 0; hr <= 24; hr += 4) {{
      const x = xOf(hr * 15);
      ctx.fillText(hr + "h", x, PAD.t + ph + 16);
    }}
    ctx.fillStyle = C.faint;
    ctx.fillText(W < 480 ? "Right ascension (hours)" : "Position around the sky (right ascension, hours)", PAD.l + pw / 2, H - 5);
    ctx.textAlign = "left";

    scoreEl.innerHTML = 'Catalogued stars that rise: <strong class="' + (catUp === 12 ? 'is-good' : 'is-bad') + '">' + catUp + '/12</strong><br>Left-out stars that never rise: <strong class="' + '' + '">' + missDown + '/12</strong>';
  }}

  function animateTo(t, lat) {{
    targetT = t; targetLat = lat;
    if (animId) cancelAnimationFrame(animId);
    const startT = curT, startLat = curLat;
    const t0 = performance.now(), dur = 520;
    function tick(now) {{
      const p = Math.min(1, (now - t0) / dur);
      const ease = 1 - Math.pow(1 - p, 3);
      curT = startT + (targetT - startT) * ease;
      curLat = startLat + (targetLat - startLat) * ease;
      render();
      if (p < 1) animId = requestAnimationFrame(tick);
    }}
    animId = requestAnimationFrame(tick);
  }}

  btns.forEach(btn => {{
    btn.addEventListener("click", () => {{
      btns.forEach(b => {{ b.classList.toggle("is-active", b === btn); b.setAttribute("aria-pressed", b === btn ? "true" : "false"); }});
      animateTo(Number(btn.dataset.t), Number(btn.dataset.lat));
    }});
  }});

  if (typeof ResizeObserver !== "undefined") {{
    new ResizeObserver(resize).observe(canvas.parentElement);
  }} else {{
    window.addEventListener("resize", resize);
  }}
  resize();
}})();
</script>
</figure>
"""


def build_verdict_html(summary: Dict) -> str:
    earliest = summary["combined_honest_epoch_labels"][0]
    bright = fmt_year(variant_epoch(summary, "vmag_le_4.0"))
    circle = fmt_year(summary["m3_geometric_cap"]["epoch"])
    free = fmt_year(summary["m2_free_extinction"]["best"]["epoch"])
    m1 = summary["primary_m1"]["epoch_label"]
    return f"""<div class="verdict">
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">The test fixed in advance</p>
    <p class="verdict-text">Could the empty patch have been set before 3000 BCE?</p>
    <p class="verdict-note">No. Every version of the test puts it after {earliest}, and a sky of 3000 BCE fits far worse.</p>
  </div>
  <p class="verdict-status is-no"><span class="dot" aria-hidden="true"></span>Excluded</p>
</div>
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">What the patch records</p>
    <p class="verdict-text">The horizon of the Greek astronomers who compiled the catalogue, about 130 BCE to 140 CE</p>
    <p class="verdict-note">Bright stars alone give {bright}, a plain empty circle {circle}, and a model free to choose its own haze {free}.</p>
  </div>
  <p class="verdict-status is-yes"><span class="dot" aria-hidden="true"></span>The known answer</p>
</div>
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">What it cannot show</p>
    <p class="verdict-text">How old the constellation figures are</p>
    <p class="verdict-note">A cataloguer lists every star he can see, so the edge of the listed stars is his own horizon. The main model also gave {m1}, an impossible date, from one assumption about haze.</p>
  </div>
  <p class="verdict-status is-open"><span class="dot" aria-hidden="true"></span>Not tested</p>
</div>
</div>
"""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))
    grids = json.loads((RESULTS / "likelihood_grids.json").read_text(encoding="utf-8"))
    cat = sh.load_catalogs(v_max=5.0)

    (OUT_DIR / "tiles.html").write_text(build_tiles_html(summary), encoding="utf-8")
    (OUT_DIR / "verdict.html").write_text(build_verdict_html(summary), encoding="utf-8")
    (OUT_DIR / "sky_dome.html").write_text(build_sky_dome_html(cat, summary, grids), encoding="utf-8")
    (OUT_DIR / "contour.html").write_text(build_contour_html(summary, grids), encoding="utf-8")
    (OUT_DIR / "rim.html").write_text(build_rim_html(cat), encoding="utf-8")

    for p in sorted(OUT_DIR.glob("*.html")):
        print(f"Wrote {p.relative_to(REPO)} ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
