# RB Lifeline

**One-line goal:** at the exact moment pressure reaches the quarterback, show whether his running back is **available as an outlet** (open, within reach, past the line of scrimmage), rank RBs and offenses on how often they are, and compare what happens next: sack rate, how often the QB throws to the RB, completion. The question being measured: **when the pocket collapses, is there a lifeline?** The same per-play output feeds a **scout ranking**, a **coach dashboard** (play by play) and a **broadcast card**.

## Data check — PASSED on the supplied dataset (verified 2026-10-21)
Dataset: NFL Big Data Bowl 2023, available locally at `nfl-data/data/` (git submodule; clone with `--recursive` or run `git submodule update --init`): 2021 season, weeks 1–8, 122 games, 8,557 **dropback plays only**.

| Need | Source | Status |
|---|---|---|
| RB running a route vs blocking | `pffScoutingData.pff_role` (`Pass Route` / `Pass Block`) + `players.officialPosition` (`RB`, `FB`) | ✅ direct label |
| QB, RB and defender positions per frame | `tracking_[gameId].csv` (10 Hz, 22 players + ball) | ✅ until ~0.5 s after the throw |
| RB body orientation (sensitivity check only) | `o` in tracking | ✅ present on 100 % of player rows; convention checked: QB at the snap faces 88° when the offense moves right and 268° when it moves left → 0° = +y, 90° = +x, clockwise |
| Snap / throw / sack frames | `event` (`ball_snap`, `autoevent_ballsnap`, `pass_forward`, `autoevent_passforward`, `qb_sack`, `qb_strip_sack`) | ✅ |
| Pressure moment | QB–defender distance from tracking, validated against `pff_hit` / `pff_hurry` / `pff_sack` | ✅ (see results) |
| Line of scrimmage | football `x` at the snap frame | ✅ |
| Outcome | `passResult` (`S` = sack), `playResult` | ✅ play level only |
| Targeted receiver | only inside `playDescription` ("pass short right to A.Kamara") | ⚠️ parsed: 96.1 % of thrown passes; matched to the RB by initial + last name |
| Catch, ball in the air, YAC | — | ❌ tracking stops at throw + ~5 frames |

**Verified counts:** RB/FB route plays 7,379 · RB/FB pass-block plays 1,700 · RB route plays with PFF pressure 2,647 · RB route plays with a tracking pressure moment 2,327.

## Definitions (fixed before the results are read)

### Pressure moment
First frame after the snap (and no later than the throw or sack) where any `Pass Rush` or `Coverage` defender is **within 2 yd of the QB**. Plays without such a frame are excluded from the metric (stated denominator: pressured plays only).

### RB availability (all four conditions at the pressure frame)
1. **Route runner:** `pff_role == "Pass Route"` and `officialPosition` in `RB`, `FB`. Blocking backs are not outlets by design and are excluded.
2. **Open:** nearest defender more than **2.5 yd** away.
3. **In range:** less than **15 yd** from the QB (a back in the flat is often 10–14 yd from a QB who has dropped back).
4. **Past the line:** at most 1 yd behind the line of scrimmage (a back standing in his own backfield is trivially "open": 99 % of RBs are 2.5 yd clear at the snap).

**No orientation condition:** the angle between the RB's orientation and the RB→QB bearing is always between 0° and 180°, so a 180° tolerance means no filter. An RB running his route rarely faces the QB before the ball is thrown (only 31.8 % are within 60° at the pressure frame). Orientation is kept as a sensitivity check (bearing = `atan2(qb.x − rb.x, qb.y − rb.y)` in degrees, same convention as `o`).

### Outcomes
- **Sack rate** = share of plays with `passResult == "S"`.
- **RB target rate** = share of plays where the parsed target is this RB.
- **Completion when the RB is targeted** = share of `passResult == "C"` among those plays.

## Prototype results (scratch DuckDB query, 2026-10-21 — re-verify after the clean re-implementation)

**Pressure proxy vs. PFF labels:** 2,797 plays with a tracking pressure moment vs. 3,216 PFF-pressured plays; **precision 80.4 %** (proxy plays that PFF also marks as pressured), **recall 69.9 %**; median time from snap to pressure 2.7 s.

