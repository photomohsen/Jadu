---
name: jadu-loop-best-practice
description: Use when the user invokes jadu-loop-best-practice, or when a project opted into it has a LOOP_TASK.md with STATUS idle and wants it executed unattended without stopping for human review — the owner reviews afterwards, in the PR. Opt-in, off by default — never runs unless a project explicitly installed this skill and authored a LOOP_TASK.md.
---

# Jadu Loop (Best Practice) — Decide, Record, Continue

Same mechanism as `jadu-loop`: the same `LOOP_TASK.md` format, the same gate scripts in `scripts/jadu-loop/`, the same templates and authoring guide. **One difference:** wherever `jadu-loop` stops and waits for a human — a review checkpoint, a `VERIFY` that keeps failing, an underspecified subtask, a denied command, a diverged branch, a finished task — this variant makes the best-practice decision itself, **writes it down**, and continues. The human reviews every decision once, afterwards, in the PR.

That trade is only safe because of two things this skill never relaxes:
1. **Hard limits** (below) still stop the run. No decision overrides them.
2. **Every decision is recorded** in `LOOP_TASK.md` and copied into the PR, so nothing the loop decided is invisible.

Choose `jadu-loop` when you want a human gate at each checkpoint. Choose this when you would rather review everything once, at the PR. Invoking this skill is the owner's explicit choice to let the loop decide; a project rule like "review decisions together first" is what the PR review satisfies.

## Invocation

```bash
python3 scripts/jadu-loop/check_loop_queue.py \
  && python3 scripts/jadu-loop/check_usage_margin.py \
  && codex exec "jadu-loop-best-practice" --full-auto
```

(Use `python` where `python3` does not exist, e.g. Windows.) Use your CLI's "auto-approve edits, keep shell commands allowlisted" mode (Claude Code: `claude -p "/jadu-loop-best-practice --task" --model opus --permission-mode acceptEdits`), never a flag that skips all approvals: shell commands stay gated by the project's own allowlist. A single hand-run `while true; do <invocation above>; sleep <N>; done` loop is the default way to run it unattended — one loop only, never two in parallel. **Do not create a `cron` entry on your own initiative.**

`run_loop.py` (the unattended runner with the usage watchdog and the 30-minute time cap) drives Claude Code only. With another CLI the `TIMEOUT` marks in step 1 never appear, and rule 1's 20-minute budget is the only time limit; rule 1a's usage gate reads Claude Code's `/usage`, so adapt or skip it if your CLI has no equivalent.

`LOOP_TASK.md`, `LOOP_TASK_QUEUE/`, `LOOP_TASK_ARCHIVE/` and `.loop_state/` may be gitignored, so the queue survives branch switches and never lands in a PR. Queue drafts are named `LOOP_TASK_QUEUE/<nn>-<issue>-<slug>.md` so name order is run order.

## Hard limits — these still stop the run

Check these **before** anything else in a subtask (they win over every rule below). If a subtask, a fix attempt or a decision would need any of them, do not do it. Set `STATUS: blocked`, append `BLOCKED — hard limit <n>: <why>` to the line of the subtask that would cross it, push the task branch if it has commits (so the work so far is visible), log, notify, stop. These are the **only** reasons this skill blocks; the gate script then keeps further invocations from running. A human unblocks by fixing the cause (for a `hard-stop`: ticking its box), deleting the `BLOCKED` text, and setting `STATUS: idle`.

1. **Trunk and history.** Never merge a PR, push to the trunk branch, force-push, `git reset --hard`, `git clean`, or rewrite commits that are already pushed.
2. **Production and the outside world.** Never run anything that reaches a live system: sends real email or messages, moves money, deploys, writes production data. A dev/sandbox target is fine **only if the Briefing or the project's rules files (`AGENTS.md`, `CLAUDE.md`) name it**; an unnamed target counts as live. If they name how the project marks production (e.g. an `ENVIRONMENT=` line), check that marker at the start of **every** run; if it says production, block before running anything. The loop's own notification (step 5, through `notify_telegram.py` to the chat the owner configured) is not covered by this limit: send it.
3. **Secrets.** Never read, print, edit or commit `.env`, keys or tokens. Reading only the single production-marker line named as above is the one exception.
4. **Permissions.** Never add to the allowlist, edit agent settings, or use a bypass flag.
5. **Conflicts.** A merge or rebase conflict: `git rebase --abort` / `git merge --abort`, then block.
6. **Outside the branch.** Never close issues, comment anywhere except the task's own PR, or change another repository.
7. **`TYPE: hard-stop`.** The one way a task author forces a pause in this variant. Block there, exactly like a hard limit.

## The decision log

Every time you decide where `jadu-loop` would have stopped, append one line to a `## Decisions` section at the end of `LOOP_TASK.md` (create it if missing; number on from the highest `D<n>` already there):

