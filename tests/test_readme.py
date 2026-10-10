import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from pulse import config, readme
from pulse.sources import Snapshot, Story

IST = config.IST


def at(d, hh, mm):
    return datetime(2026, 10, d, hh, mm, tzinfo=IST)


def snap(when, ids, source="hn", title=None):
    stories = tuple(Story(rank, i, title or f"Story {i}", f"https://example.com/{i}", 100 * i, i)
                    for rank, i in enumerate(ids, start=1))
    return Snapshot(when, source, stories)


def no_data(when):
    return Snapshot(when, "none", (), "hn: TimeoutError")


class Section(unittest.TestCase):
    def test_first_line_table_and_archive(self):
        recent = [snap(at(12, 10, 47), range(1, 11))]
        text = readme.render(recent, (1234, 456, datetime(2026, 10, 10).date()))
        lines = text.splitlines()
        self.assertEqual(lines[0], "**Last snapshot:** Mon 12 Oct 2026 · 10:47 IST · Hacker News API")
        self.assertIn("| # | Story | Points | Comments |", lines)
        self.assertIn("|--:|---|--:|--:|", lines)
        self.assertIn("| 1 | [Story 1](https://example.com/1) | 100 | 1 |", lines)
        self.assertIn("| 10 | [Story 10](https://example.com/10) | 1,000 | 10 |", lines)
        self.assertEqual(lines[-1], "**Archive:** 1,234 snapshots on 456 days since 10 Oct 2026, "
                                    "in monthly CSV files under [data/](data/).")
        self.assertNotIn("new since", text)

    def test_fallback_source_name_and_singulars(self):
        text = readme.render([snap(at(12, 10, 47), range(1, 6), source="hn-algolia")],
                             (1, 1, datetime(2026, 10, 12).date()))
        self.assertIn("· HN Algolia API (fallback)", text.splitlines()[0])
        self.assertIn("**Archive:** 1 snapshot on 1 day since 12 Oct 2026,", text)

    def test_new_story_count(self):
        prev = snap(at(12, 10, 47), range(1, 11))
        last = snap(at(12, 15, 5), [1, 2, 3, 4, 5, 6, 7, 11, 12, 13])
        text = readme.render([prev, last], (2, 1, prev.taken_at.date()))
        self.assertIn("3 of these stories are new since the previous snapshot "
                      "(Mon 12 Oct 2026 · 10:47 IST).", text)
        one = snap(at(12, 16, 0), [1, 2, 3, 4, 5, 6, 7, 11, 12, 99])
        self.assertIn("1 of these stories is new", readme.render([prev, last, one], (3, 1, None)))

    def test_none_latest_shows_last_good_snapshot(self):
        good = snap(at(12, 10, 47), range(1, 11))
        text = readme.render([good, no_data(at(12, 15, 0))], (2, 1, good.taken_at.date()))
        self.assertEqual(text.splitlines()[0],
                         "**Last check:** Mon 12 Oct 2026 · 15:00 IST · Hacker News was "
                         "unreachable. Showing the last good snapshot (Mon 12 Oct 2026 · 10:47 IST).")
        self.assertIn("| 1 | [Story 1](https://example.com/1) | 100 | 1 |", text)
        only_none = readme.render([no_data(at(12, 15, 0))], (1, 1, good.taken_at.date()))
        self.assertIn("no recent snapshot with data", only_none)
        self.assertNotIn("| # |", only_none)


class Escaping(unittest.TestCase):
    def test_markdown_escaping(self):
        self.assertEqual(readme.escape("A|B [x] *y* _z_ <b>"),
                         r"A\|B \[x\] \*y\* \_z\_ &lt;b&gt;")
        self.assertEqual(readme.escape("C:\\path `code`"), r"C:\\path \`code\`")

    def test_links(self):
        self.assertEqual(readme.link_target("https://e.com/a b(c)"), "https://e.com/a%20b%28c%29")
        self.assertEqual(readme.link_target("HTTP://e.com/x|y"), "HTTP://e.com/x%7Cy")
        self.assertIsNone(readme.link_target("javascript:alert(1)"))
        self.assertIsNone(readme.link_target("ftp://e.com/file"))
        story = Story(1, 1, "Odd *link*", "mailto:x@e.com", 1, 1)
        text = readme.render([Snapshot(at(12, 10, 0), "hn", (story,))], (1, 1, None))
        self.assertIn(r"| 1 | Odd \*link\* | 1 | 1 |", text)


class UpdateReadme(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.path = Path(self._tmp.name) / "README.md"

    def tearDown(self):
        self._tmp.cleanup()

    def test_replaces_between_markers_only(self):
        before = "# Title\n\nIntro *text*.\n\n"
        after = "\n\n## More\n\nFooter | with pipes\n"
        self.path.write_bytes(
            f"{before}{config.MARK_START}\nold stuff\n{config.MARK_END}{after}".encode("utf-8"))
        self.assertTrue(readme.update_readme(self.path, "NEW SECTION\n"))
        expected = f"{before}{config.MARK_START}\nNEW SECTION\n{config.MARK_END}{after}"
        self.assertEqual(self.path.read_bytes().decode("utf-8"), expected)
        self.assertFalse(readme.update_readme(self.path, "NEW SECTION\n"))
        self.assertEqual(self.path.read_bytes().decode("utf-8"), expected)

    def test_appends_markers_when_missing(self):
        self.path.write_bytes(b"# Title\r\n\r\nNo markers here.")
        readme.update_readme(self.path, "SECTION")
        expected = (f"# Title\n\nNo markers here.\n\n## Latest\n\n"
                    f"{config.MARK_START}\nSECTION\n{config.MARK_END}\n")
        self.assertEqual(self.path.read_bytes().decode("utf-8"), expected)
        self.assertFalse(readme.update_readme(self.path, "SECTION"))
        self.assertEqual(self.path.read_bytes().decode("utf-8"), expected)


class CommitMessage(unittest.TestCase):
    def test_normal(self):
        prev = snap(at(12, 9, 0), range(1, 11))
        last = snap(at(12, 10, 47), [21, 22, 23, 4, 5, 6, 7, 8, 9, 10],
                    title="Whistle: Speech to Text in 16.9 MB")
        self.assertEqual(readme.commit_message([prev, last]),
                         'pulse 10:47 IST · #1 "Whistle: Speech to Text in 16.9 MB" · 3 new')
        self.assertEqual(readme.commit_message([last]),
                         'pulse 10:47 IST · #1 "Whistle: Speech to Text in 16.9 MB"')

    def test_long_title_is_shortened(self):
        long = snap(at(12, 10, 47), range(1, 11), title="A really long headline " * 10)
        for recent in ([long], [snap(at(12, 9, 0), range(30, 40)), long]):
            msg = readme.commit_message(recent)
            self.assertLessEqual(len(msg), 72, msg)
            self.assertIn('…"', msg)
            self.assertTrue(msg.startswith('pulse 10:47 IST · #1 "A really long headline'))

    def test_none(self):
        msg = readme.commit_message([snap(at(12, 9, 0), range(1, 11)), no_data(at(12, 10, 47))])
        self.assertEqual(msg, "pulse 10:47 IST · no data, Hacker News unreachable")
        self.assertLessEqual(len(msg), 72)


if __name__ == "__main__":
    unittest.main()
