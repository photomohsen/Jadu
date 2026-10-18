#!/usr/bin/env python3
"""
check_loop_queue.py — cheap, read-only gate deciding whether jadu-loop's
expensive agent invocation is worth paying for right now.

A fast, no-LLM pre-check that the shell's `&&` composes with the real
command, so a "nothing to do" tick never spends a token.

Reads LOOP_TASK.md's STATUS line directly (regex, no parsing library needed):
  - missing file, or STATUS: blocked           -> exit 1 (never run the agent)
  - STATUS: idle, no open (non-BLOCKED) subtask -> exit 1 (nothing to do)
  - STATUS: idle, at least one open subtask     -> exit 0 (proceed)

Usage:
    python3 scripts/jadu-loop/check_loop_queue.py && claude -p "/jadu-loop"
"""

import re
import sys
from pathlib import Path

LOOP_TASK_FILE = Path.cwd() / "LOOP_TASK.md"

STATUS_RE = re.compile(r"^STATUS:\s*(\w+)", re.MULTILINE)
# An open subtask is an unchecked box whose own block isn't marked BLOCKED.
# Subtask blocks look like:
#   - [ ] <id>
#     TYPE: ...
#     ACTION: ...
#     VERIFY: ...
# and a blocked one gets "BLOCKED" appended to its id line by jadu-loop itself.
OPEN_SUBTASK_RE = re.compile(r"^- \[ \] (?!.*BLOCKED).+$", re.MULTILINE)


def main() -> None:
    if not LOOP_TASK_FILE.exists():
        print("no LOOP_TASK.md — nothing queued", file=sys.stderr)
        sys.exit(1)

    text = LOOP_TASK_FILE.read_text(encoding="utf-8")

    status_match = STATUS_RE.search(text)
    status = status_match.group(1).lower() if status_match else None

    if status == "blocked":
        print("STATUS: blocked — will not invoke the agent until manually cleared", file=sys.stderr)
        sys.exit(1)

    if status != "idle":
        print(
            f"STATUS missing or unrecognized ({status!r}) — treating as nothing to do",
            file=sys.stderr,
        )
        sys.exit(1)

    if OPEN_SUBTASK_RE.search(text):
        print("open subtask found — proceeding", file=sys.stderr)
        sys.exit(0)

    print("STATUS: idle, no open subtasks — nothing to do", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
