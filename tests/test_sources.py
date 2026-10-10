import http.client
import json
import socket
import ssl
import unittest
from datetime import datetime, timedelta, timezone

from pulse import config, sources
from pulse.sources import Snapshot

FB = sources.FIREBASE
NOW = datetime(2026, 10, 12, 5, 17, 30, 987654, tzinfo=timezone.utc)  # 10:47:30 IST


def now_fn():
    return NOW


def no_sleep(_seconds):
    pass


def item(i, **changes):
    data = {"id": i, "type": "story", "title": f"Story {i}", "url": f"https://example.com/{i}",
            "score": 100 + i, "descendants": i}
    data.update(changes)
    return data


def firebase_routes(count=30):
    ids = list(range(1, count + 1))
    routes = {f"{FB}/topstories.json": ids}
    routes.update({f"{FB}/item/{i}.json": item(i) for i in ids})
    return routes


def algolia_routes():
    hits = [{"objectID": str(200 + i), "title": f"Algolia {i}", "url": f"https://a.example/{i}",
             "points": 50 + i, "num_comments": i, "_tags": ["story", "front_page"]}
            for i in range(1, 16)]
    hits[0] = {"objectID": "999", "title": "We are hiring", "_tags": ["job", "front_page"]}
    hits[1]["url"] = None
    return {sources.ALGOLIA: {"hits": hits}}


class FakeWeb:
    """Stands in for get_json. Unknown URLs raise; exception values are raised."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def __call__(self, url, timeout):
        self.calls.append(url)
        if url not in self.routes:
            raise ConnectionError(f"no route to {url}")
        value = self.routes[url]
        if isinstance(value, BaseException):
            raise value
        return value


def fetch(routes):
    return sources.fetch_snapshot(now_fn, FakeWeb(routes), sleep=no_sleep)


class Firebase(unittest.TestCase):
    def test_happy_path(self):
        routes = firebase_routes()
        routes[f"{FB}/item/1.json"] = item(1, type="job")
        routes[f"{FB}/item/2.json"] = item(2, dead=True)
        routes[f"{FB}/item/3.json"] = item(3, title="Ask HN:  What are\n you working on?",
                                           url=None)
        routes[f"{FB}/item/4.json"] = {k: v for k, v in item(4).items() if k != "descendants"}
        routes[f"{FB}/item/5.json"] = item(5, deleted=True)
        routes[f"{FB}/item/6.json"] = item(6, title="   ")
        snap = fetch(routes)
        self.assertEqual(snap.source, "hn")
        self.assertEqual(snap.note, "")
        self.assertEqual([s.rank for s in snap.stories], list(range(1, 11)))
        self.assertEqual([s.hn_id for s in snap.stories], [3, 4] + list(range(7, 15)))
        ask = snap.stories[0]
        self.assertEqual(ask.title, "Ask HN: What are you working on?")
        self.assertEqual(ask.url, "https://news.ycombinator.com/item?id=3")
        self.assertEqual((ask.points, ask.comments), (103, 3))
        self.assertEqual(snap.stories[1].comments, 0)

    def test_some_item_fetches_fail(self):
        routes = firebase_routes()
        routes[f"{FB}/item/2.json"] = TimeoutError("slow")
        routes[f"{FB}/item/5.json"] = ValueError("bad json")
        del routes[f"{FB}/item/7.json"]
        snap = fetch(routes)
        self.assertEqual(snap.source, "hn")
        self.assertEqual([s.hn_id for s in snap.stories], [1, 3, 4, 6, 8, 9, 10, 11, 12, 13])

    def test_too_few_stories_falls_back_to_algolia(self):
        routes = {**firebase_routes(count=4), **algolia_routes()}
        snap = fetch(routes)
        self.assertEqual(snap.source, "hn-algolia")
        self.assertEqual(len(snap.stories), 10)
        self.assertEqual([s.rank for s in snap.stories], list(range(1, 11)))
        first = snap.stories[0]  # the job hit was skipped; this one has no url
        self.assertEqual((first.hn_id, first.title), (202, "Algolia 2"))
        self.assertEqual(first.url, "https://news.ycombinator.com/item?id=202")
        self.assertEqual((first.points, first.comments), (52, 2))
        self.assertEqual(snap.stories[1].url, "https://a.example/3")


class Failures(unittest.TestCase):
    def assert_none(self, snap):
        self.assertIsInstance(snap, Snapshot)
        self.assertEqual(snap.source, "none")
        self.assertEqual(snap.stories, ())
        self.assertTrue(snap.note)
        self.assertLessEqual(len(snap.note), 120)
        self.assertEqual(snap.note, " ".join(snap.note.split()))

    def test_both_sources_fail(self):
        web = FakeWeb({})
        snap = sources.fetch_snapshot(now_fn, web, sleep=no_sleep)
        self.assert_none(snap)
        self.assertIn("hn", snap.note)
        self.assertEqual(len(web.calls), 4)  # two attempts per source

    def test_odd_exceptions_and_junk_never_raise(self):
        class Weird(Exception):
            def __str__(self):
                raise RuntimeError("cannot even describe myself")

        oddities = [
            socket.timeout("timed out"), ssl.SSLError(1, "handshake\nfailed"),
            UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
            http.client.IncompleteRead(b"partial"), json.JSONDecodeError("Expecting", "x", 0),
            KeyError("k"), MemoryError(), RecursionError(), Weird(), OSError("x" * 500),
        ]
        junk = [None, "not json", 42, {"hits": "nope"}, [None, "a", {}], {"title": "x"}]
        for odd in oddities:
            with self.subTest(odd=type(odd).__name__):
                def get(url, timeout, odd=odd):
                    raise odd
                self.assert_none(sources.fetch_snapshot(now_fn, get, sleep=no_sleep))
        for value in junk:
            with self.subTest(junk=value):
                self.assert_none(sources.fetch_snapshot(
                    now_fn, lambda url, timeout, value=value: value, sleep=no_sleep))

    def test_budget_caps_the_whole_fetch(self):
        class SlowWeb:
            def __init__(self):
                self.t = 0.0
                self.timeouts = []

            def clock(self):
                return self.t

            def sleep(self, seconds):
                self.t += seconds

            def __call__(self, url, timeout):
                self.timeouts.append(timeout)
                self.t += 30
                raise TimeoutError("timed out")

        web = SlowWeb()
        snap = sources.fetch_snapshot(now_fn, web, clock=web.clock, sleep=web.sleep)
        self.assert_none(snap)
        self.assertEqual(len(web.timeouts), 2)  # one Firebase try, one Algolia try
        self.assertTrue(all(t <= config.HTTP_TIMEOUT for t in web.timeouts))
        self.assertLessEqual(web.t, config.FETCH_BUDGET + 2 * config.HTTP_TIMEOUT + 30)


class TakenAt(unittest.TestCase):
    def check(self, snap):
        self.assertEqual(snap.taken_at.utcoffset(), timedelta(hours=5, minutes=30))
        self.assertEqual(snap.taken_at.microsecond, 0)
        self.assertEqual(snap.taken_at.strftime("%Y-%m-%d %H:%M:%S"), "2026-10-12 10:47:30")

    def test_aware_ist(self):
        self.check(fetch(firebase_routes()))
        self.check(fetch({}))


if __name__ == "__main__":
    unittest.main()
