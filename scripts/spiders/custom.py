"""
Custom-careers-page spider. Tries plain HTTP first; if the body looks empty
(JS-only SPA), JS-only host, or blocked (Cloudflare), escalates to
DynamicFetcher and then StealthyFetcher.

`ats_id` is unused; the spider takes a `url` kwarg instead. Call via
`list_jobs(ats_id, url=...)`.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from .base import Job, import_scrapling, looks_blocked

JOB_LINK_PATTERNS = [
    re.compile(r"/(jobs?|careers?|positions?|openings?)/[A-Za-z0-9-_]+", re.IGNORECASE),
]

# Hosts that are JS-rendered React/Vue SPAs. Plain HTTP returns the app shell
# with no job data; we always escalate straight to DynamicFetcher for these.
KNOWN_SPA_HOSTS = (
    "metacareers.com",
    "www.metacareers.com",
    "careers.google.com",
    "www.google.com",
    "jobs.apple.com",
    "www.amazon.jobs",
    "amazon.jobs",
    "jobs.netflix.com",
    "netflix.com",
    "jobs.careers.microsoft.com",
    "fly.io",
)


def list_jobs(ats_id: str = "", url: str = "") -> list[dict]:
    if not url:
        raise SystemExit("custom: pass --url <careers_url>")
    Fetcher, StealthyFetcher, DynamicFetcher = import_scrapling()
    host = urlparse(url).netloc.lower()

    if host in KNOWN_SPA_HOSTS:
        # Skip the cheap fetch — these always need a real browser.
        page = DynamicFetcher.fetch(url, network_idle=True, headless=True)
        body = page.html_content
    else:
        page = Fetcher.get(url, impersonate="chrome")
        body = getattr(page, "html_content", "") or getattr(page, "body", "")
        if _is_sparse(body) or _is_app_shell(body) or looks_blocked(body, page.status):
            page = DynamicFetcher.fetch(url, network_idle=True, headless=True)
            body = page.html_content

    if looks_blocked(body, page.status):
        page = StealthyFetcher.fetch(
            url, headless=True, solve_cloudflare=True, impersonate="chrome"
        )
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

    if not jobs:
        # Surface this clearly so /scan can downgrade it to "no openings"
        # instead of silently dropping the company.
        print(f"custom: no job links found at {url} (host={host})", file=__import__("sys").stderr)
    return jobs


def _is_sparse(html: str) -> bool:
    text = re.sub(r"<[^>]+>", " ", html or "")
    return len(text.strip()) < 200


def _is_app_shell(html: str) -> bool:
    """Detect React/Vue/Next.js SPA shells that have lots of HTML but no real content."""
    if not html:
        return True
    head = html[:8000]
    spa_markers = (
        '<div id="root"',
        '<div id="__next"',
        '<div id="app"',
        'window.__INITIAL_STATE__',
        'window.__NEXT_DATA__',
        'data-reactroot',
    )
    has_spa_marker = any(m in head for m in spa_markers)
    visible_text = re.sub(r"<[^>]+>", " ", html)
    visible_text = re.sub(r"\s+", " ", visible_text).strip()
    # SPA shell: marker present + thin visible content
    return has_spa_marker and len(visible_text) < 1500


def _absolutize(base: str, href: str) -> str:
    from urllib.parse import urljoin
    return urljoin(base, href)
