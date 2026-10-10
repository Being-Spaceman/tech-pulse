"""Deterministic daily plan for tech-pulse.

Pure functions, Python standard library only. Randomness comes from SHA-256,
never from the `random` module, because `random`'s algorithms are not
guaranteed to give identical results across Python versions, and every run
on the same day (and any later re-computation of a past day) must agree.
"""
from __future__ import annotations

import hashlib
from datetime import date, time

# Never change SALT after launch: it would silently re-plan every future day.
SALT = "tech-pulse/v1"

# date.weekday(): Monday=0 ... Sunday=6. Sunday is the day off.
WORKDAYS = frozenset({0, 1, 2, 3, 4, 5})

# Snapshots per working day: each extra snapshot is half as likely.
# P(k) = 2**(9-k) / 511 for k = 1..9  ->  50.1%, 25.0%, 12.5%, 6.3%, 3.1%,
# 1.6%, 0.78%, 0.39%, 0.20%. Mean = 1013/511 = 1.98 snapshots per day.
COUNT_WEIGHTS = (256, 128, 64, 32, 16, 8, 4, 2, 1)  # sums to 511
MAX_PER_DAY = len(COUNT_WEIGHTS)  # 9

# Planned times, in minutes after midnight IST.
FIRST_START = 10 * 60       # the day's first snapshot: 10:00 ...
FIRST_END = 16 * 60         # ... to 16:00 (exclusive)
LAST_END = 19 * 60 + 30     # every other snapshot: [first, 19:30)
FINAL_CALL = time(21, 45)   # a run at/after this takes every remaining snapshot


def _u64(*parts: object) -> int:
    """Stable 64-bit integer derived from SALT and the given parts."""
    key = "|".join([SALT, *(str(p) for p in parts)]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big")


def _unit(*parts: object) -> float:
    """Stable float in [0, 1)."""
    return _u64(*parts) / 2.0**64


def raw_count(day: date) -> int:
    """Count drawn for `day` before the monthly cap (0 on Sundays)."""
    if day.weekday() not in WORKDAYS:
        return 0
    r = _u64(day.isoformat(), "count") % sum(COUNT_WEIGHTS)
    acc = 0
    for k, w in enumerate(COUNT_WEIGHTS, start=1):
        acc += w
        if r < acc:
            return k
    return MAX_PER_DAY  # unreachable


def planned_count(day: date, actual_counts: dict | None = None) -> int:
    """Snapshots planned for `day`, capped at one 9-snapshot day per month.

    `actual_counts` maps dates of the same month to the number of snapshots
    really recorded in the data files. It is a second guard, so the cap holds
    even if SALT or the weights are ever changed mid-month.
    """
    k = raw_count(day)
    if k < MAX_PER_DAY:
        return k
    for d in range(1, day.day):
        earlier = day.replace(day=d)
        if raw_count(earlier) == MAX_PER_DAY:
            return MAX_PER_DAY - 1
        if actual_counts and actual_counts.get(earlier, 0) >= MAX_PER_DAY:
            return MAX_PER_DAY - 1
    return MAX_PER_DAY


def planned_times(day: date, count: int) -> list:
    """Sorted planned times (datetime.time, IST) for `count` snapshots."""
    if count <= 0:
        return []
    iso = day.isoformat()
    first = FIRST_START + int(_unit(iso, "time", 0) * (FIRST_END - FIRST_START))
    minutes = [first]
    for i in range(1, count):
        minutes.append(first + int(_unit(iso, "time", i) * (LAST_END - first)))
    minutes.sort()
    return [time(m // 60, m % 60) for m in minutes]


def snapshots_to_take(now: time, times: list, done: int, force: bool = False) -> int:
    """How many snapshots this run should take.

    Normally 0 or 1: one snapshot per run while the plan is ahead of what is
    already recorded. The final call of the day takes everything still owed.
    `force` (manual runs only) takes one snapshot now, but never lets a
    forced run create a 9-snapshot day.
    """
    if force:
        return 1 if done < MAX_PER_DAY - 1 else 0
    remaining = len(times) - done
    if remaining <= 0:
        return 0
    if now >= FINAL_CALL:
        return remaining
    due = sum(1 for t in times if t <= now)
    return 1 if due > done else 0
