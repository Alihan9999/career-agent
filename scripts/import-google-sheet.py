#!/usr/bin/env python3
"""
Import Google Sheet
Fetches the candidate's Google Sheets application tracker (must be set to
'Anyone with the link can view') and merges rows into data/applications.jsonl.

The sheet schema (matching the user's current sheet):
  Timestamp | Role | Company | Pay Range | Status | Job Link | Notes

Status mapping (sheet -> applications.jsonl):
  Applied / Waiting           -> pending  (or ghosted if >21d old)
  Rejected                    -> auto_reject_slow  (default; refined by age)
  Interviewing                -> phone_screen
  Ghosted                     -> ghosted
  Interviewing -> Ghosted     -> responded_then_ghosted (when Notes flag it)
  Offer                       -> offer

Notes column is parsed for:
  - ATS Score (e.g., 'ATS Score: 84%' -> scores.ats_score)
  - Missing keywords (e.g., 'Missing: GCP, Backstage' -> gaps_missing_genuine)
  - Free-text context (kept in resume_notes)

Usage:
  python3 scripts/import-google-sheet.py <PUBLIC_CSV_URL>
  python3 scripts/import-google-sheet.py <PUBLIC_CSV_URL> --dry-run

Public CSV URL format:
  https://docs.google.com/spreadsheets/d/<SHEET_ID>/export?format=csv&gid=<GID>

To get this URL:
  1. Open the sheet in browser
  2. File -> Share -> 'Anyone with the link' -> Viewer
  3. Copy the URL bar (looks like .../spreadsheets/d/<SHEET_ID>/edit#gid=<GID>)
  4. Replace '/edit#gid=' with '/export?format=csv&gid='
"""

import csv
import io
import json
import re
import sys
import urllib.request
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).parent.parent
APPS_PATH = ROOT / "data" / "applications.jsonl"

