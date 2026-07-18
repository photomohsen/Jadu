---
name: jadu-kar
description: Conversational task manager for Jadu. Use when the user invokes jadu-kar, or wants to add, update, complete, list, review, reprioritize, or reschedule tasks in TASKS.md. Never asks the user to edit the file directly. Also sets the 30-minute focus reminder on its first invocation each session - jadu-bidar no longer does this.
---

# Jadu Kar - Task Manager

Manages `TASKS.md` through conversation. Never asks the user to edit the file directly.

## Set the focus reminder (first invocation only)

The 30-minute reminder starts here, not at jadu-bidar - waking up and reading context is
not work yet; jadu-kar is where real work begins.

- If no 30-minute focus reminder is active yet this session, set one now: if a
  reminder/timer tool is available, set one recurring 30-minute reminder ("30 min - check
  your focus, review progress on current task"). If no reminder/timer tool is available, do
  not fake it and do not create OS-level cron jobs; tell the user once to set an external
  30-minute reminder.
- If a reminder is already active this session (set by an earlier jadu-kar call), skip
  silently - never stack a second recurring reminder.
- Do this before handling whichever mode (A/B/C/D) applies below.

## File format

`TASKS.md` may use this compact structure:

```markdown
# TASKS

## [P1] ⬜ Task title - due: YYYY-MM-DD
**Goal:** one sentence on what done looks like
**Blocked by:** optional blocker
- [ ] Subtask A
- [ ] Subtask B <- depends on A
- [x] Completed subtask

## Done
```

Priority levels: `P1` (this week / urgent), `P2` (this sprint / important), `P3` (backlog /
someday). Completed tasks stay in the file but are moved to a `## Done` section at the
bottom when the whole task is complete - until `jadu-payan` archives fully-closed blocks out
to `TASKS_ARCHIVE.md` once the file grows past 200 lines (see `jadu-payan`'s archiving step).
Kar itself never archives; it only ever adds to `## Done`.

### Status markers

Prefix every top-level task title with one status emoji, and mirror the same emoji in its
numbered index entry:

- ⬜ **Open** - not started yet (default for a new task)
- 🔄 **Handled** - actively being worked on or partially done
- ⚠️ **Needs attention** - blocked, flagged, or waiting on a decision
- ✅ **Done** - complete (the block also moves to `## Done`)

The marker reflects the whole task's state; subtask checkboxes `[ ]`/`[x]` are
unchanged. Update the marker whenever the task's state changes, and keep the title and
index markers in sync.

### Numbered task index

Keep a numbered top-level index near the top of `TASKS.md` once there is more than a
handful of tasks. Every entry must preserve the complete title (with its leading status
emoji), status, priority, due date when present, completion ratio, and enough goal/scope
context to select it without ambiguity. The index supplements the full task blocks; it
never replaces or shortens them. Keep numbers stable during a session so the user can say
`go with 1 and 3` or `complete 2`.

## Behavior by invocation

Detect which mode applies from the user's natural-language request.

### Mode A - Add a new task

1. Ask in one message for any missing details: goal/what "done" looks like, priority
   (P1/P2/P3), due date or none, obvious subtasks or figure them out together, blockers.
2. Once clear, write the task to `TASKS.md` with a `⬜` status marker on its title (mirrored in the index). If the file does not exist, create it with a header.
3. Confirm with a clean summary of the task and where it landed, prefixed `⬜` (it starts open).

### Mode B - Update or complete a task/subtask

1. Read `TASKS.md` and match by task number when supplied; otherwise fuzzy-match the task/subtask.
2. If a subtask is complete, mark `- [x]`.
3. Set the task's title status marker to match its new state - 🔄 (in progress), ⚠️ (blocked / awaiting a decision), or ✅ (complete) - and mirror it in the numbered index.
4. If the whole task is complete, set ✅ and move the block to `## Done` with a completed date.
5. Update the numbered index status and completion ratio without truncating its explanation.
6. Confirm the change with the new marker prefixed (`✅`/`🔄`/`⚠️`), then ask "Anything to add or unblock next?" and stop.

### Mode C - List or review tasks

1. Read `TASKS.md`.
2. Print open tasks sorted by priority then due date.
3. Number every selectable top-level task and preserve the full task title and explanation; never replace it with a vague shorthand label.
4. Show subtask completion ratio when possible.
5. Highlight overdue tasks when due date is before today.
6. Suggest the single best next action and remind the user they can select multiple numbers in one message.

### Mode D - Reprioritize or change due dates

1. Ask for confirmation if ambiguous.
2. Update `TASKS.md` in place.
3. Re-sort tasks P1 -> P2 -> P3, then by due date within each group when the file format supports it.
4. Confirm with a short `✅` summary of what moved.

## Implementation handoff

Before any implementation begins after task planning or management:

1. Present the complete numbered implementation plan.
2. Ask for explicit approval covering the step or named sequence to implement.
3. Treat a plain `go` as approval for the currently stated next step.
4. Treat an explicit instruction such as `go with 1, 2, and 3` as approval for that full named sequence.
5. Complete every approved step without asking for repeated approval; pause only for a genuine ambiguity, blocker, or unapproved step.

## Rules

- Do not execute task work; only plan and update `TASKS.md`.
- Ask clarifying questions in one message, not one at a time.
- If the request is vague, make a reasonable assumption and state it.
- Keep subtasks concrete and actionable.
- Match by task number when the user supplies one.
- Never truncate a numbered explanation into a vague shorthand label.
- Never delete completed history; retain the full block under `## Done`, mark subtasks `[x]`, and update the index status/ratio. Archiving fully-closed blocks to `TASKS_ARCHIVE.md` past the 200-line threshold is `jadu-payan`'s job, not Kar's.
- Keep each task's status marker (`⬜`/`🔄`/`⚠️`/`✅`) current and identical in the title and the numbered index.
- When reporting any status change back to the user, prefix the line with the matching marker instead of describing the state in words alone.
- Flag dependencies inline with `<- depends on [subtask name]`.
- Obey this project's `AGENTS.md` approval rules before editing.
