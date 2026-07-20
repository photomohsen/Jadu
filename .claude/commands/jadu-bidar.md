# Bidar — Session Start & Task Home

Merged with Kar: starting a session and managing its task list are now one command. First
call each session does setup; every call, first or not, is also the place to see and manage
the backlog.

**Do NOT ask for confirmation at any step in setup — just do it.** Read context and expand
tasks autonomously. This does not extend to implementing features or code, which still
follows the project's `AGENTS.md` approval rules.

## Step 1 — First-call setup (skip if already done this session)

1. **Time:** run `date '+%M %H %d %m'`.
2. **Pull:** `git remote get-url origin 2>/dev/null`; if a remote exists,
   `git pull --ff-only`. Report what changed, or "already up to date." If it fails from
   local changes, divergence, auth, or network, report and continue.
3. **Read context**, if present: `TASKS.md`, `WORKLOG.md` (last 80 lines), `AGENTS.md`,
   `CLAUDE.md`, `PROJECT.md`, `README.md`, `git log --oneline -20`. Skim (don't deep-read)
   2–3 recently modified files that history points at. Never modify implementation files
   here.
4. **Reminder:** if no 30-minute focus reminder is active yet this session, set one now (a
   recurring "30 min — check your focus, review progress" job) if a timer tool is
   available; if not, don't fake it — tell the user once to set an external one. If already
   active this session, skip silently — never stack a second one.
5. **Expand the task list:** add useful subtasks to open blocks in `TASKS.md` — logically
   following from what's already started, one line each (`- [ ] ...`), dependencies flagged
   `← depends on [name]`. Never create a new top-level task unless the user asked. Never
   remove, check off, or re-prioritize existing items. If `TASKS.md` is missing, create it
   directly — no need to ask first.

## Step 2 — Every call: the backlog, live

Read `TASKS.md` and render open tasks as a table, always:

| # | Priority | Status | Description |
|---|---|---|---|
| 3 | P1 | 🔄 | Example in-progress task |

Sort by priority then due date. Show subtask completion ratio when useful. Flag overdue
tasks (due date before today). Suggest the single best next action.

### Status markers

Prefix every top-level task title with one marker, mirrored in the numbered index:

- ⬜ **Open** — not started (default)
- 🔄 **Handled** — actively being worked on
- ⚠️ **Needs attention** — blocked, flagged, or awaiting a decision
- ✅ **Done** — complete (block also moves to `## Done`)

### Numbered task index

Keep one near the top of `TASKS.md` once there are more than a handful of tasks. Every entry
keeps the full title (with marker), status, priority, due date, completion ratio, and enough
context to select without ambiguity — never a shortened label. Numbers stay stable within a
session so the user can say `go with 1 and 3`.

## Step 3 — Ambient task logging

Any prompt in this session that describes real work — not a question, not a read-only
lookup — becomes a task immediately: a new `⬜` top-level task, or a new subtask under an
existing one if it clearly belongs there. This happens without being asked, the moment the
work is described — `TASKS.md` never waits for a later `jadu-payan` to catch up. Read-only
questions and lookups never become tasks.

## Behavior by request

Detect which applies from the user's natural-language request, any time during the session:

**Add a task** — ask in one message for anything missing (goal, priority P1/P2/P3, due
date, obvious subtasks, blockers), then write it with a `⬜` marker.

**Update or complete** — match by number or fuzzy match; mark subtasks `[x]`; set the marker
to 🔄/⚠️/✅; move fully-complete blocks to `## Done` with a date; confirm with the new
marker, then ask "anything to add or unblock next?" and stop.

**List or review** — show the live table (Step 2).

**Reprioritize** — confirm if ambiguous, update in place, re-sort P1→P2→P3 then by due date.

## Implementation handoff

Before any implementation begins after planning:

1. Present the complete numbered plan.
2. State each step's exact files, intended result, and verification checks.
3. Ask for explicit approval covering the step or named sequence.
4. A plain `go` approves the currently stated next step; `go with 1, 2, and 3` approves
   that full named sequence.
5. Complete every approved step without re-asking; pause only for genuine ambiguity, a
   blocker, or an unapproved step.

## Step 4 — Report back

Prefix every status line with its marker — `⬜`/`🔄`/`⚠️`/`✅`:

- current time snapshot
- remote pull status
- which context files were found/read
- reminder status (started now, already active, or unavailable)
- new subtasks added, or proposed if approval was required
- one-line suggestion for where to start

## Rules

- Never truncate a numbered explanation into a vague shorthand label.
- Never delete completed history; retain the full block under `## Done`. Archiving past 200
  lines to `TASKS_ARCHIVE.md` is `jadu-payan`'s job, not this one's.
- Keep each task's marker current and identical in the title and the numbered index.
- Flag dependencies inline with `← depends on [name]`.
- Do not implement feature/code changes here — plan only.
- Obey this project's own `AGENTS.md` approval rules before changing files.
