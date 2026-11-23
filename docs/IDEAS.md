# Parked ideas

Possible questions that are not questions yet. Nothing here has an issue, a folder or a place in `QUESTIONS.md`,
and nothing here is worked on. Eugene decides whether an idea becomes an issue. Text is unverified unless it says
how it was checked.

## Do monument positions encode astronomical constants more often than chance?

Parked 2026-11-22 at Eugene's request. Noted by Claude Fable 5.2 (Anthropic).

**The claim.** James Q. Jacobs's "archaeogeodesy" pages (<https://jqjacobs.net/archaeogeodesy/>) report that the
latitudes of ancient monuments, and the arc distances between them, match astronomical and mathematical constants
to a few parts per million, and read this as intentional placement.

**The idea.** Give the claim the null distribution it lacks. Fix in advance the family of relations that would
count as a match, then count matches among the real sites and among many randomized site sets. Report how often
chance does as well.

**What the pages say** (fetched 2026-11-22; about 40% of the index page was read verbatim, so treat this as
partial):

- Examples of claims: "Chavin's latitude sine equals one-sixth"; Avebury at 360/7 degrees (the page gives
  51.428609° against 51.4285714°); Huaca del Sol on the latitude atan(1/7); two Machu Picchu latitudes tied to
  lunar motion per rotation; the Machu Picchu to Newark Earthworks arc as "nearly six million meters".
- Constants named: lunar orbits per rotation, rotations per solar orbit, the Metonic and Saros cycles, a 345-year
  eclipse interval, the precession cycle, and others. Phi appears on the geoglyph page ("phi relationships").
- Precision: "about one part in one million" for a 5 m GPS error over a 6,000 km arc. No numeric cut-off for what
  counts as a match was found.
- No statistical test, null model or count of comparisons tried was found.
- The code is said to cover "more than 8,500 site latitude and longitude complex numbers". No download of that
  list was found. An Amazon geoglyph list (1,550+ entries, XLS and KML) is downloadable from
  <https://jqjacobs.net/archaeology/geoglyph.html>. Licence not checked.
- `unverified`: the specific three-site ratios (pi and phi across Chavín, Machu Picchu, Chichén Itzá, Poverty
  Point, Newark, Tikal, Denali, Huascarán) come from a second-hand summary and were not found in the text read.

**Sketch of a design** (not a protocol):

1. *Latitude claims.* The cheapest test. Fix a list of "notable" latitudes (asin and atan of simple fractions,
   360/n, the lunar constants) and a tolerance. Ask whether real monument latitudes fall within tolerance more
   often than the same latitudes shifted by random amounts of a few kilometres. Needs only a site list.
2. *Arc and ratio claims.* Fix the quantities (arc distance, latitude and longitude differences, their ratios and
   trig functions), the constants and the tolerance. Count matches over all pairs or triples of real sites, and
   over randomized site sets that keep the regional clustering. With 8,500 sites there are about 10¹¹ triples, so
   the expected number of chance matches is the whole question.
3. *Out of sample.* If dated versions of the site list exist, fix the claim family from the earlier one and test
   it on sites added later.

**Why it is harder than it looks.**

- Everything turns on the claim family. Too narrow and the test is a strawman; too wide and nothing could pass.
  The fair version takes the family from the author's published method, or has him agree it before anything is
  computed.
- The null model is a choice too. Sites sit where land, rivers and people are. Shifting real sites slightly is
  safer than scattering points at random.
- Published claims are the survivors of a search whose size is not reported. The test can measure how easy such
  matches are to find. It cannot recover what was tried and discarded.

**If it became a question.** Lane `data`. It could be one case in "Coincidence court" (#8) or a question of its
own. Cost is mostly compute; a second vendor's replication from the protocol is the main paid item. Getting the
full site list would mean asking the author, which is outward-facing and needs Eugene's say-so.
