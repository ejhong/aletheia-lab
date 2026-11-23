---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The panels and interactive figures are made by questions/ancient-sky-hole/analysis/make_figures.py from the results files.
summary: The classical constellations leave a patch of the southern sky empty, centred on where the south pole stood for whoever set its edge. The pole drifts, so the patch carries a date. Whose date is it?
verdict: The hole dates the star catalogue, to Greek astronomers of about 130 BCE to 140 CE. It cannot date the first constellations
result: The empty patch in Ptolemy's star catalogue fits the sky of Hipparchus and Ptolemy, who made the catalogue, and fits a sky of 3000 BCE far worse; by the rule set in advance an origin before 3000 BCE is excluded. But the test dates the people who last filled in the stars, and they catalogued everything down to their own horizon. Whether the figures themselves are older, this record cannot say. The main model also landed at 910 CE, centuries after the catalogue was written, which shows how much such dates lean on what one assumes about haze at the horizon.
dek: Nobody can draw constellations in sky that never rises. So the 48 classical constellations leave a blank circle around the south pole of their makers, and because the pole drifts through the stars over 26,000 years, the circle's position is a clock. We read that clock from Ptolemy's star catalogue, with the rules fixed before looking at the southern sky.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Finished and replicated. A second AI system, working from the written plan alone, reproduced every date and latitude. The empty patch is the horizon of the Greek astronomers who compiled the catalogue. It is not a relic of anything older, and it cannot tell us how old the constellation figures are.

## What we figured out {menu: Findings}

Look at a map of the 48 constellations in Ptolemy's *Almagest*, written about 137 CE, and there is a hole in it. Around the south pole lies a patch with no figures and no catalogued stars. The reason is simple: from the Mediterranean that part of the sky never rises.

The patch is centred on the south pole of the sky. But the pole moves. The Earth's axis wobbles once in about 26,000 years, and the pole traces a circle among the stars as it does. So the centre of the empty patch says *when* its edge was set, and its size says *how far north* the observers stood. Since the 1960s some astronomers have argued that the patch points to about 2600 BCE, long before Greek astronomy (Ovenden 1966, as later sources report it; not read here). If it pointed further back still, it would mean an organised map of the sky older than writing.

We matched Ptolemy's stars to modern positions, wound the sky back, and asked which date and latitude best explain which stars are in the catalogue and which are missing.

{{figure: ancient-sky-hole/tiles}}

Four things came out.

1. **The patch belongs to the sky of the catalogue's own makers.** Every version of the test puts the date after 201 BCE. A sky of 3000 BCE fits very much worse, and a sky of 9600 BCE worse again. By the rule fixed in advance, an origin before 3000 BCE is excluded.
2. **That is the known answer.** The catalogue was compiled by Hipparchus on Rhodes about 128 BCE and by Ptolemy at Alexandria about 137 CE. Three versions of the test land in exactly that window: bright stars only (121 BCE), a plain empty circle with no allowance for haze (41 BCE), and a model free to choose its own haze (160 CE).
3. **So the hole dates the cataloguers, not the constellations.** An astronomer listing stars adds every star he can see to the figures he has inherited. The southern edge of the *stars* is therefore his own horizon, whatever the age of the *figures*. This test recovers a date we already knew, which shows the method works. It does not show the figures are young.
4. **The main model went wrong, and that is a finding too.** The version we had named in advance as the main one put the date at 910 CE, almost eight centuries after the catalogue was written. That is impossible, and it happened because of one assumption about how much haze dims stars near the horizon. A date from an empty patch of sky can move by a thousand years on that assumption alone.

{{figure: ancient-sky-hole/verdict}}

## Wind the sky back yourself {menu: The sky}

The figure below is the southern sky, with Ptolemy's stars in gold and the bright stars he left out in a paler tint. Drag the date, or press play, and the pole moves along its circle. The ring is the horizon: everything inside it never rises. At 128 BCE on Rhodes the ring closes neatly around the missing stars. At 3000 BCE or 9600 BCE it does not.

{{figure: ancient-sky-hole/sky_dome}}

## Where each version of the test points {menu: The dates}

The second figure shows how well each date and latitude explains the catalogue, for four versions of the test. The bright patch is the best fit; the dots are 500 reshufflings of the sky that show how far the answer can wander.

{{figure: ancient-sky-hole/contour}}

