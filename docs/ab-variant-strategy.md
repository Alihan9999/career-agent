# A/B Resume Variant Strategy

The pipeline generates one of five resume variants per application. The Application Decision Agent chooses the variant based on the role family and the target company; the Resume Customizer + Resume Narrative Strategist execute the variant; the Rejection Learning Agent tracks per-variant conversion rates over time.

The goal is not "test five variants and pick the winner." It is "use the right resume for the right job." Aggregate conversion data informs which variants work for which role classes, NOT a single universal winner.

---

## Default shape (updated 2026-05-15)

After the Fabletics 2026-05-14 run, the user explicitly rejected the previous Variant B/C/D shape (headline + Selected Achievements block + Projects above Experience). New defaults for Variants B/C/D:

1. Header (`# NAME` + contact line)
2. **Headline** — one bold line, **80-90 chars (hard max 95)** to fit one line at 9.5pt Arial without wrap
3. `## Professional Experience` (Experience above Projects)
4. `## Projects` (not "Projects")
5. `## Technical Skills`
6. `## Education`

**No "Selected Achievements" block by default.** The Experience and Projects bullets carry the anchor metrics already — a separate Achievements block restates them and bloats the top of the resume. Add an `**Achievements**` block (no "Selected" prefix) only when the user explicitly requests it AND each line adds information the body sections don't surface.

**Section labels never carry a "Selected" prefix.** Use `## Projects` not `## Projects`.

This is a hard departure from the v2 spec written in May 2026 — keep the new shape as default until conversion data indicates otherwise.

---

## Variant A — ATS-Heavy

**Lead story:** "This person matches every technical line item on the JD."

**Use for:**
- iCIMS-strict ATSes (literal token matching, JS != JavaScript).
- Taleo-based enterprise pipelines.
- Workday at companies with >5000 employees and centralized HR screening.
- Government tech, banking, defense, healthcare IT.
- Anywhere the JD is a token list rather than a narrative.

**Section order:** Header (no headline) -> Professional Experience -> Projects -> Technical Skills -> Education.

**Bullet posture:** every bullet front-loads the JD's exact tokens. Bullets are long-ish (20-25 words) to fit more matches. Tilde-metrics are tolerated here because the audience scans for tokens, not narratives. Acronym pairs explicit.

**Skills section:** wide — all categories, every tool. Comma-dense lines for full-text search.

**Cover letter:** mirror the JD's bullet structure; use "Re: <Exact Job Title>"; mention every must-have requirement at least once.

**Anti-pattern:** do NOT use for AI-infra startups, design-forward companies, or Greenhouse roles where a recruiter reads the resume in 6 seconds.

---

## Variant B — Recruiter-Impact-Heavy

**Lead story:** "Recruiter mentions this candidate to the hiring manager by name."

**Use for:**
- FAANG-level companies (when a referral path is also being pursued).
- Brand-name startups (Stripe, Datadog, Vercel, Tailscale, Cloudflare).
- AI labs (Anthropic, OpenAI, Cohere, Mistral) — sometimes paired with Variant D.
- Design-forward / developer-tools companies.
- Any company where the recruiter scans 50+ resumes per day and the 6-second scan is the binding constraint.

**Section order:** Use the default shape (Header + Headline → Professional Experience → Projects → Skills → Education). **No Achievements block by default.**

**Headline:** pulled from `data/headline-bank.md` Variant B set (B1-B4), 80-90 chars. Names role + 3 anchors. Example (B1):
```
**Platform Engineer | K8s operator in Go, ArgoCD GitOps, $30k/month FinOps platform**
```

**Bullet posture:** shorter bullets (15-20 words). Strong verbs, named systems, exact metrics (no tildes). Bold sparingly.

**Skills section:** Selected Stack (8-12 tools per row) + Languages line. Narrow.

**Cover letter:** strong hook on a specific JD detail; one story deep; closing question that exposes operational thinking.

