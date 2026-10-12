# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Mon 12 Oct 2026 · 18:36 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [QGIS bans AI assisted contributions](https://github.com/qgis/QGIS-Enhancement-Proposals/pull/387) | 149 | 108 |
| 2 | [Deloitte falsified documents to evade tax on Abramovich's wealth](https://www.bbc.com/news/articles/c64g1l5389kvo) | 338 | 98 |
| 3 | [The Making Of Super Mario 64 – full Giles Goddard interview (2001)](https://pixelatron.com/blog/the-making-of-super-mario-64-full-giles-goddard-interview-ngc/) | 39 | 8 |
| 4 | [Secret of Orange Cats Revealed After 60-Year Search](https://www.sciencealert.com/secret-of-orange-cats-finally-revealed-after-60-year-search) | 57 | 24 |
| 5 | [Fingerprints are the new cookies](https://royfish.dev/fingerprints-are-the-new-cookies) | 480 | 237 |
| 6 | [Type-safe HTML templating in Zig](https://lalinsky.com/2026/10/11/type-safe-html-templating-in-zig.html) | 151 | 62 |
| 7 | [Hackers activate automatic defrosting accross European supermarket fridges](https://www.tomshardware.com/tech-industry/cyber-security/unprecedented-cyberattack-cripples-supermarket-fridges-across-europe-as-hackers-activate-automatic-defrosting-delivery-and-store-prices-also-impacted-by-incident) | 56 | 27 |
| 8 | [Show HN: PS2 games statically recompiled to WebAssembly](https://github.com/snuri00/ps2-web-recomp) | 99 | 46 |
| 9 | [Total Annihilation, rebuilt for modern computers](https://nanolathe.gg) | 567 | 215 |
| 10 | [Citroen revives the 2CV for an electric age](https://www.bbc.co.uk/news/articles/c620r33plgppo) | 26 | 19 |

10 of these stories are new since the previous snapshot (Sun 11 Oct 2026 · 00:49 IST).

**Archive:** 2 snapshots on 2 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
