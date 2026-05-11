"""Greenhouse ATS spider. Uses the public boards API — no JS, no auth needed.

Greenhouse migrated some boards from `boards-api.greenhouse.io` to
`job-boards.greenhouse.io` between 2024 and 2026; this spider tries both
hosts so a slug that's valid on the new host doesn't 404 on us.

Returns the full /jobs response as one shot — Greenhouse's public boards
endpoint is unpaginated (one big array per board), so we never paginate;
the /scan command applies client-side filters.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from .base import Job

API_HOSTS = [
    "https://boards-api.greenhouse.io/v1/boards/{ats_id}/jobs",
    "https://job-boards.greenhouse.io/api/v1/boards/{ats_id}/jobs",
]


def list_jobs(ats_id: str) -> list[dict]:
    last_err = None
    data = None
    tried = []
    for tmpl in API_HOSTS:
        url = tmpl.format(ats_id=ats_id)
        tried.append(url)
        req = urllib.request.Request(url, headers={"User-Agent": "career-agent/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                break
        except urllib.error.HTTPError as e:
            last_err = e
            continue
        except urllib.error.URLError as e:
            last_err = e
            continue

    if data is None:
        if isinstance(last_err, urllib.error.HTTPError) and last_err.code == 404:
            raise SystemExit(
                f"greenhouse: 404 for slug '{ats_id}' on both hosts. "
                f"Tried: {tried[0]} and {tried[1]}. "
                f"The company may have moved off Greenhouse or use a different slug."
            )
        raise SystemExit(f"greenhouse: {last_err} for slug '{ats_id}'")

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
