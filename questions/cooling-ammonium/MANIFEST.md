# Data manifest

The ice-core files are those of question #43; `data` is a link to that question's git-ignored `data/` folder. No
new download was made.

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| NGRIP 10-year impurity means (`data/pangaea/935814.tab`) | <https://doi.pangaea.de/10.1594/PANGAEA.935814?format=textfile> | 2026-11-23 | CC-BY-4.0 | `b3ce78cce77d663875fd4ce664ab2831397752d636d70672094fb1bbd2841bba` | Erhardt et al. 2021 |
| NEEM 10-year impurity means (`data/pangaea/935831.tab`) | <https://doi.pangaea.de/10.1594/PANGAEA.935831?format=textfile> | 2026-11-23 | CC-BY-4.0 | `22fc97d7c50af6badda2de4cfbe66a66fad5c6552c754575916ea8c24b1ab03f` | Erhardt et al. 2021 |

## Made from a published table

`events.tsv`: the onsets of events in Rasmussen et al. 2014, *Quaternary Science Reviews* 106:14–28, Table 2
(doi:10.1016/j.quascirev.2014.09.007; read at <https://oceanrep.geomar.de/34059/1/Rasmussen.pdf> on 2026-11-23),
from the start of the 11.4 ka event to the start of GS-26: 111 rows. Names, NGRIP depths and ages were taken from
the text of the table by a script; the uncertainty classes of the stadial onsets were read from the table's
superscripts by eye. The Holocene events younger than 11,400 years were not transcribed; the data compared here
begin at 10,300.

| File | SHA-256 |
|---|---|
| `events.tsv` | `7b9c572a5f6ae8e423ca71e443dec7f01bc4370b6fe5cf037dd8485da14ab3a6` |
| `analysis/swell.py` | `b62344764c8b1d155e807c88093229ea738c66cbb3cf052357f83cb0cbb3d0c9` |
| `analysis/test_swell.py` | `41d4ab90e2a22c114673e46d1bd2526cec7298f000abedd1e95d5fb2d9021d8a` |
