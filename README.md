# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Tue 20 Oct 2026 · 23:27 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [Voxtral 3](https://mistral.ai/news/voxtral-3/) | 193 | 52 |
| 2 | [DeepInfer: High-performance, large-scale inference framework for DeepSeek models](https://github.com/deepseek-ai/DeepInfer) | 1,871 | 708 |
| 3 | [EMudhra Intermediate CA Compromise](https://emudhra.we-have-a-problem.com/) | 263 | 119 |
| 4 | [Apple broke an essential presentation feature of iPads](https://teddysvoronos.com/2026-10-19-apple-broke-an-essential-presentation-feature-of-ipads/) | 319 | 175 |
| 5 | [What Shall I Teach My Son?](https://stevekrouse.com/ends) | 19 | 10 |
| 6 | [Google open-sources TorchTPU, a native PyTorch back end for TPUs](https://github.com/google-pytorch/torch_tpu) | 51 | 14 |
| 7 | [Publish fake stats, get cited in LLMs](https://peec.ai/blog/publish-stats-get-cited-the-tactic-that-put-my-data-all-over-the-web) | 217 | 112 |
| 8 | [How I got over 300 Tor exit nodes removed](https://kaba.cx/posts/20261020_Tor/) | 181 | 53 |
| 9 | [Triplet of 'ghostly' galaxies hints at what dark matter is and isn't](https://www.quantamagazine.org/triplet-of-ghostly-galaxies-hints-at-what-dark-matter-is-and-isnt-20261014/) | 59 | 10 |
| 10 | [JAXA is about to perform a Phobos sample return mission](https://www.science.org/content/article/audacious-space-heist-japan-aims-bring-home-bits-martian-moon) | 30 | 3 |

0 of these stories are new since the previous snapshot (Tue 20 Oct 2026 · 23:27 IST).

**Archive:** 19 snapshots on 9 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
