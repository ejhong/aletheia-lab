# Strangers in the ancient-DNA record

Issue: #41 · Lane: data · Budget: $30

## Question

Before Columbus, was anyone buried on one side of the Atlantic or Pacific whose DNA belongs on the other?

1. **The scan.** In one public release of ancient DNA, is there a person buried outside the Americas who looks
   Native American, or one buried in the Americas who looks European, African, East Asian or Oceanian, either
   outright or compared with the people buried around them?
2. **The centres.** Do the people of early American civilisations (Classic Mesoamerica, the Andes) lean toward
   Old World peoples more than their neighbours do, and do the people of early Old World centres lean toward
   Native Americans more than their neighbours do?

## Why it matters

The idea of a lost seafaring civilisation that seeded cultures on several continents predicts that people, or
their descendants, crossed the oceans long before Columbus. A uniform search of a large public release is a
direct, if partial, test. The odds of a hit are low. One robust hit would be a person to look at very hard.

Contact across the Pacific is not only a fringe idea. Two studies report genetic evidence that Polynesians and
Native Americans met before Europeans arrived (Ioannidis et al. 2020, *Nature*; a 2024 *Nature* study of ancient
Rapa Nui). Neither was read for this protocol. Their evidence is admixture in later people, not a dated burial on
the far shore, so they are context here, not cases the scan must find.

Aletheia link: the atlas's lost-civilisation and transoceanic-contact cases, if any; to be checked when filing.

**What this can and cannot show.** It can find people who are outliers by these tests. It cannot find a visitor
who left no trace among the sampled dead, it cannot see places and periods with no samples, and a hit does not
say when, how or in which direction anyone travelled. In this release, after the filters below, Egypt has two
people, Mesopotamia a handful, and no Indus city has any.

## Data and sources

Allen Ancient DNA Resource (AADR) v66.p1, public 1240K set: the same files as question #31, with the same
checksums (`MANIFEST.md`). It is one release of mostly targeted SNP data, not every ancient genome ever published.

## Method

Computed by `analysis/` with Python 3.12 and numpy 2.3.5. `analysis/people.tsv` and `analysis/refs.tsv` are the
locked lists of who is tested, on which side, with which neighbours and references; their hashes are in
`MANIFEST.md`. Before the lock the code ran on made-up data (`analysis/test_scan.py`) and end to end with every
genome's SNPs shuffled (`scan.py all --blind`). No statistic was computed on unshuffled genomes before the lock.

### Statistic

f4(P1, P2; P3, P4) is the mean over autosomal SNPs of (p1 − p2)(p3 − p4), where p is the frequency of the first
allele in the `.snp` file (the reference-genome allele). In a set of people every person with data counts
equally; single-read calls count as 0 or 1. f4(O, A; R, X) is positive when X shares more alleles with A than R
does, measured against O.

- **Standard error:** weighted block jackknife, as in #31. Block = (chromosome, floor(genetic position in Morgans
  / 0.05)). With m_j SNPs in block j, n = Σm_j, g blocks, θ the estimate, θ_j the estimate without block j and
  h_j = n/m_j: θ_J = g·θ − Σ(1 − m_j/n)·θ_j, τ_j = h_j·θ − (h_j − 1)·θ_j, SE² = (1/g)·Σ(τ_j − θ_J)²/(h_j − 1).
  Z = θ/SE.
- **Centred f4:** the mean of the products minus the product of the means, with the means recomputed for every
  deleted block. It removes the part of f4 that comes from the two sides differing in their overall share of
  reference alleles. Between differently prepared ancient samples that part is mostly technical, but it can also
  be real, so the centred value is a guard and not the decision statistic.
- **The decision rule for any one statistic:** plain Z at least Z*, and the centred estimate at least half the
  plain estimate.
- **Masks.** Each statistic uses the SNPs where every set it involves has data. The statistics that are combined
  (see S below) share one mask.

### People

- **Tested people:** date mean of 500 BP (1450 CE) or more; ASSESSMENT exactly `Pass`, `PROVISIONAL_PASS` or
  `MERGE_PASS`; at least 100,000 SNPs by the `.anno` 1240k count; one version per Individual ID (highest count;
  ties to the earlier line). 12,977 people.
- **Side.** A person is on the **American side** if their political entity is in the Americas list of #31's
  `replication/FORMAT.md` (which includes Greenland) and one of these holds: their latitude is 50° or more and
  the entity is USA, Canada or Greenland (the Arctic, whatever the longitude); or they have no coordinates; or
  their longitude is between −170° and −30° and they are not on a Pacific island (Chile west of −80°, Ecuador
  west of −85°, or latitude below 30° with longitude below −130°). Everyone else is **elsewhere**. 728 people
  are on the American side.
