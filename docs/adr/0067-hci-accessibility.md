# HCI-ADR-0067: Accessibility architecture

Template for HCI decisions. Filled from [template-hci.md](template-hci.md). The full specification, tables, measurements and source list are in [docs/hci/design/accessibility.md](../hci/design/accessibility.md). Task flows are in [design/tasks/a11y-flows.json](../../design/tasks/a11y-flows.json). Ids B1 to B12 (baseline findings), M1 to M7 (my measurements), S1 to S58 (sources) and A1 to A10 (assumptions) are defined in that document.

## Status

* Status: proposed (revision 2 after audit, 2026-09-29: option F added and chosen; inset focus ring corrected)
* Date: 2026-09-29
* Aspect: accessibility
* Author / lane: research agent (Claude Code), `lane/ux-research`, aspect `accessibility`; issue number not stated in the task
* Related: principles P1, P2, P3, P6, P8, P10, P11, P12 in `docs/hci/research/PRINCIPLES.md`; invariants I1 to I5, I9, I10; ADR-003, ADR-008, ADR-011 and ADR-013 in [0000-poc-decision-log.md](0000-poc-decision-log.md); [HCI-ADR-0064](0064-hci-ai-interaction.md) (isolation layers L3 and L4, D11)

## Problem and user goal

* Persona: cross-cutting. P2 domain-model owner (drag and tree, primary for this record) and P1 agent-change reviewer (review and decide, the ICP). P4 for tables and traces. `docs/hci/personas-and-jtbd.md` has no persona for users of assistive technology (AT); its section 6 step 4 already plans a keyboard-only and a screen-reader cohort. Personas are literature-derived hypotheses.
* Job to be done: when I edit the model or review an agent's change, I want every action available without dragging, without a mouse and without seeing the picture, and I want UNKNOWN, refusals and the exact revision to reach me through whatever I use, so I can decide defensibly on my own terms.
* Task ids and frequency: T04 (weekly), T05 (weekly), T02 (daily), T08 (daily), T09 (daily), T07 (weekly), T10 (rare). Frequencies are hypotheses.
* Problem: the baseline is a form-based page, yet it already fails on measurement (Chrome 154, axe-core 4.13.0, 2026-09-29):
  * after selecting a case with Enter, focus falls to `body` (B2);
  * the four tabs and the selected case expose no state: 0 `aria-selected`, 0 `aria-current` (B3);
  * the sidebar is `display:none` at 760 CSS px or narrower, so at 200% zoom on a 1280 or 1440 px window the case list is unreachable (B4);
  * control borders are 1.68 to 1.74:1 against the 3:1 that SC 1.4.11 asks (B5);
  * axe found only 1 of these 5 failures (B1).
* The proposed Studio adds a drag canvas, a tree, a palette and a decision dialog. Each is a new place to fail SC 2.5.7, 2.4.11, 4.1.2 and 1.4.10 unless the architecture is decided first.
* Out of scope: glyph and colour values, shell layout, diagram drawing, the contents of the decision surface (A7), any claim of WCAG conformance, and legal requirements (EN 301 549 and similar were not opened).

## Evidence

Source ids map to URLs in section 14 of the design document; the URL is repeated here. All pages were opened on 2026-09-29. WebFetch returns a small-model summary, so quotations are limited to a few words. Vendor numbers are vendor-reported.

