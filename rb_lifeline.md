# RB Lifeline

**One-line goal:** at the exact moment pressure reaches the quarterback, show whether his running back is **available as an outlet** (open, within reach, past the line of scrimmage, turned toward the QB), rank RBs and offenses on how often they are, and compare what happens next: sack rate, how often the QB throws to the RB, completion. The question being measured: **when the pocket collapses, is there a lifeline?** The same per-play output feeds a **scout ranking**, a **coach dashboard** (play by play) and a **broadcast card**.

## Data check — PASSED on the supplied dataset (verified 2026-10-21)
Dataset: NFL Big Data Bowl 2023, available locally at `nfl-data/data/` (git submodule; clone with `--recursive` or run `git submodule update --init`): 2021 season, weeks 1–8, 122 games, 8,557 **dropback plays only**.

| Need | Source | Status |
|---|---|---|
| RB running a route vs blocking | `pffScoutingData.pff_role` (`Pass Route` / `Pass Block`) + `players.officialPosition` (`RB`, `FB`) | ✅ direct label |
| QB, RB and defender positions per frame | `tracking_[gameId].csv` (10 Hz, 22 players + ball) | ✅ until ~0.5 s after the throw |
| RB body orientation | `o` in tracking | ✅ present on 100 % of player rows; convention checked: QB at the snap faces 88° when the offense moves right and 268° when it moves left → 0° = +y, 90° = +x, clockwise |
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

### RB availability (all five conditions at the pressure frame)
1. **Route runner:** `pff_role == "Pass Route"` and `officialPosition` in `RB`, `FB`. Blocking backs are not outlets by design and are excluded.
2. **Open:** nearest defender more than **2.5 yd** away.
3. **In range:** less than **15 yd** from the QB (a back in the flat is often 10–14 yd from a QB who has dropped back).
4. **Past the line:** at most 1 yd behind the line of scrimmage (a back standing in his own backfield is trivially "open": 99 % of RBs are 2.5 yd clear at the snap).
5. **Turned toward the QB:** angle between the RB's orientation `o` and the RB→QB bearing **below 90°**, i.e. the QB is in the front half of the RB's body orientation, so he can see the QB and receive the ball. Bearing = `atan2(qb.x − rb.x, qb.y − rb.y)` in degrees, same convention as `o`. A tighter rule (60°) keeps only 31.8 % of RBs, because a back running his route rarely squares up before the throw; no rule at all would count backs running away from the QB.

### Outcomes
- **Sack rate** = share of plays with `passResult == "S"`.
- **RB target rate** = share of plays where the parsed target is this RB.
- **Completion when the RB is targeted** = share of `passResult == "C"` among those plays.

## Prototype results (scratch DuckDB query, 2026-10-21 — re-verify after the clean re-implementation)

**Pressure proxy vs. PFF labels:** 2,797 plays with a tracking pressure moment vs. 3,216 PFF-pressured plays; **precision 80.4 %** (proxy plays that PFF also marks as pressured), **recall 69.9 %**; median time from snap to pressure 2.7 s.

**Condition pass rates at the pressure frame** (2,327 RB route plays): open 71.8 % · within 15 yd 70.0 % · past the line 54.4 % · turned within 90° 55.4 % (within 60°: 31.8 %).

| Pressured plays, RB running a route | RB available | RB not available |
|---|---|---|
| Plays | 350 (15.0 %) | 1,977 |
| **Sack rate** (95 % interval) | **14.3 % (± 3.7)** | **19.4 % (± 1.7)** |
| QB throws to the RB | **31.7 %** | 11.8 % |
| Completion when the RB is targeted | 72.1 % | 63.5 % |

Sack-rate gap: **5.1 points (± 4.1)**, i.e. the interval of the difference excludes zero.

**Robustness — orientation limit at 15 yd** (available plays · sack gap with 95 % interval of the difference · RB targeted available vs. not):

