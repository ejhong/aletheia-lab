# The Australasian signal in the Amazon

Issue: #31 · Lane: data · Budget: $40

## Question

Some Amazonian peoples share slightly more genetic variants with Australasians (Andaman Islanders, Papuans,
Aboriginal Australians) than other Native Americans do. The source is called "Population Y" or "Ypykuéra".

1. Does that excess show up in public genomes, and does it survive changes of method?
2. Is it specific to Australasians?
3. Which living lineage is it closest to?
4. Where and when does it appear among ancient Americans?

## Why it matters

It is the one place where an unexpected long-distance link from deep time shows up in public data that anyone can
re-analyse. The literature disagrees about it:

- Skoglund et al. 2015 (*Nature* 525:104) reported it in Suruí, Karitiana and Xavante, at about Z = 3 to 4.6.
- Moreno-Mayar et al. 2018 (*Science* 362:eaav2621) reported it in one 10,400-year-old individual from Lagoa
  Santa, Brazil (Sumidouro5).
- Posth et al. 2018 (*Cell* 175:1185) replicated it in present-day Suruí and Karitiana, found it in none of the
  ancient individuals it tested, and wrote that it might be a false positive.
- Campelo dos Santos et al. 2022 (*Proc. R. Soc. B* 289:20221078; preprint read) did not find it in Sumidouro5 with
  one form of the test and did with another.
- Castro e Silva et al. 2021 (*PNAS* 118:e2025739118) reported it in a Pacific-coast population and proposed that
  it entered South America along the coast. In their own analysis it lost significance in Suruí and Karitiana
  when relatives were removed.
- A 2026 study of 128 Indigenous American genomes (*Nature*, doi:10.1038/s41586-026-10406-w) reported it in seven
  present-day groups and in ancient individuals back to Sumidouro5.

Aletheia link: the atlas's deep-memory and peopling-of-the-Americas cases, if any; to be checked when filing.

What this cannot show: a sea crossing. Every published reading has the ancestry arriving with people who walked or
paddled in from Asia by way of Beringia. A confirmed signal means an extra strand in the founding ancestry, not a
lost civilisation.

## Data and sources

Details and checksums are in `MANIFEST.md`.

- **Genotypes:** Allen Ancient DNA Resource (AADR) v66.p1, the public "1240K" set: 23,089 individuals (ancient and
  present-day) at 1,233,013 SNPs. Harvard Dataverse, doi:10.7910/DVN/FFIDCW, dataset version 14.0, CC0.
- **Coastline:** Natural Earth 1:50m coastline, v5.1.2, public domain. Used only to measure distance to the sea.

Not used, because access is controlled: the Human Origins array data for Brazilian groups in Skoglund 2015 (a
signed letter is required), the Castro e Silva 2021 data (EGA EGAS00001005022) and the 2026 data (EGA
EGAD50000002396). So the present-day coastal population (Chotuna) and the Xavante cannot be tested here.

## Method

Everything is computed by `analysis/` with Python 3.12 and numpy 2.3.5, from the files above. No genotype of any
Native American was read before the lock. Before the lock the code ran only on made-up data
(`analysis/test_f4lib.py`) and on technical checks of the file reader that use no American sample
(`analysis/check_reader.py`).

### Statistic

For four sets of individuals P1, P2, P3, P4:

    f4(P1, P2; P3, P4) = mean over SNPs of (p1 − p2)(p3 − p4)

- p is the frequency, in that set, of the first allele listed in the `.snp` file. Each genotype counts as two
  chromosomes, including the single-read ("pseudo-haploid") calls of ancient samples, which are stored as 0 or 2.
- Only autosomal SNPs (chromosomes 1 to 22) are used. A SNP is used for a statistic if all four sets have at least
  one individual with data there.
- **Sign.** We always write f4(Outgroup, A; Reference, X). A positive value means X shares more alleles with A
  than the Reference does.
- **Standard error:** weighted block jackknife (Busing et al. 1999). Blocks are 5 centimorgans: within each
  chromosome, block = floor(genetic position in Morgans / 0.05). Blocks are weighted by the number of SNPs used.
  The estimate is the full-data value, and Z = estimate / standard error.
