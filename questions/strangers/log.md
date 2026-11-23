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
