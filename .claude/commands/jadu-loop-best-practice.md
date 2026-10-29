# Jadu Loop (Best Practice) — Decide, Record, Continue

Same mechanism as `jadu-loop`: the same `LOOP_TASK.md` format, the same gate scripts in `scripts/jadu-loop/`, the same templates and authoring guide. **One difference:** wherever `jadu-loop` stops and waits for a human — a review checkpoint, a `VERIFY` that keeps failing, an underspecified subtask, a denied command, a diverged branch, a finished task — this variant makes the best-practice decision itself, **writes it down**, and continues. The human reviews every decision once, afterwards, in the PR.

That trade is only safe because of two things this skill never relaxes:
1. **Hard limits** (below) still stop the run. No decision overrides them.
2. **Every decision is recorded** in `LOOP_TASK.md` and copied into the PR, so nothing the loop decided is invisible.

Choose `jadu-loop` when you want a human gate at each checkpoint. Choose this when you would rather review everything once, at the PR. Invoking this skill is the owner's explicit choice to let the loop decide; a project rule like "review decisions together first" is what the PR review satisfies.

**Keep going.** The loop never stops to ask what it can decide. It decides by best practice (see "How to decide"), records the decision, and moves to the next step. It waits for the owner only at a hard limit or a confirmation only a human can give, and even then the runner stays alive so the work resumes the moment the block is cleared.

To turn a project's existing plan, phase files and follow-ups into a ready queue for this skill, use `/jadu-loop-prepare` first.

## Invocation

Run everything from the project root: the scripts read `LOOP_TASK.md` and write `.loop_state/` in the current directory. Use `python` where `python3` does not exist (e.g. Windows).

**Two modes, chosen by the arguments:**

