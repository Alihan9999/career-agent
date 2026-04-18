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

## Default Field Mapping
The form fields are defined in `config/google-form.md`. Typical fields:

| Form Field | Source |
|---|---|
| Company Name | job-analysis.json → company_name |
| Job Title | job-analysis.json → job_title |
| Job URL | job-analysis.json → job_url |
| Date Applied | Today's date (YYYY-MM-DD) |
| Location | job-analysis.json → location |
| Remote Policy | job-analysis.json → remote_policy |
| Salary Range | job-analysis.json → salary_range |
| ATS Score | ats-report.md → score |
| Resume File | Output folder path + /resume.md |
| Notes | Any red flags from job-analysis.json |

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