- **Transversions only** means dropping SNPs whose two alleles are A/G or C/T.
- The matching D statistic (sum of numerators over sum of (p1 + p2 − 2·p1·p2)(p3 + p4 − 2·p3·p4)) is reported
  beside each f4 for comparison with the papers. Decisions use f4.

### Sample sets

Built by `analysis/build_samples.py` from the AADR `.anno` and `.ind` files alone, and written to
`analysis/sets.tsv`. The group label is the one in the `.ind` file. "Pass" means the AADR assessment is `Pass`,
`PROVISIONAL_PASS` or `MERGE_PASS`.

**Two panels of present-day genomes.** AADR holds present-day genomes from two processing pipelines, and several
people appear in both. Mixing pipelines inside one comparison can create false signals, so each panel uses one
pipeline for its outgroup, Reference and X.

| | Panel A | Panel B |
|---|---|---|
| Pipeline | Simons Genome Diversity Project: Genetic ID starts `S_` or `B_`, ends `.DG` | New York Genome Center HGDP: starts `HGDP`, ends `.DG` |
| Outgroups | A.Mbuti (4), A.Yoruba (3), Chimp (`Chimp.REF`) | B.Mbuti (11), B.Yoruba (21), Chimp |
| Reference | A.Mixe (3); alternate A.MesoOther (6: `Mexico_Zapotec`, `Nahua`, `Mixtec_1`, `Mixtec_2`) | B.Pima (13) |
| Amazonians | A.Surui (2), A.Karitiana (3); A.Amazon = both (5) | B.Surui (8), B.Karitiana (12); B.Amazon = both (20) |
| Australasians | ONG (6), JAR (4), A.Papuan (15), A.Australian (2) | ONG, JAR, B.Papuan (17), B.Nasioi (11) |
| Controls | A.Han (3), A.French (3) | B.Han (43), B.French (28) |
| Other Americans | A.Pima (2), A.Mayan (2), A.Piapoco (2), A.Quechua (3) | B.Mayan (21), B.Piapoco (7) |

ONG (Onge) and JAR (Jarawa) are the Andamanese genomes of Mondal et al. 2016; they exist in one pipeline only and
are used in both panels. Tianyuan is `Tianyuan.AG.BY.AA`, a 40,000-year-old individual from China. Panel B has no
Mixe, so its Reference is the Pima. The panels are not independent: all of panel A's Amazonians are also in
panel B.

**World panel W** (145 groups). Every group label with at least two present-day individuals (date 0) outside the
Americas, with shotgun data, at least 900,000 SNPs and a Pass. Labels containing `-o`, `_o`, `Ignore`, `QCremove`,
`Discovery` or `outlier` are excluded, as are `Mbuti` and `MbutiPygmy`. A person present in both pipelines is
counted once (the SGDP version, otherwise the one with more SNPs).

**Ancient Americans.** Individuals whose political entity is in the Americas, dated at least 500 years before
1950 (to avoid colonial-era admixture), with at least 100,000 SNPs and a Pass. One version per individual, the one
with the most SNPs. Each goes into a region and a period:

- Periods: EARLY (8,200 BP or older), MID (4,200 to 8,200 BP), LATE (500 to 4,200 BP).
- Regions, first match wins:
  - NORTH: Greenland, Canada, and USA at latitude 50° or more.
  - NAM_WEST / NAM_EAST: rest of the USA, west / east of longitude −100°.
  - MESO: Mexico, Belize, Guatemala, Honduras, El Salvador, Nicaragua.
  - CARIB: the Caribbean islands.
  - ISTHMO_NSA: Costa Rica, Panama, Colombia, Venezuela, the Guianas.
  - EAST_SA: Brazil, Paraguay, Uruguay.
  - ANDES_COAST: Peru, Ecuador, and Chile north of 30°S, within 75 km of the sea.
  - ANDES_INLAND: the same countries farther inland, Bolivia, and Argentina between 21°S and 30°S west of −64°.
  - SOUTH_CONE: Chile south of 30°S and the rest of Argentina.
