# Jadu Loop — Autonomous Subtask Execution

Executes the one active task queued in the current project's `LOOP_TASK.md`, one invocation at a time, without asking for approval per step. This is the one deliberate exception to Jadu's normal rule ("never implement without explicit signal" — see `AGENTS.md`): it only ever touches subtasks a human already wrote into `LOOP_TASK.md` in a separate, supervised session. It never plans, decides, or explores on its own.

**Opt-in, off by default.** A project only gets this behavior if someone deliberately installs `jadu-loop` and writes a `LOOP_TASK.md`. Nothing about a normal Jadu session (`jadu-bidar` → `jadu-payan`) invokes it implicitly.

Independently callable — no dependency on `/jadu-bidar` or `/jadu-payan`, and doesn't run either of them. Meant to be invoked repeatedly — by hand, by a wrapping shell loop, or by `cron` if the project owner explicitly wants that (see "Invocation" below) — gated by `scripts/jadu-loop/check_loop_queue.py`, which confirms *before this ever runs* that `LOOP_TASK.md` has `STATUS: idle` and at least one open subtask. Works identically when run by hand.

## Invocation

```bash
python3 scripts/jadu-loop/check_loop_queue.py \
  && python3 scripts/jadu-loop/check_usage_margin.py \
  && claude -p "/jadu-loop" --permission-mode acceptEdits
```

