#!/usr/bin/env python3
"""Check every quotation in passages.md against the extracted text of its source.

    python3 check_quotes.py [folder holding the extracted texts]

The default folder is ~/research-sources/unfolding-argument/text (the texts are copyrighted or bulky and are
not in the repository; MANIFEST.md says where each came from). Each passage names its source file in its heading.
A quotation is cut at every "[…]"; each piece must occur in the source, and the pieces must occur in order.
The comparison uses letters only (case, spacing, punctuation, digits and mathematical symbols are ignored),
because text extraction garbles symbols and breaks words at line ends.
"""
import pathlib
import re
import sys
import unicodedata

HERE = pathlib.Path(__file__).resolve().parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.home() / "research-sources/unfolding-argument/text"


def letters(text):
    text = unicodedata.normalize("NFKD", text).lower()
    return re.sub(r"[^a-z]", "", text)


cache, bad, n = {}, 0, 0
for sec in re.split(r"\n## ", (HERE / "passages.md").read_text())[1:]:
    head = sec.splitlines()[0]
    pid = head.split(" ")[0]
    m = re.search(r"\[source: ([^\]]+)\]", head)
    quote = " ".join(line[2:] for line in sec.splitlines() if line.startswith("> "))
    if not m:
        print(f"{pid}: no source file named")
        bad += 1
        continue
    name = m.group(1)
    if name not in cache:
        cache[name] = letters((src / name).read_text(encoding="utf-8", errors="replace"))
    pos = 0
    for piece in quote.split("[…]"):
        key = letters(piece)
        n += 1
        at = cache[name].find(key, pos)
        if at < 0:
            bad += 1
            where = "found, but out of order" if key in cache[name] else "NOT FOUND"
            print(f"{pid}: {where}: {piece.strip()[:90]}…")
        else:
            pos = at + len(key)
print(f"{n} pieces checked, {bad} problems")
sys.exit(1 if bad else 0)
