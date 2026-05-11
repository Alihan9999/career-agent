"""Greenhouse ATS spider. Uses the public boards API — no JS, no auth needed."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from .base import Job

API = "https://boards-api.greenhouse.io/v1/boards/{ats_id}/jobs"


def list_jobs(ats_id: str) -> list[dict]:
    url = API.format(ats_id=ats_id)
    req = urllib.request.Request(url, headers={"User-Agent": "career-agent/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"greenhouse: HTTP {e.code} for {url}")
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
