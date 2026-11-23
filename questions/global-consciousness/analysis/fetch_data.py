#!/usr/bin/env python3
"""Download the day files the test needs from the Global Consciousness Project's public archive.

    python3 analysis/fetch_data.py        # run from questions/global-consciousness; writes data/ and sources/files.sha256

Each file is fetched in ranged pieces, in parallel, resuming after dropped connections. A file is accepted only if it
has the length the server reports and decompresses to the end. Standard library only.
"""
import concurrent.futures
import gzip
import hashlib
import pathlib
import time
import urllib.request

Q = pathlib.Path(__file__).resolve().parent.parent
OUT = Q / "data"
BASE = "https://global-mind.org/data/eggsummary/{y}/basketdata-{d}.csv.gz"
PIECES, FILES_AT_ONCE = 10, 2


def get(url, start, end, path):
    want = end - start + 1
    for _ in range(40):
        have = path.stat().st_size if path.exists() else 0
        if have == want:
            return True
        if have > want:
            path.unlink()
            continue
        try:
            req = urllib.request.Request(url, headers={"Range": f"bytes={start + have}-{end}"})
            with urllib.request.urlopen(req, timeout=60) as r, open(path, "ab") as f:
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
        except Exception:
            time.sleep(3)
    return False


def day(d):
    final = OUT / f"basketdata-{d}.csv.gz"
    if final.exists():
        return d, "have"
    url = BASE.format(y=d[:4], d=d)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=60) as r:
            size = int(r.headers["Content-Length"])
    except Exception as e:
        return d, f"no length: {e}"
    ch = (size + PIECES - 1) // PIECES
    parts = [OUT / f".{d}.part{i:02d}" for i in range(PIECES)]
    with concurrent.futures.ThreadPoolExecutor(PIECES) as ex:
        ok = list(ex.map(lambda i: get(url, i * ch, min((i + 1) * ch, size) - 1, parts[i]), range(PIECES)))
    if not all(ok):
        return d, "pieces missing"
    data = b"".join(p.read_bytes() for p in parts)
    try:
        gzip.decompress(data)
    except Exception as e:
        return d, f"does not decompress: {e}"
    if len(data) != size:
        return d, "wrong length"
    final.write_bytes(data)
    for p in parts:
        p.unlink()
    return d, "ok"


def main():
    OUT.mkdir(exist_ok=True)
    need = (Q / "sources" / "days_needed.txt").read_text().split()
    with concurrent.futures.ThreadPoolExecutor(FILES_AT_ONCE) as ex:
        for d, status in ex.map(day, need):
            if status not in ("ok", "have"):
                print(d, status, flush=True)
    have = [d for d in need if (OUT / f"basketdata-{d}.csv.gz").exists()]
    with open(Q / "sources" / "files.sha256", "w") as f:
        for d in have:
            f.write(f"{hashlib.sha256((OUT / f'basketdata-{d}.csv.gz').read_bytes()).hexdigest()}  basketdata-{d}.csv.gz\n")
    print(len(have), "of", len(need), "files present", flush=True)


if __name__ == "__main__":
    main()
