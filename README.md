# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Fri 23 Oct 2026 · 17:37 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [Is this the new cyber normal?](https://drew.silcock.dev/blog/is-this-the-new-cyber-normal/) | 43 | 22 |
| 2 | [Local Wikipedia: Wikipedia, but only for things a half hour walk from you](https://edjefferson.com/localwiki/) | 541 | 122 |
| 3 | [Job Loss and Cortisone Mania](https://tilschuenemann.de/job-loss-cortisone-mania) | 21 | 1 |
| 4 | [Docker is weird](https://codeandcake.dev/posts/2026-10-22-docker-is-weird) | 564 | 243 |
| 5 | [The foolishness of "natural language programming" (1978)](https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD667.html) | 214 | 127 |
| 6 | [The alien space of science: Coherent but cognitively unavailable directions](https://arxiv.org/abs/2603.01092) | 96 | 25 |
| 7 | [Swedish government offices to ban ChatGPT and Claude](https://www.sverigesradio.se/artikel/chat-gpt-och-claude-forbjuder-regeringskansliet) | 14 | 6 |
| 8 | [How does Fable 5.1 hide messages in images?](https://www.lesswrong.com/posts/WHEQps5PK8LrrcTAb/how-does-fable-5-1-hide-messages-in-images) | 116 | 38 |
| 9 | [Dutch government had hacked into Jared Kushner's phone](https://twitter.com/jaredkushner/status/2113376217415958767) | 86 | 31 |
| 10 | [Every AI model has the same "controversial" take on humans](https://www.modelcompare.ai/blog/ai-models-controversial-take-on-humans) | 468 | 471 |

4 of these stories are new since the previous snapshot (Fri 23 Oct 2026 · 15:30 IST).

**Archive:** 26 snapshots on 12 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
