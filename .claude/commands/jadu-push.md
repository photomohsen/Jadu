# Push — Commit and Push

Stage all changes, create a concise commit, then push to the current remote branch. Use
only when the user explicitly invokes `/jadu-push` or clearly asks to push.

## Steps

1. Run `git status --short` and inspect relevant diffs to understand what changed.
2. Stage all changes with `git add -A`.
3. Create a concise commit message summarizing the staged changes. Use a user-provided message if one was given.
4. Run `git push`.
5. Confirm the push succeeded and report the branch/remote.

## Rules

- Never push unless the user explicitly asks.
- Do not add Claude-specific co-author lines unless the user asks.
- If there is nothing to commit, skip the commit and push only if there are already local commits to push.
- If push fails because of auth, divergence, or network, report the error and stop.
