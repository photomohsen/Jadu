# Jadu Loop Prepare — make the project's tasks a ready loop queue

This skill takes the tasks the project already has and turns them into a queue that `jadu-loop-best-practice` can run from start to end without stopping for anything it can decide. The owner does not explain the tasks again. It prepares; it does not run tasks.

## What the owner says

Usually just:

```
/jadu-loop-prepare
```

Optional extras, each on its own line:

```
Only: phase-3, phase-4          # limit to these existing tasks
Add: <a new task in one line>   # a task not yet written anywhere
Grants: install, allowlist, security-patch, advance
Start: yes
```

## Where the existing tasks come from

Search the project in this order and take every task that is not done yet:
1. **Task files the project already has**: a `phases/` folder or similar (`tasks/`, `milestones/`), its README's status table, and any draft or ready `LOOP_TASK`-style file outside the queue.
2. **The plan**: `docs/PLAN.md`, a roadmap or `TASKS.md`, for phases or milestones that have no task file yet.
3. **Open follow-ups from finished tasks**: decision lines marked `follow-up for a human` in `LOOP_TASK_ARCHIVE/`, the "Next" section of the last task report, and any open-questions file the project keeps. Each one becomes a subtask in the right task, or a small task of its own placed before the work that depends on it (e.g. a security upgrade before the next phase).

A task is done when its archive file exists and its report says Complete, or the project's status table says so. A task whose draft is vague is still taken: fill in the exact subtasks from the plan, the design docs and the code, and record each choice as a decision. The one exception: a draft whose subtasks depend on code an unfinished task will write (e.g. phase 4 after a phase 3 that has not run) is not filled in now, because that code does not exist yet. Leave it a draft, list it as "after <task>", and let that task's rewrite subtask or a later `/jadu-loop-prepare` fill it in.

Missing extras get these defaults, recorded in the summary:
- **Which tasks**: every open task found above.
- **Order**: the project's own order (phase numbers, plan order); follow-up fixes go before the task that builds on the code they fix, even when that task is already queued, as long as it has not started (step 4 numbering leaves room).
- **Done means**: the task's own Definition of Done in the plan, else derived from its goal and the project's checks (tests, lint, build).
- **Grants**: what the owner has already said go to in this project (the project's rules files, its open-questions file, decision lines in `LOOP_TASK_ARCHIVE/`, the agent's saved memory if it has one), quoting those words with their source. Nothing said → no grants file lines.
- **Start**: no. Prepare and show the queue.

Do not ask questions about design, architecture, naming or scope. Decide them by "How to decide" in `jadu-loop-best-practice` and write the decision into the task's Briefing. Ask only for a credential, a paid call, a live target or a destructive action whose scope cannot be read from the project.

## Steps

### 1. Read the project, once

- The rules files: `CLAUDE.md`, `AGENTS.md`, and any loop rules or plan they point to.
- What exists already: `LOOP_TASK.md`, `LOOP_TASK_QUEUE/`, `LOOP_TASK_ARCHIVE/`, `.claude/loop-grants.md`, `.claude/settings.json` and `settings.local.json`.
- The project's checks: test, lint, type and build commands (`pyproject.toml`, `package.json`, `Makefile`, the README).
- The trunk branch and the current branch.

A task already active in `LOOP_TASK.md` stays where it is and is never edited here. New tasks go into the queue after it.

### 2. Align the project's loop rules

Exactly as `jadu-loop-best-practice` runner step 2a. Rewrite only rules that override decide-and-continue: a stop for a decidable choice, "no fix attempts", "no automatic advance", an owner step a grant covers. Keep each rule's number, add the date. Never loosen hard limits 1–6, paid-call or secrets rules, or read-only rules for other folders. Rewrite the same rules wherever a phase file or task Briefing repeats them (the files written in step 4 inherit the new wording). Commit the rules files on the `loop/setup-<today>` branch and open its PR, as step 2a says. Never commit on the local trunk: the trunk is never pushed, so that commit would make it diverge from `origin` and block the loop at its next `git pull --ff-only`. Clean tree only; a dirty tree → no commit, say why. Keep the old and new wording for the summary.

### 3. Write the grants file

`.claude/loop-grants.md`, one `GRANT: <category>` per line with the date and the owner's words. Categories: `install`, `allowlist`, `security-patch`, `advance`. Keep lines already there. The file stays untracked: add `.claude/loop-grants.md` to `.gitignore` if missing.

### 4. Write one task file per task

