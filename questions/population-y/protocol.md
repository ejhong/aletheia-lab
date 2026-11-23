# The Australasian signal in the Amazon

Issue: #31 · Lane: data · Budget: $40

## Question

Some Amazonian peoples share slightly more genetic variants with Australasians (Andaman Islanders, Papuans,
Aboriginal Australians) than other Native Americans do. The proposed source is called "Population Y" or
"Ypykuéra".

1. Is that excess detectable in public genomes, and does it survive changes of method?
2. Is it specific to Australasians, or a general pull toward East Asians or non-Africans?
3. Is it closer to Onge or to Papuans, and does a 40,000-year-old East Asian show it too?
4. Among ancient Americans, does any group stand out for it, and does the ancient Pacific coast differ from the
   inland Andes?

## Why it matters

It is a place where an unexpected long-distance link from deep time shows up in public data that anyone can
re-analyse, and the literature disagrees about it.

- Skoglund et al. 2015 (*Nature* 525:104) reported it in Suruí, Karitiana and Xavante. Their Table 1 gives
  D = 0.0211 (Z = 4.26) for the tree (Yoruba, (Papuan, (Mixe, Suruí))) on whole high-coverage genomes, and D
  between 0.0072 and 0.0099 (Z between 2.6 and 3.6) on SNP arrays. D depends on which SNPs are used, so these
  numbers are not on one scale.
- Raghavan et al. 2015 (*Science* 349:aab3884) reported a related signal. Not read for this protocol.
- Yang et al. 2017 (*Current Biology* 27:3202) reported that some Native Americans share more alleles than others
  with the 40,000-year-old Tianyuan individual, as cited by Posth et al. Not read for this protocol.
- Moreno-Mayar et al. 2018 (*Science* 362:eaav2621) reported it in one 10,400-year-old individual from Lagoa
  Santa, Brazil (Sumidouro5). Known here through later papers; the article itself could not be fetched.
- Posth et al. 2018 (*Cell* 175:1185) replicated it in present-day Karitiana and Suruí and could not detect it in
  any ancient South American they tested. They wrote that this "increases the previously small chance that this
  signal—despite the strong statistical evidence for it—was a false-positive" (Discussion).
- Campelo dos Santos et al. 2022 (*Proc. R. Soc. B* 289:20221078; the 2022 preprint was read, not the final
  article) did not find it in Sumidouro5 with one comparison and did with another, and reported it in an ancient
  individual from Panama.
- Castro e Silva et al. 2021 (*PNAS* 118:e2025739118) reported it in a Pacific-coast population and proposed that
  it entered South America along the coast. With relatives removed, it lost significance in Karitiana, Suruí and
  Guaraní Kaiowá in their own analysis.
- A 2026 study of 128 Indigenous American genomes (*Nature*, doi:10.1038/s41586-026-10406-w) reported it in seven
  present-day groups and in ancient individuals back to Sumidouro5.

Aletheia link: the atlas's deep-memory and peopling-of-the-Americas cases, if any; to be checked when filing.

**What this can and cannot show.** These statistics measure whether one group shares more alleles with
Australasians than another group does. They do not identify a source population, date a contact or trace a route.
Population Y is a proposed explanation for the excess, not something observed. The papers we read attribute it to
ancestry from an unsampled population, related to Australasians, that reached the Americas from Asia. Nothing
here can show a sea crossing.

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
looked at before the lock, and no statistic was computed on unshuffled ones. Before the lock the code ran on made-up data
(`analysis/test_f4lib.py`), on technical checks of the file reader that use no American sample
(`analysis/check_reader.py`), and once end to end with every genome's SNPs shuffled independently
(`analysis/run.py --blind`). Shuffling breaks the alignment of SNPs between genomes, so no shared-ancestry signal
survives; the program read the genotypes only to shuffle them. What does survive shuffling is each genome's
overall share of reference alleles, and the blind run showed that this share differs between data sources. The
centred f4 below was added for that reason.

### Statistic

