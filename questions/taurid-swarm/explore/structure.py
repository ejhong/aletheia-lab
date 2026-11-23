#!/usr/bin/env python3
"""Strictly blind structural check on NASA JPL SBDB NEO and CNEOS Fireball archives.

EXPLORATORY ONLY — inspects ONLY schema, row counts, missingness, 2P/Encke's
reference orbit, and global distributions. Never inspects Taurid longitude-of-perihelion
clustering, 7:2 resonance counts, or Taurid calendar/swarm-year fireball rates.
"""
import json
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def main():
    neos = json.loads((DATA / "jpl_neos.json").read_text(encoding="utf-8"))
    encke = json.loads((DATA / "jpl_encke.json").read_text(encoding="utf-8"))
    fb = json.loads((DATA / "cneos_fireballs.json").read_text(encoding="utf-8"))

    print("NEO fields:", neos["fields"])
    print("NEO count:", neos["count"], "rows:", len(neos["data"]))
    f_idx = {k: i for i, k in enumerate(neos["fields"])}

    # Global class & H availability
    cls_counts = Counter(r[f_idx["class"]] for r in neos["data"])
    h_vals = [float(r[f_idx["H"]]) for r in neos["data"] if r[f_idx["H"]] is not None]
    diam_n = sum(1 for r in neos["data"] if r[f_idx["diameter"]] is not None)
    print("NEO classes:", dict(cls_counts))
    print(f"NEO valid H: {len(h_vals)}/{len(neos['data'])}, H<=16.5: {sum(h<=16.5 for h in h_vals)}, "
          f"H<=18.0: {sum(h<=18.0 for h in h_vals)}, H<=20.0: {sum(h<=20.0 for h in h_vals)}, "
          f"H<=22.0: {sum(h<=22.0 for h in h_vals)}, with diameter: {diam_n}")

    # 2P/Encke reference orbit
    print("Encke:", encke["fields"], encke["data"])

    # Fireball schema, date span, energy completeness (NEVER breaking down by month or swarm year!)
    print("Fireball fields:", fb["fields"])
    print("Fireball count:", fb["count"], "rows:", len(fb["data"]))
    fb_idx = {k: i for i, k in enumerate(fb["fields"])}
    dates = sorted(r[fb_idx["date"]] for r in fb["data"] if r[fb_idx["date"]])
    ie_n = sum(1 for r in fb["data"] if r[fb_idx["impact-e"]] is not None)
    vel_n = sum(1 for r in fb["data"] if r[fb_idx["vel"]] is not None)
    yr_counts = Counter(d[:4] for d in dates)
    print(f"Fireball span: {dates[0]} to {dates[-1]}, valid impact-e: {ie_n}, valid vel: {vel_n}")
    print(f"Fireballs per year (min/med/max across {len(yr_counts)} yrs): "
          f"{min(yr_counts.values())}/{sorted(yr_counts.values())[len(yr_counts)//2]}/{max(yr_counts.values())}")
    print("Fireball pre-1994 years:", sorted((y, c) for y, c in yr_counts.items() if y < "1995"))


if __name__ == "__main__":
    main()
