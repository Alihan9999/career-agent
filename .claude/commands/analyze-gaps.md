Run the gap analysis script across all job applications and report the results.

Steps:
1. Run `python scripts/gap-analysis.py` from the project root
2. Read the generated report from `analysis/gap-analysis-<today's date>.md`
3. Print the full ranked gap list to the conversation so the user can see it

If the script fails because there are too few applications, lower the MIN_APPLICATIONS threshold in `scripts/gap-analysis.py` to 1 and re-run.

After printing the results, ask the user if they want a project schematic to address the top CRITICAL or HIGH gaps.