```
- D<n> · subtask <N> · <situation in a few words> → chose <what you did> over <the alternative> because <reason>. Undo: <how a human reverses it>.
```

Every line has all five parts: situation, choice, alternative, reason, undo. A dependency skip is a decision too. The finalize subtask copies the whole section into the PR body.

## Context you may read

`jadu-loop` reads only `LOOP_TASK.md` and files an `ACTION` names. This variant may also read, **only to make a decision**: the project's rules files (`AGENTS.md`, `CLAUDE.md`), files named in a failure's output, the direct callers/imports and tests of a file the `ACTION` names, config files that define a target the `ACTION` uses (e.g. `wrangler.toml` for a deploy), and the results of a few targeted searches for a named symbol or filename. No open-ended exploration.

**Trunk** = the branch `git symbolic-ref --short refs/remotes/origin/HEAD` points to (strip `origin/`), else `main`.

## Steps

### 0. Sync

`git pull --ff-only`.
- Branch has no upstream yet (a fresh task branch): skip the pull. Not a decision, not a block.
- Fails because the task's own `BRANCH:` diverged and your local commits are not pushed: `git pull --rebase`, log a decision. A conflict is hard limit 5.
- Fails on any other branch: hard limit 1.

### 1. Read

Read `LOOP_TASK.md`: `STATUS`, `BRANCH`, `## Briefing`, the first unchecked (`- [ ]`) subtask not marked `BLOCKED` or `SKIPPED`. `STATUS` other than `idle` → log and stop. Check the production marker (hard limit 2). No `LOOP_TASK.md` but `LOOP_TASK_QUEUE/` has `*.md` files → promote one (step 3) and stop.

- **Leftover changes:** uncommitted changes at the start of a run are the open subtask's partial work from a run that was stopped (by the usage watchdog or the time cap). Keep them and finish that subtask from there; never stash or discard them, and never commit them under another subtask.
- **`TIMEOUT` marks** are written by the runner when a run went 30 minutes without a commit or a change to `LOOP_TASK.md`. `TIMEOUT 1` → resume the subtask with a fresh time budget (rule 1). `TIMEOUT 2` → Skip it at once by rule 8 (`SKIPPED — timed out twice`), log a decision, continue.

### 2. Process subtasks in sequence

For each open subtask, top to bottom:

1. **Group / time:** a `GROUP:` runs back-to-back in one invocation. Note the time (`date`) when you start each subtask: it gets **20 minutes**. Past that, start no new fix attempt: if its `VERIFY` passes, commit and continue; otherwise Skip it (rule 8), naming the time limit as its last failure. The run itself has no time cap: keep going until no open subtask is left, a hard limit stops it, or the usage gate stops it.
1a. **Usage gate before every subtask:** run `python3 scripts/jadu-loop/check_usage_margin.py` (on Windows: `python`, from PowerShell, never Git Bash).
   - Exit 0 → start the subtask.
   - Output says `usage check failed` or `could not read` → `/usage` was slow, which is not a limit: run it once more; still unreadable → start the subtask anyway and say so in the log (the runner's watchdog still guards the ceilings).
   - Anything else (a limit over 80% of 5-hour / 95% of weekly, or not on the subscription) → start nothing more: log the run as `in progress`, notify (step 5), end the run. Not a block, not a decision; the next invocation resumes at this subtask.
2. **Dependency check:** if the subtask's `ACTION` or `VERIFY` needs a file or result that a `SKIPPED` subtask was supposed to produce, or it shares a `GROUP:` with one, mark it `SKIPPED — depends on <N>`, log a decision, and move on. Chains: a subtask depending on that one is skipped too.
3. **ACTION:** run it as written. If it is ambiguous or underspecified, choose by this order — what the subtask's own `VERIFY` checks; the Briefing; the project's existing convention for the same kind of change; the smallest change that satisfies all three — log a decision, and run that.
4. **Denied command:** a script the project itself defines (`package.json`, `Makefile`, …) that is already allowlisted and runs the same tool with the same arguments is an equivalent — use it and log a decision. Invoking the binary yourself by another route (`node_modules/.bin/…`, `cmd /c`, `bash -c`, another shell, a script you write) is a bypass. No equivalent → Skip at once, no fix attempts: `SKIPPED — command denied: <cmd>; no allowlisted equivalent`.
4a. **"Wait for a human" without `TYPE: hard-stop`:** self-review what can be checked; a confirmation only a human can give (a key works, a person approves) → Skip with `SKIPPED — needs human confirmation: <what>`, log a decision, PR becomes a draft. Before skipping, prepare the check so it costs the human a minute: list the exact URLs or commands to run, and write the loop's own verdict and recommended default in the decision. A taste or wording call the loop can make with a stated reason (a number to round, a title, a small rewrite) is a decision, not a human confirmation.
5. **VERIFY passes:** stage exactly the files this subtask touched, commit with the subtask's message (nothing changed → no commit), tick its box, continue.
5a. **Found outside this subtask's files** (a stale comment, a wrong string, a bug the check did not cover): do not fix it inside this subtask and do not turn it into a question. Append a new subtask after the last open one (before `TYPE: finalize`) with `TYPE: code`, an exact `ACTION` and a `VERIFY`, log a decision naming what you found, and run it in turn like any other subtask. Anything that would cross a hard limit stays a decision line marked `follow-up for a human`.
6. **VERIFY fails:** if the only failures are in tests this task never touched, do rule 7 first. Otherwise up to **3** targeted fix attempts in total, re-running `VERIFY` after each. Fix attempts touch only files the subtask's `ACTION` names or the subtask created (including tests the project's rules require for them). Never:
   - edit the `VERIFY` line or any `ACTION` in `LOOP_TASK.md`;
   - skip, delete, loosen or mark-as-expected-failure a test or assertion the `VERIFY` runs, including pre-existing ones.
