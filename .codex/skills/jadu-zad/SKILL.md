---
name: jadu-zad
description: Project initialization wizard for Jadu. Use when the user invokes jadu-zad, starts a new project, or wants context files (PROJECT.md, AGENTS.md, TASKS.md, optional CLAUDE.md/WORKLOG.md) set up or refreshed for the current project. Asks setup questions once, then writes the files after approval.
---

# Jadu Zad - Project Initialization Wizard

Bootstraps this project by asking a handful of setup questions once, then writing the
context files that make the project legible to any agent working in it afterward.

## Workflow

### 0. Ask everything at once

Greet the user briefly, then ask all of the following in a single message, grouped
visually:

**Project identity**
- Name, type (software/IT or something else), one-to-two sentence description, status
  (fresh / in progress / reorganizing), audience.

**Tools & setup**
- Software tools/apps, automation/integrations, other tools worth knowing.

**Team & timeline**
- Team members and roles, start date, milestones or deadlines.

**Conventions & rules**
- Preferred workflow/approval process, standards, agent rules (things agents should
  always or never do here).

**Existing files**
- Check automatically whether `AGENTS.md`, `CLAUDE.md`, `PROJECT.md`, `README.md`,
  `TASKS.md`, or `WORKLOG.md` already exist, rather than only asking.

### 1. Decide which files to create or update

| Condition | File action |
|---|---|
| Always | Create or update `PROJECT.md` |
| User mentioned agent rules, workflow rules, stack details, or "what agents should know" | Create or update `AGENTS.md` |
| User wants Claude Code-specific notes, or `CLAUDE.md` already exists | Offer to create or update `CLAUDE.md` |
| User mentioned tasks, milestones, deadlines, or backlog | Create or update `TASKS.md` |
| User wants session history | Create `WORKLOG.md` with a minimal header if missing |

Tell the user exactly what will be created or updated and where. Wait for explicit
approval before writing anything.

### 2. Write `PROJECT.md`

```markdown
# [Project Name]

> [One-sentence description]

## Overview
[2-4 sentences: what it does, who it is for, current status]

## Setup & Tools

| What | Details |
|---|---|

## Team

| Name | Role |
|---|---|

## Timeline

| Milestone | Target Date |
|---|---|

## Conventions
[Workflow rules, naming standards, approval steps, or other operating rules]

## Notes
[Key constraints, kickoff decisions, links]

---
_Initialized: YYYY-MM-DD_
```

Omit sections with no real content.

### 3. Write `AGENTS.md`

`AGENTS.md` is the shared, agent-agnostic guide - Codex, Claude Code, or any other agent
reads this first.

```markdown
# [Project Name] - Agent Guide

## What this project is
[1-2 sentences]

## Tools & setup
[Key tools, apps, languages, or structure]

## Key commands / workflows
- `...` - ...

## Conventions agents should follow
- ...

## Things agents should never do in this project
- ...
```

If the user gave an approval workflow, include it here. If they did not, keep any
existing repository instructions intact and avoid inventing restrictive rules.

### 4. Write `CLAUDE.md` only when needed

Mirror the relevant parts of `AGENTS.md`, phrased for Claude Code, and make clear
`AGENTS.md` is the source of truth. Do not create it by default.

### 5. Write `TASKS.md`

Pre-populate tasks from milestones and next steps using checkboxes: `P1` (1-2 weeks or
urgent), `P2` (current phase), `P3` (backlog).

### 6. Report back

Print a short summary: files created or updated, one sentence per file describing its
contents, and assumptions made for any skipped answers.

## Rules

- Ask all setup questions in one message.
- If the user skips a question, make a reasonable assumption and state it.
- Never overwrite an existing file without asking first.
- Never create files outside the project root.
- Do not add placeholder `TBD` sections; omit empty sections.
- Do not execute project work; only create or update context/planning files.