For four sets of individuals P1, P2, P3, P4:

    f4(P1, P2; P3, P4) = mean over SNPs of (p1 − p2)(p3 − p4)

- p is the frequency, in that set, of the first allele listed in the `.snp` file: the sum of genotype values (0,
  1, 2; missing ignored) over the set's individuals, divided by twice the number of individuals with data. Every
  individual with data counts equally. Single-read ("pseudo-haploid") calls are stored as 0 or 2.
- Only autosomal SNPs (chromosomes 1 to 22). A SNP is used for a statistic if all four sets have at least one
  individual with data there. Where a "common mask" is named, the SNP must also have data in every set named.
- **Sign.** f4(O, A; R, X) is positive when X shares more alleles with A than R does, measured against O. Check
  with one SNP: O = 0, A = 1, R = 0, X = 1 gives (0 − 1)(0 − 1) = +1.
- **Standard error:** weighted block jackknife. Block = (chromosome, floor(genetic position in Morgans / 0.05)),
  using column 3 of the `.snp` file as it stands. Let block j hold m_j used SNPs; drop blocks with m_j = 0; let g
  be the number left and n = Σm_j. Let θ be the statistic on all SNPs and θ_j the statistic with block j removed.
  With h_j = n/m_j, θ_J = g·θ − Σ(1 − m_j/n)·θ_j and τ_j = h_j·θ − (h_j − 1)·θ_j:
  SE² = (1/g)·Σ (τ_j − θ_J)²/(h_j − 1). The estimate reported is θ, and Z = θ/SE.
- Quantities built from several f4 values (ratios, adjusted values) use the same jackknife, removing the same
  block from every term, on a common mask of all the sets involved.
- **Confidence interval:** estimate ± 1.96 SE.
- **Centred f4.** The first allele in the `.snp` file is the reference-genome allele (checked: the reference
  sample `Href.REF` carries it everywhere). Over the SNPs used, f4 = f4c + mean(p1 − p2)·mean(p3 − p4), where
  f4c is the mean of the products minus the product of the means. The second term is not zero when the two sets
  of a pair differ in how often they carry the reference allele overall. Between differently processed data that
  mostly reflects processing: ancient reads lean toward the reference, and the two present-day pipelines differ
  too. f4c is reported beside every f4, with the same jackknife, together with mean(p3 − p4). It removes a uniform
  lean toward the reference, not one that varies from SNP to SNP. It is used in one decision rule, for the
  ancient sets.
- **SNP classes.** "tv" (transversions) drops SNPs whose two alleles are A and G, or C and T, in either order.
  "yri" keeps SNPs where the allele frequency in B.Yoruba is above 0.05 and below 0.95.
- **D** = Σ(p1 − p2)(p3 − p4) / Σ(p1 + p2 − 2·p1·p2)(p3 + p4 − 2·p3·p4) over the same SNPs, with the same
  jackknife. Reported for comparison with the papers. Decisions use f4.

### Sample sets

`analysis/sets.tsv` is the locked list of who is in each set. Its SHA-256 is in `MANIFEST.md`, committed before
the lock. `analysis/build_samples.py` builds it from the AADR `.anno` and `.ind` files alone, by these rules.

- The group label is column 3 of the `.ind` file, matched exactly; labels carry no suffix (for example `Surui`).
- "The person" is the `.anno` column "Individual ID". "SNP count" is the `.anno` column "SNPs hit on autosomal
  targets (Computed using easystats on 1240k snpset)". Ties on SNP count go to the earlier line of the file.
- "Pass" means the `.anno` ASSESSMENT is exactly `Pass`, `PROVISIONAL_PASS` or `MERGE_PASS`.
- The Americas are the political entities listed in `replication/FORMAT.md`.

