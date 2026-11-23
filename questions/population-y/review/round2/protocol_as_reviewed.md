# The Australasian signal in the Amazon

Issue: #31 · Lane: data · Budget: $40

## Question

Some Amazonian peoples share slightly more genetic variants with Australasians (Andaman Islanders, Papuans,
Aboriginal Australians) than other Native Americans do. The proposed source is called "Population Y" or
"Ypykuéra".

1. Is that excess detectable in public genomes, and does it survive changes of method?
2. Is it specific to Australasians, or a general pull toward non-Africans or East Asians?
3. Is it closer to Onge or to Papuans, and does a 40,000-year-old East Asian share it?
4. Among ancient Americans, which groups stand out for it, and which fall short of the Amazonian level?

## Why it matters

It is a place where an unexpected long-distance link from deep time shows up in public data that anyone can
re-analyse, and the literature disagrees about it.

- Skoglund et al. 2015 (*Nature* 525:104) reported it in Suruí, Karitiana and Xavante. Their Table 1 gives
  D = 0.0211 (Z = 4.26) for the tree (Yoruba, (Papuan, (Mixe, Suruí))) on high-coverage genomes, and D between
  0.0072 and 0.0099 (Z between 2.6 and 3.6) on arrays.
- Raghavan et al. 2015 (*Science* 349:aab3884) reported a related signal. Not read for this protocol.
- Yang et al. 2017 (*Current Biology* 27:3202) reported that the 40,000-year-old Tianyuan individual shares it, as
  cited by Posth et al. Not read for this protocol.
- Moreno-Mayar et al. 2018 (*Science* 362:eaav2621) reported it in one 10,400-year-old individual from Lagoa
  Santa, Brazil (Sumidouro5). Known here through later papers; the article itself could not be fetched.
- Posth et al. 2018 (*Cell* 175:1185) replicated it in present-day Karitiana and Suruí and could not detect it in
  any ancient South American they tested. They wrote that this "increases the previously small chance that this
  signal—despite the strong statistical evidence for it—was a false-positive" (Discussion).
- Campelo dos Santos et al. 2022 (*Proc. R. Soc. B* 289:20221078; the 2022 preprint was read, not the final
  article) did not find it in Sumidouro5 with one form of the test and did with another, and reported it in an
  ancient individual from Panama.
- Castro e Silva et al. 2021 (*PNAS* 118:e2025739118) reported it in a Pacific-coast population and proposed that
  it entered South America along the coast. With relatives removed, it lost significance in Karitiana, Suruí and
  Guaraní Kaiowá in their own analysis.
- A 2026 study of 128 Indigenous American genomes (*Nature*, doi:10.1038/s41586-026-10406-w) reported it in seven
  present-day groups and in ancient individuals back to Sumidouro5.

Aletheia link: the atlas's deep-memory and peopling-of-the-Americas cases, if any; to be checked when filing.

**What this can and cannot show.** These statistics measure whether one group shares more alleles with
Australasians than another group does. They do not identify a source population, date a contact or trace a route.
Population Y is a proposed explanation for the excess, not something observed. The published readings we have
seen place its arrival with the peopling of the Americas from Asia. Nothing here can show a sea crossing.

## Data and sources

Details and checksums are in `MANIFEST.md`.

- **Genotypes:** Allen Ancient DNA Resource (AADR) v66.p1, the public "1240K" set: 23,089 individuals (ancient and
  present-day) at 1,233,013 SNPs. Harvard Dataverse, doi:10.7910/DVN/FFIDCW, dataset version 14.0, CC0.
- **Coastline:** Natural Earth 1:50m coastline, v5.1.2, public domain. Used only to measure distance to the sea.

Not used, because access is controlled: the Human Origins array data for Brazilian groups in Skoglund 2015 (a
signed letter is required), the Castro e Silva 2021 data (EGA EGAS00001005022) and the 2026 data (EGA
EGAD50000002396). So the present-day coastal population (Chotuna) and the Xavante cannot be tested here.

## Method