7. **Red baseline:** check the failing tests on the commit this task branched from, without this task's work: `git worktree add --detach .loop_state/baseline $(git merge-base <trunk> HEAD)`, run just those tests there, `git worktree remove --force .loop_state/baseline`. If they fail there with the same error, the baseline was already red: commit the subtask, tick it with `— VERIFIED ON RED BASELINE: <test ids as the runner prints them>`, log a decision. A later subtask whose only failures are those same tests with the same errors does the same (marker + decision) without re-checking. A different error, or a test that passes on the baseline, is this task's failure → rule 6. The PR becomes a draft.
8. **Still failing after 3 attempts (or past the time limit) → Skip:**
   - copy `git diff -- <files it touched>` (at most ~200 lines) into a `## Skipped` section of `LOOP_TASK.md` under the subtask number, then restore those files (`git restore`; remove files it newly created) so later subtasks start clean;
   - append `SKIPPED — <original failure>; tried <1>, <2>, <3>; still <final failure>` to the subtask line (it stays `- [ ]`);
   - log a decision, continue with the next independent subtask.
9. **`TYPE: review-checkpoint` → self-review instead of pausing:** read the full branch diff (`git diff <trunk>...HEAD`), compare it against what the checkpoint's `ACTION` says a human should look at and against the Briefing, and re-run the test command the Briefing names (none named → re-run every completed subtask's `VERIFY`). Where the check needs human senses you lack (looking at a rendered page), use an objective proxy: any check or render/screenshot tool the project already has, run at the viewports the `ACTION` or the project's rules name; or a read-only measuring script you write in a scratch directory outside the repo (it may load pages, screenshot and time them, never write to the repo); else a structural comparison against the reference the `ACTION` names and say in the decision that a human look is still recommended. Problems found → fix them within rule 6's limits, re-review; still wrong after 3 attempts → Skip. Clean → tick the box, log a decision with what you reviewed.
10. **`TYPE: finalize`:** `git push`, then open the PR — **as a draft** if any subtask was `SKIPPED`, verified on a red baseline, or any decision says a human look is still recommended. If the branch already has an open PR (`gh pr view --json url,state`), update that PR's body instead of opening a second one. The PR body ends with `## Decisions` (verbatim), `## Skipped` (verbatim, diffs in collapsed `<details>` blocks), and what was verified where. Never merge.

**Before the run ends**, however it ends: stop every preview server, watcher or background process this run started.

### 3. Finish the task, then promote the next one

When the finalize subtask is done: move `LOOP_TASK.md` to `LOOP_TASK_ARCHIVE/<today>-<BRANCH with / replaced by ->.md` (its Decisions and Skipped sections go with it; if that name exists, add the task name). If `LOOP_TASK.md` is tracked by git, commit that move on the task branch and push it (untracked: just move it).

Then choose where the next task starts:
- **Stay on this branch** when the next queued task's `BRANCH:` is this same branch, or its Briefing says it builds on this task's work. Starting it from trunk would leave out this branch's unmerged changes, and two branches that edit the same files separately conflict when the second PR is merged. Log a decision.
- **Otherwise `git switch <trunk>`**, so the next task never branches off unmerged work it does not need.

