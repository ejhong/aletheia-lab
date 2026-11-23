# Log

Dated entries, newest last: what was tried, what happened, what next.

## 2026-11-23: setup, design, review, lock (Claude Fable 5.2)

- Eugene made #41 active and asked for it to run end to end in the session that proposed it and ran #31. That
  session's priors: it knows #31's results (no ancient American group stood out for Australasian affinity; the
  Greenland Norse and Marianas people were found among #31's "ancient Americans" through labelling).
- **Metadata read before the lock:** the `.anno` and `.ind` files, to build `analysis/people.tsv`. 12,977 tested
  people; 728 on the American side; 11,583 have neighbours for test 1. Egypt has 2 people, Mesopotamia 11, no
  Indus city has any after the filters.
- **Review:** one round by OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` ($1.08). It showed the first design
  could not see a foreign community buried together and could not see an African at all in its fallback. The
  protocol and code were rewritten; see `review/README.md`. The rewrite was not re-reviewed.
- **Blind runs:** `scan.py all --blind` twice (once per design), on genomes with SNPs shuffled. On the final
  design: no hits; the residual S has mean 0.00 and standard deviation 0.99 over 11,110 people; the plain
  absolute statistics on the American side reach Z = 25 from reference-allele share alone, and the centred guard
  removes all of them. Runtime about four minutes.
- **Lock:** after this entry.

## 2026-11-23: locked run, amendments, replication (Claude Fable 5.2)

- **Locked run** (`results/`): 174 people flagged. American side: 11 Greenland Norse and 4 Arctic people.
  Elsewhere: 159, nearly all Siberian and steppe.
- **Amendment 1** (written and pushed before running): a test of whether a hit is closer to Native Americans
  than to the Altai hunter-gatherers. 27 of 152 robust hits pass.
- **Exploratory** (`explore/profile.py`): whom the unexpected hits lean toward. The Italian and Moroccan farmers
  lean away from Native Americans on the raw comparison; the Romanian woman leans toward Native Americans and
  East Asians.
- **Replication** (OpenAI `gpt-6.2-astra`): ran first time. Differences traced to (a) a definition missing from
  our brief, supplied in a second message with nothing else; (b) 219 people of mixed data types whom our code
  left out of the neighbours test; (c) our shared SNP mask for the American-side statistics.
- **Amendment 2**: first as an added test for the 219 with the locked weights (`results/amended/other_type.*`),
  then revised: the whole scan rerun with them (`results/corrected/`), because the protocol's fit includes them.
  One line of `scan.py` was changed so the made-up strangers step skips recipients without donors.
- **Corrected run:** 178 people flagged; the replication gives the same 183 hit rows. Classes in
  `results/corrected/hits_review.tsv`: 38 known, 1 metadata error, 127 not specific, 3 unlike neighbours, 8 not
  robust, 1 standing (`PIE069.AG`).
- **Not done:** asking the laboratory about `PIE069.AG` (outward-facing; Eugene's call). Filing with Aletheia.
- **Spent:** $1.89 of $30.

## 2026-11-23: the standing hit re-examined (Claude Fable 5.2)

- Eugene asked why the Pietrele woman's lean had been put down to contamination and not taken as possibly real.
  The first write-up had assumed it. Corrected: the mitochondrial match in the release argues against
  contamination, and the three readings are now ranked by support.
- Her reads are public (ENA PRJEB62503, ERR11495483). **Amendment 3** written and pushed, then run: the lean is
  in her long fragments (Z 6.5) and weak in her short ones (Z 1.5); long minus short Z 4.1. Outcome by the rule:
  the lean sits in the long molecules, the pattern of modern contamination.
- Exploratory controls after the result: four site-mates show no gradient (Z 1.1, 0.5, −0.1, 1.2).
- The damage-based test could not be run: the public file masks the end bases.
- A download script joined two short pieces into a corrupt file once; caught by size, redone with a checksum
  check before joining. The archive was slow and dropped connections; no data were affected.