| Claim | Source URL | Source type | Confidence | Verified on |
|---|---|---|---|---|
| WCAG 2.2 is a W3C Recommendation of 12 December 2024 (current edition); new criteria include 2.4.11, 2.4.13, 2.5.7, 2.5.8, 3.2.6, 3.3.7; 4.1.1 was removed | https://www.w3.org/TR/WCAG22/ | Standard | High | 2026-09-29 |
| SC 2.5.7 (AA): dragging needs a single-pointer alternative; listed alternatives include clicking items in sequence, adjacent controls, pop-up menus and numeric fields; keyboard operation is assessed separately | https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html | Standard (Understanding) | High | 2026-09-29 |
| SC 2.5.8 (AA): 24 by 24 CSS px, with spacing, equivalent, inline, user-agent and essential exceptions; no statement on labelled checkboxes | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | Standard | High | 2026-09-29 |
| SC 2.4.11 (AA) focus not entirely hidden; scroll-padding is a named technique for sticky bars | https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html | Standard | High | 2026-09-29 |
| SC 2.4.13 (AAA): indicator area at least a 2 CSS px perimeter, computed as 4h + 4w for a rectangle (90 by 30 px button: 480 px2); a solid 2 px line inside the component against its outer edge is the smallest passing perimeter; indicators "inset further" must be thicker than 2 px | https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html | Standard (Understanding) | High | 2026-09-29 |
| SC 2.1.4 (A): single-character shortcuts need off, remap or focus-only; modifier shortcuts are exempt | https://www.w3.org/WAI/WCAG22/Understanding/character-key-shortcuts.html | Standard | High | 2026-09-29 |
| SC 2.5.2 (A) pointer cancellation, SC 2.5.1 (A) dragging is not a path-based gesture, SC 4.1.3 (AA) status messages need `role` or properties and no focus move | https://www.w3.org/WAI/WCAG22/Understanding/pointer-cancellation.html , https://www.w3.org/WAI/WCAG22/Understanding/pointer-gestures.html , https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html | Standard | High | 2026-09-29 |
| SC 1.4.10 (AA): 320 by 256 CSS px equals 400% on 1280 px; two-dimensional content such as diagrams and data tables may scroll both ways; SC 1.4.12: tolerate line height 1.5, letter 0.12 em, word 0.16 em, paragraph 2 em | https://www.w3.org/WAI/WCAG22/Understanding/reflow.html and https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html | Standard | High | 2026-09-29 |
| SC 3.2.6 (A) consistent help, SC 3.3.7 (A) redundant entry, SC 3.3.4 (AA) error prevention (reversible, checked or confirmed) for changes to user-controllable data | https://www.w3.org/WAI/WCAG22/Understanding/consistent-help.html , .../redundant-entry.html , .../error-prevention-legal-financial-data.html | Standard | High | 2026-09-29 |
| Complex images need a short and a long description; the long description may be a section of the same page, may hold headings, text and a table, and is available to everyone | https://www.w3.org/WAI/tutorials/images/complex/ | Standard (W3C tutorial) | High | 2026-09-29 |
| APG tree, tabs, dialog (initial focus on a static element when the content has lists, tables or several paragraphs; on the least destructive action when the dialog holds the final, not easily reversible step), combobox with `aria-activedescendant`, toolbar (3 or more controls), disclosure and menu button define the key tables used | https://www.w3.org/WAI/ARIA/apg/patterns/treeview/ and siblings listed as S22 to S31 | Standard (informative guide) | High | 2026-09-29 |
| APG tree: Right on an end node does nothing and Left on a root node does nothing. Option E needed two authored departures here (Right on a transition follows it, Left on a state goes to the previous state); option F needs none | https://www.w3.org/WAI/ARIA/apg/patterns/treeview/ | Standard (informative guide) | High | 2026-09-29 |
| The excursion candidate workflow is a cyclic graph: Revise goes from Rejected back to Draft; Reject may start at Submitted or Recommended | `src/eija_studio/domain/policy.py` lines 32 to 36 and 49 to 63 (repository) | Primary (code) | High | 2026-09-29 |
| Roving tabindex versus `aria-activedescendant`: roving lets the browser scroll the focused item into view | https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/ | Standard (informative guide) | High | 2026-09-29 |
| MEASURED (M2): Chromium 154 exposes SVG `role=graphics-document` (W3C Recommendation 2018) as one `img` and drops the `graphics-object` children; `role=tree` on SVG or HTML keeps tree and treeitems; axe reports 0 violations for all four candidates | https://www.w3.org/TR/graphics-aria-1.0/ ; measurement M2 | Standard plus own measurement (one browser, no AT) | Medium: Chromium tree only | 2026-09-29 |
| MEASURED (M7): excursion fixture (5 states, 5 transitions), Chromium 154, axe 4.13.0 with `target-size` enabled. E (V4 tree, roving): 1 tab stop, 0 violations, tree with 5 treeitems and nested groups. F (native nested list of buttons in a `figure`, picture `aria-hidden`): 10 tab stops, button names such as "Reject: Submitted to Rejected", 0 violations except `target-size` on 6 unstyled fixture buttons (browser-default height below 24 px; the design sets 32 px) | measurement M7 (`.tmp/a11y/run_spike_v6.py`, not committed) | Own measurement (one browser, no AT) | Medium | 2026-09-29 |
| MEASURED (M2): SVG text does not wrap (272 px for a 39-character label in a 120 px node, 346 px after the SC 1.4.12 overrides); an HTML node wraps and grows from 60 to 94 px high | measurement M2 | Own measurement | Medium: one label, one browser | 2026-09-29 |
| MEASURED (M3): with `forced_colors="active"`, SVG `fill` and `stroke` written as hex are not overridden; `currentColor` and system keywords are. MDN says SVG fill and stroke are forced; the Microsoft article says SVG is not adjusted and recommends `currentColor` | https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors and https://blogs.windows.com/msedgedev/2020/09/17/styling-for-windows-high-contrast-with-new-standards-for-forced-colors/ ; measurement M3 | Documentation plus own measurement (emulation, not a Windows theme) | Medium | 2026-09-29 |
| MEASURED (M6): a `button` inside a `treeitem` becomes part of the item name ("Submit Reconnect source"); a 24 px `aria-hidden` pointer-only handle leaves the name unchanged ("Submit"); 0 `nested-interactive` violations in all variants | measurement M6 (`.tmp/a11y/run_spike_v5.py`); https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md | Own measurement (one browser, no AT) | Medium | 2026-09-29 |
| MEASURED (M3): an outer `outline-offset: 2px` ring on a row flush with an `overflow:auto` parent is clipped; an inset ring is not | measurement M3 | Own measurement | Medium: one browser | 2026-09-29 |
| tldraw documents Tab and Shift+Tab through shapes in canvas reading order, Ctrl/Cmd+arrow to the nearest shape, and a live-region announcement "[description], [type]. [position] of [total]" | https://tldraw.dev/sdk-features/accessibility | First-party documentation | High | 2026-09-29 |
| Data Navigator is an MIT-licensed JavaScript library (npm `data-navigator` 3.0.0, no runtime dependencies listed) for keyboard, screen-reader and multi-modal navigation of data structures; its ESM packaging under a strict CSP and a no-build page was not evaluated | https://github.com/cmudig/data-navigator and https://registry.npmjs.org/data-navigator/latest | Official repository and registry metadata | Medium for licence and version; UNVERIFIED for fit | 2026-09-29 |
| Ilograph states its diagrams are screen-reader friendly and keyboard navigable | https://www.ilograph.com/features.html | Vendor claim | Medium | 2026-09-29 |
| Data Navigator builds navigable structures (lists, trees, graphs) as the accessible layer over a visualisation (abstract); Zong et al. name structure, navigation and description as design dimensions in a study with 13 blind and low-vision readers (abstract) | https://arxiv.org/abs/2308.08475 and https://arxiv.org/abs/2205.04917 | Peer-reviewed papers, abstracts read | Medium for transfer to a state editor | 2026-09-29 |
| WebAIM survey 10 (Dec 2023 to Jan 2024, 1,539 responses): JAWS 40.5%, NVDA 37.7%, VoiceOver 9.7%; Chrome 52.3%, Edge 19.3%, Firefox 16.0%; headings 71.6% and landmarks 3.7% as the way to find information on long pages | https://webaim.org/projects/screenreadersurvey10/ | Practitioner survey, self-selected | Medium | 2026-09-29 |
| axe-core is MPL-2.0; version 4.13.0; the vendor claims about 57% of WCAG issues on average; `target-size` (wcag22aa) is disabled by default | https://github.com/dequelabs/axe-core , https://registry.npmjs.org/axe-core/latest , https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md | Vendor documentation | Medium for the 57% (vendor claim); high for the licence and default | 2026-09-29 |
| A 2017 UK government audit: 10 automated tools found 71% of 143 deliberate failures together and 29% (42) were found by none. Best single tool: 41% (Asqatasun) when manual-inspection prompts are counted, 37% (Tenon) on errors and warnings only | https://accessibility.blog.gov.uk/2017/02/24/what-we-found-when-we-tested-tools-on-the-worlds-least-accessible-webpage/ | Practitioner write-up (government), old | Medium | 2026-09-29 |
| WCAG-EM 2.0 (Group Note, 23 July 2026): sampled evaluations cannot support a claim for a whole site | https://www.w3.org/TR/WCAG-EM/ | Standard (Note) | High | 2026-09-29 |
| COGA Working Group Note (29 April 2021): eight objectives, supplemental to WCAG | https://www.w3.org/TR/coga-usable/ | Standard (Note) | High | 2026-09-29 |
| KLM operators K 0.20, P 1.1, H 0.4, M 1.35, B 0.1 and RMS error 21% (tertiary table of Card, Moran and Newell 1980); Fitts constants 0.37 + 0.13 ID (R2 = 0.93, eight right-handed graduate students, vertical menu-item selection) | https://en.wikipedia.org/wiki/Keystroke-level_model and https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf | Tertiary; peer-reviewed paper (converted locally) | Medium; high for the Fitts fit within its task | 2026-09-29 |
| AGAINST E: the APG says incorrect ARIA misrepresents experiences and advises testing each browser and AT combination; WebAIM Million 2026: pages with ARIA averaged 59.1 detected errors, pages without 42 (association, not cause) | https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/ and https://webaim.org/projects/million/ | Standard guide; practitioner analysis | Medium | 2026-09-29 |
| AGAINST F: 10 tab stops for the excursion diagram against 1 for E (M7); tldraw and draw.io (dossier DGM§2.1) let keyboard users move through the picture itself, which F does not | measurement M7; https://tldraw.dev/sdk-features/accessibility | Own measurement; first-party documentation | High for the count; medium for expectations | 2026-09-29 |
| AGAINST: automated tools miss most of what matters (axe 1 of 5 on the baseline; GDS 71% combined), so an axe gate can create false comfort; no AT was run for this record, so every announcement is design intent | measurement M1; GDS row above | Own measurement | High for the count; the AT gap is stated, not measured | 2026-09-29 |
| AGAINST: KLM predicts neither cold keyboard path is faster than the baseline form (E 4.62 s, F 4.42 s, baseline 4.12 s, all inside the band); the design cannot be justified by speed | design/tasks/a11y-flows.json | Model output (PREDICTION) | Medium | 2026-09-29 |

