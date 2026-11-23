<!-- {"vendor": "openai", "model": "gpt-6.2-astra", "utc": "2026-11-23T17:05:37.476913+00:00", "input_tokens": 3600, "output_tokens": 7485, "cost_usd_list_price": 0.3282} -->

### (a) Errors of sign, algebra or logic

- **“A reference world with no sudden change, run through the same dating process and given the same make-up as the real record:”**  
  Only the *starting* bin sizes and errors match. Simulated dates can be dropped, and two simulated ages on opposite sides of a 200-year boundary can remain in one bin when the real-data rule would split them.

- **“A parabola can bend, so a slow turn in the record is not mistaken for a step.”**  
  A gradual decline confined to the target windows need not be captured by a quadratic fitted over 5,000 years. It can produce a detected step without any abrupt change.

- **“If it is 0.01 or less, the real record is higher after the onset than a halving would leave it.”**  
  The upper-tail comparison establishes that the real **after/before ratio** is unusually high under the halving model, not that the after-onset level is high. A low before-onset level can also produce a high ratio.

- **“Power is the share of them that would count as a detected drop, by the same rule and the same 2,000 crash-free records.”**  
  This computes power for a **fixed reference and cutoff**. It is not the repeated-sampling power of the full procedure, which fits its reference to the record being tested.

- **“A crash shorter, smaller or later than the one tested could go unseen. The power figures say how much.”**  
  No power figure covers a shorter crash. Every planted crash lasts 300 years; the 200- and 500-year variants change the detector windows, not the crash duration.

- **“Supported if a drop is detected in North America.” / “Supported as widespread if detected in North America and in at least one of Europe and Asia.”**  
  As overall verdicts, these overlap. Assign “Supported as widespread” when its condition holds and plain “Supported” when North America detects a drop but neither other region does.

- **“A record with no drop would not show that nothing happened to people, only that their dated traces did not thin by the amount tested.”**  
  No *detected* drop can yield “Cannot tell.” Only the separate halving-exclusion rule gives evidence against thinning by the tested amount.

- **“The false-alarm check above measures what that costs.”**  
  The check estimates the false-alarm rate of the whole procedure under one simulated trend. It does not isolate the cost attributable to fitting the reference to the record it judges.

### (b) Factual errors

- **“A flat stretch spreads dates out and a steep one bunches them, which draws false dips and peaks in any curve of dates through time.”**  
  The spread of an individual calibrated date does not imply systematic peaks or dips in the sum. For example, with uniform true calendar ages and a matching calibration prior and likelihood, the expected summed curve is uniform despite changes in slope.

- **“Southern continents need a different calibration curve and are left out.”**  
  Terrestrial curve choice depends on the sample’s atmospheric carbon source, not its continent. Africa and South America both include Northern Hemisphere sites, and Asia includes Southern Hemisphere sites.

- **“Those materials take up old carbon from water and need corrections the database does not give.”**  
  The strings do not identify only such materials: `shell` also matches “charred hazelnut shell,” a terrestrial sample. The reported exclusion count is a count of string matches, not of confirmed aquatic dates.

- **“Sites with several names, or several sites sharing a name within a continent, are mis-grouped; fixed 200-year spans split close dates that fall either side of a boundary.”**  
  The name claim applies only when the name is used as the key. With consistent, distinct `SiteID` values, varying or shared names have no effect on grouping.

### (c) Contradictory instructions

- **“Columns used from p3k14c: `Age` (radiocarbon years BP), `Error`, `SiteID`, `SiteName`, `Continent`.”**  
  The inclusion rule also requires `Material` and `Taxa`; both belong in the column list.

- **“The p-value at the target is `(k + 1)/2,001`, where `k` is the number of made-up records whose step at `T*` is at or below the real one.”**  
  The variants use 1,000 reference records and the false-alarm check uses 200. The rule must be `(k + 1)/(B + 1)`, giving denominators 2,001, 1,001 and 201 respectively; with 2,001 fixed, the reported false-alarm-check median of 0.55 is impossible.
