# Data manifest

No datasets. The sources are papers; the stimuli are pictures taken from one of them. The PDFs are kept on the
operator's machine under `~/research-sources/gobekli-star-map/`, not in this repository.

| Name | URL | Retrieved (UTC) | Licence | SHA-256 | Notes |
|---|---|---|---|---|---|
| Sweatman and Tsikritsis, "Decoding Göbekli Tepe with archaeoastronomy: What does the fox say?", *Mediterranean Archaeology and Archaeometry* 17(1) (2017) 233–250, doi:10.5281/zenodo.400780 | https://zenodo.org/record/400780/files/16_Sweatman%20and%20Tsikritsis%2017%281%29.pdf | 2026-11-23 | CC BY 4.0 per the Zenodo record; the PDF itself says "Open Access … All rights reserved" | `b5a1b30a35829581af65bf19d608722a8714f5282be212777d47302e53bcba11` | 18-page PDF. Read by a sub-agent in full; by the main session: p. 239 and the Appendix (pp. 245–247). Table 1's pictures are separate images inside the PDF. |
| Notroff et al., "More than a vulture: A response to Sweatman and Tsikritsis"; Sweatman and Tsikritsis, reply; Burley, comment. *Mediterranean Archaeology and Archaeometry* 17(2) (2017) 57–74, doi:10.5281/zenodo.581724 | https://zenodo.org/records/581724/files/6_7_8_Matters%20Arising.pdf | 2026-11-23 | CC BY 4.0 per the Zenodo record | `dd528ab1ec129c111a2fa832e688d26b0fdc6ed17447f76c869630c463c7ebf1` | One PDF, three pieces. Read by a sub-agent in full; quotations used here were checked against the text by the main session. |
| Sweatman, "Representations of calendars and time at Göbekli Tepe and Karahan Tepe support an astronomical interpretation of their symbolism", *Time and Mind* 17(3–4) (2024), accepted manuscript | https://www.pure.ed.ac.uk/ws/files/450807570/Another_update_to_my_Lunisolar_calendar_paper.pdf | 2026-11-23 | The version of record is CC BY per OpenAlex; this file is the author's accepted manuscript | `33c3733ca98b6825cf057ac28d55121327ada2d8ace109d6971ed70257e89aba` | Read in part. The publisher's PDF was blocked; quotations are `unverified` against the version of record. |
| Sweatman and Coombs, "Decoding European Palaeolithic art", arXiv:1806.00046v1 (2018) | https://arxiv.org/pdf/1806.00046v1 | 2026-11-23 | not stated in the file | `a8a0f168022259be9320b26cd1d4bf585d4e56c4269b31dc7902e8be77c87bcf` | Read in part by a sub-agent (its revised probability argument). Not used for any number here. |

The stimuli in `stimuli/` are the 20 pictures of Table 1 of the first paper, extracted from the PDF with
`pdfimages` and processed by `stimuli/make_stimuli.py`; hashes are in `stimuli/README.md`. Attribution: Sweatman
and Tsikritsis (2017), *Mediterranean Archaeology and Archaeometry* 17(1), Table 1, CC BY 4.0.

Not obtained: Sweatman, *Prehistory Decoded* (2019); the version of record of the 2024 paper; Schmidt's
descriptions of the pillar in *Neo-Lithics* (2003, 2006).

Software: Python 3.12.16, numpy 2.3.5, Pillow 11.0.0 (the repository's `.venv`).
