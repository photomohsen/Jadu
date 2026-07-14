# Payan — Session End

Close a work session by producing a compact session brief, updating documentation from
that brief, committing the resulting changes, pushing them, and reporting the result.
The brief is the source of truth; do not infer unmentioned work from git history.

## Step 1 — Write the session brief first

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
- <challenge> → <solution>

PENDING:
- [ ] <item>

AGENTS_MD_CHANGES: yes|no — <what changed structurally, or omit if no>
MEMORY_CHANGES: yes|no — <new durable preference/pattern to save, or omit if no>
```

Output the brief visibly in a code block so the user can review it.

## Step 2 — Update `WORKLOG.md`

Read or create `WORKLOG.md` as needed. Append a dated entry, omitting empty sections:

```markdown
## YYYY-MM-DD — <title from brief>

### What we built

| Feature | Files |
|---|---|
| ... | ... |

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

## Step 3 — Update `TASKS.md`

If `TASKS.md` exists:

- Mark completed tasks `[x]` only when completion is clear from the session brief.
- Move fully done blocks to `## Done` with a one-line summary and date.
- Add new pending subtasks under relevant parent tasks.
- Do not remove or re-prioritize open items.

If `TASKS.md` is missing and the brief has pending items, propose or create a minimal task
list depending on repository approval rules.

## Step 4 — Update `AGENTS.md` only when flagged

Update `AGENTS.md` only if `AGENTS_MD_CHANGES=yes` and the change is structural: new
commands, architecture patterns, workflows, setup rules, or changed conventions. This
command writes to exactly three files: `WORKLOG.md`, `TASKS.md`, and `AGENTS.md`. It never
touches `CLAUDE.md`, `README.md`, or any other file.

## Step 5 — Save memory only when flagged

If `MEMORY_CHANGES=yes`, write durable preferences/patterns to the agent's memory system if
one exists. If no memory convention exists, ask before creating a new memory directory.

## Step 6 — Archive `WORKLOG.md` if needed

Archive when `WORKLOG.md` exceeds 250 lines or contains more than 8 session entries
matching `## 20` headings.

1. Create `WORKLOG_ARCHIVE.md` if it does not exist with header `# Worklog Archive`.
2. Move all entries except the 3 most recent into the top of `WORKLOG_ARCHIVE.md`.
3. Keep the `WORKLOG.md` header intact; only session entries move.
4. Add at the bottom of `WORKLOG.md`: `> Older entries archived in WORKLOG_ARCHIVE.md` if not already present.

## Step 7 — Cancel the session's focus reminder

If `jadu-bidar` set a 30-minute focus reminder this session, cancel it now — the reminder
exists only to pace an *active* session, so it must not keep firing after close.

- If a timer-management tool is available, cancel the recurring 30-minute job Bidar created.
- If no timer tool is available, or no reminder was set this session, skip silently.
- If the user set an external reminder instead, remind them once to clear it themselves.

## Step 8 — Commit and push

After the closeout edits are complete:

1. Run `git status --short` and inspect the staged/unstaged shape.
2. Stage all changes with `git add -A`.
3. If `scripts/check-secrets.ps1` exists, run it after staging and before committing.
4. Create a concise commit message from the session title, unless the user provided one.
5. Run `git push`.
6. If there is nothing to commit, skip the commit and push only if there are already local commits to push.
7. If commit or push fails because of auth, divergence, network, or secret-scan failure, report the blocker and stop.

## Step 9 — Report back

End with a concise report:

- what was updated
- what was skipped and why
- whether archiving ran
- whether the session's 30-minute focus reminder was cancelled
- the commit hash
- whether push succeeded

## Rules

- Use the session brief as the source of truth.
- During closeout documentation, write only to `WORKLOG.md`, `TASKS.md`, and `AGENTS.md` — never `CLAUDE.md`, `README.md`, or any other file.
- Obey this project's `AGENTS.md` approval rules before editing docs when required.
- Prefer documentation/task updates only; do not change implementation files as part of session close.
- Payan includes the push workflow: stage all changes, run the repo secret scan when present, commit, and push.
- Cancel any 30-minute focus reminder `jadu-bidar` set — it must not fire after the session is closed.
