---
name: jadu-push
description: Explicit push workflow for Jadu. Use only when the user invokes jadu-push or explicitly asks to push. Stages only the files changed during the current chat session (never the whole repo), commits with a concise summary or user-provided message, and runs git push after a fetch + fast-forward-only pull check. Never push for ordinary session close or task updates.
---

# Jadu Push - Commit and Push

Stage only the files changed during the current chat session, create a concise commit, then
push to the current remote branch. Use only when the user explicitly invokes `jadu-push` or
clearly asks to push.

This intentionally does not use `git add -A`. A blind whole-repo add risks sweeping in
unrelated dirty work that happened to be sitting in the same working tree.

## Steps

1. Compile the list of files this session actually created, edited, or deleted - from the conversation's own record of edit/write operations, not by scanning the repo.
2. Run `git status --short` to see the full working-tree state.
3. Stage exactly the session-touched files that show up as dirty or untracked (`git add <path>` per file). Skip any session-touched file that is not actually dirty.
4. If `git status --short` shows other dirty or untracked files that were not touched this session, list them explicitly and leave them unstaged - do not add them and do not silently omit mentioning them.
5. Create a concise commit message summarizing the staged (session) changes. Use a user-provided message if one was given.
6. Before pushing: run `git fetch`, then `git pull --ff-only`. If that succeeds (already current, or a clean fast-forward), continue. If it fails from genuine divergence, do not force-push and do not auto-merge/rebase; report the divergence and stop, leaving this commit local and intact.
7. Run `git push`.
8. Confirm the push succeeded, report the branch and remote, and repeat the list of any files left unstaged from step 4 so nothing is lost track of.

## Rules

- Never push unless the user explicitly asks.
- Never use `git add -A`; stage only files this session touched.
- Never silently include, or silently drop from the report, other dirty files outside this session's changes.
- Do not add agent-specific co-author lines unless the user asks.
- If there is nothing session-touched to stage but there are already local commits ahead of remote, still offer to push those (still fetch + try `--ff-only` first).
- Always fetch and attempt a fast-forward pull immediately before pushing; never force-push or auto-merge past a real divergence - report and stop instead.
- If push fails because of auth, unresolved divergence, or network, report the error and stop.
- Report the final result with a status marker: `✅` pushed, `⚠️` blocked/failed, `⬜` nothing to push.
