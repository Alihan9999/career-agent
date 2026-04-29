Scan target companies for new job openings and score each match against the candidate's profile.

## Overview

Reads `config/target-companies.yml`, fetches live job listings from each company, filters for
relevant roles, scores each against `data/skills.md`, and reports ranked opportunities the
candidate has not yet applied to.

## Steps

### Step 1 — Load watchlist and candidate profile
- Read `config/target-companies.yml` (if it does not exist, tell the user to copy `config/target-companies.example.yml` and fill it in)
- Read `data/skills.md` — the candidate's full skill inventory used for scoring
- Read `output/` folder names to build an already-applied list (skip companies/roles already applied to)

### Step 2 — Fetch job listings per company

For each company in the watchlist, use the following strategy in order:

**Greenhouse ATS** (`ats: greenhouse`):
Fetch: `https://boards-api.greenhouse.io/v1/boards/{ats_id}/jobs`
Parse the `jobs` array. Each job has `title`, `absolute_url`, `location`.

**Lever ATS** (`ats: lever`):
Fetch: `https://api.lever.co/v0/postings/{ats_id}?mode=json`
Parse the JSON array. Each posting has `text` (title), `hostedUrl`, `categories.location`.

**Ashby ATS** (`ats: ashby`):
First try WebFetch on `https://jobs.ashbyhq.com/{ats_id}`.
If the page returns only a bare "Jobs" heading with no listings (Ashby renders listings via JavaScript), fall back to WebSearch: `{company name} careers site:jobs.ashbyhq.com OR site:ashbyhq.com DevOps OR SRE OR "Platform Engineer" OR "Infrastructure Engineer"`
Parse job titles and links from the search results.

**Workable** (`ats: workable`):
Fetch: `https://apply.workable.com/{ats_id}` via WebFetch.
Parse job listings from the HTML.

**Custom** (`ats: custom`):
Use WebSearch: `site:{careers_url domain} {include_keywords joined by OR}`
Take the top 10 results and extract job titles and URLs.

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
