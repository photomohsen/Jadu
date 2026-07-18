# TASKS

### Numbered task index

1. **[P1] 🔄 Publish the public GitHub repo — due: TBD (2/4)**
2. **[P3] ⬜ Nice-to-haves (0/3)**

## [P1] 🔄 Publish the public GitHub repo — due: TBD
**Goal:** `https://github.com/photomohsen/Jadu` exists, public, with this content pushed as the initial commit.
- [x] Create empty public repo named `Jadu` under the target GitHub account
- [x] Push this initial content as the first commit — confirmed live, HEAD matches `origin/main`
- [ ] Verify the copy-paste install prompt actually works end-to-end in a clean Claude Code session
- [ ] Verify the copy-paste install prompt actually works end-to-end in a clean Codex session

## [P3] ⬜ Nice-to-haves
**Goal:** polish once the base repo is live and used a few times.
- [ ] Add `README.fa.md` (Farsi translation), matching upstream's bilingual pattern
- [ ] Add a short CONTRIBUTING.md if external PRs start coming in
- [ ] Consider a GitHub Actions check that Claude/Codex command pairs haven't drifted

## Done

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
