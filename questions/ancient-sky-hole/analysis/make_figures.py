#!/usr/bin/env python3
"""Generate interactive observatory HTML figures for site/figures/ancient-sky-hole/.

Reads ONLY locked results/ and primary data/ catalogs. Produces four self-contained,
zero-dependency interactive fragments embedded into site/content/ancient-sky-hole.md:
  1. tiles.html      - Headline metric tiles
  2. sky_dome.html   - Interactive Southern Hemisphere Celestial Time Machine (Vondrak 2011)
  3. contour.html    - Interactive 2D (Epoch x Latitude) Observatory Likelihood & Contour Map
  4. rim.html        - Interactive Horizon-Elevation Rim Explorer (Ptolemy vs. Missing Stars)
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


def build_tiles_html(summary: Dict) -> str:
    return """<div class="tiles">
<div class="tile"><p class="tile-value">201 BCE–1000 CE</p><p class="tile-label">combined honest range across 500 spatial-block bootstraps &amp; all 13 locked models</p></div>
<div class="tile"><p class="tile-value">121 BCE–160 CE</p><p class="tile-label">bright-star (V≤4), geometric-void &amp; free-extinction consensus (Hipparchus to Ptolemy)</p></div>
<div class="tile"><p class="tile-value">&gt; 10<sup>46</sup> : 1</p><p class="tile-label">likelihood odds against a 3000 BCE sky (Δln L = −106.2 in primary M1; −125.6 clear sky)</p></div>
<div class="tile"><p class="tile-value">0 of 500</p><p class="tile-label">spatial-block bootstrap resamples landing before 3000 BCE (earliest: 201 BCE)</p></div>
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
.sky-obs-fig {{ margin: 2.4rem 0 2.8rem; }}
.sky-plate {{
  background: radial-gradient(ellipse at 50% 35%, #151e34 0%, #0d1220 55%, #080b13 100%);
  border: 1px solid rgba(207, 165, 68, 0.34);
  border-radius: 6px;
  color: #f3ecdf;
  overflow: hidden;
  box-shadow: 0 22px 54px rgba(12, 10, 8, 0.28), inset 0 0 0 1px rgba(255, 240, 200, 0.05);
}}
.sky-head {{
  display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between;
  gap: 0.5rem 1.25rem;
  padding: 1.15rem 1.4rem 0.9rem;
  border-bottom: 1px solid rgba(207, 165, 68, 0.18);
  background: linear-gradient(180deg, rgba(207,165,68,0.06) 0%, rgba(0,0,0,0) 100%);
}}
.sky-eyebrow {{
  font: 500 10.5px/1.4 var(--mono); text-transform: uppercase; letter-spacing: 0.2em;
  color: #d8ad5e; margin: 0 0 0.25rem;
}}
.sky-title {{
  font: 400 1.42rem/1.2 var(--serif); color: #f8f2e6; margin: 0; letter-spacing: -0.01em;
}}
.sky-readout-pill {{
  display: flex; align-items: baseline; gap: 0.85rem;
  font-family: var(--mono); font-variant-numeric: tabular-nums;
  background: rgba(8, 11, 19, 0.72); border: 1px solid rgba(207, 165, 68, 0.32);
  padding: 0.4rem 0.8rem; border-radius: 999px;
}}
.sky-readout-epoch {{ font-size: 1.02rem; font-weight: 600; color: #f4cf82; }}
.sky-readout-lat {{ font-size: 0.85rem; color: #b9c5d8; }}
.sky-stage {{
  position: relative;
  display: flex; justify-content: center; align-items: center;
  padding: 0.9rem 1rem 0.6rem;
}}
.sky-canvas-wrap {{
  position: relative; width: 100%; max-width: 660px; aspect-ratio: 1 / 1;
}}
.sky-canvas-wrap canvas {{
  display: block; width: 100%; height: 100%; cursor: crosshair; touch-action: pan-y;
}}
.sky-tip {{
  position: absolute; pointer-events: none; z-index: 12;
  min-width: 175px; max-width: 240px;
  padding: 0.55rem 0.75rem; border-radius: 4px;
  background: rgba(10, 14, 24, 0.94);
  border: 1px solid rgba(207, 165, 68, 0.45);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.55);
  color: #ede5d4; font: 400 12px/1.45 var(--sans);
  opacity: 0; transition: opacity 0.12s ease;
}}
.sky-tip.is-on {{ opacity: 1; }}
.sky-tip-name {{ font: 600 13.5px/1.25 var(--serif); color: #f8e5b8; margin-bottom: 0.15rem; }}
.sky-tip-tag {{
  display: inline-block; font: 500 10px/1.2 var(--mono); text-transform: uppercase;
  letter-spacing: 0.1em; padding: 0.1rem 0.38rem; border-radius: 2px; margin-bottom: 0.35rem;
}}
.sky-tip-tag.is-cat {{ background: rgba(240, 193, 98, 0.18); color: #f5cd7c; border: 1px solid rgba(240, 193, 98, 0.35); }}
.sky-tip-tag.is-void {{ background: rgba(114, 182, 248, 0.16); color: #8cc9ff; border: 1px solid rgba(114, 182, 248, 0.35); }}
.sky-tip-meta {{ font-family: var(--mono); font-size: 11px; color: #b9c5d8; }}
.sky-legend {{
  display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem 1.3rem;
  padding: 0.45rem 1.2rem 0.75rem;
  font: 400 11.5px/1.4 var(--sans); color: #b6c1d4;
}}
.sky-leg-item {{ display: inline-flex; align-items: center; gap: 0.4rem; }}
.sky-dot {{ width: 9px; height: 9px; border-radius: 50%; display: inline-block; }}
.sky-dot.gold {{ background: #f5cb75; box-shadow: 0 0 7px rgba(245, 203, 117, 0.8); }}
.sky-dot.blue {{ background: #6fb8ff; box-shadow: 0 0 7px rgba(111, 184, 255, 0.75); }}
.sky-dot.ring {{ width: 14px; height: 2px; border-radius: 0; background: #e08652; }}
.sky-dot.track {{ width: 14px; height: 0; border-top: 1.5px dashed #cfa544; border-radius: 0; }}
.sky-hud {{
  display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px;
  background: rgba(207, 165, 68, 0.18);
  border-top: 1px solid rgba(207, 165, 68, 0.2);
  border-bottom: 1px solid rgba(207, 165, 68, 0.2);
}}
.sky-hud-cell {{ background: rgba(11, 16, 28, 0.88); padding: 0.7rem 0.9rem; text-align: center; }}
.sky-hud-val {{ font: 600 1.08rem/1.2 var(--mono); font-variant-numeric: tabular-nums; color: #f6e7c4; }}
.sky-hud-val.is-good {{ color: #8ad3b5; }}
.sky-hud-val.is-bad {{ color: #e88565; }}
.sky-hud-lbl {{ font: 400 10.5px/1.35 var(--sans); color: #9aa7bd; margin-top: 0.2rem; }}
.sky-controls {{ padding: 1.05rem 1.35rem 1.25rem; background: rgba(8, 11, 19, 0.7); }}
.sky-sliders {{ display: grid; grid-template-columns: 1.55fr 1fr auto; gap: 0.85rem 1.25rem; align-items: end; }}
.sky-slider-group label {{
  display: flex; justify-content: space-between; align-items: baseline;
  font: 500 11px/1.3 var(--mono); text-transform: uppercase; letter-spacing: 0.12em; color: #c7b89c;
  margin-bottom: 0.35rem;
}}
.sky-slider-group label strong {{ color: #f5cf81; font-size: 12.5px; letter-spacing: 0.02em; text-transform: none; }}
.sky-range {{
  -webkit-appearance: none; appearance: none; width: 100%; height: 5px;
  border-radius: 99px; background: rgba(207, 165, 68, 0.26); outline: none;
}}
.sky-range::-webkit-slider-thumb {{
  -webkit-appearance: none; appearance: none; width: 16px; height: 16px; border-radius: 50%;
  background: #f2c66d; border: 2px solid #0b0f1b; box-shadow: 0 0 10px rgba(242, 198, 109, 0.7); cursor: pointer;
}}
.sky-range::-moz-range-thumb {{
  width: 16px; height: 16px; border-radius: 50%;
  background: #f2c66d; border: 2px solid #0b0f1b; box-shadow: 0 0 10px rgba(242, 198, 109, 0.7); cursor: pointer;
}}
.sky-play-btn {{
  font: 500 11.5px/1 var(--mono); text-transform: uppercase; letter-spacing: 0.12em;
  padding: 0.62rem 1rem; border-radius: 4px; cursor: pointer;
  background: linear-gradient(180deg, rgba(207, 165, 68, 0.25), rgba(149, 87, 48, 0.25));
  border: 1px solid rgba(207, 165, 68, 0.55); color: #f8e5b8;
  transition: background 0.15s, border-color 0.15s;
  white-space: nowrap;
}}
.sky-play-btn:hover {{ background: rgba(207, 165, 68, 0.35); border-color: #f2c66d; }}
.sky-presets {{
  display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.95rem;
}}
.sky-preset {{
  font: 400 11.5px/1.25 var(--sans); padding: 0.36rem 0.68rem; border-radius: 3px; cursor: pointer;
  background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(207, 165, 68, 0.22);
  color: #d6cbb7; transition: all 0.15s;
}}
.sky-preset:hover {{ border-color: rgba(207, 165, 68, 0.6); color: #fff5df; background: rgba(207, 165, 68, 0.12); }}
.sky-preset.is-active {{
  background: rgba(207, 165, 68, 0.24); border-color: #e6ba63; color: #fff4d6; font-weight: 500;
}}
.sky-toggles {{
  display: flex; flex-wrap: wrap; gap: 0.5rem 1.2rem; margin-top: 0.85rem; padding-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  font: 400 11.5px/1.3 var(--mono); color: #a7b4c9;
}}
.sky-toggles label {{ display: inline-flex; align-items: center; gap: 0.38rem; cursor: pointer; }}
.sky-toggles input {{ accent-color: #e6ba63; }}
@media (max-width: 44rem) {{
  .sky-sliders {{ grid-template-columns: 1fr; }}
  .sky-hud {{ grid-template-columns: 1fr; }}
}}
</style>
<div class="sky-plate">
  <div class="sky-head">
    <div>
      <p class="sky-eyebrow">Interactive Astrolabe · Vondrák (2011) Precession Engine</p>
      <h3 class="sky-title">The Celestial Time Machine: Southern Sky Void</h3>
    </div>
    <div class="sky-readout-pill">
      <span class="sky-readout-epoch" id="sky-epoch-out">128 BCE</span>
      <span class="sky-readout-lat" id="sky-lat-out">36.4° N</span>
    </div>
  </div>

  <div class="sky-stage">
    <div class="sky-canvas-wrap">
      <canvas id="sky-dome-canvas" aria-label="Interactive southern celestial hemisphere map showing Ptolemy's catalogued stars, uncatalogued southern void stars, the 26,000-year precession circle, and the moving southern horizon."></canvas>
      <div class="sky-tip" id="sky-tip"></div>
    </div>
  </div>

  <div class="sky-legend">
    <span class="sky-leg-item"><i class="sky-dot gold"></i>Ptolemy's 48 constellations (<em>Almagest</em>)</span>
    <span class="sky-leg-item"><i class="sky-dot blue"></i>Uncatalogued bright southern stars (post-1600)</span>
    <span class="sky-leg-item"><i class="sky-dot ring"></i>Invisible southern horizon (<em>h</em><sub>max</sub> ≤ 0°)</span>
    <span class="sky-leg-item"><i class="sky-dot track"></i>25,772-yr South Celestial Pole track</span>
  </div>

  <div class="sky-hud">
    <div class="sky-hud-cell">
      <div class="sky-hud-val" id="hud-ptol-vis">—</div>
      <div class="sky-hud-lbl">Bright Ptolemy stars (V≤4.0) above horizon</div>
    </div>
    <div class="sky-hud-cell">
      <div class="sky-hud-val" id="hud-void-hid">—</div>
      <div class="sky-hud-lbl">Bright missing stars (V≤3.5) hidden below horizon</div>
    </div>
    <div class="sky-hud-cell">
      <div class="sky-hud-val" id="hud-dll">—</div>
      <div class="sky-hud-lbl">Locked model fit vs. peak (Δln L, clear sky)</div>
    </div>
  </div>

  <div class="sky-controls">
    <div class="sky-sliders">
      <div class="sky-slider-group">
        <label for="sky-epoch-slider"><span>Epoch (Precession)</span><strong id="sky-epoch-lbl">128 BCE</strong></label>
        <input class="sky-range" id="sky-epoch-slider" type="range" min="-10000" max="2000" step="10" value="-127">
      </div>
      <div class="sky-slider-group">
        <label for="sky-lat-slider"><span>Observer Latitude</span><strong id="sky-lat-lbl">36.4° N</strong></label>
        <input class="sky-range" id="sky-lat-slider" type="range" min="15" max="45" step="0.2" value="36.4">
      </div>
      <button type="button" class="sky-play-btn" id="sky-play-btn">&#9654; Orbit Precession</button>
    </div>

    <div class="sky-presets" id="sky-presets">
      <button type="button" class="sky-preset" data-t="-9599" data-lat="37.2">Göbekli Tepe · 9600 BCE</button>
      <button type="button" class="sky-preset" data-t="-2999" data-lat="31.3">Early Sumer · 3000 BCE</button>
      <button type="button" class="sky-preset" data-t="-2599" data-lat="35.3">Ovenden / Crete · 2600 BCE</button>
      <button type="button" class="sky-preset" data-t="-1099" data-lat="32.5">Babylon MUL.APIN · 1100 BCE</button>
      <button type="button" class="sky-preset is-active" data-t="-127" data-lat="36.4">Hipparchus · Rhodes 128 BCE</button>
      <button type="button" class="sky-preset" data-t="137" data-lat="31.2">Ptolemy · Alexandria 137 CE</button>
      <button type="button" class="sky-preset" data-t="910" data-lat="25.8">Primary M1 Overshoot · 910 CE</button>
      <button type="button" class="sky-preset" data-t="2000" data-lat="36.0">Today · 2000 CE</button>
    </div>

    <div class="sky-toggles">
      <label><input type="checkbox" id="tog-lines" checked> Constellation filaments</label>
      <label><input type="checkbox" id="tog-modern" checked> Unmapped modern void figures</label>
      <label><input type="checkbox" id="tog-labels" checked> Star &amp; epoch labels</label>
      <label><input type="checkbox" id="tog-haze" checked> Horizon extinction haze (0°–8°)</label>
    </div>
  </div>
</div>
<figcaption>Southern celestial hemisphere in equal-area ecliptic projection centered on the South Ecliptic Pole (1,100+ real Hipparcos stars, V ≤ 5.0, cross-matched to Verbunt &amp; van Gent 2012). Drag the epoch slider or press <em>Orbit Precession</em> to move the South Celestial Pole along Earth's 25,772-year precession circle and watch how the dark never-rising horizon cap locks onto Ptolemy's empty blue void right around Hipparchus (Rhodes, 128 BCE) and Ptolemy (Alexandria, 137 CE)—and completely misses it at 3000 BCE or 9600 BCE. Hover any star to inspect its live maximum altitude.</figcaption>
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
    const w = Math.max(300, Math.round(rect.width));
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

  function render() {{
    const W = state.width;
    const cx = W / 2, cy = W / 2;
    const R = W * 0.455;
    const t = state.t, lat = state.lat;
    const dt = t - 1991.25;

    ctx.clearRect(0, 0, W, W);

    // Outer engraved brass astrolabe bezel
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, R + 12, 0, D2PI);
    ctx.strokeStyle = "rgba(207, 165, 68, 0.25)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Degree ticks around outer bezel
    for (let d = 0; d < 360; d += 5) {{
      const a = (d * Math.PI) / 180;
      const major = d % 30 === 0;
      const r0 = R + 2, r1 = R + (major ? 10 : 6);
      ctx.beginPath();
      ctx.moveTo(cx + r0 * Math.cos(a), cy + r0 * Math.sin(a));
      ctx.lineTo(cx + r1 * Math.cos(a), cy + r1 * Math.sin(a));
      ctx.strokeStyle = major ? "rgba(218, 178, 92, 0.55)" : "rgba(218, 178, 92, 0.2)";
      ctx.lineWidth = major ? 1.2 : 0.7;
      ctx.stroke();
    }}

    // Clip to celestial dome disc
    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, D2PI);
    const domeGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, R);
    domeGrad.addColorStop(0, "#121b30");
    domeGrad.addColorStop(0.6, "#0c1324");
    domeGrad.addColorStop(1, "#070b15");
    ctx.fillStyle = domeGrad;
    ctx.fill();
    ctx.clip();

    // Subtle ecliptic latitude graticule rings (-60, -30, 0 deg)
    ctx.strokeStyle = "rgba(180, 198, 228, 0.08)";
    ctx.lineWidth = 0.8;
    for (const beta of [-60, -30, 0]) {{
      const colat = ((90 + beta) * Math.PI) / 180;
      const rRing = R * ((2 * Math.sin(colat / 2)) / MAX_R_PROJ);
      ctx.beginPath();
      ctx.arc(cx, cy, rRing, 0, D2PI);
      ctx.stroke();
    }}
    // Radial spokes every 30 deg ecliptic longitude
    for (let k = 0; k < 12; k++) {{
      const a = (k * Math.PI) / 6;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + R * Math.cos(a), cy + R * Math.sin(a));
      ctx.stroke();
    }}

    // Soft ethereal Milky Way ribbon
    ctx.save();
    for (let i = 0; i < DATA.milkyWay.length; i++) {{
      const m = DATA.milkyWay[i];
      const [mx, my, mr] = eqToProj(m[0], m[1], m[2], cx, cy, R);
      if (mr < 1.15) {{
        const g = ctx.createRadialGradient(mx, my, 0, mx, my, R * 0.14);
        g.addColorStop(0, "rgba(176, 198, 240, 0.055)");
        g.addColorStop(1, "rgba(176, 198, 240, 0)");
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(mx, my, R * 0.14, 0, D2PI);
        ctx.fill();
      }}
    }}
    ctx.restore();

    // Compute South Celestial Pole at epoch t
    const pN = ltpequ(t);
    const pS = [-pN[0], -pN[1], -pN[2]];
    const [scpX, scpY] = eqToProj(pS[0], pS[1], pS[2], cx, cy, R);

    // Draw Horizon Extinction Haze Ring (lat to lat + 8 deg around SCP)
    if (togHaze.checked) {{
      const hazePts = drawCircleOnSphere(pS, ((lat + 8.0) * Math.PI) / 180, cx, cy, R);
      ctx.beginPath();
      hazePts.forEach((p, idx) => idx === 0 ? ctx.moveTo(p[0], p[1]) : ctx.lineTo(p[0], p[1]));
      ctx.closePath();
      ctx.fillStyle = "rgba(198, 118, 66, 0.085)";
      ctx.fill();
      ctx.setLineDash([3, 4]);
      ctx.strokeStyle = "rgba(224, 134, 82, 0.32)";
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.setLineDash([]);
    }}

    // Draw Dark Invisible Southern Horizon Cap (angular radius = lat around SCP)
    const horPts = drawCircleOnSphere(pS, (lat * Math.PI) / 180, cx, cy, R);
    ctx.beginPath();
    horPts.forEach((p, idx) => idx === 0 ? ctx.moveTo(p[0], p[1]) : ctx.lineTo(p[0], p[1]));
    ctx.closePath();
    const capGrad = ctx.createRadialGradient(scpX, scpY, 0, scpX, scpY, R * 0.45);
    capGrad.addColorStop(0, "rgba(4, 7, 15, 0.72)");
    capGrad.addColorStop(0.85, "rgba(8, 12, 24, 0.56)");
    capGrad.addColorStop(1, "rgba(224, 134, 82, 0.14)");
    ctx.fillStyle = capGrad;
    ctx.fill();
    ctx.strokeStyle = "#e08652";
    ctx.lineWidth = 2;
    ctx.shadowColor = "rgba(224, 134, 82, 0.65)";
    ctx.shadowBlur = 10;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Precession circle track (25,772 yrs)
    ctx.beginPath();
    precTrack.forEach((pt, idx) => {{
      const [px, py] = eqToProj(pt[0], pt[1], pt[2], cx, cy, R);
      if (idx === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }});
    ctx.closePath();
    ctx.setLineDash([4, 4]);
    ctx.strokeStyle = "rgba(218, 178, 92, 0.52)";
    ctx.lineWidth = 1.25;
    ctx.stroke();
    ctx.setLineDash([]);

    // Milestone jewels on precession circle
    if (togLabels.checked) {{
      ctx.font = "500 9.5px " + getComputedStyle(document.body).getPropertyValue("--mono");
      milestonePoles.forEach(m => {{
        const [mx, my] = eqToProj(m.u[0], m.u[1], m.u[2], cx, cy, R);
        ctx.beginPath();
        ctx.arc(mx, my, 2.5, 0, D2PI);
        ctx.fillStyle = "rgba(218, 178, 92, 0.78)";
        ctx.fill();
        ctx.fillStyle = "rgba(228, 200, 140, 0.78)";
        ctx.fillText(m.lbl, mx + 6, my + 3);
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

    // Draw Classical Ptolemy constellation filaments
    if (togLines.checked) {{
      ctx.strokeStyle = "rgba(240, 195, 108, 0.32)";
      ctx.lineWidth = 1.05;
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

    // Draw Unmapped post-1600 southern constellation outlines (inside void)
    if (togModern.checked) {{
      ctx.save();
      ctx.setLineDash([2.5, 3.5]);
      ctx.strokeStyle = "rgba(118, 186, 250, 0.30)";
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

    // Draw Stars (golden/warm for Ptolemy, sapphire-blue for uncatalogued)
    for (let i = 0; i < DATA.stars.length; i++) {{
      const s = DATA.stars[i];
      const [sx, sy, hMax, sr] = starXY[i];
      if (sr > 1.01) continue;
      const vmag = s[6], isCat = s[7] === 1;
      const rad = Math.max(0.85, Math.min(4.8, (5.5 - vmag) * 0.72));

      if (isCat) {{
        if (vmag < 2.2) {{
          const halo = ctx.createRadialGradient(sx, sy, 0, sx, sy, rad * 3.8);
          halo.addColorStop(0, "rgba(248, 212, 128, 0.55)");
          halo.addColorStop(1, "rgba(248, 212, 128, 0)");
          ctx.fillStyle = halo;
          ctx.beginPath();
          ctx.arc(sx, sy, rad * 3.8, 0, D2PI);
          ctx.fill();
        }}
        ctx.fillStyle = vmag < 2.8 ? "#fae0a2" : "#e3b462";
        ctx.globalAlpha = vmag < 3.5 ? 0.96 : 0.74;
        ctx.beginPath();
        ctx.arc(sx, sy, rad, 0, D2PI);
        ctx.fill();
      }} else {{
        if (vmag < 2.5) {{
          const halo = ctx.createRadialGradient(sx, sy, 0, sx, sy, rad * 3.4);
          halo.addColorStop(0, "rgba(114, 185, 255, 0.48)");
          halo.addColorStop(1, "rgba(114, 185, 255, 0)");
          ctx.fillStyle = halo;
          ctx.beginPath();
          ctx.arc(sx, sy, rad * 3.4, 0, D2PI);
          ctx.fill();
        }}
        ctx.fillStyle = vmag < 3.2 ? "#8ccbff" : "#5b8ec4";
        ctx.globalAlpha = vmag < 3.5 ? 0.92 : 0.45;
        ctx.beginPath();
        ctx.arc(sx, sy, rad * 0.92, 0, D2PI);
        ctx.fill();
      }}
    }}
    ctx.globalAlpha = 1;

    // Key landmark star labels
    if (togLabels.checked) {{
      const keyHips = new Set([30438, 60718, 71681, 7588, 13847, 109268, 2081, 45238, 100751, 82273, 85267, 80763, 32349, 113368]);
      ctx.font = "italic 10.5px " + getComputedStyle(document.body).getPropertyValue("--serif");
      for (let i = 0; i < DATA.stars.length; i++) {{
        const s = DATA.stars[i];
        if (!keyHips.has(s[12])) continue;
        const [sx, sy, , sr] = starXY[i];
        if (sr > 0.96) continue;
        ctx.fillStyle = s[7] === 1 ? "rgba(252, 232, 184, 0.88)" : "rgba(148, 206, 255, 0.86)";
        ctx.fillText(s[9].split(" (")[0], sx + 6, sy - 4);
      }}
    }}

    // Active South Celestial Pole glowing compass star
    ctx.save();
    ctx.strokeStyle = "#f8d483";
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.moveTo(scpX - 7, scpY); ctx.lineTo(scpX + 7, scpY);
    ctx.moveTo(scpX, scpY - 7); ctx.lineTo(scpX, scpY + 7);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(scpX, scpY, 4.2, 0, D2PI);
    ctx.fillStyle = "#e08652";
    ctx.fill();
    ctx.strokeStyle = "#fff3d1";
    ctx.lineWidth = 1.2;
    ctx.stroke();
    ctx.font = "600 9.5px " + getComputedStyle(document.body).getPropertyValue("--mono");
    ctx.fillStyle = "#f9dfb0";
    ctx.fillText("SCP", scpX + 8, scpY - 6);
    ctx.restore();

    // Hover reticle
    if (state.hoverIdx >= 0) {{
      const [hx, hy] = starXY[state.hoverIdx];
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1.3;
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

    hudDll.textContent = (dll > -0.1 ? "0.0 (peak)" : dll.toFixed(1));
    hudDll.className = "sky-hud-val " + (dll > -6 ? "is-good" : dll < -30 ? "is-bad" : "");
  }}

  function setEpochLat(t, lat) {{
    state.t = t;
    state.lat = lat;
    epSlider.value = String(t);
    latSlider.value = String(lat);
    presetBtns.forEach(b => {{
      const bt = Number(b.dataset.t), bl = Number(b.dataset.lat);
      b.classList.toggle("is-active", Math.abs(bt - t) < 35 && Math.abs(bl - lat) < 0.4);
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
    playBtn.innerHTML = "&#9654; Orbit Precession";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = null;
  }}

  playBtn.addEventListener("click", () => {{
    if (state.playing) {{
      stopPlay();
      return;
    }}
    state.playing = true;
    playBtn.innerHTML = "&#9646;&#9646; Pause Orbit";
    if (state.t >= 1950) state.t = -10000;
    function step() {{
      if (!state.playing) return;
      state.t += 45;
      if (state.t > 2000) state.t = -10000;
      epSlider.value = String(Math.round(state.t));
      presetBtns.forEach(b => b.classList.remove("is-active"));
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
      const visTxt = hMax > 0 ? ("+" + hMax.toFixed(1) + "° above horizon") : (hMax.toFixed(1) + "° (never rises)");
      tip.innerHTML =
        '<div class="sky-tip-name">' + s[9] + (s[10] && s[10] !== s[9] ? ' <span style="opacity:.65;font-size:11px">(' + s[10] + ')</span>' : '') + '</div>' +
        '<div class="sky-tip-tag ' + (isCat ? 'is-cat' : 'is-void') + '">' + (isCat ? ('Almagest · ' + s[11]) : 'Uncatalogued Void') + '</div>' +
        '<div class="sky-tip-meta">V = ' + s[6].toFixed(2) + ' mag · HIP ' + s[12] + '<br>Max alt: <strong style="color:' + (hMax > 0 ? '#f4cf82' : '#7ec2ff') + '">' + visTxt + '</strong></div>';
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
            {"id": "v40", "lbl": "Bright stars (V≤4.0)", "t": -120, "lat": 31.8, "col": "#7fe3bc"},
            {"id": "v45", "lbl": "Stars (V≤4.5)", "t": 50, "lat": 30.3, "col": "#7fe3bc"},
            {"id": "m2", "lbl": "M2 Free k_V (0.10)", "t": 160, "lat": 35.7, "col": "#f7d47c"},
            {"id": "kv15", "lbl": "Clear sky (k_V=0.15)", "t": 210, "lat": 33.2, "col": "#f7d47c"},
            {"id": "m1", "lbl": "Primary M1 (k_V=0.25)", "t": 910, "lat": 25.8, "col": "#ee825b"},
        ],
        "m3Epoch": summary["m3_geometric_cap"]["epoch"],
    }
    payload_json = json.dumps(payload, separators=(",", ":"))

    return f"""<figure class="fig sky-contour-fig" id="sky-likelihood-map">
<style>
.sky-contour-fig {{ margin: 2.2rem 0 2.6rem; }}
.con-plate {{
  background: linear-gradient(180deg, #101626 0%, #090d18 100%);
  border: 1px solid rgba(207, 165, 68, 0.34);
  border-radius: 6px;
  color: #f3ecdf;
  overflow: hidden;
  box-shadow: 0 18px 46px rgba(12, 10, 8, 0.24);
}}
.con-head {{
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  gap: 0.65rem 1rem;
  padding: 1rem 1.35rem 0.85rem;
  border-bottom: 1px solid rgba(207, 165, 68, 0.18);
}}
.con-tabs {{ display: flex; flex-wrap: wrap; gap: 0.38rem; }}
.con-tab {{
  font: 500 11px/1.2 var(--mono); padding: 0.38rem 0.68rem; border-radius: 3px; cursor: pointer;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(207,165,68,0.22); color: #cfc3ad;
}}
.con-tab:hover {{ border-color: rgba(207,165,68,0.6); color: #fff4da; }}
.con-tab.is-active {{ background: rgba(207,165,68,0.24); border-color: #e6ba63; color: #fff4da; }}
.con-legend {{
  display: flex; flex-wrap: wrap; gap: 0.45rem 1.2rem; align-items: center;
  padding: 0.55rem 1.35rem 0.2rem;
  font: 400 11px/1.3 var(--sans); color: #b7c2d6;
}}
.con-leg-i {{ display: inline-flex; align-items: center; gap: 0.38rem; }}
.con-dia {{ width: 8px; height: 8px; display: inline-block; transform: rotate(45deg); }}
.con-canvas-wrap {{ position: relative; padding: 0.5rem 1rem 0.4rem; }}
.con-canvas-wrap canvas {{ display: block; width: 100%; height: 390px; cursor: crosshair; }}
.con-bar {{
  display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;
  gap: 0.5rem 1.2rem;
  padding: 0.65rem 1.35rem 0.9rem;
  border-top: 1px solid rgba(207, 165, 68, 0.16);
  background: rgba(7, 10, 18, 0.72);
  font: 400 11.5px/1.4 var(--mono); color: #b8c4d8;
}}
.con-bar strong {{ color: #f6d483; }}
.con-right-tools {{ display: flex; flex-wrap: wrap; gap: 0.8rem; align-items: center; }}
.con-right-tools label {{ display: inline-flex; align-items: center; gap: 0.35rem; cursor: pointer; }}
.con-right-tools input {{ accent-color: #e6ba63; }}
</style>
<div class="con-plate">
  <div class="con-head">
    <div>
      <p class="sky-eyebrow" style="margin-bottom:.2rem">Locked 2D Likelihood Surface · Epoch × Latitude</p>
      <h3 class="sky-title">Where the Empty Patch Points — and Where Extinction Pulls It</h3>
    </div>
    <div class="con-tabs" id="con-tabs">
      <button type="button" class="con-tab is-active" data-grid="kv015">Clear Sky (k_V=0.15)</button>
      <button type="button" class="con-tab" data-grid="kv025">Primary M1 (k_V=0.25)</button>
      <button type="button" class="con-tab" data-grid="aratus">Aratus Core</button>
      <button type="button" class="con-tab" data-grid="infig">In-Figure Only</button>
    </div>
  </div>
  <div class="con-legend">
    <span class="con-leg-i"><i class="con-dia" style="background:#7fe3bc"></i>Bright stars (V≤4.0 / 4.5)</span>
    <span class="con-leg-i"><i class="con-dia" style="background:#f7d47c"></i>M2 free k_V &amp; Clear sky (k_V=0.15)</span>
    <span class="con-leg-i"><i class="con-dia" style="background:#ee825b"></i>Primary M1 overshoot (k_V=0.25)</span>
    <span class="con-leg-i"><span style="display:inline-block;width:13px;border-top:1.5px dotted #7fe3bc"></span>M3 geometric cap (41 BCE)</span>
    <span class="con-leg-i"><span style="display:inline-block;width:13px;border-top:1.5px dashed #e87856"></span>3000 BCE threshold</span>
  </div>
  <div class="con-canvas-wrap">
    <canvas id="con-canvas" aria-label="Interactive 2D log-likelihood heatmap across epoch and observer latitude showing 3000 BCE threshold, historical sites, and pre-registered model peaks."></canvas>
  </div>
  <div class="con-bar">
    <div id="con-hover-out">Hover anywhere on the map to inspect exact <strong>Δln L</strong> vs. peak.</div>
    <div class="con-right-tools">
      <label><input type="checkbox" id="con-deep"> Deep time (10,000 BCE–1000 CE)</label>
      <label><input type="checkbox" id="con-boot" checked> 500 block-bootstrap draws (M1)</label>
    </div>
  </div>
</div>
<figcaption>Exact locked log-likelihood surface across observer latitude (15°–45° N) and epoch. Bright gold regions mark high likelihood; dark indigo regions are ruled out by orders of magnitude. Switch between <em>Clear Sky (k_V = 0.15)</em>—which peaks cleanly on Classical Antiquity (210 CE, 33.2° N) right beside Hipparchus's Rhodes and Ptolemy's Alexandria—and <em>Primary M1 (k_V = 0.25)</em>, where harsh faint-star horizon extinction pulls the peak into the shaded anachronistic zone after 137 CE (910 CE, 25.8° N). Across every model and all 500 bootstrap resamples, 3000 BCE (vertical crimson line) lies deep in the rejected dark zone (Δln L ≤ −96).</figcaption>
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

  // Celestial magma-gold colormap for dLL in [-140, 0]
  function colorForDLL(dll) {{
    const u = Math.max(0, Math.min(1, 1 - Math.sqrt(Math.max(0, -dll) / 140)));
    const stops = [
      [0.00, 7, 11, 22],
      [0.35, 22, 37, 74],
      [0.62, 92, 52, 72],
      [0.82, 198, 102, 56],
      [0.94, 244, 196, 98],
      [1.00, 255, 245, 212]
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
    return [255, 245, 212];
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
    W = Math.max(320, Math.round(rect.width - 32));
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
      {{ v: -3.0, col: "rgba(255, 246, 214, 0.85)", w: 1.4 }},
      {{ v: -15.0, col: "rgba(244, 196, 98, 0.45)", w: 1.0 }},
      {{ v: -50.0, col: "rgba(218, 128, 78, 0.35)", w: 0.9 }}
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

    // Shaded "After Almagest (> 137 CE)" anachronism zone
    const x137 = xOf(137);
    ctx.fillStyle = "rgba(10, 12, 20, 0.38)";
    ctx.fillRect(x137, PAD.t, PAD.l + pw - x137, ph);
    ctx.save();
    ctx.setLineDash([3, 3]);
    ctx.strokeStyle = "rgba(255, 255, 255, 0.42)";
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(x137, PAD.t); ctx.lineTo(x137, PAD.t + ph); ctx.stroke();
    ctx.restore();
    ctx.font = "500 9.5px " + getComputedStyle(document.body).getPropertyValue("--mono");
    ctx.fillStyle = "rgba(235, 224, 204, 0.72)";
    ctx.fillText("After Almagest (137 CE)", Math.min(PAD.l + pw - 128, x137 + 6), PAD.t + 14);

    // Vertical 3000 BCE threshold line
    const x3000 = xOf(-2999);
    if (x3000 > PAD.l && x3000 < PAD.l + pw) {{
      ctx.save();
      ctx.setLineDash([5, 4]);
      ctx.strokeStyle = "#e87856";
      ctx.lineWidth = 1.6;
      ctx.beginPath(); ctx.moveTo(x3000, PAD.t); ctx.lineTo(x3000, PAD.t + ph); ctx.stroke();
      ctx.restore();
      ctx.fillStyle = "#f29b7e";
      ctx.fillText("3000 BCE threshold", x3000 + 6, PAD.t + 14);
    }}

    // M3 geometric cap vertical band (41 BCE)
    const xm3 = xOf(D.m3Epoch);
    ctx.save();
    ctx.setLineDash([2, 3]);
    ctx.strokeStyle = "rgba(127, 227, 188, 0.65)";
    ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.moveTo(xm3, PAD.t); ctx.lineTo(xm3, PAD.t + ph); ctx.stroke();
    ctx.restore();

    // 500 Spatial Block Bootstrap draws (for Primary M1)
    if (bootBox.checked) {{
      ctx.fillStyle = "rgba(255, 240, 195, 0.28)";
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
    ctx.font = "500 10px " + getComputedStyle(document.body).getPropertyValue("--sans");
    sites.forEach(s => {{
      const sx = xOf(s.t), sy = yOf(s.lat);
      if (sx < PAD.l || sx > PAD.l + pw) return;
      ctx.beginPath(); ctx.arc(sx, sy, 4, 0, Math.PI * 2);
      ctx.fillStyle = "#0b0f1b"; ctx.fill();
      ctx.strokeStyle = "#f4e6c4"; ctx.lineWidth = 1.6; ctx.stroke();
      ctx.fillStyle = "#f4e6c4";
      ctx.fillText(s.lbl, sx + s.dx, sy + s.dy);
    }});

    // Model peak diamonds (V<=4.0, M2, M1)
    D.variants.forEach(v => {{
      const vx = xOf(v.t), vy = yOf(v.lat);
      if (vx < PAD.l || vx > PAD.l + pw) return;
      ctx.save();
      ctx.translate(vx, vy);
      ctx.rotate(Math.PI / 4);
      ctx.fillStyle = v.col;
      ctx.strokeStyle = "#090d18";
      ctx.lineWidth = 1.4;
      ctx.fillRect(-4.5, -4.5, 9, 9);
      ctx.strokeRect(-4.5, -4.5, 9, 9);
      ctx.restore();
    }});

    // Axes frame and ticks
    ctx.strokeStyle = "rgba(207, 165, 68, 0.35)";
    ctx.lineWidth = 1;
    ctx.strokeRect(PAD.l, PAD.t, pw, ph);

    ctx.font = "400 10.5px " + getComputedStyle(document.body).getPropertyValue("--mono");
    ctx.fillStyle = "#b9c4d6";
    ctx.textAlign = "center";
    const xTicks = deepBox.checked ? [-10000, -8000, -6000, -4000, -2000, 0, 1000] : [-4000, -3000, -2000, -1000, 0, 1000];
    xTicks.forEach(tx => {{
      const x = xOf(tx);
      ctx.beginPath(); ctx.moveTo(x, PAD.t + ph); ctx.lineTo(x, PAD.t + ph + 5); ctx.stroke();
      ctx.fillText(tx === 0 ? "1 BCE" : (tx < 0 ? (-tx) + " BCE" : tx + " CE"), x, PAD.t + ph + 18);
    }});
    ctx.fillStyle = "#9aa7bd";
    ctx.fillText("Epoch (Precession Date)", PAD.l + pw / 2, H - 6);

    ctx.textAlign = "right";
    for (let ly = 15; ly <= 45; ly += 5) {{
      const y = yOf(ly);
      ctx.beginPath(); ctx.moveTo(PAD.l - 5, y); ctx.lineTo(PAD.l, y); ctx.stroke();
      ctx.fillStyle = "#b9c4d6";
      ctx.fillText(ly + "°N", PAD.l - 8, y + 3.5);
    }}
    ctx.textAlign = "left";

    // Hover crosshair
    if (hoverPt) {{
      const hx = xOf(hoverPt.t), hy = yOf(hoverPt.lat);
      ctx.save();
      ctx.strokeStyle = "rgba(255, 255, 255, 0.55)";
      ctx.lineWidth = 0.9;
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
      tabs.forEach(t => t.classList.toggle("is-active", t === tab));
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
      hoverOut.innerHTML = 'Hover anywhere on the map to inspect exact <strong>Δln L</strong> vs. peak.';
      render();
      return;
    }}
    const tMin = deepBox.checked ? -10000 : -4000;
    const t = tMin + ((mx - PAD.l) / pw) * (1000 - tMin);
    const lat = 45 - ((my - PAD.t) / ph) * 30;
    const dll = interpGrid(D.grids[activeKey], t, lat);
    const log10Odds = (-dll / Math.LN10);
    const oddsStr = log10Odds < 0.15 ? "≈ peak" : (log10Odds < 3 ? ("1 in " + Math.round(Math.pow(10, log10Odds)).toLocaleString()) : ("1 in 10^" + log10Odds.toFixed(1)));
    hoverPt = {{ t, lat }};
    hoverOut.innerHTML = '<strong>' + fmtYear(t) + ' · ' + lat.toFixed(1) + '° N</strong> &nbsp;|&nbsp; Δln L = <strong>' + dll.toFixed(1) + '</strong> &nbsp;(' + oddsStr + ' vs. peak)';
    render();
  }});
  canvas.addEventListener("mouseleave", () => {{
    hoverPt = null;
    hoverOut.innerHTML = 'Hover anywhere on the map to inspect exact <strong>Δln L</strong> vs. peak.';
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
    # Curated 12 southernmost bright Ptolemy stars vs 12 brightest missing southern stars
    ptol_hips = [30438, 60718, 71681, 68702, 85267, 62434, 85258, 83081, 59747, 42913, 45941, 13847]
    miss_hips = [7588, 45238, 109268, 41037, 82273, 100751, 112122, 45556, 2081, 61585, 52419, 110130]

    hip_idx = {int(h): i for i, h in enumerate(cat["hip"])}
    stars_out = []
    for grp, hlist in ((1, ptol_hips), (0, miss_hips)):
        for hid in hlist:
            i = hip_idx[hid]
            u = cat["u0"][i]
            v = cat["vel"][i]
            label = COMMON_NAMES.get(hid, str(cat["name"][i])).split(" (")[0]
            cst = CST_FULL.get(str(cat["cst"][i]), "") if grp == 1 else "Void"
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
.sky-rim-fig {{ margin: 2.2rem 0 2.6rem; }}
.rim-plate {{
  background: linear-gradient(180deg, #101627 0%, #090d17 100%);
  border: 1px solid rgba(207, 165, 68, 0.34);
  border-radius: 6px;
  color: #f3ecdf;
  overflow: hidden;
  box-shadow: 0 18px 46px rgba(12, 10, 8, 0.24);
}}
.rim-head {{
  display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between;
  gap: 0.5rem 1rem;
  padding: 1rem 1.35rem 0.8rem;
  border-bottom: 1px solid rgba(207, 165, 68, 0.18);
}}
.rim-score {{
  font: 500 11.5px/1.35 var(--mono); color: #d8cdb8;
  background: rgba(8, 11, 19, 0.72); border: 1px solid rgba(207, 165, 68, 0.28);
  padding: 0.35rem 0.75rem; border-radius: 999px;
}}
.rim-score strong {{ color: #8ad3b5; }}
.rim-canvas-wrap {{ position: relative; padding: 0.6rem 1rem 0.3rem; }}
.rim-canvas-wrap canvas {{ display: block; width: 100%; height: 340px; }}
.rim-controls {{
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  gap: 0.6rem 1rem;
  padding: 0.75rem 1.35rem 1rem;
  border-top: 1px solid rgba(207, 165, 68, 0.16);
  background: rgba(7, 10, 18, 0.72);
}}
.rim-presets {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
.rim-btn {{
  font: 400 11.5px/1.25 var(--sans); padding: 0.36rem 0.66rem; border-radius: 3px; cursor: pointer;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(207,165,68,0.22); color: #d6cbb7;
}}
.rim-btn:hover {{ border-color: rgba(207,165,68,0.6); color: #fff4da; }}
.rim-btn.is-active {{ background: rgba(207,165,68,0.24); border-color: #e6ba63; color: #fff4da; font-weight: 500; }}
</style>
<div class="rim-plate">
  <div class="rim-head">
    <div>
      <p class="sky-eyebrow" style="margin-bottom:.2rem">Horizon Forensics · 24 Landmark Rim Stars</p>
      <h3 class="sky-title">Fingerprints on the Horizon: Catalogued vs. Missing Stars</h3>
    </div>
    <div class="rim-score" id="rim-score">—</div>
  </div>
  <div class="rim-canvas-wrap">
    <canvas id="rim-canvas" aria-label="Interactive horizon elevation profile comparing the 12 southernmost Ptolemy stars against the 12 brightest missing southern stars across ancient sites and epochs."></canvas>
  </div>
  <div class="rim-controls">
    <div class="rim-presets" id="rim-presets">
      <button type="button" class="rim-btn is-active" data-t="-127" data-lat="36.4">Rhodes · 128 BCE (Hipparchus)</button>
      <button type="button" class="rim-btn" data-t="137" data-lat="31.2">Alexandria · 137 CE (Ptolemy)</button>
      <button type="button" class="rim-btn" data-t="-1099" data-lat="32.5">Babylon · 1100 BCE</button>
      <button type="button" class="rim-btn" data-t="-2599" data-lat="35.3">Crete · 2600 BCE</button>
      <button type="button" class="rim-btn" data-t="-9599" data-lat="37.2">Göbekli Tepe · 9600 BCE</button>
    </div>
  </div>
</div>
<figcaption>Maximum southern culmination altitude (degrees above or below the sea horizon) for the 12 southernmost bright stars Ptolemy catalogued (gold circles) versus the 12 brightest southern stars Ptolemy omitted (sapphire diamonds), ordered by Right Ascension. At <strong>Rhodes in 128 BCE</strong>, all 12 catalogued stars rise cleanly above 0° while 11 of 12 missing stars sit below the horizon (only Avior grazes +0.01°). At <strong>Alexandria in 137 CE</strong>, four bright missing stars—Ankaa (+6.4°), Avior (+4.6°), Alnair (+4.5°), and Tiaki (+3.4°)—stand clearly in the sky yet remain uncatalogued. At <strong>2600 BCE</strong> or <strong>9600 BCE</strong>, the two groups scramble completely across the horizon.</figcaption>
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
    W = Math.max(320, Math.round(rect.width - 32));
    H = W < 500 ? 310 : 340;
    canvas.style.height = H + "px";
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    render();
  }}

  function render() {{
    const pw = W - PAD.l - PAD.r, ph = H - PAD.t - PAD.b;
    const yMin = -28, yMax = 32;
    const xOf = ra => PAD.l + (ra / 360) * pw;
    const yOf = h => PAD.t + ((yMax - Math.max(yMin, Math.min(yMax, h))) / (yMax - yMin)) * ph;

    ctx.clearRect(0, 0, W, H);

    // Sky above horizon gradient vs underground dark earth below 0 deg
    const y0 = yOf(0);
    const skyG = ctx.createLinearGradient(0, PAD.t, 0, y0);
    skyG.addColorStop(0, "#101a32");
    skyG.addColorStop(0.75, "#172038");
    skyG.addColorStop(1, "rgba(180, 108, 62, 0.22)");
    ctx.fillStyle = skyG;
    ctx.fillRect(PAD.l, PAD.t, pw, y0 - PAD.t);

    // Twilight haze band (0 to +6 deg)
    const y6 = yOf(6);
    ctx.fillStyle = "rgba(224, 134, 82, 0.08)";
    ctx.fillRect(PAD.l, y6, pw, y0 - y6);

    // Below-horizon earth/void fill
    ctx.fillStyle = "rgba(5, 8, 15, 0.78)";
    ctx.fillRect(PAD.l, y0, pw, PAD.t + ph - y0);

    // Horizontal grid lines
    ctx.font = "400 10px " + getComputedStyle(document.body).getPropertyValue("--mono");
    ctx.textAlign = "right";
    for (const h of [-20, -10, 0, 10, 20, 30]) {{
      const y = yOf(h);
      ctx.beginPath(); ctx.moveTo(PAD.l, y); ctx.lineTo(PAD.l + pw, y);
      ctx.strokeStyle = h === 0 ? "#e08652" : "rgba(255,255,255,0.08)";
      ctx.lineWidth = h === 0 ? 2 : 1;
      ctx.stroke();
      ctx.fillStyle = h === 0 ? "#f2a472" : "#8f9db3";
      ctx.fillText((h > 0 ? "+" : "") + h + "°", PAD.l - 7, y + 3.5);
    }}
    ctx.textAlign = "left";
    ctx.fillStyle = "rgba(242, 164, 114, 0.85)";
    ctx.fillText("SEA HORIZON (0°)", PAD.l + 8, y0 - 6);
    ctx.fillStyle = "rgba(130, 185, 245, 0.55)";
    ctx.fillText("NEVER RISES BELOW HORIZON", PAD.l + 8, y0 + 14);

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

      // Vertical stem to horizon
      ctx.beginPath(); ctx.moveTo(sx, y0); ctx.lineTo(sx, sy);
      ctx.strokeStyle = s.cat === 1 ? "rgba(244, 198, 102, 0.28)" : "rgba(116, 186, 255, 0.25)";
      ctx.lineWidth = 1;
      ctx.stroke();

      if (s.cat === 1) {{
        ctx.beginPath(); ctx.arc(sx, sy, rad, 0, D2PI);
        ctx.fillStyle = hMax > 0 ? "#f6cf7c" : "#e86e4c";
        ctx.fill();
        ctx.strokeStyle = "#0a0e1a"; ctx.lineWidth = 1.2; ctx.stroke();
      }} else {{
        ctx.save(); ctx.translate(sx, sy); ctx.rotate(Math.PI / 4);
        ctx.fillStyle = hMax <= 0.1 ? "#74baff" : "#ff9468";
        ctx.fillRect(-rad * 0.85, -rad * 0.85, rad * 1.7, rad * 1.7);
        ctx.strokeStyle = "#0a0e1a"; ctx.lineWidth = 1.1;
        ctx.strokeRect(-rad * 0.85, -rad * 0.85, rad * 1.7, rad * 1.7);
        ctx.restore();
      }}

      // Clean non-cluttered labels for prominent stars
      const showLbl = W > 480 ? (s.vmag < 2.95 || s.hip === 85267 || s.hip === 13847) : (s.vmag < 2.2 || s.hip === 2081);
      if (showLbl) {{
        ctx.font = "500 9.5px " + getComputedStyle(document.body).getPropertyValue("--sans");
        ctx.fillStyle = s.cat === 1 ? "#fae2ae" : "#9bd0ff";
        const dy = (idx % 2 === 0 ? -rad - 4 : rad + 11);
        const alignR = s.ra > 315;
        ctx.textAlign = alignR ? "right" : "left";
        ctx.fillText(s.name, sx + (alignR ? -6 : 6), sy + dy);
      }}
    }});

    // X-axis RA ticks
    ctx.strokeStyle = "rgba(207, 165, 68, 0.3)";
    ctx.lineWidth = 1;
    ctx.strokeRect(PAD.l, PAD.t, pw, ph);
    ctx.textAlign = "center";
    ctx.font = "400 10px " + getComputedStyle(document.body).getPropertyValue("--mono");
    ctx.fillStyle = "#9aa7bd";
    for (let hr = 0; hr <= 24; hr += 4) {{
      const x = xOf(hr * 15);
      ctx.fillText(hr + "h", x, PAD.t + ph + 16);
    }}
    ctx.fillText("Right Ascension (J2000)", PAD.l + pw / 2, H - 5);

    scoreEl.innerHTML = 'Ptolemy visible: <strong style="color:' + (catUp === 12 ? '#8ad3b5' : '#e88565') + '">' + catUp + '/12</strong> &nbsp;·&nbsp; Missing hidden: <strong style="color:' + (missDown >= 11 ? '#8ad3b5' : '#e88565') + '">' + missDown + '/12</strong>';
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
      btns.forEach(b => b.classList.toggle("is-active", b === btn));
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
    return """<div class="verdict">
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">Pre-registered test · Issue #85</p>
    <p class="verdict-text">Does the empty southern patch allow an origin before 3000 BCE?</p>
    <p class="verdict-note">Every one of all 13 locked models, all 21 leave-one-constellation-out runs, and all 500 spatial-block bootstrap draws falls after 201 BCE. A 3000 BCE sky is rejected by Δln L = −106.2 (odds &gt; 10<sup>46</sup> : 1).</p>
  </div>
  <p class="verdict-status is-no"><span class="dot" aria-hidden="true"></span>Excluded</p>
</div>
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">What the void actually records</p>
    <p class="verdict-text">Classical Greco-Alexandrian horizon (Hipparchus to Ptolemy, c. 130 BCE–140 CE)</p>
    <p class="verdict-note">Bright constellation skeletons (V ≤ 4.0: 121 BCE, 31.8° N), the extinction-free circular void (41 BCE, R = 41.7°), and free-extinction profile (160 CE, 35.7° N) converge on the era the catalogue was compiled.</p>
  </div>
  <p class="verdict-status is-yes"><span class="dot" aria-hidden="true"></span>Classical sky</p>
</div>
<div class="verdict-row">
  <div>
    <p class="verdict-kicker">Methodological stress test</p>
    <p class="verdict-text">Single-model extinction fits are fragile and can overshoot past 137 CE</p>
    <p class="verdict-note">Our locked primary model (k_V = 0.25, V ≤ 5.5) overshot to 910 CE (25.8° N)—773 years after the Almagest was written—because ancient observers recorded faint stars inside named southern figures while ignoring brighter stars in blank sky.</p>
  </div>
  <p class="verdict-status is-open"><span class="dot" aria-hidden="true"></span>Wide uncertainty</p>
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
