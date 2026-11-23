# Göbekli Tepe's star map

Issue #92 · Lane: data in the issue; run as a model experiment (see Method) · Budget: $20 ·
Written 2026-11-23 by Claude Fable 5.2 (Anthropic), directed by Eugene

## Question

Sweatman and Tsikritsis (2017) read the animals carved on Pillar 43 at Göbekli Tepe as constellations, and from
them a date of 10,950 BC ± 250 years, the time of the proposed Younger Dryas impact. Their case rests on a
number: the chance that the carvings match the constellations by coincidence is "around one in 100 million, or
one in 5 million". That number is built from the authors' own ranking of how well each animal fits each
constellation.

**Shown the paper's own pictures and told nothing else, do independent judges rank the claimed animal as the
best fit to each constellation figure? If the paper's formula is fed their rankings in place of the authors',
what does the chance of coincidence come to?**

## Why it matters

It is the best-known claim tying the Younger Dryas impact idea to human testimony. The authors say their work
"hinges crucially on the statistical case" and that to dispute it "one must find sufficient flaws with our
statistical case" (reply to Notroff et al., 2017, p. 64). The excavators declined to discuss the statistics
(Notroff et al. 2017, p. 59). In 2024 Sweatman wrote that the statistical argument "remains unchallenged in the research"
literature, and named a way to challenge it: "One way this might be achieved is to challenge the ranking table
derived by Sweatman and Tsikritsis (2017a) that compares Göbekli Tepe's animal symbols with Stellarium's
constellation patterns, since this is based on a subjective evaluation" (accepted manuscript; `unverified`
against the version of record). A subjective ranking can be checked by asking someone who does not know what the
answer is supposed to be.

## The claim, as the paper states it

Sources are in `MANIFEST.md`. Page numbers are those of *Mediterranean Archaeology and Archaeometry* 17(1).

- The assignments (p. 239): "(vulture/eagle, scorpion, swimming bird, bending bird with wriggling fish/snake,
  wolf, lone bending bird, ibex, frog) = (Sagittarius, Scorpio, Libra, Ophiuchus, Lupus, Pisces, Gemini, Virgo)".
- The question the authors ask (Appendix, p. 245): "Given the symbolism at GT, by considering all permutations of
  the available animal symbols at GT how many configurations of Pillar 43 can be found that are a better fit
  than the current one".
- The formula (p. 245): "The probability that Pillar 43 does not represent the stated date is then simply
  2(P+1)/Q, where P is the number of permutations that are better than the" current one. With 12 animal symbols
  and 8 positions, Q is 12⁸ ("around 430 million") if a symbol may repeat, or "8! multiplied by C8X … around 20
  million" if not. "P+1 can be expressed as the product of (1 + the number of better symbols) for each position
  on Pillar 43."
- The ranking (Table 1, pp. 246–247, caption): "Ranking of animal symbols according to how well they are
  perceived to fit the corresponding constellations". Seven of the eight claimed symbols are ranked 1 for their
  constellation. The eighth, the ibex or rat for Gemini, is ranked "=2 with lion" (the cell is cut off in the
  published PDF).
- The result (p. 245): "around one in 100 million, or one in 5 million if we neglect permutations with repeated
  symbols". Checked here by hand: with P+1 = 2, 2 × 2 / 12⁸ is 1 in 107.5 million and 2 × 2 / 19,958,400 is 1 in
  4.99 million. So the published figures follow from the published ranks.

Table 1 prints a picture of each of the 12 animal symbols and a red stick figure of each of the 8 constellations.
Those 20 pictures are the stimuli of this test (`stimuli/`; the paper is CC BY 4.0).

## Method

This is a judging experiment. The judges are vision models from other vendors, called by script; the lab's
`model` lane rules apply (prompts, model IDs and dates recorded; no conclusion from a single vendor).

### Stimuli

- **Symbols:** the 12 photographs from Table 1, exactly as embedded in the paper's PDF, scaled to fit a 512 × 512
  white square. File names are neutral (`S01` … `S12`). `S01`–`S08` are the eight on Pillar 43 in the table's
  order (scorpion, bending bird, duck/goose, dog/wolf, eagle/vulture, bending bird with fish, frog, ibex/rat);
  `S09`–`S12` are the aurochs, wild boar, lion/leopard and fox.
- **Figures:** the 8 stick figures from Table 1 (`A01` … `A08`: Scorpio, Pisces, Libra, Lupus, Sagittarius,
  Ophiuchus, Virgo, Gemini), reduced to their red lines drawn in black on white, 512 × 512. The reduction removes
  the star-field background and the faint blue lines of neighbouring constellations, so that a judge is not told
  that the drawing is a constellation. The rule is in `stimuli/make_stimuli.py`.
- Orientation is as printed. The authors chose the crops, the orientations and the stick figures; the test takes
  them as given, which favours the claim.
- The claimed pairing is `A0k` with `S0k`, for k = 1 to 8.

### Judges and tasks

Judges: OpenAI `gpt-6.2-astra` (reasoning effort low), Google `gemini-4-neon` (thinking budget 512 tokens) and
xAI `grok-4.7` (defaults), all at their default temperature. Each is included only if it returns valid rankings
in at least 80% of its 80 trials. At least two must be included, or the result is "not testable". All three
accepted images and ranked made-up shapes sensibly in a plumbing test that used no picture from the paper.

