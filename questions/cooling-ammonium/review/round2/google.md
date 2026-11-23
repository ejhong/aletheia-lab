<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T14:57:17.056033+00:00", "input_tokens": 3725, "output_tokens": 33745, "cost_usd_list_price": 0.5173} -->

### (a) Errors of sign, algebra or logic

1. **Quiet-time condition applied to P, R, and H percentiles**
   > "Each event is placed against *quiet times*: every `t` that is a multiple of 20, from 10,500 to 107,520, with no listed event of any kind between `t − 300` and `t + 200` inclusive, and with D defined, in that core and for that chemical. An event's **percentile** is the share of quiet times with a strictly smaller value."

   **Correction:** Because percentiles (and verdicts) are also computed for P, R, and H, conditioning quiet times on `"with D defined"` includes times where those measures are undefined (e.g., `t = 10,500` and `10,520` in NGRIP, where H's bins 12–14 fall below the 10,270 yr start of the record) and excludes times where they are defined but D is not. Replace `"with D defined"` with `"with that measure defined"`.

### (b) Factual statements confident are wrong

Nothing found.

### (c) Instructions that contradict each other

1. **General description of the four measures vs. definition of P**
   > "All four measures are natural logs of ratios of means of bins:"  
   > "- **P, the peak:** the largest of after bins 0 to 9 over the median of the before bins (needs 8 of the 10)."

   **Correction:** P is the log ratio of a maximum to a median, not a ratio of means. Change the lead-in to `"All four measures are natural logs of ratios:"` (or specify that D, R, and H use means while P uses a maximum and a median).

2. **Decadal row-lookup formula vs. non-multiple-of-10 ages in Reported alongside #6**
   > "For a time `t` (a multiple of 20 for every event here; GS-1 is taken at 12,900) in one core:  
   > - *After bins:* 20-year means, bin `k` (0, 1, 2, …) from the rows labelled `t − 20k − 20` and `t − 20k − 10`. ...  
   > - *Before bins:* five 20-year means, bin `k` (0 to 4) from the rows labelled `t + 20k` and `t + 20k + 10`."  
   > "6. The stadial onsets left out by rule 1 or 2, and three smaller coolings (GI-1d, GI-1b and the 11.4 ka event): their D and percentile, for the reader."

   **Correction:** In Rasmussen et al. 2014 Table 2, GI-1d (14,075 yr b2k) and GI-1b (13,311 yr b2k) are not multiples of 10, so the row-label lookup matches no rows in the 10-yr files and cannot evaluate D. Specify a rounding rule for non-multiple-of-20 ages in item 6 (as done for GS-1).
