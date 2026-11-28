# Data manifest

Nothing in this table is kept in the repository except where a note says so. The preprint's files and the corpus
file go in `data/` (ignored by git) and are read as data; none of the preprint's programs is run.

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| Preprint, methodology paper (`Indus_Methodology_v0.7.pdf`) | <https://doi.org/10.5281/zenodo.24383779> | 2026-11-27 | CC BY 4.0 | `3d297d5fef98a3ae9690248669c45bda5dc0a1f5b47bcd473a5425db270f49ad` | Siva Raj with Claude, *Indus Script Read as Early Dravidian, with AI Assistance*, v0.7, 19 Nov 2026. 75 pages. Section 6 is the language contest. |
| Preprint, test archive (`tests_archive.zip`) | as above | 2026-11-27 | CC BY 4.0 | `910f724940e2cdcf6f907185054063964d038456a9a80a4a90dea48a578d6d7f` | One folder a test. Used: `REP-1_tamil_vs_sanskrit` and `REP-3_akkadian` (plans, programs read but not run, word and name lists, per-split outputs). |
| Preprint, README (`README.md`) | as above | 2026-11-27 | CC BY 4.0 | `b8051d9084c11d155edc7992d82410d9dcaba9cacffd94c792f4c98d8b389a58` | |
| Preprint, reading rules (`Indus_Reading_Rules_v0.7.pdf`) | as above | 2026-11-27 | CC BY 4.0 | `4f6b131dfd4f2a6b61bac6b87ac805bbe8343ae8363a3d830281bc5102023e23` | Read for context. |
| Preprint, sign readings (`Indus_Sign_Readings_v0.7.csv`) | as above | 2026-11-27 | CC BY 4.0 | `4ec2c5adc642124c7c8cc63476d8ee3bd9be00d89c16b34d708e5ebd188b05e1` | Not used in the test. |
| Preprint, test register (`test_register_v0.7.json`) | as above | 2026-11-27 | CC BY 4.0 | `0435cfdedb042148522e3ba21cc606c055bf6ee176532ae08a2904db74f9e913` | Not used in the test. |
| Seal texts (`inscriptions.csv`) | <https://raw.githubusercontent.com/yajnadevam/lipi/fc8813a52e183d19c441631dc26c33a4dccbea39/src/assets/data/inscriptions.csv> | 2026-11-27 | None stated in the repository. Not redistributed here. | `b8dcb325a2e2cd3cde12ac12e7a418b0348e45713c9ee28aad81b645d2ac5ee4` | 5,679 rows. The checksum equals the one the preprint's manifests give for its corpus file. The preprint describes the corpus as ICIT (Wells and Fuls); we have not traced the file's origin further. `unverified` |
| The 69 signs' English picture words (`inputs/sign_english_words.json`) | inside `tests_archive.zip`, `REP-1_tamil_vs_sanskrit/inputs/` | 2026-11-27 | CC BY 4.0 (Siva Raj with Claude) | `ffe5c6431b50b887e42f01477a73dbfa6b328372183032442588f83805953c5e` | Kept in the repository, unchanged. |

The Zenodo record gives an MD5 for each file; every downloaded file matched.

Made by this study after the lock: `lists/<language>/` (what each list-building session wrote) and
`inputs/<language>/` (the same, respelled and joined by `analysis/build_inputs.py`).

Software: Python 3.12.16, standard library only.
