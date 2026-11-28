# Replication

After the lock, Google's `gemini-4-neon` wrote its own program for the contest from `protocol.md`,
`analysis/METHOD.md` and `replication/FORMAT.md` alone: `python3 replication/run_replication.py google`. It saw
none of our code and none of our numbers. The name of the lab's director is taken out of the plan before it
is sent. One request, no follow-up needed; cost $0.64.

The program (`google/replicate_round1.py`, 482 lines, standard library only) lists at its top the choices it
made where it found the method open. It was read before it was run.

## Result, 2026-11-27

| Compared with | Lists | Runs | Agreement |
|---|---|---|---|
| The preprint's archived outputs (`python3 replication/compare.py OUT.json --archive <archive>/outputs/headline tamil`) | Tamil, Sanskrit; splits 0 to 9 | 20 | 20 of 20 to two decimals, readings the same |
| Our locked run (`... --ours results/contest_rounds.json <list>`) | the seven control lists; rounds 0 to 99 | 700 | 700 of 700 to two decimals |

Its outputs are in `google/output/`.

What this covers: the contest program, on the same input files. It does not cover how the lists were built,
which was done once, by sessions of one model family.
