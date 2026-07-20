---
name: jadu-payan
description: Session-end workflow for Jadu. Use when the user invokes jadu-payan or wants to close a session by writing a compact brief, updating WORKLOG.md/TASKS.md/AGENTS.md (and README.md when flagged) from it, then committing and pushing the result. Payan means end - it never stops to ask a question; it runs every step through to a final report.
---

# Jadu Payan - Session End

Close a work session by producing a compact session brief, updating documentation from
that brief, committing the resulting changes, pushing them, and reporting the result.
The brief is the source of truth; do not infer unmentioned work from git history.

**Payan means end.** It runs every step below through to the final report and stops. It
never ends with a question, a "Need from you" section, or anything else requiring a reply -
running `jadu-payan` is itself the instruction to write the docs, commit, and push, and that
instruction covers every step, not just the push. This is absolute.

## Workflow

### 0. Write the session brief first

Synthesize the session from the conversation only. Do not read files for this step. Keep
the brief under 35 lines and omit empty sections.

Use this exact format:

```text
SESSION BRIEF
Date: YYYY-MM-DD
Title: <short session title>

BUILT:
- <feature or change> | files: <key files touched>

DECISIONS:
- <title>: why=<reason> | how=<approach>

CHALLENGES:
- <challenge> -> <solution>

PENDING:
- [ ] <item>

AGENTS_MD_CHANGES: yes|no - <what changed structurally, or omit if no>
MEMORY_CHANGES: yes|no - <new durable preference/pattern to save, or omit if no>
```

Before writing this, run two mandatory self-checks - internal, not questions to the user:

- Decisions: what actually got decided this session, and why? Write it into DECISIONS even
  if the session felt routine - a thin or missing DECISIONS section is a sign this check was
  skipped, not that there was nothing to record.
- Preferences: did anything happen this session - a correction, a confirmed judgment call, a
  repeated pattern - that should change future behavior, even slightly? If so,
  `MEMORY_CHANGES: yes` with a one-line description; do not let this silently default to
  `no`.

Output the brief visibly in a code block, then continue - do not wait for the user to
review it.

### 1. Update `WORKLOG.md`

Read or create `WORKLOG.md` as needed. Append a dated entry, omitting empty sections:

```markdown
## YYYY-MM-DD - <title from brief>

### What we built

| Feature | Files |
|---|---|

### Decisions

#### 1. <title>
**Why:** ...
**How:** ...

### Challenges & Solutions

| Challenge | Solution |
|---|---|

### Pending / TODO

- [ ] ...

---
```

Focus on why decisions were made, not just what changed.

### 2. Update `TASKS.md`

Mark completed tasks `[x]` only when clear from the brief; set each task's title status
marker (`✅` complete, `⚠️` blocked or awaiting a decision, `🔄` in progress); move fully
done blocks to `## Done` with a one-line summary and date; add new pending subtasks under
relevant parent tasks (a new top-level task defaults to `⬜`); never remove or re-prioritize
open items. Render the open-task list as a table (`# - Priority - Status - Description`) if
reporting it back.

Cross-doc date check: compare any milestone/completion dates just written here against
`PROJECT.md`'s own dates for the same milestone. If they disagree, note the mismatch in the
step 8 report - flag only, never auto-fix.

If `TASKS.md` is missing and the brief has pending items, create a minimal list directly -
no need to ask first.

### 3. Update `AGENTS.md` only when flagged

Update `AGENTS.md` only if `AGENTS_MD_CHANGES=yes` and the change is structural: new
commands, architecture patterns, workflows, setup rules, or changed conventions. This skill
writes to `WORKLOG.md`, `TASKS.md`, and `AGENTS.md` - never `CLAUDE.md`, `README.md`, or
anything else - except the conditional refresh in step 3a.

### 3a. Conditional `README.md` refresh

If `AGENTS_MD_CHANGES=yes`, or this session changed architecture, setup, or CLI-facing
behavior, also refresh `README.md` to match - but only the parts that actually went stale;
do not rewrite the whole file. Skip silently if nothing user-facing changed.

### 4. Save memory only when flagged

If `MEMORY_CHANGES=yes` (per the mandatory check in step 0), write the durable
preference/pattern to the agent's memory system if one exists. If no memory convention
exists, skip saving and note it in the step 8 report instead - never pause here for a
reply, consistent with Payan never ending on a question.

### 5. Archive `WORKLOG.md` if needed

Archive when `WORKLOG.md` exceeds 250 lines or contains more than 8 session entries
matching `## 20` headings.

1. Create `WORKLOG_ARCHIVE.md` if it does not exist with header `# Worklog Archive`.
2. Move all entries except the 3 most recent into the top of `WORKLOG_ARCHIVE.md`.
3. Keep the `WORKLOG.md` header intact; only session entries move.
4. Add at the bottom of `WORKLOG.md`: `> Older entries archived in WORKLOG_ARCHIVE.md` if
   not already present.

