"""
Custom-careers-page spider. Tries plain HTTP first; if the body looks empty
(JS-only SPA) or blocked (Cloudflare), escalates to DynamicFetcher and then
StealthyFetcher.

`ats_id` is unused; the spider takes a `url` kwarg instead. Call via
`list_jobs(ats_id, url=...)`.
"""
from __future__ import annotations

import re

from .base import Job, import_scrapling, looks_blocked

JOB_LINK_PATTERNS = [
    re.compile(r"/(jobs?|careers?|positions?|openings?)/[A-Za-z0-9-_]+", re.IGNORECASE),
]


def list_jobs(ats_id: str = "", url: str = "") -> list[dict]:
    if not url:
        raise SystemExit("custom: pass --url for custom-careers spider")
    Fetcher, StealthyFetcher, DynamicFetcher = import_scrapling()

    page = Fetcher.get(url, impersonate="chrome")
    body = getattr(page, "html_content", "") or getattr(page, "body", "")
    if _is_sparse(body) or looks_blocked(body, page.status):
        page = DynamicFetcher.fetch(url, network_idle=True, headless=True)
        body = page.html_content
        if looks_blocked(body, page.status):
            page = StealthyFetcher.fetch(url, headless=True, solve_cloudflare=True, impersonate="chrome")
            body = page.html_content

    jobs = []
    seen = set()
    for a in page.css("a"):
        href = a.attrib.get("href", "")
        if not href or href.startswith(("#", "mailto:", "tel:")):
            continue
        if not any(p.search(href) for p in JOB_LINK_PATTERNS):
            continue
        text = (a.css("::text").get() or a.text or "").strip()
        if not text or len(text) < 4:
            continue
        full = href if href.startswith("http") else _absolutize(url, href)
        if full in seen:
            continue
        seen.add(full)
        jobs.append(Job(title=text, url=full, source="custom").to_dict())
    return jobs


def _is_sparse(html: str) -> bool:
    text = re.sub(r"<[^>]+>", " ", html or "")
    return len(text.strip()) < 200


def _absolutize(base: str, href: str) -> str:
    from urllib.parse import urljoin
    return urljoin(base, href)
