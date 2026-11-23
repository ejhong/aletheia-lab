#!/usr/bin/env python3
"""Read a BAM file with the standard library and call alleles at the 1240K SNPs, one read at a time.

Used by amend3.py (Amendment 3). No outside tools: BAM is a series of gzip members, which Python's gzip module reads
as one stream; the record layout follows the SAM/BAM specification (section 4.2).

    python3 analysis/reads.py describe BAM      # header, flags, mapping quality, read lengths, how ends are masked
"""
import collections
import gzip
import struct
import sys

import numpy as np

BASES = "=ACMGRSVTWYHKDBN"
CONSUMES_REF = {0: True, 1: False, 2: True, 3: True, 4: False, 5: False, 6: False, 7: True, 8: True}     # M I D N S H P = X
CONSUMES_READ = {0: True, 1: True, 2: False, 3: False, 4: True, 5: False, 6: False, 7: True, 8: True}


def records(path):
    """Yield (references, None) once, then one tuple per read: (ref_id, pos0, mapq, flag, cigar, seq, qual)."""
    with gzip.open(path, "rb") as f:
        assert f.read(4) == b"BAM\x01", "not a BAM file"
        f.read(struct.unpack("<i", f.read(4))[0])
        refs = []
        for _ in range(struct.unpack("<i", f.read(4))[0]):
            n = struct.unpack("<i", f.read(4))[0]
            refs.append(f.read(n)[:-1].decode())
            f.read(4)
        yield refs, None
        while True:
            head = f.read(4)
            if len(head) < 4:
                return
            b = f.read(struct.unpack("<i", head)[0])
            ref_id, pos, l_name, mapq, _bin, n_cig, flag, l_seq = struct.unpack_from("<iiBBHHHi", b, 0)
            o = 32 + l_name
            cigar = [(v & 0xF, v >> 4) for v in struct.unpack_from(f"<{n_cig}I", b, o)]
            o += 4 * n_cig
            packed = np.frombuffer(b, dtype=np.uint8, count=(l_seq + 1) // 2, offset=o)
            codes = np.empty(2 * len(packed), dtype=np.uint8)
            codes[0::2], codes[1::2] = packed >> 4, packed & 0xF
            o += (l_seq + 1) // 2
            qual = np.frombuffer(b, dtype=np.uint8, count=l_seq, offset=o)
            yield ref_id, pos, mapq, flag, cigar, codes[:l_seq], qual


def aligned(pos, cigar):
    """Pairs (reference position, 0-based; index in the read) for every aligned base, as two arrays."""
    r, q, rp, qp = pos, 0, [], []
    for op, n in cigar:
        if op in (0, 7, 8):
            rp.append(np.arange(r, r + n))
            qp.append(np.arange(q, q + n))
        if CONSUMES_REF[op]:
            r += n
        if CONSUMES_READ[op]:
            q += n
    if not rp:
        return np.empty(0, dtype=np.int64), np.empty(0, dtype=np.int64)
    return np.concatenate(rp), np.concatenate(qp)


def observations(path, snp_pos, min_mapq=30, min_qual=30):
    """Every usable base that lands on a SNP: arrays (SNP index, base code 1=A 2=C 4=G 8=T, read length, read number).

    snp_pos: {chromosome name without 'chr': (sorted 1-based positions, their SNP indices)}.
    Skips unmapped, secondary, supplementary, duplicate and failed reads, and bases that are not A, C, G or T.
    """
    it = records(path)
    refs, _ = next(it)
    names = [r[3:] if r.lower().startswith("chr") else r for r in refs]
    out_snp, out_base, out_len, out_read = [], [], [], []
    for n_read, (ref_id, pos, mapq, flag, cigar, seq, qual) in enumerate(it):
        if ref_id < 0 or flag & (0x4 | 0x100 | 0x200 | 0x400 | 0x800) or mapq < min_mapq or names[ref_id] not in snp_pos:
            continue
        positions, index = snp_pos[names[ref_id]]
        rp, qp = aligned(pos, cigar)
        if not len(rp):
            continue
        lo, hi = np.searchsorted(positions, rp[0] + 1), np.searchsorted(positions, rp[-1] + 1, side="right")
        for k in range(lo, hi):
            j = np.searchsorted(rp, positions[k] - 1)
            if j < len(rp) and rp[j] == positions[k] - 1:
                qi = qp[j]
                if seq[qi] in (1, 2, 4, 8) and qual[qi] >= min_qual:
                    out_snp.append(index[k])
                    out_base.append(seq[qi])
                    out_len.append(len(seq))
                    out_read.append(n_read)
    return (np.array(out_snp, dtype=np.int64), np.array(out_base, dtype=np.uint8), np.array(out_len, dtype=np.int32),
            np.array(out_read, dtype=np.int64))


def describe(path):
    it = records(path)
    refs, _ = next(it)
    print("references:", len(refs), refs[:5], "...")
    flags, mapq, length = collections.Counter(), collections.Counter(), collections.Counter()
    first, last, ops = collections.Counter(), collections.Counter(), collections.Counter()
    n = 0
    for ref_id, pos, mq, flag, cigar, seq, qual in it:
        n += 1
        flags[flag] += 1
        mapq["0-9" if mq < 10 else "10-29" if mq < 30 else "30+"] += 1
        length[len(seq)] += 1
        for op, _ in cigar:
            ops["MIDNSHP=X"[op]] += 1
        if len(seq) >= 6:
            first["".join(BASES[c] for c in seq[:3]).replace("A", "x").replace("C", "x").replace("G", "x").replace("T", "x") + f" q{min(qual[:2])}-{max(qual[:2])}"] += 1
            last["".join(BASES[c] for c in seq[-3:]).replace("A", "x").replace("C", "x").replace("G", "x").replace("T", "x") + f" q{min(qual[-2:])}-{max(qual[-2:])}"] += 1
    print("reads:", n)
    print("flags:", dict(flags.most_common(8)))
    print("mapping quality:", dict(mapq))
    print("cigar operations:", dict(ops))
    ls = sorted(length)
    cum, tot = 0, sum(length.values())
    print("read length: min", ls[0], "max", ls[-1], "| share at max:", round(length[ls[-1]] / tot, 4))
    marks = {}
    for l in ls:
        cum += length[l]
        for q in (0.1, 0.25, 0.5, 0.75, 0.9):
            if q not in marks and cum >= q * tot:
                marks[q] = l
    print("read length quantiles:", marks)
    print("lengths 60+:", {l: length[l] for l in ls if l >= 60})
    print("first three bases (x = A/C/G/T) and quality range of the first two:", dict(first.most_common(5)))
    print("last three bases and quality range of the last two:", dict(last.most_common(5)))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "describe":
        describe(sys.argv[2])
    else:
        sys.exit(__doc__)
