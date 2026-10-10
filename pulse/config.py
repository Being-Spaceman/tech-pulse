"""tech-pulse settings. Fill the <...> placeholders once at setup."""
from datetime import timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30), "IST")  # India has no DST

AUTHOR_NAME = "Sourabh"
AUTHOR_EMAIL = "20354838+Being-Spaceman@users.noreply.github.com"  # ID+login@users.noreply.github.com
BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"

REPO = "Being-Spaceman/tech-pulse"
USER_AGENT = f"tech-pulse/1.0 (+https://github.com/{REPO})"
TOP_N = 10
MIN_STORIES = 5
HTTP_TIMEOUT = 10   # seconds per request
FETCH_BUDGET = 45   # seconds for a whole fetch, both sources, all attempts

DATA_DIR = "data"
README = "README.md"
MARK_START = "<!-- PULSE:START -->"
MARK_END = "<!-- PULSE:END -->"
