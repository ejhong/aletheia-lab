# Strangers in the ancient-DNA record

Issue: #41 · Lane: data · Budget: $30

## Question

Before 1492, was anyone buried on one side of the Atlantic or Pacific whose DNA belongs on the other?

1. **The scan.** Among every ancient person in the public record, is there one buried outside the Americas who
   carries Native American ancestry, or one buried in the Americas who carries Old World or Oceanian ancestry?
2. **The centres.** Do the people of early American civilisations (Classic Mesoamerica, the Andes) carry any Old
   World ancestry that their neighbours lack, and do the people of early Old World centres carry any Native
   American ancestry that their neighbours lack?

## Why it matters

The idea of a lost seafaring civilisation that seeded cultures on several continents predicts that people, or
their descendants, crossed the oceans long before Columbus. The public record now holds about 13,000 usable
ancient genomes. A search of all of them is a direct test, and it had not been done uniformly as far as we know.
The odds of a hit are low. A clean "no", with a stated limit on what could have been missed, is worth having, and
one robust "yes" would be extraordinary.

Aletheia link: the atlas's lost-civilisation and transoceanic-contact cases, if any; to be checked when filing.

**What this can and cannot show.** It can find individuals whose ancestry is foreign to their neighbours, down to
a stated share. It cannot find visitors who left no descendants among the sampled dead, and it says nothing about
places and periods with no sampled genomes. Egypt has two usable genomes, Mesopotamia a handful, and no Indus city
has any.

Known cases the scan should find, used as checks and not counted as discoveries: medieval Norse in Greenland
(Europeans on the American side); Arctic peoples with Siberian ancestry on the American side; ancient north-east
Siberians related to the ancestors of Native Americans.

## Data and sources

- Allen Ancient DNA Resource (AADR) v66.p1, public 1240K set. Same files as question #31; see `MANIFEST.md`.
- Nothing else. The lessons of #31 apply: a person's political entity is not their geography, and comparisons mix
  data types only where stated.

## Method

Computed by `analysis/` with Python 3.12 and numpy 2.3.5. Before the lock the code ran on made-up data and end to
end with every genome's SNPs shuffled (`--blind`). No statistic was computed on unshuffled genomes before the
lock.

### Statistic

As in #31's protocol: f4(P1, P2; P3, P4) is the mean over autosomal SNPs of (p1 − p2)(p3 − p4), with a weighted
block jackknife on 5 cM blocks. **All decisions here use the centred f4**: the mean of the products minus the
product of the means, which removes the effect of data sources differing in their overall share of
reference-genome alleles. f4(O, A; R, X) is positive when X shares more alleles with A than R does, measured
against O. A SNP is used if every set in the statistic has data there.

### People

- **Ancient people (the universe):** date mean of 500 BP or more, ASSESSMENT exactly `Pass`, `PROVISIONAL_PASS` or
  `MERGE_PASS`, at least 100,000 SNPs (the `.anno` 1240k SNP count), one version per Individual ID (highest SNP
  count; ties to the earlier line). About 13,000 people.
- **Side.** A person is on the **American side** if their political entity is in the Americas list of #31's
  `replication/FORMAT.md` (which includes Greenland), and their longitude, if given, is between −170° and −30°,
  and they are not in the central Pacific (latitude below 30° with longitude below −130°). Everyone else is
  **elsewhere**.
- **Data type** by Genetic ID: capture (`.AG` at the end), shotgun (ends `.SG`, no `.AG`), Twist (ends `.TW`, no
  `.AG`). Other types are tested in step A only.
- **Present-day references**, from the two pipelines of #31 with each person counted once (panel-A version
  preferred): Mbuti, Yoruba, French, Sardinian, Han, Papuan, and **NA** = Karitiana, Surui, Mixe, Pima, Piapoco and
  Quechua together. **MA1** is the Genetic ID `MA1.SG`, a 24,000-year-old Siberian whose kind of ancestry makes up
  about a third of Native American ancestry.

### Step B: each person against their neighbours (the main test)

- **Neighbours.** For person X, take the other people of the same side and data type, with coordinates. Distance
  is great-circle kilometres plus the difference in date mean in years. The pool P is the 20 nearest, provided all
  20 lie within 1,500 km and 1,500 years. Otherwise X has no pool.
- **Elsewhere, looking for Native American ancestry.** Compute A = f4(Mbuti, NA; P, X) and, for each control
  R in {MA1, Han, Sardinian, Papuan, Yoruba}, B_R = f4(Mbuti, R; P, X). Native Americans descend from a mix of
  MA1-like and East Asian-like people, so someone with more of either than their neighbours has a positive A
  without being Native American. Fit A as a sum of u_R·B_R over all tested people elsewhere (least squares, no
  intercept, centred estimates; three rounds, each dropping people whose residual is more than 4 robust standard
  deviations from zero, where the robust standard deviation is 1.4826 times the median absolute residual). The
  decision statistic is the residual, computed SNP by SNP as one centred f4 with its own jackknife:
  **S = A − Σ u_R·B_R**. A positive S is Native American affinity that the controls do not explain.
- **American side, looking for foreign ancestry.** For R in {French, Yoruba, Han, Papuan}:
  **E_R = f4(Mbuti, R; P, X)**.
