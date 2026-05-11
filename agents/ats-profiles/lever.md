# ATS Profile: Lever

Lever uses full-text search rather than structured scorecard matching,
favoring dense skills lines over deeply categorized sections.

## Preferred Format
- **PDF** (vector text)
- DOCX accepted

## Section Order
1. Header (name + contact)
2. Professional Experience
3. Projects (if relevant)
4. Technical Skills
5. Education

## Banned Constructs
- Tables
- Two-column layouts (Lever's preview pane is single-column)
- Headers/footers with critical info

## Required Constructs
- Dense skills section: comma-separated within each category, all categories
  on a few lines (Lever's full-text search rewards keyword density)
- Tech stack mentioned inline in experience bullets, not only in the skills
  section — Lever recruiters search inside experience text

## Keyword Expansion
- Acronym + full term where common (Kubernetes / K8s, AWS / Amazon Web
  Services)
- Lever's search is fuzzy — exact phrase matches still rank higher, but
  variants score partially

## Parser Risk Flags
- Lever caps preview at ~2000 characters per section in recruiter view;
  keep the resume tight so the Skills section isn't truncated