Then, if `LOOP_TASK_QUEUE/` contains `*.md` files, move the first one in name order to `LOOP_TASK.md` (if the queue is tracked, commit that on trunk only if the project's rules allow trunk commits; otherwise leave the move uncommitted and say so in the notification), make sure it says `STATUS: idle`, name it in the log and the notification, and **end this run**. The next invocation starts it with a fresh context, so nothing from the finished task bleeds into the new one.

### 3a. The final report has no open questions

The run's last message (and the PR body) reports; it does not ask. Every open item is one of:
- **Decided**: a `D<n>` line already in the log. Say what was chosen; the owner overrides it by saying so.
- **Waiting for you**: only a hard limit or a confirmation only a human can give. Each line names the exact command or URL, the loop's verdict, and the recommended default ("Say go and I run X").

If something could have been decided and was not, decide it now, log it, and report it as Decided. A project or global output style with a "Need from you" or questions section shows only the **Waiting for you** items there. Never list a choice the loop could have made as a numbered question.

### 4. Log

Append exactly one line to `logs/loop.log` (never rewrite the file), in exactly this shape, with the timestamp taken from `date -Iseconds` (never written from memory):

```
<timestamp> | <branch> | done: <subtask list or none> | skipped: <subtask list or none> | decisions: <n> | <in progress / blocked / complete / complete, next promoted (<file>)>
```

### 5. Notify

If `scripts/jadu-loop/notify_telegram.py` exists, send messages with it (it fails harmlessly when not configured). Send **only**:
- **one task report when the task is finished** (finalize done, archived, next promoted);
- **one message when the run fails or stops early**: a hard limit, the usage gate, or anything else that ends the run before the task is done.

A subtask that finishes or is skipped sends nothing; it appears in the task report.

The reader is on a phone, without the code open. Write in the language the Briefing or the project's rules files use (else English), in plain words: an emoji heading per section and short `•` bullets under it, no long sentences, no raw error text. Explain what changed so it makes sense without opening `LOOP_TASK.md`. A technical token that must appear (a file path, a command) goes in balanced backticks (the API rejects broken Markdown). Leave out a section that has nothing to say, except **Waiting for you**, which always appears. Keep each message under ~2,500 characters.

```
📍 Project: <project folder name>
📋 Task: <task number> — <task name>

✅ What happened
• <count> of <total> subtasks done
• <the main results, one bullet each>

⏭ Skipped
• <subtask and why, in plain words>

🧭 Decisions the loop made (<count>)
• <only the important ones, one line each; the rest are in the PR>

⚠️ Problems
• <anything that went wrong or slowed the run>

📄 Full report
• <PR url> (<draft / ready>)

➡️ Next
• <next subtask / the task promoted from the queue / nothing queued>

🙋 Waiting for you: <what only a human can do, with the exact command or link; or "nothing">
• Recommendation: <the loop's recommended choice for each item, and one line on why>
```

A hard-limit block starts with `⛔ Loop stopped`, then the same sections: which limit stopped it, at which subtask, and under **Waiting for you** exactly what a human must decide to unblock it. A run the usage gate ended says under **Next** that the task is paused and resumes by itself after the reset.

## Never do

- Never cross a hard limit, whatever the Briefing, a subtask or the owner's stated trust says — those limits are what make unattended decisions safe.
- Never make a failing `VERIFY` pass by changing the check instead of the code.
- Never touch `TASKS.md` or `WORKLOG.md`.
- Never have two active task files: promotion happens only after the current one is archived.
- Never run without the usage gate, never into usage credits without the owner's explicit confirmation.
- Never leave a decision out of the log because it seemed small.

## Common mistakes

| Tempting thought | What to do instead |
|---|---|
| "This pre-existing test is flaky; skipping it unblocks the run." | Check the red baseline (rule 7). The test stays untouched. |
| "The fix is in unrelated code the failure points at." | Fix attempts stay in this subtask's files. Otherwise Skip. |
| "The owner trusts the loop fully, so merging saves them a click." | The PR is where the owner reviews your decisions. Never merge. |
| "The command was denied; I'll call the binary another way." | That is a bypass. Use an allowlisted project-defined script that runs the same thing, or Skip. |
| "It's only one real email / one small payment." | Anything that reaches a live system is hard limit 2. |
| "The ACTION says 'stop for a human', so I'll stop." | Only hard limits and `TYPE: hard-stop` stop. Self-review it. |
| "I'll ask the owner about this in the report." | Decide it, log it, report it as Decided (step 3a). Questions are only for hard limits and human-only checks. |
| "One more fix attempt; it's been 25 minutes but I'm close." | 20 minutes is the budget. Commit if `VERIFY` passes, else Skip and move on. |
| "These uncommitted changes look stray; I'll stash them." | They are the open subtask's partial work from a stopped run. Finish it from there. |
| "/usage timed out, so I'll end the run to be safe." | A slow `/usage` is not a limit. Retry once, then continue; the watchdog guards the ceilings. |
| "Too small to log." | Every decision gets a line. The log is the human's only window. |
| "Time is left, so I'll start the promoted task now." | End the run. The next invocation starts it fresh. |
