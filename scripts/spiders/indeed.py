"""
Indeed spider. Indeed sits behind Cloudflare; StealthyFetcher with
solve_cloudflare handles the challenge in most regions.

`ats_id` is the search query string, e.g. "q=Platform+Engineer&l=remote&fromage=7".
"""
from __future__ import annotations

import re

from .base import Job, import_scrapling

SEARCH_URL = "https://www.indeed.com/jobs?{query}"


def list_jobs(ats_id: str) -> list[dict]:
    _, StealthyFetcher, _ = import_scrapling()
    url = SEARCH_URL.format(query=ats_id.lstrip("?"))
    page = StealthyFetcher.fetch(
        url, headless=True, solve_cloudflare=True, impersonate="chrome"
    )
    if page.status != 200:
        raise SystemExit(f"indeed: HTTP {page.status} for {url}")

    jobs = []
    for card in page.css("a.tapItem, a[data-jk]"):
        jk = card.attrib.get("data-jk") or _extract_jk(card.attrib.get("href", ""))
        title = card.css("h2 span::text").get() or card.css("span[title]::attr(title)").get()
        company = card.css("span.companyName::text").get()
        location = card.css("div.companyLocation::text").get()
        if not jk or not title:
            continue
        jobs.append(
            Job(
                title=title.strip(),
                url=f"https://www.indeed.com/viewjob?jk={jk}",
                location=(location or "").strip(),
                department=(company or "").strip(),
                source="indeed",
            ).to_dict()
        )
    return jobs


def _extract_jk(href: str) -> str:
    m = re.search(r"[?&]jk=([A-Za-z0-9]+)", href or "")
    return m.group(1) if m else ""
