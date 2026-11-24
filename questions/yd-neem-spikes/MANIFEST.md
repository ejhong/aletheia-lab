# Data manifest — `yd-neem-spikes`

All primary public datasets were downloaded on **2026-11-24 (UTC)** into git-ignored `questions/yd-neem-spikes/data/`.

| File | Source & URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| `data/neem_cfa_1mm.tab` | Erhardt et al. (2021/2022), *Earth Syst. Sci. Data* 14:1215–1231, PANGAEA: <https://doi.pangaea.de/10.1594/PANGAEA.935837?format=textfile> | 2026-11-24 | CC-BY-4.0 | `28b8aceefbb1370748e2ded65c799e401f94cf0c275ec61b921b2e2097a69973` | 1 mm continuous-flow NEEM `EC, Na+, Ca2+, [NH4]+, [NO3]-` (`7.323–2544.049 m`, 96 MB). Column identity verified against 10-yr file on blinded 16–17 ka control band (`NH4 = 3.46` vs `3.52 µg/kg`; `NO3 = 93.25` vs `94.44 µg/kg`). |
| `data/neem_cfa_10yr.tab` | Erhardt et al. (2021), PANGAEA: <https://doi.pangaea.de/10.1594/PANGAEA.935831?format=textfile> | 2026-11-24 | CC-BY-4.0 | `22fc97d7c50af6badda2de4cfbe66a66fad5c6552c754575916ea8c24b1ab03f` | 10-yr averaged NEEM impurities on GICC05 (used strictly for blinded column-identity & age-scale cross-check). |
| `data/neem_gicc05_5cm.tab` | Gkinis et al. (2020/2021), *Scientific Data* 8:141 (incorporating Rasmussen et al. 2013 `GICC05modelext-NEEM-1`), PANGAEA: <https://doi.pangaea.de/10.1594/PANGAEA.925552?format=textfile> | 2026-11-24 | CC-BY-4.0 | `dea79326c54bfe3619b2e56e5556b4ea5426ced66c2a29fcb45c6cf3ed6ceb09` | Official 5 cm depth-to-age GICC05 timescale (`1210.50–1955.90 m`, `8,000.2–60,197.9 yr b2k`) plus NEEM `δ¹⁸O`. |

## Published event table (committed in folder)

- `events.tsv` (`7b9c572a5f6ae8e423ca71e443dec7f01bc4370b6fe5cf037dd8485da14ab3a6`): Rasmussen et al. (2014), *Quaternary Science Reviews* 106:14–28, Table 2 (GICC05 stadial onset ages, including Younger Dryas / `GS-1` onset at `12,896 yr b2k`).

## Software environment

- Python `3.12.16`, `numpy==2.3.5`, `scipy==1.18.1`.

## Analysis scripts (frozen at lock)

| File | SHA-256 |
|---|---|
| `analysis/neem_spikes.py` | `3950e4162aad4003817ff15079fde2062d3d1addc8cea761a993289a6b7c874b` |
| `analysis/test_neem_spikes.py` | `4f294a7f7d60671238e32780bb53e6dc9a1377756ffd409e5ee370c185b1217f` |
