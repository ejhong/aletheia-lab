# Stimuli

Pictures for the shape-ranking experiment. Regenerate everything with
`python stimuli/make_stimuli.py --src ~/research-sources/gobekli-star-map/images` (numpy 2.3.5, Pillow 11.0.0);
the output is byte-identical on every run (checked 2026-11-23).

## Provenance and licence

Source: Sweatman, M. B. & Tsikritsis, D. (2017). Decoding Göbekli Tepe with archaeoastronomy: what does the fox
say? *Mediterranean Archaeology and Archaeometry* 17(1), 233-250, Table 1 (PDF pages 14-15, printed 246-247).
Licence: CC BY 4.0. The pictures are the rasters embedded in the published PDF, extracted losslessly with
`pdfimages -png` (see `~/research-sources/gobekli-star-map/images/INDEX.md`). Black frames and white rectangles
(in S01, S05, S06 and A01) are part of the published images.

Attribution line: *Pictures from Sweatman & Tsikritsis 2017, MAA 17(1):233-250, Table 1, CC BY 4.0; renamed,
and for `figures/` and `symbols_512/` processed as described below.*

## Folders and processing

- `symbols/S01..S12.png`: byte-identical copies of the 12 symbol photographs, renamed.
- `asterisms_original/A01..A08.png`: byte-identical copies of the 8 asterism pictures, renamed.
- `figures/A01..A08.png`: line-only versions of the asterisms (8-bit greyscale, values 0 and 255 only):
  1. A pixel is "red line" if **R >= 110 and R − G >= 60 and R − B >= 50** (on 0-255 RGB). This keeps the
     red lines including their anti-aliased edges in the JPEG-like pictures (A01, A05, A06) and excludes the
     dark or brownish sky, the thin faint-blue lines (B > R) and the white rectangle in A01 (R = G = B).
     A02, A03, A04, A07, A08 have flat red lines; for them every threshold from the strict
     R>150, G<100, B<100 up to this one selects the same pixels.
  2. Red pixels become black (0), all others white (255); crop to the bounding box of the red pixels.
  3. Centre on a white square canvas whose side is max(width, height) / 0.8 (10% margin each side).
  4. Resize to 512x512 with Lanczos, then threshold at 128 (below = black), so lines stay crisp and binary.
  Line width is not normalised: small source pictures (e.g. A03, 118x100) come out with thicker lines.
- `symbols_512/S01..S12.png`: RGB, resized with Lanczos so the longer side is 512 (aspect kept), centred on a
  white 512x512 canvas. No other processing.
- `dummy/`: made-up pictures for plumbing tests only (never study data). D01-D12 filled black shapes on
  white (circle, square, triangle, star, cross, crescent, arrow, ring, L-shape, zigzag, ellipse, diamond);
  L01-L03 black 8-px polylines on white (triangle outline, zigzag, circle outline).

## Neutral names and the paper's captions

| Neutral name | Source file | Caption in Table 1 |
|---|---|---|
| S01 | `symbols/S01_scorpion.png` | Scorpion |
| S02 | `symbols/S02_bending_bird.png` | Bending bird |
| S03 | `symbols/S03_duck_goose.png` | Duck/goose |
| S04 | `symbols/S04_dog_wolf.png` | Dog/wolf? |
| S05 | `symbols/S05_eagle_vulture.png` | Eagle/vulture |
| S06 | `symbols/S06_bending_bird_fish.png` | Bending bird with fish |
| S07 | `symbols/S07_frog.png` | Down-crawling frog (stored at only 64x82 px) |
| S08 | `symbols/S08_ibex_rat.png` | Charging ibex /crouching rat |
| S09 | `symbols/S09_aurochs.png` | Aurochs |
| S10 | `symbols/S10_wild_boar.png` | Wild boar |
| S11 | `symbols/S11_lion_leopard.png` | Pouncing Lion or leopard |
| S12 | `symbols/S12_fox.png` | Fox |
| A01 | `asterisms/A01_scorpio.png` | Scorpio (row 1) |
| A02 | `asterisms/A02_pisces.png` | Pisces (row 2) |
| A03 | `asterisms/A03_libra.png` | Libra (row 3) |
| A04 | `asterisms/A04_lupus.png` | Lupus (row 4) |
| A05 | `asterisms/A05_sagittarius.png` | Sagittarius (row 5) |
| A06 | `asterisms/A06_ophiuchus.png` | Ophiuchus (row 6) |
| A07 | `asterisms/A07_virgo.png` | Virgo (row 7) |
| A08 | `asterisms/A08_gemini.png` | Gemini (row 8) |

