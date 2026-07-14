# Worklog

## 2026-07-14 — Generalized from the private hub-customized Jadu

### What we built

| Feature | Files |
|---|---|
| Generic single-project versions of all 5 skills (Zad/Bidar/Kar/Payan/Push) | `.claude/commands/jadu-*.md`, `.codex/skills/jadu-*/SKILL.md` |
| README with install instructions and a copy-paste agent prompt | `README.md` |
| MIT license, self-hosted context files (dogfooding Jadu on itself) | `LICENSE`, `PROJECT.md`, `AGENTS.md`, `TASKS.md` |

### Decisions

#### 1. Strip the hub-specific project registry logic
**Why:** the source version (in a private personal hub) resolves a target project via a
`PROJECTS.md` registry, subproject columns, and hub-root doc reads — all specific to that
one hub's layout. A public tool aimed at anyone should match upstream Jadu's simplicity:
operate on the current project root, no registry required.
**How:** removed all "resolve the target project" steps; every skill now reads/writes
directly at the project root (`TASKS.md`, `WORKLOG.md`, `AGENTS.md`, etc.).

#### 2. Keep Payan and Push separate (don't carry over "Payan always pushes")
**Why:** the private hub had Payan auto-push as a deliberate personal exception. For a
public default, the safer and more predictable behavior — and the one that matches
upstream — is that nothing ever pushes without an explicit ask.
**How:** Payan's steps stop at doc/task updates; README documents how to merge them back
in as a customization if someone wants that.

#### 3. Match upstream's way of working, not the private hub's
**Why:** the goal is a faithful public generalization — same working method as
`25mordad/Jadu`, only the private hub topology removed. So Push uses upstream's simple
`git add -A` (not the hub's session-scoped staging, which only matters in a shared
multi-project repo), and Payan writes docs but never pushes.
**How:** reverted Push to `git add -A`; kept the generic, non-hub-specific niceties only
(structured `TASKS.md`/`WORKLOG.md` formats, `go`/`go with 1,2,3` approval wording).
Added the 3 structural files upstream ships that the first draft missed: `.gitignore`,
`CLAUDE.md`, `sounds/30.mp3` (already present). `README.fa.md` deferred.

### Pending / TODO

- [ ] Create and push the actual public GitHub repo (see TASKS.md)
- [ ] Dry-run the copy-paste install prompt in a fresh Claude Code and Codex session

---
