"""
Workable spider. Tries the public JSON endpoint first, then falls back to
stealth rendering of the HTML board if the endpoint is rate-limited.
"""
from __future__ import annotations

import json
import re

from .base import Job, import_scrapling, looks_blocked

JSON_URL = "https://apply.workable.com/api/v3/accounts/{ats_id}/jobs"
HTML_URL = "https://apply.workable.com/{ats_id}/"


def list_jobs(ats_id: str) -> list[dict]:
    Fetcher, StealthyFetcher, _ = import_scrapling()
    jobs = []

    # 1. JSON endpoint (cheap path).
    resp = Fetcher.get(JSON_URL.format(ats_id=ats_id), impersonate="chrome")
    if resp.status == 200:
        try:
            data = json.loads(resp.body)
            for j in data.get("results", []):
                jobs.append(
                    Job(
                        title=j.get("title", ""),
                        url=j.get("url") or f"{HTML_URL.format(ats_id=ats_id)}j/{j.get('shortcode', '')}",
                        location=_loc(j.get("location")),
                        department=j.get("department", ""),
                        posted=j.get("created", ""),
                        source="workable",
                    ).to_dict()
                )
            if jobs:
                return jobs
        except json.JSONDecodeError:
            pass

    # 2. Fallback: render the HTML board with stealth.
    page = StealthyFetcher.fetch(HTML_URL.format(ats_id=ats_id), headless=True)
    if looks_blocked(page.html_content, page.status):
        raise SystemExit(f"workable: blocked at HTML board for {ats_id}")
    # Workable embeds an initial state JSON in window.__APP_STATE__.
    state = re.search(r"window\.__APP_STATE__\s*=\s*(\{.*?\})\s*;", page.html_content, re.DOTALL)
    if state:
        try:
            data = json.loads(state.group(1))
            for j in data.get("jobs", []) or data.get("results", []):
                jobs.append(
                    Job(
                        title=j.get("title", ""),
                        url=j.get("url", ""),
                        location=_loc(j.get("location")),
                        department=j.get("department", ""),
                        source="workable",
                    ).to_dict()
                )
        except json.JSONDecodeError:
            pass

    return jobs


def _loc(loc) -> str:
    if isinstance(loc, str):
        return loc
    if isinstance(loc, dict):
        parts = [loc.get("city"), loc.get("region"), loc.get("country")]
        return ", ".join(p for p in parts if p)
    return ""
