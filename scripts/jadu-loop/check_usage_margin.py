#!/usr/bin/env python3
"""
check_usage_margin.py — free pre-check that keeps jadu-loop inside the plan's
own limits, so it never runs into usage credits (extra usage) unasked.

Queries `claude -p "/usage"` (headless, no model turn, $0) and answers one of:
  GO   (exit 0) — every limit is under its line, run the next task
  WAIT (exit 2) — a limit is at/over its line; sleep and check again later
  STOP (exit 1) — something is wrong (not on the subscription, API key set,
                  wrong login, usage unreadable); a human has to look

The 5-hour and weekly limits are judged separately, each with two lines:
  start   — a new task starts only while usage is under this
  ceiling — a task already running is stopped (by run_loop.py's watchdog) here
The gap between them is room for a started task to finish. Usage only drops
when a limit resets, so "back under the start line" means "it has reset".
Plans that include Fable show a third line, "Current week (Fable)". It is judged like
the weekly limit, and required, only for a Fable run (JADU_FABLE_RUN, set by
run_loop.py --allow-fable); other runs ignore it.

Notifies once per pause (not every tick) and once on resume.

Usage:
    python3 scripts/jadu-loop/check_loop_queue.py \
      && python3 scripts/jadu-loop/check_usage_margin.py \
      && claude -p "/jadu-loop" --model opus
    python3 scripts/jadu-loop/check_usage_margin.py --watch   # judge against the ceilings
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# name: (regex on the /usage text, start line %, ceiling %)
LIMITS = {
    "5-hour": (re.compile(r"Current session:\s*(\d+)% used(?:\s*·\s*resets\s*(.+))?"), 80, 90),
    "weekly": (
        re.compile(r"Current week \(all models\):\s*(\d+)% used(?:\s*·\s*resets\s*(.+))?"),
        95,
        98,
    ),
    # Fable has its own weekly allowance on this plan (a separate /usage line, 2026-10-21).
    # Judged only for a Fable run (run_loop.py --allow-fable), so it stops before that
    # allowance is used up and could fall through to usage credits.
    "weekly-fable": (
        re.compile(r"Current week \(Fable[^)]*\):\s*(\d+)% used(?:\s*·\s*resets\s*(.+))?"),
        95,
        98,
    ),
}
# Set (to any value) by run_loop.py --allow-fable. Only then is the Fable line judged, and
# then it is required: a Fable run with no readable Fable line waits instead of starting.
FABLE_RUN_ENV = "JADU_FABLE_RUN"
SUBSCRIPTION_LINE = "using your subscription"

GO, STOP, WAIT = 0, 1, 2
POLL_MINUTES = 10  # run_loop.py's POLL_SECONDS, for the message only

REPO_ROOT = Path.cwd()
FLAG_FILE = REPO_ROOT / ".loop_state" / "usage_margin_hit"
NOTIFY_SCRIPT = Path(__file__).resolve().parent / "notify_telegram.py"


def _claude(*args: str) -> str:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    # chat_usage_guard.py skips itself inside this call, so the hook never recurses.
    env["JADU_USAGE_CHECK"] = "1"
    proc = subprocess.run(
        [shutil.which("claude") or "claude", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,  # /usage sometimes takes over a minute; 60 s killed healthy runs (2026-10-16)
        env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"claude {' '.join(args)} exited {proc.returncode}: {proc.stderr.strip()}"
        )
    return proc.stdout


def fetch_usage_text() -> str:
    return json.loads(_claude("-p", "/usage", "--output-format", "json")).get("result", "")


class AuthUnreadable(Exception):
    """`claude auth status` answered but not as JSON: no wait fixes that, a human must look."""


def fetch_auth_method() -> str:
    # --json is the default today; named anyway so a changed default cannot break the parse.
    out = _claude("auth", "status", "--json")
    try:
        return json.loads(out).get("authMethod", "")
    except (json.JSONDecodeError, AttributeError) as e:
        raise AuthUnreadable(f"`claude auth status --json` is not JSON ({e})") from e


def parse_usage(text: str) -> dict[str, tuple[int, str]]:
    """{limit name: (percent used, reset text)} for every limit found in the text."""
    found = {}
    for name, (regex, _, _) in LIMITS.items():
        m = regex.search(text)
        if m:
            found[name] = (int(m.group(1)), (m.group(2) or "").strip())
    return found


def decide(text: str, auth_method: str, env: dict, watch: bool = False) -> tuple[int, str]:
    """Pure decision: (GO/WAIT/STOP, one-line reason)."""
    if env.get("ANTHROPIC_API_KEY"):
        return STOP, "ANTHROPIC_API_KEY is set — runs would bill that key, not the subscription"
    if auth_method != "claude.ai":
        return STOP, f"logged in via {auth_method!r}, not the claude.ai subscription"
    if SUBSCRIPTION_LINE not in text:
        return STOP, "/usage does not say 'using your subscription' — would spend usage credits"
    limits = dict(LIMITS)
    if not env.get(FABLE_RUN_ENV):
        del limits["weekly-fable"]  # an opus/sonnet run does not draw on the Fable allowance
    usage = parse_usage(text)
    missing = [name for name in limits if name not in usage]
    if missing:
        return WAIT, f"could not read {', '.join(missing)} usage from /usage"
    over = []
    for name, (_, start, ceiling) in limits.items():
        pct, resets = usage[name]
        line = ceiling if watch else start
        if pct >= line:
            over.append(f"{name} at {pct}% (line {line}%, resets {resets or '?'})")
    summary = ", ".join(f"{n} {usage[n][0]}%" for n in limits)
    if over:
        return WAIT, "paused: " + "; ".join(over)
    return GO, f"ok: {summary}"


def check(watch: bool = False) -> tuple[int, str]:
    try:
        auth_method = fetch_auth_method()
    except AuthUnreadable as e:  # retrying cannot fix the format, so stop and say why
        return STOP, f"auth check failed: {e}"
    except Exception as e:
        return WAIT, f"usage check failed: {e}"
    try:
        return decide(fetch_usage_text(), auth_method, dict(os.environ), watch)
    except Exception as e:  # unreadable usage is never treated as fine
        return WAIT, f"usage check failed: {e}"


def unreadable(reason: str) -> bool:
    """True when the check could not read usage at all (slow or broken /usage), as opposed to
    reading it and finding a limit over its line. The watchdog tolerates a few of these."""
    return reason.startswith(("usage check failed", "could not read"))


def notify(message: str) -> None:
    if NOTIFY_SCRIPT.exists():
        subprocess.run(
            [sys.executable, str(NOTIFY_SCRIPT), message], capture_output=True, text=True
        )


def notify_change(verdict: int, reason: str) -> None:
    """Message once when a pause/stop starts and once when it ends, not every tick."""
    if verdict == GO:
        if FLAG_FILE.exists():
            FLAG_FILE.unlink()
            notify(f"usage back under the lines — jadu-loop resuming ({reason})")
        return
    kind = "stop" if verdict == STOP else "wait"
    if not FLAG_FILE.exists() or FLAG_FILE.read_text(encoding="utf-8").strip() != kind:
        FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
        FLAG_FILE.write_text(kind + "\n", encoding="utf-8")
        if verdict == STOP:
            msg = f"STOPPED, needs you: {reason}"
        elif unreadable(reason):
            msg = f"jadu-loop waiting, usage unreadable, retrying every {POLL_MINUTES} min: {reason}"
        else:
            msg = f"jadu-loop waiting for the limit to reset: {reason}"
        notify(msg)


def main() -> None:
    verdict, reason = check(watch="--watch" in sys.argv)
    notify_change(verdict, reason)
    print(reason, file=sys.stderr)
    sys.exit(verdict)


if __name__ == "__main__":
    main()
