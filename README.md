# Career Agent

An AI-powered job application pipeline built on [Claude Code](https://claude.ai/code). Paste a job
URL and it automatically customizes your resume, writes a cover letter, scores keyword coverage,
generates a PDF, and logs the application to a Google Form tracker — all in one shot.

Bonus tools: `/analyze-gaps` surfaces recurring skill gaps across every application you've run,
and `/project-mentor` generates a step-by-step portfolio project schematic to close those gaps.

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

Both commands are available as soon as you open the project in Claude Code.

**`/analyze-gaps`** — Scans every application in `output/`, tallies recurring skill/keyword gaps
across all of them, and writes a ranked report to `analysis/`. Use this after you've run 10+
applications to see patterns.

```
/analyze-gaps
```

**`/project-mentor`** — Reads the latest gap analysis and generates a full production-grade
portfolio project schematic targeting your highest-priority gaps. Saves to `projects/`.

```
/project-mentor          ← picks the project that covers the most CRITICAL gaps
/project-mentor Go       ← centers the project on a specific technology
```

Each schematic includes: architecture diagram, tech stack justification, phase-by-phase build
plan with exact commands, pre-written resume bullets, and interview talking points.

---

## Pipeline Architecture

```
Job URL
  │
  ▼
[Pre-flight gate]         ← experience check, salary check, role type check
  │
  ▼
[1] Job Analyzer          ← scrapes posting, extracts skills/requirements/keywords
  │
  ▼
[2] Company Researcher    ← researches culture, mission, recent news
  │
  ├──────────────────────────────────┐
  ▼                                  ▼
[3] Resume Customizer     [4] Cover Letter Writer
  │                                  │
  └──────────────┬───────────────────┘
                 ▼
           [5] ATS Optimizer    ← scores keyword match, rewrites until ≥80% coverage
                 │
                 ▼
           [6] Output Packager  ← saves all files to output/<Company>-<date>/
                 │
                 ▼
           [7] PDF Generator    ← renders resume.pdf + cover-letter.pdf via Puppeteer
                 │
                 ▼
           [8] Form Filler      ← submits Google tracking form via curl
```

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
