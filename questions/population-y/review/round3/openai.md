<!-- {"vendor": "openai", "model": "gpt-6.2-astra", "utc": "2026-11-23T04:16:47.571561+00:00", "input_tokens": 7575, "output_tokens": 11445, "cost_usd_list_price": 0.5184} -->

### (a) Errors of sign, algebra or logic

- “f4(O, A; R, X) is positive when X shares more alleles with A than R does.”  
  The comparison is **relative to O**: X’s sharing advantage over R is greater for A than for O. Differential sharing with O alone can produce a positive sign.

- “European or African ancestry in the Reference would fake the signal.”  
  Under a null of zero excess, admixture from source \(S\) at fraction \(\alpha\) produces \(P=\alpha f4(\mathrm{Mbuti},\mathrm{Papuan};S,\mathrm{Amazon})\). It fakes a **positive** signal only if that contrast is positive.

- “P_adj is what P would be if the Reference's extra European and African ancestry, relative to the Amazonians, were simple recent mixture.”  
  The subtraction is correct for **known** mixture fractions, but the two ratios do not jointly estimate them: Yoruba ancestry can affect the Sardinian numerator, and French ancestry can affect the Mbuti numerator. The two mixture equations must be solved jointly, assuming zero contrasts for the unadmixed Reference.

- “Distance is the smallest great-circle distance […] from the site to any point of the Natural Earth coastline, where each coastline segment is sampled at evenly spaced points […].”  
  The calculation gives the minimum distance to a **sampled point**, an upper bound on the distance to the coastline. A site within 75 km of a segment can therefore be classified as inland.

- “Agreement means: […] f4 values differing by no more than the larger of 1% of our value and 1e-7 […].”  
  For every negative estimate this gives a tolerance of exactly \(10^{-7}\). The relative-tolerance formula is \(\max(0.01|f4|,10^{-7})\).

- “Specific: Z(L3) ≥ 2 and Z(Han control) < 3 in panel A.”  
  This detects a Papuan excess **beyond Han**, not one exclusive to Australasians. A positive Han result with \(Z=2.9\) passes the rule.

- “It says how many times the present-day Amazonian excess a set would need to carry in order to stand out.”  
  \(Z^*SE(M1)/P_A\) is the threshold for the **observed M1 contrast against the baseline**, in units of \(P_A\), not a minimum true effect or a sufficient condition to stand out. That scale also requires \(P_A>0\).

- “This selects a set that is […] not owed to damage-prone SNPs.”  
  The half-size rule constrains only the transversion **point estimate**. It can pass even when the all-SNP result crosses its detection threshold only because of transitions.

- “Coast: […] otherwise no difference is detected.”  
  A large \(Z(C1)\) can detect a coast–inland difference while \(|Z(CF)|\ge3\) blocks its attribution to a specific Australasian excess. In that case the attribution is undetermined, not the C1 difference.

- “If every ancient American carried the excess equally, nothing would stand out.”  
  Equal ancestry removes the expected contrast **from that ancestry**. Sampling variation alone can still make a set pass the decision rule.

### (b) Factual statements that are wrong

- “No genotype of any Native American was read before the lock.”  
  The blind run had to read the Native American genotypes to shuffle them. Not inspecting unshuffled genotypes is different from not reading them.

- “[…] every genome's SNPs shuffled, which destroys all real signal […].”  
  Independent within-genome shuffling destroys locus alignment but preserves each genome’s genotype distribution. Differences in genome-wide mean allele counts can still contribute to shuffled \(f4\).

- “Which SNPs those are is not in the public files, so this cannot be isolated.”  
  The public Human Origins array-design annotations identify ascertainment panels, including the Karitiana and Papuan panels. Those SNPs can be identified by intersecting the design annotations with the 1240K sites.

- “The session that wrote this protocol had read the papers listed above first […].”  
  The literature list explicitly says Raghavan and Yang were not read and that the Moreno-Mayar article could not be fetched. The session read only a subset of the listed papers.

### (c) Contradictory instructions

- “The labels are `Mbuti`, `Yoruba`, `Han`, `French`, `Sardinian`, `Papuan`, `Australian`, `Nasioi`, `Mixe`, `Pima`, `Mayan`, `Piapoco`, `Quechua`, `Surui`, `Karitiana`.”  
  The A.MesoOther instruction also requires `Mexico_Zapotec`, `Nahua`, `Mixtec_1` and `Mixtec_2`. An exhaustive panel-label list must include those four.

- “Z(P_B.heldout) ≥ 3: also detected in other donors. From 2 to 3: weakly.”  
  Both ranges include 3 as written. The weak category is \(2\le Z<3\).
