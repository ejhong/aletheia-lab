# Log

## 2026-11-23 (Claude Fable 5.2, directed by Eugene)

- Eugene asked what test could be added for the Taurid form of the Younger Dryas impact hypothesis, then asked for
  this one to be run. Issue #100 made active.
- **Before anything else was fixed**, one record was looked at while framing the question: the GISP2 ion record
  from Summit (`iond.txt`, already in the lab for #43), where the sample spanning 1908 to 1910 holds ammonium about
  13 times its neighbours. Summit is therefore kept out of the test.
- **Data search**, by a subagent (Claude Opus 5.5) told not to open any chemistry dated 1895 to 1920: 39 files
  from NOAA, PANGAEA and the Arctic Data Center. `MANIFEST.md` and `explore/structure.py` are its work. It reports
  having read one abstract (D4 black carbon) that discusses a span including 1908, before its redaction filter
  existed; D4 is not used.
- **Program** `analysis/tunguska.py`, developed in a mode that removes 1905 to 1912 from every series.
- **Dating check on sulphur** (`explore/dating_check.py`): four cores set aside as loosely dated near 1900.
- **Review by Google `gemini-4-neon`** (`review/round1`): overlapping windows compete with one another; the first
  plan's rule for moving cores' dates by their Katmai peak was unsafe; a null result was turned into a bound it
  could not support; nitrate and black carbon cannot tell an airburst from a fire year in 1908. The plan was
  rebuilt: non-overlapping windows, the same sites in every window, no dates altered, cores chosen by a sulphur
  check, the conversion to the Younger Dryas reduced to an illustration. A second, narrow round
  (`review/round2`) found one arithmetic slip and one ambiguous phrase, both fixed.
- Eugene asked for one outside vendor, Google, for review and replication from here on.
- **Design comparison, blind** (`explore/design_power.py`): two-year window chosen over three-year for sensitivity.
- **Lock:** 2026-11-23T20:12:12Z (`protocol.lock`, in its own commit).
- First locked run stopped while writing `results/summary.json`: a numpy integer could not be written as JSON.
  Nothing had been printed or read. Fixed by converting numpy numbers on output (one line of `analysis/tunguska.py`);
  no computation changed. Rerun.
- **Locked run:** ammonium for 1908–09 ranks 10 of 56 across six sites: ordinary. NEGIS 7.0 times a typical year
  (1908), ACT11d 3.5 (1909), the others 1.2 to 1.6. Summit, reported apart: 4.7 and 5.7. Sulphur at Katmai ranks
  2 of 56.
- **Replication** by Google `gemini-4-neon` (543 lines, ran first time): every rank, score, size and verdict
  identical; sensitivity within 7 points.
- **Exploratory, after the result** (`explore/after.py`): the spikes are sharp, carry soot at Summit, and sit 3.9
  to 4.5 years before each core's Katmai sulphur peak. Two loosely dated Tunu cores hold a larger spike dated 1906.
- No amendments. Spent $1.42 of $20.