**Anti-pattern:** do not use for Taleo or iCIMS-strict — the headline gets ignored by literal token matchers, costing keyword density for no recruiter benefit. Use Variant A for those.

---

## Variant C — Platform Engineering Narrative (Kubernetes + GitOps emphasis)

**Lead story:** "This person runs production Kubernetes infrastructure with the same patterns the target company uses (Go operator, ArgoCD app-of-apps, OpenTelemetry to Datadog)."

**Use for:**
- Platform Engineer / SRE roles at infra-native companies (Grafana, Datadog, Tailscale, Vercel, Cloudflare, Cockroach, Fabletics-style hybrid EKS + on-prem).
- Any role where the homelab's K8s + GitOps + OTel stack maps directly to the JD's primary stack.

**Section order:** Use the default shape (Header + Headline → Professional Experience → Projects → Skills → Education). **No Achievements block by default.** Experience leads — the user explicitly rejected Projects-first ordering on 2026-05-14 because it bloated the top of the resume and read as "junior / new grad" to anyone expecting traditional resume shape.

**Headline emphasis:** Platform Engineer (NOT "Platform / SRE Engineer" — drop the SRE half because SRE-titled family is 0/30 in conversion data). Lead with K8s + GitOps + OTel anchors. Pull from `data/headline-bank.md` C1-C3.

**Renaming:** "Homelab Platform" → "Production Kubernetes Platform (Homelab)" in the Projects section header to give the project weight without overclaiming.

**Bullet posture:** Experience bullets carry the paid-work anchors (200+ apps, 2.5 TB/day Splunk, $30k/month FinOps, VMware-to-AWS migration). Projects section has 2 bullets max — the homelab cluster + operator combo. No 0rca/Career Agent in Variant C (those are Variant D).

**Anti-pattern:** do not use for AI-infra-led targets — Variant D is stronger there. Do not use the old projects-first shape — verified to read poorly to the user / candidate themselves.

---

## Variant D — Automation / Project-Heavy

**Lead story:** "This person is an LLM-infrastructure / multi-agent engineer who also has 3 years of DevOps."

**Use for:**
- Anthropic-adjacent companies (Anthropic itself, Claude API integrations, MCP-leveraging companies).
- OpenAI-infra, OpenAI Codex Platform, OpenAI Operator.
- AI-native startups building agent platforms.
- Developer-tools companies with active AI angles (LangChain, LlamaIndex, Tavily, etc.).

**Section order:** Use the default shape (Header + Headline → Professional Experience → Projects → Skills → Education). **No Achievements block by default.** Projects section includes 0rca first, Career Agent second, Homelab third — but stays at the bottom of the resume per the 2026-05-14 user preference.

**Headline emphasis:** "LLM-Infrastructure / Multi-Agent" positioning. Pull from `data/headline-bank.md` D1-D3. Example (D1):
```
**LLM-Infrastructure Engineer | 28-agent DAG orchestrator, 9-agent MCP pipeline, K8s in Go**
```

**0rca framing:** lead with "Designed a DAG-based task orchestration engine running up to 4 parallel agent streams across a 3-tier hierarchy of 28+ agents" — this is the wow item.

**Career Agent framing:** lead with "Built a 9-agent MCP pipeline orchestrating job application workflow via Claude Code and MCP servers."

**Experience section:** compressed to 3-4 of the strongest bullets. The AI projects do the heavy lifting.

**Anti-pattern:** do not use for traditional enterprise SRE — the AI-projects-first framing will be filtered as off-topic.

---

## Variant E — Conservative Enterprise DevOps

**Lead story:** "This person operates at enterprise scale across heterogeneous infrastructure."

**Use for:**
- Enterprise SRE roles at >5000-employee companies (HomeDepot, FICO, KPMG-style).
- Government tech (USDS, 18F-adjacent, defense IT).
- Banking, insurance, healthcare IT.
- Legacy-aware infrastructure roles where AIX / Solaris / Octopus Deploy / ServiceNow is a POSITIVE.

