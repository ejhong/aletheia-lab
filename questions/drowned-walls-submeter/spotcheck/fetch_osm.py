"""Fetch OpenStreetMap seamark objects (imported from nautical chart data) in a box, from a public Overpass server.
usage: python -I fetch_osm.py <south> <west> <north> <east> <out.json> [overpass_url]
The default server is a public mirror; the main one (overpass-api.de) was over capacity on 2026-11-27."""
import sys, urllib.parse, urllib.request
s, w, n, e, out = sys.argv[1:6]
url = sys.argv[6] if len(sys.argv) > 6 else "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
q = f'[out:json][timeout:60];(node["seamark:type"]({s},{w},{n},{e});way["seamark:type"]({s},{w},{n},{e}););out center tags;'
req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": "bathymetry-audit/1.0"})
with urllib.request.urlopen(req, timeout=120) as r:
    open(out, "wb").write(r.read())
print("saved", out)
