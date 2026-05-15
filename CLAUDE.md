# Career Agent — AI-Powered Job Application System (v2 — Interview Conversion)

## Overview

This system uses a multi-agent pipeline optimized for **interview conversion rate**, not application throughput. Paste a job URL: the orchestrator decides whether the job is worth applying to (most are not), picks a resume variant (A/B/C/D/E), generates resume + cover letter, runs 7 quality gates (Recruiter Psychology, Hiring Manager, Proof Density, Anti-Template, Wow Factor, Humanizer, ATS), refuses to ship if scores are below threshold, generates the PDF/DOCX, submits the form, and logs the row to `data/applications.jsonl` for rejection learning.

**v1 produced 80 applications and 0 interviews.** v2 trades volume for selectivity. See `analysis/system-audit.md` for the audit, `analysis/interview-conversion-redesign.md` for the architecture, and `docs/ab-variant-strategy.md` for variant routing.

**Entry point:** Paste a job posting URL into the chat. The orchestrator handles the rest, and will stop the pipeline mid-flight if the application doesn't deserve to ship.

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
/analyze-gaps
```

Generate a project schematic to fill a skill gap:
```
/project-mentor
/project-mentor Go
```

Generate interview prep for a company you've applied to:
```
/interview-prep PayNearMe
/interview-prep PayNearMe-2026-04-27
```

Scan your target company watchlist for new openings:
```
/scan              # Tier 1 only (default — keeps tokens low)
/scan tier 2       # Tiers 1 + 2
/scan all          # Full watchlist
/scan Stripe       # One company by name
```
Setup: copy `config/target-companies.example.yml` to `config/target-companies.yml` and add your companies. Each entry must have a `tier: 1|2|3`.

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

4. **Legitimacy** — After the Job Analyzer runs, the posting is assigned a tier:
   - `HIGH_CONFIDENCE`: proceed normally
   - `PROCEED_WITH_CAUTION`: display red flags and continue
   - `SUSPICIOUS`: display red flags and ask whether to proceed (likely ghost job)

---

## Agent Pipeline (v2 — Interview Conversion)

```
Job URL
  │
  ▼
[Pre-flight gate]              — experience, salary, role type, legitimacy
  │
  ▼
[1] Job Analyzer
  │
  ▼
[2] Company Researcher (parallel)
  │
  ▼
[3] Application Decision Agent — classify + pick variant; STOP if not STRONG APPLY
  │
  ▼
[4] Resume Customizer          — TRANSFORM bullets, 5 variants
  │
  ▼
[5] Resume Narrative Strategist — enforce coherent story arc
  │
  ▼
[6] Cover Letter Writer (parallel)
  │
  ▼
[7] Wow Factor Strategist      — verify wow item above the fold
  │
  ▼
[8] ATS Optimizer (v2)         — 7-dimensional match scoring
  │
  ▼
[9] Recruiter Psychology Agent — 6-second scan simulation
  │
  ▼
[10] Hiring Manager Reviewer   — 90-second manager triage
  │
  ▼
[11] Proof Density Agent       — evidence count per bullet
  │
  ▼
[12] Anti-Template Agent       — cross-application repetition check
  │
  ▼
[13] Humanizer                 — AI-detection signature break
  │
  ▼
[14] Resume Quality Gate       — composite PASS / REVISE / BLOCK (3 iter cap)
  │
  ▼
[15] LinkedIn / Portfolio Alignment Agent
  │
  ▼
[16] Output Packager
  │
  ▼
[17] PDF / DOCX Generator
  │
  ▼
[18] Form Filler
  │
  ▼
[19] Rejection Learning per-app log — append to data/applications.jsonl
```

Standalone slash commands (run on demand, not part of the pipeline):
```
/scan                  — Scans target companies for new openings and scores each match
/analyze-gaps          — Scans all output/ folders, ranks recurring skill gaps by importance
/analyze-conversions   — Weekly rejection-learning analysis: conversion rates by slice;
                         updates data/blocked-companies.json and data/role-family-conversion.json
/import-sheet <URL>    — Import the Google Sheets application tracker into data/applications.jsonl
/market-signal         — Audit LinkedIn / GitHub / portfolio footprint and produce 2-week action list
/project-mentor        — Generates project schematics with distribution plan (for credibility,
                         not just keyword closure)
