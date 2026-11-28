"""Extract the base64 JPEG panels from the committed site gallery HTML.
usage: python -I extract_gallery.py <sonar_gallery.html> <out_dir>"""
import base64, pathlib, re, sys
html = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
titles = re.findall(r'<p class="sg-title">(.*?)</p>', html)
imgs = re.findall(r'src="data:image/jpeg;base64,([^"]+)"', html)
for i, (t, b) in enumerate(zip(titles, imgs)):
    p = out / f"gallery_{i}.jpg"; p.write_bytes(base64.b64decode(b)); print(p.name, t)
