#!/usr/bin/env python3
"""
Build alias map: GitHub login -> display name for OSS Gravity Map.

For each repo in ground-truth, fetches the GitHub display name for each
contributor login via the GitHub API, then fuzzy-matches against EIS member
names to produce a mapping file.

Usage:
  python3 build-alias-map.py [--ground-truth-dir DIR] [--results-dir DIR] [--output FILE]
"""

import json
import os
import sys
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path


def load_ground_truth(gt_dir: str) -> dict[str, list[str]]:
    """Load ground truth and extract contributor logins per repo."""
    repo_logins = {}
    for f in Path(gt_dir).glob("*.json"):
        repo_name = f.stem
        try:
            with open(f) as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, IOError) as e:
            print(f"  WARN: could not load {f}: {e}", file=sys.stderr)
            continue

        logins = []
        for c in data.get("top_contributors", []):
            if c.get("type") == "User" and c.get("login"):
                logins.append(c["login"])
        repo_logins[repo_name] = logins[:100]  # cap at 100
    return repo_logins


def load_eis_members(results_dir: str) -> dict[str, list[str]]:
    """Load EIS results and extract member names per repo."""
    repo_members = {}
    for f in Path(results_dir).glob("*.json"):
        repo_name = f.stem
        try:
            with open(f) as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, IOError) as e:
            print(f"  WARN: could not load {f}: {e}", file=sys.stderr)
            continue

        members = []
        for domain in data.get("domains", []):
            for member in domain.get("members", []):
                name = member.get("member", "")
                if name and name not in members:
                    members.append(name)
        repo_members[repo_name] = members
    return repo_members


def load_cache(cache_path: str) -> dict[str, dict]:
    """Load cached GitHub user data."""
    if os.path.exists(cache_path):
        try:
            with open(cache_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_cache(cache_path: str, cache: dict):
    """Save GitHub user data cache."""
    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def fetch_github_user(login: str, token: str | None, cache: dict) -> dict | None:
    """Fetch GitHub user profile. Returns cached data if available."""
    if login in cache:
        return cache[login]

    url = f"https://api.github.com/users/{login}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            result = {
                "login": data.get("login", login),
                "name": data.get("name"),
            }
            cache[login] = result
            return result

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"    404: user '{login}' not found")
            cache[login] = {"login": login, "name": None}
            return cache[login]

        if e.code in (403, 429):
            reset = e.headers.get("X-RateLimit-Reset")
            if reset:
                wait_time = max(int(reset) - int(time.time()), 1)
                print(f"    Rate limited. Waiting {wait_time}s...")
                time.sleep(min(wait_time, 60))
            else:
                print(f"    Rate limited. Waiting 60s...")
                time.sleep(60)
            # Retry once
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    result = {"login": data.get("login", login), "name": data.get("name")}
                    cache[login] = result
                    return result
            except Exception:
                pass

        print(f"    HTTP {e.code} for '{login}'")
        cache[login] = {"login": login, "name": None}
        return cache[login]

    except Exception as e:
        print(f"    Error fetching '{login}': {e}")
        cache[login] = {"login": login, "name": None}
        return cache[login]


def normalize(s: str) -> str:
    """Normalize a string for comparison."""
    return s.lower().strip()


def fuzzy_match(github_name: str, eis_members: list[str]) -> str | None:
    """Match a GitHub display name to an EIS member name.

    Strategies:
      1. Exact match (case-insensitive)
      2. Name parts match: all parts of one name appear in the other
    """
    if not github_name:
        return None

    norm_gh = normalize(github_name)

    # 1. Exact match
    for member in eis_members:
        if normalize(member) == norm_gh:
            return member

    # 2. Name parts match
    gh_parts = set(norm_gh.split())
    if len(gh_parts) < 2:
        return None  # single-word names are too ambiguous

    for member in eis_members:
        member_parts = set(normalize(member).split())
        if len(member_parts) < 2:
            continue
        # All parts of one must be in the other
        if gh_parts <= member_parts or member_parts <= gh_parts:
            return member

    return None


