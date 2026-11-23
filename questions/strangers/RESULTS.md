# Strangers in the ancient-DNA record: results

Issue #41 · Lane: data · Protocol locked 2026-11-23T06:42:55Z · Two amendments (2026-11-23)

## Answer

**No one in the public record is buried on the wrong side of an ocean, apart from people already known to be
there. One person is left unexplained, and she is probably not what the question was looking for.**

We tested 12,977 ancient people from one public release, each dated before 1450 CE.

1. **In the Americas: no pre-Columbian person with European, African, East Asian or Oceanian ancestry**, other
   than two known groups. Of 728 people, 15 were flagged: the 11 medieval Norse of Greenland, and 4 Arctic people
   whose Siberian ancestry is well known.
2. **Outside the Americas: 163 people were flagged as leaning toward Native Americans, and 162 are explained.**
   Almost all are ancient Siberians and steppe peoples, who share deep ancestors with Native Americans. One is a
   Cuban whose longitude was recorded with the wrong sign, which the scan caught as intended.
3. **One person stands.** A woman buried at Pietrele, Romania, about 4500 BCE (`PIE069.AG`), leans toward Native
   Americans and East Asians more than the 38 other people from her site or anyone near her. The lean is what
   about 3% of such ancestry would give. It is not specific to the Americas. Chance is the best-supported
   explanation; contamination is possible, though the one check in the public file argues against it; a real
   trace of north-east Asian ancestry is not ruled out. She is a person to look at, not evidence of a crossing.
4. **The early civilisations: nothing that holds up.** Classic-period Mexico leans slightly toward Mesopotamia by
   the letter of the rule (Z = 2.8), but it leans just as much toward China, the Han and the French, so it is a
   general difference from its neighbours, not a link to Mesopotamia. The Andes show nothing. Egypt has two
   people and could not be tested.
5. **The scan can see what it was built to see.** It recovers 92% of made-up strangers with 10% Native American
   ancestry and half of those with 5%.

A model from another vendor wrote its own program from the protocol. After two of our own mistakes were
corrected, it gave the same neighbours for all 12,977 people and the same 183 hits.

## How the scan works, in brief

Each person gets two tests.

- **Against the neighbours:** are they more like Native Americans (if buried outside the Americas), or more like
  Europeans, Africans, East Asians or Papuans (if buried in the Americas), than the 20 nearest people from other
  sites, of the same data type, within 1,500 km and 1,500 years?
- **Absolute:** do they look Native American outright, or foreign outright, whoever their neighbours are?

Outside the Americas the neighbours test first subtracts what five control populations predict, because Native
Americans share old ancestry with north Eurasians and East Asians. The threshold is Z = 4.64, a 5% error rate
spread over 28,382 tests. Numbers below are from the corrected run (`results/corrected/`; see Amendments).

## The evidence

### 1. Who was flagged

| Where buried | Tested | Flagged | Explained | Standing |
|---|---|---|---|---|
| American side | 728 | 15 | 15 | 0 |
| Elsewhere | 12,249 | 163 | 162 | 1 |

| Class | People | Who |
|---|---|---|
| Known | 38 | 11 Greenland Norse; 4 Arctic people (Dorset, Saqqaq, Aleut); 18 Old Bering Sea people of Chukotka; 5 other ancient Siberians |
| Metadata error | 1 | A Cuban individual recorded at longitude +77.8 instead of −77.8 |
| Not specific to Native Americans | 127 | Russia 73, Kazakhstan 19, China 14, India 8, Mongolia 8, Europe 5 |
| Unlike their neighbours | 3 | Early farmers in Italy, Morocco and Austria |
| Not robust | 8 | Fail the transversion or second-reference check |
| **Standing** | **1** | **`PIE069.AG`, Pietrele, Romania** |

The full list, with the reason beside each person, is `results/corrected/hits_review.tsv`.

**The checks passed.** All 11 Greenland Norse are caught by the absolute test (Z = 27 to 29 toward the French).
The mislabelled Cuban is caught by both tests (Z = 65 and 56).