Not `--dangerously-skip-permissions`. `acceptEdits` auto-approves file edits (this workflow's actual job) while leaving Bash commands gated by the project's own `.claude/settings.local.json` allowlist, so an `ACTION`/`VERIFY` line can never reach for a command outside what's already approved there. Author `LOOP_TASK.md` subtasks with that allowlist in mind — if a subtask needs a new command, add it to the allowlist first, in a normal supervised session, never as part of the loop itself.

`check_usage_margin.py` is a free pre-check — it queries `claude -p "/usage"` (zero API cost) and judges the 5-hour and weekly limits separately: a new run starts only below the start lines (80% / 95% by default), and it stops outright if Claude Code isn't running on the subscription. For a long unattended task use `python3 scripts/jadu-loop/run_loop.py` instead of a hand-rolled loop: it sleeps until a limit resets and then continues, and stops a running task at the ceilings (90% / 98%), so the loop never runs into usage credits. See `scripts/jadu-loop/README.md` for setup.

**Do not create an OS-level cron entry for this on your own initiative** (this is a repo-wide Jadu rule — see `AGENTS.md`). A simple hand-run `while true; do <invocation above>; sleep <N>; done` loop in its own terminal is the default way to run this unattended for a long task. Only wire up `cron` if the project owner explicitly asks for it.

## Token discipline is the entire point of this workflow

Read *only* `LOOP_TASK.md`, plus whatever file an individual subtask's `ACTION` explicitly names. Never read `AGENTS.md`, `CLAUDE.md`, `WORKLOG.md`, `TASKS.md`, or any other policy/context doc unless a subtask's `ACTION` line says to. Never run a broad search or exploration tool to "figure out" an underspecified subtask. If a subtask isn't self-contained enough to execute without research, that's an authoring bug in `LOOP_TASK.md` — stop and flag it (see "Notify" below) rather than trying to fill the gap yourself.

## Steps

### 0. Sync

`git pull --ff-only`. If it fails (local divergence), report the error to the log and stop — don't force anything.

### 1. Read

Read `LOOP_TASK.md` in the current directory. Note `STATUS`, `BRANCH`, the `## Briefing` block, and the first unchecked (`- [ ]`), non-`BLOCKED` subtask. If `STATUS` isn't `idle` or there's no open subtask, log that and stop immediately — this shouldn't normally happen since `check_loop_queue.py` already filtered for it, but never proceed on a state it doesn't recognize.

If this is the very first subtask (`TYPE: branch`) and the branch named in `BRANCH:` doesn't exist yet, this run will create it.

### 2. Process subtasks in sequence, in this one invocation

Track the wall-clock start time. For each open subtask, top to bottom:

0. **Group awareness:** a subtask may carry an optional `GROUP: <name>` line. Subtasks sharing the same `GROUP:` value must be completed together in this one invocation, back to back, once the first one starts — they exist as a group specifically because later subtasks in it depend on context freshly built by an earlier one, and starting a new invocation for the next subtask would mean a blank conversation with none of that context. Never let a group span two invocations. **`GROUP:` only forces subtasks to run back-to-back — it does NOT defer any subtask's own `VERIFY` until the group finishes.** Each subtask's `VERIFY` still runs immediately after its own `ACTION`, so a `LOOP_TASK.md` author must never write a subtask whose `VERIFY` depends on an artifact a *later* subtask (grouped or not) will create — see `docs/jadu-loop-authoring-guide.md`.
1. **Soft time check first:** if more than ~10 minutes have elapsed since step 0, do not start this subtask — unless it shares a `GROUP:` with the subtask you just finished, in which case finish the whole group first, then apply the check before the next group or standalone subtask. This must never fire mid-subtask, and never mid-group — only between groups, or between standalone ungrouped subtasks.
2. Run the subtask's `ACTION` exactly as written — no interpretation, no substitution, no "improving" it.
3. Run its `VERIFY` check.
4. **VERIFY passes:** `git add` exactly the files this subtask touched (never `git add -A`) and commit with the message the subtask specifies (or a short, obvious one if none is given). Check the subtask's box in `LOOP_TASK.md` and commit that too. Continue to the next subtask.
5. **VERIFY fails (1st time):** read the `VERIFY` failure output and make one targeted fix — touching only the file(s) the subtask's `ACTION` already names, nothing else. This is not open-ended debugging: no broad search, no reading files the subtask didn't already name. If the fix isn't obvious from the `VERIFY` error and the files already in scope, skip straight to blocking below rather than guessing. Rerun `VERIFY` once.
6. **VERIFY fails (2nd time, after the fix attempt):** set `STATUS: blocked` at the top of `LOOP_TASK.md`, append `BLOCKED` to this subtask's line with a one-line reason (name what was tried: original action, then the fix attempt, then what still failed), commit `LOOP_TASK.md`, and go straight to step 4 below — do not attempt any further subtasks this run or any future run until the project owner manually resets `STATUS` back to `idle`.
7. **`TYPE: review-checkpoint`:** treat this the same as a `VERIFY` failure for control-flow purposes — set `STATUS: blocked`, note in the reason that this is a deliberate human-review pause (not a failure), commit, and stop. Use this `TYPE` when a subtask's own author wants a mandatory pause for eyeball review (e.g. after a visually significant change) rather than an actual bug. See `docs/jadu-loop-authoring-guide.md`.

If every subtask (including the final `finalize` one) is done and verified: move `LOOP_TASK.md` to `LOOP_TASK_ARCHIVE/<today's date>-<slug from BRANCH>.md`, commit that move, and note the task is fully complete.

### 3. Log

Append one line to `logs/loop.log` (create the file if missing): timestamp, branch/task name, subtasks completed this run, and end state (`in progress` / `blocked` / `complete`). This is a quick-glance history separate from whatever the invoking shell redirects to its own log file.

### 4. Notify

If a notification channel is configured for this project (see `scripts/jadu-loop/README.md` — Telegram is the shipped default, but the script is a thin, swappable wrapper), send exactly one message per invocation via `python3 scripts/jadu-loop/notify_telegram.py "<message>"` (send-only — never wait for or read a reply). If no notification script is configured, skip this step — it's optional, not load-bearing for the mechanism itself.

Compose the message in whatever language the project owner reads these in — match `AGENTS.md`/`CLAUDE.md` if they specify one, otherwise default to English. Keep technical tokens (branch name, subtask numbers, file paths, commands/error text) in their own `code span`s or on their own line, never inline mid-sentence unwrapped — this matters most for RTL languages, where an unwrapped Latin token breaks rendering.

Structure, regardless of language, so a blocked run is unmistakable from a normal one at a glance:

**Not blocked** (finished the run cleanly — soft time limit or full task completion):
```
<branch>

✅ Done (subtasks <range/list>):
• <one short line per completed subtask — not the raw commit message>

⏱ <why it stopped: hit the soft time limit / all subtasks done and archived>
▶️ Next: subtask `<N>` — <short description>
```

**Blocked** (a `VERIFY` failed twice, or a `review-checkpoint` was hit): lead with something that stands out at a glance —
```
🚨 Blocked — <branch>

✅ Done (subtasks <range/list>):
• <...>

🛑 Blocked on subtask `<N>` — <short subtask name>
Reason: <the exact VERIFY failure text, 1–2 lines; wrap commands/errors in `code span`s>

👉 Needs a decision: <one line on what unblocking requires>
```

If zero subtasks completed this run (blocked immediately, or hit the soft time limit before finishing even the first one), say that plainly instead of printing an empty "Done" section. Never fabricate detail to fill a section out.

## Never do

- Never invoke `--dangerously-skip-permissions` or bypass the project's `.claude/settings.local.json` allowlist
- Never merge a PR or push directly to the trunk branch — a `finalize` subtask only opens a PR
- Never touch `TASKS.md` or `WORKLOG.md` — those belong to `/jadu-bidar`/`/jadu-payan`
- Never retry a `BLOCKED` subtask automatically, this run or a future one — that's the project owner's call
- Never run a broad search to "figure out" an underspecified subtask — stop and say so instead
- Never process more than one `LOOP_TASK.md` — if one doesn't exist or is ambiguous, stop rather than guessing
- Never add a `cron` entry on your own initiative — see `AGENTS.md`

## See also

- `scripts/jadu-loop/README.md` — installing the gate/usage/notify scripts into a project
- `templates/jadu-loop/LOOP_TASK.skeleton.md` — annotated blank template
- `templates/jadu-loop/LOOP_TASK.example.md` — a small, fully worked example
- `docs/jadu-loop-authoring-guide.md` — hard-won rules for writing a `LOOP_TASK.md` that doesn't self-sabotage
