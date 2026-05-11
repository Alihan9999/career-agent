# ATS Profile: iCIMS

iCIMS Copilot scores Role Fit by literal token matching against the job
description. "JS" and "JavaScript" are different tokens; "K8s" and
"Kubernetes" are different tokens. Both must appear for full match.

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
- Text boxes
- Embedded fonts that don't render to plain text on extraction

## Required Constructs
- Standard section headings: "Experience", "Education", "Skills", "Projects"
- Reverse-chronological work history
- Plain hyphen bullets

## Keyword Expansion (CRITICAL for iCIMS)
- **Always include both acronym and full term** when both are common terms.
  Don't pick one — iCIMS's Role Fit score drops noticeably if only one form
  appears. Required pairs:
  - JavaScript (JS), TypeScript (TS) — write both forms at least once
  - Kubernetes (K8s)
  - Site Reliability Engineering (SRE)
  - Continuous Integration / Continuous Deployment (CI/CD)
  - Infrastructure as Code (IaC)
  - Service Level Objective (SLO), Service Level Indicator (SLI)
  - Amazon Web Services (AWS), Google Cloud Platform (GCP), Microsoft Azure
  - PostgreSQL (Postgres)
  - Application Programming Interface (API), GraphQL, REST
- Match the exact form of the job posting first; add the alternate form
  parenthetically once

## Parser Risk Flags
- iCIMS's keyword scorer ignores formatting (bold, italic), so don't rely on
  emphasis to surface a term — the literal token has to be present
- Avoid concatenated tech ("AWS/GCP", "CI/CD-tooling") — iCIMS treats these
  as single tokens that won't match either alternative; write
  "AWS, GCP" or "CI/CD tooling" (separated)
