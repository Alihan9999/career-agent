Import the candidate's Google Sheets application tracker into `data/applications.jsonl`.

## Usage

```
/import-sheet <PUBLIC_CSV_URL>
/import-sheet <PUBLIC_CSV_URL> --dry-run
```

## Getting the public CSV URL

1. Open the sheet in browser.
2. File -> Share -> change to "Anyone with the link" -> Viewer.
3. Copy the URL from the address bar (looks like `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit#gid=<GID>`).
4. Replace `/edit#gid=` with `/export?format=csv&gid=`.

Final URL format: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/export?format=csv&gid=<GID>`

You can also save the URL once in `config/google-sheet-url.txt` (gitignored) so `/import-sheet` with no args picks it up.

## Steps

1. Run `python3 scripts/import-google-sheet.py <URL>` (or read the URL from `config/google-sheet-url.txt` if no arg).
2. Print summary: rows read, rows appended, rows updated, rows skipped.
3. Run `python3 scripts/learning-analyzer.py` to refresh `analysis/conversions-<date>.md`, `data/blocked-companies.json`, and `data/role-family-conversion.json`.
4. Print the new conversion-rate summary.

## Status mapping

Sheet status -> applications.jsonl status:

- `Applied / Waiting` -> `pending` (or `ghosted` if >=21 days old)
- `Rejected` -> `auto_reject_slow` (refined to `auto_reject_24h` / `auto_reject_fast` by age)
- `Interviewing` -> `phone_screen`
- `Ghosted` -> `ghosted`
- `Offer` -> `offer`

If a row was previously `Interviewing` but then went silent, manually set the sheet's Status to `Ghosted` and add `(after initial response)` to the Notes column. The importer will use `responded_then_ghosted` for such rows on the next sync.

Better long-term: add a new column to the sheet called `Outcome Detail` with values like `initial_response_then_silent`, `rejected_post_screen`, etc., and we'll wire those into the importer.

## Notes

- Never use em dashes in output.
- Re-running the importer is idempotent: same-id rows are skipped, same-company+role+date rows are updated, new combinations are appended.
- The Notes column is parsed for ATS Score and Missing keywords; free-text goes into `resume_notes`.
- Tracks `data/applications.jsonl` as the source of truth. The sheet is the input.