**Two panels of present-day genomes.** AADR holds present-day genomes from two processing pipelines, and several
people appear in both. A panel-A set is everyone with the given label whose Genetic ID starts with `S_` or `B_`
and ends with `.DG` (Simons Genome Diversity Project processing), with a Pass. A panel-B set is everyone with the
label whose Genetic ID starts with `HGDP` and ends with `.DG` (New York Genome Center processing), with a Pass.
The labels are `Mbuti`, `Yoruba`, `Han`, `French`, `Sardinian`, `Papuan`, `Australian`, `Nasioi`, `Mixe`, `Pima`,
`Mayan`, `Piapoco`, `Quechua`, `Surui`, `Karitiana`, and for A.MesoOther `Mexico_Zapotec`, `Nahua`, `Mixtec_1` and
`Mixtec_2`.

| | Panel A | Panel B |
|---|---|---|
| Outgroups | A.Mbuti (4), A.Yoruba (3), Chimp | B.Mbuti (11), B.Yoruba (21), Chimp |
| Reference | A.Mixe (3); alternates A.MesoOther (6: labels `Mexico_Zapotec`, `Nahua`, `Mixtec_1`, `Mixtec_2`) and A.Pima (2) | B.Pima (13) |
| Amazonians | A.Surui (2), A.Karitiana (3); A.Amazon = both (5) | B.Surui (8), B.Karitiana (12); B.Amazon = both (20) |
| Australasians | A.Papuan (15), A.Australian (2), ONG (6), JAR (4) | B.Papuan (17), B.Nasioi (11), ONG, JAR |
| Controls | A.Han (3), A.French (3), A.Sardinian (3) | B.Han (43), B.French (28), B.Sardinian (28) |
| Other Americans | A.Mayan (2), A.Piapoco (2), A.Quechua (3) | B.Mayan (21), B.Piapoco (7) |

- ONG (Onge) and JAR (Jarawa) are everyone labelled `ONG` and `JAR` (Mondal et al. 2016). They come from a third
  pipeline and are used in both panels. Chimp is the Genetic ID `Chimp.REF`; Tianyuan is `Tianyuan.AG.BY.AA`.
- Panel A includes the Mixe and Suruí people behind Skoglund's Table 1, as re-called on the 1240K SNPs. The panels
  are not independent: every Amazonian in panel A is also in panel B.
- **DUP.SGDP / DUP.NYGC:** the 11 people from the labels Surui, Karitiana, Pima, Mayan and Piapoco who are in both
  panels, as processed by each pipeline.
- **B.Amazon.heldout / B.Pima.heldout:** B.Amazon and B.Pima without the people in DUP (15 and 11).
- **World panel W** (145 groups): every group label with at least two people who are present-day (date 0), outside
  the Americas, with data type `Shotgun.diploid` or `Shotgun`, a SNP count of at least 900,000 and a Pass. Labels
  containing the text `-o`, `_o`, `Ignore`, `QCremove`, `Discovery` or `outlier` (case-sensitive) are excluded, as
  are `Mbuti` and `MbutiPygmy`. A person with several versions is counted once, before the two-person rule: a
  version whose Genetic ID starts `S_` or `B_` and ends `.DG` if there is one, otherwise the highest SNP count.

**Ancient Americans.** Individuals whose political entity is in the Americas, with a date mean of 500 BP or more
(to avoid colonial-era admixture), a SNP count of at least 100,000 and a Pass. One version per person: the highest
SNP count. Each goes into a region and a period.

- Periods by date mean: EARLY ≥ 8,200; MID ≥ 4,200 and < 8,200; LATE ≥ 500 and < 4,200.
- Regions, first match wins. Individuals lacking coordinates where they are needed are left out. No Pacific island
  (Rapa Nui, Hawaii) is among the eligible individuals; had there been, it would be left out.
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
    great-circle distance (sphere of radius 6,371 km) from the site to a set of points on the Natural Earth
    coastline: each coastline segment is sampled at evenly spaced points (linear in latitude and longitude) no
    more than 5 km apart. This can overstate the true distance by up to about 2.5 km.
- Sets: each region-by-period cell (`CELL.*`, 23), each region over all periods (`REGION.*`, 10), `ANC.SA`
  (ANDES_COAST, ANDES_INLAND, EAST_SA, SOUTH_CONE and ISTHMO_NSA together) and `ANC.NC` (NAM_WEST, NAM_EAST and
  MESO together).