| Version of the test | Best date | Best latitude |
|---|---|---|
| **Main model as locked** (haze fixed at a typical sea-level value) | **910 CE** | 25.8° N |
| Clearer air | 210 CE | 33.2° N |
| Three other haze settings | 720 to 880 CE | 22.5° to 28.0° N |
| Haze left free | 160 CE | 35.7° N |
| A plain empty circle, no haze | 41 BCE | not fitted |
| Stars inside the figures only | 670 CE | 27.0° N |
| Leaving out two late constellations | 500 CE | 28.2° N |
| Securely identified stars only | 930 CE | 25.8° N |
| Bright stars only (magnitude 4.0 and brighter) | 121 BCE | 31.8° N |
| Magnitude 4.5 and brighter | 50 CE | 30.3° N |
| Magnitude 5.0 and brighter | 610 CE | 27.0° N |

Hipparchus worked at 36.4° N and Ptolemy at 31.2° N. The versions that fit best are the ones that land nearest them. The main model fits worse than the plain circle and worse than the model with free haze, and its date is one no historian could accept.

**Why the main model failed.** It assumes a faint star low on the horizon was very unlikely to be recorded. But Ptolemy's catalogue holds faint stars at the very bottom of old figures such as the Altar, the Ship and the Centaur, and leaves out much brighter stars nearby that belong to no figure. The cataloguers were completing pictures, not sweeping the sky evenly. A model that does not know this explains the faint low stars by moving the date and the observer until those stars stand higher.

## The stars on the rim {menu: The rim}

The last figure takes the stars one at a time: Ptolemy's southernmost against the brightest he missed.

{{figure: ancient-sky-hole/rim}}

On Rhodes in 128 BCE, every one of the southernmost stars in the catalogue cleared the sea horizon, by one to five degrees. Of the twelve brightest missing stars, eleven never rose. At Alexandria in 137 CE four of those missing stars stood three to six degrees up and still went unrecorded. That fits the view of several historians of astronomy that the catalogue's southern limit is mostly Hipparchus's, taken over by Ptolemy. This comparison was made after the results were in and is not part of the locked test.

## How it was done

- **Public data.** Ptolemy's catalogue as matched star by star to the Hipparcos satellite catalogue by Verbunt and van Gent (2012), and Hipparcos itself for positions, brightness and the slow motions of the stars.
- **Calibrated on the north.** How faint a star the cataloguers bothered to record was measured on the northern sky, which is always visible, and then held fixed.
- **Checked on made-up skies first.** Catalogues were simulated for four known dates from 9600 BCE to 137 CE; the method recovered each to within about 300 years and one degree of latitude.
- **Locked first.** The southern sky was not looked at until the plan was fixed, with thirteen versions of the test named in advance and a rule for what would count as excluding a date before 3000 BCE.
- **Replicated.** Claude Opus 5.5 (Anthropic) wrote its own program from the plan alone, including its own version of the precession formula. The main fit, all thirteen versions and all 21 leave-one-out runs came out identical, and the reshuffled range begins at 207 BCE against 201 BCE. It also listed thirteen points where the plan left a choice open; none changes the answer.
- **Cost.** Nothing: public data and a laptop.

## What went wrong

- **The main model was misjudged.** We named the fixed-haze model as the main one. It gave an impossible date. The verdict survives because the rule used the whole range of versions, and the whole range lies after 201 BCE.
- **The range is cut off at 1000 CE.** That was the edge of the search. The true upper end for the main model may lie later still, which makes the same point more strongly.
- **The question as posed could not be answered by this record.** The issue asked how old the constellations are. A star catalogue answers a different question: when its stars were last listed.

## What this cannot tell you

- **How old the figures are.** Babylonian star lists that name many of them are generally dated about a thousand years before Hipparchus (not checked here), and nothing in this study bears on that or on anything older. A test of the figures' own age would have to use what the old sources say about the figures as wholes, such as which of them rose and set together, and not the positions of single stars.
- **Whether an older empty patch was overwritten.** If an earlier people left a hole centred elsewhere, the Greek cataloguers filled their own sky in over it. Only the last edge survives.
- **Anything exact about the date.** The honest range is 201 BCE to 1000 CE, and its upper half is produced by a model we know to be wrong.
- One AI system designed, ran and wrote up the study, and another re-derived it. No historian of astronomy has checked it.

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/ancient-sky-hole/RESULTS.md)
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/ancient-sky-hole/protocol.md)
- [Code](https://github.com/ejhong/aletheia-lab/tree/main/questions/ancient-sky-hole/analysis) and the [replication](https://github.com/ejhong/aletheia-lab/tree/main/questions/ancient-sky-hole/replication/fable)

AI did this work: Antigravity (Google DeepMind) designed and ran the study and built the figures. Claude (Anthropic) replicated it and rewrote this page in the lab's plain style. Eugene directed it.
