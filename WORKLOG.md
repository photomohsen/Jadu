# Worklog

## 2026-07-20 — Session-behavior redesign (v0.8.0): Bidar+Kar merge, Bazgu, hardened Payan/Push

### What we built

| Feature | Files |
|---|---|
| Bidar absorbs Kar into one command; ambient task logging; task tables everywhere | `.claude/commands/jadu-bidar.md`, `.codex/skills/jadu-bidar/` |
| `jadu-kar` redirect stub (not deleted) | `.claude/commands/jadu-kar.md`, `.codex/skills/jadu-kar/` |
| New: Bazgu — per-request backbrief + options + confirm | `.claude/commands/jadu-bazgu.md`, `.codex/skills/jadu-bazgu/` (new, incl. `agents/openai.yaml`) |
| Payan hardened: mandatory decisions/preferences self-check, cross-doc date-drift flag, conditional README refresh, rigid commit-confirmation line + URL, explicit opt-in `git add -A` escape hatch, non-negotiable no-questions rule stated in-skill | `.claude/commands/jadu-payan.md`, `.codex/skills/jadu-payan/` |
| Push hardened: same rigid confirmation line + escape hatch | `.claude/commands/jadu-push.md`, `.codex/skills/jadu-push/` |
| Zad: closing context-compaction nudge (adopted from upstream) | `.claude/commands/jadu-zad.md`, `.codex/skills/jadu-zad/` |
| Bina: explicit completion-gate language, no behavior change | `.claude/commands/jadu-bina.md`, `.codex/skills/jadu-bina/` |
| Docs updated to match | `README.md`, `CHANGELOG.md` [0.8.0], `TASKS.md` |

### Decisions

#### 1. Merge Bidar and Kar
**Why:** two commands to remember for "start" and "manage tasks" was real friction in
practice, and Kar already silently depended on Bidar having resolved the project first.
**How:** `jadu-bidar` does first-call setup and, every call, also shows/manages the live
backlog. `jadu-kar` becomes a redirect stub rather than being deleted outright, so a user
typing it from habit gets pointed at the right place instead of a dead end.

#### 2. Ambient task logging instead of waiting for Payan
**Why:** the recurring real-world failure mode was tasks getting created in conversation
and then forgotten — nothing captured them until an explicit task-add or session close.
**How:** any actionable prompt writes to `TASKS.md` immediately; read-only questions and
lookups never do.

#### 3. Soften, not remove, the `git add -A` ban
**Why:** session-scoped staging is the right default (a real incident showed why), but a
fully rigid ban ignored that a whole-repo add is sometimes genuinely the simplest, safest
option in a single-repo context — and this repo is single-repo by design.
**How:** stays banned by default; one explicit, verbatim opt-in phrase triggers a real
`git add -A` for that call only.

#### 4. Payan states its no-questions rule in its own text, not just in practice
**Why:** "Payan means end" is easy to erode silently over time if it is only ever an
implicit convention rather than something the skill says about itself.
**How:** added the rule directly to `jadu-payan.md`/`SKILL.md`, and removed the one
existing soft spot (a permission-classifier-blocked-push fallback that used to ask) so it
now reports and stops like every other failure mode.

#### 5. Bazgu is on-demand, not the new default for every prompt
**Why:** giving every single prompt the full restate+options+confirm treatment would be
heavier than most requests warrant; ambient logging already covers "don't lose track of
things."
**How:** `jadu-bazgu` is invoked per-request; without it, `jadu-bidar`'s ambient logging and
direct execution stay the default.

### Verification

- Read this repo's own prior skill files fresh immediately before rewriting each one, to
  avoid silently reverting anything already-correct.
- Compared new content against a live fetch of upstream 25mordad/Jadu's current files for
  the 2 items adopted from there (Zad's compaction nudge, Payan's conditional README
  refresh) — confirmed both are genuinely upstream behavior, not invented.
- Confirmed the two changed agent surfaces stay behaviorally identical: same steps, same
  rules, only format conventions differ (Codex's numbered-workflow style vs. Claude Code's
  heading style).

### Pending / TODO

- [ ] Independent QA pass on all 14 changed/new files before pushing
- [ ] Push to `github.com/photomohsen/Jadu` as v0.8.0 — its own explicit go-ahead

---

## 2026-07-18 — Add `jadu-bina` as the public reviewer loop

### What we built

| Feature | Files |
|---|---|
| New Claude Code reviewer command | `.claude/commands/jadu-bina.md` |
| New Codex reviewer skill with rubric + UI metadata | `.codex/skills/jadu-bina/SKILL.md`, `references/review-rubric.md`, `agents/openai.yaml` |
| Public repo docs updated to explain Bina | `README.md`, `CHANGELOG.md`, `TASKS.md` |

### Decisions

#### 1. Keep Jadu's main session loop unchanged, and add Bina as an explicit reviewer loop
**Why:** the owner asked to rename the earlier reviewer concept from `jadu-nazer` to
`jadu-bina`, but not to replace the five core workflows or distort their order. The clean
model is still `Zad -> Bidar -> Kar -> Payan -> Push`, with `Bina` as the explicit QA loop
invoked when review is needed.
**How:** added Bina to the repo as a sixth, optional skill and updated README wording from
"five small skills" to "five core workflow skills plus one review loop skill."

#### 2. Ship Bina on both agent surfaces, not just Codex
**Why:** this repo's promise is agent-agnostic parity. Shipping only a Codex skill would
leave Claude Code behind and reintroduce the drift the project tries to avoid.
**How:** added both `.claude/commands/jadu-bina.md` and `.codex/skills/jadu-bina/`.

#### 3. Make the reviewer skill task-ledger-first
**Why:** the owner's requirement for Nazer/Bina was not just "review the work"; it was
"review, create tasks, send the executor back, and keep looping until satisfied." That only
works if the reviewer writes findings into the real Jadu records rather than leaving them as
chat-only commentary.
**How:** Bina's instructions explicitly require reading `TASKS.md` first, logging confirmed
findings as actionable tasks or subtasks, then re-checking the updated artifact itself.

### Verification

- Validated the public Codex skill with `skill-creator/scripts/quick_validate.py`.
- Validated the renamed installed global skill at `~/.codex/skills/jadu-bina`.
- Scanned the public repo for stale `jadu-nazer` references after the rename-related update;
  no public-repo leftovers remained.
- Re-checked the mirrored surfaces and docs for naming consistency before push.

### Pending / TODO

- [ ] Verify the copy-paste install prompt actually works end-to-end in a clean Claude Code session (carried over)
- [ ] Verify the copy-paste install prompt actually works end-to-end in a clean Codex session (carried over)

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
