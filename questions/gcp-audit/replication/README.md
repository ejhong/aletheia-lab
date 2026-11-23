# Independent replication

After the lock, a model from another vendor writes its own program from `protocol.md`, `windows.tsv`,
`sources/blocked.tsv` and `FORMAT.md` alone, without our code or numbers. From `questions/gcp-audit`, run
`python3 replication/run_replication.py openai` (or `google`); the program lands in
`replication/<vendor>/replicate_round1.py`, and a crash report can be sent back with
`python3 replication/run_replication.py openai FILE`. Run the program by hand with
`python replication/<vendor>/replicate_round1.py replication/<vendor>/output`, then compare it with ours using
`python3 replication/compare.py replication/<vendor>/output`.
