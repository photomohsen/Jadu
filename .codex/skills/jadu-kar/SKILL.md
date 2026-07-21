---
name: jadu-kar
description: Quick, read-only view of this project's task list. Trigger whenever the user says "Jadu-kar" or "jadu kar" anywhere in a message - mid-conversation, not just as a formal skill call - to pull TASKS.md and show it as a table (number, priority, status, description, due date). Never adds, updates, completes, or reprioritizes tasks, and never pulls git or sets the focus reminder; that is jadu-bidar's job.
---

# Jadu Kar - Quick Task Table

`jadu-kar` is a lightweight, read-only view: pull this project's TASKS.md and show it as a
table. It does not start a session, pull git, or set the focus reminder - that is
jadu-bidar's job. This reuses jadu-bidar's table format rather than duplicating it.

## Workflow

0. **Read** TASKS.md only - nothing else. No WORKLOG.md, no git pull, no reminder.
1. **Render** the open tasks as a table: #, Priority, Status, Description, Due. Sort by
   priority then due date. Flag anything overdue. Reuse jadu-bidar's numbered index and
   status markers (Open/Handled/Needs attention/Done) so numbers stay consistent across
   both skills within a session.
2. Stop there. If the same message also asks for an edit (add/update/complete/reprioritize),
   handle that the normal way - jadu-bidar's task-management behavior, or plain conversation
   - in addition to showing the table, never instead of it.

## Rules

- Read-only, always: no task-file writes, no git operations, no reminder-setting.
- Never run the rest of jadu-bidar's first-call setup (context reads, reminder) - Kar is a
  peek, not a session start.