- Sets: each region-by-period cell (`CELL.*`, 23 cells), each region over all periods (`REGION.*`, 10), all of
  South America together (`ANC.SA`: ANDES_COAST, ANDES_INLAND, EAST_SA, SOUTH_CONE, ISTHMO_NSA) and all of North
  and Central America together (`ANC.NCA`: NAM_WEST, NAM_EAST, MESO, CARIB).
- **Early individuals** (`EARLY.*`, 25): every version of every American individual dated 9,000 BP or older with
  at least 250,000 SNPs, whatever its assessment. This includes Anzick, the Ancient Beringian USR1, Spirit Cave
  (AHUR_2064), Los Rieles, Lapa do Santo and the Sumidouro individuals.

That makes 60 ancient sets.

### Tests

**T. Technical checks.** Each should be zero.

- T1, same people in two pipelines: f4(A.Mbuti, L; DUP.SGDP, DUP.NYGC) for L = ONG, A.Papuan, A.Han, A.French.
  DUP is the 11 Native American individuals present in both pipelines.
- T2, same ancient individuals as capture and as shotgun data (8 individuals): f4(A.Mbuti, ONG; VER.AG, VER.SG)
  and f4(A.Han, ONG; VER.AG, VER.SG).
- T3, European admixture in the comparison: f4(A.Mbuti, A.French; A.Mixe, A.Amazon),
  f4(A.Mbuti, A.French; A.Mixe, A.MesoOther) and f4(B.Mbuti, B.French; B.Pima, B.Amazon).

**P. Primary test: does the signal replicate?**

- P_A = f4(A.Mbuti, ONG; A.Mixe, A.Amazon)
- P_B = f4(B.Mbuti, ONG; B.Pima, B.Amazon)

**R. Robustness grid.** The same statistic with every combination of:

- Panel A (96 cells): outgroup {A.Mbuti, A.Yoruba, Chimp} × Australasian {ONG, JAR, A.Papuan, A.Australian} ×
  Reference {A.Mixe, A.MesoOther} × X {A.Surui, A.Karitiana} × SNPs {all, transversions}.
- Panel B (48 cells): outgroup {B.Mbuti, B.Yoruba, Chimp} × Australasian {ONG, JAR, B.Papuan, B.Nasioi} ×
  Reference {B.Pima} × X {B.Surui, B.Karitiana} × SNPs {all, transversions}.

Reported without a decision rule: the primary statistic for each Amazonian individual alone, and for the other
American groups in the table (with ONG and with Papuan).

**S. Specificity.** For each of the 145 world groups W: f4(A.Mbuti, W; A.Mixe, A.Amazon) and
f4(B.Mbuti, W; B.Pima, B.Amazon). Rank the groups by Z within each panel. The five Australasian groups are ONG,
JAR, Papuan, Nasioi and Australian.

**L. Lineage.** In each panel (Papuan = A.Papuan or B.Papuan, and so on):

- L1 = f4(Mbuti, Tianyuan; Reference, Amazon): does the 40,000-year-old Tianyuan individual share the excess?
- L2 = f4(ONG, Papuan; Reference, Amazon): is the excess closer to Onge (positive) or to Papuans (negative)?
- L3 = f4(Han, ONG; Reference, Amazon): is the excess specific to Onge relative to Han?
- L4 = f4(Tianyuan, ONG; Reference, Amazon).
- Control: f4(Mbuti, Han; Reference, Amazon), expected to be zero.

**N. Ancient Americans.** For each of the 60 ancient sets G:

- N1 = f4(A.Mbuti, ONG; A.Mixe, G), the form used in the papers, and the same with A.Papuan.
- N2 = f4(A.Mbuti, A.Han; A.Mixe, G), a control. Ancient data lean toward the reference genome, which can make an
  ancient sample look closer to *any* non-African. That bias would show up here too.
- **N3 = f4(A.Han, ONG; A.Mixe, G)**, the decision statistic. It equals N1 − N2, so the bias cancels.
- N4 = f4(A.Han, ONG; G, A.Amazon): do present-day Amazonians have more of the excess than G?
- N3 on transversions only, as a check against ancient DNA damage.

### Replication

A model from another vendor is given this protocol and a description of the file formats, and writes its own
program from scratch. We run it. Agreement means: every set has the same members, and for P_A, P_B and the L and T
statistics the f4 values agree within 1% and the Z-scores within 0.1. Disagreements are investigated and reported.

