# Skills — what is available, and when to use it

**Read this file when joining the project or before starting a task.**
[AGENTS.md](../AGENTS.md) explains the overall flow; [projects/README.md](../projects/README.md) lists the hypotheses and required data.

**Important: no third-party skill is bundled in this repository.** The general-purpose [environment installer](../SETUP.md) copies selected public skills into each developer's own user directory when explicitly run and consented to (`./prepare_environnement --yes --agent kiro-cli` installs the 12 P0 skills to `~/.kiro/skills`). Installation is per machine: check your own skill folder rather than assuming a teammate's setup. Review third-party sources before using them. Check what your own agent already exposes before invoking a skill.

## 1. Core capabilities (original P0/P1/P2 list)

| Priority | Need / when to activate | Candidate skill or method | State |
|---|---|---|---|
| **P0** | **Data exploration:** first contact with CSV/Parquet; inspect schema, missing fields, duplicates, coordinate/time issues **before selecting a project** | [Anthropic `explore-data`](https://github.com/anthropics/knowledge-work-plugins/blob/main/data/skills/explore-data/SKILL.md) | Public source; **not installed** |
| **P0** | **Python data science:** compute distances/scores, manipulate frames, test numeric outputs | Python **libraries**: Pandas, NumPy, SciPy, pytest (these are *not* agent skills); AI Hero [`implement`](https://github.com/mattpocock/skills) + [`tdd`](https://github.com/mattpocock/skills) for coding discipline | Libraries to verify in Step 3; workflow skills sourced, **not installed** |
| **P0** | **Data visualization:** after validating metrics, choose an honest chart/2D replay and check readability | [Anthropic `data-visualization`](https://github.com/anthropics/knowledge-work-plugins/blob/main/data/skills/data-visualization/SKILL.md); Plotly/Streamlit are *libraries/frameworks*, not skills | Public source; **not installed** |
| **P0** | **Git workflow:** before branches, commits, PRs or merge/conflict resolution | AI Hero [`pr`](https://github.com/mattpocock/skills) + [`code-review`](https://github.com/mattpocock/skills); Git/GitHub themselves are tools | Public source; **not installed** |
| **P0** | **Critical reviewer:** choosing an idea, checking methodological validity or challenging a dubious metric | AI Hero [`grill-me`](https://github.com/mattpocock/skills) + its `grilling` dependency for decisions; [Anthropic `validate-data`](https://github.com/anthropics/knowledge-work-plugins/blob/main/data/skills/validate-data/SKILL.md) for statistical evidence | Public sources; **not installed** |
| **P1** | **Presentation:** only if a slide deck helps the final demo; prioritize working visualization and submission | [Anthropic `pptx`](https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md) is one existing reference but labeled **proprietary**. The purported *Amazon PowerPoint skill* has **not been identified** | **Not approved for redistribution / not installed** |
| **P2** | **AWS / Bedrock:** only if an actual cloud or LLM feature is justified, accessible, and permitted | [Official AWS `amazon-bedrock`](https://github.com/aws/agent-toolkit-for-aws/blob/main/plugins/aws-core/skills/amazon-bedrock/SKILL.md) | Public source; **not installed** |
| **P2** | **Sports commentary:** when presenting verified results to coaches, broadcasters or reporters | **Potential custom skill**, to be authored **after kickoff if permitted**. No validated existing choice selected | **Not created / not installed** |

**Order during the event:** Data exploration → project data gate → critical review of hypothesis → Python calculation/testing → data visualization → review → optional presentation/Bedrock/commentary. **Don't force an LLM into numerical analysis.**

## 2. AI Hero workflow skills (cross-cutting helpers)

These are *additional workflow skills*, not substitutes for the eight capabilities.

| When | AI Hero skill |
|---|---|
| Idea or scope is vague | [`grill-me`](https://www.aihero.dev/skills-grill-me), which **requires** the underlying `grilling` skill to be present |
| Need reliable source documentation | [`research`](https://github.com/mattpocock/skills) |
| Build a precise small feature **after kickoff** | [`implement`](https://github.com/mattpocock/skills), with underlying `tdd` and `code-review` |
| A test fails | [`diagnosing-bugs`](https://www.aihero.dev/skills-diagnosing-bugs) |
| Change is ready to verify | [`code-review`](https://github.com/mattpocock/skills) |
| Move work to another teammate/agent | [`handoff`](https://github.com/mattpocock/skills) |
| Build an interactive setup wizard, **only when allowed** | [`wizard`](https://github.com/mattpocock/skills) |
| Unsure of which workflow | [`ask-matt`](https://github.com/mattpocock/skills) |

Upstream: [AI Hero / Matt Pocock skills](https://github.com/mattpocock/skills). Skill dependencies and tool behavior must be checked **before** installing; some skills write files, call subagents, or commit automatically.

## 3. How an agent should use this catalog

1. **Identify your task**, then find the matching row in section 1.
2. **Check actual availability** in the active Kiro, Codex, or Claude session. A GitHub URL is not an installed skill. ChatGPT web does not automatically discover repository skill folders.
3. If available and approved, load the appropriate skill with its **documented invocation method**. Some are user commands, others are model-invoked; never invent `/commands`.
4. If unavailable, follow its ordinary documented methodology where permitted, or report it as missing. **Do not claim to have executed the skill.**
5. **Respect event restrictions:** before the official kickoff, no project-specific scripts, code, notebooks, analyses, visualizations, or skills. Installing public generic skills is subject to organizer approval; never run an unreviewed installer.

## 4. Step 3 — environment installer

`./prepare_environnement` now exists; see [SETUP.md](../SETUP.md) for usage, choices, and constraints. It verifies Git, Python and Node; creates a `.venv` and installs core data libraries; offers global public skills, with an optional AWS path. It does **not** install system-wide prerequisites or pin upstream CLI/skill revisions; this remains a follow-up hardening task.

## 5. Using skills in Kiro (verified 20 October 2026)

- **Support:** the Kiro IDE reads Agent Skills (`SKILL.md`) since version 0.9. Global skills live in `~/.kiro/skills/`, workspace skills in `.kiro/skills/` (the workspace copy wins on a name clash). The IDE and `kiro-cli` share the global folder, so the installer's `--agent kiro-cli` target serves the IDE too.
- **Invocation:** automatic when a request matches the skill's description, or manually with `/skill-name` in chat. Kiro panel → *Agent Steering & Skills* → **+** → *Import a skill* also accepts a GitHub URL pointing to a skill subfolder.
- **Caveats with the installed set:** Kiro does not document the Claude-only fields `disable-model-invocation` and `user-invocable`, so manual-only skills (`implement`, `grill-me`, `handoff`) may trigger automatically. `code-review` expects `/setup-matt-pocock-skills` and `tdd` refers to `codebase-design`; neither is installed. `explore-data` links to a `CONNECTORS.md` that is not copied.
- **`AGENTS.md` is always loaded** into every Kiro chat from the workspace root. This repository's `AGENTS.md` describes pre-event rules, so open a fresh submission repository in Kiro on event day.
- **Steering:** `.kiro/steering/*.md` (workspace) or `~/.kiro/steering/` (global), with `inclusion: always | fileMatch | manual | auto`. Write event-specific steering on site only.
- **Notebooks:** the Kiro agent cannot yet edit or run individual notebook cells (open Kiro issue). Prefer `.py` scripts that save PNG/CSV outputs; save a notebook with outputs at the end if useful. Python and Jupyter extensions come from Open VSX (Pylance is unavailable; basedpyright is an alternative). Select `.venv/bin/python` with *Python: Select Interpreter* and in the notebook kernel picker.
- **Credits and models:** each prompt consumes credits; relative cost is Auto 1×, Sonnet 1.3×, Opus 2× or more. The organizers' link gives 1,000 credits; redeem it with the same account used in the IDE. The free tier gives 50 credits per month.

Sources: [Kiro skills](https://kiro.dev/docs/skills/), [steering](https://kiro.dev/docs/steering/), [model selection](https://kiro.dev/docs/chat/model-selection/), [pricing](https://kiro.dev/pricing/), [skills CLI](https://github.com/vercel-labs/skills).

Additional references:
- [Agent compatibility](agent-compatibility.md)
- [Presentation skill research](presentation-skill-research.md)
- [Official Anthropic data plugin (Apache-2.0)](https://github.com/anthropics/knowledge-work-plugins)
- [AWS agent toolkit](https://github.com/aws/agent-toolkit-for-aws)
