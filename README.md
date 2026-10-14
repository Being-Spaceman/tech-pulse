# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Wed 14 Oct 2026 · 15:39 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [Iosevka is an open-source, sans-serif and slab-serif, monospace font](https://typeof.net/Iosevka/) | 78 | 18 |
| 2 | [Gemini 4 Argon](https://deepmind.google/models/gemini/) | 1,311 | 911 |
| 3 | [Sound – Bartosz Ciechanowski (2022)](https://ciechanow.ski/sound/) | 124 | 19 |
| 4 | [Ledger confirms spy chip implant behind wallet crypto thefts](https://www.bleepingcomputer.com/news/security/ledger-confirms-hardware-wallet-spy-implant-behind-crypto-thefts/) | 695 | 444 |
| 5 | [What agents mean for Rust (and vice versa)](https://smallcultfollowing.com/babysteps/blog/2026/10/14/agentic-dev-and-rust/) | 11 | 4 |
| 6 | [AOSP Source Releases Are So Late Developers Disassemble Libraries to Report Bugs](https://github.com/android/ndk/issues/2260) | 257 | 119 |
| 7 | [Redesigning source control at Anthropic](https://www.anthropic.com/engineering/redesigning-source-control) | 776 | 789 |
| 8 | [Show HN: Guitoro, a virtual guitar you strum with your keyboard](https://guitoro.com/) | 435 | 111 |
| 9 | [900-Page Pre-Pantone Guide to Color from 1692 (With Complete High-Res Scan)](https://www.openculture.com/2026/10/a-900-page-pre-pantone-guide-to-color-from-1692.html) | 164 | 21 |
| 10 | [Starlink limit hits Ukraine's drones. The battlefield depends on SpaceX](https://defence24.com/geopolitics/starlink-limit-hits-ukraines-drones-the-battlefield-depends-on-spacex) | 36 | 21 |

10 of these stories are new since the previous snapshot (Tue 13 Oct 2026 · 18:10 IST).

**Archive:** 4 snapshots on 4 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
