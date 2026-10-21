# Functional specifications — decision first, data second

> **PRE-EVENT REFERENCE ONLY.** This directory records generic NFL domain knowledge and questions that different audiences might value. It does **not** contain findings, game analysis, an implemented product, or a validated feature specification. The official challenge, allowed tools and released dataset override everything here. Do not copy pre-event specifications or slide materials into a judged submission unless organizers explicitly permit it.

## Start here

1. [American football explained](american_football_rules.md) — understand downs, players and play phases.
2. [Roles and KPI guide](kpi_dictionary.md) — definitions, value and limits.
3. [Data availability gate](data_requirements.md) — inspect what exists **after kickoff**; no assumed column names.
4. Read the audience that actually benefits from your selected insight:
   - [Coaches and opponent analysts](roles/coaches.md)
   - [Scouts and player personnel](roles/scouts_recruitment.md)
   - [Front office and roster decisions](roles/front_office.md)
   - [Reporters and media analysts](roles/reporters.md)
   - [Live commentators and producers](roles/commentators.md)
5. [Generic product behavior and acceptance gates](functional_requirements.md).
6. After kickoff, select a possible project in [../projects/README.md](../projects/README.md), **innovative first**.

## What is our product principle?

**A metric is not a product.** For every proposed feature, be able to say:

> For **[named audience]**, when **[specific decision]** arises, show **[metric and evidence]** so they can **[action]**, with **[limitation]** made visible.

## Roles: first question to answer

| Audience | Decision to support | Most important form of value |
|---|---|---|
| Coaches / tactical analysts | What should we review or adjust in game planning? | Play-specific and repeatable tactical evidence |
| Scouts / player personnel | Who performs a valuable behavior beyond box-score volume? | Context-adjusted player comparison |
| Front office | Who might fit the roster and merit further scouting? | Evidence for a shortlist, **not** a salary recommendation from tracking alone |
| Reporters / editors | What can we publish that is defensible and new? | A fact checked against baseline and sample size |
| Live commentators / producers | What can viewers understand in seconds? | Accurate explanation and clear replay synchronized to a play |

## Ranking features when time is short

Priority order: **(1)** dataset fields exist, **(2)** specific beneficiary, **(3)** metric is interpretable and different from established Next Gen Stats, **(4)** numerical validation, **(5)** one memorable visual, **(6)** optional LLM/AWS. Never reverse this order just to get a spectacular demo.

## Trust rules

- No invented player, team or season findings; placeholder numbers must be clearly hypothetical.
- No causal language for observational spatial association.
- Show numerator, denominator, units, play count, and time reference wherever relevant.
- Distinguish targets and catches from routes/snaps, and association from counterfactual impact.
- Never infer a contract price, medical condition, coverage assignment or QB intent solely from tracking coordinates.
- No commercial claims about data access or real-time availability without evidence.
- NFL source: https://operations.nfl.com/gameday/technology/nfl-next-gen-stats
