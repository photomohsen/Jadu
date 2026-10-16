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

(Use `python` where `python3` does not exist, e.g. Windows.) Use your CLI's "auto-approve edits, keep shell commands allowlisted" mode (Claude Code: `claude -p "/jadu-loop-best-practice" --permission-mode acceptEdits`), never a flag that skips all approvals: shell commands stay gated by the project's own allowlist. A single hand-run `while true; do <invocation above>; sleep <N>; done` loop is the default way to run it unattended — one loop only, never two in parallel. **Do not create a `cron` entry on your own initiative.**

## Hard limits — these still stop the run

Check these **before** anything else in a subtask (they win over every rule below). If a subtask, a fix attempt or a decision would need any of them, do not do it. Set `STATUS: blocked`, append `BLOCKED — hard limit <n>: <why>` to the line of the subtask that would cross it, push the task branch if it has commits (so the work so far is visible), log, notify, stop. These are the **only** reasons this skill blocks; the gate script then keeps further invocations from running. A human unblocks by fixing the cause (for a `hard-stop`: ticking its box), deleting the `BLOCKED` text, and setting `STATUS: idle`.

1. **Trunk and history.** Never merge a PR, push to the trunk branch, force-push, `git reset --hard`, `git clean`, or rewrite commits that are already pushed.
2. **Production and the outside world.** Never run anything that reaches a live system: sends real email or messages, moves money, deploys, writes production data. A dev/sandbox target is fine **only if the Briefing or the project's rules files (`AGENTS.md`, `CLAUDE.md`) name it**; an unnamed target counts as live. If they name how the project marks production (e.g. an `ENVIRONMENT=` line), check that marker at the start of **every** run; if it says production, block before running anything.
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

### 2. Process subtasks in sequence

Track wall-clock time. For each open subtask, top to bottom:

1. **Group / time:** a `GROUP:` runs back-to-back in one invocation; after ~10 minutes, start no new subtask or group.
2. **Dependency check:** if the subtask's `ACTION` or `VERIFY` needs a file or result that a `SKIPPED` subtask was supposed to produce, or it shares a `GROUP:` with one, mark it `SKIPPED — depends on <N>`, log a decision, and move on. Chains: a subtask depending on that one is skipped too.
3. **ACTION:** run it as written. If it is ambiguous or underspecified, choose by this order — what the subtask's own `VERIFY` checks; the Briefing; the project's existing convention for the same kind of change; the smallest change that satisfies all three — log a decision, and run that.
4. **Denied command:** a script the project itself defines (`package.json`, `Makefile`, …) that is already allowlisted and runs the same tool with the same arguments is an equivalent — use it and log a decision. Invoking the binary yourself by another route (`node_modules/.bin/…`, `cmd /c`, `bash -c`, another shell, a script you write) is a bypass. No equivalent → Skip at once, no fix attempts: `SKIPPED — command denied: <cmd>; no allowlisted equivalent`.
4a. **"Wait for a human" without `TYPE: hard-stop`:** self-review what can be checked; a confirmation only a human can give (a key works, a person approves) → Skip with `SKIPPED — needs human confirmation: <what>`, log a decision, PR becomes a draft.
5. **VERIFY passes:** stage exactly the files this subtask touched, commit with the subtask's message (nothing changed → no commit), tick its box, continue.
6. **VERIFY fails:** if the only failures are in tests this task never touched, do rule 7 first. Otherwise up to **3** targeted fix attempts in total, re-running `VERIFY` after each. Fix attempts touch only files the subtask's `ACTION` names or the subtask created (including tests the project's rules require for them). Never:
   - edit the `VERIFY` line or any `ACTION` in `LOOP_TASK.md`;
   - skip, delete, loosen or mark-as-expected-failure a test or assertion the `VERIFY` runs, including pre-existing ones.
