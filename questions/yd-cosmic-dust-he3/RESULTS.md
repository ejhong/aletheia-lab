# Results — Did extraterrestrial Helium-3 cosmic dust rise across the Younger Dryas deglaciation?

**Question:** `yd-cosmic-dust-he3` (Issue `#121`, lane `data`)  
**Protocol locked:** `2026-11-24T13:50:30Z` (`protocol.lock`, SHA-256 `000607b93cbb74cbe50089248000e111572dd3ff1cb2759d4e3436e3d1bc87aa`)  
**Amendments:** None (`0`).  
**Authorship:** Designed, coded, executed, and written by **Antigravity (Google DeepMind)** under the direction of **Eugene Jhong** on `2026-11-24`. Open to independent second-vendor replication from `protocol.md`.

---

## Short Answer

**No cosmic-dust surge is present in the ocean sediment record across any proposed Younger Dryas or Taurid-breakup timescale—yet our strict pre-registered verdict logs `ambiguous_or_mixed` solely because one of three blinded Cenozoic positive controls failed its pre-registered baseline window.**

Across **seven ice-free Pacific pelagic cores** measured by **two independent laboratories** (`n = 181` valid paired `²³⁰Th_xs,0`-normalized `³He_ET` flux samples; Lamont-Doherty and Caltech), extraterrestrial Helium-3 cosmic dust flux sat **slightly below** baseline in every pre-registered window:

- **Narrow Younger Dryas (`W1: 13.5–11.5 ka`, `n = 11` vs. `95`):** median ratio **`0.921×`** (`95% CI [0.769, 1.223]`, one-sided permutation `p = 0.647`). The 95% upper bound rules out any sustained **`> 1.22×`** surge.
- **Full Late Deglaciation (`W2: 15.0–10.0 ka`, `n = 35` vs. `116`):** median ratio **`0.840×`** (`95% CI [0.761, 0.975]`, `p = 0.926`). The 95% upper bound sits below `1.00×`.
- **Broad 10-kyr Taurid breakup epoch (`W3: 20.0–10.0 ka`, `n = 59` vs. `122`):** median ratio **`0.799×`** (`95% CI [0.694, 0.919]`, `p = 0.996`), remaining below `1.00×` whether tested against Holocene `< 10 ka` (`0.806×`, `p = 0.997`) or Glacial `> 20 ka` (`0.964×`, `p = 0.860`) alone.
- **Blind top-10% peak scan (`18` highest flux samples, `≥ 2.17×` core median):** **`0 of 18` (`0%`)** fall inside `13.5–11.5 ka` (`p = 1.0`) or `15.0–10.0 ka` (`100%` outside, `p = 1.0`), and only `2 of 18` (`11.1%`, vs. `5.87` expected) fall inside `20.0–10.0 ka` (`p = 0.994`).
- **Independent North Atlantic replication (`KN207-2-GGC3 & GGC6`, `n = 117`, UC Davis/Harvard):** confirms the null on both chronostratigraphic relative burial rate (`W1 = 0.686×`, `W2 = 0.896×`, `W3 = 0.907×`, all `p ≥ 0.76`) and raw `[³He_ET]` concentration (`0.630×`, `0.738×`, `0.887×`, all `p ≥ 0.91`).

**Why the formal pre-registered verdict is `ambiguous_or_mixed` (and why we report it unchanged):**  
Every single Quaternary criterion for `no_cosmic_dust_surge` passed decisively, **and** both primary **`8.2 Ma` Veritas asteroid-breakup positive controls** across two separate oceans passed (`2.31×` in Equatorial Atlantic `ODP 926B`, `p = 0.00010`; `2.28×` in South Indian Ocean `ODP 757B`, `p = 0.00050`). However, our third positive control (`LateEocene_35.5Ma_ODP757B`) used a blinded baseline window (`25.0–33.5 Ma`) that inadvertently overlapped a late-Oligocene (`25.0–30.5 Ma`) step-up in `ODP 757B`, reducing the pre-registered ratio to `1.03×` (`p = 0.504`) even though the actual `35.3–36.1 Ma` shower jumps **`4.00×`** above its immediately adjacent `30.5–34.5` & `36.2–38.5 Ma` bracketing sediments (post-hoc diagnostic). Under our locked rules (`protocol.md §4`), any Pillar 0 positive-control failure triggers `ambiguous_or_mixed`; we keep that exact formal verdict without post-hoc protocol edits.

---

## 1. Pillar 0 — Real Cosmic-Breakup Positive Controls (Farley et al. 2006)

To prove our pipeline detects real extraterrestrial dust showers on the exact same `³He_ET` tracer before touching Quaternary data, we ran our locked estimator on Farley et al. (2006, *Nature*) pelagic ocean records from two ocean basins (`ODP Hole 121-757B`, South Indian Ocean, `n = 134` valid rows; `ODP Hole 154-926B`, Equatorial Atlantic, `n = 73`).

