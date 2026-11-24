# Amendments — Unmapped stone structures in public Ice Age seafloor sonar (#84)

## Record added after the spot check — 2026-11-24

Nothing in the analysis or in `results/` was changed or rerun for this record. One thing in the program was
changed: the `User-Agent` it sends to NOAA no longer names the project.

Departures from the locked plan that the first report did not record:

1. **Visual audit.** The plan (§3) says to render and inspect the positive controls and the top 8 unmasked
   candidates. The first report claims all 39 unmasked ridges were inspected. The program renders one preview for
   each of eight tiles. No per-ridge image or verdict exists; ten of the 39 ridges are in tiles never rendered by
   committed code; the gallery's New York image is made by no committed code.
2. **Background tiles for the planted-wall test.** The plan says tiles at 15 to 45 m depth. The program takes tiles
   with a median depth of 12 to 55 m and at least 60% data.
3. **Azimuths and positions.** The plan says a random non-cardinal azimuth. The program draws from seven fixed
   azimuths and plants at a fixed position.
4. **The rule for counting a planted wall as found** (within 35 pixels, within 12°, length 120 m or more) is not in
   the plan.
5. **Rings.** Three conditions added to the plan's definition.
6. **Sandwaves.** The plan says crests at regular spacing of 12 to 60 m. The program flags any two crests 12 to 76 m
   apart.
7. **Chart mask.** The plan says a ridge's centroid or segment within 150 m of a charted object. The program
   measures distance to the vertices of charted areas and does not test whether a ridge lies inside one. A ship
   inside a charted fish haven was therefore reported as uncharted.
8. **Seam filter.** Where one flank of a ridge has fewer than five valid samples the program sets the step to zero,
   so the ridge passes. The Point Judith control passed this way.
9. **Depth mask.** The plan says −120 to −2 m. For the controls the program accepts anything below +1.5 m.
10. **Errors from the chart service** are swallowed and count as "nothing charted".

Also recorded:

- **The verdict rule.** The plan's Null requires the calibration gate to pass "decisively". The planted-wall test
  scored the minimum (8 of 10); one breakwater control has no data; the other passed through item 8.
  `RESULTS.md` no longer reports a clean null.
- **A fault in the plan itself.** The planted wall (4 m wide at half height, 0.70 m high) has about 55 times the
  cross-section of the Blinkerwall as published. The plan's statement that the Delaware breakwater has data is
  wrong.
- **Analyses added by the spot check, outside the plan:** planted walls of other sizes and with gaps, at random
  positions, three seeds; the native grid size under each tile; chart queries in all four bands; shaded relief of
  the tiles in question. All are in `spotcheck/` and all are exploratory.
