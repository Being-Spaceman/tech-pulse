"""Healthchecks.io pings. The ping URLs are secrets: log env names, never URLs."""
from __future__ import annotations

import os
import sys
import time
import urllib.error
import urllib.request

from . import config


def ping(env_name: str, suffix: str = "") -> bool:
    """GET the URL in `env_name` (+ suffix, e.g. "/fail"). True on 2xx. Never raises."""
    try:
        url = os.environ.get(env_name, "").strip()
        if not url:
            return False
        req = urllib.request.Request(url.rstrip("/") + suffix,
                                     headers={"User-Agent": config.USER_AGENT})
        reason = "unknown error"
        for attempt in (1, 2):
            if attempt > 1:
                time.sleep(2)
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if 200 <= resp.status < 300:
                        print(f"[alerts] pinged {env_name}{suffix}")
                        return True
                    reason = f"HTTP {resp.status}"
            except urllib.error.HTTPError as exc:
                reason = f"HTTP {exc.code}"
            except Exception as exc:
                reason = type(exc).__name__
        print(f"[alerts] could not ping {env_name}{suffix}: {reason}", file=sys.stderr)
    except Exception as exc:
        print(f"[alerts] could not ping {env_name}: {type(exc).__name__}", file=sys.stderr)
    return False
