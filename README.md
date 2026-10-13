# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Tue 13 Oct 2026 · 18:10 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [11 year old unsoundness bugs found in Rust borrow checker](https://github.com/rust-lang/rust/issues/164250) | 224 | 94 |
| 2 | [An hour of audio transcribed in about 13s on MacBook Air](https://eg2.haku.sh/) | 85 | 25 |
| 3 | [Show HN: Use your OpenAI subscription to create audiobooks](https://pdftomp3.com/connect-ai/) | 53 | 31 |
| 4 | [Hittite royal archive found in Turkey](https://www.thehistoryblog.com/archives/77107) | 135 | 18 |
| 5 | [CFTC Staff Were Told to Retract Analysis of Suspicious Oil Trades](https://www.bloomberg.com/news/features/2026-10-13/cftc-staff-told-to-retract-analysis-of-suspicious-oil-trades-on-iran) | 138 | 37 |
| 6 | [The baffling intelligence of a single cell (2024)](https://jsomers.net/e-coli-chemotaxis/) | 325 | 90 |
| 7 | [GLM-Legal](https://z.ai/blog/glm-legal) | 601 | 335 |
| 8 | [Intel D270 GPU AI Accelerator–Up to 480 GB LPDDR5X](https://www.intel.com/content/www/us/en/products/details/discrete-gpus/data-center-gpu/d-series.html) | 259 | 127 |
| 9 | [Hackers activate automatic defrosting in supermarket fridges across Europe](https://www.tomshardware.com/tech-industry/cyber-security/unprecedented-cyberattack-cripples-supermarket-fridges-across-europe-as-hackers-activate-automatic-defrosting-delivery-and-store-prices-also-impacted-by-incident) | 761 | 888 |
| 10 | [A Modern Web App in C](https://prophitt.me/writing/a-modern-web-app-in-c) | 613 | 268 |

9 of these stories are new since the previous snapshot (Mon 12 Oct 2026 · 18:36 IST).

**Archive:** 3 snapshots on 3 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
