# Replication

After the lock, a model from each of two other vendors wrote its own program from `protocol.md`,
`windows.tsv`, `sources/blocked.tsv` and `FORMAT.md` alone: `python3 replication/run_replication.py openai` (or
`google`). The program is then run by hand from `questions/gcp-audit`
(`python replication/<vendor>/replicate_round1.py replication/<vendor>/output`) and compared with ours
(`python3 replication/compare.py replication/<vendor>/output`).

## Result, 2026-11-23

Both programs (OpenAI `gpt-6.2-astra`, 306 lines; Google `gemini-4-neon`, 500 lines) ran first time. Each lists
the choices it made where it found the protocol open, in a comment at its top. Against our run
(`<vendor>/comparison.txt`): 395 event scores and 396 control scores agree to within 0.000001; degrees of freedom
and devices used agree for every window; combined scores, agreement measures, the sign-flip p and all four
labels are the same. Cost: $1.47.

Both start from the same `windows.tsv`, so they check the scoring and not the reading of the project's tables.
The programs' on-disk caches (several GB each) were deleted after the runs and are not in git.
