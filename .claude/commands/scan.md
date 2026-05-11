Scan target companies for new job openings and score each match against the candidate's profile.

## Overview

Reads `config/target-companies.yml`, fetches live job listings from each company, filters for
relevant roles, scores each against `data/skills.md`, and reports ranked opportunities the
candidate has not yet applied to.

## Argument Parsing (token budget)

By default `/scan` only checks **Tier 1** companies — the highest-priority watchlist.
This keeps token usage low when run frequently. Override via argument:

| Invocation              | Tiers scanned | Use when…                                           |
|-------------------------|---------------|-----------------------------------------------------|
| `/scan`                 | Tier 1 only   | Daily check (default)                               |
| `/scan tier 2` or `/scan 2` | Tiers 1+2     | Weekly broader sweep                                |
| `/scan tier 3` or `/scan 3` | Tiers 1+2+3   | Full watchlist (most expensive)                     |
| `/scan all`             | All tiers     | Same as `tier 3`                                    |
| `/scan <CompanyName>`   | One company   | Quick targeted check                                |

If `config/target-companies.yml` defines `scan_tier_limit: N` at the top level, that
becomes the default (overrides Tier-1 default but is still overridden by an explicit
argument).

## Steps

### Step 1 — Load watchlist and candidate profile
- Read `config/target-companies.yml` (if it does not exist, tell the user to copy `config/target-companies.example.yml` and fill it in)
- Read `data/skills.md` — the candidate's full skill inventory used for scoring
- Read `output/` folder names to build an already-applied list (skip companies/roles already applied to)
- **Filter the watchlist by tier per the argument-parsing table above before doing anything else.** Print a one-line note: `Scanning N companies (tier <=K)`. This is the budget gate — every dropped company is one less spider call.

### Step 2 — Fetch job listings per company

For each company, call the unified scraper:

```
python3 scripts/scrape.py board <ats> <ats_id> --json
```

Supported `<ats>` values: `greenhouse`, `lever`, `ashby`, `workable`, `workday`,
`linkedin`, `indeed`, `wellfound`, `builtin`, `custom`. Each spider knows the
right URL pattern and rendering strategy:

- **greenhouse / lever / builtin** — public JSON or server-rendered HTML, no auth.
- **ashby / wellfound** — JS-rendered, uses Playwright via Scrapling's DynamicFetcher.
- **workable** — JSON endpoint first, stealth HTML fallback.
- **workday** — POST to the tenant's `wday/cxs` JSON endpoint with stealth.
- **linkedin / indeed** — Cloudflare-aware StealthyFetcher with Chrome impersonation.
- **custom** — pass `--url <careers_url>`. Auto-escalates from plain HTTP to
  DynamicFetcher to StealthyFetcher as needed.

Each spider returns a JSON array of `{title, url, location, department, posted, source}`
records. Parse the JSON and feed it into Step 3.

If `scripts/scrape.py` is unavailable (e.g. Scrapling not yet installed), fall back
to plain WebFetch on the careers URL and note the degraded mode in the report.

If a company's career page is inaccessible, note it and continue — do not block the scan.

### Step 3 — Filter results

For each job fetched:
- **Include filter**: title must contain at least one `filters.include_keywords` term (case-insensitive)
- **Exclude filter**: skip if title contains any `filters.exclude_keywords` term
- **Already applied**: skip if an `output/` folder already exists for this company (fuzzy match on company name)
- **Location filter** (if `filters.remote_only: true` and `filters.location: US`): skip if the job location contains a non-US country name (UK, Portugal, Germany, Singapore, India, Canada, etc.), a non-US city, or is explicitly listed as "On-site" or "Hybrid" without a US location. Keep if: location says "Remote", "Remote US", "United States", contains a US city/state, or lists a timezone range that covers US hours (e.g., UTC-8 to UTC-4). If location is ambiguous, fetch the job page to confirm before excluding.

### Step 4 — Score each match

Score each passing job on a 0-100 scale across four dimensions:

**Role fit (35 points)**
- 35: Exact match (SRE, Platform Engineer, Infrastructure Engineer, DevOps)
- 20: Adjacent match (Cloud Engineer, Production Engineer, Security Engineer)
- 10: Stretch (Solutions Engineer, Technical Program Manager with infra focus)
- 0: Wrong role type

**Keyword overlap (40 points)**
Compare the job title and any visible description text against `data/skills.md`.
Count how many of the candidate's proficient/expert skills are implied by the role.
- 40: 8+ skill matches
- 30: 5-7 matches
- 20: 3-4 matches
- 10: 1-2 matches
- 0: No matches

**Level fit (15 points)**
- 15: Mid-level, no year count, 2-3 years, or 3+ years
- 10: Senior with explicit 3-4 year count, or 4+ years flagged
- 0: Staff, Principal, 5+ years, or Senior with no year count (hard skip — do not include at all)

**Legitimacy signals (10 points)**
- 10: Posted recently (under 30 days), clear apply button, specific title
- 5: Posting age unknown or 30-60 days, generic role
- 0: No date, vague, or aggregator-only

**Confidence tier:**
- 85-100: STRONG MATCH — run pipeline immediately
- 70-84: GOOD MATCH — worth applying
- 60-69: POSSIBLE — apply if volume allows
- Below 60: filtered out (below `min_score` threshold)

### Step 5 — Report results

Print a ranked summary to the conversation:

```
Scan complete: [date] | [N] companies checked | [M] new matches found

STRONG MATCH (85+)
------------------
[Score] Company | Role Title | Location
        URL: [job url]
        Why: [2-line explanation of top matching skills]

GOOD MATCH (70-84)
------------------
[Score] Company | Role Title | Location
        URL: [job url]
        Why: [2-line explanation]

POSSIBLE (60-69)
----------------
[Score] Company | Role Title | Location
        URL: [job url]

Companies with no relevant openings: [list]
Companies with access errors: [list]
```

Save the full report to `scans/scan-<YYYY-MM-DD>/report.md`.

After printing, ask the user: "Want me to run the pipeline on any of these?"
If they say yes to one or more, run the standard application pipeline for each confirmed role.

## Notes
- Never use em dashes in output — use pipes and commas
- Staff/Principal/5+ year roles are excluded entirely, not just scored low
- If `config/target-companies.yml` does not exist, show the user the example and stop
- The scan is read-only — it never auto-applies without explicit user confirmation
