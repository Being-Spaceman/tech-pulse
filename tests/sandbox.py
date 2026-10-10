"""Throwaway git repos for tests, isolated from the user's global git config."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest import mock

from pulse.gitops import run_git

SEED_IDENTITY = {
    "GIT_AUTHOR_NAME": "Seed", "GIT_AUTHOR_EMAIL": "seed@example.com",
    "GIT_COMMITTER_NAME": "Seed", "GIT_COMMITTER_EMAIL": "seed@example.com",
}


class GitSandbox:
    """A bare `remote.git` holding one seed commit on main, and a clone in `work`."""

    def __init__(self, files: dict, shallow: bool = False):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.base = Path(self._tmp.name)
        empty_config = self.base / "empty.gitconfig"
        empty_config.write_text("", encoding="utf-8")
        self._env = mock.patch.dict(os.environ)
        self._env.start()
        for key in [k for k in os.environ if k.startswith(("GIT_", "PULSE_", "HC_"))]:
            del os.environ[key]
        os.environ["GIT_CONFIG_GLOBAL"] = str(empty_config)
        os.environ["GIT_CONFIG_NOSYSTEM"] = "1"

        seed = self.base / "seed"
        seed.mkdir()
        run_git(seed, "init", "-q", "-b", "main")
        for name, text in files.items():
            path = seed / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        self.commit_all(seed, "seed")
        self.remote = self.base / "remote.git"
        run_git(self.base, "clone", "-q", "--bare", str(seed), str(self.remote))
        self.work = self.clone("work", shallow=shallow)

    def clone(self, name: str, shallow: bool = False) -> Path:
        target = self.base / name
        if shallow:
            run_git(self.base, "clone", "-q", "--depth", "1", self.remote.as_uri(), str(target))
        else:
            run_git(self.base, "clone", "-q", str(self.remote), str(target))
        return target

    @staticmethod
    def commit_all(repo: Path, message: str) -> None:
        run_git(repo, "add", "-A")
        run_git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", message,
                env=SEED_IDENTITY)

    def remote_count(self) -> int:
        return int(run_git(self.remote, "rev-list", "--count", "main").strip())

    def remote_log(self, fmt: str, ref: str = "main") -> str:
        return run_git(self.remote, "log", "-1", f"--format={fmt}", ref).strip()

    def close(self) -> None:
        self._env.stop()
        self._tmp.cleanup()