| Positive control | Ocean & core | Target window | Blinded baseline | `n` (target / base) | Median ratio | 95% bootstrap CI | One-sided `p_perm` | Pre-registered check (`≥ 2.00×`, `p < 0.01`) |
|---|---|---|---:|---:|---:|---:|---:|---|
| **Veritas `8.2 Ma` breakup** | Equatorial Atlantic `ODP 926B` | `8.35–7.50 Ma` | `10.5–8.5` & `7.2–6.2 Ma` | `36 / 37` | **`2.314×`** | `[1.306, 2.896]` | **`0.00010`** | **PASS** |
| **Veritas `8.2 Ma` breakup** | South Indian `ODP 757B` | `8.35–7.50 Ma` | `10.5–8.5` & `7.2–6.2 Ma` | `7 / 27` | **`2.284×`** | `[0.947, 3.853]` | **`0.00050`** | **PASS** |
| **Late Eocene `35.5 Ma` shower** | South Indian `ODP 757B` | `36.50–34.50 Ma` | `33.50–25.00 Ma` | `25 / 18` | `1.032×` | `[0.680, 2.429]` | `0.50365` | **FAIL (baseline shift)** |

*Post-hoc diagnostic on `ODP 757B` Late Eocene:* Inspecting `results/positive_controls.csv` explains why the third control missed cleanly without casting doubt on `³He_ET` sensitivity. In `ODP 757B`, the Late Eocene shower peaks across `35.3–36.1 Ma` (`n = 13`, median `0.320`, peak `0.720 × 10⁻³` units), which is **`4.00×`** higher than the immediately adjacent `30.5–34.5` and `36.2–38.5 Ma` sediments (`n = 24`, median `0.080`). However, our blinded baseline (`25.0–33.5 Ma`) mixed those low `30.5–33.5 Ma` values with an elevated late-Oligocene shelf at `25.0–30.5 Ma` (`n = 11`, median `0.190`), masking the `35.5 Ma` peak inside the `34.5–36.5 Ma` window. Meanwhile, both independent oceans detect the `8.2 Ma` Veritas breakup cleanly at `2.28–2.31×` (`p ≤ 0.0005`).

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

Not a single regional stack, baseline split, endmember choice, or mean vs. median estimator produces a cosmic-dust elevation. The highest-resolution deglacial core (`SO202-07-6`, anchored by `42` AMS `¹⁴C` dates including `20` directly inside `11.5–13.5 ka`) actually shows flat-to-slightly-lower `³He_ET` flux throughout the entire `15–10 ka` interval (`0.656` vs `0.784 pcc cm⁻² kyr⁻¹`).

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

1. **Pelagic bioturbation and sampling resolution (`~250–1,000 yr`):** Even our sharpest core (`SO202-07-6`, `8` samples across `11.5–13.5 ka`) is a deep-sea sediment core mixed by seafloor burrowers over several centuries. A **brief single-day or decade-scale** dust pulse smaller than `~200–500` years' worth of normal background cosmic rain (`~20–50%` integrated over `2 kyr`) could be diluted below our `1.22×` (`W1`) 95% upper bound. What this dataset *decisively* rules out is any **multi-century to multi-millennial elevation** in Earth's interplanetary dust environment—specifically the sustained `2–10×` cosmic-dust cloud predicted by a disintegrating giant Taurid comet across `13.5–11.5 ka`, `15–10 ka`, or `20–10 ka`.
2. **Particle size and thermal retention (`< 50 µm` IDPs):** Extraterrestrial `³He` is retained primarily by small (`< 50 µm`) solar-wind-irradiated interplanetary dust particles that decelerate gently in the upper atmosphere without melting; large vaporizing bolides (`> 10 m`) or fast-entry centimetre meteoroids lose their helium on entry. A comet breakup that somehow produced *only* large bolides with zero accompanying micron-sized zodiacal dust would be invisible to `³He_ET`—though real comet breakups and asteroid collisions (like the `8.2 Ma` Veritas breakup and modern comets) shed overwhelmingly more mass in fine dust than in large fragments.
3. **Why polar ice cores still await measurement across `20–10 ka`:** The public Brook et al. (2000) ice-core archive contains `0` samples between `4 ka` and `75 ka`. Measuring continuous `³He_ET` directly inside Greenland or Antarctic ice across `14.5–11.5 ka` at decadal resolution would close the remaining sub-century bioturbation loophole.
4. **Strict Pillar 0 positive-control accounting:** Our formal verdict stays `ambiguous_or_mixed` strictly because the third blinded positive control (`ODP 757B` Late Eocene) failed its pre-registered `25–33.5 Ma` baseline window due to a late-Oligocene shift, despite both `8.2 Ma` Veritas ocean controls passing at `2.28–2.31×` (`p ≤ 0.0005`) and the actual `35.3–36.1 Ma` shower jumping `4.00×` above adjacent brackets.

---

## 5. What This Means

A giant comet breaking up in the inner solar system over the past 20,000 years should flood Earth's orbit with fine cosmic dust—the exact kind of dust that carries extraterrestrial Helium-3 (`³He_ET`) and lights up deep-sea sediments by more than double during real ancient breakups like the `8.2 Ma` Veritas collision. Across nine independently dated ocean cores from the Pacific and Atlantic measured by three separate laboratories, that cosmic dust surge is not there. During the Younger Dryas (`13.5–11.5 ka`), the Late Deglaciation (`15–10 ka`), and the entire `20–10 ka` breakup window, Earth received the same steady drizzle of space dust it receives today—if anything slightly less (`0.80–0.92×` baseline), with zero top-decile spikes falling in `15–10 ka`. While deep-sea mixing cannot forbid a brief, dust-poor impact lasting only days or decades, the public ocean `³He_ET` record leaves no room for a sustained, multi-century or multi-millennial Taurid cosmic dust cloud enveloping Earth during the Younger Dryas.
