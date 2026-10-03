# HCI-ADR-NNNN: {short title of the interaction, layout, colour, type or content decision}

Template for HCI decisions. File name: `00NN-hci-<slug>.md`, number from the HCI block 0057-0088 (one file per decision). Start from [template.md](template.md) for anything that is not a UI decision. A record is never rewritten after acceptance; supersede it with a new one ([README.md](README.md)). Delete the guidance text in braces when you fill a section. Every section is required; write "not applicable" with a reason rather than deleting one.

Rules that apply to every section:

- Every factual claim about a product, law, standard or number has a source URL that the author opened, with the access date. If it could not be verified, write UNVERIFIED and do not build on it.
- Model outputs are labelled **PREDICTION**. Measurements are labelled **MEASURED** and name the tool, browser, viewport and date. Nothing is called a benefit without a user study.
- Source ids may point to research dossiers in `docs/hci/research/`, but the evidence table must still carry the URL.
- Summarise and attribute; quote at most a few words; no copied proprietary assets. Fonts and icons must be OFL, MIT, Apache, ISC or equivalent, with the licence and source URL recorded.

## Status

* Status: {proposed | accepted | superseded by HCI-ADR-NNNN | rejected}
* Date: {YYYY-MM-DD}
* Aspect: {layout | interaction | navigation | status and evidence display | review | colour | type | motion | iconography | content | accessibility | tokens | security boundary (CSP, assets) | onboarding}
* Author / lane: {name, `lane/<name>`, issue}
* Related: {ADRs, principles from `docs/hci/research/PRINCIPLES.md` (P1 to P12), invariants I1 to I10}

## Problem and user goal

* Persona: {P1 to P5 from `docs/hci/personas-and-jtbd.md`; state whether this is the primary persona}
* Job to be done: {when / I want / so I can}
* Task ids and frequency: {T01 to T14 from `design/brief.json`; daily, weekly or rare; note that frequencies are hypotheses unless measured}
* Problem: {two or three sentences: what fails today in the baseline or in the current proposal; cite the measured baseline value if there is one}
* Out of scope: {what this decision does not settle}

## Evidence

{One row per claim the decision leans on. Source type: standard, peer-reviewed paper, official documentation, first-party engineering blog, vendor claim, practitioner write-up, forum. Confidence: high, medium, low. Vendor-reported numbers are medium at best. Include at least one row that argues against the decision.}

| Claim | Source URL | Source type | Confidence | Verified on |
|---|---|---|---|---|
| {claim} | {URL} | {type} | {high / medium / low} | {YYYY-MM-DD} |

## Quantitative model

{Required whenever the decision is about layout, interaction cost, colour or type. If the decision is not quantifiable, say so and state which qualitative principle stands in for it.}

* Model and formula: {for example Fitts (Shannon form) MT = a + b log2(D/W + 1); KLM sum of operators; Hick-Hyman T = a + b log2(n); WCAG contrast ratio; latency class; complexity counts from the DOM}
* Inputs and sources: {constants profile with source; geometry from `design/layouts/<screen>.json`; task flows from `design/tasks/<aspect>.json`; M count and its rationale}
* Result for the current design: {value, unit, band} **PREDICTION**
* Result for the proposed design: {value, unit, band} **PREDICTION**
* Decision flips inside the band? {yes or no. KLM error is about plus or minus 21%; a decision that flips inside the band is not evidence}
* Validity limits: {population, device, expertise; for example KLM covers expert, error-free, routine tasks only and not learning, errors or reading; Fitts is one-dimensional pointing and not keyboard; Hick-Hyman needs stable positions and practised users and does not model typed search}
* Deliberate deviations from the model: {for example the approval control is not shortened even though Fitts favours it (P2)}

## Options considered

{At least three, including the baseline or "do nothing". For each option state what competing products do, with a source, and why it was rejected or chosen. Name existing OSS first where a custom module is involved.}

| Option | What it is and who does it (source) | Advantages | Drawbacks | Verdict |
|---|---|---|---|---|
| A: baseline | {current Studio behaviour} | | | |
| B | {option; product and source} | | | |
| C | {option; product and source} | | | |

## Decision

Chosen option: "{option}", because {justification tied to the evidence table and the model}.

{State the concrete behaviour, values and tokens. State which invariants and principles it preserves and how (AI proposes, kernel checks, owner decides; generated from the model; UNKNOWN visible; providers never approve or apply).}

## Anti-slop rubric check

{Mark each item pass, fail, not applicable or UNKNOWN. UNKNOWN is a legal answer; it is never counted as pass. Give the MEASURED or PREDICTED value where the item is numeric. Targets are starting hypotheses; every deviation needs its own justification here.}

