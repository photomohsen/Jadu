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

Usage:
    python3 scripts/jadu-loop/run_loop.py                        # /jadu-loop
    python3 scripts/jadu-loop/run_loop.py "/jadu-loop-best-practice --task"
    python3 scripts/jadu-loop/run_loop.py --model <session model> --effort <session effort>
"""

import argparse
import hashlib
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

MODEL = "opus"  # always named: Fable models bill usage credits in -p mode
POLL_SECONDS = 600
WATCH_SECONDS = 180
PAUSE_SECONDS = 20
MAX_STALLS = 3
MAX_CHECK_FAILURES = 3
HARD_CAP_SECONDS = 30 * 60
TIMEOUT = "timeout"

ROOT = Path.cwd()
LOG = ROOT / ".loop_state" / "runs.log"
QUEUE_GATE = Path(__file__).resolve().parent / "check_loop_queue.py"
CLAUDE_CMD = [shutil.which("claude") or "claude"]
# The subtask a run is working on: the first open box not already given up on.
OPEN_SUBTASK_RE = re.compile(r"^- \[ \] (?!.*(?:BLOCKED|SKIPPED)).+$", re.MULTILINE)


def log(line: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')} {line}\n")


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


def kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
    else:
        os.killpg(proc.pid, signal.SIGTERM)
    proc.wait()


def run_task(prompt: str, model: str = MODEL, effort: str | None = None) -> str | None:
    """One `claude -p` run under the watchdog. Returns why it was killed, or None."""
    out_file = ROOT / ".loop_state" / "last_run.out"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    cmd = [*CLAUDE_CMD, "-p", prompt, "--model", model, "--permission-mode", "acceptEdits"]
    if effort:
        cmd += ["--effort", effort]
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
    args = parser.parse_args(argv)
    if "fable" in args.model.lower():  # Fable bills usage credits in -p mode
        log(f"model {args.model} is Fable, using {MODEL} instead")
        args.model = MODEL
    log(f"model {args.model}, effort {args.effort or 'default'}")

    stalls = 0
    for i in range(1, args.max_runs + 1):
        if subprocess.run([sys.executable, str(QUEUE_GATE)], cwd=ROOT).returncode != 0:
            log("queue gate: nothing to do, loop finished")
            return 0
        if not wait_for_go():
            log("usage gate said STOP, loop needs a human")
            return 1
        before = progress_state()
        log(f"=== run {i} ===")
        killed = run_task(args.prompt, args.model, args.effort)
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
