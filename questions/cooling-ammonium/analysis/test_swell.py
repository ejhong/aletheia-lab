#!/usr/bin/env python3
"""Tests of swell.py on made-up data. Run: python test_swell.py (from questions/cooling-ammonium/analysis)."""
import math

import swell

# 1. Bins and measures by hand. Rows every 10 years; value 10 before t = 1000 (older), 30 for the 60 years after, 15 beyond.
s = {a: (10.0 if a >= 1000 else 30.0 if a >= 940 else 15.0) for a in range(0, 3000, 10)}
after, before = swell.bins(s, 1000)
assert len(after) == 10 and len(before) == 5 and after[:4] == [30.0, 30.0, 30.0, 15.0] and before == [10.0] * 5
m = swell.measures(s, 1000)
assert abs(m["P"] - math.log(3)) < 1e-12 and abs(m["R"] - math.log((3 * 30 + 7 * 15) / 10 / 10)) < 1e-12 and m["peak_bin_starts_years_after"] == 0
assert abs(m["D"] - math.log((30 + 5 * 15) / 6 / 10)) < 1e-12 and m["H"] is None          # bins 2-7: one at 30, five at 15
m3 = swell.measures(s, 1000, 300)
assert abs(m3["H"] - math.log((30 + 5 * 15) / 6 / 15)) < 1e-12                             # later level is 15
del s[990], s[980]                       # after-bin 0 gone: D is untouched, P and R still have 9 of 10
m = swell.measures(s, 1000)
assert m is not None and m["P"] is not None and swell.bins(s, 1000)[0][0] is None
for a in (950, 940, 930, 920):           # bins 2 and 3 gone: 4 of the 6 delayed bins remain, under the 5 needed
    s.pop(a, None)
assert swell.measures(s, 1000) is None
s2 = {a: 5.0 for a in range(0, 3000, 10)}
del s2[1010]                             # half a bin missing: the bin is the mean of what is there
assert swell.bins(s2, 1000)[1][0] == 5.0 and swell.measures(s2, 1000)["D"] == 0.0
s2[900] = -1.0                           # a non-positive delayed bin (mean of -1 and 5 is positive: still fine)
assert swell.measures(s2, 1000) is not None
s2[910] = -9.0                           # now that bin's mean is negative: no measure
assert swell.measures(s2, 1000) is None

# 2. Which coolings enter, and which times are quiet.
ev = [{"event": "GI-x", "age": 20000, "kind": "other", "unc": ""}, {"event": "GS-a", "age": 19900, "kind": "stadial onset", "unc": "a"},     # warm phase 100 years: in
      {"event": "GI-y", "age": 19700, "kind": "other", "unc": ""},                                                                         # cold phase 200 years: in
      {"event": "GS-b", "age": 19650, "kind": "stadial onset", "unc": "b"},                                                                # warm phase 50 years: out
      {"event": "GS-c", "age": 30000, "kind": "stadial onset", "unc": "d"},                                                                # dated too loosely: out
      {"event": "GS-d", "age": 40000, "kind": "stadial onset", "unc": "b"}, {"event": "GI-z", "age": 39850, "kind": "other", "unc": ""},   # cold phase 150 years: out
      {"event": "GS-e", "age": 12896, "kind": "stadial onset", "unc": "4yr"}, {"event": "GS-f", "age": 10400, "kind": "stadial onset", "unc": "a"}]   # f: too near the edge
got = swell.coolings(ev)
assert [e["event"] for e in got] == ["GS-a", "GS-e"] and got[1]["t"] == 12900, got
q = swell.quiet_times(ev)
assert q[0] >= 10500                                        # the grid starts at or after 10,500
assert 12700 not in q and 13180 not in q and 13200 in q and 12580 in q     # an event within 300 after or 200 before bars a time
assert all(t % 20 == 0 for t in q) and max(q) <= 107520

# 3. Verdicts.
mk = lambda name, D, pct: {"event": name, "D": D, "D_pct": pct}
rows = [mk("GS-1", 2.0, 0.99)] + [mk(f"GS-{i}", 1.0, 0.9) for i in range(2, 8)] + [mk(f"GS-{i}", 0.1, 0.3) for i in range(8, 11)]
v = swell.verdicts({"NGRIP": rows, "NEEM": rows})
assert v["general"] == "general" and v["younger_dryas"] == "the largest" and v["q1"]["NGRIP"]["in_top_quarter"] == 6 and v["q2"]["NEEM"]["of"] == 10
assert v["paired"]["both"] == [f"GS-{i}" for i in range(2, 8)] and v["paired"]["one_core_only"] == [] and v["q2"]["NGRIP"]["largest_other"] == 1.0
rows2 = [mk("GS-1", 0.05, 0.2)] + [mk(f"GS-{i}", 1.0, 0.9) for i in range(2, 5)] + [mk(f"GS-{i}", 0.1, 0.3) for i in range(5, 14)]
v = swell.verdicts({"NGRIP": rows2, "NEEM": rows})
assert v["general"] == "mixed" and v["younger_dryas"] == "not among the largest", v          # 3 of 12 in NGRIP, 6 of 9 in NEEM
v = swell.verdicts({"NGRIP": rows2, "NEEM": rows2})
assert v["general"] == "not seen" and v["q2"]["NGRIP"]["rank"] == 13
rows3 = [mk("GS-1", 1.5, 0.95)] + [mk("GS-0", 1.8, 0.97)] + [mk(f"GS-{i}", 1.0, 0.9) for i in range(2, 9)] + [mk(f"GS-{i}", 0.1, 0.3) for i in range(9, 16)]
v = swell.verdicts({"NGRIP": rows3, "NEEM": rows3})
assert v["general"] == "mixed" and v["younger_dryas"] == "among the largest", v              # 8 of 15; rank 2 of 16
rows4 = rows + [{"event": "GS-99", "D": None}]
v = swell.verdicts({"NGRIP": rows4, "NEEM": rows})
assert v["q1"]["NGRIP"]["not_evaluable"] == ["GS-99"] and v["q1"]["NGRIP"]["others"] == 9
rows5 = [mk("GS-1", 2.0, 0.99)] + [mk(f"GS-{i}", -0.1, 0.9) for i in range(2, 8)]            # high percentile but no rise: not counted
assert swell.verdicts({"NGRIP": rows5, "NEEM": rows5})["general"] == "not seen"
print("all tests pass")
