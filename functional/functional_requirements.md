# Generic functional requirements and acceptance gates

**This is an audience-needs reference, not a design ready to submit.** Select requirements only when the official prompt and dataset allow them. No product implementation or solution scaffolding before kickoff.

## FR-01 — Trustworthy input gate (P0)

**As an analyst**, I need to know which requested metrics can be computed from the released files **so I do not present fabricated claims**.

**Accept when:** required fields mapped; missing/partial fields visible; incompatible ideas marked SKIP; units/time alignment understood.

## FR-02 — Select an audience and decision (P0)

**As a user**, I need a clear statement of the football decision supported by the feature.

**Accept when:** one named primary persona; a decision or question; why alternatives/existing NFL metrics don't already solve it; explicit non-goals.

## FR-03 — Metric and proof (P0)

**As a skeptical coach or analyst**, I need a defensible KPI definition and evidence I can check.

**Accept when:** numerator/denominator, units, filters, comparison group, limits and illustrative play references can be explained in plain English. Avoid any metric without sufficient data.

## FR-04 — Traceable visualization (P0)

**As a user**, I need to see *why* a calculated value occurred rather than a decorative plot.

**Accept when:** chart or 2D replay maps correctly to the metric, has labels and readable annotations, can show sample size, and contains no fake data.

## FR-05 — Audience-specific summary (P1)

**As a coach, scout, reporter or commentator**, I need a concise conclusion in my own language.

**Accept when:** wording names possible action, supports it with data, and avoids causal or overstated language. Optional LLM commentary must be generated only from verified computations.

## FR-06 — Export / share (P2)

**As a media or team user**, I may want a shareable view or a short summary.

**Accept when:** exported artifact is permitted and retains definitions, source, timeframe and caveats.

## FR-07 — Reliability and reproducibility (P0)

**As a judge**, I need confidence the demo works on the supplied dataset.

**Accept when:** repository instructions are actionable, core computation can be reproduced, edge cases are handled, and the app can show at least one verified example if the dataset allows.

## Cross-cutting non-functional requirements

- Short response time for a live demo (profile and bound workload; do not claim real-time data availability).
- Accessible labels and color contrasts; 2D visuals should work without proprietary assets.
- No API keys in Git, no unauthorized use of tracking data.
- Unit tests for calculations and coordinate transformations **created during the allowed event window**.
- Don't prioritize speculative GenAI/3D over correctness.