Everything is computed by `analysis/` with Python 3.12 and numpy 2.3.5. No genotype of any Native American was
read before the lock. Before the lock the code ran only on made-up data (`analysis/test_f4lib.py`) and on
technical checks of the file reader that use no American sample (`analysis/check_reader.py`).

### Statistic

For four sets of individuals P1, P2, P3, P4:

    f4(P1, P2; P3, P4) = mean over SNPs of (p1 − p2)(p3 − p4)

- p is the frequency, in that set, of the first allele listed in the `.snp` file: the sum of genotype values (0,
  1, 2; missing ignored) over the set's individuals, divided by twice the number of individuals with data. Every
  individual with data counts equally. Single-read ("pseudo-haploid") calls are stored as 0 or 2.
- Only autosomal SNPs (chromosomes 1 to 22). A SNP is used for a statistic if all four sets have at least one
  individual with data there. Where a "common mask" is named, the SNP must also have data in the extra sets named.
- **Sign.** f4(O, A; R, X) is positive when X shares more alleles with A than R does. Check with one SNP: O = 0,
  A = 1, R = 0, X = 1 gives (0 − 1)(0 − 1) = +1.
- **Standard error:** weighted block jackknife. Block = (chromosome, floor(genetic position in Morgans / 0.05)),
  using column 3 of the `.snp` file as it stands. For a statistic, let block j hold m_j used SNPs with product
  sum s_j; drop blocks with m_j = 0; let g be the number of blocks left, n = Σm_j, θ = Σs_j / n,
  θ_j = (Σs − s_j)/(n − m_j), h_j = n/m_j, θ_J = g·θ − Σ(1 − m_j/n)·θ_j and τ_j = h_j·θ − (h_j − 1)·θ_j. Then
  SE² = (1/g)·Σ (τ_j − θ_J)²/(h_j − 1). The estimate reported is θ, and Z = θ/SE.
- **Confidence interval:** estimate ± 1.96 SE.
- **SNP classes.** "tv" (transversions) drops SNPs whose two alleles are A and G, or C and T, in either order.
  "yri" keeps SNPs where the allele frequency in B.Yoruba is above 0.05 and below 0.95.
- **D** = Σ(p1 − p2)(p3 − p4) / Σ(p1 + p2 − 2·p1·p2)(p3 + p4 − 2·p3·p4) over the same SNPs, with the same
  jackknife (delete-one ratio of sums, blocks weighted by m_j). Reported for comparison with the papers.
  Decisions use f4.

### Sample sets

`analysis/sets.tsv` is the locked list of who is in each set. Its SHA-256 is in `MANIFEST.md`, committed before
the lock. `analysis/build_samples.py` builds it from the AADR `.anno` and `.ind` files alone, by the rules
below. The group label is column 3 of the `.ind` file, matched exactly. "The person" is the `.anno` column
"Individual ID" (the third column). "SNP count" is the `.anno` column "SNPs hit on autosomal targets (Computed
using easystats on 1240k snpset)". "Pass" means the `.anno` ASSESSMENT is exactly `Pass`, `PROVISIONAL_PASS` or
`MERGE_PASS`. The Americas are the political entities listed in `replication/FORMAT.md`.

**Two panels of present-day genomes.** AADR holds present-day genomes from two processing pipelines, and several
people appear in both. A set in panel A takes the individuals with the given group label whose Genetic ID starts
with `S_` or `B_` and ends with `.DG` (Simons Genome Diversity Project processing), with a Pass. A set in panel B
takes those whose Genetic ID starts with `HGDP` and ends with `.DG` (New York Genome Center processing), with a
Pass.

| | Panel A | Panel B |
|---|---|---|
| Outgroups | A.Mbuti (4), A.Yoruba (3), Chimp (`Chimp.REF`) | B.Mbuti (11), B.Yoruba (21), Chimp |
| Reference | A.Mixe (3); alternates A.MesoOther (6: labels `Mexico_Zapotec`, `Nahua`, `Mixtec_1`, `Mixtec_2`) and A.Pima (2) | B.Pima (13) |
| Amazonians | A.Surui (2), A.Karitiana (3); A.Amazon = both (5) | B.Surui (8), B.Karitiana (12); B.Amazon = both (20) |
| Australasians | A.Papuan (15), A.Australian (2), ONG (6), JAR (4) | B.Papuan (17), B.Nasioi (11), ONG, JAR |
| Controls | A.Han (3), A.French (3) | B.Han (43), B.French (28) |
| Other Americans | A.Mayan (2), A.Piapoco (2), A.Quechua (3) | B.Mayan (21), B.Piapoco (7) |

