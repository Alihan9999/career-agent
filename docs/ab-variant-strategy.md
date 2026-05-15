# A/B Resume Variant Strategy

The pipeline generates one of five resume variants per application. The Application Decision Agent chooses the variant based on the role family and the target company; the Resume Customizer + Resume Narrative Strategist execute the variant; the Rejection Learning Agent tracks per-variant conversion rates over time.

The goal is not "test five variants and pick the winner." It is "use the right resume for the right job." Aggregate conversion data informs which variants work for which role classes, NOT a single universal winner.

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

**Section order:** Header + 1-line Headline + Selected Achievements (3 lines) -> Professional Experience -> Selected Projects -> Technical Skills -> Education.

**Headline format:**
```
**Platform / SRE Engineer | Go Kubernetes operator in production, GitOps across 12 Helm charts, $30k/month cost optimization platform**
```
One line, ~120 characters, three concrete anchors.

**Selected Achievements format:**
```
**Selected Achievements**
- Production Go Kubernetes operator (kubebuilder) running 60s reconciliation in a homelab K8s platform; 12 Helm charts deployed via ArgoCD GitOps; OpenTelemetry pipeline to Datadog across 6 services
- Scaled developer-platform CI/CD onboarding from 10 to 200+ application teams via a ServiceNow-triggered intake; eliminated manual setup org-wide
- Built AWS cost optimization platform (Lambda + EventBridge + Terraform) cutting non-production compute by $30k/month
```
Three lines. Three different domain wins. Each line names a wow item.

**Bullet posture:** shorter bullets (15-20 words). Strong verbs, named systems, exact metrics (no tildes). Bold sparingly.

**Skills section:** Selected Stack (8-12 tools) + Languages line + Education. Narrow.

**Cover letter:** strong hook on a specific JD detail; one story deep; closing question that exposes operational thinking.

**Anti-pattern:** do not use for Taleo or iCIMS-strict — the headline + Selected Achievements get ignored by literal token matchers, costing keyword density for no recruiter benefit.

---

## Variant C — SRE / Platform Narrative

**Lead story:** "This person runs production-grade Kubernetes infrastructure on their own time the way a senior SRE does at work."

**Use for:**
- SRE roles at infra-native companies (Grafana, Datadog, Tailscale, Vercel, Cloudflare, Cockroach).
- Platform Engineer roles where Kubernetes / GitOps / OpenTelemetry are core.
- Any role where the homelab + Go operator + ArgoCD + OTel stack is closer to the job than the paid-work history is.

**Section order:** Header + Headline + Selected Achievements -> Selected Projects (Homelab first, renamed "Production Kubernetes Platform (Homelab)") -> Professional Experience -> Technical Skills -> Education.

**Headline emphasis:** Platform / SRE positioning; lead with Kubernetes / Go / GitOps / OTel.

**Projects come BEFORE Experience.** This is the unusual choice and the variant's defining move. The homelab is positioned as the strongest evidence of capability for THIS role. paid-work bullets are still present but framed as "in addition to the homelab work."

**Renaming:** "Homelab Platform" -> "Production Kubernetes Platform (Homelab-Hosted)" to give it weight. "Career Agent" -> "Multi-Agent MCP Pipeline" if the role is AI-infra.

**Bullet posture:** the first 2 project bullets are the wow items (Go operator with kubebuilder; full GitOps via ArgoCD app-of-apps; OTel Collector to Datadog). The first Experience bullet is the 200+ apps platform.

**Anti-pattern:** do not use for enterprise SRE roles where the recruiter expects a traditional resume shape — they will read "Projects first" as "junior / new grad."

---

## Variant D — Automation / Project-Heavy

**Lead story:** "This person is an LLM-infrastructure / multi-agent engineer who also has 3 years of DevOps."

**Use for:**
- Anthropic-adjacent companies (Anthropic itself, Claude API integrations, MCP-leveraging companies).
- OpenAI-infra, OpenAI Codex Platform, OpenAI Operator.
- AI-native startups building agent platforms.
- Developer-tools companies with active AI angles (LangChain, LlamaIndex, Tavily, etc.).

**Section order:** Header + Headline + Selected Achievements (3 project-led lines) -> Selected Projects (0rca first, Career Agent second, Homelab third) -> Professional Experience -> Technical Skills -> Education.

**Headline emphasis:** "AI-infra / multi-agent / MCP" positioning. Example: "LLM-Infrastructure & Platform Engineer | 28-agent DAG orchestration, 9-agent MCP pipeline, production Kubernetes platform"

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

**Section order:** Header (no headline) -> Professional Experience -> Selected Projects -> Technical Skills -> Education. Traditional shape.

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
