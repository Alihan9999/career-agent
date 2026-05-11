"""
Workday spider. Workday tenants expose a JSON search endpoint at
<tenant>/wday/cxs/<tenant>/<site>/jobs with a POST body. Most tenants block
plain HTTP, so we use StealthyFetcher with Chrome impersonation.

`ats_id` here is the full tenant URL prefix, e.g.
  "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"
The spider derives the JSON endpoint from it.
"""
from __future__ import annotations

import json
import re

from .base import Job, import_scrapling


def list_jobs(ats_id: str) -> list[dict]:
    _, StealthyFetcher, _ = import_scrapling()
    base = ats_id.rstrip("/")
    match = re.match(r"https?://([^/]+)/(.+)", base)
    if not match:
        raise SystemExit(f"workday: ats_id must be a full Workday URL, got {ats_id!r}")
    host, path = match.group(1), match.group(2)
    # Tenant slug is the subdomain before .wd*.myworkdayjobs.com
    tenant = host.split(".")[0]
    site = path.split("/")[-1]
    endpoint = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"

    page = StealthyFetcher.fetch(
        endpoint,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json_body={"limit": 50, "offset": 0, "searchText": ""},
        headless=True,
    )
    try:
        data = json.loads(page.body if hasattr(page, "body") else page.html_content)
    except json.JSONDecodeError:
        raise SystemExit(f"workday: non-JSON response from {endpoint}")

    jobs = []
    for j in data.get("jobPostings", []):
        external_path = j.get("externalPath", "")
        url = f"{base}{external_path}" if external_path else ""
        jobs.append(
            Job(
                title=j.get("title", ""),
                url=url,
                location=j.get("locationsText", ""),
                posted=j.get("postedOn", ""),
                source="workday",
            ).to_dict()
        )
    return jobs
