#!/usr/bin/env python3
"""
run_loop.py — runs jadu-loop task after task, unattended, without ever
running into usage credits.

Before each run: check_loop_queue.py (anything to do?), then the usage gate
  (check_usage_margin.py). WAIT -> sleep POLL_SECONDS and ask again, however
  long it takes (a weekly limit can mean days). STOP -> notify and exit.
During a run: a watchdog asks the gate against the ceilings every
  WATCH_SECONDS and kills the run once a limit reaches its ceiling (or the
  subscription line disappears). A slow or failed /usage is not a limit: only
  MAX_CHECK_FAILURES unreadable checks in a row stop the run. LOOP_TASK.md
  holds the progress, so the next run picks the task back up after the reset.
  The watchdog also kills a run that goes HARD_CAP_SECONDS without a new
  commit or a change to LOOP_TASK.md, and marks the open subtask `TIMEOUT 1`
  (then `TIMEOUT 2`); the skill retries the first and gives up on the second.
After a run: three runs in a row that change nothing stop the loop, killed
  runs included.
On a block: exit (default), or with --wait-on-block stay alive, check
  LOOP_TASK.md every BLOCK_POLL_SECONDS, and continue once STATUS is no
  longer blocked (2026-10-22: a late unblock must not leave the loop dead).

Usage:
    python3 scripts/jadu-loop/run_loop.py                        # /jadu-loop
    python3 scripts/jadu-loop/run_loop.py "/jadu-loop-best-practice --task"
    python3 scripts/jadu-loop/run_loop.py --model <session model> --effort <session effort>
    python3 scripts/jadu-loop/run_loop.py "/jadu-loop-best-practice --task"         --model fable --effort xhigh --allow-fable
        # Fable only with --allow-fable: on plans with a separate Fable weekly line,
        # check_usage_margin.py watches it; without the flag, Fable -> MODEL
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_usage_margin as usage  # noqa: E402
from check_loop_queue import STATUS_RE  # noqa: E402

MODEL = "opus"  # always named: a Fable model in -p can bill usage credits; see --allow-fable
POLL_SECONDS = 600
WATCH_SECONDS = 180
PAUSE_SECONDS = 20
MAX_STALLS = 3
MAX_CHECK_FAILURES = 3
BLOCK_POLL_SECONDS = 60
HARD_CAP_SECONDS = 30 * 60
TIMEOUT = "timeout"

ROOT = Path.cwd()
LOG = ROOT / ".loop_state" / "runs.log"
OUTBOX = ROOT / ".loop_state" / "telegram.md"
QUEUE_GATE = Path(__file__).resolve().parent / "check_loop_queue.py"
CLAUDE_CMD = [shutil.which("claude") or "claude"]
# The subtask a run is working on: the first open box not already given up on.
OPEN_SUBTASK_RE = re.compile(r"^- \[ \] (?!.*(?:BLOCKED|SKIPPED)).+$", re.MULTILINE)


def log(line: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')} {line}\n")


def send_outbox() -> None:
    """Send the Telegram message a task left in OUTBOX. The runner sends it, not the task:
    inside `claude -p` the global script's path breaks under MSYS_NO_PATHCONV, and only
    the runner's environment is sure to hold the bot token (2026-10-21)."""
    if not OUTBOX.exists():
        return
    text = OUTBOX.read_text(encoding="utf-8").strip()
    if not text:
        OUTBOX.unlink()
        return
    sent = subprocess.run(
        [sys.executable, str(usage.NOTIFY_SCRIPT), text], capture_output=True
    ).returncode == 0
    if sent:
        OUTBOX.unlink()
        log("telegram: task message sent")
    else:  # kept, not retried: the owner reads it from the file
        unsent = OUTBOX.with_name(f"telegram-unsent-{datetime.now():%Y%m%d-%H%M%S}.md")
        OUTBOX.rename(unsent)
        log(f"telegram: send failed, message kept in .loop_state/{unsent.name}")


def progress_state() -> str:
    h = hashlib.md5()
    task = ROOT / "LOOP_TASK.md"
    if task.exists():
        h.update(task.read_bytes())
    for name in ("LOOP_TASK_ARCHIVE", "LOOP_TASK_QUEUE"):
        folder = ROOT / name
        if folder.is_dir():
            h.update("\n".join(sorted(p.name for p in folder.iterdir())).encode())
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    h.update(head.stdout.encode())
    return h.hexdigest()


