# tech-pulse: notes for Claude Code

Unattended Hacker News front-page archiver on GitHub Actions. The owner expects never to touch it.

## Invariants
- Never change `SALT` or `COUNT_WEIGHTS` in pulse/planner.py.
- Every commit carries a real snapshot and the real current time. No backdating, no empty or dummy commits, no keep-alive tricks.
- Author = owner's noreply email (pulse/config.py); committer = github-actions[bot]; default branch only.
- Python standard library + plain git only. No pip dependencies, no third-party actions.
- Cron lines must keep tests/test_schedule.py green.
- Never commit secrets (HC_DAILY_URL, HC_RUNS_URL, HC_SOURCE_URL live in GitHub secrets).
- The bot pushes to main daily: always `git pull --rebase` before editing.

## Commands
- `python3 -m unittest discover -s tests -v`
- `python3 -m pulse --dry-run`
- `python3 scripts/setup_alerts.py --status` (needs a Healthchecks read-write API key)
- `gh workflow run tech-pulse.yml -f force=true` (one snapshot now)
