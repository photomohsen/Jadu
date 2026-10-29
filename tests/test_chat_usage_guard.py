import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "jadu-loop"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import chat_usage_guard as guard  # noqa: E402
from test_check_usage_margin import usage_text  # noqa: E402

NOW = 1_000_000.0


class ChatGuardTest(unittest.TestCase):
    def test_under_the_ceilings_passes(self):
        self.assertIsNone(guard.decide(usage_text(89, 97), None, NOW))

    def test_five_hour_ceiling_holds_the_message(self):
        self.assertIn("5-hour at 90%", guard.decide(usage_text(90, 10), None, NOW))

    def test_weekly_ceiling_holds_the_message(self):
        self.assertIn("weekly at 98%", guard.decide(usage_text(10, 98), None, NOW))

    def test_not_on_subscription_holds_the_message(self):
        self.assertIsNotNone(guard.decide(usage_text(10, 10, subscription=False), None, NOW))

    def test_resending_after_a_hold_goes_through(self):
        self.assertIsNone(guard.decide(usage_text(95, 10), NOW - 60, NOW))

    def test_warns_again_after_the_ack_expires(self):
        self.assertIsNotNone(
            guard.decide(usage_text(95, 10), NOW - guard.ACK_MINUTES * 60 - 1, NOW)
        )


if __name__ == "__main__":
    unittest.main()
