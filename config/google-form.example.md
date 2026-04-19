# Google Form — Job Application Tracker
# Copy this file to config/google-form.md and fill in your real values.
# config/google-form.md is gitignored — never commit your real form URL.

## Submission URL
```
https://docs.google.com/forms/d/e/YOUR_FORM_ID_HERE/formResponse
```

## Field Entry IDs
To find your entry IDs: open your form, click the 3-dot menu → "Get pre-filled link",
fill every field with a dummy value, copy the URL, and extract the `entry.XXXXXXXXX` parameters.

| Field | Entry ID | Source |
|---|---|---|
| Role | entry.XXXXXXXXX | job-analysis.json → job_title |
| Company | entry.XXXXXXXXX | job-analysis.json → company_name |
| Pay Range | entry.XXXXXXXXX | job-analysis.json → salary_range (use "Not Listed" if blank) |
| Status | entry.XXXXXXXXX | Always hardcoded: `Applied / Waiting` |
| Job Link | entry.XXXXXXXXX | job-analysis.json → job_url |
| Notes | entry.XXXXXXXXX | "ATS Score: X% — [key gaps if any]" |

## Submit Command (used by form-filler agent)

Always assign dynamic values to single-quoted shell variables FIRST to prevent `$` signs
in salary ranges from being interpreted as bash variables:

```bash
pay_range='$82,200 - $168,200 + equity'
notes='ATS Score: 83% — Missing: Golang'

curl -s -o /dev/null -w "%{http_code}" -X POST \
  "https://docs.google.com/forms/d/e/YOUR_FORM_ID_HERE/formResponse" \
  --data-urlencode "entry.XXXXXXXXX=ROLE" \
  --data-urlencode "entry.XXXXXXXXX=COMPANY" \
  --data-urlencode "entry.XXXXXXXXX=$pay_range" \
  --data-urlencode "entry.XXXXXXXXX=Applied / Waiting" \
  --data-urlencode "entry.XXXXXXXXX=JOB_LINK" \
  --data-urlencode "entry.XXXXXXXXX=$notes"
```
A response of `0` or `200` means success. Google Forms redirects on success so any 2xx/3xx is a pass.
