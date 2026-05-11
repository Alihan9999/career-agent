"""
Workday spider. Workday tenants expose a JSON search endpoint at
<tenant>/wday/cxs/<tenant>/<site>/jobs. The endpoint requires:
  - HTTP POST (not GET)
  - JSON body with appliedFacets, limit, offset, searchText
  - Chrome TLS fingerprint (most tenants reject curl-default fingerprints)

We use Scrapling's `Fetcher.post()` directly — NOT `StealthyFetcher.fetch(method="POST")`,
which silently sends GET (the stealth Playwright path doesn't expose
non-navigation HTTP methods). Fetcher.post() goes through Scrapling's
HTTP client with Chrome TLS impersonation, which is what we actually need
for a JSON API call.

`ats_id` is the full tenant URL prefix, e.g.
  "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"
The spider derives the JSON endpoint from it.
"""
from __future__ import annotations

import json
import re

from .base import Job, import_scrapling


def list_jobs(ats_id: str) -> list[dict]:
    Fetcher, _, _ = import_scrapling()
    base = ats_id.rstrip("/")
    match = re.match(r"https?://([^/]+)/(.+)", base)
    if not match:
        raise SystemExit(f"workday: ats_id must be a full Workday URL, got {ats_id!r}")
    host, path = match.group(1), match.group(2)
    tenant = host.split(".")[0]
    site = path.split("/")[-1]
    endpoint = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"

    body = {
        "appliedFacets": {},
        "limit": 50,
        "offset": 0,
        "searchText": "",
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Referer": base + "/",
        "Origin": f"https://{host}",
    }

    page = Fetcher.post(
        endpoint,
        json=body,
        headers=headers,
        impersonate="chrome",
    )

    if page.status != 200:
        raise SystemExit(
            f"workday: HTTP {page.status} from {endpoint}. "
            f"Verify the tenant URL is correct (no trailing /jobs, no /en-US prefix). "
            f"Run: curl -X POST '{endpoint}' -H 'Content-Type: application/json' "
            f"-d '{{\"appliedFacets\":{{}},\"limit\":1,\"offset\":0,\"searchText\":\"\"}}'"
        )

    body_text = getattr(page, "body", None) or getattr(page, "text", None) or page.html_content
    try:
        data = json.loads(body_text)
    except (json.JSONDecodeError, TypeError):
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
