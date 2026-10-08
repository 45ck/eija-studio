# PlayIDE: market gaps and ideal customer profile

Research date: **8 October 2026**. Desk research from public surveys, studies and press coverage; no customer has been interviewed. Figures marked *vendor* come from a company that sells a related product. Figures marked *secondary* were read in coverage, not in the original report, and should be checked before quoting. Everything under "Inference" is a reading of the evidence, not a finding. The designed version of this report is published at <https://claude.ai/artifact/QQZ9VJb6ps81GcxFpnPKsy>. It builds on the earlier comparison [PlayIDE vs the field](https://claude.ai/code/artifact/dc30591f-f632-404b-b271-64ec152bbe9e), which covers competitors, AI pull-request acceptance, comprehension debt and cognitive surrender, so those are not repeated here.

## Summary

- **The shared gap.** Enterprise teams, small companies and vibe coders all go from intent (prompts, tickets, chat) straight to code. Nothing between them is both readable by people and binding on the running app. Each group fails in that gap in a different way: enterprise teams in review, small teams in continuity, vibe coders in correctness.
- **The ideal customer.** The tech lead who owns a rules-heavy workflow system (approvals, claims, bookings, onboarding, case handling) that AI agents now edit, at a 20 to 500 person company or in an internal-tools team of a regulated firm.
- **The current audience statement.** Keep "software engineers". Drop "who already know UML" as the entry requirement, and add non-coders (PMs, analysts, ops leads, auditors) as a second seat who read and sign off on the model.

## Sourced findings by group

### Enterprise engineering teams