- **Threshold.** Z* is the one-sided 5% level with a Bonferroni correction for all step-B tests: one per person
  elsewhere and four per person on the American side. A person is a **hit** if Z(S) ≥ Z*, or Z(E_R) ≥ Z* for any
  R.

### Step A: people with no pool

For every person, D1 = f4(Mbuti, X; Han, NA) and D2 = f4(Mbuti, X; MA1, NA). Both are large and positive for a
Native American. They decide only for people without a step-B test:

- elsewhere: a hit if Z(D1) and Z(D2) are both at least Z*_A;
- American side: a hit if Z(D1) or Z(D2) is at most −Z*_A.

Z*_A is the Bonferroni level for the number of such tests (one per person elsewhere, two per person on the
American side).

### The centres

Sets by group label, within the universe:

- Old World: EGYPT (`Egypt_…`), MESOPOTAMIA (`Iraq_…` and `Syria_EMBA`), CHINA_EARLY (`China_…` labels containing
  `Longshan`, `Shang`, `Yangshao`, `Dawenkou` or `Erlitou`).
- American: MESOAMERICA (`Mexico_LateClassic` and `Honduras_Copan_Classic_Maya`), ANDES (`Peru_…` and `Bolivia_…`
  dated under 4,200 BP).

For each centre and data type with at least two people, the pool is the union of its members' step-B pools
without centre members. Old World centres get S; American centres get E_R for the four references, and also
f4(Mbuti, O; P, centre) for each Old World centre O as a whole. A centre result counts at Z ≥ 3.5.

### Checking each hit

Fixed in advance. A hit is **robust** if both hold:

- on transversions only, the estimate has the same sign and is at least half the all-SNP estimate;
- with a second reference, the same. For S, NA is replaced by ancient Americans (all capture-type people on the
  American side with at least 500,000 SNPs). For E_R: Sardinian for French, the world-panel Mandenka for Yoruba,
  Japanese for Han, Australian for Papuan.

Every robust hit is then put in one class, with the evidence written down:

- **Known:** its label or publication already says it (for example `Norse`, an outlier suffix such as `-o…`), or
  it belongs to one of the known cases listed above.
- **Metadata:** its coordinates or entity contradict its label or publication.
- **Contamination:** AADR's own estimates flag it (X-chromosome contamination interval with lower bound above
  0.02, or mitochondrial match with upper bound below 0.95), or its `.anno` warnings mention contamination.
- **Neighbourhood:** three or more of its 20 neighbours are also hits, or it is a hit of its own pool's kind
  across a whole site. That is a difference between populations, not a stranger, and is reported as a cluster.
- **Standing:** none of the above.

### What could have been missed

Made-up strangers measure it. Take 200 tested people elsewhere, chosen at random (numpy `default_rng(41)`). For
each share f in {100%, 25%, 10%, 5%}, replace that share of each one's SNP calls with the calls of a random
ancient American of the same data type with at least 500,000 SNPs, and recompute S against the same pool. The
detection rate at Z* is reported. The same is done on the American side with 200 people and ancient European
donors (elsewhere, same data type, at least 500,000 SNPs, group label starting with a European country in a fixed
list), read through E_French.

### Replication

A model from another vendor writes its own program from this protocol and #31's format note. Agreement means the
same universe, sides, types and pools; S, E_R, D1 and D2 within max(1%, 1e-7) and Z within 0.1 for every person;
and the same list of hits. The made-up strangers are not required.

One round of criticism by two other vendors' models was taken before the lock; see `review/`.

## What would count

- **For:** at least one hit classed as **standing**. Each is reported with everything known about it. One would
  not prove a crossing; it would be a person to look at very hard.
- **Against, within limits:** no standing hit, and the made-up strangers show what share of foreign ancestry would
  have been detected. The conclusion is then "no one among the sampled dead carries more than about that share".
- **The checks:** the Greenland Norse must come out as hits (class: known). If they do not, the scan is not
  working and that is the headline.
- **Centres:** a centre result at Z ≥ 3.5 that is robust by the same two rules counts for shared ancestry. None
  counts against, for the centres that have data.

## Known weaknesses

- **Coverage of the past.** The sampled dead are not the people who lived. Whole regions, periods and social
  classes are missing. Key centres have almost no genomes.
- **Travellers who left no trace.** A visitor without descendants among the sampled dead is invisible.
- **Neighbours as the baseline.** In thinly sampled places the 20 nearest people may be poor neighbours, or a
  person may have no pool. Mixed cities make everyone look a little foreign.
- **The controls.** The fit removes the kinds of Old World ancestry that are common. A rare kind that happens to
  resemble Native Americans, such as ancient north-east Siberians, will show as hits and has to be explained.
- **Ancient-DNA artefacts.** Centring removes a uniform lean toward the reference genome, not all of it.
  Contamination by modern people can look like foreign ancestry; the contamination class exists for that.
- **Judgement in the classes.** Deciding that a hit is "known" involves reading labels and papers after seeing
  the result. Every such decision is written down with its source.
- **Dates.** Many dates come from context, not radiocarbon. A hit near 500 BP may postdate contact.

## Budget

$30: up to $3 for the review round, up to $10 for the replication, the rest in reserve.