ONG (Onge) and JAR (Jarawa) are all individuals labelled `ONG` and `JAR` (Mondal et al. 2016). They come from a
third pipeline and are used in both panels. Tianyuan is `Tianyuan.AG.BY.AA`. Panel A's genomes are the ones behind
Skoglund's Table 1. The panels are not independent: every Amazonian in panel A is also in panel B.

- **DUP.SGDP / DUP.NYGC:** the 11 people from the labels Surui, Karitiana, Pima, Mayan and Piapoco who are in both
  panels, as processed by each pipeline.
- **B.Amazon.heldout / B.Pima.heldout:** B.Amazon and B.Pima without the people in DUP (15 and 11).
- **World panel W** (145 groups): every group label with at least two people who are present-day (date 0), outside
  the Americas, with data type `Shotgun.diploid` or `Shotgun`, a SNP count of at least 900,000 and a Pass. Labels
  containing `-o`, `_o`, `Ignore`, `QCremove`, `Discovery` or `outlier` (case-sensitive) are excluded, as are
  `Mbuti` and `MbutiPygmy`. A person with several versions is counted once before the two-person rule: the
  panel-A version if there is one, otherwise the version with the highest SNP count.

**Ancient Americans.** Individuals whose political entity is in the Americas, with a date mean of 500 BP or more
(to avoid colonial-era admixture), a SNP count of at least 100,000 and a Pass. One version per person: the highest
SNP count. Each goes into a region and a period.

- Periods by date mean: EARLY ≥ 8,200; MID ≥ 4,200 and < 8,200; LATE ≥ 500 and < 4,200.
- Regions, first match wins. Individuals lacking coordinates where they are needed are left out.
  - NORTH: Greenland; Canada; USA at latitude ≥ 50°.
  - NAM_WEST / NAM_EAST: the rest of the USA, longitude < −100° / ≥ −100°.
  - MESO: Mexico, Belize, Guatemala, Honduras, El Salvador, Nicaragua.
  - CARIB: the Caribbean islands.
  - ISTHMO_NSA: Costa Rica, Panama, Colombia, Venezuela, Guyana, Suriname, French Guiana.
  - EAST_SA: Brazil, Paraguay, Uruguay.
  - SOUTH_CONE: Chile at latitude ≤ −30°; Argentina except the part named next.
  - ANDES_INLAND: Bolivia; Argentina with −30° < latitude < −21° and longitude < −64°; and Peru, Ecuador and
    northern Chile more than 75 km from the sea.
  - ANDES_COAST: Peru, Ecuador and Chile north of −30°, 75 km or less from the sea. Distance is the smallest
    great-circle distance (sphere of radius 6,371 km) to the Natural Earth coastline, with each coastline segment
    sampled at points no more than 5 km apart.
- Sets: each region-by-period cell (`CELL.*`, 23), each region over all periods (`REGION.*`, 10), `ANC.SA`
  (ANDES_COAST, ANDES_INLAND, EAST_SA, SOUTH_CONE and ISTHMO_NSA together) and `ANC.NCA` (NAM_WEST, NAM_EAST, MESO
  and CARIB together).
- **Early individuals** (`EARLY.<Genetic ID>`, 25 versions): every version of every American individual with a
  date mean of 9,000 BP or more and a SNP count of at least 250,000, whatever its assessment. Versions without a
  Pass are reported but cannot support a conclusion.
- **VER.AG / VER.SG:** the 8 ancient Americans (date ≥ 500 BP, Pass, SNP count ≥ 400,000 in each version) who
  have both a capture version (Genetic ID ends `.AG`) and a shotgun version (ends `.SG` and does not contain
  `.AG`); where there are several, the highest SNP count of each kind.

That makes 60 ancient sets.

