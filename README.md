# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Thu 22 Oct 2026 · 15:37 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [CVE-2026-111943: Compromised Intermediate Certificate Authority](https://nvd.nist.gov/vuln/detail/cve-2026-111943) | 79 | 20 |
| 2 | [WorldTUI: I trained a 360M model to pretend to be a terminal](https://simedw.com/2026/10/21/world-model-terminal/) | 209 | 66 |
| 3 | [The recently proposed o(n log n) integer multiplication algorithm \[pdf\]](https://web.maths.unsw.edu.au/~davidharvey/research/subnlogn.pdf) | 207 | 138 |
| 4 | [Faster than earcut: triangulating 3.7M map polygons in 489 ms](https://globus.software/blog/2026/10/16/cutting-map-polygons/) | 6 | 0 |
| 5 | [Achieving AI-style reasoning without an LLM](https://fleetingswallow.com/minotaur-ai-deep-dive-achieving-reasoning-without-a-language-model/) | 15 | 1 |
| 6 | [Security Disclosure](https://blog.railway.com/p/security-disclosure-wednesday-october-21st) | 466 | 271 |
| 7 | [Claude Duet](https://claude.com/product/claude-duet) | 382 | 348 |
| 8 | [No more icons in every menu by default](https://blog.jim-nielsen.com/2026/icons-in-every-menu/) | 316 | 194 |
| 9 | [Using LLM for confidence scoring is a bad idea](https://rumple.github.io/blog/2026/10/20/asking-llm-for-confidence.html) | 97 | 49 |
| 10 | [Compromised LiteLLM 1.107.0 on PyPI Installs a Credential Stealer and Backdoor](https://safedep.io/litellm-pypi-compromise-credential-stealer-backdoor/) | 517 | 170 |

10 of these stories are new since the previous snapshot (Wed 21 Oct 2026 · 19:31 IST).

**Archive:** 23 snapshots on 11 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
<!-- PULSE:END -->

## How it works

- **Schedule:** the workflow wakes 12 times a day, Monday to Saturday, between 10:47 and 21:59 IST. Each date has a plan derived from the date itself: how many snapshots (usually 1; each extra one half as likely; at most 9) and roughly when. Each wake-up takes at most one snapshot that is due, and the last one takes anything still owed.
- **Snapshot:** the top 10 stories from the official Hacker News API, with the HN Algolia API as a fallback. If both fail, a "no data" row records the gap.
- **Data:** one CSV per month in `data/YYYY/YYYY-MM.csv`. The section above is regenerated on every snapshot.
- **No dependencies:** Python standard library and plain `git`. No third-party actions.
- **Monitoring:** Healthchecks.io alerts by email when a working day has no snapshot by 21:00 IST, a run fails, or the news source is down for 3 days.

## Data format

| Column | Meaning |
|---|---|
| `snapshot_at` | Snapshot time, ISO 8601 in IST (`+05:30`) |
| `source` | `hn` (official API), `hn-algolia` (fallback) or `none` (no data) |
| `rank` | Front-page position 1–10 (`0` on a no-data row) |
| `hn_id` | Hacker News item id |
| `title` | Story title |
| `url` | Link (the HN discussion page for Ask/Show HN) |
| `points` | Points at snapshot time |
| `comments` | Comments at snapshot time |

## Run it locally

```bash
python3 -m pulse --dry-run                 # today's plan and a live snapshot; writes nothing
python3 -m unittest discover -s tests -v
```

## Operations

| Alert | Meaning | What to do |
|---|---|---|
| **tech-pulse daily** is DOWN | No snapshot today by 21:00 IST | Before midnight IST: Actions → tech-pulse → Run workflow → tick *force*. If Actions is broken, push any commit of your own. |
| **tech-pulse runs** is DOWN | A run failed | Open the failed run in the Actions tab. |
| **tech-pulse source** is DOWN | Hacker News unreachable for 3 days | Nothing urgent; snapshots continue as no-data rows. |

To pause: Actions → tech-pulse → ⋯ → Disable workflow, and pause the checks on Healthchecks.io.

## License

Code: MIT (see LICENSE). Headlines and links belong to their authors and Hacker News.