/interview-prep        — STAR-formatted prep doc for any company you've applied to
```

Outcome tracking flow: Form Filler writes every application to your Google Form -> the response Sheet collects rows. You update the **Status** column in the Sheet as outcomes happen. Then run:
```
/import-sheet <CSV_EXPORT_URL>
/analyze-conversions
```
The importer is idempotent. See `.claude/commands/import-sheet.md` for the CSV URL format.

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
│   ├── ats-profiles/            ← Per-ATS rules (greenhouse, workday, lever,
│   │                              icims, taleo, generic). Read by ATS Optimizer.
│   ├── humanizer.md             ← Breaks AI-detection signatures, preserves ATS keywords
│   ├── form-filler.md
│   ├── gap-analyzer.md          ← Backing agent for /analyze-gaps
│   └── project-mentor.md        ← Backing agent for /project-mentor
├── .claude/
│   └── commands/
│       ├── analyze-gaps.md      ← /analyze-gaps slash command
│       └── project-mentor.md   ← /project-mentor slash command
├── scripts/
│   ├── gap-analysis.py          ← Run by gap-analyzer agent
│   ├── humanize-metrics.py      ← Run by humanizer agent (burstiness/cliche/dash check)
│   ├── scrape.py                ← Unified scraping CLI (fetch + board subcommands)
│   ├── to-pdf.js                ← Markdown -> PDF (default output)
│   ├── to-docx.js               ← Markdown -> DOCX (Workday/Taleo profile prefers DOCX)
│   └── spiders/                 ← Per-board scrapers (greenhouse, lever, ashby, workable,
│                                   workday, linkedin, indeed, wellfound, builtin, custom)
├── templates/
│   └── resume-template.md       ← Formatting rules for resume output
├── config/
│   ├── google-form.md           ← Form URL + field mappings (gitignored — use .example.md)
│   └── target-companies.yml     ← Company watchlist for /scan (gitignored — use .example.yml)
├── output/                      ← Generated applications (gitignored)
│   └── <Company>-<YYYY-MM-DD>/
│       ├── job-analysis.json
│       ├── company-research.json
│       ├── resume.md
│       ├── resume.pdf
│       ├── cover-letter.md
│       ├── ats-report.md
│       └── humanizer-report.md
├── analysis/                    ← Gap analysis reports (gitignored)
│   └── gap-analysis-<date>.md
├── scans/                       ← Scan results per run (gitignored)
│   └── scan-<YYYY-MM-DD>/
│       └── report.md
└── projects/                    ← Project schematics (gitignored)
    └── <project-name>.md
```

---

## Setup Checklist

### Personal data
- [ ] Fill in `data/personal-info.md` with your contact details
- [ ] Fill in `data/base-resume.md` with your full work history
- [ ] Fill in `data/experience.md` with detailed bullets for each role
- [ ] Fill in `data/projects.md` with all projects + descriptions
- [ ] Fill in `data/skills.md` with all your skills

### Configuration
- [ ] Copy `config/google-form.example.md` → `config/google-form.md` and fill in your form URL + field IDs
- [ ] Copy `config/target-companies.example.yml` → `config/target-companies.yml` and fill in your watchlist. Tag each company with `tier: 1|2|3`. `/scan` defaults to Tier 1 only — raise `scan_tier_limit` in the file (or pass `/scan tier 2`, `/scan all`, etc.) when you want a wider sweep.

### Node.js (PDF + DOCX generation)
Requires Node ≥18.
```
npm install
```
Installs: `puppeteer` (PDF rendering), `html-to-docx` (Workday/Taleo profiles produce DOCX), `marked`, `@anthropic-ai/sdk`, `express`, `dotenv`.

### Python (scraping + metrics scripts)
Requires Python ≥3.10.
```
pip install -r requirements.txt
scrapling install     # one-time: fetches Chromium browser binaries
```
Installs: `scrapling[ai,fetchers]` (stealth scraping + Cloudflare bypass + MCP server), `PyYAML` (watchlist parser).

> Greenhouse and Lever spiders use stdlib `urllib` only and work without Scrapling, so you can defer the install if you only watch those boards.

> **Windows note:** if `python3` isn't on PATH, install with `py -3.14 -m pip install -r requirements.txt` and run scripts with `py -3.14 scripts/scrape.py ...`. Make sure the `pip install` and the script invocation use the **same** Python — using one Python to install and a different one to run is the most common cause of `ModuleNotFoundError: No module named 'scrapling'`.

