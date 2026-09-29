# Personas and jobs to be done

Lane `lane/ux-research`. Date 2026-09-29. Source ids (`AIC§2.12`, `REV§2`, `V2`) are defined in [research/SYNTHESIS.md](research/SYNTHESIS.md) section 1. Task ids (T01 to T14) are in [../../design/brief.json](../../design/brief.json).

## 0. Decisions first

| # | Decision | Basis |
|---|---|---|
| 1 | Five personas. **P1, the agent-change reviewer, is the ICP** (ideal customer profile) for the OSS project. P5, the 10-minute evaluator, is the adoption gate for everyone else. | Section 2 |
| 2 | Personas are **roles one person can hold**, not people. The POC has a single local owner (ADR-011), so P1 or P2 typically also holds the owner role that approves and applies. | ADR-011 |
| 3 | **These personas are literature-derived hypotheses.** No interview, observation or survey of Studio users exists. Every frequency, pain ranking and success target is labelled HYPOTHESIS unless it cites a source. | Section 1 |
| 4 | The AI agent is an **actor, not a persona**. It has no goals the interface serves and no authority to approve or apply. | Invariants I1, I4 |
| 5 | Today the POC supports one synthetic excursion workflow and two typed edits under a frozen vocabulary (ADR-003; README). The ICP is a target; until a second domain exists, the usable personas are P5 and learners. | README; ADR-003 |

## 1. Method and limits

- Built from the ten research dossiers. Behaviour, pains and numbers cite them. Where a persona statement is my inference from the dossiers, it says HYPOTHESIS.
- Trust and outcome evidence comes from studies of developers using general AI coding tools, not from users of a semantic review tool: METR 2025 (n=16, 19% slower, early-2025 tools), METR 2026 update (intervals include zero; the authors call the signal unreliable), Anthropic RCT (n=52, mostly junior, immediate quiz), Perry et al. 2023, Stack Overflow 2025 and DORA 2025 self-reports (AIC§2.12, §3). None tested a tool that shows evidence with UNKNOWN visible (AIC§2.12).
- Frequencies (daily, weekly, rare) are assumptions about a team that runs coding agents on domain rules; they are inputs to KLM weighting (LAW§2.4), which is valid for expert, routine tasks only.
- Validation plan: section 6.

## 2. Ideal customer profile

**Hypothesis.** An engineer or tech lead on a small team that already lets coding agents change business rules with consequences (who may approve what, what happens to a record, what is sent to whom), who is accountable for those changes, and who cannot tell from a line diff what a change means or what else it touches.

| Attribute | Value | Evidence or label |
|---|---|---|
| Who | Engineer, tech lead or architect who reviews and answers for agent-authored change | HYPOTHESIS; 31% of Stack Overflow 2025 respondents use agents regularly and 3.1% highly trust accuracy (AIC§3, self-report) |
| Situation | Agent changes are frequent and large; reviewers reconstruct meaning from scattered edits | Understanding the change is the main review challenge (REV§2); rejected agent PRs tend to be larger and touch more files (AIC§2.9, abstract-level) |
| Existing workaround | Line diff, CI status, an LLM summary, a spec file | Kiro, Spec Kit, Devin Review, CodeRabbit (AIC§2.6-2.7, REQ§2.1, REV§2) |
| Trigger | A change that alters a permission, state or journey and must be defended later | HYPOTHESIS |
| Values | Knowing what is not known; a decision record; keyboard speed | HYPOTHESIS; DEV§2 craft benchmarks |
| Disqualifiers | Wants a universal compiler or arbitrary repository ingestion (not supported); needs multi-user or institutional sign-off (ADR-011); wants AI to auto-approve (invariant) | README; ADR-011; I4 |
| Adoption signal | Public spec tools draw large followings even with reported review pain (Spec Kit 139,274 stars, OpenSpec 70,589 on 2026-09-29, GitHub API) | REQ§4; pull is real, fit for EIJA is not shown |

## 3. Personas

Each block: role, jobs (when / I want / so I can), frequency, context, pains with evidence, success measure, tasks. Success measures marked PREDICTION or STUDY are targets, not results.

### P1. Agent-change reviewer (ICP)

