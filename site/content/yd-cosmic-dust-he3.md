---
# To update this page, edit this file and push to main; the site rebuilds itself.
# The figures are made by questions/yd-cosmic-dust-he3/analysis/make_figures.py from the results files.
summary: If a giant comet broke up over the last 20,000 years, the Earth should have passed through its fine dust for a long time. That dust carries helium-3, which fires and volcanoes cannot supply, and deep-sea mud keeps it. We looked for a rise in nine ocean cores from the Pacific and Atlantic. This tests a long-lived dust cloud; it cannot see a single day.
verdict: Mixed by the locked rule (one control failed). No rise in cosmic dust lasting thousands of years; a single day is beyond this method
result: Across 20,000 to 10,000 years ago, nine ocean cores measured by three laboratories hold the usual amount of helium-3 dust or slightly less (0.80 to 0.92 of the baseline). That is good evidence against a dust cloud lasting thousands of years. For a rise lasting only centuries it rests on one core, which rules out anything above about a third more than usual. Sea-floor mud blurs a thousand years or more together, and helium-3 rides only on fine dust, so the test says nothing about one day of large fragments, which is what the hypothesis's authors describe. One of three checks that the method works did not pass, so by the rule fixed in advance the verdict is mixed.
dek: Did the Earth pass through a long-lived cloud of comet dust at the end of the ice age? Spot-checked afterwards; not replicated.
updated: 2026-11-24
---

> **Where things stand, 24 November 2026.** The locked run finished with no amendments (by Antigravity, Google DeepMind, directed by Eugene). The verdict by the rule fixed in advance is **mixed** (`ambiguous_or_mixed`), because one of three positive controls failed. A spot check by Claude Fable 5.2 (Anthropic) reran the program, got the same numbers, and found that the page claimed more than they show: see the next section. No model from a second company has replicated the study, and none is planned for now.

{{figure: yd-cosmic-dust-he3/tiles}}

## Spot check: what holds and what does not

Anthropic's model checked this study after it was published and reran its program. Every number came out the same, and all 181 Pacific samples were read a second time from the public files with no mismatch. The page has been corrected in these places. The figures are as first made.

- **No rise lasting thousands of years: this holds.** Nine cores, three laboratories, the same answer.
- **"No surge on any timescale" does not.** Only one of the nine cores builds up fast enough to tell a thousand years from the next; the others blur two to nine thousand years together. For the Younger Dryas itself the test is that one core, and its upper limit is about a third above normal.
- **The checks that the method works are narrower than they sound.** Both that passed are the same event, an asteroid break-up 8.2 million years ago whose dust lasted about 1.5 million years. They do not show that a rise of centuries, or a comet's dust, would be seen. The third check failed, and the explanation for that was found afterwards.
- **A dating claim was wrong.** The best core does not have 20 radiocarbon dates inside the Younger Dryas. It has 6.
- **Which version of the hypothesis this tests.** A long-lived dust cloud belongs to the wider theory of a comet breaking up over thousands of years. The hypothesis's authors describe a single day of large fragments, and this test cannot see that.

The full list is in the study's `RESULTS.md`, and the checking script is in `questions/yd-cosmic-dust-he3/spotcheck/`.

## Why helium-3 is a clean test of a comet's dust cloud

Most physical arguments over the Younger Dryas Impact Hypothesis get tangled in terrestrial look-alikes: wildfires, soils, and volcanoes can all move ammonium, charcoal, or platinum around. **Extraterrestrial Helium-3 (`³He_ET`)** cannot be faked that way. Fine interplanetary dust particles (`< 50 µm`) shed by comets and asteroids soak up solar wind in space, giving them a `³He/⁴He` ratio roughly **10,000 times higher** than volcanic ash or Earth's crust. When a real comet or asteroid breaks up in the inner solar system, that dust settles evenly across the entire globe and turns up in deep-sea mud.

