# Jadu — Agent Guide

## What this project is

Jadu itself — the five workflow skills in this repo (`jadu-zad`, `jadu-bidar`, `jadu-kar`,
`jadu-payan`, `jadu-push`). This project manages itself using its own workflows.

## Tools & setup

Plain Markdown files only: `.claude/commands/*.md` for Claude Code, `.codex/skills/*/SKILL.md`
for Codex. No build step, no dependencies.

## Key commands / workflows

- `jadu-zad` / `/jadu-zad` — set up or refresh this repo's own context files
- `jadu-bidar` / `/jadu-bidar` — start a session on this repo
- `jadu-kar` / `/jadu-kar` — manage `TASKS.md`
- `jadu-payan` / `/jadu-payan` — close a session, update `WORKLOG.md`/`TASKS.md`
- `jadu-push` / `/jadu-push` — commit and push, only when asked

## Conventions agents should follow

1. First define the task with the user.
2. Then refine the task and subtasks together.
3. Then confirm the exact intended path, scope, and implementation plan.
4. Start coding or changing implementation files only after the user explicitly gives permission.
5. A plain `go` approves the currently stated next step; `go with 1, 2, and 3` approves that full sequence. Once approved, complete it without asking again — pause only for a genuine ambiguity or blocker.
6. Do not make decisions on the user's behalf. When something is ambiguous, ask.
7. Never run `git push` unless the user explicitly asks.
8. Whenever a Claude Code command changes behavior, mirror the same change into its Codex counterpart in the same turn — the two must never drift apart.
9. When `jadu-payan` or `jadu-push` do push, stage only the files that session actually touched (never `git add -A`), and fetch + attempt a fast-forward pull immediately before pushing — report and stop on real divergence rather than forcing or auto-merging.

## Things agents should never do in this project

- Never assume a hub/multi-project registry structure — this repo is deliberately a
  single, standalone project. If someone wants a monorepo-of-projects variant, that's a
  fork/extension, not a change to the base skills here.
- Never add a 60-minute reminder variant.
- Never push without an explicit ask.
- Never stage with `git add -A` in `jadu-payan` or `jadu-push` — session-touched files only.