- **Task A, the paper's direction.** The judge sees one figure and the 12 symbols, labelled A to L in a random
  order, and ranks all 12 by how closely the carved shape resembles the line drawing. 8 figures × 5 repetitions,
  each with its own random order.
- **Task B, the reverse.** The judge sees one of the 8 pillar symbols and the 8 figures, labelled A to H in a
  random order, and ranks all 8. 8 symbols × 5 repetitions.

The prompts (`PROMPT_A`, `PROMPT_B` in `judging/run_judges.py`) say only that the photographs show shapes carved
in stone and ask for a ranking by shape. They do not mention animals, stars, constellations, the site or any
hypothesis. Trial orders come from seed 92 and are the same for every judge (`judging/trials.json`). A reply
that does not list every option exactly once is asked again, up to twice; if still invalid the trial is dropped.

**After all ranking trials**, one more call per judge shows the 8 figures and the 12 symbols and asks what they
are and where they might come from. It measures whether the judge recognised the material. A judge that knows
the paper would be biased towards the claimed pairings, so recognition can only help the claim.

### Analysis

For each judge, `M[a][s]` is the mean rank (1 = most similar) that the judge gave symbol `s` for figure `a`,
over the valid repetitions of Task A. The pooled table is the mean of the judges' tables.

1. **Main statistic.** `S` = the mean over the 8 figures of the rank of the claimed symbol, `M[a][claimed]`.
   Chance gives 6.5; a judge who agrees with the paper gives a value near 1.
2. **Its chance distribution, exactly.** Every way of assigning 8 different symbols out of the 12 to the 8
   figures (19,958,400 ways, the paper's Q without repeats) gets the same statistic from the same table. `p` is
   the share of assignments whose statistic is at most that of the claimed one. This is the paper's own
   question, "how many configurations … are a better fit than the current one", answered with the judges'
   ranks. It is computed for each judge and for the pooled table.
3. **The paper's formula with the judges' ranks.** For each figure, the number of symbols with a strictly better
   mean rank than the claimed one; P+1 is the product of (1 + that number) over the 8 figures; the paper's
   probability is 2(P+1)/19,958,400 and 2(P+1)/12⁸.
4. **Without the scorpion.** Scorpion = Scorpius is the reading's starting point, and a scorpion drawing looks
   like the scorpion stick figure whoever judges it. Items 1 to 3 are repeated for the other 7 figures, with the
   11 other symbols (assignments of 7 out of 11).
5. **Task B.** The mean over the 8 pillar symbols of the rank given to the claimed figure (chance 4.5), with its
   exact chance distribution over the 40,320 orderings of the 8 figures.
6. For each figure: which symbol each judge ranked first, and the rank of the claimed symbol.

### Labels fixed in advance

From the pooled Task A result over all 8 figures (item 2):

| Label | Condition |
|---|---|
| **Blind judges see the claimed matches** | pooled `p ≤ 0.001`, and `p ≤ 0.01` for every included judge |
| **Blind judges do not see them** | pooled `p > 0.05` |
| **Weak or mixed** | anything else |

A second label, by the same rule, for the 7 figures without the scorpion. Both are reported; the second is the
one that bears on the paper's argument, since the first can be carried by the scorpion alone.

The number set beside the paper's "one in 5 million" is item 3's 2(P+1)/19,958,400 from the pooled table.

### Replication

A model from another vendor writes its own analysis program from this protocol and the raw rankings
(`results/rankings.tsv`), and its numbers are compared with ours.

## What would count

- **For the paper's statistical case:** "blind judges see the claimed matches" without the scorpion. The
  rankings would then be shared by judges who were told nothing. The larger question would remain: the eight
  constellations, their stick figures and their orientations were chosen by the authors after seeing the
  carvings, from a sky of 88 constellations and more asterisms, and the formula counts none of that. A test of
  it needs decoy constellations drawn in one style, and is not done here.
- **Against the paper's statistical case:** "blind judges do not see them" without the scorpion. The one-in-5-
  million figure would then rest on a ranking that independent judges do not reproduce.
- **Weak or mixed** is reported as it is.

None of these outcomes shows what the carvers meant. A pillar could record the sky without its animals looking
like our stick figures, and animals could look like stick figures by accident.

## Known weaknesses

- **The judges are models, not people.** They may weigh shapes differently from a human eye. No human panel was
  run.
- **Models may know the paper.** The recognition question measures this; it cannot remove it. The bias would
  favour the claim.
- **The pictures are the paper's.** Small, low-resolution photographs (the frog is 64 × 82 pixels), cropped and
  oriented by the authors, with white patches in three of them. Other photographs of the same carvings might be
  judged differently.
- **Reducing the stick figures to black lines** is our step. It removes context that the authors' readers had.
  Line thickness was not evened out, so figures taken from small pictures (Libra most of all) have bolder lines.
- **Only resemblance is tested.** The positions of the carvings on the pillar, which the paper says would
  strengthen its case, the dating step and the choice of constellations are not.
- **The instruction "by shape"** is ours. The authors' own criterion is how well symbols "are perceived to fit".
- **Twelve symbols.** The pool is the paper's; the carvings it left out (snakes, the squat bird, others) are not
  in it.
- **One session** designs, runs and writes up the question. A sub-agent of the same vendor gathered the sources
  and built the stimuli and the judging script.

## Budget

$20. Expected spend under $10: the judging calls, a design review by two other vendors' models, and a
replication of the analysis.