If ADMIXTOOLS 2 can be installed, P_A and P_B are also computed with it. This is a courtesy check; nothing depends
on it.

Before the lock, models from two other vendors are asked to criticise this protocol. Their comments and what was
changed are kept in `review/`.

## What would count

**Primary (P).**
- For: the larger of Z(P_A), Z(P_B) is 3 or more and the other is positive. The signal replicates.
- Against: both are below 2. The signal does not replicate in public genomes.
- Inconclusive: anything else.

**Technical (T).** A T1 or T2 statistic with |Z| of 3 or more means comparisons that mix those data types are
unsafe. P and R stay within one pipeline and are unaffected. The ancient results (N) are then reported as
unreliable unless N2 is near zero for the set in question. A T3 statistic with |Z| of 3 or more means the
Reference or the Amazonians carry European-related ancestry unevenly, and the affected panel's P result is
reported as doubtful.

**Robustness (R).** A panel's signal is robust if at least 90% of its grid cells are positive and the median Z
across cells is 2 or more. Robust in both panels: robust. In one: partly robust. In neither: not robust.

**Specificity (S).** In a panel, the excess is Australasian-specific if at least four of the five Australasian
groups are among the ten highest of the 145. Both panels: specific. One: partly. Neither: not specific.

**Lineage (L).** Threshold |Z| of 3 or more, read per panel.
- L1 positive: an ancient East Asian shares the excess, so its source is an old Asian lineage and not specifically
  an Oceanian one.
- L2 near zero: the source is equally related to Onge and Papuans, which is what an old, deep lineage predicts.
  L2 strongly negative (Papuan side) would be what recent contact with Pacific islanders predicts.
- L3 positive: the excess is not a general pull toward East Eurasians.

**Ancient (N).** Threshold: Z of 3.15 or more, which is the one-sided 5% level corrected for 60 sets.
- A set **carries the signal** if Z(N3) ≥ 3.15.
- A set **lacks the Amazonian level** if Z(N4) ≥ 3.15 and Z(N3) < 2.
- Otherwise it is **uninformative**: the data cannot tell. Most single genomes are expected to land here, because
  the effect is about 1 to 2% of ancestry.
- Sumidouro5: the published claim replicates if Z(N1) ≥ 3 in either of its two versions, fails if both are below
  2, and is unresolved otherwise.
- Early presence: supported if any EARLY cell or early individual carries the signal.
- Coast: REGION.ANDES_COAST carrying the signal supports a coastal population having had it. REGION.ANDES_COAST
  lacking the Amazonian level counts against the sampled coastal populations having had it at Amazonian strength.
  That would not rule out a coastal route, since the published model has the signal rising by drift after the
  Amazonian branch formed.

**Headline.** "Real and robust in public data" requires: P replicates, R is robust or partly robust, and the T3
check is clean for the panel that replicates. If P fails, the headline is that it does not replicate.

## Known weaknesses

- **Same people.** The Suruí and Karitiana genomes are from the same HGDP donors the original studies used, so
  this checks the data and the method, not a new sample of people. Both groups are small and closely related.
- **Small Reference.** Panel A's Mixe are three people. Panel B uses Pima instead of Mixe.
- **Route.** These statistics cannot tell a separate migration from an uneven founding population. Both leave the
  same trace. The ancient results can only say when and where the trace is visible.
- **Power.** One ancient genome can rarely detect a 1 to 2% effect. "Uninformative" is not "absent".
- **Ancient data biases.** N3 removes reference bias to first order only. The Onge genomes come from one pipeline.
  Contamination from modern people would pull N3 down and could hide a real signal.
- **Crude geography.** "Within 75 km of the sea" misplaces some valley sites. The assignments are in
  `analysis/sets.tsv` for inspection.
- **Missing populations.** The present-day coastal and central-Brazilian groups that carry the claim are under
  controlled access and are not tested.
- **This session's priors.** The session that wrote this protocol had read the papers listed above first; see
  `log.md`. It had not computed anything.

## Budget

$40. Up to $6 for the pre-lock review by two vendors, up to $25 for the replication, the rest in reserve. Data
and compute are free.
