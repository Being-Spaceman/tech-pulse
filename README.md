# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Thu 15 Oct 2026 · 15:21 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [Things to know when you get cancer](https://jjmaxwell4.com/writing/things-to-know-when-you-get-cancer/) | 1,361 | 336 |
| 2 | [Wanted to download an ISO, ended up writing a kernel exploit](https://blog.dfb.sh/blog/eap770-root-for-two-zeros/) | 83 | 31 |
| 3 | [Creating a Garmin "MCP"](https://jackantico.io/garmin-mcp) | 38 | 37 |
| 4 | [OpenCode 2.0](https://anoma.ly/notes/opencode-2-0/) | 614 | 241 |
| 5 | [Tiny Little Office](https://tinylittleoffice.com/) | 436 | 70 |
| 6 | [Show HN: Indigene – Native plants for where you stand](https://indigene.app/) | 25 | 5 |
| 7 | [LFM2.5-24B-A2B: Built for fast on-device agents](https://www.liquid.ai/blog/lfm2-5-24b-a2b) | 212 | 44 |
| 8 | [Do dentists know what they're doing?](https://mapwriting.substack.com/p/dentists) | 698 | 507 |
| 9 | [The cost of getting a job today](https://weli.dev/blog/the-cost-of-getting-a-job-today/) | 5 | 0 |
| 10 | [Catch a Bird – I made it for my own sanity](https://catchabird.com) | 176 | 44 |

10 of these stories are new since the previous snapshot (Wed 14 Oct 2026 · 15:39 IST).

**Archive:** 5 snapshots on 5 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
