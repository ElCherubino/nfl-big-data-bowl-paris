# AGENTS.md — Start here (humans and AI agents)

> **Official event-day guide and submission constraints:** [EVENT_DAY_CONTEXT.md](EVENT_DAY_CONTEXT.md). Keep all previously prepared files intact; the final entry must be made on-site in a fresh public repository.

This is the **NFL x AWS hackathon preparation repo**, not an already implemented solution.

**Kiro note:** Kiro loads this file into every chat when this folder is the workspace. On event day, open a fresh submission repository in Kiro instead of this one.

## Read in this order
1. [README.md](README.md) — event rules, deliverable and timing.
2. [projects/README.md](projects/README.md) — choose **innovative projects first**, then basic fallbacks. In every idea, read **Data needed** first and SKIP when required data is missing.
3. [functional/README.md](functional/README.md) — NFL rules, role-specific user needs, KPI definitions and data limitations.
4. [skills/README.md](skills/README.md) — which skills exist, which are installed, and when to use them.
5. [presentation_template/README.md](presentation_template/README.md) — required storytelling checklist and *reference-only* editable slide deck.

## What to do

**Presentation compliance:** the PowerPoint template is a data-free rehearsal/reference asset, NOT an official Amazon template or a pre-built submission artifact. Do not reuse it in the judged deliverable unless the organizers explicitly permit prebuilt slides.

**Before official kickoff:** study general tools and publicly available skills; clarify rules; keep ideas as hypotheses. Do **not** write hackathon-specific solution code, notebooks, statistical analyses, visuals, scripts or pre-built competition assets.

**After official kickoff:** read official prompt + permitted tools + actual dataset → check required data for innovative ideas → select a defensible decision-oriented insight → implement one small working algorithm + verified metric + clear visualization → test → prepare submission under the published rules.

## Environment preparation

Run `./prepare_environnement --dry-run` to preview the generic tooling setup, then `./prepare_environnement` (or `--yes` for unattended setup), followed by `./prepare_environnement --check`. See [SETUP.md](SETUP.md). Skill installation is only performed when the developer runs the installer; check actual installed files before invoking one.

## Verify environment after setup

Run `./test_env` to exercise the actual generic Python stack and report AI skill availability; see [TEST_ENV.md](TEST_ENV.md). Do not claim that an AI skill works solely because its SKILL.md file exists; confirm it inside the target assistant.

## Quick skill router — first the capability, then the workflow

**No third-party skills are bundled in this repo.** The installer copies them per machine (e.g. `~/.kiro/skills`); see [skills/README.md](skills/README.md) for the exact upstream links, checks and invocation details, including Kiro specifics.

| What I am doing | Capability / existing candidate |
|---|---|
| Inspect a new dataset or check required columns | **Data exploration (P0)** — Anthropic `explore-data` |
| Compute or test a score, distance or algorithm | **Python data science (P0)** — Pandas/NumPy/pytest + AI Hero `implement`, `tdd` |
| Build a 2D replay, chart or dashboard | **Data visualization (P0)** — Anthropic `data-visualization` |
| Commit, branch or review a PR | **Git workflow (P0)** — AI Hero `pr`, `code-review` |
| Challenge a metric or question its evidence | **Critical reviewer (P0)** — AI Hero `grill-me` + `grilling`; Anthropic `validate-data` |
| Prepare an optional slide deck | **Presentation (P1)** — licensing/source verification still required |
| Add justified model narration/cloud service | **AWS / Bedrock (P2)** — official AWS `amazon-bedrock` |
| Explain verified results to viewers | **Sports commentary (P2)** — custom skill not yet created |

**AI Hero support tools:** `research` (verify documentation), `diagnosing-bugs` (reproduce failures), `handoff` (transfer state), `wizard` (setup when permitted), `ask-matt` (choose workflow). Do not invoke skills that are not actually loaded; `grill-me` needs its `grilling` dependency.

## Operating rules
- Official event instructions override repository planning notes.
- Do not assume unknown dataset columns, infer causation from correlation, or claim an idea is novel without checking published work.
- An optional LLM may explain **verified numerical outputs**; it must never invent the findings.
- Do not pretend to have loaded an uninstalled skill. ChatGPT web does not automatically ingest this repository's local skills.
- Explain and verify any proposed script, dependency, external service or changes to the repository before running them.
