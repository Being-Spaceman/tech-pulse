# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Tue 20 Oct 2026 · 19:15 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [DeepSeek just open-sourced its inference engine](https://github.com/deepseek-ai/DeepInfer) | 1,032 | 353 |
| 2 | [Apple broke an essential presentation feature of iPads](https://teddysvoronos.com/2026-10-19-apple-broke-an-essential-presentation-feature-of-ipads/) | 41 | 9 |
| 3 | [MicroG: Free-libre re-implementation of Google's proprietary Android user space](https://github.com/microg/GmsCore/wiki) | 202 | 19 |
| 4 | [Nordwand Mono – A monospace font for coders and adventurers](https://github.com/tywr/Nordwand-Mono) | 396 | 119 |
| 5 | [NixOS is making me less afraid](https://entropicthoughts.com/nixos-is-making-me-less-afraid) | 16 | 1 |
| 6 | [OpenBSD 8.0](https://www.openbsd.org/80.html) | 385 | 122 |
| 7 | [WhatsApp's help pages hid LLM instructions: dont recommend a regulator](https://redact.dev/blog/whatsapp-help-pages-hidden-ai-instructions) | 593 | 168 |
| 8 | [DeepSeek banned from U.S. federal civilian agencies under new DHS order](https://www.reuters.com/technology/us-banning-chinese-ai-deepseek-government-agency-it-systems-2026-10-19/) | 392 | 337 |
| 9 | [Making a 88x31 button book using ImageMagick](https://k.sosnierz.me/08-11-24/) | 90 | 13 |
| 10 | [Google cloud outage takes down banks](https://www.neowin.net/news/google-cloud-outage-takes-down-hsbc-revolut-bank-of-scotland-llyods-equifax-more/) | 139 | 59 |

2 of these stories are new since the previous snapshot (Tue 20 Oct 2026 · 18:36 IST).

**Archive:** 14 snapshots on 9 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
