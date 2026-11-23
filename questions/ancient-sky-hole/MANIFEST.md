# Data Manifest — The hole in the ancient sky (`ancient-sky-hole`)

Large raw astronomical catalogs live in git-ignored `data/`. Every file is directly downloadable from official public astronomical archives (CDS/VizieR via the Harvard-Smithsonian CfA mirror) and verified by SHA-256 below.

## Primary Astronomical Catalogs (`data/`)

| File | Primary Source | Exact Download URL | Retrieved (UTC) | Licence / Terms | Rows | SHA-256 |
|---|---|---|---|---|---|---|
| `data/ptolemy_verbunt2012.tsv` | Verbunt & van Gent (2012), *The star catalogues of Ptolemaios and Ulugh Beg*, A&A 544, A31 (`VizieR J/A+A/544/A31/ptolema`) | `https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=J/A+A/544/A31/ptolema&-out=P,C,cst,N,f_N,Elon,Elat,VP,q_VP,HIP,I,T,Vmag,Dl,Db,dist,Flag&-out.max=unlimited` | 2026-11-23 | CDS/VizieR Open Data (`https://cds.unistra.fr/vizier-org/licences_vizier.html`; CC-BY 4.0 for A&A tables) | 1,028 stars | `f5bbf948a517601c2e2a3c88800a490bbdc4621acb3ee7f9328aa058c1b085be` |
| `data/hipparcos_v70.tsv` | ESA (1997), *The Hipparcos and Tycho Catalogues*, ESA SP-1200 (`VizieR I/239/hip_main`, filtered `Vmag <= 7.0`) | `https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=I/239/hip_main&Vmag=<=7.0&-out=HIP,HD,RAICRS,DEICRS,Vmag,pmRA,pmDE,B-V,SpType&-out.max=unlimited` | 2026-11-23 | ESA Public Domain / CDS VizieR Open Data | 15,544 stars | `77b8a65cf6077f012863b1466a45000fa833fa138ae58099f38619b98c3a493e` |
| `data/bsc5.tsv` | Hoffleit & Warren (1991), *Bright Star Catalogue, 5th Revised Ed.* (`VizieR V/50/catalog`) | `https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=V/50/catalog&-out=HR,Name,HD,RAJ2000,DEJ2000,Vmag,B-V,pmRA,pmDE&-out.max=unlimited` | 2026-11-23 | Public Astronomical Catalogue / CDS VizieR Open Data | 9,110 stars | `8bf0e8052e6c930f2447c35b420f14813082ec495e97c68b937634fa299ebae5` |

## Re-download Commands

```bash
mkdir -p questions/ancient-sky-hole/data
curl -sS "https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=J/A+A/544/A31/ptolema&-out=P,C,cst,N,f_N,Elon,Elat,VP,q_VP,HIP,I,T,Vmag,Dl,Db,dist,Flag&-out.max=unlimited" -o questions/ancient-sky-hole/data/ptolemy_verbunt2012.tsv
curl -sS "https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=I/239/hip_main&Vmag=<=7.0&-out=HIP,HD,RAICRS,DEICRS,Vmag,pmRA,pmDE,B-V,SpType&-out.max=unlimited" -o questions/ancient-sky-hole/data/hipparcos_v70.tsv
curl -sS "https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=V/50/catalog&-out=HR,Name,HD,RAJ2000,DEJ2000,Vmag,B-V,pmRA,pmDE&-out.max=unlimited" -o questions/ancient-sky-hole/data/bsc5.tsv
```

## Notes on Precession Reference

Long-term precession equations are implemented directly in `analysis/skyhole.py` from Vondrák, Capitaine & Wallace (2011), *A&A* 534, A22 and Corrigendum (2012), *A&A* 541, C1 (IAU SOFA / ERFA `eraLtpequ` and `eraLtpecl` coefficients, BSD-licensed via `liberfa/erfa`), valid over `±200,000 years` around J2000.0 to arcsecond precision.

## Code Checksums (Locked Analysis Pipeline)

| File | SHA-256 |
|---|---|
| `analysis/skyhole.py` | `3e805737471c7bf6c6ec242c59a976b062a5bceaded23b0e74a478ad52482178` |
| `analysis/test_skyhole.py` | `09b3fe0d8acc765714e10b75a8f93feb94624e55a9977a03dadd7ab0faf099e8` |
| `explore/structure.py` | `852bb937471c7639f9213348120dd1be3e936778a0a8613e2023bf6b6bf7f512` |

