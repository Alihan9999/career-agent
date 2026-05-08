#!/usr/bin/env python3
"""
Humanize Metrics
Reports AI-tell signals on a markdown file (resume or cover letter):
sentence-length stddev (burstiness proxy), top bigrams, em/en-dash counts,
cliche regex hits, fragment ratio, average sentence length per paragraph.

The humanizer agent runs this as a self-check between rewrite passes.
Stdlib-only. Usage: python3 scripts/humanize-metrics.py <file.md>
Exit code 0 if all thresholds pass, 1 if any fail.
"""

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

CLICHE_PATTERNS = [
    r"\bpassionate about\b",
    r"\bproven track record\b",
    r"\bteam player\b",
    r"\bresults[- ]driven\b",
    r"\bsynerg(y|ies|ize)\b",
    r"\bleverag(e|ing|ed)\b",
    r"\bdelv(e|ing|ed) into\b",
    r"\bin today'?s fast[- ]paced\b",
    r"\bI am writing to\b",
    r"\bI would welcome the opportunity\b",
    r"\bmaps directly\b",
    r"\bmaps closely\b",
    r"\brobust solution\b",
    r"\bdynamic environment\b",
    r"\bcutting[- ]edge\b",
    r"\bworld[- ]class\b",
    r"\bbest[- ]in[- ]class\b",
    r"\bdeep dive\b",
    r"\bgame[- ]changer\b",
    r"\bthought leader\b",
    r"\b(hit|hitting) the ground running\b",
]

# Burstiness thresholds for prose paragraphs (cover letter).
# Resume bullets are evaluated separately with looser rules.
PROSE_MIN_STDDEV = 7.0
PROSE_MIN_SHORT_PER_PARA = 1   # sentences <= 12 words
PROSE_MIN_LONG_PER_PARA = 1    # sentences >= 22 words

SHORT_SENTENCE_WORDS = 12
LONG_SENTENCE_WORDS = 22


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'])", text)
    return [p.strip() for p in parts if p.strip()]


def word_count(s: str) -> int:
    return len(re.findall(r"\b\w+\b", s))


def stddev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(var)


def is_resume(path: Path, text: str) -> bool:
    name = path.name.lower()
    if "resume" in name:
        return True
    if "cover" in name or "letter" in name:
        return False
    # Heuristic: lots of bullet lines suggests a resume.
    bullet_lines = sum(1 for line in text.splitlines() if re.match(r"^\s*[-*]\s+", line))
    total_lines = max(1, len([l for l in text.splitlines() if l.strip()]))
    return bullet_lines / total_lines > 0.4


def get_paragraphs(text: str) -> list[str]:
    """Split prose into paragraphs (blank-line separated). Skip headings, lists, fences."""
    paragraphs = []
    buf = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if not stripped:
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            continue
        if stripped.startswith("#"):
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            continue
        if re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            continue
        buf.append(stripped)
    if buf:
        paragraphs.append(" ".join(buf))
    return paragraphs


def get_bullets(text: str) -> list[str]:
    bullets = []
    for line in text.splitlines():
        m = re.match(r"^\s*[-*]\s+(.+)$", line)
        if m:
            bullets.append(m.group(1).strip())
    return bullets


def find_cliches(text: str) -> list[tuple[str, int]]:
    hits = []
    for pat in CLICHE_PATTERNS:
        matches = re.findall(pat, text, flags=re.IGNORECASE)
        if matches:
            hits.append((pat, len(matches)))
    return hits


def top_bigrams(text: str, n: int = 10) -> list[tuple[str, int]]:
    words = re.findall(r"\b[a-zA-Z']+\b", text.lower())
    if len(words) < 2:
        return []
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]
    counter = Counter(bigrams)
    return [(bg, c) for bg, c in counter.most_common(n) if c > 1]


def count_dashes(text: str) -> tuple[int, int]:
    em = len(re.findall(r"—", text))
    en = len(re.findall(r"–", text))
    return em, en


def analyze_prose(paragraphs: list[str]) -> dict:
    para_stats = []
    all_sentences = []
    for para in paragraphs:
        sentences = split_sentences(para)
        if not sentences:
            continue
        lengths = [word_count(s) for s in sentences]
        para_stats.append({
            "sentence_count": len(sentences),
            "avg_words": round(sum(lengths) / len(lengths), 1),
            "stddev": round(stddev(lengths), 2),
            "short_count": sum(1 for l in lengths if l <= SHORT_SENTENCE_WORDS),
            "long_count": sum(1 for l in lengths if l >= LONG_SENTENCE_WORDS),
            "lengths": lengths,
        })
        all_sentences.extend(lengths)
    overall_stddev = round(stddev(all_sentences), 2) if all_sentences else 0.0
    fragments = sum(1 for l in all_sentences if l <= 6)
    return {
        "paragraph_count": len(para_stats),
        "sentence_count": len(all_sentences),
        "overall_stddev": overall_stddev,
        "fragment_count": fragments,
        "fragment_ratio": round(fragments / max(1, len(all_sentences)), 3),
        "paragraphs": para_stats,
    }


