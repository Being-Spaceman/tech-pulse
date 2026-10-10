import unittest
from datetime import date, time, timedelta

from pulse import planner as P


def hhmm(times):
    return [t.strftime("%H:%M") for t in times]


class GoldenValues(unittest.TestCase):
    """Pinned outputs. If any of these fail, planner.py was not copied exactly."""

    def test_hash(self):
        self.assertEqual(P._u64("probe"), 5460208960125926599)

    def test_first_weeks(self):
        expected = {
            "2026-10-10": ["11:47"],
            "2026-10-11": [],
            "2026-10-12": ["10:57"],
            "2026-10-15": ["14:08", "19:17"],
            "2026-10-19": ["15:14", "15:24"],
            "2026-10-20": ["13:43", "14:42", "14:53", "15:21", "16:57",
                           "17:24", "17:37", "19:17", "19:29"],
            "2026-10-23": ["14:10", "14:59", "16:15", "16:57"],
            "2026-10-24": ["10:06"],
        }
        for iso, times in expected.items():
            day = date.fromisoformat(iso)
            k = P.planned_count(day)
            self.assertEqual(k, len(times), iso)
            self.assertEqual(hhmm(P.planned_times(day, k)), times, iso)

    def test_monthly_cap_golden(self):
        self.assertEqual(P.planned_count(date(2097, 5, 17)), 9)
        self.assertEqual(P.raw_count(date(2097, 5, 29)), 9)
        self.assertEqual(P.planned_count(date(2097, 5, 29)), 8)

    def test_actual_count_guard(self):
        self.assertEqual(P.planned_count(date(2026, 10, 20)), 9)
        self.assertEqual(P.planned_count(date(2026, 10, 20), {date(2026, 10, 5): 9}), 8)


class Properties(unittest.TestCase):
    def test_fifty_years(self):
        start = date(2026, 10, 1)
        counts = {k: 0 for k in range(10)}
        nine_days_per_month = {}
        workdays = 0
        for i in range(50 * 365):
            day = start + timedelta(days=i)
            k = P.planned_count(day)
            counts[k] += 1
            if day.weekday() == 6:
                self.assertEqual(k, 0, day)
                continue
            workdays += 1
            self.assertTrue(1 <= k <= 9, day)
            times = P.planned_times(day, k)
            self.assertEqual(len(times), k)
            self.assertEqual(times, sorted(times))
            self.assertTrue(time(10, 0) <= times[0] < time(16, 0), day)
            self.assertTrue(all(t < time(19, 30) for t in times), day)
            if k == 9:
                key = (day.year, day.month)
                nine_days_per_month[key] = nine_days_per_month.get(key, 0) + 1
        self.assertEqual(max(nine_days_per_month.values()), 1)
        share_of_ones = counts[1] / workdays
        self.assertTrue(0.47 < share_of_ones < 0.53, share_of_ones)
        mean = sum(k * c for k, c in counts.items()) / workdays
        self.assertTrue(1.9 < mean < 2.1, mean)


class TakeRule(unittest.TestCase):
    times = [time(11, 0), time(15, 0), time(18, 0)]

    def test_one_per_run_while_behind(self):
        self.assertEqual(P.snapshots_to_take(time(10, 47), self.times, 0), 0)
        self.assertEqual(P.snapshots_to_take(time(11, 5), self.times, 0), 1)
        self.assertEqual(P.snapshots_to_take(time(16, 0), self.times, 0), 1)
        self.assertEqual(P.snapshots_to_take(time(16, 0), self.times, 2), 0)

    def test_final_call_takes_the_rest(self):
        self.assertEqual(P.snapshots_to_take(time(21, 23), self.times, 0), 1)
        self.assertEqual(P.snapshots_to_take(time(21, 59), self.times, 0), 3)
        self.assertEqual(P.snapshots_to_take(time(21, 59), self.times, 3), 0)

    def test_force(self):
        self.assertEqual(P.snapshots_to_take(time(3, 0), self.times, 0, force=True), 1)
        self.assertEqual(P.snapshots_to_take(time(3, 0), [], 7, force=True), 1)
        self.assertEqual(P.snapshots_to_take(time(3, 0), [], 8, force=True), 0)
        # a forced snapshot counts toward the plan
        self.assertEqual(P.snapshots_to_take(time(11, 30), [time(11, 0)], 1), 0)


if __name__ == "__main__":
    unittest.main()
