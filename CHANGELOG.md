# Changelog

All notable changes to the public Jadu repo. Newest first. This project uses simple,
date-stamped version tags (no strict semver — it's a docs/skills collection).

## [0.8.0] — 2026-07-20

Session-behavior redesign, driven by real usage friction: tasks getting created and
forgotten mid-session, task-doc formatting inconsistency, hard-to-verify commit/push
success, and inconsistent status-icon reporting. Grounded in a live fetch of upstream
[25mordad/Jadu](https://github.com/25mordad/Jadu)'s current files, a direct read of this
repo's own prior skills, and a friction-mining pass over real session history. Applies to
Claude Code and Codex identically.

- **Bidar absorbs Kar.** Starting a session and managing `TASKS.md` are one skill now —
  `jadu-bidar`. First call each session does setup (pull, read context, expand tasks,
  start the reminder); every call, first or not, also renders the live backlog as a table
  and handles add/update/list/reprioritize. `jadu-kar` is kept as a thin redirect stub on
  both agent surfaces, not deleted, so existing habit doesn't hit a dead end.
- **Ambient task logging.** Any prompt describing real work becomes a task in `TASKS.md`
  immediately — no more waiting for an explicit task-add or for `jadu-payan` to catch up at
  close. Read-only questions and lookups never become tasks.
- **New: Bazgu (بازگو — "retell").** `jadu-bazgu` is a per-request, on-demand skill: log
  the request as a task, restate the understood scope back (a statement, not a question),
  offer 2–3 concrete options instead of just the literal ask, wait for explicit
  confirmation, then execute. Not a session-wide mode — the next prompt without it goes
  back to ambient logging and direct execution.
- **Payan is now unambiguously terminal.** Stated plainly in the skill itself: Payan never
  ends with a question, a "Need from you" section, or anything requiring a reply — it runs
  brief → docs → commit → push → report, then stops.
- **Rigid commit/push confirmation.** Both Payan and Push now report a fixed-format line —
  `✅ Committed <hash> to <branch>, pushed to <remote>/<branch> — N files left unstaged`, or
  a clear `⚠️ NOT pushed: <reason>` — plus the direct commit URL, so success is
  independently checkable instead of just asserted.
- **`git add -A` gets one explicit, opt-in escape hatch.** Still banned by default in Payan
  and Push — staging stays session-scoped. But if the user's own message for a given push
  explicitly says something like "stage everything," that one call runs a real
  `git add -A`. Never triggered by anything softer, never the default.
- **Payan: mandatory decisions/preferences self-check.** Before writing the session brief,
  Payan now runs an internal check — what got decided this session and why; did anything
  happen that should change future behavior — instead of a self-assessed field that's easy
  to leave thin.
- **Payan: cross-doc date-drift flag.** When updating `TASKS.md`, Payan compares completion
  dates against `PROJECT.md`'s own dates for the same milestone and flags a mismatch in its
  report — flag only, never auto-fixed.
- **Payan: conditional `README.md` refresh**, adopted from upstream — when a session
  changes architecture, setup, or CLI-facing behavior, Payan refreshes the relevant part of
  `README.md` too, not just `WORKLOG.md`/`TASKS.md`/`AGENTS.md`.
- **Zad: closing context-compaction nudge**, also adopted from upstream — after a long
  setup conversation, Zad now suggests compacting/summarizing before moving on.
- **Bina: explicit completion-gate language**, no behavioral change — states plainly what
  was already true: a task counts as done when Bina is satisfied, not when the executor
  says so. "Close enough" was already not an exit condition; now it says so up front.
- Task listings render as a table (`# · Priority · Status · Description`) everywhere tasks
  get shown, not just inside `TASKS.md`'s own format.

## [0.7.0] — 2026-07-18

- Added **Bina** as Jadu's explicit reviewer loop on both agent surfaces:
  `.claude/commands/jadu-bina.md` and `.codex/skills/jadu-bina/`.
- Bina's job is to review active work independently, log confirmed findings into Jadu task
  records, hand concrete fixes back to the executor, and keep the loop going until no
  material issues remain or a real blocker needs a user decision.
- Added the Codex-side reviewer rubric reference and UI metadata for `jadu-bina`.
- Updated the README to describe Jadu as five core workflow skills plus the optional Bina
  reviewer loop skill.

## [0.6.0] — 2026-07-18

- **Focus reminder moved from Bidar to Kar.** The 30-minute reminder now starts on `jadu-kar`'s
  first invocation each session, not on `jadu-bidar`'s. Reasoning: waking up and reading
  context isn't work yet — the clock should start when real work does. Kar guards against
  stacking a second recurring reminder on later calls in the same session; Bidar's report
  now notes the reminder hasn't started yet instead of claiming to set it.
- **Payan's session-close line is now unconditional.** It always ends with `Session closed.
  Now run /clear, then start the next session with /jadu-bidar.` — stated as fact, not "if
  you'd like." This cannot be triggered automatically by any tool available to Payan; the
  user still has to run both commands themselves.
- Updated every cross-reference to reminder ownership: `AGENTS.md`, `CLAUDE.md`, `README.md`,
  `PROJECT.md`, and both Codex frontmatter descriptions for Bidar and Kar.

## [0.5.0] — 2026-07-18

Converges this base repo with the private hub-customized fork, after a side-by-side audit
against both that fork and the original [25mordad/Jadu](https://github.com/25mordad/Jadu).
Everything below applies to Claude Code and Codex identically.

- **Payan & Push: no more `git add -A`.** Both now stage only the files the current chat
  session actually touched — matching the hub fork's discipline — and both list (never
  silently drop) any other dirty files they leave unstaged.
- **Payan & Push: fetch + fast-forward pull before every push.** Catches a remote that moved
  ahead (for example a concurrent contributor pushing first) before attempting to push.
  Never force-pushes and never auto-merges/rebases past a real divergence — reports and
  stops instead.
- **Kar: numbered task index.** Ported from the hub fork — a stable numbered list at the top
  of `TASKS.md` so tasks can be selected by number (`go with 1 and 3`), without shortening
  their full explanations.
- **Payan: `TASKS.md` archiving.** Adopts Origin Jadu's own mechanism — fully-closed blocks
  move out to `TASKS_ARCHIVE.md` once `TASKS.md` exceeds 200 lines. This repo's Payan had
  dropped that mechanism when it diverged from Origin; it's now back.
- **Status icons everywhere.** The `⬜`/`🔄`/`⚠️`/`✅` markers Kar already used for tasks now
  prefix the status lines every skill's own reports print (Bidar's session-start summary,
  Payan's close report, Push's confirmation, Zad's setup summary), not just `TASKS.md` itself.
- **Bidar:** no structural change (Bidar here never carried implementation-handoff logic —
  that stays Kar's job alone, as it always has been in this repo).
- **Zad:** intentionally unchanged on secrets/registry — those stay a hub-fork-only concern,
  since not every project that uses Jadu needs either.
- `PROJECT.md`: corrected a stale Timeline line that still said "pending GitHub repo
  creation" — the repo has been live since v0.1.0.

## [0.4.0] — 2026-07-15

- **README:** added **Persian** and **Meaning** columns to the workflow table
  (زاد/بیدار/کار/پایان + English meanings; `Zad` = *born*); merged the Claude Code and Codex
  columns into a single **Command** column (`/jadu-…` · `jadu-…`).
- **README:** description now states that **Jadu (جادو) is Persian for "magic."**
- **README:** the copy-paste install prompt is now explicitly **global** — it installs into
  the user-level `~/.claude` / `~/.codex`, not a project-local dir.
- **Bidar & Payan:** adopted 25mordad's rule **"Do NOT ask for confirmation at any step — just
  do it."** Session start and session close run their own steps autonomously. Implementing
  features/code still follows the project's `AGENTS.md` approval rules.
- Added this `CHANGELOG.md` (+ README pointer).

## [0.3.0] — 2026-07-14

- **Payan now commits and pushes** at session close — closing a session is treated as the
  explicit request to push. `jadu-push` remains the manual commit/push path.
- **README:** added first-run onboarding guidance (hub folder, GitHub sign-in, first project);
  clarified GitHub is optional but useful for backup / collaboration / `jadu-push` / syncing
  across devices and agents; removed a machine-specific workspace example.

## [0.2.0] — 2026-07-14

- Added optional `.env.example` as a starter for downstream projects (Jadu itself needs no
  secrets), a `.gitignore` rule excluding `.env` (keeping `.env.example`), and a README note.

## [0.1.0] — 2026-07-14

- **Initial public release** — the five workflow skills (Zad, Bidar, Kar, Payan, Push) for
  both Claude Code (`.claude/commands/`) and Codex (`.codex/skills/`), plus `AGENTS.md`,
  `CLAUDE.md`, `LICENSE` (MIT), `PROJECT.md`, `TASKS.md`, `WORKLOG.md`, and the optional
  `sounds/30.mp3`. Structure and workflow behavior follow the original
  [25mordad/Jadu](https://github.com/25mordad/Jadu) by Bahman.