def evaluate_thresholds(report: dict, doc_kind: str) -> list[str]:
    failures = []
    if doc_kind == "cover-letter":
        prose = report["prose"]
        if prose["overall_stddev"] < PROSE_MIN_STDDEV:
            failures.append(
                f"burstiness too low: stddev={prose['overall_stddev']} (need >= {PROSE_MIN_STDDEV})"
            )
        for i, p in enumerate(prose["paragraphs"], 1):
            if p["short_count"] < PROSE_MIN_SHORT_PER_PARA:
                failures.append(f"paragraph {i}: missing a short sentence (<= {SHORT_SENTENCE_WORDS} words)")
            if p["long_count"] < PROSE_MIN_LONG_PER_PARA:
                failures.append(f"paragraph {i}: missing a long sentence (>= {LONG_SENTENCE_WORDS} words)")
    if report["em_dash_count"] > 0:
        failures.append(f"em-dash hits: {report['em_dash_count']} (must be 0)")
    if doc_kind == "cover-letter" and report["en_dash_count"] > 0:
        failures.append(f"en-dash in prose: {report['en_dash_count']} (must be 0 in cover letter)")
    if report["cliche_hits"]:
        for pat, count in report["cliche_hits"]:
            failures.append(f"cliche match: /{pat}/ x{count}")
    return failures


def build_report(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    doc_kind = "resume" if is_resume(path, text) else "cover-letter"
    paragraphs = get_paragraphs(text)
    bullets = get_bullets(text)
    em, en = count_dashes(text)
    report = {
        "file": str(path),
        "doc_kind": doc_kind,
        "em_dash_count": em,
        "en_dash_count": en,
        "cliche_hits": find_cliches(text),
        "top_bigrams": top_bigrams(text, n=15),
        "bullet_count": len(bullets),
        "prose": analyze_prose(paragraphs),
    }
    if bullets:
        bullet_lengths = [word_count(b) for b in bullets]
        report["bullet_stats"] = {
            "count": len(bullets),
            "avg_words": round(sum(bullet_lengths) / len(bullet_lengths), 1),
            "stddev": round(stddev(bullet_lengths), 2),
            "min": min(bullet_lengths),
            "max": max(bullet_lengths),
        }
    failures = evaluate_thresholds(report, doc_kind)
    report["failures"] = failures
    report["passed"] = len(failures) == 0
    return report


def format_human(report: dict) -> str:
    lines = []
    lines.append(f"# Humanize Metrics")
    lines.append(f"**File:** {report['file']}")
    lines.append(f"**Type:** {report['doc_kind']}")
    lines.append(f"**Status:** {'PASS' if report['passed'] else 'FAIL'}")
    lines.append("")
    lines.append("## Punctuation")
    lines.append(f"- em-dashes: {report['em_dash_count']}")
    lines.append(f"- en-dashes: {report['en_dash_count']}")
    lines.append("")
    prose = report["prose"]
    lines.append("## Prose Burstiness")
    lines.append(f"- paragraphs: {prose['paragraph_count']}")
    lines.append(f"- sentences: {prose['sentence_count']}")
    lines.append(f"- overall stddev: {prose['overall_stddev']} (target >= {PROSE_MIN_STDDEV} for cover letters)")
    lines.append(f"- fragments (<=6 words): {prose['fragment_count']}")
    for i, p in enumerate(prose["paragraphs"], 1):
        lines.append(f"  - para {i}: {p['sentence_count']} sentences, avg {p['avg_words']}w, stddev {p['stddev']}, short={p['short_count']}, long={p['long_count']}")
        lines.append(f"    lengths: {p['lengths']}")
    lines.append("")
    if "bullet_stats" in report:
        b = report["bullet_stats"]
        lines.append("## Resume Bullets")
        lines.append(f"- count: {b['count']}, avg {b['avg_words']}w, stddev {b['stddev']}, range {b['min']}-{b['max']}")
        lines.append("")
    lines.append("## Cliche Hits")
    if report["cliche_hits"]:
        for pat, count in report["cliche_hits"]:
            lines.append(f"- /{pat}/ x{count}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Top Repeated Bigrams")
    if report["top_bigrams"]:
        for bg, count in report["top_bigrams"]:
            lines.append(f"- \"{bg}\" x{count}")
    else:
        lines.append("- none repeated")
    lines.append("")
    lines.append("## Failures")
    if report["failures"]:
        for f in report["failures"]:
            lines.append(f"- {f}")
    else:
        lines.append("- none")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/humanize-metrics.py <file.md> [--json]", file=sys.stderr)
        sys.exit(2)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)
    as_json = "--json" in sys.argv[2:]
    report = build_report(path)
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print(format_human(report))
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
