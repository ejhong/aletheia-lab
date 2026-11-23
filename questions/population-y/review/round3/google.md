<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T04:17:44.823971+00:00", "input_tokens": 8149, "output_tokens": 37821, "cost_usd_list_price": 0.5918} -->

### (a) Errors of sign, algebra or logic

1. **Quote:** `α_eur = f4(Mbuti, Sardinian; Amazon, Reference) / f4(Mbuti, Sardinian; Amazon, French); α_afr = f4(Chimp, Mbuti; Amazon, Reference) / f4(Chimp, Mbuti; Amazon, Yoruba); ... P_adj is what P would be if the Reference's extra European and African ancestry, relative to the Amazonians, were simple recent mixture.`
   **Correction:** Under the stated three-way mixture model, the numerator of `α_eur` equals `α_eur·f4(Mbuti, Sardinian; Amazon, French) + α_afr·f4(Mbuti, Sardinian; Amazon, Yoruba)`, where the omitted cross-term is large and negative (minus the Out-of-Africa drift), so any African ancestry in the Reference biases `α_eur` sharply downward (even negative) and corrupts `P_adj`. Compute `(α_eur, α_afr)` by solving the 2×2 linear system `M · [α_eur, α_afr]^T = [f4(Mbuti, Sardinian; Amazon, Reference), f4(Chimp, Mbuti; Amazon, Reference)]^T`, where row 1 of `M` is `[f4(Mbuti, Sardinian; Amazon, French), f4(Mbuti, Sardinian; Amazon, Yoruba)]` and row 2 is `[f4(Chimp, Mbuti; Amazon, French), f4(Chimp, Mbuti; Amazon, Yoruba)]`.

### (b) Factual statements confident are wrong

Nothing found.

### (c) Instructions that contradict each other

1. **Quote:** `P_B.unrel is P_B on what remains, if at least two Amazonians and two Pima remain.` (under **Support**) vs. `Every f4 statistic above is compared. ... Agreement is required for P, the support tests, A, T, L, M and C. Kinship is not required.` (under **Replication**)
   **Correction:** `P_B.unrel` is a support f4 statistic whose donor set is determined by KING-robust kinship (and cannot be pre-locked in `sets.tsv` since no Native American genotypes were read before the lock), so it cannot be computed without kinship. Either explicitly exclude `P_B.unrel` from the required replication tests alongside kinship, or require kinship in the replication as well.
