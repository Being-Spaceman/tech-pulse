"""The README's "Latest" section and the commit message for each snapshot."""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from . import config

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
SOURCE_NAMES = {"hn": "Hacker News API", "hn-algolia": "HN Algolia API (fallback)"}
COMMIT_MAX = 72

_MD_ESCAPES = {c: "\\" + c for c in "\\`*_[]|"}
_MD_ESCAPES.update({"<": "&lt;", ">": "&gt;"})
_URL_ESCAPES = {" ": "%20", "(": "%28", ")": "%29", "<": "%3C", ">": "%3E",
                "|": "%7C", "\\": "%5C", "`": "%60"}


# Fixed English names: never locale-dependent.
def fmt_date(d: date) -> str:
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def fmt_day(d: date) -> str:
    return f"{DAYS[d.weekday()]} {fmt_date(d)}"


def fmt_hhmm(t) -> str:
    return f"{t.hour:02d}:{t.minute:02d}"


def fmt_stamp(when: datetime) -> str:
    when = when.astimezone(config.IST)
    return f"{fmt_day(when.date())} · {fmt_hhmm(when)} IST"


def escape(text: str) -> str:
    """Make text safe inside a markdown table cell."""
    return "".join(_MD_ESCAPES.get(c, c) for c in " ".join(str(text).split()))


def link_target(url: str) -> str | None:
    """`url` ready for a markdown link, or None when it should not be linked."""
    url = (url or "").strip()
    if not url.lower().startswith(("http://", "https://")):
        return None
    return "".join(_URL_ESCAPES.get(c, "%{:02X}".format(ord(c)) if ord(c) < 32 else c)
                   for c in url)


def _ok(snaps: list) -> list:
    return [s for s in snaps if s.source != "none" and s.stories]


def _story_key(story):
    return story.hn_id if story.hn_id is not None else story.title


def count_new(current, previous) -> int:
    seen = {_story_key(s) for s in previous.stories}
    return sum(1 for s in current.stories if _story_key(s) not in seen)


def _plural(n: int, word: str) -> str:
    return f"{n:,} {word}" + ("" if n == 1 else "s")


def _table(snap) -> list:
    lines = ["| # | Story | Points | Comments |", "|--:|---|--:|--:|"]
    for s in snap.stories:
        title = escape(s.title)
        target = link_target(s.url)
        story = f"[{title}]({target})" if target else title
        points = "–" if s.points is None else f"{s.points:,}"
        comments = "–" if s.comments is None else f"{s.comments:,}"
        lines.append(f"| {s.rank} | {story} | {points} | {comments} |")
    return lines


def render(recent: list, stats: tuple) -> str:
    """Markdown for the README section between the PULSE markers."""
    total, days, first = stats
    lines = []
    if recent:
        latest = recent[-1]
        ok = _ok(recent)
        last_ok = ok[-1] if ok else None
        prev_ok = ok[-2] if len(ok) > 1 else None
        if latest.source != "none":
            name = SOURCE_NAMES.get(latest.source, latest.source)
            lines.append(f"**Last snapshot:** {fmt_stamp(latest.taken_at)} · {name}")
        elif last_ok:
            lines.append(f"**Last check:** {fmt_stamp(latest.taken_at)} · Hacker News was "
                         f"unreachable. Showing the last good snapshot "
                         f"({fmt_stamp(last_ok.taken_at)}).")
        else:
            lines.append(f"**Last check:** {fmt_stamp(latest.taken_at)} · Hacker News was "
                         f"unreachable, and there is no recent snapshot with data.")
        if last_ok:
            lines += [""] + _table(last_ok)
            if prev_ok:
                n = count_new(last_ok, prev_ok)
                verb = "is" if n == 1 else "are"
                lines += ["", f"{n} of these stories {verb} new since the previous snapshot "
                              f"({fmt_stamp(prev_ok.taken_at)})."]
        lines.append("")
    if first:
        lines.append(f"**Archive:** {_plural(total, 'snapshot')} on {_plural(days, 'day')} "
                     f"since {fmt_date(first)}, in monthly CSV files under [data/](data/).")
    else:
        lines.append("**Archive:** no snapshots yet.")
    return "\n".join(lines)


def update_readme(path, section: str) -> bool:
    """Put `section` between the markers (adding them if missing). True if the file changed."""
    path = Path(path)
    old = ""
    if path.exists():
        with open(path, encoding="utf-8") as f:  # universal newlines: CRLF becomes LF
            old = f.read()
    body = section.strip("\n")
    start = old.find(config.MARK_START)
    end = old.find(config.MARK_END, start) if start != -1 else -1
    if start != -1 and end != -1:
        new = f"{old[:start + len(config.MARK_START)]}\n{body}\n{old[end:]}"
    else:
        head = old if old.endswith("\n") or not old else old + "\n"
        new = f"{head}\n## Latest\n\n{config.MARK_START}\n{body}\n{config.MARK_END}\n"
    if new == old and path.exists():
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    return True


def commit_message(recent: list) -> str:
    latest = recent[-1]
    head = f"pulse {fmt_hhmm(latest.taken_at.astimezone(config.IST))} IST"
    if latest.source == "none" or not latest.stories:
        return f"{head} · no data, Hacker News unreachable"
    ok = _ok(recent)
    prev_ok = ok[-2] if len(ok) > 1 else None
    tail = f" · {count_new(latest, prev_ok)} new" if prev_ok else ""
    top = latest.stories[0]
    lead = f"{head} · #{top.rank} \""
    room = COMMIT_MAX - len(lead) - len("\"") - len(tail)
    title = " ".join(top.title.split())
    if len(title) > room:
        title = title[:room - 1].rstrip() + "…"
    return f"{lead}{title}\"{tail}"
