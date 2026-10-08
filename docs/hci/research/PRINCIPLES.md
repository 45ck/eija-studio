# Design principles for EIJA Studio

Lane `lane/ux-research`. Date 2026-09-29. Status: proposed; accepted principles become HCI-ADRs (block 0057-0088). Source ids (`AIC§2.1`, `REV§9`, `V2`, `R3`) are defined in [SYNTHESIS.md](SYNTHESIS.md) section 1. Every number below is a hypothesis or a PREDICTION unless it says MEASURED. Nothing here has been tested on users.

## 0. Decisions first

Twelve principles, ranked. **When two conflict, the higher-ranked wins**, and the lower one may deviate only through an HCI-ADR (template: [../../adr/template-hci.md](../../adr/template-hci.md)).

| Rank | Principle | Type | Strongest evidence | Confidence |
|---|---|---|---|---|
| 1 | UNKNOWN is always visible, counted, bounded and never rolled up into PASS | Invariant | REV§0 #1, REV§4, REV§9; LAW§2.11 (Norman gulfs) | High for the failure it prevents; untested for user benefit |
| 2 | The owner decides; nothing an AI or provider can reach may approve or apply | Invariant | V2, V5, AIC§2.1, REV§0 #6; Horvitz (LAW§2.11) | High |
| 3 | What you see is generated from the model; every edit is a typed request the kernel accepts or refuses | Invariant | DGM§3.1, MOK§2.1, ADC§2.7 | Medium |
| 4 | The unit of review is a semantic operation, not a line | Differentiator | AIC§4 #1, REQ§2.2, REV§2, LAW§2.5 | Medium |
| 5 | Every change shows its ripple next to it; no silent knock-on edit | Differentiator | LAW§2.7, DGM§3.2, AIC§4 #2, REV§8 | Medium |
| 6 | Status is never carried by colour alone, and contrast is computed, not asserted | Standard | VIS§2.3-2.4, SLP M15-M16, WCAG 1.4.1 | High for the standard; MEASURED for the palette risk |
| 7 | Local actions answer inside 0.1 s; slow work shows progress, a cancel and a real outcome | Standard | V1, LAW§2.6, DEV§2.12 | High as convention; PREDICTION for our latencies |
| 8 | Keyboard first: one palette, and every drag has a non-drag path | Standard | V6, DGM§2.5, DEV§2.1, MOK§3; LAW§2.4 | Medium |
| 9 | AI proposals are grounded in the model and visibly provisional | Differentiator | ADC§2.6, ADC§2.3, DGM§2.4, MOK§2.6 | Medium |
| 10 | Restraint: budgets for words, containers, type, disclosure depth; chrome recedes | Hypothesis | SLP§3, V7, DEV§2.5, VIS§2.5, LAW§2.12 | Low to medium; numbers are ours |
| 11 | Every undo states what it does not restore | Practice | AIC§2.1, 2.4, 2.9 | Medium |
| 12 | Predictions are labelled and no benefit is claimed before a study | Method | LAW§0, all dossiers | High |

Ranking rule: invariants first (they are repository rules that cannot be traded); then differentiators and standards ordered by evidence strength and by how many top tasks in [brief.json](../../../design/brief.json) they touch; hypotheses and method last. The order is a judgement I made; the study can reorder it.

## 1. Principles

### P1. UNKNOWN is always visible, counted, bounded and never rolled up into PASS

- **Statement.** Every roll-up shows counts by state ("12 PASS, 3 UNKNOWN, 1 FAIL"), never a percentage alone. Any UNKNOWN caps the aggregate at "pass with unknowns". Every verdict carries its bound ("PASS on 125 of 125 declared cells"; "no violation within N steps, seed S"). A check that cannot be computed reports UNKNOWN or NOT_RUN, never PASS.
- **Evidence.** GitHub reports a skipped required check as success and Codecov defaults `if_not_found` to success (REV§4). Bounded-check tools print their bound (Quint `--max-steps` 10, Alloy scope 3) (REV§5). Two denominators and a "No coverage" state in Stryker (REV§6). The kernel already returns UNKNOWN when it has no authority to establish a claim and STALE when only stale receipts exist (R3), and marks human understanding UNKNOWN by construction (ADR-010).
- **Laws.** Norman gulf of evaluation (LAW§2.11); automation complacency is not removed by prose warnings, so unknowns must be structural (REV§9, inference).
- **Status vocabulary (resolves SYNTHESIS C2).** Evidence: PASS, FAIL, CONFLICT, STALE, UNKNOWN, NOT_RUN. Eligibility: BLOCKED, ELIGIBLE_FOR_LOCAL_REVIEW. Job state: RUNNING. PARTIAL only after a kernel ADR.
- **Check.** Rendered UNKNOWN count equals the model's UNKNOWN count and each has a non-colour cue (SLP M21, HARD). Roll-up string is never "PASS" while UNKNOWN greater than 0 (unit test).
- **Tension.** Uses words and space at level 0. Wins over the word budget (P10); a deviation is recorded, not skipped.

