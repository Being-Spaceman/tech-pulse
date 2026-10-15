# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Thu 15 Oct 2026 · 23:15 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [Simons Foundation launches $15M effort to help mathematicians navigate AI era](https://www.simonsfoundation.org/news/simons-foundation-launches-15m-effort-to-help-mathematicians-navigate-ai-era/) | 156 | 122 |
| 2 | [Neural Networks Are Already Clean](https://already-clean.goodfire.com/) | 92 | 24 |
| 3 | [Wayland desktop for Linux with skeuomorphic design](https://github.com/fyzugx/DEsk) | 285 | 115 |
| 4 | [Krea 3 – Frontier Image Model 4× faster than Nano Banana Pro](https://www.krea.ai/krea-3) | 74 | 36 |
| 5 | [I Know Why the Mathematicians Weep](https://www.derekthompson.org/p/i-know-why-the-mathematicians-weep) | 215 | 325 |
| 6 | [Libreboot 26.10 "Ominous Olive" released with UEFI, Chromebook support](https://libreboot.org/news/libreboot2610.html) | 181 | 94 |
| 7 | [Celebrating 70 Years of Fortran](https://fortran-lang.org/news/2026/09-15-Fortran-birthday/) | 95 | 46 |
| 8 | [More on Anthropic's Scion ripping off Mononoke](https://sunshowers.io/posts/anthropic-mononoke-2/) | 36 | 3 |
| 9 | [Biscoff Cookies Were Supposed to Be Temporary. Then Passengers Fell in Love](https://www.seriouseats.com/biscoff-history-12168161) | 49 | 37 |
| 10 | [Zero-Click Spyware Delivered via Targeted Ads: AdFection](https://citizenlab.ca/research/how-discover-tech-turned-targeted-ads-into-a-pipeline-for-spyware/) | 186 | 30 |

10 of these stories are new since the previous snapshot (Thu 15 Oct 2026 · 15:21 IST).

**Archive:** 6 snapshots on 5 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
