# Review of the plan before it was locked

Two models from other vendors read `protocol.md` before any picture from the paper had been shown to a judge:
OpenAI `gpt-6.2-astra` and Google `gemini-4-neon`, on 2026-11-23, one round. Their replies are in `round1/`,
with the text they saw. Cost: $0.73 at list price. To run a round: `python3 review/run_review.py <round>` from
`questions/gobekli-star-map`.

The first plan had one test (the claimed pairing's total rank against every assignment of 8 of the 12 symbols)
and one label built on it, and fed the judges' ranks into the paper's formula as a second "probability".

| Point (who) | Done |
|---|---|
| Three different questions were mixed: are the claimed animals ranked first, is the pairing better than a shuffled one, and what does the paper's formula give (OpenAI) | Separated. Each is reported by itself; the first and second have their own labels. |
| A pairing can beat chance without a single claimed animal being ranked first (OpenAI); passing a p-value does not show the paper's ranking is reproduced (Google) | The reproduction label counts figures where the claimed symbol is the outright best. |
| Judges may simply prefer the eight pillar photographs to the four others; test the pairing within the pillar's own animals (both) | The pairing test now shuffles the pillar's symbols among the figures. The 12-symbol count is still reported. |
| The paper's formula with judges' ranks is not a probability; with ties it gives its most impressive value for an uninformative table (both) | Reported for comparison only, said not to be a probability; ties now count against the claim. |
| "Do not see them" was claimed from p > 0.05 (OpenAI) | Label renamed "pairing not better than chance in this test". |
| No competence floor before a negative result (Google) | Added: a judge must rank the scorpion photograph at 2.0 or better for the scorpion figure. |
| A judge could pass 80% of trials and still have no ranking for one figure (OpenAI) | Coverage is now per target: at least 3 valid rankings each. |
| Removing the scorpion: from the finished table or from each ranking? (both) | From each ranking, closing the gap, then averaging. Counts stated: 5,040 and 1,663,200. |
| Ties and floating point (both) | All comparisons are on exact integers; ties count as "as good". |
| What exactly does the judge see? Do identifiers leak the key? (OpenAI) | Stated: prompt, a text label per picture, and image data. No file names or ids are sent. The letter-to-picture decoding was checked on made-up shapes. |
| Low reasoning budgets and 13 pictures per call risk a false negative (Google) | OpenAI raised from low to medium; Google's thinking budget from 512 to 2,048 tokens. |
| Recognition is neither reliably measured by one question nor one-directional (OpenAI); gate the result on it (Google) | Reworded as a rough indicator; reported, not a gate. Two separate calls, figures and photographs. |
| The chance distribution is conditional on the tables; it is not "the chance of coincidence" (OpenAI) | Said so. |

Not done, and why:

- **Each judge with its own balanced orders** (Google). All judges share five random orders per target; listed
  as a weakness.
- **Pairwise calls** (one figure, one photograph at a time) as a check on many-picture overload (Google). About
  100 more calls per judge; left out for cost and time.
- **A gate on recognition** (Google). There is no clean way to tell recall of the paper from recognition of a
  scorpion.
- **Side-by-side verification of every stimulus against the page** (OpenAI) was done by the sub-agent that built
  them and by me on contact sheets, not as a recorded pixel comparison.
- **The factor of 2 in the paper's formula** (Google) is the paper's: the top-row symbols "can equally be read
  left-to-right or right-to-left". It is kept as printed.
