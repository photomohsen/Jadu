# Payan — Session End

Close a work session by producing a compact session brief, updating documentation from
that brief, committing the resulting changes, pushing them, and reporting the result.
The brief is the source of truth; do not infer unmentioned work from git history.

**Do NOT ask for confirmation at any step — just do it.** Running `jadu-payan` is itself the
instruction to write the docs, commit, and push; run every step through to the push without
pausing for approval.

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

Output the brief visibly in a code block, then continue — do not wait for the user to review it.

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
- Set each task's title status marker before moving on: `✅` for a task the brief shows complete (then move its block to `## Done` with a one-line summary and date), `⚠️` for one left blocked or awaiting a decision, `🔄` for one still in progress.
- Add new pending subtasks under relevant parent tasks; any new top-level task defaults to `⬜`.
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

## Step 6a — Archive `TASKS.md` if needed

Do this alongside Step 6, before the commit/push step.

Archive when `TASKS.md` exceeds 200 lines (Origin Jadu's threshold):

1. Create `TASKS_ARCHIVE.md` if it does not exist, with header `# Tasks Archive`.
2. Move every top-level task block that is fully `[x]` and already marked `✅`/moved to `## Done` to the top of `TASKS_ARCHIVE.md`, under a `### Done YYYY-MM-DD` header using that block's completion date.
3. Leave every open or partial block (anything not fully `✅`) in `TASKS.md`, along with the numbered index — archiving never touches open work.
4. Never archive a block that isn't fully complete, and never delete a block outright; it only ever moves between `TASKS.md` and `TASKS_ARCHIVE.md`.

## Step 7 — Cancel the session's focus reminder

If `jadu-bidar` set a 30-minute focus reminder this session, cancel it now — the reminder
exists only to pace an *active* session, so it must not keep firing after close.

- If a timer-management tool is available, cancel the recurring 30-minute job Bidar created.
- If no timer tool is available, or no reminder was set this session, skip silently.
- If the user set an external reminder instead, remind them once to clear it themselves.

## Step 8 — Commit and push

This does **not** use `git add -A`. A blind whole-repo add risks sweeping in unrelated dirty
work that happened to be sitting in the same working tree — stage only what this session
actually touched, the same discipline `jadu-push` uses on its own.

1. Compile the list of files this session actually created, edited, or deleted — from the conversation's own record of edits, not by scanning the repo. This naturally includes whatever Steps 1–6a just wrote (`WORKLOG.md`, `TASKS.md`, `AGENTS.md`, archive files).
2. Run `git status --short` to see the full working-tree state.
3. Stage exactly the session-touched files that show up as dirty or untracked (`git add <path>` per file). Never run `git add -A`.
4. If `git status --short` shows other dirty or untracked files that were **not** touched this session, list them explicitly and leave them unstaged.
5. If `scripts/check-secrets.ps1` exists, run it now that staging is set — after staging, before committing — and treat a non-zero exit as a blocker.
6. **Before pushing:** run `git fetch`, then `git pull --ff-only`. If that succeeds (already current, or a clean fast-forward), continue. If it fails from genuine divergence, do not force-push and do not auto-merge/rebase; report the divergence and stop, leaving this commit local and intact.
7. Create a concise commit message from the session title, unless the user provided one.
8. Run `git push`.
9. If there is nothing to commit, skip the commit and push only if there are already local commits to push (still fetch + try `--ff-only` first).
10. If commit or push fails because of auth, unresolved divergence, network, or secret-scan failure, report the blocker and stop.

## Step 9 — Report back

End with a concise report. Prefix each status line with the marker that matches its state —
`✅` done · `🔄` in progress · `⚠️` blocked/failed · `⬜` skipped/nothing to do:

- what was updated
- what was skipped and why
- whether archiving ran (WORKLOG and/or TASKS)
- whether the session's 30-minute focus reminder was cancelled
- the commit hash
- whether push succeeded

## Rules

- Use the session brief as the source of truth.
- During closeout documentation, write only to `WORKLOG.md`, `TASKS.md`, and `AGENTS.md` — never `CLAUDE.md`, `README.md`, or any other file.
- Obey this project's `AGENTS.md` approval rules before editing docs when required.
- Prefer documentation/task updates only; do not change implementation files as part of session close.
- Payan includes the push workflow: stage only session-touched files (never `git add -A`), run the repo secret scan when present, commit, and push.
- Always fetch and attempt a fast-forward pull immediately before pushing. Never force-push and never auto-merge/rebase past a real divergence — report and stop instead.
- Archive `TASKS.md` past 200 lines into `TASKS_ARCHIVE.md` the same way `WORKLOG.md` archives past 250 lines/8 entries — move only fully-closed blocks, never open or partial ones.
- Cancel any 30-minute focus reminder `jadu-bidar` set — it must not fire after the session is closed.
