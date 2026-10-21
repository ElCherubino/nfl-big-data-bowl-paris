# TE Block or Release

**One-line goal:** for every pass play, show how much more (or less) open the wide receivers were *when the tight end released into a route instead of blocking*, compared with similar plays; how much time and pressure the QB had; and whether the outcome matched what similar plays usually produce. The trade-off being measured: **TE in = more time for the QB, TE out = more space for the WRs?** The same per-play output feeds a **coach dashboard** (game review, play by play) and a **broadcast card** (one sentence during a replay).

## Data check — PASSED on the supplied dataset (verified 2026-10-21)
Dataset: NFL Big Data Bowl 2023, expected locally at `nfl-big-data-bowl-regional-event-data/data/` (≈ 834 MB, **not committed to this repo**; each teammate copies it there): 2021 season, weeks 1–8, 122 games, 8,557 **dropback plays only** (passes, sacks, scrambles; no designed runs).

| Need | Source | Status |
|---|---|---|
| TE status per play | `pffScoutingData.pff_role` (`Pass Block` / `Pass Route`) + `pff_blockType` | ✅ direct label, no inference needed |
| WR and defender positions per frame | `tracking_[gameId].csv` (10 Hz, 22 players + ball) | ✅ until ~0.5 s after the throw |
| Snap / throw / sack frames | `event` (`ball_snap`, `autoevent_ballsnap`, `pass_forward`, `autoevent_passforward`, `qb_sack`, `qb_strip_sack`, `run` for scrambles) | ✅ |
| QB pressure | `pff_hit`, `pff_hurry`, `pff_sack` on rushers + rusher–QB distance from tracking | ✅ |
| Coverage and defensive call | `pff_passCoverage`, `pff_passCoverageType`, number of `Pass Rush` players, `defendersInBox`, `personnelD` | ✅ |
| Outcome | `passResult`, `playResult`, `yardsToGo` | ✅ play level only |
| Targeted receiver | only inside `playDescription` text ("pass short right to C.Kupp") | ⚠️ must be parsed and matched |
| Catch, ball in the air, YAC | — | ❌ tracking stops at throw + ~5 frames |
| EPA / win probability | not supplied; joinable from nflverse (`old_game_id`, `play_id`) | ⚠️ only if the event rules and network allow it |

**Verified counts (play level, rule defined below):** release 6,057 · block 1,195 · chip-and-release 1,037 · no TE 268. Plays with 2+ TEs: 1,944. Blocking-TE plays per offense over 8 weeks: median 35 (min 12, max 63), so **≈ 4–5 per game**.

## Definitions (fixed before the adjusted results are computed)

### TE status
TE = `players.officialPosition == "TE"`. Per TE on a play (from `pffScoutingData`):
- **block** — `pff_role == "Pass Block"`.
- **chip_release** — `pff_role == "Pass Route"` and `pff_blockType` present and not `NB` (mostly `CH` chip, `SR` set-and-release).
- **release** — `pff_role == "Pass Route"` with no block.

Play-level status: `block` if any TE blocks; else `chip_release` if any TE chips; else `release`; `no_te` if no TE is on the field (reference group only). Chip-and-release stays its **own category** and is never merged into either side.

