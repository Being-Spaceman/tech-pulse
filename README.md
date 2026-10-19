# tech-pulse

A self-updating archive of the Hacker News front page. A small Python job on GitHub Actions takes one to nine snapshots every Monday to Saturday and commits each one here: the top 10 stories with their points and comment counts.

Built as an always-on side project for scheduled automation, [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) and monitoring.

## Latest

<!-- PULSE:START -->
**Last snapshot:** Mon 19 Oct 2026 · 19:27 IST · Hacker News API

| # | Story | Points | Comments |
|--:|---|--:|--:|
| 1 | [Documents: Police officer gave her Flock login to her ICE agent husband](https://www.wjcl.com/article/savannah-police-officer-ice-agent-flock-access/74135816) | 386 | 190 |
| 2 | [Show HN: Qwen3-4B with the AI writing tics trained out](https://100toolkit.com/blog/deslop-model/) | 41 | 16 |
| 3 | [Linux 7.3 Released](https://lwn.net/Articles/1101143/) | 389 | 170 |
| 4 | [Timestral: Mistral release time-series foundation models](https://mistral.ai/news/timestral/) | 193 | 36 |
| 5 | [Let's Encrypt is adding two additional remote perspectives for domain validation](https://community.letsencrypt.org/t/lets-encrypt-is-adding-two-additional-remote-perspectives-for-domain-validation/252166) | 74 | 22 |
| 6 | [Alternatives to Animal Testing Are Finally Taking Off](https://spectrum.ieee.org/alternatives-to-animal-testing) | 71 | 10 |
| 7 | [Harness Engineering 101: The LLM is the brain, the harness is the body](https://github.com/IsuruMaduranga/harness-engineering-101) | 76 | 33 |
| 8 | [ESA's Hera Will View Asteroid Scars from DART's Strike](https://spectrum.ieee.org/esa-hera-dimorphos-rendezvous) | 31 | 0 |
| 9 | [Gdynia and the Dream of a Maritime Poland](https://engelsbergideas.com/notebook/gdynia-and-the-dream-of-a-maritime-poland/) | 48 | 13 |
| 10 | [Stripe will acquire OpenRouter for $7.5B](https://startupfortune.com/stripe-will-pay-75-billion-for-openrouter-the-ai-model-traffic-cop/) | 29 | 2 |

9 of these stories are new since the previous snapshot (Mon 19 Oct 2026 · 16:13 IST).

**Archive:** 10 snapshots on 8 days since 11 Oct 2026, in monthly CSV files under [data/](data/).
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
