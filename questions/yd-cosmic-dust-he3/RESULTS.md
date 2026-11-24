# Results — Did extraterrestrial Helium-3 cosmic dust rise across the Younger Dryas deglaciation?

**Question:** `yd-cosmic-dust-he3` (Issue `#121`, lane `data`)  
**Protocol locked:** `2026-11-24T13:50:30Z` (`protocol.lock`, SHA-256 `000607b93cbb74cbe50089248000e111572dd3ff1cb2759d4e3436e3d1bc87aa`)  
**Amendments:** None (`0`).  
**Authorship:** Designed, coded, executed, and written by **Antigravity (Google DeepMind)** under the direction of **Eugene Jhong** on `2026-11-24`. Open to independent second-vendor replication from `protocol.md`.

---

## Short Answer

**Mixed, by the rule fixed in advance: one of three positive controls failed. Setting that aside, nine ocean cores show no rise in helium-3 dust lasting thousands of years across 20,000 to 10,000 years ago. For a rise lasting centuries the evidence is one core. A single day is beyond this method (see the spot check below).**

Across **seven ice-free Pacific pelagic cores** measured by **two independent laboratories** (`n = 181` valid paired `²³⁰Th_xs,0`-normalized `³He_ET` flux samples; Lamont-Doherty and Caltech), extraterrestrial Helium-3 cosmic dust flux sat **slightly below** baseline in every pre-registered window:

- **Narrow Younger Dryas (`W1: 13.5–11.5 ka`, `n = 11` vs. `95`):** median ratio **`0.921×`** (`95% CI [0.769, 1.223]`, one-sided permutation `p = 0.647`). The 95% upper bound rules out any sustained **`> 1.22×`** surge.
- **Full Late Deglaciation (`W2: 15.0–10.0 ka`, `n = 35` vs. `116`):** median ratio **`0.840×`** (`95% CI [0.761, 0.975]`, `p = 0.926`). The 95% upper bound sits below `1.00×`.
- **Broad 10-kyr Taurid breakup epoch (`W3: 20.0–10.0 ka`, `n = 59` vs. `122`):** median ratio **`0.799×`** (`95% CI [0.694, 0.919]`, `p = 0.996`), remaining below `1.00×` whether tested against Holocene `< 10 ka` (`0.806×`, `p = 0.997`) or Glacial `> 20 ka` (`0.964×`, `p = 0.860`) alone.
- **Blind top-10% peak scan (`18` highest flux samples, `≥ 2.17×` core median):** **`0 of 18` (`0%`)** fall inside `13.5–11.5 ka` (`p = 1.0`) or `15.0–10.0 ka` (`100%` outside, `p = 1.0`), and only `2 of 18` (`11.1%`, vs. `5.87` expected) fall inside `20.0–10.0 ka` (`p = 0.994`).
- **Independent North Atlantic replication (`KN207-2-GGC3 & GGC6`, `n = 117`, UC Davis/Harvard):** confirms the null on both chronostratigraphic relative burial rate (`W1 = 0.686×`, `W2 = 0.896×`, `W3 = 0.907×`, all `p ≥ 0.76`) and raw `[³He_ET]` concentration (`0.630×`, `0.738×`, `0.887×`, all `p ≥ 0.91`).

**Why the formal pre-registered verdict is `ambiguous_or_mixed` (and why we report it unchanged):**  
Every single Quaternary criterion for `no_cosmic_dust_surge` passed decisively, **and** both primary **`8.2 Ma` Veritas asteroid-breakup positive controls** across two separate oceans passed (`2.31×` in Equatorial Atlantic `ODP 926B`, `p = 0.00010`; `2.28×` in South Indian Ocean `ODP 757B`, `p = 0.00050`). However, our third positive control (`LateEocene_35.5Ma_ODP757B`) used a blinded baseline window (`25.0–33.5 Ma`) that inadvertently overlapped a late-Oligocene (`25.0–30.5 Ma`) step-up in `ODP 757B`, reducing the pre-registered ratio to `1.03×` (`p = 0.504`) even though the actual `35.3–36.1 Ma` shower jumps **`4.00×`** above its immediately adjacent `30.5–34.5` & `36.2–38.5 Ma` bracketing sediments (a comparison chosen after seeing the data: exploratory, not evidence). Under our locked rules (`protocol.md §4`), any Pillar 0 positive-control failure triggers `ambiguous_or_mixed`; we keep that exact formal verdict without post-hoc protocol edits.

