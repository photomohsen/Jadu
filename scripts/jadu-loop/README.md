# jadu-loop scripts

Small, dependency-light scripts that make `jadu-loop` safe to run unattended. Copy this whole `jadu-loop/` folder into your project's `scripts/` directory (or wherever you keep project scripts — just update the paths in `.claude/commands/jadu-loop.md` / `.codex/skills/jadu-loop/SKILL.md` if you move it).

```bash
mkdir -p /your-project/scripts
cp -R scripts/jadu-loop /your-project/scripts/
```

## What each script does

| Script | Purpose | Required? |
|---|---|---|
| `check_loop_queue.py` | Reads `LOOP_TASK.md`'s `STATUS` line and whether an open (non-`BLOCKED`) subtask exists. Exits `0` (proceed) only when there's real work to do — so the `&&` chain never spends a token on a "nothing to do" tick. | **Yes** — this is the actual gate |
| `check_usage_margin.py` | A second, free pre-check. Queries `claude -p "/usage"` ($0, no model turn) and judges the 5-hour and weekly limits separately: a new task starts only under the **start line** (5-hour 80%, weekly 95%). Exits `0` GO, `2` WAIT (a limit is over its line), `1` STOP (not on the subscription, `ANTHROPIC_API_KEY` set, or not a claude.ai login — a human must look). `--watch` judges against the **ceilings** (5-hour 90%, weekly 98%) instead. Edit `LIMITS` to change the numbers. | Recommended on Claude Code — it is what keeps the loop off usage credits |
| `run_loop.py` | The unattended runner. Before each task: queue gate, then usage gate — on WAIT it sleeps 10 minutes and asks again until the limit has reset, then continues by itself. During a task: a watchdog checks the ceilings every 3 minutes and stops the run if one is reached (the task resumes after the reset); a slow or failed `/usage` is tolerated twice and only the third in a row stops the run. It also stops a run that goes 30 minutes without a new commit or a change to `LOOP_TASK.md` and marks the open subtask `TIMEOUT 1` (a second time `TIMEOUT 2`, which the skill gives up on). Three runs in a row without progress, stopped runs included, end the loop. Always passes `--model opus` (Fable models bill usage credits in `-p` mode). | Recommended for unattended runs |
| `chat_usage_guard.py` | A `UserPromptSubmit` hook for normal chats: once a limit reaches its ceiling, it holds your message once and says why; sending it again goes through. | Optional |
| `notify_telegram.py` | Sends the loop's Telegram messages: one report when a task finishes, one when a run fails or stops early, and the runner's own pause/resume/timeout notes. | Optional — `jadu-loop`'s "Notify" step is a no-op if this script (or your own replacement) isn't present |

## Install

1. Copy `scripts/jadu-loop/` into your project (see above).
2. Install the one Python dependency these scripts need:
   ```bash
   pip3 install python-dotenv
   ```
3. Make sure `LOOP_TASK.md` (root of your project) and `LOOP_TASK_ARCHIVE/` (a tracked directory) exist — see `templates/jadu-loop/LOOP_TASK.skeleton.md`.
4. Add `.loop_state/` to your project's `.gitignore` — it holds only local run-state (the usage-margin flag file, and a lockfile if you add one — see "Concurrency" below). Never commit it.
5. If you want Telegram notifications, set up a bot (below) and copy `.env.example` into your project's `.env` (never commit `.env`).
6. Add whatever commands your `LOOP_TASK.md` subtasks will actually run to your agent's Bash/shell allowlist (e.g. Claude Code's `.claude/settings.local.json`) **before** running the loop — `jadu-loop` deliberately cannot expand its own permissions mid-run.

## Setting up Telegram notifications (optional)

1. Message [@BotFather](https://t.me/BotFather) on Telegram, run `/newbot`, follow the prompts. You'll get a bot token like `123456:ABC-DEF...`.
2. Create (or reuse) a group/channel you want notifications in, add the bot to it.
3. Get the chat ID: send any message in the group, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates` in a browser and read `"chat":{"id": ...}` from the JSON.
4. Add to your project's `.env`:
   ```
   LOOP_TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   LOOP_TELEGRAM_CHAT_ID=-100123456789
   ```
5. Optional: `LOOP_NOTIFY_LANG=fa` writes the runner's own messages in Persian (default `en`). The skills write their task reports in the language your project's rules name.
6. Test it: `python3 scripts/jadu-loop/notify_telegram.py "test message"`.

If your project already uses `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` (or similar) for something else — a customer-facing bot, an alerting bot — do **not** reuse those names. That's exactly why these are `LOOP_`-prefixed: a name collision makes this script silently post through the wrong bot. Grep your `.env` for existing names before wiring this up.

Don't want Telegram? Swap `send()` in `notify_telegram.py` for Slack/email/a webhook/anything else, or delete the script entirely — `jadu-loop`'s notify step degrades to a no-op if the script isn't there.

## Concurrency (optional, recommended if you'll run this via `cron`)

If you run the invocation chain on a schedule (rather than a single hand-run `while` loop), two overlapping invocations could both pass `check_loop_queue.py` and race on the same subtask. Wrap the whole chain in a `flock` so only one instance ever runs at a time:

```bash
flock -n .loop_state/jadu-loop.lock -c '
  python3 scripts/jadu-loop/check_loop_queue.py \
    && python3 scripts/jadu-loop/check_usage_margin.py \
    && claude -p "/jadu-loop" --permission-mode acceptEdits
'
```

`.loop_state/` must exist and be writable (create it once with `mkdir -p .loop_state`); the lockfile itself is created by `flock` on first run. A hand-run `while ...; sleep N; done` loop in its own terminal doesn't need this — it's inherently single-instance.

## Running unattended without touching usage credits

Usage credits (extra usage) kick in silently once a plan limit passes 100%, and `claude -p` has no "wait for the reset" option. `run_loop.py` does the waiting itself:

```bash
python3 scripts/jadu-loop/run_loop.py                  # runs /jadu-loop task after task
python3 scripts/jadu-loop/run_loop.py "/jadu-loop-best-practice --task"
```

| | Start new tasks below | Stop a running task at | Continues when |
|---|---|---|---|
| 5-hour limit | 80% | 90% | the 5-hour window resets |
| Weekly limit | 95% | 98% | the weekly window resets |

The gap between the two lines is room for a started task to finish. Progress lives in `LOOP_TASK.md`, so a task the watchdog stopped picks up where it left off. Its log goes to `.loop_state/runs.log`.

The only hard switch is turning usage credits off in claude.ai → Settings → Usage (on Team/Enterprise plans that is the org admin's setting). These scripts are the guard for when it stays on.

To also guard normal chats, copy `check_usage_margin.py` and `chat_usage_guard.py` side by side into e.g. `~/.claude/hooks/jadu-usage/` and register `chat_usage_guard.py` as a `UserPromptSubmit` hook (see its docstring).

On Windows, run the scripts with `python` instead of `python3`.
