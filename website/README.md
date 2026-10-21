# CHECKDOWN web client

React/Vite client for **real Python exports**, useful for coach review, scout shortlists and reporter preparation. No AWS credentials are required. No product fallback supplies demonstration statistics.

From the repository root, initialize source submodules and the Python environment as described in [README](../README.md), then:

```bash
cd website
npm ci
cd ..
./run --build-data  # explicit costly calculation, progress printed
./run --check
./run              # validates/copies exports, starts final React site
```

Node >=22.12 is required. `npm run data` validates and copies the manifest-selected generation from `../outputs/site` to `public/data`, including observed frame trajectories. `RB_DATA_DIR` can choose another real publication relative to the repository root. Validation errors stop the build instead of supplying synthetic results. Python validates schemas, generation references, match-to-season count conservation and current source fingerprints. Historical export generations are not copied.

```bash
npm test                 # data-client, replay and broadcaster boundary tests
npm run build            # validates/copies real exports, then static dist/
npm run preview          # serve the built client including /data/
npm run test:browser     # real exported metrics and actual browser flows
```

Browser tests use installed Chromium (`npx playwright install chromium`). The default config starts Vite on port 4173. To verify a separately served production build, set `RB_BROWSER_URL=http://127.0.0.1:4173/`. For a subpath, compile with `npm run build -- --base=/checkdown/`, preview with `npm run preview -- --base=/checkdown/`, then run tests with `RB_BROWSER_URL=http://127.0.0.1:4173/checkdown/ npm run test:browser`. Requests resolve using Vite’s base prefix; game bundles load on coach selection only.

Coach: match → dropback → dynamic field → automatic pause at first pressure → resume; select a back to compare five published checks, or open match/season tables and follow evidence. Broadcaster: eligible league season ranks and qualified source statements, with no game replay or game-bundle request. Scout: use the season tables to filter identities, teams and sample sizes while retaining published league ranks.

Missing publication, network failures, incompatible schemas and mixed generations show explicit errors. Invalid URL selections can return to the catalogue. SVG markers have textual descriptions, playback is keyboard accessible, and positions/checks have a text alternative. See [validation evidence](../docs/validation.md) for actual results and limits.

The name and styling are an unofficial hackathon project. NFL and team names are third-party marks; verify event sharing rules before public distribution.
