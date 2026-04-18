# Career Agent — AI-Powered Job Application System

## Overview

This system uses a multi-agent pipeline to automatically customize a resume and write a cover letter for any job posting URL. After applying, it fills out your tracking Google Form.

**Entry point:** Paste a job posting URL (and optionally a job title/role) into the chat. The orchestrator agent handles the rest.

---

## Quick Start

```
Apply for this job: <JOB_POSTING_URL>
```

Or with extra context:
```
Apply for this job: <URL>
Role focus: Backend Engineer
Emphasize: distributed systems, Go, Kubernetes
```

---

## Agent Pipeline

```
Job URL
  │
  ▼
[1] Job Analyzer          — Scrapes posting, extracts skills/requirements/keywords
  │
  ▼
[2] Company Researcher    — Researches company culture, mission, recent news
  │
  ├──────────────────────────────────┐
  ▼                                  ▼
[3] Resume Customizer     [4] Cover Letter Writer
  │                                  │
  └──────────────┬───────────────────┘
                 ▼
           [5] ATS Optimizer    — Reviews both docs for keyword density + ATS pass
                 │
                 ▼
           [6] Output Packager  — Saves files to /output/<company>-<date>/
                 │
                 ▼
           [7] Form Filler      — Fills Google tracking form
```

---

## Folder Structure

```
career-agent/
├── CLAUDE.md                   ← You are here
├── data/
│   ├── personal-info.md        ← Name, contact, LinkedIn, GitHub
│   ├── base-resume.md          ← Full master resume (never sent directly)
│   ├── experience.md           ← Work history with detailed bullets
│   ├── projects.md             ← Side projects, open source, portfolio
│   └── skills.md               ← Technical + soft skills inventory
├── agents/
│   ├── orchestrator.md         ← Main coordination prompt
│   ├── job-analyzer.md
│   ├── company-researcher.md
│   ├── resume-customizer.md
│   ├── cover-letter-writer.md
│   ├── ats-optimizer.md
│   └── form-filler.md
├── config/
│   └── google-form.md          ← Form URL + field mappings
├── templates/
│   └── resume-template.md      ← Formatting rules for output
└── output/                     ← Generated applications (gitignored)
    └── <Company>-<YYYY-MM-DD>/
        ├── resume.md
        ├── resume.pdf (if pandoc available)
        └── cover-letter.md
```

---

## Setup Checklist

- [ ] Fill in `data/personal-info.md` with your contact details
- [ ] Fill in `data/base-resume.md` with your full work history
- [ ] Fill in `data/experience.md` with detailed bullets for each role
- [ ] Fill in `data/projects.md` with all projects + descriptions
- [ ] Fill in `data/skills.md` with all your skills
- [ ] Fill in `config/google-form.md` with your form URL + field IDs

---

## Agent Roles Summary

| Agent | Input | Output |
|---|---|---|
| Job Analyzer | Job URL | `job-analysis.json` — skills, keywords, requirements, red flags |
| Company Researcher | Company name + URL | `company-research.json` — mission, culture, recent news, talking points |
| Resume Customizer | job-analysis + your data | `resume.md` — tailored 1-page resume |
| Cover Letter Writer | job-analysis + company-research | `cover-letter.md` — 3-paragraph letter |
| ATS Optimizer | resume.md + cover-letter.md + job-analysis | Revised docs with keyword gaps filled |
| Output Packager | All outputs | Saves to `/output/<Company>-<date>/` |
| Form Filler | Output folder path + job URL | Submits Google Form |

---

## Rules

1. **Never modify** files in `data/` — they are the source of truth.
2. **Always create** a new subfolder in `output/` per application.
3. Resume must be **1 page max** unless the role explicitly requires more.
4. Cover letter must be **under 400 words**, 3 paragraphs.
5. ATS Optimizer must verify **at least 80% of required keywords** appear in the resume.
6. All monetary figures and dates in experience must be **preserved exactly** from source data.