| Finding | Source |
|---|---|
| In telemetry from about 10,000 developers in 1,255 teams, high AI adoption came with 98% more PRs and 91% more review time, while company-level delivery metrics stayed flat. | [Faros AI, AI Productivity Paradox](https://www.faros.ai/ai-productivity-paradox), July 2025 (*vendor*) |
| AI acts as an amplifier: it improves throughput, but often at the cost of stability when the foundations are weak. | [DORA 2025 year in review](https://dora.dev/insights/dora-2025-year-in-review/) |
| 68% of developers say AI saves them 10+ hours a week; 50% lose 10+ hours a week to organisational friction (up from 33%), led by fragmented knowledge. n=3,500. | [Atlassian State of DevEx 2025](https://www.atlassian.com/blog/developer/developer-experience-report-2025) |
| Architecture documentation is usually out of date (2014, n=147). Keeping it current is still the top documentation challenge in 2025 (n=75, *vendor*). | [Fraunhofer IESE](https://www.iese.fraunhofer.de/content/dam/iese/dokumente/alte-dateien/study_software_architecture_documentation_for_developers_survey-en-fraunhofer_iese.pdf), [IcePanel 2025](https://icepanel.medium.com/state-of-software-architecture-report-2025-12178cbc5f93) |
| Regulated regimes (SOX, PCI-DSS, FDA validation, ISO/IEC 62304) expect traceable, attributable changes; AI-written changes make that harder to show. | [CODE Magazine webinar listing](https://www.codemag.com/event/CP-2026-04) (*industry commentary*) |

### Small companies and startups

| Finding | Source |
|---|---|
| Creation tools churn heavily; retention comes from hosting the live app. Replit grew by selling custom internal software to non-engineers inside companies. | [Sacra interview with a former Replit product leader](https://sacra.com/research/product-engineering-leader-replit-churn-retention-vibe-coding) (one interview) |
| In 2024, copy-pasted lines outnumbered moved (refactored) lines for the first time; duplicated 5+ line blocks rose about eightfold. 211M changed lines. | [GitClear via DevClass](https://devclass.com/2025/02/20/ai-is-eroding-code-quality-states-new-in-depth-report/) (*vendor*, *secondary*) |
| Nearly half of unsuccessful projects miss their goals because of poor requirements management. | [PMI requirements management survey](https://www.pmi.org/learning/library/requirements-management-survey-13449) (older data) |

No good survey of design knowledge loss in small firms was found.

### Vibe coders and non-technical builders

| Finding | Source |
|---|---|
| 63% of AI app-builder users are non-developers. | [Hostinger statistics](https://www.hostinger.com/blog/?p=9016) (*vendor*) |
| A passive scan of 5,600+ public vibe-coded apps (about 4,000 on Lovable) found 2,000+ vulnerabilities, 400+ exposed secrets and 175 cases of exposed personal data, including medical records and IBANs. Most were reachable without authentication, often through missing Supabase row-level security. The authors call the figures a lower bound. | [Escape methodology post](https://escape.tech/blog/methodology-how-we-discovered-vulnerabilities-apps-built-with-vibe-coding/), 29 October 2025 |
| Lovable's missing ownership checks were catalogued as CVE-2025-48757; Wiz found a platform-wide authentication bypass in Base44 in July 2025. | [The Next Web](https://thenextweb.com/news/lovable-vibe-coding-security-crisis-exposed) (*secondary*) |

### Developers as individuals

| Finding | Source |
|---|---|
| 84% use or plan to use AI tools; 46% distrust their accuracy, up from 31%. About 77% say vibe coding is not part of their professional work. n=49,009. | [Stack Overflow 2025 press release](https://stackoverflow.co/company/press/archive/stack-overflow-2025-developer-survey/) |
| The top frustration (66%) is AI output that is "almost right, but not quite"; 45% say debugging AI code takes longer. | [InfoWorld on the 2025 survey](https://infoworld.com/article/4031673/ai-use-among-software-developers-grows-but-trust-remains-an-issue-stack-overflow-survey.html) (*secondary*) |
| 16 experienced developers were 19% slower with AI on their own repositories while believing they were 20% faster. | METR, July 2025, via [eWeek](https://eweek.com/news/news-ai-tools-slow-developer-productivity-study) (*secondary*, small sample) |

### UML use

In Petre's interviews with 50 professional engineers in 50 companies, 35 used no UML, 11 used it selectively, 3 for code generation, 1 retrofitted it and none used it wholeheartedly. Selective users mostly drew class, sequence and activity diagrams; state machines and use cases were rarer. This is an interview corpus, not a representative survey. [UML in Practice, ICSE 2013](https://2013.icse-conferences.org/content/uml-practice.html); [summary](https://neverworkintheory.org/2013/06/13/uml-in-practice-2.html).

## Inference: the ideal customer profile

**Primary: the tech lead who owns a rules-heavy workflow system that AI now edits.**

| | |
|---|---|
| Company | 20 to 500 people: a software company with a workflow product, or an internal-tools or platform team in a larger regulated firm (fintech operations, insurance, health administration, government, education). |
| System | Work where the question is "who may do what, in which state": approvals, claims, bookings, onboarding, case handling, permits, loans. |
| Today | Uses Claude Code, Cursor or Codex daily; reviews more AI PRs than they can read properly; diagrams are on a whiteboard or out of date. |
| Trigger | An AI change silently opened a path (a clerk approving their own claim), or an auditor, customer or new hire asked what the system allows and nobody could answer quickly. |
| Job | "Let the AI change the system fast, and let me prove what changed before it ships." |
| Buyer | Head of engineering or CTO; in regulated firms, risk or platform budget can co-fund. |
| UML | Reads a state machine or sequence diagram on sight; may never have drawn one. |

**Secondary: agencies and consultancies building workflow apps for clients.** They repeat similar builds, must hand over something the client can read, and benefit from client sign-off on behaviour.

**Second seat, not first buyer: non-coders who approve behaviour.** PMs, analysts, ops leads, auditors, and founders whose vibe-coded app now has paying users. They read diagrams, run Simulate and approve, and arrive through the primary customer.

**Not for, for now:** hobby vibe coders and landing pages; CRUD-only apps where reading the diff is the review; algorithms, ML pipelines, games and infrastructure code; teams wanting a full low-code runtime.

## Inference: the current audience statement

| Part | Verdict | Reason |
|---|---|---|
| Software engineers as the primary user | Keep | They own the systems and feel the review pain; professionals reject one-shot vibe coding for their work. |
| "Who already know UML" | Change | Too small a gate (Petre), and the state machine, PlayIDE's strongest view, is one many engineers have never drawn. Target engineers who think in states and roles, and show them UML they can read. |
| "Startups and enterprise" | Narrow | Choose by system type (rules-heavy workflow apps) and company size (20 to 500) first. |
| "System design plus frontend design" | Keep, reorder | Lead with behaviour and permissions; the screen designer matters because screens are bound to the rules, not as a Figma competitor. |
| "Beats other tools on robustness" | Make concrete | The app cannot disobey the model; an AI change shows as a diagram diff; permission questions get exact answers. |
| Non-technical users | Add as second seat | A growing share of AI-builder users and the group whose apps fail on access rules. They can read a diagram but not code. |

## Inference: product consequences

Ordered by value to the primary customer.

1. **Lead with reviewing an AI change.** The first screen should be an AI change arriving as a diagram diff with the risky part marked, plus a reachability question such as "can anyone now reach Approved without a manager?". Exists: plan mode, preview and the checks ring ([ADR-0156](../adr/0156-chat-plan-mode-proposes-typed-steps.md), [ADR-0157](../adr/0157-drawn-edits-and-checks-ring.md)). To build: a diff-first entry screen.
2. **A who-can-do-what view.** Show the role × action × state permission matrix the kernel already enforces, and flag changes to it. This is what vibe-coded apps get wrong and what auditors ask for.
3. **Start from an existing codebase.** Every target customer already has an app; read-only intake is the on-ramp, as the [self-dogfood acceptance](../engineering/SELF-DOGFOOD-ACCEPTANCE.md) already requires for EIJA itself.
4. **Reader mode for people who do not know UML.** The same diagrams with plain-language captions, Simulate one click away, and an approve action; no editing tools in view. Approval stays owner-only as the kernel requires.
5. **Meet teams in their pull requests.** Post the model diff and check results into the PR with a link into PlayIDE, rather than asking teams to stop using PR review.
6. **A readable change record.** Goal, model diff, approver and the checks that ran on which version, described as evidence and never as compliance or certification.
7. **Show where the guarantees stop.** Code outside the model gets a normal diff marked as outside the model's guarantees ([ADR-0150](../adr/0150-build-apps-from-the-model-with-a-kernel-oracle.md) scope).
8. **One domain pack aimed at the beachhead**, such as an approvals or claims flow, so the demo and sample model look like the buyer's own system.

## How to test it

1. Ten interviews with tech leads of workflow systems about the last AI change that touched permissions or states. If fewer than half can name one, the trigger is weaker than assumed.
2. A seeded-defect review test: the same AI change as a code diff and as a model diff, with one planted permission bug; measure detection and time. This fits the [V&V protocol](2026-10-02-vv-protocol.md).
3. A sign-off test: three PMs or analysts approve or reject a change in reader mode only, then explain what changed.
4. An expressiveness test on one real workflow app from a design partner.
5. A willingness-to-pay check: what the buyer spends today on review, audits or rework for that system.

Until these run, this profile is a hypothesis and the [product thesis](../engineering/PRODUCT-THESIS.md) audience decision stands as the owner recorded it.
