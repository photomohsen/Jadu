import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "jadu-loop" / "check_loop_queue.py"


def gate(loop_task: str | None) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        if loop_task is not None:
            Path(tmp, "LOOP_TASK.md").write_text(loop_task, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT)], cwd=tmp, capture_output=True
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


if __name__ == "__main__":
    unittest.main()
