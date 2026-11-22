#!/usr/bin/env python3
"""Lock a question's protocol: python scripts/lock.py questions/<slug>"""
import datetime
import hashlib
import pathlib
import sys

if len(sys.argv) != 2:
    sys.exit(__doc__)
q = pathlib.Path(sys.argv[1])
protocol, lock = q / "protocol.md", q / "protocol.lock"
if not protocol.is_file():
    sys.exit(f"no {protocol}")
if lock.exists():
    sys.exit(f"{lock} already exists; changes after locking go in amendments.md")
if (q / "results").exists() or (q / "RESULTS.md").exists():
    sys.exit("results already exist; a lock must come first")
digest = hashlib.sha256(protocol.read_bytes()).hexdigest()
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
lock.write_text(f"sha256 {digest}\nlocked {stamp}\n")
print(f"locked {protocol} ({digest[:12]}) at {stamp}; commit {lock} on its own, then push")
