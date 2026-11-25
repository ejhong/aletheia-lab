"""Independent hillshade renderer (multi-direction, 2x VE) with candidate outlines and zoom panels."""
import sys, json, math, pathlib
import numpy as np
from PIL import Image, ImageDraw
A = pathlib.Path(sys.argv[1]); out = A / "out/hillshades"
s = json.load(open(A / "out/rerun_summary.json"))
recs = {t["id"]: t for t in s["tiles"]}
for r in s["calibration"]["real_breakwater_controls"]: recs[r["id"]] = r
def hs(z, v, az, alt=40, ve=2.0, px=2.0):
    zf = np.where(v, z, np.nanmedian(z[v]))
    gy, gx = np.gradient(zf * ve, px)
    slope = np.arctan(np.hypot(gx, gy)); aspect = np.arctan2(-gx, gy)
    a = math.radians(360 - az + 90); al = math.radians(alt)
    return np.sin(al) * np.cos(slope) + np.cos(al) * np.sin(slope) * np.cos(a - aspect)
def render(tid, zoom_px=90):
    z = np.array(Image.open(A / "work/questions/drowned-walls/data/bag_tiles" / f"{tid}.tif"), dtype=np.float64)
    v = np.isfinite(z) & (z > -1000) & (z < 5)
    h = np.mean([hs(z, v, a) for a in (315, 45, 270)], axis=0)
    g = np.clip((h - np.percentile(h[v], 1)) / (np.percentile(h[v], 99) - np.percentile(h[v], 1)), 0, 1)
    rgb = np.stack([g * 255] * 3, -1).astype(np.uint8); rgb[~v] = (120, 40, 40)
    im = Image.fromarray(rgb).resize((1024, 1024), Image.NEAREST); d = ImageDraw.Draw(im)
    cands = recs[tid]["candidates"]
    for i, c in enumerate(cands):
        x1, y1, x2, y2 = [q * 2 for q in c["px_endpoints"]]
        col = (255, 200, 0) if c["unmasked"] else (0, 200, 255)
        d.line([(x1, y1), (x2, y2)], fill=col, width=1)
        cx, cy = [q * 2 for q in c["px_centroid"]]
        d.text((cx + 6, cy + 6), str(i), fill=col)
    d.text((8, 8), f"{tid}  depth {np.nanmin(z[v]):.1f}..{np.nanmax(z[v]):.1f} m  yellow=unmasked cyan=flagged  2x VE multi-dir hillshade", fill=(255, 0, 255))
    im.save(out / f"{tid}_full.png")
    # zooms on up to 3 unmasked candidates
    for i, c in enumerate([c for c in cands if c["unmasked"]][:3]):
        cx, cy = [int(q) for q in c["px_centroid"]]
        r0, r1 = max(0, cy - zoom_px), min(512, cy + zoom_px); c0, c1 = max(0, cx - zoom_px), min(512, cx + zoom_px)
        sub = (rgb[r0:r1, c0:c1]); zi = Image.fromarray(sub).resize(((c1 - c0) * 4, (r1 - r0) * 4), Image.NEAREST)
        dz = ImageDraw.Draw(zi); x1, y1, x2, y2 = c["px_endpoints"]
        dz.line([((x1 - c0) * 4, (y1 - r0) * 4), ((x2 - c0) * 4, (y2 - r0) * 4)], fill=(255, 200, 0), width=1)
        dz.text((6, 6), f"{tid} cand L={c['length_m']} m maxBPI={c['max_bpi_m']} m z={c['mean_depth_m']} ({(c1-c0)*2} m wide view)", fill=(255, 0, 255))
        zi.save(out / f"{tid}_zoom{i}.png")
for tid in sys.argv[2:]:
    render(tid); print("rendered", tid)
