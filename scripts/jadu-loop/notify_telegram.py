#!/usr/bin/env python3
"""
Send a one-way Telegram notification for jadu-loop. Send-only — no
reply-mapping or thread-tracking; jadu-loop never reads replies.

Usage:
    python3 notify_telegram.py "your message here"
    echo "message" | python3 notify_telegram.py

Env vars (loaded from .env via python-dotenv):
    LOOP_TELEGRAM_BOT_TOKEN  — bot token from BotFather
    LOOP_TELEGRAM_CHAT_ID    — chat to send to

Named LOOP_-prefixed rather than a plain TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID,
in case your project already defines those generic names for something else
(e.g. an existing customer-facing bot) — reusing a generic name would make
this script silently post through the wrong bot. Check your project's own
.env for a naming collision before wiring this up.

This is a thin, swappable notifier: if you'd rather notify via Slack, email,
a webhook, or nothing at all, replace send() (or delete this script and the
"Notify" step in jadu-loop becomes a no-op — it's optional, not load-bearing).
"""

import argparse
import json
import os
import re
import sys
import urllib.request

from dotenv import load_dotenv

load_dotenv()

ICON = "\U0001f501"  # 🔁


def _neutralize_stray_underscores(text: str, parse_mode: str | None) -> str:
    """Legacy Telegram Markdown reads a single '_' as an italics marker. Identifiers
    like 'my_variable' or 'jadu_loop' show up in these messages and an unpaired
    underscore causes a hard 400 from the API — swap word_word underscores for a
    hyphen so sends never break on this."""
    if not parse_mode or "markdown" not in parse_mode.lower():
        return text
    return re.sub(r"(?<=\w)_(?=\w)", "-", text)


def send(message: str, chat_id: str | None = None, parse_mode: str | None = "Markdown") -> int | None:
    """Returns the sent message_id on success, None on failure."""
    token = os.environ.get("LOOP_TELEGRAM_BOT_TOKEN", "")
    chat_id = chat_id or os.environ.get("LOOP_TELEGRAM_CHAT_ID", "")
    if not token:
        print("Error: LOOP_TELEGRAM_BOT_TOKEN not set", file=sys.stderr)
        return None
    if not chat_id:
        print("Error: LOOP_TELEGRAM_CHAT_ID not set", file=sys.stderr)
        return None

    prefixed = message if message.startswith(ICON) else f"{ICON} jadu-loop: {message}"
    payload = {
        "chat_id": chat_id,
        "text": _neutralize_stray_underscores(prefixed, parse_mode),
        "disable_web_page_preview": True,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    data = json.dumps(payload).encode()

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                return None
            result = json.loads(resp.read()).get("result", {})
            return result.get("message_id")
    except Exception as e:
        print(f"Telegram send failed: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a one-way jadu-loop Telegram notification")
    parser.add_argument("message", nargs="?", help="Message to send (or pipe via stdin)")
    parser.add_argument("--chat-id", help="Override LOOP_TELEGRAM_CHAT_ID")
    parser.add_argument("--parse-mode", default="Markdown", help="Telegram parse_mode: Markdown, MarkdownV2, HTML, or 'none' to disable (default: Markdown)")
    args = parser.parse_args()

    parse_mode = None if args.parse_mode.lower() == "none" else args.parse_mode

    # stdin as UTF-8: Windows Python reads pipes as cp1252 and breaks Persian and emoji (2026-10-18)
    message = args.message or sys.stdin.buffer.read().decode("utf-8").strip()
    if not message:
        print("Error: no message provided", file=sys.stderr)
        sys.exit(1)

    mid = send(message, args.chat_id, parse_mode)
    print(f"sent {mid}" if mid else "failed")
    sys.exit(0 if mid else 1)
