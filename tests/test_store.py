import contextlib
import io
import tempfile
import unittest
from datetime import date, datetime

from pulse import config, store
from pulse.sources import Snapshot, Story

IST = config.IST


def at(y, m, d, hh, mm, ss=0):
    return datetime(y, m, d, hh, mm, ss, tzinfo=IST)


def snap(when, n=10, source="hn", prefix="Story"):
    stories = tuple(Story(i, 100 + i, f"{prefix} {i}", f"https://example.com/{i}", 10 * i, i)
                    for i in range(1, n + 1))
    return Snapshot(when, source, stories)


def no_data(when, note="hn: TimeoutError; hn-algolia: HTTP 503 (Service Unavailable)"):
    return Snapshot(when, "none", (), note)


class Store(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_round_trip_with_awkward_text(self):
        stories = (
            Story(1, 41, 'Commas, "quotes", and \'more\'', 'https://e.com/a,b?q="x"', 1234, 56),
            Story(2, 42, "हिंदी में ताज़ा ख़बरें", "https://e.com/hi", 7, 0),
            Story(3, None, "Rocket 🚀 launch, again", "https://e.com/🚀", None, None),
        )
        original = Snapshot(at(2026, 10, 12, 10, 47), "hn-algolia", stories)
        path = store.append_snapshot(self.root, original)
        self.assertEqual(path, store.month_path(self.root, 2026, 10))
        self.assertTrue(path.as_posix().endswith("data/2026/2026-10.csv"))
        self.assertEqual(store.read_month(self.root, 2026, 10), [original])

    def test_none_round_trip(self):
        original = no_data(at(2026, 10, 12, 10, 47))
        store.append_snapshot(self.root, original)
        text = store.month_path(self.root, 2026, 10).read_text(encoding="utf-8")
        self.assertIn("2026-10-12T10:47:00+05:30,none,0,,(no data: hn: TimeoutError;", text)
        self.assertEqual(store.read_month(self.root, 2026, 10), [original])

    def test_counts_distinct_snapshots(self):
        for s in (snap(at(2026, 10, 12, 10, 47)), snap(at(2026, 10, 12, 15, 0)),
                  snap(at(2026, 10, 12, 15, 0)),  # same second, still its own snapshot
                  no_data(at(2026, 10, 13, 11, 0)), no_data(at(2026, 10, 13, 11, 0))):
            store.append_snapshot(self.root, s)
        self.assertEqual(store.counts_by_day(self.root, 2026, 10),
                         {date(2026, 10, 12): 3, date(2026, 10, 13): 2})
        self.assertEqual(store.counts_by_day(self.root, 2026, 11), {})

    def test_recent_snapshots_across_months_and_years(self):
        oct31, nov2 = snap(at(2026, 10, 31, 19, 0)), snap(at(2026, 11, 2, 10, 5))
        dec31, jan1 = snap(at(2026, 12, 31, 12, 0)), no_data(at(2027, 1, 1, 12, 0))
        for s in (nov2, oct31, jan1, dec31):
            store.append_snapshot(self.root, s)
        self.assertEqual(store.recent_snapshots(self.root, date(2026, 11, 1)), [oct31, nov2])
        self.assertEqual(store.recent_snapshots(self.root, date(2026, 12, 1)), [nov2, dec31])
        self.assertEqual(store.recent_snapshots(self.root, date(2027, 1, 1)), [dec31, jan1])

    def test_archive_stats_across_years(self):
        self.assertEqual(store.archive_stats(self.root), (0, 0, None))
        for s in (snap(at(2026, 12, 30, 10, 0)), snap(at(2026, 12, 30, 17, 0)),
                  snap(at(2026, 12, 31, 11, 0)), no_data(at(2027, 1, 2, 21, 59))):
            store.append_snapshot(self.root, s)
        self.assertEqual(store.archive_stats(self.root), (4, 3, date(2026, 12, 30)))

    def test_malformed_rows_are_skipped(self):
        good = [snap(at(2026, 10, 12, 10, 0), n=5), snap(at(2026, 10, 12, 12, 0), n=5)]
        for s in good:
            store.append_snapshot(self.root, s)
        path = store.month_path(self.root, 2026, 10)
        with open(path, "a", encoding="utf-8", newline="") as f:
            f.write("not,a,valid,row\n"
                    "2026-10-12T13:00:00+05:30,hn,abc,1,t,u,1,1\n"
                    "2026-10-12T13:00:00,hn,1,1,t,u,1,1\n"
                    "2026-10-12T13:00:00+05:30,weird,1,1,t,u,1,1\n"
                    "2026-10-12T13:00:00+05:30,hn,1,1,t\x00,u,1,1,extra\n")
        last = snap(at(2026, 10, 12, 14, 0), n=5)
        store.append_snapshot(self.root, last)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            result = store.read_month(self.root, 2026, 10)
        self.assertEqual(result, good + [last])
        self.assertEqual(len(err.getvalue().strip().splitlines()), 5)
        self.assertIn("skipped malformed row", err.getvalue())

    def test_lf_only(self):
        store.append_snapshot(self.root, snap(at(2026, 10, 12, 10, 47)))
        store.append_snapshot(self.root, no_data(at(2026, 10, 12, 11, 0)))
        data = store.month_path(self.root, 2026, 10).read_bytes()
        self.assertNotIn(b"\r\n", data)
        self.assertTrue(data.startswith(
            b"snapshot_at,source,rank,hn_id,title,url,points,comments\n"))
        self.assertEqual(data.count(b"\n"), 12)


if __name__ == "__main__":
    unittest.main()
