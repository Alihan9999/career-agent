#!/usr/bin/env python3
"""
Learning Analyzer
Reads data/applications.jsonl, aggregates conversion patterns, and writes
analysis/conversions-<date>.md. Also updates data/blocked-companies.json
and data/role-family-conversion.json which the Application Decision Agent
reads as input.

Run weekly or after status updates. Backed by Rejection Learning Agent
(agents/rejection-learning-agent.md).

Usage: python3 scripts/learning-analyzer.py
"""

import json
import re
from collections import defaultdict, Counter
from datetime import datetime, date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
APPS_PATH = ROOT / "data" / "applications.jsonl"
REPORT_DIR = ROOT / "analysis"
REPORT_DIR.mkdir(exist_ok=True)
BLOCKED_PATH = ROOT / "data" / "blocked-companies.json"
ROLE_CONV_PATH = ROOT / "data" / "role-family-conversion.json"

POSITIVE_STATUSES = {"phone_screen", "hiring_manager", "take_home", "on_site", "offer"}
REJECTION_STATUSES = {"auto_reject_24h", "auto_reject_fast", "auto_reject_slow"}
GHOST_STATUSES = {"ghosted"}
BLOCKED_STATUSES = {
    "blocked_by_quality_gate",
    "blocked_networking_first",
    "blocked_gap_project",
    "blocked_pre_pipeline",
}


def load_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"  skipping invalid row at line {i}: {e}")
    return rows


def submitted_only(rows: list[dict]) -> list[dict]:
    """Rows that actually went out, not blocked."""
    return [r for r in rows if r.get("status") not in BLOCKED_STATUSES]


def with_outcome(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r.get("status") and r["status"] != "pending"]


def is_positive(row: dict) -> bool:
    return row.get("status") in POSITIVE_STATUSES


def is_rejected(row: dict) -> bool:
    return row.get("status") in REJECTION_STATUSES or row.get("status") in GHOST_STATUSES


def conversion_rate(rows: list[dict]) -> tuple[int, int, float]:
    n = len(rows)
    if n == 0:
        return (0, 0, 0.0)
    pos = sum(1 for r in rows if is_positive(r))
    return (pos, n, round(100 * pos / n, 1))


def group_by(rows: list[dict], key: str) -> dict[str, list[dict]]:
    out = defaultdict(list)
    for r in rows:
        v = r.get(key) or "unknown"
        out[v].append(r)
    return out


def per_group_conversion(rows: list[dict], key: str, min_n: int = 5) -> list[tuple]:
    groups = group_by(rows, key)
    out = []
    for k, vs in groups.items():
        pos, n, rate = conversion_rate(vs)
        if n >= min_n or pos > 0:
            out.append((k, pos, n, rate))
    return sorted(out, key=lambda x: (-x[3], -x[2]))


def time_to_response_dist(rows: list[dict]) -> dict:
    buckets = {"<24h": 0, "1-7d": 0, "7-21d": 0, "21d+": 0, "unknown": 0}
    for r in rows:
        ttr = r.get("time_to_response_days")
        if ttr is None:
            buckets["unknown"] += 1
            continue
        if ttr < 1:
            buckets["<24h"] += 1
        elif ttr <= 7:
            buckets["1-7d"] += 1
        elif ttr <= 21:
            buckets["7-21d"] += 1
        else:
            buckets["21d+"] += 1
    return buckets


def find_blocked_companies(rows: list[dict]) -> list[str]:
    """Companies with 3+ ghost/reject and 0 positives."""
    by_co = group_by(rows, "company")
    blocked = []
    for company, rs in by_co.items():
        rejected = sum(1 for r in rs if is_rejected(r))
        positive = sum(1 for r in rs if is_positive(r))
        if rejected >= 3 and positive == 0:
            blocked.append(company)
    return sorted(blocked)


def role_family_conversion_map(rows: list[dict]) -> dict:
    by_family = group_by(rows, "role_family")
    out = {}
    for fam, rs in by_family.items():
        pos, n, rate = conversion_rate(rs)
        out[fam] = {
            "applied": n,
            "positives": pos,
            "rate_pct": rate,
            "last_30d": conversion_rate([
                r for r in rs
                if "date_applied" in r and _within_days(r["date_applied"], 30)
            ])[:2],
        }
    return out


def _within_days(date_str: str, days: int) -> bool:
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return False
    return (date.today() - d).days <= days


def keyword_correlation(rows: list[dict]) -> dict:
    """Keywords that appear in keywords_added of positive vs rejected apps."""
    pos_keywords = Counter()
    neg_keywords = Counter()
    for r in rows:
        kws = r.get("keywords_added") or []
        if is_positive(r):
            pos_keywords.update(kws)
        elif is_rejected(r):
            neg_keywords.update(kws)
    return {
        "positive_top": pos_keywords.most_common(15),
        "negative_top": neg_keywords.most_common(15),
    }


def variant_performance(rows: list[dict]) -> list[tuple]:
    return per_group_conversion(rows, "resume_variant", min_n=3)


