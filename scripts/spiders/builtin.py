"""
BuiltIn spider. BuiltIn (builtin.com / builtinnyc.com / etc.) renders job
cards server-side, so a plain Fetcher with Chrome impersonation works.

`ats_id` is the company slug, e.g. "stripe".
"""
from __future__ import annotations

import re

from .base import Job, import_scrapling

COMPANY_URL = "https://builtin.com/company/{ats_id}/jobs"


def list_jobs(ats_id: str) -> list[dict]:
    Fetcher, _, _ = import_scrapling()
    url = COMPANY_URL.format(ats_id=ats_id)
    page = Fetcher.get(url, impersonate="chrome")
    if page.status != 200:
        raise SystemExit(f"builtin: HTTP {page.status} for {url}")

    jobs = []
    for card in page.css("[data-id^='job-card']"):
        title = card.css("h3 a::text").get() or card.css("a[href*='/job/']::text").get()
        href = card.css("a[href*='/job/']::attr(href)").get()
        location = card.css("[class*='location']::text").get()
        if not title or not href:
            continue
        if not href.startswith("http"):
            href = "https://builtin.com" + href
        jobs.append(
            Job(
                title=_clean(title),
                url=href,
                location=_clean(location or ""),
                source="builtin",
            ).to_dict()
        )
    return jobs


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()
