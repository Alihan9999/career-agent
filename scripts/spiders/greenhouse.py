"""Greenhouse ATS spider. Three-tier resolver:

1. boards-api.greenhouse.io (legacy JSON API)
2. job-boards.greenhouse.io/api (newer JSON API — used by post-2024 customers
   like Anthropic, Coinbase, Metronome, Glean)
3. boards.greenhouse.io/embed/job_board (server-rendered HTML embed — works
   for almost every Greenhouse customer even when both JSON APIs 404)

The embed page is the durable fallback because it's what Greenhouse iframes
into customers' careers pages, so they keep it working forever for backwards
compatibility.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

from .base import Job

API_HOSTS = [
    "https://boards-api.greenhouse.io/v1/boards/{ats_id}/jobs",
    "https://job-boards.greenhouse.io/api/v1/boards/{ats_id}/jobs",
]
EMBED_HTML = "https://boards.greenhouse.io/embed/job_board?for={ats_id}"


def list_jobs(ats_id: str) -> list[dict]:
    # Tier 1+2: try both JSON API hosts.
    api_err = None
    for tmpl in API_HOSTS:
        url = tmpl.format(ats_id=ats_id)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "career-agent/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return _parse_api(data)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            api_err = e
            continue

    # Tier 3: embed HTML (server-rendered, almost always works).
    embed_url = EMBED_HTML.format(ats_id=ats_id)
    try:
        req = urllib.request.Request(embed_url, headers={"User-Agent": "career-agent/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        jobs = _parse_embed(html, ats_id)
        if jobs:
            return jobs
    except (urllib.error.HTTPError, urllib.error.URLError):
        pass

    # All three tiers failed.
    if isinstance(api_err, urllib.error.HTTPError) and api_err.code == 404:
        raise SystemExit(
            f"greenhouse: slug '{ats_id}' returned 404 from both JSON APIs and "
            f"the embed page returned no jobs. The company likely moved off "
            f"Greenhouse entirely (check {embed_url} in a browser to confirm)."
        )
    raise SystemExit(f"greenhouse: {api_err} for slug '{ats_id}'")


def _parse_api(data: dict) -> list[dict]:
    jobs = []
    for j in data.get("jobs", []):
        location = ""
        if isinstance(j.get("location"), dict):
            location = j["location"].get("name", "")
        jobs.append(
            Job(
                title=j.get("title", ""),
                url=j.get("absolute_url", ""),
                location=location,
                posted=j.get("updated_at", ""),
                department=", ".join(d.get("name", "") for d in j.get("departments", [])),
                source="greenhouse",
            ).to_dict()
        )
    return jobs


def _parse_embed(html: str, slug: str) -> list[dict]:
    """Server-rendered Greenhouse embed.

    Each opening is a `<div class="opening">` containing an `<a>` with the job
    title and a `<span class="location">` with the location.
    """
    jobs = []
    pattern = re.compile(
        r'<div[^>]*class="[^"]*opening[^"]*"[^>]*>.*?'
        r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
        r'.*?<span[^>]*class="[^"]*location[^"]*"[^>]*>(.*?)</span>',
        re.DOTALL,
    )
    for href, title, location in pattern.findall(html):
        title = re.sub(r"<[^>]+>", "", title).strip()
        location = re.sub(r"<[^>]+>", "", location).strip()
        if not href.startswith("http"):
            href = "https://boards.greenhouse.io" + href if href.startswith("/") else f"https://boards.greenhouse.io/{slug}/{href.lstrip('/')}"
        if title:
            jobs.append(Job(title=title, url=href, location=location, source="greenhouse").to_dict())
    return jobs
