import contextlib
import io
import os
import unittest
from datetime import datetime
from unittest import mock

from pulse import config, store
from pulse.gitops import run_git
from pulse.main import main
from pulse.sources import Snapshot, Story
from tests.sandbox import GitSandbox

IST = config.IST
README = ("# tech-pulse\n\n## Latest\n\n"
          f"{config.MARK_START}\n_The first snapshot will appear here._\n{config.MARK_END}\n\n"
          "## Footer\n\nUntouched.\n")
SOURCE, DAILY, RUNS = "HC_SOURCE_URL", "HC_DAILY_URL", "HC_RUNS_URL"


def stories(prefix="Story"):
    return tuple(Story(i, 1000 + i, f"{prefix} {i}", f"https://example.com/{i}", 100 - i, i)
                 for i in range(1, 11))


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.box = GitSandbox({"README.md": README})
        self.work = self.box.work
        self.pings = []
        self.fetches = 0

    def tearDown(self):
        self.box.close()

    def ping(self, name, suffix=""):
        self.pings.append(name + suffix)
        return True

    def run_main(self, when, *argv, source="hn", env=None):
        self.pings.clear()
        now_fn = lambda: when  # noqa: E731

        def fetch():
            self.fetches += 1
            if source == "none":
                return Snapshot(now_fn(), "none", (), "test outage")
            return Snapshot(now_fn(), source, stories())

        out = io.StringIO()
        with mock.patch.dict(os.environ, env or {}), mock.patch("pulse.gitops.time.sleep"), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = main(list(argv), root=self.work, now_fn=now_fn, fetch=fetch, ping=self.ping)
        return code, out.getvalue()

    def csv_lines(self, year=2026, month=10):
        path = store.month_path(self.work, year, month)
        return path.read_text(encoding="utf-8").splitlines() if path.exists() else []

    def test_one_planned_snapshot_then_nothing(self):
        when = datetime(2026, 10, 12, 11, 30, tzinfo=IST)  # plan: 10:57
        code, out = self.run_main(when)
        self.assertEqual(code, 0)
        self.assertIn("[pulse] Mon 12 Oct 2026 11:30 IST · plan 1 at 10:57 · done 0 · taking 1", out)
        self.assertEqual(self.box.remote_count(), 2)
        self.assertEqual(len(self.csv_lines()), 11)
        self.assertEqual(self.pings, [SOURCE, DAILY, RUNS])
        self.assertEqual(self.box.remote_log("%an|%cn|%aI"),
                         f"{config.AUTHOR_NAME}|{config.BOT_NAME}|2026-10-12T11:30:00+05:30")
        text = (self.work / "README.md").read_text(encoding="utf-8")
        self.assertIn("[Story 1](https://example.com/1)", text)
        self.assertIn("## Footer\n\nUntouched.\n", text)
        self.assertEqual(run_git(self.work, "status", "--porcelain"), "")

        code, _ = self.run_main(when)
        self.assertEqual(code, 0)
        self.assertEqual(self.box.remote_count(), 2)
        self.assertEqual(self.pings, [RUNS])

    def test_nine_snapshot_day_final_call(self):
        when = datetime(2026, 10, 20, 21, 59, tzinfo=IST)
        code, out = self.run_main(when)
        self.assertEqual(code, 0)
        self.assertIn("plan 9 at 13:43,", out)
        self.assertEqual(self.box.remote_count(), 1 + 9)
        self.assertEqual(len(self.csv_lines()), 1 + 90)
        self.assertEqual(self.pings, [SOURCE] * 9 + [DAILY, RUNS])
        code, out = self.run_main(when)
        self.assertEqual(code, 0)
        self.assertIn("done 9 · taking 0", out)
        self.assertEqual(self.box.remote_count(), 1 + 9)

    def test_force(self):
        sunday = datetime(2026, 10, 11, 3, 0, tzinfo=IST)
        code, _ = self.run_main(sunday, env={"PULSE_FORCE": "true"})
        self.assertEqual((code, self.box.remote_count()), (0, 2))

        day = datetime(2026, 10, 21, 12, 0, tzinfo=IST)
        for hour in range(10, 18):  # eight snapshots already recorded today
            store.append_snapshot(self.work, Snapshot(day.replace(hour=hour), "hn", stories()))
        code, out = self.run_main(day, env={"PULSE_FORCE": "true"})
        self.assertEqual(code, 0)
        self.assertIn("done 8 · taking 0 (forced)", out)
        self.assertEqual(self.box.remote_count(), 2)
        self.assertEqual(self.pings, [RUNS])

    def test_simulated_failure(self):
        when = datetime(2026, 10, 12, 11, 30, tzinfo=IST)
        code, out = self.run_main(when, env={"PULSE_SIMULATE_FAILURE": "true"})
        self.assertEqual(code, 1)
        self.assertIn("alert drill: failing on purpose", out)
        self.assertEqual((self.box.remote_count(), self.pings, self.fetches), (1, [], 0))

    def test_no_data_snapshot_is_still_committed(self):
        when = datetime(2026, 10, 12, 11, 30, tzinfo=IST)
        code, _ = self.run_main(when, source="none")
        self.assertEqual(code, 0)
        self.assertEqual(self.box.remote_count(), 2)
        self.assertEqual(self.pings, [DAILY, RUNS])
        self.assertIn("(no data: test outage)", self.csv_lines()[1])
        self.assertEqual(self.box.remote_log("%s"),
                         "pulse 11:30 IST · no data, Hacker News unreachable")

    def test_push_failure(self):
        run_git(self.work, "remote", "set-url", "origin", str(self.box.base / "missing.git"))
        when = datetime(2026, 10, 12, 11, 30, tzinfo=IST)
        code, _ = self.run_main(when)
        self.assertEqual(code, 1)
        self.assertEqual(self.pings, [SOURCE])
        self.assertEqual(self.box.remote_count(), 1)

    def test_dry_run_changes_nothing(self):
        when = datetime(2026, 10, 12, 11, 30, tzinfo=IST)
        head = run_git(self.work, "rev-parse", "HEAD")
        code, out = self.run_main(when, "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("pulse 11:30 IST · #1 \"Story 1\"", out)
        self.assertIn("**Last snapshot:** Mon 12 Oct 2026 · 11:30 IST · Hacker News API", out)
        self.assertIn("**Archive:** 1 snapshot on 1 day since 12 Oct 2026", out)
        self.assertEqual(run_git(self.work, "status", "--porcelain", "--ignored"), "")
        self.assertEqual(run_git(self.work, "rev-parse", "HEAD"), head)
        self.assertEqual((self.box.remote_count(), self.pings), (1, []))


if __name__ == "__main__":
    unittest.main()
