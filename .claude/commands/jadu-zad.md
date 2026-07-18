# Zad — Project Initialization Wizard

Bootstraps this project by asking a handful of setup questions once, then writing the
context files that make the project legible to any agent working in it afterward.

## What this command does

1. Ask all setup questions in one message — never one at a time.
2. Check which context files already exist in the project root.
3. Show the exact file plan and wait for approval.
4. Write each approved file and confirm what changed.

## Step 1 — Ask everything at once

Greet the user briefly, then ask all of the following in a single message, grouped visually:

### Project identity
- **Name:** What is this project called?
- **Type:** Software/IT, or something else (writing, research, personal workflow, etc.)?
- **Description:** One or two sentences — what does it do, what problem does it solve?
- **Status:** Starting fresh, picking up something in progress, or reorganizing something existing?
- **Audience:** Who uses it or benefits from it?

### Tools & setup
- **Software tools / apps:** Languages, frameworks, databases, hosting, services, scripts.
- **Automation / integrations:** Scripts, APIs, connected services, CI/CD.
- **Other tools:** Anything else worth knowing.

### Team & timeline
- **Team:** Who is involved? Names and roles if known.
- **Start date:** When did or will the project start?
- **Milestones:** Any phases, deadlines, or target outcomes?

### Conventions & rules
- **Workflow:** Preferred process, branching/review process, naming conventions, approval steps.
- **Standards:** Style, quality, security, or process standards.
- **Agent rules:** Anything agents should always or never do in this project.

### Existing files
- Does the project already have `AGENTS.md`, `CLAUDE.md`, `PROJECT.md`, `README.md`,
  `TASKS.md`, or `WORKLOG.md`? Check automatically rather than only asking.

## Step 2 — Decide which files to create or update

| Condition | File action |
|---|---|
| Always | Create or update `PROJECT.md` |
| User mentioned agent rules, workflow rules, stack details, or "what agents should know" | Create or update `AGENTS.md` |
| User wants Claude Code–specific notes, or `CLAUDE.md` already exists | Offer to create or update `CLAUDE.md` |
| User mentioned tasks, milestones, deadlines, or backlog | Create or update `TASKS.md` |
| User wants session history | Create `WORKLOG.md` with a minimal header if missing |

Before writing, tell the user exactly what will be created/updated and where. Wait for
explicit approval before writing anything.

## Step 3 — Write `PROJECT.md`

```markdown
# [Project Name]

> [One-sentence description]

## Overview
[2–4 sentences: what it does, who it is for, current status]

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

## Step 4 — Write `AGENTS.md`

`AGENTS.md` is the shared, agent-agnostic guide — Claude Code, Codex, or any other agent
reads this first.

```markdown
# [Project Name] — Agent Guide

## What this project is
[1–2 sentences]

## Tools & setup
[Key tools, apps, languages, or structure]

## Key commands / workflows
- `...` — ...

## Conventions agents should follow
- ...

## Things agents should never do in this project
- ...
```

If the user gave an approval workflow, include it here (see the "Golden rules" suggestion
in this repo's own README — many projects copy those verbatim). If they did not, keep any
existing repository instructions intact and avoid inventing restrictive rules.

## Step 5 — Write `CLAUDE.md` only when needed

Mirror the relevant parts of `AGENTS.md`, phrased for Claude Code, and make clear
`AGENTS.md` is the source of truth. Do not create `CLAUDE.md` by default.

## Step 6 — Write `TASKS.md`

Pre-populate tasks from milestones and next steps using checkboxes:

- P1: due in the next 1–2 weeks or explicitly urgent
- P2: current phase/sprint work
- P3: backlog or someday items

## Step 7 — Report back

Print a short summary. Prefix each line with the marker that matches its state — `✅`
created/updated · `⬜` skipped/not requested · `⚠️` needs the user's decision: files
created/updated, one sentence per file describing its contents, and assumptions made for
any skipped answers.

## Rules

- Ask all setup questions in one message.
- If the user skips a question, make a reasonable assumption and state it.
- Never overwrite an existing file without asking first.
- Never create files outside the project root.
- Do not add placeholder `TBD` sections; omit empty sections.
- Do not execute project work; only create or update context/planning files.
