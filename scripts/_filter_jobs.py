"""Temporary filter script for scan — filters jobs by include/exclude keywords and remote/US location."""
import json, sys, re

INCLUDE = [
    "devops", "sre", "site reliability", "platform engineer", "platform engineering",
    "infrastructure engineer", "cloud engineer", "production engineer", "reliability engineer",
    "systems engineer", "kubernetes", "observability"
]
EXCLUDE = [
    "staff", "principal", "director", "manager", "vp", "head of", "lead",
    "data scientist", "data engineer", "ml engineer", "machine learning",
    "frontend", "front end", "full stack", "ios", "android", "mobile",
    "sales", "marketing", "recruiter", "customer", "support", "intern"
]
REMOTE_SIGNALS = ["remote", "united states", "us only", "usa", "work from home"]
NON_US = ["uk", "united kingdom", "london", "germany", "berlin", "canada", "toronto",
          "portugal", "singapore", "india", "bangalore", "australia", "sydney",
          "amsterdam", "netherlands", "ireland", "dublin", "paris", "france"]

jobs = json.load(open(sys.argv[1]))
company = sys.argv[2] if len(sys.argv) > 2 else "Unknown"
results = []
on_site_skipped = []
no_match = 0

for j in jobs:
    title = j.get("title", "")
    tl = title.lower()
    loc = (j.get("location") or "").lower()

    # Exclude filter
    if any(kw in tl for kw in EXCLUDE):
        continue
    # Include filter
    if not any(kw in tl for kw in INCLUDE):
        no_match += 1
        continue
    # Location: skip non-US
    if any(c in loc for c in NON_US):
        continue
    # Location: skip clearly on-site US cities (no remote signal)
    if loc and not any(s in loc for s in REMOTE_SIGNALS) and loc not in ("", "anywhere"):
        on_site_skipped.append({"company": company, "title": title, "location": j.get("location", "")})
        continue
    results.append(j)

print(json.dumps({"matches": results, "on_site": on_site_skipped, "no_match_count": no_match}))
