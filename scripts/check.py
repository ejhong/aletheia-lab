#!/usr/bin/env python3
"""Fail-closed checks for every question folder (run by CI): python scripts/check.py"""
import hashlib
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REQUIRED = ["protocol.md", "MANIFEST.md", "log.md"]
errors = []


def first_commit_time(path):
    """Unix time of the earliest commit that added anything under path, or None if uncommitted."""
    out = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%ct", "--reverse", "--", str(path)],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    return int(out[0]) if out else None


for q in sorted((ROOT / "questions").iterdir()):
    if not q.is_dir() or q.name.startswith("_"):
        continue
    rel = q.relative_to(ROOT)
    for name in REQUIRED:
        if not (q / name).is_file():
            errors.append(f"{rel}: missing {name}")

    lock = q / "protocol.lock"
    results = [p for p in (q / "results", q / "RESULTS.md") if p.exists()]

    if lock.exists():
        fields = dict(line.split(" ", 1) for line in lock.read_text().splitlines() if " " in line)
        actual = hashlib.sha256((q / "protocol.md").read_bytes()).hexdigest()
        if fields.get("sha256") != actual:
            errors.append(f"{rel}: protocol.md changed after locking (put changes in amendments.md)")

    if results:
        if not lock.exists():
            errors.append(f"{rel}: results exist but the protocol is not locked")
            continue
        lock_t = first_commit_time(lock.relative_to(ROOT))
        if lock_t is None:
            errors.append(f"{rel}: protocol.lock must be committed before any results")
            continue
        for r in results:
            r_t = first_commit_time(r.relative_to(ROOT))
            if r_t is not None and r_t <= lock_t:
                errors.append(f"{rel}: {r.name} was committed no later than the lock")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("all question folders pass")
