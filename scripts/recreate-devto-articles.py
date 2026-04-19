#!/usr/bin/env python3
"""
Unpublish old dev.to articles and create fresh copies — in command-line order.

Forem (dev.to) orders series entries by
`COALESCE(crossposted_at, published_at) ASC`, and `published_at` is set only
at the *first* publish. Unpublish + republish does not reset it. The only
way to put an article later in a series is to create a fresh article (POST).

This script:
  1. For each markdown file on the command line, in order:
     a. Unpublishes the currently-mapped article (PUT published: false).
     b. Creates a brand new article from the file's body_markdown (POST).
     c. Updates docs/.blog-mapping.json to point filename → new devto_id.
  2. Saves the mapping after each article, so a mid-run failure is recoverable.

Side effects:
  - The original URLs for the listed articles are lost (the old articles stay
    in your dev.to account as unpublished drafts; delete via the UI if desired).
  - Comments / reactions / stats on the old articles do not migrate.
  - New articles get new slugs (dev.to derives slug from title + suffix).

Usage:
    DEVTO_API_KEY=... python scripts/recreate-devto-articles.py <file> [<file> ...]

Example (recreate ch6 through ch10 of the SDO series in book order):
    python scripts/recreate-devto-articles.py \\
        docs/blog-en-devto-structure-ch6.md \\
        docs/blog-en-devto-structure-ch7.md \\
        docs/blog-en-devto-structure-ch8.md \\
        docs/blog-en-devto-structure-ch9.md \\
        docs/blog-en-devto-structure-ch10.md
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAPPING_FILE = REPO_ROOT / "docs" / ".blog-mapping.json"


def devto_headers():
    api_key = os.environ.get("DEVTO_API_KEY", "")
    if not api_key:
        raise RuntimeError("DEVTO_API_KEY not set")
    return {
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "EIS-Blog-Recreator/1.0",
    }


def devto_request(method: str, url: str, payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
    max_attempts = 6

    for attempt in range(max_attempts):
        req = urllib.request.Request(url, data=data, headers=devto_headers(), method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            retriable = e.code == 429 or 500 <= e.code < 600
            if retriable and attempt < max_attempts - 1:
                retry_after = 0
                try:
                    retry_after = int(e.headers.get("Retry-After", 0) or 0)
                except (TypeError, ValueError):
                    retry_after = 0
                wait = retry_after if retry_after > 0 else 2 ** (attempt + 1)
                print(f"  {e.code} received; sleeping {wait}s (attempt {attempt + 2}/{max_attempts})", file=sys.stderr)
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {e.code}: {body}") from e
    raise RuntimeError("exhausted retries")


def unpublish(article_id: int):
    return devto_request("PUT", f"https://dev.to/api/articles/{article_id}", {"article": {"published": False}})


def create_from_markdown(content: str) -> dict:
    return devto_request("POST", "https://dev.to/api/articles", {"article": {"body_markdown": content}})


def save_mapping(mapping: dict):
    MAPPING_FILE.write_text(json.dumps(mapping, indent=2, ensure_ascii=False) + "\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    files = [Path(p) for p in sys.argv[1:]]
    for f in files:
        if not f.exists():
            raise RuntimeError(f"{f}: file does not exist")

    mapping = json.loads(MAPPING_FILE.read_text())
    for f in files:
        if f.name not in mapping or "devto_id" not in mapping[f.name]:
            raise RuntimeError(f"{f.name}: no devto_id in {MAPPING_FILE} — cannot unpublish")

    print(f"Recreating {len(files)} articles in this order:")
    for i, f in enumerate(files, 1):
        print(f"  {i:>2}. {f.name}  (old id {mapping[f.name]['devto_id']})")
    print()

    for f in files:
        fn = f.name
        old_id = mapping[fn]["devto_id"]

        print(f"[{fn}] unpublishing old article {old_id}...")
        unpublish(old_id)
        time.sleep(2)

        print(f"[{fn}] creating new article from markdown...")
        result = create_from_markdown(f.read_text())
        new_id = result["id"]
        new_url = result["url"]
        print(f"[{fn}] new id={new_id}")
        print(f"[{fn}] new url={new_url}")

        mapping[fn]["devto_id"] = new_id
        mapping[fn]["devto_url"] = new_url
        save_mapping(mapping)

        # Space articles apart so their published_at is strictly increasing.
        time.sleep(3)
        print()

    print("All articles recreated. Mapping saved.")


if __name__ == "__main__":
    main()
