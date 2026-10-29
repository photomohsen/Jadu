# Authoring a `LOOP_TASK.md`

`jadu-loop` is deliberately dumb by design — it executes exactly what a subtask's `ACTION`/`VERIFY` says, with no research and no judgment calls. That means every bug in an unattended run is almost always an authoring bug in `LOOP_TASK.md`, not a mistake the loop made. This guide is a set of rules distilled from running `jadu-loop` on real, multi-day, 30+ subtask tasks — each one below corresponds to a bug that actually shipped in a `LOOP_TASK.md` and was only caught once the loop hit it.

## 1. A `test` subtask must cover *everything* your project checks, not just the part you thought of first

If your project has two independent checks — say, a test suite and a separate style/lint checker — a `test` subtask that only runs the test suite will let a style violation ride straight through to `finalize` with nobody noticing. Any `LOOP_TASK.md` with a `finalize` subtask must have a preceding `test` subtask whose `ACTION` runs **all** of your project's checks, e.g.:

```
ACTION: <test command> && <lint/style command, scoped to touched files>
```

## 2. Scope lint/style checks to the files the task actually touched — never run them repo-wide, unless the repo is already 100% clean

Most real codebases have pre-existing style debt somewhere unrelated to your task. A repo-wide `lint --check` will false-block every future `finalize` on inherited debt that has nothing to do with what this task changed. Pass an explicit file/path list — exactly the file(s) the task's own `code` subtask(s) edited — never a bare repo-wide invocation.

## 3. `GROUP:` only forces subtasks to run back-to-back — it does NOT defer any subtask's `VERIFY` until the group finishes

`jadu-loop` still runs each subtask's own `ACTION` → `VERIFY` in order, one at a time, even inside a `GROUP`. Grouping only guarantees they happen in the same invocation with no context-loss gap between them — it does not mean a later subtask's artifact "counts" for an earlier one's check.

**Failure shape:** subtask 7 (register a route pointing at a controller) and subtask 8 (create that controller) share a `GROUP`. Subtask 7's `VERIFY` checks that the route resolves to the target controller class — but that class doesn't exist until subtask 8 runs. Subtask 7 fails `VERIFY` even though its own `ACTION` was correct, because the check was written against something a later subtask in the same group would create.

**Rule:** order every subtask (inside a `GROUP` or not) so its own `VERIFY` only ever depends on artifacts a **strictly lower-numbered** subtask already produced — never "earlier in the same group" as a stand-in for actually checking the number.

## 4. Never write an exact-match `VERIFY` against rendered/templated/composed output

**Failure shape:** a placeholder view correctly extends the real shared layout (the right call — it matches what the final version will do), but its `VERIFY` asserted the *entire* trimmed render equaled one bare string. That's impossible once real header/footer/wrapper chrome from the layout surrounds it. The `ACTION` was right; the `VERIFY` assumption was wrong.

**Rule:** whenever a `VERIFY` checks rendered/templated/compiled output — a view, a compiled asset, anything composed from other files — assert with a substring/contains check against the expected fragment, never an exact string/byte match, unless the `ACTION` explicitly produces standalone output with nothing else wrapping it.

## 5. A `test` subtask's own assertions can create the exact same forward-dependency bug as rule 3 — and it's easy to miss on a read-through

**Failure shape:** a `test` subtask right after a placeholder-content subtask planned several test cases. Some were satisfiable immediately (e.g. a 404 check); others asserted on *real* content that wouldn't exist until a much later, differently-grouped subtask built it. The file read as well-reasoned line by line — the gap is only visible when you ask, case by case, "does the artifact this specific assertion needs already exist by this subtask's position?"

**Rule:** split a `test` subtask's cases by their actual dependency, not by which subtask they were drafted alongside. Move content-dependent cases to a `test` subtask positioned after the subtask that actually builds that content.

## 6. Required pre-flight check before any `LOOP_TASK.md` is considered ready to run

