# Bazgu — Backbrief

بازگو (bazgu — "retell/recount"). Invoke this for one specific request when you want it
restated back, weighed against alternatives, and confirmed before anything runs — instead of
Jadu just executing your literal framing. Per-request, not a session-wide mode: without it,
`jadu-bidar` still logs the request as a task ambiently and just gets on with it.

## Step 1 — Log the task

Write the request into `TASKS.md` as a `⬜` task (or subtask, if it clearly belongs under an
existing one) before anything else happens — the same ambient logging `jadu-bidar` does,
just guaranteed here rather than inferred.

## Step 2 — Backbrief

First, quote the user's request back verbatim — their exact words, unedited — so they can
confirm it was received correctly before anything else. Then restate it in your own words:
what you understood the goal to be, its scope, and anything you're assuming. This is a
statement, not a question — the point is for the user to see both their literal words and
your interpretation reflected back, so a misreading or a misunderstanding surfaces now rather
than after work starts.

## Step 3 — Offer options

Propose 2–3 concrete ways to approach it — not just the literal framing restated as a plan. If
the request itself looks like it could be improved (a missing constraint, an ambiguous scope,
a simpler framing that gets the same result), include that as one of the options. Lead with a
recommendation and say why. If there's genuinely only one sane approach and the request is
already well-formed, say that plainly instead of inventing alternatives for their own sake.

## Step 4 — Wait for confirmation

Ask which option to go with (or confirm the single option, if that's all there was). A plain
`go` approves the recommended/currently-stated option. Naming a different one by number or
name approves that one instead.

## Step 5 — Execute

Once confirmed, run it via the same plan/`go` mechanics `jadu-bidar`'s implementation handoff
already uses: numbered steps, exact files and verification per step, run to completion
without re-asking unless a genuine ambiguity or blocker comes up.

## Rules

- Per-request only — never a standing session mode. The next prompt without `jadu-bazgu`
  goes back to ambient logging + direct execution.
- The backbrief in Step 2 is a statement, not a question — don't dress it up as one.
- Don't invent alternatives when there's genuinely only one reasonable approach.
- Obey this project's own `AGENTS.md` approval rules before touching implementation files.
