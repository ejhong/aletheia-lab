"""Turn the two saved GCP pages into tables.

Reads  sources/pred_formal.html  (formal event registry)
       sources/results.html      (published per-event results)
Writes sources/registry.tsv, sources/published.tsv, sources/matched.tsv

Python 3.9 standard library only. Deterministic. Text is changed only by
decoding HTML entities, turning <br> into a space, collapsing runs of
whitespace to one space and trimming. Rows inside HTML comments are not part
of the rendered tables and are ignored.
Usage: python3 analysis/build_registry.py   (from questions/gcp-audit/)
"""
import csv
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SRC = HERE / "sources"

REG_HEADER = ["Num", "Description", "Begin Date/Time", "End Date/Time",
              "Resolution", "Recipe", "Statistic", "Include"]
PUB_HEADER = ["Event", "Description", "Timeframe", "Hypothesis Source",
              "REGs", "Resolution", "Z-score", "Probability"]
REG_ROWS, PUB_ROWS = 512, 513  # data rows seen in the 2026-11-23 snapshots
TIME_FMT = "%Y-%m-%d %H:%M:%S"


class TableParser(HTMLParser):
    """Collect every <table> as a list of rows, each a list of cell texts."""

    def __init__(self):
        super().__init__(convert_charrefs=True)  # decodes &sup2; &amp; etc.
        self.tables, self.row, self.cell, self.depth = [], None, None, 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.depth += 1
            assert self.depth == 1, "nested table"
            self.tables.append([])
        elif tag == "tr":
            assert self.depth == 1, "<tr> outside a table"
            self.end_cell()
            self.row = []
            self.tables[-1].append(self.row)
        elif tag in ("td", "th"):
            assert self.row is not None, "cell outside a row"
            self.end_cell()
            self.cell = []
        elif tag == "br" and self.cell is not None:
            self.cell.append(" ")

    def handle_endtag(self, tag):
        if tag in ("td", "th", "tr", "table"):
            self.end_cell()
        if tag in ("tr", "table"):
            self.row = None
        self.depth -= tag == "table"

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def end_cell(self):
        if self.cell is not None:
            self.row.append(norm("".join(self.cell)))
            self.cell = None


def norm(s):
    return re.sub(r"\s+", " ", s).strip()  # \s also covers non-breaking space


def table_with_header(path, header):
    p = TableParser()
    p.feed(path.read_text(encoding="utf-8"))
    p.close()
    hits = [t for t in p.tables if t and t[0] == header]
    assert len(hits) == 1, f"{path.name}: expected one table with header {header}"
    rows = hits[0][1:]
    bad = [r for r in rows if len(r) != len(header)]
    assert not bad, f"{path.name}: rows with wrong cell count: {bad[:3]}"
    return rows


def seconds(begin, end):
    try:
        b, e = datetime.strptime(begin, TIME_FMT), datetime.strptime(end, TIME_FMT)
    except ValueError:
        return ""
    return str(int((e - b).total_seconds()) + 1)


def date_check(begin_utc, timeframe):
    """Compare registry begin date with the first date in the Timeframe."""
    try:
        b = datetime.strptime(begin_utc[:10], "%Y-%m-%d")
        t = datetime.strptime(timeframe[:8], "%Y%m%d")
    except ValueError:
        return "date unparsed"
    d = abs((t - b).days)
    return {0: "same date", 1: "1 day apart"}.get(d, f"dates {d} days apart")


def write_tsv(path, header, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def main():
    reg_raw = table_with_header(SRC / "pred_formal.html", REG_HEADER)
    pub_raw = table_with_header(SRC / "results.html", PUB_HEADER)
    assert len(reg_raw) == REG_ROWS, f"registry has {len(reg_raw)} rows"
    assert len(pub_raw) == PUB_ROWS, f"results has {len(pub_raw)} rows"

    registry = []
    for i, (num, desc, beg, end, res, rec, stat, inc) in enumerate(reg_raw, 1):
        included = "1" if inc.lower().startswith("yes") else "0"
        registry.append([num, desc, beg, end, seconds(beg, end), res, rec,
                         stat, inc, included, str(i)])
    write_tsv(SRC / "registry.tsv", ["num", "description", "begin_utc",
              "end_utc", "seconds", "resolution", "recipe", "statistic",
              "include", "included", "row"], registry)

    published = []
    for i, (ev, desc, tf, srcs, regs, res, z, prob) in enumerate(pub_raw, 1):
        m = re.search(r"\d+", ev)
        published.append([ev, m.group() if m else "", desc, tf, srcs, regs,
                          res, z, prob, str(i)])
    write_tsv(SRC / "published.tsv", ["event", "event_num", "description",
              "timeframe", "source", "regs", "resolution", "z", "probability",
              "row"], published)

    # Join rule: registry num (all plain integers) == published event_num
    # (digits of the Event cell, ignoring ~ and * marks), the number unique on
    # both sides, EXCEPT numbers 344-347, where the pages number differently:
    # registry 344 is "Earthdance 2010", which results.html lacks, and
    # results 344-346 carry the events registry numbers 345-347. Those rows
    # are left unmatched rather than re-paired by guesswork. Dates never
    # decide the join; they are compared afterwards and the result recorded.
    offset = {"344", "345", "346", "347"}
    reg_by = {r[0]: r for r in registry}
    pub_by = {p[1]: p for p in published}
    assert reg_by["344"][1] == "Earthdance 2010", "offset block moved"
    assert pub_by["344"][2] == "Astrology III.1", "offset block moved"
    reg_nums, pub_nums = [r[0] for r in registry], [p[1] for p in published]
    assert all(n.isdigit() for n in reg_nums), "non-integer registry num"
    matched = []
    for r in registry:
        n, p = r[0], pub_by.get(r[0])
        unique = reg_nums.count(n) == 1 and pub_nums.count(n) == 1
        if p is None or not unique or n in offset:
            rule, p = "unmatched", [""] * 10
        else:
            rule = "num; " + date_check(r[2], p[3])
        matched.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[9],
                        p[0], p[2], p[3], p[6], p[7], rule])
    write_tsv(SRC / "matched.tsv", ["num", "description", "begin_utc",
              "end_utc", "seconds", "resolution", "recipe", "statistic",
              "included", "pub_event", "pub_description", "pub_timeframe",
              "pub_resolution", "pub_z", "match_rule"], matched)
    print(f"registry {len(registry)}, published {len(published)}, "
          f"matched {sum(m[-1] != 'unmatched' for m in matched)}")


if __name__ == "__main__":
    main()