STATUS_MAP = {
    "applied / waiting": None,  # decided dynamically by age
    "applied/waiting": None,
    "applied": None,
    "waiting": None,
    "rejected": "auto_reject_slow",
    "ghosted": "ghosted",
    "interviewing": "phone_screen",
    "interview": "phone_screen",
    "phone screen": "phone_screen",
    "screen": "phone_screen",
    "offer": "offer",
    "withdrew": "withdrew",
    "withdrawn": "withdrew",
    "passed": "auto_reject_slow",  # candidate rejected role
}


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def parse_timestamp(ts: str) -> date | None:
    if not ts:
        return None
    # Try common Google Forms timestamp formats
    for fmt in ("%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(ts.strip(), fmt).date()
        except ValueError:
            continue
    return None


def categorize_role_family(title: str) -> str:
    t = title.lower()
    if "site reliability" in t or " sre" in t or t.startswith("sre"):
        return "SRE"
    if "platform engineer" in t or "platform" in t:
        return "Platform Engineer"
    if "infrastructure engineer" in t or "infra eng" in t or "infrastructure & reliability" in t:
        return "Infrastructure Engineer"
    if "devops" in t:
        return "DevOps Engineer"
    if "cloud" in t:
        return "Cloud Engineer"
    if "security" in t or "observability" in t and "security" in t:
        return "Security Engineer"
    if "production engineer" in t:
        return "Production Engineer"
    if "reliability" in t:
        return "Reliability Engineer"
    return "Other"


def parse_notes(notes: str) -> dict:
    """Extract ATS score, missing keywords, and free-text from the Notes column."""
    result = {
        "ats_score": None,
        "gaps_missing_genuine": [],
        "free_text": notes.strip() if notes else "",
    }
    if not notes:
        return result

    # ATS Score: 84%
    m = re.search(r"ATS\s+Score:\s*(\d+)\s*%", notes, re.IGNORECASE)
    if m:
        result["ats_score"] = int(m.group(1))

    # Missing: GCP, Backstage  /  Missing: ...
    m = re.search(r"Missing:\s*([^.|\n]+?)(?:\.|$|\||—| --)", notes, re.IGNORECASE)
    if m:
        raw = m.group(1).strip()
        # Strip parenthetical clarifications then split
        items = [it.strip() for it in re.split(r"[,;/]", raw) if it.strip()]
        # Drop very long fragments (likely sentences, not keywords)
        items = [it for it in items if len(it) <= 40 and not it.startswith("(")]
        result["gaps_missing_genuine"] = items

    return result


def parse_pay_range(pay: str) -> str:
    return pay.strip() if pay else "Not Listed"


def parse_job_link(link: str) -> tuple[str, str]:
    """Return (url, ats_platform_guess)."""
    if not link:
        return "", "unknown"
    url = link.strip()
    ats = "unknown"
    low = url.lower()
    if "greenhouse.io" in low or "boards.greenhouse.io" in low or "job-boards.greenhouse.io" in low:
        ats = "greenhouse"
    elif "lever.co" in low:
        ats = "lever"
    elif "ashbyhq.com" in low:
        ats = "ashby"
    elif "myworkdayjobs.com" in low or "wd1.myworkdaysite.com" in low or "wd5.myworkdaysite.com" in low:
        ats = "workday"
    elif "workable.com" in low:
        ats = "workable"
    elif "icims.com" in low:
        ats = "icims"
    elif "taleo.net" in low:
        ats = "taleo"
    elif "linkedin.com/jobs" in low:
        ats = "linkedin"
    elif "indeed.com" in low:
        ats = "indeed"
    elif "wellfound.com" in low:
        ats = "wellfound"
    elif "builtin" in low and "job" in low:
        ats = "builtin"
    else:
        ats = "custom"
    return url, ats


def fuzzy_company_match(company: str, existing_rows: list[dict]) -> dict | None:
    norm = re.sub(r"[^a-z0-9]", "", company.lower())
    if not norm:
        return None
    candidates = []
    for r in existing_rows:
        co = r.get("company", "")
        co_norm = re.sub(r"[^a-z0-9]", "", co.lower())
        if not co_norm:
            continue
        if norm == co_norm or norm in co_norm or co_norm in norm:
            candidates.append(r)
    if not candidates:
        return None
    # Prefer most recent
    candidates.sort(key=lambda r: r.get("date_applied", ""), reverse=True)
    return candidates[0]


def derive_status(sheet_status: str, date_applied: date | None, today: date) -> tuple[str, int | None]:
    """Map sheet status + age to applications.jsonl status. Returns (status, ttr_days)."""
    s = (sheet_status or "").strip().lower()
    mapped = STATUS_MAP.get(s)
    ttr = None
    if date_applied:
        ttr = (today - date_applied).days

    if mapped is None:  # Applied/Waiting
        if ttr is not None and ttr >= 21:
            return "ghosted", ttr
        return "pending", ttr

    if mapped == "auto_reject_slow" and ttr is not None:
        if ttr < 1:
            return "auto_reject_24h", ttr
        if ttr <= 7:
            return "auto_reject_fast", ttr
        return "auto_reject_slow", ttr

    return mapped, ttr


def fetch_csv(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "career-agent-sheet-importer/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    text = data.decode("utf-8", errors="replace")
    if "<html" in text[:500].lower():
        raise RuntimeError("Got HTML instead of CSV. Make sure the sheet is shared 'Anyone with the link can view' and the URL uses /export?format=csv&gid=<GID>.")
    return text


def load_existing() -> list[dict]:
    if not APPS_PATH.exists():
        return []
    rows = []
    for line in APPS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return rows


def save(rows: list[dict]) -> None:
    APPS_PATH.parent.mkdir(exist_ok=True)
    with APPS_PATH.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")


def build_row(sheet_row: dict, today: date) -> dict | None:
    company = (sheet_row.get("Company") or "").strip()
    role = (sheet_row.get("Role") or "").strip()
    if not company or not role:
        return None

    ts = parse_timestamp(sheet_row.get("Timestamp", ""))
    date_applied = ts.isoformat() if ts else ""
    status, ttr = derive_status(sheet_row.get("Status", ""), ts, today)

    notes_parsed = parse_notes(sheet_row.get("Notes", ""))
    url, ats = parse_job_link(sheet_row.get("Job Link", ""))
    pay = parse_pay_range(sheet_row.get("Pay Range", ""))

    return {
        "id": f"{slugify(company)}-{slugify(role)[:40]}-{date_applied or 'unknown'}",
        "company": company,
        "role_title": role,
        "role_family": categorize_role_family(role),
        "job_url": url,
        "date_applied": date_applied,
        "ats_platform": ats,
        "company_brand_tier": 3,
        "company_size": "",
        "salary_range": pay,
        "remote_policy": "",
        "resume_variant": None,
        "cover_letter_variant": None,
        "wow_item": None,
        "decision_classification": "STRONG APPLY",  # pre-v2 default; updated when v2 ships
        "scores": {
            "job_fit_probability": None,
            "ats_score": notes_parsed["ats_score"],
            "recruiter_scan_score": None,
            "hiring_manager_confidence": None,
            "technical_depth": None,
            "sre_platform_ownership": None,
            "scale_impact": None,
            "wow_factor": None,
            "ai_genericness_risk": None,
            "believability": None,
            "proof_density": None,
            "composite_interview_probability": None,
        },
        "scores_per_dimension_ats": None,
        "gaps_missing_intentional": [],
        "gaps_missing_genuine": notes_parsed["gaps_missing_genuine"],
        "keywords_added": [],
        "status": status,
        "rejection_type": None,
        "time_to_response_days": ttr,
        "first_response_date": None,
        "referral_used": False,
        "referral_outcome": None,
        "networking_attempted": False,
        "networking_outcome": None,
        "blocking_reason": None,
        "resume_notes": notes_parsed["free_text"][:500],
        "suspected_failure_reason": None,
        "next_experiment": None,
    }


def merge_into_existing(new_row: dict, existing: list[dict]) -> tuple[str, dict]:
    """
    Returns (action, row):
      action = "append" | "update" | "skip"
      row    = the row to write (for append/update) or None for skip
    """
    match = fuzzy_company_match(new_row["company"], existing)
    if not match:
        return "append", new_row

    # Same id => skip (already imported)
    if match.get("id") == new_row["id"]:
        return "skip", match

    # Same company, different role/date => append as new application
    if match.get("role_title", "").lower() != new_row["role_title"].lower():
        return "append", new_row
    if match.get("date_applied") != new_row["date_applied"]:
        return "append", new_row

    # Same company + role + date => update status and scores
    updated = dict(match)
    updated["status"] = new_row["status"]
    if new_row["time_to_response_days"] is not None:
        updated["time_to_response_days"] = new_row["time_to_response_days"]
    if new_row["scores"]["ats_score"] is not None:
        updated["scores"]["ats_score"] = new_row["scores"]["ats_score"]
    if new_row["gaps_missing_genuine"]:
        updated["gaps_missing_genuine"] = new_row["gaps_missing_genuine"]
    if new_row["resume_notes"]:
        updated["resume_notes"] = new_row["resume_notes"]
    return "update", updated


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    url = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    print(f"Fetching CSV from {url[:80]}...")
    try:
        text = fetch_csv(url)
    except Exception as e:
        print(f"Failed to fetch: {e}", file=sys.stderr)
        sys.exit(1)

    reader = csv.DictReader(io.StringIO(text))
    today = date.today()
    existing = load_existing()
    existing_by_id = {r.get("id"): r for r in existing}

    n_append = n_update = n_skip = 0
    sheet_rows_seen = 0

    new_rows = []
    for sheet_row in reader:
        sheet_rows_seen += 1
        row = build_row(sheet_row, today)
        if row is None:
            continue
        action, result = merge_into_existing(row, existing)
        if action == "append":
            existing.append(result)
            existing_by_id[result["id"]] = result
            n_append += 1
        elif action == "update":
            # Replace the matched row in place
            for i, r in enumerate(existing):
                if r.get("id") == result.get("id"):
                    existing[i] = result
                    break
            n_update += 1
        else:
            n_skip += 1

    print(f"\nRead {sheet_rows_seen} rows from sheet.")
    print(f"  Append: {n_append}")
    print(f"  Update: {n_update}")
    print(f"  Skip:   {n_skip} (already imported)")

    if dry_run:
        print("\nDry run. data/applications.jsonl NOT modified.")
        if n_append > 0:
            print("\nFirst new row preview:")
            for r in existing:
                if r.get("id") not in existing_by_id or True:  # always show one
                    print(json.dumps(r, indent=2)[:1500])
                    break
        return

    save(existing)
    print(f"\nWrote {len(existing)} rows to {APPS_PATH}")
    print("\nNext: python3 scripts/learning-analyzer.py")


if __name__ == "__main__":
    main()
