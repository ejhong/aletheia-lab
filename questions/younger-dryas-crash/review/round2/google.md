<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T17:08:19.643935+00:00", "input_tokens": 3892, "output_tokens": 39633, "cost_usd_list_price": 0.6062} -->

### (a) Errors of sign, algebra or logic

1. **Made-up records systematically lose bins relative to the real record**
   - Quote: *"It has the real record's bins, each with as many dates as the real bin and those dates' real errors. Each bin gets one calendar age drawn from the reference density, and one curve error: normal with standard deviation `σ(t)`. Each of its dates gets radiocarbon age `μ(t)` plus the bin's curve error plus a normal laboratory error of that date's own `E`, rounded to the nearest year. A date whose radiocarbon age falls outside 9,000 to 13,800 is dropped, as a real one would be; a bin left empty disappears."*
   - Correction: Because the real bin count is already post-filter while `μ(t) < 9,000` 14C BP below ~10,180 cal BP (where the 9,500–16,500 reference density puts substantial mass), dropping empty bins leaves every made-up record with systematically fewer surviving bins and inflated variance compared to the real record. Redraw each bin until it survives the 9,000–13,800 14C BP filter (or draw enough bins that the surviving count matches the real record).

2. **Substring filter excludes non-aquatic terrestrial materials**
   - Quote: *"A date is used if its `Age` is from 9,000 to 13,800 radiocarbon years inclusive, its `Error` is above zero, and its `Material` and `Taxa` fields together do not contain any of the strings `shell`, `marine`, `fish`, `mollus`, `whale`, `seal`, `otolith`, `coral` (in any letter case). Those materials take up old carbon from water and need corrections the database does not give."*
   - Correction: Case-insensitive substring matching on `shell` (and `fish`) excludes terrestrial materials such as `nutshell` and `eggshell` (and terrestrial taxa such as `fisher`), which are not aquatic and do not take up old carbon from water. Exempt terrestrial compounds like `nutshell` and `eggshell` (and match whole words where appropriate).

3. **Non-exclusive overall decision rules**
   - Quote: *"- **Supported** if a drop is detected in North America."* / *"- **Supported as widespread** if detected in North America and in at least one of Europe and Asia."*
   - Correction: Both conditions fire simultaneously when a drop is detected in North America and in Europe or Asia. Restrict **Supported** to a drop detected in North America and in neither Europe nor Asia (matching the mutual exclusivity used in the regional table).

### (b) Factual statements you are confident are wrong

1. **p3k14c as the largest public archaeological radiocarbon database**
   - Quote: *"In the largest public database of archaeological radiocarbon dates, does the record of human activity drop at the Younger Dryas onset, in North America and in Europe and Asia, by more than the dating method and chance produce?"*
   - Correction: XRONOS (`xronos.ch`), a public archaeological chronological database that incorporates p3k14c alongside other datasets, contains over 250,000 radiocarbon dates versus p3k14c's 173,946. Name p3k14c directly rather than calling it the largest public database.

### (c) Instructions that contradict each other

1. **Columns used from p3k14c omit `Material` and `Taxa`**
   - Quote: *"Columns used from p3k14c: `Age` (radiocarbon years BP), `Error`, `SiteID`, `SiteName`, `Continent`."* (contradicts *"its `Material` and `Taxa` fields together do not contain any of the strings..."* in **Dates and regions**).
   - Correction: Add `Material` and `Taxa` to the list of columns used from p3k14c in **Data and sources**.