| Item | Target | Result | Value | MEASURED or PREDICTION |
|---|---|---|---|---|
| No decorative gradient, glassmorphism or blur | 0 | | | |
| No card inside card; containers only where they encode grouping or state | nesting depth at most 3 | | | |
| Containers per primary viewport | at most about 12 | | | |
| No emoji and no icon-per-bullet; icon-only controls have visible labels | 0 violations | | | |
| No generic centred hero plus three-feature grid | 0 | | | |
| No purple or blue default gradient; no unexamined default font stack (a type choice, including Inter, needs a recorded rationale) | rationale present | | | |
| No placeholder, lorem or fake data; every number has a source | 0 unsourced values | | | |
| No paragraph where a label, glyph, number or diagram would do | prose blocks of 8 or more words per viewport at most about 30 words in total | | | |
| Visible chrome words in the primary viewport | at most about 120 | | | |
| Distinct font sizes per viewport | at most 6 | | | |
| Type families | at most 2 plus one monospace | | | |
| Elevations | at most 2 | | | |
| Accent hues | 1 accent plus semantic status hues | | | |
| Eyebrow labels | at most 1 | | | |
| Disclosure depth | at most 2 levels; UNKNOWN, proof status and blocked reasons at level 0 | | | |
| Colour is never the only carrier of meaning (glyph and word accompany it) | 0 violations | | | |

## Accessibility check

| Check | Standard | Result | Evidence |
|---|---|---|---|
| Text contrast computed, not asserted | WCAG 2.2 SC 1.4.3: 4.5:1 text, 3:1 large text | {pass / fail / UNKNOWN} | {ratios; a contrast that cannot be computed is UNKNOWN} |
| Non-text contrast | SC 1.4.11: 3:1 for UI components and graphics | | |
| Colour not the only cue | SC 1.4.1 | | {glyph, word and shape per status; CVD simulation result} |
| Target size | SC 2.5.8: at least 24 by 24 CSS px (or spacing exception) | | |
| Dragging has a non-dragging path | SC 2.5.7 (Level AA) | | {the keyboard or click path} |
| Keyboard operable, visible focus, reading order | SC 2.1.1, 2.4.7 | | |
| Text spacing and reflow tolerate overrides | SC 1.4.12, 1.4.10 | | |
| Reduced motion respected; motion never carries meaning | `prefers-reduced-motion` | | |
| Screen-reader name, role, state, position in set | ARIA APG pattern used: {pattern} | | |
| APCA Lc (advisory only) | not a gate | {value} | {note if it disagrees with the WCAG ratio} |

## Validation plan

* Prototype measurements (one browser at a time, at 1440x900 and 1280x720): {which of: layout JSON run through `fitts_mt` and `klm_time`; slop-budget script; latency probe p95 against the action's class (0.1 s, 1 s, 10 s); contrast and CVD checks; CSP smoke test; keyboard-path test}
* Pass criteria, fixed before running: {numbers}
* User-study protocol reference: {path to the study protocol in `docs/hci/design/`, or inline}
  * Design: {within-subject or between; counterbalancing; baseline Studio versus proposed}
  * Participants and sample size: {n and why; for example formative rounds of about 5 find problems but do not estimate prevalence, quantitative comparisons need about 20 or more; include a keyboard-only cohort where relevant}
  * Tasks: {T-ids from `design/brief.json` on the excursion workflow}
  * Measures: time on task; error count; UNKNOWN items misread as PASS (target zero); calibration; SUS score; per-task SEQ; Raw NASA-TLX; task-specific measures
  * Analysis: {effect sizes with confidence intervals; pre-registered hypotheses; how SUS is compared to the 68 benchmark, only with an interval}
  * Stop criteria: {for example stop and redesign if any participant approves with an unread UNKNOWN on a seeded item; stop if error rate on the primary task exceeds a stated threshold; stop when the confidence interval excludes the pre-registered minimum effect}
* Status of results: {none yet | reference to results}. **No user-benefit claim is made until results exist.**

## Consequences

* Good: {}
* Bad: {including added words, containers, latency or maintenance}
* Cognitive Dimensions impact: {viscosity, hidden dependencies, premature commitment, provisionality, visibility, secondary notation, role-expressiveness, error-proneness}
* Security and repository impact: {CSP, `/assets` allowlist, caching, ADR-013 (untrusted text through DOM text nodes only), new dependency and its `docs/oss/REGISTER.md` row}
* Licence check: {fonts, icons, libraries: licence and source URL}
* Revisit when: {a measurable trigger, for example the study shows a difference inside the KLM band, p95 latency exceeds its class, the slop-budget metric leaves the calibrated band, a cited source changes}

## Definition of ready

- [ ] Persona, task ids and frequency stated
- [ ] Each evidence row has a URL, type, confidence and verification date; one row argues against the decision
- [ ] Model outputs labelled PREDICTION with constants and band; validity limits stated
- [ ] At least three options, including the baseline
- [ ] Rubric table complete (UNKNOWN allowed, not counted as pass)
- [ ] Accessibility table complete
- [ ] Validation plan with pass criteria fixed in advance, and the study reference and stop criteria
- [ ] No claim of user benefit without a study