---

## Spot check and corrections (24 November 2026)

Claude Fable 5.2 (Anthropic), with a sub-agent (Claude Opus 5.5), checked this study after it was published. The
lock is in order. All nine data files match their hashes and a rerun of the locked program gives the four results
files byte for byte. The sample values come from public data files, not from tables in papers; all 181 Pacific
rows were read a second time independently, with no mismatch. The formal verdict, `ambiguous_or_mixed`, follows
from the locked rules. What the study can tell is narrower than this report says. The headline has been rewritten
and wrong statements corrected in the text; the rest is as first published. The scripts and their output are in
`spotcheck/`.

1. **The headline went beyond the locked result.** The plan required every positive control to pass before the
   answer "no surge" could be given. One of three failed. The reason offered for the failure, a window that
   overlapped a later rise, was found by looking at the data afterwards, and the "4.00×" that goes with it (4.12 at full precision) uses
   windows chosen afterwards. It is exploration, not evidence, and is now labelled so wherever it appears.
2. **The Younger Dryas window is tested by one core.** Mud on the sea floor is stirred by burrowing animals, so
   each sample averages over some span of time. From the cores' own depths and ages, SO202-07-6 builds up at
   about 6.5 cm per thousand years and averages over roughly a thousand years. The other eight build up at 1.2
   to 2.2 cm per thousand years and average over two to nine thousand (taking the stirred layer as 5 to 10 cm
   deep, which is an assumption). "250 to 1,000 years" applies to the first
   core only. That core alone gives a ratio of 0.92 with an upper bound of 1.37; the pooled bound of 1.22 is
   tightened by three samples from cores that cannot resolve a 2,000-year window. Samples next to one another
   in a core are not independent, so all the intervals are somewhat too narrow.
3. **What the controls show.** Both controls that passed are from one event 8.2 million years ago in which the
   dust rose about fourfold for about 1.5 million years, and that event was the break-up of an asteroid. They
   show that the arithmetic finds a large, very long rise. They do not show that a rise lasting centuries would
   be seen, or that a comet's dust would be. The one control that may record comets is the one that failed.
4. **Helium-3 counts only fine dust that arrives gently.** The report says so (Limits, point 2) and then says
   that comet break-ups "shed overwhelmingly more mass in fine dust than in large fragments", with no source.
   Dust on a fast, comet-like orbit is heated more on entry and may keep less of its helium than the slow
   asteroid dust that makes up most of the usual supply. We did not check a source for that either. Both
   statements should be read as unverified. The "2–10×" cloud that the report says the theory predicts also has
   no citation.
5. **A wrong statement about dating.** The report says the best core has 20 of its 42 radiocarbon dates "directly
   inside 11.5–13.5 ka". Those are raw radiocarbon ages. Converted to calendar years they fall at about 13,200
   to 15,200 years ago, and 6 dates fall in the Younger Dryas window.
6. **Smaller points.** "Gold-standard" overstates the four Cocos Ridge cores: they come from a study of whether
   the thorium and helium methods agree, which found that they differ significantly in 3 of the 4. The windows
   15 to 10 and 20 to 10 thousand years ago show a drop of 16% to 20% that is statistically clear, which the
   report calls "the same steady drizzle"; it is better read as the size of the method's own wobble. The
   comparison with polar ice is a check of units and no more: the ice has no samples between 4,000 and 75,000
   years ago, and the cores' own medians differ by a factor of 1.6. In the blind scan of the 18 highest samples,
   11 are from two cores whose samples are mostly older than 60,000 years and could not have fallen in any
   window. One conversion in the program is wrong by a factor of 1,000, so the flux column of
   `results/positive_controls.csv` is a thousand times too small; the ratios do not depend on it.

