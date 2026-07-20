---
name: jadu-bazgu
description: Backbrief workflow for Jadu. Use when the user invokes jadu-bazgu for one specific request and wants it logged as a task, restated back, weighed against 2-3 concrete options, and confirmed before anything runs - instead of Jadu executing the literal ask directly. Per-request only, not a session-wide mode.
---

# Jadu Bazgu - Backbrief

بازگو (bazgu - "retell/recount"). Invoke this for one specific request when you want it
restated back, weighed against alternatives, and confirmed before anything runs - instead of
Jadu just executing your literal framing. Per-request, not a session-wide mode: without it,
`jadu-bidar` still logs the request as a task ambiently and just gets on with it.

## Workflow

### 0. Log the task

Write the request into `TASKS.md` as a `⬜` task (or subtask, if it clearly belongs under an
existing one) before anything else happens - the same ambient logging `jadu-bidar` does,
just guaranteed here rather than inferred.

### 1. Backbrief

Restate the request in your own words: what you understood the goal to be, its scope, and
anything you are assuming. This is a statement, not a question - the point is for the user
to see their own ask reflected back, so a misunderstanding surfaces now rather than after
work starts.

### 2. Offer options

Propose 2-3 concrete ways to approach it - not just the literal framing restated as a plan.
Lead with a recommendation and say why. If there is genuinely only one sane approach, say
that plainly instead of inventing alternatives for their own sake.

### 3. Wait for confirmation

Ask which option to go with (or confirm the single option, if that is all there was). A
plain `go` approves the recommended/currently-stated option. Naming a different one by
number or name approves that one instead.

### 4. Execute

Once confirmed, run it via the same plan/`go` mechanics `jadu-bidar`'s implementation
handoff already uses: numbered steps, exact files and verification per step, run to
completion without re-asking unless a genuine ambiguity or blocker comes up.

## Rules

- Per-request only - never a standing session mode. The next prompt without `jadu-bazgu`
  goes back to ambient logging and direct execution.
- The backbrief in step 1 is a statement, not a question - do not dress it up as one.
- Do not invent alternatives when there is genuinely only one reasonable approach.
- Obey this project's own `AGENTS.md` approval rules before touching implementation files.
