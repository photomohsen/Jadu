# Worklog

## 2026-07-18 — Move the focus reminder to Kar; make Payan's restart line unconditional

### What we built

| Feature | Files |
|---|---|
| Reminder ownership moved from Bidar to Kar (first invocation each session, guarded against stacking) | `jadu-bidar.md`, `jadu-kar.md`, both `.codex/skills/` mirrors |
| Payan's session-close line made unconditional (`Session closed. Now run /clear, then start the next session with /jadu-bidar.`) | `jadu-payan.md`, Codex mirror |
| Cross-reference updates | `AGENTS.md`, `CLAUDE.md`, `README.md`, `PROJECT.md`, Codex frontmatter descriptions |

### Decisions

#### 1. Reminder starts with work (Kar), not with waking up (Bidar)
**Why:** the owner asked for this directly — reading context at session start isn't the
part worth timeboxing; actual task work is.
**How:** removed the reminder step from Bidar entirely (in both this repo and the hub fork);
added a "first invocation only" reminder step to Kar, guarded so a second `jadu-kar` call in
the same session never stacks a duplicate recurring job. Bidar's report now states the
reminder hasn't started yet rather than claiming to set it.

#### 2. Payan's closing instruction is stated as fact, not a suggestion — with the limitation disclosed
**Why:** the owner asked that `/clear` + `/jadu-bidar` always happen after `jadu-payan`.
No tool available to Payan can actually clear a conversation or start a new one — those are
client-level actions, not something a skill's instructions can trigger. The honest fix is to
make the *instruction* to the user unconditional and unambiguous, not to pretend the agent
can perform the action itself.
**How:** replaced the old conditional "if staying in this tab, consider clearing..." line
with an unconditional one in both this repo and the hub fork, and added an explicit rule
against softening it back into a suggestion.

### Pending / TODO

- [ ] Dry-run the copy-paste install prompt in a fresh Claude Code and Codex session (carried over)

---

## 2026-07-18 — Converge with the private hub fork after a 3-way audit

### What we built

| Feature | Files |
|---|---|
| Session-touched-file staging in Payan and Push (no more `git add -A`) | `.claude/commands/jadu-payan.md`, `jadu-push.md`, both `.codex/skills/` mirrors |
| Fetch + fast-forward-only pull immediately before every push | same 4 files |
| `TASKS.md` archiving past 200 lines into `TASKS_ARCHIVE.md` | `jadu-payan.md` + Codex mirror |
| Numbered task index in Kar | `jadu-kar.md` + Codex mirror |
| Status icons (`⬜`/`🔄`/`⚠️`/`✅`) in every skill's own reports, not just `TASKS.md` | all 5 skills, both agent surfaces |
| `CHANGELOG.md` [0.5.0], corrected stale `PROJECT.md` timeline line | `CHANGELOG.md`, `PROJECT.md` |

### Decisions

#### 1. Reverse the 2026-07-14 "match upstream's `git add -A`" call
**Why:** that decision was deliberate at the time — reasoned as "session-scoped staging only
matters in a shared multi-project repo," which this standalone repo isn't. The owner
requested convergence with the private hub fork specifically, after a fresh side-by-side
audit (this repo vs. the hub fork vs. upstream 25mordad/Jadu) surfaced the hub's staging
discipline as worth adopting everywhere, not just in the hub.
**How:** Payan and Push in both this repo and the hub fork now stage only session-touched
files and fetch + `--ff-only` pull before pushing. Multi-repo-root awareness and the
entangled-file wait-then-push logic stayed hub-only — this repo is still single-repo by
design, so that machinery doesn't apply here.

#### 2. Backport Origin's `TASKS.md` archiving, not its `WORKLOG.md` thresholds
**Why:** the audit found Origin Jadu still archives `TASKS.md` past 200 lines into
`TASKS_ARCHIVE.md` — a mechanism both this fork and the hub had silently dropped. Origin's
`WORKLOG.md` thresholds (120 lines / 4 entries) were not reverted; both this repo and the hub
keep the already-established 250-line / 8-entry threshold there.
**How:** Added a `TASKS.md`-archiving step to Payan, mirrored in both agent surfaces, in both
this repo and the hub fork.

#### 3. Extend status icons beyond `TASKS.md` into every skill's reports
**Why:** the owner asked for the `⬜`/`🔄`/`⚠️`/`✅` vocabulary used everywhere a skill
reports a state, not only inside the task file format.
**How:** Bidar, Kar, Payan, Push, and Zad each now prefix their own report lines with the
matching marker, in both this repo and the hub fork.

#### 4. Leave Zad's secrets/registry step hub-only
**Why:** not every project using this base repo needs a secrets story, and the hub's version
is tied to its own project-registry model. Generalizing it here was considered and declined.
**How:** no change to `jadu-zad.md` beyond the same status-icon reporting convention.

### Pending / TODO

- [ ] Dry-run the copy-paste install prompt in a fresh Claude Code and Codex session (carried over from 2026-07-14)

---

## 2026-07-14 — Generalized from the private hub-customized Jadu

### What we built

| Feature | Files |
|---|---|
| Generic single-project versions of all 5 skills (Zad/Bidar/Kar/Payan/Push) | `.claude/commands/jadu-*.md`, `.codex/skills/jadu-*/SKILL.md` |
| README with install instructions and a copy-paste agent prompt | `README.md` |
| MIT license, self-hosted context files (dogfooding Jadu on itself) | `LICENSE`, `PROJECT.md`, `AGENTS.md`, `TASKS.md` |

### Decisions

#### 1. Strip the hub-specific project registry logic
**Why:** the source version (in a private personal hub) resolves a target project via a
`PROJECTS.md` registry, subproject columns, and hub-root doc reads — all specific to that
one hub's layout. A public tool aimed at anyone should match upstream Jadu's simplicity:
operate on the current project root, no registry required.
**How:** removed all "resolve the target project" steps; every skill now reads/writes
directly at the project root (`TASKS.md`, `WORKLOG.md`, `AGENTS.md`, etc.).

#### 2. Keep Payan and Push separate (don't carry over "Payan always pushes")
**Why:** the private hub had Payan auto-push as a deliberate personal exception. For a
public default, the safer and more predictable behavior — and the one that matches
upstream — is that nothing ever pushes without an explicit ask.
**How:** Payan's steps stop at doc/task updates; README documents how to merge them back
in as a customization if someone wants that.

#### 3. Match upstream's way of working, not the private hub's
**Why:** the goal is a faithful public generalization — same working method as
`25mordad/Jadu`, only the private hub topology removed. So Push uses upstream's simple
`git add -A` (not the hub's session-scoped staging, which only matters in a shared
multi-project repo), and Payan writes docs but never pushes.
**How:** reverted Push to `git add -A`; kept the generic, non-hub-specific niceties only
(structured `TASKS.md`/`WORKLOG.md` formats, `go`/`go with 1,2,3` approval wording).
Added the 3 structural files upstream ships that the first draft missed: `.gitignore`,
`CLAUDE.md`, `sounds/30.mp3` (already present). `README.fa.md` deferred.

### Pending / TODO

- [ ] Create and push the actual public GitHub repo (see TASKS.md)
- [ ] Dry-run the copy-paste install prompt in a fresh Claude Code and Codex session

---
