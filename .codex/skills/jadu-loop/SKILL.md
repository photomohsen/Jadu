---
name: jadu-loop
description: Autonomous subtask execution for Jadu. Use when the user invokes jadu-loop, or when a project has an opted-in LOOP_TASK.md with STATUS idle and an open subtask that should be executed without per-step approval. Opt-in, off by default — never runs unless a project explicitly installed this skill and authored a LOOP_TASK.md.
---

# Jadu Loop — Autonomous Subtask Execution

Executes the one active task queued in the current project's `LOOP_TASK.md`, one invocation at a time, without asking for approval per step. This is the one deliberate exception to Jadu's normal rule ("never implement without explicit signal" — see `AGENTS.md`): it only ever touches subtasks a human already wrote into `LOOP_TASK.md` in a separate, supervised session. It never plans, decides, or explores on its own.

**Opt-in, off by default.** A project only gets this behavior if someone deliberately installs `jadu-loop` and writes a `LOOP_TASK.md`. Nothing about a normal Jadu session (`jadu-bidar` → `jadu-payan`) invokes it implicitly.

Independently callable — no dependency on `jadu-bidar` or `jadu-payan`, and doesn't run either of them. Meant to be invoked repeatedly — by hand, by a wrapping shell loop, or by `cron` if the project owner explicitly wants that — gated by `scripts/jadu-loop/check_loop_queue.py`, which confirms *before this ever runs* that `LOOP_TASK.md` has `STATUS: idle` and at least one open subtask.

## Invocation

```bash
python3 scripts/jadu-loop/check_loop_queue.py \
  && python3 scripts/jadu-loop/check_usage_margin.py \
  && codex exec "jadu-loop" --full-auto
```

(Substitute whatever your Codex CLI's equivalent of "auto-approve edits, keep shell commands allowlisted" flag is — the intent is the same as Claude Code's `--permission-mode acceptEdits`: file edits auto-approve, but shell commands stay gated by the project's own approval config, so an `ACTION`/`VERIFY` line can never reach for a command outside what's already approved. Never use a flag that skips all approvals outright.) Author `LOOP_TASK.md` subtasks with that allowlist in mind — if a subtask needs a new command, add it to the allowlist first, in a normal supervised session, never as part of the loop itself.

`check_usage_margin.py` is a free pre-check gating on your provider's usage/rate-limit signal, if one is available headlessly; adapt or skip it if your agent surface has no equivalent. See `scripts/jadu-loop/README.md` for setup.

**Do not create an OS-level cron entry for this on your own initiative** (repo-wide Jadu rule — see `AGENTS.md`). A simple hand-run `while true; do <invocation above>; sleep <N>; done` loop in its own terminal is the default way to run this unattended for a long task. Only wire up `cron` if the project owner explicitly asks for it.

## Token discipline is the entire point of this skill

Read *only* `LOOP_TASK.md`, plus whatever file an individual subtask's `ACTION` explicitly names. Never read `AGENTS.md`, `WORKLOG.md`, `TASKS.md`, or any other policy/context doc unless a subtask's `ACTION` line says to. Never run a broad search or exploration tool to "figure out" an underspecified subtask. If a subtask isn't self-contained enough to execute without research, that's an authoring bug in `LOOP_TASK.md` — stop and flag it (see "Notify" below) rather than trying to fill the gap yourself.

## Steps

### 0. Sync

`git pull --ff-only`. If it fails (local divergence), report the error to the log and stop — don't force anything.

### 1. Read

Read `LOOP_TASK.md` in the current directory. Note `STATUS`, `BRANCH`, the `## Briefing` block, and the first unchecked (`- [ ]`), non-`BLOCKED` subtask. If `STATUS` isn't `idle` or there's no open subtask, log that and stop immediately — this shouldn't normally happen since `check_loop_queue.py` already filtered for it, but never proceed on a state it doesn't recognize.

If this is the very first subtask (`TYPE: branch`) and the branch named in `BRANCH:` doesn't exist yet, this run will create it.

Uncommitted changes at the start of a run are the open subtask's partial work from a run that was stopped. Keep them and finish that subtask from there — never stash or discard them, never commit them under another subtask. If the open subtask's line carries `TIMEOUT 1` (written by `run_loop.py`), resume it with a fresh time budget. `TIMEOUT 2` → block it at once (step 2, item 6), reason `timed out twice`.

### 2. Process subtasks in sequence, in this one invocation

For each open subtask, top to bottom:

