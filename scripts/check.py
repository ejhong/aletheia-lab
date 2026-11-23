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
    """Unix time of the earliest commit that added anything under path, or None if uncommitted.

    --full-history looks down every side of a merge. Without it git follows one parent only, and a question
    branch that was merged alongside a squashed copy of itself would be skipped.
    """
    out = subprocess.run(
        ["git", "log", "--full-history", "--diff-filter=A", "--format=%ct", "--", str(path)],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    return min(map(int, out)) if out else None


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for q in sorted((ROOT / "questions").iterdir()):
    if not q.is_dir() or q.name.startswith("_"):
        continue
    rel = q.relative_to(ROOT)
    for name in REQUIRED:
        if not (q / name).is_file():
            errors.append(f"{rel}: missing {name}")

    lock = q / "protocol.lock"
    results = [p for p in (q / "results", q / "RESULTS.md") if p.exists()]
    locked_statements = {}

    if lock.exists():
        lines = [line.split() for line in lock.read_text().splitlines()]
        protocol_sha = next((parts[1] for parts in lines if len(parts) >= 2 and parts[0] == "sha256"), None)
        if protocol_sha != sha(q / "protocol.md"):
            errors.append(f"{rel}: protocol.md changed after locking (put changes in amendments.md)")
        locked_statements = {parts[1]: parts[2] for parts in lines if len(parts) >= 3 and parts[0] == "statement"}
        for path, digest in locked_statements.items():
            if not (q / path).is_file():
                errors.append(f"{rel}: locked statement {path} is missing")
            elif sha(q / path) != digest:
                errors.append(f"{rel}: {path} changed after locking (add a new statement file via amendments.md)")

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
        # Proof lane: every formal statement file must be locked before results are reported.
        for s in sorted((q / "lean").glob("**/Statement*.lean")):
            path = s.relative_to(q).as_posix()
            if ".lake" not in s.parts and path not in locked_statements:
                errors.append(f"{rel}: {path} is not locked (python scripts/lock.py {rel} --statement {path})")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("all question folders pass")
