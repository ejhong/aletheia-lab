---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/population-y/analysis/make_figures.py from the results files.
summary: A few Amazonian peoples carry a faint genetic resemblance to Australasians. We checked whether it is real, and what it does and does not show.
dek: A few Amazonian peoples share slightly more DNA variants with New Guineans, Aboriginal Australians and Andaman Islanders than other Native Americans do. We tested that ten-year-old claim on public genomes, with the plan locked before any result existed.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Finished. The resemblance is real and faint, and it is older than it looks: it leads back to mainland Asia tens of thousands of years ago, not across the Pacific. No ancient American we could test clearly carries it.

## What we figured out

In 2015 geneticists reported something odd. The Suruí and Karitiana, two small peoples of the Brazilian Amazon, appeared to be slightly more closely related to New Guineans and Aboriginal Australians than other Native Americans are. An ocean and half a world lie between them. Later studies disagreed about whether ancient skeletons show the same thing, and one raised the chance that it was a statistical accident.

We rechecked the claim on public data, and then asked which explanation the data fit. Four things came out.

1. **The resemblance is real.** It is not an accident of chance, of one laboratory's processing, or of a few donors. It shows up however the test is set up, and three separately written programs give the same numbers.
2. **It is faint, and fuzzier than its reputation.** Published estimates put it at one to three percent of ancestry. Part of what the standard test picks up turns out to be a general lean of these Amazonians toward all non-African peoples. The part that is specific to Australasians is there, but with less certainty than the headline number suggests.
3. **It is not really "Australian".** The same Amazonians are just as close to Andaman Islanders, and just as close to a person who lived near what is now Beijing about 40,000 years ago, long before anyone lived in the Americas. What all of these share is descent from a very old population of mainland Asia. The reading that fits is that a little of that old ancestry came into the Americas over land with the first settlers, and happens to survive in a few Amazonian groups.
4. **It is missing from the ancient bones we could test.** Not one of 58 groups of ancient Americans stands out for it, including people of the ancient Pacific coast. So where it was for ten thousand years, and why it survives in these groups, is still unknown.

In short: a real curiosity with an ordinary explanation. Nothing here points to ancient voyages across the Pacific.

{{figure: population-y/tiles}}

## The signal, tested several ways

The test asks one question at about a million places in the genome. Where Papuans and a distant African group carry different variants, do the Amazonians side with the Papuans more often than a comparison group of Native Americans does? A small, consistent yes is the signal.

{{figure: population-y/tests}}

- **The excess is there.** The primary test is clearly above zero. So is each community alone, and so are 26 donors who were not part of the original study.
- **Andaman Islanders and a 40,000-year-old show it too.** Swap Papuans for either and the excess stays the same size or grows.
- **Han Chinese show a little of it.** That control should sit at zero if the excess were purely Australasian. It sits at about a quarter of the signal: not enough on its own to count, but enough to matter.
- **Subtract the control and less is left.** Compared with the Mixe of Mexico, about three quarters of the excess survives, at Z = 2.8, just under the usual bar of 3. Compared with the Pima, what survives is not distinguishable from zero.

## Who the Amazonians lean toward

The same test can be run against every population in the public data. If the excess were only about Australasians, they alone would sit apart from a crowd centred on zero.

{{figure: population-y/world}}

Compared with the Mixe, the picture is close to the published one: Papuans and Aboriginal Australians lead, with Andaman Islanders just behind. But the whole crowd sits to the right of zero. Compared with the Pima, East Asian populations lead and the Australasians are scattered among them. The answer to "is it specifically Australasian?" depends on whom the Amazonians are compared with, and we cannot say which comparison group is the unusual one.

## Two explanations, and what each predicts

