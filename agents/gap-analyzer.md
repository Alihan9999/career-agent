# Gap Analyzer Agent

## Role
Scan all job application output folders, aggregate recurring skill and keyword gaps,
rank them by importance, and write a report to `/output/gap-analysis-<date>.md`.

This agent runs silently — no output to the user unless they ask for it.
It requires at least 30 applications before it runs.

## When to Invoke
- When the user explicitly says "run gap analysis" or "check my gaps"
- Do NOT run automatically after every application

## How to Run

```bash
python scripts/gap-analysis.py
```

## What It Does
1. Reads every `output/*/ats-report.md` — extracts missing keywords
2. Reads every `output/*/job-analysis.json` — extracts red_flags
3. Counts how many applications each gap appeared in
4. Scores gaps by frequency × domain importance weight
5. Writes a ranked report to `output/gap-analysis-<date>.md`

## Output
Report saved to `output/gap-analysis-YYYY-MM-DD.md` with:
- Ranked gap list with CRITICAL / HIGH / MEDIUM / LOW priority
- Companies each gap appeared in
- Recommended actions for top gaps

## Priority Scoring
- Score = frequency × importance_weight
- CRITICAL: score ≥ 20
- HIGH: score ≥ 10
- MEDIUM: score ≥ 5
- LOW: score < 5

Importance weights favor gaps that block the most roles (Go, Datadog, GCP)
over gaps that are role-specific (Slurm, Tanka, Workato).

## Notes
- Gaps appearing in only 1 application are filtered out (noise)
- Report is written to file, not printed to conversation
- Run again after every ~10 new applications for updated signal
