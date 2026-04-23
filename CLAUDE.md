# Career Agent — AI-Powered Job Application System

## Overview

This system uses a multi-agent pipeline to automatically customize a resume and write a cover
letter for any job posting URL. After applying, it logs the application to a Google Form tracker
and generates a PDF. A gap analysis script surfaces recurring skill gaps across all applications.

**Entry point:** Paste a job posting URL into the chat. The orchestrator handles the rest.

---

## Quick Start

```
Apply for this job: <JOB_POSTING_URL>
```

Optional context:
```
Apply for this job: <URL>
Role focus: Backend Engineer
Emphasize: distributed systems, Go, Kubernetes
```

Run gap analysis across all applications:
```
analyze my gaps
```

Generate a project schematic to fill a skill gap:
```
give me a project schematic
give me a project for Go
```

---

## Pre-Flight Gates (checked before every pipeline run)

Before running any agent, the orchestrator checks:

1. **Experience threshold** — If the role requires 5+ years, OR has a "Senior" title with no year
   count, OR is Staff/Principal level: **hard skip, do not run pipeline.** If 4+ years required:
   flag and ask the user whether to proceed.

2. **Salary floor** — If salary is listed and the entire range is below $150k: flag and ask the
   user whether to proceed. If no salary is listed: proceed normally.

3. **Role type** — If the role is clearly outside DevOps/SRE/Platform/Infrastructure/Security
   (e.g., frontend, sales, data science): flag and ask before running.

---

## Agent Pipeline

```
Job URL
  │
  ▼
[Pre-flight gate]         — Experience check, salary check, role type check
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
           [5] ATS Optimizer    — Reviews both docs, scores keyword match, writes ats-report.md
                 │
                 ▼
           [6] Output Packager  — Saves all files to /output/<company>-<date>/
                 │
                 ▼
           [7] Form Filler      — Submits Google tracking form
```

Standalone agents (run on demand, not part of the pipeline):
```
[Gap Analyzer]     — Scans all output/ folders, ranks recurring skill gaps by importance
[Project Mentor]   — Generates step-by-step project schematics to fill specific skill gaps
```

---

## Folder Structure

```
career-agent/
├── CLAUDE.md                    ← You are here
├── data/                        ← Source of truth — NEVER modify during pipeline
│   ├── personal-info.md         ← Name, contact, LinkedIn, GitHub
│   ├── base-resume.md           ← Full master resume (never sent directly)
│   ├── experience.md            ← Work history with detailed bullets
│   ├── projects.md              ← Side projects, open source, portfolio
│   └── skills.md                ← Technical + soft skills inventory
├── agents/
│   ├── orchestrator.md          ← Main coordination prompt
│   ├── job-analyzer.md
│   ├── company-researcher.md
│   ├── resume-customizer.md
│   ├── cover-letter-writer.md
│   ├── ats-optimizer.md
│   ├── form-filler.md
│   ├── gap-analyzer.md          ← On-demand: scans gaps across all applications
│   └── project-mentor.md        ← On-demand: generates project schematics
├── scripts/
│   └── gap-analysis.py          ← Run by gap-analyzer agent
├── templates/
│   └── resume-template.md       ← Formatting rules for resume output
├── config/
│   └── google-form.md           ← Form URL + field mappings (gitignored — use .example.md)
├── output/                      ← Generated applications (gitignored)
│   └── <Company>-<YYYY-MM-DD>/
│       ├── job-analysis.json
│       ├── company-research.json
│       ├── resume.md
│       ├── resume.pdf
│       ├── cover-letter.md
│       └── ats-report.md
├── analysis/                    ← Gap analysis reports (gitignored)
│   └── gap-analysis-<date>.md
└── projects/                    ← Project schematics (gitignored)
    └── <project-name>.md
```

---

## Setup Checklist

- [ ] Fill in `data/personal-info.md` with your contact details
- [ ] Fill in `data/base-resume.md` with your full work history
- [ ] Fill in `data/experience.md` with detailed bullets for each role
- [ ] Fill in `data/projects.md` with all projects + descriptions
- [ ] Fill in `data/skills.md` with all your skills
- [ ] Copy `config/google-form.example.md` to `config/google-form.md` and fill in your form URL + field IDs
- [ ] Install Node.js + Puppeteer for PDF generation (`npm install` in project root)

---

## Agent Roles Summary

| Agent | Trigger | Input | Output |
|---|---|---|---|
| Job Analyzer | Every pipeline | Job URL or pasted text | `job-analysis.json` |
| Company Researcher | Every pipeline | Company name + URL | `company-research.json` |
| Resume Customizer | Every pipeline | job-analysis + data/ | `resume.md` |
| Cover Letter Writer | Every pipeline | job-analysis + company-research + data/ | `cover-letter.md` |
| ATS Optimizer | Every pipeline | resume.md + cover-letter.md + job-analysis | Revised docs + `ats-report.md` |
| Output Packager | Every pipeline | All outputs | `/output/<Company>-<date>/` folder |
| Form Filler | Every pipeline | Output folder + job URL | Google Form submission |
| Gap Analyzer | On demand | All output/ folders | `analysis/gap-analysis-<date>.md` |
| Project Mentor | On demand | Latest gap analysis | `projects/<name>.md` schematic |

---

## Pipeline Rules

1. **Never modify** files in `data/` — they are the source of truth.
2. **Always create** a new subfolder in `output/` per application.
3. Resume must be **1 page max** unless the role explicitly requires more.
4. Cover letter must be **under 400 words**, 3 paragraphs.
5. ATS Optimizer must verify **at least 80% of required keywords** appear in the resume.
6. All monetary figures and dates in experience must be **preserved exactly** from source data.
7. **Never commit** `data/`, `output/`, `analysis/`, `projects/`, or `config/google-form.md` — all gitignored.

---

## Privacy Rules (public repo)

This repo is public. The following are gitignored and must never be committed:
- `data/*.md` — contains real resume content and contact info
- `output/*/` — contains personal resume and cover letter content
- `analysis/` — reveals job search targets
- `projects/` — reveals skill gap strategy
- `config/google-form.md` — contains real form URL and entry IDs
- `.env`, `.env.local` — any secrets
- `*.pdf` — generated resume/cover letter PDFs