## Quantitative model

* Model and formula: Keystroke-Level Model, T = sum of operator times, chords count each key; pointing with geometry by Fitts (Shannon form) MT = a + b log2(D/W + 1); contrast by the WCAG 2.x relative-luminance ratio; focus-indicator area by the 4h + 4w perimeter rule of SC 2.4.13; reflow and sticky chrome by arithmetic on CSS px; tab stops and message lengths by COUNT.
* Inputs and sources:
  * KLM: K 0.20 s, M 1.35 s, B 0.10 s, H 0.40 s, P 1.10 s without geometry, R as stated (Wikipedia KLM table, opened 2026-09-29). R 70 ms is the server-side MEASURED p50 from `canvas-flows.json`; 100 ms is an assumption. Band plus or minus 21%.
  * Fitts: a = 0.37 s, b = 0.13 s per bit (Cockburn et al. 2007).
  * Geometry, two profiles from `design/tasks/canvas-flows.json`. **Headline (D)**: D = 175 px, W = 24 px (handle); D = 203 px, W = 56 px (node). **Layout-file cross-check (L)**: from `design/layouts/current-impact.json` and `proposed-canvas.json`, D = 46 px, W = 24 px (handle); D = 213 px, W = 48 px (node). Tables use D unless a column says L. The P ops in `a11y-flows.json` carry the `layout` stems and ids, so a consumer that recomputes from the layout files obtains the L totals.
  * Flows: `design/tasks/a11y-flows.json` (10 tasks). M placement is listed per flow in each task's assumptions; it is not identical across flows (T05 proposed has 2 more M than current, T08 1 more, both charged against the proposed design). T04 flows have no closing M so they compare with the drag path.
* Result for the current design: **PREDICTION**

| Flow | Current (s) | Band (s) |
|---|---|---|
| T04 keyboard, baseline form | 4.12 | 3.25 to 4.99 |
| T04 pointer, baseline form | 5.62 | 4.44 to 6.80 |
| T05 keyboard move, ESTIMATED editor workaround | 8.55 (7.55 with Shift held once) | 6.75 to 10.35 |
| T08 keyboard decide, baseline | 6.74 | 5.32 to 8.16 |

* Result for the proposed design: **PREDICTION**. "Like for like" says whether both flows start from the same state; a row that is not like for like is not a speed comparison.