| Orientation limit | Available | Sack gap | RB targeted |
|---|---|---|---|
| **90° (default)** | **350 (15.0 %)** | **5.1 ± 4.1 pts** | **31.7 % vs. 11.8 %** |
| 105° | 397 (17.1 %) | 3.7 ± 4.0 pts | 31.2 % vs. 11.4 % |
| 120° | 435 (18.7 %) | 4.0 ± 3.8 pts | 29.9 % vs. 11.3 % |
| 135° | 458 (19.7 %) | 4.7 ± 3.7 pts | 29.3 % vs. 11.2 % |
| none | 505 (21.7 %) | 5.1 pts (14.7 % vs. 19.8 %) | 27.7 % vs. 11.2 % |

The sack gap stays at about 4–5 points and the target rate at about ×2.6 whatever the limit; 90° is the clearest football rule with an interval that excludes zero. **Other variants:** within 12 yd and no orientation rule, 333 plays (14.3 %): sack rate 13.8 % (± 3.7) vs. 19.5 % (± 1.7), RB targeted 31.2 % vs. 12.0 %. Within 12 yd and facing < 90°, 221 plays (9.5 %): sack rate 12.7 % (± 4.4) vs. 19.3 % (± 1.7), RB targeted 37.1 % vs. 12.4 %. Within 12 yd and facing < 60°, 132 plays (5.7 %): sack rate 12.9 % vs. 19.0 %. The direction holds across definitions; stricter rules give a larger gap on fewer plays.

**Top 10 RBs** (min 20 pressured route plays; 48 RBs qualify; league mean 15.0 %; shrunk % = (available + 20 × league mean) / (n + 20)):

| RB | n | Available | Raw % | Shrunk % | Targeted when available |
|---|---|---|---|---|---|
| Chuba Hubbard | 39 | 14 | 35.9 | 28.8 | 64.3 % |
| Devonta Freeman | 22 | 9 | 40.9 | 28.6 | 22.2 % |
| Leonard Fournette | 26 | 9 | 34.6 | 26.1 | 22.2 % |
| Ty Johnson | 30 | 10 | 33.3 | 26.0 | 40.0 % |
| Antonio Gibson | 24 | 7 | 29.2 | 22.7 | 42.9 % |
| Alvin Kamara | 46 | 11 | 23.9 | 21.2 | 36.4 % |
| Carlos Hyde | 24 | 6 | 25.0 | 20.5 | 50.0 % |
| Najee Harris | 44 | 10 | 22.7 | 20.3 | 20.0 % |
| Kenneth Gainwell | 36 | 8 | 22.2 | 19.7 | 25.0 % |
| Devin Singletary | 31 | 7 | 22.6 | 19.6 | 42.9 % |

**Offenses:** all 32 teams have 37+ pressured RB route plays (median 70); availability ranges from 5.4 % to 27.4 %.

## Rankings — who can use which one
- **Scouts / front office — RB ranking:** availability rate per RB with n, the shrunk value as the sort key and an interval; companion columns: targeted when available, completion. Read it as **indicative** (20+ plays per RB over 8 weeks), not a grade. Use it to choose whose film to watch, e.g. an RB who is often available but rarely targeted.
- **Coaches — offense ranking:** availability per team (37+ plays each, median 70) is more stable and partly reflects play design (route assignments, protection rules), which is what a coordinator controls.
- **Broadcasters — percentile line:** "this RB is in the top 10 % of backs at being available under pressure (n = …)", only when n ≥ 20.

## Known biases — must be shown in the deliverable
- **Selection:** teams keep the RB in to block when they expect pressure. Raw first look (plays with exactly one RB/FB): when the RB blocks, PFF pressure is higher (Man 47 % vs. 39 %, Zone 43 % vs. 35 %) and so is the sack rate. Never conclude that blocking or releasing *causes* fewer sacks.
- **Association, not causation:** an available RB may also mean a coverage that left space everywhere. Compare inside coverage family and blitz strata before any claim.
- **Proxy pressure:** 2 yd from the QB is a proxy (80 % precision vs. PFF); a defender can be close while still engaged with a blocker.
- **Orientation** is body orientation, not where the RB is looking; the 90° rule is a coarse "QB in front of him" filter, reported with the 105–135° and no-rule variants.
- **Target matching** by initial + last name can miss suffixes or name changes; unmatched plays are counted as "not targeted" in the prototype and must be flagged in the clean version.
- **Small samples per RB;** nearest defender is not the assigned defender; 8 weeks of one season.

