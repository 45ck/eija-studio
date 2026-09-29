# Content design, microcopy and onboarding

Lane `lane/ux-research`, aspect `content-onboarding`. Date 2026-09-29. Status: proposed; the decision record is [HCI-ADR-0065](../../adr/0065-hci-content-onboarding.md). Machine-readable task flows: [design/tasks/onboarding-flows.json](../../../design/tasks/onboarding-flows.json).

Scope: the words in the Studio that developers use every day (labels, statuses, notices, errors, empty states, definitions, first run). Not README, marketing or docs pages. Personas and frequencies are hypotheses ([personas-and-jtbd.md](../personas-and-jtbd.md)). Every number is labelled MEASURED (I ran it or counted it; method stated), PREDICTION (model output with constants and band) or a design target (a hypothesis of ours). No user-benefit claim is made; no user study has run.

Source ids: `S1` to `S31` are pages I opened on 2026-09-29 (section 13). `R:` is a file in this repository. `LAW§`, `DEV§`, `SYN§`, `PRI§` point into the research dossiers and are defined in [SYNTHESIS.md](../research/SYNTHESIS.md).

## 0. Decisions first

| # | Decision | Confidence | Main evidence |
|---|---|---|---|
| D1 | **Vocabulary is the ubiquitous language.** Terms come from `docs/architecture/ARCHITECTURE.md`. A vocabulary lint bans the baseline's variant spellings (that part follows S12 and S17). **Hypothesis, not evidence-backed:** kernel words (PASS, FAIL, CONFLICT, STALE, UNKNOWN, NOT_RUN, BLOCKED, stage names) are printed verbatim in the monospace family so a reader can grep them. S12 does not address user-visible text; S16 and S4 argue against jargon and obscure codes; no source measures the reading cost of upper-case tokens. The study tests it (ONB-1 arm C, H-ON7). The owner's act keeps the kernel verb Approve, always with its object; a distinct owner verb was scored and rejected in HCI-ADR-0065 (Authorise diverges from the kernel's `approve` capability and APPROVED stage; Sign off is the ambiguous word the sample resolves), with a revert condition (H-ON8). | The drift is MEASURED (section 2.2). Verbatim kernel words: low | S12 (definition only), S16 and S4 (against), S17; R: app.js, compiler.py, service.py |
| D2 | **Text budgets per screen:** at most 120 visible words in the primary viewport (owner decision surface at most 160, recorded deviation), persistent shell at most 20 words, per-class limits for headings, buttons, notices, errors, definitions (section 3, 4). | Low to medium. Numbers are hypotheses; the baseline problem is MEASURED | S5; R: index.html (121-word persistent chrome) |
| D3 | **Status strings have a fixed grammar:** subject, kernel word, reason, bound. Roll-ups show counts, never a percentage alone, and never a bare PASS while UNKNOWN is above 0. A refusal by a rule is a result, not an error. | Medium | S9, S4, S20; R: evidence.py |
| D4 | **Errors say what happened, what is unchanged, what to do next**, in at most 20 words and 4 short sentences, next to the source, with the code one level down. Errors get longer than the baseline (+69% words, MEASURED); notices get shorter (-38%). Recovery keeps typed input but never the acknowledgement of UNKNOWNs: after a reload of a changed case the owner ticks it again (I4, P2; section 5.5). Refusals are result rows with `role="status"`. | Medium | S4, S2, S7, S17 |
| D5 | **Definitions are generated from the model and shown on demand:** a term chip opens a popover on click or Enter, with Esc to dismiss, and `Define <term>` in the palette. Nothing essential is hidden: status, reason and bound stay at level 0. Break-even against always-visible text: 44% of visits if every inline word is read, 12% if only 28% of inline words are read (PREDICTION; the time case for on-demand is weak, the case is the word budget and the single source). | Low to medium | S14, S8, S10, S25, S11, S5 |
| D6 | **First run is sample-first, with no tour and no checklist:** empty state with one action, then Select meaning, then Run verification. A state-driven Next slot names the next step from the case stage. Time to first value is defined (section 7.4); the 5 minute target is a hypothesis. The Next slot is a form of pull help (S13); a dismissible hint on HOME is scored as option F in the ADR and left to the study. | Low to medium. Structure has precedent; the benefit is untested | S1, S3, S13, S19, S29 to S31 |
| D7 | **Copy is measured, not judged:** every UI string carries its source (`chrome`, `model`, `ai`, `provider`, `user`), and a lint counts words per screen, checks copy classes and banned synonyms. | Medium | SLP§6 hooks (SYN§8) |
| D8 | **Dependencies stated, not guessed:** kernel reason codes for UNKNOWN, STALE and FAIL; the case stage word PREVIEW collides with Preview Instance; the kernel string "human comprehension" contradicts its own key `human_understanding`. Interim behaviour is specified for each (section 1.3). | High that they exist; the fixes belong to other lanes | R: evidence.py, change_case.py, compiler.py |

## 1. Scope, inputs, interfaces

### 1.1 Inputs read

All ten dossiers via SYNTHESIS.md and PRINCIPLES.md; personas-and-jtbd.md; design/brief.json; README.md, AGENTS.md, ARCHITECTURE.md, docs/adr/README.md, docs/oss/REGISTER.md, ADR-013 in docs/adr/0000-poc-decision-log.md; the baseline `index.html`, `app.css`, `app.js`; the kernel files that emit user-visible strings (`policy.py`, `compiler.py`, `evidence.py`, `impact.py`, `change_case.py`, `service.py`, `runtime.py`, `providers.py`, `http.py`). Pages S1 to S31 were opened by me.

### 1.2 Not decided here

Visual design of chips, glyphs and containers (colour, type, layout lanes); the review chapter names and ripple tiers (review and ripple lanes); the command list (palette lane); where term definitions live (ubiquitous-language lane); kernel changes (kernel lane; each needs its own ADR).

### 1.3 Interface assumptions (stated so nothing is guessed silently)

| # | Assumption | Owner lane | If false |
|---|---|---|---|
| A1 | Screens are named SH (persistent shell), HOME, TREE, REVIEW, RIPPLE, EVID, DECIDE, PAL, CEX, DIA. Budgets in section 4 are per screen id. | layout | Budgets are re-mapped by the integrator; the totals still hold per viewport |
| A2 | Every status renders as glyph plus kernel word plus reason; the glyph shape is not decided here | status and colour | The word and reason still appear, so meaning survives (WCAG 1.4.1, S9) |
| A3 | Term records exist in the model: `{id, term, definition, not_the_same_as, source, role}`. In the POC the definitions come from ARCHITECTURE.md | ubiquitous-language | Definitions ship as a static JSON file generated from ARCHITECTURE.md and diffed in a test |
| A4 | The kernel returns a reason with each UNKNOWN, STALE and FAIL (which branch of `evidence.py`, which subject dimension changed). Today it returns only the status word | kernel (needs an ADR) | The UI prints `FAIL · reason not reported`. It never invents a reason |
| A5 | API errors keep `{code, message}`. The client maps `code` to copy from a table in section 9.3; an unmapped code shows the kernel message verbatim plus the code | interface | No change needed |
| A6 | The palette has a `Define <term>` command and no approve or apply command | palette | Terms stay reachable by click and by `?` on a focused term |
| A7 | `popover` and `<dfn>` work under the strict CSP (SYN C15 is open) | security spike | Fall back to native `<details>` beside the term. No JavaScript is added either way |
| A8 | Sample creation uses the offline fixture. That needs nothing new when the provider is `offline` (the default). With a networked provider the sample opens the case only (section 7.5) | interface | Same |
| A9 | Task-flow element ids for proposed screens are names proposed here (`home.open-sample`, `review.select-meaning`, `review.run-verification`, `term.<id>`, `notice.reload-case`, `blocker.<code>`); the layout lane maps them | layout | The integrator remaps ids; flows stay valid |

## 2. Vocabulary

### 2.1 Canonical terms

Source of truth: the "Ubiquitous language" section of `docs/architecture/ARCHITECTURE.md` (R:) and kernel enumerations. Fowler describes the ubiquitous language as a shared language built with the domain model and used in code and conversation (S12); that page does not discuss text shown in a user interface, so using the terms verbatim in the UI is our inference. UI form is sentence case; identity is case-insensitive.

| Term | UI form | Replaces in the baseline UI | Source |
|---|---|---|---|
| Change Case | change case; short id `1589262d` | "case", "Case", "candidate" when the whole case is meant | R: ARCHITECTURE.md |
| interpretation | interpretation: a provider-proposed reading, untrusted | "alternatives", "option" | R: policy.py CANONICAL_OPTIONS |
| Meaning Selection | verb "Select meaning"; noun "meaning" = the owner-chosen interpretation | "SUPPORTED MEANING" badge as a noun | R: ARCHITECTURE.md |
| Semantic Transaction | transaction (list); "edit" is the gesture | "typed semantic edit", "rule-table edit", "state-view edit" | R: ARCHITECTURE.md |
| Workflow Definition | baseline (active), candidate (proposed), each with a version number | "local baseline", "active baseline", "local demo baseline" | R: ARCHITECTURE.md |
| Preview Instance | preview instance; short "preview" | "instance", "isolated instance", tab "Try" | R: ARCHITECTURE.md |
| Evidence Receipt | receipt; claim = what is asserted; observation = one checked combination | "evidence" used as a count noun, "claims" cards | R: ARCHITECTURE.md, compiler.py |
| Review Packet | review packet (source view only) | "Raw review packet / source-review boundary" | R: ARCHITECTURE.md |
| Local Decision | decision; verbs Approve and Apply, always with their object | "authorise", "acknowledged", "authorisation" | R: ARCHITECTURE.md |
| Effect Intent | effect intent, "queued, not delivered" | "simulated outbox" | R: ARCHITECTURE.md |
| Authority | authority (in refusals) | "capability required" | R: ARCHITECTURE.md, models.py |
| subject | subject with hash; owner-facing verbs use "revision N" | "exact local revision", "exact subject" | R: compiler.py |
| provider | provider (`offline`, `openrouter`, `codex`); provenance label "AI-proposed" | "model", "configured provider" | R: ARCHITECTURE.md |
| human understanding | human understanding (kernel key `human_understanding`); human outcomes = benefit in the field | "human comprehension", "human evidence", "human benefit" | R: compiler.py |
| status words | verbatim, monospace: PASS, FAIL, CONFLICT, STALE, UNKNOWN, NOT_RUN, BLOCKED, ELIGIBLE_FOR_LOCAL_REVIEW, RUNNING | "inapplicable", "immutable evidence" | R: evidence.py, compiler.py; AGENTS.md; SYN C2 |
| sample domain | Draft, Submitted, Recommended, Approved, Rejected; Teacher, Registrar, Viewer; Submit, Recommend, Approve, Reject, Revise | none | R: examples/excursion-candidate.json |

Registered short forms: owner (for local owner), case (for change case, after first use in a sentence), baseline (for baseline version N). Anything else is a synonym and fails the lint.

### 2.2 Drift and collisions in the baseline (MEASURED by reading `index.html`, `app.js` and kernel strings, 2026-09-29)

| # | Finding | Evidence | Rule |
|---|---|---|---|
| V1 | One act, three verbs: the hero says "Authorise", the button says "Approve exact local revision", the notice says "acknowledged". | index.html hero and evidence tab; app.js approve notice | One verb: Approve. Noun: decision. "Authorise" is retired |
| V2 | Five phrasings for what is not known about people: "human benefit", "human comprehension", "human outcomes", "human evidence", "human understanding". They name at least three different claims. | boundary bar, evidence tab, acknowledge box, verify notice, footer | `human understanding` (kernel key) for the reviewer; `human outcomes` for benefit in the field; `human evidence` is retired |
| V3 | "Approve" names two acts on one screen family: the Registrar's workflow action in the Try tab and the owner's decision in the Evidence tab. | app.js `runtime-actions`; index.html `approve` | The domain action is always shown with its role in monospace (`Registrar · Approve`). The owner action always carries its object (`Approve revision 3`). Mis-targeting is a study measure |
| V4 | The button "Discard candidate" closes the whole case (stage DISCARDED, then CASE_CLOSED), and the notice says "Candidate closed". | service.py `discard`; change_case.py line 26 | "Discard case" |
| V5 | The case stage word PREVIEW collides with Preview Instance and the "Try" tab. | change_case.py `stage` literal; ARCHITECTURE.md | Show the stage word verbatim; its popover states "candidate selected; not verified". Rename is a kernel-lane decision (section 12) |
| V6 | "operation" is already taken in the kernel for command retry safety (`operation_id`, guard `operation_binding`, code OPERATION_CONFLICT). Our own research docs say "semantic operation" where the language says Semantic Transaction. | runtime.py, sqlite_store.py; PRI§P4 | UI says transaction. The review lane should align its docs |
| V7 | The kernel contradicts its own key: `human_understanding` in the packet, but `limitations` says "Human comprehension is not established" and the offline fixture says "Reviewer comprehension has not been measured". | compiler.py line 51; providers.py line 44 | UI shows kernel text verbatim (I2), so the kernel lane should align it |
| V8 | "baseline" appears as "local baseline", "active baseline", "local demo baseline". | app.js notices | "baseline" plus a version number; "local demo" lives in the scope chip |
| V9 | Spelling: prose in the repository is mostly en-GB (line counts in README, AGENTS, docs, src: `authoris` 10, `behaviour` 7, `initialis` 5) with en-US in identifiers and a few words (`normaliz` 5). | grep on 2026-09-29 | UI prose is en-GB; kernel identifiers and status words are unchanged. Low-stakes decision, majority rule |

### 2.3 Rules

1. A domain concept in UI copy is produced by term lookup, not typed, so a rename in the model renames the UI. Typed strings that contain a registered term must match its canonical spelling.
2. Kernel enumerations and codes are printed verbatim in the monospace family, never translated or lowercased when they act as status (`UNKNOWN`, not "unknown"). Plain English "unknown" is allowed only inside untrusted provider text.
3. Sentence case for every label, heading and button (S16, S17). Verb first for actions (S17, S3, S22).
4. No first-person voice for the product or the AI. AI is a provenance label, not a speaker. No "please", "sorry", "oops", exclamation marks, humour in errors (S2, S17), emoji (S22) or marketing adjectives.
5. Never explain a term inline where a definition exists; link to the definition (section 6).
6. Banned in chrome copy (lint list, initial): authorise, comprehension, human evidence, operation (semantic sense), candidate (for a case), generate (for AI proposals), magic, smart, simply, just, easy.

### 2.4 Vocabulary lint (specification; the implementation belongs to the integrator)

Input: term registry `{id, canonical, short_forms[], banned[]}` and every string tagged `data-eija-source="chrome"`. Fail on a banned synonym. Warn on a capitalised noun phrase not in the registry. The registry is generated from the same records as the glossary (A3), so the lint, the glossary and the tree cannot disagree.

## 3. Voice and copy classes

Limits are design targets (hypotheses). The source column names the precedent for brevity or form, not for the number.

| Class | Limit | Form | Precedent | Draft compliance (MEASURED, section 9) |
|---|---|---|---|---|
| Screen heading | at most 5 words | noun phrase, no period | S16 | all drafted headings (longest 5) |
| Button or command | at most 4 words, verb first | `Run verification` | S17, S22, S3 | all drafted labels |
| Field label | at most 4 words | noun phrase | S17 | all |
| Status line | at most 10 words | `subject STATUS · reason · bound` | S9, S4 | all drafted status lines (longest 9) |
| Notice (result) | at most 10 words, at most 3 short sentences | result, then what is unchanged | S6 (role `status`) | 13 of 13 (longest 8 words, 3 sentences) |
| Error or refusal | at most 20 words in at most 4 short sentences, each at most 14 words; the first is an outcome tag of at most 2 words | outcome, what happened or is unchanged, what to do | S4, S2, S7 | 20 of 20 after the audit fix (script `.tmp/onb/errlint.py`; longest 20 words; 4 rows use 4 sentences). The first version claimed 20 of 20 but 8 rows failed the tag rule; the integrator's lint must reproduce this count |
| Empty state | title at most 6, description at most 15, one action at most 4 | purpose first, one verb-first action | S2, S1 | 6 of 6 (section 5.2) |
| Definition | at most 20 words, plus optional "not the same as" at most 12 | one sentence, no jargon beyond registered terms | S14 | 14 of 14 (longest 19) |
| Confirmation | at most 25 words | names what is not restored | PRI§P11 | 5 of 5 (longest 18) |
| Tooltip | none for essential information; no hover-only content | | S14, S8 | not used |
| Prose | text nodes of 8 words or more, excluding structured status and data lines: at most about 30 words per viewport | | rubric | HOME 30, DECIDE 22, others 0 |

Numbers in the last column come from `.tmp` scripts described in section 9; the strings are all in this document, so anyone can recount them.

## 4. Text budgets per screen

**Counting rule.** Split on whitespace; count tokens containing a letter or digit. `·`, `→`, `/` and `&` are not words; an identifier such as `1589262d` is one word. This gives 386 words for the static `index.html`; SYN C3 reports 404 because it counts every whitespace token including symbols. Both are the same page.

**Chrome and data.** Chrome is copy we author. Data is model text (term, state and role names), the user's request, kernel messages, and untrusted provider text. The cap applies to all visible words including data, because a reader reads both. Provenance is tagged per string so the lint can report chrome and data separately.

| Screen | Serves | Cap (visible words) | Draft (section 8) | Baseline comparator (MEASURED, page level, viewport not measured) |
|---|---|---|---|---|
| SH persistent shell | all | 20 | 19 | 121 in every workspace screen (98 above the footer); 117 on first load |
| HOME | T10 | 60 | 53 | 117 first load |
| REVIEW at PROPOSED | T01 | 120 | 117 | 241 (Change tab after "Ask for interpretations") |
| REVIEW at PREVIEW | T02, T03 | 120 | 91 | 290 (Change tab with the edit panel) |
| RIPPLE | T03 | 120 | not drafted | inside the Impact tab (62 static words plus table) |
| EVID | T06, T14 | 120 | 91 | 212 before, 227 after verification |
| DECIDE | T08 | 160 (deviation) | 141 | inside the Evidence tab (227) |
| PAL | T09 | 80 | not drafted | absent |
| CEX | T07 | 100 | not drafted | absent |
| DIA | T04 | 60 | not drafted | inside the Impact tab |
| TREE | T05 | 100 | not drafted | absent |

Caps for screens I did not draft are proposals for the owning lane to accept or contest with an HCI-ADR.

**Deviation.** DECIDE gets 160, not 120: the owner must see the exact revision, every UNKNOWN and the coverage row before Approve is enabled, and P1 outranks P10. The draft is 141.

**What the baseline shows.** The first screen is at budget (117 words). The workspace is not: persistent chrome alone is 121 words (header 9, aside 25, case list 6, hero 21, boundary 15, case heading 13, tabs 9, footer 23), so every workspace screen starts at the whole budget before any tab content. Static counts come from `.tmp/regions.py`, an HTML parse of `index.html` (scripts are in the gitignored `.tmp/` and are not committed; the rule and every string are in this document); dynamic strings from `app.js`, `policy.py` and `providers.py` are hand-counted. Viewport-level counts need the slop-budget script on a running build (no build could run here: `fastapi` is not installed and I did not install it).

## 5. Microcopy patterns

### 5.1 Status strings

Grammar: `<subject> <STATUS> · <reason> · <bound>`. Every part except the bound is required; a missing bound is written `bound not stated`, never omitted (P1).

| Case | String | Basis |
|---|---|---|
| PASS with bound | `runtime matrix PASS · 125 of 125 one-step observations` | README: 125 one-step observations; 5 actors x 5 states x 5 actions |
| never run | `runtime matrix UNKNOWN · no receipt` | evidence.py: no receipts gives UNKNOWN |
| unknown by construction | `human understanding UNKNOWN · not measured` | compiler.py constant; ADR-010 |
| stale | `runtime matrix STALE · subject changed: semantic` | evidence.py: a dimension differs; needs A4 |
| failed | `runtime matrix FAIL · reason not reported` until A4 | evidence.py returns FAIL for a mismatch and for a malformed receipt |
| disagreement | `runtime matrix CONFLICT · receipts disagree` | evidence.py: PASS and FAIL both current |
| prerequisite missing | `harness NOT_RUN · prerequisite missing: Chromium` | AGENTS.md lane rule |
| running | `runtime matrix RUNNING · 125 observations · previous result STALE` | P7; measured verification 2.0 to 2.4 s (section 10) |
| closure | `modelled impact closure PASS · within this mapping` | impact.py `envelope` text, shown in full at level 1 |

**Reasons are a closed list**, each traced to a branch of `evidence.py`: `no receipt` (no receipts), `no verifier for this claim` (claim or kind not the runtime matrix), `unrecognised method` (producer or method differs), `subject changed: <dimension>` (semantic, implementation, policy, environment, harness), `receipts disagree`, `closure frontier open` (impact `complete` is false), `not measured` (human understanding).

**Roll-up.** `3 PASS · 1 UNKNOWN · 0 FAIL`. Zero counts are printed so "none" is distinct from "not computed" (`UNKNOWN: not computed`). While UNKNOWN is above 0 the aggregate label is `pass with unknowns` (PRI§P1). No percentage appears without its counts.

**Checked and none versus not checked.** `0 dependants · closure PASS within mapping` means checked. `Ripple not analysed · UNKNOWN` means the edit is outside the supported vocabulary. Never draw the second as an empty list (P5; S1: ambiguous empty states cause confusion).

### 5.2 Empty states

Three kinds after Primer (S2): never used, temporarily empty, error. A fourth case, "not analysed", is a result and uses 5.1.

| Kind | Title | Description | Action | Words |
|---|---|---|---|---|
| never used (HOME) | No change cases yet | Open the sample to review one change by what it means. | Open excursion sample | 4 / 11 / 3 |
| temporarily empty | No interpretations yet | Nothing is selected until you choose. | Ask for interpretations | 3 / 6 / 3 |
| loading | Connecting to Studio | (none) | (none) | 3 |
| error, no session | No session | Open the full link printed by `eija serve`, including the part after #. | (none; nothing to click) | 2 / 11 / 0 |
| error, load failed | Could not load change cases | Studio is not responding. Check the terminal, then reload. | Reload | 5 / 9 / 1 |
| palette, no match | No command or term matches | Search terms, states, journeys, tests. | (none) | 5 / 5 / 0 |

A loading state is shown before any empty state so "No change cases yet" never flashes while the list request is in flight (S1: communicate loading, error and no results distinctly). The no-session row matters: opening the address without the private fragment leaves the baseline on a blank "Connecting..." chip with an API error code (R: http.py `SESSION_REQUIRED`).

### 5.3 The Next slot (state-driven, no AI)

One line under the case heading, computed from the case stage and the packet blockers. It is a pure function `next_action(stage, blockers)`, unit-testable, and it never names or offers Approve or Apply: the owner performs those on the decision surface only (P2, I4).

| Stage (kernel word) | Next slot | Control |
|---|---|---|
| DRAFT | Next: Ask for interpretations | Ask for interpretations |
| PROPOSED | Next: Select a meaning | none; the cards are the controls |
| PREVIEW, SAVED | Next: Run verification | Run verification |
| VERIFIED, eligible | Next: Open decision | Open decision |
| VERIFIED, blocked | Blocked · n reasons (5.6) | the blocker actions |
| APPROVED | Approved, not applied | none (status only; Apply is on the decision surface) |
| APPLIED | Applied to baseline version 1 | New change case |
| DISCARDED | Closed. History is kept | New change case |

Why neither Approve nor Apply is a next step: the invariants (P2, I4) keep approval a deliberate act on the surface that shows the exact revision and every UNKNOWN, so a control elsewhere that offers it is a shortcut around that surface. The audit found the first draft contradicted this rule in the APPROVED row (it offered Apply); the row is now a status. A vendor-reported approval-rate figure that the first draft cited as extra rationale was never opened and has been removed (Q10). The Next slot leads to evidence, and the study counts its click-through (section 11).

### 5.4 Notices (result, then what is unchanged)

Notice text states the result and the unchanged baseline in at most 10 words and 3 short sentences. Results use `role="status"` (WCAG 4.1.3, S6). Rows N01 to N13 in section 9.2.

### 5.5 Errors, refusals and failures

Three different things, three treatments.

| Kind | What it is | Treatment | Examples |
|---|---|---|---|
| **Refusal** | The kernel applied a rule and said no. Information, not a fault. | Result row at the point of action: `Refused. <who> cannot <action>. <rule>.` Neutral: the row carries `role="status"` (a polite live region, SC 4.1.3, S6) so a refusal after a click, key press or drop is announced without moving focus; never `role="alert"`. At a drag drop target it names the vocabulary rule. | STATE_DENIED, ROLE_DENIED, ASSIGNMENT_DENIED, UNSUPPORTED_EDIT, MEANING_UNSUPPORTED |
| **Failure** | Something did not complete. | Error pattern below; `role="alert"`; next to the source; input kept (S4) | STALE_VERSION, PROVIDER_TRANSPORT, SESSION_REQUIRED |
| **Blocker** | A precondition for Approve is unmet. | Row with its resolving action (5.6) | GATE_BLOCKED and its codes |

**Error pattern:** `<Outcome tag>. <What happened or is unchanged>. <What to do>.` The tag is at most 2 words (`Not saved`, `Not approved`, `Refused`). Recovery uses a control in the message where one exists (`Reload case`). The code follows in monospace at level 1. NN/g asks for plain language, constructive advice and preserved input (S4); GitHub Primer asks for specific messages and rejects "There was a problem" (S2). WCAG 3.3.3 asks for correction suggestions for automatically detected input errors (S7); it applies to the input rows only (`INVALID_REQUEST`, `UNKNOWNS_NOT_ACKNOWLEDGED`, `MEANING_CHECK_FAILED`), not to `STALE_VERSION` or provider failures, which the rest of the pattern covers by design choice. NN/g also asks to avoid blaming words such as "invalid" (S4); the drafts avoid them. Google PAIR asks systems to state limitations specifically and return control (S20).

**Recovery keeps input, not consent.** After `STALE_VERSION` the message carries a `Reload case` control. Reload keeps the open tab and the typed meaning answers whose question id and text are unchanged. It always clears the acknowledgement of UNKNOWNs, because the case version changed and the acknowledgement is consent to one exact state: the owner ticks it again on the reloaded case (I4, P2). The notice reads `Case reloaded. Answers kept. Acknowledge again.` (N14). A changed subject still blocks approval in the kernel (`SUBJECT_CHANGED`). The first draft kept the tick across the reload; the audit found that this carried consent over a changed case, and it was removed.

Twenty rewrites with word counts are in 9.3.

### 5.6 Blockers

Today the baseline prints raw codes (`Review blocked: MEANING_REQUIRED, RUNTIME_EVIDENCE_UNKNOWN`). Each blocker becomes a row: reason, then its action. Codes from `compiler.py`.

| Code | Row text | Action |
|---|---|---|
| MEANING_REQUIRED | Meaning not selected | Select meaning |
| POLICY_BLOCKED | Candidate breaks policy: `<policy error>` | Edit rejection source |
| SOURCE_REVIEW_REQUIRED | Source differs from the release fixture | none in the Studio (maintainer action) |
| IMPACT_INCOMPLETE | Ripple not closed · UNKNOWN | Show frontier |
| RUNTIME_EVIDENCE_UNKNOWN, _STALE, _FAIL, _CONFLICT | Runtime evidence `<STATUS>` (status word verbatim) | Run verification; for FAIL and CONFLICT, Open observations |
| STALE_BASELINE | Baseline changed after this case started | New change case |
| HUMAN_FIELD_EVIDENCE_REQUIRED | Field use blocked: no human evidence | none, blocked by design (ADR-010) |
| CASE_DISCARDED | Case discarded | New change case |

### 5.7 Confirmations and undo coverage

Every control that closes, resets or writes states what it does not restore, inside the confirmation and not on the button (PRI§P11; Claude Code, Bolt and Windsurf precedents are in AIC§2.1, 2.4, 2.9).

| Control | Confirmation (words) |
|---|---|
| Discard case | Discard this case? History and receipts are kept. The baseline is unchanged. A closed case cannot be reopened. (18) |
| Reset preview | Reset the preview? A new instance starts in Draft. The current instance is kept but no longer used. (18) |
| Apply | Apply writes baseline version 1. Not undoable here. Nothing outside the local demo changes. (14) |
| Move a node | Moving keeps evidence. Renews presentation approval. (6) (ADR-008) |
| Clear suspect flag | Record that this item is still valid given the change shown. Logged. This item only. (15) |

### 5.8 Jobs and progress

Verification takes 2.0 to 2.4 s on the reference PC (MEASURED, section 10), inside the 1 to 10 s class (the 0.1 s, 1 s and 10 s limits, S26). The control shows `RUNNING · 125 observations` within 0.1 s and the previous result stays visible and marked STALE. The kernel does not report incremental progress, so there is no percentage and no cancel today; the string does not imply either.

### 5.9 AI and provider strings

| Situation | String | Rule |
|---|---|---|
| Provider chip | `offline fixture`, `openrouter`, `codex` | names the source; no "AI assistant" |
| Fixture summary | Fixture, not an LLM · 3 interpretations | from the fixture's own summary: "no model inference was used" |
| Consent (networked) | Allow provider call to openrouter. Sends request and synthetic baseline. Not sent: database, receipts, repository. | README states what is sent and not sent; I8 |
| Provenance | `AI-proposed`, `AI-estimated`, `Provider text, untrusted` | text label; dashed treatment belongs to the visual lane |
| Prompt verb | Ask AI to propose... | PRI§P9; never "Generate", "Magic", sparkle glyphs |
| Feedback | Not useful | logged per source (PRI§P9) |

## 6. Glossary affordances

**Behaviour.** Any registered term rendered in the UI is a button (a native `<button>` with `popovertarget`, S10) that opens a non-modal popover: definition, optional "not the same as", "used in n places" (from the ripple), and "Open in tree". `popover="auto"` gives light dismiss (click outside, Esc) and returns focus to the invoker on Esc without script (S25; the overview page S10 confirms `popovertarget` and Baseline 2025 status). It opens on click or Enter, never on hover alone, so touch and keyboard work. WCAG 1.4.13 (S8) covers content that appears on hover or focus and does not apply to click-opened content, so no conformance claim is made for the click path. If the `?` shortcut opened the popover on focus alone, 1.4.13 would apply (dismissible, hoverable, persistent) and would have to be tested; the design opens it on the `?` key press, not on focus. A focused term opens on `?`. The palette offers `Define <term>`. Only the first occurrence per screen is a chip; later occurrences are plain text.

**Content rule.** A definition is generated from the term record (A3), so it cannot drift from the language. Essential information is not hidden: status word, reason and bound are level 0 text; the popover only explains the term. Disclosure stays at two levels (S15; a 2006 practitioner rule, medium confidence). NN/g says vital task information should not live in a tooltip (S14). `<dfn>` is used only at the defining site (the glossary list in the tree), because MDN says the full definition must be nearby (S11).

**Untrusted text.** Definitions are set through `textContent`. Provider text never enters a definition (ADR-013).

**Fallback.** If A7 fails, use native `<details>` beside the term.

**Draft definitions** (source: ARCHITECTURE.md and kernel branches; the ubiquitous-language lane owns the final text). Counts are words.

| Term | Definition | Not the same as |
|---|---|---|
| Change Case | One request and everything decided about it: interpretations, chosen meaning, candidate, evidence, decision. (13) | a workflow instance; its revision is not an instance version |
| Meaning Selection | The owner's explicit choice of one supported interpretation. (8) | a provider explanation |
| Semantic Transaction | One typed edit to business meaning. Rule-table and state-view edits produce the same transaction. (14) | an operation id, which only makes a command safe to retry |
| Workflow Definition | Typed states, transitions, roles, guards and effects. Order carries no meaning; names do. (13) | a preview instance |
| Preview Instance | One isolated run of the candidate. A changed candidate makes it stale; reset starts a new one. (17) | the case stage PREVIEW |
| Evidence Receipt | A dated record of what a local verifier observed about one subject. (12) | a status label; applicability is recomputed |
| Review Packet | A read-only view of the current subject, blockers, claims and questions. (11) | a source you edit |
| Local Decision | The owner's approval of one exact subject and scope. Separate from eligibility and from apply. (15) | technical eligibility |
| Effect Intent | A queued synthetic notification or audit entry. Queued is not delivered. (11) | a sent message |
| Authority | Permission to act at the moment of commit. An earlier success or the current selection does not grant it. (19) | a role name |
| UNKNOWN | The kernel has no admissible evidence for this claim. It is counted and never rounded up to PASS. (18) | FAIL: nothing failed, nothing was established |
| STALE | The only receipts describe an earlier subject. The changed dimension is named. (12) | FAIL |
| CONFLICT | Current receipts disagree: at least one PASS and one FAIL. (10) | UNKNOWN |
| NOT_RUN | A prerequisite is missing, so the check did not run. It is never shown as PASS. (16) | FAIL |

In the kernel today an unrun verification yields UNKNOWN (no receipts); NOT_RUN is the lane-rule word for a missing prerequisite (AGENTS.md).

**Inline text replaced.** Five explanatory sentences in the baseline (17, 14, 15, 24 and 17 words, 87 in total: the aside note, the editor note, the impact note, the try note and the unknown note) become definitions read on demand. Break-even in HCI-ADR-0065: on-demand is cheaper in expectation when fewer than about 44% of visits need the explanation (PREDICTION, band 41% to 49%, assuming every inline word is read); if readers read only 28% of inline words (S5) the figure falls to about 12%, so on-demand is a word-budget and single-source decision, not a proven time saving.

## 7. First run

### 7.1 Flow (sample-first)

| Step | Screen | The user does | The user sees | Novel words |
|---|---|---|---|---|
| 0 | HOME | starts `eija serve --open` and lands on the private URL | `Connecting to Studio`, then the empty state | 53 |
| 1 | HOME | clicks Open excursion sample | a change case at PROPOSED with three interpretations: one supported, two not supported with their reason; provider chip `offline fixture` | 98 |
| 2 | REVIEW | clicks Select meaning on "Teacher recommends; registrar decides" | transactions in chapters, ripple line (3 changed, 20 dependants), `runtime matrix UNKNOWN · no receipt`, `human understanding UNKNOWN · not measured`; Next: Run verification | 60 |
| 3 | EVID | clicks Run verification | `RUNNING`, then `runtime matrix PASS · 125 of 125 one-step observations` beside the two UNKNOWN lines and the four-slot coverage row | 72 |

Value moments: after step 2 the developer has seen a change as typed transactions with its ripple (TTFV-1); after step 3 they have seen PASS with its bound next to UNKNOWN (TTFV-2). Optional next actions, offered by the palette and not forced: try Recommend as `teacher-unassigned` (a refusal shown as a result) and open DECIDE to read it. Approving and applying happen only on DECIDE; no palette command or Next slot offers them.

Word counts are design caps from the section 8 drafts. The baseline path is 420 novel words over 6 screens and 5 required clicks; the proposal is 283 over 4 screens and 3 required clicks (section 10).

### 7.2 States around the flow

| State | Behaviour |
|---|---|
| Connecting | Title bar plus `Connecting to Studio`; no empty state yet |
| No session | The no-session error (5.2); no controls |
| Provider not ready | Provider chip shows `not ready`; HOME still opens the sample (offline needs no provider) |
| Source review required | A banner states approval is blocked; sample review still works |
| Returning user | HOME is not shown when cases exist; the case list opens the latest case; `Open excursion sample` stays in the palette |
| After the sample | Nothing persistent: no checklist, no progress bar, no badge. The sample is an ordinary case; history and receipts are retained (ADR-012) |

### 7.3 Deliberately absent

No modal tour, no checklist container, no "Welcome" copy, no animated illustration, no "skip" control, and no coach marks in v1. NN/g reports that onboarding tutorials do not improve task performance and recommends help that appears when the user needs it (S13, practitioner article; the underlying studies were not opened). The same article lists coach marks, hover tooltips and step-by-step flows as acceptable pull help, so it does not argue against every contextual hint; the ADR scores a dismissible hint on HOME as option F. Storybook offers a new user an opt-in interactive tour and example stories (S19), so the absence of a tour is a hypothesis the study tests, not a fact. The first-run guides of three AI coding tools also have no product tour: Claude Code's quickstart has the user ask about their own project and about the tool itself, then make a small change (S29); Cursor's has the user ask the agent to explain the codebase, make a small change and review the diff (S30); VS Code's agent quickstart builds a small app in an empty folder and reviews the diff (S31). None of them uses a sample-first empty state, so they support "no tour" and "review a real change early", not the sample itself.

### 7.4 Time to first value

| Metric | Definition | Target (hypothesis) | PREDICTION floor |
|---|---|---|---|
| TTFV-1 | first paint to the transaction list of a selected meaning visible | median at most 3 min | not modelled separately |
| TTFV-2 | first paint to a verification result with human understanding UNKNOWN visible | median at most 5 min; 90th percentile at most 10 min | 79 s expert, error-free floor if every novel word is read (baseline 117 s), range 77 to 108 s (baseline 114 to 159 s); 30 s if 28% of words are read (baseline 44 s), range 28 to 40 s (baseline 41 to 59 s) |
| Unassisted | share of participants who reach TTFV-2 without opening README or docs | at least 80% | not modelled |

The 10-minute figure is the P5 task framing, not a measurement ([personas-and-jtbd.md](../personas-and-jtbd.md)); 5 minutes is half of it and leaves room to read the decision surface. The floor is not a forecast of novice time: KLM covers expert, error-free, routine tasks only (LAW§2.4), so a novice will be slower and the study measures the real value. The product itself collects no telemetry (I6); measurement happens in the study only.

### 7.5 Provider-live variant

With a networked provider (`--provider openrouter` or `codex`), Open excursion sample creates the case and stops: the Next slot reads `Next: Ask for interpretations`, and the consent line of 5.9 applies. The sample never triggers a provider call by itself (I8).

## 8. Draft screens on the real excursion data

Text only; layout is not decided here. Numbers are from real code: 125 observations (README; verified by running `verify_runtime`), 3 changed actions and 20 dependants (`model_impact(baseline(), candidate)`), 5 states. **Identifiers are real kernel output** from one run of the excursion sample on 2026-09-29 in an ephemeral sandbox (fresh workspace in the gitignored `.tmp/onb/ws`, offline fixture, deleted after the run; script `.tmp/onb/real_run.py`): case id `1589262d…` (first 8 hex characters; ids are random per case, so another run prints a different one), case version 1 at PROPOSED, 2 at PREVIEW, 3 at VERIFIED (the revision approved), baseline version 0 before apply and 1 after, subject hash `649b3df3…466c`. To reach approve and apply, the sandbox marked the local identity as the trusted release fixture, which a worktree checkout is not; nothing else was changed.

```text
SH   EIJA Studio · Local demo · synthetic data · one owner · human outcomes UNKNOWN · offline fixture · Change cases · New change case · Ctrl+K   (19 words)

HOME (53 words including SH title, scope and provider chips)
  No change cases yet
  Open the sample to review one change by what it means.
  [Open excursion sample]  [New change case]
  Sample: excursion sign-off. Synthetic data, offline fixture, no provider call.
  AI proposes. The kernel checks. The local owner decides.

REVIEW at PROPOSED (117 words including SH)
  Change case 1589262d · revision 1 · baseline 0     Let teachers sign off excursions.     PROPOSED
  Next: Select a meaning
  What does "sign off" mean?      Fixture, not an LLM · 3 interpretations      Provider lists 2 unknowns
  Supported      Teacher recommends; registrar decides
    Only active, assigned teachers recommend.
    Registrar approval AND rejection initially require Recommended.
    Teachers do not receive final approval authority.
    Provider text, untrusted        [Select meaning]
  Not supported  Teacher grants final approval
    Expands protected authority; blocked by this POC's policy.        Provider text, untrusted
  Not supported  Teacher confirms a completed section
    A different domain operation; not implemented by this bounded POC.   Provider text, untrusted

REVIEW at PREVIEW (91 words including SH)
  Change case 1589262d · revision 2 · baseline 0     Let teachers sign off excursions.     PREVIEW
  Next: Run verification
  Core
    ADDED state Recommended
    ADDED transition Recommend · Submitted → Recommended · Teacher · guard actor_assigned
  Consequences
    MODIFIED transition Approve · from Submitted to Recommended
    MODIFIED transition Reject · from Submitted to Recommended
  Glue     0 hidden formatting-only edits
  Ripple · 3 changed · 20 dependants · closure PASS within mapping
  runtime matrix UNKNOWN · no receipt
  human understanding UNKNOWN · not measured
  [Run verification]  [Edit]  [Discard case]

EVID after verification (91 words including SH)
  Evidence
  schema policy PASS
  runtime matrix PASS · 125 of 125 one-step observations
  modelled impact closure PASS · within this mapping
  human understanding UNKNOWN · not measured
  3 PASS · 1 UNKNOWN · 0 FAIL
  Claim           Covered                               Assumed                              Not covered
  runtime matrix  125 actor, state and action           Synthetic actors stand for real roles   Multi-step sequences
                  observations · one step each          Shipped kernel matches release hash     Real users · Human understanding
                                                                                                Dependencies outside the mapping
  [Open decision]  [Run again]  [Source]

DECIDE (141 words including SH)
  Decision · revision 3          Subject 649b…466c · baseline 0 · 3 changed · 20 dependants
  schema policy PASS
  runtime matrix PASS · 125 of 125 one-step observations
  modelled impact closure PASS · within this mapping
  human understanding UNKNOWN · not measured
  (coverage row as in EVID)
  Who retains final approval authority?  Can an unassigned teacher recommend?  Which state must precede registrar rejection?
  Answers below record acknowledgement, not understanding.
  [ ] Acknowledge: local demo, synthetic actors, human outcomes UNKNOWN
  [Approve revision 3]  [Apply to local baseline]
  Apply writes baseline version 1. Not undoable here. Nothing outside the local demo changes.
```

In the drafts the "Not covered" slot is never empty (H1 in REV§9 is untested), each coverage item is a short list entry so the prose lint does not fire on fragments, and the EVID roll-up reads `3 PASS · 1 UNKNOWN · 0 FAIL`, which the label `pass with unknowns` summarises. Chapter names Core, Consequences and Glue follow SYN S8; the review lane owns them.

Prose words (text nodes of 8 words or more, excluding structured status, transaction and data lines): HOME 30, DECIDE 22, others 0 (the mechanical count without exclusions is HOME 30, PROPOSED 18, PREVIEW 17, EVID 8, DECIDE 38, because status lines of 8 or more tokens and kernel consequence text are counted; the lint needs the `status` and `data` kinds).

## 9. Before and after

Word counts use the rule in section 4. Rows are strings or string groups, not a partition of the page. "Before" is the baseline text as rendered; "after" is the proposal.

### 9.1 Labels and static text

| # | Where | Before | After | Words |
|---|---|---|---|---|
| R01 | hero (persistent, every screen) | EXECUTABLE INTENT & JOURNEY ASSURANCE See Meaning. Prove Change. Understand the decision. Try the consequence. Authorise only the exact revision you reviewed. | No change cases yet | 21 to 4 |
| R02 | aside note (persistent) | One model. Separate truths. Intent is not implementation. Tests are not human evidence. Proposal is not approval. | (none) | 17 to 0 |
| R03 | boundary bar (persistent) | Synthetic excursion workflow One local owner · no institutional SSO · no external effects · human benefit unmeasured | Local demo · synthetic data · one owner · human outcomes UNKNOWN | 15 to 9 |
| R04 | footer (persistent) | AI may propose. The kernel checks. The local owner decides. Not a universal compiler, institutional approval system, or formal proof of human understanding. | (none; its human-understanding limit is carried by the shell chip `human outcomes UNKNOWN` (R03) and by `human understanding UNKNOWN` on REVIEW, EVID and DECIDE) | 23 to 0 |
| R05 | tab labels | 01 / Change 02 / Impact 03 / Try 04 / Evidence & Decision | Transactions Ripple Preview Evidence Decision | 9 to 5 |
| R06 | create panel | START WITH INTENT What should change? Create Change Case No model call is made until you request a proposal. | What should change? Create change case No provider call yet. | 19 to 10 |
| R07 | change heading | MEANING BEFORE IMPLEMENTATION What does “sign off” mean? Ask for interpretations | What does “sign off” mean? Ask for interpretations | 11 to 8 |
| R08 | consent checkbox (networked provider) | I consent to sending this request and synthetic model to the configured provider. | Allow provider call to openrouter. Sends request and synthetic baseline. Not sent: database, receipts, repository. | 13 to 15 |
| R09 | proposal summary, none yet | No interpretation has been requested. Your request is not yet a semantic change. | No interpretations yet | 13 to 3 |
| R10 | blocked option button | Explain boundary | Why not supported | 2 to 3 |
| R11 | provider explanation summary | Untrusted provider explanation | Provider text, untrusted | 3 to 3 |
| R12 | editor block | TYPED SEMANTIC EDIT Make the prerequisite explicit. Teacher recommendation is not final approval. Registrar rejection is a separate consequence to review. Registrar may reject from Apply rule-table edit This changes only the candidate. It invalidates matching evidence and any prior decision. Save review checkpoint Discard candidate | Edit rejection source Registrar rejects from Apply edit Invalidates 1 receipt and the decision. Baseline unchanged. Save checkpoint Discard case | 46 to 20 |
| R13 | impact header and editors | ONE SUBSTRATE, SYNCHRONISED VIEWS Follow the actual consequences. State-view edit: Reject starts at Apply state-view edit Both editors issue the same typed command; the state view does not own another model. | Ripple Reject starts at Apply edit Generated from model 649b | 31 to 10 |
| R14 | layout note | Layout is recorded independently. Domain evidence survives; exact-presentation approval must be renewed. | Moving keeps evidence. Renews presentation approval. | 12 to 6 |
| R15 | impact summary | 3 changed actions · 20 modelled dependants · closure complete within this mapping | 3 changed · 20 dependants · closure PASS within mapping | 11 to 8 |
| R16 | try intro | ISOLATED EXECUTABLE PREVIEW Try the rule. Not a mock response. The instance starts in Draft. Use Submit as a teacher, Recommend, then Approve as the registrar. Assignment belongs to this one synthetic excursion fixture. | Preview instance Shortest path to Approved: Submit, Recommend, Approve | 34 to 9 |
| R17 | runtime state | COMMITTED STATE Not started No candidate state has been executed | State: not started | 10 to 3 |
| R18 | trace summary | Persisted audit and simulated outbox | Audit and effect intents | 5 to 4 |
| R19 | evidence header | COMPUTED, NOT SELF-REPORTED Evidence with an exact subject. Run bounded verification | Evidence Run verification | 11 to 3 |
| R20 | blockers | Review blocked: MEANING_REQUIRED, RUNTIME_EVIDENCE_UNKNOWN | BLOCKED · 2 reasons. Meaning not selected: Select meaning. Runtime evidence UNKNOWN: Run verification. | 4 to 13 |
| R21 | eligible line | Technical scope eligible. Human authorisation is still a separate decision. | ELIGIBLE_FOR_LOCAL_REVIEW · owner decision pending | 10 to 4 |
| R22 | unknown box | Human comprehension: UNKNOWN The runtime matrix uses synthetic actors. These questions acknowledge meaning; they do not measure real reviewer benefit. | Human understanding UNKNOWN · not measured. Answers below record acknowledgement, not understanding. | 20 to 11 |
| R23 | acknowledge checkbox | I understand this is a local synthetic demo, with human outcomes and production readiness unproved. | Acknowledge: local demo, synthetic actors, human outcomes UNKNOWN | 15 to 8 |
| R24 | approve button | Approve exact local revision | Approve revision 3 | 4 to 3 |
| R25 | apply (no confirmation today) | (none) | Apply writes baseline version 1. Not undoable here. Nothing outside the local demo changes. | 0 to 14 |
| R26 | raw JSON toggles | Dependency closure and fingerprint details Raw review packet / source-review boundary | Source | 10 to 1 |

Totals over these rows: before 369 words, after 177. Rows R20 and R25 grow on purpose: R20 gives each blocker its action, R25 adds a confirmation the baseline lacks (P11). R20 shows two blockers (4 words to 13); the T06 flow models one blocker (`RUNTIME_EVIDENCE_UNKNOWN`, 3 words to 8). The four persistent rows R01 to R04 fall from 76 words to 13: 9 stay in the shell (R03) and 4 move to HOME only (R01). The 3-word chip `human outcomes UNKNOWN` stays in the shell on purpose: without it, the boundary bar's "human benefit unmeasured" and the footer's "not a formal proof of human understanding" would leave every screen, and TREE, RIPPLE and PAL would carry no statement that human outcomes are UNKNOWN (I3). The chip opens the scope popover (Q7).

### 9.2 Notices

| # | Where | Before | After | Words |
|---|---|---|---|---|
| N01 | case created | Case created. No provider call or baseline change has occurred. | Case created. Baseline unchanged. | 10 to 4 |
| N02 | interpretations | Interpretations received. No meaning was selected automatically. | 3 interpretations received. None selected. | 7 to 5 |
| N03 | meaning selected | Meaning selected. The local baseline has not changed. | Meaning selected. Baseline unchanged. | 8 to 4 |
| N04 | checkpoint | Review checkpoint saved; the active baseline is unchanged. | Checkpoint saved. Baseline unchanged. | 8 to 4 |
| N05 | discard | Candidate closed. History is retained; the baseline is unchanged. | Case discarded. History kept. Baseline unchanged. | 9 to 6 |
| N06 | edit | Candidate changed. Old evidence remains immutable and is now inapplicable; re-run verification. | Edit applied. Runtime matrix STALE. Decision cleared. | 12 to 7 |
| N07 | layout | Layout metadata changed. Domain receipts remain applicable; exact-presentation approval is cleared. | Layout saved. Evidence kept. Presentation approval cleared. | 11 to 7 |
| N08 | reset preview | Fresh isolated instance created in Draft. | Preview reset to Draft | 6 to 4 |
| N09 | verify | Bounded runtime verification finished. Human evidence remains UNKNOWN. | Verified. 1 UNKNOWN remains. | 8 to 4 |
| N10 | approve | Exact local revision acknowledged. Apply remains a separate action. | Revision 3 approved. Not applied. | 9 to 5 |
| N11 | apply | Applied to the local demo baseline only. No production system was touched. | Applied to baseline version 1. Nothing else changed. | 12 to 8 |
| N12 | export | Case exported with model, evidence, observations and integrity hash. | Exported eija-1589262d….json | 9 to 2 |
| N13 | commit | Commit completed; the displayed state is persisted. | Submit committed. State Submitted, version 1. | 7 to 6 |
| N14 | case reloaded after `STALE_VERSION` | (none: the baseline has no reload control; F5 reloads the page and clears the form) | Case reloaded. Answers kept. Acknowledge again. | 0 to 6 |

Totals: before 116, after 72 (-38%). N14 is new and has no baseline counterpart; N01 to N13 alone go from 116 to 66 (-43%).

### 9.3 Errors and refusals

"Before" is what the baseline shows: the code, a colon, the kernel message. The kernel message stays in the API (I2); the client maps the code to the "after" copy and prints the code at level 1. Illustrative values in the "after" text (revision 4) come from the state at the time. Twenty of 47 distinct codes are rewritten here (41 `DomainError` codes plus 7 HTTP-layer codes, of which `NOT_FOUND` is in both; counted by grep on `src` on 2026-09-29). The rest use the verbatim fallback (A5) until someone rewrites them, and a test enumerates the codes from source so a new code cannot ship unmapped by accident.

| Code | Before (as rendered) | After | Words |
|---|---|---|---|
| `STALE_VERSION` | STALE_VERSION: Case changed; reload before acting | Not saved. This case changed after you opened it. Reload it, then repeat the action. | 6 to 15 |
| `STALE_BASELINE` | STALE_BASELINE: The local baseline changed; no automatic rebase | Not applied. The baseline changed after this case started. Nothing is rebased automatically. Create a new change case. | 8 to 18 |
| `SUBJECT_CHANGED` | SUBJECT_CHANGED: The exact review subject has changed | Not approved. The subject changed after you opened this decision. Review revision 4, then approve again. | 7 to 16 |
| `STALE_DECISION` | STALE_DECISION: Decision is invalid or no longer matches the exact subject | Not applied. The decision no longer matches this revision. Approve the current revision first. | 11 to 14 |
| `UNKNOWNS_NOT_ACKNOWLEDGED` | UNKNOWNS_NOT_ACKNOWLEDGED: Acknowledge the local/synthetic/human-unknown scope | Not approved. Acknowledge the scope first: local demo, synthetic actors, human outcomes UNKNOWN. | 5 to 13 |
| `MEANING_CHECK_FAILED` | MEANING_CHECK_FAILED: Critical consequences were not correctly acknowledged | Not approved. At least one answer does not match the model. Your answers are kept. Check them and approve again. | 7 to 20 |
| `GATE_BLOCKED` | GATE_BLOCKED: MEANING_REQUIRED, RUNTIME_EVIDENCE_UNKNOWN | Not approved. 2 blockers: meaning not selected, runtime evidence UNKNOWN. | 3 to 10 |
| `EGRESS_CONSENT_REQUIRED` | EGRESS_CONSENT_REQUIRED: Enable network at startup and explicitly consent to sending the request and synthetic model | Not sent. It needs the --allow-network start flag and your consent for this request. | 15 to 14 |
| `PROVIDER_TRANSPORT` | PROVIDER_TRANSPORT: Provider request failed or timed out; it may still have been billed | Call failed. It may have timed out and may still have been billed. Nothing was retried. Ask again. | 13 to 18 |
| `PROVIDER_OUTPUT_INVALID` | PROVIDER_OUTPUT_INVALID: Provider returned an invalid proposal; no repair or authority promotion | Reply discarded. It did not match the proposal format and was not repaired. Ask again or change the request. | 11 to 19 |
| `MEANING_UNSUPPORTED` | MEANING_UNSUPPORTED: Expands protected authority; blocked by this POC's policy. | Refused. Teacher final approval is not supported. Choose a supported meaning. | 9 to 11 |
| `UNSUPPORTED_EDIT` | UNSUPPORTED_EDIT: After selection, use the typed rejection-source edit | Refused. Only the rejection source can be edited today. Other edits are outside the supported vocabulary. | 8 to 16 |
| `STATE_DENIED` | STATE_DENIED: Action is invalid from the current state | Refused. Approve is not modelled from Draft. It starts from Recommended. | 8 to 11 |
| `ROLE_DENIED` | ROLE_DENIED: Actor does not hold the current required role | Refused. viewer cannot Approve. Required role: Registrar. | 9 to 7 |
| `ASSIGNMENT_DENIED` | ASSIGNMENT_DENIED: Actor is not assigned in the trusted fixture directory | Refused. teacher-unassigned is not assigned to this excursion, so it cannot Recommend. | 10 to 12 |
| `STALE_INSTANCE` | STALE_INSTANCE: Model changed; reset the isolated preview | Not run. The candidate changed after this preview started. Reset the preview to start again from Draft. | 7 to 17 |
| `CASE_CLOSED` | CASE_CLOSED: Create a new Change Case; this case is closed | Not saved. This case is closed. History is kept. Create a new change case to continue. | 10 to 16 |
| `SOURCE_REVIEW_REQUIRED` | SOURCE REVIEW REQUIRED: implementation differs from the release fixture | Not approved. The source changed since release. Approval stays blocked until the implementation is reviewed. | 9 to 15 |
| `SESSION_REQUIRED` | SESSION_REQUIRED: Use the private launch link | No session. Open the full link printed by eija serve, including the part after #. | 6 to 14 |
| `INVALID_REQUEST` | INVALID_REQUEST: Provide 1–6000 characters of synthetic request text | Not created. Request needs 1 to 6000 characters. Use synthetic text only. | 8 to 12 |

Totals: before 170 words, after 288: errors get **69% longer**, by design (what is unchanged and what to do are new). The class limit is 20 words; the longest rewrite is 20. Every row now passes the whole class rule, checked by `.tmp/onb/errlint.py` and not by hand counting: at most 20 words, at most 4 sentences, each sentence after the tag at most 14 words, tag at most 2 words. The first version of this table failed the tag rule in 8 rows (`EGRESS_CONSENT_REQUIRED`, `PROVIDER_TRANSPORT`, `PROVIDER_OUTPUT_INVALID`, `STALE_INSTANCE`, `CASE_CLOSED`, `SOURCE_REVIEW_REQUIRED`, `SESSION_REQUIRED`, `INVALID_REQUEST`), which the audit found; those rows now start with a short tag (`Not sent.`, `Call failed.`, `Reply discarded.`, `Not run.`, `Not saved.`, `Not approved.`, `No session.`, `Not created.`). The `SESSION_REQUIRED` copy is also the text of the no-session empty state (5.2).

### 9.4 Readability (MEASURED on strings, with a weak instrument)

Flesch-Kincaid grade uses 0.39 x (words per sentence) + 11.8 x (syllables per word) - 15.59 (formula from S18, original Kincaid et al. 1975, which I did not open). Syllables are counted by a vowel-group heuristic, so treat the grades as plus or minus 1. The formula was built for school books (S18) and is not a usability measure. Pooled prose of 8 words or more (baseline 33 blocks and 374 words: 12 static text nodes, 13 notices and other dynamic strings, 8 error messages without their code; proposal 48 blocks and 631 words: HOME lines, rows above, notices, errors, definitions):

| Set | Mean words per sentence | Longest sentence | Flesch-Kincaid grade | Flesch reading ease |
|---|---|---|---|---|
| Baseline | 8.5 | 15 | 11.2 | 29.7 |
| Proposal | 6.2 | 14 | 7.4 | 53.3 |

Sentences were already short in the baseline (only 4% above 14 words). The grade drops mainly because of vocabulary ("institutional", "authorisation", "implementation" leave; registered kernel terms stay). The proposal has more prose in total because it adds definitions and error guidance.

## 10. Quantitative summary

Full arithmetic, constants and validity limits are in HCI-ADR-0065. All numbers are PREDICTION unless marked MEASURED. Flow ids: T10, T09-define-term, T09-define-term-kbd, T08-recover-stale, T06-resolve-blocker (variants of brief tasks T10, T09, T09, T08, T06); the T10 word counts are drafts and must be re-counted on the built screens with the lint.

| Quantity | Baseline | Proposal | Note |
|---|---|---|---|
| Persistent chrome words per workspace screen | 121 MEASURED | 19 draft | frees about 102 words per screen for content; includes the 3-word `human outcomes UNKNOWN` chip (I3) |
| Novel words along the first-run path | 420 | 283 | 33% fewer |
| Reading time of those words at 250 wpm (band 250 to 180) | 100.8 s (100.8 to 140.0) | 67.9 s (67.9 to 94.3) | assumes every word is read (upper bound) |
| First-run action skeleton (KLM, expert floor, all P at 1.1 s) | 16.05 s | 10.95 s | bands 12.7 to 19.4 and 8.7 to 13.3 overlap by 0.6 s: not decisive. With Fitts geometry (S28) on the current flow only, the baseline is 15.11 s (band 11.9 to 18.3) |
| First-run total if every novel word is read (upper bound) | 116.9 s | 78.9 s | ranges 113.5 to 159.4 s and 76.6 to 107.6 s. Reading is 86% of the baseline total and rests on drafted word counts: not evidence of benefit |
| First-run total if 28% of words are read (NN/g upper figure, S5) | 44.3 s | 30.0 s | ranges 40.9 to 58.6 s and 27.7 to 39.7 s; the ordering is set by the word counts (420 against 283), which are hand counts for the baseline and design caps for the proposal |
| First-run total if 20% of words are read (NN/g average, S5) | 36.2 s | 24.5 s | ranges 32.8 to 47.4 s and 22.2 to 32.1 s; same caveat |
| Recover from STALE_VERSION, keyboard-Tab baseline (`T08-recover-stale-kbd`, primary) | 28.3 s | 22.9 s | ranges 22.7 to 34.6 s and 19.1 to 28.6 s **overlap**: no decisive difference. Action skeleton 9.05 s less, reading 3.6 s more (21 words against 6), total 5.45 s less. The proposal re-ticks the acknowledgement (M, P, B). With Fitts geometry on the baseline: 27.6 s |
| Recover from STALE_VERSION, mouse-only baseline (`T08-recover-stale`, strawman: pointer to every field, 8 H) | 33.9 s | 22.9 s | ranges 27.1 to 41.3 s and 19.1 to 28.6 s overlap by 1.5 s; total 11.05 s less. Reported for completeness, not as the comparison |
| Look up a term by click, against a docs window (1 H each side) | 12.7 s | 7.6 s | ranges 11.0 to 16.2 s and 6.9 to 9.9 s do not overlap; keyboard path 12.3 s against 9.0 s (ranges 10.7 to 15.7 s and 8.0 to 11.6 s) overlaps |
| Resolve one blocker | 7.0 s | 6.9 s | no difference within the band (5.7 to 8.6 s against 5.8 to 8.7 s): reading adds 1.2 s, decoding saves 1.35 s |
| Break-even for on-demand definitions | | p* 0.44 (0.41 to 0.49) if every inline word is read; about 0.12 if 28% are read | worth it below this share of visits; not robust to the read fraction |
| Verification wall time | 2.0 to 2.4 s MEASURED | same | Windows 11, Python 3.12.10, 3 runs, 125 observations |
| Error words (20 codes) | 170 | 288 | +69% |
| Notice words (14; N14 is new) | 116 | 72 | -38% (-43% for N01 to N13) |
| Flesch-Kincaid grade of pooled prose | 11.2 | 7.4 | plus or minus 1 |

## 11. Study protocol for content and onboarding (design only; nothing run)

Extends the study in SYN section 8. **Registered protocol id: ONB-1.**

* **Design.** First run is **between-subjects** (baseline Studio versus proposal): once a participant has seen either, they are no longer a first-time user, so a within-subject design cannot test T10. Sub-flows T09-define-term, T06-resolve-blocker and T08-recover-stale are within-subject with order counterbalanced, after the first-run task. **Arm C (vocabulary legibility, tests D1):** a third group sees the proposal with plain-word labels and the kernel word secondary (for example `Unknown` with `UNKNOWN` one level down) instead of verbatim kernel words at level 0; the comparison is misreading of status words and term-to-definition matching, with P3-type participants recruited on purpose. Optional arm D: a dismissible one-time hint on HOME (option F in the ADR). No arm tests a distinct owner verb: the ADR records why one verb wins, and H-ON8 is the revert condition.
* **Participants.** Engineers who have used an AI coding assistant in the last 3 months and have never seen EIJA. A formative round of 5 per arm finds problems but does not estimate prevalence (LAW§2.10); the quantitative comparison needs about 20 users per arm, which Nielsen gives a margin of about 19% of the mean (S27), so a proportion such as the 80% unassisted target will have a wide interval and is reported with it. Include 3 or more keyboard-only participants and 3 or more screen-reader users as a qualitative cohort.
* **Task and framing.** "Decide within 10 minutes whether this tool is worth trying." No documentation is offered; opening README is recorded, not forbidden.
* **Measures.** TTFV-1 and TTFV-2 (section 7.4); first click on HOME; dead ends; documentation opened; **UNKNOWN misread as PASS (target zero)** from a probe question "what does UNKNOWN on this screen mean?", coded by two raters; "who decides whether the change is applied?"; a probe on the coverage row ("what did the verification cover, and what did it not cover?", H1); term-to-definition matching for 8 terms; T08 recovery time and errors after a seeded stale case, including whether the participant notices the cleared acknowledgement; Approve-versus-Approve mis-targeting (V3); glossary opens per participant; Next slot click-through; per-task SEQ; SUS with an interval (compared to 68 only with an interval); Raw TLX.
* **Pre-registered hypotheses.** H-ON1 median TTFV-2 in the proposal is 5 min or less. H-ON2 at least 80% reach TTFV-2 unassisted. H-ON3 zero UNKNOWN-as-PASS misreads in the proposal arm. H-ON4 vocabulary matching accuracy is no lower than baseline. H-ON5 the proposal is not slower on T08 than the baseline; the observed median difference is compared with the predicted 5.45 s (keyboard baseline) to 11.05 s (mouse baseline), whose model ranges overlap, so no direction is claimed in advance beyond non-inferiority. H-ON6 the blocker task is not slower than baseline (the model predicts no difference within the band). H-ON7 verbatim kernel words at level 0 (arm A) do not increase status misreads or lower term-matching accuracy compared with plain words with the kernel word secondary (arm C); if they do, D1's verbatim rule is reversed. H-ON8 owner-verb collision: in the proposal arm no participant confuses the owner's `Approve revision 3` with the Registrar's workflow action `Registrar · Approve` when asked "what will this control do?"; if 2 or more of the first 5 do, the owner verb is changed and retested formatively (`Authorise revision 3` is the first candidate, at the cost of a second word for one kernel act).
* **Analysis.** Medians with bootstrap 95% confidence intervals (times are skewed); effect sizes; no significance-only claims.
* **Stop criteria.** Stop and redesign if, among the first 5 participants in the proposal arm, 2 or more miss the primary action on HOME for 60 s, or 1 or more reads UNKNOWN as PASS, or 2 or more cannot reach TTFV-2 in 15 min. Stop if any participant cannot find the private link recovery. Stop and redesign if any participant approves a reloaded case without seeing that the acknowledgement was cleared.
* **Status.** No results. No benefit is claimed.

## 12. Open questions, risks, UNVERIFIED

| # | Item | Effect | Owner |
|---|---|---|---|
| Q1 | Kernel reason codes for UNKNOWN, STALE, FAIL (A4) | Without them the reason slot says `reason not reported` for FAIL and cannot name the changed dimension | kernel lane ADR |
| Q2 | Case stage PREVIEW collides with Preview Instance (V5) | Popover mitigates; rename is cleaner | kernel lane |
| Q3 | Research docs say "semantic operation"; the language says Semantic Transaction (V6) | UI and docs disagree | review lane and integrator |
| Q4 | Kernel strings say "comprehension" (V7) | UI shows kernel text verbatim, so the drift is visible | kernel lane |
| Q5 | `popover` and `<dfn>` under the strict CSP untested (A7; SYN C15) | Fallback is `<details>` | security spike |
| Q6 | Is Approve versus Approve confusing (V3)? Untested. Alternatives scored in HCI-ADR-0065 (Authorise, Sign off) | Study measure H-ON8 with a revert rule | study lane |
| Q7 | Does sample-first over-promise generality? README supports one domain only | The scope chip popover states "Supported domain: excursion sign-off only" | this doc |
| Q8 | Text budgets are hypotheses; viewport counts were not measured because no build could run here | Re-measure with the slop-budget script | integrator |
| Q9 | Localisation, right-to-left and long identifiers not considered | Out of scope | later |
| Q10 | UNVERIFIED: Brysbaert 2019 reading-rate figures (I could confirm the paper exists, not its numbers, so the 238 wpm figure is not used); Kincaid et al. 1975 original; the research behind NN/g's claim about tutorials; Carroll's minimalism primary sources (S21 is a secondary page); any published benchmark for "time to first value" in developer tools (none found); a vendor-reported figure that 93% of Claude Code permission prompts are approved (synthesis dossier V2; no URL was opened this session, so it is removed from 5.3 and not built on) | Not built on | none |
| Q11 | Is a dismissible contextual hint on HOME (option F) better than the Next slot alone? NN/g lists coach marks as acceptable pull help (S13); nothing measured here | Study arm D | study lane |
| Q12 | Refusal rows as `role="status"` are untested with a screen reader; repeated identical refusals may not be re-announced by some readers (UNVERIFIED, not researched here) | Keyboard and screen-reader test in the ADR validation plan | accessibility lane |

## 13. Sources (all opened 2026-09-29; WebFetch returns a model-written summary, not the raw page)

| Id | URL | What I used | Confidence |
|---|---|---|---|
| S1 | https://www.nngroup.com/articles/empty-state-interface-design/ | Kaplan 2021: empty states communicate status, give learning cues, offer a direct path; no quantitative data. It does not recommend sample or demo data (a demo-data example appears only in passing), so it is not a precedent for sample-first | medium |
| S2 | https://primer.style/product/ui-patterns/empty-states/ | Three kinds of empty state; purpose first; "There was a problem" is vague; no playful art for errors; avoid obscure error codes | medium |
| S3 | https://code.visualstudio.com/api/ux-guidelines/walkthroughs | Avoid excessive steps; an action for each step; action-oriented language | high |
| S4 | https://www.nngroup.com/articles/error-message-guidelines/ | Neusesser and Sunwall 2023: plain language, constructive advice, near the source, preserve input, hide obscure codes, avoid blaming words; also "avoid technical jargon", which argues against verbatim kernel words in error text | medium |
| S5 | https://www.nngroup.com/articles/how-little-do-users-read/ | Nielsen 2008: at most 28% of words read (2005 data, 25 users, general web pages), about 4.4 s per 100 added words, 250 wpm assumed, half read at 111 words or fewer | medium; not app screens |
| S6 | https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html | SC 4.1.3, Level AA | high |
| S7 | https://www.w3.org/WAI/WCAG22/Understanding/error-suggestion.html | SC 3.3.3, Level AA; covers automatically detected input errors when a suggestion is known | high |
| S8 | https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html | SC 1.4.13 (AA): dismissible, hoverable, persistent; applies to content shown on hover or focus, not to click-opened content | high |
| S9 | https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html | SC 1.4.1, Level A | high |
| S10 | https://developer.mozilla.org/en-US/docs/Web/API/Popover_API | `popover`, `popovertarget`, light dismiss, no JavaScript needed; Baseline 2025 newly available (January 2025) | high |
| S11 | https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dfn | `<dfn>` marks the defining occurrence; definition must be nearby | high |
| S12 | https://martinfowler.com/bliki/UbiquitousLanguage.html | Ubiquitous language: Evans; shared, rigorous, used in code and conversation | medium |
| S13 | https://www.nngroup.com/articles/onboarding-tutorials/ | Laubheimer 2023: tutorials do not improve task performance; prefer pull revelations, and the article lists hover tooltips, coach marks and step-by-step flows as acceptable pull help | medium |
| S14 | https://www.nngroup.com/articles/tooltip-guidelines/ | Kendrick 2019: essential information stays visible; tooltips fail keyboard and touch; brevity | medium |
| S15 | https://www.nngroup.com/articles/progressive-disclosure/ | Nielsen 2006: typically 2 disclosure levels | medium |
| S16 | https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice | Sentence case, front-load, be brief; also "avoid jargon" (argues against verbatim kernel terms) | high (vendor style guide) |
| S17 | https://primer.style/design/guides/content | Sentence case, imperative buttons, specific errors, consistent terms, "clarity over consistency" | medium |
| S18 | https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests | Formulas; cites Kincaid et al. 1975; built for school books | medium (secondary) |
| S19 | https://storybook.js.org/docs/get-started/install | Init generates example stories; a new user who opts in is welcomed with an interactive tour (counter-evidence to D6; the tour is opt-in) | high |
| S20 | https://pair.withgoogle.com/chapter/errors-failing/ | Disclose limitations specifically; return control; "humanity and humility" (tone argues against our neutral voice) | medium |
| S21 | https://en.wikipedia.org/wiki/Minimalism_(technical_communication) | Carroll's minimalism: action-oriented, real tasks, error recovery | low (secondary) |
| S22 | https://code.visualstudio.com/api/ux-guidelines/command-palette | Clear command names, category prefixes, no emoji | high |
| S23 | https://en.wikipedia.org/wiki/Words_per_minute | Proofreading at 200 wpm on paper and 180 wpm on a monitor (pre-1992 studies), the low end of the reading band | low |
| S24 | https://en.wikipedia.org/wiki/Keystroke-level_model | KLM operator times, 21% RMS error, expert error-free limit; constants also in LAW§2.4 | medium (secondary) |
| S25 | https://developer.mozilla.org/en-US/docs/Web/API/Popover_API/Using | Light dismiss by click outside or Esc; focus returns to the invoker on Esc; `popovertarget` needs no JavaScript | high |
| S26 | https://www.nngroup.com/articles/response-times-3-important-limits/ | Nielsen 1993: 0.1 s feels instantaneous, 1 s keeps the flow of thought, 10 s keeps attention; used for the popover and RUNNING targets | medium (perceptual limits, conventions) |
| S27 | https://www.nngroup.com/articles/quantitative-studies-how-many-users/ | Nielsen 2006: test with 20 users for a quantitative study; margin of error about 19% of the mean | medium |
| S28 | https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf | Cockburn, Gutwin and Greenberg, CHI 2007: menu pointing Tp = 0.37 + 0.13 ID s (R2 0.93), 8 participants, mouse; PDF text read locally with pdftotext; used only for the Fitts sensitivity. The paper states no ID validity range; the 2 to 8 bit range is LAW§2.1 (Soukoreff and MacKenzie 2004) | high for the formula, medium for transfer |
| S29 | https://code.claude.com/docs/en/quickstart | Claude Code quickstart: no tour; the first steps ask about the user's own project ("what does this project do?") and about the tool itself, then a small change the user may be asked to approve | high (official docs) |
| S30 | https://cursor.com/docs/get-started/quickstart | Cursor quickstart: ask the agent to explain the codebase, make a small change, review the diff, run the project's checks; no tour or sample project | high (official docs; WebFetch summary) |
| S31 | https://code.visualstudio.com/docs/agents/quickstart?agent-surface=chat-view | VS Code agent quickstart (updated 2026-09-16): empty folder, the agent builds a small app, the user reviews the diff and can restore a checkpoint; no tour | high (official docs; WebFetch summary) |
| R | this repository | index.html, app.js, app.css, policy.py, compiler.py, evidence.py, impact.py, change_case.py, service.py, runtime.py, providers.py, http.py, ARCHITECTURE.md, README.md, AGENTS.md | high |
| M | measurements | `.tmp/regions.py` (static words), `.tmp/screens.py`, `.tmp/eija_copy.py`, `.tmp/readability.py`, `.tmp/gen_flows.py`; KLM and Fitts recomputation `.tmp/onb/klm_rev.py`, `.tmp/onb/fitts_rev.py`; real identifiers `.tmp/onb/real_run.py`; verification timing: `verify_runtime` on `examples/excursion-candidate.json` in an ephemeral sandbox, 3 runs, 2.17, 2.38 and 2.01 s, Windows 11, Python 3.12.10, 2026-09-29 | high for what it measures |
