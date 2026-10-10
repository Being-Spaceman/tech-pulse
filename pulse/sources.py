"""Fetch the Hacker News front page.

The official API (Firebase) is tried first and HN Algolia is the fallback.
`fetch_snapshot` never raises: when both sources fail it returns a "none"
snapshot whose note says why, so the day still gets its commit.
"""
from __future__ import annotations

import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime

from . import config

FIREBASE = "https://hacker-news.firebaseio.com/v0"
ALGOLIA = "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30"
ITEM_PAGE = "https://news.ycombinator.com/item?id={}"

CANDIDATES = 30         # ids read from topstories.json
WORKERS = 10            # concurrent item requests
ATTEMPTS = 2            # per source
RETRY_PAUSE = 3         # seconds between attempts at the same source
FALLBACK_RESERVE = 18   # seconds of FETCH_BUDGET that Firebase must leave for Algolia
NOTE_MAX = 120


@dataclass(frozen=True)
class Story:
    rank: int
    hn_id: int | None
    title: str
    url: str
    points: int | None
    comments: int | None


@dataclass(frozen=True)
class Snapshot:
    taken_at: datetime   # aware, IST, microsecond=0
    source: str          # "hn", "hn-algolia" or "none"
    stories: tuple
    note: str = ""


def get_json(url: str, timeout: float = config.HTTP_TIMEOUT):
    """GET `url` and decode JSON. Raises on any error or non-200 response."""
    req = urllib.request.Request(
        url, headers={"User-Agent": config.USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


def _one_line(value) -> str:
    return " ".join(str(value).split()) if value is not None else ""


def _int(value) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _ranked(found: list) -> tuple:
    if len(found) < config.MIN_STORIES:
        raise ValueError(f"only {len(found)} usable stories")
    return tuple(Story(rank, *fields) for rank, fields in enumerate(found[:config.TOP_N], start=1))


def from_firebase(get, timeout: float = config.HTTP_TIMEOUT) -> tuple:
    ids = get(f"{FIREBASE}/topstories.json", timeout)
    if not isinstance(ids, list):
        raise ValueError("topstories.json is not a list")
    ids = [i for i in (_int(x) for x in ids[:CANDIDATES]) if i is not None]

    def item(hn_id):
        try:
            return get(f"{FIREBASE}/item/{hn_id}.json", timeout)
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        items = list(pool.map(item, ids))  # map keeps the original order

    found = []
    for hn_id, raw in zip(ids, items):
        if not isinstance(raw, dict) or raw.get("type") != "story":
            continue
        if raw.get("dead") or raw.get("deleted"):
            continue
        title = _one_line(raw.get("title"))
        if not title:
            continue
        hn_id = _int(raw.get("id")) or hn_id
        url = _one_line(raw.get("url")) or ITEM_PAGE.format(hn_id)
        comments = _int(raw.get("descendants"))
        found.append((hn_id, title, url, _int(raw.get("score")),
                      0 if comments is None else comments))
    return _ranked(found)


def from_algolia(get, timeout: float = config.HTTP_TIMEOUT) -> tuple:
    data = get(ALGOLIA, timeout)
    hits = data.get("hits") if isinstance(data, dict) else None
    if not isinstance(hits, list):
        raise ValueError("Algolia response has no hits list")
    found = []
    for hit in hits:
        if not isinstance(hit, dict):
            continue
        tags = hit.get("_tags")
        if isinstance(tags, list) and "job" in tags:  # match Firebase: stories only
            continue
        hn_id = _int(hit.get("objectID"))
        title = _one_line(hit.get("title"))
        if hn_id is None or not title:
            continue
        url = _one_line(hit.get("url")) or ITEM_PAGE.format(hn_id)
        found.append((hn_id, title, url, _int(hit.get("points")), _int(hit.get("num_comments"))))
    return _ranked(found)


def _describe(exc: BaseException) -> str:
    try:
        text = _one_line(exc)
    except Exception:
        text = ""
    return f"{type(exc).__name__}: {text}" if text else type(exc).__name__


def _bounded(get, end: float, clock):
    """Wrap `get` so no request outlives the deadline `end`."""
    def bounded_get(url, timeout=config.HTTP_TIMEOUT):
        left = end - clock()
        if left < 1:
            raise TimeoutError("fetch time budget used up")
        return get(url, min(timeout, left))
    return bounded_get


def _stamp(now_fn) -> datetime:
    try:
        when = now_fn()
    except Exception:
        when = datetime.now(config.IST)
    return when.astimezone(config.IST).replace(microsecond=0)


def fetch_snapshot(now_fn, get=get_json, *, budget: float = config.FETCH_BUDGET,
                   pause: float = RETRY_PAUSE, clock=time.monotonic, sleep=time.sleep) -> Snapshot:
    """One snapshot of the front page. Never raises."""
    errors = {}
    try:
        start = clock()
        stages = (
            ("hn", from_firebase, start + budget - FALLBACK_RESERVE),
            ("hn-algolia", from_algolia, start + budget),
        )
        for source, parse, end in stages:
            for attempt in range(1, ATTEMPTS + 1):
                if attempt > 1:
                    if end - clock() < pause + 1:
                        break
                    sleep(pause)
                if end - clock() < 1:
                    errors.setdefault(source, "no time left")
                    break
                try:
                    stories = parse(_bounded(get, end, clock))
                    return Snapshot(_stamp(now_fn), source, stories)
                except Exception as exc:
                    errors[source] = _describe(exc)
    except Exception as exc:
        errors["internal"] = _describe(exc)
    note = "; ".join(f"{k}: {v}" for k, v in errors.items()) or "unknown error"
    if len(note) > NOTE_MAX:
        note = note[:NOTE_MAX - 1].rstrip() + "…"
    return Snapshot(_stamp(now_fn), "none", (), note=note)
