"""One run of tech-pulse: work out today's plan, take what is due, commit, push, ping."""
from __future__ import annotations

import argparse
import os
import traceback
from datetime import datetime
from pathlib import Path

from . import alerts, config, gitops, planner, readme, sources, store

ROOT = Path(__file__).resolve().parent.parent


def _now() -> datetime:
    return datetime.now(config.IST).replace(microsecond=0)


def main(argv=None, *, root=None, now_fn=None, fetch=None, ping=None) -> int:
    try:
        return _run(argv, root, now_fn, fetch, ping)
    except Exception:
        traceback.print_exc()
        return 1


def _run(argv, root, now_fn, fetch, ping) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m pulse")
    parser.add_argument("--dry-run", action="store_true",
                        help="show the plan and a live snapshot; write nothing")
    args = parser.parse_args(argv)

    if os.environ.get("PULSE_SIMULATE_FAILURE") == "true":
        print("alert drill: failing on purpose")
        return 1

    root = Path(root) if root is not None else ROOT
    now_fn = now_fn or _now
    fetch = fetch or (lambda: sources.fetch_snapshot(now_fn))
    ping = ping or alerts.ping
    force = os.environ.get("PULSE_FORCE") == "true"

    now = now_fn()
    today = now.date()
    counts = store.counts_by_day(root, today.year, today.month)
    done = counts.get(today, 0)
    planned = planner.planned_count(today, counts)
    times = planner.planned_times(today, planned)
    n = planner.snapshots_to_take(now.time(), times, done, force=force)
    n = max(0, min(n, planner.MAX_PER_DAY - done))

    at = " at " + ", ".join(readme.fmt_hhmm(t) for t in times) if times else ""
    print(f"[pulse] {readme.fmt_day(today)} {readme.fmt_hhmm(now)} IST · plan {planned}{at}"
          f" · done {done} · taking {n}{' (forced)' if force else ''}")

    if args.dry_run:
        snap = fetch()
        recent = store.recent_snapshots(root, today) + [snap]
        total, days, first = store.archive_stats(root)
        stats = (total + 1, days + (0 if done else 1), first or snap.taken_at.date())
        print(f"[dry-run] source: {snap.source}" + (f" ({snap.note})" if snap.note else ""))
        print(f"[dry-run] commit message: {readme.commit_message(recent)}")
        print("[dry-run] README section:\n")
        print(readme.render(recent, stats))
        print("\n[dry-run] nothing written, committed, pushed or pinged.")
        return 0

    if n == 0:
        ping("HC_RUNS_URL")
        return 0

    readme_path = root / config.README
    for _ in range(n):
        snap = fetch()
        if snap.source != "none":
            ping("HC_SOURCE_URL")
        csv_path = store.append_snapshot(root, snap)
        recent = store.recent_snapshots(root, snap.taken_at.date())
        readme.update_readme(readme_path, readme.render(recent, store.archive_stats(root)))
        message = readme.commit_message(recent)
        gitops.commit(root, [csv_path, readme_path], message, now_fn())
        print(f"[pulse] committed: {message}")

    gitops.push(root)
    ping("HC_DAILY_URL")
    ping("HC_RUNS_URL")
    return 0
