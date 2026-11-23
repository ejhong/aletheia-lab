# Data manifest

Large files live in `data/` (git-ignored). Everything below can be downloaded again and checked.

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| AADR v66.p1, 1240K genotypes (`v66.p1_1240K.aadr.patch.PUB.geno`) | <https://dataverse.harvard.edu/api/access/datafile/13994829> | 2026-11-23 | CC0 1.0 | `ce9e13a990b26e29eadbb5630dfd2f706cff0aea7a5df59c8d7744346d7428b4` | 7,117,276,654 bytes; MD5 matches the release's `files.md5sum` |
| AADR v66.p1, SNP list (`v66.p1_1240K.aadr.patch.PUB.snp`) | <https://dataverse.harvard.edu/api/access/datafile/13994514> | 2026-11-23 | CC0 1.0 | `1189e253b82058822fddabc4966c1448dea70373a96c40106e720bedd93b55bf` | MD5 matches |
| AADR v66.p1, individual list (`v66.p1_1240K.aadr.patch.PUB.ind`) | <https://dataverse.harvard.edu/api/access/datafile/13994513> | 2026-11-23 | CC0 1.0 | `c7500f8d337a42833d034800f989e1c6419855a6427769cc74de9d0a8bf76f98` | MD5 matches |
| AADR v66.p1, annotations (`v66.p1_1240K.aadr.PUB.anno`) | <https://dataverse.harvard.edu/api/access/datafile/13994515> | 2026-11-23 | CC0 1.0 | `4a8e15d0b8d5a8bd6c929ccab7ff83a17091dc91b5e0d8015d9896dd9a5f7f7a` | MD5 matches |
| AADR v66.p1, checksums (`v66.p1__files.md5sum`) | <https://dataverse.harvard.edu/api/access/datafile/13995422> | 2026-11-23 | CC0 1.0 | `e1825584d17612f6b16e12c4e096355f0d9eb12351b6ea5991a32cb8353777c8` | |
| AADR v66.p1, README (`aadr_v66.p1__README.docx`) | <https://dataverse.harvard.edu/api/access/datafile/13994530> | 2026-11-23 | CC0 1.0 | `9fc352fcf69743289261a6e7dd738cf5adefd5749e9d8eb39e0bab94b2a81dae` | Not used by the analysis |
| Natural Earth 1:50m coastline, v5.1.2 (`ne_50m_coastline.geojson`) | <https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_50m_coastline.geojson> | 2026-11-23 | Public domain | `271f1c4c1908312bac6b29d158ea1356544beafc129f260005300913aa5ea283` | |

The AADR dataset is Harvard Dataverse doi:10.7910/DVN/FFIDCW, dataset version 14.0 (released 2026-06-08). Put the
AADR files in `data/aadr_v66.p1/` and the coastline in `data/naturalearth/`.

## Locked inputs made from the data

Committed before the protocol lock. `analysis/sets.tsv` is the list of who is in each set; the others are the
programs that will be run.

| File | SHA-256 |
|---|---|
| `analysis/sets.tsv` | `f68ceb5cfda4cf1e1b45de0d6997f1b1268b269826a30058bae4637aeccca1da` |
| `analysis/build_samples.py` | `e131f1e18c94611a2de6b437c3b06dd3ddee6765431df3fff340786f478bcc77` |
| `analysis/f4lib.py` | `cb9a14aa9b582877a441b87c78d33da609bc9356874de007ef3c328ec7f66255` |
| `analysis/run.py` | `55e0f0f1d9f2999f9c3590f4cb81c0336e7006f80d1ac39276421c72f4dd6cb3` |
| `analysis/check_reader.py` | `3e2ad2556528fa61ea37bdc7ba5d6db0b9cbb96c6638a0ab05defab2c3ed03a4` |
| `analysis/test_f4lib.py` | `0d807eaf27cb3168b3c2b3af17104195015d5b080d9fa6cbb105fdbcdd6b6b16` |
| `analysis/requirements.txt` | `7bd6b8946940b79948c548c8048e545684b91c8edc9444d8dfc0c8f76a97c0a7` |
| `replication/FORMAT.md` | `ed1b8c3dfe2d87c9c5a86ecbde8e39f4f719bf12f8bfffa928cbd077fc162f82` |
