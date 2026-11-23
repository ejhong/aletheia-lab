# Review of the plan before it was locked

Two models from other vendors read `protocol.md` before any event or control window had been read: OpenAI
`gpt-6.2-astra` and Google `gemini-4-neon`, on 2026-11-23. Their replies are in `round1/` and `round2/`, with the
text they saw. Cost: $1.71 at list price.

## Round 1

The first plan standardised each event window by egg variances measured in its one control window, and each
control by its event; and it switched to an event-minus-control test if the controls looked wrong.

| Point (who) | Done |
|---|---|
| Standardising a window by a single other window inflates the scores' spread and ties event to control (both) | Egg spreads are now measured over all the control windows of the same year, leaving out the window being scored. |
| The switch to a difference test, triggered by the controls, is uncalibrated, and its benchmark was wrong by √2 (both) | Removed. One test decides. Calibration is a label only; a paired check is always reported. |
| Event windows and control windows may overlap or be reused (both) | Rules added; the list as built has no overlap among its 116 windows. |
| A half-covered day counted as evaluable (both) | 80% of seconds are now required. |
| The 0.33 figure is a yardstick, not a prediction; a smaller network may give a smaller score (both) | Reworded; egg counts reported; weakness added. |
| "No departure" hid the sign and size (OpenAI) | Renamed; the mean score per event with an interval is reported. |
| Split the chi-square into each egg's own part and the part from pairs of eggs (Google) | The cross-egg part is reported. |
| Validate the reader on the project's own published events, not on the controls to be scored (both) | Done: six formal events of 2011–2015, within about 0.4 of the published scores, one exact. The control-only run was dropped. |
| Parser left open (both) | Spelled out; the program stops on a layout it does not expect. |
| "Over 500" events; 19 against 20 calendar instances; "fixed in advance" (OpenAI) | Corrected. |

Not done: a placebo run on hundreds of other non-event days (the 58 controls stand in, and would show only a
gross failure); a full simulation of false-verdict rates with realistic gaps (a one-tenth-scale simulation is in
the tests); checks for serial dependence and duplicated streams; local-time or attention-based windows.

## Round 2: errors only

Wording corrected before the lock: the standardiser is a mean square about 100, not a variance; the p-values
are nominal because events of a year share measured spreads; the paired check is not assumption-free; its power
figure assumes uncorrelated scores; the cross-egg part is blind to one egg's variance only in expectation; the
case of no evaluable event. Google found one of these and nothing else.

There was no third round.
