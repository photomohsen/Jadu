# Jadu (جادو)

A collection of AI-agent workflow skills for structured, productive project sessions. Fork the repo, copy the workflows you want, and use them with Claude Code or Codex.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[فارسی](README.fa.md)

---

## Workflows included

| Workflow | Claude Code | Codex | What it does |
|---|---|---|---|
| Bidar | `/jadu-bidar` | `jadu-bidar` skill | Session start — reads project state and expands planning subtasks |
| Zad | `/jadu-zad` | `jadu-zad` skill | Project initialization wizard — asks setup questions once and writes project context files |
| Payan | `/jadu-payan` | `jadu-payan` skill | Session end — inline close (no brief), updates docs/tasks, then commits and pushes automatically |
| Loop | `/jadu-loop` | `jadu-loop` skill | **Opt-in, off by default.** Autonomous execution of pre-approved subtasks from `LOOP_TASK.md` — no per-step approval. See [Loop setup](#loop-setup-opt-in) below |
| Loop (best practice) | `/jadu-loop-best-practice` | `jadu-loop-best-practice` skill | **Opt-in, off by default.** Same as Loop, but decides and records instead of pausing for a human; you review every decision in the PR. See [Best-practice variant](#best-practice-variant-opt-in) below |

`jadu-tamam` was renamed to `jadu-payan`.

---

## How to use

### Claude Code

Copy the commands you want into your project's `.claude/commands/` directory:

```bash
cp .claude/commands/jadu-bidar.md /your-project/.claude/commands/
```

Or install all Claude Code commands globally:

```bash
mkdir -p ~/.claude/commands
cp .claude/commands/jadu-*.md ~/.claude/commands/
```

The commands become available as slash commands such as `/jadu-bidar`.

### Codex

Copy the skill folders you want into your project or user-level Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R .codex/skills/jadu-* ~/.codex/skills/
```

Then start a new Codex session and invoke the workflow by name, for example: `jadu-bidar`.

### Shared project guide

For projects that use multiple agents, keep an `AGENTS.md` file in the project root. Jadu’s Codex workflows treat `AGENTS.md` as the primary source of instructions. Claude Code can keep a smaller `CLAUDE.md` that points to the shared guide.

---

## Typical session flow

1. `jadu-zad` — initialize or refresh project context files.
2. `jadu-bidar` — start a session, pull latest safely, read context, and choose a focus.
3. `jadu-payan` — close the session inline, update docs/tasks, and commit + push automatically.
4. An explicit `push` request — commit and push on demand any time you're not closing the session.

---

## Loop setup (opt-in)

`jadu-loop` is different from the other three workflows: it's the one deliberate exception to "never implement without explicit signal," so it needs a few extra pieces installed and a human-authored task file before it can run at all. Nothing here happens automatically just by copying `jadu-loop.md`/`jadu-loop`'s skill folder in.

1. Copy the command/skill as usual (see "How to use" above).
2. Copy the supporting scripts: `cp -R scripts/jadu-loop /your-project/scripts/` — see [`scripts/jadu-loop/README.md`](scripts/jadu-loop/README.md) for what each one does and how to install its one dependency (`python-dotenv`) and, optionally, Telegram notifications.
3. Create `LOOP_TASK.md` in your project root from [`templates/jadu-loop/LOOP_TASK.skeleton.md`](templates/jadu-loop/LOOP_TASK.skeleton.md), or start from the fully worked [`templates/jadu-loop/LOOP_TASK.example.md`](templates/jadu-loop/LOOP_TASK.example.md).
4. **Read [`docs/jadu-loop-authoring-guide.md`](docs/jadu-loop-authoring-guide.md) before writing your first real task.** Every rule in it maps to a bug that actually shipped in an unattended run — it's short, and skipping it is how those bugs happen again.
5. Create a tracked `LOOP_TASK_ARCHIVE/` directory (completed task files move there) and gitignore `.loop_state/` (local run state only).
6. Add whatever commands your subtasks will run to your agent's shell allowlist *before* running the loop — it can't expand its own permissions mid-run.
7. Run it: `python3 scripts/jadu-loop/check_loop_queue.py && python3 scripts/jadu-loop/check_usage_margin.py && claude -p "/jadu-loop" --permission-mode acceptEdits` — by hand, or wrapped in your own `while ... sleep N; done` loop for a long unattended task. **Do not wire this to `cron` unless you've deliberately decided to** — see the Customization/Repository-rules notes on cron below. For a long unattended run, `python3 scripts/jadu-loop/run_loop.py` does the looping for you: it waits for the 5-hour/weekly limits to reset instead of running into usage credits (see `scripts/jadu-loop/README.md`).

### Best-practice variant (opt-in)

`jadu-loop-best-practice` uses the same setup, task files and scripts. The difference: where `jadu-loop` stops and waits for you (a `review-checkpoint`, a `VERIFY` that fails twice, an unclear subtask, a finished task), it makes the best-practice decision, writes it to a `## Decisions` section in `LOOP_TASK.md`, and continues. You review everything once, in the PR: a subtask that still fails after three fix attempts is skipped and the PR opens as a draft, with the decisions and skipped subtasks listed in its body. Hard limits still block: it never merges, pushes to trunk, touches production or secrets, or expands its own permissions.

- Install it like `jadu-loop` (step 1 above). Typed in a chat, `/jadu-loop-best-practice` starts `run_loop.py` detached and returns; the runner then works through the whole queue, one `claude -p "/jadu-loop-best-practice --task" --model opus --permission-mode acceptEdits` per run. Use that `--task` form in place of `/jadu-loop` in step 7 to run one task by hand.
- Each subtask gets 20 minutes; a run that goes 30 minutes without a commit is stopped by the runner and its subtask marked `TIMEOUT 1` (retried) or `TIMEOUT 2` (skipped).
- Optional queue: put further ready task files in `LOOP_TASK_QUEUE/`. Once a task's PR is open and it is archived, the next file (in name order) is promoted to `LOOP_TASK.md` and the following run starts it.
- If the Briefing names how your project marks production (e.g. an `ENVIRONMENT=` line), the loop checks it first and refuses to run against production.

---

## Customization

- **Rename the prefix** — the `jadu-` prefix is arbitrary. Rename the files to anything you like (`/start`, `/push`, `/done`) and Claude Code will pick up the new names.
- **Edit the workflows** — each command or skill is plain Markdown. Change the steps, tone, or structure to match your workflow.
- **Keep agents aligned** — when behavior changes, update both `.claude/commands/` and `.codex/skills/`.
- **Add your own** — create a new `.md` file in `.claude/commands/` for Claude Code, or a new `.codex/skills/<name>/SKILL.md` folder for Codex.

---

## Contributing

PRs are welcome. Please keep Claude Code commands, Codex skills, and user documentation aligned when changing workflow behavior.
