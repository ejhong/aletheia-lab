<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-28T03:14:52.864560+00:00", "input_tokens": 5482, "output_tokens": 27298, "cost_usd_list_price": 0.4259} -->

### (a) Errors of sign, arithmetic or logic

1. **Decision rule vs. summary of outcomes ("Supports the preprint" / "For the preprint's contest")**
   - Quote: *"3. **Supports the preprint** if Answer 2 is 'yes', at most one control passes, and no control's mean reaches half the fresh Tamil average."* vs. *"- **For the preprint's contest:** both fresh Tamil lists pass and outrank every control, and no control comes within half of them."* and *"- **Neither clearly:** Tamil ahead on average with a control passing, or one fresh Tamil list high and one low."*
   - Correction: Under Rule 3, if two controls pass below half the fresh Tamil average the verdict is **Mixed** (not **For**), whereas if one control passes below half the fresh Tamil average while both Tamil lists pass and outrank all controls the verdict is **Supports the preprint** (not **Neither clearly**). Add "at most one control passes" and "half the fresh Tamil average" to the **For** bullet, and restrict the **Neither clearly** bullet to cases where two or more controls pass, a control reaches half the fresh Tamil average, or only one fresh Tamil list is ahead.

### (b) Factual statements you are confident are wrong

Nothing found.

### (c) Instructions that contradict each other

1. **List size threshold vs. fixed 600-name size**
   - Quote: *"A list with fewer than 550 different names is built again once; if still short it is run at its size and marked. A list with more than 600 is cut to 600 names, once, at random (seed 20261127), so that every new list enters at one size."* and *"A new list is used whole (600 names)."*
   - Correction: A list with 550–599 unique names is neither rebuilt nor cut, and a twice-short list enters below 550, so not every new list enters at 600 names. Either raise the rebuild threshold to 600 (noting twice-short lists as exceptions), or change the size wording to "at most 600 names (used whole, at 550–600 names unless still short after one rebuild)."

2. **Preprint's own layout for Akkadian (splits 0–9 vs. splits 20–29)**
   - Quote: *"For the preprint's lists, the whole list in rounds 0 to 9, the preprint's own layout."* vs. *"all 80 archived runs checked: Tamil and Sanskrit, splits 0 to 9, and Tamil and Akkadian, splits 20 to 29, real and shuffled."*
   - Correction: In the preprint's archive, Akkadian was run on splits 20 to 29, not 0 to 9. Change the instruction to run Tamil and Sanskrit in rounds 0 to 9 and Akkadian (and its paired Tamil run, if reproducing the archive) in rounds 20 to 29, or note that rounds 0 to 9 matches the preprint's splits only for Tamil and Sanskrit.
