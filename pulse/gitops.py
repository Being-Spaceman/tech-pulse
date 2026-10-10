"""Plain-git helpers: commit as owner + bot, push with rebase-and-retry."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from . import config

BOT_COMMITTER = {"GIT_COMMITTER_NAME": config.BOT_NAME, "GIT_COMMITTER_EMAIL": config.BOT_EMAIL}


def run_git(repo, *args, env=None) -> str:
    """Run git in `repo` and return stdout. `env` adds to the current environment."""
    full_env = {**os.environ, **env} if env else None
    try:
        done = subprocess.run(["git", *args], cwd=str(repo), env=full_env, check=True,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace")
    except subprocess.CalledProcessError as exc:
        tail = (exc.stderr or exc.stdout or "").strip()[-600:]
        raise RuntimeError(f"git {' '.join(args[:3])} failed "
                           f"(exit {exc.returncode}): {tail}") from None
    return done.stdout


def commit(repo, paths, message: str, when) -> None:
    """Commit `paths` authored by the owner, committed by the bot, dated `when` (IST)."""
    rel = [Path(os.path.relpath(p, repo)).as_posix() if os.path.isabs(p) else str(p)
           for p in paths]
    run_git(repo, "add", "--", *rel)
    stamp = f"{int(when.timestamp())} +0530"
    env = {
        "GIT_AUTHOR_NAME": config.AUTHOR_NAME,
        "GIT_AUTHOR_EMAIL": config.AUTHOR_EMAIL,
        **BOT_COMMITTER,
        "GIT_AUTHOR_DATE": stamp,
        "GIT_COMMITTER_DATE": stamp,
    }
    run_git(repo, "-c", "commit.gpgsign=false", "commit", "-m", message, env=env)


def push(repo, attempts: int = 3, wait: float = 5) -> None:
    """Push HEAD to its branch on origin; if rejected, rebase on origin and retry."""
    branch = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
    if branch == "HEAD":
        raise RuntimeError("detached HEAD: no branch to push")
    last = None
    for attempt in range(1, attempts + 1):
        try:
            run_git(repo, "push", "origin", f"HEAD:refs/heads/{branch}")
            print(f"[git] pushed to {branch}")
            return
        except RuntimeError as exc:
            last = exc
        if attempt == attempts:
            break
        print(f"[git] push attempt {attempt}/{attempts} failed; rebasing on origin/{branch}",
              file=sys.stderr)
        time.sleep(wait)
        try:
            run_git(repo, "pull", "--rebase", "origin", branch, env=BOT_COMMITTER)
        except RuntimeError as exc:
            last = exc
            try:
                run_git(repo, "rebase", "--abort")
            except RuntimeError:
                pass
    raise RuntimeError(f"push failed after {attempts} attempts: {last}")