def ats_platform_timing(rows: list[dict]) -> dict:
    by_plat = group_by(rows, "ats_platform")
    out = {}
    for plat, rs in by_plat.items():
        ttrs = [r["time_to_response_days"] for r in rs if r.get("time_to_response_days") is not None]
        if not ttrs:
            continue
        median = sorted(ttrs)[len(ttrs) // 2]
        out[plat] = {
            "median_response_days": median,
            "samples": len(ttrs),
        }
    return out


def build_report(rows: list[dict]) -> str:
    lines = []
    today = date.today().isoformat()
    lines.append(f"# Conversion Analysis — {today}")
    lines.append("")

    total = len(rows)
    submitted = submitted_only(rows)
    finished = with_outcome(rows)
    pos, _, rate = conversion_rate(finished)

    lines.append(f"**Total rows:** {total}")
    lines.append(f"**Submitted (not blocked):** {len(submitted)}")
    lines.append(f"**With known outcome:** {len(finished)}")
    lines.append(f"**Conversions (any positive response):** {pos}")
    lines.append(f"**Conversion rate:** {rate}%")
    if total < 30:
        lines.append("")
        lines.append("> Data thin (<30 rows). Patterns are suggestive, not statistically meaningful.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Conversion by slice
    lines.append("## Conversion by Resume Variant")
    for variant, p, n, r in variant_performance(submitted):
        lines.append(f"- Variant {variant}: {p}/{n} = {r}%")
    if not variant_performance(submitted):
        lines.append("- No data yet.")
    lines.append("")

    lines.append("## Conversion by Role Family")
    for fam, p, n, r in per_group_conversion(submitted, "role_family"):
        lines.append(f"- {fam}: {p}/{n} = {r}%")
    lines.append("")

    lines.append("## Conversion by ATS Platform")
    for plat, p, n, r in per_group_conversion(submitted, "ats_platform"):
        lines.append(f"- {plat}: {p}/{n} = {r}%")
    lines.append("")

    lines.append("## Conversion by Brand Tier")
    for tier, p, n, r in per_group_conversion(submitted, "company_brand_tier"):
        lines.append(f"- Brand tier {tier}: {p}/{n} = {r}%")
    lines.append("")

    # Timing
    lines.append("## Time-to-Response Distribution")
    for bucket, n in time_to_response_dist(submitted).items():
        lines.append(f"- {bucket}: {n}")
    lines.append("")

    lines.append("## ATS Platform Median Response Time")
    for plat, stats in ats_platform_timing(submitted).items():
        lines.append(f"- {plat}: {stats['median_response_days']}d (n={stats['samples']})")
    lines.append("")

    # Blocked companies
    blocked = find_blocked_companies(submitted)
    lines.append("## Companies Promoted to NETWORKING_FIRST (3+ rejects, 0 positives)")
    if blocked:
        for c in blocked:
            lines.append(f"- {c}")
    else:
        lines.append("- None.")
    lines.append("")

    # Keyword correlation
    kw = keyword_correlation(submitted)
    lines.append("## Keywords in Positive Apps (top 15)")
    if kw["positive_top"]:
        for k, c in kw["positive_top"]:
            lines.append(f"- {k}: {c}")
    else:
        lines.append("- Insufficient positive samples.")
    lines.append("")

    lines.append("## Keywords in Rejected Apps (top 15)")
    if kw["negative_top"]:
        for k, c in kw["negative_top"]:
            lines.append(f"- {k}: {c}")
    else:
        lines.append("- No data.")
    lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    if total < 30:
        lines.append("- Continue applying under v2 pipeline; analyze again after 30 outcomes.")
    if blocked:
        lines.append(f"- Add the {len(blocked)} blocked companies to the NETWORKING_FIRST list (already written to data/blocked-companies.json).")
    families_zero = [
        fam for fam, p, n, r in per_group_conversion(submitted, "role_family")
        if n >= 10 and p == 0
    ]
    if families_zero:
        lines.append(f"- Role family rework needed: {', '.join(families_zero)} (10+ apps, 0 conversions).")
    return "\n".join(lines)


def main():
    if not APPS_PATH.exists():
        print(f"No applications log at {APPS_PATH}. Pipeline has not produced rows yet.")
        return

    rows = load_rows(APPS_PATH)
    if not rows:
        print("Application log is empty.")
        return

    submitted = submitted_only(rows)

    # Write the report
    today = date.today().isoformat()
    report_path = REPORT_DIR / f"conversions-{today}.md"
    report_path.write_text(build_report(rows), encoding="utf-8")
    print(f"Wrote: {report_path}")

    # Write blocked-companies.json
    blocked = find_blocked_companies(submitted)
    BLOCKED_PATH.write_text(json.dumps({"blocked": blocked, "as_of": today}, indent=2), encoding="utf-8")
    print(f"Wrote: {BLOCKED_PATH} ({len(blocked)} companies)")

    # Write role-family-conversion.json
    rf = role_family_conversion_map(submitted)
    ROLE_CONV_PATH.write_text(json.dumps({"as_of": today, "families": rf}, indent=2), encoding="utf-8")
    print(f"Wrote: {ROLE_CONV_PATH}")

    pos, n, rate = conversion_rate(with_outcome(submitted))
    print(f"\nSummary: {pos}/{n} conversions ({rate}%) across {len(submitted)} submitted applications.")


if __name__ == "__main__":
    main()