### 5a. Archive `TASKS.md` if needed

Do this alongside step 5, before the commit/push step.

Archive when `TASKS.md` exceeds 200 lines (Origin Jadu's threshold):

1. Create `TASKS_ARCHIVE.md` if it does not exist, with header `# Tasks Archive`.
2. Move every top-level task block that is fully `[x]` and already marked `✅` / moved to
   `## Done` to the top of `TASKS_ARCHIVE.md`, under a `### Done YYYY-MM-DD` header using
   that block's completion date.
3. Leave every open or partial block (anything not fully `✅`) in `TASKS.md`, along with the
   numbered index - archiving never touches open work.
4. Never archive a block that is not fully complete, and never delete a block outright - it
   only ever moves between `TASKS.md` and `TASKS_ARCHIVE.md`.

### 6. Cancel the session's focus reminder

If a 30-minute focus reminder was set this session (by `jadu-bidar`'s first call), cancel it
now.

- If a timer-management tool is available, cancel the recurring 30-minute job.
- If no timer tool is available, or no reminder was set this session, skip silently.
- If the user set an external reminder instead, remind them once to clear it themselves.

### 7. Commit and push

This does not default to `git add -A`. A blind whole-repo add risks sweeping in unrelated
dirty work that happened to be sitting in the same working tree.

1. Compile the list of files this session actually created, edited, or deleted - from the
   conversation's own record of edits, not by scanning the repo. This naturally includes
   whatever steps 0-5a just wrote.
2. Run `git status --short` to see the full working-tree state.
3. Stage exactly the session-touched files that show up as dirty or untracked. Never
   `git add -A` by default. The one exception: if the user's message for this run
   explicitly says something like "stage everything," run one real `git add -A` for that
   call only - never triggered by anything less explicit than that phrase.
4. List any other dirty or untracked files that were not touched this session; leave them
   unstaged.
5. If `scripts/check-secrets.ps1` (or an equivalent secret scan) exists, run it now that
   staging is set - after staging, before committing - and treat a non-zero exit as a
   blocker.
6. Before pushing: run `git fetch`, then `git pull --ff-only`. If that succeeds (already
   current, or a clean fast-forward), continue. If it fails from genuine divergence, do not
   force-push and do not auto-merge/rebase; report the divergence and stop, leaving this
   commit local and intact.
7. Create a concise commit message from the session title, unless the user provided one.
8. Run `git push`.
9. Report the result as a rigid, unmissable line: `✅ Committed <hash> to <branch>, pushed
   to <remote>/<branch> - N files left unstaged`, or `⚠️ NOT pushed: <reason>`. Include the
   direct commit URL so it is independently checkable.
10. If there is nothing to commit but there are already local commits ahead of remote, push
    those anyway (still fetch + `--ff-only` first).
11. Any failure - auth, network, or unresolved divergence - report it plainly in the rigid
    `⚠️` line above and stop. Do not ask a question about it; the documentation updates from
    steps 0-5a already happened regardless.

### 8. Report back

End with a concise report. Prefix each status line with the marker that matches its state -
`✅` done, `🔄` in progress, `⚠️` blocked/failed, `⬜` skipped/nothing to do: what was
updated, what was skipped and why, whether archiving ran (WORKLOG and/or TASKS), any
cross-doc date-drift flag from step 2, whether the session's 30-minute focus reminder was
cancelled, and the rigid commit/push line from step 7 with its commit URL.

Then print exactly, every time: `Session closed. Now run /clear, then start the next
session with /jadu-bidar.` This cannot be triggered automatically - there is no tool
available to Payan that clears the conversation or starts a new one; the user has to run
both themselves. Do not soften this into "consider" or "if you would like."

Full stop here. No further text, no question, nothing pending a reply.

## Rules

- Use the session brief as the source of truth.
- During closeout documentation, write only to `WORKLOG.md`, `TASKS.md`, `AGENTS.md`, and -
  only when step 3a's condition is met - `README.md`. Never anything else.
- Prefer documentation/task updates only; do not change implementation files as part of
  session close.
- Payan includes the push workflow: stage only session-touched files (never `git add -A`
  outside the one explicit opt-in phrase), run the repo secret scan when present, commit,
  and push.
- Always fetch and attempt a fast-forward pull immediately before pushing. Never force-push
  and never auto-merge/rebase past a real divergence - report and stop instead.
- Cancel any 30-minute focus reminder set this session - it must not fire after close.
- Always close by directing the user to run `/clear` then `/jadu-bidar` - stated as a fact,
  not a suggestion.
- Never end with a question, a confirmation request, or a "Need from you" section - report
  and stop, always.
