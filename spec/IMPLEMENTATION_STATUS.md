# Implementation status — 21 October 2026

One dedicated agent was assigned to each spec, in dependency-aware waves with a maximum of three worker agents alongside integration. The root agent integrated the CLI, data client, full real-data build and independent numerical/visual review. No public hosting or event submission was performed.

| Spec / agent | Delivered behavior | Evidence |
| --- | --- | --- |
| 01 / `spec_01` | Validated CSV loading, composite identities, SHA source fingerprint, JSON Schema, atomic generation publication | `tests/test_data.py`, `tests/test_publish.py`; full publication and source validation |
| 02 / `spec_02` | One evaluator for first pressure, normalized coordinates, per-frame checks and fixed observations | `tests/test_metrics.py`; five independently recomputed real plays |
| 03 / `spec_03` | Conservative targets, play-level outcomes, bootstrap intervals, coverage/blitz groups, fourteen threshold variants, pressure-proxy diagnostics | `tests/test_targets.py`, `tests/test_analysis.py`; `analysis.json` and `quality.json` |
| 04 / `spec_04` | Separate player/team references, regularized availability, raw-rate intervals, eligible ranks/percentiles and labelled ranking variants | `tests/test_aggregates.py`; 49 eligible backs and 32 attacks |
| 05 / `spec_05` | SVG observed replay, trails, body orientation, frame states, exact pressure pause/resume and accessible controls | Replay unit tests, real browser animation test and five visually inspected screenshots |
| 06 / `spec_06` | French Coach/Broadcaster shell, match/play selection, three coach views, scout tables, URL/history and explicit data errors | Built-site browser tests, mobile keyboard and stable filtered season values |
| 07 / `spec_07` | League-only broadcaster ranking and deterministic citation from published values; no match bundles or model calls | Broadcaster boundary tests and network-request browser check |
| 08 / `spec_08` | React launcher, validated source-aware preparation, reproducible build/docs and compiled-site browser verification | [Delivery verification](../docs/validation-browser.md) |
| 09 / `spec_09` | Unranked match counts and independently reconstructed player/team conservation; rejection of corrupted publications | `tests/test_game_counts.py`, corruption tests in `tests/test_publish.py` |

Current publication: generation `3a999d342ff04d23bcd5f333e2bb4837`, 122 games and 8,557 retained dropbacks from 2021 weeks 1–8. Of those, 8,533 have replayable event tracking; 24 remain present with explicit diagnostics. Generated JSON and screenshots are ignored artifacts and can be reproduced locally.

See [numerical and visual evidence](../docs/validation.md) and the root [launch instructions](../README.md). A clean-clone execution on a different machine has not been claimed; the current checkout's installation, generation, validation, production compilation and browser path were exercised.
