"""
Ashby spider. Public listings render via JS, so we use DynamicFetcher.
Replaces the WebSearch fallback that the old /scan command used.
"""
from __future__ import annotations

import json
import re

from .base import Job, import_scrapling

BOARD_URL = "https://jobs.ashbyhq.com/{ats_id}"
API_GRAPHQL = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"


def list_jobs(ats_id: str) -> list[dict]:
    _, _, DynamicFetcher = import_scrapling()
    url = BOARD_URL.format(ats_id=ats_id)
    page = DynamicFetcher.fetch(url, network_idle=True, headless=True)
    jobs = []

    # Ashby embeds the full job list as JSON in a __NEXT_DATA__-style script tag.
    # First try that; fall back to DOM scraping if the schema shifts.
    script_match = re.search(
        r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        page.html_content,
        re.DOTALL,
    )
    if script_match:
        try:
            payload = json.loads(script_match.group(1))
            postings = _walk_for_postings(payload)
            for p in postings:
                jobs.append(
                    Job(
                        title=p.get("title", ""),
                        url=f"https://jobs.ashbyhq.com/{ats_id}/{p.get('id', '')}",
                        location=_location_str(p.get("locationName") or p.get("location")),
                        department=p.get("departmentName", ""),
                        posted=p.get("publishedDate", ""),
                        source="ashby",
                    ).to_dict()
                )
        except (json.JSONDecodeError, KeyError):
            pass

    if not jobs:
        # DOM fallback: each card links to /{ats_id}/<uuid>.
        for a in page.css("a[href*='/" + ats_id + "/']"):
            href = a.attrib.get("href", "")
            title = a.css("::text").get() or a.text or ""
            if not href or not title.strip():
                continue
            if not href.startswith("http"):
                href = "https://jobs.ashbyhq.com" + href
            jobs.append(
                Job(title=title.strip(), url=href, source="ashby").to_dict()
            )

    return jobs


def _walk_for_postings(node):
    """Recursively find 'jobPostings' or 'jobs' arrays in the Next.js payload."""
    if isinstance(node, dict):
        for key in ("jobPostings", "jobs", "postings"):
            if key in node and isinstance(node[key], list):
                return node[key]
        for v in node.values():
            found = _walk_for_postings(v)
            if found:
                return found
    elif isinstance(node, list):
        for v in node:
            found = _walk_for_postings(v)
            if found:
                return found
    return []


def _location_str(loc) -> str:
    if isinstance(loc, str):
        return loc
    if isinstance(loc, dict):
        return loc.get("name", "") or loc.get("locationName", "")
    return ""
