import unittest
from datetime import datetime

from pulse import config, gitops
from pulse.gitops import run_git
from tests.sandbox import GitSandbox

WHEN = datetime(2026, 10, 12, 10, 47, tzinfo=config.IST)
OWNER = f"{config.AUTHOR_NAME}|{config.AUTHOR_EMAIL}"
BOT = f"{config.BOT_NAME}|{config.BOT_EMAIL}"


class GitOps(unittest.TestCase):
    def setUp(self):
        self.box = GitSandbox({"README.md": "# seed\n"})
        self.work = self.box.work

    def tearDown(self):
        self.box.close()

    def commit_file(self, repo, name="data.csv", text="a,b\n", message="pulse test"):
        path = repo / name
        path.write_text(text, encoding="utf-8")
        gitops.commit(repo, [path], message, WHEN)

    def test_commit_identity_and_ist_date(self):
        self.commit_file(self.work)
        log = run_git(self.work, "log", "-1", "--format=%an|%ae|%cn|%ce|%aI|%cI|%s").strip()
        self.assertEqual(log, f"{OWNER}|{BOT}|2026-10-12T10:47:00+05:30|"
                              f"2026-10-12T10:47:00+05:30|pulse test")

    def test_push(self):
        self.commit_file(self.work)
        gitops.push(self.work, wait=0)
        self.assertEqual(self.box.remote_count(), 2)
        self.assertEqual(self.box.remote_log("%H"), run_git(self.work, "rev-parse", "HEAD").strip())

    def _rebase_retry(self, work):
        other = self.box.clone("other")
        (other / "owner-edit.md").write_text("edited elsewhere\n", encoding="utf-8")
        self.box.commit_all(other, "edit from another clone")
        run_git(other, "push", "-q", "origin", "HEAD:refs/heads/main")

        self.commit_file(work)
        gitops.push(work, wait=0)
        self.assertEqual(self.box.remote_count(), 3)
        self.assertEqual(self.box.remote_log("%an|%ae|%cn|%ce|%aI|%s"),
                         f"{OWNER}|{BOT}|2026-10-12T10:47:00+05:30|pulse test")
        self.assertEqual(self.box.remote_log("%s", "main~1"), "edit from another clone")

    def test_rejected_push_rebases_and_retries(self):
        self._rebase_retry(self.work)

    def test_rebase_retry_from_shallow_clone(self):
        self._rebase_retry(self.box.clone("shallow", shallow=True))

    def test_broken_remote_raises(self):
        self.commit_file(self.work)
        run_git(self.work, "remote", "set-url", "origin", str(self.box.base / "missing.git"))
        with self.assertRaises(RuntimeError):
            gitops.push(self.work, attempts=2, wait=0)


if __name__ == "__main__":
    unittest.main()
