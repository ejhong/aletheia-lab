# Data manifest

No datasets. These are the copies of the sources that were read, and the software dependency. Nothing here is
stored in the repo; the hashes identify the exact bytes retrieved. The files are kept on the operator's machine
under `~/research-sources/unfolding-argument/`.

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| Doerig, Schurger, Hess and Herzog, "The unfolding argument: Why IIT and other causal structure theories cannot explain consciousness", *Consciousness and Cognition* 72 (2019) 49–59, doi:10.1016/j.concog.2019.04.002 | https://infoscience.epfl.ch/bitstreams/2a96eaba-fd88-40ba-9f8d-b0c5e723b5a8/download | 2026-11-23 | CC BY 4.0 (per Crossref) | `83224c9b793893f87c7dd94b2e1b156d2ec8b0ac854f57c4d674641996d623d5` | Publisher's PDF, 11 pages, from EPFL's repository (the publisher's site refused automated download). Read: §§1–2.7 and Appendix A. Extracted text: `8f29c94f59ec19a1c320d86b2a5c38965242a5f5acc593a36def96bae64156ca`. |
| Kleiner and Hoel, "Falsification and consciousness", arXiv:2004.03541v3 (28 April 2021) | https://arxiv.org/pdf/2004.03541 | 2026-11-23 | arXiv; licence not checked | `313f2e4a581fa5c4f8bd1b5d2a85b9f3ad6835f0569900e7790ebeae22eea679` | 24-page PDF. Read: §§2–5. Quoted from this copy, with its page numbers. Page 14 (Theorem 4.3) was also read as an image, because text extraction loses the bar on O. Extracted text: `d02f8b9a0125841a2f18521a62dc30873ad1d412e0bdbe8791c4c8a13a983081`. |
| Kleiner and Hoel, "Falsification and consciousness", *Neuroscience of Consciousness* 2021(1), niab001, doi:10.1093/nc/niab001 | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8052953/fullTextXML | 2026-11-23 | CC BY | `f72059a36028fc4d73ea18c5c3f507f70121d758cabc87023e8ba9eff2b580ac` | Journal text as XML from Europe PMC. Used to confirm that section, definition and theorem numbers match the arXiv copy. Formulas are garbled in the XML. |
| Hanson and Walker, "Formalizing falsification for theories of consciousness across computational hierarchies", *Neuroscience of Consciousness* 2021(2), niab014, doi:10.1093/nc/niab014 | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8339439/fullTextXML | 2026-11-23 | CC BY-NC | `828960fd5464d1f08e88d8a9c633ca7f7bd140735c4022ad8ebe708d10ec1b10` | Journal text as XML from Europe PMC; no page numbers. Read: the passages on Krohn–Rhodes, the feed-forward circuit, and the section on falsification. Not read in full. The arXiv copy (v2, `403515932bec193f16508ccf5879614a03ba206e741ab4d63c8549e456d97285`) was also downloaded. |
| Herzog, Schurger and Doerig, "First-person experience cannot rescue causal structure theories from the unfolding argument", *Consciousness and Cognition* 98 (2022) 103261, doi:10.1016/j.concog.2021.103261 | https://infoscience.epfl.ch/bitstreams/3f7a6209-c654-4be3-a49a-fbaed2b0d461/download | 2026-11-23 | CC BY-NC-ND | `2fc8e32ce1ce585f3f95ec7d6dae9cac2895cc85997a18330bce180d69fd2a6d` | Publisher's PDF, 12 pages, from EPFL's repository. Read: §1 (the summary of Usher), §2 opening, DR2 and DR5. Extracted text: `d7edf96a1699bd18efc5c248b6cdf0b402eee9613d15a5d9489a24036bee6285`. |
| O'Reilly-Shah, Selvitella and Schurger, "A caveat regarding the unfolding argument: implications of plasticity", *Neuroscience of Consciousness* 2026(1), niag027, doi:10.1093/nc/niag027 | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13271385/fullTextXML | 2026-11-23 | CC BY-NC | `aa05fcdfc999c9e9ad48dd8df8a3f822167f1c0ef42c44e32864b0ac1721fda5` | Journal text as XML from Europe PMC; no page numbers. Read: abstract, "The plasticity caveat", "Claims", "Direct response", "Proofs", "The Turing Completeness generalization", "Lenient dependency". The supplementary appendix with the formal proofs was not obtained. |
| Usher, "Refuting the unfolding-argument on the irrelevance of causal structure to consciousness", *Consciousness and Cognition* 95 (2021) 103212, doi:10.1016/j.concog.2021.103212 | https://pubmed.ncbi.nlm.nih.gov/34627098 | 2026-11-23 | © Elsevier; abstract only | `0a37a13536d7510c55a3a3ee3b8313b004937900c22c7e9cc8186561616767ca` (the abstract as text) | Abstract only. The article is paywalled and was not read. What it argues is taken from its abstract and from Herzog et al. (2022), pp. 3 and 10–11. |
| Mathlib (Lean 4 library) | https://github.com/leanprover-community/mathlib4 at commit `56a005855ea17e0b0958f73ec801ae140b0a1679` (v4.35.0) | 2026-11-23 | Apache-2.0 | git commit hash, as given | Fetched by Lake, not stored here. Every transitive dependency is pinned in `lean/lake-manifest.json`; the toolchain is Lean v4.35.0. |

## Cited but not read

- Tsuchiya, Andrillon and Haun, "A reply to 'the unfolding argument'", *Consciousness and Cognition* 79 (2020)
  102877, doi:10.1016/j.concog.2020.102877. Paywalled; the preprint (doi:10.31234/osf.io/a2ms9) could not be
  downloaded. What it argues is taken only from Herzog et al. (2022), p. 9, who are its opponents. `unverified`
  against the original.
- Hoel, "A Disproof of Large Language Model Consciousness", arXiv:2512.12802. Downloaded
  (`3f466a17f429ef903209b7d5c4e5743a1079d0acb63a4c3db0ae4d0877ef3784`), not read. Found by the prior-art search.
- Mayeux, "A Machine-Checked Formalization of Integrated Information Theory in Lean4", Zenodo (2026),
  doi:10.5281/zenodo.22659407. Found by the prior-art search; the abstract only was read, by a sub-agent.
- Krohn–Rhodes in Lean 4: https://github.com/adii800/krohn-rhodes-lean. Found by the prior-art search; not read.
