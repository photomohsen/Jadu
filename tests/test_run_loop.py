import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "jadu-loop"))
import check_usage_margin as usage  # noqa: E402
import run_loop  # noqa: E402


class RunLoopTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for name, value in {
            "ROOT": self.root,
            "LOG": self.root / "runs.log",
            "WATCH_SECONDS": 0.2,
            "PAUSE_SECONDS": 0,
            "OUTBOX": self.root / "telegram.md",
        }.items():
            patcher = mock.patch.object(run_loop, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = mock.patch.object(usage, "notify_change")
        patcher.start()
        self.addCleanup(patcher.stop)

    def fake_claude(self, body: str) -> None:
        script = self.root / "fake_claude.py"
        script.write_text(body, encoding="utf-8")
        run_loop.CLAUDE_CMD = [sys.executable, str(script)]

    def test_wait_sleeps_until_the_limit_resets(self):
        verdicts = [(usage.WAIT, "5-hour at 85%"), (usage.WAIT, "5-hour at 85%"), (usage.GO, "ok")]
        sleeps = []
        with mock.patch.object(usage, "check", side_effect=verdicts):
            self.assertTrue(run_loop.wait_for_go(sleep=sleeps.append))
        self.assertEqual(sleeps, [run_loop.POLL_SECONDS] * 2)

    def test_stop_ends_the_wait(self):
        with mock.patch.object(usage, "check", return_value=(usage.STOP, "not on subscription")):
            self.assertFalse(
                run_loop.wait_for_go(sleep=lambda s: self.fail("must not sleep on STOP"))
            )

    def test_watchdog_kills_a_run_at_the_ceiling(self):
        self.fake_claude("import time; print('working', flush=True); time.sleep(30)")
        started = time.monotonic()
        with mock.patch.object(usage, "check", return_value=(usage.WAIT, "5-hour at 90%")):
            killed = run_loop.run_task("/jadu-loop")
        self.assertEqual(killed, "5-hour at 90%")
        self.assertLess(time.monotonic() - started, 15)

    def test_run_under_the_ceiling_finishes(self):
        self.fake_claude("import time; time.sleep(0.5); print('done')")
        with mock.patch.object(usage, "check", return_value=(usage.GO, "ok")):
            self.assertIsNone(run_loop.run_task("/jadu-loop"))
        self.assertIn("done", (self.root / "runs.log").read_text(encoding="utf-8"))

    FAILED = (usage.WAIT, "usage check failed: timed out")

    def watch(self, verdicts):
        """run_task with the watchdog's checks answered in order. The fake run ends once
        the list is used up, so the outcome does not depend on timing."""
        done = self.root / "done"
        self.fake_claude(
            "import pathlib, time\n"
            f"end = time.monotonic() + 30\n"
            f"while not pathlib.Path({str(done)!r}).exists() and time.monotonic() < end:\n"
            "    time.sleep(0.05)\n"
        )
        script = list(verdicts)

        def check(watch=False):
            if script:
                return script.pop(0)
            done.touch()
            return usage.GO, "ok"

        with mock.patch.object(usage, "check", side_effect=check):
            return run_loop.run_task("/jadu-loop")

    def test_watchdog_rides_out_two_failed_checks(self):
        self.assertIsNone(self.watch([self.FAILED, self.FAILED, (usage.GO, "ok")]))

    def test_watchdog_kills_on_three_failed_checks_in_a_row(self):
        self.assertEqual(self.watch([self.FAILED] * 3), self.FAILED[1])

    def test_watchdog_resets_the_count_on_a_readable_check(self):
        sequence = [self.FAILED, self.FAILED, (usage.GO, "ok"), self.FAILED, self.FAILED]
        self.assertIsNone(self.watch(sequence))

    def test_no_progress_hits_the_hard_cap(self):
        self.fake_claude("import time; time.sleep(30)")
        started = time.monotonic()
        with (
            mock.patch.object(run_loop, "HARD_CAP_SECONDS", 0.5),
            mock.patch.object(usage, "check", return_value=(usage.GO, "ok")),
        ):
            self.assertEqual(run_loop.run_task("/jadu-loop"), run_loop.TIMEOUT)
        self.assertLess(time.monotonic() - started, 15)

    def test_timeout_marks_the_open_subtask_once_then_twice(self):
        task = self.root / "LOOP_TASK.md"
        task.write_text(
            "STATUS: idle\n\n- [x] 1\n- [ ] 2 — SKIPPED — broke\n- [ ] 3\n  TYPE: code\n- [ ] 4\n",
            encoding="utf-8",
        )
        self.assertEqual(run_loop.mark_timeout(), "TIMEOUT 1")
        self.assertIn("- [ ] 3 — TIMEOUT 1\n", task.read_text(encoding="utf-8"))
        self.assertEqual(run_loop.mark_timeout(), "TIMEOUT 2")
        self.assertIn("- [ ] 3 — TIMEOUT 2\n  TYPE: code\n- [ ] 4\n", task.read_text(encoding="utf-8"))

    def test_killed_runs_without_progress_count_as_stalls(self):
        (self.root / "LOOP_TASK.md").write_text("STATUS: idle\n\n- [ ] 1\n", encoding="utf-8")
        with (
            mock.patch.object(usage, "check", return_value=(usage.GO, "ok")),
            mock.patch.object(usage, "notify"),
            mock.patch.object(run_loop, "run_task", return_value="5-hour at 90%") as run_task,
            mock.patch.object(run_loop.time, "sleep"),
        ):
            self.assertEqual(run_loop.main([]), 1)
        self.assertEqual(run_task.call_count, run_loop.MAX_STALLS)

    def test_loop_exits_when_the_gate_says_stop(self):
        (self.root / "LOOP_TASK.md").write_text(
            "STATUS: idle\n\n- [ ] 1. Do it\n", encoding="utf-8"
        )
        with (
            mock.patch.object(usage, "check", return_value=(usage.STOP, "api key set")),
            mock.patch.object(run_loop, "run_task") as run_task,
        ):
            self.assertEqual(run_loop.main([]), 1)
        run_task.assert_not_called()

    def write_task(self, text: str) -> None:
        (self.root / "LOOP_TASK.md").write_text(text, encoding="utf-8")

    def test_progress_state_changes_when_the_task_file_changes(self):
        self.write_task("STATUS: idle\n\n- [ ] 1. Do it\n")
        before = run_loop.progress_state()
        self.write_task("STATUS: idle\n\n- [x] 1. Do it\n")
        self.assertNotEqual(run_loop.progress_state(), before)

    def test_progress_state_changes_when_a_task_is_archived_or_queued(self):
        for folder in ("LOOP_TASK_ARCHIVE", "LOOP_TASK_QUEUE"):
            (self.root / folder).mkdir()
            before = run_loop.progress_state()
            (self.root / folder / "010-x.md").write_text("x", encoding="utf-8")
            self.assertNotEqual(run_loop.progress_state(), before, folder)

    def test_progress_state_is_stable_when_nothing_changes(self):
        self.write_task("STATUS: idle\n\n- [ ] 1. Do it\n")
        (self.root / "LOOP_TASK_QUEUE").mkdir()
        (self.root / "LOOP_TASK_QUEUE" / "b.md").write_text("b", encoding="utf-8")
        (self.root / "LOOP_TASK_QUEUE" / "a.md").write_text("a", encoding="utf-8")
        self.assertEqual(run_loop.progress_state(), run_loop.progress_state())

    def test_nothing_to_do_ends_the_loop_cleanly_and_logs_why(self):
        self.write_task("STATUS: idle\n\n- [x] 1. Done\n")
        with mock.patch.object(run_loop, "run_task") as run_task:
            self.assertEqual(run_loop.main([]), 0)
        run_task.assert_not_called()
        log = (self.root / "runs.log").read_text(encoding="utf-8")
        self.assertIn("no open subtasks", log)
        self.assertIn("nothing to do, loop finished", log)

    def test_max_runs_bounds_the_loop(self):
        self.write_task("STATUS: idle\n\n- [ ] 1. Do it\n")
        calls = []

        def progress(*args):  # each run changes the task, so the stall check never fires
            calls.append(args)
            self.write_task(f"STATUS: idle\n\n- [ ] 1. Do it\n<!-- run {len(calls)} -->\n")

        with (
            mock.patch.object(usage, "check", return_value=(usage.GO, "ok")),
            mock.patch.object(run_loop, "run_task", side_effect=progress),
        ):
            self.assertEqual(run_loop.main(["--max-runs", "2"]), 0)
        self.assertEqual(len(calls), 2)

    def test_three_runs_without_progress_stop_the_loop(self):
        self.write_task("STATUS: idle\n\n- [ ] 1. Do it\n")
        with (
            mock.patch.object(usage, "check", return_value=(usage.GO, "ok")),
            mock.patch.object(usage, "notify"),
            mock.patch.object(run_loop, "run_task", return_value=None) as run_task,
        ):
            self.assertEqual(run_loop.main([]), 1)
        self.assertEqual(run_task.call_count, run_loop.MAX_STALLS)

    def test_a_block_exits_by_default(self):
        self.write_task("STATUS: blocked\n\n- [ ] 1. Do it BLOCKED\n")
        with mock.patch.object(usage, "notify"), mock.patch.object(run_loop, "run_task") as run_task:
            self.assertEqual(run_loop.main([]), 1)
        run_task.assert_not_called()

    def test_wait_for_unblock_returns_once_status_is_idle(self):
        self.write_task("STATUS: blocked\n")
        sleeps = []

        def sleep(seconds):
            sleeps.append(seconds)
            if len(sleeps) == 2:
                self.write_task("STATUS: idle\n")

        run_loop.wait_for_unblock(sleep=sleep)
        self.assertEqual(sleeps, [run_loop.BLOCK_POLL_SECONDS] * 2)

    def test_task_blocked_reads_status_like_the_gate(self):
        for text, blocked in [
            ("STATUS: blocked\n", True),
            ("STATUS: Blocked\n", True),
            ("STATUS:blocked\n", True),
            ("STATUS: idle\n\nnot STATUS: blocked\n", False),
            ("no status line\n", False),
        ]:
            self.write_task(text)
            self.assertEqual(run_loop.task_blocked(), blocked, text)

    def test_wait_on_block_notifies_waits_and_continues(self):
        self.write_task("STATUS: Blocked\n\n- [ ] 1. Do it BLOCKED\n")

        def unblock():
            self.write_task("STATUS: idle\n\n- [ ] 1. Do it\n")

        with (
            mock.patch.object(usage, "check", return_value=(usage.GO, "ok")),
            mock.patch.object(usage, "notify") as notify,
            mock.patch.object(run_loop, "wait_for_unblock", side_effect=unblock) as wait,
            mock.patch.object(run_loop, "run_task", return_value=None) as run_task,
        ):
            run_loop.main(["--wait-on-block", "--max-runs", "2"])
        wait.assert_called_once()
        self.assertIn("waiting on a block", notify.call_args_list[0][0][0])
        run_task.assert_called_once()

    def test_queue_flag_lets_a_queue_only_project_start(self):
        (self.root / "LOOP_TASK_QUEUE").mkdir()
        (self.root / "LOOP_TASK_QUEUE" / "010-next.md").write_text("STATUS: idle\n", encoding="utf-8")
        with mock.patch.object(run_loop, "run_task") as run_task:
            self.assertEqual(run_loop.main([]), 0)
        run_task.assert_not_called()
        with (
            mock.patch.object(usage, "check", return_value=(usage.GO, "ok")),
            mock.patch.object(run_loop, "run_task", return_value=None) as run_task,
        ):
            run_loop.main(["--queue", "--max-runs", "1"])
        run_task.assert_called_once()

    def test_fable_is_replaced_unless_allowed(self):
        with mock.patch.dict(run_loop.os.environ, {}, clear=False):
            run_loop.os.environ.pop(usage.FABLE_RUN_ENV, None)
            self.assertEqual(run_loop.resolve_model("fable"), run_loop.MODEL)
            self.assertNotIn(usage.FABLE_RUN_ENV, run_loop.os.environ)
            self.assertEqual(run_loop.resolve_model("fable", allow_fable=True), "fable")
            self.assertIn(usage.FABLE_RUN_ENV, run_loop.os.environ)
        self.assertEqual(run_loop.resolve_model("sonnet"), "sonnet")

    def test_project_allowlist_is_read_from_both_settings_files(self):
        (self.root / ".claude").mkdir()
        (self.root / ".claude" / "settings.json").write_text(
            '{"permissions": {"allow": ["Bash(git status)"]}}', encoding="utf-8")
        (self.root / ".claude" / "settings.local.json").write_text(
            '{"permissions": {"allow": ["Bash(pytest:*)"]}}', encoding="utf-8")
        self.assertEqual(run_loop.project_allow(), ["Bash(git status)", "Bash(pytest:*)"])

    def test_a_broken_settings_file_is_skipped_and_logged(self):
        (self.root / ".claude").mkdir()
        (self.root / ".claude" / "settings.json").write_text(
            '{"permissions": {"allow": ["Bash(git status)"]}}', encoding="utf-8")
        (self.root / ".claude" / "settings.local.json").write_text(
            '{"permissions": {"allow": ["Bash(pytest:*)",]}}', encoding="utf-8")
        self.assertEqual(run_loop.project_allow(), ["Bash(git status)"])
        self.assertIn("skipped .claude/settings.local.json",
                      (self.root / "runs.log").read_text(encoding="utf-8"))

    def test_outbox_is_sent_and_removed(self):
        run_loop.OUTBOX.write_text("task done", encoding="utf-8")
        with mock.patch.object(run_loop.subprocess, "run", return_value=mock.Mock(returncode=0)) as run:
            run_loop.send_outbox()
        self.assertIn("task done", run.call_args[0][0])
        self.assertFalse(run_loop.OUTBOX.exists())

    def test_outbox_send_failure_keeps_the_message(self):
        run_loop.OUTBOX.write_text("task done", encoding="utf-8")
        with mock.patch.object(run_loop.subprocess, "run", return_value=mock.Mock(returncode=1)):
            run_loop.send_outbox()
        self.assertFalse(run_loop.OUTBOX.exists())
        kept = list(self.root.glob("telegram-unsent-*.md"))
        self.assertEqual([k.read_text(encoding="utf-8") for k in kept], ["task done"])

    def test_loop_uses_the_session_model_and_effort_but_never_fable(self):
        (self.root / "LOOP_TASK.md").write_text("STATUS: idle\n\n- [ ] 1\n", encoding="utf-8")
        for model, want in (("claude-opus-5-5", "claude-opus-5-5"), ("claude-fable-5-1", run_loop.MODEL)):
            with (
                mock.patch.object(usage, "check", return_value=(usage.GO, "ok")),
                mock.patch.object(run_loop, "run_task", return_value=None) as run_task,
                mock.patch.object(run_loop.time, "sleep"),
            ):
                run_loop.main(["--max-runs", "1", "--model", model, "--effort", "xhigh"])
            run_task.assert_called_once_with("/jadu-loop", want, "xhigh")


if __name__ == "__main__":
    unittest.main()
