# Jadu — Agent Guide

Jadu is a public collection of reusable AI-agent workflows for structured project sessions. It supports Claude Code through slash-command Markdown files and Codex through skill folders.

## Source of truth

- Use this `AGENTS.md` as the shared guide for all agents.
- Keep `CLAUDE.md` as Claude-specific compatibility notes only.
- Keep `README.md` and `README.fa.md` user-facing and installation-focused.
- Keep `.claude/commands/` and `.codex/skills/` behavior aligned whenever a Jadu workflow changes.

## Workflow names

| Workflow | Meaning | Claude Code | Codex |
|---|---|---|---|
| Bidar | Start/resume a session | `/jadu-bidar` | `jadu-bidar` skill |
| Zad | Initialize project context | `/jadu-zad` | `jadu-zad` skill |
| Payan | Close a session (commits and pushes automatically at the end) | `/jadu-payan` | `jadu-payan` skill |
| Loop | Autonomous, unattended execution of pre-approved subtasks from `LOOP_TASK.md` — opt-in, off by default | `/jadu-loop` | `jadu-loop` skill |
| Loop (best practice) | Same as Loop, but decides and records instead of pausing for a human; the owner reviews every decision in the PR — opt-in, off by default | `/jadu-loop-best-practice` | `jadu-loop-best-practice` skill |
| Loop prepare | Turns the project's existing tasks into a ready `LOOP_TASK_QUEUE/` for the best-practice loop; prepares only, never runs tasks | `/jadu-loop-prepare` | `jadu-loop-prepare` skill |

`jadu-tamam` has been renamed to `jadu-payan`. Do not add new references to `jadu-tamam` except as historical migration notes.

## Jadu Loop is a deliberate exception, not a precedent

`jadu-loop` (see `scripts/jadu-loop/`, `templates/jadu-loop/`, `docs/jadu-loop-authoring-guide.md`) is the one Jadu workflow that implements without per-step approval. It is safe only because of what it refuses to do:

- It only ever executes subtasks a human already wrote, fully specified, into a project's own `LOOP_TASK.md` during a normal supervised session.
- It never plans, decides, reads context beyond a subtask's own `ACTION`, or runs a broad search to fill a gap in an underspecified subtask.
- It never expands its own permissions — shell commands stay gated by whatever allowlist the project's agent surface already has configured.
- A `VERIFY` failure gets exactly one targeted fix attempt, then blocks and waits for a human — never a second guess, never a retry loop.

### The best-practice variant moves the human gate, it does not remove it

`jadu-loop-best-practice` is a second, separately opted-in variant for owners who would rather review once, at the PR, than be paged at every checkpoint. Where `jadu-loop` blocks and waits, it decides and continues: it self-reviews a `review-checkpoint`, makes up to three fix attempts on a failing `VERIFY` and then skips that subtask (and the ones depending on it) instead of blocking, resolves an underspecified `ACTION` or a design choice by a fixed order (what the `VERIFY` checks, the Briefing and the project's rules files, the project's convention for the same kind of change, recognised best practice, then the smallest change that satisfies all of these), turns findings outside the subtask into new subtasks, and promotes the next task from `LOOP_TASK_QUEUE/` once the current one is archived. It stays safe because of what it still refuses to do:

- Every decision is written to a `## Decisions` section of `LOOP_TASK.md` (situation, choice, alternative, reason, undo) and copied into the PR. Any skipped subtask makes the PR a draft.
- It never makes a failing `VERIFY` pass by editing the check, a test or an assertion instead of the code.
- Hard limits still block: never merge, push to trunk, force-push or rewrite pushed history; never touch production or anything live (real messages, money, production deploys/data); never read or commit secrets; never expand its own permissions; abort and block on any merge/rebase conflict; never act outside its own branch and PR.
- Only hard limits and `TYPE: hard-stop` (a paid call, a destructive action, a credential, an install the allowlist cannot run) block. Owner-only steps the owner pre-approved in `.claude/loop-grants.md` are cleared by the watching chat session, never by the loop's `--task` runs, and never for a hard limit.
- Context reads beyond `ACTION` are bounded to what a decision needs — no open-ended exploration.

Do not generalize either pattern to any other Jadu workflow. `jadu-bidar`/`jadu-payan` keep the normal "confirm before implementing" rule.

## Agent compatibility rules

- Prefer agent-neutral wording: “agent”, “Codex”, or “Claude Code” only when the distinction matters.
- `AGENTS.md` is the default project guide created by Jadu workflows. Create or update `CLAUDE.md` only for Claude compatibility.
- Codex workflows live in `.codex/skills/<skill-name>/SKILL.md`.
- Claude Code workflows live in `.claude/commands/<command-name>.md`.
- If a tool exists in one agent surface but not another, document a safe fallback instead of assuming the tool exists.
- Do not create OS-level cron jobs unless the user explicitly asks.
- Jadu has no focus-reminder or sound-alert feature. Do not reintroduce one (no `sounds/*.mp3`, no reminder scheduling) without an explicit new request.

## Repository rules

- First define the task with the user.
- Then refine the task and subtasks together.
- Then confirm the exact intended path, scope, and implementation plan.
- Start coding or changing implementation files only after the user explicitly gives permission.
- Documentation and task-file updates requested by the user are allowed, but feature/code changes require explicit approval first.
- Never run `git push` unless the user explicitly asks to push, with one exception: `jadu-payan` always commits and pushes as its final step, since closing a session is treated as that explicit request.

## Maintenance checklist

When changing a workflow:

1. Update the matching Claude command and Codex skill.
2. Update `README.md` and `README.fa.md` if users need to know.
3. Update this `AGENTS.md` if agent behavior or conventions changed.
4. Update `CLAUDE.md` only for Claude-specific notes.
5. Check for stale names with `grep -R "jadu-tamam\|jadu-kar\|jadu-push\|60.mp3\|60-minute\|30.mp3\|30-minute" .`.
