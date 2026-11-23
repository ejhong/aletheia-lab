#!/usr/bin/env python3
"""Render the share images that appear when a page of the site is linked on X, Slack and the like.

    python3 scripts/make_cards.py            every card
    python3 scripts/make_cards.py NAME ...   only site/cards/NAME.html

Each site/cards/NAME.html is a 1200 by 630 page. This script screenshots it with a local headless Chrome into
site/assets/cards/NAME.png, which is committed: the site build only copies the PNGs, so CI needs no browser.
A question page uses the card named after its slug if there is one, and default.png otherwise.
"""
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "site" / "cards"
OUT = ROOT / "site" / "assets" / "cards"
CHROME = os.environ.get("CHROME") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def main(argv):
    names = argv or sorted(p.stem for p in SRC.glob("*.html"))
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        for name in names:
            out = OUT / (name + ".png")
            subprocess.run(
                [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--user-data-dir=" + profile,
                 "--force-device-scale-factor=1", "--window-size=1200,630", "--virtual-time-budget=5000",
                 "--screenshot=" + str(out), (SRC / (name + ".html")).as_uri()],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120, check=True)
            print(out.relative_to(ROOT), out.stat().st_size, "bytes")


if __name__ == "__main__":
    main(sys.argv[1:])
