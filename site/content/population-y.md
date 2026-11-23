---
# To update this page, edit this file and push to main; the site rebuilds itself.
summary: Some Amazonian peoples share a faint genetic resemblance with Australasians. Is it real, and what does it show?
dek: Some Amazonian peoples share slightly more genetic variants with Papuans, Aboriginal Australians and Andaman Islanders than other Native Americans do. We tested that claim on public genomes, with the plan locked before any result existed.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Done, awaiting Eugene's review. The signal is real in public genomes, and it is weaker and less specific than its reputation. It points to an old Asian lineage, not to voyages across the Pacific. No ancient American group tested clearly carries it. Models from two other vendors reproduced every number from the protocol alone.

## The question

In 2015 two research groups reported that a few Amazonian peoples, the Suruí and Karitiana among them, share slightly more genetic variants with Australasians than other Native Americans do. The proposed source was named "Population Y", or Ypykuéra, "ancestor" in Tupi. Later studies disagreed about whether ancient skeletons carry it, and one raised the chance that it was a false positive.

We asked four things. Is the excess detectable in public genomes, and does it survive changes of method? Is it specific to Australasians? Which living lineage is it closest to? And does any ancient American group stand out for it?

## What we found

| Question | Answer | Key number |
|---|---|---|
| Is it there? | Yes. | Primary test Z = 4.2. On the 2015 paper's own comparison, D = 0.017 against the published 0.021. |
| Does it survive changes of method and donors? | Yes. | Positive in 97% of 216 method variants; in each community alone; with any one donor removed; and in 26 donors the 2015 study did not use (Z = 4.2). |
| Is it specific to Australasians? | Partly. | Against the Mixe, about three quarters of the excess is beyond what the Amazonians also share with Han Chinese (Z = 2.8). Against the Pima, the Papuan-specific part is not significant (Z = 1.4). |
| Closer to Onge or to Papuans? | No difference. | Z = 0.5. |
| Does a 40,000-year-old East Asian show it? | Yes, just as strongly. | Tianyuan: Z = 4.0. |
| Does any ancient American group stand out? | No. | 75 tests on 58 ancient sets; none passed. Ancient South America as a whole: at most about 5% of the present-day excess over ancient North and Central Americans. |
| The ancient Pacific coast? | No excess detected. | At most about 25% of the present-day excess; no difference from the inland Andes (Z = 1.6). |
| The disputed 10,400-year-old Sumidouro5 individual? | Not supported. | Depends on which version of his genome is used; neither passes. |

By the rule fixed in advance, the headline is **"detected, with caveats: admixture"**. One planned check, for European or African ancestry in the comparison group, turned out to be unable to tell anything. The simpler statistics show no sign of such ancestry, but a general lean toward non-Africans of about a quarter of the signal cannot be excluded.

## What it means

A small group of Amazonian peoples carry a faint genetic resemblance to people from New Guinea, Australia and the Andaman Islands that other Native Americans lack. The resemblance is there, and it does not go away when the method or the donors are changed. But it is smaller and blurrier than the headline version: the part that is specific to Australasians is less certain than the published figures suggest.

It is not a sign of ancient voyages across the Pacific. The Amazonians are just as close to a man who lived in China 40,000 years ago, which is what you would expect if the ancestry came from an old population of mainland Asia and entered the Americas with everyone else.

No ancient skeleton from the Americas tested here clearly carries it, so where it was for the ten thousand years in between is still unknown. The people who could settle that are living communities in Brazil and Peru whose genomes are, rightly, not public.

## How it was done

- **Data.** The Allen Ancient DNA Resource, release v66.p1: 23,089 ancient and present-day people, public domain.
- **Plan locked first.** The protocol was written, criticised in three rounds by models from OpenAI and Google, and locked in its own commit before any statistic on a Native American genome was computed.
- **Two amendments, in the open.** The locked run's own controls exposed two mistakes in the plan: 18 ancient people from Guam and the Marianas, and 12 Greenland Norse, had been counted as ancient Americans; and the admixture check could not work. Both corrections were written down before the corrected parts ran. The original results are kept beside the corrected ones.
- **Replicated.** OpenAI's and Google's models each wrote their own program from the protocol alone. Both matched every sample list and every required statistic.
- **Cost.** $5.72, all for the other vendors' reviews and replications.

## Limits

- Every genome carrying the signal comes from two small, closely related Amazonian communities. The present-day coastal and central-Brazilian groups in the published claims are under controlled access and were not tested.
- The answer on specificity depends on which group the Amazonians are compared with.
- Only one kind of method was used, on a set of SNPs built partly from a Karitiana and from Papuans.
- Nothing here identifies a source population, dates an arrival or traces a route.
- One session proposed, designed, ran and wrote up the question, after reading the main papers.

## Files

- [Results](https://github.com/ejhong/aletheia-lab/blob/main/questions/population-y/RESULTS.md)
- [Protocol](https://github.com/ejhong/aletheia-lab/blob/main/questions/population-y/protocol.md) and [amendments](https://github.com/ejhong/aletheia-lab/blob/main/questions/population-y/amendments.md)
- [Pre-lock reviews](https://github.com/ejhong/aletheia-lab/blob/main/questions/population-y/review/README.md)
- [Analysis code](https://github.com/ejhong/aletheia-lab/tree/main/questions/population-y/analysis) and [replications](https://github.com/ejhong/aletheia-lab/tree/main/questions/population-y/replication)

AI did this work: Claude Opus 5.5 and Claude Fable 5.2 (Anthropic), with OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` as reviewers and replicators. Eugene directed it. No human has checked the numbers.
