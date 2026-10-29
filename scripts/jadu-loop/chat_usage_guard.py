#!/usr/bin/env python3
"""
chat_usage_guard.py — UserPromptSubmit hook that holds a chat message once a
plan limit reaches its ceiling (the same ceilings the loop's watchdog uses),
so a normal chat never slides into usage credits unnoticed.

Holds the message once and says why; sending it again goes through, and the
guard stays quiet for ACK_MINUTES after that. /usage is cached for
CACHE_MINUTES so most messages cost no extra call. If /usage can't be read the
message goes through: this guard must never lock you out of your own chat.

Install (copy this file and check_usage_margin.py side by side, e.g. into
~/.claude/hooks/jadu-usage/), then in ~/.claude/settings.json:
    "hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command",
        "command": "python ~/.claude/hooks/jadu-usage/chat_usage_guard.py",
        "timeout": 60}]}]}
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_usage_margin as usage  # noqa: E402

CACHE_MINUTES = 5
ACK_MINUTES = 30
STATE_DIR = Path(__file__).resolve().parent
CACHE = STATE_DIR / "usage_cache.json"
ACK = STATE_DIR / "usage_ack"


def usage_text(now: float) -> str:
    try:
        cached = json.loads(CACHE.read_text(encoding="utf-8"))
        if now - cached["at"] < CACHE_MINUTES * 60:
            return cached["text"]
    except (OSError, ValueError, KeyError):
        pass
    text = usage.fetch_usage_text()
    CACHE.write_text(json.dumps({"at": now, "text": text}), encoding="utf-8")
    return text


def over_ceiling(text: str) -> str | None:
    """Why this message should be held, or None."""
    if usage.SUBSCRIPTION_LINE not in text:
        return "/usage no longer says 'using your subscription' — this message would spend usage credits"
    found = usage.parse_usage(text)
    over = [
        f"{name} at {found[name][0]}% (line {ceiling}%, resets {found[name][1] or '?'})"
        for name, (_, _, ceiling) in usage.LIMITS.items()
        if name in found and found[name][0] >= ceiling
    ]
    return "; ".join(over) or None


def decide(text: str, acked_at: float | None, now: float) -> str | None:
    """The block reason to show, or None to let the message through."""
    reason = over_ceiling(text)
    if reason is None or (acked_at is not None and now - acked_at < ACK_MINUTES * 60):
        return None
    return (
        f"Held: {reason}. Send the message again to go on anyway "
        f"(no more warnings for {ACK_MINUTES} minutes)."
    )


def main() -> None:
    if os.environ.get("JADU_USAGE_CHECK"):
        return
    now = time.time()
    try:
        text = usage_text(now)
    except Exception:
        return
    acked_at = ACK.stat().st_mtime if ACK.exists() else None
    reason = decide(text, acked_at, now)
    if reason:
        ACK.touch()
        print(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    main()
