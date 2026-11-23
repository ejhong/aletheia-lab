#!/usr/bin/env python3
"""Test reads.py on a hand-made BAM file. Run: python test_reads.py (from questions/strangers/analysis)."""
import gzip
import os
import struct
import tempfile

import numpy as np

import reads


def record(ref_id, pos, mapq, flag, cigar, seq, qual):
    name = b"r\x00"
    ops = b"".join(struct.pack("<I", (n << 4) | "MIDNSHP=X".index(op)) for op, n in cigar)
    codes = [reads.BASES.index(c) for c in seq] + [0]
    packed = bytes((codes[i] << 4) | codes[i + 1] for i in range(0, len(seq), 2))
    body = struct.pack("<iiBBHHHiiii", ref_id, pos, len(name), mapq, 0, len(cigar), flag, len(seq), -1, -1, 0) + name + ops + packed + bytes(qual)
    return struct.pack("<i", len(body)) + body


header = b"BAM\x01" + struct.pack("<i", 0) + struct.pack("<i", 2)
for nm, ln in ((b"chr1\x00", 1000), (b"2\x00", 1000)):
    header += struct.pack("<i", len(nm)) + nm + struct.pack("<i", ln)
recs = [
    record(0, 99, 60, 0, [("M", 8)], "ACGTACGT", [40] * 8),                          # covers 1-based 100..107
    record(0, 99, 60, 0, [("M", 3), ("D", 2), ("M", 3), ("I", 1), ("M", 2)], "ACGTTTAGC", [40] * 9),   # deletion then insertion
    record(0, 99, 5, 0, [("M", 8)], "TTTTTTTT", [40] * 8),                           # low mapping quality: skipped
    record(0, 99, 60, 0x400, [("M", 8)], "TTTTTTTT", [40] * 8),                      # duplicate: skipped
    record(1, 199, 60, 16, [("S", 2), ("M", 5)], "NNACGTA", [2, 2, 40, 40, 10, 40, 40]),   # soft clip; one low-quality base
]
path = os.path.join(tempfile.mkdtemp(), "t.bam")
with open(path, "wb") as f:
    f.write(gzip.compress(header + recs[0] + recs[1]) + gzip.compress(b"".join(recs[2:])))     # two gzip members, as in BGZF

it = reads.records(path)
refs, _ = next(it)
assert refs == ["chr1", "2"]
got = list(it)
assert len(got) == 5 and got[0][1] == 99 and got[0][2] == 60 and "".join(reads.BASES[c] for c in got[1][5]) == "ACGTTTAGC"
rp, qp = reads.aligned(99, [(0, 3), (2, 2), (0, 3), (1, 1), (0, 2)])
assert rp.tolist() == [99, 100, 101, 104, 105, 106, 107, 108] and qp.tolist() == [0, 1, 2, 3, 4, 5, 7, 8]

# SNPs: chr1 at 100, 102, 103 (in read 2's deletion), 106, 109; chr2 at 200, 202 (low quality), 204.
snp_pos = {"1": (np.array([100, 102, 103, 106, 109]), np.array([0, 1, 2, 3, 4])), "2": (np.array([200, 202, 204]), np.array([5, 6, 7]))}
snp, base, length, read = reads.observations(path, snp_pos)
obs = sorted(zip(snp.tolist(), [reads.BASES[b] for b in base], length.tolist(), read.tolist()))
# read 0 (ACGTACGT at 100..107): SNP 100 -> A, 102 -> G, 103 -> T, 106 -> G.
# read 1: 100 -> A, 102 -> G, 103 in the deletion, 106 -> T (read index 4), 109 -> C (index 8).
# read 4 (chr2, soft clip 2, ACGTA at 200..204): 200 -> A, 202 low quality, 204 -> A.
assert obs == [(0, "A", 8, 0), (0, "A", 9, 1), (1, "G", 8, 0), (1, "G", 9, 1), (2, "T", 8, 0), (3, "G", 8, 0), (3, "T", 9, 1), (4, "C", 9, 1),
               (5, "A", 7, 4), (7, "A", 7, 4)], obs
print("all tests pass")
