# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Sat 17 Oct 2026 · 14:48 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [DeepSeek: DeepSeek v4.1 Flash 1017](https://openrouter.ai/deepseek/deepseek-v4.1-flash-1017) | 43 | 2 |
| 2 | [Ultramarine 1 Flash](https://www.paperinstruments.com/ultramarine) | 235 | 68 |
| 3 | [Show HN: Llmspeed – feel how fast a local LLM runs before you buy the hardware](https://llmspeed.dev/) | 65 | 23 |
| 4 | [Tesla Roadster](https://www.tesla.com/roadster) | 1,417 | 2,487 |
| 5 | [DeepSeek-v4.1-Flash-1017](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017) | 67 | 21 |
| 6 | [Intuitive concurrent programming in any language](https://www.lf-lang.org/) | 33 | 6 |
| 7 | [Llama.cpp on a jailbroken PS5: run any GGUF model natively on the console](https://github.com/cobanov/PS5LM) | 287 | 72 |
| 8 | [You could have invented transformers from memory](https://alexwang.ai/posts/associative-memory/) | 296 | 68 |
| 9 | [Claude reveals ECDSA curve origins](https://www.anthropic.com/research/ecdsa-curve-origins) | 863 | 321 |
| 10 | [FLUX 3 Image Klein](https://bfl.ai/blog/flux-3-image-klein) | 166 | 45 |

10 of these stories are new since the previous snapshot (Fri 16 Oct 2026 · 15:15 IST).

**Archive:** 8 snapshots on 7 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
