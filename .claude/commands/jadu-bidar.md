# Bidar — Session Start

Called at the beginning of a work session. Studies the project's current state, expands
its task list with new subtasks, and sets or suggests one 30-minute focus reminder.

The reminder serves two purposes: keeping you focused and keeping sessions short. Shorter
sessions mean smaller context windows, which saves tokens and keeps agent responses sharper.

**Do NOT ask for confirmation at any step — just do it.** Read context, expand tasks, and set
the reminder autonomously. This does not extend to implementing features or code, which still
follows the project's `AGENTS.md` approval rules.

## Steps

### 1. Get current time

Run `date '+%M %H %d %m'` to get current minute, hour, day-of-month, and month. Use it for
the session summary and reminder context.

### 2. Pull latest from remote when safe

Run `git remote get-url origin 2>/dev/null`. If a remote URL is returned, run
`git pull --ff-only`. Report what changed or say "already up to date". If the pull fails
because of local changes, divergence, auth, or network, report the error and continue
without aborting the session.

### 3. Read project context

Read, if present:

- `TASKS.md` — focus on P1/P2 open items and subtasks
- `WORKLOG.md` — read the last 80 lines and focus on recent Pending / TODO
- `AGENTS.md` — shared agent instructions, architecture notes, approval rules, commands, and conventions
- `CLAUDE.md` — Claude-specific compatibility notes, if present
- `PROJECT.md` and `README.md` — skim for project identity and setup
- `git log --oneline -20` — recent commit history

Skim, but do not deep-read, 2–3 recently modified files indicated by that git history or
status. Do not modify implementation files.

### 4. Expand the task list

If `TASKS.md` exists, add useful subtasks to open task blocks. Rules:

- Do not execute feature work — only plan
- Add subtasks that logically follow from what is already done or partially started
- Break vague items into concrete, actionable steps
- Flag dependencies inline with `← depends on [name]`
- Keep each new item one line, prefixed with `- [ ]`
- Add subtasks under relevant existing task blocks; do not create new top-level tasks unless the user asked
- Do not remove, check off, or re-prioritize existing items
- Leave each task's status marker as-is — `⬜` open · `🔄` handled · `⚠️` needs attention · `✅` done (defined in `jadu-kar`); adding subtasks never changes it, and a new top-level task (only when the user asked) defaults to `⬜`

If `TASKS.md` is missing, create one — no need to ask first.

### 5. Set or suggest the 30-minute reminder

If a reminder/timer tool is available, set one recurring 30-minute reminder:
"30 min — check your focus, review progress on current task."

If no reminder/timer tool is available, do not fake it and do not create OS-level cron
jobs. Tell the user to set an external 30-minute reminder instead.

### 6. Report back

Print a short summary. Prefix each status line with the marker that matches its state —
`⬜` open/none · `🔄` in progress · `⚠️` needs attention/unavailable · `✅` done — the same
four `jadu-kar` uses for tasks:

- current time snapshot
- remote pull status (e.g. `✅ pulled 3 commits` / `✅ already up to date` / `⚠️ pull failed: <reason>`)
- which context files were found/read
- how many new subtasks were added, or proposed if approval was required
- whether the 30-minute reminder was set (`✅`) or unavailable (`⚠️`)
- one-line suggestion for where to start

### 7. Hand off to implementation

Bidar is planning only — it never writes feature code itself. When you move on to actual
implementation afterward, follow the project's `AGENTS.md` approval rules for code changes.

## Rules

- Treat this as planning/session setup only.
- Do not implement feature/code changes.
- Obey this project's own `AGENTS.md` approval rules before changing files.
- Keep only the 30-minute reminder; do not add 60-minute reminders.