### Step 1: screen for European and African admixture

Run first. It uses Mbuti, French, Yoruba, Chimp and the Americans, and no Australasian. For each present-day
American individual i in a panel, with U = that panel's Amazon set (leaving i out if i belongs to it):

- e_i = f4(Mbuti, French; U, i), a pull toward Europeans;
- a_i = f4(Chimp, Yoruba; U, i), a pull toward Africans.

An individual is dropped from every set if Z(e_i) ≥ 3 or Z(a_i) ≥ 3. If a set would fall below two people, it
keeps its unscreened members and every result that uses it is marked doubtful. From here on, the American set
names mean the screened sets. DUP, heldout, world and ancient sets are not screened, except that heldout sets drop
the same individuals.

### Step 2: tests

Panel names: Mbuti means A.Mbuti in panel A and B.Mbuti in panel B, and so on. Reference is A.Mixe or B.Pima.

**P. Primary test.**

- **P_A = f4(A.Mbuti, A.Papuan; A.Mixe, A.Amazon).** All four sets come from one pipeline.

**Supporting tests** (correlated with P_A; reported, with rules under "What would count"):

- P_B = f4(B.Mbuti, B.Papuan; B.Pima, B.Amazon): more donors, a different pipeline, a different Reference.
- P_B.heldout = f4(B.Mbuti, B.Papuan; B.Pima.heldout, B.Amazon.heldout): donors who are not in panel A.
- Anchor: D(A.Yoruba, A.Papuan; A.Mixe, A.Surui), Skoglund's Table 1 quartet on the same genomes.
- Leave-one-donor-out: P_A and P_B recomputed with each Reference and Amazonian donor removed in turn.
- Relatives (descriptive): KING-robust kinship for every pair within B.Surui, B.Karitiana and B.Pima. Starting
  from all donors, remove the donor with the most partners at kinship above 0.0884 (ties: the later one in file
  order) until no such pair is left. P_B is recomputed on what remains if at least two Amazonians and two Pima
  remain.

**T. Technical checks.** Each should be zero.

- T1, same people in two pipelines: f4(A.Mbuti, L; DUP.SGDP, DUP.NYGC) for L = A.Papuan, ONG, A.Han, A.French, and
  the same for each of the 11 people alone.
- T2, same ancient people as capture and as shotgun data: f4(A.Mbuti, L; VER.AG, VER.SG) for L = A.Papuan and
  A.Han, pooled and for each of the 8 people alone.
- T3, European-related ancestry in the comparison after screening: f4(Mbuti, French; Reference, Amazon) in each
  panel. From it, the share of P that admixture could explain: with α = f4(Mbuti, French; Amazon, Reference) /
  f4(Mbuti, French; Amazon, French), the induced value is α · f4(Mbuti, Papuan; French, Amazon), reported as a
  fraction of P.

**R. Robustness grid.** f4(O, A; R, X) for every combination of:

- Panel A (216 cells): O in {A.Mbuti, A.Yoruba, Chimp} × A in {A.Papuan, A.Australian, ONG, JAR} × R in {A.Mixe,
  A.MesoOther, A.Pima} × X in {A.Surui, A.Karitiana} × SNPs in {all, tv, yri}.
- Panel B (72 cells): O in {B.Mbuti, B.Yoruba, Chimp} × A in {B.Papuan, B.Nasioi, ONG, JAR} × R = B.Pima × X in
  {B.Surui, B.Karitiana} × SNPs in {all, tv, yri}.

Reported per axis (median Z for each choice on each axis) as well as overall. Also reported, without a rule: the
primary statistic for each Amazonian donor alone, and for the other American groups in the table.

**S. World ranking (descriptive).** For each of the 145 world groups W: f4(Mbuti, W; Reference, Amazon) in each
panel, ranked by Z and by f4. The ranks of `ONG`, `JAR`, `Papuan`, `Nasioi` and `Australian` are reported. This is
a picture, not a test.

**L. Specificity and lineage**, in each panel:

