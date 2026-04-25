# Resume Template — Formatting Rules

The Resume Customizer must produce output that exactly follows these rules.

---

## Page Layout
- 1 page maximum (strict)
- Margins: 0.5in all sides (when exported to PDF)
- Font: single font family, clean sans-serif (for PDF export)
- Font size: 11pt body, 14pt name, 12pt section headers

## Section Order (in this order, no exceptions)
1. Header (`# Name` + contact line)
2. `## Professional Experience`
3. `## Projects` (if space permits and relevant)
4. `## Technical Skills`
5. `## Education`

**No summary section.** Section headers use title case, not ALL CAPS.

## Header Format
```
# FIRSTNAME LASTNAME
email@example.com | (555) 123-4567 | linkedin.com/in/yourhandle | yoursite.com
```
- Name uses `#` (h1) so it renders centered and large in the PDF
- All contact info on one line immediately below, separated by ` | `
- LinkedIn and Portfolio as plain visible URLs — not masked as link text
- No city/state in header — location is already shown in the experience entry
- Go straight into the first `##` section — no `---` divider, no blank line between header and section

## Section Headers
```
## EXPERIENCE
```
- All caps
- Plain horizontal rule below (---) or bold styling
- No icons or decorative elements

## Experience Entry Format
```
**Company Name** | ***Job Title*** | *Month Year – Month Year* | City, State (or Remote)

- Bullet starting with strong action verb
- Bullet with metric
- Bullet
```
- Company, job title, date, and location all on ONE line as a bold paragraph — no h3 header
- Job title in bold italic (`***text***`), date in italic (`*text*`)
- Max 4-5 bullets per role
- Bullets: plain hyphens, no nested bullets
- Each bullet: one sentence, past tense (except current role)
- Lead with verb: Built, Reduced, Designed, Led, Implemented, Shipped, Scaled, etc.

### Bolding within bullets
Bold two things in every bullet — no more, no less:
1. **Key technology or tool** — the most relevant tech name from the job posting (e.g. `**Ansible**`, `**Kubernetes**`, `**Terraform**`)
2. **Metric or outcome** — the quantified result (e.g. `**~25%**`, `**1,000+**`, `**200+**`, `**~40%**`)

If a bullet has no metric, bold the two most important technology names instead.
Never bold generic words (e.g. "automation", "platform", "system") — only proper tool/technology names and numbers.

## Projects Section Format
```
**Project Name** | Brief descriptor (e.g. Internal Production System)
*Tech stack: list, of, technologies*

- What it does in one line
- Key technical achievement
```
- Project name as bold paragraph (not h3)
- Tech stack on next line in italics — same paragraph block (no blank line between name and stack)
- Max 2 bullets — apply the same bolding rules as experience bullets
- Blank line before the next project name (so `ul + p` CSS adds visual separation)
- Project URL (if public) goes on the descriptor line: `**Project Name** | Personal — github.com/user/repo` — never repeat a URL already in the header

## Skills Section Format
```
**Languages:** Python, Go, TypeScript

**Frameworks:** React, FastAPI, Django

**Cloud:** AWS (EC2, RDS, Lambda), GCP

**Tools:** Docker, Kubernetes, GitHub Actions, Terraform
```
- Each category on its own paragraph — blank line between every row
- Blank lines are required so each row renders as a separate line in the PDF
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
