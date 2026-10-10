"""Create (or update) the tech-pulse checks on Healthchecks.io and store their
ping URLs as GitHub Actions secrets. Safe to re-run: checks are matched by slug.

Needs a read-write *project* API key (Healthchecks.io -> Project Settings ->
API Access) and, unless --no-secrets is given, the GitHub CLI (`gh`) logged in
and run from inside the repository folder.

    python3 scripts/setup_alerts.py             # asks for the API key (hidden)
    python3 scripts/setup_alerts.py --status    # show the checks' current state

The key can also come from the HC_API_KEY environment variable. It is never
written to disk, printed, or committed. Ping URLs are treated as secrets too:
anyone holding one could send fake "all good" pings.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = os.environ.get("HC_API_BASE", "https://healthchecks.io/api/v3")
TAG = "tech-pulse"

CHECKS = [
    {
        "secret": "HC_DAILY_URL",
        "body": {
            "name": "tech-pulse daily",
            "slug": "tech-pulse-daily",
            "desc": (
                "DOWN = no tech-pulse commit has landed today (Mon-Sat) by 21:00 IST. "
                "Act before midnight IST: run the workflow with force=true "
                "(GitHub > tech-pulse > Actions > tech-pulse > Run workflow), "
                "or push any commit of your own."
            ),
            # Expect at least one ping after 00:00 IST every Mon-Sat; alert 21 h later (21:00 IST).
            "schedule": "0 0 * * 1-6",
            "tz": "Asia/Kolkata",
            "grace": 21 * 3600,
        },
    },
    {
        "secret": "HC_RUNS_URL",
        "body": {
            "name": "tech-pulse runs",
            "slug": "tech-pulse-runs",
            "desc": (
                "DOWN = a workflow run failed, or no run has finished for 2 days. "
                "Today's snapshot may already be in. Open the repo's Actions tab to see why."
            ),
            "timeout": 2 * 86400,
            "grace": 3600,
        },
    },
    {
        "secret": "HC_SOURCE_URL",
        "body": {
            "name": "tech-pulse source",
            "slug": "tech-pulse-source",
            "desc": (
                "DOWN = Hacker News has been unreachable for 3 days. Daily commits "
                "continue as no-data snapshots, so nothing is urgent."
            ),
            "timeout": 3 * 86400,
            "grace": 3600,
        },
    },
]

NEEDED_CHANNELS = ("email", "telegram")


def api(method: str, path: str, key: str, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "X-Api-Key": key,
            "Content-Type": "application/json",
            "User-Agent": "tech-pulse-setup/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:300]
        hints = {
            401: "the API key is missing or wrong (it must be a read-write project key)",
            403: "access denied, or the account hit its check limit",
        }
        raise SystemExit(f"Healthchecks API {method} {path} -> HTTP {err.code}: "
                         f"{hints.get(err.code, detail)}")
    except urllib.error.URLError as err:
        raise SystemExit(f"Could not reach Healthchecks.io: {err.reason}")


def masked(url: str) -> str:
    return url[: url.rfind("/") + 1] + "…" + url[-4:]


def show_status(key: str) -> None:
    _, payload = api("GET", f"/checks/?tag={TAG}", key)
    checks = {c.get("slug"): c for c in payload.get("checks", [])}
    for spec in CHECKS:
        c = checks.get(spec["body"]["slug"])
        if not c:
            print(f"  {spec['body']['name']:<20} MISSING (run without --status to create it)")
            continue
        print(f"  {c['name']:<20} status={c['status']:<7} last_ping={c.get('last_ping')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--status", action="store_true", help="only show the checks' status")
    parser.add_argument("--no-secrets", action="store_true", help="do not set GitHub secrets")
    parser.add_argument("--allow-missing-channels", action="store_true",
                        help="continue even if email or Telegram is not connected yet")
    args = parser.parse_args()

    key = os.environ.get("HC_API_KEY", "").strip()
    if not key:
        key = getpass.getpass("Healthchecks.io read-write API key (input hidden): ").strip()
    if not key:
        print("No API key given.", file=sys.stderr)
        return 2

    if args.status:
        show_status(key)
        return 0

    _, payload = api("GET", "/channels/", key)
    kinds = sorted({c.get("kind", "?") for c in payload.get("channels", [])})
    print("Integrations found:", ", ".join(kinds) or "none")
    missing = [k for k in NEEDED_CHANNELS if k not in kinds]
    if missing and not args.allow_missing_channels:
        print("Missing integration(s): " + ", ".join(missing) + ". Add them on Healthchecks.io "
              "(Integrations page), then run this again.", file=sys.stderr)
        return 2

    for spec in CHECKS:
        body = dict(spec["body"], tags=TAG, channels="*", unique=["slug"])
        code, check = api("POST", "/checks/", key, body)
        ping_url = check.get("ping_url", "")
        if not ping_url.startswith("https://"):
            raise SystemExit(f"Unexpected response for {spec['body']['slug']}: no ping_url")
        verb = "created" if code == 201 else "updated"
        print(f"  {check.get('name')}: {verb}, status={check.get('status')}, ping {masked(ping_url)}")
        if not args.no_secrets:
            subprocess.run(["gh", "secret", "set", spec["secret"]],
                           input=ping_url, text=True, check=True)
            print(f"    GitHub secret {spec['secret']} set")
    print("Done. New checks stay 'new' (no alerts) until their first ping.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