- **Invoked without `--task` (the owner typed it in chat): start the runner, do no task yourself.** The runner works through the whole queue, one fresh `claude -p` per task, and this skill's decide-and-record rules run inside each of those. In this mode:
  1. Check that no runner is already going — one loop only (`pgrep -af run_loop.py`; on Windows, PowerShell: `Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object CommandLine -like '*run_loop.py*'`). One is listed → do not start a second; report its PID and stop.
  2. No `LOOP_TASK.md` and no `LOOP_TASK_QUEUE/*.md` → report "nothing queued" and stop. Only queued files → fine: the runner's `--queue` lets the first run promote one.
  2a. **Project rules match this skill.** Read the project's rules files (`CLAUDE.md`, `AGENTS.md`) and any loop rules they point to (e.g. a plan's "loop rules" part), plus the Briefings of `LOOP_TASK.md` and every `LOOP_TASK_QUEUE/*.md`, which often repeat those rules. A rule that overrides this skill's decide-and-continue behaviour is rewritten to match it, in the rules files and in every Briefing that repeats it: a stop for a choice the loop can decide (design, architecture, upgrades, audits, approving a well-known permissive licence), "no fix attempts", "no automatic advance", or an owner step a standing grant can cover. Rewrite only those lines, keep each rule's number, add the date, and list every changed rule in chat with its old and new wording. **Where to commit: never on the local trunk.** Hard limit 1 forbids pushing the trunk, so a local trunk commit makes it diverge from `origin` as soon as anything is merged there, and step 0's `git pull --ff-only` then blocks the loop. Use a setup branch instead: with a clean working tree, `git switch -c loop/setup-<today> <trunk>`, commit `align loop rules with jadu-loop-best-practice`, push, open a PR, switch back. A dirty tree → do not commit; report what is uncommitted and why. **Task files tracked on the trunk** (`git ls-files LOOP_TASK.md LOOP_TASK_QUEUE` lists anything): untrack them in the same setup PR (`git rm -r --cached LOOP_TASK.md LOOP_TASK_QUEUE`, plus their `.gitignore` lines). The setup PR is a **Waiting for you** item (recommended: merge it; it changes only loop rules and ignore lines). Start the runner only after the merge: copy the task files aside, `git switch <trunk>`, `git pull --ff-only`, put the task files back (the pull deletes the working copies of files the PR untracks). Nothing to rewrite and nothing tracked → no setup PR. Gitignored task files need no commit. Never loosen hard limits 1–6, a paid-call or secrets rule, or a read-only rule for other folders. Also write the grants file (see "Standing grants") with the categories the owner has already said go to, quoting the owner's words. The same check applies whenever the owner asks to set up a loop or author a `LOOP_TASK.md`.
  3. **Permissions first.** The runner passes the project's `.claude/settings.json` + `settings.local.json` allowlist to every `claude -p` as `--allowedTools`, so folder trust does not matter. Read the `ACTION` and `VERIFY` lines of `LOOP_TASK.md` and every `LOOP_TASK_QUEUE/*.md`, plus the archive/promote `mv` and the gate scripts, and check each shell command they need is covered by that allowlist. Missing ones → if the grants file has `GRANT: allowlist`, add the exact narrow entries yourself (never a bypass, never a wildcard interpreter) and list them in your next chat message; otherwise show the owner the exact entries and add them on the owner's yes. Loop entries go in `.claude/settings.local.json`, which the runner reads and which must be in `.gitignore` (add the line if missing): untracked, they survive every branch switch and need no commit. Then start. Never start a run you know will hit a denied command.
  4. Start the runner **inside this session**, as a background shell task, so the owner follows it here:
     ```bash
     python3 scripts/jadu-loop/run_loop.py "/jadu-loop-best-practice --task" --model <model> --effort <effort> --wait-on-block --queue
     ```
     `--wait-on-block` keeps the runner alive on a block: it checks `LOOP_TASK.md` every minute and continues by itself once `STATUS` is back to `idle`. Without it the runner exits on a block and the loop stays dead until someone restarts it. `--queue` lets a run start when only `LOOP_TASK_QUEUE/` has tasks, so the run promotes the first one (step 1); without it the gate sees no `LOOP_TASK.md` and the loop ends at once.
     **The loop inherits this session's model and effort.** `<model>` = the alias of this session's model family (`opus`, `sonnet`, `haiku`), never the full ID: the `claude` on PATH can be older than this session and rejects newer IDs. A Fable model becomes `opus` unless the plan's `/usage` shows a separate Fable weekly line and the owner asked for it (`--allow-fable`). `<effort>` = this session's effort level if the session states it, else `effortLevel` from `~/.claude/settings.json`, else leave out `--effort <effort>`. On Windows under Git Bash, prefix `MSYS_NO_PATHCONV=1` so the `/` argument is not rewritten into a path.
  5. Watch it here: put a monitor on new lines of `.loop_state/runs.log` and `logs/loop.log` (a monitor tool, else re-read them when the background task notifies). A monitor expires: re-arm it at once, every time, for as long as the runner lives. On each event — a task started, finished, promoted, skipped, the usage gate pausing, a block — tell the owner in this chat in two or three plain lines, in the owner's language. Never answer an event with "routine, no action needed" and nothing else; say where the loop is. Closing this session stops the loop; `LOOP_TASK.md` keeps the progress, so the next start resumes there.
  6. **Clear blocks without waiting for the owner when you may.** On a block, read the `BLOCKED` line:
     - a permission the queued work needs, with `GRANT: allowlist` → add the exact narrow entry to `.claude/settings.local.json` (step 3);
     - a `TYPE: hard-stop` whose category is granted (e.g. `GRANT: install` for a package install the subtask names) → do exactly what the hard-stop says, check it worked, tick its box with a one-line note of what you ran;
     - then unblock `LOOP_TASK.md` (delete the `BLOCKED` text, `STATUS: idle`), log a decision line for what you did, and tell the owner.
     Anything not granted, and every hard limit 1–6, waits for the owner: report it once with the exact command and your recommended default, and keep watching. Never clear a hard limit 1–6, whatever the grants say. (A narrow allowlist entry under `GRANT: allowlist` is not a hard-limit block: a denied command makes the loop skip, not block, and the session adds the entry before the next run.)
  7. **Check the loop is really running** after any start, restart or unblock: the process check from step 1 lists exactly one runner, and a new `=== run` or `usage:` line appears in `.loop_state/runs.log` within ~5 minutes. No new line → find out why (blocked again, usage gate, the runner died) and fix it. A gap of more than ~30 minutes between log lines while a task was open means the machine slept or the runner died: check and restart it (one runner only).
  8. **No side work.** Besides the setup in steps 2a and 3 (rules, grants, permissions), this session only watches, clears blocks, restarts and reports. It never edits code, reports or a branch the loop finished. New work that turns up (a follow-up fix, an audit, a review finding) becomes a new subtask in `LOOP_TASK.md` before `TYPE: finalize`, or a new task file in `LOOP_TASK_QUEUE/`, and the loop does it.
  9. **When the queue is empty**, the session's last message follows step 3a: it reports what was decided and lists only the items that truly wait for the owner, each with the loop's recommended default. No other questions.