| Flow | Proposed (s) | Band (s) | Ratio to current | Like for like? |
|---|---|---|---|---|
| T04 keyboard cold, **F** Outline (Ctrl+K, "Reject", Down, Enter, Enter, Enter, Down, Enter): M 1.35 + K 1.60 (8 keys) + T 1.20 + R 0.27 | 4.42 | 3.49 to 5.35 | 1.07 | yes: both from document start |
| T04 keyboard cold, E tree (Shift+F10 instead of the first Enter): K 1.80 (9 keys) | 4.62 | 3.65 to 5.59 | 1.12 | yes |
| T04 keyboard warm, **F** (Enter, Enter, Down, Enter): M 1.35 + K 0.80 + R 0.17 | 2.32 | 1.83 to 2.81 | 0.56 | **no**: focus is already on the Reject button |
| T04 keyboard warm, E pick-up (Space, Down, Enter): M 1.35 + K 0.60 + R 0.07 | 2.02 | 1.60 to 2.44 | 0.49 | **no**, as above; F against E warm is 1.15, inside the band |
| T04 click handle, click target (D): M 1.35 + P 0.767 + 2 B + P 0.657 + 2 B + R 0.07 | 3.24 (D); 3.08 (L) | 2.56 to 3.93 (D) | 0.58 (D); 0.57 (L, against 5.43) | partly: the current flow includes an ESTIMATED 22 px native popup row (0.576 s) and, in D only, an assumed one-notch scroll |
| T05 keyboard move (type-ahead, Shift+F10, Move to..., dry run 1 s) | 8.15 | 6.44 to 9.86 | 0.95 (1.08 with Shift held once) | no: the current flow is a guess |
| T08 keyboard decide | 5.69 | 4.50 to 6.88 | 0.84 | no: document start versus a focused card |
| T11 return to the tree by Shift+Tab (14 K; baseline 12 K, Shift held once) | 4.15 | 3.28 to 5.02 | 1.11 | approximately: different regions |
| T11 return to the tree by palette (Ctrl+K, "tree", Enter) | 2.75 | 2.17 to 3.33 | 0.73 | approximately; palette ranking assumed |

Reference: the drag path for the same edit is 3.04 s (D) or 2.88 s (L): M 1.35 + Fitts 0.766 + 0.10 + Fitts 0.657 + 0.10 + 0.07 in D. Non-drag paths against it, D / L:

| Path | Ratio to drag D / L |
|---|---|
| Click handle, click target | 1.07 / 1.07 |
| F keyboard warm | 0.76 / 0.81 |
| F keyboard cold | 1.45 / 1.53 |
| E keyboard warm | 0.66 / 0.70 |
| E keyboard cold | 1.52 / 1.60 |

* Decision flips inside the band? The flip range for a ratio is 0.79/1.21 = 0.653 to 1.21/0.79 = 1.532.
  * Inside the range, so no evidence of a difference: both cold keyboard paths against the baseline (1.07, 1.12), F warm against E warm (1.15), T05 (0.95 or 1.08), T08 (0.84), T11 by Shift+Tab (1.11) and by palette (0.73).
  * Against the drag, F cold is 1.45 (D) and 1.535 (L, 0.003 over the boundary); E cold is 1.52 (D) and 1.60 (L). L places the handle 46 px from the pointer start, which favours the drag, so the sign is not robust and no gap is claimed.
  * Outside the range but **not like for like**: the warm rows (0.49, 0.56) and the click row (0.58). `canvas-flows.json` section 11.2 finds T04-click not robust: its band overlaps the baseline when the current flow is charged one M fewer (4.27 s against 3.24 s).
  * No speed claim is made for any T04 row. E versus F is not decided by speed: their predicted difference (0.20 to 0.30 s) is inside the band.
  * Contrast, focus area, reflow and tab-stop results are exact properties of the specified values, not predictions with a band.
* Validity limits:
  * KLM covers expert, error-free, routine use. It does not model learning, errors, reading or **listening to a screen reader**, so no total above predicts a screen-reader user's time.
  * The Fitts constants were fitted to vertical menu-item selection by eight right-handed graduate students with a mouse. 2-D canvas handle and node pointing (the T04 click and drag rows, 1.07 and 0.58) lies outside that calibration task and is an extrapolation. The constants are not valid for users with tremor or limited dexterity, the people SC 2.5.8 protects.
  * Fitts index at D = 400 px: 4.14, 3.75 and 3.46 bits for 24, 32 and 40 px targets; 24 to 32 px saves 0.050 s (5.5% of 0.909 s), under that profile only.
  * The current T05 flow is a guess (assumed line counts). The T08 start states differ.
* Deliberate deviations from the model:
  * Approve and Apply are not shortened even where keys could be saved (P2, ADR-0064 D5); no shortcut, `accesskey` or palette command reaches them.
  * Tab stops in the default review view: 29 against 16 in the baseline Evidence view (COUNT), accepted only conditionally. The States lens adds the Outline: 10 stops for the excursion diagram, n states plus m transitions in general (M7).
  * Region reach is Tab x k plus Enter (k = 1, 2, 3 for main, tree, inspector; 2 to 4 keys) **from document start only**. From the inspector the tree is 13 Shift+Tab presses away (4.15 s) or the palette command "Focus tree" (2.75 s, T11). A region-cycle chord would shorten this and is undecided (design document Q3).

## Options considered

The decision is the accessibility architecture of the surfaces that a canvas and a tree add. Precedent sources are documentation pages; no product was run.

