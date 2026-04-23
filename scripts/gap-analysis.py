#!/usr/bin/env python3
"""
Gap Analysis Agent
Scans all output folders, aggregates recurring skill/keyword gaps
across job applications, and writes a ranked report.

Run when the user asks for a gap analysis. Requires at least 30 applications.
Usage: python scripts/gap-analysis.py
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output"
REPORT_DIR = Path(__file__).parent.parent / "analysis"
REPORT_DIR.mkdir(exist_ok=True)
MIN_APPLICATIONS = 1  # analyze all available applications

# Importance weights — these gaps matter more than others
IMPORTANCE_WEIGHTS = {
    "go": 10,
    "golang": 10,
    "datadog": 9,
    "gcp": 8,
    "google cloud": 8,
    "5+ years": 9,
    "senior": 7,
    "typescript": 7,
    "rust": 6,
    "node.js": 6,
    "postgres": 5,
    "postgresql": 5,
    "istio": 5,
    "service mesh": 5,
    "backstage": 4,
    "argocd": 4,
    "helm": 4,
    "tanka": 4,
    "kustomize": 4,
    "opentelemetry": 4,
    "sentry": 4,
    "cmake": 6,
    "slurm": 6,
    "bare metal": 6,
    "pre-sales": 3,
    "data pipelines": 5,
    "forensics": 4,
    "saml": 4,
    "scim": 4,
    "oidc": 5,
    "mtls": 5,
    "spiffe": 5,
    "spire": 5,
    "redis": 3,
    "openSearch": 3,
    "workato": 3,
    "okta workflows": 3,
    "google workspace": 3,
    "zendesk": 3,
    "dns": 4,
    "tls": 4,
    "load balancer": 3,
    "networking": 4,
    "finops": 3,
    "cost optimization": 3,
}

def parse_ats_missing(ats_path: Path) -> list[str]:
    """Extract missing keywords from ats-report.md."""
    missing = []
    if not ats_path.exists():
        return missing
    content = ats_path.read_text(encoding="utf-8")
    in_missing = False
    for line in content.splitlines():
        if "## Keywords: MISSING" in line:
            in_missing = True
            continue
        if in_missing:
            if line.startswith("## "):
                break
            match = re.match(r"[-*]\s+\*\*(.+?)\*\*", line)
            if match:
                missing.append(match.group(1).strip().lower())
    return missing


def parse_job_analysis_gaps(job_path: Path) -> list[str]:
    """Extract red_flags items that look like skill gaps from job-analysis.json."""
    gaps = []
    if not job_path.exists():
        return gaps
    try:
        data = json.loads(job_path.read_text(encoding="utf-8"))
        for flag in data.get("red_flags", []):
            flag_lower = flag.lower()
            gaps.append(flag_lower)
    except (json.JSONDecodeError, KeyError):
        pass
    return gaps


def extract_gap_tokens(text: str) -> list[str]:
    """Pull recognizable gap keywords from free text."""
    tokens = []
    for keyword in IMPORTANCE_WEIGHTS:
        if keyword in text.lower():
            tokens.append(keyword)
    return tokens


def score_gap(gap: str, count: int) -> int:
    """Score a gap by frequency × importance weight."""
    for keyword, weight in IMPORTANCE_WEIGHTS.items():
        if keyword in gap.lower():
            return count * weight
    return count * 1


def collect_applications() -> list[Path]:
    """Return all application output folders."""
    folders = []
    for entry in sorted(OUTPUT_DIR.iterdir()):
        if entry.is_dir() and not entry.name.startswith("gap-analysis"):
            folders.append(entry)
    return folders


def run_analysis():
    apps = collect_applications()
    total = len(apps)

    if total == 0:
        print("No applications found in output/. Run some pipelines first.")
        return

    # Aggregate gaps
    gap_counter = defaultdict(int)      # gap_name -> count of apps it appeared in
    gap_sources = defaultdict(list)     # gap_name -> list of company names

    for folder in apps:
        company = folder.name.rsplit("-", 3)[0]  # strip date suffix
        ats_path = folder / "ats-report.md"
        job_path = folder / "job-analysis.json"

        seen_this_app = set()

        # From ATS missing keywords
        for gap in parse_ats_missing(ats_path):
            tokens = extract_gap_tokens(gap) or [gap]
            for token in tokens:
                if token not in seen_this_app:
                    gap_counter[token] += 1
                    gap_sources[token].append(company)
                    seen_this_app.add(token)

        # From job analysis red flags
        for flag in parse_job_analysis_gaps(job_path):
            tokens = extract_gap_tokens(flag)
            for token in tokens:
                if token not in seen_this_app:
                    gap_counter[token] += 1
                    gap_sources[token].append(company)
                    seen_this_app.add(token)

    # Filter to gaps appearing in 2+ applications
    filtered = {k: v for k, v in gap_counter.items() if v >= 2}

    # Score and rank
    ranked = sorted(
        filtered.items(),
        key=lambda x: score_gap(x[0], x[1]),
        reverse=True
    )

    # Build report
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORT_DIR / f"gap-analysis-{date_str}.md"

    lines = [
        f"# Gap Analysis Report",
        f"**Generated:** {date_str}",
        f"**Applications analyzed:** {total}",
        f"",
        f"Gaps are ranked by importance score (frequency × domain weight).",
        f"Priority reflects how much each gap is costing you in the current pipeline.",
        f"",
        f"---",
        f"",
        f"## Ranked Gaps",
        f"",
    ]

    priority_labels = {range(0, 3): "Low", range(3, 8): "Medium", range(8, 999): "High"}

    def get_priority(score: int) -> str:
        if score >= 20:
            return "CRITICAL"
        elif score >= 10:
            return "HIGH"
        elif score >= 5:
            return "MEDIUM"
        else:
            return "LOW"

    for i, (gap, count) in enumerate(ranked, 1):
        score = score_gap(gap, count)
        priority = get_priority(score)
        sources = list(dict.fromkeys(gap_sources[gap]))[:6]  # dedupe, cap at 6
        source_str = ", ".join(sources)
        lines.append(f"### {i}. `{gap.title()}` — {priority}")
        lines.append(f"- **Appeared in:** {count}/{total} applications")
        lines.append(f"- **Companies:** {source_str}")
        lines.append(f"- **Score:** {score}")
        lines.append(f"")

    lines += [
        f"---",
        f"",
        f"## Summary by Priority",
        f"",
    ]

    critical = [g for g, c in ranked if score_gap(g, c) >= 20]
    high = [g for g, c in ranked if 10 <= score_gap(g, c) < 20]
    medium = [g for g, c in ranked if 5 <= score_gap(g, c) < 10]

    if critical:
        lines.append(f"**CRITICAL** (address immediately): {', '.join(f'`{g.title()}`' for g in critical)}")
    if high:
        lines.append(f"**HIGH** (address soon): {', '.join(f'`{g.title()}`' for g in high)}")
    if medium:
        lines.append(f"**MEDIUM** (address over time): {', '.join(f'`{g.title()}`' for g in medium)}")

    lines += [
        f"",
        f"---",
        f"",
        f"## Recommended Actions",
        f"",
        f"Based on the CRITICAL and HIGH gaps above:",
        f"",
    ]

    action_map = {
        "go": "Build a Go CLI tool or Kubernetes controller and publish to GitHub.",
        "golang": "Build a Go CLI tool or Kubernetes controller and publish to GitHub.",
        "datadog": "Instrument a sample app with Datadog APM, build monitors and SLOs on free trial.",
        "gcp": "Rebuild the AWS Cost Optimization Engine equivalent on GCP free tier.",
        "google cloud": "Rebuild the AWS Cost Optimization Engine equivalent on GCP free tier.",
        "typescript": "Build a Node.js automation script or CLI in TypeScript; publish to GitHub.",
        "5+ years": "Target mid-level (3+ year) roles — avoid Senior/Staff titles.",
        "senior": "Avoid Senior titles — they imply 5+ years and will hard-filter at ATS.",
        "data pipelines": "Build a Python security log ingestion pipeline (CloudTrail → Splunk/ELK).",
        "postgres": "Add a Postgres-backed project; document schema design and query optimization.",
        "postgresql": "Add a Postgres-backed project; document schema design and query optimization.",
        "istio": "Add Istio service mesh to a local Kubernetes cluster demo; document it.",
        "service mesh": "Add Istio service mesh to a local Kubernetes cluster demo; document it.",
        "argocd": "Set up ArgoCD on a local cluster; build a GitOps pipeline demo.",
        "helm": "Author a Helm chart for a multi-service app; publish to GitHub.",
        "oidc": "Implement an OIDC auth flow in a small Python or Go service.",
        "backstage": "Set up a local Backstage instance with a custom plugin; document it.",
    }

    added_actions = set()
    for gap, _ in ranked:
        if score_gap(gap, gap_counter[gap]) >= 10:
            action = action_map.get(gap.lower())
            if action and action not in added_actions:
                lines.append(f"- **{gap.title()}:** {action}")
                added_actions.add(action)

    report_content = "\n".join(lines)
    report_path.write_text(report_content, encoding="utf-8")
    print(f"Gap analysis written to: {report_path}")
    print(f"Applications analyzed: {total}")
    print(f"Top 3 gaps: {', '.join(g.title() for g, _ in ranked[:3])}")


if __name__ == "__main__":
    run_analysis()
