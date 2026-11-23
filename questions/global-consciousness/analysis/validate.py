#!/usr/bin/env python3
"""Before the lock: score six of the project's own formal events (2011-2015, full UTC days) and compare with the
scores the project published. Tests the file reader and the statistic on real data that is not part of the test.

    python analysis/validate.py        # run from questions/global-consciousness; fetches six day files if absent
"""
import json

import fetch_data
import netvar

# day, the project's name for the event, and its published Z-score (https://global-mind.org/results.html, read 2026-11-23)
PUBLISHED = [("2011-04-22", "Earth Day, 2011", 0.282), ("2011-09-21", "Internat Day Peace", 3.136), ("2013-03-08", "Internat Women's Day", 0.943),
             ("2014-02-14", "V-day and Toning 2014", -0.579), ("2015-12-03", "Arbaeen, Hussein", -0.117), ("2015-12-12", "Climate Agreement", 1.013)]


def main():
    fetch_data.OUT.mkdir(exist_ok=True)
    out = []
    for day, name, z_pub in PUBLISHED:
        status = fetch_data.day(day)[1]
        assert status in ("ok", "have"), (day, status)
        eggs, x = netvar.window(f"{day} 00:00:00")
        ok = netvar.passes(*netvar.egg_stats(x))
        r = netvar.score(x[:, ok], netvar.SD)
        own = netvar.score(x[:, ok], (netvar.egg_stats(x)[2][ok]) ** 0.5)
        out.append({"day": day, "event": name, "published": z_pub, "ours_theoretical": round(r["z"], 3), "ours_own_window_variances": round(own["z"], 3),
                    "eggs": int(ok.sum()), "eggs_seen": len(eggs), "seconds": r["df"]})
        print(out[-1], flush=True)
    json.dump(out, open(netvar.Q / "explore" / "validation.json", "w"), indent=1)


if __name__ == "__main__":
    main()