| Option | What it is and who does it (source) | Advantages | Drawbacks | Verdict |
|---|---|---|---|---|
| A: baseline | Native form controls, no canvas; sidebar hidden at 760 px or narrower; tabs as plain buttons (M1) | Few ARIA surfaces; forced colours stay legible; 1 axe violation | Loses functionality at about 170 to 190% zoom (B4); focus lost after selecting a case (B2); tab and case state not exposed (B3); no drag or tree, so it cannot deliver the product | Rejected as a target; its native-first habit is kept |
| B: picture with a text alternative, edits through separate forms | SVG or canvas as `img` with a short and a long description; all edits through forms elsewhere (W3C complex-image tutorial, https://www.w3.org/WAI/tutorials/images/complex/) | Cheapest; few ARIA roles | The long description is read-only; edits live in a second system away from the items they change | Rejected; F keeps its long-description idea and makes it operable |
| C: ARIA graphics module roles on SVG | `graphics-document` and `graphics-object` (https://www.w3.org/TR/graphics-aria-1.0/) | Standard vocabulary for diagrams | MEASURED in Chromium 154: the tree collapses to one `img`; AT support not shown | Rejected on measurement |
| D: Tab per shape on an SVG canvas | tldraw: Tab and Shift+Tab in canvas reading order, Ctrl/Cmd+arrow spatial jump, live announcement with position (https://tldraw.dev/sdk-features/accessibility); draw.io (dossier DGM§2.1) | Precedent users know; simple to build | Reading order from coordinates changes when layout changes, against P3; SVG text does not wrap (M2); custom focus handling inside SVG | Rejected; its position-in-set announcement is kept as an idea |
| E: HTML nodes, SVG edges, `role=tree` focus layer, one tab stop, authored pick-up keys | APG tree (S22), roving tabindex (S25), the navigable-structure idea of Data Navigator (S34) | 1 tab stop (M7); in-picture keyboard navigation; fastest warm keyboard path (2.02 s, not a significant gap) | Custom composite: ARIA risk (APG read-me-first, WebAIM Million); tree semantics announce a hierarchy (level, position in set) that a cyclic state graph does not have; two authored departures from the APG tree keys; pick-up keys must be learned; AT behaviour untested; conflicts with D2 | **Not chosen**; kept as the comparison arm of script S1 and adopted only if F fails a named task there |
| F: native Outline primary; picture pointer-only and `aria-hidden`, focus echoed | Visible generated Outline (nested list of native menu buttons, e.g. "Reject: Submitted to Rejected") as the keyboard, screen-reader and voice-control surface; picture HTML nodes and SVG edges inside an `aria-hidden` container with no focusable descendants; Outline focus is echoed on the picture (W3C complex-image long description, S33; Zong et al. structure and navigation, S35; APG menu button, S30) | Native roles need no custom key table and no AT-specific verification of a composite; no authored keys; a list of states with their outgoing transitions describes a cyclic graph without claiming a hierarchy; named targets for voice control; Outline is already required, generated and parity-tested; 0 axe violations apart from fixture sizing (M7) | 10 tab stops for the excursion diagram against 1 (M7); sighted keyboard users move through the Outline, not the picture, and rely on the echo; warm keyboard path 0.30 s slower than E (inside the band) | **Chosen** |

**OSS-first note (Data Navigator, MIT, https://github.com/cmudig/data-navigator, opened 2026-09-29).** Not adopted:

* Decision: ADR-013 keeps the browser free of a build-time framework and the Studio serves three static files under a strict CSP. A shipped npm ES module would have to be vendored, pinned and reviewed as a runtime dependency. Option F needs only native HTML.
* UNVERIFIED: its compatibility with the CSP and positioned HTML nodes (A10), and its screen-reader behaviour.
* Status: a rejection for now, not a finding that it is unsuitable; revisited together with E if F fails script S1.
* `docs/oss/REGISTER.md` is not owned by this lane: it needs a row "Data Navigator, MIT, evaluated, not adopted" from the integrator.

## Decision

Chosen option: "F", together with the supporting rules below.

* Measurement shows the baseline already fails on cheap things automated tools miss (B2 to B5).
* F follows the record's own native-first rule (D2). The evidence against custom ARIA (APG read-me-first; WebAIM Million 59.1 against 42 errors, an association) weighs on E, not on F.
* The excursion graph is cyclic (Revise: Rejected to Draft). **Tree semantics on it are a known misrepresentation**: `aria-level` and position in set announce a parent-child hierarchy between states that does not exist. A list of states, each with its outgoing transitions named with source and target, states the adjacency without claiming a hierarchy.
* F needs no authored keys; E needed two departures from the APG tree plus the pick-up keys.
* F's cost is measured: 10 tab stops for the excursion diagram against 1 (M7). It is accepted because AT users in browse mode move by list, button and heading commands rather than Tab, and because the region exits (palette commands, skip links) apply. It is a revisit trigger.
* The model predicts no speed benefit for any keyboard path; the decision rests on parity of function and semantic accuracy, not speed.

1. **D1 Target and claim.** WCAG 2.2 AA on every view, plus 2.4.12 and 2.4.13 as design constraints. No conformance claim until a WCAG-EM 2.0 audit; publish a statement listing failing SC.
2. **D2 Native first.** Custom widgets only from the catalogue: tree (the language tree, which is a real hierarchy), tabs, dialog, combobox, toolbar, menu button, disclosure. Destinations are `nav` links with `aria-current`; lenses are ARIA tabs. The diagram uses no custom composite.
3. **D3 Keyboard.** Skip links (main, tree, inspector) and palette commands to focus regions; composites are one tab stop with roving tabindex; Escape closes the topmost layer and returns focus to its invoker; one shortcut registry; only modifier shortcuts by default, `/` and `?` opt-in (SC 2.1.4); no key, `accesskey` or command reaches approve or apply.
4. **D4 Diagram.**
   * Structure: a `figure` whose `figcaption` is the short description ("State diagram, Excursion: 5 states, 5 transitions, 1 UNKNOWN"), holding the picture and the Outline.
   * Outline (primary surface, visible): a `section` with heading "Outline" and a nested `ul` in model order. Each state is a native `button` with `aria-haspopup="menu"`, named by its visible text; its outgoing transitions form a sublist of buttons named "Reject: Submitted to Rejected". Ripple counts including UNKNOWN are in each button's description.
   * Picture: HTML nodes and `aria-hidden` SVG edges inside one `aria-hidden` container; content-sized nodes; no focusable descendant (checked by axe `aria-hidden-focus`). Pointer-operable only. The reconnect handle is the 24 px pointer-only element of M6.
   * Focus echo: focus on an Outline button draws the focus ring token on the matching node or edge (visual only). A pointer selection on the picture updates the inspector and sets `aria-current="true"` on the matching Outline button, without moving DOM focus.
   * The Outline, the Table lens and the picture come from one function; a parity test compares them. No graphics roles, no tree role on the diagram.
   * Voice control: the Outline buttons are the named targets. UNVERIFIED; script S2 covers it.
5. **D5 Dragging.** Each drag has a single-pointer path (click the handle, then click the target) and a keyboard and voice path through the Outline menu ("Reconnect source...", "Move to...", "Position..." with X and Y fields), all into the same typed-request dispatcher. Abort before commit; targets at least 24 px, default 32 px. The pick-up keys of E are not built.
6. **D6 Focus.**
   * Outer ring: `:focus-visible` 2 px outline at 2 px offset. Area (w + 8)(h + 8) - (w + 4)(h + 4) = 4w + 4h + 48, above the 4w + 4h of SC 2.4.13.
   * Inset ring (tree rows, list rows, tabs, anything inside a scroll container): **3 px at offset exactly -3 px**, so the ring sits flush with the outer edge and is never inset further. Area 6w + 6h - 36, at least 4w + 4h whenever w + h is at least 18 px, so for every target of 24 px or more. A 2 px flush inset ring gives 4w + 4h - 16 and falls 16 px2 short (S5).
   * Colour: `--focus` at least 3:1 on every surface step and fill.
   * Not obscured: scroll-padding 48 px top and 36 px bottom; bars static below 752 CSS px.
   * Stability: renderers keyed by id so focus is never lost; focus goes to the `h1` on a destination change.
   * Dialogs (APG modal dialog, S23): the decision dialog holds a revision id, typed operations and UNKNOWN items, so initial focus is its heading (static `tabindex="-1"`). **If Apply is not easily reversible, Apply moves to a separate confirmation whose initial focus is Cancel.** Reversibility belongs to the decision aspect (A7); until it is stated this is a condition, not a settled choice. Apply is never the initial focus.
7. **D7 Announcements.** One `status` (polite) and one `alert` (assertive) at load; kernel-generated text only; at most one polite message per action, at most 20 words; job end announced once; no live status bar.
8. **D8 Status semantics.** Word plus `aria-hidden` glyph; word in ink, hue on the glyph; "NOT RUN" shown with a space; contrast computed on every surface step; not computable is UNKNOWN and fails the build; blocked controls use `aria-disabled` plus a visible reason.
9. **D9 Forced colours, zoom, spacing.** Paint through `currentColor` or a `forced-colors` block (MEASURED: hex not overridden); transparent 1 px borders on rows; three regimes at 1112 and 752 CSS px (hypothesis); every region reachable at 320 by 256; only the diagram canvas and data tables scroll in two directions; no `user-scalable=no`.
10. **D10 Cognitive.** COGA objectives as rules: one Help entry in the same relative order (SC 3.2.6), no retyping of shown values (3.3.7), confirmation of the exact revision (3.3.4), refusals state reason and allowed alternative, status definitions on demand, no UI time limits, one settings surface with storage never required.
11. **D11 Testing.** Static checks, axe-core 4.13 with `target-size` enabled, scripted keyboard, focus (including the 2.4.13 area), reflow, forced-colour and text-spacing tests in one Chromium, manual screen-reader passes (NVDA with Chrome first), and the cohort study. Automated results never stand alone.
12. **D12 Deviations recorded.** P8 "Tab and Shift+Tab through canvas shapes" becomes Tab through Outline items in **model order**; the picture itself takes no focus. P8 "`/` alias" becomes opt-in.

Invariants preserved:

* **AI proposes, kernel checks, owner decides**: every announcement is kernel-generated data; the decision dialog holds no AI text and takes initial focus on its heading; there is no shortcut to approve or apply.
* **Generated from the model**: the Outline, Table and picture come from one function with a parity test; reading order comes from the model, so layout cannot change it.
* **UNKNOWN visible**: a word plus a glyph, a count in each Outline item's description, announced in job results; legality that is not checked shows as "unchecked".
* **Untrusted text**: live regions and Outline labels are set through `textContent` only (I5).

## Anti-slop rubric check

Numeric values are COUNT or MEASURED where stated. The screens are not built, so per-viewport counts belong to the layout aspect and are UNKNOWN here. "Specified, unmeasured" means the design states a rule and names the check that will measure it; it is UNKNOWN, never a pass.

| Item | Target | Result | Value | MEASURED or PREDICTION |
|---|---|---|---|---|
| No decorative gradient, glassmorphism or blur | 0 | UNKNOWN | specified: 0 added, and forced colours removes gradients anyway (S38); no built screen to count, the check is pending in the lint | specified, unmeasured |
| No card inside card; containers only where they encode grouping or state | nesting depth at most 3 | UNKNOWN | specified: this aspect adds no container except the modal dialogs, drawers, one settings surface and the diagram `figure` (picture plus Outline); depth is measured on the built DOM | specified, unmeasured |
| Containers per primary viewport | at most about 12 | UNKNOWN | depends on layout | not measured |
| No emoji and no icon-per-bullet; icon-only controls have visible labels | 0 violations | UNKNOWN | specified: the markup lint fails an icon-only control (design document section 12.1); the lint does not exist yet | specified, unmeasured |
| No generic centred hero plus three-feature grid | 0 | not applicable | no hero is specified | |
| No purple or blue default gradient; no unexamined default font stack | rationale present | not applicable | this aspect adds no gradient and sets no family; the type record is HCI-ADR-0060; it requires rem units and content-sized boxes | |
| No placeholder, lorem or fake data; every number has a source | 0 unsourced values | pass | every number is MEASURED, COUNT or PREDICTION with constants; examples use the real excursion candidate (`policy.py`: Submit, Recommend, Approve, Reject, Revise) | |
| No paragraph where a label, glyph, number or diagram would do | prose blocks of 8 or more words at most about 30 words | pass | live announcements are at most 15 words and are shown as a status line; Outline items are labels of 1 to 4 words | COUNT |
| Visible chrome words in the primary viewport | at most about 120 | UNKNOWN | adds one visible word for Help, one settings control, up to 15 words in the status line while a message shows, skip-link text only on focus; in the States lens the Outline adds 35 words for the excursion (10 items, 25 words; caption 9; heading 1), counted into the viewport total by the layout aspect | COUNT |
| Distinct font sizes per viewport | at most 6 | UNKNOWN | specified: this aspect adds 0 sizes | specified, unmeasured |
| Type families | at most 2 plus one monospace | UNKNOWN | specified: this aspect adds 0 | specified, unmeasured |
| Elevations | at most 2 | UNKNOWN | specified: focus and state use outlines and surface steps, never shadow (shadows vanish in forced colours) | specified, unmeasured |
| Accent hues | 1 accent plus status hues | UNKNOWN | specified: `--focus` reuses the accent | specified, unmeasured |
| Eyebrow labels | at most 1 | UNKNOWN | specified: this aspect adds 0 | specified, unmeasured |
| Disclosure depth | at most 2 levels; UNKNOWN, proof status and blocked reasons at level 0 | UNKNOWN | specified: definitions on hover or focus are level 1, source view is level 2, blocked reasons are visible text at level 0; not built | specified, unmeasured |
| Colour is never the only carrier of meaning | 0 violations | UNKNOWN | specified: word plus shape plus hue; the forced-colour test checks it and has not run | specified, unmeasured |

## Accessibility check

Results for the proposed design where it is specified; UNKNOWN where the built UI is needed. The baseline result is given where it differs.

| Check | Standard | Result | Evidence |
|---|---|---|---|
| Text contrast computed, not asserted | WCAG 2.2 SC 1.4.3: 4.5:1 text, 3:1 large text | baseline pass; proposed UNKNOWN | Baseline 5.29 to 13.61:1 (computed). Provisional status text tokens are 4.50 to 4.54:1 on surface step 0 but 3.66 to 3.86:1 on step 2, so status words use ink; the token lint must compute every pairing |
| Non-text contrast | SC 1.4.11: 3:1 | baseline **fail**; proposed UNKNOWN until built | Baseline control borders 1.68 and 1.74:1. Provisional glyph hues at least 3.66:1 on all three steps; focus accent 3.83 to 4.50 (light), 3.66 to 4.50 (dark) |
| Colour not the only cue | SC 1.4.1 | UNKNOWN until the forced-colour and monochrome tests run | Word plus glyph plus hue; deutan dE_OK proved versus unknown 0.025 (dossier VIS§2.4) shows hue cannot separate them |
| Target size | SC 2.5.8: at least 24 by 24 CSS px | pass on the layout file; baseline UNKNOWN for two 18 px checkboxes | COUNT: 48 of 48 interactive elements in nav-proposed have both sides at least 24 px; smallest is `main-hidden` (776 by 24, the hidden-edit reveal); all others at least 28 px. `main-hidden` is below the 32 px default density and is handed to the layout aspect to raise to 32 px |
| Focus appearance | SC 2.4.13 (AAA, design constraint): area at least 4w + 4h, 3:1 change | pass by specification; UNKNOWN until the scripted area test runs | Outer ring 4w + 4h + 48; inset ring 3 px at -3 px gives 6w + 6h - 36 (D6) |
| Dragging has a non-dragging path | SC 2.5.7 (Level AA) | pass by design | Click-then-click; Outline menu commands; X and Y fields; PREDICTION click path +0.2 s over drag |
| Keyboard operable, visible focus, reading order | SC 2.1.1, 2.4.3, 2.4.7, 2.4.11 | baseline fail on focus loss (B2); proposed UNKNOWN until scripted tests run | Native Outline buttons in model order (M7), focus destinations, inset outline (MEASURED clipping), scroll-padding |
| Text spacing and reflow tolerate overrides | SC 1.4.12, 1.4.10 | baseline **fail** reflow (B4), pass crude spacing test (B10); proposed UNKNOWN | HTML text wraps (MEASURED); regimes and region reach tested at 320 by 256 |
| Reduced motion respected; motion never carries meaning | `prefers-reduced-motion` | UNKNOWN; specified | Follows motion-and-performance section 9; state changes also change glyph and word |
| Screen-reader name, role, state, position in set | Native list and button semantics; APG patterns: tree (language tree), tabs, dialog, combobox, toolbar, disclosure, menu button | UNKNOWN | Chromium tree keeps the Outline's lists and button names (M7); no screen reader was run; manual passes S1 to S8 |
| APCA Lc (advisory only) | not a gate | not computed for the proposal | Provisional dark tokens at 4.5:1 are about Lc 35 (VIS§2.4, MEASURED there), below the guidance of Lc 60 to 75; open (SYNTHESIS C10) |

## Validation plan

* Prototype measurements (one Chromium at a time, at 1440x900, 1024x768 and 320x256): axe-core 4.13.0 (test-only, MPL-2.0) with tags wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa and best-practice and `target-size` enabled, over every destination, lens, dialog, palette, empty and error state, both themes; scripted keyboard, focus, reflow, forced-colour (`forced_colors="active"`), text-spacing, reduced-motion and blocked-storage tests; token contrast matrix; layout and DOM target-size check; latency probe for lens switching against the 100 ms class.
* Pass criteria, fixed before running:
  * axe: 0 violations and 0 incomplete results without a written triage; `aria-hidden-focus` 0 on the picture.
  * Each composite has exactly one `tabindex="0"` item at rest.
  * After every action in `a11y-flows.json`, `document.activeElement` is not `body`; it is the specified element for dialogs and destination changes.
  * Tab from a modal cycles inside it; Escape closes it and returns focus to the invoker.
  * For every focusable item at 1440x900 and 320x256, the focus ring is fully inside the viewport and not under sticky chrome.
  * For every focusable item, the count of pixels that change between unfocused and focused screenshots is at least 4w + 4h, and those pixels change by at least 3:1 (SC 2.4.13 area and contrast).
  * Focus echo: focusing each Outline button marks exactly one picture element, the one with the same model id.
  * At 320x256 there is no horizontal page scroll outside the diagram canvas and data tables; 5 of 5 primary regions are reachable.
  * With forced colours, every SVG paint and glyph resolves to a system colour; two states that differ only in background colour are 0.
  * With the SC 1.4.12 overrides, 0 clipped or overlapping elements.
  * Exactly two live regions at load; at most one polite message per action; at most 20 words; no provider text.
  * Every text token at least 4.5:1 and every glyph, border and focus token at least 3:1 on every surface step, both themes; UNKNOWN counts as fail.
  * Parity test: Outline, Table and picture list identical ids, names and relations.
  * Manual: scripts S1 to S8 on NVDA with Chrome first, then JAWS with Chrome and VoiceOver with Safari; a combination not run is recorded NOT_RUN, never assumed to pass. S1 runs F and an E fixture side by side on the same tasks.
* User-study protocol reference: [docs/hci/design/accessibility.md](../hci/design/accessibility.md) section 13.
  * Design: within-subject, baseline Studio versus proposed, counterbalanced; cohorts keyboard-only, screen-reader (own AT), low-vision with zoom or magnifier, plus a mouse-and-keyboard control.
  * Participants and sample size: formative rounds of about 5 per cohort (finds problems, estimates no prevalence; L = 0.31 via LAW§2.10); quantitative comparison needs about 20 or more per group, usually out of reach for AT cohorts, so results there are descriptive with intervals.
  * Tasks: T04 (click-then-click and Outline menu), T05, T02, T08, T09, T10 on the excursion workflow.
  * Measures: time on task; error count; UNKNOWN items misread as PASS (target zero); for screen-reader users whether each seeded UNKNOWN was heard before approval; calibration; SUS; per-task SEQ; Raw NASA-TLX.
  * Analysis: pre-registered H1 every participant completes T04 and T08 with their own AT; H2 median non-drag time at most 3 times the pointer-drag median (the 3 is arbitrary; PREDICTION 1.07 for click-then-click and 0.76 to 1.45 for the Outline keyboard path, D profile); H3 no approval with an unheard or unread UNKNOWN; H4 at least half of keyboard participants find "Reconnect source..." in the Outline menu without instruction (unfounded threshold, revised after the formative round). Effect sizes with confidence intervals; SUS against 68 only with an interval.
  * Stop criteria: stop and redesign if any participant approves with an unread or unheard UNKNOWN on a seeded item, if any participant cannot complete T08 with their AT, or if the Outline (F) fails script S1 in two AT combinations.
* Status of results: none yet. **No user-benefit claim is made until results exist.**

## Consequences

* Good: functionality that survives zoom, keyboard-only use and forced colours; the diagram's accessible surface uses native HTML only, with no authored keys and no misrepresented hierarchy; named targets for voice control; one dispatcher for pointer, keyboard and menu; announcements that cannot carry provider text; a testing plan that does not rest on axe alone; recorded deviations from P8.
* Bad:
  * 29 tab stops in the default review view against 16 in the baseline Evidence view (COUNT).
  * The States lens adds one tab stop per state and per transition (10 for the excursion, M7); larger models scale linearly.
  * Region reach costs 2 to 4 keys only from document start; from another region it costs the palette command (PREDICTION 2.75 s) or up to 13 Shift+Tab presses; the region-cycle chord is undecided.
  * Sighted keyboard users do not move through the picture itself; they rely on the focus echo, which is untested.
  * The cold keyboard path is predicted no faster than the baseline form; up to 15 more visible words while a message shows; 35 Outline words in the States lens; manual AT passes and cohort recruiting cost time; the settings surface adds one dialog.
* Cognitive Dimensions impact: viscosity down for non-drag users (one dispatcher, menu paths); hidden dependencies down (ripple counts in each Outline item's description); premature commitment unchanged; provisionality kept (unchecked legality shown); visibility of UNKNOWN up; secondary notation protected (layout cannot change reading order); role-expressiveness up (a list of states and named transitions matches a graph; a tree would not); error-proneness down (refusal with reason and allowed alternative).
* Security and repository impact:
  * No server change and no new asset. Icons and glyphs are built with `createElementNS`; live regions and Outline labels take `textContent` only (ADR-013, I5).
  * Node positions use `element.style` and are subject to the untested CSP behaviour (A10, SYNTHESIS C15), so the CSP smoke test gates the picture; the Outline does not depend on it.
  * `localStorage` reads and writes sit in try and catch and are never required.
  * Test-only dependencies: axe-core 4.13.0 (MPL-2.0, fetched at test time with a pinned checksum, not shipped) and Playwright for Python (Apache-2.0); both need rows in `docs/oss/REGISTER.md`, which already lists them as rows still to add.
  * Baseline fix list from B1 to B5 and B11: focus keyed by id, `aria-current` and tab roles, sidebar drawer below 752 px, control borders at 3:1, `tabindex="0"` on scrollable `pre`.
* Licence check: Data Navigator MIT (https://github.com/cmudig/data-navigator, https://registry.npmjs.org/data-navigator/latest; evaluated, not adopted); axe-core MPL-2.0 (https://registry.npmjs.org/axe-core/latest, https://github.com/dequelabs/axe-core); Playwright for Python Apache-2.0 (https://raw.githubusercontent.com/microsoft/playwright-python/main/LICENSE). No font, icon or asset is added.
* Revisit when:
  * the Outline fails script S1 in two AT combinations, or F fails a named task that the E fixture passes in S1 (then evaluate E and Data Navigator);
  * the formative round shows that Tab traversal of the Outline blocks keyboard-only users, or the region-cycle chord is decided (recompute T11);
  * A7 states whether Apply is reversible (D6 dialog focus);
  * any cohort participant cannot complete T08;
  * axe or scripted tests find a failure the baseline of this record did not list;
  * p95 lens switch exceeds 100 ms (switch tabs to manual activation);
  * WCAG 3.0 or APCA is ratified or the DTCG colour module changes the contrast gate; an SC 3.2.6 interpretation for single-page applications is published; the 1112 and 752 px breakpoints move with the layout aspect.

## Definition of ready

- [x] Persona, task ids and frequency stated
- [x] Each evidence row has a URL, type, confidence and verification date; five rows argue against a candidate or the decision
- [x] Model outputs labelled PREDICTION with constants and band; validity limits stated (including screen-reader listening time and the Fitts calibration task)
- [x] At least three options, including the baseline (six)
- [x] Rubric table complete (UNKNOWN allowed, not counted as pass)
- [x] Accessibility table complete
- [x] Validation plan with pass criteria fixed in advance, and the study reference and stop criteria
- [x] No claim of user benefit without a study
