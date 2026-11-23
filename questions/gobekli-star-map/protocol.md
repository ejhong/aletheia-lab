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

Judges: OpenAI `gpt-6.2-astra` (reasoning effort medium), Google `gemini-4-neon` (thinking budget 2,048 tokens)
and xAI `grok-4.7` (defaults), all at their default temperature, with no tools and no memory between calls. All
three accepted images and ranked made-up shapes sensibly in a plumbing test that used no picture from the paper.

- **Task A, the paper's direction.** The judge sees one figure and the 12 symbols, labelled A to L in a random
  order, and ranks all 12 by how closely the carved shape resembles the line drawing. 8 figures × 5 repetitions,
  each with its own random order.
- **Task B, the reverse.** The judge sees one of the 8 pillar symbols and the 8 figures, labelled A to H in a
  random order, and ranks all 8. 8 symbols × 5 repetitions.

The prompts (`PROMPT_A`, `PROMPT_B` in `judging/run_judges.py`) say only that the photographs show shapes carved
in stone and ask for a ranking by overall shape. They do not mention animals, stars, constellations, the site or
any hypothesis. A request holds the prompt, a short text label before each picture ("Line drawing:",
"Photograph A:" …) and the pictures themselves as image data; no file name, caption or identifier is sent. Trial
orders come from seed 92 and are the same for every judge (`judging/trials.json`, 80 trials).

**Invalid replies.** A reply is valid if it lists every option exactly once. An invalid reply is asked again in a
fresh call with the same pictures and order, up to twice; the first valid reply counts and every attempt is
kept. If none is valid the trial is dropped.

**Which judges count.** A judge counts for a task only if every target of that task (each figure in Task A, each
symbol in Task B) has at least 3 valid rankings. A judge must also pass a **competence check**: in Task A it
must give the scorpion photograph a mean rank of 2.0 or better for the scorpion figure. That pairing is the
reading's starting point and the one resemblance nobody disputes; a judge that cannot see it is not measuring
resemblance, and is left out. At least two judges must count for Task A, or the result is "not testable".

**After all ranking trials**, two more calls per judge: one shows the 8 figures and asks what they are and
whether the judge has seen them before; the other shows the 12 photographs and asks where the carvings are from
and whether the judge knows of a published claim about them. The replies are reported. They are a rough
indicator: a judge may hold an association it does not report. A judge that knows the paper would more likely be
pushed towards its pairings than away from them, so recognition makes a failure to reproduce them more telling
and a success less.

### Analysis

All arithmetic on ranks is exact (integers; `analysis/analyse.py`).

**Tables.** For a judge, the mean rank of symbol `s` for figure `a` is the mean, over that judge's valid Task A
rankings of `a`, of the position of `s` (1 = most similar). The pooled table is the mean of the judges' tables,
each judge counting equally whatever its number of valid rankings.

**Without the scorpion.** The scorpion is the reading's premise, and its match would carry any test alone. For
the main results the scorpion figure is set aside and the scorpion photograph is removed from every ranking,
closing the gap, so that the other 11 symbols are ranked 1 to 11; means are then taken as above. This leaves 7
figures and their 7 claimed symbols among 11.

Three things are reported, and they are different questions:

1. **Do the judges reproduce the paper's ranking?** The paper ranks the claimed symbol first for six of these
   seven figures and equal second for the seventh. Count the figures, out of 7, for which the claimed symbol
   has the best pooled mean rank outright (a tie for best does not count). Also given: each figure's best
   symbol or symbols, the claimed symbol's mean rank, and the same per judge.

   | Label | Condition |
   |---|---|
   | **Blind judges largely reproduce the paper's ranking** | 5 or more of 7 |
   | **Blind judges partly reproduce the paper's ranking** | 3 or 4 |
   | **Blind judges do not reproduce the paper's ranking** | 2 or fewer |

2. **Is the claimed pairing better than a shuffled one?** Hold the pooled table fixed. Among the 5,040 ways of
   pairing the 7 figures with the 7 pillar symbols, one to one, `p` is the share whose total mean rank is as
   good as the claimed pairing's or better (ties count as "as good"). This asks: given the animals that are on
   the pillar, did the judges put each with its claimed figure? It is a statement about these judges and these
   pictures; it is not the chance that the pillar's carvings match the sky by accident.

   | Label | Condition |
   |---|---|
   | **Blind judges pair the pillar's animals with the claimed figures better than chance** | pooled `p ≤ 0.01`, and `p ≤ 0.05` for each judge |
   | **Pairing not better than chance in this test** | pooled `p > 0.05` |
   | **Weak or mixed** | anything else |

   Also given: the same share among all 1,663,200 ways of assigning 7 different symbols out of the 11 (the
   paper's own way of counting, which also credits the judges for preferring the pillar's animals to the four
   others), and both shares with the scorpion included (8 figures; 40,320 pairings; 19,958,400 assignments).

3. **The paper's formula with the judges' ranks.** For each of the 8 figures, the number of other symbols whose
   pooled mean rank is as good as the claimed one's or better; P+1 is the product of (1 + that number);
   2(P+1)/19,958,400 and 2(P+1)/12⁸. This is what the paper's own arithmetic gives when its ranks are replaced
   by the judges'. It is shown beside the paper's "one in 5 million" for comparison and is not a probability of
   anything: the product counts choices that reuse a symbol, and the formula takes the eight constellations as
   given.

**Task B** is reported the same way from the other direction (for each pillar symbol, the mean rank of each
figure): the number of symbols whose claimed figure is the outright best, and the share of the 5,040 pairings as
good as the claimed one, without the scorpion; and both with it. It has no label.

Also reported: the correlation between judges' tables, as a measure of whether they agree with one another.

### Replication

A model from another vendor writes its own analysis program from this protocol and the raw rankings
(`results/rankings.tsv`), and its numbers are compared with ours.

## What would count

- **For the paper's statistical case:** "largely reproduce" together with "better than chance". The rankings
  would then be shared by judges who were told nothing. The larger question would remain: the eight
  constellations, their stick figures and their orientations were chosen by the authors after seeing the
  carvings, from a sky of 88 constellations and more asterisms, and the formula counts none of that. A test of
  it needs decoy constellations drawn in one style, and is not done here.
- **Against the paper's statistical case:** "do not reproduce". The one-in-5-million figure is built on the
  claimed symbols being ranked first; if independent judges do not rank them first, the figure has no
  independent support, whatever the pairing test says.
- **In between:** "partly reproduce", or "do not reproduce" with a pairing that is still better than chance,
  would mean the judges see some of the resemblances and not the ranking the number needs. Reported as it is.

None of these outcomes shows what the carvers meant. A pillar could record the sky without its animals looking
like our stick figures, and animals could look like stick figures by accident.

## Known weaknesses

- **The judges are models, not people.** They may weigh shapes differently from a human eye. No human panel was
  run.
- **Models may know the paper.** The recognition questions give a rough indication; they cannot remove the
  problem or prove its absence.
- **Twelve pictures at once is hard for a model.** A judge may attend unevenly to them. The competence check and
  the agreement between judges are the guards; five repetitions per figure is a small number.
- **Shared trial orders.** All judges see the same five random orders per target.
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

## Review before the lock

One round by OpenAI `gpt-6.2-astra` and Google `gemini-4-neon`; the reviews are in `review/`, and
`review/README.md` lists what was changed and what was not.

## Budget

$20. Expected spend about $12: the judging calls, a design review by two other vendors' models, and a
replication of the analysis.
