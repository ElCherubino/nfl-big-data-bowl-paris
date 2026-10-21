# Live commentators and broadcast producers

## Job to be done
Explain **what just happened** to a broad audience with a simple, visually memorable, accurate football takeaway.

## Highest-value questions / KPIs

| Broadcast question | KPI / evidence | Required data | Why useful |
|---|---|---|---|
| How much separation emerged during the play? | Distance + selected timestamp | Players/defenders + events | Clear visual explanation |
| Who moved where and when? | Annotated trajectories, speeds, timing | Frame-aligned movement | Show behavior viewers missed |
| Why might an untargeted receiver matter? | Apparent space/defender shift **as association** | Multi-player tracks | Adds context beyond the catch |
| Is this moment remarkable? | Ranked context with sample and comparison | Representative history | Avoids exaggerated superlatives |

## Minimum functional behavior
- One replay or chart with **one callout**, readable on screen, with a compact verified number.
- Narration in plain English / French if needed; avoid ungrounded tactical diagnoses.
- Visible event timestamp and play source; no reliance on hidden color-only encodings.
- **Do not imply live low-latency data** unless the contest actually provides live feeds.

## Decision supported
"What useful, accurate thing can I say in the next 10–20 seconds?"

## STOP / skip
If only historical static data is provided, label this **post-play / replay illustration**, not live game detection. Never let an LLM narrate events the algorithm did not establish.

## Done when
A non-expert understands the football insight after one replay, and an expert can audit the metric.
