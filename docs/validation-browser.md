# Delivery and browser verification

Executed locally on 2026-10-21 against the actual supplied tracking exports. This is execution evidence, not a claim that a fresh clone, public deployment or human analyst review was performed.

## Publication and static delivery

`npm run build -- --base=/checkdown/` passed. Its preparation step ran Python schema/integrity validation **and current source fingerprint verification**, then copied the selected generation, including game trajectories, into `website/public/data` and `website/dist/data`.

- Generation: `3a999d342ff04d23bcd5f333e2bb4837`.
- 122 matches, 8,557 dropbacks, 8,533 replayable; 2,751 detected-pressure plays.
- 9,124 RB/FB observations, 6,834 excluded observations (non-opportunities are excluded too; this is not a missing-data count).
- Vite compiled 1,582 modules. Exported resources total approximately 513 MB; game bundles load on coach match selection rather than being embedded in JavaScript.

A static Vite preview served the production build at `http://127.0.0.1:4173/checkdown/`. The entire browser suite used that prefix, covering asset URLs, manifest/resources and lazy-loaded trajectories. The final local `dist` is rebuilt with the default `/` base for ordinary `npm run preview` use, without repeating unchanged numerical calculations.

## Executed browser checks

Command: `RB_BROWSER_URL=http://127.0.0.1:4173/checkdown/ npm run test:browser`.

**11 passed, zero skipped, 11.1 seconds.** Tests live in [product.spec.js](../website/tests/browser/product.spec.js).

1. Choose a real match/dropback, render SVG positions, play from snap, automatically pause at the exact exported pressure frame, resume beyond pressure, seek back and display the five-condition table.
2. Follow a match RB's evidence to its filtered play list, remove the filter, then restore/remove it with browser back/forward.
3. Read a real scout row's published rank and n, filter its team and verify every displayed cell stays unchanged.
4. Open broadcaster directly: render the season table, request no `game_*.json` bundle and expose no replay slider.
5. Reject an absent match from a URL and recover to the catalogue.
6. A 404 manifest produces an explicit publication-absent error.
7. An unsupported schema produces an incompatibility error.
8. A season table with a different generation produces a mixed-generation error.
9. An aborted manifest request produces an explicit network error.
10. At 390 × 844 pixels, activate the pressure control with Enter, inspect the textual positions alternative, and verify no horizontal page overflow.
11. Capture five real plays from match `2021090900`: `4560` (available/completion), `2279` (unavailable/sack), `97` (no pressure), `349` (blocking/left direction), `1368` (multiple backs). Captures use pressure when detected, otherwise snap.

Failure tests intercept only the failing response; successful-path tests use real exports. Screenshots persist locally in `outputs/browser-audit/audit-2021090900-<playId>.png`. Those ignored artifacts can be regenerated; numerical and human visual interpretation are documented in [validation](validation.md).

`npm test` passes the data-client, replay and broadcaster boundary test files. The Python suite passes **63 tests**. `bash -n run` passed, launcher help was exercised, and a missing `RB_DATA_DIR` failed explicitly with the absent manifest path. The launcher performs no silent installation or calculation; `--build-data` prints its cost before starting. Installation failures propagate via shell `set -e` and npm exit status; an intentionally failed installation was not attempted.

## Limits

No pristine-machine/fresh-clone installation was executed. The documented `npm ci` and environment setup describe the reproducible route; these checks used the existing local environment. No public deployment or submission occurred. Browser assertions complement the independent source audit; they do not establish causality or scouting validity. Only Chromium was exercised; other engines and assistive technologies were not manually tested.

## Final current-frame inspection follow-up

Visual inspection led to adding a collapsed **Conditions à l’instant affiché** table, including for no-pressure plays. It displays Python's current-frame checks and leaves the fixed pressure verdict distinct. After this change, `npx vite build` rebuilt the final root-base static client, then `RB_BROWSER_URL=http://127.0.0.1:4173/ npm run test:browser -- --grep 'coach selects|no-pressure replay'` passed both targeted checks (5.2 s). The new test opens real no-pressure play `97`, checks all five rows, advances a frame, verifies the displayed time changes and retains the explicit “non compté” explanation. The root-base preview serves the final client and the unchanged verified full publication.
