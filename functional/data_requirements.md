# Data availability gate — MUST READ BEFORE SPECIFYING A FEATURE

**We do not yet have the October 21 dataset.** This file defines what to look for, not what is guaranteed to exist.

## What the participant guide says (received 20 October 2026)

- The dataset and the detailed brief are handed out at kickoff. You must use the provided dataset; free public external data may be added.
- Content: NFL Next Gen Stats frame-by-frame tracking (x/y of the 22 players, 10 frames per second, for each play) plus PFF scouting data (player roles, matchups, results).
- `playDirection` is `left` or `right`: normalize coordinates so every play goes in the same direction.
- `passResult` is C (complete), I (incomplete), S (sack), R (scramble) or IN (interception).
- Libraries available: pandas, numpy, matplotlib, seaborn, plotly, scikit-learn, scipy.

Everything else (files, other columns, units, which events and frames are included) is unknown until kickoff: run the Level 0 inventory below.

## Level 0 — what was actually released?

Agent/human must note: files/formats, years/seasons, permitted scope, dictionary, restrictions, reference frames, outcome labels, identifiers, number of plays, units, missingness and whether both teams are tracked. Mark each field group as **AVAILABLE**, **PARTIAL** or **UNAVAILABLE**. **Do not write guesses as actual column names.**

## Required data groups

| Capability | Information required | Hard stop if absent |
|---|---|---|
| Identify plays | Unique play/game IDs, attacking team, play type | Cannot compare unrelated frames |
| Reconstruct movement | Player identity, frame/time, x/y coordinates, units and field direction | Cannot animate meaningful trajectories |
| Identify roles | WR/TE/RB labels or reliable roster join | Cannot claim positional insights |
| Measure receiving outcomes | Pass attempts, targets, catch events, play results | Cannot evaluate catch-based KPIs |
| Off-ball candidates | **All** relevant eligible receiver trajectories plus defender tracks | Cannot claim contributions of untargeted players |
| QB opportunity | QB location/timing, relevant ball/event timing and defenders | Cannot approximate throwing window responsibly |
| Recurrent defensive weakness | Multiple comparable plays, defenders and context | Cannot claim recurring tactical patterns |
| Compare players | Meaningful repeated opportunities, denominators, context and sample size | Cannot publish a useful ranking |

## Sanity checks before metrics

1. Inspect coordinate units; do not assume yards, meters or orientation.
2. Check duplicate (game, play, player, frame) rows and missing timestamps.
3. Identify snap, pass arrival and catch event labels **if present**.
4. Confirm which players and periods are included.
5. Normalize play direction carefully; some datasets encode possession or play direction differently.
6. Separate passing vs rushing plays.
7. Decide what the denominator means: pass routes, snaps, targets, catches or plays.
8. Check small-sample bias and missing games/players; never overgeneralize the subset.
9. Do not call a measure expected value, causal impact or probability without methodology and validation.
10. Confirm publicly published NFL metrics are not being rediscovered under a new name.

## Suggested evidence record after kickoff (not pre-filled)

- **Selected audience and decision:** TBD
- **Claim and KPI:** TBD
- **Data file(s) / fields:** TBD (from official release)
- **Computational definition and units:** TBD
- **Sample size and denominator:** TBD
- **Baseline / comparable cohort:** TBD
- **Observational limitations:** TBD
- **Verification tests:** TBD

Sources: https://operations.nfl.com/gameday/technology/nfl-next-gen-stats and https://operations.nfl.com/programs-initiatives/innovation/big-data-bowl
