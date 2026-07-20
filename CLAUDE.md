# Jadu — Claude Code Guide

This file is the Claude-specific compatibility guide. All agents should treat `AGENTS.md`
as the shared source of truth first.

## What this project is

Jadu is a public collection of reusable AI-agent workflows for structured project
sessions. Claude Code uses the Markdown slash commands in `.claude/commands/`.

## Claude Code commands

| Command | Purpose |
|---|---|
| `/jadu-bidar` | Start or resume a session, read project context, update planning subtasks. Also manages `TASKS.md` as a live table for the rest of the session (merged from the former `/jadu-kar`), and sets the 30-minute focus reminder on its first invocation each session |
| `/jadu-zad` | Initialize project context files such as `PROJECT.md`, `AGENTS.md`, optional `CLAUDE.md`, and `TASKS.md` |
| `/jadu-kar` | Retired — redirect stub pointing at `/jadu-bidar`, which now handles task management |
| `/jadu-bazgu` | For one specific request: log it as a task, restate it, offer 2–3 options, confirm, then execute |
| `/jadu-payan` | Close a session by writing a session brief and updating project docs; never ends with a question |
| `/jadu-push` | Stage, commit, and push only when the user explicitly invokes it |
| `/jadu-bina` | Optional reviewer loop; a task counts as done when Bina is satisfied, not when the executor says so |

## Conventions Claude should follow

- Read and follow `AGENTS.md` before making changes.
- Keep `.claude/commands/` aligned with `.codex/skills/`.
- Use agent-neutral language unless documenting a Claude-only feature.
- Keep each command self-contained enough to work without hidden conversation context.
- Do not reintroduce 60-minute reminders; Jadu uses only the 30-minute reminder.
- Never push unless the user explicitly asks.

## PR review workflow

Public PRs may be reviewed by Claude. When reviewing:

- Check that the skill is well-structured and follows the existing format.
- Flag anything that could cause unexpected or unsafe behavior.
- Confirm matching Codex skills and user docs were updated when behavior changed.
- Be welcoming and constructive; this is a public, contribution-friendly repo.
