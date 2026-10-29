# Jadu — Claude Code Guide

This file is the Claude-specific compatibility guide. All agents should treat `AGENTS.md` as the shared source of truth first.

## What this project is

Jadu is a public collection of reusable AI-agent workflows for structured project sessions. Claude Code uses the Markdown slash commands in `.claude/commands/`.

## Claude Code commands

| Command | Purpose |
|---|---|
| `/jadu-bidar` | Start or resume a session, read project context, and update planning subtasks |
| `/jadu-zad` | Initialize project context files such as `PROJECT.md`, `AGENTS.md`, optional `CLAUDE.md`, and `TASKS.md` |
| `/jadu-payan` | Close a session inline (no brief), update project docs, and commit + push automatically as the final step |
| `/jadu-loop` | Opt-in, off by default. Autonomously execute pre-approved subtasks from a project's `LOOP_TASK.md`, no per-step approval. See `scripts/jadu-loop/README.md` and `docs/jadu-loop-authoring-guide.md` before installing |
| `/jadu-loop-best-practice` | Opt-in, off by default. Same as `/jadu-loop`, but where it would pause for a human it makes the best-practice decision, records it, and continues; hard limits still block. The owner reviews every decision in the PR |
| `/jadu-loop-prepare` | Turns the project's existing tasks (phase files, plan, open follow-ups) into ready task files in `LOOP_TASK_QUEUE/` for `/jadu-loop-best-practice`. Prepares only; runs the loop only on `Start: yes` |

`/jadu-tamam` was renamed to `/jadu-payan`.

## Conventions Claude should follow

- Read and follow `AGENTS.md` before making changes.
- Keep `.claude/commands/` aligned with `.codex/skills/`.
- Use agent-neutral language unless documenting a Claude-only feature.
- Keep each command self-contained enough to work without hidden conversation context.
- Jadu has no focus-reminder or sound-alert feature; do not reintroduce one (no `sounds/*.mp3`) without an explicit new request.
- Never push unless the user explicitly asks, except `/jadu-payan`, which always commits and pushes as its last step by design.

## PR review workflow

Public PRs may be reviewed by Claude. When reviewing:

- Check that the skill is well-structured and follows the existing format
- Flag anything that could cause unexpected or unsafe behavior
- Confirm matching Codex skills and user docs were updated when behavior changed
- Be welcoming and constructive; this is a public, contribution-friendly repo