def mark_timeout() -> str | None:
    """Tag the open subtask TIMEOUT 1, or TIMEOUT 1 -> TIMEOUT 2. Returns the mark."""
    task = ROOT / "LOOP_TASK.md"
    if not task.exists():
        return None
    text = task.read_text(encoding="utf-8")
    m = OPEN_SUBTASK_RE.search(text)
    if not m:
        return None
    line = m.group(0)
    if "TIMEOUT 2" in line:
        return "TIMEOUT 2"
    if "TIMEOUT 1" in line:
        new, mark = line.replace("TIMEOUT 1", "TIMEOUT 2"), "TIMEOUT 2"
    else:
        new, mark = f"{line} — TIMEOUT 1", "TIMEOUT 1"
    task.write_text(text[: m.start()] + new + text[m.end() :], encoding="utf-8")
    return mark


def wait_for_go(sleep=time.sleep) -> bool:
    """Sleep until the usage gate says GO. False means STOP (a human must look)."""
    while True:
        verdict, reason = usage.check()
        usage.notify_change(verdict, reason)
        log(f"usage: {reason}")
        if verdict == usage.GO:
            return True
        if verdict == usage.STOP:
            return False
        sleep(POLL_SECONDS)


def task_blocked() -> bool:
    """Reads STATUS the way the queue gate does, so `STATUS: Blocked` or `STATUS:blocked`
    is a block here too, not "nothing to do" (2026-10-29)."""
    task = ROOT / "LOOP_TASK.md"
    if not task.exists():
        return False
    match = STATUS_RE.search(task.read_text(encoding="utf-8"))
    return bool(match) and match.group(1).lower() == "blocked"


def wait_for_unblock(sleep=time.sleep) -> None:
    """--wait-on-block: stay alive until the watching session (or a human) clears the block."""
    log(f"waiting for unblock, checking every {BLOCK_POLL_SECONDS}s")
    while task_blocked():
        sleep(BLOCK_POLL_SECONDS)
    log("task unblocked, loop continues")


def kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
    else:
        os.killpg(proc.pid, signal.SIGTERM)
    proc.wait()


def project_allow() -> list[str]:
    """The project's own allowlist. Passed on the command line because Claude Code
    ignores .claude/settings.json in a folder it has not trusted (2026-10-17)."""
    allow = []
    for name in ("settings.json", "settings.local.json"):
        f = ROOT / ".claude" / name
        if not f.exists():
            continue
        try:
            settings = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:  # a hand-edit must not kill an unattended loop
            log(f"allowlist: skipped .claude/{name}, not valid JSON: {e}")
            continue
        allow += settings.get("permissions", {}).get("allow", [])
    return allow


def resolve_model(model: str, allow_fable: bool = False) -> str:
    """The model for `claude -p`. A Fable model is replaced by MODEL unless the owner passed
    --allow-fable: on this plan Fable has its own weekly allowance, which the usage gate
    watches (2026-10-21); on a plan without that line, Fable in -p would bill usage credits."""
    if "fable" not in model.lower():
        return model
    if not allow_fable:
        log(f"model {model} is Fable, using {MODEL} instead (pass --allow-fable to keep it)")
        return MODEL
    os.environ[usage.FABLE_RUN_ENV] = "1"  # the gate now judges, and requires, the Fable line
    return model


