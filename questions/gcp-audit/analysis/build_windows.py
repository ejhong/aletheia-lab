#!/usr/bin/env python3
"""Fix the events of the audit and a control window for each, from the project's own tables (protocol.md).

    python3 analysis/build_windows.py        # run from questions/gcp-audit
                                             # writes windows.tsv, sources/blocked.tsv and sources/days_needed.txt

Reads sources/matched.tsv (made by build_registry.py from the two saved pages) and sources/available_days.txt.
Reads no network data. Standard library only.
"""
import csv
import datetime
import pathlib
import re

Q = pathlib.Path(__file__).resolve().parent.parent
FMT = "%Y-%m-%d %H:%M:%S"
RECIPES = {"Stouffer Z Meanshift", "Stouffer Z"}
STATISTIC = "Chisquare 600 df weight"
RESOLUTION = "1-sec"
MAX_SECONDS = 7 * 86400
SHIFTS = [-7, 7, -14, 14, -21, 21, -28, 28]          # days, tried in this order
# Two events are in the published table and not in the registry; their days are kept clear of controls.
PUBLISHED_ONLY_DAYS = ["2010-10-13", "2015-09-21"]


def ts(text):
    return int(datetime.datetime.strptime(text, FMT).replace(tzinfo=datetime.timezone.utc).timestamp())


def days_of(a, b):
    """UTC days touched by the seconds a..b inclusive."""
    d = datetime.datetime.fromtimestamp(a, datetime.timezone.utc).date()
    last = datetime.datetime.fromtimestamp(b, datetime.timezone.utc).date()
    out = []
    while d <= last:
        out.append(d.isoformat())
        d += datetime.timedelta(days=1)
    return out


def day_span(day0, day1):
    a = int(datetime.datetime.strptime(day0, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc).timestamp())
    b = int(datetime.datetime.strptime(day1, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc).timestamp()) + 86399
    return a, b


def main():
    rows = list(csv.DictReader(open(Q / "sources" / "matched.tsv", encoding="utf-8"), delimiter="\t"))
    have = set((Q / "sources" / "available_days.txt").read_text().split())

    # Every stretch of time that any registered or published event occupies. Controls must stay clear of all of it.
    blocked = []
    for r in rows:
        try:
            a, b = ts(r["begin_utc"]), ts(r["end_utc"])
            if b < a:
                raise ValueError
            blocked.append((a, b))
        except ValueError:
            found = sorted(set(re.findall(r"\d{4}-\d{2}-\d{2}", r["begin_utc"] + " " + r["end_utc"])))
            if found:
                first, last = found[0], found[-1]
                gap = (datetime.date.fromisoformat(last) - datetime.date.fromisoformat(first)).days
                if gap <= 7:
                    blocked.append(day_span(first, last))
                else:
                    blocked += [day_span(d, d) for d in found]
    # A row whose registry date and published date disagree may really have happened on the published date:
    # keep that day and the next clear of controls as well.
    for r in rows:
        if r["match_rule"] not in ("num; same date", "num; 1 day apart") and re.fullmatch(r"\d{8}", r["pub_timeframe"] or ""):
            d = f"{r['pub_timeframe'][:4]}-{r['pub_timeframe'][4:6]}-{r['pub_timeframe'][6:]}"
            try:
                blocked.append(day_span(d, (datetime.date.fromisoformat(d) + datetime.timedelta(days=1)).isoformat()))
            except ValueError:
                pass
    for d in PUBLISHED_ONLY_DAYS:
        blocked.append(day_span(d, (datetime.date.fromisoformat(d) + datetime.timedelta(days=1)).isoformat()))

    blocked = sorted(set(blocked))
    with open(Q / "sources" / "blocked.tsv", "w", encoding="utf-8") as f:
        f.write("begin_unix\tend_unix\n" + "".join(f"{a}\t{b}\n" for a, b in blocked))

    def clear(a, b, taken):
        return all(b < x or a > y for x, y in blocked) and all(b < x or a > y for x, y in taken)

    out, taken = [], []
    for r in rows:
        why = []
        if r["included"] != "1":
            why.append("not included by the project")
        if r["recipe"] not in RECIPES or r["statistic"] != STATISTIC:
            why.append("not the standard recipe")
        if r["resolution"] != RESOLUTION:
            why.append("not 1-second resolution")
        try:
            a, b = ts(r["begin_utc"]), ts(r["end_utc"])
            if b < a:
                why.append("end before begin")
            elif b - a + 1 > MAX_SECONDS:
                why.append("longer than 7 days")
        except ValueError:
            a = b = None
            why.append("times do not parse")
        try:
            float(r["pub_z"])
        except ValueError:
            why.append("no published score")
        if r["match_rule"] not in ("num; same date", "num; 1 day apart"):
            why.append("registry and published dates disagree or no match")
        if not why and not all(d in have for d in days_of(a, b)):
            why.append("no data file")
        row = {"num": r["num"], "description": r["description"], "begin_utc": r["begin_utc"], "end_utc": r["end_utc"],
               "seconds": "" if a is None or b < a else b - a + 1, "published_z": r["pub_z"], "in_test": "", "why_out": "; ".join(why),
               "control_begin_utc": "", "control_shift_days": ""}
        if not why:
            for k in SHIFTS:
                ca, cb = a + k * 86400, b + k * 86400
                if all(d in have for d in days_of(ca, cb)) and clear(ca, cb, taken):
                    taken.append((ca, cb))
                    row["control_begin_utc"] = datetime.datetime.fromtimestamp(ca, datetime.timezone.utc).strftime(FMT)
                    row["control_shift_days"] = k
                    break
            else:
                row["why_out"] = "no control window"
        row["in_test"] = "1" if not row["why_out"] else "0"
        out.append(row)

    with open(Q / "windows.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    inside = [r for r in out if r["in_test"] == "1"]
    need = set()
    for r in inside:
        a = ts(r["begin_utc"])
        n = int(r["seconds"])
        c = ts(r["control_begin_utc"])
        need |= set(days_of(a, a + n - 1)) | set(days_of(c, c + n - 1))
    (Q / "sources" / "days_needed.txt").write_text("\n".join(sorted(need)) + "\n")
    reasons = {}
    for r in out:
        for w_ in (r["why_out"].split("; ") if r["why_out"] else []):
            reasons[w_] = reasons.get(w_, 0) + 1
    pub = [float(r["published_z"]) for r in inside]
    shifts = {}
    for r in inside:
        shifts[r["control_shift_days"]] = shifts.get(r["control_shift_days"], 0) + 1
    print(len(out), "registry rows;", len(inside), "in the test;", len(need), "day files needed")
    print("left out, by reason (a row can have several):", reasons)
    print("control shifts:", shifts)
    print("published scores of the events in the test: sum %.3f, combined %.3f, mean %.3f" % (sum(pub), sum(pub) / len(pub) ** 0.5, sum(pub) / len(pub)))
    secs = sorted(int(r["seconds"]) for r in inside)
    print("window seconds: min %d, median %d, max %d; total event seconds %d" % (secs[0], secs[len(secs) // 2], secs[-1], sum(secs)))


if __name__ == "__main__":
    main()
