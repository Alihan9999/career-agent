#!/usr/bin/env python3
"""
scrape.py — unified scraping CLI for the career agent.

Two subcommands:

  fetch <url> [--stealth] [--render]
      Fetch a single job-posting URL and print the rendered text body.
      Used by the Job Analyzer agent. Auto-detects whether to escalate
      from plain HTTP -> dynamic browser -> stealth (Cloudflare-aware).

  board <ats> <ats_id> [--url <url>] [--json]
      List jobs from a known board. <ats> is one of:
        greenhouse, lever, ashby, workable, workday, linkedin,
        indeed, wellfound, builtin, custom
      Prints one job per line (TSV: title, url, location) or JSON with --json.
      Used by /scan.

Examples:
  python3 scripts/scrape.py fetch https://example.com/jobs/123
  python3 scripts/scrape.py board greenhouse stripe
  python3 scripts/scrape.py board ashby tailscale --json
  python3 scripts/scrape.py board custom "" --url https://fly.io/jobs
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow `python3 scripts/scrape.py` from the repo root.
sys.path.insert(0, str(Path(__file__).parent))

from spiders import REGISTRY  # noqa: E402
from spiders.base import looks_blocked  # noqa: E402


def cmd_fetch(args) -> int:
    """Single URL fetch with auto-escalation. Prints rendered text."""
    try:
        from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
    except ImportError:
        print("Scrapling not installed. Run: pip install -r requirements.txt && scrapling install",
              file=sys.stderr)
        return 2

    url = args.url
    page = None
    fetcher_used = ""
    body = ""

    # 1. Plain HTTP with Chrome impersonation.
    if not args.stealth and not args.render:
        try:
            page = Fetcher.get(url, impersonate="chrome")
            body = getattr(page, "html_content", "") or getattr(page, "body", "")
            fetcher_used = "Fetcher"
        except Exception as e:
            print(f"Fetcher failed: {e}", file=sys.stderr)

    # 2. Escalate to DynamicFetcher if blocked, sparse, or --render forced.
    if args.render or (page is not None and (looks_blocked(body, page.status) or _is_sparse(body))):
        page = DynamicFetcher.fetch(url, network_idle=True, headless=True)
        body = page.html_content
        fetcher_used = "DynamicFetcher"

    # 3. Escalate to StealthyFetcher if still blocked or --stealth forced.
    if args.stealth or (page is not None and looks_blocked(body, page.status)):
        page = StealthyFetcher.fetch(
            url, headless=True, solve_cloudflare=True, impersonate="chrome"
        )
        body = page.html_content
        fetcher_used = "StealthyFetcher"

    if page is None:
        print("All fetchers failed", file=sys.stderr)
        return 2

    result = {
        "url": url,
        "status": page.status,
        "fetcher": fetcher_used,
        "blocked": looks_blocked(body, page.status),
        "text": _strip_html(body),
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["text"])
        print(f"\n---\n[fetcher={result['fetcher']} status={result['status']} blocked={result['blocked']}]",
              file=sys.stderr)
    return 0 if not result["blocked"] else 1


def cmd_board(args) -> int:
    ats = args.ats.lower()
    if ats not in REGISTRY:
        print(f"Unknown ats: {ats}. Choices: {', '.join(REGISTRY)}", file=sys.stderr)
        return 2
    spider = REGISTRY[ats]
    try:
        if ats == "custom":
            jobs = spider.list_jobs(args.ats_id, url=args.url)
        else:
            jobs = spider.list_jobs(args.ats_id)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(jobs, indent=2))
    else:
        for j in jobs:
            print(f"{j.get('title','')}\t{j.get('url','')}\t{j.get('location','')}")
    return 0 if jobs else 1


def _strip_html(html: str) -> str:
    """Minimal HTML to text. Good enough for job-posting bodies."""
    import re
    if not html:
        return ""
    # Drop scripts and styles.
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    # Convert <br> and <p> to newlines.
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</p>", "\n\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</?(div|li|tr|h[1-6])[^>]*>", "\n", html, flags=re.IGNORECASE)
    # Strip remaining tags.
    text = re.sub(r"<[^>]+>", " ", html)
    # Collapse whitespace.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _is_sparse(html: str) -> bool:
    return len(_strip_html(html or "")) < 200


def main():
    parser = argparse.ArgumentParser(prog="scrape.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="Fetch a single URL with auto-escalation")
    f.add_argument("url")
    f.add_argument("--stealth", action="store_true", help="Force StealthyFetcher")
    f.add_argument("--render", action="store_true", help="Force DynamicFetcher (Playwright)")
    f.add_argument("--json", action="store_true", help="Emit JSON instead of plain text")
    f.set_defaults(func=cmd_fetch)

    b = sub.add_parser("board", help="List jobs from a known board")
    b.add_argument("ats", help="ATS name (greenhouse, lever, ashby, workable, workday, linkedin, indeed, wellfound, builtin, custom)")
    b.add_argument("ats_id", help="Board ID, slug, or query string for the board")
    b.add_argument("--url", default="", help="Required when ats=custom")
    b.add_argument("--json", action="store_true", help="Emit JSON instead of TSV")
    b.set_defaults(func=cmd_board)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