Not optional, not "read it once and it looked fine." For every subtask — and *especially* every `test`-type one — list what it assumes already exists (a file, a config key, a function, a route, real rendered content) and confirm each was produced by a subtask with a strictly lower number. Never accept "earlier in the same `GROUP`" as a substitute for checking the real number, and never assume a subtask is safe just because it reads as internally coherent — internally coherent and correctly *sequenced* are different properties, and only one of them is checked by reading top to bottom once. `assertSee`/exact-match-style assertions against real content are the highest-risk category: a test can be perfectly correct code and still be scheduled before the thing it asserts on is built. Do this as its own explicit pass, subtask by subtask — not folded into a general read-through.

## 7. When a subtask says "keep X identical to a reference implementation," its `VERIFY` must directly assert X survived — not just that the surrounding code exists

**Failure shape:** an `ACTION` said to duplicate an existing function into a new location, "changing only Y, everything else stays identical" — including some specific behavior (e.g. an encrypted ID appended to a return URL). The implementation silently dropped that detail. `VERIFY` only checked that the new function/route existed and had the right name — true regardless of whether the preserved detail survived — so it passed clean. A later subtask then built on top of the (silently regressed) output, cementing the bug as "tested and passing," and it only surfaced several subtasks later when something downstream had no way to use the missing piece.

**Rule, two parts:**
1. Any `VERIFY` for a "duplicate-but-keep-X-identical" subtask needs an explicit check for the literal preserved fragment itself — not just proof the surrounding function/route was created.
2. A `test` subtask immediately following such a `code` subtask must include a case for the *specific reason* that code needed to diverge from the shared original — not only the surface difference that motivated writing a new subtask in the first place, but the invariant the `ACTION` explicitly called out as unchanged.

## 8. Use `TYPE: review-checkpoint` for deliberate human-review pauses, not a fake `VERIFY` that always fails

Some subtasks — a visually significant redesign, a payment-flow change, anything you genuinely want eyeballed before the loop continues — deserve a mandatory stop even when nothing is technically broken. `jadu-loop` treats `TYPE: review-checkpoint` exactly like a blocked `VERIFY`: it sets `STATUS: blocked`, notes it's a deliberate pause (not a failure), commits, and stops until you manually set `STATUS: idle` again. Use this instead of writing a `VERIFY` designed to fail — that pollutes the run log with a fake failure and makes real blocks harder to spot.

## 9. Writing a task for `jadu-loop-best-practice`

The best-practice variant runs the same file, but it never pauses for a `review-checkpoint` — it self-reviews and continues — and it resolves gaps instead of stopping. Write the file so its decisions land where you want them:

- **Need a real stop?** Use `TYPE: hard-stop`. It is the only subtask type that pauses this variant; a `review-checkpoint` or an `ACTION` that says "wait for X" does not. Keep it for what the loop cannot do or must not decide (a paid call, a destructive action, a credential, an install its allowlist cannot run), with the exact command; a design or architecture choice is a decision, not a hard stop.
- **Name the production marker** in the Briefing (e.g. "production = `ENVIRONMENT=production` in `.env`"). The loop checks it every run and refuses to run against production.
- **Name every dev/sandbox target** the subtasks may reach (a dev worker URL, a sandbox payment API). An unnamed target counts as live and blocks.
- **Name the project's test command** in the Briefing. Self-review re-runs it at every `review-checkpoint`.
- **Order matters more, not less:** a skipped subtask also skips everything that depends on it, so rules 3, 5 and 6 decide how much work survives one failure.

## General shape to aim for

- **`branch`** subtask first, always.
- **`code`** subtasks: one focused change each, self-contained `ACTION`, objective `VERIFY`.
- **`test`** subtask(s): full test suite + full lint/style, scoped to touched files, positioned after every `code` subtask whose output it needs.
- **`review-checkpoint`** subtasks: sparingly, only where a human genuinely should look before continuing.
- **`finalize`** subtask last: push + open PR (never merge), with a `VERIFY` that confirms the PR exists and is open.
