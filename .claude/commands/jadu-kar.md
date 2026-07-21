# Kar — Quick Task Table

`jadu-kar` is a lightweight, read-only view: pull this project's `TASKS.md` and show it as a
table. It does not start a session, pull git, or set the focus reminder — that's
`jadu-bidar`'s job. This reuses `jadu-bidar`'s table format rather than duplicating it.

## Trigger

Fires on an explicit `/jadu-kar`, or on a plain mid-conversation mention of "Jadu-kar" /
"jadu kar" anywhere in a message — no slash needed.

## Steps

1. **Read** `TASKS.md` only. Nothing else — no `WORKLOG.md`, no git pull, no reminder.
2. **Render** the open tasks as a table: `#`, Priority, Status, Description, Due. Sort by
   priority then due date. Flag anything overdue. Reuse `jadu-bidar`'s numbered index and
   status markers (⬜/🔄/⚠️/✅) so numbers stay consistent across both commands within a
   session.
3. Stop there. If the same message also asks for an edit (add/update/complete/reprioritize),
   handle that the normal way — `jadu-bidar`'s task-management behavior, or plain
   conversation — in addition to showing the table, never instead of it.

## Rules

- Read-only, always: no task-file writes, no git operations, no reminder-setting.
- Never run the rest of `jadu-bidar`'s first-call setup (context reads, reminder) — Kar is a
  peek, not a session start.
