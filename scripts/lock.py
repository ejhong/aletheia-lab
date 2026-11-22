#!/usr/bin/env python3
"""Lock a question's protocol, or a formal statement file added at a later stage.

    python scripts/lock.py questions/<slug>
    python scripts/lock.py questions/<slug> --statement lean/Stage2/Statement.lean

The first form writes protocol.lock with the SHA-256 of protocol.md, and of lean/Statement.lean if it exists.
The second form appends one more statement file to an existing lock; lines already in the lock never change.
"""
import datetime
import hashlib
import pathlib
import sys

args = sys.argv[1:]
if len(args) not in (1, 3) or (len(args) == 3 and args[1] != "--statement"):
    sys.exit(__doc__)
q = pathlib.Path(args[0])
protocol, lock = q / "protocol.md", q / "protocol.lock"
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def statement_line(rel):
    return f"statement {rel.as_posix()} {sha(q / rel)} {stamp}\n"


if len(args) == 3:
    rel = pathlib.PurePosixPath(args[2])
    if not lock.exists():
        sys.exit(f"no {lock}; lock the protocol first")
    if rel.is_absolute() or ".." in rel.parts or not (q / rel).is_file():
        sys.exit(f"no {q / rel} (give the path relative to {q})")
    recorded = [line.split()[1] for line in lock.read_text().splitlines() if line.startswith("statement ")]
    if rel.as_posix() in recorded:
        sys.exit(f"{rel} is already locked; a changed statement is a new file, explained in amendments.md")
    with lock.open("a") as f:
        f.write(statement_line(rel))
    print(f"locked {q / rel} at {stamp}; note it in amendments.md and commit before proving it")
    sys.exit(0)

if not protocol.is_file():
    sys.exit(f"no {protocol}")
if lock.exists():
    sys.exit(f"{lock} already exists; changes after locking go in amendments.md")
if (q / "results").exists() or (q / "RESULTS.md").exists():
    sys.exit("results already exist; a lock must come first")
text = f"sha256 {sha(protocol)}\nlocked {stamp}\n"
default_statement = pathlib.PurePosixPath("lean/Statement.lean")
if (q / default_statement).is_file():
    text += statement_line(default_statement)
lock.write_text(text)
print(f"locked {protocol} ({sha(protocol)[:12]}) at {stamp}; commit {lock} on its own, then push")
