Run the application pipeline on a list of job URLs in one go.

## Overview

Default mode: for each URL, fetch + analyze + apply pre-flight gates + score, then show a table and ask which to pipeline. This keeps token cost predictable when you paste 30 URLs.

`--yolo` mode: skip the confirmation, run the full pipeline on every URL that passes the gates.

## Argument Parsing

`/bulk-apply` accepts either inline URLs or a file path:

| Invocation                              | Behavior                                           |
|-----------------------------------------|----------------------------------------------------|
| `/bulk-apply <url1> <url2> ...`         | Run on the listed URLs                             |
| `/bulk-apply <url1> <url2> --yolo`      | Same, skip confirmation                            |
| `/bulk-apply inputs/jobs.txt`           | Read URLs from file (one per line, # for comments) |
| `/bulk-apply inputs/jobs.txt --yolo`    | Read file, skip confirmation                       |
| `/bulk-apply` (no args)                 | Prompt the user to paste URLs on the next line     |

**Auto-detect rule:** if the first non-flag argument starts with `http://` or `https://`, treat all non-flag args as URLs. Otherwise treat it as a file path.

## Steps

### Step 1 — Collect URLs
- Parse args per the table above.
- If reading a file: open it, skip blank lines and lines starting with `#`, strip trailing whitespace and inline `# comments`.
- Deduplicate URLs (exact-match) and print the final count: `Collected N URLs (X duplicates dropped)`.
- Cross-check against `output/` folder names — if a URL maps to an already-applied company within the last 90 days, mark it `ALREADY_APPLIED` and exclude from processing (still show in the table).

### Step 2 — Analyze and gate (cheap pass)

For each remaining URL, run the **Job Analyzer** subagent only. Skip the full pipeline. Capture:
- `company_name`
- `job_title`
- `salary_range`
- `experience_gate` (HARD_SKIP / FLAG / PROCEED — already set by job-analyzer)
- `legitimacy.tier` (HIGH_CONFIDENCE / PROCEED_WITH_CAUTION / SUSPICIOUS)
- `ats_platform`

If a fetch fails, record the error and continue — do NOT halt the batch on a single failure.

Compute a quick fit score using the **same 0-100 rubric as /scan** (role fit 35, keyword overlap 40, level fit 15, legitimacy 10). The score lives in conversation memory; do not write a `job-analysis.json` for URLs the user hasn't approved yet — only write JSON for URLs that go through the full pipeline in Step 4.

### Step 3 — Report and confirm

Print a numbered table. Sort by score descending; group HARD_SKIP and ALREADY_APPLIED at the bottom.

```
Bulk apply: N URLs analyzed | M passed pre-flight gates | K already applied | F fetch failures

| # | Company       | Role                          | Score | Gate    | ATS       | Notes                          |
|---|---------------|-------------------------------|-------|---------|-----------|--------------------------------|
| 1 | Stripe        | Site Reliability Engineer     | 92    | PROCEED | greenhouse| strong match                   |
| 2 | Cloudflare    | Platform Engineer             | 87    | PROCEED | greenhouse|                                |
| 3 | Datadog       | Infrastructure Engineer       | 81    | PROCEED | greenhouse|                                |
| 4 | Anthropic     | DevOps Engineer               | 78    | PROCEED | greenhouse|                                |
| 5 | Random Co     | Senior SRE                    | --    | SKIP    | --        | 5+ years required              |
| 6 | Stripe        | Production Engineer           | --    | SKIP    | --        | already applied 2026-04-22     |
| 7 | (fetch fail)  | --                            | --    | ERROR   | --        | HTTP 403 / login required      |
```

**Default mode:** Ask the user which to pipeline:
> Run pipeline on which? (e.g. `1,3,4` | `all` | `top 5` | `none`)

**`--yolo` mode:** Skip the prompt. Run the pipeline on every URL with score >= 60 and gate == PROCEED. Print `Pipelining N URLs (yolo mode)` and continue.

### Step 4 — Pipeline run

For each confirmed URL, run the standard application pipeline by invoking the **Orchestrator** subagent. The orchestrator handles everything from `job-analyzer.json` write through Form Filler.

Run pipelines **sequentially**, not in parallel. Each pipeline takes 30-90s; serializing keeps tool-call rate sensible and avoids two simultaneous writes to the same Google Form session.

Between each pipeline, print a one-line progress note:
```
[3/7] Pipelining Datadog | Infrastructure Engineer ...
```

If a single pipeline fails (e.g., the page is now 404, the form submit errors), record the error and continue with the next URL — do not abort the batch.

### Step 5 — Final report

After all pipelines finish, print a summary:
```
Bulk apply complete: 4 succeeded | 0 partial | 1 failed | 2 skipped by user

Succeeded:
  output/Stripe-2026-05-11/      | ATS 87% | Form submitted
  output/Cloudflare-2026-05-11/  | ATS 91% | Form submitted
  output/Datadog-2026-05-11/     | ATS 84% | Form submitted
  output/Anthropic-2026-05-11/   | ATS 88% | Form submitted

Failed:
  https://example.com/jobs/123   | Pipeline aborted at ATS Optimizer: keyword score 42%

Skipped by user: 2
```

Save the full report to `analysis/bulk-apply-<YYYY-MM-DD-HHMM>.md` so the user can audit later.

## Notes
- Never use em dashes in output — use pipes and commas.
- The cheap pass in Step 2 still costs tokens (one job-analyzer per URL); don't paste 200 URLs without checking your budget first.
- `--yolo` mode threshold is **score >= 60 AND gate == PROCEED**. Hard-skip and suspicious-legitimacy listings are never auto-pipelined.
- Already-applied dedup is fuzzy on company name (case-insensitive, ignores spaces and punctuation). If you genuinely want to reapply within 90 days, delete the existing `output/<Company>-<date>/` folder first.
- If you provide a file path that doesn't exist, error out clearly and show the expected format (`one URL per line, # for comments`).
