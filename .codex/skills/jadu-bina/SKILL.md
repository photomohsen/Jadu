---
name: jadu-bina
description: Review active Jadu work as an independent QA and reviewer loop. Use when the user asks for QA, review, a reviewer pass, a bina pass, or wants execution to continue until the reviewer is satisfied. Convert confirmed findings into actionable Jadu tasks for the executor, re-check the fixes against the artifact itself, and keep looping until no material issues remain or a real blocker needs the user's decision.
---

# Jadu Bina

Act as the reviewer inside a Jadu execution loop.

Your job is not to be nice to the artifact. Your job is to help the work become
ready.

## Core behavior

1. Rebuild context from the current project artifacts and task ledger before judging the work.
2. Review the output independently.
3. Convert every confirmed issue into an actionable task or subtask for the executor.
4. Send the executor back to fix the issues.
5. Re-review the updated artifact from the artifact itself, not from memory.
6. Repeat until there are no material findings left.

Do not stop at "looks good" if you have not actually checked the artifact.

## Review loop

### Step 1 - Resolve the review scope

- Reuse the current Jadu project or subproject scope if `jadu-bidar` or `jadu-kar` already resolved it.
- If the scope is not explicit, identify the one active project the work belongs to before reviewing.
- Read the current `TASKS.md` first so your findings land in the real ledger rather than floating only in chat.
- When relevant, also read `PROJECT.md`, `WORKLOG.md`, and the current artifact files the executor changed.

### Step 2 - Inspect the actual artifact

Review the output itself, not just the diff.

Examples:

- Decks: inspect slide renders, flow, overlap, copy clarity, hierarchy, consistency, and beginner comprehension when applicable.
- Documents: inspect layout, tone, structure, and factual traceability.
- Skills: inspect trigger wording, workflow clarity, resource references, and whether the skill would actually guide another agent.
- Code: inspect behavior, regressions, missing verification, and integration risk.

Prefer evidence from the artifact, render, output file, or verification logs over assumptions.

## Step 3 - Separate confirmed findings from open questions

Use this split:

- Confirmed finding: a real issue, regression, omission, or weak point you can point to.
- Open question: something ambiguous that needs a user or domain decision.

Do not inflate uncertainty into fake bugs.
Do not soften real bugs into vague "maybe" language.

## Step 4 - Log findings into Jadu tasks

Before the executor fixes anything, make sure the work is represented in the task ledger.

- If the issue belongs under an existing active task, add a concrete unchecked subtask there.
- If the issue changes the scope materially, add a new task block instead of hiding it inside a vague note.
- Keep each task actionable and testable.
- Include dependencies inline when one fix depends on another.

Use concise executor-facing wording such as:

- "Tighten slide 10 layout so all four cards show body copy"
- "Regenerate `agents/openai.yaml` for `jadu-bina` with valid UI metadata"
- "Re-review the deck after the slide 9 loop-card spacing fix"

## Step 5 - Hand findings back to the executor

After logging them, report findings in priority order:

- What is wrong
- Where it is
- Why it matters
- What a passing fix must achieve

Do not bury the finding under a long summary.
Do not approve the work while unchecked tasks remain.

## Step 6 - Re-review from fresh artifacts

When the executor says a fix is done:

1. Re-open the updated artifact or verification output.
2. Check the specific issue again.
3. Check for collateral regressions around the changed area.
4. Mark the related task or subtask complete only if the fix truly passes.

If the fix is incomplete, log the remaining gap clearly and continue the loop.

## Exit conditions

Stay in the loop until one of these is true:

- No material findings remain.
- A real blocker needs a user decision.
- The remaining work is outside the approved scope and needs new approval.

"Close enough" is not an exit condition.

## Deck-specific rubric

When reviewing presentation decks, check at minimum:

- Narrative: each slide has a job and the sequence teaches or persuades cleanly.
- Copy: audience-facing, natural, concrete, and not tool-internal.
- Layout: no overlap, clipping, empty broken cards, or accidental whitespace traps.
- Consistency: typography, spacing, borders, labels, and status accents stay coherent.
- Teaching value: if the deck is for beginners, it should reduce confusion rather than show off vocabulary.

Use [references/review-rubric.md](references/review-rubric.md) for the compact rubric and issue format.

## Skill-specific rubric

When reviewing a skill:

- Confirm the description clearly says what the skill does and when it should trigger.
- Confirm the workflow is executable by another agent without hidden context.
- Confirm any referenced files actually exist.
- Confirm validation was run when appropriate.
- Confirm the skill does not promise impossible behavior.

## Rules

- Stay reviewer-first. Do not silently become the executor without saying so.
- Preserve Jadu approval gates. If a fix would expand implementation scope, surface that.
- Prefer concrete findings over stylistic churn.
- If no findings remain, say so plainly and close the loop.
