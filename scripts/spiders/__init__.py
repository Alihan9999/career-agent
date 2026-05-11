"""
Per-board spiders.

Each module exposes `list_jobs(ats_id) -> list[Job]` and optionally
`fetch_posting(url) -> str`. The CLI in scripts/scrape.py dispatches
to the right module by ats name.
"""
from . import (
    ashby,
    builtin,
    custom,
    greenhouse,
    indeed,
    lever,
    linkedin,
    wellfound,
    workable,
    workday,
)

REGISTRY = {
    "greenhouse": greenhouse,
    "lever": lever,
    "ashby": ashby,
    "workable": workable,
    "workday": workday,
    "linkedin": linkedin,
    "indeed": indeed,
    "wellfound": wellfound,
    "builtin": builtin,
    "custom": custom,
}
