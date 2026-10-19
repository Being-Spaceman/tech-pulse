# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Mon 19 Oct 2026 · 16:13 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [Linux 7.3 Released](https://lwn.net/Articles/1101143/) | 216 | 97 |
| 2 | [Hybrid Reasoning Agents: LLM agents that think in latent space, act through text](https://arxiv.org/abs/2610.18861) | 403 | 196 |
| 3 | [How to Train Your Robot](https://www.construction-physics.com/p/how-to-train-your-robot) | 44 | 14 |
| 4 | [Rabbits were a medieval royal luxury in England until the Black Death](https://phys.org/news/2026-10-rabbits-medieval-royal-luxury-england.html) | 91 | 84 |
| 5 | [William Gibson and the trademarking of cyberspace](https://colo.to/cyberspace.html) | 191 | 72 |
| 6 | [There's never been a better time to go into math (by: 3blue1brown) \[video\]](https://www.youtube.com/watch?v=LKrwhjOI8Nc) | 383 | 460 |
| 7 | [Tmux and Claude Code: Sessions, Send-Keys, and the Ceiling](https://crystl.dev/guides/tmux-for-ai-agents/) | 38 | 21 |
| 8 | [If you don't run your own LLM proxy, how do you know whats going on?](https://jrdsgl.com/if-you-dont-run-your-own-llm-proxy-how-the-fuck-do-you-even-know-whats-going-on/) | 175 | 121 |
| 9 | [Someone behind the software](https://karrisaarinen.com/posts/someone-behind-the-software/) | 452 | 167 |
| 10 | [Laptop Based on 6502 CPU](https://www.maddox.pro/?p=448) | 135 | 59 |

10 of these stories are new since the previous snapshot (Sat 17 Oct 2026 · 14:48 IST).

**Archive:** 9 snapshots on 8 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
