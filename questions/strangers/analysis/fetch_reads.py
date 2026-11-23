#!/usr/bin/env python3
"""Download the public mapped reads of PIE069 from the European Nucleotide Archive (study PRJEB62503).

    python3 analysis/fetch_reads.py        # run from questions/strangers; writes data/ena_PRJEB62503/

Fetches the file in ranged pieces, in parallel, checks every piece's size and the whole file's MD5 against the
archive's record, and only then joins the pieces. Standard library only.
"""
import concurrent.futures
import hashlib
import pathlib
import sys
import time
import urllib.request

URL = "https://ftp.sra.ebi.ac.uk/vol1/run/ERR114/ERR11495483/PIE069.A0101.TF1.1_trim2.bam"
SIZE, MD5, PIECES = 72916233, "f650805de9dd54b9f41a7549f2c8d0a6", 24      # size and MD5 from ENA's file report for ERR11495483
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "ena_PRJEB62503"
CH = (SIZE + PIECES - 1) // PIECES


def piece(i):
    """Fetch one piece, resuming from whatever part of it is already on disk."""
    start, end = i * CH, min((i + 1) * CH, SIZE) - 1
    want = end - start + 1
    path = OUT / f"part_{i:02d}"
    if path.exists() and path.stat().st_size > want:
        path.unlink()
    for attempt in range(60):
        have = path.stat().st_size if path.exists() else 0
        if have == want:
            return True
        try:
            req = urllib.request.Request(URL, headers={"Range": f"bytes={start + have}-{end}"})
            with urllib.request.urlopen(req, timeout=60) as r, open(path, "ab") as f:
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
        except Exception as e:                                               # network errors: keep what arrived, try again
            print(f"piece {i}: {type(e).__name__}; resuming", flush=True)
            time.sleep(3)
    return path.exists() and path.stat().st_size == want


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / "PIE069.A0101.TF1.1_trim2.bam"
    if final.exists() and hashlib.md5(final.read_bytes()).hexdigest() == MD5:
        sys.exit("already downloaded and verified")
    with concurrent.futures.ThreadPoolExecutor(24) as ex:
        ok = list(ex.map(piece, range(PIECES)))
    if not all(ok):
        sys.exit(f"pieces missing: {[i for i, o in enumerate(ok) if not o]}; run again")
    data = b"".join((OUT / f"part_{i:02d}").read_bytes() for i in range(PIECES))
    md5 = hashlib.md5(data).hexdigest()
    if len(data) != SIZE or md5 != MD5:
        sys.exit(f"checksum mismatch: {len(data)} bytes, md5 {md5}; pieces kept for inspection")
    final.write_bytes(data)
    for i in range(PIECES):
        (OUT / f"part_{i:02d}").unlink()
    print("verified:", final.name, len(data), "bytes, md5", md5, "sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
