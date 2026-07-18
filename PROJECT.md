# Jadu

> Five small AI-agent workflow skills — session start, task management, session end,
> and explicit push — that work identically in Claude Code and Codex.

## Overview

Jadu structures a coding session into a repeatable loop: initialize a project's context
once (Zad), start each session with fresh context and a focus reminder (Bidar), manage
tasks conversationally (Kar), close with a written brief and updated docs (Payan), and
push only when explicitly asked (Push). Public, MIT-licensed, forked and generalized from
[25mordad/Jadu](https://github.com/25mordad/Jadu).

## Setup & Tools

| What | Details |
|---|---|
| Format | Plain Markdown — `.claude/commands/*.md`, `.codex/skills/*/SKILL.md` |
| Dependencies | None required; `ffmpeg`/`ffplay` optional for the 30-min sound alert |
| Distribution | GitHub, public repo |

## Team

| Name | Role |
|---|---|
| Mohsen Zarei | Maintainer |

## Timeline

| Milestone | Target Date |
|---|---|
| Generalized from private hub-customized version | 2026-07-14 |
| First public release — live at [github.com/photomohsen/Jadu](https://github.com/photomohsen/Jadu) | 2026-07-14 |
| Converged with the private hub version: precise git staging (no `git add -A`), pre-push fetch+ff-only safety, `TASKS.md` archiving, numbered task index in Kar, universal status icons in every skill's reports | 2026-07-18 |

## Conventions

See `AGENTS.md` for the full agent rulebook. In short: plan before implementing, ask when
ambiguous, never push without being asked, keep Claude Code and Codex versions identical.

## Notes

- This repo intentionally does **not** assume a multi-project hub/monorepo structure —
  every skill operates on the current project root directly, matching the original
  upstream Jadu's simplicity. A hub-aware variant is a fork, not a base feature.
- The private version this was generalized from lives in a separate personal hub repo and
  keeps its own hub-specific customizations (project registry, subprojects, auto-push on
  Payan) — those are deliberately not carried over here.

---
_Initialized: 2026-07-14_