## Method (rules + simple statistics, no black box)
1. One row per pressured play with an RB route runner: pressure frame, the five conditions, outcome, parsed target.
2. League comparison available vs. not available: sack rate, target rate, completion, with bootstrap intervals **resampling plays**.
3. Strata check: repeat inside Man / Zone and blitz (≥ 5 rushers) vs. not.
4. Player and team rates with shrinkage toward the league mean (k = 20) and minimum n = 20.
5. Sensitivity: pressure radius 1.5 / 2 / 2.5 yd, openness 2 / 2.5 / 3 yd, range 12 / 15 / 18 yd, orientation 90° / 120° / none.

## Open decisions (team to confirm)
- Range: 15 yd (default) vs. 12 yd (stricter check-down, larger sack gap on fewer plays).
- Orientation: 90° (default, clearest rule) vs. 120° (more plays, gap 4.0 ± 3.8 pts).
- Minimum n for the RB ranking: 20 (48 RBs, default) vs. 15 (61 RBs) vs. 30 (33 RBs). The conditions change the numerator only; the per-RB sample is the number of pressured route plays.
- Count FB with RB (default) or RB only.
- nflverse join to cross-check targets (allowed as free public data; confirm network and rules).

## Deliverables
### Scout ranking
Sortable RB table (n, available, raw %, shrunk %, interval, targeted when available) + team table.
### Coach dashboard (game review)
Game → play list (pressured plays only) → **freeze-frame at the pressure moment**: QB, closest defender with an arrow, RB circled with the five checks and their values; play animation from snap to throw as a GIF.
### Broadcast card
One sentence built only from computed numbers, e.g. (illustrative values) "Pressure at 2.4 s · RB open (4.1 yd), 9 yd from the QB, past the line, turned toward him (40°) → lifeline available." Shown only when the play passes all checks.

## Definition of done
- Definitions above applied in code with unit tests; prototype numbers reproduced or corrected.
- League comparison with intervals and the strata check.
- RB and team rankings with n and shrinkage.
- Two verified freeze-frames (available → completion, not available → sack) and one GIF.
- At least 5 plays checked by eye (pressure frame, RB checks vs. drawn positions).
- Submission README with the limitations from **Known biases**.

## Concrete build plan — functions
`load_play_table()`; `normalize_play_direction()`; `find_snap_and_throw_or_sack_frames()`; `line_of_scrimmage()`; `qb_defender_distance()`; `find_pressure_frame()`; `validate_pressure_proxy()`; `rb_checks_at(frame)` (open, in range, past the line, turned toward the QB); `flag_rb_available()`; `parse_target_receiver()`; `outcomes_by_availability()` (with bootstrap); `rank_rbs()` and `rank_offenses()` (shrinkage, minimum n); `render_freeze_frame()`; `render_play_gif()`; `broadcast_sentence()`.

**Tests:** synthetic frames for direction normalization, bearing vs. `o` (0° = +y, clockwise), the five checks on hand-built positions, pressure frame when no defender reaches 2 yd, sack plays without a throw, target parser on real descriptions incl. unmatched names, ranking refuses to list an RB below the minimum n.

## Who is it useful for, and why
- **Scouts and front offices:** which RBs give their QB an escape route under pressure, a third-down skill box scores do not show.
- **Offensive coordinators and RB coaches:** how often their check-down design actually produces an outlet when the pocket breaks.
- **Broadcasters:** a verified explanation of a sack ("no lifeline") or of a check-down completion.

## Novelty caveat
Hypothesis, not a proven original idea. BDB 2023 centered on pass rush and protection, where the RB is studied as a blocker; the angle here is the RB as the **receiving outlet at the moment of pressure**. Check existing BDB 2023 notebooks and Next Gen Stats before claiming novelty.
