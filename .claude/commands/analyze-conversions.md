Run the rejection-learning analysis across all applications and report patterns.

## Steps

1. Run `python3 scripts/learning-analyzer.py` from the project root.
2. Read the generated report from `analysis/conversions-<today's date>.md`.
3. Print a concise summary to the chat:
   - Total apps, submitted, conversions, conversion rate
   - Best-performing variant
   - Worst-performing role family (10+ apps, 0 conversions)
   - Companies promoted to NETWORKING_FIRST
   - Top 3 keywords in positive apps (if any)
   - Median time-to-response by ATS platform
4. After printing, ask the user if they want to:
   - Run `/project-mentor` on a specific gap surfaced by the analysis
   - Update LinkedIn / GitHub for the role family that's not converting
   - Set a `scan_tier_limit` change based on which brand tier converts best

## Notes

- If `data/applications.jsonl` does not exist or is empty, tell the user and stop.
- The analyzer also rewrites `data/blocked-companies.json` and `data/role-family-conversion.json`. Mention this so the user knows the Application Decision Agent's apply/skip logic is now updated.
- Never use em dashes in output.
