# CHECKDOWN · RB Lifeline

A local website for coaches, scouts and reporters reviewing NFL running backs under pressure. Coaches choose a match and replay the observed positions; scouts trace season rankings back to match evidence; reporters use the season-only leaderboard and copy a sourced, qualified statement. The analysis covers the supplied 2021 weeks 1–8 tracking files, without an AWS key.

The geometric proxy asks whether a routing RB/FB was open, within QB range, sufficiently past the snap line and facing the QB at the first detected pressure. Python calculates every flag and statistic; React displays the exported results. [Method and validation](docs/validation.md) distinguish calculated evidence from unperformed checks.

## Reproduce locally

Requires Git, Python 3.11+, Node >=22.12, npm and enough disk space for the source CSVs and derived trajectories.

```bash
git clone --recurse-submodules <repository-url>
cd nfl-big-data-bowl-paris
# For an existing clone:
git submodule update --init --recursive
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

Expected sources in `nfl-data/nfl-big-data-bowl-regional-event-data/data/`: `games.csv`, `plays.csv`, `players.csv`, `pffScoutingData.csv` and one `tracking/tracking_<gameId>.csv` file per match. The supplied release contains 122 tracking files. If missing, initialize the submodule and check the supplied event-data access instructions; no synthetic data substitutes for absent inputs.

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

Développement RB Lifeline : [spécifications](spec/README.md), [architecture et contrats](adr/README.md), [répartition de l’implémentation](adr/IMPLEMENTATION.md).

[Repository instructions](AGENTS.md) describe the separate event submission requirements. Official organizer rules remain authoritative for submission, prebuilt assets and sharing. The website is locally reproducible; publication and submission are separate actions.
