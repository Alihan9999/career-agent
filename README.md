# Career Agent

An AI-powered job application pipeline built on [Claude Code](https://claude.ai/code). Paste a job URL and it customizes your resume, writes a cover letter, scores against 9 quality dimensions (recruiter scan, hiring manager confidence, proof density, wow factor, ATS, anti-template, believability, job fit), refuses to ship if quality is below threshold, generates a PDF, and logs the application to a structured outcome log for rejection learning.

The system is optimized for **interview conversion rate**, not application throughput. Volume falls. Per-application quality rises. The pipeline will REFUSE to apply when the resume cannot honestly clear the bar, and instead recommend a referral path or a portfolio project that would close the credibility gap first.

Bonus tools: `/analyze-gaps` surfaces recurring skill gaps; `/analyze-conversions` runs weekly rejection-learning analysis; `/import-sheet` syncs outcomes from your Google Sheets tracker; `/market-signal` audits LinkedIn / GitHub / portfolio; `/project-mentor` generates a step-by-step project schematic designed for both keyword-gap closure AND recruiter wow factor; `/scan` triages a target-company watchlist; `/interview-prep` generates STAR-formatted prep notes for any logged application.

---

## What It Produces

For every application, the pipeline creates an output folder:

```
output/Stripe-2026-04-23/
├── job-analysis.json       ← parsed role requirements, salary, keywords
├── company-research.json   ← culture, mission, recent news
├── resume.md               ← tailored 1-page resume
├── resume.pdf              ← print-ready PDF
├── cover-letter.md         ← 3-paragraph cover letter (<400 words)
├── cover-letter.pdf        ← print-ready PDF
└── ats-report.md           ← ATS keyword score + missing terms
```

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| [Claude Code](https://claude.ai/code) | Latest | Runs the AI pipeline |
| Python | 3.10+ | Gap analysis script |
| Node.js | 18+ | PDF generation via Puppeteer |
| curl | Any | Google Form submission |

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Alihan9999/career-agent.git
cd career-agent
```

### 2. Install Node dependencies

```bash
npm install
```

This installs Puppeteer (headless Chrome) for PDF generation. It will download a Chromium binary
on first run (~150 MB).

### 3. Fill in your personal data files

Each `data/*.example.md` file is a template. Copy it, remove `.example` from the name, and fill
in your real information. These files are gitignored — your personal data will never be committed.

```bash
cp data/personal-info.example.md   data/personal-info.md
cp data/base-resume.example.md     data/base-resume.md
cp data/experience.example.md      data/experience.md
cp data/projects.example.md        data/projects.md
cp data/skills.example.md          data/skills.md
```

| File | What to put in it |
|---|---|
| `personal-info.md` | Name, email, phone, LinkedIn, GitHub, work authorization |
| `base-resume.md` | Your full master resume (every role, every bullet — never trimmed) |
| `experience.md` | Detailed work history with metrics, tech stack per role |
| `projects.md` | Side projects, open source, portfolio items with descriptions |
| `skills.md` | Technical and soft skills inventory, organized by category |

> The agents use these as the source of truth. They select and reorder content per role —
> you never touch the output files directly.

### 4. Set up your Google Form tracker (optional but recommended)

Create a Google Form with fields for: Role, Company, Pay Range, Status, Job Link, Notes.

Then configure the connection:

```bash
cp config/google-form.example.md config/google-form.md
```

Open `config/google-form.md` and fill in your form's submission URL and entry IDs. The example
file explains how to find the entry IDs using Google's pre-filled link tool.

If you skip this step, the pipeline will still run — the form submission step will just fail
silently at the end.

### 5. Open Claude Code in the project directory

```bash
claude
```

Or open the folder in VS Code with the Claude Code extension installed.

---

## Usage

### Run a full application pipeline

Paste a job URL into the chat:

```
Apply for this job: https://jobs.stripe.com/jobs/12345
```

The pipeline runs automatically end-to-end. You will only be prompted if a pre-flight gate fires
(see below). Otherwise it goes all the way through to PDF and form submission without interruption.

You can add optional hints:

```
Apply for this job: https://jobs.stripe.com/jobs/12345
Emphasize: distributed systems, Go, Kubernetes
```

### Slash commands

- **`/scan`** — triage target-company watchlist; ranks fresh openings 0-100 by fit
- **`/analyze-gaps`** — frequency × importance-weighted gap aggregation across applications
- **`/analyze-conversions`** — weekly rejection-learning analysis: conversion rates by variant, role family, ATS platform, brand tier; companies promoted to NETWORKING_FIRST; keyword correlation with positive outcomes
- **`/import-sheet <CSV_URL>`** — pull the latest Status column from your Google Sheets tracker into `data/applications.jsonl`
- **`/market-signal`** — audit LinkedIn / GitHub / portfolio external footprint and produce a 2-week action list
- **`/project-mentor [gap-or-tech]`** — generate a project schematic designed for credibility + keyword gap closure, with a distribution plan (GitHub README, Hacker News submission, conference CFP, LinkedIn post, technical write-up)
- **`/interview-prep <Company>`** — STAR-formatted prep notes for any logged application

Each project schematic includes architecture diagram, tech stack justification with alternatives considered, phase-by-phase build plan with exact commands, pre-written resume bullets (per variant), interview talking points, AND a distribution plan with target outlets and CFP deadlines.

---

## Pipeline Architecture (v2 — Interview Conversion)

```
Job URL
  │
  ▼
[Pre-flight gate]              ← experience, salary, role type, legitimacy
  │
  ▼
[1] Job Analyzer               ← scrape + extract structured signals
  │
  ▼
[2] Company Researcher         ← parallel
  │
  ▼
[3] Application Decision Agent ← classify: STRONG APPLY / WITH CUSTOMIZATION /
  │                              NETWORKING FIRST / SKIP / BUILD GAP / TOO SENIOR /
  │                              WRONG ROLE / LOW ROI
  │                              Decides variant (A/B/C/D/E). Most jobs are NOT
  │                              STRONG APPLY. Volume falls deliberately.
  │
  ▼
[4] Resume Customizer          ← transform bullets (not just select). 5 variants.
  │
  ▼
[5] Resume Narrative Strategist ← enforce coherent story arc; fix conflicts
  │
  ▼
[6] Cover Letter Writer        ← parallel
  │
  ▼
[7] Wow Factor Strategist      ← verify the wow item is above the fold
  │
  ▼
[8] ATS Optimizer (v2)         ← 7-dimensional match scoring, flag-not-force
  │                              keyword insertion
  │
  ▼
[9] Recruiter Psychology Agent ← simulate the 6-second scan
  │
  ▼
[10] Hiring Manager Reviewer   ← simulate the manager's 90-second triage
  │
  ▼
[11] Proof Density Agent       ← count evidence elements per bullet
  │
  ▼
[12] Anti-Template Agent       ← cross-application repetition check
  │
  ▼
[13] Humanizer                 ← break AI-detection signatures (existing)
  │
  ▼
[14] Resume Quality Gate       ← composite PASS / REVISE / BLOCK
  │                              up to 3 revise iterations
  │
  ├─── BLOCK ──> log to applications.jsonl with reason, stop, recommend
  │             BUILD GAP PROJECT FIRST or NETWORKING FIRST
  │
  ▼
[15] LinkedIn / Portfolio Alignment Agent ← cross-channel consistency
  │
  ▼
[16] Output Packager           ← write to output/<Company>-<date>/
  │
  ▼
[17] PDF / DOCX Generator      ← Puppeteer / html-to-docx per ATS profile
  │
  ▼
[18] Form Filler               ← submit Google tracking form
  │
  ▼
[19] Rejection Learning per-app ← append row to data/applications.jsonl
```

### Minimum scores to ship

The Resume Quality Gate blocks Output Packager unless ALL of:

| Score | Minimum |
|---|---|
| ATS Score | 80% |
| Recruiter 6-Second Scan | 8/10 |
| Hiring Manager Confidence | 8/10 |
| Technical Depth | 8/10 |
| Proof Density | 8/10 |
| Wow Factor | 7/10 |
| AI-Genericness Risk | <= 3/10 (lower is better) |
| Resume Believability | 8/10 |
| Job Fit Probability | 7/10 |

If any fail, the system revises up to 3 times. On final fail, the application is BLOCKED. The system does NOT generate PDFs and does NOT submit the form. It logs the block reason and recommends `/project-mentor` or a referral path.

This is deliberately strict. Most current outputs would fail the gate. That is the point.

---

## Pre-Flight Gates

The orchestrator checks these before running any pipeline:

| Gate | Condition | Action |
|---|---|---|
| Experience threshold | Role requires 5+ years, has "Senior" title, or is Staff/Principal | Hard skip |
| Experience threshold | Role requires 4+ years | Flag and ask whether to proceed |
| Salary floor | Entire listed range is below $150k | Flag and ask whether to proceed |
| Role type | Clearly outside DevOps/SRE/Platform/Infra/Security | Flag and ask before running |
| Location | Role is clearly outside your target geography | Flag and ask before running |

If no gates fire, the pipeline runs fully automatically.

---

## Adapting for Your Own Use

This system is built around one person's job search (DevOps/SRE roles), but the structure is
generic. To adapt it:

1. **Change the role filter** — edit the role type gate in `agents/orchestrator.md` to match
   your target function (frontend, data science, product, etc.)

2. **Change the salary floor** — edit the `$150k` threshold in `agents/orchestrator.md`

3. **Change the experience gate** — adjust the year thresholds to match your level

4. **Change the gap weights** — edit `IMPORTANCE_WEIGHTS` in `scripts/gap-analysis.py` to
   reflect the skills that matter most in your target market

5. **Change the resume template** — edit `templates/resume-template.md` for your preferred
   formatting style

---

## Privacy

This repo is public. The following are gitignored and will never be committed:

| Path | Why |
|---|---|
| `data/*.md` | Contains your real resume and contact info |
| `output/*/` | Contains personalized resume and cover letter content |
| `analysis/` | Reveals your job search targets |
| `projects/` | Reveals your skill gap strategy |
| `config/google-form.md` | Contains your real form URL and field IDs |
| `.claude/settings*.json` | Claude Code machine-specific permissions |
| `*.pdf` | Generated application documents |

The only Claude Code files that are committed are `.claude/commands/` — the slash command
definitions, which contain no personal data.

---

## Project Structure

```
career-agent/
├── README.md
├── CLAUDE.md                        ← instructions for the AI agents
├── data/                            ← your personal data (gitignored)
│   ├── personal-info.md
│   ├── base-resume.md
│   ├── experience.md
│   ├── projects.md
│   ├── skills.md
│   └── *.example.md                 ← safe templates to copy from
├── agents/                          ← agent prompt files
│   ├── orchestrator.md
│   ├── job-analyzer.md
│   ├── company-researcher.md
│   ├── resume-customizer.md
│   ├── cover-letter-writer.md
│   ├── ats-optimizer.md
│   ├── output-packager.md
│   ├── form-filler.md
│   ├── gap-analyzer.md
│   └── project-mentor.md
├── .claude/
│   └── commands/
│       ├── analyze-gaps.md          ← /analyze-gaps slash command
│       └── project-mentor.md        ← /project-mentor slash command
├── scripts/
│   ├── gap-analysis.py              ← gap analysis engine
│   └── to-pdf.js                    ← Puppeteer PDF renderer
├── templates/
│   └── resume-template.md           ← resume formatting rules
├── config/
│   ├── google-form.example.md       ← safe template
│   └── google-form.md               ← your real config (gitignored)
├── output/                          ← generated applications (gitignored)
├── analysis/                        ← gap reports (gitignored)
└── projects/                        ← project schematics (gitignored)
```