def run_task(prompt: str, model: str = MODEL, effort: str | None = None) -> str | None:
    """One `claude -p` run under the watchdog. Returns why it was killed, or None."""
    out_file = ROOT / ".loop_state" / "last_run.out"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    cmd = [*CLAUDE_CMD, "-p", prompt, "--model", model, "--permission-mode", "acceptEdits"]
    if effort:
        cmd += ["--effort", effort]
    allow = project_allow()
    if allow:
        cmd += ["--allowedTools", *allow]  # variadic: keep last
    killed = None
    with out_file.open("w", encoding="utf-8") as out:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=subprocess.STDOUT,
            cwd=ROOT,
            env=env,
            start_new_session=os.name != "nt",
        )
        failures = 0
        state, moved = progress_state(), time.monotonic()
        while True:
            try:
                proc.wait(timeout=WATCH_SECONDS)
                break
            except subprocess.TimeoutExpired:
                now = progress_state()
                if now != state:
                    state, moved = now, time.monotonic()
                elif time.monotonic() - moved >= HARD_CAP_SECONDS:
                    killed = TIMEOUT
                    kill_tree(proc)
                    break
                verdict, reason = usage.check(watch=True)
                # A slow or failed /usage is not a limit: only a reading over the ceiling, or
                # MAX_CHECK_FAILURES unreadable checks in a row, stops the run (2026-10-16).
                if usage.unreadable(reason):
                    failures += 1
                    log(f"usage check failed ({failures}/{MAX_CHECK_FAILURES}), run continues: {reason}")
                    if failures < MAX_CHECK_FAILURES:
                        continue
                else:
                    failures = 0
                if verdict != usage.GO:
                    killed = reason
                    kill_tree(proc)
                    break
    with LOG.open("a", encoding="utf-8") as f:
        f.write(out_file.read_text(encoding="utf-8", errors="replace"))
    return killed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run jadu-loop unattended inside the plan's limits"
    )
    parser.add_argument("prompt", nargs="?", default="/jadu-loop")
    parser.add_argument("--max-runs", type=int, default=80)
    parser.add_argument("--model", default=MODEL, help="the starting session's model")
    parser.add_argument("--effort", help="the starting session's effort level")
    parser.add_argument(
        "--allow-fable",
        action="store_true",
        help="run a Fable model in -p (owner's explicit choice; the gate watches the Fable weekly line)",
    )
    parser.add_argument(
        "--wait-on-block",
        action="store_true",
        help="on a blocked task, wait for STATUS to leave 'blocked' instead of exiting",
    )
    parser.add_argument(
        "--queue",
        action="store_true",
        help="run when only LOOP_TASK_QUEUE/ has tasks (the task run promotes one); for jadu-loop-best-practice",
    )
    args = parser.parse_args(argv)
    args.model = resolve_model(args.model, args.allow_fable)
    log(f"model {args.model}, effort {args.effort or 'default'}")
    send_outbox()  # left by a task run by hand, without the runner

    stalls = 0
    for i in range(1, args.max_runs + 1):
        gate = [sys.executable, str(QUEUE_GATE)] + (["--queue"] if args.queue else [])
        result = subprocess.run(gate, cwd=ROOT, capture_output=True, text=True)
        if result.stderr.strip():
            log(f"queue gate: {result.stderr.strip()}")
        if result.returncode != 0:
            if task_blocked():
                log("task is blocked, loop needs a human")
                if args.wait_on_block:
                    usage.notify(
                        "jadu-loop is waiting on a block (see the BLOCKED line in LOOP_TASK.md); "
                        "it continues by itself once STATUS is back to idle."
                    )
                    wait_for_unblock()
                    continue
                usage.notify(
                    "jadu-loop STOPPED, needs you: a subtask is blocked (see the BLOCKED line in LOOP_TASK.md)."
                )
                return 1
            log("queue gate: nothing to do, loop finished")
            return 0
        if not wait_for_go():
            log("usage gate said STOP, loop needs a human")
            return 1
        before = progress_state()
        log(f"=== run {i} ===")
        killed = run_task(args.prompt, args.model, args.effort)
        send_outbox()
        stalls = stalls + 1 if progress_state() == before else 0
        if stalls >= MAX_STALLS:
            log(f"no progress in {MAX_STALLS} runs, stopping")
            usage.notify(usage.say("stalled", n=MAX_STALLS))
            return 1
        if killed == TIMEOUT:
            mark = mark_timeout() or "TIMEOUT"
            log(f"watchdog stopped the run: no progress in {HARD_CAP_SECONDS // 60} min, marked {mark}")
            usage.notify(usage.say("timeout", minutes=HARD_CAP_SECONDS // 60, mark=mark))
        elif killed:
            log(f"watchdog stopped the run: {killed}")
            usage.notify(usage.say("killed", why=usage.explain(killed)))
            continue  # wait_for_go sleeps until the limit resets
        time.sleep(PAUSE_SECONDS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
