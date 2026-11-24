# Copies the first run's White Pond (OCR) block into a rerun's results, unchanged. Run: python carry_white_pond.py results/first_run results
# Why: the first run used tesseract 5.3.4; the Amendment 2 rerun had tesseract 5.5.4, which reads one more White Pond row
# (204 cm: Pt 2.4, Pd 5.0 ppb) and so shifts the White Pond baselines and z-scores slightly. White Pond does not enter the
# verdict (only the 'independent' columns do), so the first run's White Pond numbers are kept as they were.
import csv, io, json, pathlib, sys

old_dir, new_dir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
old = json.loads((old_dir / "summary.json").read_text())
new = json.loads((new_dir / "summary.json").read_text())

for key in ("white_pond_n", "white_pond_samples"):
    new["pillar1b_cross_site"][key] = old["pillar1b_cross_site"][key]
old_wp = [a for a in old["pillar2_blind_peaks"]["audits"] if a["site"].startswith("White Pond")]
new_audits = new["pillar2_blind_peaks"]["audits"]
wp_idx = [i for i, a in enumerate(new_audits) if a["site"].startswith("White Pond")]
assert [new_audits[i]["proxy"] for i in wp_idx] == [a["proxy"] for a in old_wp]
for i, a in zip(wp_idx, old_wp):
    new_audits[i] = a
(new_dir / "summary.json").write_text(json.dumps(new, indent=2) + "\n")

def rows(p):
    return list(csv.reader(io.StringIO(p.read_text()), delimiter="\t"))
old_rows = {(r[0], r[3]): r for r in rows(old_dir / "blind_peaks.tsv") if r[0].startswith("White Pond")}
out = [old_rows.get((r[0], r[3]), r) for r in rows(new_dir / "blind_peaks.tsv")]
with (new_dir / "blind_peaks.tsv").open("w", newline="") as f:
    csv.writer(f, delimiter="\t").writerows(out)
print("carried over White Pond block:", len(old_wp), "audits,", old["pillar1b_cross_site"]["white_pond_n"], "samples")