- **Early individuals** (`EARLY.<Genetic ID>`, 25 versions): every version of every American individual with a
  date mean of 9,000 BP or more and a SNP count of at least 250,000, whatever its assessment. Versions without a
  Pass are reported but cannot support a conclusion.

That makes 60 ancient sets.

- **VER.AG / VER.SG:** the 8 ancient Americans (date ≥ 500 BP, Pass, SNP count ≥ 400,000 in each version) who
  have both a capture version and a shotgun version; where there are several, the highest SNP count of each kind.
- **Data types of ancient genomes:** capture means the Genetic ID ends `.AG`; shotgun means it ends `.SG` and does
  not contain `.AG`. Other types (Twist capture, merged data) are left out of type-matched tests.

### Tests

Panel names: in panel A, Mbuti means A.Mbuti, Reference means A.Mixe, and so on; in panel B, Reference means
B.Pima.

**P. Primary test.**

- **P_A = f4(A.Mbuti, A.Papuan; A.Mixe, A.Amazon)**, on the locked sets as they stand. All four come from one
  pipeline.

**Support** (correlated with P_A; rules under "What would count"):

- P_B = f4(B.Mbuti, B.Papuan; B.Pima, B.Amazon): more donors, another pipeline, another Reference.
- P_B.heldout = f4(B.Mbuti, B.Papuan; B.Pima.heldout, B.Amazon.heldout): donors who are not in panel A.
- Each community alone: f4(Mbuti, Papuan; Reference, Surui) and f4(Mbuti, Papuan; Reference, Karitiana).
- Leave-one-donor-out: P_A and P_B with each Reference and Amazonian donor removed in turn.
- Anchor: D(A.Yoruba, A.Papuan; A.Mixe, A.Surui), Skoglund's Table 1 quartet.
- Block size: P_A with 10 cM blocks.
- Relatives (descriptive): KING-robust kinship for every pair within A.Mixe, A.Surui, A.Karitiana, B.Surui,
  B.Karitiana and B.Pima. For two people, over autosomal SNPs where both have data, let H1 ≤ H2 be their counts of
  heterozygous SNPs, HH the count where both are heterozygous, and OPP the count where they are opposite
  homozygotes; kinship = (HH − 2·OPP)/(2·H1) + 1/2 − (H1 + H2)/(4·H1). In each of the three panel-B sets, remove
  the donor with the most partners at kinship above 0.0884 (ties: the later one in file order) until no such pair
  is left. P_B.unrel is P_B on what remains, if at least two Amazonians and two Pima remain.

**A. Admixture check.** European or African ancestry in the Reference, or in the Amazonians, shifts P.

- Per individual (diagnostic): for each present-day American individual i in a panel, with U = that panel's
  Amazon set (without i if i belongs to it), e_i = f4(Mbuti, French; U, i) and a_i = f4(Chimp, Yoruba; U, i). An
  individual is flagged if Z(e_i) ≥ 3 or Z(a_i) ≥ 3. P.unflagged is P with flagged donors left out of the
  Reference and the Amazonians, computed if anyone is flagged and at least one donor remains on each side.
- Group level, on the common mask of Mbuti, Chimp, Papuan, French, Sardinian, Yoruba, Reference and Amazon.
  Suppose the Reference is the Amazonians' kind of Native American plus a fraction α_eur of French-like and α_afr
  of Yoruba-like ancestry. Then, writing g(S) = f4(Mbuti, Sardinian; Amazon, S) and
  h(S) = f4(Chimp, Mbuti; Amazon, S):
  - g(Reference) = α_eur·g(French) + α_afr·g(Yoruba);
  - h(Reference) = α_eur·h(French) + α_afr·h(Yoruba).
  Solve these two equations for α_eur and α_afr. Then
  - P_adj = [P − α_eur·f4(Mbuti, Papuan; French, Amazon) − α_afr·f4(Mbuti, Papuan; Yoruba, Amazon)] /
    (1 − α_eur − α_afr).
  P_adj is what P would be if the Reference's extra European and African ancestry, relative to the Amazonians,
  were simple recent mixture from those sources. It is one scenario, not a bound.

