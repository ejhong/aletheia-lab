#!/usr/bin/env python3
"""Generate the site illustrations with OpenAI's image API (stdlib only).

Usage: OPENAI_API_KEY=... python3 scripts/make_illustrations.py MODEL [name ...]
Saves raw PNGs to site/illustrations/raw/ (not in git). Prints token usage, never the key.

The pictures on the site were made on 2026-11-23 with gpt-image-2.6-sunburst and turned into JPEGs with
    sips -s format jpeg -s formatOptions 58 site/illustrations/raw/NAME.png --out site/assets/illustrations/NAME.jpg
A rerun gives different pictures; the committed JPEGs are the record. They are decoration and are labelled as
AI-made wherever they are shown. A topic page uses one by naming it in its front matter ("image: NAME").
"""
import base64, json, os, sys, urllib.request, urllib.error
from pathlib import Path

STYLE = ("A fine copperplate engraving in the manner of a nineteenth-century natural-history or astronomy plate. "
 "Dense cross-hatching and stipple, confident line work, generous empty margins. Printed on warm cream paper (#f6f1e8) "
 "in dark brown-black ink (#201b12) with a single sparing accent of copper-orange (#955730) and, at most, a touch of "
 "muted green (#47705f). Flat paper background, no frame, no border, no caption, no lettering, no numbers, no signature, "
 "no watermark. Wide landscape composition with the subject centred and calm space at the left and right edges. ")
SUBJECTS = {
 "younger-dryas": "A bright comet breaking into several fragments in the night sky above the edge of a vast ice sheet. Below, a tundra plain with three woolly mammoths small in the middle distance and low spruce trees. In the foreground at the right, a cylindrical ice core lying on its side, its fine annual layers visible, one thin layer picked out in copper.",
 "minds-and-machines": "On the left, a human head in profile drawn as a classical bust with the brain shown as a looped tangle of fine threads. On the right, an intricate brass calculating engine of gears and columns. Between them a single long ribbon that leaves the head as a closed loop and arrives at the machine unrolled into a straight chain of links. The ribbon is picked out in copper.",
 "ancient-crossings": "A double-hulled Polynesian voyaging canoe with a crab-claw sail on a wide open ocean at night, seen from a distance, under a sky dense with stars and the band of the Milky Way. Its wake trails behind as a faint twisted double strand like a strand of DNA. A low island with palms on the far horizon. The sail is picked out in copper.",
 "mind-over-matter": "A terrestrial globe on a brass stand, its continents lightly engraved, with several dozen tiny lanterns scattered across the land, each joined to its neighbours by hair-thin threads. Above the globe a single coin spinning in the air, picked out in copper. Around the base, a faint crowd of small human figures looking up.",
 "ancient-skies": "An antique planisphere of the southern sky shown as a large circular star chart: engraved constellation figures, a centaur, a ship, an altar, a wolf and a winding river, crowd its outer ring, and at its centre lies a conspicuously empty circular patch of plain paper with no stars and no figures. At the lower edge a small robed astronomer on a rocky shore sights along a rod toward the horizon. The rim of the empty circle is picked out in copper.",
 "workshop": "A scholar's workbench seen from the front: an ice core in a cradle, a brass astrolabe, a knotted-cord khipu hanging from a peg, a clay tablet with wedge marks, a fossil ammonite, a magnifying lens, and an open blank notebook. A single shaft of light falls across the bench. The astrolabe is picked out in copper.",
}
OUT = Path(__file__).resolve().parent.parent / "site" / "illustrations" / "raw"

def main():
    model, names = sys.argv[1], sys.argv[2:] or list(SUBJECTS)
    key = os.environ["OPENAI_API_KEY"]
    OUT.mkdir(parents=True, exist_ok=True)
    for n in names:
        body = {"model": model, "prompt": STYLE + SUBJECTS[n], "size": "1536x1024", "quality": "high", "n": 1}
        req = urllib.request.Request("https://api.openai.com/v1/images/generations",
            data=json.dumps(body).encode(), method="POST",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json", "User-Agent": "image-script/1.0"})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=600))
        except urllib.error.HTTPError as e:
            print(n, "HTTP", e.code, e.read().decode()[:500]); continue
        (OUT / f"{n}.png").write_bytes(base64.b64decode(r["data"][0]["b64_json"]))
        print(n, "ok", json.dumps(r.get("usage")))

if __name__ == "__main__":
    main()
