# Google Form Configuration

## Setup Instructions
1. Create a Google Form with the fields listed below
2. Get the form's submission URL:
   - Open the form, click the three dots → "Get pre-filled link"
   - Fill in dummy values and click "Get link"
   - The URL will show `entry.XXXXXXXXX` IDs for each field
3. Fill in the FORM_ID and entry IDs below

## Form Submission URL
```
https://docs.google.com/forms/d/e/YOUR_FORM_ID_HERE/formResponse
```

## Field Mappings
Replace `entry.XXXXXXXXX` with the actual entry IDs from your form.

```
Company Name:      entry.XXXXXXXXX
Job Title:         entry.XXXXXXXXX
Job URL:           entry.XXXXXXXXX
Date Applied:      entry.XXXXXXXXX
Location:          entry.XXXXXXXXX
Remote Policy:     entry.XXXXXXXXX   (remote / hybrid / on-site)
Salary Range:      entry.XXXXXXXXX
Employment Type:   entry.XXXXXXXXX   (full-time / contract)
ATS Score:         entry.XXXXXXXXX   (percentage)
Application Status:entry.XXXXXXXXX   (Applied / Interview / Offer / Rejected)
Notes:             entry.XXXXXXXXX
Resume Path:       entry.XXXXXXXXX
```

## Recommended Google Form Fields
Set these up in your form before filling in the entry IDs above:

1. **Company Name** (Short answer)
2. **Job Title** (Short answer)
3. **Job URL** (Short answer)
4. **Date Applied** (Date or Short answer)
5. **Location** (Short answer)
6. **Remote Policy** (Multiple choice: Remote / Hybrid / On-site)
7. **Salary Range** (Short answer)
8. **Employment Type** (Multiple choice: Full-time / Contract / Part-time)
9. **ATS Score %** (Short answer)
10. **Application Status** (Multiple choice: Applied / Phone Screen / Interview / Offer / Rejected / Ghosted)
11. **Notes / Red Flags** (Paragraph)
12. **Resume File Path** (Short answer)

## Testing
After filling in the config, test with:
```bash
curl -X POST "https://docs.google.com/forms/d/e/YOUR_FORM_ID/formResponse" \
  -d "entry.XXXXXXXXX=Test Company" \
  -d "entry.XXXXXXXXX=Test Engineer"
```
A successful submission returns an HTML page — the form filler agent checks for "freebirdFormviewerViewResponseConfirmationMessage" in the response.
