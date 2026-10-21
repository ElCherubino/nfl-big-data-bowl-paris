# Numerical audit — 21 October 2026

This records actual recalculated output, rather than the exploratory numbers in `rb_lifeline.md`.

Publication generation: `3a999d342ff04d23bcd5f333e2bb4837`. Parameters: pressure ≤ 2 yd, separation > 2.5 yd, QB distance < 15 yd, line progress ≥ −1 yd, body-facing angle < 90°, RB and FB included. Bootstrap: 2,000 play resamples, seed 20261021. Season scope: **2021, weeks 1–8**.

## Coverage and quality

| Check | Recalculated result |
| --- | ---: |
| Games retained | 122 |
| Dropbacks retained | 8,557 |
| Replayable dropbacks | 8,533 |
| Dropbacks with unavailable snap/end tracking | 24, retained with diagnostics |
| Detected pressure candidates | 2,751 |
| Evaluable RB/FB player-play observations | 2,290 |
| Evaluable unique team-play observations | 2,155 |
| Eligible individual ranking cohort, n ≥ 20 | 49 |
| Eligible attacks | 32 |
| Player-play availability reference | 14.8908% |
| Team-play availability reference | 15.6381% |
| Target descriptions matched | 7,211 / 7,565 thrown passes (95.3206%) |
| Unmatched target descriptions | 354; excluded from relevant denominators |
| Pressure proxy validation population | 8,533 dropbacks, including those without an RB route |
| Pressure proxy TP / FP / TN / FN | 2,221 / 530 / 4,800 / 982 |
| Pressure proxy precision | 2,221 / 2,751 = 80.7343% |
| Pressure proxy recall | 2,221 / 3,203 = 69.3412% |
| Median time to detected pressure | 2.7 s |

Match summaries and season totals use the same opportunities. The publication validator independently reconstructs match rows and distinct team-play totals and checks all availability, target and completion numerators, denominators and unknown counts. Multiple backs do not multiply the collective denominator; transferred players retain their global identity.

## Descriptive comparison

| Outcome | Available collective solution | Unavailable collective solution |
| --- | --- | --- |
| Unique eligible plays | 337 | 1,818 |
| Sacks | 47 / 337 (13.95%) | 360 / 1,818 (19.80%) |
| Route RB/FB targeted, known outcomes | 116 / 326 (35.58%); 11 unknown | 238 / 1,703 (13.98%); 115 unknown |
| Completion when a route RB/FB was targeted | 83 / 116 (71.55%) | 150 / 238 (63.03%) |

The unavailable-minus-available sack-rate difference is **5.855 percentage points**, with a play-bootstrap 95% interval of **1.521 to 9.946 points**. This is an observational association, not a causal effect. The completion-rate difference interval includes zero. The exports also contain coverage/blitz cells, missing-context cells, fourteen threshold sensitivity rows, and separately identified minimum-n/RB-only ranking variants. The sack-rate gap is not uniformly conclusive across thresholds: the 1.5 yd and 2.5 yd pressure variants and the 18 yd range variant have intervals including zero. Do not describe the baseline result as robust under every definition.

## Five independently checked real plays

All examples are from DAL at TB, `gameId=2021090900`. The scalar audit reads the original tracking and scouting CSVs and does **not** import the evaluator. It verifies snap/end events, first pressure, normalization, orientation, precise measures, check flags, and pressure-frame agreement. Values below are rounded for reading only.

| Case | playId | Direction | Audited frame | Observation |
| --- | --- | --- | ---: | --- |
| Available → completed pass to RB | 4560 | Right | 32, pressure | Giovani Bernard: separation 3.9008 yd; QB distance 13.1115 yd; progress 3.43 yd; angle 63.1166°; all five checks pass. Description names G.Bernard and outcome C. |
| Unavailable → sack | 2279 | Right | 40, pressure | Ezekiel Elliott: QB distance 16.1641 yd fails the strict 15 yd condition. Outcome S; subsequent replay frames do not change this verdict. |
| No pressure | 97 | Right | 6, snap | No defender within 2 yd on any evaluated post-snap frame through throw. Replay remains available; excluded from pressure metrics. |
| Blocking / opposite direction | 349 | Left | 28, pressure | Ezekiel Elliott is PFF Pass Block. State remains blocking even when spatial measures are available. Leftward source coordinates and orientation are rotated together. |
| Multiple backs | 1368 | Right | 6, snap | Ezekiel Elliott and Tony Pollard both appear with their own states. No detected pressure, so neither contributes a pressured opportunity. Multi-back pressured counting is also covered by the synthetic conservation tests. |

Reproduce with:

```bash
.venv/bin/python tools/audit_plays.py
```

Detailed numerical evidence is written to `outputs/validation/play-audit.json`. Browser screenshots and visual-review evidence are recorded separately by the delivery checks; passing a numerical audit alone is not a claim of visual verification.

## Differences from the exploratory notes

The notes mix 90° and 120° orientation rules and later introduce an availability-times-catch score. The accepted specs and JSON contract instead require the 90° default and ranking by regularized **availability**. The implementation follows those specs; it does not force the prototype’s player order, 48-player cohort or 18.7% reference.

The pressure count differs from the prototype’s 2,797 candidates. The implementation requires pressure strictly after the identified snap, caps evaluation at the first throw/sack/scramble event, retains missing-event diagnostics, and treats unknown roles conservatively. These definition and quality differences are documented; their individual numerical contributions have not been isolated, so this is not an asserted exact decomposition of the 46-play difference.

The prototype target recognition rate of 96.1% is replaced by 95.3206% under conservative unique offensive-participant matching. Unknown targets remain unknown. Differences can also arise from unique collective play counting instead of adding player observations. The new comparison is reproducible from the published counts and does not imply novelty or causality.

Remaining limitations: backs selected to block differ from route runners; coverage/blitz control is limited; body orientation is not gaze; nearest defender is not an assigned defender; pressure is a geometric proxy; small samples are unstable; tracking ends shortly after the throw; eight historical weeks do not represent a full season.
