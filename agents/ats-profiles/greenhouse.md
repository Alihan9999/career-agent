# ATS Profile: Greenhouse

Greenhouse's parser maps the **Skills** section first to scorecard criteria,
so a Skills-first layout earns measurably higher match scores. Vector-text
PDFs from design tools parse correctly in 2026.

## Preferred Format
- **PDF** (vector text, not scanned)
- DOCX accepted but PDF preferred for scorecard rendering

## Section Order
1. Header (name + contact)
2. **Technical Skills** ← first scored section
3. Professional Experience
4. Projects (if relevant)
5. Education

## Banned Constructs
- Tables (skills-as-rows is fine if rendered as flowing paragraphs, not as a
  `<table>` element)
- Two-column layouts (Greenhouse handles narrow left-rail layouts ~80% of the
  time; safer to use single column)
- Headers/footers with critical info

## Required Constructs
- Skills must be one categorized block with **bold category labels** and
  comma-separated lists, e.g. `**Cloud:** AWS, GCP, Azure`
- Role context line for each job: `**Company** | **Title** | Dates | Location`
  Greenhouse's scorecard parser uses the title and tools mentioned in the
  first bullet of each role.

## Keyword Expansion
- Include both acronym and full term at least once for any compound skill.
  Greenhouse scorecard does literal token matching when posting uses the
  full term but resume uses the acronym (or vice versa).
- Required pairs (when relevant):
  - Kubernetes (K8s)
  - Amazon Web Services (AWS), Google Cloud Platform (GCP)
  - Continuous Integration / Continuous Deployment (CI/CD)
  - Infrastructure as Code (IaC)
  - Site Reliability Engineering (SRE)

## Parser Risk Flags
- Avoid mixing `●` and `-` bullet markers — pick one
- Avoid skills inside a `| col1 | col2 |` markdown table — render as
  paragraph rows with bold category prefix
