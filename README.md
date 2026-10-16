# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Fri 16 Oct 2026 · 15:15 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [Meta’s new commercial terms will allow the scraping of news sites: experts](https://www.niemanlab.org/2026/10/metas-new-commercial-terms-will-allow-the-scraping-of-news-sites-legal-experts-say/) | 290 | 104 |
| 2 | [Muse Spark Open](https://research.meta.ai/blog/muse-spark-open) | 813 | 402 |
| 3 | [Woman who rescued injured crow keeps getting 'thank-you gifts' from birds \[video\]](https://www.youtube.com/watch?v=sjNpfz4UzqU) | 289 | 93 |
| 4 | [The insider trading you're allowed to do](https://coached.com/essays/the-insider-trading-youre-allowed-to-do/) | 24 | 11 |
| 5 | [RPKI now protects 70% of internet routes](https://ipinfo.io/blog/rpki-protects-70-internet-routes) | 157 | 49 |
| 6 | [The Folders Programming Language](https://danieltemkin.com/esolangs/folders) | 54 | 8 |
| 7 | [New York City's iconic horse-drawn carriages expected to take their last trot](https://www.cnn.com/2026/10/13/us/nyc-horse-carriage-ban) | 37 | 25 |
| 8 | [Neural networks are clean](https://already-clean.goodfire.com/) | 682 | 254 |
| 9 | [Two-Stack Sliding-Window Aggregation](https://orlp.net/blog/two-stack-sliding-window-aggregation/) | 10 | 0 |
| 10 | [What I self-host](https://viceconsole.fyi/blog/2026/10/10/what-i-self-host/) | 483 | 297 |

9 of these stories are new since the previous snapshot (Thu 15 Oct 2026 · 23:15 IST).

**Archive:** 7 snapshots on 6 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