0. **Group awareness:** a subtask may carry an optional `GROUP: <name>` line. Subtasks sharing the same `GROUP:` value must be completed together in this one invocation, back to back, once the first one starts — later subtasks in it depend on context freshly built by an earlier one, and starting a new invocation for the next subtask would mean a blank conversation with none of that context. Never let a group span two invocations. **`GROUP:` only forces subtasks to run back-to-back — it does NOT defer any subtask's own `VERIFY` until the group finishes.** Each subtask's `VERIFY` still runs immediately after its own `ACTION`, so a `LOOP_TASK.md` author must never write a subtask whose `VERIFY` depends on an artifact a *later* subtask (grouped or not) will create — see `docs/jadu-loop-authoring-guide.md`.
1. **Time budget:** note the time (`date`) when you start each subtask; it gets **20 minutes**. Past that, start no new fix attempt: if its `VERIFY` passes, commit and continue; otherwise block it (item 6), naming the time limit as the last failure.
2. Run the subtask's `ACTION` exactly as written — no interpretation, no substitution, no "improving" it.
3. Run its `VERIFY` check.
4. **VERIFY passes:** stage exactly the files this subtask touched (never a blanket add-everything) and commit with the message the subtask specifies (or a short, obvious one if none given). Check the subtask's box in `LOOP_TASK.md` and commit that too. Continue to the next subtask.
5. **VERIFY fails (1st time):** read the `VERIFY` failure output and make one targeted fix — touching only the file(s) the subtask's `ACTION` already names, nothing else. No broad search, no reading files the subtask didn't already name. If the fix isn't obvious, skip straight to blocking below rather than guessing. Rerun `VERIFY` once.
6. **VERIFY fails (2nd time, after the fix attempt):** set `STATUS: blocked` at the top of `LOOP_TASK.md`, append `BLOCKED` to this subtask's line with a one-line reason (original action, then the fix attempt, then what still failed), commit `LOOP_TASK.md`, and stop — do not attempt any further subtasks this run or any future run until the project owner manually resets `STATUS` back to `idle`.
7. **`TYPE: review-checkpoint`:** treat like a `VERIFY` failure for control flow — set `STATUS: blocked`, note this is a deliberate human-review pause (not a failure), commit, and stop. Use this `TYPE` when a subtask's author wants a mandatory pause for eyeball review rather than an actual bug. See `docs/jadu-loop-authoring-guide.md`.

If every subtask (including the final `finalize` one) is done and verified: move `LOOP_TASK.md` to `LOOP_TASK_ARCHIVE/<today's date>-<slug from BRANCH>.md`, commit that move, and note the task is fully complete.

Before the run ends, however it ends: stop every preview server, watcher or background process this run started.

### 3. Log

Append one line to `logs/loop.log` (create if missing): timestamp, branch/task name, subtasks completed this run, and end state (`in progress` / `blocked` / `complete`).

### 4. Notify

If a notification channel is configured for this project (see `scripts/jadu-loop/README.md`), send a message via `python3 scripts/jadu-loop/notify_telegram.py "<message>"` (send-only) **only** when the task is complete (archived) or the run blocks or stops early. A subtask finishing sends nothing. If none is configured, skip this step.

Compose the message in whatever language the project owner reads these in. Keep technical tokens (branch name, subtask numbers, file paths, commands/error text) isolated in their own spans or lines, never inline mid-sentence unwrapped.

**Complete** (all subtasks done and archived):
```
<branch>

Done (subtasks <range/list>):
- <one short line per completed subtask>

PR: <url>
Next: <the next queued task / nothing queued>
```

**Blocked** (a `VERIFY` failed twice, the time budget ran out, a `review-checkpoint` was hit, or anything else ended the run early) — lead with something that stands out:
```
BLOCKED — <branch>

Done (subtasks <range/list>):
- <...>

Blocked on subtask <N> — <short subtask name>
Reason: <the exact VERIFY failure text, 1-2 lines>

Needs a decision: <one line on what unblocking requires>
```

If zero subtasks completed this run, say that plainly instead of printing an empty "Done" section.

## Never do

- Never bypass the project's approval/allowlist config for shell commands
- Never merge a PR or push directly to the trunk branch — a `finalize` subtask only opens a PR
- Never touch `TASKS.md` or `WORKLOG.md` — those belong to `jadu-bidar`/`jadu-payan`
- Never retry a `BLOCKED` subtask automatically, this run or a future one — that's the project owner's call
- Never run a broad search to "figure out" an underspecified subtask — stop and say so instead
- Never process more than one `LOOP_TASK.md`
- Never add a `cron` entry on your own initiative — see `AGENTS.md`

## See also

- `scripts/jadu-loop/README.md` — installing the gate/usage/notify scripts into a project
- `templates/jadu-loop/LOOP_TASK.skeleton.md` — annotated blank template
- `templates/jadu-loop/LOOP_TASK.example.md` — a small, fully worked example
- `docs/jadu-loop-authoring-guide.md` — hard-won rules for writing a `LOOP_TASK.md` that doesn't self-sabotage