- **Site:** latitude and longitude rounded to two decimals.
- **Data type** by Genetic ID: capture (ends `.AG`), shotgun (ends `.SG`, no `.AG`), Twist (ends `.TW`, no `.AG`),
  other.
- **Present-day references**, from the two pipelines of #31, each person once (panel-A version preferred), all
  people of the labels pooled: Mbuti, Yoruba, French, Sardinian, Han, Papuan, Mandenka, Japanese, Australian, and
  **NA** = Karitiana, Surui, Mixe, Pima, Piapoco and Quechua. #31's per-person check found no European or African
  pull in these groups' panel-A genomes.
- **EHG** (15 people labelled `Russia_Karelia_Mesolithic` or `Russia_Karelia_Mesolithic_HG`): ancient
  hunter-gatherers rich in the north Eurasian ancestry that Native Americans also carry. They are a reference and
  are not tested.
- **Clean ancient Americans:** people on the American side south of latitude 50° whose label does not contain
  `Norse`, by data type. They are the baseline for the absolute test, and the capture ones with at least 500,000
  SNPs are the second Native American reference.

### Test 1: against the neighbours

- **Neighbours.** For person X, take the other tested people of the same side and data type who have coordinates
  and are from a different site. Distance is great-circle kilometres (sphere of radius 6,371 km) plus the absolute
  difference in date mean in years; ties go to the earlier line of the file. The pool P is the 20 nearest,
  provided every one of them is within 1,500 km and within 1,500 years. Otherwise X has no neighbours and gets
  test 2 only.
- **Elsewhere, looking for Native American ancestry.** A = f4(Mbuti, NA; P, X) and, for each control
  R in {EHG, Han, Sardinian, Papuan, Yoruba}, B_R = f4(Mbuti, R; P, X), all on one mask. Native Americans descend
  from a mix of north Eurasian-like and East Asian-like people, so someone with more of either than their
  neighbours has a positive A without being Native American. Fit A as Σ u_R·B_R over everyone elsewhere with
  neighbours (least squares on the plain estimates, no intercept). Refit up to three times, each time using only
  the people whose residual is within 4 robust standard deviations of zero, the robust standard deviation being
  1.4826 times the median absolute residual of the people in the previous fit. The decision statistic is the
  residual, **S = A − Σ u_R·B_R**, computed SNP by SNP as one f4 with its own jackknife; u is treated as fixed. A
  positive S is Native American affinity that the controls do not predict. It is a predictor, not a measurement
  of ancestry.
- **American side, looking for foreign ancestry.** For R in {French, Yoruba, Han, Papuan}:
  **E_R = f4(Mbuti, R; P, X)**.

### Test 2: absolute

A whole foreign community buried together would look normal against its own neighbours, so everyone also gets a
test that does not use neighbours.

- **Elsewhere:** D1 = f4(Mbuti, X; Han, NA) and D2 = f4(Mbuti, X; EHG, NA). A person passes if both pass the
  decision rule: closer to Native Americans than to East Asians and than to north Eurasian hunter-gatherers.
- **American side:** **G_R = f4(Mbuti, R; base, X)** for the same four R, where base is the clean ancient
  Americans of X's data type without X. If fewer than 20 remain, or X's type is "other", the capture baseline is
  used.

### Threshold and hits

One family: every test-1 and test-2 statistic (one per person elsewhere for each test; four per person on the
American side for each test). Z* is the one-sided 5% level with a Bonferroni correction for that count. A **hit**
is a person with at least one statistic passing the decision rule (both D1 and D2 for the elsewhere absolute
test).

### The centres

Rosters by group label among the tested people, excluding labels with an outlier suffix (`-o`):

- Old World: EGYPT (`Egypt_…`), MESOPOTAMIA (`Iraq_…`, `Syria_EMBA`), CHINA_EARLY (`China_…` labels containing
  `Longshan`, `Shang`, `Yangshao`, `Dawenkou` or `Erlitou`).
- American: MESOAMERICA (`Mexico_LateClassic`, `Honduras_Copan_Classic_Maya`), ANDES (`Peru_…` and `Bolivia_…`
  dated under 4,200 BP).

These labels are coarse: they are people buried in those regions and periods, not known residents of the cities.
For each centre with at least two members who have neighbours, the members' own test-1 block sums are added up,
so each member is compared with their own neighbours. Old World centres get S. American centres get E_R, and
f4(Mbuti, O; P, X) summed the same way for each Old World centre O with at least two members. A centre result
counts at the Bonferroni level for the number of centre statistics, by the same decision rule.

### Looking at each hit

Fixed in advance. A hit is **robust** if, for the statistic that passed:

