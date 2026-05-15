Audit the candidate's external footprint (LinkedIn, GitHub, portfolio, conference / blog signals) and produce a 2-week action list.

## Steps

1. Run the **Market Signal Agent** (`agents/market-signal-agent.md`).
2. Save the report to `analysis/market-signal-<today's date>.md`.
3. Print a summary to chat:
   - Market Signal Score (0-10)
   - The top 3 DO THIS WEEK actions
   - The top 2 DO NEXT WEEK actions
4. Ask if the user wants help drafting the LinkedIn post / README update / blog draft for any DO THIS WEEK item.

## Notes
- Handle inaccessible surfaces (LinkedIn login wall) gracefully.
- Reuse the live-fetch logic from `agents/linkedin-portfolio-alignment-agent.md` when surfaces overlap.
- Never use em dashes.
