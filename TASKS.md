# TASKS

### Numbered task index

1. **[P1] 🔄 Publish the public GitHub repo — due: TBD (2/4)**
2. **[P1] ✅ Add `jadu-bina` reviewer loop to the public repo — due: 2026-07-18 (4/4)**
3. **[P3] ⬜ Nice-to-haves (0/3)**
4. **[P1] ✅ Session-behavior redesign (v0.8.0) — completed 2026-07-20 (5/5)**

## [P1] 🔄 Publish the public GitHub repo — due: TBD
**Goal:** `https://github.com/photomohsen/Jadu` exists, public, with this content pushed as the initial commit.
- [x] Create empty public repo named `Jadu` under the target GitHub account
- [x] Push this initial content as the first commit — confirmed live, HEAD matches `origin/main`
- [ ] Verify the copy-paste install prompt actually works end-to-end in a clean Claude Code session
- [ ] Verify the copy-paste install prompt actually works end-to-end in a clean Codex session

## Done

## [P1] ✅ Add `jadu-bina` reviewer loop to the public repo — due: 2026-07-18
**Goal:** the public Jadu repo includes an explicit reviewer skill on both Claude Code and Codex surfaces, with docs and QA records that explain how the loop works.
- [x] Add `.claude/commands/jadu-bina.md`
- [x] Add `.codex/skills/jadu-bina/` with `SKILL.md`, `references/review-rubric.md`, and `agents/openai.yaml`
- [x] Update public docs/changelog to describe `jadu-bina`
- [x] Run QA on the repo copy, validate the skill, and clear naming/doc consistency before push

- [x] ✅ **Converge with the private hub-customized fork — completed 2026-07-18.** After a
  side-by-side audit against both the hub fork and upstream 25mordad/Jadu: Payan and Push no
  longer use `git add -A` (session-touched-file staging only, matching the hub); both fetch
  and attempt a fast-forward pull immediately before pushing, never force/auto-merge past a
  real divergence; Kar gained a numbered task index; Payan gained `TASKS.md` archiving past
  200 lines into `TASKS_ARCHIVE.md` (Origin's mechanism, previously lost in this fork); every
  skill's own reports now prefix status lines with the `⬜`/`🔄`/`⚠️`/`✅` markers. Zad's
  secrets/registry step was deliberately left hub-only. `PROJECT.md`'s stale "pending GitHub
  repo creation" line was corrected. See `CHANGELOG.md` [0.5.0].

- [x] ✅ **Move the focus reminder from Bidar to Kar; make Payan's clear+restart line
  unconditional — completed 2026-07-18.** The 30-minute reminder now starts on `jadu-kar`'s
  first invocation each session instead of `jadu-bidar`'s; Kar guards against stacking a
  second one. Payan always ends with `Session closed. Now run /clear, then start the next
  session with /jadu-bidar.` — stated as a fact every time, not a conditional suggestion;
  this cannot be automated, it still needs the user's own keystroke. Updated every
  cross-reference (`AGENTS.md`, `CLAUDE.md`, `README.md`, `PROJECT.md`, Codex frontmatter).
  See `CHANGELOG.md` [0.6.0].

- [x] ✅ **Session-behavior redesign (v0.8.0) — completed 2026-07-20.** Bidar absorbed Kar
  (merged into one command, ambient task logging, live task tables); `jadu-kar` kept as a
  redirect stub. New `jadu-bazgu` (backbrief: log task, restate, offer options, confirm,
  execute — on demand only). Payan is now unambiguously terminal (states its own
  no-questions rule, reports a rigid commit-confirmation line + URL) and Push matches; both
  keep `git add -A` banned by default with one explicit opt-in phrase. Zad gained a closing
  compaction nudge; Bina gained explicit completion-gate language. Root `AGENTS.md` /
  `CLAUDE.md` brought back in sync. Independent QA pass caught and fixed 4 issues (a
  Claude/Codex parity break, a self-contradiction in Payan's own memory step, the 2 stale
  root docs, a leftover "subproject" reference) before push. See `CHANGELOG.md` [0.8.0].

## [P3] ⬜ Nice-to-haves
**Goal:** polish once the base repo is live and used a few times.
- [ ] Add `README.fa.md` (Farsi translation), matching upstream's bilingual pattern
- [ ] Add a short CONTRIBUTING.md if external PRs start coming in
- [ ] Consider a GitHub Actions check that Claude/Codex command pairs haven't drifted
