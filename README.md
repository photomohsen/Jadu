# Jadu (جادو)

**Jadu** (جادو) is Persian for "magic." It's five core AI-agent workflow skills plus one
review loop skill that keep a coding session structured: start with context, work through
tasks, review until the work is actually ready, close with a clean record, and push only
when the workflow or user request explicitly calls for it. Works the same in **Claude Code**
and **Codex**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Based on the original [25mordad/Jadu](https://github.com/25mordad/Jadu) by Bahman.

---

## The idea in one sentence

Every session follows the same loop — **Zad → Bidar → Kar → Payan → Push** — so any
agent, in any project, on any machine, picks up exactly where the last session left off.

| Workflow | Persian | Meaning | Command | What it does |
|---|---|---|---|---|
| **Zad** | زاد | born | `/jadu-zad` · `jadu-zad` | Ask setup questions once, write `PROJECT.md` / `AGENTS.md` / `TASKS.md` |
| **Bidar** | بیدار | wake up | `/jadu-bidar` · `jadu-bidar` | Start a session — read context, pull latest, expand tasks (no reminder yet) |
| **Kar** | کار | work | `/jadu-kar` · `jadu-kar` | Manage `TASKS.md` through conversation — add, update, complete, review; starts the 30-min focus reminder on its first call each session |
| **Payan** | پایان | end | `/jadu-payan` · `jadu-payan` | Close a session — write a brief, update docs/tasks, commit and push, then tell you to `/clear` and run `/jadu-bidar` next |
| **Push** | — | push (English) | `/jadu-push` · `jadu-push` | Commit and push without a full session close |

Command shows **Claude Code** (`/jadu-…`) · **Codex** (`jadu-…`, no leading slash).

Optional reviewer loop:

| Workflow | Persian | Meaning | Command | What it does |
|---|---|---|---|---|
| **Bina** | بینا | seeing / observant | `/jadu-bina` · `jadu-bina` | Review active work, turn confirmed findings into tasks, and keep the QA loop going until the artifact is actually ready |

---

## Install in 60 seconds

### Option A — copy-paste prompt (easiest)

Open Claude Code or Codex in any project, paste this, and let the agent do it. It installs
Jadu **globally** (into your user-level `~/.claude` / `~/.codex`), so every project on the
machine gets it — you only do this once:

```
Install the Jadu agent workflow skills from https://github.com/photomohsen/Jadu
GLOBALLY on this machine — into my user-level config, so they work in every project,
not just this one:

1. Fetch that repo (clone it to a temp folder, or read the raw files).
2. If I'm using Claude Code: copy every file from its `.claude/commands/` into my
   GLOBAL `~/.claude/commands/` (create the folder if missing) — NOT this project's local `.claude/`.
3. If I'm using Codex: copy every folder from its `.codex/skills/` into my GLOBAL
   `~/.codex/skills/` (create the folder if missing) — NOT this project's local `.codex/`.
4. Optionally copy `sounds/30.mp3` to `~/.claude/sounds/30.mp3` (Claude Code only,
   for the 30-minute focus sound).
5. Ask me before overwriting any file or folder that already exists with the same name.
6. Report exactly what was installed, skipped, or needs my decision.
7. Then offer first-run setup:
   - ask whether I want a new Jadu hub folder, an existing project folder, or only the
     global skill install
   - if I choose a hub, ask for the hub name and location, create it, and add a
     `projects/` folder inside it
   - ask for my first project name and where it should live
   - check whether Git is installed and whether GitHub is connected; if not, help me
     create a GitHub account or sign in, then guide me through `gh auth login` or open
     the GitHub authorization page
   - run `jadu-zad` (or `/jadu-zad`) in the new project folder to create its context files

Do not push, publish, or change anything outside these installs.
```

### Option B — manual commands

**Claude Code** — copy the commands you want, or all of them, globally:

```bash
git clone https://github.com/photomohsen/Jadu.git
mkdir -p ~/.claude/commands
cp Jadu/.claude/commands/jadu-*.md ~/.claude/commands/
```

They become available as slash commands: `/jadu-bidar`, `/jadu-zad`, `/jadu-kar`,
`/jadu-payan`, `/jadu-push`.

**Codex** — copy the skill folders globally:

```bash
mkdir -p ~/.codex/skills
cp -R Jadu/.codex/skills/jadu-* ~/.codex/skills/
```

Start a new Codex session and invoke a workflow by name, e.g. `jadu-bidar`.

Either way, installing globally (`~/.claude`, `~/.codex`) means every project on that
machine gets Jadu — you don't need to repeat this per project.

---

## First-run setup: hub, GitHub, first project

After installing the skills, a new user usually needs three things:

1. A **hub folder** somewhere on their machine, for example `~/Projects`, `~/AI Work`,
   or any folder name they prefer.
2. Optional **GitHub connection**, so projects can be backed up, shared, pushed when
   the user explicitly asks, or synced across multiple devices and agents.
3. A first **project folder** inside the hub, initialized with Jadu's context files.

You can ask an agent to do that setup with this prompt:

```text
Set up my first Jadu workspace.

1. Ask me for the hub folder name and where I want it created.
2. Create the hub folder and a `projects/` folder inside it.
3. Ask me for my first project name and desired folder path.
4. Create that project folder.
5. Check whether Git is installed.
6. Check whether GitHub CLI (`gh`) is installed and authenticated.
7. If GitHub is not connected, help me create a GitHub account or sign in by running
   `gh auth login` or by opening the GitHub authorization page. If I do not want GitHub
   yet, continue locally.
8. In the project folder, run `jadu-zad` or `/jadu-zad` and ask me the normal setup
   questions.
9. Do not push anything unless I explicitly say `jadu-payan`, `jadu-push`, or `push`.
```

Manual version:

```bash
mkdir -p ~/Projects/projects/my-first-project
cd ~/Projects/projects/my-first-project

# Optional GitHub sign-in, if you want remote backup later:
gh auth login

# Then initialize the project with Jadu:
# Claude Code: /jadu-zad
# Codex:      jadu-zad
```

GitHub is optional. Jadu is agent-agnostic and works locally with Markdown files even if
the user has no GitHub account yet. Connecting GitHub only matters when they want backup,
collaboration, `jadu-push`, or syncing the same Jadu workflow across multiple agents on
multiple devices.

There are two separate, agent-agnostic things to keep in mind:

1. **The public Jadu repo** — [github.com/photomohsen/Jadu](https://github.com/photomohsen/Jadu).
   This is the source people clone or ask an agent to install from. It should stay generic
   and usable for anyone.
2. **The local installed Jadu skills** — the files copied into `~/.claude/commands/` or
   `~/.codex/skills/` on one machine. These are what Claude Code or Codex actually runs.
   They can be updated from the public repo, or customized locally for a specific hub.

---

## Typical session

```
jadu-zad     (once)   → initialize this project's context files
jadu-bidar   (start)  → read context, pull latest, expand tasks (no reminder yet)
jadu-kar     (as needed) → add/update tasks — the 30-min focus reminder starts here
   ... do the actual work ...
jadu-payan   (end)    → write the session brief, update docs/tasks, commit, and push
jadu-push    (manual) → commit and push without a full session close
```

`Payan` now includes the push workflow: after it writes the session brief and updates
`WORKLOG.md` / `TASKS.md` / `AGENTS.md`, it stages changes, commits, and pushes. Use
`jadu-push` when you want to commit and push without doing the full Payan closeout.
Payan always closes by telling you to run `/clear` then `/jadu-bidar` for the next
session — that part needs your own keystroke; no skill can trigger it for you.

---

## What each skill actually reads and writes

All six skills work on files in the current project's root — no special folder
structure required:

- `AGENTS.md` — the shared, agent-agnostic guide every agent reads first
- `CLAUDE.md` — optional, Claude-only notes, points back to `AGENTS.md`
- `PROJECT.md` — identity, tools, team, timeline
- `TASKS.md` — the live task list `jadu-kar` and `jadu-bidar`/`jadu-payan` manage
- `WORKLOG.md` — a dated log of what happened each session, written by `jadu-payan`

None of this requires a database, a server, or an account — it's just Markdown files an
agent reads and edits like any other file in your repo.

---

## Optional: project secrets (`.env`)

**Jadu itself needs no secrets** — none of the six skills read a token or key. But if
*your project* uses API keys or credentials, the repo ships an optional
[`.env.example`](.env.example) as a starting point:

```bash
cp .env.example .env   # then fill in real values
```

`.gitignore` already excludes `.env` (and keeps `.env.example`), so your real secrets
never get committed. Commit only the keys-only template. If your project needs no
secrets, ignore this entirely and delete both files.

---

## Suggested golden rules for `AGENTS.md`

Many projects add something like this to their `AGENTS.md` so every agent — Claude Code,
Codex, or otherwise — behaves predictably:

1. First define the task with the user.
2. Then refine the task and subtasks together.
3. Then confirm the exact intended path, scope, and implementation plan.
4. Start coding or changing implementation files only after the user explicitly gives permission.
5. A plain `go` approves the currently stated next step; `go with 1, 2, and 3` approves that full sequence. Once approved, complete it without asking again — pause only for a genuine ambiguity or blocker.
6. Do not make decisions on the user's behalf. When something is ambiguous, ask.
7. Never run `git push` unless the user explicitly asks, or the user invoked a workflow
   such as `jadu-payan` that clearly includes commit and push.

Copy, trim, or ignore this — it's a starting point, not a requirement.

---

## Customization

- **Rename the prefix** — `jadu-` is arbitrary. Rename the files to anything (`/start`, `/push`, `/done`) and Claude Code/Codex will pick up the new names.
- **Edit the workflows** — every command/skill is plain Markdown. Change the steps, tone, or structure to match how you work.
- **Keep agents aligned** — when you change behavior, update both `.claude/commands/` and `.codex/skills/` so Claude Code and Codex don't drift apart.
- **Add your own** — a new `.md` file in `.claude/commands/` for Claude Code, or a new `.codex/skills/<name>/SKILL.md` folder for Codex.
- **Multi-project workspace?** If you keep many projects in one repo, you'll want each skill to ask which project is in scope before reading or writing anything. That's a straightforward addition to each skill's first step — not included here to keep this base version simple.

---

## Optional: 30-minute sound alert

`jadu-kar` sets the only focus reminder — 30 minutes, on its first call each session, no
60-minute variant. (`jadu-bidar` doesn't set one at all; waking up and reading context
isn't billable focus time.) Claude Code can play a sound at each reminder if `ffplay`
(part of `ffmpeg`) is installed and `30.mp3` exists at `~/.claude/sounds/`:

```bash
# macOS:  brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg

mkdir -p ~/.claude/sounds
cp sounds/30.mp3 ~/.claude/sounds/
```

If the file or `ffplay` isn't present, the reminder just skips the sound silently — no
error, no fake success.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for what's changed across versions.

## Contributing

PRs are welcome. Keep the Claude Code commands and Codex skills behaviorally identical
when you change a workflow — that's the whole point of "agent-agnostic."

## License

MIT — see [LICENSE](LICENSE).