**T. Technical checks.** Each should be zero.

- T1, same people in two pipelines: f4(A.Mbuti, L; DUP.SGDP, DUP.NYGC) for L = A.Papuan, ONG, A.Han, A.French. At
  each SNP only people with data in both versions count, in both pools. Reported pooled, for the five Amazonian
  pairs together, and for each person.
- T2, same ancient people as capture and as shotgun data: f4(A.Mbuti, L; VER.AG, VER.SG) for L = A.Papuan and
  A.Han, with the same both-versions rule, pooled and per person.

**R. Robustness grid.** f4(O, A; R, X) for every combination of:

- Panel A (216 cells): O in {A.Mbuti, A.Yoruba, Chimp} × A in {A.Papuan, A.Australian, ONG, JAR} × R in {A.Mixe,
  A.MesoOther, A.Pima} × X in {A.Surui, A.Karitiana} × SNPs in {all, tv, yri}.
- Panel B (72 cells): O in {B.Mbuti, B.Yoruba, Chimp} × A in {B.Papuan, B.Nasioi, ONG, JAR} × R = B.Pima × X in
  {B.Surui, B.Karitiana} × SNPs in {all, tv, yri}.

Reported overall and per axis (median Z and median f4 for each choice on each axis). Also reported, without a
rule: the primary statistic for each Amazonian donor alone; the Reference compared with each other American group,
f4(Mbuti, Papuan; Reference, X); and Suruí against Karitiana, f4(Mbuti, Papuan; Surui, Karitiana), on all and yri
SNPs.

**S. World ranking (descriptive).** For each of the 145 world groups W: f4(Mbuti, W; Reference, Amazon) in each
panel, ranked by Z and by f4. The ranks of `ONG`, `JAR`, `Papuan`, `Nasioi` and `Australian` are reported. This is
a picture, not a test.

**L. Specificity and lineage**, in each panel, all on the common mask of Mbuti, Papuan, ONG, Han, Tianyuan,
Reference and Amazon. P_L is P recomputed on that mask.

- Han control = f4(Mbuti, Han; Reference, Amazon). A general pull of the Amazonians toward East Asians or
  non-Africans would make it positive.
- L3 = f4(Han, Papuan; Reference, Amazon) = P_L − Han control: the excess toward Papuans beyond any toward Han.
- L2 = f4(ONG, Papuan; Reference, Amazon): positive means closer to Papuans, negative closer to Onge.
- L1 = f4(Mbuti, Tianyuan; Reference, Amazon): do the Amazonians share more with Tianyuan than the Reference does?
- L4 = f4(Tianyuan, Papuan; Reference, Amazon) = P_L − L1.
- L1 and L4 are also given on transversions, since Tianyuan is ancient DNA.

**N. Ancient Americans.** Ancient genotypes differ from present-day ones in ways that can fake or hide a 1 to 2%
effect: they lean toward the reference genome, they carry chemical damage, and some are contaminated. So decisions
compare ancient groups only with other ancient groups of the same data type.

- Baseline: BASE_t = the members of ANC.NC of type t (capture: 155 people; shotgun: 53). The Caribbean is left out
  of the baseline because its ancient people descend largely from South America.
- For each ancient set G and type t with at least one member, let G_t be G's members of type t and B = BASE_t
  without the people in G. Skip if B has fewer than 10 people. On the common mask of A.Mbuti, A.Papuan, ONG,
  A.Han, A.French, B and G_t:
  - M1 = f4(A.Mbuti, A.Papuan; B, G_t), and the same with ONG in place of A.Papuan, and on transversions;
  - M3 = f4(A.Han, A.Papuan; B, G_t);
  - MF = f4(A.Mbuti, A.French; B, G_t).
