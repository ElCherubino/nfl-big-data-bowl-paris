# CHECKDOWN · RB Lifeline

**RB Lifeline** helps an offensive coach answer one question: when pressure reaches my quarterback (QB), is my running back (RB) there as an outlet? The coach dashboard replays dropback plays in 2D, shows frame by frame whether a routing RB/FB is open, within QB range, sufficiently past the line and facing the QB, and summarizes availability so staff can choose which plays and protections to review on film. Scouts use the season tables to identify backs worth reviewing; broadcasters use the season-only “Best safety valves” ranking.

The updated [project description](rb_lifeline.md) specifies a 120° orientation rule and a **Lifeline score** combining availability under pressure with receiving reliability. The current implementation still defaults to 90° and ranks regularized availability; those newer requirements remain to be integrated. Read the parameters in each publication to identify the rules behind its results.

A local website for coaches, scouts and reporters reviewing NFL running backs under pressure. Coaches choose a match and replay the observed positions; scouts trace season rankings back to match evidence; reporters use the season-only leaderboard and copy a sourced, qualified statement. The analysis covers the supplied 2021 weeks 1–8 tracking files, without an AWS key.

The geometric proxy asks whether a routing RB/FB was open, within QB range, sufficiently past the snap line and facing the QB at the first detected pressure. Python calculates every flag and statistic; React displays the exported results. [Method and validation](docs/validation.md) distinguish calculated evidence from unperformed checks.

## Reproduce locally

Requires Git, Python 3.11+, Node >=22.12, npm and enough disk space for the source CSVs and derived trajectories.

```bash
git clone <repository-url>
cd nfl-big-data-bowl-paris
./prepare_environnement --dry-run
./prepare_environnement --no-skills
./prepare_environnement --check --no-skills
./test_env --no-skills
cd website
npm ci
cd ..
# Explicit costly calculation over the real sources; progress is printed.
./run --build-data
./run --check
./run
```

Open the URL printed by Vite. The default `./run` validates and copies existing exports before launching the final React site. It never silently recalculates tracking or launches the starter Streamlit app. Missing dependencies and invalid/missing publications fail with a corrective command. See [SETUP.md](SETUP.md) for generic tooling and optional AWS support.

The source CSVs are included directly in `nfl-data/data/`: `games.csv`, `plays.csv`, `players.csv`, `pffScoutingData.csv` and 122 `tracking/tracking_<gameId>.csv` files. A normal clone includes them; no submodule initialization is needed. Source: [NFL regional event dataset](https://github.com/ThompsonJamesBliss/nfl-big-data-bowl-regional-event-data). No synthetic data substitutes for absent inputs.

For a faster explicitly limited run, use `RB_DATA_DIR=outputs/one-game ./run --build-data --game-id 2021090900`, then `RB_DATA_DIR=outputs/one-game ./run`. Counts and ranking eligibility reflect that reduced publication; it is not the full league result.

## Verify and compile

```bash
.venv/bin/python -m pytest
cd website
npm test
npm run build
npx playwright install chromium
npm run test:browser
npm run preview
```

`npm run build` validates the selected publication and copies its manifest, tables and observed trajectories into the static build. `RB_DATA_DIR` selects another export folder relative to the repository. A path-prefix build is supported with `npm run build -- --base=/checkdown/`; serve it with `npm run preview -- --base=/checkdown/` and verify with `RB_BROWSER_URL=http://127.0.0.1:4173/checkdown/ npm run test:browser`. Derived exports, environments, browser captures and `dist` are ignored by Git. This repository does not claim a public deployment.

## Interpret carefully

Availability is descriptive, not causal or a talent grade. Backs kept in protection form a selected group. Coverage/blitz controls are limited; pressure is a distance proxy; body orientation differs from gaze; some targets are unknown; samples can be small; the nearest defender is not necessarily the assigned defender. Results cover eight weeks of one historical season and tracking stops shortly after release. Season ranks use a published minimum sample and regularization; team filters retain league ranks and full-period counts.

## Development

RB Lifeline development: [specifications](spec/README.md), [architecture and contracts](adr/README.md), [implementation split](adr/IMPLEMENTATION.md).

[Repository instructions](AGENTS.md) describe the separate event submission requirements. Official organizer rules remain authoritative for submission, prebuilt assets and sharing. The website is locally reproducible; publication and submission are separate actions.
