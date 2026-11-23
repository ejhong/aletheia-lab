# Data Manifest — Does the Taurid comet stream hide a swarm of large fragments? (`taurid-swarm`)

Large raw NASA/JPL JSON catalogs live in git-ignored `data/`. Every file is downloaded directly from official public NASA Jet Propulsion Laboratory (JPL) Solar System Dynamics APIs and verified by SHA-256 below.

## Primary NASA/JPL Archives (`data/`)

| File | Primary Source | Exact Download URL | Retrieved (UTC) | Licence / Terms | Rows | SHA-256 |
|---|---|---|---|---|---|---|
| `data/jpl_neos.json` | NASA/JPL Small-Body Database (SBDB) Query API v1.0, all Near-Earth Objects (`sb-group=neo`) | `https://ssd-api.jpl.nasa.gov/sbdb_query.api?fields=spkid,pdes,full_name,a,e,i,om,w,ma,q,ad,per_y,epoch_mjd,H,diameter,albedo,class,pha,moid&sb-group=neo` | 2026-11-23 | NASA Public Domain (US Government Work) | 43,374 NEOs | `1fdac6b030514b158f63342e081d8fbc8022b1e5bc34ad24c30df1f094ef9e6e` |
| `data/jpl_encke.json` | NASA/JPL SBDB Query API v1.0, Comet `2P/Encke` reference orbit | `https://ssd-api.jpl.nasa.gov/sbdb_query.api?fields=spkid,pdes,full_name,a,e,i,om,w,ma,q,ad,per_y,epoch_mjd,H,diameter,albedo,class&sb-cdata=%7B%22AND%22%3A%5B%22pdes%7CEQ%7C2P%22%5D%7D` | 2026-11-23 | NASA Public Domain (US Government Work) | 1 comet | `021af5a6321f08bfc24d80e71c3a4bd1654b6a44870d37c46021b4611ced20d7` |
| `data/cneos_fireballs.json` | NASA/JPL CNEOS Fireball and Bolide Data API v1.2 (US Government satellite sensors, 1988-04-15 to 2026-10-04) | `https://ssd-api.jpl.nasa.gov/fireball.api?req-alt=false&req-loc=false` | 2026-11-23 | NASA Public Domain (US Government Work) | 1,074 bolides | `6bfc721f21c85e2f4ac09afa9902d8eb623ce2fa7df1173ef3c3a3545a541c5a` |

## Re-download Commands

```bash
mkdir -p questions/taurid-swarm/data
curl -sS "https://ssd-api.jpl.nasa.gov/sbdb_query.api?fields=spkid,pdes,full_name,a,e,i,om,w,ma,q,ad,per_y,epoch_mjd,H,diameter,albedo,class,pha,moid&sb-group=neo" -o questions/taurid-swarm/data/jpl_neos.json
curl -sS "https://ssd-api.jpl.nasa.gov/sbdb_query.api?fields=spkid,pdes,full_name,a,e,i,om,w,ma,q,ad,per_y,epoch_mjd,H,diameter,albedo,class&sb-cdata=%7B%22AND%22%3A%5B%22pdes%7CEQ%7C2P%22%5D%7D" -o questions/taurid-swarm/data/jpl_encke.json
curl -sS "https://ssd-api.jpl.nasa.gov/fireball.api?req-alt=false&req-loc=false" -o questions/taurid-swarm/data/cneos_fireballs.json
```

*Note:* Because JPL SBDB and CNEOS are live databases updated daily as new NEOs and bolides are detected, re-downloads at later dates will contain additional newly discovered objects beyond the 2026-11-23 snapshot.

## Code Checksums (Locked Analysis Pipeline)

| File | SHA-256 |
|---|---|
| `analysis/taurid.py` | `c9cc12d386ec48c2776524440a527e959985ff7b4146bf128a170e5daf10e045` |
| `analysis/test_taurid.py` | `8272e43961706e0655923ec2f5ef5b0beb9b1d9b29debedbad2be20f9e41673c` |
| `explore/structure.py` | `c680a33ac9facbc3f68d335671ff94a3b257497ccfc0ddc5db8e9b756a051b7d` |

