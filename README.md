# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Thu 22 Oct 2026 · 19:29 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [CVE-2026-111943: Compromised Intermediate Certificate Authority](https://nvd.nist.gov/vuln/detail/cve-2026-111943) | 296 | 93 |
| 2 | [What Is Gridifcation](https://musicalform.substack.com/p/what-is-gridifcation) | 114 | 28 |
| 3 | [Jailbreaking the Switch 2](https://pepsipu.com/blog/2026-10-switch2-jailbreak-ns2jb/) | 299 | 104 |
| 4 | [Faster than earcut: triangulating 3.7M map polygons in 489 ms](https://globus.software/blog/2026/10/16/cutting-map-polygons/) | 111 | 20 |
| 5 | [Woman faces six years in prison over Cash App account she never opened](https://www.techspot.com/news/114296-woman-spends-three-nights-jail-faces-six-years.html) | 92 | 28 |
| 6 | [eMudhra to Exit Global SSL/TLS Certificate Business;](https://news.ycombinator.com/item?id=50194909) | 51 | 13 |
| 7 | [WorldTUI: I trained a 360M model to pretend to be a terminal](https://simedw.com/2026/10/21/world-model-terminal/) | 348 | 110 |
| 8 | [Startup taps underwater volcano as energy source in "proof point" test](https://arstechnica.com/science/2026/10/startup-taps-underwater-volcano-as-energy-source-in-proof-point-test/) | 53 | 20 |
| 9 | [The painter behind Manhattan’s Gilded Age interiors](https://engelsbergideas.com/notebook/the-unknown-painter-behind-manhattans-gilded-age-interiors/) | 13 | 0 |
| 10 | [Several Linux kernel vulnerabilities accidentally posted to public mailing list](https://www.phoronix.com/news/LKML-New-Trend-Vulnerabilities) | 127 | 29 |

7 of these stories are new since the previous snapshot (Thu 22 Oct 2026 · 15:37 IST).

**Archive:** 24 snapshots on 11 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
