# Format notes for the replication

These notes describe the input file and the output wanted. The analysis is the one in `protocol.md` ("Analysis");
where these notes define an output key, they only say which of the protocol's numbers it is.

## Input file (path relative to the working directory, `questions/gobekli-star-map/`)

`results/rankings.tsv`: tab-separated, UTF-8, with a header line:

    vendor	trial_id	task	target_id	position	option_id

One row per ranked option of one valid trial (invalid trials are already left out). A ranking is the set of rows
with the same `vendor` and `trial_id` (the same `trial_id` is used by every judge, so group by both). `position`
runs from 1 (most similar) to the number of options, each option once.

- `vendor`: the judge, e.g. `openai`, `google`, `xai`.
- `task`: `A` or `B`.
- Task `A`: `target_id` is a figure `A01` … `A08`; the options are the 12 symbols `S01` … `S12` (12 rows per trial).
- Task `B`: `target_id` is a symbol `S01` … `S08`; the options are the 8 figures `A01` … `A08` (8 rows per trial).

Figure `A0k` is claimed to be symbol `S0k`, for k = 1 to 8. `A01` is the scorpion figure and `S01` the scorpion
photograph. `S01` … `S08` are the pillar symbols; `S09` … `S12` are the four others. There are up to 5 valid
rankings per judge, task and target.

Python 3.12 and numpy are available. No other packages. Enumerating all 19,958,400 assignments of 8 distinct
symbols out of 12 must be done efficiently (with numpy, or by dynamic programming over subsets of used symbols);
it is feasible in well under a minute.

## Output wanted

Write one file, `summary.json`, to the directory given as the first command-line argument. All "mean ranks" are
those of the protocol's "Tables" section; "pooled" means the mean of the per-judge tables, each counted judge
weighing equally. "Without the scorpion" means the protocol's re-ranking: drop `S01` from every Task A ranking and
close the gap (ranks 1..11), and leave out figure `A01`; for Task B, drop `A01` from every ranking (ranks 1..7)
and leave out symbol `S01`. A claimed symbol is "sole best" for a figure when its mean rank is strictly lower
(better) than that of every other symbol in the row; a tie for best does not count.

- `judges_included`: sorted list of the vendors that count for Task A (coverage of every figure with at least 3
  valid rankings, and the competence check: mean rank of `S01` for `A01`, with all 12 symbols, at most 2.0).
- `judges_excluded`: object, vendor -> a short reason in words, for every vendor in the file not counted for
  Task A.
- `without_scorpion` (Task A, pooled over `judges_included`, 7 figures `A02`…`A08`, 11 symbols `S02`…`S12`):
  - `claimed_sole_best_count`: integer, the number of the 7 figures for which the claimed symbol is sole best
    (the protocol's item 1).
  - `mean_rank_of_claimed`: the mean over the 7 figures of the claimed symbol's pooled mean rank (ranks 1..11).
  - `p_among_pillar_7`: item 2: the share of the 5,040 one-to-one pairings of the 7 figures with the 7 pillar
    symbols `S02`…`S08` whose total pooled mean rank is less than or equal to the claimed pairing's total.
  - `p_among_11`: the same share among all 1,663,200 assignments of 7 distinct symbols out of the 11 to the 7
    figures.
  - `per_judge`: object, vendor -> {`claimed_sole_best_count`, `p_among_pillar_7`}, the same two numbers computed
    from that judge's own table, for every vendor in `judges_included`.
- `all8` (Task A, pooled over `judges_included`, 8 figures, 12 symbols, ranks 1..12):
  - `claimed_sole_best_count`: of 8.
  - `mean_rank_of_claimed`: mean over the 8 figures of the claimed symbol's pooled mean rank.
  - `p_among_pillar_8`: share of the 40,320 pairings of the 8 figures with `S01`…`S08`, as above.
  - `p_among_12`: share of the 19,958,400 assignments of 8 distinct symbols out of 12, as above.
  - `P_plus_1`: integer, item 3: the product over the 8 figures of (1 + the number of other symbols, among all 12,
    whose pooled mean rank is less than or equal to the claimed symbol's).
- `task_b`: pooled over the judges that count for Task B: those in `judges_included` that also have at least 3
  valid Task B rankings for each of `S01`…`S08`. Rows are the pillar symbols, columns the figures.
  - `without_scorpion`: {`claimed_sole_best_count` (of the 7 symbols `S02`…`S08`, figures `A02`…`A08`),
    `p_orderings` (share of the 5,040 pairings as good as or better than the claimed one)}.
  - `all8`: {`claimed_sole_best_count` (of 8), `p_orderings` (share of the 40,320 pairings)}.
- `labels`: {`reproduction`, `pairing`}, the labels of the protocol's two tables, written in lower case and
  without the leading words "Blind judges". Exactly one of:
  - `reproduction`: `largely reproduce the paper's ranking`, `partly reproduce the paper's ranking`,
    `do not reproduce the paper's ranking`.
  - `pairing`: `pair the pillar's animals with the claimed figures better than chance`,
    `pairing not better than chance in this test`, `weak or mixed`.
  - Both are `not testable` if fewer than two judges count for Task A.

If fewer than two judges count for Task A, write `null` for `without_scorpion` and `all8`; if fewer than two count
for Task B, write `null` for `task_b`. Shares (`p_…`) are plain numbers between 0 and 1.
