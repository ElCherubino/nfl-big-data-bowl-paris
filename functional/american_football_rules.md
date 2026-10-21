# American football, explained for a software engineer

This is a **beginner-friendly NFL guide**, not an exhaustive rulebook. For disputed or 2026-specific rules, use the [official 2026 NFL rulebook](https://operations.nfl.com/rules-officiating/2026-nfl-rulebook) and [NFL football terminology](https://operations.nfl.com/rules-officiating/nfl-football-basics/football-terms).

## The game in 60 seconds

Two teams alternate **offense** (trying to advance the ball and score) and **defense** (trying to stop them, take possession or limit gains). **11 players per team** are on the field during a standard play. The 100-yard field of play has a **10-yard end zone at each end**; teams attack opposite directions, which can switch across periods and possessions.

The offense usually has **four downs (attempts) to advance 10 yards**, after which it earns a new first down. A play generally begins with a **snap** from the center to the quarterback. The offense may run or throw a forward pass. A play ends when a ball carrier is ruled down, goes out of bounds, a pass is incomplete, a score occurs, etc. On fourth down a team may attempt to convert, punt or try a field goal.

Example: **2nd & 7** means the second down of the current set and 7 yards still needed for a first down. It does **not** mean 7 yards to a touchdown.

## How points are scored

| Event | Points | Meaning |
|---|---:|---|
| Touchdown | 6 | Carry/catch the ball into the opponent's end zone under the applicable rules |
| Extra-point kick | 1 | Successful try after a touchdown |
| Two-point conversion | 2 | Successful run/pass try after a touchdown |
| Field goal | 3 | Kick the ball through the uprights in normal play |
| Safety | 2 | Usually when the defending team causes the ball to become dead in the offense's own end zone under the rules |

The game usually has **four 15-minute quarters**, with clock stoppages and special end-of-half rules. Overtime and try/kickoff details have additional rules; do not rely on this primer for officiating judgments.

## The positions we are most likely to see

| Position | Short name | What they do | Analytics implication |
|---|---|---|---|
| Quarterback | QB | Receives snap; often makes the pass/run decision | Throw timing and target choice depend on context |
| Wide receiver | WR | Runs routes to receive passes | A good route need not result in a catch or target |
| Tight end | TE | May block or run receiving routes | Must distinguish blocking from receiving opportunities |
| Running back | RB | Receives handoffs and may receive passes or block | Rushing and receiving behaviors are different |
| Offensive line | OL | Blocks for QB/runner | Changes available space; cannot be ignored in attribution |
| Cornerback | CB | Typically covers wide receivers | Nearest defender is not always the assigned defender |
| Safety | S | Supports coverage or run defense | Deep positioning can affect apparent openness |
| Linebacker | LB | Supports run defense and pass coverage | May cover TE/RB or patrol zones |
| Defensive line | DL | Pressures quarterback; stops running plays | Pressure can make a nominally open receiver untargetable |

## What happens during a passing play?

1. **Pre-snap:** teams line up; offense may move players.
2. **Snap:** ball is put into play; QB receives it.
3. **Routes and coverage:** eligible players move; defenders cover receivers or zones.
4. **QB decision and throw:** not every open player is a feasible target (timing, pass lane, pressure, progression).
5. **Catch / incomplete / interception:** the outcome changes possession and potential gain.
6. **After catch:** the receiver may advance and defenders attempt to tackle.

**Target** = receiver selected by a pass attempt. **Reception** = completed pass caught. **Route** = path run on a pass play. **YAC** = yards after catch. **Separation** = spatial distance, whose precise definition and measurement time matter.

## Tactical ideas in plain English

- **Man coverage:** defenders primarily match particular offensive players.
- **Zone coverage:** defenders primarily protect areas; real schemes are more nuanced.
- **Blitz / pass rush:** defense sends pressure toward the QB.
- **Motion:** offensive player shifts before snap; can reveal or manipulate defensive reactions.
- **Play action:** passing play initially resembles a run.
- **Route concept:** combination of receiving routes designed to stress a coverage.
- **Blocking:** players protect QB or open rushing lanes.
- **Turnover:** interception, recovered fumble or other possession change.

## Common penalties / misconceptions

- **Offside:** defender is improperly across the neutral zone at snap.
- **False start:** offensive player makes a prohibited abrupt pre-snap movement.
- **Holding:** illegally restraining an opponent.
- **Pass interference:** prohibited contact affecting a catch opportunity under the relevant rules.
- A receiver being unguarded in a frame does **not** prove the quarterback made a mistake.
- A receiver drawing a defender does **not** prove they caused another player to get open.
- Speed or separation alone does **not** equal player quality, and highlights are not a representative sample.

## What tracking data represents

NFL Next Gen Stats collects locations and motion repeatedly, including player position, speed and acceleration. Its production system can collect **10 observations per second**, but **the hackathon's released dataset may be a subset** with different columns or event availability. Align plays, player IDs, timestamps and attacking direction before interpreting trajectories. The participant guide confirms x/y for the 22 players at 10 frames per second, plus PFF scouting data.

Source: https://operations.nfl.com/gameday/technology/nfl-next-gen-stats