### P2. The owner decides; nothing an AI or provider can reach may approve or apply

- **Statement.** Approve and apply exist only on the owner decision surface, which shows the exact revision and every UNKNOWN before the action is enabled. The palette, the agent bridge and any provider contain no approve or apply command. No "always allow" mode exists for either. Agents are shown as delegates; the owner as the assignee. Approval stays one deliberate step: we optimise the path to evidence, not the time to approve.
- **Evidence.** 93% of Claude Code permission prompts are approved (V2, vendor-reported), which suggests reflex approval; the classifier misses 17% of 52 real overeager actions (V2). Linear: an agent cannot be the primary assignee (V5). Approving AI reviews exist in preview, off by default (REV§0). Zed's "allowed" mode and Codex `auto_review` show the pattern to avoid (DEV§2.4, AIC§2.3). Repository rules: ADR-004, `AGENTS.md`.
- **Laws.** Fitts and KLM would favour a bigger, nearer Approve; we deliberately do not use them for this control (LAW§3). Horvitz: AI may suggest, ask or stay silent (LAW§2.11).
- **Check.** Static test: no route or command reachable from the palette or agent bridge maps to approve or apply. Study arm: time from opening the decision surface to approval, share of UNKNOWN items opened before approval (rubber-stamp indicator).
- **Tension.** Slower for expert owners by design; this deviation needs its own HCI-ADR (LAW§5 #3).

### P3. What you see is generated from the model; every edit is a typed request the kernel accepts or refuses

- **Statement.** Tree, diagram, journey, evidence row and text views are projections of the executable model. A drag, connect or rename emits a typed operation; the kernel accepts it or refuses it with a reason shown at the drop target; the picture is regenerated from the accepted model. No code path edits the picture and infers meaning. Layout is stored apart from meaning and keyed by stable element id. Generated text views (Mermaid, PlantUML) are read-only.
- **Evidence.** GLSP and Sirius Web document edits that change a semantic model; Mermaid Chart, draw.io and Lucid lose formatting or layout on some round-trip path (DGM§3.1). Figma's server rejects cycle-creating reparents (MOK§2.1). Lovable's stable ids make DOM click resolve to source (ADC§2.7). Structurizr separates model and views (DGM§2.8).
- **Repo constraint.** The kernel supports two typed edits today (enable recommendation; registrar rejection source) under a frozen vocabulary (ADR-003; README). Any other drop is a visible refusal. The design must not imply general model editing. A layout change keeps domain evidence but invalidates exact-presentation approval (ADR-008), and the UI must say so.
- **Check.** Regeneration test: DOM equals render(model, layout). Layout file contains only ids and coordinates. Every drag op has a kernel-side operation type or a refusal reason.
- **Tension.** Direct manipulation (Shneiderman, LAW§2.11) wants immediate feedback; the kernel round trip must stay inside the 0.1 s class (P7) or the drag shows a provisional state.

### P4. The unit of review is a semantic operation, not a line

- **Statement.** A change is listed first as typed semantic operations (glossary term, state, guard, journey step, test), ordered by dependency and grouped into chapters (core, consequences, glue), each labelled ADDED, MODIFIED or REMOVED. At most about 4 top-level chunks per change, expandable (stated range 3 to 5). Grouping comes from the model diff, never from a model summary. The line or JSON diff is one disclosure level down. A permanent counter shows "N formatting-only or null edits hidden", revealed on click. "Viewed" marks persist across revisions and clear when the operation's hash changes.
- **Evidence.** All surveyed agent products review at line or hunk level except Devin, whose grouping is an LLM judgement (AIC§0 #1). Understanding the change is the main review challenge; alphabetical order is judged optimal by 10.2% of 1,355 surveyed developers (REV§2). Linear chapters, OpenSpec deltas (REQ§2.2, 2.1). SemanticDiff states it cannot guarantee hidden edits are irrelevant (REV§7), hence the counter.
- **Laws.** Miller and Cowan: 3 to 5 chunks held in mind (LAW§2.5); NN/g range limit is about held items, not visible items (SYNTHESIS C12).
- **Check.** Study: seeded-defect detection and time versus baseline. Prototype: chunk count per change in the excursion fixtures (target at most 4, PREDICTION).
- **Tension.** A typed transaction list is exact only for operations the kernel supports; other changes fall back to a diff with an explicit "not analysed" label (P1).

### P5. Every change shows its ripple next to it; no silent knock-on edit

- **Statement.** Selecting a change shows counts per affected model (states, journeys, tests, personas, requirements) with UNKNOWN listed separately and "not analysed" never drawn like "unaffected". Each impact edge is labelled kernel-derived, heuristic or unknown. The ripple is a perspective switch over one model with a finder, not another diagram. Suspect status is computed by the kernel from hashes of meaning-bearing fields, shown with the causing diff, and cleared only by a logged owner decision; there is no "Clear All".
- **Evidence.** No surveyed product shows how one edit propagates across such models (AIC§0 #5, §4 #2). Nx over-approximates on purpose (REV§8). Ilograph perspectives (DGM§2.10). DOORS Next triggers only on flagged attributes; Jama and DOORS allow manual clearing (REQ§2.2).
- **Laws.** Cognitive Dimensions: hidden dependencies and knock-on viscosity; invariant is zero silent knock-on edits (LAW§2.7). Information scent: counts and kinds beside each node (LAW§2.8).
- **Check.** Property test: for each supported operation, the set of models changed is a subset of the listed ripple. First-click study on "which test is affected".
- **Tension.** One glyph per row keeps density down; DOORS Next admins can switch icons off to reduce clutter (REQ§2.2).

### P6. Status is never carried by colour alone, and contrast is computed, not asserted

- **Statement.** Each status has a shape, a word and a colour. UNKNOWN is a neutral grey hollow shape, never tinted like a pass. Contrast is gated on WCAG 2.2 ratios by computation; a contrast that cannot be computed reports UNKNOWN. APCA Lc is advisory. Light and dark themes ship together; dark elevation uses a lighter surface step plus a 1 px border, not shadow.
- **Evidence.** MEASURED (VIS§2.3-2.4): the baseline green and red pair drops from 0.204 to about 0.08 dE_OK for protan and deutan against a 0.02 JND; proved versus unknown is 0.025 and refuted versus stale 0.016 for deutan, so hue cannot separate them. Dark shadow contrast is 1.025 to 1.08. Text at exactly 4.5:1 on the dark surface scores about Lc 35 (APCA, unratified; SYNTHESIS C10). WCAG 1.4.1, 1.4.3, 1.4.11; DTCG 2025.10 is stable, not a W3C Standard (V3, V4).
- **Check.** SLP M15 and M16 (HARD). CVD simulation over every status pair at the used sizes.
- **Tension.** Extra glyphs cost containers and words; keep them inline with the row.

### P7. Local actions answer inside 0.1 s; slow work shows progress, a cancel and a real outcome

- **Statement.** Every action declares a latency class: 0.1 s direct manipulation and local selection, 1 s view switch, 10 s attention limit. Verification, model checks and agent runs run as jobs with progress, cancel and a visible RUNNING state, then a real outcome. The previous verdict stays visible and marked STALE while re-checking. A spinner never implies a pass.
- **Evidence.** V1; DEV§2.12; Zed frame budget and Superhuman 100 ms target (DEV§2.4, 2.10, vendor-reported). Doherty and Thadani is used only as "fast feedback has value"; the "400 ms threshold" is not in the text read (SYNTHESIS C1). Dafny distinguishes in-progress and stale (REV§6). Two edit lanes: direct edits (no provider) versus a prompt lane marked as a provider call (ADC§2.6-2.7).
- **Check.** Browser probe (one Chromium) records p95 per action against its class; `latency_band(ms)` in the model code (LAW§2.6). Values are PREDICTION targets until measured.
- **Tension.** Direct manipulation with a kernel round trip may miss 0.1 s on slow disks (D: is an HDD on the reference PC per `AGENTS.md`); measure before promising.

### P8. Keyboard first: one palette, and every drag has a non-drag path

- **Statement.** One Ctrl/Cmd+K palette (with `/` as an alias) acts on the current selection, uses entity prefixes and synonyms, shows the shortcut beside each result, and supports pinned commands. Each command shows kernel-enabled, blocked-with-reason or AI-proposal by glyph and word; disabled commands stay listed. The tree follows the APG tree model. The canvas offers Tab and Shift+Tab in reading order with live-region announcements and Alt+Tab to the parent. Every drag has a non-dragging path; targets are at least 24 by 24 CSS px.
- **Evidence.** WCAG 2.5.7 is Level AA (V6); 2.5.8 sets 24 px (VIS§2.2). Linear, Superhuman, JetBrains, Obsidian, Zed patterns (DEV§2.1-2.11). tldraw's announcement design (DGM§2.5). Azure DevOps documents gap queries as prompts (REQ§2.2).
- **Laws.** KLM PREDICTION: a palette beats hidden or deep targets (about 3.2 s versus 5.4 s, bands do not overlap) and does not beat a visible control (2.75 s versus 2.55 s); all values are for expert, error-free users who know the name, band plus or minus 21% (SYNTHESIS C5; LAW§2.4). Fitts ID at D = 400 px: 24 px is 4.14 bits and 32 px is 3.75 (PREDICTION; VIS§2.8). Hick-Hyman only for stable command order; typed search is not modelled (SYNTHESIS C4).
- **Check.** Task-flow JSON carries both paths so the executable model recomputes times from real layout geometry. Automated target-size check.
- **Tension.** The palette must never contain approve or apply (P2).

### P9. AI proposals are grounded in the model and visibly provisional

- **Statement.** A proposal may cite only entities, tokens and components resolvable in the model or token files; anything else appears as an explicit new item awaiting the owner. Proposed elements use a dashed outline plus a text badge, never colour alone. AI-authored tweak controls are data proposals validated against registered parameters and ranges; unbound controls show as rejected. Every import ends with a list of unmapped items rendered as UNKNOWN. AI severity and effort carry an "AI-estimated" label. A "Not useful" action on AI suggestions is logged per source.
- **Evidence.** v0's verifiability rule, Figma Make kits' disclosed loss, Claude Design tweaks (ADC§2.6, 2.3, 2.1); Balsamiq's visibly unfinished style, Excalidraw's draft look (MOK§2.6, DGM§2.4); Google's "Not useful" loop as a trust mechanism (REV§2). The anti-generic effect follows from construction: the picture comes from the model, so nothing generic is sampled (ADC§2.13). Repo: proposals are untrusted (ADR-004; `AGENTS.md`).
- **Check.** Grounding checker rejects an unresolved reference (unit test). Every AI-authored string carries `data-eija-source` (SLP M13).
- **Tension.** Provisional styling adds visual variety; keep it to one dashed treatment.

### P10. Restraint: budgets for words, containers, type and disclosure depth; chrome recedes

- **Statement.** Starting targets (hypotheses, each deviation needs an HCI-ADR): at most about 120 visible chrome words and about 12 containers per primary viewport, nesting at most 3, at most 6 font sizes, at most 2 elevations, one accent hue plus status hues, at most 2 type families plus one mono, eyebrow labels at most 1, no gradient, blur or translucency (zero by construction). Progressive disclosure at most 2 levels; UNKNOWN counts, proof status and blocked reasons stay at level 0; raw JSON moves behind an explicit source view. Containers appear only where they encode grouping or state; proximity and alignment come first.
- **Evidence.** MEASURED baseline (SYNTHESIS C3): 13 font sizes, 7 weights, 19 hex colours, 10 eyebrows, 6 panels, 3 `<pre>`, 404 words, 0 gradients. Users read at most about 28% of words on an average page and about 50% on pages of 111 words or fewer (SLP§5, 2005 data, general web). NN/g: beyond 2 disclosure levels typically lowers usability (V7). Linear's noise reduction and JetBrains' density switch (DEV§2.1, 2.5). Complexity acts early on first impressions, but low complexity plus high prototypicality also rates well, so we do not argue that generic looks worse (SYNTHESIS C18).
- **Check.** `slop-budget` script at 1440x900 and 1280x720; HARD metrics fail, BAND metrics print the reference distribution beside our value; `data-eija-source`, `data-eija-state`, `data-eija-model` hooks (SLP§6). Calibration of about 10 pages yields bands only; it cannot show that the metrics predict quality (SLP§4.5).
- **Tension.** Directly against P1 and P4 at level 0; those win.

### P11. Every undo states what it does not restore

- **Statement.** Each undo, rewind or discard control lists what it does not cover (external state, data, other models, provider spend, receipts). No undo that cannot itself be undone. Original receipts are retained; a discard never rewrites history (ADR-012).
- **Evidence.** Claude Code lists untracked changes; Bolt states database state is not restored; Windsurf says reverts are irreversible (AIC§2.1, 2.9, 2.4). VS Code stopping "doesn't undo completed actions" (AIC§2.5).
- **Check.** Every undo control has a coverage string (lint on markup).
- **Tension.** Adds words to a control; place it in the confirmation, not the button.

### P12. Predictions are labelled and no benefit is claimed before a study

- **Statement.** Every number derived from a law or model is labelled PREDICTION with its constants profile and band (KLM plus or minus 21%; Fitts in bits unless a constants profile is stated). A decision that flips inside the band is not evidence. Each HCI-ADR names its validation measurement and study reference. "Feels good" is measured with SUS, per-task SEQ and Raw TLX with intervals, plus decision-quality measures, not inferred from laws.
- **Evidence.** LAW§0, §2.4, §2.10, §5; METR and Perry et al. show perceived and measured effects diverge (AIC§2.12); SLP§4.5 on sample size.
- **Check.** Model functions return the PREDICTION label and constants; ADR lint requires the section.
- **Tension.** Slows claims; that is intended.

## 2. Non-negotiable invariants

| # | Invariant | Source |
|---|---|---|
| I1 | AI proposes, the kernel checks, the owner decides | README; ADR-004 |
| I2 | What you see is generated from, or checked against, the code and model | ADR-0019; ARCHITECTURE.md |
| I3 | UNKNOWN is never hidden or rounded up; human understanding stays UNKNOWN until measured | ADR-010; R3 |
| I4 | Providers and agents never approve or apply; no palette command, agent-bridge tool or provider response reaches approve or apply | ADR-004; `AGENTS.md` |
| I5 | Untrusted text reaches the page only through DOM text nodes; no provider HTML, no iframe, no inline script or style | ADR-013; R2 |
| I6 | The Studio serves loopback only, with a single local owner and synthetic actors; no multi-user or institutional-identity claim | ADR-011 |
| I7 | Original receipts and decisions are retained; no silent rebase | ADR-012 |
| I8 | Egress needs the startup flag and per-request consent; the prompt lane is marked as a provider call | README; `AGENTS.md` |
| I9 | Every fact about a product, law or standard carries a source opened by the author; unverified items are labelled UNVERIFIED and not built on | Lane rules |
| I10 | No user-benefit claim without a user study | Lane rules; P12 |

## 3. Cognitive Dimensions vocabulary for ADRs

Use the Green and Petre terms in every ADR (LAW§2.7): viscosity (repetition and knock-on), hidden dependencies (ripple list), premature commitment (do not force approval order), provisionality (proposals look provisional), visibility (UNKNOWN visible), secondary notation (layout by id), role-expressiveness (glyph by DDD role), error-proneness (kernel refusal). Ratings in the dossiers are analyst judgement, not measurement.

## 4. How the principles get tested

| Layer | What | Where |
|---|---|---|
| Unit | `fitts_mt`, `hick_time`, `klm_time`, `latency_band`, `contrast_ratio`, `sus_score`, `tlx`, `p_star` against the oracles in LAW | model code (owned by another lane) |
| Prototype | Slop-budget script; CSP smoke test (SVG attributes, worker load, style APIs); target size; contrast; latency probe; CVD simulation | one Chromium at a time |
| Study | Within-subject baseline versus proposed; seeded defects; UNKNOWN misread as PASS; calibration; SUS, SEQ, Raw TLX; keyboard-only cohort | `docs/hci/design/` (study protocol owner) |
