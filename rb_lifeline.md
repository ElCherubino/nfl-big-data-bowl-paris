# RB Lifeline

**One-line goal:** at the exact moment pressure reaches the quarterback, show whether his running back is **available as an outlet** (open, within reach, past the line of scrimmage, turned toward the QB), rank RBs on a **Lifeline score** (available under pressure × reliable hands) and offenses on availability, and compare what happens next: sack rate, how often the QB throws to the RB, completion. The question being measured: **when the pocket collapses, is there a lifeline?** The same per-play output feeds **one website with two dashboards**: a **coach dashboard** (game → play by play in 2D, RB availability per game and per season) and a **broadcaster dashboard** (season ranking "Best safety valves"). See [Deliverable — the POC website](#deliverable--the-poc-website).

## Deliverable — the POC website

**What we ship:** one website, two entry points (Coach / Broadcaster). Every number on it comes from the Python pipeline below; the site only displays precomputed files, it computes nothing and invents nothing. The current `website/` scaffold (React + Vite) holds **synthetic demo content only** and must be wired to the computed files before the demo.

**Scope of "season":** the dataset covers **2021, weeks 1–8** (122 games). Every season figure is labelled "2021 · weeks 1–8", never "full season".

### The one metric shown everywhere — availability rate
**Availability rate = pressured plays where the RB is available ÷ pressured plays where the RB runs a route** (five conditions at the pressure frame, see [Definitions](#definitions-fixed-before-the-results-are-read)). The same definition is used at play, game and season level; only the set of plays changes. Always displayed with its **n** ("4 / 11 · 36 %"). The **season RB ranking** sorts by the **Lifeline score** = shrunk availability × shrunk catch rate (see [Prototype results](#prototype-results-scratch-duckdb-query-2026-10-21--re-verify-after-the-clean-re-implementation)).

### 1. Coach dashboard
Navigation: **Game** (week, teams, score) → three views.

**1a. Play by play (per game)**
- Play list: every dropback play of the game, with quarter, clock, down & distance, `playDescription`, outcome (sack / completion / incompletion / RB targeted) and a badge **pressured · RB available / not available / RB blocking**. Default filter: pressured plays with an RB route runner (the plays that count in the rate).
- **2D animation** of the selected play, from the snap to the throw or sack (10 Hz, play/pause, frame slider, speed ×0.5/×1):
  - all 22 players + ball on a field drawn to scale, line of scrimmage shown, offense always moving left → right (`normalize_play_direction()`);
  - **trajectory:** trail of past positions for the RB and the QB (short fading trail for the other players);
  - **where he faces:** an orientation arrow on the RB and the QB from `o`. It is **body orientation**, labelled as such ("facing", not "looking");
  - **RB colour per frame:** **green** when the four spatial checks pass at that frame (open > 2.5 yd, < 15 yd from the QB, at most 1 yd behind the line, QB within 120° of his orientation), **red** otherwise, **grey** when the RB is blocking (not an outlet by design). A ✓/✗ mark next to the dot so the colour is not the only signal;
  - **pressure moment:** marked on the slider; the animation pauses there and a side panel shows the five checks with their values (e.g. "nearest defender 4.1 yd ✓ · 9.2 yd from QB ✓ · 2 yd past the line ✓ · 40° ✓"), plus the closest defender to the QB highlighted. **The play verdict is the colour at the pressure frame**, not at any other frame.
- Plays without a tracking pressure moment are viewable (colours still shown) but labelled "no pressure → not counted".

**1b. RB availability — this game**
Table of every RB/FB of both teams who ran a route on at least one pressured play: available / pressured route plays, raw %, RB targeted when available. Clicking an RB filters the play list to his plays. **No ranking, no shrinkage, no interval at game level:** n is typically 0–10 per RB per game, so the table is a play-count summary, shown with the caption "small sample, use the plays as film references".

**1c. RB availability — season (2021, weeks 1–8)**
Sortable table for every RB, filterable by team: n (pressured route plays), available, raw %, availability shrunk % (k = 20 toward the league mean), catch rate shrunk % (k = 10), **Lifeline score** (sort key), 95 % interval, targeted when available, completion when targeted. RBs below the minimum n (20) appear greyed out with "n too small" and no rank. A team table (availability per offense, 37+ plays each) sits next to it, because team rates are more stable and reflect play design, which is what a coordinator controls.

### 2. Broadcaster dashboard — "Best safety valves"
One screen: **league-wide ranking of RBs by Lifeline score** (availability under pressure × catch rate; 2021, weeks 1–8), only RBs with n ≥ 20 (48 RBs with the default rules).
- Each row: rank, RB, team, Lifeline score, availability % and catch rate (shrunk, raw in small print), n, percentile ("top 10 % of backs").
- League mean shown as a reference line (Lifeline score 14.0 %, availability 18.7 % with the default rules).
- Fixed caption: "Chance that, on a pressured snap, the RB was open, in range, past the line and facing the QB, times his catch rate. Reflects the player *and* his team's play design; not a causal grade."
- No per-play view, no animation, no model text. A sentence such as "top 10 % of backs at being available under pressure (n = 39)" is generated only from the computed table.

### Data flow (POC)
`nfl-data/` CSV → Python pipeline (functions in the build plan, tested) → static files read by the site:
- `season_rb.json`, `season_team.json` — season tables (coach 1c + broadcaster);
- `games.json` — game list;
- `game_<gameId>.json` — plays of one game, per-play checks and verdict, per-game RB table, and the frames of the dropback plays (positions rounded to 0.1 yd, `o`, per-frame RB check flags), loaded only when the game is opened.

The site is static (no backend), so it can be served locally or from any static host if the rules permit it.

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
5. **Turned toward the QB:** angle between the RB's orientation `o` and the RB→QB bearing **below 120°**, i.e. the QB is within the RB's field of view (not behind him), so he can see the QB and receive the ball. Bearing = `atan2(qb.x − rb.x, qb.y − rb.y)` in degrees, same convention as `o`. Tighter rules shrink the sample (90°: 55.4 % of RBs pass, 60°: 31.8 %), because a back running his route rarely squares up before the throw; no rule at all would count backs running away from the QB.

### Outcomes
- **Sack rate** = share of plays with `passResult == "S"`.
- **RB target rate** = share of plays where the parsed target is this RB. Name matching: last name + first-name prefix, because play descriptions sometimes use two letters (`Mi.Carter`, `Da.Williams`, `Dj.Moore`).
- **Completion when the RB is targeted** = share of `passResult == "C"` among those plays.

## Prototype results (scratch DuckDB query, 2026-10-21 — re-verify after the clean re-implementation)

**Pressure proxy vs. PFF labels:** 2,797 plays with a tracking pressure moment vs. 3,216 PFF-pressured plays; **precision 80.4 %** (proxy plays that PFF also marks as pressured), **recall 69.9 %**; median time from snap to pressure 2.7 s.

**Condition pass rates at the pressure frame** (2,327 RB route plays): open 71.8 % · within 15 yd 70.0 % · past the line 54.4 % · orientation rules: within 90° 55.4 %, within 60° 31.8 % (120° in the robustness table).

| Pressured plays, RB running a route | RB available | RB not available |
|---|---|---|
| Plays | 435 (18.7 %) | 1,892 |
| **Sack rate** (95 % interval) | **15.4 % (± 3.4)** | **19.4 % (± 1.8)** |
| QB throws to the RB | **31.0 %** | 11.8 % |
| Completion when the RB is targeted (135 vs. 223 passes) | **71.9 %** | 61.9 % |

Sack-rate gap: **4.0 points (± 3.8)**: the interval of the difference narrowly excludes zero; report it as a moderate association.

**Robustness — orientation limit at 15 yd** (available plays · sack gap with 95 % interval of the difference · RB targeted available vs. not):

| Orientation limit | Available | Sack gap | RB targeted |
|---|---|---|---|
| 90° | 350 (15.0 %) | 5.1 ± 4.1 pts | 31.7 % vs. 11.8 % |
| 105° | 397 (17.1 %) | 3.7 ± 4.0 pts | 31.2 % vs. 11.4 % |
| **120° (default)** | **435 (18.7 %)** | **4.0 ± 3.8 pts** | **31.0 % vs. 11.8 %** |
| 135° | 458 (19.7 %) | 4.7 ± 3.7 pts | 29.3 % vs. 11.2 % |
| none | 505 (21.7 %) | 5.1 pts (14.7 % vs. 19.8 %) | 27.7 % vs. 11.2 % |

The sack gap stays at about 4–5 points and the target rate at about ×2.6 whatever the limit. 120° (QB within the field of view) is the default because it keeps more plays; 90° gives the cleanest interval. Target rates in this table use first-initial matching except the 120° row. **Other variants:** within 12 yd and no orientation rule, 333 plays (14.3 %): sack rate 13.8 % (± 3.7) vs. 19.5 % (± 1.7), RB targeted 31.2 % vs. 12.0 %. Within 12 yd and facing < 90°, 221 plays (9.5 %): sack rate 12.7 % (± 4.4) vs. 19.3 % (± 1.7), RB targeted 37.1 % vs. 12.4 %. Within 12 yd and facing < 60°, 132 plays (5.7 %): sack rate 12.9 % vs. 19.0 %. The direction holds across definitions; stricter rules give a larger gap on fewer plays.

**RB ranking — Lifeline score** (48 RBs with at least 20 pressured route plays):

- **Availability (shrunk)** = (available plays + 20 × 18.7 %) / (n + 20): how often he is a usable outlet when pressure arrives.
- **Catch rate (shrunk)** = (receptions + 10 × 75.2 %) / (targets + 10), on **all** his targets in the dataset (1,225 RB targets league-wide), because catching is a skill that does not depend on the pressure moment and per-RB samples under pressure are tiny.
- **Lifeline score = availability × catch rate** = the chance that, on a pressured play, he is available **and** a pass to him is completed. Two probabilities multiplied, no arbitrary weights. League mean 14.0 %.
- Not in the score: how often the QB actually throws to him (a QB decision), shown as a context column.

| RB | n | Available | Avail. raw % | Avail. shrunk % | Targets | Rec. | Catch raw % | Catch shrunk % | **Lifeline score** |
|---|---|---|---|---|---|---|---|---|---|
| Ty Johnson | 30 | 14 | 46.7 | 35.5 | 24 | 16 | 66.7 | 69.2 | **24.5** |
| Leonard Fournette | 26 | 11 | 42.3 | 32.0 | 29 | 21 | 72.4 | 73.1 | **23.4** |
| Devonta Freeman | 22 | 9 | 40.9 | 30.3 | 9 | 6 | 66.7 | 71.1 | **21.6** |
| Chuba Hubbard | 39 | 15 | 38.5 | 31.8 | 23 | 14 | 60.9 | 65.2 | **20.7** |
| Carlos Hyde | 24 | 8 | 33.3 | 26.7 | 11 | 8 | 72.7 | 73.9 | **19.7** |
| Antonio Gibson | 24 | 9 | 37.5 | 29.0 | 15 | 9 | 60.0 | 66.1 | **19.1** |
| Najee Harris | 44 | 12 | 27.3 | 24.6 | 43 | 33 | 76.7 | 76.4 | **18.8** |
| Javonte Williams | 38 | 9 | 23.7 | 22.0 | 18 | 16 | 88.9 | 84.0 | **18.4** |
| Brandon Bolden | 24 | 6 | 25.0 | 22.1 | 14 | 12 | 85.7 | 81.3 | **18.0** |
| D'Andre Swift | 75 | 18 | 24.0 | 22.9 | 47 | 36 | 76.6 | 76.3 | **17.5** |

Context check (90° prototype): a logistic model of availability on coverage, rushers, down and distance, formation, dropback type, play action and time to pressure (AUC 0.68, 5-fold) gives an "availability over expected" whose top 10 is identical to the raw-rate top 10, so the ranking is not a product of easy situations.

**Offenses:** all 32 teams have 37+ pressured RB route plays (median 70); availability ranges from 8.1 % to 35.5 % (120° rule).

## How to read the rankings
- **RB season ranking (coach 1c, broadcaster):** **indicative** (20+ plays per RB over 8 weeks), not a grade. Use it to choose whose film to watch, e.g. an RB who is often available but rarely targeted.
- **Offense ranking (coach 1c):** availability per team (37+ plays each, median 70) is more stable and partly reflects play design (route assignments, protection rules).
- **Per-game RB table (coach 1b):** counts, not a ranking.

## Known biases — must be shown in the deliverable
- **Selection:** teams keep the RB in to block when they expect pressure. Raw first look (plays with exactly one RB/FB): when the RB blocks, PFF pressure is higher (Man 47 % vs. 39 %, Zone 43 % vs. 35 %) and so is the sack rate. Never conclude that blocking or releasing *causes* fewer sacks.
- **Association, not causation:** an available RB may also mean a coverage that left space everywhere. Compare inside coverage family and blitz strata before any claim.
- **Proxy pressure:** 2 yd from the QB is a proxy (80 % precision vs. PFF); a defender can be close while still engaged with a blocker.
- **Orientation** is body orientation, not where the RB is looking; the 120° rule is a coarse "QB within his field of view" filter, reported with the 90–135° and no-rule variants.
- **Target matching** by last name + first-name prefix can still miss suffixes or name changes; unmatched plays are counted as "not targeted" in the prototype and must be flagged in the clean version.
- **Catch rate** includes QB accuracy and easy designed passes (screens); it is shrunk toward the league rate and only half of the score.
- **Small samples per RB;** nearest defender is not the assigned defender; 8 weeks of one season.

## Method (rules + simple statistics, no black box)
1. One row per pressured play with an RB route runner: pressure frame, the five conditions, outcome, parsed target.
2. League comparison available vs. not available: sack rate, target rate, completion, with bootstrap intervals **resampling plays**.
3. Strata check: repeat inside Man / Zone and blitz (≥ 5 rushers) vs. not.
4. Player and team rates with shrinkage toward the league mean (k = 20) and minimum n = 20.
5. Sensitivity: pressure radius 1.5 / 2 / 2.5 yd, openness 2 / 2.5 / 3 yd, range 12 / 15 / 18 yd, orientation 90° / 120° / none, shrinkage k = 10 / 20 / 40.

## Open decisions (team to confirm)
- Range: 15 yd (default) vs. 12 yd (stricter check-down, larger sack gap on fewer plays).
- Orientation: 120° (default, more plays) vs. 90° (cleaner interval, gap 5.1 ± 4.1 pts).
- Minimum n for the RB ranking: 20 (48 RBs, default) vs. 15 (61 RBs) vs. 30 (33 RBs). The conditions change the numerator only; the per-RB sample is the number of pressured route plays.
- Count FB with RB (default) or RB only.
- nflverse join to cross-check targets (allowed as free public data; confirm network and rules).
- Hosting of the static site (local demo vs. public static host): confirm with the event rules.

**Out of the POC scope (only if time remains):** per-play broadcast sentence ("Pressure at 2.4 s · RB open (4.1 yd) … → lifeline available"), exported GIF of a play, scout-specific views beyond the season table.

## Definition of done
- Definitions above applied in code with unit tests; prototype numbers reproduced or corrected.
- League comparison with intervals and the strata check.
- RB and team season rankings with n and shrinkage; per-game RB tables with n.
- JSON exports generated by the pipeline and loaded by the site; **no synthetic value left on the site**.
- Coach dashboard: any of the 122 games opens, any dropback play animates from snap to throw/sack with trails, orientation arrows, per-frame green/red RB and the pressure-frame panel.
- Broadcaster dashboard: "Best safety valves" ranking with n, min n = 20, league mean, caption.
- At least 5 plays checked by eye: pressure frame and RB colour in the animation vs. the computed checks (incl. one available → completion and one not available → sack).
- Per-game RB counts summed over all games equal the season n (consistency test).
- Submission README with the limitations from **Known biases**.

## Concrete build plan — functions
**Pipeline (Python):** `load_play_table()`; `normalize_play_direction()`; `find_snap_and_throw_or_sack_frames()`; `line_of_scrimmage()`; `qb_defender_distance()`; `find_pressure_frame()`; `validate_pressure_proxy()`; `rb_checks_at(frame)` (open, in range, past the line, turned toward the QB) applied to **every frame** for the animation colour; `flag_rb_available()` (checks at the pressure frame = play verdict); `parse_target_receiver()`; `outcomes_by_availability()` (with bootstrap); `rb_availability_by_game()`; `catch_rate()`; `lifeline_score()`; `rank_rbs()` and `rank_offenses()` (shrinkage, minimum n); `export_site_data()` (season, games and per-game JSON).

**Website (`website/`):** game picker; play list with badges; `FieldAnimation` (field, players, trails, orientation arrows, per-frame RB colour, pressure marker and checks panel); per-game RB table; season RB + team tables; broadcaster "Best safety valves" page.

**Tests:** synthetic frames for direction normalization, bearing vs. `o` (0° = +y, clockwise), the five checks on hand-built positions, pressure frame when no defender reaches 2 yd, sack plays without a throw, target parser on real descriptions incl. unmatched names, ranking refuses to list an RB below the minimum n, per-frame flag at the pressure frame equals the play verdict, per-game sums equal season totals.

## Who is it useful for, and why
- **Offensive coordinators and RB coaches (coach dashboard):** replay each pressured play of a game and see whether the back was a usable outlet when the pocket broke; follow each RB over the game and the season; compare offenses on how often their check-down design produces an outlet.
- **Scouts and front offices (season table):** which RBs give their QB an escape route under pressure, a third-down skill box scores do not show.
- **Broadcasters (broadcaster dashboard):** a ready, verified "Best safety valves" ranking to quote on air, with n.

## Novelty caveat
Hypothesis, not a proven original idea. BDB 2023 centered on pass rush and protection, where the RB is studied as a blocker; the angle here is the RB as the **receiving outlet at the moment of pressure**. Check existing BDB 2023 notebooks and Next Gen Stats before claiming novelty.