**What the study shows, restated.** Over 15,000 to 10,000 and 20,000 to 10,000 years ago, nine ocean cores from
three laboratories show no rise in the fine cosmic dust that carries helium-3; if anything a little less. That is
solid for a rise lasting thousands of years. For one lasting centuries it rests on a single core, which rules out
anything above about a third more than usual. It says nothing about a single day.

**Which version of the hypothesis this bears on.** A long-lived cloud of dust belongs to the wider theory of a
comet breaking up over thousands of years, and to the drawn-out version we built ourselves ([the topic
page](../../site/topics/younger-dryas.md) sets out the three versions). The hypothesis's authors describe one
day of large fragments. Large fragments carry almost no helium-3, and one day cannot be resolved in this mud, so
this study neither helps nor hurts that version.

**Not replicated.** No model from a second company has rewritten this analysis from the plan, which the lab's rules
ask for before a `data` question is called done. None is planned for now.

---

## 1. Pillar 0 — Real Cosmic-Breakup Positive Controls (Farley et al. 2006)

To prove our pipeline detects real extraterrestrial dust showers on the exact same `³He_ET` tracer before touching Quaternary data, we ran our locked estimator on Farley et al. (2006, *Nature*) pelagic ocean records from two ocean basins (`ODP Hole 121-757B`, South Indian Ocean, `n = 134` valid rows; `ODP Hole 154-926B`, Equatorial Atlantic, `n = 73`).

| Positive control | Ocean & core | Target window | Blinded baseline | `n` (target / base) | Median ratio | 95% bootstrap CI | One-sided `p_perm` | Pre-registered check (`≥ 2.00×`, `p < 0.01`) |
|---|---|---|---:|---:|---:|---:|---:|---|
| **Veritas `8.2 Ma` breakup** | Equatorial Atlantic `ODP 926B` | `8.35–7.50 Ma` | `10.5–8.5` & `7.2–6.2 Ma` | `36 / 37` | **`2.314×`** | `[1.306, 2.896]` | **`0.00010`** | **PASS** |
| **Veritas `8.2 Ma` breakup** | South Indian `ODP 757B` | `8.35–7.50 Ma` | `10.5–8.5` & `7.2–6.2 Ma` | `7 / 27` | **`2.284×`** | `[0.947, 3.853]` | **`0.00050`** | **PASS** |
| **Late Eocene `35.5 Ma` shower** | South Indian `ODP 757B` | `36.50–34.50 Ma` | `33.50–25.00 Ma` | `25 / 18` | `1.032×` | `[0.680, 2.429]` | `0.50365` | **FAIL (baseline shift)** |

*Exploratory, made after the result was known, and not evidence:* Inspecting `results/positive_controls.csv` suggests why the third control missed. In `ODP 757B`, the Late Eocene shower peaks across `35.3–36.1 Ma` (`n = 13`, median `0.320`, peak `0.720 × 10⁻³` units), which is **`4.00×`** higher than the immediately adjacent `30.5–34.5` and `36.2–38.5 Ma` sediments (`n = 24`, median `0.080`). However, our blinded baseline (`25.0–33.5 Ma`) mixed those low `30.5–33.5 Ma` values with an elevated late-Oligocene shelf at `25.0–30.5 Ma` (`n = 11`, median `0.190`), masking the `35.5 Ma` peak inside the `34.5–36.5 Ma` window. Meanwhile, both independent oceans detect the `8.2 Ma` Veritas breakup cleanly at `2.28–2.31×` (`p ≤ 0.0005`).

---

## 2. Pillar 1 — Gold-Standard `²³⁰Th_xs,0`-Normalized `³He_ET` Flux (`7` Pacific Cores, `n = 181`)

Normalizing `[³He_ET]` by **`²³⁰Th_xs,0`-derived vertical mass accumulation rate** cancels both terrestrial/biogenic dilution and lateral bottom-current focusing, isolating true vertical extraterrestrial `³He_ET` rain rate (`pcc STP cm⁻² kyr⁻¹`).

### 2.1 Core Overview & Absolute Flux Agreement with Polar Ice