| Field | Content |
|---|---|
| Role | Engineer or tech lead who reviews changes an AI agent proposed to an executable model and, in the POC, may also be the owner who approves and applies |
| Jobs | **J1** When an agent proposes a change, I want to see what it means in domain terms, so I can judge it without rebuilding it from a diff. **J2** When a change lands, I want to see what else it touches and what is not known, so I do not approve a hidden consequence. **J3** When I approve, I want the exact revision and every UNKNOWN in front of me, so my decision is defensible. |
| Frequency | Daily (HYPOTHESIS) |
| Context | Desktop, keyboard-heavy, alongside an editor and terminal; sessions interleave with other work (LAW§2.6 on interruption) |
| Pains | Line diffs make meaning a reconstruction task (AIC§0 #1). Approval prompts train reflex approval: 93% approved (V2, vendor-reported). Perceived and measured effect of AI diverge (AIC§2.12). Summaries written by a model are not checkable (REV§2). |
| Success measure | STUDY: seeded defects found; UNKNOWN items misread as PASS (target zero); calibration (confidence versus correctness); time to reach the first evidence. PREDICTION: at most 4 top-level chunks per change (LAW§2.5) |
| Tasks | T02, T03, T08, T09, T12 |
| Confidence | Pains: medium (self-report and small trials); success targets: untested |

### P2. Domain-model owner (architect)

| Field | Content |
|---|---|
| Role | Owns the ubiquitous language and the DDD structure (contexts, aggregates, entities and value objects, terms); also holds the owner role for structural decisions |
| Jobs | **J4** When the language changes, I want every dependent state, journey, test and requirement shown, so nothing drifts silently. **J5** When I restructure the model, I want the diagram and the tree to stay in step with the executable model, so I do not hand-synchronise. **J6** When something becomes suspect, I want the cause shown and a recorded way to clear it. |
| Frequency | Weekly (HYPOTHESIS) |
| Context | Long sessions on the tree and diagram; mouse plus keyboard; needs both drag and a non-drag path |
| Pains | Knock-on viscosity: one conceptual change forces many manual edits (LAW§2.7). Hidden dependencies behind connectors (DGM§3.2). Visual editing gets harder as models grow (Structurizr, vendor argument, DGM§2.8). Spec drift is described as the normal failure (Kiro docs, REQ§2.1). Suspect flags cleared by hand erode trust (REQ§2.2). |
| Success measure | STUDY and prototype: zero silent knock-on edits (every changed artefact listed in the ripple); edits needed to restore consistency after one rename (LAW§2.7 oracle: 0 with full propagation); tree depth at most 4 |
| Tasks | T04, T05, T11, T01 |
| Constraint | Only operations in the frozen vocabulary are executable (ADR-003); drops outside it are refusals with a reason |

### P3. Requirements and product owner

| Field | Content |
|---|---|
| Role | States intent ("Let teachers sign off excursions"), chooses among interpretations, owns acceptance criteria and persona or ICP statements |
| Jobs | **J7** When I state an intent, I want ambiguity resolved explicitly by my choice, so a model never picks a meaning for me. **J8** When I ask "what has no evidence?", I want the answer in one step. **J9** When I ask AI for options, I want only grounded items, with anything new labelled. |
| Frequency | Weekly (HYPOTHESIS) |
| Context | Less tool-heavy; reads more than edits; may not know the kernel vocabulary |
| Pains | Verbose spec artefacts: one reported small bug became 4 user stories and 16 criteria (n=1, REQ§2.1). Requirements with no linked test are hard to find without a widget (REQ§2.2). Prompt-only control has an articulation barrier (ADC§2.13, UNVERIFIED as a finding). |
| Success measure | STUDY: time to find requirements with no evidence; wrong-meaning selections (target zero); acceptance criteria written in a constrained form (EARS-style or Given/When/Then) that the kernel can parse (REQ§5 #7) |
| Tasks | T01, T13, T14 |
| Note | The baseline already makes the ambiguous request choose among interpretations and blocks unsupported teacher final approval (README) |

### P4. Verification and QA engineer

| Field | Content |
|---|---|
| Role | Runs verification, reads proofs, model checks, property tests and mutation results, decides whether evidence supports a claim |
| Jobs | **J10** When a check runs, I want to know what it covered, what it assumed and what it did not cover, so I never read "pass" as "proved". **J11** When a check fails, I want the failing step in a replayable form pinned to the model action. **J12** When evidence is stale, I want to see it stale, not replaced by a spinner. |
| Frequency | Daily to weekly (HYPOTHESIS) |
| Context | Dense tables and traces; comfortable with formal tools; will notice a rounded-up verdict |
| Pains | Skipped required checks count as success on GitHub; Codecov defaults `if_not_found` to success (REV§4). Merged coverage numbers hide the uncovered part (REV§6). Full state graphs become unreadable (REV§5). Bounded results without bounds mislead (REV§5). |
| Success measure | STUDY: correct reading of the four-slot coverage row (HYPOTHESIS H1 in REV§9); time to locate the failing step; UNKNOWN recall |
| Tasks | T06, T07, T14, T12 |

### P5. OSS evaluator (10-minute adopter)

| Field | Content |
|---|---|
| Role | An engineer deciding in a short session whether the project is worth trying |
| Jobs | **J13** When I open the Studio for the first time, I want to see one real change reviewed by meaning, with UNKNOWN shown, so I understand the point without reading docs. **J14** I want install and first run to need no build step, so I can try it now. |
| Frequency | Rare per person, decisive for adoption (HYPOTHESIS). The "10 minutes" figure is the task framing, not a measured behaviour |
| Context | Fresh install; no domain knowledge; skims. First impressions form within 50 ms to 500 ms and correlate (Lindgaard 2006, excerpt-only; SLP§2.3) |
| Pains | Text-heavy first screens: users read at most about 28% of words on an average page (NN/g, 2005 data; SLP§5). Baseline first screen is a hero with about 404 static words across the page (MEASURED, SYNTHESIS C3). |
| Success measure | STUDY: time to first reviewed change; first-click success; 50 ms and 500 ms appeal ratings (SLP§4.4); completion without documentation. PREDICTION: onboarding of at most a few steps, each with an action (DEV§2.3, VS Code guidance) |
| Tasks | T10, T09 |
| Install fact | Python 3.11 or later; no Node build; dependencies not vendored (README) |

## 4. Authority map

| Capability | P1 | P2 | P3 | P4 | P5 | AI agent | Provider |
|---|---|---|---|---|---|---|---|
| Propose (via prompt lane) | yes | yes | yes | yes | yes | is the proposer | supplies text only |
| Direct edit through kernel (no provider) | yes | yes | limited | no | try only | no | no |
| Read evidence | yes | yes | yes | yes | yes | read-only context | no |
| Clear a suspect item (logged) | owner role | owner role | no | no | no | no | no |
| Approve exact revision | owner role | owner role | no | no | no | never | never |
| Apply to baseline | owner role | owner role | no | no | no | never | never |

Rows are design intent, not implemented permissions; the POC has one local owner and synthetic actors (ADR-011). "Owner role" means whoever the single local owner is.

## 5. Task-to-persona map

| Task | Name | Primary | Also | Frequency (HYPOTHESIS) |
|---|---|---|---|---|
| T01 | Create a change case and select a meaning | P3 | P2 | weekly |
| T02 | Review an agent's change by meaning | P1 | P2 | daily |
| T03 | See the ripple of a change | P1 | P2, P4 | daily |
| T04 | Edit a state diagram by drag and drop | P2 | | weekly |
| T05 | Edit the ubiquitous-language tree | P2 | P3 | weekly |
| T06 | Run and read verification evidence | P4 | P1 | daily |
| T07 | Inspect a counterexample | P4 | P1 | weekly |
| T08 | Approve and apply the exact revision | P1 | P2 | daily |
| T09 | Find anything via the command palette | P1 | all | daily |
| T10 | First-run onboarding | P5 | | rare |
| T11 | Resolve a stale or suspect item | P2 | P1 | weekly |
| T12 | Map a concept to code and check drift | P1 | P4 | weekly |
| T13 | Ask AI to propose at a selected element | P3 | P2 | weekly |
| T14 | Find gaps: items with no evidence | P4 | P3 | weekly |

## 6. Validating the personas

Nothing above is validated. Minimum plan (protocol only; nothing run):

1. Five to eight semi-structured interviews with engineers who review agent-authored changes (formative rounds of about 5 find problems but do not estimate prevalence; LAW§2.10). Questions on how they decide today, what they do with unknowns, and what they would refuse to delegate.
2. Observe the baseline Studio on the excursion tasks; record time, errors and UNKNOWN misreads to calibrate the KLM predictions (LAW§2.4 validity: expert, error-free only).
3. Update this file; personas whose pains are not confirmed are removed rather than kept.
4. Recruit a keyboard-only cohort and a screen-reader cohort for P2 and P4 tasks (DGM§5 #10).

## 7. Open questions

- Is the reviewer the same human as the owner in real teams? The POC assumes yes (ADR-011); the answer changes the decision-surface design.
- Does the ICP exist without a second supported domain? Unknown; ADR-003 restricts the current vocabulary.
- Which of P2 and P3 will use the tree first? Unknown; the tree is designed for P2 with P3 reading.
