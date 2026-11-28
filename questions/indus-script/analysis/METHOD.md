# The contest, step by step

This is the full procedure of one run of the preprint's language contest (its test REP-1), written so that a
program can be made from it without seeing ours. It is part of the locked plan. Randomness is Python's
`random.Random(seed)` (Mersenne Twister) with its `shuffle` and `sample`; a program in Python that follows these
steps gives the same numbers as `analysis/contest.py` to two decimal places.

A run has four inputs: a list's settings file, a seed (a whole number), a mode (`real` or `null`), and the
corpus file.

## 1. Inputs

**Settings (`cfg.json`).** Keys: `lang`; `names`, `parts`, `words` (file names, relative to the settings file);
`number_words` (a map from "1", "2", "3", "4", "5", "6", "7", "12" to a word); `punmax` (0.5); `weights`
(`"once"`: every name has weight 1; `"stored"`: use each name's `weight`); optional `sample_n`; optional
`drop_parts` (list), `keep_noninitial` (list), `loan_category` (default `"sanskrit_loan"`).

**Names file** (JSON lines). Each line has `morphemes`, the name's parts in order, and may have `weight`.

**Parts file** (JSON lines). Each line has `m` (the part), `category` and `stability` (1, 2 or 3).

**Words file** (JSON). `{sign: {english word: [words of the language]}}` for the 69 signs.

**Corpus** (`inscriptions.csv`, read with a CSV reader, UTF-8). Columns used: `text`, `dir.`, `type`.

## 2. Spelling

`norm(s)`: Unicode NFC of `s` in lowercase, then delete every character matching the regular expression
`[\s\-’'’;:,.()\[\]?/*0-9]`.

`phonemes(s)`: scan `norm(s)` left to right; at each position take the first entry of this list that matches
there, in this order; if none matches, skip one character:

    kh gh ch jh ṭh ḍh th dh ph bh ai au ā ī ū ē ō ṛ ṝ ṅ ñ ṇ ṉ ṟ ḻ ḷ ṭ ḍ ṃ ḥ ś ṣ
    a i u e o k g c j t d p b n m y r l v h s

Vowels are `a ā i ī u ū e ē o ō ai au ṛ ṝ`.

**Cost of replacing one sound by another** (symmetric): 0 if equal; otherwise the value in this table; otherwise
1.0 if both are vowels or both are not, else 1.4.

| Cost | Pairs |
|---|---|
| 0.35 | l–ḷ, ḷ–ḻ, r–ṟ |
| 0.5 | l–ḻ |
| 0.2 | n–ṇ, n–ṉ, ṇ–ṉ, n–ñ, m–ṃ, n–ṃ, n–ṅ |
| 0.3 | a–ā, i–ī, u–ū, e–ē, o–ō, ṛ–ṝ |
| 0.6 | t–ṭ, ṭ–ṟ, r–l, d–ḍ |
| 0.5 | e–i, o–u, a–ai, a–au, ai–e, au–o |
| 0.3 | k–g, c–j, ṭ–ḍ, t–d, p–b |
| 0.2 | each of k g c j ṭ ḍ t d p b with itself followed by h (k–kh, g–gh, …) |
| 0.45 | k–gh, g–kh, c–jh, j–ch, ṭ–ḍh, ḍ–ṭh, t–dh, d–th, p–bh, b–ph |
| 0.3 | kh–gh, ch–jh, ṭh–ḍh, th–dh, ph–bh |
| 0.3 | s–ś, s–ṣ, ś–ṣ |
| 0.5 | c–s, c–ś |
| 0.4 | ṛ–r, ṛ–i, ṛ–u |
| 0.5 | ṛ–a |
| 0.2 | h–ḥ |
| 0.6 | v–b |

Where a pair appears twice the later row wins (none does).

**Cost of inserting or deleting a sound:** 0.6 for a vowel, 0.4 for `h` or `ḥ`, 1.0 otherwise.

`distance(x, y)`: the least total cost of turning `phonemes(x)` into `phonemes(y)` by replacements, insertions
and deletions (ordinary edit distance with these costs).

`stem(w)`: `norm(w)`; then, trying the endings `am aḥ as ai au a ā i ī u ū e ē o ō ṛ` in that order, if the
word is longer than 3 characters and ends with the ending, remove it and stop.

`pun_cost(part, word) = min(distance(part, word), distance(stem(part), stem(word)) + 0.2)`.

## 3. Seal texts

For each row of the corpus, in file order: `t` = the `text` field with spaces trimmed; `ss` = every run of
exactly three digits found in `t` by the pattern `\d{3}`, left to right, leaving out `999`. Skip the row if any
of these holds: `ss` is empty; `t` contains `[`, `]` or `/`; `dir.` is not `R/L` or `L/R`; `ss` contains `000`;
`ss` has fewer than 2 entries; `type` does not begin with `SEAL`; the same sequence `ss` has already been kept.
Otherwise keep the text as `ss` **reversed**.

## 4. The language's lists

- `info`: for each line of the parts file, `info[norm(m)]` = that line. `loans` = the settings' `drop_parts`
  plus `norm(m)` of every part whose category equals `loan_category`.
- For each name: normalise every non-empty part; then drop a part if it is in `loans`, unless it is in
  `keep_noninitial` and is not the first part (position counted before dropping). Keep the name if any part
  is left. Its weight is 1, or its stored weight if `weights` is `"stored"`.
- `words[sign]` = the set of `norm(w)` over all the sign's words. Remove from `words` the eleven number signs
  `032 033 031 001 003 017 004 055 005 013 016`.
- The number signs have the values 2, 3, 1, 1, 3, 7, 4, 12, 5, 3, 6 in that order. `fixed[sign]` = the
  settings' number word for that value (not normalised).
- If `sample_n` is given and there are more names than that: `names = random.Random(100 + seed).sample(names,
  sample_n)`.

Side analyses only: signs "left unread" are removed from `words` at this point. For "pictures shuffled" with
shuffle number `k`: sort the remaining signs, list their word sets in that order, shuffle that list with
`random.Random(600000 + k)`, and give the sets back to the sorted signs in the new order.

## 5. Splits

- `top` = the signs in `words` plus the eleven number signs. In every seal text replace a sign not in `top` by
  the token `GAP`. Keep the texts that have at most one `GAP` and at least two signs that are not `GAP`. Call
  them `seals`.
- `order = list(range(len(seals)))`; `random.Random(800 + seed).shuffle(order)`. Half 1 = the seals at the first
  `len(order) // 2` positions of `order`; half 2 = the rest.
- `scramble(names, s)`: put every part of every name into one list, in order; shuffle it with
  `random.Random(s)`; deal the parts back in order so that each name keeps its length and its weight.
- `full` = `scramble(names, 7000 + seed)` in `null` mode, the names as they are in `real` mode.
- `idx = list(range(len(full)))`; `random.Random(500 + seed).shuffle(idx)`. Names A = `full` at the first
  `len(idx) // 2` positions of `idx`; names B = the rest.
- Models A: the name model (section 6) of names A, followed by the models of `scramble(A, 3000 + i)` for
  `i` = 0 to 7. Models B: the same with names B and `4000 + i`.

## 6. The name model

Built from a list of (parts, weight). Constants: mix 0.45, 0.4, 0.15; break probability 0.3. `cat(m)` is
`info[m].category`, or `"other"` if the part is not in `info`; `stab(m)` is `info[m].stability`, or 2.

For each name, with `w = ln(1 + weight)` and the sequence `<s>`, parts…, `</s>`: for each neighbouring pair
`(a, b)` add `w` to `wb[a, b]` and to `wu[a]`; with `ca`, `cb` the categories of `a` and `b` (the edge tokens
stand for themselves) add `w` to `cb[ca, cb]` and to `cu[ca]`. For each part `m` add `w` to `mc[cat(m)][m]`.
Then `uni[m]` = the total for `m`, `uni_tot` = the sum of `uni`, `V` = the number of different parts, `ncat` =
the number of categories present plus 2.

- `freq(b) = (uni[b] + 0.5) / (uni_tot + 0.5 · V)`.
- `in_cat(m, c)`: with `cnt = mc[c]`, `tot` its sum and `n = max(1, number of parts in cnt)`:
  `emp = (cnt[m] + 0.5) / (tot + 0.5 · (n + 1))`, `flat = 1 / (n + 1)`, `a` = 0.9, 0.7 or 0.3 for stability 3,
  2 or 1; the value is `a · emp + (1 − a) · flat`.
- `mixed(a, b) = 0.45 · pw + 0.4 · pc · pm + 0.15 · pu`, where `pw = wb[a, b] / wu[a]` (0 if `wu[a]` is 0);
  `pc = (cb[ca, cb] + 0.1) / (cu[ca] + 0.1 · ncat)`; `pm` = 1 if `b` is `</s>`, else `in_cat(b, cb)`; `pu` =
  1/50 if `b` is `</s>`, else `freq(b)`.
- `lp(a, b)`, the log-probability of `b` after `a`:
  - if `b` is `GAP`: 0;
  - else if `a` is `GAP`: `ln(0.3)` if `b` is `</s>`, else `ln(freq(b))`;
  - else `p = mixed(a, b)`; if `a` is not `<s>` and `b` is not `</s>`, replace `p` by
    `0.7 · p + 0.3 · exp(ln(mixed(a, </s>) + 1e-12) + ln(mixed(<s>, b) + 1e-12))`; the value is `ln(p + 1e-12)`.

## 7. Candidates

- `counts` = how many times each part occurs in `full`. The pool is every part of at least two characters that
  occurs at least twice and is not one of the `fixed` number words, sorted.
- `signs` = the signs in `words` that occur in at least one text of `seals`, sorted.
- For each sign, its candidates are: every one of its words that is itself in the pool; and every pool part
  `m` such that, for some word `w` of the sign, the lengths of `m` and `w` in characters differ by at most 3,
  their first characters are equal, and `pun_cost(m, w) ≤ punmax`. Sort the candidates.

## 8. Choosing readings (half 1, models A)

- `slots[s]`: go through the texts of half 1 in order; for each, form `<s>`, tokens…, `</s>`; for each
  neighbouring pair `(a, b)` in order, for every sign `s` among `a` and `b` that is in `signs`, add 1 to
  `slots[s][(a, b)]`. Keep the pairs in the order first seen.
- `occ[x]` = the number of times token `x` occurs in half 1.
- `value(x)`: the reading assigned to `x` if it has one; else `fixed[x]` if `x` is a number sign; else `<s>` or
  `</s>` for themselves; else `GAP`. A sign assigned `GAP` has the value `GAP`.
- `gain(s, m)`: for each pair `(l, r)` of `slots[s]` with its count `n`: `l1` = `m` if `l` is `s`, else
  `value(l)`; `r1` likewise; `l0`, `r0` the same with `GAP` in place of `m`. For each of the nine models A,
  total `n · (lp(l1, r1) − lp(l0, r0))` over the pairs. The gain is the first model's total minus the mean of
  the other eight.
- Start with every sign assigned `GAP`. Do this twice: go through the signs in order of falling `occ` (ties in
  sorted order); for each, among its candidates not already assigned to another sign, in sorted order, take the
  one with the largest gain if that gain is above 0 (the first such on a tie), else `GAP`.

## 9. Scoring (half 2, models B)

For each text of half 2: form `<s>`, `value(x)` for each token, `</s>`; for each of the nine models B total
`lp` over neighbouring pairs; add the first model's total minus the mean of the other eight. The sum over
texts, rounded to two decimals, is the run's `heldout`.

## 10. A list's result

For a list and a seed, the **difference** is `heldout` in `real` mode minus `heldout` in `null` mode. Over a
set of seeds: the mean, median, standard deviation (with n − 1) and quartiles of the differences, and the
number of seeds whose difference is above 0 (strictly).