The paper pairs A0n with S0n (rows 1-8); S09-S12 have no asterism in the table.

## SHA-256

```
584765e34cd4061dc53d29d63593e5fd09520bf9b0dff851d2584e5b7bde77fc  symbols/S01.png
1744bb2ae846d5f5e04124ec62be8bd107127e773ed3c6316fa7f577039f41fd  symbols/S02.png
2703ca4724043c61417ab1a8b1b8d65029f73c414a657fbe6ee6851d4e632bc8  symbols/S03.png
4eb715ed763db49d0fa15a651785cffaadf6bb2687ebeb0585ef8a66caaf3468  symbols/S04.png
edc66108c9e253951bd7f3d155bac39b67f788f27656e45a7a4ce5103eee0434  symbols/S05.png
813f5589a58cd073c253044b5cdef56a8ee8c666d8007ea58f3323b182055723  symbols/S06.png
6cb332b0d3dae7311aeecaae31e963c4f82f6d5dd474dc80b7e8f7c451d15add  symbols/S07.png
90b06a197a7fd0b088ec41fc0951574772fe5e767fbf77321eb5da369b37cd74  symbols/S08.png
527ded8762a6c99a357d925ae7ff3d748523ad1b731a76c2cfe2ce0fe076c978  symbols/S09.png
5e688345ad97b5e01bc7712376b3b1d5ce336567143155460b98792a3055eaec  symbols/S10.png
221f274ff866de8f9eda153bb47e6462cbb11ac4121b6bfce57a0cc717305529  symbols/S11.png
22699f58dcfc0be9983b3ef0e446e415205bc067a62b6427a41ec426ccb3117a  symbols/S12.png
ee98506eb38fb46c1891657ffaa47cb2ffa455e91993c90f4881fb155bf3c15f  asterisms_original/A01.png
9044610effbf6e869834aac8335a327d7c46674b9efff899981741a5cc28db16  asterisms_original/A02.png
7985d6f128f2243edcce132afd3f4762a3bb6285258ac6f295feb8038f612c5a  asterisms_original/A03.png
99f9ba5faea0355089eb1c90e87741bcba34a9826a7553c462adb5341c822de8  asterisms_original/A04.png
84d7287dc5c300163927399502ed34c23b081faae67ddd50a4909edce53ba2e3  asterisms_original/A05.png
cd38c1837637bebadd6707767d304dad26b3e73a0c926e1da826eb86c34151d0  asterisms_original/A06.png
38de6fd979ebab994551fc4351b90bd06db311da3a883635a996b1b7ae5c2439  asterisms_original/A07.png
1c8971c06e6a1223c1f3f030fc3efb10cebad3626d2d061cab05f9f4c4b008a8  asterisms_original/A08.png
52c4ad45f8725013d9bf069fb798fecfc151056f70319480114b8154e3003d11  figures/A01.png
eaf3bfd89c5b669551117d4cfc941f6faa01e89794a9702d2d86f0d4650f9474  figures/A02.png
98187b597b4566db491964cfa8c76ca837c30213d076a1848bb30348348da642  figures/A03.png
595089423372bcb9c3087f083d457c3bd34f16b72651d61ea0522cc830e79d49  figures/A04.png
4027dce517e88e46b0bd8dcb9e07c610b19ab2c37a9872db90012a43041c8ef9  figures/A05.png
01c24be4387814e4055ef02ac3a5305d25fb07fc7e82e46586a3157f2190ffb8  figures/A06.png
4d7079b04bcad4cc74e9ff3ff823f707447e843ecfcc68434769dc2580877f80  figures/A07.png
7f47a8548a9eecd336c7922aac9e1dc5959e69aa38f2cfe0aab46270bdeb71a0  figures/A08.png
01ae020fdd7589026c14aa8619c69e462457bdd5d733ab6c923fc69e5c70da80  symbols_512/S01.png
9c3ad288316a21aa7e8f2a7cfa167a528da0b326562b317c2d71b2b373e2c07b  symbols_512/S02.png
0b1080ff7af1d8ca79ce976033aefb439d169b8ac62403599c1fb96e80bcccd6  symbols_512/S03.png
64c7bc5c2376a68f05efd920ae892dd7bb56c6d9d5343039f45a826d990bc06a  symbols_512/S04.png
86b909ac6f817b5d7aaa2e12356b75ffe143c1acb06c1aeec7ebf29f016f1ea5  symbols_512/S05.png
8c31725a8ed8ec56e9a1718fb2d58a9241ee02bbfaaff5d34ff729c1fc5fc510  symbols_512/S06.png
c9c18e0e1b8606e4814285f9809c78e93fe28b982aa385d89675abb531e28d46  symbols_512/S07.png
c660e15294e70c96c04a8696cb250d6108ff1d06a0e8a716d929a11a0cefecb3  symbols_512/S08.png
e8bcd5e4efed9e086a759da44ac2feb419886e30be004d2193001df91b2b78b8  symbols_512/S09.png
6d3c6c4d3936f3422ff5edb0e201106f63386ba0aea846cce8dd0a26b90b2247  symbols_512/S10.png
bb2a25d74acaa5a579121bf1a7bd305d025479ae5fd2caf31bc062eebcf13fa6  symbols_512/S11.png
d5ad8bf666f26b6a72b2add3651d5035f9f236643d963912c981078b7fcbd6b7  symbols_512/S12.png
eca9d7048ca8f016791290f167fc4cc1dad6044787fc017a324d19d333943588  dummy/D01.png
d006b89944a20c5ddd00889244c6c079cc1e0b419e726aa3ae24f5cc6acdc0c7  dummy/D02.png
8089984a0c89a52ce698cccfa4222775e76ab5a55dede92cf8f70bbbfeea9228  dummy/D03.png
cc6cb13475b3d3d73b7b53d4346aa791db37dd1989cc461ce579a31c4130b1fd  dummy/D04.png
21a252029235d99fbceebf481ad2cdb317aa8388149971c9a17d31175966b6ea  dummy/D05.png
a41682145ffcae1102578dd885cc0a928e7bac4f9fade82fec82f5801cf796c9  dummy/D06.png
cbd6823c5f86623cedf9ca75dda1c0b14619d831530b86b9e5c5de11b0c85907  dummy/D07.png
53d5848b49299068ee54d56d553da1cc66dacc76cddf97def2432720e3007c9c  dummy/D08.png
3490dc3c03e79f053185f15413673c9276bf00ea47be215010ddebe267aa2034  dummy/D09.png
0e720d78509c308206047b12c44afad98b9333e68ee9966798f7dff5084dd2f9  dummy/D10.png
09e19ed9bebef80b4bac959ea450cfae059c8d2882c8f98a031d5de2e74d1273  dummy/D11.png
1f6d6cc85fb64117451f17cd04149249fd49748f62aa238f5a804f31dc8fe55c  dummy/D12.png
6c609c70507488605766cc261f02590237fc7ccd8137483ae1e650d1f8277343  dummy/L01.png
a208e951dc826cb4857ea170ccfcd31781fa2eef2ab2c6b8747689e50eb078be  dummy/L02.png
8f9be05255bfe2e6c3adbb5877eebacbebe57a9c49048bdb8dce2206dc4dce71  dummy/L03.png
```
