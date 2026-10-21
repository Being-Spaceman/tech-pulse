# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Wed 21 Oct 2026 · 19:31 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [Updated PHP version released to GitHub](https://github.com/php/php-src/releases/tag/php-8.2.35) | 103 | 23 |
| 2 | [PHP 8.5.12, 8.4.27, 8.3.36 and 8.2.35 out](https://www.php.net/index.php) | 58 | 7 |
| 3 | [Eight Bits of Trust; eMudhra's CA keys cracked in milliseconds](https://scotthelme.co.uk/eight-bits-of-trust-emudhras-ca-keys-cracked-in-milliseconds/) | 430 | 195 |
| 4 | [Qwen3-Coder writes less secure code when told it's for a US persona](https://www.hirundo.io/blog/qwen3-coder-vulnerabilities) | 117 | 55 |
| 5 | [Most advice is right for the person giving it](https://coached.com/essays/most-advice-is-right-for-the-person-giving-it/) | 31 | 12 |
| 6 | [LayerFS: The filesystem for AI coding agents](https://layerfs.ai/) | 26 | 11 |
| 7 | [Whatever Happened to Fire Escapes](https://practical.engineering/blog/2026/10/20/whatever-happened-to-fire-escapes) | 95 | 51 |
| 8 | [PHP2Shell: AI uncovers critical RCE in PHP](https://www.wiz.io/blog/php2shell-php-rce) | 8 | 0 |
| 9 | [The Future of CSS](https://www.joshwcomeau.com/css/interop-2027/) | 486 | 200 |
| 10 | [Upcoming critical PHP security release (CVE-2026-109618 / -109619)](https://news-web.php.net/php.announce/509) | 1,342 | 562 |

6 of these stories are new since the previous snapshot (Wed 21 Oct 2026 · 17:55 IST).

**Archive:** 22 snapshots on 10 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
