# Changelog

All notable changes to the public Jadu repo. Newest first. This project uses simple,
date-stamped version tags (no strict semver — it's a docs/skills collection).

## [0.4.0] — 2026-07-15

- **README:** added **Persian** and **Meaning** columns to the workflow table
  (زاد/بیدار/کار/پایان + English meanings; `Zad` = *born*); merged the Claude Code and Codex
  columns into a single **Command** column (`/jadu-…` · `jadu-…`).
- **README:** description now states that **Jadu (جادو) is Persian for "magic."**
- **README:** the copy-paste install prompt is now explicitly **global** — it installs into
  the user-level `~/.claude` / `~/.codex`, not a project-local dir.
- **Bidar & Payan:** adopted 25mordad's rule **"Do NOT ask for confirmation at any step — just
  do it."** Session start and session close run their own steps autonomously. Implementing
  features/code still follows the project's `AGENTS.md` approval rules.
- Added this `CHANGELOG.md` (+ README pointer).

## [0.3.0] — 2026-07-14

- **Payan now commits and pushes** at session close — closing a session is treated as the
  explicit request to push. `jadu-push` remains the manual commit/push path.
- **README:** added first-run onboarding guidance (hub folder, GitHub sign-in, first project);
  clarified GitHub is optional but useful for backup / collaboration / `jadu-push` / syncing
  across devices and agents; removed a machine-specific workspace example.

## [0.2.0] — 2026-07-14

- Added optional `.env.example` as a starter for downstream projects (Jadu itself needs no
  secrets), a `.gitignore` rule excluding `.env` (keeping `.env.example`), and a README note.

## [0.1.0] — 2026-07-14

- **Initial public release** — the five workflow skills (Zad, Bidar, Kar, Payan, Push) for
  both Claude Code (`.claude/commands/`) and Codex (`.codex/skills/`), plus `AGENTS.md`,
  `CLAUDE.md`, `LICENSE` (MIT), `PROJECT.md`, `TASKS.md`, `WORKLOG.md`, and the optional
  `sounds/30.mp3`. Structure and workflow behavior follow the original
  [25mordad/Jadu](https://github.com/25mordad/Jadu) by Bahman.
