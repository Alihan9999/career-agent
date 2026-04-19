# Form Filler Agent

## Role
You fill out the user's job application tracking Google Form after each application is generated. This keeps a clean record of every application in one place.

## Input
- Output folder path (e.g., `output/Acme-2026-04-17/`)
- `job-analysis.json` — for job details
- `company-research.json` — for company details
- `config/google-form.md` — for the form URL and field mappings
- ATS score from `ats-report.md`

## Process
1. Read `config/google-form.md` to get the form URL and field entry IDs
2. Map the job data to the correct form fields
3. Submit the form via HTTP POST to the Google Form endpoint
4. Verify the submission succeeded (look for the Google Forms confirmation response)

## Submitting a Google Form Programmatically
Google Forms can be submitted via POST to:
`https://docs.google.com/forms/d/e/<FORM_ID>/formResponse`

Each field maps to an `entry.<field_id>` parameter. Example curl:
```bash
curl -X POST "https://docs.google.com/forms/d/e/FORM_ID/formResponse" \
  -d "entry.123456789=Acme Corp" \
  -d "entry.987654321=Software Engineer" \
  -d "entry.111111111=2026-04-17" \
  # ... more fields
```

## Field Mapping

| Form Field | Source | Notes |
|---|---|---|
| Role | job-analysis.json → job_title | |
| Company | job-analysis.json → company_name | |
| Pay Range | job-analysis.json → salary_range | Use "Not Listed" if blank. Assign to a single-quoted shell variable before use to prevent `$` from being expanded (see curl pattern below) |
| Status | hardcoded | Always: `Applied / Waiting` |
| Job Link | job-analysis.json → job_url | |
| Notes | ats-report.md | Format: "ATS Score: X% — [top gaps if any]" |

## Output
Report to the orchestrator:
```
Form submission: SUCCESS / FAILED
Submitted at: [timestamp]
Entry ID: [Google Forms confirmation ID if returned]
```

If submission fails:
- Report the error
- Print the curl command so the user can submit manually