- Coast against inland, capture data only, on the common mask of the same five present-day sets and both ancient
  sets: C1 = f4(A.Mbuti, A.Papuan; INLAND, COAST), C3 = f4(A.Han, A.Papuan; INLAND, COAST) and
  CF = f4(A.Mbuti, A.French; INLAND, COAST), where INLAND and COAST are the capture members of
  REGION.ANDES_INLAND and REGION.ANDES_COAST. C1 is also given on transversions.
- Descriptive only, because they compare ancient with present-day data: for each whole set G, on the common mask
  of A.Mbuti, A.Papuan, ONG, A.Han, A.French, A.Mixe, A.Amazon and G: f4(A.Mbuti, X; A.Mixe, G) for X = A.Papuan,
  ONG, A.Han and A.French, the first also on transversions, and f4(A.Mbuti, A.Papuan; G, A.Amazon).
- Detection threshold: for each tested G_t, Z*·SE(M1) divided by the P_A estimate (given only if P_A is
  positive). It is the size the measured M1 would have to reach, in units of the present-day Amazonian excess.

### Replication

A model from another vendor is given this protocol and `replication/FORMAT.md`, and writes its own program from
scratch. We run it. Every f4 statistic above is compared. Agreement means: every locked set has the same members;
the same SNP counts; f4 values differing by no more than max(0.01·|our value|, 1e-7); and Z-scores by no more than
0.1. Agreement is required for P, the support tests, A, T, L, M and C. Kinship and P_B.unrel are not required.
Disagreements are investigated and reported.

If ADMIXTOOLS 2 can be installed, P_A is also computed with it as a courtesy check.

Before the lock, models from two other vendors criticised this protocol in three rounds. Their comments and what
was changed are in `review/`.

## What would count

**Primary (P_A).** Z ≥ 3: detected. Z < 2: not detected by this test. Between: inconclusive. In every case the
estimate and interval are given. The anchor is reported beside Skoglund's array values (D of 0.0072 to 0.0099) as
a comparison, not a test, because D differs between SNP sets.

**Checks on the primary result.**
- Direction holds: at least 90% of panel A's grid cells are positive.
- Each community: Z ≥ 2 for the Suruí alone and for the Karitiana alone.
- Donors: every leave-one-donor-out estimate of P_A is at least half the full estimate.
- Admixture: Z(P_adj) ≥ 2 in panel A.
- Beyond Han: Z(L3) ≥ 2 and Z(Han control) < 3 in panel A. This shows an excess toward Papuans beyond any toward
  Han. It does not show that the excess is exclusive to Australasians.

**Beyond the original donors.** Z(P_B.heldout) ≥ 3: also detected in other donors. At least 2 and below 3: weakly.
Below 2: not detected in them. P_B, P_B.unrel, panel B's checks and the kinship between held-out and panel-A donors are
reported beside it. The held-out donors come from the same two communities, so this is not a new population.

**Technical (T).** |Z| ≥ 3 in the pooled T1 means the two pipelines disagree about the same people; differences
between panels A and B then cannot be read as biology. |Z| ≥ 3 in the pooled T2 means capture and shotgun data
disagree about the same people; it confirms the need to keep types apart.

**Lineage (L).** Reported with 95% intervals, and with the intervals divided by the P_L estimate for scale. They
are differences between affinities and nothing more.
- L2: Z ≥ 3 is the Papuan side, Z ≤ −3 the Onge side. Otherwise no difference is detected.
- L1: Z ≥ 3 means the Amazonians also share more with Tianyuan. L4: Z ≥ 3 means more with Papuans than with
  Tianyuan; Z ≤ −3 the reverse.

