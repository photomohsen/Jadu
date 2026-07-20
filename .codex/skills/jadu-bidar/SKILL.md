---
name: jadu-bidar
description: Session-start and task-management workflow for Jadu, merged from the former jadu-bidar + jadu-kar. Use when the user invokes jadu-bidar, starts or resumes a session, or wants to add, update, complete, list, review, or reprioritize tasks in TASKS.md at any point in the session. Reviews the project's TASKS/WORKLOG/AGENTS context, pulls latest changes safely, sets the 30-minute focus reminder on first invocation, expands and manages the task list as a live table, and recommends where to begin without implementing code.
---

# Jadu Bidar - Session Start and Task Home

Merged from the former `jadu-bidar` and `jadu-kar`: starting a session and managing its task
list are now one skill. First call each session does setup; every call, first or not, is
also the place to see and manage the backlog.

**Do NOT ask for confirmation at any step in setup - just do it.** Read context and expand
tasks autonomously. This does not extend to implementing features or code, which still
follows the project's `AGENTS.md` approval rules.

## Workflow

### 0. First-call setup (skip if already done this session)

Get the time:

```bash
date '+%M %H %d %m'
```

Pull latest from remote when safe:

```bash
git remote get-url origin 2>/dev/null
```

If a remote URL is returned, run `git pull --ff-only`. Report what changed or say `already
up to date`. If the pull fails because of local changes, divergence, auth, or network,
report the error and continue.

Read project context, if present: `TASKS.md`, `WORKLOG.md` (last 80 lines), `AGENTS.md`,
`CLAUDE.md`, `PROJECT.md`, `README.md`, `git log --oneline -20`. Skim, but do not deep-read,
2-3 recently modified files that history points at. Do not modify implementation files.

Set the focus reminder: if no 30-minute focus reminder is active yet this session, set one
now - a recurring "30 min - check your focus, review progress" job - if a timer tool is
available. If not, do not fake it; tell the user once to set an external one. If already
active this session, skip silently - never stack a second one.

Expand the task list: add useful subtasks to open blocks in `TASKS.md` - logically following
from what is already started, one line each (`- [ ] ...`), dependencies flagged
`<- depends on [name]`. Never create a new top-level task unless the user asked. Never
remove, check off, or re-prioritize existing items. If `TASKS.md` is missing, create it
directly - no need to ask first.

### 1. Every call - the backlog, live

Read `TASKS.md` and render open tasks as a table, always:

| # | Priority | Status | Description |
|---|---|---|---|
| 3 | P1 | 🔄 | Example in-progress task |

Sort by priority then due date. Show subtask completion ratio when useful. Flag overdue
tasks (due date before today). Suggest the single best next action.

Status markers - prefix every top-level task title with one, mirrored in the numbered
index:

- ⬜ **Open** - not started (default)
- 🔄 **Handled** - actively being worked on
- ⚠️ **Needs attention** - blocked, flagged, or awaiting a decision
- ✅ **Done** - complete (block also moves to `## Done`)

Numbered task index - keep one near the top of `TASKS.md` once there are more than a handful
of tasks. Every entry keeps the full title (with marker), status, priority, due date,
completion ratio, and enough context to select without ambiguity - never a shortened label.
Keep numbers stable within a session so the user can say `go with 1 and 3`.

### 2. Ambient task logging

Any prompt in this session that describes real work - not a question, not a read-only
lookup - becomes a task immediately: a new `⬜` top-level task, or a new subtask under an
existing one if it clearly belongs there. This happens without being asked, the moment the
work is described - `TASKS.md` never waits for a later `jadu-payan` to catch up. Read-only
questions and lookups never become tasks.

### 3. Behavior by request

Detect which applies from the user's natural-language request, any time during the session.

Add a task - ask in one message for anything missing (goal, priority P1/P2/P3, due date,
obvious subtasks, blockers), then write it with a `⬜` marker.

Update or complete - match by number or fuzzy match; mark subtasks `[x]`; set the marker to
🔄/⚠️/✅; move fully-complete blocks to `## Done` with a date; confirm with the new marker,
then ask "Anything to add or unblock next?" and stop.

List or review - show the live table (step 1).

Reprioritize - confirm if ambiguous, update in place, re-sort P1 -> P2 -> P3 then by due
date.

### 4. Implementation handoff

Before any implementation begins after planning:

1. Present the complete numbered plan.
2. State each step's exact files, intended result, and verification checks.
3. Ask for explicit approval covering the step or named sequence.
4. A plain `go` approves the currently stated next step; `go with 1, 2, and 3` approves that
   full named sequence.
5. Complete every approved step without re-asking; pause only for genuine ambiguity, a
   blocker, or an unapproved step.

### 5. Report back

Prefix every status line with its marker - `⬜`/`🔄`/`⚠️`/`✅`:

- current time snapshot
- remote pull status
- which context files were found and read
- reminder status (started now, already active, or unavailable)
- new subtasks added, or proposed if approval was required
- one-line suggestion for where to start

## Rules

- Never truncate a numbered explanation into a vague shorthand label.
- Never delete completed history; retain the full block under `## Done`. Archiving past 200
  lines to `TASKS_ARCHIVE.md` is `jadu-payan`'s job, not this one's.
- Keep each task's marker current and identical in the title and the numbered index.
- Flag dependencies inline with `<- depends on [name]`.
- Do not implement feature or code changes here - plan only.
- Obey this project's own `AGENTS.md` approval rules before changing files.
