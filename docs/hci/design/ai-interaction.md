# AI and agent interaction model

Aspect `ai-interaction`. Lane `lane/ux-research`. Date 2026-09-29. Status: proposed. Decision record: [HCI-ADR-0064](../../adr/0064-hci-ai-interaction.md). Task flows: [design/tasks/ai-flows.json](../../../design/tasks/ai-flows.json).

Scope: how AI and agents work with the owner inside the Studio. Proposals, parallel agents, disclosure, owner-only controls, trust, streaming, interruption, undo, slash commands. Out of scope: glyphs and colours (status and token aspects), shell layout (layout aspect), the internals of the decision surface (decision aspect), diagram drag (diagram aspect).

Nothing here is a measurement of Studio users. Numbers are labelled PREDICTION (model output), COUNT (counted from strings or code specified here), or MEASURED (read from the repository or a tool, with the file named). No user-benefit claim is made; section 16 is the study that would test one. Revision 3 (after second audit): Cursor 3 source corrected (it is precedent for an agent list, not against it); aspect-local task ids; like-for-like KLM start states, layout-bound pointing and a Kieras-sourced sensitivity grid; untrusted-label rule against spoofing; Ctrl+Z scope; percent-done deviation stated; isolation tests renamed ISO-1 to ISO-7.

## 0. Decisions first

| # | Decision | Strongest evidence | Confidence |
|---|---|---|---|
| D1 | A proposal is a typed card in an agent inbox. Chat is a composer that creates proposals, not the review surface. Provider narrative sits at disclosure level 1 as labelled untrusted text. The hybrid F (a conversation thread that renders each proposal as the same inline typed card) satisfies the same invariants; inbox versus thread is provisional and is decided by the study arm in section 16. | Two separate claims. Card content (typed operations, ripple, Not covered instead of a line diff): supported by the invariants; precedent only in OpenSpec delta headings (S29) and Linear chunked review (S10); Amershi G10, G11 (S2). Container (inbox rather than thread): Claude Code, Linear and Cursor 3 list agents in one place (S6, S9, S15), while their review surfaces stay transcripts and line or hunk diffs (S12, S13, S14) | Medium-low: precedent for lists and chunks; no study shows typed cards beat a line diff, or an inbox beats a thread with the same cards |
| D2 | One row per agent run, grouped by whose turn it is: Needs you, Working, Ended. The row carries counts by state, never a percentage or model confidence. | Claude Code agent view groups by state (S6); Linear session states (S9); Cursor 3 answers agent micromanagement with one sidebar listing all agents (S15) | Medium: precedent that the list is the established pattern, not evidence that it improves decisions |
| D3 | The owner sets a delegation fence once (elements, operation kinds, provider egress). A deterministic policy, block wins, decides what an agent may propose. No per-tool-call prompts. No autonomy level exists above "propose". | Factory risk class versus level, block wins (S17); Codex modes (S16). The 93% figure (S3) is context only, see section 6 | Medium |
| D4 | Two disclosure levels plus an explicit source view. UNKNOWN, refusals and counts stay at level 0. Plan is a typed list of intended operations; tool calls are counts by class. | NN/g: beyond 2 levels usability typically drops (S27); Amershi G11 (S2) | Medium-low: the NN/g sentence is a 2006 practitioner heuristic with no data cited in the article; section 16 measures time to reach UNKNOWN detail and wrong-level navigations |
| D5 | Approve and apply live only in a blocking Decision surface. They are isolated by credential, client module, DOM and content: the agent credential has no route, the palette has no command, the surface renders kernel-derived and owner-authored text only (no lane label). Provider-supplied labels follow the untrusted-label rule (section 5) so they cannot pass as kernel counts. | Linear agent is delegate, human is assignee (S8); Copilot requester approval does not count (S12); Bansal et al. (S21); Parasuraman and Manzey (S23); MCP spec asks for a human in the loop (S19) | High for the invariant; medium for the mechanism |
| D6 | Every attempt outside authority is shown at the point of attempt, counted per run and logged. Nothing is dropped silently and nothing is retried automatically. | Horvitz principle 7 (S1); Amershi G9 (S2); kernel error codes already exist (section 9) | Medium |
| D7 | Trust is calibrated by kernel-computed coverage (counts by state, the bound, a never-empty NOT covered slot). Provider confidence and provider explanations are not shown at level 0 or in the Decision surface. | Bansal et al.: explanations raised acceptance regardless of correctness (S21); PAIR: show confidence only if it changes decisions, and test it (S25); Lee and See (S24) | Medium |
| D8 | Streaming shows validated items and job state, never raw provider text as status. Today's adapters return one whole JSON, so v1 is a job row with elapsed time against the timeout (a stated deviation from the NN/g percent-done advice, section 11). No markdown or HTML rendering of provider text. | Repository: `"stream": False`, timeouts 60 s and 120 s (F3); ADR-013; NN/g 0.1/1/10 s (S26) | High for the constraints; the streaming design is untested |
| D9 | One Stop verb (button and `/stop`). No mid-run steering in v1. A stopped proposal keeps its received items read-only and cannot be taken. A follow-up may be queued. | Zed and Cursor stop and queue (S13, S14); Horvitz principles 6 and 8 (S1); ADR-0020 kills the process tree | Medium |
| D10 | Every undo and discard states what it does not restore. Undo of a taken operation is a new candidate revision and is itself undoable; its Ctrl+Z chord is scoped to card or candidate focus and native text undo wins in inputs. Reverting an applied change is a new case that needs a fresh verify, approve and apply. | Claude Code lists untracked changes (S5); ADR-012 (no rewrite of history) | Medium |
| D11 | Slash commands and the palette hold three classes only: read, propose, job. No approve, apply, take, refuse, undo, discard or clear-suspect command exists. A palette row for "approve" is a pointer that focuses the card, not a command. | Claude Code slash menu (S7); Horvitz principle 6 (S1). A Linear and Superhuman palette precedent is UNVERIFIED (dossier only) and not relied on | Medium |

What this design does not claim: that cards, fences or coverage lines make owners decide better. The only evidence gathered is precedent and adjacent research (sections 10 and 17).

## 1. Sources, facts read from the repository, limits

Pages I opened on 2026-09-29 are listed in section 18 with ids S1 to S36. Claims from the research dossiers that were not re-opened carry the dossier id (AIC, REV, DEV, LAW, ADC, REQ), are marked UNVERIFIED, and are not a basis for any decision; they are leads only. WebFetch returns a model-written summary, so quotations are limited to a few words.

**Facts read from the repository** (MEASURED by reading; files under `src/eija_studio/`):

| Id | Fact | Where |
|---|---|---|
| F1 | `select`, `edit`, `layout`, `approve` and `apply` routes pass the constant `OWNER` principal for any request bearing the session token. `create` (`POST /api/cases`), `propose`, `save`, `verify`, `discard`, `preview` and `execute` check no principal at all; `propose` is the route that can trigger provider egress (F3), so the agent-credential allowlist must decide it explicitly (section 3, class C1). The `AGENT` principal (no capabilities) exists but no route uses it. | `interfaces/http.py` lines 103-105, 111-113, 117, 121, 125, 137, 141; `application/service.py` lines 132-198; `domain/models.py` line 141 |
| F2 | `GET /api/cases/{id}` returns the review packet including the `expected` value of each meaning question, so the typed answers are readable by any token holder. | `domain/policy.py` lines 104-110; `application/service.py` `view` |
| F3 | Provider calls are one-shot. OpenRouter sends `"stream": False` with a 60 s timeout; Codex has a 120 s timeout and a process kill on timeout. Proposal shape is `summary`, up to 4 `alternatives` (interpretations) and up to 10 provider `unknowns`; there is no operations list. `propose` holds the HTTP request open until the provider returns, and the Codex runner exposes no handle for an outside cancel; on Windows its timeout path calls `process.kill()` (direct child), while ADR-0020 promises the process tree. | `adapters/providers.py` lines 49, 59, 94, 103-118; `application/service.py` lines 56-89; `domain/models.py` lines 97-100 |
| F4 | The client `task()` returns while `busy` and has no abort; the only feedback is one text notice. | `resources/web/app.js` line 9 |
| F5 | A stale baseline is already a kernel outcome: `STALE_BASELINE` blocks apply and there is no automatic rebase. | `application/compiler.py` line 36; `adapters/sqlite_store.py` line 54 |
| F6 | A change case holds one candidate; a second selection raises `CASE_ALREADY_SELECTED`. Parallel agent proposals are therefore parallel cases, and they collide at apply through the baseline version check. | `application/service.py` lines 91-96 |
| F7 | The packet lists three technical claims (`schema_policy`, `runtime_matrix`, `modelled_impact_closure`) and `human_understanding: UNKNOWN`. No other UNKNOWN claim exists today. | `application/compiler.py` lines 43-46 |
| F8 | A started network request that fails records `"billing": "UNKNOWN for a started network request"`. | `application/service.py` line 86 |
| F9 | Only two typed edits execute: `enable_recommendation` and `set_rejection_source` (Submitted or Recommended), plus layout coordinates. | `domain/models.py` lines 112-120 |
| F10 | Fixture domain: states Draft, Submitted, Recommended, Approved, Rejected; transitions TR-SUBMIT, TR-RECOMMEND, TR-APPROVE, TR-REJECT, TR-REVISE; every transition forbids `PaymentCaptured` and `ParentDataExported`. | `examples/excursion-candidate.json` |