**On the American side** the neighbours test flags no one, and the absolute test flags only the 15 above. The
largest lean toward Africans (Yoruba) among 728 people is Z = 3.6, and toward Papuans 3.7, both under the
threshold. The nearest miss is one person from the Paraná river in Argentina, about 1,000 years old
(`I30899.TW`, 211,601 SNPs): Z = 4.3 toward the French on the neighbours test and 4.1 on the absolute test, under
the threshold of 4.64, with a lean away from Han. That is the pattern modern European contamination gives in a
low-coverage sample. It is not a hit, and is mentioned so that nothing near the line is hidden.

### 2. The 127 "not specific" and Amendment 1

The locked protocol could not tell a person with ancestry *from* America apart from a person with more of the old
Siberian ancestry that Native Americans also carry. Amendment 1 added a test for that: is the person closer to
Native Americans than to the Altai hunter-gatherers, a well-sampled group of such relatives? Of 155 robust hits
outside the Americas, 127 are not. They are steppe and Siberian groups (Botai, Okunevo, Yamnaya of the Kazakh
steppe, the Tarim Basin, the Altai and Yenisei hunter-gatherers themselves) and eight people at Roopkund Lake in
the Himalaya, whose neighbours in this release are Tibetan-plateau people unlike them.

28 pass. One is the Cuban. 23 are Siberians from the Bering Strait to Lake Baikal, the closest known kin of
Native Americans on the Asian side: 18 Old Bering Sea people, the 9,800-year-old Kolyma individual, two from the
Okhotsk coast and two others. We give this from memory of the literature and did not re-read it.

Four are early farmers in Europe and north Africa. Three of them have a *negative* raw lean toward Native
Americans (Z = −5.6, −8.4, −3.6): they are less like Native Americans than their neighbours, not more. They were
flagged because their neighbours are mostly hunter-gatherers, and the controls over-correct for that. Real Native
American ancestry would raise the raw lean, as it does for the Cuban (Z = +69). This reasoning was made after
seeing the result and is marked as such.

### 3. The one left standing

`PIE069.AG`: a woman from Pietrele, Romania, Gumelnița culture, directly dated 6,458 ± 34 BP (about 4500 BCE),
260,114 SNPs, mitochondrial haplogroup H, published in 2023.

| Measure | Value |
|---|---|
| Residual lean toward Native Americans, against 20 Copper Age neighbours | Z = 5.65 |
| Raw lean toward Native Americans | Z = +5.0 |
| On transversions only | 1.06 of the estimate, Z = 3.5 |
| With ancient Americans as the reference | 0.84 of the estimate |
| Closer to Native Americans than to Altai hunter-gatherers (Amendment 1) | Z = 5.1 |
| Closer to Native Americans than to Han | Z = 3.3 |
| The 38 other people from her site | Z between −2.6 and +2.2 |
| AADR contamination flags | none; she is female, so the X-chromosome estimate does not exist |
| Mitochondrial reads matching her own type (AADR) | 99.5–99.7%, like the others at her site (99.4–100%) |

Whom she leans toward, compared with her neighbours (exploratory), beside ten made-up strangers built from her
own neighbours with 3% ancient American ancestry:

| Reference | She | Made-up 3% strangers (median) |
|---|---|---|
| Native Americans, present-day | 5.1 | 4.1 |
| Native Americans, ancient | 4.6 | 4.3 |
| Japanese | 3.9 | 2.4 |
| Chukotka | 3.5 | 3.1 |
| Han | 3.4 | 2.4 |
| Altai hunter-gatherers | 2.2 | 1.9 |
| French | 0.4 | −1.6 |
| Yamnaya (steppe) | −0.2 | −0.7 |
| Western hunter-gatherers | −2.3 | −1.9 |

Her pattern is what about 3% of Native American-like or north-east Asian ancestry looks like. What it could be:

