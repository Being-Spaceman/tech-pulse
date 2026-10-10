"""Keeps the workflow's cron lines consistent with the planner's assumptions."""
import re
import unittest
from datetime import time
from pathlib import Path

from pulse import planner as P

WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "tech-pulse.yml"
CRON = re.compile(r'^\s*-\s*cron:\s*"(\d+) ([\d,]+) \* \* ([^"]+)"', re.M)


def runs_ist():
    text = WORKFLOW.read_text(encoding="utf-8")
    runs = []
    for minute, hours, dow in CRON.findall(text):
        assert dow == "1-6", f"runs must be Monday-Saturday only, got {dow!r}"
        for h in hours.split(","):
            total = int(h) * 60 + int(minute) + 330  # UTC -> IST (+5:30)
            assert total < 24 * 60, "a run would fall on the next IST date"
            runs.append(time(total // 60, total % 60))
    return sorted(runs), [int(m) for m, _, _ in CRON.findall(text)]


class Schedule(unittest.TestCase):
    def test_runs(self):
        runs, minutes = runs_ist()
        self.assertEqual(len(runs), 12)
        self.assertNotIn(0, minutes, "avoid minute 0: GitHub delays top-of-hour runs most")
        self.assertGreater(len(set(runs)), 11, "runs must not share a time")
        first_start = time(P.FIRST_START // 60, P.FIRST_START % 60)
        self.assertGreaterEqual(runs[0], first_start)
        self.assertLessEqual(runs[-1], time(22, 30))
        last_end = time(P.LAST_END // 60, P.LAST_END % 60)
        self.assertGreaterEqual(sum(t >= last_end for t in runs), 3,
                                "need spare runs after the last planned time")
        self.assertGreaterEqual(runs[-1], P.FINAL_CALL, "the last run must be a final call")
        self.assertGreaterEqual(sum(t < P.FINAL_CALL for t in runs), P.MAX_PER_DAY,
                                "a 9-snapshot day needs 9 separate runs")


if __name__ == "__main__":
    unittest.main()