**Condition pass rates at the pressure frame** (2,327 RB route plays): open 71.8 % · within 15 yd 70.0 % · past the line 54.4 % · (facing within 60°: 31.8 %, not used).

| Pressured plays, RB running a route | RB available | RB not available |
|---|---|---|
| Plays | 505 (21.7 %) | 1,822 |
| **Sack rate** (95 % interval) | **14.7 % (± 3.1)** | **19.8 % (± 1.8)** |
| QB throws to the RB | **27.7 %** | 11.2 % |
| Completion when the RB is targeted | 71.4 % | 62.7 % |

**Robustness (stricter variants):** within 15 yd and facing < 120°, 435 plays (18.7 %): sack rate 15.4 % (± 3.4) vs. 19.4 % (± 1.8), RB targeted 29.9 % vs. 11.3 % — the intervals overlap, so the orientation rule costs plays without sharpening the result. Within 12 yd and no orientation rule, 333 plays (14.3 %): sack rate 13.8 % (± 3.7) vs. 19.5 % (± 1.7), RB targeted 31.2 % vs. 12.0 %. Within 12 yd and facing < 90°, 221 plays (9.5 %): sack rate 12.7 % (± 4.4) vs. 19.3 % (± 1.7), RB targeted 37.1 % vs. 12.4 %. Within 12 yd and facing < 60°, 132 plays (5.7 %): sack rate 12.9 % vs. 19.0 %. The direction holds across definitions; stricter rules give a larger gap on fewer plays.

**Top 10 RBs** (min 20 pressured route plays; 48 RBs qualify; league mean 21.7 %; shrunk % = (available + 20 × league mean) / (n + 20)):

| RB | n | Available | Raw % | Shrunk % | Targeted when available |
|---|---|---|---|---|---|
| Leonard Fournette | 26 | 14 | 53.8 | 39.9 | 21.4 % |
| Ty Johnson | 30 | 15 | 50.0 | 38.7 | 33.3 % |
| Antonio Gibson | 24 | 11 | 45.8 | 34.9 | 27.3 % |
| Chuba Hubbard | 39 | 16 | 41.0 | 34.5 | 68.8 % |
| Devonta Freeman | 22 | 10 | 45.5 | 34.1 | 20.0 % |
| Carlos Hyde | 24 | 9 | 37.5 | 30.3 | 44.4 % |
| Najee Harris | 44 | 14 | 31.8 | 28.7 | 14.3 % |
| Alvin Kamara | 46 | 13 | 28.3 | 26.3 | 30.8 % |
| Devin Singletary | 31 | 9 | 29.0 | 26.2 | 33.3 % |
| Kenneth Gainwell | 36 | 10 | 27.8 | 25.6 | 20.0 % |

**Offenses:** all 32 teams have 37+ pressured RB route plays (median 70); availability ranges from 12.6 % to 42.6 %.

## Rankings — who can use which one
- **Scouts / front office — RB ranking:** availability rate per RB with n, the shrunk value as the sort key and an interval; companion columns: targeted when available, completion. Read it as **indicative** (20+ plays per RB over 8 weeks), not a grade. Use it to choose whose film to watch, e.g. an RB who is often available but rarely targeted.
- **Coaches — offense ranking:** availability per team (37+ plays each, median 70) is more stable and partly reflects play design (route assignments, protection rules), which is what a coordinator controls.
- **Broadcasters — percentile line:** "this RB is in the top 10 % of backs at being available under pressure (n = …)", only when n ≥ 20.

## Known biases — must be shown in the deliverable
- **Selection:** teams keep the RB in to block when they expect pressure. Raw first look (plays with exactly one RB/FB): when the RB blocks, PFF pressure is higher (Man 47 % vs. 39 %, Zone 43 % vs. 35 %) and so is the sack rate. Never conclude that blocking or releasing *causes* fewer sacks.
- **Association, not causation:** an available RB may also mean a coverage that left space everywhere. Compare inside coverage family and blitz strata before any claim.
- **Proxy pressure:** 2 yd from the QB is a proxy (80 % precision vs. PFF); a defender can be close while still engaged with a blocker.
- **No facing rule:** an "available" RB may be running away from the QB (e.g. a wheel route); the 15 yd and past-the-line rules limit this, and the facing variant is reported as a check.
- **Target matching** by initial + last name can miss suffixes or name changes; unmatched plays are counted as "not targeted" in the prototype and must be flagged in the clean version.
- **Small samples per RB;** nearest defender is not the assigned defender; 8 weeks of one season.

