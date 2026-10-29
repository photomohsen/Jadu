# Loop Task: <short-kebab-case-name>

STATUS: idle
BRANCH: <type>/<kebab-case-branch-name>

## Briefing

<!--
Everything jadu-loop needs to know that ISN'T already obvious from a
subtask's own ACTION/VERIFY. Keep this short — jadu-loop reads it once
per invocation, so every line here costs tokens on every run. Good things
to put here:
  - Why this task exists / what problem it fixes (root cause, if a bug fix)
  - Any environment quirk that applies to EVERY subtask (e.g. "this project
    runs in a container — all test/lint commands below must be run inside
    it, not on the host")
  - Explicit statement of what's OUT of scope, if that's not obvious
Do NOT put here: step-by-step instructions (those belong in each subtask's
own ACTION), or anything only relevant to authoring this file (that belongs
in your own working notes, not in what jadu-loop reads every run).
-->

## Subtasks

<!--
One block per subtask. Required fields: the checkbox line (unique number,
never reused even if you resequence), TYPE, ACTION, VERIFY. Optional: a
GROUP: line (see below).

TYPE values in use:
  - branch            first subtask of a task: create+checkout the branch
  - code              an edit to source/content
  - test              run your test suite and/or lint/style checker
  - review-checkpoint deliberate pause for a human to eyeball something
                       (jadu-loop treats this exactly like a blocked VERIFY:
                       STATUS -> blocked, and it stops)
  - finalize          push the branch + open a PR; NEVER merges
  - hard-stop         jadu-loop-best-practice only: the one forced pause in
                       that variant. Use it only for what the loop cannot do
                       or must not decide (a paid call, a destructive action,
                       a credential, an install its allowlist cannot run),
                       with the exact command. Never for a design choice.

jadu-loop-best-practice extras (plain jadu-loop ignores them):
  - NEXT: <task file> in the Briefing names the task that builds on this one
    (queued only with GRANT: advance; see the skill's step 3).
  - The loop appends a "## Decisions" section (and "## Skipped" when needed)
    at the end of this file; do not write them yourself.
  - Queued files live in LOOP_TASK_QUEUE/<nnn>-<issue>-<slug>.md, numbered
    010, 020, ... so name order is run order and a fix can slot in (015).

ACTION must be fully self-contained: exact file(s), exact command(s), no
research needed. If executing it requires reading a file the ACTION doesn't
name, or making a judgment call, it's not ready for jadu-loop yet — that
judgment call belongs in a normal supervised session, not in this file.

VERIFY must be a single objective, scriptable check whose pass/fail is
unambiguous — a grep, an exit code, a test command, a string comparison.
See docs/jadu-loop-authoring-guide.md before writing anything that checks
rendered/templated output, or that asserts "X stayed identical to Y" — both
have specific footguns documented there.

GROUP: <name> is optional. Give two or more subtasks the same GROUP value
ONLY when a later one in the group genuinely needs conversational context
built by an earlier one in the SAME invocation (not just "these feel
related"). Grouped subtasks always run back-to-back in one invocation, but
each subtask's own VERIFY still runs immediately after its own ACTION —
GROUP does not let a later subtask's VERIFY pass because an even-later
subtask will eventually create what it's checking for. Order every subtask
(grouped or not) so its VERIFY only ever depends on artifacts a
STRICTLY LOWER-numbered subtask already produced.
-->

- [ ] 1
  TYPE: branch
  ACTION: `git checkout main && git pull --ff-only && git checkout -b <type>/<kebab-case-branch-name>`
  VERIFY: `git branch --show-current` prints exactly `<type>/<kebab-case-branch-name>`

- [ ] 2
  TYPE: code
  ACTION: <exact file, exact change, exact commit message>
  VERIFY: <single objective check>

- [ ] 3
  TYPE: test
  ACTION: <your test command> && <your lint/format command, scoped to the files subtask(s) above touched — never run repo-wide unless the repo is already 100% clean>
  VERIFY: exit code `0`, no failing tests, no style violations reported on the touched file(s)

- [ ] 4
  TYPE: finalize
  ACTION: `git push -u origin <branch>`, then open a PR via your CLI/API of choice with a title and body summarizing the change. Never merge.
  VERIFY: PR exists and is open (e.g. `gh pr view <branch> --json state -q .state` outputs `OPEN`)
