"""Lever ATS spider. Public postings JSON API."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from .base import Job

API = "https://api.lever.co/v0/postings/{ats_id}?mode=json"


def list_jobs(ats_id: str) -> list[dict]:
    url = API.format(ats_id=ats_id)
    req = urllib.request.Request(url, headers={"User-Agent": "career-agent/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"lever: HTTP {e.code} for {url}")
    jobs = []
    for p in data:
        cats = p.get("categories") or {}
        jobs.append(
            Job(
                title=p.get("text", ""),
                url=p.get("hostedUrl", ""),
                location=cats.get("location", ""),
                department=cats.get("team", ""),
                posted=str(p.get("createdAt", "")),
                source="lever",
            ).to_dict()
        )
    return jobs
