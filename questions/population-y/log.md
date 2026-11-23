# Log

Dated entries, newest last: what was tried, what happened, what next.

## 2026-11-22: activation and setup (Claude Opus 5.5)

- Eugene made #31 active and asked for the whole question to run in the brainstorm session that proposed it.
  AGENTS.md §2 asks for a fresh session; this is a departure at Eugene's direction, recorded here and in `RESULTS.md`.
- **Priors brought in from that session, disclosed.** Before the protocol existed, the session had read search-result
  summaries of Castro e Silva et al. 2021 (PNAS 118:e2025739118: Australasian signal also in a Pacific-coast
  population; proposed coastal route). It knew from memory of Skoglund et al. 2015 (Nature 525:104) and of
  suggested alternatives, such as Tianyuan-related ancestry in Northeast Asia (Yang et al. 2017; unverified at
  this point). No statistic was computed and no genotype data was opened.
- Data: AADR v66.p1 (Harvard Dataverse doi:10.7910/DVN/FFIDCW, dataset version 14.0, released 2026-06-08,
  CC0 1.0). Downloading the 1240K and HO public sets into `data/` (git-ignored). Only metadata (`.ind`,
  `.anno`) will be read before the lock, to see which samples exist. No genotype will be read before the lock.
- Tools: R via Homebrew; ADMIXTOOLS 2 to be pinned to a commit. Keys present for OpenAI, Google and xAI. No
  other vendor's coding CLI is installed, so the second-vendor replication will be scripted through their APIs.

## 2026-11-22 to 23: survey, design, three rounds of outside review (Claude Fable 5.2)

- Eugene switched the session to Claude Fable 5.2 and said to run everything here.
- **Literature read before designing** (and so part of this session's priors): Skoglund 2015 (PDF from the Reich
  lab site; Table 1 and main text), Posth 2018 (PDF from the Reich lab site; the Population Y passages),
  Castro e Silva 2021 (main text, through a fetch agent), the Campelo dos Santos 2022 preprint (first half, through
  a fetch agent), and the 2026 *Nature* article's page (the Ypykuéra passages, methods and data statement). Not
  read: Raghavan 2015, Yang 2017, Moreno-Mayar 2018 (fetch refused).
- **Metadata read before the lock:** the AADR `.anno`, `.ind` and `.snp` files, to see who and what is in the
  release and to build `analysis/sets.tsv`. Findings that shaped the design: the Human Origins set adds almost no
  Native Americans, so only the 1240K set is used; present-day genomes come from two pipelines with 11 Native
  Americans in both; the Onge and Jarawa genomes are a third pipeline; the coastal and central-Brazilian groups
  behind the published claims are not in the public release.
- **Download:** the 7.1 GB genotype file came down in 24 ranged chunks because single connections were slow.
  MD5 matches the release's checksum file.
- **Tools:** Python 3.12 with numpy 2.3.5 in `.venv`. The statistics are implemented here (`analysis/f4lib.py`),
  not taken from ADMIXTOOLS, because the release is in TGENO format and so that a second vendor can replicate from
  the protocol. Homebrew could not install R (a lock held by another install), so the ADMIXTOOLS 2 courtesy check
  has not been done.
- **Reader checks** (`analysis/check_reader.py`, no American sample): header, heterozygosity by data type, sex
  chromosomes, four well-known variants (SLC24A5, EDAR, Duffy, SLC45A2) landing on the right SNP with the right
  allele, and two f4 statistics with a known answer. All pass. Two of my first assertions were wrong and were
  changed: women do have some Y-chromosome calls in diploid data, and the first two X SNPs are pseudo-autosomal.
- **Outside review before the lock:** three rounds with OpenAI `gpt-6.2-astra` and Google `gemini-4-neon`; see
  `review/README.md`. Round 1 caught a sign error and a false-positive path in the ancient design. Round 2 caught
  the Caribbean in the baseline, an ancient-versus-modern decision rule, selection in the admixture screen and a
  biased admixture ratio. Round 3 caught that the two admixture fractions must be solved jointly. The protocol was
  rewritten twice. Cost $3.34 at list price, plus one timed-out call.
- **Blind run:** `analysis/run.py --blind` runs the whole pipeline with every genome's SNPs shuffled
  independently, writing to `results_blind/` (git-ignored). Used to find bugs without seeing a result.
- **What the blind run showed (2026-11-23).** The pipeline ran end to end in 80 seconds and wrote 1,553
  statistics. On shuffled genomes the primary statistic was noise (Z = −0.34), but the ancient comparisons reached
  Z = 15. Cause: the first allele in the `.snp` file is the reference allele, and data sources differ in their
  overall share of it (for example French: 70.4% in the SGDP pipeline, 68.2% in the NYGC one), which adds
  mean(p1 − p2)·mean(p3 − p4) to f4. A centred f4 was added to the protocol and code. On shuffled genomes its Z
  has mean 0.03 and standard deviation 1.02 across the 410 ancient-design statistics. This was learned from
  shuffled data and from non-American samples; no real statistic on a Native American genome was computed.
- **Lock.** Protocol locked after this entry; `MANIFEST.md` holds the hashes of `analysis/sets.tsv` and the code.

## 2026-11-23: locked run, amendments, replication (Claude Fable 5.2)

- **Locked run** (`results/`): primary test detected (Z = 4.23); four of five checks pass; the admixture check
  fails. The ancient part showed `REGION.NAM_EAST` with impossible values (M1 +7.6, M3 −12.0, MF −10.7).
- **Cause 1:** `REGION.NAM_EAST` was 18 ancient people from Guam and the Northern Marianas, and `REGION.NORTH`
  held 12 Greenland Norse. Amendment 1 written and pushed, then `analysis/build_samples_amended.py` and
  `analysis/amend.py` written and run (`results/amended/`). All 760 present-day statistics are identical between
  the two runs.
- **Cause 2:** the admixture check's second equation is degenerate. `explore/admixture_terms.py` (exploratory)
  shows why. Amendment 2 written and pushed before the amended check ran. The amended check is well defined but
  too imprecise to pass.
- **Replication:** OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` each wrote a program from the protocol,
  amendments and format note alone. Both agree with ours on every set and every required statistic, in both runs.
  My first comparison script matched the primary statistic to the replicator's 10 cM row by mistake and reported
  one disagreement; the two rows have the same estimate and differ only in block size. Fixed in
  `replication/compare.py`.
- **Not done:** the ADMIXTOOLS 2 courtesy check (R would not install). Filing with Aletheia is Eugene's call.
- **Spent:** $5.72 of $40.