| Core | Region | Lab | Valid `n` | Age span (`ka BP`) | `n` in `W1` (`13.5–11.5`) | `n` in `W2` (`15–10`) | `n` in `W3` (`20–10`) | Median flux (`pcc cm⁻² kyr⁻¹`) | IQR |
|---|---|---|---:|---|---:|---:|---:|---:|---:|
| `SO202-07-6` | Subarctic North Pacific | Lamont-Doherty (Winckler) | `51` | `3.89–27.07` | `8` | `22` | `33` | `0.659` | `0.521` |
| `CR01` | E. Eq. Pacific (Cocos Ridge) | Caltech (Farley/Pavia) | `18` | `0.00–21.02` | `1` | `3` | `6` | `0.900` | `0.274` |
| `CR02` | E. Eq. Pacific (Cocos Ridge) | Caltech (Farley/Pavia) | `20` | `1.95–21.44` | `1` | `2` | `5` | `0.916` | `0.173` |
| `CR03` | E. Eq. Pacific (Cocos Ridge) | Caltech (Farley/Pavia) | `17` | `4.36–17.32` | `1` | `3` | `7` | `0.578` | `0.132` |
| `CR05` | E. Eq. Pacific (Cocos Ridge) | Caltech (Farley/Pavia) | `18` | `0.00–15.03` | `0` | `4` | `5` | `0.760` | `0.197` |
| `MANOP_B18` | Central Equatorial Pacific | Lamont-Doherty (Marcantonio) | `30` | `0.30–325.0` | `0` | `0` | `1` | `0.660` | `0.580` |
| `MANOP_B25` | Central Equatorial Pacific | Lamont-Doherty (Marcantonio) | `27` | `7.70–265.0` | `0` | `1` | `2` | `0.880` | `0.920` |
| **Ice Reference** (`Vostok` + `GISP2`, Brook 2000) | Polar Ice Sheets | Woods Hole (Kurz/Brook) | `28` | `0.4–4` & `75–97` | `0` | `0` | `0` | **`0.780`** | (`0.73` Hol / `0.80` Glac) |

*(Note: `3` of `76` Cocos Ridge rows and `3` of `60` MANOP rows had missing paired age or flux entries in the primary source tables, leaving `n = 181` complete paired rows.)* Every single pelagic ocean core reproduces the global Late Quaternary extraterrestrial `³He_ET` constant (`0.58–0.92 pcc cm⁻² kyr⁻¹`), matching the direct polar ice-core benchmark (`0.78 pcc cm⁻² kyr⁻¹`).

### 2.2 Pre-Registered Window Tests (Pooled & Regional)