def main():
    parser = argparse.ArgumentParser(description="Build GitHub login -> display name alias map")
    parser.add_argument("--ground-truth-dir", default="data/ground-truth",
                        help="Directory with ground truth JSON files")
    parser.add_argument("--results-dir", default="data/results",
                        help="Directory with EIS result JSON files")
    parser.add_argument("--output", default="data/alias-map.json",
                        help="Output alias map file")
    parser.add_argument("--cache", default="data/github-users-cache.json",
                        help="GitHub user cache file")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        print("Using GITHUB_TOKEN for authentication")
    else:
        print("No GITHUB_TOKEN set - using unauthenticated requests (60 req/hr limit)")

    # Load data
    print("\nLoading ground truth...")
    repo_logins = load_ground_truth(args.ground_truth_dir)
    print(f"  {len(repo_logins)} repos, {sum(len(v) for v in repo_logins.values())} total logins")

    print("Loading EIS results...")
    repo_members = load_eis_members(args.results_dir)
    print(f"  {len(repo_members)} repos, {sum(len(v) for v in repo_members.values())} total members")

    print("Loading cache...")
    cache = load_cache(args.cache)
    print(f"  {len(cache)} cached users")

    # Collect all unique logins across all repos
    all_logins = set()
    for logins in repo_logins.values():
        all_logins.update(logins)

    # Filter out already-cached logins
    to_fetch = [login for login in sorted(all_logins) if login not in cache]
    print(f"\nNeed to fetch {len(to_fetch)} users ({len(all_logins) - len(to_fetch)} cached)")

    # Fetch GitHub profiles
    if to_fetch:
        print(f"\nFetching {len(to_fetch)} GitHub user profiles...")
        for i, login in enumerate(to_fetch):
            print(f"  [{i+1}/{len(to_fetch)}] {login}", end="")
            result = fetch_github_user(login, token, cache)
            name = result.get("name") if result else None
            if name:
                print(f" -> {name}")
            else:
                print(f" -> (no name)")

            # Save cache periodically
            if (i + 1) % 20 == 0:
                save_cache(args.cache, cache)

            # Rate limit: 0.5s between calls
            if i < len(to_fetch) - 1:
                time.sleep(0.5)

        # Final cache save
        save_cache(args.cache, cache)
        print(f"\nCache saved ({len(cache)} users)")

    # Build alias map per repo
    print("\nBuilding alias map...")
    alias_map = {}
    total_matched = 0
    total_unmatched = 0

    for repo_name in sorted(repo_logins.keys()):
        logins = repo_logins[repo_name]
        members = repo_members.get(repo_name, [])

        if not members:
            print(f"  {repo_name}: no EIS results, skipping")
            continue

        repo_aliases = {}
        matched = 0
        unmatched = 0

        for login in logins:
            user_data = cache.get(login, {})
            github_name = user_data.get("name")

            if not github_name:
                unmatched += 1
                continue

            # Try to match against EIS members
            eis_match = fuzzy_match(github_name, members)
            if eis_match:
                repo_aliases[login] = eis_match
                matched += 1
            else:
                # Still store the GitHub name even without EIS match
                # This is useful for manual review
                repo_aliases[login] = github_name
                unmatched += 1

        if repo_aliases:
            alias_map[repo_name] = repo_aliases

        total_matched += matched
        total_unmatched += unmatched
        print(f"  {repo_name}: {matched} matched, {unmatched} unmatched, {len(repo_aliases)} aliases")

    # Write output
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(alias_map, f, indent=2, ensure_ascii=False)

    print(f"\nAlias map written to {args.output}")
    print(f"  Total repos: {len(alias_map)}")
    print(f"  Total aliases: {sum(len(v) for v in alias_map.values())}")
    print(f"  Fuzzy matched to EIS: {total_matched}")
    print(f"  GitHub name only: {total_unmatched}")


if __name__ == "__main__":
    main()
