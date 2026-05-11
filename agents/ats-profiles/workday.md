# ATS Profile: Workday

Workday's parser favors DOCX over PDF in 2026 (measurably higher
section-extraction accuracy). Like Greenhouse, Workday maps Skills first to
scorecard criteria.

## Preferred Format
- **DOCX** (preferred — higher parse accuracy)
- PDF accepted as fallback

## Section Order
1. Header (name + contact)
2. **Technical Skills** ← first scored section
3. Professional Experience
4. Projects (if relevant)
5. Education

## Banned Constructs
- Tables (Workday parser drops table cells silently)
- Text boxes
- Page headers/footers with name or contact info — Workday strips these
- Two-column layouts
- Images, icons, custom fonts

## Required Constructs
- Field labels that match Workday's expected headings: "Experience" (not
  "Work History"), "Education" (not "Academic Background"), "Skills" (not
  "Capabilities")
- Date format: "Month Year - Month Year" (e.g. "Jan 2023 - Dec 2024"); avoid
  "01/2023 - 12/2024" — Workday parses inconsistently
- One job per company per entry; consecutive titles at the same company can
  share a company header but each role must have its own date range

## Keyword Expansion
- Acronym + full term pairs, same rules as Greenhouse profile
- Workday's keyword matcher is case-insensitive but token-based; "PostgreSQL"
  and "Postgres" are different tokens — include both if the posting uses
  either

## Parser Risk Flags
- Long bullet sentences (>30 words) may be truncated in Workday's bullet
  preview pane — keep bullets at 20-25 words max
- Special characters in metrics: write "25%" not "25 percent"; write "$1M"
  not "1 million"