If the drawn-out Taurid comet-breakup model (Clube & Napier 1984; Napier 2010) is right—that a giant comet fragmented over the past ~20,000 years and filled Earth's orbit with debris—then **dilution-corrected `²³⁰Th`-normalized `³He_ET` flux** in ice-free pelagic ocean sediments should rise across the Younger Dryas (`13.5–11.5 ka`), the Late Deglaciation (`15–10 ka`), or the broad breakup epoch (`20–10 ka`).

We locked our protocol before inspecting any deglacial `³He_ET` values, assembling three pillars from open geochemical archives:

1. **Pillar 0 — Real cosmic-breakup positive controls:** Farley et al. (2006, *Nature*) pelagic records (`ODP 926B` in the Equatorial Atlantic and `ODP 757B` in the South Indian Ocean) spanning the confirmed **`8.2 Ma` Veritas asteroid breakup** and the **`35.5 Ma` Late Eocene comet/asteroid shower**.
2. **Pillar 1 — `²³⁰Th_xs,0`-normalized Pacific pelagic flux (`n = 181`, `7` cores, `2` labs):** Subarctic North Pacific `SO202-07-6` (Serno et al. 2015, Lamont-Doherty; `42` AMS `¹⁴C` dates, `6` of them in `13.5–11.5 ka` once calibrated), four Eastern Equatorial Pacific Cocos Ridge cores `CR01–CR05` (Tomchovska, Pavia & Farley 2025/2026, Caltech; `67` AMS `¹⁴C` dates), and Central Equatorial Pacific `MANOP_B18/B25` (Marcantonio et al. 2001, Lamont-Doherty; `0.3–325 ka`).
3. **Pillar 2 — Independent North Atlantic replication (`n = 117`, `2` cores, `3rd` lab) & polar ice benchmark:** Mid-Atlantic Ridge cores `KN207-2-GGC3` and `GGC6` (Middleton et al. 2018, UC Davis/Harvard), plus Brook et al. (2000) `GISP2` + `Vostok` ice-core absolute flux reference (`0.78 pcc cm⁻² kyr⁻¹`).

## Positive control: real breakups light up ocean mud

Before judging the Younger Dryas, we checked whether our locked median-ratio test catches real extraterrestrial dust showers in Farley et al. (2006). Use the toggle below to view both oceans across the **`8.2 Ma` Veritas breakup** and the **`35.5 Ma` Late Eocene shower**:

{{figure: yd-cosmic-dust-he3/positive_control}}

Both **`8.2 Ma` Veritas controls** pass cleanly: Equatorial Atlantic `ODP 926B` jumps **`2.31×`** (`95% CI [1.31, 2.90]`, `p = 0.00010`) and South Indian Ocean `ODP 757B` jumps **`2.28×`** (`95% CI [0.95, 3.85]`, `p = 0.00050`).

Our third blinded control (`ODP 757B` Late Eocene) missed its pre-registered threshold (`1.03×`, `p = 0.504`)—not because the shower is missing, but because our blinded baseline window (`25.0–33.5 Ma`) overlapped a late-Oligocene (`25.0–30.5 Ma`) step-up in `ODP 757B`. Relative to its immediately adjacent `30.5–34.5` and `36.2–38.5 Ma` bracketing sediments the `35.3–36.1 Ma` shower stands `4.00×` higher. That comparison was chosen after seeing the data, so it is exploration and not evidence. Under our locked rules, that single baseline miss still sets the formal rule-engine verdict to `ambiguous_or_mixed`.

## Deglacial cosmic dust across nine Pacific and Atlantic cores

Switch between the three Pacific regions and the North Atlantic replication below to inspect every individual sample across `0–30 ka`:

{{figure: yd-cosmic-dust-he3/deglacial_timeseries}}

No matter which ocean, which laboratory, or which target window we test, **extraterrestrial `³He_ET` flux does not rise**:

{{figure: yd-cosmic-dust-he3/window_forest}}

