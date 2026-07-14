---
name: jadu-bidar
description: Session-start workflow for Jadu. Use when the user invokes jadu-bidar, starts or resumes a session, wants Codex to review the project's TASKS/WORKLOG/AGENTS context, pull latest changes safely, expand planning subtasks, set or suggest a 30-minute focus reminder, and recommend where to begin without implementing code.
---

# Jadu Bidar - Session Start

Called at the beginning of a work session. Studies the project's current state, expands
its task list with new subtasks, and sets or suggests one 30-minute focus reminder.

The reminder serves two purposes: keeping you focused and keeping sessions short. Shorter
sessions mean smaller context windows, which saves tokens and keeps agent responses
sharper.

## Workflow

### 0. Get current time

Run:

```bash
date '+%M %H %d %m'
```

Use it for the session summary and reminder context.

### 1. Pull latest from remote when safe

Run:

```bash
git remote get-url origin 2>/dev/null
```

If a remote URL is returned, run:

```bash
git pull --ff-only
```

Report what changed or say `already up to date`. If the pull fails because of local
changes, divergence, auth, or network, report the error and continue without aborting the
session.

### 2. Read project context

Read, if present:

- `TASKS.md` - focus on P1/P2 open items and subtasks.
- `WORKLOG.md` - read the last 80 lines and focus on recent Pending / TODO.
- `AGENTS.md` - shared agent instructions, architecture notes, approval rules, commands, and conventions.
- `CLAUDE.md` - Claude-specific compatibility notes, if present.
- `PROJECT.md` and `README.md` - skim for project identity and setup.
- `git log --oneline -20` - recent commit history.

Skim, but do not deep-read, 2-3 recently modified files indicated by that git history or
status. Do not modify implementation files.

### 3. Expand the task list

If `TASKS.md` exists, add useful subtasks to open task blocks. Rules:

- Do not execute feature work - only plan.
- Add subtasks that logically follow from what is already done or partially started.
- Break vague items into concrete, actionable steps.
- Flag dependencies inline with `<- depends on [name]`.
- Keep each new item one line, prefixed with `- [ ]`.
- Add subtasks under relevant existing task blocks; do not create new top-level tasks unless the user asked.
- Do not remove, check off, or re-prioritize existing items.
- If repository instructions require approval before file changes, present the proposed `TASKS.md` edits and wait for explicit permission before editing.

If `TASKS.md` is missing, propose creating one but do not create it without approval.

### 4. Set or suggest the 30-minute reminder

If a reminder/timer tool is available, set one recurring reminder:

- 30-minute recurring reminder: `30 min - check your focus, review progress on current task`

If no reminder/timer tool is available, do not fake it and do not create OS-level cron
jobs. Tell the user to set an external 30-minute reminder.

### 5. Report back

Print a short summary:

- current time snapshot
- remote pull status
- which context files were found and read
- how many new subtasks were added, or proposed if approval was required
- whether the 30-minute reminder was set or unavailable
- one-line suggestion for where to start

### 6. Gate implementation on explicit approval

Before any implementation begins after this planning-only workflow:

1. Present the complete numbered implementation plan.
2. Ask for explicit approval covering the step or named sequence to implement.
3. Treat a plain `go` as approval for the currently stated next step.
4. Treat an explicit instruction such as `go with 1, 2, and 3` as approval for that full named sequence.
5. Complete every approved step without asking for repeated approval; pause only for a genuine ambiguity, blocker, or unapproved step.

## Rules

- Treat this as planning and session setup only.
- Do not implement feature or code changes.
- Obey this project's own `AGENTS.md` approval rules before changing files.
- Keep only the 30-minute reminder; do not add 60-minute reminders.
