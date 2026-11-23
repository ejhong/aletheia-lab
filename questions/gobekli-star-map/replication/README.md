# Replication

After the lock, a model from another vendor writes its own analysis program from `protocol.md` and
`FORMAT.md` alone, with none of our code and none of the rankings: `python3 replication/run_replication.py google`. The program is then run by hand from `questions/gobekli-star-map` on the real rankings
(`python replication/<vendor>/replicate_round1.py replication/<vendor>/output`) and compared with our
`results/summary.json` (`python3 replication/compare.py replication/<vendor>/output`).

## Result

Google `gemini-4-neon` wrote `google/replicate_round1.py` on 2026-11-23 at 21:10 UTC, before any ranking had been
analysed ($0.41). On the real rankings it leaves out the same three judges as our program, each for failing the
competence check, and gives the same two labels, "not testable" (`google/comparison.txt`). Every other number is
empty in both, because no judge counts. On made-up rankings in which judges pass, the two programs agree on all
23 numbers. One outside vendor was used, as Eugene now prefers.
