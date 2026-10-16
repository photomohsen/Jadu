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


class ExplainTest(unittest.TestCase):
    def test_unreadable_is_told_apart_from_a_limit(self):
        self.assertTrue(usage.unreadable("usage check failed: timed out after 180 seconds"))
        self.assertTrue(usage.unreadable("could not read weekly usage from /usage"))
        _, over = usage.decide(usage_text(10, 96), OK_AUTH, {})
        self.assertFalse(usage.unreadable(over))

    def test_explains_a_limit_in_plain_words_per_language(self):
        _, over = usage.decide(usage_text(91, 10), OK_AUTH, {}, watch=True)
        with mock.patch.dict(usage.os.environ, {"LOOP_NOTIFY_LANG": "en"}):
            self.assertEqual(
                usage.explain(over),
                "The 5-hour limit is at 91% (line 90%); it resets Oct 14, 2:19pm (Europe/Berlin).",
            )
        with mock.patch.dict(usage.os.environ, {"LOOP_NOTIFY_LANG": "fa"}):
            self.assertIn("سهمیه‌ی ۵ ساعته به 91٪", usage.explain(over))


if __name__ == "__main__":
    unittest.main()
