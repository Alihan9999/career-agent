# Resume Template — Formatting Rules

The Resume Customizer must produce output that exactly follows these rules.

---

## Page Layout
- 1 page maximum (strict)
- Margins: 0.5in all sides (when exported to PDF)
- Font: single font family, clean sans-serif (for PDF export)
- Font size: 11pt body, 14pt name, 12pt section headers

## Section Order (in this order, no exceptions)
1. Header (name + contact)
2. Summary (2-3 sentences)
3. Experience
4. Projects (if space permits and relevant)
5. Skills
6. Education

## Header Format
```
FIRSTNAME LASTNAME
email@example.com | (555) 123-4567 | City, State | linkedin.com/in/handle | github.com/handle
```
- Name on its own line, ALL CAPS or Title Case
- All contact info on one line, separated by ` | `
- No photo, no address beyond city/state

## Section Headers
```
## EXPERIENCE
```
- All caps
- Plain horizontal rule below (---) or bold styling
- No icons or decorative elements

## Experience Entry Format
```
### Job Title — Company Name
*Month Year – Month Year* | City, State (or Remote)

- Bullet starting with strong action verb
- Bullet with metric
- Bullet
```
- Date and location on same line as header
- Max 4-5 bullets per role
- Bullets: plain hyphens, no nested bullets
- Each bullet: one sentence, past tense (except current role)
- Lead with verb: Built, Reduced, Designed, Led, Implemented, Shipped, Scaled, etc.

## Projects Section Format
```
### Project Name | [github.com/link](url) | Live: [url](url)
*Tech stack: list, of, technologies*

- What it does in one line
- Key technical achievement
```
- Max 2 bullets
- Include URLs

## Skills Section Format
```
**Languages:** Python, Go, TypeScript
**Frameworks:** React, FastAPI, Django
**Cloud:** AWS (EC2, RDS, Lambda), GCP
**Tools:** Docker, Kubernetes, GitHub Actions, Terraform
```
- Grouped by category on single lines
- Only include skills at Proficient or Expert level (from skills.md)
- Use exact terminology from the job posting where possible

## Education Format
```
**B.S. Computer Science** — University Name — 2021
```
- One line per degree
- No GPA unless above 3.7 and applying to early-career roles
- Certifications can go here too

## General Rules
- No "References available upon request"
- No objective statement
- No personal pronouns (I, my, we) in bullets
- Numbers: spell out under 10 in prose, use digits for metrics (increased speed by 3x, managed 12 engineers)
- Dates: "Jan 2023" format (abbreviated month + year)
- Consistency: if you use dashes, use them everywhere; if bullets, everywhere