**Section order:** Header (no headline) -> Professional Experience -> Projects -> Technical Skills -> Education. Traditional shape.

**Bullet posture:** lead with the 1,000+ multi-OS server bullet and the Splunk SIEM cluster bullet. The 200+ apps platform is second. Tilde-metrics are tolerated.

**Skills section:** wide categorization, AIX / Solaris / OpenShift / Octopus Deploy retained as visible. These are negatives at startup targets, positives here.

**Projects section:** keep professional projects (CI/CD Onboarding Platform, AWS Cost Optimization Engine, Splunk Deployment Automation, Centralized Observability) prominent. Homelab and 0rca de-emphasized but present.

**Anti-pattern:** do not use for startup or AI-infra targets — the legacy-friendly framing tanks the Recruiter Scan score there.

---

## Variant selection table

| Target | Variant | Reasoning |
|---|---|---|
| Stripe Payments Infra (FAANG-tier) | B (paired with referral attempt) | Brand-name; 6-second scan; recruiter screens hard |
| Datadog SRE | C | Infra-native; Kubernetes + OTel + Go is the binding match |
| Anthropic MCP / Claude infrastructure | D | AI-infra; 0rca + Career Agent are the wow items |
| Grafana Labs Platform Productivity | C | Infra-native; Backstage gap exists but homelab is the strongest signal |
| Tailscale Security Infra | C with security overlay | Infra-native; Istio mTLS + WireGuard from homelab are the bridge |
| Vercel SRE | B or C | Brand-name; Variant C if Kubernetes-heavy, B otherwise |
| Spotify Backstage SRE | C with AI overlay | Infra-native + Backstage product is AI-adjacent right now |
| HomeDepot SRE | E | Enterprise; 1,000+ servers and Splunk SIEM cluster are positives |
| Microsoft Substrate SRE | E | Enterprise + Microsoft-internal tooling expectations |
| FICO SRE | E | Enterprise; legacy stack expected |
| LaunchDarkly Platform | C | Infra-native, Datadog gap to flag |
| GitLab Platform | C | Infra-native; GitLab actually loves the GitLab CI/CD platform bullet |
| Coinbase Corp Sec | C with security overlay | Crypto + infrastructure + security |
| OpenAI Infra Sec | D + referral | AI-native + security; cold app low ROI without referral |
| KPMG Cloud Eng | E | Enterprise consulting |
| Ramp DevOps | B (with Postgres in flagged gaps) | Brand-name fintech; recruiter scan matters |
| ElevenLabs SRE | C or D | AI-native depending on what the JD foregrounds |

---

## Tracking and learning

Each application logs `resume_variant` (and `cover_letter_variant`) in `data/applications.jsonl`. The Rejection Learning Agent computes per-variant conversion rate weekly.

After 30 outcomes per variant (or 90 days of data, whichever is sooner), surface the per-variant table:

```
Variant A: X/N = Y% (n role-family-fit-adjusted)
Variant B: X/N = Y%
Variant C: X/N = Y%
Variant D: X/N = Y%
Variant E: X/N = Y%
```

Adjust the variant selection table above based on what works. If Variant C converts at 8% and Variant B converts at 2%, route more borderline cases to Variant C. If a variant is unused after 60 days (<3 applications), prune it or merge it with the closest neighbor.

---

## Cross-cutting rules (all variants)

- Never use em dashes.
- Never modify the current employer's title ("DevOps Engineer" at the candidate's current employer).
- Never invent metrics, dates, system names, or claims.
- Every bullet must hit at least 4 of 6 proof elements (verb / system / mechanism / scale / outcome / impact).
- Resume is 1 page.
- ATS score >= 80%.
- Quality Gate minimum scores must pass before output packaging (see `agents/resume-quality-gate.md`).
