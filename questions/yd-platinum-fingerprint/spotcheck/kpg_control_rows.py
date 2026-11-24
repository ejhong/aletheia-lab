# Lists every row of sheets "Data 2" and "Data 3" of kpg2025_MOESM4.xlsx with Ir >= 0.1 ppb and marks those that pass the control filter (six elements > 0, Ir >= 0.5 ppb) before the Amendment 2 fix, showing the four RSD% rows. Run: python spotcheck/kpg_control_rows.py [data_dir]
import pathlib
import sys

from _common import QDIR, load_program

m = load_program()
data = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else QDIR / "data"
xlsx = data / "kpg2025_MOESM4.xlsx"
COLS = {2: dict(Os=5, Ir=8, Ru=11, Pt=14, Pd=17, Re=20), 3: dict(Os=8, Ir=11, Ru=14, Pt=17, Pd=20, Re=23)}
for sheet, cols in COLS.items():
    print(f"## sheet Data {sheet}")
    for i, r in enumerate(m._read_xlsx_sheet_rows(xlsx, sheet)[2:], start=3):
        v = {e: (m._to_float(r[c]) if c < len(r) else None) for e, c in cols.items()}
        if v["Ir"] is None or v["Ir"] < 0.1:
            continue
        passes = all(v[e] is not None and v[e] > 0 for e in cols) and v["Ir"] >= 0.5
        print(f"  non-empty row {i:3d} {r[0][:34]:34s} Ir={v['Ir']:.3g} ppb Pt={v['Pt']:.3g} ppb {'PASSED OLD FILTER' if passes else ''}")
kept = m.parse_kpg2025_benchmark(xlsx)
print("Samples kept by the current parser:", [s["sample"] for s in kept])
