import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "jadu-loop"))
import check_usage_margin as usage  # noqa: E402

OK_AUTH = "claude.ai"


def usage_text(session: int, weekly: int, subscription: bool = True) -> str:
    head = (
        "You are currently using your subscription to power your Claude Code usage\n\n"
        if subscription
        else ""
    )
    return (
        f"{head}Current session: {session}% used · resets Oct 14, 2:19pm (Europe/Berlin)\n"
        f"Current week (all models): {weekly}% used · resets Oct 14, 11:59pm (Europe/Berlin)\n"
        "Current week (Fable): 0% used · resets Oct 15, 12am (Europe/Berlin)\n"
    )


class DecideTest(unittest.TestCase):
    def decide(self, text, auth=OK_AUTH, env=None, watch=False):
        return usage.decide(text, auth, env or {}, watch)[0]

    def test_under_both_start_lines_goes(self):
        self.assertEqual(self.decide(usage_text(79, 94)), usage.GO)

    def test_five_hour_start_line_80_waits(self):
        self.assertEqual(self.decide(usage_text(80, 10)), usage.WAIT)

    def test_weekly_start_line_95_waits(self):
        self.assertEqual(self.decide(usage_text(10, 95)), usage.WAIT)

    def test_running_task_may_finish_between_start_and_ceiling(self):
        self.assertEqual(self.decide(usage_text(89, 97), watch=True), usage.GO)

    def test_five_hour_ceiling_90_stops_the_run(self):
        self.assertEqual(self.decide(usage_text(90, 10), watch=True), usage.WAIT)

    def test_weekly_ceiling_98_stops_the_run(self):
        self.assertEqual(self.decide(usage_text(10, 98), watch=True), usage.WAIT)

    def test_not_on_subscription_stops(self):
        self.assertEqual(self.decide(usage_text(10, 10, subscription=False)), usage.STOP)

    def test_api_key_stops(self):
        self.assertEqual(
            self.decide(usage_text(10, 10), env={"ANTHROPIC_API_KEY": "x"}), usage.STOP
        )

    def test_other_login_stops(self):
        self.assertEqual(self.decide(usage_text(10, 10), auth="apiKey"), usage.STOP)

    def test_unreadable_usage_waits(self):
        self.assertEqual(self.decide("You are currently using your subscription\n"), usage.WAIT)

    def test_reason_names_the_limit_and_reset(self):
        _, reason = usage.decide(usage_text(10, 96), OK_AUTH, {})
        self.assertIn("weekly at 96%", reason)
        self.assertIn("Oct 14, 11:59pm", reason)

    def test_check_fails_closed(self):
        with mock.patch.object(usage, "fetch_usage_text", side_effect=RuntimeError("boom")):
            self.assertEqual(usage.check()[0], usage.WAIT)


    def test_fable_line_ignored_outside_a_fable_run(self):
        text = usage_text(10, 10).replace("Fable): 0%", "Fable): 99%")
        self.assertEqual(self.decide(text), usage.GO)

    def test_fable_run_waits_on_the_fable_line(self):
        text = usage_text(10, 10).replace("Fable): 0%", "Fable): 96%")
        self.assertEqual(self.decide(text, env={usage.FABLE_RUN_ENV: "1"}), usage.WAIT)

    def test_fable_run_without_a_fable_line_waits(self):
        text = usage_text(10, 10).split("Current week (Fable)")[0]
        self.assertEqual(self.decide(text, env={usage.FABLE_RUN_ENV: "1"}), usage.WAIT)

    def test_unreadable_reasons_are_told_apart_from_limits(self):
        self.assertTrue(usage.unreadable("usage check failed: timeout"))
        self.assertTrue(usage.unreadable("could not read weekly usage from /usage"))
        self.assertFalse(usage.unreadable("paused: 5-hour at 85% (line 80%, resets ?)"))


class AuthStatusTest(unittest.TestCase):
    """The real _claude() -> fetch_auth_method() -> check() path, with only subprocess faked."""

    def check_with_auth_output(self, out: str):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd[1:])
            body = out if cmd[1] == "auth" else '{"result": "x"}'
            return mock.Mock(returncode=0, stdout=body, stderr="")

        with mock.patch.object(usage.subprocess, "run", side_effect=fake_run):
            result = usage.check()
        return result, calls

    def test_asks_for_json_explicitly(self):
        _, calls = self.check_with_auth_output('{"authMethod": "claude.ai"}')
        self.assertIn(["auth", "status", "--json"], calls)

    def test_json_auth_status_reaches_decide(self):
        (verdict, reason), _ = self.check_with_auth_output('{"authMethod": "claude.ai"}')
        # the faked /usage text has no subscription line, so decide() ran and stopped on that
        self.assertEqual(verdict, usage.STOP)
        self.assertIn("using your subscription", reason)

    def test_text_auth_status_stops_instead_of_waiting_forever(self):
        (verdict, reason), _ = self.check_with_auth_output("Logged in\nMethod: claude.ai\n")
        self.assertEqual(verdict, usage.STOP)
        self.assertIn("auth check failed", reason)

    def test_failing_auth_command_still_waits(self):
        failed = mock.Mock(returncode=1, stdout="", stderr="network")
        with mock.patch.object(usage.subprocess, "run", return_value=failed):
            self.assertEqual(usage.check()[0], usage.WAIT)


class NotifyChangeTest(unittest.TestCase):
    def test_notifies_once_per_pause_and_once_on_resume(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch.object(usage, "FLAG_FILE", Path(tmp) / "flag"),
            mock.patch.object(usage, "notify") as notify,
        ):
            usage.notify_change(usage.WAIT, "paused")
            usage.notify_change(usage.WAIT, "paused")
            usage.notify_change(usage.STOP, "stop")
            usage.notify_change(usage.GO, "ok")
            usage.notify_change(usage.GO, "ok")
        self.assertEqual(notify.call_count, 3)


if __name__ == "__main__":
    unittest.main()