- on transversions only, the estimate is at least half the all-SNP estimate and its Z is at least 2;
- with a second reference, the estimate is at least half. For S, D1 and D2, NA is replaced by the clean ancient
  Americans, with u unchanged. For E_R and G_R: Sardinian for French, Mandenka for Yoruba, Japanese for Han,
  Australian for Papuan.

For every hit, robust or not, these are recorded, and none of them removes it from the table:

- **Label:** whether its label names a foreign origin (for example `Norse`) or marks it as an outlier.
- **Date:** whether date mean minus two standard deviations falls after 1492, and whether the date is direct or
  from context.
- **Contamination:** AADR's X-chromosome estimates (flagged if a lower bound is above 0.02), mitochondrial match
  (flagged if the upper bound is below 0.95), its warnings, and the person's sex, since the X estimate exists
  only for males. A clean record does not prove clean DNA.
- **Lineages:** mitochondrial and Y-chromosome haplogroups as given in AADR.
- **Company:** how many of its neighbours, and how many people at its site, are also hits.
- **Library:** AADR's library type, to compare with the neighbours'.

Then each robust hit is described in words in `RESULTS.md` as one of: already known for this ancestry (with the
source); a metadata error (with the contradiction); possibly later than 1492; contamination suspected; or
**standing**. A group of hits at one site is reported as a group and can be standing as a group.

### What the scan can recover

Made-up strangers. From everyone elsewhere with neighbours, in file order, 200 are drawn without replacement
(numpy `default_rng(41)`, `permutation`, first 200). For each share f in {0, 5%, 10%, 25%, 100%} and each
recipient, a donor is drawn at random from the clean ancient Americans of the recipient's data type with at least
500,000 SNPs; each 5 cM block is replaced with probability f by the donor's calls where the donor has data; S is
recomputed against the same neighbours with the same u. The share detected by the decision rule is reported. The
same is done on the American side with donors from elsewhere of the same type with at least 500,000 SNPs whose
political entity is United Kingdom, Hungary, Italy, Austria, Spain, Germany, Denmark, France, Poland or Czechia,
read through E_French.

This measures recovery among people who have good neighbours, for two kinds of donor, at the first gate only. It
is not a limit on what any one burial could carry.

### Replication

A model from another vendor writes its own program from this protocol and #31's format note. Agreement means the
same tested people, sides, types, neighbours and references; every test statistic's estimate within max(1%, 1e-7)
and Z within 0.1; the same fitted u to three significant figures; and the same hits. The made-up strangers are
not required.

Two other vendors' models criticised this protocol once before the lock; see `review/`.

## What would count

- **For:** at least one robust hit, or group of hits, described as **standing**.
- **Against, within limits:** none standing. The statement is then: no outlier of this kind among the tested
  people, with the recovery rates showing what kind of outlier the scan can see.
- **Checks that the scan works:** the Greenland Norse should pass the absolute test toward French. A Cuban
  individual whose longitude is recorded with the wrong sign (`CDE003.AG`), and so lands "elsewhere", should come
  out as Native American there. If neither does, that is the headline.
- **Centres:** a centre statistic past its threshold that is robust by the two rules counts for shared ancestry.
  None doing so counts against only for the centres with enough people, and weakly.

## Known weaknesses

- **The sampled dead are not the people who lived.** Regions, periods and classes are missing; key centres have
  almost no one.
- **Two relative tests and one crude absolute one.** Test 1 sees a person unlike the people at other nearby
  sites. Test 2 sees a person who is foreign outright. Someone with a modest share of foreign ancestry in a
  region where everyone has it is seen by neither.
- **The controls.** The fit learns the Old World variation that is common. Rare lineages that resemble Native
  Americans without having come from America, such as ancient north-east Siberians, will show as hits and have
  to be explained. Real American-related ancestry that is common somewhere could be fitted away. The fit's own
  uncertainty is not in the standard errors.
- **References are proxies.** Han and the Karelian hunter-gatherers are not the actual ancestors of Native
  Americans; Papuans are not Polynesians. A person can pass a test for reasons other than the one it is named for.
- **Ancient-DNA artefacts.** Matching data type and centring remove some technical differences, not all; library
  chemistry varies within a type. Contamination by modern people can look like foreign ancestry and cannot be
  ruled out from this file, least of all in females.
- **Close relatives** among the neighbours are not removed.
- **Judgement.** Describing a hit as known, mislabelled, late or contaminated involves reading labels and papers
  after seeing the result. Each description gives its evidence.
- **Dates.** 500 BP is 1450 CE. Many dates come from context, and marine diets can make bones look older than
  they are.
- **Normal tails.** The threshold assumes Z behaves like a normal variable far into its tail. The distributions
  of every statistic are reported so the reader can see whether it does.

## Budget

$30: up to $3 for the review round, up to $10 for the replication, the rest in reserve.
