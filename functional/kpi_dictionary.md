# KPI catalog — useful questions, NOT ready-made numbers

**No NFL dataset has been supplied.** Each line is a *candidate definition*. Implement only if data exists and the official challenge permits it. Prefer one actionable KPI with proof over 20 dashboards.

| Candidate KPI | Working definition / interpretation | Who needs it | Essential data | Risk |
|---|---|---|---|---|
| Separation at a chosen moment | Nearest-defender distance (yd if units confirmed) at snap, pass release or arrival | Coaches, scouts, broadcast | Receiver + defenders, event frame | Standard NFL family of metrics; not novel |
| Separation trend | Change in nearest-defender distance over a documented interval | Coaches, scouting | Synchronized trajectories and time | Defender assignment unknown |
| Yards after catch (YAC) | Receiving gain after completed catch, using consistent field/yards definitions | Analysts, media | Catch event and subsequent gain | Already mainstream; selection bias |
| Apparent untargeted opportunity rate | Count of clearly defined spatial windows while eligible receiver wasn't targeted / **relevant pass routes** | Scouts, player personnel | All route participants, defenders, QB/ball timing, target label | NOT proof QB should throw |
| Off-ball association indicator | Instances where defender shift and teammate space increase coincide with another offensive player's movement | Coaches, scouts | Synchronized multiple offense/defense trajectories | Correlation, not causal credit |
| Recurrent open zone frequency | Fraction of **comparable plays** with low defender proximity in a defined spatial region | Opponent analysts | Normalized field, defender tracks, context | Empty region may be unexploitable |
| Contextual player comparison | Player score relative to comparable route/down/coverage situations, with sample counts | Personnel, reporters | Behavior, context, denominators | Confounding and small samples |
| Max observed speed | Highest recorded player speed in an included play | Commentators, reporters | Consistent speed fields or verified reconstruction | Frame noise; not season record |
| Pressure-to-throw window | Timing of defender proximity to QB versus release, only if pressure proxy defensible | Coaches, broadcast | QB/defender movement + throw frame | Not true QB pressure without validation |
| Demonstrated repeatability | Number and percentage of consistent event signals across eligible plays | Coaches, scouts, media | Multiple comparable plays | Generalization beyond provided data |

## Required metadata for *every* published KPI

- Definition (formula or precise rule), units, timeframe and frame reference.
- Dataset version/scope, filters, denominator and sample count.
- Baseline: what are we comparing against, and why is it fair?
- Known false positives, uncertainty and obvious football confounders.
- Source play IDs to audit the claim if permitted.
- **Never invent or label hypothetical values as measured findings.**

## Existing metrics / novelty check

NFL Next Gen Stats already provides separation-related measures, yards-after-catch analytics, completion probability, route recognition and advanced rushing analyses. Unless our work shows a **new decision** supported by evidence, do not market a renamed version as a breakthrough. https://www.nfl.com/news/next-gen-stats-new-advanced-metrics-you-need-to-know-for-the-2026-nfl-season
