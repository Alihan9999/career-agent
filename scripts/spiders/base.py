"""Shared types and helpers for spider modules."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Job:
    title: str
    url: str
    location: str = ""
    posted: str = ""
    department: str = ""
    source: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FetchResult:
    url: str
    status: int
    content: str
    fetcher: str = ""
    blocked: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


CLOUDFLARE_MARKERS = (
    "Just a moment",
    "Checking your browser",
    "cf-chl-bypass",
    "challenge-platform",
    "__cf_chl_",
)


def looks_blocked(html: str, status: int) -> bool:
    """Heuristic: did this response come from a bot wall?"""
    if status in (401, 403, 429):
        return True
    if status >= 500:
        return False
    head = html[:4000]
    return any(marker in head for marker in CLOUDFLARE_MARKERS)


def import_scrapling():
    """Lazy import so JSON-API spiders work without Scrapling installed."""
    try:
        from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
        return Fetcher, StealthyFetcher, DynamicFetcher
    except ImportError as e:
        raise SystemExit(
            "Scrapling not installed. Run: pip install -r requirements.txt && scrapling install"
        ) from e
