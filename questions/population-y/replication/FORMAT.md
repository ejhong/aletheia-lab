# File formats and output layout for the replication

This note describes the input files and the output we need. It says nothing about method; the method is in
`protocol.md`. All paths are relative to `questions/population-y/`.

## Inputs

`data/aadr_v66.p1/v66.p1_1240K.aadr.patch.PUB.ind`: one line per individual, whitespace-separated:
Genetic ID, sex, group label. 23,089 lines. Line order is the order of individuals in the genotype file.

`data/aadr_v66.p1/v66.p1_1240K.aadr.patch.PUB.snp`: one line per SNP, whitespace-separated: SNP name,
chromosome (1 to 22 autosomes, 23 = X, 24 = Y, 90 = mitochondrial), genetic position in Morgans, physical
position, first allele, second allele. 1,233,013 lines. Line order is the order of SNPs in the genotype file.

`data/aadr_v66.p1/v66.p1_1240K.aadr.patch.PUB.geno`: EIGENSOFT "TGENO" (transposed packed) format, 7,117,276,654
bytes.
- Bytes 0 to 47: an ASCII header, `TGENO <n_individuals> <n_snps> <hash> <hash>`, padded with zero bytes.
- Then one record per individual, in `.ind` order. Each record is ceil(n_snps / 4) = 308,254 bytes.
- Each SNP takes 2 bits. The first SNP is in the two highest bits of the record's first byte, the second SNP in
  the next two bits, and so on.
- Values: 0, 1 or 2 = number of copies of the first allele in the `.snp` file; 3 = missing.

`data/aadr_v66.p1/v66.p1_1240K.aadr.PUB.anno`: tab-separated, UTF-8, one header line, then one line per
individual in the same order as the `.ind` file. Some fields are quoted and contain commas; a few header cells
are very long. Columns used (0-based index, start of header text):

| Index | Header starts with | Notes |
|---|---|---|
| 0 | `Genetic ID` | same as `.ind` column 1 |
| 2 | `Individual ID` | the person; several Genetic IDs can share one |
| 6 | `Publication abbreviation` | |
| 10 | `Date mean in BP` | years before 1950; 0 for present-day people; may be `..` |
| 14 | `Group ID` | use the `.ind` label where the two differ |
| 16 | `Political Entity` | country or territory |
| 17 | `Latitude` | may be `..` |
| 18 | `Longitude` | may be `..` |
| 21 | `Data type` | for example `Shotgun.diploid`, `Shotgun`, `1240k` |
| 26 | `SNPs hit on autosomal targets (Computed using easystats on 1240k snpset)` | integer |
| 47 | `ASSESSMENT` | for example `Pass`, `PROVISIONAL_PASS`, `Questionable` |

Political entities that count as "the Americas": USA, Canada, Greenland, Mexico, Belize, Guatemala, Honduras,
El Salvador, Nicaragua, Costa Rica, Panama, Colombia, Venezuela, Ecuador, Peru, Bolivia, Brazil, Chile, Argentina,
Uruguay, Paraguay, Guyana, Suriname, French Guiana, Cuba, Dominican Republic, Puerto Rico, Bahamas, Haiti,
Jamaica, Curacao, Guadeloupe, Saint Lucia, Barbados, Sint Maarten, Trinidad and Tobago. The Caribbean islands are
the entities from Cuba onward in that list.

`data/naturalearth/ne_50m_coastline.geojson`: a GeoJSON FeatureCollection of `LineString` and `MultiLineString`
features; coordinates are [longitude, latitude] and may carry a third value.

## Outputs

Write two tab-separated files with a header line.

`sets.tsv`: columns `set`, `genetic_id`. One line per member of each set. Set names:
- panel sets: `A.<label>` and `B.<label>` for the labels in the protocol (for example `A.Mbuti`, `B.Surui`),
  `A.MesoOther`, `A.Amazon`, `B.Amazon`, `B.Amazon.heldout`, `B.Pima.heldout`, `ONG`, `JAR`, `Chimp`, `Tianyuan`;
- `DUP.SGDP`, `DUP.NYGC`, `VER.AG`, `VER.SG`;
- `W.<group label>` for the world panel;
- `CELL.<REGION>.<PERIOD>`, `REGION.<REGION>`, `ANC.SA`, `ANC.NC`;
- `EARLY.<Genetic ID>` for each early individual version.

`f4.tsv`: columns `P1`, `P2`, `P3`, `P4`, `snps` (`all`, `tv` or `yri`), `mask` (free text, `-` if none),
`n_snps`, `f4`, `se`, `Z`. One line per f4 statistic, using the set names above and these names for derived sets:
- a set with one donor removed: `<set>-<Genetic ID>`, for example `A.Mixe-S_Mixe-2.DG`;
- one donor alone: `<panel>.ind.<Genetic ID>`, for example `A.ind.S_Surui-1.DG`;
- the pooled paired sets keep the names `DUP.SGDP`, `DUP.NYGC`, `VER.AG`, `VER.SG`; the Amazonian pairs are
  `DUP.SGDP.Amazon` and `DUP.NYGC.Amazon`; one person is `DUP.SGDP:<Individual ID>`, `VER.AG:<Individual ID>`
  and so on;
- the members of an ancient set of one data type: `<set>@AG` or `<set>@SG`;
- the baseline for a set: `BASE.AG-<set>` or `BASE.SG-<set>`;
- unrelated subsets: `B.Amazon.unrel`, `B.Pima.unrel` (optional).

Also write `composites.tsv` with columns `panel`, `name` (`alpha_eur`, `alpha_afr`, `P_adj`), `estimate`, `se`.
