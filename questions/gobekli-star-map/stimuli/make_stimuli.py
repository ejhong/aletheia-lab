"""Regenerate every picture in stimuli/ from the source folder, deterministically.

Usage:
    python stimuli/make_stimuli.py [--src ~/research-sources/gobekli-star-map/images]

Writes symbols/, asterisms_original/, figures/, symbols_512/, dummy/ next to this file
and prints SHA-256 of every output (README.md carries the same table).
Needs numpy and Pillow only (tested with numpy 2.3.5, Pillow 11.0.0).
"""
import argparse
import glob
import hashlib
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 512
MARGIN = 0.10  # white margin on each side of the line figures, as a fraction of the square side


def red_mask(rgb):
    """Pixels that belong to the red stick figure.

    Rule: R >= 110 and R - G >= 60 and R - B >= 50.
    Excludes the dark/brown sky background (R - G small), the faint blue lines (B > R),
    and the white rectangle in A01 (R = G = B)."""
    a = rgb.astype(np.int32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    return (R >= 110) & (R - G >= 60) & (R - B >= 50)


def pad_square(img, fill, margin=0.0):
    """Centre img on a white square canvas whose side gives `margin` on the longer axis."""
    w, h = img.size
    side = int(round(max(w, h) / (1 - 2 * margin)))
    canvas = Image.new(img.mode, (side, side), fill)
    canvas.paste(img, ((side - w) // 2, (side - h) // 2))
    return canvas


def line_figure(path):
    rgb = np.asarray(Image.open(path).convert("RGB"))
    m = red_mask(rgb)
    ys, xs = np.nonzero(m)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]  # crop to the figure itself
    gray = Image.fromarray(np.where(m, 0, 255).astype(np.uint8), "L")
    sq = pad_square(gray, 255, MARGIN)
    # Lanczos resample, then threshold at 128: lines stay pure black on pure white, edges smooth.
    big = np.asarray(sq.resize((SIZE, SIZE), Image.LANCZOS))
    return Image.fromarray(np.where(big < 128, 0, 255).astype(np.uint8), "L"), int(m.sum())


def symbol_512(path):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    s = SIZE / max(w, h)
    img = img.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    return pad_square(img, (255, 255, 255))


def dummies(outdir):
    os.makedirs(outdir, exist_ok=True)
    c, k = SIZE // 2, (0, 0, 0)

    def canvas():
        im = Image.new("RGB", (SIZE, SIZE), "white")
        return im, ImageDraw.Draw(im)

    def star(n=5, r1=200, r2=80):
        pts = []
        for i in range(2 * n):
            r = r1 if i % 2 == 0 else r2
            t = np.pi * i / n - np.pi / 2
            pts.append((c + r * np.cos(t), c + r * np.sin(t)))
        return pts

    shapes = {
        "D01": lambda d: d.ellipse([86, 86, 426, 426], fill=k),                       # circle
        "D02": lambda d: d.rectangle([106, 106, 406, 406], fill=k),                   # square
        "D03": lambda d: d.polygon([(256, 66), (446, 426), (66, 426)], fill=k),       # triangle
        "D04": lambda d: d.polygon(star(), fill=k),                                    # star
        "D05": lambda d: (d.rectangle([206, 76, 306, 436], fill=k),
                          d.rectangle([76, 206, 436, 306], fill=k)),                   # cross
        "D06": lambda d: (d.ellipse([76, 76, 436, 436], fill=k),
                          d.ellipse([156, 46, 496, 386], fill="white")),               # crescent
        "D07": lambda d: d.polygon([(66, 206), (296, 206), (296, 106), (446, 256),
                                    (296, 406), (296, 306), (66, 306)], fill=k),       # arrow
        "D08": lambda d: (d.ellipse([76, 76, 436, 436], fill=k),
                          d.ellipse([166, 166, 346, 346], fill="white")),              # ring
        "D09": lambda d: d.polygon([(126, 66), (226, 66), (226, 346), (406, 346),
                                    (406, 446), (126, 446)], fill=k),                  # L-shape
        "D10": lambda d: d.line([(56, 356), (146, 156), (236, 356), (326, 156),
                                 (416, 356), (466, 246)], fill=k, width=50, joint="curve"),  # zigzag
        "D11": lambda d: d.ellipse([56, 156, 456, 356], fill=k),                       # ellipse
        "D12": lambda d: d.polygon([(256, 56), (436, 256), (256, 456), (76, 256)], fill=k),  # diamond
    }
    for name, draw in shapes.items():
        im, d = canvas()
        draw(d)
        im.save(os.path.join(outdir, name + ".png"))

    lines = {
        "L01": [(256, 86), (436, 406), (76, 406), (256, 86)],                         # triangle outline
        "L02": [(66, 356), (156, 156), (246, 356), (336, 156), (426, 356)],           # zigzag
        "L03": [(c + 180 * np.cos(t), c + 180 * np.sin(t))
                for t in np.linspace(0, 2 * np.pi, 121)],                              # circle outline
    }
    for name, pts in lines.items():
        im = Image.new("L", (SIZE, SIZE), 255)
        ImageDraw.Draw(im).line(pts, fill=0, width=8, joint="curve")
        im.save(os.path.join(outdir, name + ".png"))


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, optimize=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.expanduser("~/research-sources/gobekli-star-map/images"))
    a = ap.parse_args()
    sym = sorted(glob.glob(os.path.join(a.src, "symbols", "S??_*.png")))
    ast = sorted(glob.glob(os.path.join(a.src, "asterisms", "A??_*.png")))
    assert len(sym) == 12 and len(ast) == 8, (len(sym), len(ast))
    for p in sym:
        sid = os.path.basename(p)[:3]
        os.makedirs(os.path.join(HERE, "symbols"), exist_ok=True)
        shutil.copyfile(p, os.path.join(HERE, "symbols", sid + ".png"))
        save(symbol_512(p), os.path.join(HERE, "symbols_512", sid + ".png"))
    for p in ast:
        aid = os.path.basename(p)[:3]
        os.makedirs(os.path.join(HERE, "asterisms_original"), exist_ok=True)
        shutil.copyfile(p, os.path.join(HERE, "asterisms_original", aid + ".png"))
        fig, n = line_figure(p)
        save(fig, os.path.join(HERE, "figures", aid + ".png"))
        print(f"{aid}: {n} red pixels kept")
    dummies(os.path.join(HERE, "dummy"))
    for sub in ("symbols", "asterisms_original", "figures", "symbols_512", "dummy"):
        for f in sorted(glob.glob(os.path.join(HERE, sub, "*.png"))):
            h = hashlib.sha256(open(f, "rb").read()).hexdigest()
            print(f"{h}  {sub}/{os.path.basename(f)}")


if __name__ == "__main__":
    main()
