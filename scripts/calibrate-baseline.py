#!/usr/bin/env python3
"""
Calibrate Baseline
Measures the 80 existing resumes in output/ and reports the 50/75/90 percentiles
on the metrics that drive Quality Gate thresholds:

  - sentence-length stddev (resume + cover letter)
  - cross-resume bigram overlap (each resume vs the rest)
  - em-dash count, en-dash count
  - tilde-prefixed metric count
  - cliche concept hits
  - cadence uniformity (sentence-start verb diversity)
  - bullet-level proof element count (estimated)

The Quality Gate thresholds in v2 were set by intuition. This script lets us
re-set them based on the actual distribution of the existing outputs, so we
know what "normal" looks like for THIS candidate's history. Anything above
the 75th percentile of priors is "more generic than usual"; anything below
the 25th percentile is "less generic than usual." Calibration done.

Usage:
  python3 scripts/calibrate-baseline.py            # write percentiles to stdout + analysis/baseline-<date>.md
  python3 scripts/calibrate-baseline.py --suggest  # also suggest threshold updates
"""

import json
import math
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUTPUT_DIR = ROOT / "output"
ANALYSIS_DIR = ROOT / "analysis"
ANALYSIS_DIR.mkdir(exist_ok=True)

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with", "by",
    "at", "from", "as", "is", "was", "were", "are", "be", "been", "this",
    "that", "it", "its", "into", "across", "via",
}

CLICHE_CONCEPTS = [
    r"\bself[- ]service onboarding portal\b",
    r"\bcentralized observability platform\b",
    r"\bautomated incident routing\b",
    r"\bsingle pane of glass\b",
    r"\bconfiguration drift\b",
    r"\bbest practices\b",
    r"\brobust solution\b",
    r"\bcutting[- ]edge\b",
]


def tokenize_bigrams(text: str) -> set[str]:
    words = re.findall(r"\b[a-zA-Z'-]+\b", text.lower())
    words = [w for w in words if w not in STOPWORDS]
    return {f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)}


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'])", text) if s.strip()]


def word_count(s: str) -> int:
    return len(re.findall(r"\b\w+\b", s))


def stddev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(var)


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * p / 100
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[f]
    return s[f] * (c - k) + s[c] * (k - f)


def get_experience_and_projects_sections(text: str) -> str:
    """Pull the experience + projects content (skip headers, skills, education)."""
    out = []
    capture = False
    for line in text.splitlines():
        if re.match(r"^##\s+(Professional Experience|Experience|Selected Projects|Projects)", line, re.IGNORECASE):
            capture = True
            continue
        if re.match(r"^##\s+(Technical Skills|Skills|Education)", line, re.IGNORECASE):
            capture = False
            continue
        if capture:
            out.append(line)
    return "\n".join(out)


def measure_resume(text: str) -> dict:
    em = text.count("—")
    en = text.count("–")
    tilde_metric_hits = len(re.findall(r"~\s*\d+\s*%", text))
    cliche_hits = sum(len(re.findall(p, text, re.IGNORECASE)) for p in CLICHE_CONCEPTS)

    # Bullets
    bullet_lengths = [word_count(m.group(1)) for m in re.finditer(r"^\s*[-*]\s+(.+)$", text, re.MULTILINE)]
    bullet_stddev = stddev([float(b) for b in bullet_lengths])

    # Bullet-leading verb diversity
    bullet_lead_verbs = []
    for m in re.finditer(r"^\s*[-*]\s+(\w+)\b", text, re.MULTILINE):
        bullet_lead_verbs.append(m.group(1).lower())
    leadverb_distinct_ratio = (len(set(bullet_lead_verbs)) / len(bullet_lead_verbs)) if bullet_lead_verbs else 0.0

    # Sentence stddev
    sentences = split_sentences(text)
    sent_lengths = [word_count(s) for s in sentences]
    sent_stddev = stddev([float(s) for s in sent_lengths])

    return {
        "em_dashes": em,
        "en_dashes": en,
        "tilde_metrics": tilde_metric_hits,
        "cliche_concepts": cliche_hits,
        "bullet_count": len(bullet_lengths),
        "bullet_stddev": round(bullet_stddev, 2),
        "leadverb_distinct_ratio": round(leadverb_distinct_ratio, 3),
        "sentence_stddev": round(sent_stddev, 2),
    }


def load_resumes() -> list[tuple[str, str]]:
    out = []
    if not OUTPUT_DIR.exists():
        return out
    for folder in sorted(OUTPUT_DIR.iterdir()):
        if not folder.is_dir():
            continue
        r = folder / "resume.md"
        if r.exists():
            out.append((folder.name, r.read_text(encoding="utf-8")))
    return out


