"""
LinkedIn spider. Personal job-search use only. Uses the public guest jobs API
(no auth) which returns HTML cards.

`ats_id` here is a search-spec string in the form:
    keywords=Platform+Engineer&location=United+States&f_TPR=r604800

The spider URL-encodes it onto the public endpoint.
"""
from __future__ import annotations

import re

from .base import Job, import_scrapling

GUEST_API = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?{query}"


def list_jobs(ats_id: str) -> list[dict]:
    _, StealthyFetcher, _ = import_scrapling()
    url = GUEST_API.format(query=ats_id.lstrip("?"))
    page = StealthyFetcher.fetch(
        url, headless=True, impersonate="chrome", solve_cloudflare=True
    )
    if page.status != 200:
        raise SystemExit(f"linkedin: HTTP {page.status} for {url}")

    jobs = []
    for card in page.css("li"):
        title_node = card.css("h3.base-search-card__title::text").get()
        link_node = card.css("a.base-card__full-link::attr(href)").get()
        loc_node = card.css(".job-search-card__location::text").get()
        company_node = card.css("h4.base-search-card__subtitle a::text").get()
        if not title_node or not link_node:
            continue
        jobs.append(
            Job(
                title=_clean(title_node),
                url=_clean(link_node).split("?")[0],
                location=_clean(loc_node or ""),
                department=_clean(company_node or ""),
                source="linkedin",
            ).to_dict()
        )
    return jobs


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()
