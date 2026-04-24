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

# Canonical gap names and their importance weights.
# Add aliases in ALIASES below — do not add duplicates here.
IMPORTANCE_WEIGHTS = {
    "go":               10,   # highest ROI — blocks ~50% of roles
    "datadog":          9,
    "experience gate":  9,    # merged: "5+ years" + "senior" title filter
    "gcp":              8,    # merged: "google cloud"
    "typescript":       7,
    "rust":             6,
    "node.js":          6,
    "bare metal":       6,
    "postgres":         5,    # merged: "postgresql"
    "istio":            5,
    "service mesh":     5,
    "argocd":           5,
    "oidc":             5,
    "mtls":             5,
    "spiffe":           5,
    "spire":            5,
    "data pipelines":   5,
    "backstage":        4,
    "helm":             4,
    "kustomize":        4,
    "opentelemetry":    4,
    "tanka":            4,
    "forensics":        4,
    "saml":             4,
    "scim":             4,
    "dns":              4,
    "tls":              4,
    "networking":       4,
    "sentry":           3,
    "redis":            3,
    "opensearch":       3,    # merged: "elasticsearch"
    "load balancer":    3,
    "finops":           3,
    "cost optimization":3,
    "cmake":            2,    # role-specific (HPC/systems)
    "slurm":            2,    # role-specific (HPC)
    "workato":          2,
    "okta workflows":   2,
    "google workspace": 2,
    "zendesk":          2,
}

# Aliases — all normalized to their canonical key before counting.
# Keeps the report clean: "golang" and "go" show up as one gap, not two.
ALIASES = {
    "golang":        "go",
    "google cloud":  "gcp",
    "postgresql":    "postgres",
    "5+ years":      "experience gate",
    "senior":        "experience gate",
    "elasticsearch": "opensearch",
    "elastic":       "opensearch",
}

def normalize(gap: str) -> str:
    """Resolve aliases to their canonical name."""
    return ALIASES.get(gap.lower(), gap.lower())


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
    """Pull recognizable gap keywords from free text, normalized to canonical names."""
    tokens = []
    seen = set()
    # Check aliases first so e.g. "golang" matches before "go"
    all_keywords = list(ALIASES.keys()) + list(IMPORTANCE_WEIGHTS.keys())
    for keyword in all_keywords:
        if keyword in text.lower():
            canonical = normalize(keyword)
            if canonical not in seen:
                tokens.append(canonical)
                seen.add(canonical)
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
                canonical = normalize(token)
                if canonical not in seen_this_app:
                    gap_counter[canonical] += 1
                    gap_sources[canonical].append(company)
                    seen_this_app.add(canonical)

        # From job analysis red flags
        for flag in parse_job_analysis_gaps(job_path):
            tokens = extract_gap_tokens(flag)
            for token in tokens:
                canonical = normalize(token)
                if canonical not in seen_this_app:
                    gap_counter[canonical] += 1
                    gap_sources[canonical].append(company)
                    seen_this_app.add(canonical)

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
        "go":               "Build a Go Kubernetes operator or CLI tool and publish to GitHub.",
        "datadog":          "Instrument a sample app with Datadog APM, build monitors and SLOs on free trial.",
        "gcp":              "Rebuild the AWS Cost Optimization Engine equivalent on GCP free tier.",
        "experience gate":  "Target mid-level (3+ year) roles — avoid Senior/Staff titles in search filters.",
        "typescript":       "Build a Node.js automation script or CLI in TypeScript; publish to GitHub.",
        "rust":             "Build a Rust CLI tool (e.g. a log parser or k8s resource lister); publish to GitHub.",
        "postgres":         "Add a Postgres-backed project; document schema design and query optimization.",
        "istio":            "Add Istio service mesh to a local Kubernetes cluster demo; document it.",
        "service mesh":     "Add Istio service mesh to a local Kubernetes cluster demo; document it.",
        "argocd":           "Set up ArgoCD on a local cluster; build a GitOps pipeline demo.",
        "helm":             "Author a Helm chart for a multi-service app; publish to GitHub.",
        "oidc":             "Implement an OIDC auth flow in a small Python or Go service.",
        "backstage":        "Set up a local Backstage instance with a custom plugin; document it.",
        "opentelemetry":    "Instrument a Go or Python service with OTEL traces; ship to Datadog or Jaeger.",
        "data pipelines":   "Build a Python log ingestion pipeline (CloudTrail → Splunk/ELK).",
        "bare metal":       "Document server rack provisioning experience from the 1000+ Linux server fleet.",
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
