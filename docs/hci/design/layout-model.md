# Layout model: regions, density and responsiveness

Aspect `layout-model`. Lane `lane/ux-research`. Date 2026-09-29. Status: proposed; the decision record is [HCI-ADR-0058](../../adr/0058-hci-layout-model.md). Machine-readable geometry: [design/layouts/](../../../design/layouts/) (`proposed-*.json`, `current-*.json`). Nothing here measures an EIJA user. No page was built: proposed geometry is a specification, and every number derived from it is a DESIGN COUNT or a PREDICTION.

Labels used in this file:

| Label | Meaning |
|---|---|
| MEASURED | A command ran on the real baseline Studio (one headless Chromium, DPR 1, 2026-09-29; method in 2.1) |
| DESIGN COUNT | Computed by the scoring function (section 5) from the layout JSON of the specification; not from a built page |
| PREDICTION | A model output (Fitts, KLM, demand allocation) with its constants and band; never a measurement of a person |
| ASSUMPTION | An input I chose and state; it can be wrong |
| UNVERIFIED | Not read in a primary or official form this session; not built on |

## 0. Decisions first

| # | Decision | Confidence | Basis |
|---|---|---|---|
| D1 | Five persistent regions and two modal overlays (chosen over the baseline with only the hero removed, option A', and over the inspector as a bottom panel, option C; see 6.3 and 6.5). Regions: top bar (40 px), sidebar (model tree), main (the lens), inspector (ripple, evidence, properties), status bar (28 px). Overlays: command palette and owner decision dialog. Agent activity has no panel of its own: it is a count in the status bar (attention set), a jobs list opened from it, and one provider-marked "Ask AI" control in the inspector. | Medium | Precedent for the surfaces: VS Code (S3, S4), Storybook (S7). Allocation model (3.2). |
| D2 | The document never scrolls. Panes scroll inside themselves. At 1440x900 and 1024x768 every element with importance 0.5 or more (the daily tasks T02, T03, T06, T08) is inside the first viewport on all six proposed screens (DESIGN COUNT, scroll-free 1.000). The 1.000 follows from how the layouts were specified, not from a measurement of a built page; it is a design target. The baseline scores 0.059 to 0.500 on the tabs that carry those tasks (MEASURED geometry, element-weighted; 0.30 to 0.40 when each table or list counts once, 6.1). | High for the count; the value of "no scroll" is a brief requirement, not a finding (S9) | 6.1, 6.2 |
| D3 | Width rule. Each region gets its content minimum. Surplus goes to the regions in proportion to a demand share. Two quantities are rounded to 4 px, each once: the sidebar's share of the surplus and the combined sidebar-plus-inspector share; main takes the rest. With that rule no pane changes by more than 4 px when the window grows by 1 px anywhere from 1208 to 1600 (checked at every width; the first-draft rule, which rounded sidebar and inspector separately, moved main 7 px at 1457 to 1458). Minima: sidebar 288, inspector 360, main a floor that rises continuously from 560 to the canvas floor of 720 (main_min(W) = clamp(560, W - 648, 720)). Result: 296 / 752 / 392 at 1440, 288 / 720 / 360 at 1368, 288 / 632 / 360 at 1280. **The sidebar minimum is provisional**: 288 rests on 6.5 px per character; the typography lane's 14 px face gives about 7.0 px, which makes the minimum 296 (widths then 304 / 748 / 388 at 1440, 296 / 624 / 360 at 1280, L breakpoint 1216). The value is fixed when the chosen font is measured in a built row (9). The demand model moves widths by at most 12 px inside its sensitivity band, and gets no surplus at all below 1368, so the minima decide, not the model. | Medium; low for the sidebar minimum | 3.2; canvas floor and inspector floor are other lanes' stated requirements (9) |
| D4 | Breakpoints are sums of minima: 1208 (three panes), 960 (sidebar collapses to a 40 px rail), 600 (inspector becomes a drawer), below 600 one column. The sidebar collapses first because it has the lowest demand share in all 10,000 perturbed draws (PREDICTION; the perturbation is mine). | Medium | 3.3 |
| D5 | UNKNOWN is at level 0 on every screen: the status bar carries six status counts in fixed order (UNKNOWN, FAIL, CONFLICT, STALE, NOT_RUN, PASS), each a button that filters the tree and lists. Zero counts are shown. The baseline shows UNKNOWN on one tab, below the first viewport at 1440x900 (MEASURED). | Medium | P1; Storybook's testing widget totals with press-a-count-to-filter (S25), VS Code's status bar as a named surface (S3); 4.6 |
| D6 | Two resizable seams (sidebar to main, main to inspector) follow the ARIA window-splitter pattern: focusable separator, arrow keys, Enter collapses. F6 cycles regions. Sizes are per-viewer preferences kept in `localStorage` (wrapped in try/catch) and never enter the model layout or the presentation hash. | Medium | S5, S7; ADR-008 in `docs/adr/0000-poc-decision-log.md` |
| D7 | Two density modes, not three: Default (list row and chrome control height 28, gutter 12) and Compact (24 and 8). Fields that take typed answers (decision dialog, rename, definition) stay 32. The mode is set from the palette and the `?` sheet, not from a visible control. | Low | 3.5; WCAG 2.5.8 floor (S1); JetBrains added a compact mode (S8, vendor) |
| D8 | Placement follows selection, not Fitts optimisation, for one control: "Review decision" sits after the UNKNOWN group in the inspector. A nearer slot would save 0.03 to 0.16 s (PREDICTION, inside the KLM band) and is not taken. Approve and Apply exist only inside the decision dialog, 24 px apart, and nowhere else. | High for the invariant | P2; LAW§3; placement study 6.4 |
| D9 | Overlays are centred over the main region, not the viewport, at most 640 (palette) and 720 (decision) wide, modal, with no blur and at most one elevation step. | Medium | WCAG 2.4.11 note on modal content (S2) |
| D10 | The layout scoring function is a vector, not a score: pointing seconds per task flow, chrome words, prose words, containers, nesting depth, sub-24 px targets, per-region alignment share, scroll-free share; plus one diagnostic sum of budget excesses. Definitions and file conventions are in section 5 so the model package can compute all of it from the JSON. | High | 5 |
| D11 | Option A' (the baseline with the hero removed, a 48 px header and a sticky status strip) is modelled (6.5) and becomes a control arm in the study (10.2). The layout numbers alone cannot separate the value of the five regions from the value of removing the hero: A' is within 0.7 % (1440) and 0.3 % (1024) of B on the weekly KLM total, and B is chosen over A' on grounds the model does not measure (tree, inspector beside the selection, a 720 x 520 canvas floor, one place for Review decision), which are other lanes' requirements and study hypotheses. | Low | 6.5 |

What this file does not claim: that developers will like the layout, decide better with it, or work faster. KLM predicts no reliable time change (6.2). The case for the layout is structural (UNKNOWN in view, no page scroll, budgets, constant regions) and rests on a user study that has not run.

## 1. Scope and stated interfaces

I own the shell: regions, sizes, density, breakpoints, overlay placement, and the geometry files. I do not own what goes inside a region. Where another lane has already published an assumption about the shell, section 9 lists it, my decision and the consequence for that lane. Element ids in the layout files are an interface: the task-flow owner, the slop-budget script and the study protocol read them.

Inputs read in full: `docs/hci/research/SYNTHESIS.md`, `PRINCIPLES.md`, `hci-laws-and-quantitative-models.md`, `developer-tool-craft-benchmarks.md`; `docs/hci/personas-and-jtbd.md`; `design/brief.json`; the baseline `index.html`, `app.css`, `app.js`; `README.md`, `AGENTS.md`, `docs/adr/README.md`, `docs/oss/REGISTER.md`, ADR-003, ADR-008, ADR-013; the CSP in `interfaces/http.py`. Read for interfaces only (other lanes, still moving): `docs/hci/design/{ai-interaction,canvas-uml-interaction,language-and-ddd-tree,evidence-and-change-review,content-and-onboarding,motion-and-performance}.md`, `design/layouts/nav-*.json`, `design/tasks/*.json`.

## 2. Method

### 2.1 Baseline geometry (MEASURED)

The real baseline `index.html`, `app.css` and `app.js` were served by a local stub that returns the real Studio service's JSON for one verified case (the excursion request "Let teachers sign off excursions.", meaning "recommend only", verification run). Chromium (Chrome 154, headless, DPR 1) loaded it at 1440x900 and at 1024x768. For each of five screens (start, and tabs Change, Impact, Try, Evidence and Decision) a script recorded `getBoundingClientRect` in page coordinates for every visible control, heading, text block and container, plus computed styles. Definitions follow the slop dossier metrics M1 to M4, M17 and M18 (`docs/hci/research/ai-generated-ui-slop-and-first-impressions.md` 3.2). Counts of containers, nesting depth and sub-24 px targets from the JSON files equal the DOM script exactly on all ten screens; word counts differ by at most 3 (element-own text versus text nodes). "Chrome words" exclude text that comes from the model or evidence (case title, state names, rule cells, claim values, provider explanations).

Not measured: fonts other than the computed sizes, dynamic text I did not trigger (notices, errors), scrolled states, Firefox and Safari. The stub grants `trusted_fixture` (the worktree hashes differ from the shipped fixture); nothing else was changed.

### 2.2 Proposed geometry (specification)

Rules R1 to R8 (3.2 to 3.6 and 4) produce every coordinate. Element sizes come from anatomy (row and chrome control 28 px, typed-answer field 32 px, chip 24 px, gutter 12 to 16 px on a 4 px grid; 28 and 24 are also the row heights that the typography and language lanes and the navigation layout use) and are an ASSUMPTION until a built page is measured. Fixture content is the real excursion case: states Draft, Submitted, Recommended, Approved, Rejected; five actions; 125 one-step runtime cells; three PASS claims; human comprehension UNKNOWN. Two things are design intent, not kernel data: the context and aggregate grouping rows in the tree, and the NOT_RUN rows for evidence kinds listed in ADR-0018 whose lanes have not landed.

### 2.3 Models and constants

| Model | Formula | Constants | Source |
|---|---|---|---|
| Fitts, Shannon form | MT = a + b log2(D/W + 1) | a = 0.37 s, b = 0.13 s/bit (mouse, vertical pointing to menu items of 130 x 22 px at positions 1 to 16, so amplitudes of about 22 to 350 px and ID about 1 to 4 bits, 8 participants, R2 = 0.93). D is centre to centre. W is the smaller side of the target: ASSUMPTION. MacKenzie (1992, S10) offers "the smaller of W or H" as a possibility ("perhaps"), not as a tested rule, and refers to MacKenzie and Buxton (CHI '92) for a test of two-dimensional models; that paper was not opened. Profile B (W = width) is the sensitivity check. | S6 (Cockburn et al. 2007, PDF read); S10 (MacKenzie 1992: Shannon form, width for 2D targets) |
| KLM | sum of operators | K 0.20, H 0.40, M 1.35, B 0.10 s; R as stated; scroll page as one K per page (ASSUMPTION: one page-down scrolls 0.875 of the viewport; the Chrome value is UNVERIFIED) | S11 (Wikipedia summary; original scan not legible) |
| Band | plus or minus 21 % on a task total | RMS error of KLM for single unit tasks | S11 |
| Sensitivity | profile B: W = width only; C: Card 1978 constants a = 1.03, b = 0.096 (UNVERIFIED: taken from a repo dossier, not opened in this session; profile C is a sensitivity check only and no decision rests on it); D: P = 1.1 s flat | | LAW dossier 2.1 (secondary) |

Validity limits: expert, error-free, routine tasks; mouse; no reading, no learning. Reading time is not modelled, and review is mostly reading, so KLM says nothing about review quality. The Fitts constants were fitted on one-dimensional vertical moves of about 22 to 350 px (ID up to about 4.1 bits; my reading of the item size and positions in S6) on a 1400 x 1050 display. The flows here use two-dimensional moves, most of 300 to 1000 px and up to 1074 px (ID up to 4.8 bits), which is extrapolation in both distance and direction. Keyboard paths are outside it.

## 3. Region model

### 3.1 Regions

| Region | L size (1440x900) | Level 0 contents | Primary tasks | Precedent |
|---|---|---|---|---|
| Top bar | 1440 x 40 | Mark, case scope (title and revision), destinations Changes, Model, Evidence, palette trigger, provider and egress state | T09, T01 | VS Code separates navigation, editor and status surfaces (S3); the nav lane's destinations (9) |
| Sidebar (model tree) | 296 wide | Filter field; tree of context, aggregate, group, term (depth 4); one status shape per row | T05, T09, T14 | Storybook: story tree at the left with search (S7) |
| Main (the lens) | 752 wide | Changes: chapters of typed operations and before/after pictures. Model: lens row (Language, States, Journeys, Requirements, Tests, Personas), then the lens. Evidence: segments Claims and Mapping, claims table | T02, T04, T05, T06, T07, T12 | Storybook canvas (S7); Cursor 3 diffs view (S12) |
| Inspector | 392 wide | Selection-driven: Ripple (Changes), properties (Model), coverage (Evidence); UNKNOWN group; "Review decision"; "Ask AI to propose" with a provider-call mark | T03, T06, T08, T13 | Storybook panel (S7); VS Code secondary side bar (S4); Stripe drawer for context (dossier DEV 2.8) |
| Status bar | 1440 x 28 | Six status counts as filter buttons; attention set ("n need you, n running"); stage | T14, T06, T08 | VS Code status bar as a named surface (S3); Storybook testing widget at the foot of the sidebar with totals and press-a-count-to-filter (S7 for the position, S25 for the counts and the filter) |
| Palette (overlay) | 640 wide over main | Input, seven result rows with kind, shortcut and enabled or blocked state; no approve, no apply | T09 | Linear, Superhuman, VS Code (dossier DEV) |
| Decision dialog (overlay) | 720 wide over main | Exact revision, every UNKNOWN, the baseline's typed answers, acknowledgement, Approve and Apply | T08 | Stripe FocusView (dossier DEV 2.8) |

Region ids in the JSON are `region-topbar`, `region-sidebar`, `region-main`, `region-inspector`, `region-statusbar`. A region is separated by a single 1 px rule and shares the page surface; it is not a container in the sense of the slop metric M2 (single-side rules and no fill are excluded). Containers are only the UNKNOWN group, the refusal message, the palette and the decision dialog.

Why no separate agent panel. The brief lists agent activity as a region. The AI lane's design puts the inbox in the main column and needs a status footer that can show "2 need you" (`ai-interaction.md` assumption A1). A permanent panel would cost 300 or more px for content that is empty most of the time. This is a design decision, not a finding, and the study has an arm for it (10.2).

### 3.2 Allocation rule

Purpose: decide how to split width when the viewport is larger than the minima. It is a heuristic (area follows expected use); no paper I read establishes that area should follow attention.

Inputs (all ASSUMPTIONS):

* f_t, uses per week: daily 5, weekly 1, rare 0.25.
* c_t, criticality: 3 if the output feeds approve or apply (T02, T03, T06, T07, T08), 2 if it writes to the model (T01, T04, T05, T11, T12, T14), 1 for navigation, onboarding and AI asks (T09, T10, T13).
* a_t,r, the share of task attention spent in each region (TB top bar, SB sidebar, MA main, IN inspector, ST status bar), from a walkthrough of the proposed screens. No eye tracking exists.

| Task | Class | f | c | w = f x c | TB | SB | MA | IN | ST |
|---|---|---|---|---|---|---|---|---|---|
| T01 create case | weekly | 1 | 2 | 2 | 0.10 | 0 | 0.70 | 0.15 | 0.05 |
| T02 review by meaning | daily | 5 | 3 | 15 | 0.05 | 0.15 | 0.55 | 0.25 | 0 |
| T03 ripple | daily | 5 | 3 | 15 | 0 | 0.10 | 0.30 | 0.60 | 0 |
| T04 edit diagram | weekly | 1 | 2 | 2 | 0.05 | 0.05 | 0.70 | 0.20 | 0 |
| T05 edit tree | weekly | 1 | 2 | 2 | 0.05 | 0.60 | 0.15 | 0.20 | 0 |
| T06 run and read evidence | daily | 5 | 3 | 15 | 0.05 | 0.05 | 0.55 | 0.30 | 0.05 |
| T07 counterexample | weekly | 1 | 3 | 3 | 0 | 0 | 0.60 | 0.35 | 0.05 |
| T08 approve and apply (entry) | daily | 5 | 3 | 15 | 0 | 0 | 0.30 | 0.70 | 0 |
| T09 palette | daily | 5 | 1 | 5 | 0.80 | 0 | 0.20 | 0 | 0 |
| T10 first run | rare | 0.25 | 1 | 0.25 | 0 | 0.20 | 0.60 | 0.20 | 0 |
| T11 resolve stale | weekly | 1 | 2 | 2 | 0 | 0.30 | 0.20 | 0.50 | 0 |
| T12 map concept to code | weekly | 1 | 2 | 2 | 0 | 0.30 | 0.60 | 0.10 | 0 |
| T13 ask AI | weekly | 1 | 1 | 1 | 0 | 0.10 | 0.30 | 0.10 | 0.50 |
| T14 find gaps | weekly | 1 | 2 | 2 | 0.30 | 0.50 | 0.20 | 0 | 0 |

The overlay share of T08 (the dialog) and of T09 (the palette) is not a region and is left out of the columns; the T08 row covers the entry step only.

Demand D_r = sum over tasks of w_t x a_t,r. Result (PREDICTION): TB 6.50, SB 8.15, MA 33.85, IN 31.25, ST 1.50. Shares among the three width-bearing regions: sidebar 0.111, main 0.462, inspector 0.427.

Rules:

* R1. Minimum widths: sidebar 288 (PROVISIONAL), main 560, inspector 360.
  * Sidebar 288: 12 gutter, 3 levels x 16 indent, 16 chevron, 16 kind letter, 8 gap, 78 name (12 characters at 6.5 px, ASSUMPTION written for a 13 px sans), 8 gap, 60 status-word column, 16 status shape, 12 change mark, 12 gutter = 286, rounded to the 8 px grid. The typography lane (HCI-ADR-0060) proposes 14 px and measures its sans about 6 % wider than Segoe UI, which puts the average near 7.0 px: the name then needs 84 px, the sum 292, rounded 296. Both lanes are proposed; the value is set by measuring a built tree row in the chosen font. Every width and breakpoint below is given for 288, and 3.2 lists the 296 values beside them so nothing downstream has to be recomputed by hand. The language lane's row anatomy is the source of the 60 px column (`language-and-ddd-tree.md` section 1).
  * Main 560: one operation row needs 12 + 72 (kind badge) + 8 + 168 (name, truncated) + 8 + 3 x 56 (count chips, with gaps 176) + 8 + 96 (UNKNOWN chip) + 12 = 560.
  * Inspector 360: three lanes (AI, IA, review) assume 360 or more (section 9).
* R2. Main floor, continuous: main_min(W) = clamp(560, W - 288 - 360, 720). Main takes all growth from 1208 (560) to 1368 (720), where it reaches the canvas floor (canvas lane requirement I-L1: canvas pane at least 720 x 520 at 1440 x 900). A step from 560 to 720 at 1440 would move the inspector 68 px and main 85 px for a 1 px change of the window (audit finding, reproduced from the first-draft rule at 1439 and 1440); the clamp removes that step.
* R3. Surplus S = W - (288 + main_min(W) + 360), zero below 1368. Mode L: sidebar = 288 + q4(0.111 S); inspector = 360 + q4(0.538 S) - q4(0.111 S), where q4 rounds to the nearest multiple of 4 and 0.538 = 0.111 + 0.427; main takes the rest. Rounding the sidebar step and the combined side-pane step once each means main moves by at most 4 px per pixel of window, and sidebar and inspector by 0 or 4. The cost is that the inspector can shrink by 4 px when the window grows by 1 px (for example 400 to 396 at 1457 to 1458, when the sidebar steps up). The first-draft rule rounded sidebar and inspector separately; when both stepped at the same width, main moved 7 px (1457 to 1458: 296 / 765 / 396 to 300 / 758 / 400), which failed the pass criterion in 10.1. The two rules give the same widths at every width listed in the table below. Mode M (sidebar is a 40 px rail): the rail takes no surplus and S = W - (40 + 560 + 360); the surplus splits between main and inspector in the ratio 0.462 : 0.427, that is inspector = 360 + 0.480 S rounded to 4 px (at 1024: S = 64, 390.7, 392) and main takes the rest (592). A plain three-way split of S at 1024 would give inspector 388 and main 596; the two-way rule is the one the 1024 files use. Caps: sidebar 480, inspector 560 (80 characters at 6.5 px is 520, plus 16 padding each side is 552, rounded to 560; WCAG 1.4.8 limits line width to 80 characters at Level AAA, S14). At 7.0 px per character the 560 cap holds about 76 characters; the cap stays 560 because 1.4.8 is a maximum, not a target.
* R4. Users may drag the seams within [minimum, cap]; sizes persist per viewer (3.4).

Widths (DESIGN COUNT, rule output):

| Viewport width | Mode | Sidebar / main / inspector, minimum 288 | Same with minimum 296 (provisional alternative) |
|---|---|---|---|
| 1600 | L | 312 / 828 / 460 | 320 / 824 / 456 |
| 1440 | L | 296 / 752 / 392 | 304 / 748 / 388 |
| 1368 | L | 288 / 720 / 360 | 296 / 712 / 360 |
| 1280 | L | 288 / 632 / 360 | 296 / 624 / 360 |
| 1216 | L | 288 / 568 / 360 | 296 / 560 / 360 (L breakpoint) |
| 1208 | L | 288 / 560 / 360 (L breakpoint) | mode M: 40 / 688 / 480 |
| 1024 | M | 40 (rail) / 592 / 392 | 40 / 592 / 392 |
| 960 | M | 40 (rail) / 560 / 360 | 40 / 560 / 360 |
| 800 | S | 40 (rail) / 760 / drawer | 40 / 760 / drawer |

With the minimum at 296 the main floor becomes clamp(560, W - 656, 720) and reaches 720 at 1376; at 1440 main is 748, still above the canvas lane's 720.

The mode change at a breakpoint is a deliberate discontinuity (at 1207 to 1208: 40 / 687 / 480 to 288 / 560 / 360); the 4 px stability criterion applies inside mode L, 1208 to 1600, and inside mode M, 960 to 1207, where the maximum change is also 4 px (checked at every width).

Sensitivity (PREDICTION; script in Appendix C). I perturbed f by a factor between 0.5 and 2 (log-uniform), c by plus or minus 1 (clipped to 1 to 3) and every attention share by a factor between 0.5 and 1.5 (renormalised), 10,000 draws, seed 20260929. The perturbation ranges are my choice; they are not measured uncertainty.

| Viewport | Sidebar P10 to P90 | Main P10 to P90 | Inspector P10 to P90 |
|---|---|---|---|
| 1440 | 296 to 300 | 748 to 756 | 384 to 396 |
| 1280 | 288 (no surplus) | 632 (no surplus) | 360 (no surplus) |
| 1024 | 40 | 588 to 600 | 384 to 396 |

Readings: the surplus is small (72 px at 1440) and is zero from 1208 to 1368, so the demand model can only move about 12 px at 1440 and nothing at 1280; the minima decide. The main P10 to P90 of 748 to 756 comes from Python's `random` with the seed above; an independent numpy run in the audit gave 748 to 760, so the tail depends on the generator, and the ranges are indicative only. The sidebar has the lowest demand share in 10,000 of 10,000 draws, which fixes the collapse order. If T05 (tree editing) were daily instead of weekly, the sidebar share would rise (not simulated); that is the trigger in the ADR.

### 3.3 Breakpoints and collapse behaviour

| Mode | Viewport width | Behaviour | Derivation |
|---|---|---|---|
| L | 1208 and wider | Sidebar, main, inspector all docked | 288 + 560 + 360 |
| M | 960 to 1207 | Sidebar becomes a 40 px rail with its button and label "Model tree"; the status counts stay in the status bar. Ctrl+B expands it as an overlay that pushes nothing. | 40 + 560 + 360 |
| S | 600 to 959 | Inspector becomes a drawer from the right, at most 392 wide, opened from a button or by selection; it overlays main | 40 + 560 |
| XS | below 600 | One column. Destinations stay in the top bar (two rows); sidebar and inspector are full-width overlays. The diagram and data tables keep two-dimensional scrolling. | WCAG 1.4.10 exempts content that needs two-dimensional layout, such as diagrams and data tables (S16) |

Zoom equivalence: at 200 % browser zoom a 1440 px window is 720 CSS px wide (S mode); at 400 % on 1280 px it is 320 (XS). WCAG 1.4.10 asks for no two-dimensional scrolling at 320 CSS px (S16); 1.4.4 asks for 200 % text without loss (S17). The XS geometry is specified, not laid out in JSON, so its compliance is UNKNOWN.

Breakpoints are viewport media queries (guaranteed). Component-level container queries would let a pane adapt to a user-resized width, but the MDN page I opened does not state browser support, so container queries are an enhancement to test, not a dependency (S18).

Vertical: the shell is `height: 100vh` (the newer viewport units were not checked), top bar 40 and status bar 28 fixed, panes between them scroll internally. At 1280x720 the panes are 652 px tall; the 18-row fixture tree (48 filter + 18 x 28 = 552) fits without scrolling. 1280x720 is the template's second standard viewport, so I applied the same generator to it for all six screens (widths 288 / 632 / 360). DESIGN COUNT: scroll-free 1.000 on all six; the lowest non-status element ends at y = 692 (canvas surface) and the others by 684; containers, depth, chrome words and alignment equal the 1440x900 values (for example review 72 words, 1 container, 0.883); no target under 24 px. Two things change: the canvas surface is 632 x 576, below the canvas lane's 720 x 520 floor on width (that floor is stated for 1440x900; main reaches 720 only from 1368 up); and the before and after pictures on the review screen shrink to fit the pane. These files are not published, because this lane's file list does not include a 1280x720 stem; the integrator can add `proposed-*-1280x720.json` from the same rules (open item O10).

### 3.4 Seams, keyboard and persistence

* Seam element: `role="separator"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, `aria-controls` naming the pane, and an accessible name matching the primary pane (the pattern requires one: `aria-labelledby` pointing at the pane's visible label, else `aria-label`; here "Model tree" and "Inspector"), focusable; arrow keys move it; Enter collapses and restores the primary pane; Home and End jump to the limits (optional in the pattern); F6 cycles panes (optional in the pattern) (S5). Storybook also binds F6 and Shift+F6 to move between sidebar, toolbar, preview and panel (S7). Step 8 px; Shift plus arrow 32 px (mine). Double-click resets to default (mine).
* Palette and `?` sheet list "Widen sidebar", "Narrow inspector", "Reset layout" (the non-pointer path for resizing).
* Hit area 8 px wide, visual line 1 px. That is below 24 px. WCAG 2.5.8 passes an undersized target if a 24 px circle centred on it meets no other target (S1), so content is inset at least 12 px from the seam centre line (the 12 px gutter). Whether a splitter counts as a target under that exception is my reading; it needs the accessibility test in section 10.
* Persistence: `localStorage` key `eija.shell.v1`, value `{sidebar, inspector, density, collapsed}`, every read and write in try/catch, default values when absent, values clamped to limits at load. It is a per-viewer convenience; it never reaches the server. Pane sizes are chrome layout. Diagram node coordinates are model layout: they go through the kernel, change the presentation hash and renew the exact-presentation approval (ADR-008, baseline `app.js` message). Pane sizes must never be part of that subject.
* URL state uses the query string. The hash carries the session token in the baseline and is cleared on load (`history.replaceState`), so it cannot hold a route.
* Applying sizes under the CSP: `style-src 'self'` blocks inline `style` attributes and `style.cssText`, and does not block properties set through the element's `style` object (S15). Sizes are applied with `document.documentElement.style.setProperty('--w-sidebar', ...)` and read in `app.css` by a grid template. Whether `setProperty` is treated like a property assignment is untested in this repository (open item C15 in SYNTHESIS). Fallback if the smoke test fails: quantised widths as `data-` attribute values matched by attribute selectors in `app.css` (eight steps per pane), no inline style at all.

### 3.5 Density modes

Interface with the token and type aspects (not decided here): 4 px base grid; at most six font sizes in total; base text 14 px as proposed in HCI-ADR-0060 (my first assumption was 13 px; the derivations in 3.2 use 6.5 px per character and section 9 gives the 7.0 px sensitivity).

| Property | Default | Compact |
|---|---|---|
| Tree row, list row, chrome control (button, tab, filter field) | 28 | 24 |
| Typed-answer field (dialog, rename, definition) | 32 | 28 |
| Chip height | 24 | 20 (non-interactive only; interactive chips stay 24) |
| Pane gutter | 12 to 16 | 8 |
| Tree rows visible at 1440x900 (784 px below the filter) | 28 | 32 |
| Tree rows visible at 1280x720 (604 px) | 21 | 25 |

The fixture tree has 18 rows and fits in both modes; the language lane's larger sample has 43 nodes and 15 default-expanded rows, which fits at 28 px (`language-and-ddd-tree.md` D1; the typography lane hands the layout aspect the same 28 and 24 px row heights, HCI-ADR-0060). 24 px equals the WCAG 2.5.8 minimum, so Compact is the floor, not a comfort size. I first considered 32 px rows (the visual-foundations dossier) and took 28 because three lanes already use it and the pointing cost is negligible. Fitts index of difficulty at D = 400 px: 24 px 4.14 bits, 28 px 3.93 bits, 32 px 3.75 bits (PREDICTION); at the Cockburn constants a step of 4 px changes movement time by about 0.03 s, inside the band; that is 0.05 s per pointing act, inside the band. Density is therefore justified by capacity, not by speed.

## 4. Screens

All six proposed screens keep the same five regions in the same place (constant regions: no pane changes size when the lens changes). Counts are DESIGN COUNT at 1440x900 with 1024x768 in brackets.

| Screen (file stem) | Destination and lens | Main | Inspector | Chrome words | Containers |
|---|---|---|---|---|---|
| `review` | Changes | Header (operations, viewed n of 4, hidden-edit counter, Source). Chapters Core and Consequences with four typed operations (ADDED State Recommended; ADDED Action Recommend; MODIFIED Action Approve; MODIFIED Action Reject), each with kind badge, count chips (States, Journeys, Tests) and an UNKNOWN chip. Before and after pictures side by side. | Ripple groups States 3, Journeys 3, Tests 125 cells, each with the tier "kernel". Unknown group: human comprehension not measured; personas and requirements not analysed. Review decision. Ask AI to propose (provider call). | 72 (69) | 1 (1) |
| `canvas` | Model, States lens | Lens row, toolbar (Select, Connect, Tidy, Fit and the note "Layout edits renew presentation review"), canvas 752 x 756. Five state nodes; two 24 x 24 handles at the source end of the Approve and Reject edges. | Edge Reject: verdict with bound, role, "Starts at" select with Apply (the non-drag path), ends at, guards, required and forbidden effects, links. | 63 (60) | 0 (0) |
| `language` | Model, Language lens | Lens row, term header (name, kind, Move, Rename, Add child), definition field, children table (term, tests, status). | Rename preview: new name, ripple counts with tier, the kernel's refusal ("outside the supported edits", ADR-003), Apply rename. | 71 (68) | 1 (1) |
| `evidence` | Evidence, Claims | Segments Claims and Mapping, Run verification, filter chips, nine claim rows (three PASS, five NOT_RUN, one UNKNOWN), empty trace area. | Four-slot coverage row for the selected claim: claim, covered, assumed, NOT covered. | 66 (63) | 0 (0) |
| `palette` | overlay on Changes | Palette 640 wide, at most 592 at 1024. Rows: Go to, Show ripple of, Set rejection source, Run verification, Rename term (blocked, reason), Ask AI to propose (AI proposal, provider call), Density. No Approve or Apply row. | (underlying) | 90 (87) | 2 (2) |
| `decision` | overlay on Changes | Dialog 720 wide: revision, UNKNOWN (3), the kernel's three questions, acknowledgement, Cancel, Approve revision, Apply to baseline (24 px apart). | (underlying) | 72 (69) | 2 (2) |

Notes on the five task-critical placements:

* T03 (ripple): selecting an operation row updates the inspector; the counts sit beside each row as scent (LAW 2.8) and the items in the inspector. Nothing is behind a disclosure at level 0.
* T04 (drag): handles are 24 x 24; the drop target is the node (minimum side 48, scaled to 43 at narrow widths). The non-drag path is the inspector select plus Apply, the same two controls the baseline has. A refusal appears at the drop target (canvas lane).
* T05 (rename): the ripple and the refusal show before the request is sent. Today rename is refused because it is outside the two executable edits (ADR-003, README); the layout reserves the space for the refusal message so a later executable rename changes content, not geometry.
* T06 (evidence): the status bar, the claims table and the coverage row are all inside the first viewport; Run verification is the first control in main.
* T08 (decision): the entry button follows the UNKNOWN group in reading order. The dialog lists every UNKNOWN before Approve. Approve and Apply are separate buttons, Approve left of Apply, 24 px apart. Approve is never the default focus target (decision lane).

`design/layouts/` also holds the current UI: `current-{start,change,impact,try,evidence}` at both viewports, MEASURED. `nav-current.json` and `nav-proposed.json` belong to the navigation lane and are not mine.

## 5. Layout scoring function

Input: one layout file L = {ui, screen, viewport V = (w, h), elements}. Optional: task flows in `eija.taskflow.v1` that reference `L` by file stem in their `P` operations.

Conventions the model package must apply:

| Convention | Rule |
|---|---|
| Virtual elements | ids starting `__` (for example `__pointer`, the pointer rest position at the viewport centre, and `__open-decision`) are only pointing anchors. They are excluded from every count. |
| Region elements | ids starting `region-` are regions. They have role `panel` but are not containers. |
| `words` | Chrome words: static interface text and status words (PASS, UNKNOWN, kernel, provider call). Names, ids and numbers that come from the model or evidence count 0. A word is a run of letters or digits. |
| `importance` | w_t / max w_t for the task that uses the element (the maximum over tasks if several), where w_t = f_t x c_t (3.2). Default 0.05. Virtual elements 0. |
| Roles | `button`, `input`, `tab`, `tree-item` are interactive. `chip` is interactive only if its id starts `filter-` or `st-`; in the files, interactive chips carry role `button`. `canvas` covers diagram surface and nodes and is free-positioned. |
| Overlays | An overlay file (`palette`, `decision`) contains the base screen's elements that the overlay does not intersect, plus the overlay elements (occlusion rule). |

Metrics (all per file, computed over elements that intersect V unless stated):

1. `words` = sum of `words` over visible elements. `prose_words` = the same over elements with 8 or more words.
2. `containers` = number of visible elements with role `panel`, id not starting `region-`, area at least 2500 px2. (The slop metric M2 also needs 2 children; with geometry only, I take elements that contain at least two other elements or are a modal, and the two counts agree on all ten baseline screens.)
3. `depth` = longest chain of containers where each contains the next (1 px tolerance).
4. `small_targets` = interactive elements with min(w, h) < 24. The spacing exception of WCAG 2.5.8 is not applied, so the count is conservative.
5. `align_top6` = for each region (the smallest full, unclipped `region-` box containing the element centre; else "root"), cluster the integer left edges of the visible non-panel, non-canvas elements by chaining (a sorted edge joins the previous cluster if it is at most 1 px from that cluster's last edge) and count the elements on the six largest clusters; the result is that count summed over regions divided by the number of elements. "Visible" means the box intersects the viewport, even partly. Code: Appendix C.3. The slop dossier target is at least 0.85 (BAND, hypothesis; tree indentation legitimately adds edges).
6. `scroll_free` = sum of importance over elements with importance at least 0.5 (excluding panels and regions) that lie fully inside V, divided by the sum over all such elements. 1.0 means no critical element needs a page scroll. The elements considered are those present in the file, so read it together with the task list. Two limits. (a) It counts elements, so a table of 25 cells weighs 25 times one button; the report in 6.1 therefore adds a group-weighted variant in which each table or list counts once. (b) It does not score pane-internal scroll: content that a proposed screen reaches only by scrolling inside a pane is not in the files, and 6.1 lists it separately. Importance mapping for the baseline files: an element takes the importance of the task that uses it (T03 and T04 on the Impact tab; T06, T07 and T08 on the Evidence tab), 1.0 for the daily criticality-3 tasks, so every matrix cell, journey line, question field, UNKNOWN text and action button is 1.0; panels are excluded from the metric but their text children (the UNKNOWN heading and its paragraph) are not.
7. `point_cost(task)` = sum over `P` operations that name this layout of MT(from, to) = a + b log2(D/W + 1), D the distance between centres, W = min(w, h) of the target, constants from 2.3. Report ID beside MT. `time(task)` = KLM sum of all operations with the operator times in 2.3; report a band of plus or minus 21 %. A `P` without a layout uses 1.1 s. A scroll is one `K` per page.
8. `total_words` (ESTIMATE) = word tokens (runs of letters or digits) in the `label` of every visible element that is not a panel, canvas or region and contains no other such element. It includes model and evidence text and numbers, which `words` excludes; the brief's "about 120 visible words" is checked against it (6.1).
9. `chips` = visible elements with role `chip`. Reported beside `containers` because a chip with a border or fill is a "bordered or filled container" in the brief's sense, and that styling is not decided here.
10. `budget_excess` = max(0, words - 120)/120 (chrome words) + max(0, containers - 12)/12 + max(0, depth - 3)/3 + small_targets + max(0, 0.85 - align_top6)/0.85 + (1 - scroll_free). It is a diagnostic sum of fractions over budget, 0 when every budget is met; decisions cite the vector, not this sum. Font sizes are not in it: the layout files carry no font size (the DOM script measures them).

Every output carries the label PREDICTION or DESIGN COUNT, the constants profile and the band.

Reference implementation: about 200 lines of Python (pure functions over the JSON, plus the flow tables of Appendix B) produced every number in section 6; it is not shipped from this lane, so Appendix C gives unrounded totals for every flow, the allocation script and the alignment function. The task-flow schema has no scroll operator and no way to name a pointer position after a scroll. This file models a scroll as one `K` (one page-down is 0.875 of the viewport, ASSUMPTION) and, for the first pointing act after it, computes two values: page coordinates (the pointer and target as they were before the scroll) and scroll-corrected coordinates (the target re-based by the scroll distance, the pointer unmoved). Neither bounds the other: the corrected act is shorter when the target was far below the pointer and longer when the scroll carries the target past it (T04 1440 and T08 1024 in Appendix C). Headline numbers use the scroll-corrected value because it follows the physical sequence; the page-coordinate value is reported beside it.

## 6. Results

### 6.1 Layout vectors, current versus proposed

Current rows are MEASURED geometry scored by the function; proposed rows are DESIGN COUNT; A' rows are the current geometry shifted and edited by the rules in 6.5 (DESIGN COUNT on a modelled page, not measured). The current UI's own screens are the four tabs; the proposed screens carry the same tasks under different names, so pairs are by task, not by tab.

| File | Words | Prose words | Containers | Depth | Targets < 24 | align_top6 | scroll_free | Excess |
|---|---|---|---|---|---|---|---|---|
| current-change | 93 | 36 | 7 | 2 | 1 | 0.816 | 1.000 | 1.040 |
| current-impact | 85 | 23 | 9 | 2 | 0 | 0.762 | 0.059 | 1.045 |
| current-try | 109 | 47 | 5 | 2 | 0 | 0.875 | 1.000 | 0.000 |
| current-evidence | 80 | 23 | 7 | 2 | 0 | 0.833 | 0.500 | 0.520 |
| current-change (1024) | 93 | 36 | 4 | 1 | 1 | 0.875 | 1.000 | 1.000 |
| current-impact (1024) | 77 | 23 | 7 | 2 | 0 | 0.857 | 0.059 | 0.941 |
| current-evidence (1024) | 80 | 23 | 7 | 2 | 0 | 0.818 | 0.333 | 0.705 |
| A' change (modelled, 6.5) | 90 | 24 | 6 | 2 | 1 | 0.900 | 1.000 | 1.000 |
| A' impact | 89 | 26 | 8 | 2 | 0 | 0.778 | 0.600 | 0.485 |
| A' try | 103 | 35 | 4 | 2 | 0 | 0.833 | 1.000 | 0.020 |
| A' evidence | 82 | 28 | 7 | 2 | 0 | 0.907 | 0.833 | 0.167 |
| A' change (1024) | 81 | 24 | 6 | 2 | 1 | 0.889 | 1.000 | 1.000 |
| A' impact (1024) | 84 | 26 | 8 | 2 | 0 | 0.867 | 0.200 | 0.800 |
| A' try (1024) | 98 | 35 | 4 | 2 | 0 | 0.825 | 1.000 | 0.029 |
| A' evidence (1024) | 82 | 28 | 7 | 2 | 0 | 0.900 | 0.750 | 0.250 |
| proposed-review | 72 | 0 | 1 | 1 | 0 | 0.883 | 1.000 | 0.000 |
| proposed-canvas | 63 | 0 | 0 | 0 | 0 | 0.875 | 1.000 | 0.000 |
| proposed-language | 71 | 0 | 1 | 1 | 0 | 0.875 | 1.000 | 0.000 |
| proposed-evidence | 66 | 0 | 0 | 0 | 0 | 0.929 | 1.000 | 0.000 |
| proposed-palette | 90 | 9 | 2 | 1 | 0 | 0.946 | 1.000 | 0.000 |
| proposed-decision | 72 | 0 | 2 | 1 | 0 | 0.962 | 1.000 | 0.000 |
| proposed-review (1024) | 69 | 0 | 1 | 1 | 0 | 0.855 | 1.000 | 0.000 |
| proposed-canvas (1024) | 60 | 0 | 0 | 0 | 0 | 0.826 | 1.000 | 0.028 |
| proposed-language (1024) | 68 | 0 | 1 | 1 | 0 | 0.839 | 1.000 | 0.013 |
| proposed-evidence (1024) | 63 | 0 | 0 | 0 | 0 | 0.909 | 1.000 | 0.000 |
| proposed-palette (1024) | 87 | 9 | 2 | 1 | 0 | 0.929 | 1.000 | 0.000 |
| proposed-decision (1024) | 69 | 0 | 2 | 1 | 0 | 0.950 | 1.000 | 0.000 |

Word counts in the proposed rows follow one convention (section 5, `words`): fixed status words count, model and evidence terms do not. The three UNKNOWN items ("Human comprehension not measured", "Personas not analysed", "Requirements not analysed") count 2 each in every file ("not measured", "not analysed"); the first draft counted 2, 3 and 3, which made review, palette and decision 2 to 4 words higher.

Total visible words and chips. The chrome-word budget above leaves out model and evidence text and all numbers, so it says nothing about how much text a screen shows. The brief's budget is "at most about 120 visible words", and its container budget is "bordered or filled containers". Two further columns, one row per screen:

| Screen | Total words, current (MEASURED, DOM text nodes in the viewport) | Total words, proposed (ESTIMATE, label tokens of leaf elements) | Chips, current (JSON) | Chips, proposed (DESIGN COUNT) | Panels plus chips, proposed |
|---|---|---|---|---|---|
| review (current: Change tab) | 171 (144) | 144 (122) | 2 (2) | 29 (29) | 30 (30) |
| canvas (current: Impact tab) | 156 (140) | 121 (99) | 2 (2) | 3 (3) | 3 (3) |
| language (no current equivalent) | not applicable | 120 (98) | not applicable | 15 (15) | 16 (16) |
| evidence (current: Evidence tab) | 134 (131) | 143 (121) | 2 (2) | 16 (16) | 16 (16) |
| palette (overlay) | not applicable | 152 (130) | not applicable | 10 (10) | 12 (12) |
| decision (overlay; current: Evidence tab after scroll) | not applicable | 159 (137) | not applicable | 9 (9) | 11 (11) |

1440x900 first, 1024x768 in brackets. Current Try tab: 155 (151) words; Start: 126 (103).

* Total words, proposed: the sum of word tokens (runs of letters or digits) over the `label` of every visible element that is not a panel, canvas or region and does not contain another such element (leaf rule, so a row and its cell are not counted twice). It counts numbers as words and assumes the label is all the text the element shows; it is an estimate from the specification, not a DOM count. The current column is the DOM count from 2.1 (`wordsVP`), a different method, so the two columns are not strictly comparable. The current JSON labels are cut at 70 characters and cannot be used for this.
* Reading: on total words both the baseline (126 to 171) and the proposal (120 to 159 at 1440x900; 98 to 137 at 1024x768) exceed "about 120" on most screens. The chrome-word budget is met; the total-word budget is not. The excess is model and evidence content that the tasks require (18 tree rows, four operation rows with their counts, nine claim rows); cutting it would hide the tree or evidence. This is a recorded deviation from the brief (HCI-ADR-0058 carries it), not a pass. The 120 target itself is a hypothesis to calibrate against reference products, and nobody has measured those yet.
* Chips: `containers` follows slop metric M2, which needs at least two children, so a single-text chip is not a container in either the baseline DOM count or the JSON count. The comparison with the baseline is therefore like for like. But the brief counts "bordered or filled" boxes, and whether a chip has a border or fill is a token and colour decision that has not been made. If status chips are drawn as filled or bordered pills, the review screen has 30 boxes against a budget of about 12 and fails; if they are drawn as a word plus a status shape with no box, it has 1. The containers row of the rubric is therefore **pass only if chips carry no border or fill**, and this lane asks the token and colour lanes to draw status chips unboxed (word plus shape) or to record the deviation.
* Alignment reproducibility. The auditor reported current-* `align_top6` values 0.02 to 0.03 below the table. The function in Appendix C.3, applied to the published JSON, reproduces every value in the table exactly, current and proposed (for example current-change 0.816, current-impact 0.762, current-try 0.875, current-evidence 0.833; 1024: 0.875, 0.857, 0.818). The values are not from the DOM script: its text-node measure (no regions, whole viewport) gives 0.55, 0.55, 0.60 and 0.55 for the four current tabs at 1440x900. The definition has two details that change the result if read differently, and C.3 fixes both: an element counts if its box intersects the viewport, even partly; and region membership uses the full region box, not the box clipped to the viewport. Clipping the region boxes gives 0.737 for current-change and 0.829 and 0.788 for current-impact and current-evidence at 1024, which is one possible source of the auditor's lower values; no ordering or budget conclusion changes either way.

Honest reading:

* The baseline is inside the word and container budgets at these viewports (chrome words 77 to 109 over the ten baseline files, containers 4 to 9, MEASURED). The words budget is not the baseline's problem. Its problems are position and type: task content starts at y = 630 of 900 on the four tabs (70 % of the viewport is hero, tabs and headings; y = 587 of 768 at 1024), page height is 1698 to 1863 px at 1440x900 and 1691 to 1921 at 1024x768, the approve and apply controls are below the first viewport, and the first viewport uses 10 to 13 distinct font sizes (MEASURED) against a target of 6.
* The Impact tab carries T03 and T04 and scores 0.059: the ripple summary, journeys, the 25-cell rule table and the closure details are all below the fold. That value is driven by the table, which contributes 25 of the 34 elements with importance 1.0; the two tabs that are in view contribute 2. Counting each table or list once (group-weighted: tabs, summary line, table, journeys), the same screens score 0.400 (2 of 5 groups in view) at both viewports; the Evidence tab scores 0.400 at 1440 (4 of 10 groups) and 0.300 at 1024. The proposal's 1.000 against 0.30 to 0.40 is therefore the fair comparison; 1.000 against 0.059 exaggerates it.
* The baseline's UNKNOWN box is counted. The metric skips panels, but the box's heading and paragraph are separate elements with importance 1.0 (Evidence tab, y = 969 and 996 of a 900 px viewport) and both are below the fold; "Human comprehension: UNKNOWN" is one of the six groups out of view on that tab.
* The proposal's 1.000 holds by construction: the layouts were specified so that every element of importance 0.5 or more sits in the first viewport, so the value is a design target, not a result. What it leaves out is pane-internal scroll, which the files do not model. Critical content reached by scrolling inside a pane: the 125-cell Tests lens (not laid out; the inspector shows the count and the tier), the language lane's 43-node tree when fully expanded (43 x 28 = 1204 px against 784 px of pane at 1440x900; 15 default-expanded rows fit), and the claims table beyond nine rows. Three critical items therefore need pane scroll and are not counted in the 1.000.
* Baseline has one target under 24 px on the Change tab (the egress checkbox, 18 x 18) and another below the fold (the acknowledgement checkbox, 18 x 18).
* The proposal saves chrome words (60 to 90 against 77 to 109 in the current screens) and has fewer containers, but two 1024x768 layouts fall short of the alignment hypothesis (0.826 and 0.839 against 0.85). That is reported, not tuned away.
* Persistent shell words: 24 (top bar 13, sidebar filter 1, status bar 10). The content lane's budget for the shell is 20 (`content-and-onboarding.md` D2), so this is a recorded deviation: the status bar carries six counts because P1 requires counts by state.
* UNKNOWN first sight. Baseline: page-down after opening the Evidence tab, 0.91 s of operators (P 0.61 + B 0.10 + K 0.20) at 1440x900, and the UNKNOWN box is never visible before that. Proposed: 0 operators; the count is in the status bar on all six screens.

### 6.2 Pointing and KLM, current versus proposed (PREDICTION)

Constants: Cockburn profile, W = smaller side. Scroll-corrected values (page-coordinate values and unrounded totals in Appendix C); band plus or minus 21 %. Content is held constant between the flows: the same three typed answers (22 characters), one acknowledgement, Approve, Apply, the same kernel response times (400 ms each, ASSUMPTION), the same reading pauses (one M each). Only geometry, tab or lens switches and scrolls differ. The pointer starts at the viewport centre in both.

| Task (frequency) | Viewport | Current s | Proposed s | Change | Bands overlap? | Note |
|---|---|---|---|---|---|---|
| T03 ripple (daily) | 1440x900 | 4.77 | 3.68 | -23 % | yes | Current: tab, one page-down, open the closure details. The current UI shows a JSON dump, not counts per model kind. |
| T03 | 1024x768 | 4.85 | 3.67 | -24 % | yes | Two page-downs in the current UI |
| T06 run and read evidence (daily) | 1440x900 | 5.56 | 5.54 | 0 % | yes | The 1 s verification job is included in both |
| T06 | 1024x768 | 5.48 | 5.54 | +1 % | yes | |
| T08 approve and apply (daily) | 1440x900 | 13.22 | 14.03 | +6 % | yes | Terms identical in both flows are 9.6 s of the total |
| T08 | 1024x768 | 13.61 | 13.82 | +2 % | yes | Current needs two page-downs |
| T04 edit by drag (weekly) | 1440x900 | 4.85 (form) | 5.21 drag, 4.43 if the States lens is already open | +7 %, -9 % | yes | Includes the destination and lens clicks |
| T04 non-drag path (weekly) | 1440x900 | 4.85 | 6.74, 5.95 if the lens is open | +39 %, +23 % | yes, barely | Costs one more point-and-click than the baseline form: select the edge first. This is the price of the WCAG 2.5.7 alternative; a keyboard path is not modelled. Picking the option from the open select is modelled as a point from the select to itself (D = 0, MT = a = 0.37 s), which understates a list that opens below the select; the baseline flow uses the same shortcut, so the comparison is symmetric but both totals are low. |
| T09 go to Reject (daily) | 1440x900 | not applicable | 2.65 palette, 2.49 tree click, 3.05 palette from the mouse | | | The palette does not beat a visible tree row (0.16 s), as the dossier predicted. At 1024x768 the tree is collapsed and only the palette applies. |
| T14 find gaps (weekly) | 1440x900 | not supported | 2.55 | | | One click on "1 UNKNOWN" in the status bar |
| T05 rename with ripple (weekly) | 1440x900 | not supported | 6.47 | | | Includes destination and lens clicks |

Weekly total over T03, T06, T08 and T04 (form versus drag), frequencies 5, 5, 5, 1, unrounded: current 122.585 s, proposed 121.468 s, -0.91 % at 1440x900 (page-coordinate current value 123.772 s, -1.86 %); 124.438 versus 120.379 s, -3.26 % at 1024x768 (page-coordinate 125.283 s, -3.91 %). Inside the band by a factor of about 5 to 23 (21 % divided by each change: 23 at 1440 corrected, 11 at 1440 page-coordinate, 6 at 1024 corrected, 5 at 1024 page-coordinate). Sensitivity (T03 current versus proposed, T08 current versus proposed): profile B 4.27 versus 3.34 s and 12.52 versus 12.73 s; profile C (Card's constants, UNVERIFIED) 5.87 versus 4.23 s and 16.11 versus 16.68 s; profile D (flat 1.1 s pointing) 5.40 versus 4.00 s and 15.30 versus 15.20 s. No ordering flips between profiles. Two differences exceed the 21 % size of the band, T03 (-23 %) and the non-drag T04 path (+39 %); in both cases the plus or minus 21 % intervals of the two flows still overlap, so neither is evidence.

Decision flips inside the band? For adopting the layout on time grounds: not supported, because the aggregate change is 1 % against a band of 21 %. The decision does not rest on time. What the model does show: the layout does not cost time for the daily tasks, and the accessible drag alternative costs about 1.5 s per use.

Arithmetic for T03 (1440x900, page coordinates, upper bound):

| Current | s | Proposed | s |
|---|---|---|---|
| M plan | 1.350 | M plan | 1.350 |
| P __pointer to tab-impact (D 297, W 50, ID 2.79) | 0.733 | P __pointer to op-1 (D 318, W 40, ID 3.16) | 0.781 |
| B | 0.100 | B | 0.100 |
| K page-down | 0.200 | R local selection | 0.100 |
| P tab-impact to summary-2 (D 1074, W 41, ID 4.77) | 0.989 | M read ripple | 1.350 |
| B | 0.100 | | |
| R local disclosure | 0.100 | | |
| M read closure JSON | 1.350 | | |
| Total | 4.922 | Total | 3.681 |

The scroll-corrected current total is 4.767 s. After the page-down (scroll 787.5 px, ASSUMPTION 0.875 of 900) the pointer is still where the tab click left it, at (452, 577) on screen; the closure-details button, whose page centre is (842.5, 1577.5), is now at screen y = 790. The second act is D = 445 px, W = 41, ID 3.57, MT 0.834 s, against D = 1074 px and MT 0.989 s in page coordinates (total 4.923 s). An earlier draft gave 287 px for this act; that figure was wrong. The difference between the flows is one tab click, one scroll and a longer second reach, about 1.1 s (scroll-corrected).

The same re-basing for the other current flows at 1440x900: T08, first act after the page-down, from the Evidence tab to the question field q-authority: pointer (682, 577), target page centre (432, 1123.5), screen y 336, D = 347 px, W = 47, MT 0.769 s against D = 601 px and 0.862 s in page coordinates (13.217 s against 13.310 s in total). T04, first act to the state-view select: pointer (452, 577), target page centre (617, 892), screen y 104.5, D = 500 px, W = 44, MT 0.842 s against D = 356 px and 0.784 s in page coordinates (4.853 s against 4.795 s). In T04 the scroll carries the target past the pointer, so the corrected time is the longer one: the scroll-corrected value is not a lower bound, and an earlier draft that called it one was wrong. At 1024x768 T08 takes two page-downs (1344 px), which scrolls the first question field 241 px above the top of the viewport; the model has no scroll-up operator, so that flow is an approximation (13.612 s corrected, 13.564 s page-coordinate). All differences discussed here are far inside the 21 % band.

Arithmetic for T08 (1440x900): current 22 operations, 13.31 s; proposed 22 operations, 14.03 s. Terms identical in both flows: two M 2.70, typing and tabs 4.80 (1.8 + 0.2 + 0.4 + 0.2 + 2.2), two H 0.80, two kernel responses 0.80, five B 0.50, total 9.60 s. Current adds five pointing acts (0.613 + 0.862 + 0.741 + 0.598 + 0.696 = 3.51 s) and one page-down (0.20 s). Proposed adds five pointing acts (0.933 + 0.935 + 0.873 + 0.861 + 0.728 = 4.33 s) and the dialog open (0.10 s). The 0.72 s difference is longer reaches: the launcher is 534 px from the pointer and the dialog inputs are 32 px tall against 47 to 50 px in the baseline. The baseline's acknowledgement checkbox is 18 px wide (ID 2.86 for D 112), a target below the WCAG floor that the proposal removes.

### 6.3 Option comparison by geometry (PREDICTION)

Rail at the bottom (VS Code Panel style) versus the inspector at the right (chosen), same content, same flows:

| Quantity | Inspector at right (chosen) | Panel at bottom | Note |
|---|---|---|---|
| T03 time | 3.681 s | 3.696 s | difference 0.015 s; reproducible: in option C the operation row spans main at full width, x 308, y 116, 1120 x 40 (centre 868, 136), so the pointing act from the pointer rest position is D = 348 px, W = 40, MT 0.796 s |
| T08 time | 14.030 s | not reproducible, withdrawn | the first draft gave 14.112 s, but the option C geometry of the ripple panel, the decision entry and the dialog was not recorded and cannot be reconstructed from one number; nothing in the decision rests on it |
| Diagram canvas area | 752 x 756 = 568,512 px2 | 1144 x 496 = 567,424 px2 | equal within 1 % |
| Canvas aspect (w/h) | 0.99 | 2.31 | |

Pointing cost cannot separate the two (0.015 s on T03, inside the band). Options B and C have the same regions and the same status bar, so both put the daily tasks and the six status counts in the first viewport; the first-viewport argument does not distinguish them. The choice rests on precedent (both exist) and on reading order: an inspector beside the selected row keeps the ripple next to what it explains. It is a revisit item in the ADR.

### 6.4 Placement of "Review decision" (PREDICTION)

Movement time from the selected operation (op-1, centre (672, 136) in `proposed-review`) and from the pointer rest position (`__pointer`, (720.5, 450.5)) to five candidate slots, each a button 28 px tall (W = 28). Only the chosen slot is in the layout file; the other centres were not recorded in the first draft and are reconstructed here (they reproduce the first-draft times to within 0.001 s):

| Slot | Centre (x, y), 1440x900 | MT from op-1 | MT from pointer |
|---|---|---|---|
| Inspector after the UNKNOWN group (chosen; `open-decision`) | (1244, 558) | 0.984 s | 0.933 s |
| Inspector top | (1244, 62) | 0.946 s | 0.968 s |
| Inspector bottom | (1244, 842) | 1.028 s | 0.969 s |
| Main, bottom right | (928, 842) | 0.994 s | 0.899 s |
| Main header right (the navigation lane's "Decide" slot) | (956, 62) | 0.828 s | 0.904 s |

The spread is 0.20 s at most and inside the band. The slot is chosen for reading order: the button follows the evidence that the decision depends on. Fitts and KLM favour the header slot by 0.16 s from op-1 and the bottom-right slot by 0.03 s from the pointer rest position; this is the deliberate deviation of D8 (P2, LAW section 3): we optimise time to evidence, not time to approve.

### 6.5 Option A': the baseline with the hero removed (PREDICTION, DESIGN COUNT)

Question raised by the audit: how much of the gain comes from removing the hero, and how much from the five regions? A' is the smallest change that fixes the measured position problem on the existing single page. It is modelled from the MEASURED current geometry by these rules (script `aprime.py`, not shipped; rules complete enough to redo by hand):

* Delete the hero group: eyebrow, the two-line heading, the paragraph, the boundary bar and its two text runs (24 chrome words).
* Header 48 px instead of 82. A sticky status strip of 28 px directly below it carries the six status counts (ids, widths, words and importance copied from `proposed-review`; no attention item, no stage chip).
* The case heading starts 16 px below the strip. Every element of the main column from the case heading down moves up by 352 px at 1440x900 (309 px at 1024x768). The left case list, the tabs, the panels and the page scroll stay as they are; nothing else changes, and content is the baseline's (JSON dump for closure, no tree, no inspector).

Layout vectors are in 6.1 (rows marked A'). Times use the same flows as the current UI (Appendix B), scroll-corrected, Cockburn profile:

| Task | Viewport | A (baseline) s | A' s | B (chosen) s | B against A' |
|---|---|---|---|---|---|
| T03 ripple | 1440x900 | 4.767 | 4.794 | 3.681 | -23 % |
| T03 | 1024x768 | 4.853 | 4.713 | 3.674 | -22 % |
| T06 evidence | 1440x900 | 5.563 | 5.443 | 5.540 | +2 % |
| T06 | 1024x768 | 5.481 | 5.288 | 5.543 | +5 % |
| T08 approve and apply | 1440x900 | 13.217 | 13.297 | 14.030 | +6 % |
| T08 | 1024x768 | 13.612 | 13.231 | 13.817 | +4 % |
| T04 edit (form or drag) | 1440x900 | 4.853 | 4.622 | 5.212 | +13 % |
| T04 | 1024x768 | 4.707 | 4.565 | 5.208 | +14 % |
| Weekly total (5, 5, 5, 1) | 1440x900 | 122.585 | 122.287 | 121.468 | -0.7 % |
| Weekly total | 1024x768 | 124.438 | 120.725 | 120.379 | -0.3 % |

Readings, all PREDICTION and all inside the plus or minus 21 % band:

* At 1024x768 removing the hero recovers about 90 % of B's modelled gain over the baseline (A' -3.0 %, B -3.3 %); at 1440x900 A' recovers about a quarter (-0.2 % against -0.9 %). The regions add little to the modelled time.
* B is faster on T03 because the ripple is a selection with counts beside the row, while the baseline's closure is a disclosure that opens a JSON dump. That is a content difference introduced by the review lane, not an effect of the regions, so the -23 % cannot be credited to the layout.
* A' still needs a page scroll for T03 (closure details at page y 1205 of 900) and T08 (Approve and Apply at 1054 of 900 at 1440x900): scroll-free 0.600 and 0.833 on the Impact and Evidence tabs at 1440, 0.200 and 0.750 at 1024. The status strip gives the UNKNOWN count at zero operators on every tab, as B does.
* A' has no model tree (T05, T09 and T14 are unsupported in the baseline and stay so), no inspector beside a selection and no fixed 720 x 520 canvas; adding them means adding regions or scrolling. Those needs come from the language, canvas and review lanes; they are requirements stated there, not results of this file.
* B stays the choice because of those requirements and because the study can test them, not because the numbers favour it. If the study shows no difference between A' and B on the first-sight and error measures for T06 and T08, the regions are justified by the tree and canvas lanes alone, and the decision should be revisited.

## 7. Overlays, focus and motion

* Overlays are centred on the main region so that the sidebar and inspector stay readable behind the scrim and no overlay covers the inspector's UNKNOWN group. A dimming scrim is allowed; blur and translucent text backgrounds are not (rubric).
* Modal dialogs and the palette move focus in and return it on close. WCAG 2.4.11 (Level AA) says sticky headers, footers and non-modal dialogs must not entirely hide a focused component and lists making content modal and scroll padding as remedies (S2). The top bar and status bar are outside every scroll container, so they never overlap scrolled content; pane scroll containers use `scroll-padding` equal to their sticky headers.
* Enter and exit of the palette and drawers follow the motion lane's 150 ms rule (`motion-and-performance.md`); reduced motion removes translation. Pane resize is direct manipulation and must stay inside 16.7 ms per frame (motion lane budget); a grid-template change is a layout operation, so the prototype must measure it (section 10).

## 8. Anti-slop and accessibility, layout scope only

| Item | Result | Basis |
|---|---|---|
| Containers per viewport (target at most about 12) | Pass only if status chips have no border or fill: panels 0 to 2; panels plus chips 3 to 30 (review 30, fails if chips are boxed) | DESIGN COUNT, 6.1; chip styling belongs to the token and colour lanes (UNKNOWN) |
| Nesting depth (at most 3) | 0 to 1 | DESIGN COUNT |
| Chrome words (the budget as applied here) | 60 to 90 | DESIGN COUNT |
| Total visible words (the brief's "at most about 120 visible words") | Fails on most screens: 120 to 159 at 1440x900, 98 to 137 at 1024x768 (baseline 126 to 171, MEASURED); recorded deviation | ESTIMATE, 6.1 |
| Prose blocks of 8 or more words (at most about 30 words in total) | 0, except 9 in the palette's "Ask AI" row | DESIGN COUNT |
| Eyebrow labels (at most 1) | 0 | by construction: the layout has none |
| Font sizes, type families, colour, gradients, elevation | UNKNOWN here; decided by the type, token and colour aspects. The layout asks for at most 6 sizes and one overlay elevation. | |
| Target size at least 24 x 24 | 0 targets below 24 in 12 files (DESIGN COUNT, spacing exception not applied). The seam hit area (8 px) relies on the spacing exception: UNKNOWN until tested. | |
| Contrast, CVD | UNKNOWN: no colour values exist yet | |
| Dragging has a non-dragging path | Yes: diagram handle has the inspector select plus Apply; tree move has "Move to" (language lane); seams have arrow keys | |

## 9. Interfaces with other aspects

Published assumptions from other lanes as of 2026-09-29, read in their files, and what this decision does with each. The integrator should reconcile these; the layout JSON of those lanes should use `region-*` ids for region panels so that the containers count is comparable.

| Lane and source | Their assumption | This decision | Consequence |
|---|---|---|---|
| AI, `ai-interaction.md` A1 | Context drawer at least 360 wide at 1440x900; status footer can hold "2 need you" | Inspector 392; status bar item "n need you, n running" | Met. The AI inbox is a lens in main; the composer control is "Ask AI to propose" in the inspector. |
| Canvas, `canvas-uml-interaction.md` I-L1 and Appendix B.2 | Canvas pane at least 720 x 520 at 1440x900; toolbar inside its top edge; inspector docked at the right; example canvas at x 320, y 120, w 752, h 520 | Main 752; canvas surface 752 x 756 below a 36 px lens row and 36 px toolbar; inspector at the right | Met. Their absolute coordinates move: canvas x 296, y 112, w 752, h 760. |
| Language, `language-and-ddd-tree.md` D1 and shell row | Top bar 48, left rail 400, status bar 32, inspector fills the rest | Top bar 40, sidebar 296 (user limit 480), status bar 28, inspector 392 | Conflict on three numbers. The tree fits at 296 by the anatomy in 3.2 (286 needed); 400 is available by resizing. Their status-bar counts that filter on click are adopted as D5. |
| Review, `evidence-and-change-review.md` A1, O5 | 40 px top bar, 48 px navigation rail, tree not on the review screen; evidence rail 360 at x 1080; three columns need about 1232 px after the rail | Persistent sidebar and destinations in the top bar; inspector 392 at x 1048 | Conflict. Main plus inspector is 1144 px at 1440, less than 1232: the review lane's three columns become two, or the sidebar is collapsed with Ctrl+B (main plus inspector then 1400 px). Open item O1. |
| Navigation, `design/layouts/nav-proposed.json` | Top bar 40; sidebar 272; inspector 360; status bar 28 with six status buttons, attention and stage; destinations Changes, Model, Evidence; "Decide" in a main header slot | Top bar 40; sidebar 296; inspector 392; status bar 28; same destinations and status order (UNKNOWN first); "Review decision" in the inspector (D8) | Close. Differences: +24 px sidebar, +32 px inspector, decision entry position. Their panels use ids without the `region-` prefix and would count as containers. |
| Content and onboarding, `content-and-onboarding.md` D2, A9 | Shell at most 20 words; proposed element ids `home.open-sample`, `review.select-meaning`, `review.run-verification`, `term.<id>` | Shell 24 words (6.1); `run-verify` in the Evidence lens; `tree-item-<slug>` | Mapped: `review.run-verification` to `run-verify`, `term.<id>` to `tree-item-<slug>`. HOME and first-run are not laid out here: open item O2. |
| Motion, `motion-and-performance.md` | Cancel and Abandon wait at least 24 x 24; 16.7 ms frame budget; 150 ms enter and exit | Job controls live in the jobs list opened from the status bar attention item, with 28 px targets | Met on geometry; resize cost to be measured. |
| Typography, HCI-ADR-0060 | UI text 14 px, caption 12, prose 16; row heights 28 and 24 handed to the layout aspect; the chosen sans is about 6 % wider than Segoe UI at equal size (their MEASURED figure) | Rows 28 and 24 adopted. My anatomy assumed 6.5 px per character; at 14 px and about 7.0 px per character a 12-character name needs 84 px, so the sidebar minimum becomes about 292, rounded 296 | Unresolved, and the sidebar minimum is marked PROVISIONAL in D3 and the ADR. If the built row needs it, `MIN_SIDEBAR` becomes 296: the 296 column of the width table in 3.2 gives every derived width (each moves by 8 px or less) and the L breakpoint becomes 1216. The inspector cap of 560 then holds about 76 characters instead of 80. The published layout files use 288 and would be regenerated. |
| Navigation, HCI-ADR-0057 | Frame 40 / 272 / 360 / 28; deep links in the URL hash; the inspector hides below 1280 px; a primary action slot at the top right of main | Frame as in D1 to D3; inspector kept down to 960 px and then a drawer; "Run verification" is the first control in main, "Review decision" is in the inspector | Two conflicts. (1) The hash carries the session token in the baseline (`app.js` reads `location.hash`, stores it in `sessionStorage` and clears it with `history.replaceState`), so a route cannot use the hash until the token is consumed; use the query string. (2) The inspector at 1024x768 is 392 wide here; hiding it below 1280 would take the ripple and UNKNOWN group off a 1024 px screen. |
| Tokens and colour | not yet published | 4 px grid; at most six font sizes; one overlay elevation; status words reserved in every status element | Contrast, hue and elevation values are theirs; the layout has no colour dependence. |

## 10. Validation plan

### 10.1 Prototype measurements (fixed before running)

One Chromium at a time; 1440x900, 1280x720 and 1024x768; the excursion fixture; default and Compact density.

| Check | Pass criterion |
|---|---|
| Scoring function on the built page (DOM script) | chrome words at most 120 on each of the six screens and within plus 10 % of the DESIGN COUNT; containers at most 12; depth at most 3; font sizes at most 6 |
| Page scroll | `document.scrollingElement.scrollHeight` equals the viewport height on all six screens; every element with importance 0.5 or more inside the viewport |
| Region widths | equal to section 3.2 within 4 px at 1600, 1440, 1368, 1280, 1208, 1024; between every pair of adjacent widths W and W + 1 no pane changes by more than 4 px, tested at every width from 1208 to 1600 and from 960 to 1207 (not only at sample points; the rule itself meets this at every width, 3.2 R3); no pane changes width when the lens or destination changes |
| Targets | no interactive target under 24 x 24 except the seams; seam spacing exception verified with a 24 px circle test |
| Reflow | no two-dimensional page scroll at 320 CSS px except the diagram and tables; text at 200 % without loss; text spacing overrides without loss of the UNKNOWN counts |
| Seam drag | p95 frame interval at most 16.7 ms and no long animation frame while dragging over 200 frames |
| CSP smoke test | pane widths applied with `setProperty` under the shipped CSP; if it fails, the attribute fallback passes |
| Keyboard | every seam moves by keyboard; F6 visits all five regions; Ctrl+B toggles the sidebar; focus never hidden under the top or status bar |

### 10.2 User study

Reference: the study protocol owned by the study lane in `docs/hci/design/` (not yet published when this was written). Layout-specific arms, to be merged into it:

* Design: within-subject, three arms: A the baseline Studio, A' the baseline with the hero removed and a sticky status strip (6.5, built as a variant of the current page), B the proposed shell; excursion tasks T03, T06, T08, T04; order counterbalanced (Latin square over three arms); 12 or more participants (the floor the dossiers use; formative rounds of about 5 find problems but do not estimate prevalence, LAW 2.10); a keyboard-only cohort.
* Layout measures: page scrolls per task; time to first sight of the UNKNOWN count and first-click accuracy on "where is the number of UNKNOWN items" (status bar versus baseline and A'); pointing errors; UNKNOWN misread as PASS (target zero); SEQ per task; SUS and Raw TLX with intervals; whether the absence of an agent panel is missed (open question after each session).
* Pre-registered stop criteria: stop and redesign if any participant approves with an unread UNKNOWN on a seeded item; if median time to first sight of UNKNOWN is not lower than the baseline's; if more than 2 of 12 participants cannot find the UNKNOWN count within 10 s; if the accessible drag alternative (T04 non-drag) has a higher error rate than the baseline form.
* Contrasts fixed in advance: A' versus A estimates the effect of position (no hero, persistent counts); B versus A' estimates what the five regions add on top of it. A study without the A' arm cannot attribute an effect of B to the regions.
* Status: none run. No user-benefit claim is made.

### 10.3 Open items and UNVERIFIED

| # | Item |
|---|---|
| O1 | The review lane's three-column review at 1232 px does not fit beside a persistent sidebar at 1440. Needs the review lane and the integrator. |
| O2 | HOME and first-run layouts are not in the five screens. |
| O3 | Container-query support was not stated on the MDN page I opened; UNVERIFIED. |
| O4 | Whether one page-down scrolls 0.875 of the viewport in Chrome is UNVERIFIED (ASSUMPTION). |
| O5 | Splitter as a target under WCAG 2.5.8's spacing exception is my reading, not tested. |
| O6 | Figma UI3 layout page returned 404; no claim about Figma's panel layout is made. tldraw's docs gave no layout statement. The OpenAI Codex app layout is UNVERIFIED: the page cited in the first draft (S13) describes the ChatGPT desktop app and does not list a project sidebar, review pane or terminal, and the Codex documentation URLs redirect to it; nothing is built on it. |
| O9 | Option A' is modelled from the baseline geometry by rules, not built. Its figures (6.1, 6.5) are DESIGN COUNT and PREDICTION. |
| O7 | OSS splitters and layout libraries were not evaluated this session (Split.js, allotment, others): UNVERIFIED. ADR-0016 requires that check, and a REGISTER row, before the custom module is written. |
| O8 | The smaller-side rule for W is offered as a possibility, untested, in MacKenzie 1992 (S10); the paper refers to MacKenzie and Buxton (CHI '92) for a test of two-dimensional models, which was not opened. The rule stays an ASSUMPTION, checked by profile B of 2.3. |
| O10 | 1280x720 layout files are not published (not in this lane's file list); the numbers in 3.3 come from the same generator. The integrator should add them or record 1280x720 as unspecified. |
| O11 | Option C's T08 time is withdrawn (6.3): its geometry was not recorded. |
| O12 | Reconciliation of the shell with HCI-ADR-0057, the language lane and the review lane (section 9) is a precondition for accepting HCI-ADR-0058. Owner: the integrator for `lane/ux-research`, with the three lane authors. |
| O13 | The sidebar minimum (288 or 296) waits on a measurement of a built tree row in the typography lane's chosen font. |

## 11. Sources

All opened on 2026-09-29 through WebFetch (a small model summarises the page; numbers below were read from the summary unless marked PDF).

| Id | URL | Used for |
|---|---|---|
| S1 | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | SC 2.5.8: 24 x 24 CSS px, five exceptions including spacing |
| S2 | https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html | SC 2.4.11 Level AA; sticky headers and footers; modal remedy |
| S3 | https://code.visualstudio.com/api/ux-guidelines/overview | Named surfaces: activity bar, primary and secondary sidebar, editor, panel, status bar |
| S4 | https://code.visualstudio.com/docs/getstarted/userinterface | Panel can be moved; side bar toggle Ctrl+B; secondary side bar |
| S5 | https://www.w3.org/WAI/ARIA/apg/patterns/windowsplitter/ | Separator role, valuenow, valuemin, valuemax, controls, required accessible name (aria-labelledby or aria-label, matching the primary pane), arrow keys, Enter, optional Home and End, optional F6 |
| S6 | https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf | PDF read locally: pointing time 0.37 + 0.13 ID, R2 = 0.93; expert decision 0.24 + 0.08 log2(n), R2 = 0.98; novice search 0.08 n + 0.3; 8 participants |
| S7 | https://storybook.js.org/docs/get-started/browse-stories | Sidebar with search, canvas, addons panel below, F6 and Shift+F6 between regions |
| S8 | https://blog.jetbrains.com/blog/2024/07/08/the-new-ui-becomes-the-default-in-2024-2/ | A compact mode was added after user feedback (vendor) |
| S9 | https://www.nngroup.com/articles/scrolling-and-attention/ | 2010: 80 % of viewing time above the fold; 2018 (120 participants, 130,000 fixations, 1920x1080): 57 % above the fold, 74 % in the first two screenfuls |
| S10 | https://www.yorku.ca/mack/hci1992.html | MacKenzie (1992), Fitts' law as a research and design tool in HCI: Shannon form MT = a + b log2(A/W + 1); the original form can be negative; for rectangular 2D targets, "perhaps the smaller of W or H" is offered as a possibility, not tested there (page saved and searched 2026-09-29) |
| S11 | https://en.wikipedia.org/wiki/Keystroke-level_model | Operator times K, P, H, M, D and RMS error 21 % (secondary) |
| S12 | https://cursor.com/blog/cursor-3 | Agents Window: agents in a sidebar, diffs view |
| S13 | https://learn.chatgpt.com/docs/app | UNVERIFIED and not used: the first draft cited it for a Codex app layout; the page describes the ChatGPT desktop app and lists no project sidebar, review pane or terminal (O6) |
| S14 | https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html | SC 1.4.8 (AAA): line width at most 80 characters |
| S15 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/style-src | Inline style attributes and cssText blocked; `element.style.property` not blocked |
| S16 | https://www.w3.org/WAI/WCAG22/Understanding/reflow.html | SC 1.4.10: 320 CSS px, equal to 400 % at 1280; two-dimensional content exempt |
| S17 | https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html | SC 1.4.4: 200 % without loss |
| S18 | https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_containment/Container_queries | Container query syntax; support not stated on the page |
| S19 | https://www.nngroup.com/articles/fitts-law/ | Screen edges act as walls for a mouse pointer (not for touch); controls used in sequence should sit close together, for example Submit next to the last form field |
| S20 | https://www.nngroup.com/articles/progressive-disclosure/ | 2006: beyond two disclosure levels typically lowers usability |
| S21 | https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html | SC 2.5.7 Level AA: single-pointer alternative to dragging |
| S22 | https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html | SC 1.4.12 values |
| S23 | https://linear.app/now/how-we-redesigned-the-linear-ui | Sidebar, tabs, headers and panels adjusted to reduce noise, alignment and density; no statement on resizable sidebars |
| S24 | https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes | Width classes at 600, 840, 1200, 1600 dp (a comparison only; my breakpoints are derived from minima) |
| S25 | https://storybook.js.org/docs/writing-tests/integrations/vitest-addon | Testing widget: totals of tests run, passed and failed; pressing the failure number filters the sidebar to failing stories (opened 2026-09-29; the widget's position at the foot of the sidebar is from S7) |

Repo sources: `src/eija_studio/resources/web/*` (baseline), `src/eija_studio/interfaces/http.py` (CSP), `docs/adr/0000-poc-decision-log.md` (ADR-003, -008, -013), `docs/adr/0018-formal-vv-portfolio.md`, `AGENTS.md`, `README.md`.

## Appendix A. Layout files

| File stem | UI | Viewport | Elements |
|---|---|---|---|
| `current-start`, `current-change`, `current-impact`, `current-try`, `current-evidence` | current, MEASURED | 1440x900 | 33, 73, 98, 52, 64 |
| the same with suffix `-1024` | current, MEASURED | 1024x768 | 33, 73, 98, 52, 64 |
| `proposed-review`, `-canvas`, `-language`, `-evidence`, `-palette`, `-decision` | proposed, specification | 1440x900 | 103, 78, 87, 90, 82, 87 |
| the same with suffix `-1024` | proposed, specification | 1024x768 | 85, 60, 69, 72, 64, 69 |
| 1280x720 | proposed, specification | 1280x720 | not published (3.3, O10) |

The two `decision` files carry one more element than in the first draft: the virtual anchor `__open-decision`, the pointer position after pressing "Review decision" (the centre of `open-decision` in the review file: (1244, 558) at 1440x900 and (828, 558) at 1024x768), so the T08 pointing act from it to `decision-q1` can be recomputed from the JSON alone. Status bar counts in all twelve proposed files read 1 UNKNOWN, 0 FAIL, 0 CONFLICT, 0 STALE, 5 NOT_RUN, 3 PASS: nine claims, the same nine rows the Evidence screen lists (3 PASS, 5 NOT_RUN, 1 UNKNOWN). The first draft said 6 NOT_RUN and did not reconcile.

Each file has `screen` equal to the stem without prefix and suffix (`canvas` is the Model destination with the States lens; `language` is Model with the Language lens). The two viewports of one screen share `ui` and `screen`; the pair key is (`ui`, `screen`, `viewport.w`). Task flows reference the stem, for example `"layout": "proposed-review-1024"`.

## Appendix B. Flows used in 6.2 (operation lists, ids from the layout files)

| Task | Current | Proposed |
|---|---|---|
| T03 | M; P __pointer to tab-impact (current-change); B; K page-down; P tab-impact to summary-2 (current-impact); B; R 100; M | M; P __pointer to op-1 (proposed-review); B; R 100; M |
| T06 | M; P __pointer to tab-evidence; B; P tab-evidence to verify (current-evidence); B; R 1000; K page-down; M | M; P __pointer to tab-evidence (proposed-review); B; P tab-evidence to run-verify (proposed-evidence); B; R 1000; M |
| T08 | M; P __pointer to tab-evidence; B; K page-down; M; P tab-evidence to q-authority; B; H; T 9; K Tab; T 2; K Tab; T 11; H; P q-reject_entry to acknowledge; B; P acknowledge to approve; B; R 400; P approve to apply; B; R 400 | M; P __pointer to open-decision (proposed-review); B; R 100; M; P __open-decision to decision-q1 (proposed-decision); B; H; T 9; K Tab; T 2; K Tab; T 11; H; P decision-q3 to decision-ack; B; P decision-ack to decision-approve; B; R 400; P decision-approve to decision-apply; B; R 400 |
| T04 | M; P __pointer to tab-impact; B; K page-down; P tab-impact to diagram-source (current-impact); B; P diagram-source to diagram-source; B; P diagram-source to edit-state; B; R 300 | Drag: M; P __pointer to tab-model; B; P tab-model to lens-states (proposed-canvas); B; P lens-states to handle-reject-source; B press; P handle-reject-source to node-submitted; B release; R 300. Non-drag: the same to the lens, then P lens-states to edge-reject-label; B; P edge-reject-label to insp-source; B; P insp-source to insp-source; B; P insp-source to insp-source-apply; B; R 300 |
| T09 | not applicable | Palette: M; K ctrl+k; T 3; K Enter; R 100. Tree: M; P __pointer to tree-item-reject; B; R 100 |
| T14 | not supported | M; P __pointer to st-unknown; B; R 100 |
| T05 | not supported | M; P __pointer to tab-model; B; P tab-model to lens-language (proposed-language); B; P lens-language to term-rename; B; H; T 8; K Enter; R 100 |

The task-flow files of the other lanes use their own ids; the integrator maps them to these.

Option A' (6.5) runs the Current column unchanged on the A' layouts (ids as in the current files; the number of page-downs is recomputed from the shifted geometry: one for T03 and T08 at both viewports, none for T04 and T06).

## Appendix C. Reproduction data

### C.1 Unrounded totals (KLM seconds, Cockburn profile, W = smaller side)

Page = pointing acts in page coordinates; corrected = the first act after a scroll re-based (section 5). Columns A' are option A' (6.5). B has no scroll. The two proposed T04 paths at 1440x900 / 1024x768: drag 5.212 / 5.208 s, non-drag 6.735 / 6.688 s (flows in Appendix B).

| Task | Viewport | A page | A corrected | A' page | A' corrected | B |
|---|---|---|---|---|---|---|
| T03 | 1440x900 | 4.923 | 4.767 | 4.950 | 4.794 | 3.681 |
| T06 | 1440x900 | 5.563 | 5.563 | 5.443 | 5.443 | 5.540 |
| T08 | 1440x900 | 13.310 | 13.217 | 13.389 | 13.297 | 14.030 |
| T04 | 1440x900 | 4.795 | 4.853 | 4.622 | 4.622 | 5.212 |
| Weekly (5, 5, 5, 1) | 1440x900 | 123.772 | 122.585 | 123.532 | 122.287 | 121.468 |
| T03 | 1024x768 | 5.059 | 4.853 | 4.865 | 4.713 | 3.674 |
| T06 | 1024x768 | 5.481 | 5.481 | 5.288 | 5.288 | 5.543 |
| T08 | 1024x768 | 13.564 | 13.612 | 13.370 | 13.231 | 13.817 |
| T04 | 1024x768 | 4.759 | 4.707 | 4.565 | 4.565 | 5.208 |
| Weekly (5, 5, 5, 1) | 1024x768 | 125.283 | 124.438 | 122.182 | 120.725 | 120.379 |

Changes: B against A corrected, -0.91 % (1440) and -3.26 % (1024); B against A page, -1.86 % and -3.91 %. Computing from the rounded 124.4 and 120.4 gives -3.2 %; the unrounded value is -3.26 %, which rounds to -3.3 %.

### C.2 Allocation and sensitivity script

Self-contained; it reproduces the widths in 3.2, checks the 4 px stability rule at every width in mode L, and reproduces the P10 to P90 ranges (Python 3.12 `random`, seed 20260929, 10,000 draws). Run it with no argument for the 288 px sidebar minimum and with `296` for the provisional alternative. The widths use the revised rounding of R3; the P10 to P90 ranges are the same as with the first-draft rounding.

```python
import random, sys
MIN_SB = int(sys.argv[1]) if len(sys.argv) > 1 else 288
F = {"daily": 5.0, "weekly": 1.0, "rare": 0.25}
# task: (frequency class, criticality c, attention shares TB, SB, MA, IN, ST)
T = {"T01": ("weekly", 2, (.10, 0, .70, .15, .05)), "T02": ("daily", 3, (.05, .15, .55, .25, 0)),
     "T03": ("daily", 3, (0, .10, .30, .60, 0)), "T04": ("weekly", 2, (.05, .05, .70, .20, 0)),
     "T05": ("weekly", 2, (.05, .60, .15, .20, 0)), "T06": ("daily", 3, (.05, .05, .55, .30, .05)),
     "T07": ("weekly", 3, (0, 0, .60, .35, .05)), "T08": ("daily", 3, (0, 0, .30, .70, 0)),
     "T09": ("daily", 1, (.80, 0, .20, 0, 0)), "T10": ("rare", 1, (0, .20, .60, .20, 0)),
     "T11": ("weekly", 2, (0, .30, .20, .50, 0)), "T12": ("weekly", 2, (0, .30, .60, .10, 0)),
     "T13": ("weekly", 1, (0, .10, .30, .10, .50)), "T14": ("weekly", 2, (.30, .50, .20, 0, 0))}
def shares(w, att):                      # demand share of sidebar, main, inspector
    D = [sum(w[k] * att[k][i] for k in T) for i in (1, 2, 3)]
    return [d / sum(D) for d in D]
def q4(x): return int(round(x / 4.0) * 4)
def widths(W, S):                        # R1 to R3 of section 3.2
    if W >= MIN_SB + 560 + 360:          # mode L
        mm = min(720, max(560, W - MIN_SB - 360)); sur = W - (MIN_SB + mm + 360)
        ds = q4(S[0] * sur); dsr = q4((S[0] + S[2]) * sur)   # round the sidebar step and the side-pane total once each
        a = min(MIN_SB + ds, 480); c = min(360 + dsr - ds, 560)
        return a, W - a - c, c
    sur = W - 960; c = q4(360 + sur * S[2] / (S[1] + S[2]))   # mode M: 40 px rail takes no surplus
    return 40, W - 40 - c, c
w0 = {k: F[f] * c for k, (f, c, a) in T.items()}; a0 = {k: v[2] for k, v in T.items()}
S0 = shares(w0, a0); print("base shares", [round(x, 3) for x in S0])
print("max pane change between W and W+1 in mode L:",
      max(max(abs(x - y) for x, y in zip(widths(W, S0), widths(W + 1, S0))) for W in range(MIN_SB + 920, 1600)))
random.seed(20260929); res = {W: [] for W in (1440, 1280, 1024)}
for _ in range(10000):
    w, att = {}, {}
    for k, (f, c, a) in T.items():
        w[k] = F[f] * 2 ** random.uniform(-1, 1) * min(3, max(1, c + random.choice((-1, 0, 1))))
        b = [x * random.uniform(0.5, 1.5) for x in a]; att[k] = [x / sum(b) for x in b]
    S = shares(w, att)
    for W in res: res[W].append(widths(W, S))
def q(xs, p): xs = sorted(xs); return xs[int(p * (len(xs) - 1))]
for W in (1600, 1440, 1368, 1280, MIN_SB + 920, 1024, 960):
    print(W, "base", widths(W, S0))
for W in res:
    print(W, [("P10", q([r[i] for r in res[W]], .1), "P90", q([r[i] for r in res[W]], .9)) for i in range(3)])
```

### C.3 Alignment function (`align_top6`, section 5 item 5)

Applied to the published JSON, this reproduces every `align_top6` value in 6.1, current and proposed.

```python
def align_top6(L):
    V = L["viewport"]
    def visible(e):  # box intersects the viewport, even partly
        return e["x"] < V["w"] and e["y"] < V["h"] and e["x"] + e["w"] > 0 and e["y"] + e["h"] > 0
    els = [e for e in L["elements"] if not e["id"].startswith("__") and visible(e)]
    regions = [e for e in els if e["id"].startswith("region-")]          # full boxes, not clipped
    members = [e for e in els if e["role"] not in ("panel", "canvas")]
    groups = {}
    for e in members:
        cx, cy = e["x"] + e["w"] / 2, e["y"] + e["h"] / 2
        inside = [r for r in regions if r["x"] <= cx < r["x"] + r["w"] and r["y"] <= cy < r["y"] + r["h"]]
        key = min(inside, key=lambda r: r["w"] * r["h"])["id"] if inside else "root"
        groups.setdefault(key, []).append(e["x"])
    on_top6 = 0
    for xs in groups.values():
        clusters = []
        for x in sorted(xs):                                               # chain clustering, gap <= 1 px
            if clusters and x - clusters[-1][-1] <= 1: clusters[-1].append(x)
            else: clusters.append([x])
        on_top6 += sum(sorted(map(len, clusters), reverse=True)[:6])
    return on_top6 / len(members)
```
