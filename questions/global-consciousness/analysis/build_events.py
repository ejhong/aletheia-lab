#!/usr/bin/env python3
"""Build the event list and its control windows by rule (protocol.md). Reads only sources/; never the network data.

    python3 analysis/build_events.py        # run from questions/global-consciousness; writes events.tsv
"""
import datetime
import json
import pathlib

Q = pathlib.Path(__file__).resolve().parent.parent
DAYS = set((Q / "sources" / "available_days.txt").read_text().split())
CALENDAR = [("02-14", "14 February"), ("03-08", "8 March"), ("04-22", "22 April"), ("09-21", "21 September")]
FIRST, LAST = datetime.datetime(2016, 1, 1), datetime.datetime(2025, 10, 31, 23, 59, 59)
DAY = datetime.timedelta(days=1)


def days_of(start):
    """The UTC days a 24-hour window starting at `start` touches."""
    end = start + DAY - datetime.timedelta(seconds=1)
    return sorted({start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")})


def main():
    events = []
    for year in range(2016, 2026):
        for md, label in CALENDAR:
            events.append(("calendar", f"{label} {year}", datetime.datetime.strptime(f"{year}-{md}", "%Y-%m-%d")))
    for q in json.load(open(Q / "sources" / "noaa_earthquakes_2016_2025_deaths_100_or_more.json")):
        start = datetime.datetime(q["year"], q["month"], q["day"], q["hour"])          # the top of the hour of the origin time
        events.append(("earthquake", f"{q['country'].title()} {q['year']}-{q['month']:02d}-{q['day']:02d} (NOAA id {q['id']}, {q['deaths']} deaths)", start))
    events.sort(key=lambda e: e[2])
    near = lambda a, b: abs((a - b).total_seconds()) < 86400            # two 24-hour windows that share any second
    rows, kept, controls = [], [], []
    for kind, name, start in events:                                    # pass 1: which events stand
        why = ""
        if start < FIRST or start + DAY - datetime.timedelta(seconds=1) > LAST:
            why = "outside 2016-01-01 to 2025-10-31"
        elif not all(d in DAYS for d in days_of(start)):
            why = "no data file for the event window"
        elif any(near(start, k) for k in kept):
            why = "overlaps an earlier event in the list"
        else:
            kept.append(start)
        rows.append([kind, name, start, None, why])
    all_starts = [e[2] for e in events]
    for r in rows:                                                      # pass 2: a control for each, in date order
        if r[4]:
            continue
        for shift in (-7, 7, -14, 14):
            c = r[2] + datetime.timedelta(days=shift)
            if all(d in DAYS for d in days_of(c)) and not any(near(c, w) for w in all_starts) and not any(near(c, k) for k in controls):
                r[3] = c
                controls.append(c)
                break
        if r[3] is None:
            r[4] = "no control window with data"
    with open(Q / "events.tsv", "w") as f:
        f.write("kind\tevent\tstart_utc\tcontrol_start_utc\tin_test\twhy_not\n")
        for kind, name, start, control, why in rows:
            f.write(f"{kind}\t{name}\t{start:%Y-%m-%d %H:%M:%S}\t{control.strftime('%Y-%m-%d %H:%M:%S') if control else ''}\t{'yes' if control else 'no'}\t{why}\n")
    ok = [r for r in rows if r[3]]
    print(len(rows), "candidate events;", len(ok), "in the test:", sum(1 for r in ok if r[0] == "calendar"), "calendar days,",
          sum(1 for r in ok if r[0] == "earthquake"), "earthquakes")
    for r in rows:
        if not r[3]:
            print("  left out:", r[1], "-", r[4])
    need = sorted({d for r in ok for s in (r[2], r[3]) for d in days_of(s)})
    (Q / "sources" / "days_needed.txt").write_text("\n".join(need) + "\n")
    print(len(need), "day files needed")
    shifts = {}
    for r in ok:
        shifts[(r[3] - r[2]).days] = shifts.get((r[3] - r[2]).days, 0) + 1
    print("control shifts (days):", shifts)


if __name__ == "__main__":
    main()