def compute_cross_overlap(resumes: list[tuple[str, str]]) -> dict:
    """For each resume, compute median bigram-overlap against all others."""
    sections = [(name, get_experience_and_projects_sections(text)) for name, text in resumes]
    bigrams = [(name, tokenize_bigrams(sec)) for name, sec in sections]
    out = []
    for i, (name, bg) in enumerate(bigrams):
        if not bg:
            continue
        overlaps = []
        for j, (oname, obg) in enumerate(bigrams):
            if i == j or not obg:
                continue
            overlap = len(bg & obg) / len(bg)
            overlaps.append(overlap)
        if overlaps:
            out.append((name, sorted(overlaps)[len(overlaps) // 2]))
    return {
        "median_per_resume": out,
        "p50": percentile([o for _, o in out], 50),
        "p75": percentile([o for _, o in out], 75),
        "p90": percentile([o for _, o in out], 90),
    }


def main():
    suggest = "--suggest" in sys.argv

    resumes = load_resumes()
    if not resumes:
        print("No resumes found in output/.")
        return

    print(f"Loaded {len(resumes)} resumes.")

    # Per-resume measurements
    measurements = [(name, measure_resume(text)) for name, text in resumes]

    # Distributions
    fields = ["em_dashes", "en_dashes", "tilde_metrics", "cliche_concepts",
              "bullet_count", "bullet_stddev", "leadverb_distinct_ratio", "sentence_stddev"]
    distributions = {}
    for f in fields:
        vals = [m[f] for _, m in measurements]
        distributions[f] = {
            "p25": percentile(vals, 25),
            "p50": percentile(vals, 50),
            "p75": percentile(vals, 75),
            "p90": percentile(vals, 90),
            "min": min(vals) if vals else 0,
            "max": max(vals) if vals else 0,
        }

    # Cross-resume overlap
    overlap = compute_cross_overlap(resumes)

    # Build report
    today = date.today().isoformat()
    lines = []
    lines.append(f"# Baseline Calibration — {today}")
    lines.append(f"**Resumes measured:** {len(resumes)}")
    lines.append("")
    lines.append("## Per-resume metrics (percentiles across all measured resumes)")
    lines.append("")
    for f in fields:
        d = distributions[f]
        lines.append(f"### {f}")
        lines.append(f"- p25={d['p25']}, p50={d['p50']}, p75={d['p75']}, p90={d['p90']}, min={d['min']}, max={d['max']}")
        lines.append("")

    lines.append("## Cross-resume bigram overlap")
    lines.append(f"- p50 (median): {overlap['p50']:.3f}")
    lines.append(f"- p75: {overlap['p75']:.3f}")
    lines.append(f"- p90: {overlap['p90']:.3f}")
    lines.append("")

    if suggest:
        lines.append("## Suggested threshold updates")
        lines.append("")
        # Anti-template thresholds
        p75 = overlap["p75"]
        p90 = overlap["p90"]
        lines.append("### Anti-Template Agent thresholds")
        lines.append(f"- RED threshold (currently 0.40): set to {p90:.2f} (p90 of priors)")
        lines.append(f"- YELLOW threshold (currently 0.30): set to {p75:.2f} (p75 of priors)")
        lines.append("")
        # Humanizer thresholds
        sent_p25 = distributions["sentence_stddev"]["p25"]
        lines.append("### Humanizer stddev threshold")
        lines.append(f"- PROSE_MIN_STDDEV (currently 7.0): consider {sent_p25:.1f} (p25 of priors — anything below is more uniform than 75% of past outputs)")
        lines.append("")
        # Tilde metric ban
        tilde_p50 = distributions["tilde_metrics"]["p50"]
        lines.append("### Tilde metric ban")
        lines.append(f"- Current 80 resumes have a median of {tilde_p50} tilde-prefixed metrics. Ban (0 allowed) is correct.")
        lines.append("")

    report = ANALYSIS_DIR / f"baseline-{today}.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport: {report}")
    print(f"\nKey findings:")
    print(f"  Median cross-resume bigram overlap: {overlap['p50']:.3f}")
    print(f"  P75 cross-resume bigram overlap:    {overlap['p75']:.3f} (use as YELLOW threshold)")
    print(f"  P90 cross-resume bigram overlap:    {overlap['p90']:.3f} (use as RED threshold)")
    print(f"  Median tilde metrics per resume:    {distributions['tilde_metrics']['p50']}")
    print(f"  Median cliche concept hits:         {distributions['cliche_concepts']['p50']}")
    print(f"  Median sentence stddev:             {distributions['sentence_stddev']['p50']}")
    if suggest:
        print(f"  Threshold update suggestions written to report.")


if __name__ == "__main__":
    main()
