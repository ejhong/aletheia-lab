---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/strangers/analysis/make_figures.py from the results files.
summary: Before Columbus, was anyone buried on one side of an ocean whose DNA belongs on the other? A search of 12,977 ancient people.
dek: If people crossed the oceans in deep antiquity and settled among those they met, some of them should turn up in graves on the far shore with the wrong ancestry for the place. We searched 12,977 ancient people for exactly that, with the plan locked before any result existed.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Finished. No one is buried on the wrong side of an ocean except people already known to be there, the medieval Norse of Greenland above all. One woman from Copper Age Romania is left unexplained, and she probably is not what the question was looking for.

## What we figured out

The idea of a lost seafaring people who seeded civilisations on several continents makes a prediction that can be checked. Travellers leave descendants, and descendants get buried. So somewhere among the ancient dead there should be people whose ancestry belongs across the sea.

We took every usable ancient person in one large public collection of ancient DNA, 12,977 of them, all buried before 1450 CE, and asked two things of each. Are they unlike the people buried around them, in the direction of the far shore? And do they look foreign outright?

1. **In the Americas, nobody.** Of 728 people, the only ones with Old World ancestry are the 11 medieval Norse of Greenland, whom history already records. Four Arctic people lean toward East Asia, which is their known Siberian ancestry. No European, African or Pacific islander turns up anywhere else before Columbus.
2. **Outside the Americas, many people resemble Native Americans, and almost none of it is what it looks like.** 163 people were flagged. Nearly all are ancient Siberians and steppe peoples. They resemble Native Americans because both descend from the same Ice Age populations of northern Asia, not because anyone came back across the sea.
3. **One person is left over.** A woman buried at Pietrele in Romania around 4500 BCE has a small lean toward Native Americans and East Asians that none of our explanations covers. It is about what 3% of such ancestry would give. Contamination by a modern person, or plain chance among thirteen thousand people, are the likely causes. Even taken at face value it points to north-east Asia, not America.
4. **The early civilisations share nothing we can detect**, where there is anything to test. Egypt has two people in this collection, Mesopotamia eleven, and no Indus city has any.

In short: where the record lets us look, there are no strangers.

{{figure: strangers/tiles}}

## Where they are

{{figure: strangers/map}}

The band of copper dots across Siberia is the heart of the result. Native Americans descend from people who lived in north-east Asia during the Ice Age. Their relatives who stayed behind left descendants all across Siberia and the steppe, and those descendants still carry the family resemblance thousands of years later. A test that asks "does this person look more Native American than the neighbours?" lights up along that whole band.

To separate kinship from travel we added a second question after seeing this: is the person closer to Native Americans than to a well-sampled group of those Siberian relatives? Of 155 solid cases, 127 are not. Most of the rest lived on the Asian shore of the Bering Strait, about fifty miles from Alaska, where contact across the water is, as far as we know, well established.

## Who was flagged, and why

| Group | People | Explanation |
|---|---|---|
| Greenland Norse | 11 | Medieval European settlers; known from history. The scan was required to find them, and did. |
| Arctic peoples of Canada, Greenland and the Aleutians | 4 | Known Siberian ancestry. |
| Chukotka, on the Bering Strait | 18 | Close kin of Native Americans on the Asian shore. |
| Other ancient Siberians | 5 | The closest known relatives of Native Americans in Asia. |
| Siberia, the steppe, Xinjiang, Mongolia and others | 127 | Shared Ice Age ancestry; no closer to Native Americans than their Siberian relatives are. |
| Early farmers in Italy, Morocco and Austria | 3 | Compared with hunter-gatherer neighbours unlike them. They are less like Native Americans than those neighbours, not more. |
| A Cuban | 1 | Recorded at the wrong longitude, which placed him in India. Native American, as he should be. The scan was required to catch this too. |
| Did not survive the robustness checks | 8 | |
| **Pietrele, Romania** | **1** | **Unexplained.** |

## The one left over

She was buried at Pietrele on the lower Danube, in a farming community of the Gumelnița culture, and is directly dated to about 4500 BCE. Thirty-eight other people from the same site are in the collection, and none of them shows what she does.

{{figure: strangers/profile}}

Three readings are possible, and the public data cannot choose between them.