**Ancient (N).** Z* = Φ⁻¹(1 − 0.05/m), a Bonferroni correction, where m is the number of (set, type) pairs tested
whose members all have a Pass.
- G_t **stands out from the ancient northern baseline** if Z(M1) ≥ Z*, Z(M3) ≥ 2, |Z(MF)| < 3, the transversion
  M1 is at least half the all-SNP M1, and the centred M1 is at least half of M1. Only a Pass set can stand out. This selects a set that is
  closer to Papuans than the baseline is, more so than it is closer to Han, with no detectable difference in
  West Eurasian affinity, and whose estimate does not collapse on transversions or on centring. A real signal that comes with
  other ancestry differences can fail it, and chance alone can pass it at the stated error rate.
- Anything else is **undetermined**. A set that does not stand out has not been shown to lack the excess. Most
  single genomes are expected to land here; the detection threshold shows why.
- Sumidouro5 is judged on its Pass version, `Sumidouro5_d.SG`.
- Early presence is supported if a Pass early individual (9,000 BP or older) or an EARLY cell (8,200 BP or older)
  stands out.
- Coast: the ancient coast has more of the excess than the inland Andes if Z(C1) ≥ 3, Z(C3) ≥ 2 and |Z(CF)| < 3;
  less if Z(C1) ≤ −3, Z(C3) ≤ −2 and |Z(CF)| < 3. In both cases the centred C1 must be at least half of C1;
  if it is not, no difference is counted. If |Z(C1)| ≥ 3 but the other conditions fail, there is a
  difference whose cause is unclear. Otherwise no difference is detected. This is about the sampled ancient
  people, mostly from the last 4,000 years, and does not settle a route.

The ancient design is relative. If every ancient American carried the excess equally, nothing would be expected
to stand out.

**Headline.** Two lines.
1. For P_A: "detected and robust" if detected and all five checks pass (direction, each community, donors,
   admixture, beyond Han); "detected, with caveats" if detected and
   any check fails, naming them; "inconclusive"; or "not detected by the primary test".
2. Beyond the original donors: as above.

## Known weaknesses

- **Same people.** Panel A's key genomes are the ones the original study used, so P_A checks the data and the
  method, not a new sample of people. Panel B adds donors from the same two small, closely related communities.
- **Small sets.** Three Mixe and five Amazonians in panel A. Panel B uses Pima instead of Mixe, so a difference
  between panels could come from the Reference, the pipeline or the donors.
- **Reference choice.** Every result is relative to the Reference. The Mixe have been reported to carry ancestry
  from an otherwise unsampled Native American lineage (attributed to Moreno-Mayar et al. 2018; not checked by
  us). If the Reference is unusual, the Amazonians will look unusual.
- **Ascertainment.** The 1240K SNP set includes SNPs chosen because they vary in particular people, among them a
  Karitiana and Papuans. Which SNPs those are is not in the AADR files. Public array-design annotations might
  identify them; that was not attempted. The Suruí-alone test, the yri SNP class and the Suruí-against-Karitiana
  contrast are partial guards.
- **One method.** Everything here is one kind of allele-frequency statistic. Haplotype-based tests, which the
  original study also used, are not attempted.
- **A third pipeline.** The Onge and Jarawa genomes, and the chimpanzee reference, are processed differently from
  both panels. P_A avoids them; parts of R and L use them.
- **Admixture model.** The admixture check assumes simple mixture from French-like and Yoruba-like sources.
- **Route and source.** These statistics cannot tell a separate migration from an uneven founding population, and
  cannot identify the source. A Papuan-side L2 would not date or prove contact with Pacific islanders.
- **Ancient data.** Matching data types removes the largest known biases, not all of them: library chemistry
  differs within a type. Pools are dominated by their best-covered individuals and sites, and the baseline
  changes slightly with the set tested. Today's coastline is not the early Holocene one, and "within 75 km of the
  sea" misplaces some valley sites. Assignments are in `analysis/sets.tsv`.
- **Missing populations.** The present-day coastal and central-Brazilian groups behind the published claims are
  under controlled access and are not tested.
- **This session's priors.** The session that wrote this protocol had first read those of the papers above that
  are not marked as unread; see `log.md`. It had computed nothing.

## Budget

$40. Up to $6 for the pre-lock review by two vendors, up to $25 for the replication, the rest in reserve. Data
and compute are free.