## Method (rules + simple statistics, no black box)
1. One row per pressured play with an RB route runner: pressure frame, the four conditions, outcome, parsed target.
2. League comparison available vs. not available: sack rate, target rate, completion, with bootstrap intervals **resampling plays**.
3. Strata check: repeat inside Man / Zone and blitz (≥ 5 rushers) vs. not.
4. Player and team rates with shrinkage toward the league mean (k = 20) and minimum n = 20.
5. Sensitivity: pressure radius 1.5 / 2 / 2.5 yd, openness 2 / 2.5 / 3 yd, range 12 / 15 / 18 yd, optional facing filter 60° / 90°.

## Open decisions (team to confirm)
- Range: 15 yd (default) vs. 12 yd (stricter check-down, larger sack gap on fewer plays).
- Orientation: not used (default; it keeps the largest sample); 120° / 90° kept as sensitivity checks.
- Minimum n for the RB ranking: 20 (48 RBs, default) vs. 15 (61 RBs) vs. 30 (33 RBs). The conditions change the numerator only; the per-RB sample is the number of pressured route plays.
- Count FB with RB (default) or RB only.
- nflverse join to cross-check targets (allowed as free public data; confirm network and rules).

## Deliverables
### Scout ranking
Sortable RB table (n, available, raw %, shrunk %, interval, targeted when available) + team table.
### Coach dashboard (game review)
Game → play list (pressured plays only) → **freeze-frame at the pressure moment**: QB, closest defender with an arrow, RB circled with the four checks and their values; play animation from snap to throw as a GIF.
### Broadcast card
One sentence built only from computed numbers, e.g. (illustrative values) "Pressure at 2.4 s · RB open (4.1 yd), 9 yd from the QB, past the line → lifeline available." Shown only when the play passes all checks.

## Definition of done
- Definitions above applied in code with unit tests; prototype numbers reproduced or corrected.
- League comparison with intervals and the strata check.
- RB and team rankings with n and shrinkage.
- Two verified freeze-frames (available → completion, not available → sack) and one GIF.
- At least 5 plays checked by eye (pressure frame, RB checks vs. drawn positions).
- Submission README with the limitations from **Known biases**.

## Concrete build plan — functions
`load_play_table()`; `normalize_play_direction()`; `find_snap_and_throw_or_sack_frames()`; `line_of_scrimmage()`; `qb_defender_distance()`; `find_pressure_frame()`; `validate_pressure_proxy()`; `rb_checks_at(frame)` (open, in range, past the line; facing as an optional check); `flag_rb_available()`; `parse_target_receiver()`; `outcomes_by_availability()` (with bootstrap); `rank_rbs()` and `rank_offenses()` (shrinkage, minimum n); `render_freeze_frame()`; `render_play_gif()`; `broadcast_sentence()`.

**Tests:** synthetic frames for direction normalization, bearing vs. `o` (0° = +y, clockwise) for the optional facing check, the four checks on hand-built positions, pressure frame when no defender reaches 2 yd, sack plays without a throw, target parser on real descriptions incl. unmatched names, ranking refuses to list an RB below the minimum n.

## Who is it useful for, and why
- **Scouts and front offices:** which RBs give their QB an escape route under pressure, a third-down skill box scores do not show.
- **Offensive coordinators and RB coaches:** how often their check-down design actually produces an outlet when the pocket breaks.
- **Broadcasters:** a verified explanation of a sack ("no lifeline") or of a check-down completion.

## Novelty caveat
Hypothesis, not a proven original idea. BDB 2023 centered on pass rush and protection, where the RB is studied as a blocker; the angle here is the RB as the **receiving outlet at the moment of pressure**. Check existing BDB 2023 notebooks and Next Gen Stats before claiming novelty.