- Han control = f4(Mbuti, Han; Reference, Amazon). A general pull toward East Asians or non-Africans shows here.
- L3 = f4(Han, Papuan; Reference, Amazon): is the excess specific to Papuans relative to Han?
- L2 = f4(ONG, Papuan; Reference, Amazon): positive means the excess is closer to Papuans, negative closer to
  Onge.
- L1 = f4(Mbuti, Tianyuan; Reference, Amazon), and L4 = f4(Tianyuan, Papuan; Reference, Amazon).

**N. Ancient Americans.** Ancient genotypes differ from present-day ones in ways that can fake or hide a 1 to 2%
effect: they lean toward the reference genome, they carry chemical damage, and some are contaminated. So the
decision design compares ancient groups only with other ancient groups of the same data type.

- Types: capture (Genetic ID ends `.AG`) and shotgun (ends `.SG` and does not contain `.AG`). Other types are left
  out of this design.
- Baseline: BASE_t = the members of ANC.NCA of type t. This is ancient North and Central America and the
  Caribbean, the nearest ancient counterpart of the Mixe.
- For each ancient set G and type t with at least one member, let G_t be G's members of type t and B = BASE_t
  without the people in G. Skip if B has fewer than 10 people. On the common mask of A.Mbuti, A.Papuan, ONG,
  A.Han, A.French, B and G_t:
  - M1 = f4(A.Mbuti, A.Papuan; B, G_t), and the same with ONG and on transversions;
  - M3 = f4(A.Han, A.Papuan; B, G_t);
  - MF = f4(A.Mbuti, A.French; B, G_t).
- Against the Amazonians, for each whole set G, on the common mask of A.Mbuti, A.Papuan, A.Han, A.Amazon and G:
  - K1 = f4(A.Mbuti, A.Papuan; G, A.Amazon);
  - K3 = f4(A.Han, A.Papuan; G, A.Amazon).
- In the form used by the papers, for each whole set G, on the common mask of A.Mbuti, A.Papuan, ONG, A.Han,
  A.French, A.Mixe and G (descriptive; ancient against present-day):
  f4(A.Mbuti, A.Papuan; A.Mixe, G), f4(A.Mbuti, ONG; A.Mixe, G), f4(A.Mbuti, A.Han; A.Mixe, G),
  f4(A.Mbuti, A.French; A.Mixe, G), and the first on transversions.
- Detectability (descriptive): for each early individual, each A.Amazon donor is cut down to that individual's
  SNPs with one allele drawn at random per SNP (numpy `default_rng(31)`), and f4(A.Mbuti, A.Papuan; A.Mixe, donor)
  is computed. This shows what a present-day Amazonian looks like at that coverage. It measures loss of data, not
  ancient-DNA bias.

### Replication

A model from another vendor is given this protocol and `replication/FORMAT.md`, and writes its own program from
scratch. We run it. Agreement means: every locked set has the same members; the screen drops the same
individuals; and for P_A, P_B, P_B.heldout, T, L and M the f4 values differ by no more than the larger of 1% and
1e-7, and the Z-scores by no more than 0.1. The parts that use random numbers or kinship are not required.
Disagreements are investigated and reported.

If ADMIXTOOLS 2 can be installed, P_A is also computed with it as a courtesy check.

Before the lock, models from two other vendors criticised this protocol. Their comments and what was changed are
in `review/`.

## What would count

**Primary (P_A).** Z ≥ 3: detected. Z < 2: not detected. Between: inconclusive. If not detected, and the upper end
of the anchor's 95% interval is below D = 0.0072 (the smallest value in Skoglund's Table 1), the data count
against a signal of the published size. If the interval reaches 0.0072, the data cannot say.

**Support.**
- Donors: holds across donors if every leave-one-donor-out Z for P_A is 2 or more.
- Other donors: seen outside panel A if Z(P_B.heldout) ≥ 2.
- Admixture: clean if |Z(T3)| < 3 and admixture could explain less than half of P in that panel.

**Technical (T).** |Z| ≥ 3 in the pooled T1 means the two pipelines disagree about the same people; differences
between panels A and B then cannot be read as biology. |Z| ≥ 3 in the pooled T2 means capture and shotgun data
disagree about the same people; it confirms the need to keep types apart in N, and the paper-form ancient
statistics are then reported as unreliable.