| | If people crossed the Pacific | If it is an old Asian lineage | What we found |
|---|---|---|---|
| Closer to Papuans than to Andaman Islanders? | Yes | No | No difference (Z = 0.5) |
| Shared with someone who lived in China 40,000 years ago? | No | Yes | Yes, just as strongly (Z = 4.0) |
| Stronger on the ancient Pacific coast than inland? | Likely | No reason to be | No difference (Z = 1.6) |

The predictions are our own reasoning about what each story implies. The findings are measurements. None of this identifies the source population or dates its arrival; it only shows which story the measurements sit more comfortably with.

## Ancient Americans

If the ancestry came in with early settlers, some ancient group might carry more of it than others. We compared each ancient group only with other ancient people whose DNA was prepared the same way, because ancient DNA differs from modern DNA in ways that can fake or hide so small an effect.

{{figure: population-y/ancient}}

- **No group stands out**, in 75 tests across 58 ancient sets.
- **Ancient South America as a whole** has at most about 5% of today's Amazonian excess over ancient North and Central Americans.
- **The ancient Pacific coast** shows none, with an upper limit of about 25%. That bears on a published proposal that the ancestry entered South America along the coast, though it does not settle it.
- **Sumidouro5**, a 10,400-year-old individual from Brazil reported in 2018 to carry the signal, does not show it in the version of his genome that passes quality control. A version that fails quality control shows it weakly (Z = 1.7). The claim depends on which is used.

This comparison is relative. It shows that no sampled ancient group has more of the excess than ancient northerners do. It cannot show that ancient people had none. For a single ancient genome, the data are simply too thin to tell.

## How it was done

- **Public data.** The Allen Ancient DNA Resource, release v66.p1: 23,089 ancient and present-day people, in the public domain.
- **The plan was locked first.** Every test and every decision rule was written down, criticised in three rounds by models from OpenAI and Google, and committed before any statistic on a Native American genome was computed. The reviews caught a reversed sign and a rule that would have mistaken contamination for the signal.
- **Replicated twice.** OpenAI's and Google's models each wrote their own program from the written plan alone, without seeing our code or numbers. Both matched every list of samples and every required statistic.
- **Cost.** $5.72, all of it for the other vendors' reviews and replications.

## What went wrong

Two mistakes in the locked plan surfaced when it was run. Both corrections were written down and published before the corrected parts ran, and the original results are kept beside the corrected ones.

- **Not everyone in "ancient America" was an ancient American.** The plan selected people by modern country. That let in 18 ancient islanders from Guam and the Marianas, which are United States territory, and 12 medieval Norse from Greenland. The plan's own controls flagged them as impossible, which is how the mistake was found.
- **One check could not work.** A test for European or African ancestry in the comparison group was built on an equation that carries no information. A repaired version is too imprecise to pass. Simpler statistics show no sign of such ancestry, but by the rule fixed in advance the official headline is "detected, with caveats: admixture".

## What this cannot tell you

- Every genome carrying the signal comes from two small, closely related Amazonian communities. Coastal and central-Brazilian groups named in published claims are, rightly, under controlled access, and were not tested.
- Only one family of method was used, on a set of DNA markers chosen partly from a Karitiana and from Papuans.
- Nothing here identifies the source population, dates its arrival or traces its route.
- One AI session proposed, designed, ran and wrote up the study, after reading the main papers. No human has checked the numbers.

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/population-y/RESULTS.md), with every number behind the figures
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/population-y/protocol.md) and its [amendments](https://github.com/ejhong/aletheia-lab/blob/main/questions/population-y/amendments.md)
- [The reviews before the lock](https://github.com/ejhong/aletheia-lab/blob/main/questions/population-y/review/README.md)
- [Analysis code](https://github.com/ejhong/aletheia-lab/tree/main/questions/population-y/analysis) and the [two replications](https://github.com/ejhong/aletheia-lab/tree/main/questions/population-y/replication)

AI did this work: Claude Opus 5.5 and Claude Fable 5.2 (Anthropic), with OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` as reviewers and replicators. Eugene directed it.
