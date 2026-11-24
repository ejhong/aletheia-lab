"""Item 1: compare the study's hand-typed dictionaries with my own reading of the SI table images
(img/q-001..q-007.png, extracted with pdfimages from kennett2025_si.pdf pp. 2-5; zoomed crops img/s5_*.png, s6_z.png, s8_z.png)."""
# My readings (from the images), shocked quartz / slide column only where a number is shown (else '--')
MINE = {
 "S2": [("10860,70 (482.5 cm)", 12810, 60, (12835, 12735), (12965, 12715)),
        ("11020,25 (500.5 cm)", 12955, 60, (13055, 12845), (13070, 12840))],
 "S3": [("AA-89168", 12825, 65, (12880, 12745), (12970, 12725)),
        ("SMU-1880", 12760, 105, (12840, 12625), (13055, 12490)),
        ("AA-1362", 12710, 95, (12770, 12620), (12895, 12485))],
 "S4": [("Haynes: 10885, 50", 12805, 45, (12830, 12750), (12895, 12735))],
 # rows in table, then {depth: shocked-quartz count}
 "S5": (31, {489.0: 0, 493.0: 0, 497.0: 0, 501.0: 5}),          # depth cm; ARL-4B, 3B, 2B, 1B
 "S6": (16, {1238.40: 0, 1238.37: 7, 1238.17: 0}),             # elevation m asl
 "S8": (19, {26.0: 0, 44.0: 0, 44.8: 0, 46.5: 4, 52.0: 0, 63.0: 0}),  # profile depth cm
}
STUDY_DATES = {  # from analysis/audit_plos_retractions.py KENNETT2025_SI_DATES
 "S2": [(12810, 60, [12715, 12965]), (12955, 60, [12840, 13070])],
 "S3": [(12825, 65, [12725, 12970]), (12760, 105, [12490, 13055]), (12710, 95, [12485, 12895])],
 "S4": [(12805, 45, [12735, 12895])],
}
STUDY_Q = {  # KENNETT2025_SI_QUARTZ_CONTROLS
 "S5": (31, {489.0: 0, 493.0: 0, 497.0: 0, 501.0: 5}),
 "S6": (16, {1238.40: 0, 1238.37: 7, 1238.17: 0}),
 "S8": (19, {26.0: 0, 44.0: 0, 44.8: 0, 46.5: 4, 52.0: 0, 63.0: 0}),
}
n_mis = 0
for t in ("S2", "S3", "S4"):
    for mine, st in zip(MINE[t], STUDY_DATES[t]):
        ok = (mine[1], mine[2]) == st[:2] and sorted(mine[4]) == sorted(st[2])
        n_mis += (not ok)
        print(f"Table {t} {mine[0]:22s} image mu {mine[1]} sd {mine[2]} 95% {mine[4]} | code {st} -> {'OK' if ok else 'MISMATCH'}")
for t in ("S5", "S6", "S8"):
    ok = MINE[t] == STUDY_Q[t]; n_mis += (not ok)
    print(f"Table {t}: image rows {MINE[t][0]}, quartz {MINE[t][1]} | code {STUDY_Q[t]} -> {'OK' if ok else 'MISMATCH'}")
tot_rows = sum(MINE[t][0] for t in ("S5", "S6", "S8")); tot_q = sum(len(MINE[t][1]) for t in ("S5", "S6", "S8"))
grains = sum(sum(MINE[t][1].values()) for t in ("S5", "S6", "S8"))
print(f"\nStrata analysed for shocked quartz: {tot_q} of {tot_rows} ({100*tot_q/tot_rows:.1f}%); per site S5 {len(MINE['S5'][1])}/31, S6 {len(MINE['S6'][1])}/16, S8 {len(MINE['S8'][1])}/19; grains {grains}")
print("Mismatches:", n_mis)