- **Chance.** This has the best support. The residual has heavier tails than a normal curve: 99 people pass the
  threshold on the positive side and 71 fall as far on the negative side, where no ancestry explanation applies.
  Among 12,249 people, one unexplained outlier of this size is not strange.
- **Contamination.** A few percent of DNA from a modern person with Native American or East Asian ancestry, picked
  up in excavation, storage or the laboratory, would look like this. It is the usual explanation for a small
  unexpected ancestry in one person, and that is a prior, not a finding. The one check available argues against
  it: 99.5–99.7% of her mitochondrial reads match her own type (H), the same as her site-mates, and a contaminant
  with that ancestry would usually carry a different type and lower the figure. It is not decisive; a contaminant
  can share her type. The signal also holds on transversions, so ancient damage is not making it.
- **A real trace of north-east Asian ancestry** in Copper Age Europe. Not ruled out. It would be surprising and
  would be a Eurasian matter, with no ocean involved.

What it is not: evidence that anyone crossed the Atlantic. She leans toward Japanese and Han nearly as much as
toward Native Americans.

**Correction, 23 November 2026.** The first version of this section called contamination and chance "the likely
ones" and said that nothing in the public file could test contamination. Eugene asked why a real anomaly had
been set aside. The mitochondrial figure was in the file all along and points against contamination; the text
above now says so, and ranks the three readings by their support.

Her sequence reads are public (European Nucleotide Archive, study PRJEB62503, run ERR11495483), so a further
check needs no contact with the laboratory. See Amendment 3.

### 4. The centres

| Centre | People | With neighbours | Result |
|---|---|---|---|
| Egypt | 2 | 1 | Not testable |
| Mesopotamia | 11 | 9 | S: Z = −0.5 |
| Early China | 102 | 63 | S: Z = −5.6 (less like Native Americans than the controls predict; not the direction tested) |
| Classic Mesoamerica | 33 | 30 | Toward Han 3.0, Mesopotamia 2.8, early China 2.6, French 2.3, Papuans 1.7, Egypt 0.8, Yoruba 0.5 |
| Andes | 66 | 46 | All between −1.7 and +1.0 |

The centre threshold is Z = 2.73 for 16 statistics. Two Mesoamerican ones pass it. "Toward Han" fails the
transversion check. "Toward Mesopotamia" passes both checks, so by the locked rule it counts. It should not be read
as a link to Mesopotamia:

- These 30 people lean toward every non-African reference by about the same amount. Their lean toward Mesopotamia
  beyond their lean toward Han is Z = −0.3 (exploratory).
- All 30 are from one study, nearly all prepared with one kind of library, and most of their neighbours are
  ancient Cubans and Bahamians from other studies. A general difference between this set and its neighbours,
  in ancestry or in data, would produce exactly this.

### 5. What the scan can recover

Made-up strangers: 200 real people with a share of their genome, in 5 cM pieces, replaced by a donor's.

| Share of foreign ancestry | Native American ancestry, buried elsewhere | European ancestry, buried in the Americas |
|---|---|---|
| 0% | 0% flagged | 0% flagged |
| 5% | 52% | 6% |
| 10% | 92% | 28% |
| 25% | 100% | 85% |
| 100% | 100% | 93% |

The American side is the weaker half of the scan: there are fewer people, so fewer neighbours, and the centring
guard discards some real signals. A person in the Americas with a tenth European ancestry would more likely be
missed than found by the neighbours test. Someone wholly foreign is found 93% of the time by that test, and the
absolute test caught all 11 Norse.

These rates are for people with good neighbours, two kinds of donor, and the first gate only. They are not a
limit on what any one burial could carry.

## Replication

OpenAI's `gpt-6.2-astra` was given `protocol.md`, `amendments.md` and the format notes, and wrote a 471-line
program (`replication/openai/`). It ran first time. The comparison found three differences, all ours:

1. **Our brief left out a definition** (how the present-day reference panels are built), so its first version
   guessed. We sent the definition, quoted from #31's protocol, and nothing else.