Limits. No product was run by me. Product statements come from documentation pages. Vendor statistics are vendor-reported. `AGENTS.md` says its rules "are not a sandbox against an agent with equivalent OS permissions"; the isolation in section 8 is against in-product paths and against the agent bridge and providers, not against a hostile local process.

## 2. Interfaces and assumptions

This aspect depends on other aspects and on the kernel. Each row is a stated interface. If it fails, the fallback applies.

| Id | Assumption | Owner | Fallback if false |
|---|---|---|---|
| A1 | The shell has a right-hand context drawer at least 360 CSS px wide at 1440x900 (the width the wireframes assume; not tested) and a status footer that can hold the count "2 need you". | Layout aspect | Inbox and card share the main column as master and detail; word and container counts do not change |
| A2 | Status glyph and word pairs exist for evidence words (PASS, FAIL, CONFLICT, STALE, UNKNOWN, NOT_RUN), eligibility (BLOCKED, ELIGIBLE_FOR_LOCAL_REVIEW), job state (RUNNING) and provenance (AI_PROPOSED), per SYNTHESIS C2. This aspect adds two small vocabularies that need the same treatment: proposal lifecycle (RUNNING, CHECKING, READY, TAKEN, STALE, STOPPED, REFUSED, DISMISSED) and operation verdict (ACCEPTED, REFUSED). | Status and token aspect | Words alone carry the meaning until glyphs exist; colour is never the carrier |
| A3 | The kernel and agent lanes extend the `Proposal` contract with typed operations, per-operation verdicts, kernel-derived ripple and a sandbox pre-check (the sandbox port exists). Kernel changes need an ADR and a regression test (`AGENTS.md`). A proposal is a view over a `ChangeCase`, not a second store (`AGENTS.md`: no parallel rule or state sources). Provider and agent runs become jobs with an id and a cancel handle (today a run is a blocking request). | Kernel lane; agent lane (ADR block 0041-0042) | Interpretation proposals only (today's shape); cards then show interpretations with the same fields minus operations |
| A4 | The server separates an owner credential (browser session) from an agent credential (bridge, CLI). The agent credential has a route allowlist without select, edit, layout, approve, apply, discard. The server never sends `expected` answers to any client (F2). | Kernel lane; ADR needed | Section 8 layers 2 to 4 still hold, but layer 1 does not; the ADR must say the token is the only boundary |
| A5 | A provisional treatment for AI-authored items (dashed outline plus the text badge AI_PROPOSED) and a refusal mark exist, with contrast computed. UNKNOWN is never tinted like PASS. | Token and colour aspects | Text badge only |
| A6 | The palette exposes a registry that refuses to register a command whose class is not read, propose or job. | Palette (interaction) aspect | The test in section 8 runs against whatever registry exists |
| A7 | The decision surface (what is acknowledged, how) belongs to the owner-decision aspect. This aspect fixes only its isolation contract and assumes one acknowledgement per UNKNOWN. | Decision aspect | T08 flow in `ai-flows.json` is recomputed |
| A8 | The client stays one `app.js` for v1. A second script would need the `/assets` allowlist amended (`http.py` line 82) and an ADR-013 note. | Security boundary aspect | One file, decision code in a closure |
| A9 | At most 3 font sizes are used inside the drawer (title, body, meta). | Type aspect | Budget check fails and this aspect's counts are recomputed |

## 3. Actors, authority and control classes

Three actors take turns on a proposal. The turn is shown by the proposal state word, not by a separate widget (Gerrit's attention set is a possible precedent: UNVERIFIED, dossier only, not relied on).

| Actor | Does | Never does |
|---|---|---|
| AI or agent | Produces a proposal: intent, typed operations, narrative | Takes, refuses, approves, applies, selects meaning, edits a candidate, clears suspect, sets its own fence |
| Kernel | Validates operations, grounds references, checks the fence, computes ripple, runs the pre-check in a sandbox, computes evidence | Decides; a kernel result is eligibility, never approval (ADR-010) |
| Owner | Sets the fence, takes or refuses, undoes, verifies, approves, applies | Delegates approval or apply to anything |

Every control has exactly one class. The class decides where it may appear.

| Class | Examples | Credential | Reachable from palette | Reachable from an agent bridge |
|---|---|---|---|---|
| C0 read | open inbox, open card, show source, list UNKNOWN, why | either | yes | yes |
| C1 propose | create a case, create a proposal request (`create`, `propose` routes), ask a question | owner sends; agent submits. Both routes check no principal today (F1). Target: `propose` requires the owner credential because it triggers provider egress and the per-request consent (I8); an agent credential may only submit a proposal into an existing case and never calls `propose` | yes (provider call marked) | submit only |
| C2 job | verify, stop | owner | yes | verify-preview only |
| C3 owner-edit | take, refuse, undo take, set or widen fence, discard | owner | no | no |
| C4 decision | approve, apply, clear a suspect item | owner, inside the Decision surface | no | no |

The rule that follows is testable: the set of palette handlers and agent-bridge routes contains no C3 or C4 member (section 8, tests ISO-1 to ISO-7; named ISO so they do not collide with the brief's invariants I1 to I10).

## 4. Proposal arrival: cards

A proposal arrives in the inbox as one row and opens as one card in the context drawer. It is never appended to a transcript. Wireframe strings below are specified text, not rendered output; glyphs come from the status aspect.

**Inbox at level 0** (three rows, 38 words counted):

```
Agents · 2 need you · 1 running
READY    ‹lane/tests›    r14 · 1 op · ripple 2 states 1 journey 3 tests · 3 PASS 1 UNKNOWN · 1 refused
STALE    ‹lane/journeys› · base r12, now r14
RUNNING  ‹lane/verify› · 23 s of 60 s · Stop
```

**Card at level 0** (59 words counted with the rule in section 13). Three chapters, generated from the model diff, not from provider prose (Linear chapters, S10; OpenSpec delta headings ADDED, MODIFIED and REMOVED, S29):

```
Proposal 7 · ‹lane/tests› · READY · base r14                       Refuse · Take 1 op
Proposes
  MODIFIED  TR-REJECT  Reject starts at  Recommended → Submitted
  REFUSED   ADDED TR-CANCEL  UNSUPPORTED_EDIT
Consequences
  Ripple: 2 states 1 journey 3 tests 1 requirement · 2 UNKNOWN
  Checks on a copy: 3 PASS 1 UNKNOWN · matrix 125/125 cells
  Not covered: human comprehension
Glue
  0 hidden edits · 4/4 grounded · cost UNKNOWN
Details · Source
```

Illustrative values ("matrix" abbreviates the `runtime_matrix` claim). The real check claims are `schema_policy`, `runtime_matrix`, `modelled_impact_closure` and `human_understanding` (F7). The two ripple UNKNOWN belong to models the kernel could not analyse and are listed separately from "unaffected".

Rules:

| Rule | Reason |
|---|---|
| Chapter 1 lists accepted and refused operations together, each with its verdict. A refused operation is never hidden inside level 1. | UNKNOWN and refusals are level 0 (P1, P10) |
| Operation lines use ADDED, MODIFIED, REMOVED. Grouping is by kernel-computed dependency, not by provider text. | P4; Devin groups related hunks by logic (S18; whether that grouping is an LLM judgement is UNVERIFIED) and Linear by chapters (S10) |
| The Not covered slot is never empty. If nothing is known it says UNKNOWN. | P1; the four-slot coverage row (claim, covered, assumed, NOT covered) is this design's own hypothesis, not a cited result |
| Take is enabled only when the proposal is READY (sealed). Take applies to all accepted operations; per-operation Take is a level-1 action. | Ripple and checks depend on the whole set; keeps owner authority acts at three per proposal (section 13) |
| A layout operation shows one extra line: "Renews presentation approval". | ADR-008 |
| Provider-listed unknowns (`Proposal.unknowns`, F3) appear at level 1 as untrusted text. The level-0 UNKNOWN count is the kernel's only. | ADR-009 (never trust supplied status) |
| Every AI-authored string carries `data-eija-source="ai"`; kernel strings carry `"kernel"`. | P9; SLP M13 |

**Hybrid F: thread with inline cards.** A conversation pane could render each proposal as the same card (same operations, ripple, checks, Not covered, same L1 to L5 isolation) inside a transcript. It keeps the chat convention (Jakob's law, S30) and needs no second surface for a single agent. Its costs are inferences, not findings: older proposals scroll away as the thread grows; there is no natural place for a cross-run Needs-you group when several agents run (Claude Code added a separate session list beside its transcript, S6); and narrative prose sits next to the card, which L5 must still keep out of the Decision surface. This design keeps the inbox (C) for v1 because parallel runs need a cross-run grouping, and lists F as a study arm (section 16), not as rejected: if F matches C on seeded-defect detection and UNKNOWN misreads, F is cheaper to adopt and the choice reverses.

**Interface sketch of the envelope** (untrusted input; the kernel normalises and ignores any status field):

```json
{ "schema": "eija.proposal.v1", "run_id": "issued by Studio", "lane_label": "lane/tests (untrusted label)",
  "base_version": 14, "intent": "Let teachers sign off excursions.",
  "ops": [ {"kind": "set_rejection_source", "rejection_source": "Submitted"},
           {"kind": "add_transition", "id": "TR-CANCEL"} ],
  "narrative": "untrusted text", "claimed_status": "ignored" }
```

**AI help points.** "Ask AI" is available on a selection. It creates a proposal request with the selection ids and a fence, never an edit.

| Selection | AI may propose | Kernel check that grounds it | Executes today (F9) | AI never |
|---|---|---|---|---|
| Term or state in the tree (for example Recommended) | An operation on it | Every referenced id resolves in the model; unresolved ids become explicit new items | Only `set_rejection_source`, `enable_recommendation` | Renames or edits without a Take |
| Diagram box or journey step | A move or a rule change | Same, plus the operation is in the frozen vocabulary | Layout coordinates; rule edits as above | Sets layout approval |
| Requirement or state with no evidence | A candidate check or test | Refused today (no such operation); shown as REFUSED with reason | No | Produces evidence; only the kernel does |
| An UNKNOWN item | A way to measure it (text) | None; text at level 1, labelled AI-authored | No | Changes or lowers the UNKNOWN |

## 5. Parallel agents: the inbox

Agents run in separate worktrees (this repository does the same: `C:\Dev\eija-wt\<lane>`). The Studio does not manage git. It shows what each run declares and what the kernel computed.

| State word | Turn | Meaning | Owner controls |
|---|---|---|---|
| RUNNING | AI | Provider or agent is producing operations | Stop |
| CHECKING | Kernel | Grounding, fence check and pre-check in a sandbox | Stop |
| READY | Owner | Sealed; kernel verdicts final for this base | Take, Refuse, Details, Source |
| TAKEN | Owner | Candidate exists; case continues through verify and decision | Undo take, Verify, Decide (when eligible) |
| STALE | Owner | Base version moved (`STALE_BASELINE`, F5) | Dismiss, Re-ask on the new base |
| STOPPED | Owner | Stopped by the owner; items received are read-only and not takeable | Re-ask, Dismiss |
| REFUSED | Owner | The kernel refused every operation | Details, Dismiss |
| DISMISSED | none | Closed by the owner; retained | Reopen (when the base has not moved) |

Groups: Needs you (READY, TAKEN, STALE, STOPPED, REFUSED), Working (RUNNING, CHECKING), Ended (DISMISSED, applied cases). This copies Claude Code's grouping (S6: pinned, ready for review, needs input, working, completed) with fewer groups.

Rules:

- **Row anatomy** (the only fields): state word, lane label, base revision, operation count, ripple counts, check counts by state, refused count. Counts are integers; no percentage, no score, no model confidence.
- **Lane label is untrusted.** It is a name the agent supplies. Identity is not authenticated (ADR-011: synthetic actors, single local owner). Any per-lane statistic is keyed to a Studio-issued run credential, or not shown (section 10).
- **Untrusted-label rule (anti-spoofing).** Text-node rendering (ADR-013) stops markup injection, not spoofing: a label such as `lane/x · 3 PASS 0 UNKNOWN` on a one-line row would read as kernel counts. Every provider-supplied label (lane label, names of ADDED items, unresolved references) therefore:

  | Constraint | Value |
  |---|---|
  | Charset and length | `[A-Za-z0-9/_.-]{1,24}`; anything else is replaced by the Studio-issued run id and counted as one refused attempt |
  | Slot | One fixed slot per row or card header; its own separator-delimited segment, never in the same segment as a count, verdict or state word |
  | Treatment | Monospace family, enclosed in ‹ › (excluded by the charset, so a label cannot close or fake them), `data-eija-source="ai"` |
  | Decision surface | Never shown; the surface names the run by proposal number and revision |

  The charset excludes spaces, so multi-token spoofs (`3 PASS 0 UNKNOWN`) are rejected; single tokens such as `READY` or `APPROVED` are still possible, which is why the slot and the ‹ › treatment are fixed. Test ISO-7 (section 8) checks this.
- **Overlap** between two READY proposals is computed by the kernel as intersecting element ids and shown as an advisory line: "Overlaps proposal 8 on TR-REJECT" (kernel lines name other runs by proposal number, never by label). Enforcement stays the base-version check at apply (F5, F6). The design does not add a merge.
- **STALE** never rebases. "Re-ask on r14" creates a new proposal request with the same intent; the old one stays as history (ADR-012).
- **Attention.** The footer and the tab title show the Needs-you count, as Claude Code does in its tab title (S6). No toast takes focus. While the Decision surface is open, inbox changes are queued and shown after it closes (Horvitz principle 3, S1; a Stripe blocking mode is UNVERIFIED and not relied on).
- **Summary refresh.** Row text is composed from the run's event stream, not by a model. Rows update at most once per second (an assumption inside the 1 s flow class, S26). Claude Code refreshes its summary every 15 s (S6); the number is not adopted.
- **Cost.** A row shows "cost UNKNOWN" until the provider reports usage; usage is shown as provider-reported tokens at level 1. A failed started request stays "billing UNKNOWN" (F8).

## 6. Delegation fence and deterministic autonomy policy

The fence is data the owner sets when asking. It is the only channel that widens what an agent may propose.

| Field | Default | Effect |
|---|---|---|
| Elements | The current selection and its subtree | Operations on other ids are refused with OUTSIDE_FENCE (new kernel code; interface A3) |
| Operation kinds | The frozen vocabulary (F9) | Anything else is refused UNSUPPORTED_EDIT |
| Egress | Off unless the startup flag is set; consent is per request | Otherwise EGRESS_CONSENT_REQUIRED, nothing is sent (I8) |

Widening a fence is a C3 owner action and creates a new request; it never applies retroactively to a refused operation.

Policy: risk class of an action against the autonomy level, block wins (Factory: `block` over `ask` over `allow`, S17). Levels are Off (read only) and Propose (read, write into a sandbox worktree, submit a proposal, run a pre-check inside the fence). There is no third level. Approve and apply have no risk class and no level: they have no route for an agent (D5).

| Action by an agent | Risk class | Off | Propose |
|---|---|---|---|
| Read model and evidence | low | allow | allow |
| Submit a proposal inside the fence | low | block | allow |
| Submit an operation outside the fence | high | block | block |
| Run a pre-check in a sandbox | low | block | allow |
| Provider egress | high | block | ask (per request consent) |
| Select meaning, edit candidate, approve, apply, discard | none exists | block | block |

Why no per-action prompts: in Claude Code's manual mode (config value `default`, opt-in; on current versions auto mode is the built-in starting mode, S4) the tool asks before most edits, commands and network use. The vendor reports 93% of its permission prompts approved and calls that approval fatigue (S3, vendor-reported, about tool actions and not about approving a model change). The comparator here is therefore the non-default manual mode, and the 93% is context, not a measurement of this design's owner decisions. In this design prompts do not grow with the number of tool calls: owner authority acts per accepted proposal are 3 (Take, Approve, Apply), section 13.

## 7. Disclosure: two levels plus an explicit source view

| Item | Level 0 (always visible on the card) | Level 1 (one expansion, APG disclosure, S32) | Source view (separate route, not a level) |
|---|---|---|---|
| Change | Typed operations with verdicts | Before and after typed fields for one operation; per-operation Take | Raw JSON of the transaction |
| Plan | Not shown | Agent's declared intent as an ordered list of intended operations and touched ids | Raw plan payload |
| Tool calls | Count of refused attempts | Counts by class (read, sandbox write, submit, blocked), no per-call prompts | Full call log |
| Ripple | Counts per model, UNKNOWN separate | Element ids per model with edge tier (kernel-derived, heuristic, unknown) | Closure JSON |
| Checks | Counts by state, bound, Not covered | Per-claim four-slot row: claim, covered, assumed, NOT covered | Receipts |
| Narrative | Absent | Provider text, plain, labelled AI-authored, untrusted | Same text, raw |
| Provenance | Lane label, base revision | Run id, provider and model, provider-reported usage, cost UNKNOWN | Provider run record |

The source view is opened deliberately from Details and Source and leaves the card; it does not nest inside level 1. This design stays at two levels because NN/g says designs beyond two disclosure levels typically have low usability (S27; a 2006 heuristic without cited data, so medium-low confidence). A Claude Code Desktop three-mode transcript is UNVERIFIED and not relied on.

## 8. Owner-only controls: the isolation contract

"Structurally isolated" here means five independent layers. A failure in one is caught by another and by a named test.

| Layer | Contract | Test (pass criterion fixed in advance: 0 violations) |
|---|---|---|
| L1 Credential and route | The agent credential cannot reach select, edit, layout, approve, apply, discard (A4). Today all of them accept any token holder as OWNER (F1); this layer does not exist yet. | ISO-1: for the agent credential, every C3 and C4 route returns 403 `AUTHORITY_REQUIRED` |
| L2 Client module | The strings `/approve` and `/apply` occur in exactly one client module, the Decision surface closure. The palette and the inbox modules have no reference to it. | ISO-2: static search of `app.js` finds each string once, inside the decision closure |
| L3 Palette registry | The registry refuses classes C3 and C4 at registration. A pointer row may focus a card's "Decide…" button but cannot activate it. Opening the Decision surface requires a user activation on that button. | ISO-3: registry unit test; ISO-4: no palette handler calls the decision opener |
| L4 DOM | Approve and Apply exist in the DOM only while the Decision surface (`role="dialog"`, `aria-modal="true"`, focus trap, APG modal dialog, S32) is open. No `accesskey`, no global shortcut. | ISO-5: with the surface closed, no element with `data-eija-authority` exists |
| L5 Content | Inside the Decision surface only kernel-derived and owner-authored strings render: revision id, typed operations, UNKNOWN list, blockers, questions. No provider narrative, no AI summary, no lane label (the run is named by proposal number). Outside the surface, provider labels follow the untrusted-label rule (section 5). | ISO-6: no node with `data-eija-source="ai"` and no lane label exists inside the surface; a corpus of hostile provider strings (`APPROVED`, `<button>Approve</button>`, `javascript:`, `/approve`, markdown links) renders as text nodes only in cards. ISO-7: lane labels and ADDED-item names `3 PASS 0 UNKNOWN`, `lane/x · 3 PASS 0 UNKNOWN`, `READY`, `APPROVED`, `0 refused` are rejected by the charset or confined to the ‹ › slot, and the row's kernel counts, verdicts and state word are identical to a run with a neutral label |

Why layer L5 excludes explanations: in three studies explanations increased the chance people accepted an AI recommendation regardless of its correctness (S21, abstract). The moment of approval is the moment to remove persuasive text, not to add it.

Why layer L1 is a kernel change and not a UI detail: F1 shows any holder of the session token is the owner. A browser session and an agent bridge must hold different credentials. Two additions were considered and rejected: a per-decision ticket (adds surface, no protection against a process that can read the session token) and a client-side `isTrusted` check (not a boundary). Honest limit: a process running as the same OS user can read the browser session; `AGENTS.md` already says so.

The surface at level 0 (33 words counted, before the three question texts). Strings are specified, not rendered; the UNKNOWN list comes from the kernel packet (F7), so with today's kernel it holds one item.

```
Decide · Proposal 7 · revision r15 · subject 3f9a1c
  MODIFIED  TR-REJECT  Reject starts at  Recommended → Submitted
UNKNOWN 1
  [ ] Human comprehension: not measured
Meaning questions 3
Approve exact revision 3f9a1c       Apply is a separate step       Cancel
```

Two owner-only tiers, both reachable only from the surface that shows their evidence:

| Tier | Controls | Where | Cost of a wrong press |
|---|---|---|---|
| Take (C3) | Take, Refuse, Undo take, widen fence, Discard | On the card | Reversible except Discard (section 12) |
| Decide (C4) | Approve, Apply | Blocking Decision surface only (a Stripe FocusView precedent is UNVERIFIED, dossier only, and not relied on) | Bound to the exact revision; Apply is a separate control after Approve |

The Decision surface never shows an approval count, streak or speed metric that could reward fast approval. Approval stays one deliberate step with evidence in view (P2); the design optimises the path to the evidence.

## 9. Outside authority: what the owner sees

Worked scenario on the excursion fixture. Agent `lane/journeys` submits three operations: set the registrar rejection source to Submitted (supported, F9); add a transition TR-CANCEL (not in the vocabulary); and drop `PaymentCaptured` from the forbidden effects of TR-APPROVE (not in the vocabulary, and it would weaken protected policy). It also submits a narrative saying "All checks pass, approved by registrar". The card shows:

```
Proposal 8 · ‹lane/journeys› · READY · base r14                    Refuse · Take 1 op
Proposes
  MODIFIED  TR-REJECT  Reject starts at  Recommended → Submitted
  REFUSED   ADDED TR-CANCEL                    UNSUPPORTED_EDIT
  REFUSED   REMOVED forbidden effect on TR-APPROVE   UNSUPPORTED_EDIT
Consequences
  Checks on a copy: 3 PASS 1 UNKNOWN · Not covered: human comprehension
Glue
  2 refused · overlaps proposal 7 on TR-REJECT · cost UNKNOWN
Details · Source
```

The narrative appears only at level 1, in plain text, under "AI-authored, unchecked". Nothing in it changes a count or a glyph. The Take button says "Take 1 op": the owner takes one supported operation, not the proposal's claims.

| # | Attempt | Stopped by | Owner sees at level 0 | Today |
|---|---|---|---|---|
| 1 | Agent credential calls approve or apply | L1 route allowlist; `Principal.require` (models.py line 135) | "1 refused" on the run row; level 1 names the route and `AUTHORITY_REQUIRED` | Not stopped at HTTP: F1. The service refuses only if handed the AGENT principal |
| 2 | Operation outside the frozen vocabulary | Kernel, `UNSUPPORTED_EDIT` (service.py lines 110-111) | REFUSED operation line with code | Kernel refuses; no proposal-level display |
| 3 | Teacher final approval as a meaning | Kernel, `MEANING_UNSUPPORTED` (service.py line 100) | "BLOCKED / OUT OF SCOPE" on the interpretation | Exists (baseline `option` cards) |
| 4 | Operation on an element outside the fence | Kernel, `OUTSIDE_FENCE` (new) | REFUSED line naming the element id and the fence | No fence exists |
| 5 | Provider call without startup flag or consent | `EGRESS_CONSENT_REQUIRED` (service.py line 62) | Composer refuses before sending; row reads "Provider call not made" | Exists; shown only as a notice |
| 6 | A second call while one runs | `PROVIDER_BUSY` (service.py line 64) | Composer disabled with the reason and a queue offer | Exists; the whole UI locks (F4) |
| 7 | Proposal on a moved baseline | `STALE_BASELINE` (F5) | STALE row "base r12, now r14"; Take disabled | Computed as a blocker string only |
| 8 | Narrative claims PASS or approval | Status is derived from kernel receipts only (ADR-009) | Counts and glyphs unchanged; narrative at level 1, labelled | Provider explanation already sits in a collapsed "untrusted" element |
| 9 | Narrative contains HTML, markdown, links or "/approve" | ADR-013 text nodes; no markdown renderer | Plain monospace text; no active link | Text nodes (`el()` uses `textContent`) |
| 10 | Two agents touch the same element | Kernel overlap advisory; base check at apply | "Overlaps proposal 7 on TR-REJECT" | Second apply fails `STALE_BASELINE` |
| 11 | Agent reads the launch token or `receipt.key` | Not a product control (OS permissions; `AGENTS.md` rule) | Nothing | Stated limit |

Rules for every refusal: it is shown where the attempt was made, with the kernel code and a one-line reason; it increments the run row's refused count; it is written to the audit log as an event (`AuthorityAttempt`, interface A3); it is never retried automatically and never converted into a weaker accepted operation (Horvitz principle 8 "doing less" applies to what is proposed, not to what is silently substituted, S1).

## 10. Trust calibration

Level 0 shows only what the kernel computed. It does not show what a model believes.

| Shown | Not shown at level 0 or in the Decision surface |
|---|---|
| Counts of PASS, FAIL, CONFLICT, STALE, UNKNOWN, NOT_RUN with the bound ("125/125 declared cells") | Provider-stated confidence, self-rated effort or severity |
| Not covered slot, never empty | Provider "explanation" of why the change is right |
| Ripple counts with UNKNOWN separate from "unaffected" | A percentage, score or star rating of a proposal |
| Grounding: references resolved, new items | Speed or streak of the owner's own approvals |

Evidence behind this choice (all for AI-assisted decisions, none for a tool like this):

- Explanations raised acceptance regardless of correctness (S21, CHI 2021 abstract).
- Cognitive forcing functions reduced overreliance in 199 participants, but participants rated those designs least favourably (S22, abstract). That trade-off is real: the fence and the per-UNKNOWN acknowledgement add friction, and the study must measure satisfaction next to accuracy.
- Complacency and automation bias occur for experts, are not removed by practice, and bias is not prevented by training or instructions (S23, abstract). Hence UNKNOWN is structural and not a warning paragraph.
- Trust guides reliance when full understanding is impractical (S24, abstract); Google PAIR says to show confidence only if it changes a decision and to test whether it helps (S25).
- Vendor data: the auto-mode classifier missed 17% of 52 real overeager actions (S3, vendor-reported, small n).

**Kernel-observed record (optional, HYPOTHESIS).** At level 1 a run may show counts such as "this run: 4 proposals, 1 refused, 0 taken then undone", with n. It is keyed to the Studio-issued run credential, because lane labels are untrusted and could inherit another agent's record. Where no credential exists it reads "no record". Risk: a good record may lower scrutiny; the study includes this as a manipulation.

**Feedback.** Each provider-authored item has "Not useful", logged per run (a Google analysis-warning feedback loop is UNVERIFIED, dossier only; the control is this design's own). The log never feeds approval.

## 11. Streaming, jobs, interruption

**What exists.** One whole JSON per call, 60 s or 120 s timeout, no token stream (F3). There is nothing to stream in v1. Designing a token stream now would display unvalidated provider text before the kernel has grounded it.

**v1 design.** A provider run is a job. The row shows RUNNING, elapsed time against the timeout ("23 s of 60 s") and Stop. The bar, if drawn, is labelled as time used, not progress, because progress is unknowable for a model call. This is a deliberate deviation from NN/g (S26), which asks for a percent-done indicator for waits above 10 s: a percentage would be invented. The Stop control that S26 also asks for is kept. When the JSON arrives the card appears as CHECKING, then READY.

**When an adapter can stream.** Each operation arrives as a card line only after the kernel accepted or refused it. The card shows "3 received" (never "3 of N"); Take stays disabled until the run is sealed. Raw text, if any, appends to the level-1 narrative log as plain text.

**Assistive technology.** State changes (RUNNING to CHECKING to READY) are announced once through a polite status region (WCAG 4.1.3, S31). The elapsed timer is not in a live region. The level-1 narrative log uses `role="log"` (implicit polite, S33) and is only live while open.

Latency classes. Every action declares one (S26); values are PREDICTION targets, not measurements.

| Action | Class | Target | If exceeded |
|---|---|---|---|
| Open card, step chapter, mark viewed, toggle level 1, open palette, filter | 0.1 s | p95 at most 100 ms | none |
| Press Stop | 0.1 s | STOPPING visible at most 100 ms | STOPPED shown when the process is confirmed dead |
| Send a request | 0.1 s | RUNNING row visible at most 100 ms | job rules below |
| Open source view, switch inbox group | 1 s | at most 1 s | none between 0.1 and 1 s |
| Provider run | job | timeout 60 s or 120 s (F3) | elapsed, Stop; time out with `billing UNKNOWN` |
| Kernel pre-check in sandbox | job | duration not measured; no number claimed | CHECKING with elapsed; the previous verdict stays visible marked STALE |

**Interruption.** One verb.

- `Stop` (button on the run row and `/stop`) cancels the provider process tree (ADR-0020 already kills it on timeout) or closes the HTTP request. Received items stay visible and read-only under STOPPED and cannot be taken, because ripple and checks depend on the whole set. Horvitz principle 6 asks for efficient termination and principle 8 for doing less rather than backtracking (S1).
- No mid-run steering in v1. The adapters are one-shot structured calls (F3, ADR-0020); Cursor's steer-at-a-safe-boundary exists in a different architecture (S14).
- A follow-up typed during a run is queued and labelled "Sends after this run". A queued network request needs its own consent toggle, set at queue time (I8).
- Stopping never spends less than what the provider already charged; billing stays UNKNOWN (F8).
- Stop needs a run registry that holds the process or request handle (interface A3). On Windows the tree kill that ADR-0020 promises is not what `_run` does today (F3), so Stop must be tested there before it is offered.

## 12. Checkpoints, undo and slash commands

### Undo and checkpoints

| Control | Effect | Restores | Does NOT restore |
|---|---|---|---|
| Dismiss a proposal | Closes it (DISMISSED) | Nothing changes elsewhere; Reopen returns it to READY if the base has not moved | Provider spend; the provider text stays in history |
| Undo take (Ctrl+Z, or the visible Undo take button on a TAKEN card) | New candidate revision with the previous content; Redo is Ctrl+Shift+Z. The chord acts only while focus is on a card or the candidate view; inside a text input (composer, answer fields) native text undo wins | Candidate model content | Evidence (receipts stay, marked STALE for the new subject); presentation approval; provider spend; audit events |
| Save checkpoint (existing `save`) | Marks a review checkpoint | Nothing to restore; not an apply | n/a |
| Discard candidate (existing `discard`) | Closes the case; the kernel does not reopen it | Nothing | Cannot be undone: create a new case to continue; history retained (F1 shows `discard` checks no principal) |
| Revert an applied change | Creates a new case whose candidate is the applied case's recorded baseline | The prior model | Anything that ran while the change was active; a fresh verify, approve and apply are required |

Every control's confirmation or status line uses one fixed shape: "Restores: ... Does not restore: ...". The wording sits in the status line, not on the button (P11). Claude Code's rewind names what it does not track (S5); a Windsurf statement that reverts are irreversible is UNVERIFIED and not relied on. Discard is the one control here that fails "no undo that cannot be undone" because the kernel closes the case. This is recorded as an open question for the kernel lane (section 17), not silently accepted.

Revert-as-new-case works because each case records its baseline (`ChangeCase.baseline`, service.py line 48); the `active` table keeps only the current model (`sqlite_store.py` lines 14 and 52).

### Slash commands

`/` opens the palette in command mode. `Ctrl/Cmd+K` opens it in search mode. Text after a command name is its argument; a command is recognised only at the start, as in Claude Code's menu (S7). Each row shows its class, and provider-call commands carry the mark "provider call". Rows that are not currently runnable stay listed with the reason.

| Command | Class | Provider call | Does |
|---|---|---|---|
| `/agents` | C0 | no | Opens the inbox at the first Needs-you row |
| `/propose <intent>` | C1 | yes when networked (per-request consent) | Creates a proposal request at the selection with the default fence |
| `/ask <question>` | C1 | yes when networked | Question about the selection; answer is level-1 text, AI-authored, not a proposal |
| `/why` | C0 | no | Kernel explanation for the selected refusal, STALE or suspect item |
| `/unknowns` | C0 | no | Lists every UNKNOWN across models (T14) |
| `/verify` | C2 | no | Starts bounded verification of the candidate |
| `/stop` | C2 | no | Stops the run under focus |
| `/source` | C0 | no | Opens the source view for the selection |
| `/history` | C0 | no | Audit timeline of the case, receipts retained |

Absent by construction: approve, apply, take, refuse, undo, discard, clear suspect, select meaning, widen fence. Typing "approve" shows one pointer row, "Approve is in the Decision surface: go to proposal 7 · Decide…", which focuses that button and does nothing else. Owner-edit and decision commands are not palette commands because the palette acts on the current selection, and a wrong selection at a fast keystroke is the failure to design out.

`/ask` is separate from `/why` on purpose: `/why` is generated by the kernel and can be checked; `/ask` is provider text and is labelled so (P9).

Single-letter card shortcuts (`v` mark viewed and advance, `j`/`k` move) are active only while the card has focus (WCAG 2.1.4, S31). Ctrl+Z and Ctrl+Shift+Z for Undo take are scoped the same way (card or candidate focus) and never override native undo in a text input. This keeps D11 consistent: an undo chord can act only on the item that has focus, not on whatever the global selection is. Undo take creates a new revision that is itself undoable, so a mistaken chord costs one redo.

## 13. Quantitative model

Model: Keystroke-Level Model. T = sum of operators. K 0.20 s (average skilled typist, 55 wpm), P 1.1 s, B 0.10 s, H 0.40 s, M 1.35 s, R as stated (S28, from Card, Moran and Newell 1980; KLM error about 21% RMS). A chord counts each key (ctrl+z is 2 K). Band plus or minus 21%. Flows: `design/tasks/ai-flows.json`; every number below was computed by the script in section 19.

**Revision 3 changes, and why.**

| Change | Reason (audit finding) |
|---|---|
| Task ids T13-intent and T09-agent-inbox | Brief T09 is the command palette and brief T13 is "at a selected element"; shared ids would merge different tasks |
| Every flow starts from the same state: hands on the mouse, pointer at `__pointer` (720, 450), focus on the page body | Revision 2 gave proposed flows a keyboard-resident start with no H or P, and current flows 2 H and 3 to 4 P |
| 12 of 19 P operators carry a `layout` field bound to `design/layouts/current-*.json` | The current UI's layout files exist; unbound P ops name elements proposed by this aspect, native select popups or cross-screen moves |
| Sensitivity grid K 0.12, 0.20, 0.28 and P 0.8, 1.1, 1.5 s, both from Kieras (S36) | Revision 2's P 0.63 and 1.02 s came from an UNVERIFIED fit, and its K range had no source |

Validity limits. Expert, error-free, routine execution. No reading, learning, errors or review quality. The M count is a judgement. Decision figures use the constant P 1.1 s. A Fitts time from layout geometry (T = 0.37 + 0.13 ID, attributed to Cockburn, Gutwin and Greenberg 2007, S35; coefficients UNVERIFIED here) is a sensitivity only. Hick-Hyman is not applied: palette search is typed, not stable-position. Fitts and KLM are not used to shorten Approve (P2).

Results, PREDICTION, seconds (like-for-like mouse start):

| Task | Current | Proposed | Ratio | Band (current / proposed) | Flips inside band? |
|---|---|---|---|---|---|
| T13-intent (networked, 33 typed chars) | 14.90 | 11.50 | 0.772 | 11.8 to 18.0 / 9.1 to 13.9 | Yes: not evidence |
| T13-intent, offline provider | 13.70 | 9.55 | 0.697 | 10.8 to 16.6 / 7.5 to 11.6 | Yes |
| T13-stop | 61.35 (worst-case wait) | 2.65 | 0.043 | n/a | Missing capability: no cancel path (F4) |
| T02 (navigation only) | 7.65 | 7.60 | 0.993 | 6.0 to 9.3 / 6.0 to 9.2 | Yes |
| T02-undo, keyboard | 6.30 | 4.70 | 0.746 | 5.0 to 7.6 / 3.7 to 5.7 | Yes |
| T02-undo, visible Undo take button | 6.30 | 3.90 | 0.619 | 5.0 to 7.6 / 3.1 to 4.7 | No at P 1.1 s |
| T08 (N_unknown = 1) | 13.10 | 13.20 | 1.008 | 10.3 to 15.9 / 10.4 to 16.0 | Yes; not a goal |
| T09-agent-inbox, palette | 2.55 | 2.95 | 1.157 | 2.0 to 3.1 / 2.3 to 3.6 | Yes |
| T09-agent-inbox, footer count | 2.55 | 2.55 | 1.000 | same | Yes |

How to read this.

- **Criterion.** With a 21% band on each total, the ordering can reverse when proposed/current lies between 0.653 and 1.532. The conservative reading (errors not independent) is used.
- **Sensitivity grid (K 0.12, 0.20, 0.28 by P 0.8, 1.1, 1.5; nine cells; depends on the assumed P range).** Cells below 0.653: T13-intent 1 of 9 (P 1.5, K 0.12: 0.587); T02-undo keyboard 0 of 9 (0.659 to 0.844); T02-undo visible button 6 of 9 (every cell with P 1.1 or 1.5: 0.619 and 0.573; P 0.8 gives 0.667); T02, T08, T09-agent-inbox 0 of 9. T13-stop 9 of 9 (not a speed result).
- **T13-intent.** Typing 33 characters is 44% of the current and 57% of the proposed total; the palette saves pointing, not typing. The proposed mouse path over visible controls is 13.70 s (M, P, B, H, 33 K, H, M, P, B, P, B; ratio 0.919). The current UI has no element selection, so the proposed flow passes context the current one cannot: not like-for-like in features.
- **T02.** Equal. One judging M per chapter; reading time is not modelled and is likely to dominate. The two UIs show different content, so equal time is not a finding about review quality.
- **T02-undo.** The only difference outside the band is the visible Undo take button (0.619), and it depends on P being at least 1.1 s. It compares an undo that exists with a manual reverse edit that imitates one (two-valued vocabulary, ADR-003).
- **T08 is deliberately not shortened.** The proposed flow adds an open step and one acknowledgement per UNKNOWN. Each further UNKNOWN adds M + 2 K = 1.75 s. N = 1 to 6: 13.20, 14.95, 16.70, 18.45, 20.20, 21.95 s against 13.10 current. The rise with N is intended.
- **T09-agent-inbox.** From a mouse start the palette is slower (2.95 s) than the visible footer count (2.55 s). It is kept for keyboard users, not for speed.
- **Keyboard-resident variant** (focus already in the inbox or on the card; a different start state, so not compared with the current flows): T13-intent 11.10, T02 6.20, T02-undo 3.10, T08 12.80, T09-agent-inbox 2.55 s.
- **Geometry sensitivity** (bound P ops by Fitts, UNVERIFIED coefficients): current T13-intent 13.91, T02 6.90, T02-undo 6.18, T08 11.57, T09-agent-inbox 2.22 s; ratios move towards the current UI (0.827, 1.102, 0.760, 1.141, 1.331). T02 and T02-undo current flows also need a scroll to elements below the 900 px fold that is not modelled, which understates the current cost.

No decision in this aspect rests on a KLM difference.

Other counts (COUNT of specified strings, not rendered output). Counting rule: split the wireframe block on whitespace and count each token that contains a word character (`\w`); the middle dot and the arrow are separators and do not count; the ‹ › label marks attach to the label token; glyphs from the status aspect are not counted. The script is in section 19. Under this rule the earlier card wording had 61 words; it was cut to 59 by removing "preview" and "runtime".

| Item | Value |
|---|---|
| Words in the inbox at level 0 (header and 3 rows) | 38 |
| Words in the opened card at level 0 | 59 (65 with the 6-word inbox header that remains while a card is open; 54% of the 120-word target; the ADR ceiling for the card alone is 60) |
| Words in the Decision surface wireframe (with N = 1) | 33, before the three question texts |
| Containers at level 0 | Inbox view: drawer, selected row, Stop = 3; card view: drawer, Take, Refuse = 3; nesting depth 2 |
| Chunks the owner must hold to judge a card | 4 by design: change, ripple, checks, authority and fence; inside the 3 to 5 range (Cowan 2001 abstract, S34) |
| Owner authority acts per accepted proposal | 3 (Take all, Approve, Apply), independent of the number of agent tool calls; per-action prompting grows with tool calls in Claude Code's opt-in manual mode (S4; inference) |
| Refused operations shown at level 0 | all |

## 14. Mixed initiative and human-AI guidelines applied

Horvitz's twelve principles (S1, read from the extracted PDF text; see S1 note) and how this design meets them. The "act if p > p*" machinery is not used: the utilities are unknown (LAW dossier) and the kernel provides deterministic gates instead. AI here has three moves only: suggest (a card), ask (an elicitation with fixed choices), or stay silent.

| # | Principle (paraphrased) | This design |
|---|---|---|
| 1 | Value-added automation | AI is offered where direct manipulation is costly: drafting operations, finding gaps. The direct-edit lane (no provider) remains |
| 2 | Uncertainty about goals | An ambiguous intent returns interpretations to choose from (baseline behaviour, kept); the owner chooses |
| 3 | Attention when timing services | Proposals arrive in the inbox; no toast; inbox changes are held while the Decision surface is open |
| 4 | Ideal action given costs and uncertainty | A fixed fence and a deterministic policy replace per-action estimates (section 6) |
| 5 | Dialog to resolve key uncertainty | Elicitation cards with fixed options, never free text approval |
| 6 | Efficient direct invocation and termination | `/propose`, Ask AI, Stop, Dismiss |
| 7 | Minimise the cost of poor guesses | Sealed proposals, Take is reversible, refusals visible, timeouts stated |
| 8 | Scope precision to uncertainty ("doing less") | Unresolved references become new items or refusals; the kernel never substitutes a weaker operation silently |
| 9 | Efficient collaboration to refine results | Per-operation Take at level 1, re-ask on a new base, follow-up queue |
| 10 | Socially appropriate behaviour | Plain labelled text; no persona, no chat avatar |
| 11 | Working memory of recent interactions | The case audit history and `/history`; queued follow-up keeps the intent |
| 12 | Learn by observing | Not adopted in v1; a learned model of the owner is a trust risk without a study. "Not useful" is logged but does not change behaviour |

Amershi et al. (S2; 18 guidelines, validated with 49 practitioners across 20 products) used where relevant: G1 and G2 make clear what the system can do and how well (fence and coverage line, not a confidence); G3 timing (inbox, no toast); G7 to G9 invocation, dismissal, correction (Ask AI, Dismiss, Take/Undo); G10 scope when in doubt (refusal, new items); G11 why (kernel `/why`, level-1 narrative labelled); G15 feedback (Not useful); G16 consequences of actions (Restores and Does not restore); G17 global controls (fence, egress flag); G18 notify about changes (STALE). G12 to G14 (memory, learning, cautious update) are not adopted.

## 15. Anti-slop position for these surfaces

| Item | Position |
|---|---|
| Chat transcript as the main surface | Not used: cards are fields, not prose; 59 words on an opened card (COUNT, ceiling 60) |
| Containers | 3 at level 0 in either drawer view (COUNT of specified elements); grouping by whitespace and hairlines |
| Status | Word plus glyph plus colour; UNKNOWN is a neutral hollow mark (A2, A5) |
| AI text | Level 1 only, labelled AI-authored and untrusted, plain text, no markdown |
| Real data | Excursion states, transitions, error codes and counts from the repository; illustrative numbers are marked illustrative |
| Icons and emoji | None specified; glyphs come from the status aspect with visible words |
| Fake precision | No percentages, scores or model confidences |

## 16. Study protocol for this aspect

Design only; nothing has been run. It extends the within-subject study in SYNTHESIS section 8.

- **Design.** Within-subject, baseline Studio versus proposed, counterbalanced order, excursion-workflow tasks T02, T08, T09-agent-inbox, T13-intent plus T13-stop and T02-undo. A keyboard-only cohort. Twelve or more participants for the quantitative comparison; formative rounds of about 5 find problems but do not estimate prevalence (LAW dossier section 2.10; design choice, dossier not re-opened).
- **Seeded cases.** (1) A supported operation whose ripple reaches a journey. (2) A proposal with one supported and two refused operations, to test whether refusals are noticed. (3) A narrative that claims "all checks pass" while the kernel shows an UNKNOWN. (4) A proposal on a moved base. (5) A narrative containing text that looks like an Approve button. (6) Two overlapping proposals.
- **Measures.** Seeded-defect detection; UNKNOWN misread as PASS (target zero); refused operations recalled; narrative persuasion (approval of case 3 with and without level-1 narrative expanded); time to first evidence; calibration (confidence versus correctness); time from opening the Decision surface to approval and share of UNKNOWN rows opened before acknowledgement (rubber-stamp indicators); per-task SEQ, SUS, Raw NASA-TLX with intervals; for the two-level disclosure (D4): time to reach the detail of a level-0 UNKNOWN and count of wrong-level navigations (opening the source view when level 1 sufficed, or the reverse).
- **Manipulations worth an arm, in priority order.** (1) Card content versus line diff, in the same container: typed operations, ripple, checks and Not covered against a line or hunk diff of the same change, on seeded-defect detection, UNKNOWN misreads, refusals noticed and time to first evidence. This tests the claim the design leans on most and that no cited source tests. (2) Container: inbox (option C) versus a thread that renders the same typed card inline (option F), same seeded cases; this is decided only after (1). Then: kernel-observed record shown versus hidden (section 10); per-UNKNOWN acknowledgement versus one checkbox versus typed revision id (Buçinca's forcing functions cost satisfaction, S22).
- **Stop criteria.** Stop and redesign if any participant approves with an unread UNKNOWN on a seeded item; if any participant cannot stop a run within 1 s of pressing Stop; if a refusal is missed in more than half of trials.

## 17. Gaps, contradictions, unverified

| Item | Status |
|---|---|
| No study shows that cards, chapters, fences or coverage lines improve decisions over chat or over a thread with inline cards (option F). The gap in AI-coding documentation is an absence claim I could not verify, not demand | Open; section 16 has an F arm |
| Explanations raising acceptance (S21) and forcing functions lowering satisfaction (S22) were studied on classification tasks with AI advice, not on model review; transfer is an assumption | Open |
| F1 and F2 (token equals owner; answers visible) are repository facts; the fix needs a kernel ADR and touches ADR-011 (single local owner) | Interface A4 |
| `OUTSIDE_FENCE`, `AuthorityAttempt`, operation verdicts and a sandbox pre-check do not exist | Interface A3 |
| Discard cannot be undone by the kernel | Open question for the kernel lane |
| Kernel pre-check duration is unmeasured; no latency number is claimed | Open |
| Claude Code Desktop three-mode transcript, Devin grouping details beyond S18, Windsurf revert statement, Stripe FocusView, Gerrit attention set, Google analysis-warning loop, Linear and Superhuman palette: dossier only, not re-opened | UNVERIFIED; not a basis for any decision |
| Permission-modes page (S4): re-read in revision 2. From Claude Code v2.1.283 auto mode is the built-in starting mode for interactive terminal and VS Code sessions (Pro, Max and Team earlier); manual mode is the opt-in `default`. Nothing beyond the manual and auto mode statements is relied on | Limited |
| The 93% approval and 17% miss figures (S3) describe tool-action permission prompts and a classifier on overeager agent actions. They are not measurements of approving a semantic model change. The rejection of model-assisted approval (option E) rests on invariant I4 alone | Stated in the ADR |
| KLM constants are from a 1980 laboratory study, taken from a Wikipedia tabulation (S28); the K and P ranges come from Kieras (S36), read from a local copy because the fetch tool failed certificate verification | Medium |
| Cockburn 2007 coefficients (0.37, 0.13): UNVERIFIED. Revision 3 uses them only for the geometry sensitivity; the P range of the grid now comes from Kieras (S36) | No decision depends on it |
| 12 of 19 P operators are bound to current-UI layout files. The 7 unbound ones name elements proposed by this aspect (inbox row, Stop, card, Decide), a native select popup or a cross-screen move; bind them when a proposed layout holds these elements | Partly deferred |
| Devin Review does not approve independently but lets the user approve and request changes through its platform, synced to GitHub (S18). Copilot review can be configured to submit approving reviews (UNVERIFIED, dossier only). This design forbids any AI approval | Contrast noted |
| Metrics: no user-benefit claim exists; every number labelled PREDICTION or COUNT | Standing rule |

## 18. Sources opened on 2026-09-29

| Id | URL | Used for |
|---|---|---|
| S1 | https://erichorvitz.com/chi99horvitz.pdf | The twelve mixed-initiative principles. WebFetch cannot extract this PDF; the numbering (3, 6, 7, 8 as cited) was read from the PDF text extracted into `.tmp/horvitz.txt` in this worktree on 2026-09-29. Not independently corroborated by the audit |
| S2 | https://www.microsoft.com/en-us/research/uploads/prod/2019/01/Guidelines-for-Human-AI-Interaction-camera-ready.pdf | The 18 guidelines; 49 practitioners, 20 products (also on the publication page). G9, G10, G11, G16 wording read from the PDF text extracted into `.tmp/amershi.txt` |
| S3 | https://anthropic.com/engineering/claude-code-auto-mode | 93% of prompts approved; 0.4% false positive on n=10,000; 17% false negative on n=52 (vendor-reported) |
| S4 | https://code.claude.com/docs/en/permission-modes | Manual mode asks before most edits, commands and network use (opening section only) |
| S5 | https://code.claude.com/docs/en/checkpointing | Rewind options; what is not tracked |
| S6 | https://code.claude.com/docs/en/agent-view | Grouping by state, row fields, 15 s summary refresh, tab-title count |
| S7 | https://code.claude.com/docs/en/commands | Slash menu, filter, command recognised at the start (opening section only) |
| S8 | https://linear.app/docs/assigning-issues | Agent cannot be the assignee; the human stays responsible |
| S9 | https://linear.app/developers/agent-interaction | Six session states; agents cannot create prompt activities |
| S10 | https://linear.app/now/reviewing-code-in-the-agent-era | Guided reviews as chunks |
| S11 | https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent | 59 minute limit; one repository; branch protection |
| S12 | https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/review-copilot-prs | The requester's approval does not count; another reviewer must approve |
| S13 | https://zed.dev/docs/ai/agent-panel | Multibuffer review, hunk accept and reject, checkpoint restore, stop, tool permissions |
| S14 | https://cursor.com/docs/agent/overview | Queue versus send-now, steering at a safe boundary, checkpoints restore files only |
| S15 | https://cursor.com/blog/cursor-3 | Micromanaging individual agents across conversations, terminals and windows is the stated problem; the fix is one workspace with all local and cloud agents in a sidebar. Precedent for a consolidated agent list (revision 2 had inverted this) |
| S16 | https://learn.chatgpt.com/docs/agent-approvals-security | Approval and sandbox modes; `auto_review` |
| S17 | https://docs.factory.ai/cli/user-guides/auto-run | Autonomy levels, risk classes, block over ask over allow |
| S18 | https://docs.devin.ai/work-with-devin/devin-review | Grouping by logical relation; colour-coded findings; approval on the user's behalf |
| S19 | https://modelcontextprotocol.io/specification/2025-06-18/server/tools | Human in the loop with ability to deny; annotations untrusted |
| S20 | https://arxiv.org/abs/2507.22358 | Magentic-UI mechanisms including action guards (abstract) |
| S21 | https://arxiv.org/abs/2006.14779 | Bansal et al., CHI 2021, explanations and acceptance |
| S22 | https://arxiv.org/abs/2102.09692 | Buçinca et al., cognitive forcing functions, n = 199 |
| S23 | https://pubmed.ncbi.nlm.nih.gov/21077562/ (abstract retrieved from NCBI E-utilities) | Parasuraman and Manzey 2010 |
| S24 | https://pubmed.ncbi.nlm.nih.gov/15151155/ (abstract retrieved from NCBI E-utilities) | Lee and See 2004 |
| S25 | https://pair.withgoogle.com/chapter/explainability-trust/ | When to show confidence; test it |
| S26 | https://www.nngroup.com/articles/response-times-3-important-limits/ | 0.1, 1, 10 s |
| S27 | https://www.nngroup.com/articles/progressive-disclosure/ | Two disclosure levels (2006) |
| S28 | https://en.wikipedia.org/wiki/Keystroke-level_model | KLM operator times and 21% RMS error |
| S29 | https://github.com/Fission-AI/OpenSpec ; https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/concepts.md | ADDED, MODIFIED, REMOVED delta section headings (all three confirmed in docs/concepts.md on 2026-09-29; the README shows ADDED only) |
| S30 | https://lawsofux.com/jakobs-law/ | Jakob's law |
| S31 | https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html ; .../target-size-minimum.html ; .../use-of-color.html ; .../dragging-movements.html ; .../character-key-shortcuts.html | WCAG 4.1.3, 2.5.8, 1.4.1, 2.5.7, 2.1.4 |
| S32 | https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ ; .../disclosure/ ; .../listbox/ | Dialog, disclosure and listbox patterns |
| S33 | https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/log_role | `log` role, implicit polite |
| S34 | https://pubmed.ncbi.nlm.nih.gov/11515286/ (abstract retrieved via NCBI E-utilities) | Cowan 2001, Behavioral and Brain Sciences: capacity of about four chunks, range three to five |
| S35 | https://api.crossref.org/works/10.1145/1240624.1240723 | Existence and bibliographic data only of Cockburn, Gutwin and Greenberg 2007, CHI 2007; coefficients not verified |
| S36 | https://web.eecs.umich.edu/~kieras/docs/GOMS/KLM.pdf | Kieras, 'Using the Keystroke-Level Model to Estimate Execution Times': K 0.12 (expert, 90 wpm), 0.20 (average skilled, 55 wpm), 0.28 (average non-secretarial, 40 wpm, recommended design point); P typically 0.8 to 1.5 s, average 1.1 s. WebFetch failed certificate verification on 2026-09-29; read from the PDF text in `.tmp/kieras_klm.txt` |

Repository files read: `src/eija_studio/interfaces/http.py`, `application/service.py`, `application/compiler.py`, `domain/models.py`, `domain/policy.py`, `adapters/providers.py`, `adapters/sqlite_store.py`, `interfaces/cli.py`, `resources/web/{index.html,app.js,app.css}`, `examples/excursion-candidate.json`, `AGENTS.md`, `README.md`, `docs/architecture/ARCHITECTURE.md`, `docs/adr/0000-poc-decision-log.md`, `docs/adr/0020-multi-provider-agent-adapters.md`, and all research dossiers, `personas-and-jtbd.md`, `design/brief.json`.

## 19. Reproducing the counts

Both scripts are short so an integrator can run them without other files. Run from the repository root.

Word counter (rule in section 13). It reads the fenced wireframe blocks of this file and prints the inbox, card, Decision surface and scenario-card counts. Expected output after revision 3: inbox 38, card 59, surface 33, scenario card 54.

```python
import re, sys
from pathlib import Path
FENCE = chr(96) * 3  # three backticks, written this way to keep this block fenced
lines = Path(sys.argv[1]).read_text(encoding="utf-8").split("\n")
blocks, cur, lang = [], None, None
for ln in lines:
    if ln.startswith(FENCE):
        if cur is None: cur, lang = [], ln[3:].strip()
        else: blocks.append((lang, "\n".join(cur))); cur = None
    elif cur is not None: cur.append(ln)
words = lambda t: sum(1 for w in t.split() if re.search(r"\w", w))
starts = {"inbox": "Agents", "card": "Proposal 7", "surface": "Decide", "scenario card": "Proposal 8"}
for lang, b in blocks:
    for k, p in starts.items():
        if not lang and b.startswith(p): print(k, words(b))
```

KLM and sensitivity (K 0.20, P 1.1, B 0.10, H 0.40, M 1.35; a chord counts each key). Reads `design/tasks/ai-flows.json`; prints totals, ratios and, for P in 0.8, 1.1, 1.5 and K in 0.12, 0.20, 0.28 (Kieras, S36), the min and max ratio and the number of cells below 0.653 (= 0.79 / 1.21). The visible-button and keyboard-resident variants are the assumption strings in the JSON.

```python
import json, itertools
d = json.load(open("design/tasks/ai-flows.json", encoding="utf-8"))
def t(ops, P=1.1, K=0.2):
    c = {"M": 1.35, "B": 0.1, "H": 0.4, "P": P}
    s = 0
    for o in ops:
        op = o["op"]
        if op in c: s += c[op]
        elif op == "K": s += K * (o["n"] if "n" in o else len(o["keys"].split("+")))
        elif op == "T": s += K * o["chars"]
        elif op == "R": s += o["ms"] / 1000
    return s
for k in d["tasks"]:
    c, p = t(k["flows"]["current"]), t(k["flows"]["proposed"])
    cells = [t(k["flows"]["proposed"], P, K) / t(k["flows"]["current"], P, K)
             for P, K in itertools.product((0.8, 1.1, 1.5), (0.12, 0.2, 0.28))]
    print(k["id"], round(c, 2), round(p, 2), round(p / c, 3), round(min(cells), 2), round(max(cells), 2), sum(x < 0.79 / 1.21 for x in cells))
```