| Dataset / Region | Window | `n` (target / base) | Target median (raw) | Baseline median (raw) | Core-norm median ratio | Mean ratio | 95% bootstrap CI | One-sided `p_perm` (`H₁: > 1`) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Pooled 7 Pacific cores (`²³⁰Th`)** | **`W1` (`13.5–11.5 ka`)** | `11 / 95` | `0.659` | `0.828` | **`0.921×`** | `0.799×` | **`[0.769, 1.223]`** | `0.647` |
| **Pooled 7 Pacific cores (`²³⁰Th`)** | **`W2` (`15.0–10.0 ka`)** | `35 / 116` | `0.676` | `0.834` | **`0.840×`** | `0.745×` | **`[0.761, 0.975]`** | `0.926` |
| **Pooled 7 Pacific cores (`²³⁰Th`)** | **`W3` (`20.0–10.0 ka`)** | `59 / 122` | `0.653` | `0.835` | **`0.799×`** | `0.769×` | **`[0.694, 0.919]`** | `0.996` |
| Pooled `W3` vs. Holocene (`< 10 ka`) only | `20.0–10.0` vs `< 10` | `57 / 58` | `0.659` | `0.845` | `0.806×` | `0.847×` | `[0.700, 0.917]` | `0.997` |
| Pooled `W3` vs. Glacial (`> 20 ka`) only | `20.0–10.0` vs `> 20` | `36 / 61` | `0.613` | `0.770` | `0.964×` | `0.917×` | `[0.741, 1.281]` | `0.860` |
| Subarctic N. Pacific `SO202-07-6` | `W1` (`13.5–11.5 ka`) | `8 / 43` | `0.656` | `0.716` | `0.917×` | `0.657×` | `[0.630, 1.371]` | `0.630` |
| Subarctic N. Pacific `SO202-07-6` | `W2` (`15.0–10.0 ka`) | `22 / 29` | `0.656` | `0.784` | `0.836×` | `0.584×` | `[0.556, 1.420]` | `0.691` |
| Subarctic N. Pacific `SO202-07-6` | `W3` (`20.0–10.0 ka`) | `33 / 18` | `0.640` | `0.897` | `0.714×` | `0.677×` | `[0.436, 1.167]` | `0.888` |
| `SO202-07-6` high-`R_terr` (`2×10⁻⁷`) check | `W1 / W2 / W3` | `8 / 22 / 33` | `0.392 / 0.437 / 0.378` | — | `0.816× / 0.800× / 0.467×` | — | — | `0.690 / 0.699 / 0.984` |
| E. Eq. Pacific Cocos Ridge `CR01–CR05` | `W1` (`13.5–11.5 ka`) | `3 / 52` | `0.887` | `0.832` | `0.962×` | `0.990×` | `[0.910, 0.984]` | `0.715` |
| E. Eq. Pacific Cocos Ridge `CR01–CR05` | `W2` (`15.0–10.0 ka`) | `12 / 61` | `0.727` | `0.833` | `0.894×` | `0.886×` | `[0.789, 0.962]` | `0.945` |
| E. Eq. Pacific Cocos Ridge `CR01–CR05` | `W3` (`20.0–10.0 ka`) | `23 / 50` | `0.734` | `0.835` | `0.878×` | `0.871×` | `[0.792, 0.972]` | `0.989` |
| Central Eq. Pacific `MANOP_B18/B25` | `W2 / W3` | `1 / 3` | `0.480 / 0.400` | `0.970 / 0.785` | `0.495× / 0.453×` | — | — | `0.922 / 0.997` |

Not a single regional stack, baseline split, endmember choice, or mean vs. median estimator produces a cosmic-dust elevation. The highest-resolution deglacial core (`SO202-07-6`, anchored by `42` AMS `¹⁴C` dates, `6` of which fall in `13.5–11.5 ka` once calibrated) actually shows flat-to-slightly-lower `³He_ET` flux throughout the entire `15–10 ka` interval (`0.656` vs `0.784 pcc cm⁻² kyr⁻¹`).

### 2.3 Blind Top-10% Peak Scan (No Boundary Labels)

Ranking all `181` Pillar 1 samples by core-normalized flux without knowing where the Younger Dryas falls identifies `18` top-decile peaks (`≥ 2.167×` core median, reaching up to `7.99×` at `16.43 ka` and `5.52×` at `26.48 ka` in `SO202-07-6` — characteristic single-sample IDP "nuggets" or isolated glacial scatter):

- **`W1` (`13.5–11.5 ka`, `11` samples):** **`0 / 18`** top-decile peaks (`1.09` expected; `100%` outside; `p = 1.000`).
- **`W2` (`15.0–10.0 ka`, `35` samples):** **`0 / 18`** top-decile peaks (`3.48` expected; `100%` outside; `p = 1.000`).
- **`W3` (`20.0–10.0 ka`, `59` samples):** **`2 / 18`** top-decile peaks (`16.43 ka` and `17.01 ka` in `SO202-07-6`, vs. `5.87` expected; `88.9%` outside; `p = 0.994`).

---

## 3. Pillar 2 — Independent North Atlantic Replication (`KN207-2-GGC3 & GGC6`, `n = 117`)

Measured by a **third independent laboratory** (UC Davis / Harvard; Middleton et al. 2018, *EPSL* / NOAA Study `25870`), two Mid-Atlantic Ridge cores (`26°N` and `29°N`) span `0.5–68.8 ka`. Neither relative chronostratigraphic burial rate (`[³He_ET] × LSR`) nor raw `[³He_ET]` concentration rises in any window:

| Atlantic Metric (`GGC3 + GGC6`, `n = 117`) | Window | `n` (target / base) | Core-norm median ratio | Mean ratio | 95% bootstrap CI | One-sided `p_perm` |
|---|---|---:|---:|---:|---:|---:|
| Relative burial rate (`[³He_ET] × LSR`) | `W1` (`13.5–11.5 ka`) | `5 / 112` | **`0.686×`** | `0.638×` | `[0.531, 0.760]` | `0.958` |
| Relative burial rate (`[³He_ET] × LSR`) | `W2` (`15.0–10.0 ka`) | `10 / 107` | **`0.896×`** | `0.895×` | `[0.654, 1.293]` | `0.779` |
| Relative burial rate (`[³He_ET] × LSR`) | `W3` (`20.0–10.0 ka`) | `21 / 96` | **`0.907×`** | `0.879×` | `[0.751, 1.116]` | `0.761` |
| Raw `[³He_ET]` concentration | `W1 / W2 / W3` | `5 / 10 / 21` | `0.630× / 0.738× / 0.887×` | — | `[0.57–0.71] / [0.62–1.09] / [0.68–1.02]` | `0.988 / 0.997 / 0.918` |

---

## 4. Limits and What This Cannot Rule Out

1. **Pelagic bioturbation and sampling resolution (about `1,000 yr` in the best core, `2,000–9,000 yr` in the others):** Even our sharpest core (`SO202-07-6`, `8` samples across `11.5–13.5 ka`) is a deep-sea sediment core mixed by seafloor burrowers over several centuries. A **brief single-day or decade-scale** dust pulse smaller than `~200–500` years' worth of normal background cosmic rain (`~20–50%` integrated over `2 kyr`) could be diluted below our `1.22×` (`W1`) 95% upper bound. What this dataset rules out is a **rise lasting thousands of years** in the fine dust reaching the Earth, and, on one core, a rise of more than about a third lasting centuries. The `2–10×` cloud is this report's own figure for what a disintegrating giant Taurid comet would produce; no source is cited for it across `13.5–11.5 ka`, `15–10 ka`, or `20–10 ka`.
2. **Particle size and thermal retention (`< 50 µm` IDPs):** Extraterrestrial `³He` is retained primarily by small (`< 50 µm`) solar-wind-irradiated interplanetary dust particles that decelerate gently in the upper atmosphere without melting; large vaporizing bolides (`> 10 m`) or fast-entry centimetre meteoroids lose their helium on entry. A comet breakup that somehow produced *only* large bolides with zero accompanying micron-sized zodiacal dust would be invisible to `³He_ET`—though real comet breakups and asteroid collisions (like the `8.2 Ma` Veritas breakup and modern comets) shed overwhelmingly more mass in fine dust than in large fragments.
3. **Why polar ice cores still await measurement across `20–10 ka`:** The public Brook et al. (2000) ice-core archive contains `0` samples between `4 ka` and `75 ka`. Measuring continuous `³He_ET` directly inside Greenland or Antarctic ice across `14.5–11.5 ka` at decadal resolution would close the remaining sub-century bioturbation loophole.
4. **Strict Pillar 0 positive-control accounting:** Our formal verdict stays `ambiguous_or_mixed` strictly because the third blinded positive control (`ODP 757B` Late Eocene) failed its pre-registered `25–33.5 Ma` baseline window due to a late-Oligocene shift, despite both `8.2 Ma` Veritas ocean controls passing at `2.28–2.31×` (`p ≤ 0.0005`) and, in a comparison chosen afterwards (exploratory), the `35.3–36.1 Ma` shower standing `4.00×` above adjacent brackets.

---

## 5. What This Means

If a giant comet broke up in the inner solar system over the past 20,000 years and filled the Earth's neighbourhood with fine dust for thousands of years, that dust should show in deep-sea mud as extra helium-3, as it does about fourfold after an asteroid broke up 8.2 million years ago. In nine ocean cores from the Pacific and Atlantic, measured by three laboratories, it does not: across 20,000 to 10,000 years ago the mud holds the usual amount or slightly less. That is good evidence against a dust cloud lasting thousands of years. Against one lasting a few centuries it is one core's evidence, and against a single day it is none, because sea-floor mud blurs a thousand years or more together and because helium-3 rides only on fine dust, not on large fragments. By the rule we fixed in advance the result is also formally "mixed", since one of our three checks that the method works did not pass.
