import os
import sys

from .main import main

if __name__ == "__main__":
    # Never crash on a headline the console cannot encode.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except (AttributeError, ValueError):
            pass
    if os.environ.get("GITHUB_ACTIONS") != "true" and "--dry-run" not in sys.argv[1:]:
        print("Real runs only happen on GitHub Actions; use --dry-run locally", file=sys.stderr)
        sys.exit(2)
    sys.exit(main())
