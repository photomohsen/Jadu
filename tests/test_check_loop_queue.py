import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "jadu-loop" / "check_loop_queue.py"


def gate(loop_task: str | None, queued: bool = False, *flags: str) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        if loop_task is not None:
            Path(tmp, "LOOP_TASK.md").write_text(loop_task, encoding="utf-8")
        if queued:
            Path(tmp, "LOOP_TASK_QUEUE").mkdir()
            Path(tmp, "LOOP_TASK_QUEUE", "010-next.md").write_text("STATUS: idle\n", encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), *flags], cwd=tmp, capture_output=True
        ).returncode


class CheckLoopQueueTest(unittest.TestCase):
    def test_idle_with_open_subtask_proceeds(self):
        self.assertEqual(gate("STATUS: idle\n\n- [ ] 1. Do it — now\n"), 0)

    def test_no_file_blocks(self):
        self.assertEqual(gate(None), 1)

    def test_blocked_status_blocks(self):
        self.assertEqual(gate("STATUS: blocked\n\n- [ ] 1. Do it\n"), 1)

    def test_unknown_status_blocks(self):
        self.assertEqual(gate("STATUS: ready\n\n- [ ] 1. Do it\n"), 1)

    def test_only_done_or_blocked_subtasks_blocks(self):
        self.assertEqual(gate("STATUS: idle\n\n- [x] 1. Done\n- [ ] 2. Stuck BLOCKED\n"), 1)

    def test_queue_alone_blocks_without_the_flag(self):
        self.assertEqual(gate(None, True), 1)

    def test_queue_alone_proceeds_with_the_flag(self):
        self.assertEqual(gate(None, True, "--queue"), 0)

    def test_queue_flag_with_nothing_queued_blocks(self):
        self.assertEqual(gate(None, False, "--queue"), 1)

    def test_queue_flag_never_overrides_a_block(self):
        self.assertEqual(gate("STATUS: blocked\n\n- [ ] 1. Do it\n", True, "--queue"), 1)


if __name__ == "__main__":
    unittest.main()
