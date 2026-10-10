"""Monthly CSV archive: data/YYYY/YYYY-MM.csv, one row per story."""
from __future__ import annotations

import csv
import sys
from datetime import date, datetime
from pathlib import Path

from . import config
from .sources import Snapshot, Story

HEADER = ["snapshot_at", "source", "rank", "hn_id", "title", "url", "points", "comments"]
SOURCES = ("hn", "hn-algolia", "none")
NO_DATA = "(no data: "


def month_path(root, year: int, month: int) -> Path:
    return Path(root) / config.DATA_DIR / f"{year:04d}" / f"{year:04d}-{month:02d}.csv"


def _cell(value) -> str:
    return "" if value is None else str(value)


def _rows(snap: Snapshot) -> list:
    at = snap.taken_at.astimezone(config.IST).isoformat()
    if snap.source == "none":
        title = f"{NO_DATA}{snap.note})" if snap.note else "(no data)"
        return [[at, "none", 0, "", title, "", "", ""]]
    if not snap.stories:
        raise ValueError("a snapshot with data must have stories")
    return [[at, snap.source, s.rank, _cell(s.hn_id), s.title, s.url,
             _cell(s.points), _cell(s.comments)] for s in snap.stories]


def append_snapshot(root, snap: Snapshot) -> Path:
    at = snap.taken_at.astimezone(config.IST)
    path = month_path(root, at.year, at.month)
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        if new:
            writer.writerow(HEADER)
        writer.writerows(_rows(snap))
    return path


def _opt_int(text: str) -> int | None:
    return int(text) if text != "" else None


def _parse(row: list):
    """(taken_at, source, story or None, note) for one data row; ValueError if malformed."""
    if len(row) != len(HEADER):
        raise ValueError(f"expected {len(HEADER)} fields, got {len(row)}")
    at, source, rank, hn_id, title, url, points, comments = row
    taken_at = datetime.fromisoformat(at)
    if taken_at.tzinfo is None:
        raise ValueError("snapshot_at has no UTC offset")
    taken_at = taken_at.astimezone(config.IST)
    if source not in SOURCES:
        raise ValueError(f"unknown source {source!r}")
    if source == "none":
        if title.startswith(NO_DATA) and title.endswith(")"):
            return taken_at, source, None, title[len(NO_DATA):-1]
        return taken_at, source, None, ""
    rank = int(rank)
    if rank < 1:
        raise ValueError(f"bad rank {rank}")
    story = Story(rank, _opt_int(hn_id), title, url, _opt_int(points), _opt_int(comments))
    return taken_at, source, story, ""


def _read_file(path: Path) -> list:
    """Snapshots in file order. Rows are grouped by snapshot_at; a rank that
    does not increase also starts a new snapshot, so two snapshots taken in
    the same second still count as two."""
    snaps = []
    current = None  # [taken_at, source, stories, note, last_rank]
    with path.open(encoding="utf-8", newline="", errors="replace") as f:
        reader = csv.reader(f)
        while True:
            try:
                row = next(reader)
                if row == HEADER or not row:
                    continue
                taken_at, source, story, note = _parse(row)
            except StopIteration:
                break
            except (csv.Error, ValueError, TypeError) as exc:
                print(f"[store] warning: {path.name} line {reader.line_num}: "
                      f"skipped malformed row ({exc})", file=sys.stderr)
                continue
            rank = story.rank if story else 0
            if (current is None or current[0] != taken_at or current[1] != source
                    or rank <= current[4]):
                current = [taken_at, source, [], note, rank]
                snaps.append(current)
            if story:
                current[2].append(story)
            current[4] = rank
    return [Snapshot(at, source, tuple(stories), note) for at, source, stories, note, _ in snaps]


def read_month(root, year: int, month: int) -> list:
    path = month_path(root, year, month)
    return _read_file(path) if path.exists() else []


def counts_by_day(root, year: int, month: int) -> dict:
    counts = {}
    for snap in read_month(root, year, month):
        day = snap.taken_at.date()
        counts[day] = counts.get(day, 0) + 1
    return counts


def recent_snapshots(root, day: date) -> list:
    """Snapshots of the previous month and this month, oldest first."""
    prev = (day.year - 1, 12) if day.month == 1 else (day.year, day.month - 1)
    snaps = read_month(root, *prev) + read_month(root, day.year, day.month)
    return sorted(snaps, key=lambda s: s.taken_at)


def archive_stats(root) -> tuple:
    """(total snapshots, days with snapshots, first date or None) over all CSVs."""
    total = 0
    days = set()
    for path in sorted((Path(root) / config.DATA_DIR).glob("[0-9][0-9][0-9][0-9]/*.csv")):
        for snap in _read_file(path):
            total += 1
            days.add(snap.taken_at.date())
    return total, len(days), (min(days) if days else None)
