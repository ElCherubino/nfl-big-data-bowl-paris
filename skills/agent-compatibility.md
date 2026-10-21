# Agent compatibility and reproducible skills

| Agent surface | Team file location | Caveat |
|---|---|---|
| Kiro IDE/CLI | `.kiro/skills/<name>/SKILL.md` | Supports Agent Skills and import; verify installed version |
| Claude Code | `.claude/skills/<name>/SKILL.md` | Repo skills recognized; requires installed Claude Code and authorization |
| OpenAI agents / Codex | Depending on runtime, `.agents/skills/<name>/SKILL.md` and `AGENTS.md` | Check actual runtime; ChatGPT web is not equivalent to local Codex |
| ChatGPT web | No assumed filesystem auto-discovery | Share context via GitHub connector or attach files; avoid promising auto-loading |

**Proposal:** Maintain a reviewed, licensed central catalog; install into tool-specific paths only when confirmed compatible. Avoid symlinks/platform assumptions for Windows teammates. Pin source revisions and provide verification checks.

**Security:** An SKILL.md is executable guidance to an agent; treat scripts, tool use and prompts as supply-chain risks. Do not run unknown installers with elevated privileges.

**Timing:** Build an installation executable at Step 3 after organizer rules are clarified. Do not author challenge-specific workflows before the event.
