# Data manifest

The same public files as question #31; `data` is a link to that question's git-ignored `data/` folder. No new
download was made.

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| AADR v66.p1, 1240K genotypes (`v66.p1_1240K.aadr.patch.PUB.geno`) | <https://dataverse.harvard.edu/api/access/datafile/13994829> | 2026-11-23 | CC0 1.0 | `ce9e13a990b26e29eadbb5630dfd2f706cff0aea7a5df59c8d7744346d7428b4` | 7,117,276,654 bytes; MD5 matches the release's `files.md5sum` |
| AADR v66.p1, SNP list (`v66.p1_1240K.aadr.patch.PUB.snp`) | <https://dataverse.harvard.edu/api/access/datafile/13994514> | 2026-11-23 | CC0 1.0 | `1189e253b82058822fddabc4966c1448dea70373a96c40106e720bedd93b55bf` | MD5 matches |
| AADR v66.p1, individual list (`v66.p1_1240K.aadr.patch.PUB.ind`) | <https://dataverse.harvard.edu/api/access/datafile/13994513> | 2026-11-23 | CC0 1.0 | `c7500f8d337a42833d034800f989e1c6419855a6427769cc74de9d0a8bf76f98` | MD5 matches |
| AADR v66.p1, annotations (`v66.p1_1240K.aadr.PUB.anno`) | <https://dataverse.harvard.edu/api/access/datafile/13994515> | 2026-11-23 | CC0 1.0 | `4a8e15d0b8d5a8bd6c929ccab7ff83a17091dc91b5e0d8015d9896dd9a5f7f7a` | MD5 matches |
| AADR v66.p1, checksums (`v66.p1__files.md5sum`) | <https://dataverse.harvard.edu/api/access/datafile/13995422> | 2026-11-23 | CC0 1.0 | `e1825584d17612f6b16e12c4e096355f0d9eb12351b6ea5991a32cb8353777c8` | |

The AADR dataset is Harvard Dataverse doi:10.7910/DVN/FFIDCW, dataset version 14.0 (released 2026-06-08).

## Locked inputs made from the data

Committed before the protocol lock. `analysis/people.tsv` lists every tested person with their side, data type,
site and neighbours; `analysis/refs.tsv` lists the reference sets. The others are the programs.

| File | SHA-256 |
|---|---|
| `analysis/people.tsv` | `ba555ac101f78a6567c90543845db6463fcfdac658d1aa60e9969fe01f33e0a9` |
| `analysis/refs.tsv` | `380427fbfc7644360916d721f3bc9cc0d72b8f4ad8f83ac3ec82901645003e8b` |
| `analysis/build_people.py` | `75df4e3b0300301b25ce5ff063a5a424c843fbb8ccc28631c5c23410dca36e1d` |
| `analysis/scan.py` | `6b49997987a0b38b0f4b872b76dc5ce031818c61093001f8d627eed7d0a4b2b9` |
| `analysis/f4lib.py` | `cb9a14aa9b582877a441b87c78d33da609bc9356874de007ef3c328ec7f66255` |
| `analysis/test_scan.py` | `7d30f31317cb7ea05980ea906c24895d47ca24198db2f9f82c68ab8567cc8265` |

After the lock, one line of `analysis/scan.py` was changed (see `amendments.md`, Amendment 2), so its hash no
longer matches the one above. The locked version is commit `7e3b0d7`.

## Added for Amendment 3

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| Mapped reads of PIE069 (`PIE069.A0101.TF1.1_trim2.bam`), ENA study PRJEB62503, run ERR11495483 | <https://ftp.sra.ebi.ac.uk/vol1/run/ERR114/ERR11495483/PIE069.A0101.TF1.1_trim2.bam> | 2026-11-23 | ENA: open access, cite the study (Penske et al. 2023, doi:10.1038/s41586-023-06334-8) | `e56774d45f646b6d71228660f6b2ddd90c2da2668126d128169c914f2c2895eb` | 72,916,233 bytes; MD5 matches ENA's record. In `data/ena_PRJEB62503/`. |