- **Invoked with `--task` (the runner, or a one-off by hand): do exactly one task** by the Steps below, then end the run. Never start the runner from this mode — the runner calls this mode, so starting it here would loop without end.

One task by hand (the same gates, no waiting):

```bash
python3 scripts/jadu-loop/check_loop_queue.py --queue \
  && python3 scripts/jadu-loop/check_usage_margin.py \
  && claude -p "/jadu-loop-best-practice --task" --model opus --permission-mode acceptEdits
```

Not `--dangerously-skip-permissions`: shell commands stay gated by the project's own allowlist. One loop only, never two in parallel. **Do not create a `cron` entry on your own initiative.**

**Usage credits are never spent without the owner's explicit confirmation.** `check_usage_margin.py` reads `claude -p "/usage"` ($0, no model turn): a new task starts only below 80% of the 5-hour limit and 95% of the weekly one; `run_loop.py` sleeps until the reset when a limit is over its line, stops a running task at 90% / 98% (`LOOP_TASK.md` keeps the progress, so it resumes after the reset), and stops and notifies if `/usage` does not say "using your subscription". Always name the model in `claude -p` (`--model opus`). On Windows run `/usage` from PowerShell, never Git Bash (MSYS rewrites it into a path and it becomes a paid model turn). This gate is for the loop only — never apply it to the owner's normal chat.

