# RB Lifeline delivery validation

The delivered product is a static React website backed by recalculated NFL tracking exports. Coaches can review games and pressure-frame checks; scouts use the season RB and attack tables to choose film; reporters use the league ranking and a sentence constructed only from published fields.

- [Numerical audit and five identified source-coordinate checks](validation/numerical-audit.md)
- [Build and browser execution evidence](validation-browser.md)

The full real-data build retained **122 games and 8,557 dropbacks**, with **8,533 replayable plays**. The other 24 remain listed with explicit missing-event diagnostics. Season tables use 2021 weeks 1–8, the accepted 90° rule and regularized availability. They do not reproduce the later exploratory availability-times-catch score.

Reproduce the calculation and checks using the commands in the root [README](../README.md). The numerical audit writes detailed source measures to `outputs/validation/play-audit.json`; browser screenshots remain in ignored output directories. No generated data is replaced with a synthetic fallback in the product.

## Visual review

The five full-publication screenshots were visually inspected on 21 October 2026 alongside the independent source measures. The field has equal yard scales, the leftward source play is rotated toward the right, and observed points, ball, past trails, QB/back orientation arrows and pressure-defender ring render coherently. Check values and status glyphs agree with the independent audit:

- `4560`: green Giovani Bernard, five passing checks at pressure frame 32.
- `2279`: red Ezekiel Elliott, 16.2 yd QB distance fails the 15 yd range check at frame 40.
- `97`: no-pressure play remains viewable and explicitly uncounted.
- `349`: leftward source play normalized, Elliott gray and labelled blocking at frame 28.
- `1368`: two backs selectable with individual states; no pressure and no counted observation.

Screenshots: `outputs/browser-audit/audit-2021090900-{4560,2279,97,349,1368}.png`. The browser suite additionally verified animated pressure pause and resume, mobile keyboard controls and a text alternative. Current-frame check details are also available separately from the fixed pressure verdict, including on plays without pressure.