An existing task file (a phase file) is the source: keep its subtask numbers, `MANDATORY:` marks and Definition of Done, rewrite only what is vague or conflicts with the best-practice skill, and set it ready (`STATUS: idle`). The project's status table (if it has one) changes only inside a commit: when step 2 opens a setup PR, mark the task ready there in the same commit; otherwise leave the table to the task's own finalize subtask. Never leave it as an uncommitted edit, which would travel across branch switches into an unrelated PR. The queue file is a copy; the original stays in its folder. Start new files from `templates/jadu-loop/LOOP_TASK.skeleton.md` and follow `docs/jadu-loop-authoring-guide.md`. Name the file `LOOP_TASK_QUEUE/<nnn>-<issue or task>-<slug>.md` with a three-digit number in steps of ten (`010`, `020`, `030`), going on from the highest number already in `LOOP_TASK_QUEUE/` (`010` when it is empty; archive files are named by date and have no number, so never take one from there), so name order is run order and a later fix can slot in between (`015`). A follow-up fix that must run before a queued task that has not started gets a number between. The runner promotes from the queue by itself (best-practice runner `--queue`), so no `LOOP_TASK.md` is needed to start. Each file has:

- `STATUS: idle` and a `BRANCH:` of `<type>/<slug>`.
- **Briefing**: why the task exists, what is out of scope, environment quirks, the decisions already taken for it (with source), and a `NEXT:` line when the following task builds on this one.
- **Subtask 1, `TYPE: branch`**: branch from the trunk, or, when this task depends on the previous task's unmerged work, name that branch as the base (`git switch -c <new> <previous branch>`) and say so in the Briefing.
- **`TYPE: code` subtasks**: one focused change each. The `ACTION` names exact files and exact commands, needs no research, and ends with an exact commit message.
- **A `VERIFY` per subtask**: one objective, scriptable check. Follow the authoring guide: no exact match on rendered output, a check for every "keep X identical" detail, and each check depends only on lower-numbered subtasks.
- **A `TYPE: test` subtask** after the code it covers: the project's full test command plus lint and type checks scoped to the touched files.
- **A `TYPE: review-checkpoint`** only where the loop must self-review a visible result (a page, a report). The best-practice loop self-reviews it; it does not stop.
- **A `TYPE: hard-stop`** only for a paid call, a destructive action, a credential, or an install the loop's allowlist cannot run. Write the exact command. Never for design or architecture.
- **A last `TYPE: finalize` subtask**: update the project's status table if it has one and step 2 did not, then push and open a PR (or write `.loop_state/pr-<branch>.md` when the project has no remote or the push fails), never merge. It is never skipped (best-practice rule 10).

Keep subtasks small enough to finish within the project's per-subtask time limit.

### 5. Pre-flight check, as its own pass

For every file, subtask by subtask (authoring guide rule 6):
- everything a subtask needs is made by a strictly lower-numbered subtask, or exists already;
- every `VERIFY` can fail, and passes only when the `ACTION` worked;
- every shell command in an `ACTION` or `VERIFY`, plus the archive and promote moves and the gate scripts, is covered by the project allowlist. Missing entries → under `GRANT: allowlist`, add the narrow entries to `.claude/settings.local.json` (untracked; add it to `.gitignore` if missing, no commit) and list them; without that grant, list them for the owner's yes.

Fix what the pass finds before the summary.

### 6. Show the queue, then start or stop

One short message, in the owner's reply style:
- the rules changed in step 2, old and new wording, and the setup PR's link (the runner starts after the owner merges it);
- the grants written;
- where each task came from (phase file, plan section, follow-up);
- a table: file, task, number of subtasks, hard stops (with the exact command), base branch;
- the decisions taken while preparing, each with its source;
- **Waiting for you**: only hard stops and the human-only items from `jadu-loop-best-practice` rule 4a, each with a recommended default.

`Start: yes` → invoke `/jadu-loop-best-practice` (runner mode); with a setup PR open, it starts the runner once the owner has merged it. Otherwise end with the one line that starts it.

## Never do

- Never run a task's subtasks here; the loop runs them.
- Never edit the active `LOOP_TASK.md`. Never overwrite or renumber a file already in the queue without the owner saying so; inserting a new file between two queued ones is fine.
- Never write a `VERIFY` that always passes or always fails.
- Never add a hard stop for a choice the loop can decide.
- Never add a bypass flag or a wildcard interpreter to the allowlist.
- Never touch the folders the project marks read-only.