**Robustness (R).** A panel's score is the share of grid cells that are positive and the median Z. We call it
robust if at least 90% are positive and the median Z is 2 or more. The cells are correlated, so this is a
description of consistency, not added evidence.

**Specificity (L).** Specific in a panel if |Z(Han control)| < 3 and Z(L3) ≥ 2.

**Lineage (L).** Reported with 95% intervals, as differences between affinities and nothing more.
- L2: Z ≥ 3 is the Papuan side, Z ≤ −3 the Onge side. Otherwise no difference is detected, and the interval is
  given as a fraction of P so the reader can see how large a difference could be hiding.
- L1 and L4: whether Tianyuan shares the excess, and whether Papuans share more of it than Tianyuan does.

**Ancient (N).** The threshold Z* is the one-sided 5% level corrected for the number of tests in a family. The
"stands out" family is every (set, type) pair tested; the "falls short" family is the 60 sets.
- G_t **stands out from the ancient northern baseline** if Z(M1) ≥ Z*, Z(M3) ≥ 2, |Z(MF)| < 3 and the
  transversion M1 is positive. The conjunction is there because contamination by modern Europeans lowers M1,
  extra East Asian ancestry lowers M3, and a general bias moves MF.
- G **falls short of the Amazonian level** if Z(K1) ≥ Z* and Z(K3) ≥ 2. A set can do both.
- Anything else is **undetermined**: the data cannot tell. Most single genomes are expected to land here.
- Only versions with a Pass count. Sumidouro5 is judged on its Pass version, `Sumidouro5_d.SG`.
- Early presence is supported if a Pass early individual, or an EARLY cell, stands out.
- Coast: REGION.ANDES_COAST standing out supports the sampled coastal populations having had more of the excess
  than ancient northerners. REGION.ANDES_COAST falling short counts against their having had it at Amazonian
  strength. Neither settles a route.

Limits of the ancient design, stated now: it is relative. If every ancient American carried the excess equally,
nothing would stand out. And a set that does not stand out has not been shown to lack it.

**Headline.**
- "Detected and robust in public genomes" needs all of: P_A detected; panel A robust; panel A specific; panel A's
  admixture check clean; holds across donors.
- "Detected, with caveats" if P_A is detected and any of the others fails; the failures are named.
- "Not detected in public genomes" if P_A is not detected.
- Whether it is also seen outside panel A's donors is reported beside the headline.

## Known weaknesses

- **Same people.** Panel A's genomes are the ones the original study used, so P_A checks the data and the method,
  not a new sample of people. Panel B adds donors from the same two small, closely related communities.
- **Small sets.** Three Mixe and five Amazonians in panel A. Panel B uses Pima instead of Mixe.
- **Reference choice.** Every result is relative to the Reference. If the Reference itself is unusual, the
  Amazonians will look unusual.
- **Ascertainment.** The 1240K SNP set includes SNPs chosen because they vary in particular people, among them a
  Karitiana and Papuans. The Suruí-only cells, the yri SNP class, the Han control and the leave-one-donor-out
  runs are the guards against that. They are not a proof.
- **A third pipeline.** The Onge and Jarawa genomes, and the chimpanzee reference, are processed differently from
  both panels. P_A avoids them; parts of R and L use them.
- **Route and source.** These statistics cannot tell a separate migration from an uneven founding population, and
  cannot identify the source. A Papuan-side L2 would not date or prove contact with Pacific islanders.
- **Ancient data.** Matching data types removes the largest known biases, not all of them. Pools are dominated
  by their best-covered individuals and sites. Today's coastline is not the early Holocene one, and "within 75 km
  of the sea" misplaces some valley sites. Assignments are in `analysis/sets.tsv`.
- **Missing populations.** The present-day coastal and central-Brazilian groups behind the published claims are
  under controlled access and are not tested.
- **This session's priors.** The session that wrote this protocol had read the papers listed above first; see
  `log.md`. It had computed nothing.

## Budget

$40. Up to $6 for the pre-lock review by two vendors, up to $25 for the replication, the rest in reserve. Data
and compute are free.