2. **Our code skipped 219 people** in the neighbours test (Amendment 2).
3. **Our code uses one shared SNP mask** for the four American-side statistics where the protocol gives each its
   own.

Against the corrected run:

| | Agreement |
|---|---|
| Tested people, sides, data types | 12,977 of 12,977 |
| Neighbours | 12,977 of 12,977 |
| Fitted control weights | identical to four decimals |
| S, D1 and D2 | 35,827 of 35,827 within tolerance |
| American-side statistics | Z within 0.1 for all 4,804; estimates within 1% for 3,153 (the mask difference) |
| Hits | the same 183 |

The replication covers the two tests and the hits. It did not cover the robustness checks, the centres, the
made-up strangers or Amendment 1, and it cannot catch a mistake in the protocol itself.

## Amendments and mistakes

Both amendments were written and pushed before the amended parts ran (`amendments.md`).

1. **A test the protocol lacked.** The locked run flagged 159 people outside the Americas, nearly all Siberian
   relatives of Native Americans. The protocol had warned of this and given no way to tell them from people with
   ancestry from America. Amendment 1 added one, after the results were seen.
2. **219 people our code left out.** The locked code built no neighbour pools for people of mixed data types,
   against the protocol's wording. The replication exposed it. The whole scan was rerun with them
   (`results/corrected/`), which added four hits, none of them standing. One line of the locked code was changed
   to make the rerun possible. The locked run is kept in `results/`.

Also learned on the way:

- Before the lock, two other vendors' models showed that the first design could not see a foreign community
  buried together, and could not see an African in the Americas at all. The design was rebuilt (`review/`). The
  rebuilt design was not sent back for review.
- On shuffled genomes the absolute test on the American side reached Z = 25 from technical differences between
  data sources alone. The centring guard removed all of it.
- The centre robustness checks were in the protocol and missing from the locked code; they were computed
  afterwards as specified.

## Limits

- **The sampled dead are not the people who lived.** Whole regions, periods and classes are missing. Egypt has two
  people here, Mesopotamia eleven, and no Indus city has any.
- **Travellers who left no trace** among these 12,977 are invisible.
- **Small shares.** Below about 5% Native American ancestry outside the Americas, and below about 25% European
  ancestry inside them, the neighbours test misses more than it finds.
- **The tests are proxies.** A person can pass for reasons other than the one the test is named for; most of the
  178 did.
- **Judgement.** Calling a hit "known" or "unlike neighbours" was done after seeing it. The reasons are written
  beside each person.
- **Contamination** cannot be excluded from genotype files.
- **One release.** This is one public compilation of mostly targeted SNP data, not every ancient genome.
- **This session's priors.** One session proposed, designed, ran and wrote up the question, knowing #31's results.

## Who did this

Eugene directed the work. Claude Fable 5.2 (Anthropic) designed and ran the analysis and wrote this report on
23 November 2026. OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` reviewed the protocol before the lock;
`gpt-6.2-astra` wrote the independent replication. No human checked the numbers.

Cost: $1.89 of the $30 budget (`SPENDING.md`).

## What this means

If people had been crossing the oceans in deep antiquity and settling among those they met, some of them, or
their descendants, ought to turn up in graves on the far shore with the wrong ancestry for the place. We went
through nearly thirteen thousand ancient people looking for exactly that. In the Americas we found the Norse of
Greenland, whom everyone knew about, and nobody else. In the Old World we found many people who resemble Native
Americans, but they are Siberians and steppe peoples who resemble them because they share ancestors from the Ice
Age, not because anyone came back across the sea. One woman from Copper Age Romania has a small lean we cannot
explain. Chance is the best-supported reading and contamination is possible; a real trace of ancestry from far
to the east is not ruled out. Even taken at face value it points to Asia, not America. The search has real blind spots: it only sees the people who happen to have been
dug up and sequenced, and Egypt, Mesopotamia and the Indus are almost empty. But where it can see, it sees no
strangers.
