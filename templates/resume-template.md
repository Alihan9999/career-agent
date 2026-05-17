# Resume Template — Formatting Rules

The Resume Customizer must produce output that exactly follows these rules. The template now supports **five variants** (A/B/C/D/E) chosen by the Application Decision Agent. See `docs/ab-variant-strategy.md` for which variant goes where.

---

## Page Layout
- 1 page maximum (strict)
- Margins: 0.5in all sides (when exported to PDF)
- Font: single font family, clean sans-serif (for PDF export)
- Font size: 11pt body, 14pt name, 12pt section headers

## Section Order

**Updated 2026-05-17:** the default resume shape is **no headline, Experience-first**. Drop straight from the contact line into `## Professional Experience`. The Achievements block and projects-first ordering are special-case patterns, NOT defaults. Section labels never carry a "Selected" prefix — use `## Projects` not `## Selected Projects`, and `**Achievements**` (no "Selected") on the rare occasions the block is used.

**Default shape for ALL variants (A/B/C/D/E):**
1. Header (`# NAME` + contact line — no headline)
2. `## Professional Experience`
3. `## Projects`
4. `## Technical Skills`
5. `## Education`

**Variant differentiation happens through content, not structure:**
- **Variant A — ATS-Heavy:** wide skills section, comma-dense lines, long bullets that front-load JD tokens.
- **Variant B — Recruiter-Impact:** terse bullets, named systems, exact metrics, bold sparingly. Positioning comes through the first Experience bullet.
- **Variant C — SRE / Platform Narrative:** homelab MUST be the first Projects entry. Lead Experience with the 200+ apps CI/CD platform bullet or the Splunk SIEM bullet depending on the JD emphasis.
- **Variant D — Automation / Project-Heavy:** Projects section includes 0rca + Career Agent before the homelab. Experience compressed to 3-4 of the strongest bullets.
- **Variant E — Conservative Enterprise:** lead with the 1,000+ multi-OS + Splunk SIEM bullet. Skills section retains AIX / Solaris / Octopus Deploy as visible positives.

**ATS Profile Override:** For Greenhouse and Workday + Variant A/E, the ATS Optimizer may swap Technical Skills to position 2 (Skills-first scorecard mapping). The default shape applies otherwise.

Section headers use title case, not ALL CAPS.

## Parser-Safe Constraints (apply to both layouts)
- Single column only — never two-column (61% of ATS parsers drop the right column entirely)
- No tables (`| col1 | col2 |`) — render category rows as bold-prefixed paragraphs
- No text boxes, page headers/footers, or embedded images
- Standard section names exactly: "Professional Experience", "Technical Skills",
  "Projects", "Education". Do not rename to creative titles.
- Plain hyphen (`-`) for bullets — never Unicode bullets (`●`, `◦`, `▪`)
- Dates: "Mon YYYY" or "Month YYYY" everywhere (Taleo prefers "MM/YYYY"; the
  ATS Optimizer applies that swap if the profile demands it)

## Header Format

```
# FIRSTNAME LASTNAME
email@example.com | (555) 123-4567 | linkedin.com/in/yourhandle | yoursite.com
```

- Name uses `#` (h1)
- Contact line: ` | ` separated
- **No headline.** (Updated 2026-05-17.) The prior 80-90 char headline pattern was retired; every anchor a headline would carry is already repeated in body bullets, and the headline burned a line of vertical space the 1-page budget needed. Drop straight from the contact line to the first `##` section.
- LinkedIn and Portfolio as plain visible URLs — not masked as link text
- No city/state in header — location is shown in the experience entry
- Go straight into the first `##` section — no `---` divider

### Achievements block (OPTIONAL, OFF BY DEFAULT)

An `**Achievements**` block (3 lines, no "Selected" prefix) MAY be added between the contact line and the first section when the user explicitly requests it for a specific run. **Do not add it by default.** Reason: the Experience and Projects bullets already carry the anchor metrics (200+ apps, $30k/month, 60-second reconciliation, etc.) — a separate Achievements block restates them and bloats the top of the resume. If used, each line must add information not already in the body sections (e.g., a cross-cutting metric the body bullets don't surface). Verified through the Fabletics application 2026-05-15: the Achievements block read as duplicative and was dropped, freeing two visual lines of breathing room.

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
- Project URL (if public) goes on the descriptor line: `**Project Name** | Personal | github.com/user/repo` — never repeat a URL already in the header

### Project differentiation rule (CRITICAL)
Every project must add something the experience section does not already show. Before including a project, check it against every experience bullet. If the project uses the same tools AND the same metric AND the same domain as an experience bullet, cut it or find a different angle to tell.

Specifically:
- Never repeat the same metric in both experience and a project (e.g., "MTTR by ~25%" appearing in both sections means one is wasted)
- Never repeat the same tool list if the framing is also identical
- Each project should contribute at least one of: a new tool not in experience, a new domain (cost optimization vs. observability vs. orchestration), a new metric, or a new technical depth (e.g., homelab shows Datadog and Go which work experience does not)

Project priority order for selection:
1. Projects that cover a gap keyword from the job posting (e.g., Datadog, Go, ArgoCD)
2. Projects that show a different domain than the experience bullets
3. Projects that add a tool not present anywhere in the experience section
4. Drop a project entirely rather than include one that only repeats what experience already covers

If only two projects qualify after applying this rule, use two — a tight two-project section is stronger than three where one is redundant.

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
- Never use em dashes (—) anywhere in the resume or cover letter; they read as AI-generated. Use commas, semicolons, or pipes (|) depending on context
