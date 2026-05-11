"""
Wellfound (formerly AngelList Talent) spider. Pages are JS-rendered; we use
DynamicFetcher and read the Apollo state blob embedded in the HTML.

`ats_id` is the company slug, e.g. "stripe".
"""
from __future__ import annotations

import json
import re

from .base import Job, import_scrapling

COMPANY_URL = "https://wellfound.com/company/{ats_id}/jobs"


def list_jobs(ats_id: str) -> list[dict]:
    _, _, DynamicFetcher = import_scrapling()
    url = COMPANY_URL.format(ats_id=ats_id)
    page = DynamicFetcher.fetch(url, network_idle=True, headless=True)
    jobs = []

    # Wellfound embeds Apollo cache as __APOLLO_STATE__.
    state = re.search(r"window\.__APOLLO_STATE__\s*=\s*(\{.*?\});", page.html_content, re.DOTALL)
    if state:
        try:
            data = json.loads(state.group(1))
            for key, val in data.items():
                if not isinstance(val, dict):
                    continue
                if val.get("__typename") not in ("JobListing", "Job", "StartupJob"):
                    continue
                jobs.append(
                    Job(
                        title=val.get("title", ""),
                        url=_job_url(ats_id, val),
                        location=", ".join(val.get("locationNames", []) or []),
                        posted=val.get("liveStartAt", ""),
                        source="wellfound",
                    ).to_dict()
                )
        except json.JSONDecodeError:
            pass

    if not jobs:
        for a in page.css("a[href*='/jobs/']"):
            href = a.attrib.get("href", "")
            title = (a.css("::text").get() or "").strip()
            if title and href:
                if not href.startswith("http"):
                    href = "https://wellfound.com" + href
                jobs.append(Job(title=title, url=href, source="wellfound").to_dict())

    return jobs


def _job_url(slug: str, val: dict) -> str:
    jid = val.get("id") or val.get("publicId")
    if jid:
        return f"https://wellfound.com/jobs/{jid}"
    return f"https://wellfound.com/company/{slug}/jobs"
