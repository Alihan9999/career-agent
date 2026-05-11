# ATS Profile: Generic / Unknown

Use this profile when the target ATS is unknown or not in the supported list.
It encodes the conservative, parser-safe defaults that work across all major
ATSs in 2026.

## Preferred Format
- **PDF** — universally parsed; DOCX accepted as alternative.

## Section Order
1. Header (name + contact)
2. Professional Experience
3. Projects (if relevant)
4. Technical Skills
5. Education

## Banned Constructs
- Tables of any kind
- Text boxes
- Page headers/footers with critical info (parser drops them)
- Two-column layouts (61% of parsers skip the right column entirely)
- Embedded images, icons, charts
- Non-standard section names ("My Journey", "What I Bring") — use plain
  "Experience", "Education", "Skills"

## Required Constructs
- Reverse-chronological work history
- Each role: company + title + dates on one logical line
- Dates as "Month Year" or "Mon YYYY", consistent throughout
- Plain hyphens (-) for bullets; no Unicode markers

## Keyword Expansion
- Include both acronym and full term at least once per document when both
  forms are in common use. Examples:
  - Kubernetes (K8s)
  - Continuous Integration (CI), Continuous Deployment (CD)
  - Site Reliability Engineering (SRE)
  - Infrastructure as Code (IaC)
  - Service Level Objective (SLO), Service Level Indicator (SLI)

## Parser Risk Flags
- Em-dashes (—) and en-dashes (–) — replace with hyphens, commas, or splits
- Bullets using `●`, `◦`, `▪` — use `-` instead
- Section headers in all caps with letter-spacing — keep plain title case