Keep `LOOP_TASK.md`, `LOOP_TASK_QUEUE/`, `LOOP_TASK_ARCHIVE/` and `.loop_state/` gitignored (add them to the project's `.gitignore`), so the queue survives branch switches and never lands in a PR. **`LOOP_TASK.md` and `LOOP_TASK_QUEUE/` are never committed on the trunk:** step 3 switches to the trunk after every task, and a committed copy comes back with that switch, idle with every box open, so the loop would run the finished task again. Runner mode step 2a checks this at setup. A tracked `LOOP_TASK_ARCHIVE/`, as plain `jadu-loop` suggests, still works: step 3 then commits the archive move on the task branch. Queue files are named `LOOP_TASK_QUEUE/<nnn>-<issue>-<slug>.md`, numbered in steps of ten (`010`, `020`) so name order is run order and a fix can slot in between (`015`).

## Hard limits — these still stop the run

Check these **before** anything else in a subtask (they win over every rule below). If a subtask, a fix attempt or a decision would need any of them, do not do it. Set `STATUS: blocked`, append `BLOCKED — hard limit <n>: <why>` to the line of the subtask that would cross it, push the task branch if it has commits (so the work so far is visible), log, notify, stop. These are the **only** reasons this skill blocks; the gate script then keeps further invocations from running. A human unblocks by fixing the cause (for a `hard-stop`: ticking its box), deleting the `BLOCKED` text, and setting `STATUS: idle`. For a `hard-stop` whose category is granted (see "Standing grants"), the watching chat session does that instead (runner mode step 6); write the category in the line: `BLOCKED — hard limit 7 (grant: <category>): <exact command>`.

1. **Trunk and history.** Never merge a PR, push to the trunk branch, force-push, `git reset --hard`, `git clean`, or rewrite commits that are already pushed.
2. **Production and the outside world.** Never run anything that reaches a live system: sends real email or messages, moves money, deploys, writes production data. A dev/sandbox target is fine **only if the Briefing or the project's rules files (`AGENTS.md`, `CLAUDE.md`) name it**; an unnamed target counts as live. If they name how the project marks production (e.g. an `ENVIRONMENT=` line), check that marker at the start of **every** run; if it says production, block before running anything. The loop's own notification (step 5, through `notify_telegram.py` to the chat the owner configured) is not covered by this limit: send it.
3. **Secrets.** Never read, print, edit or commit `.env`, keys or tokens. Reading only the single production-marker line named as above is the one exception.
4. **Permissions.** Never add to the allowlist, edit agent settings, or use a bypass flag. (This binds the loop's `--task` runs. Only the watching chat session may add a narrow entry, and only under `GRANT: allowlist`.)
5. **Conflicts.** A merge or rebase conflict: `git rebase --abort` / `git merge --abort`, then block.
6. **Outside the branch.** Never close issues, comment anywhere except the task's own PR, or change another repository.
7. **`TYPE: hard-stop`.** The one way a task author forces a pause in this variant. Block there, exactly like a hard limit. Task authors use it only for what the loop cannot do or must not decide: a paid call, a destructive action, a credential, or a step the loop's allowlist cannot run (an install). Never for a design or architecture choice: that is a decision.

## Standing grants

The owner can pre-approve categories of owner-only steps in `.claude/loop-grants.md` in the project, one per line, each with the date and the owner's words. Keep the file untracked (add it to `.gitignore` if missing), like the task files, so a branch switch never hides it:

```
GRANT: install         # package installs a subtask names (pip, npm, npx playwright install)
GRANT: allowlist       # narrow allowlist entries the queued work needs (never a bypass or wildcard interpreter)
GRANT: security-patch  # upgrade a dependency to the lowest version that fixes a known advisory
GRANT: advance         # queue the next phase file when a task finishes (step 3)
```

A granted step is done without waiting for the owner, by whoever is allowed to run it: the loop itself when its allowlist covers the command (e.g. a `security-patch` upgrade through an allowlisted `pip install`), else the watching chat session (runner mode step 6). Every granted step gets a decision line and appears in the report. No file, or a category not in it → the step waits for the owner as before. A grant never lets the loop or the session cross hard limits 1–6 (an allowlist entry added by the watching session under `GRANT: allowlist` is the owner's pre-approval, not the loop editing its own permissions), a paid call, or deleting what the task did not create.

## How to decide

Wherever this skill says "decide", choose in this order and stop at the first that settles it:
1. what the subtask's own `VERIFY` checks;
2. the Briefing and the project's rules files;
3. the project's existing convention for the same kind of change;
4. **recognised best practice**: the official documentation of the framework or tool, OWASP and the advisory databases for security, semantic versioning for upgrades, and what well-maintained projects of the same kind do;
5. the smallest change that satisfies all of the above.

The decision line names the step that settled it (e.g. "because OWASP CSRF guidance"). Design, architecture, security fixes, dependency upgrades, wording and taste are all decisions: decide them, record them, continue. Runner mode step 2a aligns such rules at setup. If one still turns a decidable choice into a stop (e.g. "architecture changes stop for the owner") or removes fix attempts, follow the rule, and name it in the task report's problems section as the cause of an avoidable stop or skip, so the owner can change it.

## The decision log

Every time you decide where `jadu-loop` would have stopped, append one line to a `## Decisions` section at the end of `LOOP_TASK.md` (create it if missing; number on from the highest `D<n>` already there):

```
- D<n> · subtask <N> · <situation in a few words> → chose <what you did> over <the alternative> because <reason, naming its source from "How to decide">. Undo: <how a human reverses it>.
```

Every line has all five parts: situation, choice, alternative, reason, undo. A dependency skip is a decision too. The finalize subtask copies the whole section into the PR body.

## Context you may read

`jadu-loop` reads only `LOOP_TASK.md` and files an `ACTION` names. This variant may also read, **only to make a decision**: the project's rules files (`AGENTS.md`, `CLAUDE.md`), files named in a failure's output, the direct callers/imports and tests of a file the `ACTION` names, config files that define a target the `ACTION` uses (e.g. `wrangler.toml` for a deploy), and the results of a few targeted searches for a named symbol or filename. No open-ended exploration.

**Trunk** = the branch `git symbolic-ref --short refs/remotes/origin/HEAD` points to (strip `origin/`), else `main`.

## Steps

These steps run only in `--task` mode (see Invocation). Without `--task`, start the runner instead.

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

1. **Group / time:** a `GROUP:` runs back-to-back in one invocation. Note the time (`date`) when you start each subtask: it gets **20 minutes** (or the limit the Briefing names). Past that, start no new fix attempt: if its `VERIFY` passes, commit and continue; otherwise Skip it (rule 8), naming the time limit as its last failure. The run itself has no time cap: keep going until no open subtask is left, a hard limit stops it, or the usage gate stops it.
1a. **Usage gate before every subtask:** run `python3 scripts/jadu-loop/check_usage_margin.py` (on Windows: `python`, from PowerShell, never Git Bash).
   - Exit 0 → start the subtask.
   - Output says `usage check failed` or `could not read` → `/usage` was slow, which is not a limit: run it once more; still unreadable → start the subtask anyway and say so in the log (the runner's watchdog still guards the ceilings).
   - Anything else (a limit over 80% of 5-hour / 95% of weekly, or not on the subscription) → start nothing more: log the run as `in progress`, notify (step 5), end the run. Not a block, not a decision; the next invocation resumes at this subtask.
2. **Dependency check:** if the subtask's `ACTION` or `VERIFY` needs a file or result that a `SKIPPED` subtask was supposed to produce, or it shares a `GROUP:` with one, mark it `SKIPPED — depends on <N>`, log a decision, and move on. Chains: a subtask depending on that one is skipped too.
3. **ACTION:** run it as written. If it is ambiguous or underspecified, choose by "How to decide", log a decision, and run that.
4. **Denied command:** a script the project itself defines (`package.json`, `Makefile`, …) that is already allowlisted and runs the same tool with the same arguments is an equivalent — use it and log a decision. Invoking the binary yourself by another route (`node_modules/.bin/…`, `cmd /c`, `bash -c`, another shell, a script you write) is a bypass. No equivalent → Skip at once, no fix attempts: `SKIPPED — command denied: <cmd>; no allowlisted equivalent`.
4a. **"Wait for a human" without `TYPE: hard-stop`:** first do every part the loop can do, then decide the rest by "How to decide". Only these are human-only: a credential or key that must be entered or tested, a payment or paid call, anything that reaches a live system, merging into the trunk, and deleting or overwriting what the task did not create. One of those → Skip with `SKIPPED — needs human confirmation: <what>`, log a decision, PR becomes a draft; prepare the check so it costs the human a minute (start the preview, list the exact URLs or commands) and write the loop's own verdict and recommended default in the decision. Everything else is a decision, never a skip: an audit or a check the loop can run, an install or upgrade the grants cover, a design or architecture choice, a taste or wording call (a number to round, a title, a small rewrite). An audit whose tool will not start is run another allowlisted way, or the loop records what it could check and decides the verdict.
5. **VERIFY passes:** stage exactly the files this subtask touched, commit with the subtask's message (nothing changed → no commit), tick its box, continue.
5a. **Found outside this subtask's files** (a stale comment, a wrong string, a bug the check did not cover): do not fix it inside this subtask and do not turn it into a question. Append a new subtask after the last open one (before `TYPE: finalize`) with `TYPE: code`, an exact `ACTION` and a `VERIFY`, log a decision naming what you found, and run it in turn like any other subtask. Anything that would cross a hard limit stays a decision line marked `follow-up for a human`.
6. **VERIFY fails:** if the only failures are in tests this task never touched, do rule 7 first. Otherwise up to **3** targeted fix attempts in total, re-running `VERIFY` after each. Fix attempts touch only files the subtask's `ACTION` names or the subtask created (including tests the project's rules require for them). Never:
   - edit the `VERIFY` line or any `ACTION` in `LOOP_TASK.md`;
   - skip, delete, loosen or mark-as-expected-failure a test or assertion the `VERIFY` runs, including pre-existing ones.
7. **Red baseline:** check the failing tests on the commit this task branched from, without this task's work: run `git merge-base <trunk> HEAD`, then `git worktree add --detach .loop_state/baseline <the SHA it printed>` (two plain commands: the allowlist cannot match a `$(...)` substitution, so that form is denied every time), run just those tests there, `git worktree remove --force .loop_state/baseline`. If they fail there with the same error, the baseline was already red: commit the subtask, tick it with `— VERIFIED ON RED BASELINE: <test ids as the runner prints them>`, log a decision. A later subtask whose only failures are those same tests with the same errors does the same (marker + decision) without re-checking. A different error, or a test that passes on the baseline, is this task's failure → rule 6. The PR becomes a draft.
8. **Still failing after 3 attempts (or past the time limit) → Skip** (never the `TYPE: finalize` subtask: see rule 10):
   - copy `git diff -- <files it touched>` (at most ~200 lines) into a `## Skipped` section of `LOOP_TASK.md` under the subtask number, then restore those files (`git restore`; remove files it newly created) so later subtasks start clean;
   - append `SKIPPED — <original failure>; tried <1>, <2>, <3>; still <final failure>` to the subtask line (it stays `- [ ]`);
   - log a decision, continue with the next independent subtask.
9. **`TYPE: review-checkpoint` → self-review instead of pausing:** read the full branch diff (`git diff <trunk>...HEAD`), compare it against what the checkpoint's `ACTION` says a human should look at and against the Briefing, and re-run the test command the Briefing names (none named → re-run every completed subtask's `VERIFY`). Where the check needs human senses you lack (looking at a rendered page), use an objective proxy: any check or render/screenshot tool the project already has, run at the viewports the `ACTION` or the project's rules name; or a read-only measuring script you write in a scratch directory outside the repo (it may load pages, screenshot and time them, never write to the repo); else a structural comparison against the reference the `ACTION` names and say in the decision that a human look is still recommended. Problems found → fix them within rule 6's limits, re-review; still wrong after 3 attempts → Skip. Clean → tick the box, log a decision with what you reviewed.
10. **`TYPE: finalize`:** `git push`, then open the PR — **as a draft** if any subtask was `SKIPPED`, verified on a red baseline, or any decision says a human look is still recommended. If the branch already has an open PR (`gh pr view --json url,state`), update that PR's body instead of opening a second one. The PR body ends with `## Decisions` (verbatim), `## Skipped` (verbatim, diffs in collapsed `<details>` blocks), and what was verified where. Never merge. **Finalize is never skipped**, because a skipped finalize leaves the task open forever and the queue never moves: if the push or the PR still fails after 3 attempts (or the project has no remote), write the PR body to `.loop_state/pr-<BRANCH with / replaced by ->.md`, log a decision naming the failure, tick the box, and go on to step 3.

**Before the run ends**, however it ends: stop every preview server, watcher or background process this run started.

### 3. Finish the task, then promote the next one

When the finalize subtask is done: move `LOOP_TASK.md` to `LOOP_TASK_ARCHIVE/<today>-<BRANCH with / replaced by ->.md` (its Decisions and Skipped sections go with it; if that name exists, add the task name). If git tracks `LOOP_TASK_ARCHIVE/`, commit the new archive file on the task branch and push it (untracked: just move it).

**Phase chaining:** if the queue is empty, the grants file has `GRANT: advance`, the Briefing names the next task file (a `NEXT:` line, e.g. `NEXT: phases/phase-3.md`), and that file already says `STATUS: idle`, copy it to `LOOP_TASK_QUEUE/` and log a decision line. Never change a draft's status to make it run: a file that is still a draft is not queued; say in the report's next-steps section that it needs `/jadu-loop-prepare` first. The next phase builds on this one's unmerged work, so its first subtask must name this task's branch as its base (`git switch -c <new> <this branch>`); if it does not, add that to its Briefing as a decision. A project rule that forbids advancing wins: then follow it and name the rule in the report's problems section.

Then `git switch <trunk>`, so the next task never branches off unmerged work by accident. **A `LOOP_TASK.md` that is there right after the switch is stale:** the finished one was just archived, so this is the trunk's committed copy (see Invocation). Never run, promote over or delete it: set its `STATUS: blocked`, add a line `BLOCKED — hard limit 1: LOOP_TASK.md is committed on <trunk>; untrack it in a setup PR (runner mode step 2a)`, log, notify, end the run. Otherwise, if `LOOP_TASK_QUEUE/` contains `*.md` files, move the first one in name order to `LOOP_TASK.md` (untracked files, so this is a plain move: never commit on the trunk), make sure it says `STATUS: idle`, name it in the log and the notification, and **end this run**. The next invocation starts it with a fresh context (its first subtask creates its own branch), so nothing from the finished task bleeds into the new one.

**A promoted task that builds on this one** (its `BRANCH:` is this same branch, or its Briefing says it builds on this task's work) must start from this branch, not the trunk: from the trunk it would leave out this branch's unmerged changes, and two branches that edit the same files separately conflict when the second PR is merged. If its first subtask does not already start from this branch (`git switch <this branch>`, or `git switch -c <new> <this branch>`), add that to its Briefing and log a decision.

### 3a. The final report has no open questions

The run's last message (and the PR body) reports; it does not ask. Every open item is one of:
- **Decided**: a `D<n>` line already in the log. Say what was chosen; the owner overrides it by saying so.
- **Waiting for you**: only a hard limit or a confirmation only a human can give (the human-only list in rule 4a). Each line names the exact command or URL, the loop's verdict, and the recommended default ("Say go and I run X").

If something could have been decided and was not, decide it now, log it, and report it as Decided. A project or global output style with a "Need from you" or questions section shows only the **Waiting for you** items there. Never list a choice the loop could have made as a numbered question. This applies to the watching chat session's messages too, not only to the run and the PR: "should I upgrade X?" or "accept these four proposals?" are decisions, not questions.

### 4. Log

Append exactly one line to `logs/loop.log` (never rewrite the file), in exactly this shape, with the timestamp taken from `date -Iseconds` (never written from memory):

```
<timestamp> | <branch> | done: <subtask list or none> | skipped: <subtask list or none> | decisions: <n> | <in progress / blocked / complete / complete, next promoted (<file>)>
```

### 5. Notify

Never send a test message to the notification channel (owner's rule 2026-10-18): it is the owner's real channel.

Do not call `notify_telegram.py` yourself. Write the message to `.loop_state/telegram.md` (UTF-8, overwrite). `run_loop.py` sends it right after this run ends and deletes the file, so the message goes through the runner's environment, which holds the bot token; a run by hand without the runner has it sent at the next runner start. A failed send is kept as `.loop_state/telegram-unsent-*.md` and logged in `.loop_state/runs.log`. The owner reads these without the code open. Write **only**:
- **one task report when the task is finished** (finalize done, archived, next promoted);
- **one message when the run fails or stops early**: a hard limit, the usage gate, or anything else that ends the run before the task is done.

A subtask that finishes or is skipped sends nothing; it appears in the task report.

Write in the language the Briefing or the project's rules files use, else English: short sections with an emoji heading and short bullets, no raw error text or codes. Explain what changed in plain words, so it makes sense without opening `LOOP_TASK.md`. A technical token that must appear (a file path, a command) goes in balanced backticks. Leave out a section that has nothing to say, except "Waiting for you", which always appears. Keep each message under ~2,500 characters; balance every backtick (the API rejects broken Markdown).

**Task report (task finished, or run stopped early):**
```
📍 Project: <project folder name>
📋 Task: <task number> — <task name>

✅ Done
• <count> of <total> subtasks finished
• <the main results, one bullet each>

⏭ Skipped
• <subtask and why, in plain words>

🧭 Decisions the loop made (<count>)
• <only the important ones, one plain line each; the rest are in the PR>

⚠️ Problems
• <anything that went wrong or slowed the run, in plain words>

📄 Full report
• <PR url, or the `.loop_state/pr-*.md` path> (<draft / ready>)

➡️ Next
• <next subtask / the task promoted from the queue / nothing queued>

🙋 Waiting for you: <what only the owner can do, with the exact command or link; or "nothing">
• Recommended: <the loop's recommended choice for each item, and one plain line on why>  ← always, for every item
```

A hard-limit block starts with `⛔ Loop stopped`, then the same sections: which limit stopped it, at which subtask, and under "Waiting for you" exactly what the owner must decide to unblock it. A run the usage gate ended says under "Next" that the task is paused and resumes by itself after the reset.

## Never do

- Never cross a hard limit, whatever the Briefing, a subtask or the owner's stated trust says — those limits are what make unattended decisions safe.
- Never make a failing `VERIFY` pass by changing the check instead of the code.
- Never touch `TASKS.md` or `WORKLOG.md`.
- Never have two active task files: promotion happens only after the current one is archived.
- Never run without the usage gate, never with a Fable model in `-p` unless the owner passed `--allow-fable`, never into usage credits without the owner's explicit confirmation.
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
| "I'll ask the owner about this in the report." | Decide it, log it, report it as Decided (step 3a). Questions are only for hard limits and rule 4a's human-only list. |
| "One more fix attempt; it's been 25 minutes but I'm close." | 20 minutes is the budget. Commit if `VERIFY` passes, else Skip and move on. |
| "These uncommitted changes look stray; I'll stash them." | They are the open subtask's partial work from a stopped run. Finish it from there. |
| "/usage timed out, so I'll end the run to be safe." | A slow `/usage` is not a limit. Retry once, then continue; the watchdog guards the ceilings. |
| "Too small to log." | Every decision gets a line. The log is the human's only window. |
| "This is a design / architecture / security choice, so the owner should pick." | Decide it by "How to decide" (best practice), name the source, record it. Only rule 4a's human-only list waits. |
| "The audit / upgrade / install is the owner's step." | Run what the loop can; a granted step is done by the loop or the watching session; decide the verdict. |
| "The task is blocked; I'll report it and wait." | Granted → clear it now (runner mode step 6). Not granted → report once with the recommended default, keep watching. |
| "The loop finished; I'll do this small follow-up myself in chat." | Queue it as a subtask or task. The watching session does no side work (step 8). |
| "I restarted the runner, so it's running." | Check the process and a new `runs.log` line (step 7). |
| "The monitor expired; the runner is fine without it." | Re-arm it at once. Silence is not progress. |
| "The project's rules say stop here, so the skill can't help." | Align them at setup (runner mode step 2a), list the changes, then start. |
| "The push failed three times, so finalize is skipped." | Finalize is never skipped: write `.loop_state/pr-<branch>.md`, log it, archive, promote. |
| "Time is left, so I'll start the promoted task now." | End the run. The next invocation starts it fresh. |