### WR separation (the core measure)
- Receivers measured: players with `officialPosition == "WR"` and `pff_role == "Pass Route"`. The TE and RBs are not counted in the "WR separation" figure (the TE's own separation can be shown separately).
- Separation = distance from the WR to the **nearest defender** (any defensive player), in yards, after normalizing play direction.
- **Primary moment: snap + 2.5 s** (frame snap + 25), or the throw/sack frame if earlier. This removes the effect of *when* the QB throws. **Secondary moment: the throw frame** (no throw on sacks → fixed time only).
- Play-level values: **mean WR separation** and **best WR separation** (the most open WR = the best option available).

### QB pressure
Two complementary measures, both shown:
- **PFF pressure (play level):** any defender credited with hit, hurry or sack → pressured. It covers the whole play, not a single moment.
- **Tracking pressure at the throw:** distance from the nearest `Pass Rush` defender to the QB at the throw (or sack) frame. Turned into a **low / medium / high** level with distance thresholds (starting values: > 3 yd / 1.5–3 yd / < 1.5 yd), calibrated against the PFF labels.

### QB time (how much time the TE choice buys or costs)
- **Time to throw** = (first `pass_forward`/`autoevent_passforward`, `qb_sack`/`qb_strip_sack` or `run` frame − first `ball_snap`/`autoevent_ballsnap` frame) / 10, in seconds. Available for 8,533 / 8,557 plays (verified). It mixes protection **and** QB decision / route depth (longer routes on play action are held longer).
- **Time to pressure** (cleaner measure of the time the protection gave) = first frame after the snap where a `Pass Rush` defender is within the pressure radius of the QB (starting value: 2 yd), in seconds. Plays where this never happens before the throw are **censored** ("no pressure before the throw"), never dropped or set to zero.
- **TE time effect** = difference in time to throw and in time to pressure between `block` and `release`, inside the same strata as separation (play action is mandatory). Reported as "+x s for the QB when the TE stays in, on similar plays", with n and bootstrap interval; time to pressure compared with a survival curve (Kaplan–Meier) because of the censored plays.
- Raw, unadjusted first look (2026-10-21, for orientation only): mean time to throw 3.47 s with the TE blocking vs. 2.98 s releasing; within non-play-action 3.14 vs. 2.91 s; within play action 3.58 vs. 3.46 s. The adjusted values and intervals are the ones to report.

### Defensive and offensive context (comparison strata)
- Defense: coverage family (`pff_passCoverageType`: Man / Zone / Other), coverage scheme (`pff_passCoverage`), **blitz** (≥ 5 pass rushers), defenders in the box.
- Offense: **play action** (`pff_playAction`), dropback type, down and distance bucket, field zone (red zone), number of route runners.

## Per-play outputs (what the dashboard shows for each play)
1. **Observed WR separation** (mean and best, at 2.5 s and at the throw).
2. **Expected WR separation** for the same context, with the actual TE status and with the other status, both learned from all league plays.
3. **TE release effect** = expected separation with the actual status − expected separation with the other status, in **yards** and in **%** of the other status' expected value. Example: "TE released: WRs +0.5 yd (+18 %) vs. similar plays where the TE stays in."
4. **Play vs. expectation** = observed − expected (with the actual status): did this play open up more or less than usual?
5. **QB pressure level** (low / medium / high), PFF pressure flag, **time to throw and time to pressure**, compared with the expected value for similar plays with the other TE status ("QB had 0.3 s more / less than on similar plays with the TE out").
6. **Outcome checks** (see below).

> **Interpretation rule.** On a single play only one TE status is observed; the other one is a **counterfactual estimated from similar plays**, not a measurement. Every number is worded "compared with similar plays", never "the TE created X yards". Associations, not causation.

## Outcome analysis — "was the result the best one?"
**Observed outcome per play (available):** `passResult` — `C` complete (4,620), `I` incomplete (2,755), `S` sack (543), `R` QB scramble (449), `IN` interception (190); `playResult` net yards (incl. penalties; `prePenaltyPlayResult` without); first down = `playResult ≥ yardsToGo`; touchdown can be read from `playDescription`. Not available: who caught it from tracking, ball flight, yards after catch.

What happens on the same play with the other TE choice cannot be observed, and the tracking stops at the throw. So "best outcome" is replaced by two checks that the data can support:
1. **Target choice:** was the targeted receiver (parsed from `playDescription`, matched to `nflId` via abbreviated name + offense team; unmatched plays flagged, never guessed) the **most open option at the throw**? Show the gap in yards to the most open receiver.
2. **Decision context:** in this context (coverage family × blitz × play action × down bucket), what did similar plays produce with the TE blocking vs. releasing: completion rate, yards (`playResult`), first-down rate (`playResult ≥ yardsToGo`), sack rate, pressure rate, each with **n and a bootstrap interval**? A verdict ("releasing usually pays off here") is shown only when the interval excludes zero and both groups reach the minimum n; otherwise "no clear difference".

League-level output: outcome and pressure differences between the TE statuses, overall and by coverage family, blitz and play action, with intervals.

## Known biases — measured on the data, must be shown in the deliverable
- **Play action dominates the blocking group:** 75 % of `block` plays are play action (898 / 1,195) vs. 12 % of `release` plays (743 / 6,057). The raw yard gain is higher when the TE blocks (8.2 vs. 6.2 yd per play), very likely because of play-action shots rather than the block itself. **Play action is a mandatory stratum.** Show raw and adjusted figures side by side.
- **Blitz:** 37 % of `block` plays face ≥ 5 rushers vs. 23 % of `release` plays.
- **Chip-and-release** has the highest pressure rate (41 % vs. ~36 %): chips are called when protection is expected to struggle.
- **Pressure is a consequence, not a context.** The TE choice changes pressure, so separation is **not adjusted for pressure**; pressure is reported alongside.
- **Mechanical effect:** a blocking TE means one route runner fewer per coverage defender. Report route runners vs. coverage defenders so the effect is not read as "TE gravity".
- **Small samples:** ~35 blocking plays per team over 8 weeks. Expected values come from **league-wide** models; team-level effects are shown overall only (with n and a minimum), **never per team × coverage**. Rare coverages (Cover-0: 51 blocking plays league-wide, Bracket, Goal Line, Prevent) are pooled or excluded.
- Nearest defender is not the assigned defender. 8 weeks of one season do not generalize to other seasons.

## Method (rules + simple statistics, no black box)
1. Build one row per play with TE status, context, WR separation, pressure and outcome.
2. **Expected separation model:** linear regression `sep ~ te_status × coverage_family + blitz + play_action + down_bucket + n_route_runners` on all plays; stratum means with shrinkage toward the league mean as a cross-check. Fit with plays from other games than the one displayed (leave-one-game-out) so a play does not predict itself.
3. Per-play effect = prediction with the actual status − prediction with the other status (block ↔ release; chip_release compared with both).
4. Intervals: bootstrap **resampling plays** (not WR-frames).
5. Sensitivity: fixed time 2.0 / 2.5 / 3.0 s, pressure thresholds ± 0.5 yd, with and without 2+ TE plays.
6. **Minimum sample:** no effect, verdict or broadcast claim is shown when a compared group has fewer than **30 plays** (starting value; report how results change at 20 / 50).

## Open decisions (team to confirm)
- **nflverse join for EPA / target receiver:** allowed by the brief ("free public external data may be added"); confirm against the official rules and venue network before using it. Without it, the target comes from `playDescription` parsing.
- **Chip-and-release:** kept as a third category (default). Alternative: exclude it from the block vs. release comparison.
- **Thresholds:** fixed time 2.5 s, pressure radius 2 yd, pressure levels 1.5 / 3 yd, minimum n = 30 are starting values to be confirmed by the sensitivity checks, not tuned to get a nicer result.

## Deliverables
### Coach dashboard (game review)
- Team + game selector → **play-by-play table**: quarter, clock, down & distance, coverage, blitz, play action, TE status, observed vs. expected WR separation, TE release effect (yd / %), pressure level, outcome, "threw to the most open WR?" flag.
- Click a play → **2D replay** from snap to throw: WR separation bubbles, TE path highlighted, pressure ring around the QB, nearest defender to the TE highlighted.
- Summary panel: league-wide TE release effect by coverage family / blitz / play action, and the team's overall effect, with n and intervals.

### Broadcast card (single play, during the replay)
- One generated sentence built **only from computed numbers**, for example: "TE released · WRs +18 % more open than on similar plays with the TE in · QB pressure: high (rusher 1.2 yd away at the throw)."
- Shown only when the comparable-play sample reaches the minimum and the interval excludes zero; otherwise no claim.
- An optional LLM (e.g. Amazon Bedrock) may rephrase the sentence; it receives only the computed values and must not add causes or facts.
- Limit: this dataset is post-game. Live use would need a real-time tracking feed; in the hackathon it is a **demo on recorded plays**.

## Definition of done
- Written definitions above applied in code with unit tests.
- Play-level table for all 8,557 plays with TE status, separation, pressure, outcome.
- League-wide TE release effect with raw vs. adjusted values, n and bootstrap intervals; outcome and pressure comparison by status and context.
- Working dashboard (game → play table → replay) and broadcast card for at least one verified play.
- At least 5 plays checked by eye (TE status label vs. drawn TE path, separation numbers vs. replay).
- Submission README with the limitations listed in **Known biases**.

## Concrete build plan — functions
`load_play_table()`; `normalize_play_direction()`; `find_snap_and_throw_or_sack_frames()`; `label_te_status()`; `wr_separation_at(frame)`; `play_wr_separation()` (mean + best, 2.5 s + throw); `qb_pressure()` (PFF flag + rusher distance + level); `time_to_throw()`; `time_to_pressure()` (with censoring flag); `te_time_effect()`; `defensive_context()`; `parse_target_receiver()`; `fit_expected_separation()` (leave-one-game-out); `te_release_effect()`; `outcome_by_status()` (with bootstrap); `count_route_runners_vs_coverage()`; `render_play_replay()`; `broadcast_sentence()`; dashboard app.

**Tests:** synthetic frames for direction normalization, frame selection (2.5 s vs. earlier throw, sack without throw) and nearest-defender distance; time to throw with `autoevent_*` fallbacks and missing snap; time to pressure censored when no rusher reaches the radius; TE status rule on hand-built scouting rows (block / chip / release / multi-TE / no TE); target parser on real descriptions incl. unmatched names; bootstrap resampling unit = play; broadcast sentence refuses to print below the minimum n.

## Who is it useful for, and why
- **Offensive coordinators and TE/WR coaches:** what a max-protect call costs the receivers and what it buys the QB, per coverage and blitz look, on their own games.
- **Scouts:** a TE's indirect receiving value (space created for the WRs), beyond targets and catches.
- **Broadcasters:** a verified one-line explanation of why a WR was wide open.

## Novelty caveat
Hypothesis, not a proven original idea. BDB 2023 centered on pass protection, so TE blocking roles have been studied; the angle here is the **link between TE release and WR separation** plus the per-play counterfactual. Check existing BDB 2023 notebooks and Next Gen Stats before claiming novelty. Overlaps with [The Invisible MVP](invisible_mvp.md) and [Race Against Pressure](race_against_pressure.md).
