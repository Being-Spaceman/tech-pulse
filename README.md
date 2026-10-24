# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Sat 24 Oct 2026 · 15:00 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [OBS Studio 33](https://github.com/obsproject/obs-studio/releases/tag/33.0.0) | 136 | 37 |
| 2 | [Kimi K3.1 Pro and K3.1 Pro Highspeed](https://www.kimi.ai/blog/kimi-k3-1-pro) | 907 | 530 |
| 3 | [Physicists trap a single antimatter particle for a month](https://www.scientificamerican.com/article/physicists-trap-a-single-antimatter-particle-for-a-month/) | 31 | 8 |
| 4 | [Today, we hacked what we'd set out to hack: the iPhone](https://blog.calif.io/p/iphone) | 878 | 569 |
| 5 | [Twelve years of distributed SQLite](https://philipotoole.com/twelve-years-of-distributed-sqlite/) | 192 | 23 |
| 6 | [How close can pure functional programming get to C?](https://rtfeldman.com/fp-vs-c) | 114 | 11 |
| 7 | [Apple Music 404 Not Found](https://music.apple.com/this-url-doesnt-exist) | 757 | 230 |
| 8 | [Local Wikipedia: Wikipedia, but only for things a half hour walk from you](https://edjefferson.com/localwiki/) | 1,379 | 234 |
| 9 | [A practical guide to AI image generation, from diffusion to agents](https://danielball.com/notes/ai_image_generation.html) | 89 | 24 |
| 10 | [Bringing uv and ty together](https://astral.sh/blog/uv-ty-integration) | 149 | 36 |

9 of these stories are new since the previous snapshot (Fri 23 Oct 2026 · 19:12 IST).

**Archive:** 29 snapshots on 13 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
