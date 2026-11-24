# Amendments — Is Linear A cracked? (#12)

## Record added after the spot check — 2026-11-24

Nothing in the program or in `results/` was changed or rerun for this record.

1. **The check on the method failed, and the verdict rule had no case for that.** The plan (§3.3, §4) requires
   Amarna Canaanite and Akkadian to beat the shuffle at `p < 0.001` and to exceed Linear B by 15 percentage points
   or more, and allows both "Supported" and "Not supported" only if they do. The margins were 0.0, −14.9 and +1.6
   (Amarna) and −29.9, −50.1 and −21.9 (Akkadian) in the three regimes, and Amarna's `p` was 0.016, 0.027 and 0.002.
   The first report gave the verdict "Not supported" with "zero amendments". `RESULTS.md` now reports the test as
   unable to tell.
2. **Novel signs.** The plan says 32 novel or revised sign assignments; the program finds 27. Five of the 27 carry
   the standard Linear B value in a different transliteration or do not change the consonant class; one (`PU₂`) is
   never counted because of a spelling mismatch in the program.
3. **Test 4** ran with 798 skeletons per root list, not the 1,500 in the plan, and on regime A1 only.
4. **The SigLA cross-check** (§2) was not run: `sigla_database.js` is downloaded and never read. Nor is
   `unread_words.json`.
5. **The split of lexicon words by confidence rating** (§3.2) was not made in Tests 1 to 3.
6. **Test 5's breakdown** of mismatches into shifts, deletions and metatheses was not measured.
7. **Analyses added by the spot check, outside the plan:** known Semitic word lists through the length-matched
   comparison; power; the shuffle test on words spelled with the proposal's values; the 22 signs that are new; a
   reading of the 188 lexicon mismatches. All are in `spotcheck/` and all are exploratory.