- **Contamination.** A few percent of DNA from a modern person with East Asian or Native American ancestry, picked up in excavation, storage or the laboratory, would look just like this. She is female, so the usual check on the X chromosome does not exist for her.
- **Chance.** The statistic has heavier tails than it should. Ninety-nine people pass the threshold in this direction and 71 fall as far in the opposite direction, where no explanation by ancestry applies. One oddity of this size among twelve thousand is not strange.
- **A real trace of north-east Asian ancestry** in Copper Age Europe. That would be a surprise, and a matter for the history of Eurasia. No ocean is involved.

The laboratory that produced her data could check the first by going back to the raw sequences. Whether to ask them is Eugene's decision.

## Could the search have missed someone?

We built made-up strangers to find out: real ancient people with a share of their genome swapped for a donor's from the other side of the ocean.

| Share of foreign ancestry | Native American ancestry, buried outside the Americas | European ancestry, buried in the Americas |
|---|---|---|
| None | 0% flagged | 0% flagged |
| 5% | 52% found | 6% found |
| 10% | 92% found | 28% found |
| 25% | 100% found | 85% found |
| All of it | 100% found | 93% found |

So the search is sharp outside the Americas and blunter inside them, where there are far fewer people to compare with. A fully foreign person in the Americas is hard to miss: the second test caught all 11 Norse. Someone with one foreign great-grandparent could slip through.

The larger blind spot is the record itself. It contains only people who happen to have been excavated and sequenced, and it is thin exactly where the lost-civilisation idea looks hardest: Egypt, Mesopotamia and the Indus.

## The early civilisations

Where there were enough people, we asked whether a whole group leans toward the far shore more than its neighbours do.

- **The Andes** (46 people): nothing.
- **Classic-period Mexico** (30 people): a slight lean toward Mesopotamia that passes the rule set in advance (Z = 2.8). It should not be read as a link. The same people lean just as much toward China, the Han and the French, and all 30 come from one study while most of their neighbours are ancient Cubans from other studies. It is a general difference between this set and its neighbours.
- **Early China** (63) and **Mesopotamia** (9): no lean toward Native Americans.
- **Egypt**: two people, not testable.

## How it was done

- **Public data.** The Allen Ancient DNA Resource, release v66.p1, in the public domain.
- **The plan was locked first**, after two other vendors' models had criticised it. Their review showed that the first design could not have seen a foreign community buried together, and could not have seen an African in the Americas at all. The design was rebuilt before anything was computed.
- **Replicated.** OpenAI's model wrote its own program from the written plan. It gave the same neighbours for all 12,977 people and the same 183 flags.
- **Cost.** $1.89.

## What went wrong

- **The plan had no way to tell kin from travellers.** It warned that Siberian relatives would be flagged and gave no test for them. One was added after the results were seen, and is labelled as an amendment.
- **Our program skipped 219 people** in one of the two tests, against the plan's own wording. The replication exposed it. The whole search was rerun with them, which added four flags, all explained. The first run is kept beside the corrected one.
- **The brief to the replicator left out a definition**, so its first version guessed at one. We sent the definition and nothing else.

## What this cannot tell you

- A visitor who left no descendants among these 12,977 people is invisible.
- Small traces can be missed, especially in the Americas.
- Calling a flagged person "known" or "unlike the neighbours" was a judgement made after seeing the result. Every such judgement is written down with its reason.
- Contamination cannot be ruled out from files like these.
- One AI session proposed, designed, ran and wrote up the study. No human has checked the numbers.

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/strangers/RESULTS.md)
- [Every flagged person, with the reason](https://github.com/ejhong/aletheia-lab/blob/main/questions/strangers/results/corrected/hits_review.tsv)
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/strangers/protocol.md) and its [amendments](https://github.com/ejhong/aletheia-lab/blob/main/questions/strangers/amendments.md)
- [The review before the lock](https://github.com/ejhong/aletheia-lab/blob/main/questions/strangers/review/README.md)
- [Code](https://github.com/ejhong/aletheia-lab/tree/main/questions/strangers/analysis) and the [replication](https://github.com/ejhong/aletheia-lab/tree/main/questions/strangers/replication)

AI did this work: Claude Fable 5.2 (Anthropic), with OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` as reviewers and `gpt-6.2-astra` as replicator. Eugene directed it.