### Claude Code MCP server
`.mcp.json` in the repo root registers Scrapling's MCP server at project scope. When you open the project in Claude Code, it starts automatically — confirm with `/mcp` and look for `scrapling`. No manual registration needed.

### Token budget tips
- `/scan` defaults to Tier 1 only. Use `/scan tier 2` or `/scan all` when you actively want a broader pass.
- The full application pipeline (resume + cover letter + ATS optimizer + humanizer) is the most expensive operation per run. Use `/scan` to surface STRONG matches first, then approve only the ones worth a full pipeline run.
- The Scrapling JSON-API spiders (greenhouse, lever, builtin) cost almost nothing — they're plain HTTP. The browser-based spiders (ashby, wellfound, workday, linkedin, indeed) are heavier; prefer the JSON-API boards in your watchlist where possible.

---

## Agent Roles Summary

| Agent | Trigger | Output |
|---|---|---|
| Job Analyzer | Every pipeline | `job-analysis.json` |
| Company Researcher | Every pipeline | `company-research.json` |
| **Application Decision Agent** | Every pipeline | `application-decision.json` (STRONG APPLY / SKIP / NETWORKING FIRST / BUILD GAP / ...) |
| Resume Customizer (v2) | If decision is APPLY-class | `resume.md` per variant (A/B/C/D/E) |
| **Resume Narrative Strategist** | After Customizer | rewrites `resume.md` for arc coherence |
| Cover Letter Writer | If APPLY-class | `cover-letter.md` |
| **Wow Factor Strategist** | After Narrative | verifies wow item above the fold |
| ATS Optimizer (v2) | Every pipeline | 7-dimensional `ats-report.md`; flags rather than forces unbelievable keywords |
| **Recruiter Psychology Agent** | After ATS | `recruiter-review.md` |
| **Hiring Manager Reviewer** | After Recruiter | `hiring-manager-review.md` |
| **Proof Density Agent** | After Hiring Manager | `proof-density-review.md` |
| **Anti-Template Agent** | After Proof Density | `anti-template-review.md` (cross-app bigram overlap) |
| Humanizer | After Anti-Template | `humanizer-report.md` |
| **Resume Quality Gate** | After Humanizer | `quality-gate-verdict.md` (PASS / REVISE / BLOCK) |
| **LinkedIn/Portfolio Alignment Agent** | After Quality Gate PASS | `linkedin-portfolio-alignment.md` |
| Output Packager | After Alignment | `/output/<Company>-<date>/` folder |
| Form Filler | After packaging | Google Form submission |
| **Rejection Learning Agent (per-app)** | After Form Filler | appends row to `data/applications.jsonl` |
| **Rejection Learning Agent (aggregate)** | `/analyze-conversions` | `analysis/conversions-<date>.md` |
| Gap Analyzer | `/analyze-gaps` | `analysis/gap-analysis-<date>.md` |
| Project Mentor (v2) | `/project-mentor` | `projects/<name>.md` with distribution plan |
| Interview Prep | `/interview-prep` | `output/<Company>/interview-prep.md` |
| Scanner | `/scan` | `scans/scan-<date>/report.md` |

New agents marked **bold**.

---

## Pipeline Rules

1. **Never modify** files in `data/` (other than `data/applications.jsonl` which the pipeline maintains and `data/blocked-companies.json` + `data/role-family-conversion.json` which the learning analyzer writes).
2. **Always create** a new subfolder in `output/` per application — only after the Quality Gate passes.
3. Resume must be **1 page max** unless the role explicitly requires more.
4. Cover letter must be **under 400 words**, 3 paragraphs.
5. ATS Optimizer must reach **80% composite ATS score** but ATS Score alone does not unblock the gate.
6. **Resume Quality Gate must PASS** — ALL minimum scores must clear, not just ATS. If any fail after 3 revisions, BLOCK the application.
7. All monetary figures and dates in experience must be **preserved exactly** from source data.
8. **Never commit** `data/`, `output/`, `analysis/`, `projects/`, `scans/`, or `config/google-form.md` — all gitignored.
9. **Never invent** metrics, system names, or claims to clear a score. Block honestly instead.

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
