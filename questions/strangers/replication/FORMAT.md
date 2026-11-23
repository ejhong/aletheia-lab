# File formats and output layout for the replication

The input files are described in `questions/population-y/replication/FORMAT.md` (included below this note when the
replicator is briefed). Paths there are relative to `questions/population-y/`; the same files are reachable from
`questions/strangers/` under `data/aadr_v66.p1/`. Run from `questions/strangers/`.

Extra `.anno` columns used here (0-based index): 11 = date standard deviation; 30 = molecular sex; 35 = Y
haplogroup; 38 = mitochondrial haplogroup; 39 = mitochondrial match interval; 42 and 43 = X-chromosome
contamination intervals; 44 = library type; 48 = assessment warnings.

## Outputs

Write these tab-separated files, with a header line, into the output folder.

`people.tsv`: one line per tested person: `genetic_id`, `side` (`american` or `elsewhere`), `type` (`AG`, `SG`,
`TW`, `other`), `neighbours` (the Genetic IDs of the 20 neighbours joined by commas, or empty).

`scan.tsv`: one line per tested person: `genetic_id`, then for each statistic that applies a pair of columns
`<name>_f4` and `<name>_Z`, empty where it does not apply. Names: `S`, `D1`, `D2` (elsewhere); `E_French`,
`E_Yoruba`, `E_Han`, `E_Papuan`, `G_French`, `G_Yoruba`, `G_Han`, `G_Papuan` (American side).

`hits.tsv`: one line per hit: `genetic_id`, `test` (`neighbours` or `absolute`), `toward` (`NA`, `French`,
`Yoruba`, `Han` or `Papuan`).

`fit.tsv`: `control`, `coefficient` for the five controls.