- **Narrow Younger Dryas (`13.5–11.5 ka`):** Pooled Pacific flux is **`0.921×`** baseline (`95% CI [0.769, 1.223]`, `p = 0.647`), with an upper limit of **`1.22×`** pooled; on the one core that can resolve this window the limit is `1.37×`.
- **Full Late Deglaciation (`15.0–10.0 ka`):** Pooled flux is **`0.840×`** (`95% CI [0.761, 0.975]`, `p = 0.926`)—even the 95% upper bound sits below `1.00×`.
- **Broad 10-kyr Taurid breakup epoch (`20.0–10.0 ka`):** Pooled flux is **`0.799×`** (`95% CI [0.694, 0.919]`, `p = 0.996`), remaining below `1.00×` against Holocene (`< 10 ka`, `0.806×`) and Glacial (`> 20 ka`, `0.964×`) baselines separately.
- **Blind top-10% peak scan:** Ranking all `181` Pacific samples without boundary labels puts **`0 of 18`** top-decile peaks (`≥ 2.17×` core median) inside `13.5–11.5 ka` or `15.0–10.0 ka` (`100%` outside; `p = 1.000`).
- **North Atlantic replication:** Mid-Atlantic Ridge `KN207-2-GGC3 & GGC6` (`n = 117`) show `0.686×` (`W1`), `0.896×` (`W2`), and `0.907×` (`W3`) on relative burial rate (`p ≥ 0.76`), and `0.630–0.887×` on raw `[³He_ET]` (`p ≥ 0.91`).
- **Endmember robustness:** Raising the assumed terrestrial `³He/⁴He` endmember tenfold in `SO202-07-6` shifts all three ratios even lower (`0.816×`, `0.800×`, `0.467×`).

## What this means

After an asteroid broke up 8.2 million years ago, fine dust reached the Earth in two to four times the usual amount for more than a million years, and ocean mud records it. Nothing like that shows across `20–10 ka` in nine Pacific and Atlantic cores from three laboratories (`0.80×` to `0.92×` of the baseline). That is good evidence against a cloud of comet dust lasting thousands of years.

It is weaker for anything shorter. Burrowing animals stir sea-floor mud, so the best of these cores blurs about a thousand years together and the others two to nine thousand; a rise lasting a few centuries is tested by one core, and a single day not at all. Helium-3 also rides only on fine dust that reaches the ground unheated, not on large fragments. So this study counts against a long-lived dust cloud, which is part of the wider theory and of the drawn-out version we built ourselves, and has nothing to say about the single day its authors describe. By the rule fixed in advance its verdict is "mixed", because one of the three checks on the method did not pass.

::: details Methods, data, and verification
- **Protocol and lock:** `questions/yd-cosmic-dust-he3/protocol.md`, locked at `2026-11-24T13:50:30Z` (`protocol.lock`, SHA-256 `000607b93cbb`). Zero amendments.
- **Public datasets:** Serno et al. (2015, *Paleoceanography*, `PANGAEA.845998` & `845972`), Tomchovska, Pavia & Farley (2025/2026, `Figshare 30340705`), Marcantonio et al. (2001, *Paleoceanography*, `PANGAEA.846689`), Middleton et al. (2018, *EPSL*, NOAA Study `25870`), Brook et al. (2000, *GRL*, NOAA Study `2454`), and Farley et al. (2006, *Nature*, `PANGAEA.769829` & `769830`). Full URLs, licences, and SHA-256 checksums in `questions/yd-cosmic-dust-he3/MANIFEST.md`.
- **Full report and code:** `questions/yd-cosmic-dust-he3/RESULTS.md`, `questions/yd-cosmic-dust-he3/analysis/cosmic_dust_he3.py`, and `questions/yd-cosmic-dust-he3/analysis/test_cosmic_dust_he3.py` (`5/5` synthetic verification tests passing).
:::
