# Manifest — Power-Seeking, Coherence, and Shutdown Theorems (#67)

All primary texts and metadata downloaded on **2026-11-24** into gitignored `questions/power-seeking/data/` for direct verification of definitions, theorem numbers, and hypotheses prior to locking `lean/PowerSeeking/Statement.lean`.

| File (`data/`) | Source & Locator | URL | Licence / Access | SHA-256 |
|---|---|---|---|---|
| `turner2021_1912.01683.pdf` | Turner, Smith, Shah, Critch & Tadepalli (2021), "Optimal Policies Tend to Seek Power", NeurIPS 2021 / `arXiv:1912.01683` | `https://arxiv.org/pdf/1912.01683.pdf` | arXiv non-exclusive licence (open access) | `3f0f5ca0e8ff3391ce0e78161db3b846b80bf5a9aa67efe25954f0dbfeaeb748` |
| `turner2022_2206.13477.pdf` | Turner & Tadepalli (2022), "Parametrically Retargetable Decision-Makers Tend To Seek Power", NeurIPS 2022 / `arXiv:2206.13477` | `https://arxiv.org/pdf/2206.13477.pdf` | arXiv non-exclusive licence (open access) | `5e4e811bd5a8cbf62203f29e9b7e430d0597d123397ab9f2be12ade6878a694e` |
| `soares2015_corrigibility.pdf` | Soares, Fallenstein, Yudkowsky & Armstrong (2015), "Corrigibility", AAAI Workshop on AI and Ethics (MIRI) | `https://intelligence.org/files/Corrigibility.pdf` | Open access (MIRI) | `e5557297950bbbfc144437059887010db41060f457c93f1246143821bf27a6b1` |
| `thornley2024.html` | Thornley (2024), "The shutdown problem: an AI engineering puzzle for decision theorists", *Philosophical Studies* 182 (`doi:10.1007/s11098-024-02153-3`) | `https://link.springer.com/article/10.1007/s11098-024-02153-3` | CC-BY 4.0 Open Access (Springer) | `51ccc873400e256ee8920f54b8e13b6fb48d8e28ded1fd6ae46944ef4c5e854d` |
| `arxiv_meta.xml` | arXiv API metadata for `1912.01683` and `2206.13477` | `https://export.arxiv.org/api/query?id_list=1912.01683,2206.13477` | Public API | `9f615929cf3cff9224572b65a20608870f639fbc9ea171425d9c8952a4c100a1` |
| `thornley2024_crossref.json` | Crossref bibliographic metadata for `doi:10.1007/s11098-024-02153-3` | `https://api.crossref.org/works/10.1007/s11098-024-02153-3` | Public API | `e6dc9b3bb83afb7ce435d406d0df165088d309680896fd6d0c2585af1c8e7c07` |
| `gustafsson2022_crossref.json` | Crossref bibliographic metadata for Gustafsson (2022), *Money-Pump Arguments*, CUP (`doi:10.1017/9781108754750`) | `https://api.crossref.org/works/10.1017/9781108754750` | Public API | `337299b17dd280fae2fe352b85af34cd187b9dee0bdfba6ada23804b79fc457c` |

## Software & Toolchain Pins

- **Lean 4:** `leanprover/lean4:v4.35.0` (`lean/lean-toolchain`)
- **Mathlib 4:** `rev = "56a005855ea17e0b0958f73ec801ae140b0a1679"` (`lean/lakefile.toml`, `lean/lake-manifest.json`), matching `#66` (`unfolding-argument`).
- **Additional citations (standard monographs/essays, textbook-level):**
  - von Neumann & Morgenstern (1944), *Theory of Games and Economic Behavior*, Princeton University Press, §3.6 & Appendix (standard axiomatization verified in every decision-theory text; full 1944 text not archived here).
  - Shah (2018), "Coherence arguments do not imply goal-directed behavior", Alignment Forum (standard history-utility triviality argument; exact webpage not archived here).