7. **Red baseline:** check the failing tests on the commit this task branched from, without this task's work: `git worktree add --detach .loop_state/baseline $(git merge-base <trunk> HEAD)`, run just those tests there, `git worktree remove --force .loop_state/baseline`. If they fail there with the same error, the baseline was already red: commit the subtask, tick it with `— VERIFIED ON RED BASELINE: <test ids as the runner prints them>`, log a decision. A later subtask whose only failures are those same tests with the same errors does the same (marker + decision) without re-checking. A different error, or a test that passes on the baseline, is this task's failure → rule 6. The PR becomes a draft.
8. **Still failing after 3 attempts → Skip:**
   - copy `git diff -- <files it touched>` (at most ~200 lines) into a `## Skipped` section of `LOOP_TASK.md` under the subtask number, then restore those files (`git restore`; remove files it newly created) so later subtasks start clean;
   - append `SKIPPED — <original failure>; tried <1>, <2>, <3>; still <final failure>` to the subtask line (it stays `- [ ]`);
   - log a decision, continue with the next independent subtask.
9. **`TYPE: review-checkpoint` → self-review instead of pausing:** read the full branch diff (`git diff <trunk>...HEAD`), compare it against what the checkpoint's `ACTION` says a human should look at and against the Briefing, and re-run the test command the Briefing names (none named → re-run every completed subtask's `VERIFY`). Where the check needs human senses you lack (looking at a rendered page), use an objective proxy: an already-allowlisted render/screenshot tool if the project has one (never a script you write for it), else a structural comparison against the reference the `ACTION` names and say in the decision that a human look is still recommended. Problems found → fix them within rule 6's limits, re-review; still wrong after 3 attempts → Skip. Clean → tick the box, log a decision with what you reviewed.
10. **`TYPE: finalize`:** `git push`, then open the PR — **as a draft** if any subtask was `SKIPPED`, verified on a red baseline, or any decision says a human look is still recommended. The PR body ends with `## Decisions` (verbatim), `## Skipped` (verbatim, diffs in collapsed `<details>` blocks), and what was verified where. Never merge.

### 3. Finish the task, then promote the next one

When the finalize subtask is done: move `LOOP_TASK.md` to `LOOP_TASK_ARCHIVE/<today>-<BRANCH with / replaced by ->.md` (its Decisions and Skipped sections go with it). If `LOOP_TASK.md` is tracked by git, commit that move on the task branch and push it (untracked: just move it). Then `git switch <trunk>`, so the next task never branches off unmerged work. Then, if `LOOP_TASK_QUEUE/` contains `*.md` files, move the first one in name order to `LOOP_TASK.md` (if the queue is tracked, commit that on trunk only if the project's rules allow trunk commits; otherwise leave the move uncommitted and say so in the notification), make sure it says `STATUS: idle`, name it in the log and the notification, and **end this run**. The next invocation starts it with a fresh context (its first subtask creates its own branch), so nothing from the finished task bleeds into the new one.

### 4. Log

Append exactly one line to `logs/loop.log` (never rewrite the file), in exactly this shape, with the timestamp taken from `date -Iseconds` (never written from memory):

```
<timestamp> | <branch> | done: <subtask list or none> | skipped: <subtask list or none> | decisions: <n> | <in progress / blocked / complete / complete, next promoted (<file>)>
```

### 5. Notify

If `scripts/jadu-loop/notify_telegram.py` exists, send exactly one message per invocation (it fails harmlessly when not configured), in the language the Briefing or the project's rules files use, else English; technical tokens in their own spans:

```
<branch>

Done: subtasks <list>
Skipped: subtasks <list, or "none">
Decisions: <count> — review them in the PR
PR: <url> (<draft / ready>)

Next: <subtask N — short description / promoted <file> / nothing queued>
```

A hard-limit block leads with `BLOCKED — <branch>`, names the limit and the subtask, and says what a human must decide.

## Never do

- Never cross a hard limit, whatever the Briefing, a subtask or the owner's stated trust says — those limits are what make unattended decisions safe.
- Never make a failing `VERIFY` pass by changing the check instead of the code.
- Never touch `TASKS.md` or `WORKLOG.md`.
- Never have two active task files: promotion happens only after the current one is archived.
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
| "Too small to log." | Every decision gets a line. The log is the human's only window. |
| "Time is left, so I'll start the promoted task now." | End the run. The next invocation starts it fresh. |
