# Accessibility and inclusive design for EIJA Studio

Aspect `accessibility`. Lane `lane/ux-research`. Date 2026-09-29. Status: proposed, revision 2 after audit (option F, a native Outline as the primary diagram surface, replaces the tree focus layer; inset focus ring corrected to 3 px). Decision record: [HCI-ADR-0067](../../adr/0067-hci-accessibility.md). Task flows: [design/tasks/a11y-flows.json](../../../design/tasks/a11y-flows.json).

Scope: how the Studio meets WCAG 2.2 Level AA and stays usable by keyboard-only, screen-reader, low-vision, forced-colour and cognitively loaded users, while keeping the invariants (AI proposes, kernel checks, owner decides; UNKNOWN visible; generated views). Out of scope: glyph and colour values (token aspect), shell layout (layout aspect), diagram drawing (diagram aspect), the internals of the decision surface (decision aspect).

Labels. **MEASURED** = produced by a script I ran on 2026-09-29 (tool, browser and version named). **COUNT** = counted from a specified design or file. **PREDICTION** = model output with a band, never a user result. **UNVERIFIED** = not opened or not confirmed; nothing is built on it. No user study was run and no assistive technology (AT) was run: every statement about what a screen reader says is a design intent until the manual passes in section 12 are done.

## 0. Decisions first

| # | Decision | Strongest evidence | Confidence |
|---|---|---|---|
| D1 | Target WCAG 2.2 AA on every view, plus two AAA items as design constraints (2.4.12 focus not obscured, 2.4.13 focus appearance). **No conformance claim** until a WCAG-EM style audit exists; publish a statement that lists the SC that fail. | WCAG 2.2 is a Recommendation of 12 Dec 2024 (S1); sampled evaluations cannot support a full claim (S48); ADR-013 already disclaims certification | High for the target; the claim policy is ours |
| D2 | Native HTML first. Custom ARIA widgets only from a closed catalogue of APG patterns: tree, tabs, dialog, combobox, toolbar, menu button, disclosure. Each has one keyboard table in section 5. | APG says no ARIA is better than bad ARIA (S27); pages with ARIA averaged 59.1 detected errors against 42 without in WebAIM Million 2026, an association only (S54) | Medium |
| D3 | Keyboard model: skip links plus palette focus commands for regions; composites are one tab stop with roving tabindex; Escape and focus-return rules are uniform; shortcuts live in one registry; **no bare-key global shortcut is on by default** (deviation from P8: `/` is opt-in); no key, `accesskey` or palette command reaches approve or apply. | APG keyboard interface (S25); SC 2.1.4 (S10); ai-interaction layers L3, L4 | Medium |
| D4 | The diagram (option F): a visible, generated **Outline** is the primary keyboard, screen-reader and voice-control surface: a nested list in **model order** of native menu buttons, one per state and one per outgoing transition ("Reject: Submitted to Rejected"). The picture (HTML nodes over SVG edges) is pointer-operable and `aria-hidden`, with no focusable descendant; Outline focus is echoed on it. Outline, **Table** and picture come from one function; a parity test compares them. No `role=tree` on the diagram and no ARIA graphics roles. | The excursion graph is cyclic (Revise: Rejected to Draft, `policy.py`), so tree semantics would announce a hierarchy that does not exist; W3C complex images: a long description on the same page, structured (S33); MEASURED (M7): native Outline keeps list and button names in Chromium, 10 tab stops against 1 for the tree layer; MEASURED: Chromium 154 exposes `graphics-document` as one `img` (section 6.3) | Medium: no AT was run |
| D5 | Every drag has a single-pointer path (click the handle, then click the target) and a keyboard and voice path through the Outline menu ("Reconnect source...", "Move to...", "Position..." with X and Y fields), all through the same typed-request dispatcher. Abort before commit is always possible. Interactive targets are at least 24 by 24 CSS px, default density 32. | SC 2.5.7, 2.5.2, 2.5.8 (S2, S15, S3); PREDICTION: click path costs +0.2 s over the drag path | High for the requirement; the menu path uses the APG menu button (S30), no authored keys |
| D6 | Focus: outer ring 2 px at 2 px offset; **inset ring 3 px at offset exactly -3 px** inside any scroll container, row or tab strip (a 2 px flush inset ring falls 16 px2 short of the SC 2.4.13 area); ring colour at least 3:1 against every surface step; scroll-padding so sticky chrome never covers the focused item; sticky chrome becomes static below the compact breakpoint; a re-render never destroys the focused element. | MEASURED: an outer outline is clipped by an `overflow:auto` parent, the inset one is not; MEASURED: baseline focus falls to `body` after selecting a case; SC 2.4.11, 2.4.13 area rule 4h + 4w (S4, S5) | High for the arithmetic; measured on one browser |
| D7 | Two live regions exist at load: one `status` (polite) and one `alert` (assertive). Text comes only from kernel-generated templates. At most one polite message per user action, at most 20 words; the status bar is not a live region; a job announces its end once. | SC 4.1.3 (S11); MDN live-region caveats (S47); COUNT: longest live message 15 words | Medium |
| D8 | Status is a visible word plus a glyph. The glyph is `aria-hidden`; the word is set in the ink colour; hue lives on the glyph only. Contrast is computed against every surface step the item can sit on. `NOT_RUN` is displayed as "NOT RUN". | Computed: the provisional status text tokens fall from 4.5:1 to 3.66-3.86:1 on the third surface step (section 9.1); SC 1.4.1, 1.4.3, 1.4.11 (S12, S9) | High for the arithmetic; medium for the rule |
| D9 | Forced colours, zoom and text spacing: paint every SVG shape through system colours in a `forced-colors` block (MEASURED: hex `fill` and `stroke` are not overridden, `currentColor` is); three layout regimes at 1112 and 752 CSS px; every region reachable at 320 by 256 CSS px; node boxes are content-sized. The baseline fails here: its sidebar is `display:none` at 760 px or narrower. | MEASURED in Chrome 154 (section 3); SC 1.4.10, 1.4.12 (S8, S13) | High for the baseline facts; medium for the design |
| D10 | Cognitive accessibility follows the eight COGA objectives, made testable: one consistent Help entry (SC 3.2.6), no retyping of values already shown (SC 3.3.7), confirmation with the exact revision before approve and apply (SC 3.3.4), every refusal states the reason and the allowed alternative, status definitions on demand, no time limits, personalisation in one place. | COGA Working Group Note (S45); SC 3.2.6, 3.3.7, 3.3.4 (S6, S7, S21) | Medium: COGA is guidance, not a requirement |
| D11 | Testing: axe-core 4.13 with `target-size` enabled on every view, state, theme and viewport; scripted keyboard, focus, reflow, forced-colour and text-spacing tests in one Chromium; manual screen-reader passes on the combinations the WebAIM survey ranks highest; a cohort study. Automated results never stand alone. | MEASURED: axe found 1 of 5 baseline failures (B1 to B5) and scripts or a reading of `app.js` found the other 4 (section 3); GDS audit: 10 tools found 71% of 143 barriers together; best single tool 41% counting manual-inspection prompts, 37% on errors and warnings only (S43) | High for the layering |
| D12 | Deviations from `PRINCIPLES.md` are recorded, not silent: P8 canvas Tab per shape becomes Tab per Outline item in **model order** (the picture takes no focus); P8 `/` alias becomes opt-in. | SC 2.1.4; P3 (layout must not change reading order); MEASURED (M7): 10 tab stops for the excursion Outline | Medium |

What this does not claim: that the design is conformant, that any screen reader announces what is specified, or that keyboard users decide better. Section 12 is the test and the study.

## 1. Sources, method, limits

**Opened on 2026-09-29** (ids S1 to S56 in section 14; every URL was fetched this session; WebFetch returns a small-model summary, so quotations are limited to a few words). Research dossiers in `docs/hci/research/` are cited by section (`DGM§2.5`); I did not re-open pages they cite except where an S id says so.

**Run on this machine** (one headless Chrome 154.0.8037.58 at a time, Playwright for Python 1.58.0, axe-core 4.13.0 fetched from npm, all inside `.tmp/a11y/`, which is gitignored and not committed; the testing lane may promote the scripts to a nox session):

| Id | What | Output |
|---|---|---|
| M1 | Baseline Studio (the real `index.html`, `app.css`, `app.js` served with real Studio data, GET-only stub): axe on 5 views, keyboard tab order, focus after selecting a case, target sizes, reflow at 4 viewports, text-spacing override, forced-colour emulation, accessibility tree | `.tmp/a11y/baseline.json`, `tabs.json` |
| M2 | Spike: four candidate diagram semantics through axe and the Chromium accessibility tree; SVG versus HTML label under the SC 1.4.12 overrides | `.tmp/a11y/spike.json` |
| M3 | Probe: outline clipping in an `overflow:auto` parent (pixel test); SVG paint under `forced-colors: active` | `.tmp/a11y/probe2.json`, `baseline.json` |
| M4 | Computed WCAG 2.x contrast ratios for the baseline tokens and for the provisional tokens in `visual-design-foundations.md` | `.tmp/a11y/contrast.py` |
| M6 | V5 spike (audit follow-up): interactive parts inside the chosen V4 tree, three variants, through axe (all tags, `target-size` enabled) and the Chromium accessibility tree | `.tmp/a11y/spike_v5.json` |
| M7 | V6 spike (audit follow-up 2): option E (V4 tree, roving) against option F (native Outline in a `figure`, picture `aria-hidden`) on the real excursion candidate (5 states, 5 transitions from `policy.py`): axe (all tags, `target-size` enabled), Chromium accessibility tree, Tab count | `.tmp/a11y/spike_v6.json` |
| M5 | Geometry from `design/layouts/nav-current.json` and `nav-proposed.json`; KLM over `design/tasks/a11y-flows.json` | `.tmp/a11y/gen_flows.py` |

**Limits.**

- The forced-colour runs use Playwright's emulation (`forced_colors="active"`, options confirmed at S49), not a Windows contrast theme.
- Chromium's accessibility tree, read through `aria_snapshot`, is not what NVDA, JAWS or VoiceOver announce. NVDA 2026.2 documents Browse and Focus modes (S46); the JAWS and VoiceOver documentation was not opened, so their behaviour is UNVERIFIED.
- The proposed design is not built. Section 3 measures the baseline; sections 5 to 9 are specifications; section 10 and the flow file hold PREDICTIONS.
- WebAIM survey number 11 is closed with results not posted (S37); survey 10 (Dec 2023 to Jan 2024, 1,539 responses) is the newest with numbers (S36). It is self-selected.

## 2. Interfaces and assumptions

This aspect depends on others. Each row is a stated interface; if it fails, the fallback applies.

| Id | Assumption | Owner | Fallback if false |
|---|---|---|---|
| A1 | Shell regions as in `design/layouts/nav-proposed.json`: top bar 40 px, tree sidebar 272 px, main, inspector 360 px, status bar 28 px. Regimes: three columns from 1112 CSS px (272 + 360 + a 480 px main minimum, my assumption), two columns 752 to 1111 (inspector becomes a drawer), one column below 752. | Layout | Regimes recomputed; the requirement "every region reachable at 320 by 256" stands |
| A2 | Tokens provide: `--focus`, three surface steps per theme, status glyph hues, an ink colour for status words, and a `forced-colors` mapping. Dark and light ship together. | Token and colour | Section 9 gives the required pairs; the token lint fails until they exist |
| A3 | Status glyphs are distinguishable in monochrome and at 16 px; the word is always present (SYNTHESIS C2 vocabulary). | Status | Words carry the meaning alone |
| A4 | The palette registry accepts only classes read, propose and job (ai-interaction A6, L3). | Palette | The static test in section 12 runs against whatever registry exists |
| A5 | The diagram lane renders nodes as positioned HTML, edges as `aria-hidden` SVG, sizes nodes from content, stores position only, and can ask the kernel for a dry-run legality result. | Diagram | If it renders SVG-only, labels must wrap in code and D4 is re-decided with the section 6.3 numbers |
| A6 | The language tree follows the APG tree pattern and offers "Move to..." as a dialog listing only legal parents (language-flows T05-move-menu). | Language | Section 5.3 is applied to whatever tree exists |
| A7 | The decision surface is a modal dialog with the isolation contract of ai-interaction section 8; what is acknowledged and how is its own decision. | Decision | Section 5.6 constrains focus and semantics only |
| A8 | Reduced motion and job states follow `motion-and-performance.md` sections 5 and 9. | Motion | Motion never carries meaning in either case |
| A9 | The kernel returns refusals as data: a code, a reason and the allowed alternatives. Every string in a live region is built from such data (invariant I5). | Kernel | Announcements degrade to "Refused" plus the code |
| A10 | Setting `element.style.left/top` on nodes is allowed under `style-src 'self'` and SVG attributes work (SYNTHESIS C15, untested). | Security boundary | Position through classes on a coarse grid, or the diagram is rejected until the CSP smoke test passes |

## 3. What the baseline does today (MEASURED, Chrome 154, 2026-09-29)

Method: M1. Views: start, Change, Impact, Try, Evidence. Strengths worth keeping first.

| Strength | Evidence |
|---|---|
| `lang="en"`, a skip link, landmarks (`header`, `aside`, `nav` x2, `main`, `footer`), one `h1`, a polite `role="status"` region | `structure` in `baseline.json` |
| Native controls with labels; no gradients or shadows; `viewport` meta without `user-scalable=no` | `index.html`; one forced-colour screenshot judged usable by eye |
| Every interactive box except the two checkboxes is at least 41.4 px on its shorter side (the checkboxes are 18 by 18, see B12) | targets scan, 5 views |
| Text contrast passes: ink 13.6:1, muted 5.3-5.9:1, green 6.2-6.7:1 on their surfaces (computed) | M4 |

| # | Finding | Value | Which SC |
|---|---|---|---|
| B1 | axe 4.13.0 (tags wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa, best-practice; `target-size` enabled) reports **1 violation** in 5 views: `scrollable-region-focusable` on `pre#trace` (Try). Chrome 154 nevertheless reaches `pre#trace` by Tab (M3), so this is a browser-dependent issue, not a lockout in Chrome. Incomplete results: 0. | 37 to 42 rules pass per view | 2.1.1 |
| B2 | After selecting a case with Enter, `document.activeElement` is `body`: the case list is rebuilt with `replaceChildren`, which destroys focus. | focus lost | 2.4.3 |
| B3 | The four "tabs" are `button` elements inside a `nav`: 0 `role=tab`, 0 `aria-selected`, 0 `aria-current` for the selected tab or the selected case. Selection is visible only. | 0 of 4 tabs expose state | 4.1.2 |
| B4 | The sidebar is `display:none` at 760 CSS px or narrower. At 640 by 512 and at 320 by 256 CSS px (200% and 400% of a 1280 by 1024 window) the case list, New case and the provider check are unreachable: 0 visible case buttons. Arithmetic: a 1280 px window reaches 760 CSS px at 1.68 zoom, a 1440 px window at 1.89. | functionality lost at about 170-190% zoom | 1.4.10 |
| B5 | Control borders are pale: input border 1.74:1, secondary button border 1.68:1 against their backgrounds. A text input is identified by its border, so 3:1 applies. axe does not test this. | 1.7:1 against 3:1 | 1.4.11 |
| B6 | Focus ring is 3 px solid `#bf7400` at 3 px offset: 3.68:1 on white, 3.41 on the page, 3.28 on the sidebar, 3.16 on the pale panel. Passes 3:1, with little margin. | min 3.16:1 | 1.4.11, 2.4.7 |
| B7 | Raw JSON in three `pre` blocks (packet, impact, trace) is exposed as one long text run. | 3 blocks | 1.3.1 (judgement) |
| B8 | No `prefers-color-scheme`, `prefers-reduced-motion` or `forced-colors` rule (0 of each). Forced-colour emulation stays legible because controls are native; the active tab keeps a 3 px bottom border. | 0 rules | 1.4.1, 2.3.3 |
| B9 | Tab stops from document start: Change 16, Impact 12, Try 12, Evidence 16. The Impact edit control is the 9th stop, Apply the 10th; Approve is the 14th. | COUNT from a real run | 2.4.3 |
| B10 | Text-spacing override (line height 1.5, letter 0.12 em, word 0.16 em, paragraph 2 em) at 1440 and 1024: 0 clipped elements and no horizontal overflow (a crude test: it detects clipping, not overlap). | 0 | 1.4.12 |
| B11 | `apply` is a disabled button: it is absent from the tab order (MEASURED: the Evidence sequence goes from Approve to Export) and has no reason beside it in the accessibility tree; the reason is elsewhere on the page. A blocked control must stay reachable with its reason (section 5.5, 5.6). | 1 case | 3.3.1 (judgement) |
| B12 | The consent and acknowledge checkboxes are 18 by 18 px (1 in Change, 1 in Evidence). axe `target-size`, enabled, did not flag them. Whether the label counts as an equivalent target is not stated on the Understanding page (S3). | 2 elements | 2.5.8: UNKNOWN |

`aria-busy` is toggled on `body` during tasks; its effect on AT was not evaluated.

**Reading of B1 against the rest.** Of the five failures B1 to B5, axe found 1. B2 to B5 were found by scripts written for them or by reading `app.js` and the CSS. The GDS audit reached the same conclusion on a larger scale: 10 tools together found 71% of 143 deliberate failures and 29% were found by none (S43). axe's own README claims 57% of WCAG issues on average, a vendor number (S42).

## 4. Landmarks, headings, titles, focus destinations

| Element | Specification | Source |
|---|---|---|
| Landmarks | `banner` (top bar), `nav` "Destinations", `complementary` "Model tree", `main`, `complementary` "Inspector", `region` "Evidence status" (holds the roll-up toolbar). Six. | ARIA landmarks; layout A1 |
| Destinations | Changes, Model, Evidence are links in a `nav` with `aria-current="page"`, not ARIA tabs: each destination has its own `h1` and document title. | Design choice; SC 2.4.2 (S1) |
| Lenses | Language, States, Journeys, Requirements, Tests, Personas are ARIA tabs (APG tabs, automatic activation because the panels are client-side projections; manual activation if p95 switch time exceeds 100 ms). | APG tabs (S26) |
| Headings | `h1` = view title. `h2` = each review chapter (Core, Consequences, Glue), the tree, the inspector. `h3` = facets. Chapters are headings so that heading navigation reaches them: 71.6% of surveyed screen-reader users find information on long pages by headings, 3.7% by landmarks. | S36 (self-selected survey) |
| Document title | `<view> · <case or scope> · EIJA Studio`, updated on every destination change. | SC 2.4.2 (WCAG 2.2, S1; not separately opened) |
| Skip links | Three, first in tab order, visible on focus, 24 px minimum: main, model tree, inspector. The baseline's single skip link is kept. | Baseline strength (M1) |
| Focus on destination change | Focus moves to the new `h1` (`tabindex="-1"`). Focus on dialog open: section 5.6. Focus on refusal: stays where it is; the `alert` region speaks. | SC 2.4.3 (S19) |
| Focus on re-render | Renderers are keyed by model id and update in place. If the focused item disappears, focus moves to its next sibling, else its parent, and the status region says so. Baseline defect B2. | MEASURED; P3 |

## 5. Keyboard model

Conventions: every composite is one tab stop with roving tabindex, so Tab and Shift+Tab move between regions and controls, arrows move inside a composite (APG keyboard interface, S25: roving tabindex keeps the browser's scroll-into-view). Escape closes the topmost transient layer and returns focus to its invoker. Keys marked *authored* are proposals with no cited product source; they enter the study in section 13.

### 5.1 Global

| Key | Action | Source or rule |
|---|---|---|
| Tab, Shift+Tab | Next and previous tab stop; skip links first | APG |
| Ctrl+K (Cmd+K on macOS) | Open the palette | Modifier shortcut, exempt from SC 2.1.4 (S10) |
| `/` and `?` | Palette and key sheet. **Off by default**; a setting turns them on; active only when focus is not in an editable field | SC 2.1.4 needs off, remap or focus-only (S10); PREDICTION: `/` saves one K = 0.20 s per open |
| Escape | Close palette, menu, dialog, pending click-then-click; return focus to the invoker | SC 2.1.2 note on modal escape (S17) |
| Palette commands "Focus tree", "Focus main", "Focus inspector", "Focus status" | Region jump without a chord | The chord for region cycling is undecided (section 13, open Q3) |
| Approve, Apply | **No shortcut, no `accesskey`, no palette command.** A palette row "Decide..." only focuses the card's button | ai-interaction L3, L4, D11 |

### 5.2 Tabs and lenses (APG tabs, S26)

Left and Right move and activate; Home and End go to the first and last; Tab leaves the tablist into the panel. Panel `aria-labelledby` points at its tab; the active tab has `aria-selected="true"`.

### 5.3 Language tree (APG tree, S22)

| Key | Action |
|---|---|
| Down, Up | Next, previous visible node, without opening or closing |
| Right | Open a closed node; on an open node go to its first child |
| Left | Close an open node; otherwise go to the parent |
| Home, End | First, last node |
| Enter | Select the focused node (single-select tree); the inspector updates silently |
| Type-ahead | A typed character moves to the next node whose name starts with it (active only inside the tree, so SC 2.1.4 is met by focus-only) |
| `*` | Open all siblings (optional in the APG) |
| F2, Shift+F10 or the Menu key | Rename; context menu with "Move to...", "Add child term...", "Delete...". *Authored menu contents.* |
| Alt+Up, Alt+Down (optional accelerator) | Move among siblings. *Authored.* Whether Alt+arrow collides with browser or AT keys is UNVERIFIED, so the menu path is the required one |

A treegrid is reserved for multi-column trees (S28); the language tree has one column, so the plain tree is used. `aria-expanded` on parents only; `aria-selected` on the selected node; the whole set is in the DOM, so `aria-level`, `aria-setsize` and `aria-posinset` are not needed (S22). Row accessible name and description: name "Recommended, state, ADDED"; description "2 states, 1 journey, 3 tests, 1 UNKNOWN" (ripple counts beside the row are also the visible information scent, LAW§2.8).

### 5.4 Change list (chapters and operation rows)

Each chapter is an `h2`. Each operation row is a list item with a disclosure button (`aria-expanded`, `aria-controls`, APG disclosure S29) and a "Viewed" toggle (`aria-pressed`). Tab moves through the buttons; there are about 4 chunks per change (P4), so at most 8 stops in the list. A listbox is not used because APG listbox options cannot hold interactive children. The palette command "Next unviewed operation" is the accelerator.

### 5.5 Palette (APG combobox with listbox popup, S24, inside a modal dialog)

DOM focus stays in the input; `aria-activedescendant` names the highlighted option; `aria-expanded`, `aria-controls`, `aria-autocomplete="list"`. Down and Up move; Enter runs; Escape closes and returns focus. Each option shows its shortcut, and one of enabled, blocked-with-reason, AI-proposal as **glyph plus word**; blocked commands stay listed with `aria-disabled="true"` so their reason is reachable (a native `disabled` button leaves the tab order: MEASURED on the baseline, B11; SR behaviour for `aria-disabled` options is UNVERIFIED and is a manual-pass item). A polite message "5 results." follows the query after a short pause. Label in name: the option's accessible name contains its visible text (SC 2.5.3, S18).

### 5.6 Decision surface (APG modal dialog, S23)

`role="dialog"`, `aria-modal="true"`, `aria-labelledby` the title. Initial focus goes to the **heading** (a static element with `tabindex="-1"`), not to Approve. The APG page has two rules (S23, read again 2026-09-29): a static element with `tabindex="-1"` when the content has lists, tables or several paragraphs that must be perceived to understand it, and the least destructive action when the dialog holds the final step of a process that is not easily reversible. The first applies here: the dialog lists a revision id, typed operations and the UNKNOWN items. The second applies to Apply only if Apply is not easily reversible, and its reversibility is not specified in this document (decision aspect, A7). **Condition:** if Apply is not easily reversible, Apply leaves this dialog and becomes a separate confirmation whose initial focus is Cancel; Apply is never the initial focus in either case. Tab cycles inside; Escape closes with no effect. Order: acknowledgement per UNKNOWN, questions, Approve exact revision, Apply (separate), Cancel. Approve is `aria-disabled="true"` with a visible reason ("1 UNKNOWN not acknowledged") until every UNKNOWN is acknowledged. On a stale revision the `alert` region speaks and focus stays. The dialog contains kernel-derived and owner-authored text only (ai-interaction L5).

### 5.7 Diagram: the Outline is the keyboard surface (option F)

The picture takes no keyboard focus. Keyboard, screen-reader and voice-control users operate the generated Outline, whose items are native buttons (APG menu button, S30). No key in this table is authored.

| Key | Action |
|---|---|
| Tab, Shift+Tab | Next, previous Outline item in **model order**: each state followed by its outgoing transitions (native buttons, 1 stop each; 10 for the excursion, M7) |
| Enter, Space, Down on an item | Open its menu on the first item (APG menu button) |
| Menu of a transition | "Reconnect source...", "Rename..." (only two typed edits execute today, ADR-003; further commands follow the kernel vocabulary) |
| Menu of a state | "Rename...", "Position..." (X and Y fields) |
| "Reconnect source..." | Opens a chooser dialog listing every state as legal, "refused: reason" or "unchecked" (UNKNOWN); Down and Up move, Enter submits, Escape cancels and returns focus to the item |
| Screen-reader browse mode | List, button and heading navigation work natively; the Outline sits under an `h2` "Outline" |

Focus echo. Focus on an Outline button draws the focus ring token on the node or edge with the same model id (visual only, so sighted keyboard users see where they are in the picture). A pointer selection on the picture updates the inspector and sets `aria-current="true"` on the matching Outline button without moving DOM focus.

Model order rather than screen order: layout is stored apart from meaning (P3), so a layout drag must not change what a screen reader hears or where Tab lands. tldraw orders shapes by canvas position (S53); we depart from that on purpose.

**Not chosen: option E, a `role=tree` focus layer on the picture** (one tab stop; Down and Up in model order; Right on a transition follows it and Left on a state goes to the previous state; Space picks up a transition end). Reasons: (1) the excursion graph is cyclic (Revise: Rejected to Draft), so `aria-level` and position in set would announce a hierarchy between states that does not exist; (2) two keys depart from the APG tree, where Right on an end node and Left on a root node do nothing (S22); (3) the pick-up keys are authored; (4) it is a custom composite, against D2. Its measured advantage is 1 tab stop against 10 (M7). E is kept as the comparison arm of script S1 (section 12.4) and is adopted only if F fails a named task that E passes.

### 5.8 Toolbars, menus, disclosure

The status roll-up is an APG toolbar (S31): one tab stop, Left and Right between the count buttons, Home and End (three or more controls). Context menus and "Move to..." follow the APG menu button (S30): Enter, Space or Down opens on the first item; the keys inside an open menu (Escape, Home, End, type-ahead) are in the APG menu pattern, which was not opened, so they are UNVERIFIED and checked in the manual pass. Disclosures (source view, hidden-edit counter) follow S29.

## 6. Screen-reader semantics

### 6.1 Name, role, state catalogue

| Component | Role and states | Accessible name pattern | Notes |
|---|---|---|---|
| Status word and glyph | text plus `aria-hidden` glyph | "UNKNOWN 3" | The word is visible; the glyph never carries the name. "NOT RUN" is displayed with a space, the token stays `NOT_RUN` in `data-eija-state`. Whether an SR reads the underscore is UNVERIFIED |
| Tree row | `treeitem`, `aria-expanded`, `aria-selected` | "Recommended, state, ADDED" | Description carries counts; visible text starts the name (SC 2.5.3) |
| Chapter | `h2` plus list | "Core, 2 operations" | |
| Operation row | list item; disclosure button; toggle | "ADDED state Recommended, expand" | |
| Evidence coverage row | `table` with four `th`: claim, covered, assumed, NOT covered | one row per claim | The last column is never empty (P1); native table navigation works in AT |
| Counterexample | `table`, one row per step; Step, Back, Pause are buttons with visible labels | "Step 3 of 7" | Changed variables only (review-flows T07) |
| Diagram, Outline, Table | section 6.3 | | |
| Job | button "Run verification"; `progressbar` only when a real percent exists | "Verification, running, 2 of 5" | The end is one `status` message |
| Blocked control | `aria-disabled="true"` plus `aria-describedby` the visible reason | "Approve exact revision, unavailable" | |

Labels come from visible text. Icon-only controls are not allowed (rubric); every control has a visible label, which also satisfies label in name.

### 6.2 Live regions

| Region | Politeness | Content | Budget |
|---|---|---|---|
| `status` | polite, `aria-atomic="true"`, present and empty at load | result of the last user action, job end, filter result, result count | at most 1 message per user action, at most 20 words |
| `alert` | assertive | refusals, stale revision, errors | only outcomes of an action the user just took |

Both are created before the first update (MDN caveat, S47), updated through `textContent` with kernel-generated strings only (I5; ADR-013). Not live: the status bar, the tree, the inspector, job progress ticks. COUNT of the live catalogue (words): accepted 11, refused 9, verification finished 15, filter 6, results 2, stale case 11. Not live, read on dialog open: dialog title 5; the reconnect chooser's description (13 words) "Reconnect source of Reject. 2 legal targets: Submitted, Recommended. Enter submits, Escape cancels." Texts such as "Refused: Reject cannot start at Approved. Allowed: Submitted, Recommended." are real to the fixture (only Submitted and Recommended are accepted Reject sources, `policy.py` and F9 in ai-interaction). A setting "Verbose hints" shortens the chooser description after first use. Live text is also shown visibly in the status line so sighted users get it too; that costs up to 15 words while it is displayed against a 120-word chrome budget. (Revision 1 had an 18-word pick-up message; it went with option E.)

### 6.3 The diagram: candidates measured, and the choice

M2 put four candidates through axe (rules aria-allowed-role, aria-required-children, aria-required-parent, aria-valid-attr-value, aria-allowed-attr, aria-roles, nested-interactive, svg-img-alt) and Chromium's accessibility tree.

| Candidate | axe | Chromium tree (Playwright `aria_snapshot`) |
|---|---|---|
| V1 `svg role=tree`, `g role=treeitem` | 0 violations | tree, treeitems, nested group: structure kept |
| V2 `svg role=graphics-document`, `g role=graphics-object` (W3C Recommendation 2018, S32) | 0 violations | **one `img`**; the children are gone |
| V3 `svg role=group`, `g role=button` | 0 violations | group with buttons |
| V4 HTML nodes with `role=tree`, SVG edges `aria-hidden` | 0 violations | tree, treeitems, nested group: structure kept |

Text spacing (SC 1.4.12 overrides) on a 39-character label in a fixed 120 px node: SVG text is 272 px wide before the override and 346 px after (no wrapping, +27%); the HTML node stays 120 px wide and grows from 60 to 94 px high (+56%), with `scrollWidth` 118. Rendering choice: **HTML nodes** (V4 rendering), because HTML text wraps and SVG text does not. Node boxes are content-sized and edges reroute on resize; layout stores only x and y. Semantics choice: the picture is `aria-hidden` and the semantics live in the Outline (option F, below). The W3C tutorial for complex images asks for a short description plus a long one, and allows the long description to be a structured section of the same page that everyone can use (S33): the short description is the `figcaption` ("State diagram, Excursion: 5 states, 5 transitions, 1 UNKNOWN") and the long description is the **Outline**, a visible nested list generated by the same function as the picture, plus the **Table** lens that the baseline already has (`#rule-table`). Data Navigator argues for navigable structures (lists, trees, graphs) as the accessible layer over a visual, with several input modes (S34); its library is MIT-licensed (S57, S58) and is **not adopted here**: ADR-013 keeps the browser free of a build-time framework and the Studio ships three static files under a strict CSP, so an npm ES module would have to be vendored, pinned and reviewed, while option F needs only native HTML; its CSP behaviour and AT behaviour are UNVERIFIED, and it is re-evaluated if script S1 fails; Zong et al. name structure, navigation and description as the design dimensions in a study of 13 blind and low-vision readers, from the abstract only (S35). Neither tested a state-machine editor.

**V5 (M6, audit follow-up): interactive parts inside V4.** The M2 fixtures hold text only, but the design needs a reconnect handle (D5 click-then-click). Three variants, Chromium 154, axe 4.13.0 with all tags and `target-size` enabled:

| Variant | axe | Chromium tree |
|---|---|---|
| V5a `button` inside the transition `treeitem` | 0 `nested-interactive`; `color-contrast` incomplete (fixture has no paint); `page-has-heading-one` (fixture has no `h1`) | button kept, but the item name becomes "Submit Reconnect source" |
| V5b `button` outside the tree, in a labelled group | same | tree unchanged ("Submit"); button separate |
| V5c 24 px `aria-hidden` pointer-only handle inside the item, no tab stop | same | tree unchanged ("Submit") |

Choice: V5c, kept under option F. The handle is a pointer-only element inside the `aria-hidden` picture, with no tab stop; its named equivalents are the Outline menu command "Reconnect source..." (D5). Voice-control users say the Outline button's visible name; whether their software reaches it is UNVERIFIED (script S2). Chromium and axe only; no AT.

**V6 (M7, audit follow-up 2): E against F on the real excursion candidate.** Chromium 154, axe 4.13.0 with all tags and `target-size` enabled.

| Candidate | axe | Tab stops inside | Chromium tree |
|---|---|---|---|
| E: V4 tree, roving tabindex, transitions nested under their source state | 0 violations; `color-contrast` and `target-size` incomplete | 1 | tree with 5 treeitems; transitions in groups ("Reject, to Rejected") |
| F: `figure` with `figcaption`, `aria-hidden` picture, `section` "Outline" with nested `ul` of native buttons (`aria-haspopup="menu"`) | `target-size` on 6 buttons (fixture artefact: unstyled buttons below 24 px high; the design sets 32 px); `color-contrast` incomplete | 10 | figure, region "Outline", heading, lists of buttons ("Reject: Submitted to Rejected") |

**Choice: F.** Reasons, in order: native roles need no custom key table and no AT verification of a composite (D2, S27; WebAIM Million association, S54); a list of states with named outgoing transitions describes a cyclic graph honestly, a tree does not; no authored keys; the Outline was already required, generated and parity-tested. Cost: 10 tab stops against 1, and sighted keyboard users move through the Outline rather than the picture (focus echo, section 5.7). The predicted keyboard times of E and F differ by 0.20 to 0.30 s, inside the band (section 11), so speed does not decide.

Caveat: these are Chromium and axe results. Whether NVDA, JAWS or VoiceOver present the Outline well is UNVERIFIED and is the first manual pass (section 12, script S1), run side by side with an E fixture.

## 7. Dragging alternatives (SC 2.5.7) and pointer rules

SC 2.5.7 asks for a single-pointer alternative; its Understanding page lists clicking items in sequence instead of drawing connections, adjacent controls for reordering, pop-up menus for moving items and numeric fields (S2). Keyboard operability is assessed separately (S2), so both are provided. Dragging is not a path-based gesture under SC 2.5.1 (S14).

| Drag | Single-pointer path | Keyboard path | Refusal |
|---|---|---|---|
| Reconnect a transition source (T04) | Click the handle, then click a target; legal targets carry glyph and word | Outline item, Enter, menu "Reconnect source...", chooser (section 5.7) | Text at the target and in `alert`: reason plus allowed alternatives; only two typed edits execute today (ADR-003), so most drops are refusals |
| Re-parent a term (T05) | Row menu "Move to..." dialog listing legal parents | Shift+F10, Move to..., type-ahead, Enter | Refused parents are listed with their reason |
| Reorder siblings | "Move up" and "Move down" in the row menu | Same menu; optional Alt+arrows | as above |
| Position a node (layout) | Inspector "Position" X and Y fields (the baseline already has them) and "Tidy" | Same fields | States that a layout change renews presentation approval (ADR-008) |
| Add an element from a palette | "Add state..." command | Palette | Refusal outside the frozen vocabulary |

Pointer cancellation (SC 2.5.2): no action fires on pointer down; a drag or a pending click-click completes on the up event and can be aborted with Escape or by moving back or clicking outside; a committed edit has an undo that states what it does not restore (P11). Targets: at least 24 by 24 CSS px, or a 24 px spacing circle (SC 2.5.8, S3). COUNT from the two layout files (interactive roles button, tab, input, tree-item, chip, plus text elements labelled as bare buttons or the palette): 13 elements in `nav-current` (smallest side 34 px) and 48 in the default state of `nav-proposed` are all at 24 px or more. The smallest is `main-hidden` ("n formatting-only edits hidden, show", 776 by 24, the hidden-edit reveal and a main-region tab stop in section 11.3); all other 47 are at least 28 px. Counting the Baseline-scope and Changes-view variants in the same file gives 57, same minimum. `main-hidden` passes SC 2.5.8 but is below the 32 px default density; raising it to 32 px is handed to the layout aspect, which owns the file. The reconnect handle is exactly 24 px (canvas-flows); the compact density is 24 px and the default is 32 px, for pointer inputs marked coarse as well.

## 8. Focus appearance and visibility

| Rule | Value | Evidence |
|---|---|---|
| Indicator, outer | `:focus-visible`, `outline: 2px solid var(--focus)`, offset 2 px, for controls not inside a scroll container | MEASURED (M3): outer rings are clipped by an `overflow:auto` parent, so the outer form is used only outside scroll containers |
| Indicator, inset | `outline: 3px solid var(--focus)`, `outline-offset: -3px` (offset pinned to exactly minus the width, so the ring is flush with the outer edge and never inset further) for tree rows, list rows, Outline buttons, tabs and anything inside a scroll container | MEASURED (M3): with the row flush to an `overflow:auto` parent, the outer ring band was page white (clipped) and the inset ring band was the ring colour |
| Colour | `--focus` at least 3:1 against every surface step and against selected and hover fills, both themes | Computed with the provisional tokens: accent on the three surface steps 3.83, 4.23, 4.50 (light) and 3.66, 4.17, 4.50 (dark) |
| SC 2.4.13 area | Required area: a 2 px perimeter, 4h + 4w for a rectangle (S5; the page's example: 90 by 30 px needs 480 px2). Outer ring: (w + 8)(h + 8) - (w + 4)(h + 4) = 4w + 4h + 48, passes. Inset 3 px at -3 px: wh - (w - 6)(h - 6) = 6w + 6h - 36, passes whenever w + h is at least 18 px, so for every target of 24 px or more. A 2 px ring at -2 px would give 4w + 4h - 16 and **fail by 16 px2**; S5 says indicators inset from the edge must be thicker than 2 px. Revision 1 claimed the 2 px inset ring satisfied 2.4.13; that was wrong | S5 (AAA); arithmetic |
| SC 2.4.13 contrast | 3:1 change between the same pixels focused and unfocused; the inset ring sits on the component's own fill, which is one of the surface steps above | S5; section 9.1 |
| Forced colours | Outline only, never `box-shadow` (forced to none) | S38, S40 |
| Not obscured (SC 2.4.11, AAA 2.4.12) | `scroll-padding-top: 48px; scroll-padding-bottom: 36px` on scroll containers (chrome 40 and 28 px plus 8 px); below the compact breakpoint both bars are static, not sticky | S4 names scroll-padding; arithmetic: at 320 by 256 CSS px the sticky chrome would take 68 of 256 px (26.6%) and leave 188 px |
| Focus never on `body` after an action | Test in section 12 | Baseline defect B2 |

## 9. Colour, contrast, forced colours, zoom, spacing, motion

### 9.1 Contrast (computed, WCAG 2.x ratio)

| Pair | Ratio | Reading |
|---|---|---|
| Baseline ink on paper, muted on paper, green on white | 13.61, 5.50, 6.68 | pass AA text |
| Baseline input border on white, secondary button border on paper | 1.74, 1.68 | fail 3:1 for identifying a control (B5) |
| Provisional light status text tokens (`visual-design-foundations.md` 2.4), on surface step 0 and step 2 | 4.50-4.54 and 3.83-3.86 | **fail 4.5:1 as text on step 2** (selected or hover fills) |
| Provisional dark status text tokens, on step 0 and step 2 | 4.50-4.54 and 3.66-3.69 | same |

Rule that follows: **status words use the ink colour** (baseline ink on paper is 13.61:1; the new ink token must be computed the same way), and **status hue lives on the glyph**, which needs 3:1 and has 3.66 or more on every step. A colour token that is chosen as the lowest lightness reaching 4.5:1 on one surface cannot be used as text on a darker surface. The token lint computes every text and surface pairing and reports UNKNOWN when a value cannot be computed. APCA is advisory (SYNTHESIS C10). CVD: proved and unknown differ by 0.025 dE_OK for deutan and refuted and stale by 0.016 (VIS§2.4, MEASURED there), so shape and word carry status, never hue.

### 9.2 Forced colours

MDN says forced colours also overrides SVG `fill` and `stroke` (S38); Microsoft's 2020 article says SVG is not adjusted automatically and recommends `currentColor` (S40). **MEASURED (M3, Chrome 154, `forced_colors="active"` emulation):** `fill="#ff0000"` and `stroke="#00ff00"` stay red and green whether written as attributes or in a CSS class; `currentColor` and system keywords (`CanvasText`, `Highlight`) resolve to the forced palette. The contradiction is resolved for Chromium in favour of the Microsoft article. Rules: paint SVG through `currentColor` or an explicit `@media (forced-colors: active)` block that maps classes to system colours; keep 1 px transparent borders on interactive rows so selection can show as a border; never use `forced-color-adjust: none` except for a colour legend swatch, if one exists; no `box-shadow` for state; every state has a shape or a word. MDN adds that system colours follow native element semantics, not ARIA roles (S38), so a `div role="button"` is not given `ButtonText`: custom widgets style their colours from CSS system colours themselves. `prefers-contrast` (widely available since May 2022, `custom` matches forced colours, S41) is used only to raise border contrast.

### 9.3 Reflow, zoom, text spacing

SC 1.4.10: 320 CSS px wide and 256 high, equal to 400% on a 1280 by 1024 window (S8). Two-dimensional content (diagrams, data tables) may scroll in both directions; everything else reflows (S8).

| Regime (CSS px) | Layout | Requirement |
|---|---|---|
| 1112 and wider | tree, main, inspector | |
| 752 to 1111 | tree and main; inspector as a drawer | toggle buttons with visible labels and `aria-expanded` |
| below 752 | one column; tree and inspector as drawers behind labelled buttons; top and status bars static | every region reachable; the diagram canvas and tables are the only 2D scroll areas |

The baseline instead hides its sidebar at 760 px (B4). The 1112 and 752 boundaries follow from my assumed 480 px main minimum and are hypotheses. Text in rem; no fixed heights on text containers; no `user-scalable=no` or `maximum-scale` (static lint). SC 1.4.12 (S13): content must tolerate line height 1.5, paragraph spacing 2 times, letter spacing 0.12 em and word spacing 0.16 em. Node labels are HTML text that wraps; the override test in section 12 fails a clipped or overlapped element.

### 9.4 Motion and hover content

Motion never carries meaning; `prefers-reduced-motion` follows the motion aspect (section 9 there). Tooltips and popovers (status definitions, blocked reasons) are dismissible, hoverable and persistent (SC 1.4.13, S16) and open on focus as well as hover.

## 10. Cognitive accessibility

The COGA Working Group Note (29 April 2021) has eight objectives (S45). Each becomes a rule with a check.

| COGA objective | Studio rule | Check |
|---|---|---|
| 1 Understand what things are and how to use them | Status glyph plus word everywhere; verb-first commands; empty states name what is missing and offer one action; a "What does UNKNOWN mean?" definition on focus or hover, generated from the kernel vocabulary | Lint: every status token has a definition string |
| 2 Find what they need | One palette; headings; a tree filter with three modes; stable positions of regions | Manual: first-click test on "where are the UNKNOWN items" |
| 3 Clear content | Labels of at most a few words; sentence case; no idioms; AI text is labelled and never in the decision dialog | Word budget per view (P10) |
| 4 Avoid mistakes and correct them | Refusal states reason and allowed alternative; approve and apply confirm the exact revision (SC 3.3.4, S21); undo states what it does not restore | Scripted: every refusal string has both parts |
| 5 Help users focus | One modal at a time; no autoplay; notices never take focus; chrome recedes (P10) | Scripted: focus unchanged after a `status` update |
| 6 Do not rely on memory | Evidence stays beside the decision; a value shown is never retyped (SC 3.3.7, S7); Viewed marks persist across revisions (P4); the last focused item is restored when a composite is re-entered | Manual: no task needs a value typed twice |
| 7 Provide help and support | **One Help entry, same relative order in every view** (SC 3.2.6, S6): key sheet, status glossary, local docs. Whether one page with several views counts as a "set of pages" is UNVERIFIED; treated as applicable | Scripted: Help is at the same DOM index among banner controls in every view |
| 8 Support adaptation | One settings surface: density (24 or 32), theme, verbose hints, single-key shortcuts, outline as the default lens; stored in `localStorage` inside try and catch and never required (a private window may return empty) | Scripted: the Studio renders correctly with storage blocked |

No UI time limit exists; provider timeouts are job states with a Cancel (ai-interaction D9). Accessible authentication (SC 3.3.8, S20) does not apply: the Studio has no login, only a private link (ADR-011). Open question: the baseline requires three typed free-text answers to meaning questions; typing is error-prone and the expected values are known to the kernel, so choices would reduce error and effort. That belongs to the decision aspect (A7).

## 11. Quantitative model (all PREDICTION unless marked)

Constants: KLM operators K 0.20 s (a chord counts each key), M 1.35, B 0.10, H 0.40, P 1.10 without geometry, R as stated; RMS error 21% (S51). Pointing with geometry: Fitts (Shannon) MT = 0.37 + 0.13 log2(D/W + 1) s (Cockburn et al. 2007, eight participants, R2 = 0.93; S52; fitted to vertical menu-item selection, so 2-D canvas pointing is an extrapolation). Flow ops and notes are in [a11y-flows.json](../../../design/tasks/a11y-flows.json). Flip range: a ratio proposed/current between 0.79/1.21 = 0.653 and 1.21/0.79 = 1.532 is inside the bands.

### 11.1 Task totals

Geometry profiles as in `canvas-flows.json`: D (headline; current MEASURED, proposed from the canvas design) and L (cross-check from `current-impact.json` and `proposed-canvas.json`). The P ops in `a11y-flows.json` carry those layout stems and ids, so a consumer recomputing from the layout files obtains the L totals. Totals below are D unless marked.

| Flow | Current (s) | Proposed (s) | Ratio | Inside the flip range? | Like for like? |
|---|---|---|---|---|---|
| T04 keyboard, cold start, **F**: baseline form versus palette plus Outline menu (T04-a11y-outline-cold) | 4.12 | 4.42 | 1.07 | yes: no evidence of a difference | yes, both from document start |
| T04 keyboard, cold start, E (not chosen): palette plus tree context menu (T04-a11y-kbd-cold) | 4.12 | 4.62 | 1.12 | yes | yes |
| T04 keyboard, warm, **F**: Enter, Enter, Down, Enter on the focused Outline button (T04-a11y-outline-warm) | 4.12 | 2.32 | 0.56 | outside, but **not like for like** | no: focus is already on the Reject button |
| T04 keyboard, warm, E (not chosen): Space, Down, Enter in the tree (T04-a11y-kbd-warm) | 4.12 | 2.02 | 0.49 | outside, but not like for like; F against E is 2.32/2.02 = 1.15, inside the range | no |
| T04 pointer, non-drag: baseline pointer form versus click handle then click target | 5.62 (L 5.43) | 3.24 (L 3.08) | 0.58 (L 0.57) | outside, but not robust: `canvas-flows.json` 11.2 finds an overlap when the current flow is charged one M fewer (4.27 s against 3.24 s) | partly: the current flow has an ESTIMATED 22 px popup row (0.576 s) and, in D only, an assumed one-notch scroll |
| T05 keyboard move: ESTIMATED editor workaround versus tree menu (kernel dry run budget 1 s) | 8.55 (7.55 with Shift held once) | 8.15 | 0.95 (1.08) | yes, under both Shift conventions | no: current is a guess; proposed carries 2 more M than current |
| T08 keyboard decide: baseline versus decision dialog | 6.74 | 5.69 | 0.84 | yes | no: start states differ; proposed carries 1 more M (the deliberate reading step) |
| T11 return to the tree: Shift+Tab (baseline 12 K, proposed 14 K) | 3.75 | 4.15 | 1.11 | yes | approximately: inspector to tree versus Approve to case list |
| T11 return to the tree: palette command (Ctrl+K, "tree", Enter) | 3.75 | 2.75 | 0.73 | yes | approximately; palette ranking assumed |
| T11 skip link from document start: baseline case row (3 K) versus tree link (Tab x2, Enter) | 1.95 | 1.95 | 1.00 | yes | yes |

Arithmetic for T04 cold. Current: M 1.35 + K 2.60 (13 keys: Tab x6, Enter, Tab x3, Down, Tab, Enter) + R 0.17 (100 ms view change + 70 ms commit) = 4.12 s. Proposed: M 1.35 + K 1.80 (Ctrl+K 2, Down, Enter, Shift+F10 2, Enter, Down, Enter = 9 K) + T 1.20 (6 chars) + R 0.27 (100 + 100 + 70 ms) = 4.62 s for E; F replaces Shift+F10 (2 K) with Enter (1 K): 4.42 s. M placement differs per flow and is listed in each task's assumptions (T05: current 1 M, proposed 3; T08: current 2, proposed 3; all others equal). Shift convention: T05 charges shift+down as 2 K per press, T11 holds Shift once; each task states its choice and the alternative total. T11 Shift+Tab: Shift held once, so n + 1 K; the per-press convention (2n K) gives 5.75 s and 6.55 s (ratio 1.14). Skip-link order main, tree, inspector (section 4) makes region reach Tab x k plus Enter, 2 to 4 keys, **from document start only**.

### 11.2 Equity against the drag path

The drag path for the same edit is 3.04 s in D (canvas-flows.json: M 1.35 + Fitts 0.766 + B 0.10 + Fitts 0.657 + B 0.10 + R 0.07) and 2.88 s in L.

| Path | Time D / L (s) | Ratio to drag D / L | Reading |
|---|---|---|---|
| Click handle, click target | 3.24 / 3.08 | 1.07 / 1.07 | +0.20 s = 2 extra B; inside the band |
| Keyboard, warm, F (Outline menu) | 2.32 / 2.32 | 0.76 / 0.81 | Keys are cheap for a practised user; the start state differs (focus already on the item) |
| Keyboard, cold, F (palette, Outline menu) | 4.42 / 4.42 | 1.45 / 1.535 | D: inside the flip range. L: 0.003 above the boundary 1.532; L favours the drag (the handle is 46 px from the pointer start), so **no gap is claimed in either direction** |
| Keyboard, warm, E (not chosen) | 2.02 / 2.02 | 0.66 / 0.70 | for comparison |
| Keyboard, cold, E (not chosen) | 4.62 / 4.62 | 1.52 / 1.60 | for comparison; same reading as F cold |

The predicted cost of non-drag paths is small for an expert. The real risks are **discoverability and learning**, which KLM does not model; they are the study's job.

### 11.3 Other counts and computations

| Quantity | Value | Label |
|---|---|---|
| Baseline tab stops from document start (Change, Impact, Try, Evidence) | 16, 12, 12, 16 | MEASURED |
| Proposed tab stops in the default review view: skip links 3, top bar 7 (3 destinations, scope, palette, attention, provider), sidebar 2 (filter, tree), main 11 (Decide, lens tablist, 4 rows x 2 buttons, hidden-edit reveal), inspector 4, status 2 (toolbar, job) | 29. Region reach from document start is Tab x k plus Enter (k = 1 to 3), 2 to 4 keys; from another region it is the palette command (3 K plus 4 characters, PREDICTION 2.75 s) or up to 13 Shift+Tab presses (PREDICTION 4.15 s); no region-cycle chord exists (Q3) | COUNT from nav-proposed.json and the composite rules; PREDICTION for the times |
| Tab stops for the excursion diagram: F Outline (5 states + 5 transitions, native buttons) versus E roving tree | 10 versus 1 | MEASURED (M7, Chromium 154) |
| Fitts ID at D = 400 px: W 24, 32, 40 | 4.14, 3.75, 3.46 bits | PREDICTION; MT 0.909, 0.858, 0.820 s under the able-bodied Cockburn profile; 24 to 32 px saves 0.050 s (5.5% of 0.909 s); **not valid for users with tremor or limited dexterity** |
| Sticky chrome share of viewport height: 900, 512, 256 px | 7.6%, 13.3%, 26.6% | COUNT |
| Messages in the T04 Outline path | 1 chooser description (13 words, not live) and 1 live result (11 or 9 words) | COUNT |

Validity limits. KLM covers expert, error-free, routine tasks; it does not model listening to a screen reader (speech output time is not in these totals), learning, errors or reading. Fitts is one-dimensional pointing with able-bodied constants, fitted to vertical menu-item selection by eight right-handed graduate students; 2-D canvas handle and node pointing (the T04 click and drag rows) is outside that calibration task and is an extrapolation; it says nothing about keyboards. Contrast ratios are properties of colour pairs, not of readers. The sign of a difference inside the 21% band is not evidence. "Feels good" for users of AT is measured only by section 13.

## 12. Testing plan

Order of cost: static checks, then axe, then scripted tests, then manual AT, then the study. A layer does not replace the one after it: on the baseline axe found 1 of 5 failures and scripts or a reading of the source found the other 4 (section 3).

### 12.1 Static and unit (no browser)

| Check | Pass criterion |
|---|---|
| Layout and DOM target size | every interactive element has both sides at least 24 CSS px, or the spacing exception; today COUNT 48 of 48 in the default state of the proposed layout file, smallest 24 px (`main-hidden`); a second criterion, at least 32 px at default density, fails today on that one element |
| Token contrast matrix | every text token at least 4.5:1 and every glyph, border and focus token at least 3:1 on every surface step and fill it can sit on, both themes; not computable is UNKNOWN and fails the build |
| Markup lint | every control has a visible label and an accessible name that contains it; no `tabindex` above 0; every status glyph is `aria-hidden` with an adjacent word; every undo has a coverage string; `accesskey` absent; `viewport` has no `user-scalable=no` |
| Authority | `approve` and `apply` occur only in the decision closure; the palette registry rejects other classes (ai-interaction I2, I3) |
| Parity | Outline, Table and picture list the same ids, names and relations, generated from one function |

### 12.2 axe-core (test-only dependency)

axe-core 4.13.0, MPL-2.0 (npm registry, S56; README S42). Run through the Python Playwright package (Apache-2.0, S50) in one Chromium. Tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa`, `best-practice`; **enable `target-size` explicitly**, it is disabled by default (S44). Scope: every destination, every lens, dialog open states, palette open, empty and error states, both themes, viewports 1440x900, 1024x768 and 320x256. Criterion: 0 violations and 0 incomplete results without a written triage; `aria-hidden-focus` must report 0 on the `aria-hidden` picture. Not shipped; both packages need rows in `docs/oss/REGISTER.md` (the register already lists HCI Playwright and axe-core as rows still to add, `docs/oss/REGISTER.md` line 16). A pinned checksum protects the fetched script.

### 12.3 Scripted browser tests (one Chromium at a time)

| Test | Pass criterion, fixed in advance |
|---|---|
| Roving invariant | every composite has exactly one `tabindex="0"` item at rest |
| Focus after action | after each action in the flow file, `document.activeElement` is not `body`, and is the specified element for dialogs and destination changes |
| No trap | Tab from a modal cycles inside it; Escape closes it and focus returns to the invoker |
| Focus area (SC 2.4.13) | for each focusable item, screenshot it unfocused and focused; the number of changed pixels is at least 4w + 4h of its box, and the changed pixels differ by at least 3:1; a ring whose `outline-offset` is below minus its `outline-width` fails |
| Focus echo | focusing each Outline button marks exactly one picture element, the one with the same model id; the picture contains no focusable element |
| Not obscured | for each focusable item at 1440x900 and 320x256, the focus ring is fully inside the viewport and not under sticky chrome (AAA target; AA requires only not entirely hidden) |
| Reflow | at 320x256 no horizontal page scroll outside the diagram canvas and data tables; the count of reachable primary regions is 5 (tree, main, inspector, status, help) |
| Forced colours | with `forced_colors="active"`, every SVG paint and glyph resolves to a system colour; no state is carried by background fill alone (heuristic: two states that differ in computed `background-color` must also differ in border, outline or text) |
| Text spacing | with the SC 1.4.12 override, 0 clipped or overlapping elements |
| Reduced motion, dark, storage blocked | renders and stays operable |
| Live regions | exactly two exist at load; at most one polite message per action; each at most 20 words; none contains provider text |

### 12.4 Manual screen-reader passes (owner: a human tester; not run here)

Combinations follow WebAIM survey 10: JAWS 40.5%, NVDA 37.7%, VoiceOver 9.7% as primary screen reader; Chrome 52.3%, Edge 19.3%, Firefox 16.0% on desktop (S36). Priority: NVDA with Chrome (runnable on this Windows machine), JAWS with Chrome, VoiceOver with Safari. Status of each combination today: NOT_RUN. NVDA browse and focus modes and automatic switching are documented (S46); which controls trigger focus mode is UNVERIFIED.

| Script | Task | Pass criterion |
|---|---|---|
| S1 | Diagram, side by side: the F Outline (chosen) and an E fixture (V4 tree), same tasks, order alternated: find the Reject transition, hear its source, target, status and ripple counts, reach "Reconnect source..." | Every state and transition is reachable and named in F; record every task F fails that E passes (the E adoption trigger) and whether the tree's level and position announcements mislead about the cyclic graph |
| S2 | T04 reconnect via the Outline menu and chooser; also with voice control if available (say the Outline button's name) | Legal targets and the result heard once each; refusal heard with reason; the menu command is reachable by its name |
| S3 | T02 review by chapters, by headings | Chapters reached by heading navigation; each operation's status and UNKNOWN count heard |
| S4 | T09 palette | Result count, active option, blocked reason, shortcut heard; focus returns |
| S5 | T08 decision dialog | The UNKNOWN list is heard before Approve is reachable; `aria-disabled` reason heard; no shortcut exists |
| S6 | T07 counterexample table | Steps and changed variables navigable by table commands |
| S7 | Status words | "NOT RUN", "UNKNOWN 3", CONFLICT are heard as words; the underscore is not read |
| S8 | Zoom 200 and 400 percent, keyboard, and a magnifier | All regions reachable; no focus hidden |

Each script records product, version, browser, verbosity and punctuation level.

### 12.5 Conformance policy

An audit follows WCAG-EM 2.0 (W3C Group Note of 23 July 2026, S48): scope, explore, sample (with a random 10% set and every complete process), audit, report. The Note says a sampled evaluation cannot support a claim for a whole site. Until a full audit exists the Studio publishes a statement with the known failing SC and no conformance badge.

## 13. Study protocol (design only; nothing was run)

* **Design.** Within-subject, baseline Studio versus proposed, order counterbalanced, on the excursion workflow. Cohorts: keyboard-only, screen-reader (NVDA or JAWS, the participant's own setup), low-vision with zoom or magnifier, plus a mouse-and-keyboard control group.
* **Tasks.** T04 (click-then-click and the Outline menu), T05 (move by menu), T02 (review by chapters), T08 (decide), T09 (palette), T10 (first run, unprompted).
* **Sample.** Formative rounds of about 5 per cohort: with a mean discovery rate L = 0.31 (Nielsen and Landauer, via LAW§2.10, medium) 5 users find about 84% of problems and estimate no prevalence. Quantitative comparisons need about 20 or more per group (NN/g, LAW§2.10), which AT cohorts rarely reach; then only descriptive statistics are reported, with intervals.
* **Measures.** Task success; time; errors; **UNKNOWN misread as PASS (target zero)**; for screen-reader users, whether each seeded UNKNOWN was recalled before approval; calibration; SUS, per-task SEQ, Raw TLX with intervals (SUS compared with 68 only with an interval).
* **Pre-registered hypotheses (all HYPOTHESIS).** H1 every participant in each cohort completes T04 and T08 with their own AT. H2 median non-drag time is at most 3 times the pointer-drag median for the same task (PREDICTION 1.07 for click-then-click and 0.76 to 1.45 for the Outline keyboard path, D profile, gives slack; the 3 is arbitrary). H3 no participant approves a change with an unheard or unread UNKNOWN. H4 "Reconnect source..." in the Outline menu is found without instruction by at least half of keyboard participants (unfounded threshold; to be revised after the formative round).
* **Stop criteria.** Stop and redesign if any participant approves with an unread or unheard UNKNOWN on a seeded item, if any participant cannot complete T08 with their AT, or if the Outline fails script S1 in two AT combinations.
* **Status of results.** None. No user-benefit claim is made.

## 14. Sources opened on 2026-09-29

Standards and documentation (W3C, MDN, vendor): S1 https://www.w3.org/TR/WCAG22/ (Recommendation 12 Dec 2024; new SC list; 4.1.1 removed). Understanding pages under https://www.w3.org/WAI/WCAG22/Understanding/: S2 dragging-movements, S3 target-size-minimum, S4 focus-not-obscured-minimum, S5 focus-appearance, S6 consistent-help, S7 redundant-entry, S8 reflow, S9 non-text-contrast, S10 character-key-shortcuts, S11 status-messages, S12 use-of-color, S13 text-spacing, S14 pointer-gestures, S15 pointer-cancellation, S16 content-on-hover-or-focus, S17 no-keyboard-trap, S18 label-in-name, S19 focus-order, S20 accessible-authentication-minimum, S21 error-prevention-legal-financial-data (each `.html`). APG under https://www.w3.org/WAI/ARIA/apg/: S22 patterns/treeview, S23 patterns/dialog-modal, S24 patterns/combobox, S25 practices/keyboard-interface, S26 patterns/tabs, S27 practices/read-me-first, S28 patterns/treegrid, S29 patterns/disclosure, S30 patterns/menu-button, S31 patterns/toolbar. S32 https://www.w3.org/TR/graphics-aria-1.0/. S33 https://www.w3.org/WAI/tutorials/images/complex/. S45 https://www.w3.org/TR/coga-usable/. S48 https://www.w3.org/TR/WCAG-EM/. S38 https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors. S39 https://developer.mozilla.org/en-US/docs/Web/CSS/forced-color-adjust. S40 https://blogs.windows.com/msedgedev/2020/09/17/styling-for-windows-high-contrast-with-new-standards-for-forced-colors/. S41 https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-contrast. S47 https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Live_regions. S46 https://download.nvaccess.org/documentation/userGuide.html (NVDA 2026.2). S49 https://playwright.dev/python/docs/api/class-page. S50 https://raw.githubusercontent.com/microsoft/playwright-python/main/LICENSE (Apache-2.0).

Research and practitioner sources: S34 https://arxiv.org/abs/2308.08475 (Data Navigator, IEEE VIS 2023, abstract). S35 https://arxiv.org/abs/2205.04917 (Zong et al., Computer Graphics Forum 2022, 13 participants, abstract). S36 https://webaim.org/projects/screenreadersurvey10/. S37 https://webaim.org/projects/screenreadersurvey11/ (closed, no results). S54 https://webaim.org/projects/million/ (2026 analysis). S42 https://github.com/dequelabs/axe-core (MPL-2.0). S44 https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md. S56 https://registry.npmjs.org/axe-core/latest (4.13.0, MPL-2.0). S57 https://github.com/cmudig/data-navigator (MIT). S58 https://registry.npmjs.org/data-navigator/latest (3.0.0, MIT, no runtime dependencies listed). S43 https://accessibility.blog.gov.uk/2017/02/24/what-we-found-when-we-tested-tools-on-the-worlds-least-accessible-webpage/. S53 https://tldraw.dev/sdk-features/accessibility. S55 https://www.ilograph.com/features.html. S51 https://en.wikipedia.org/wiki/Keystroke-level_model (K 0.20, P 1.1, H 0.4, M 1.35, B 0.1, RMS error 21%). S52 https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf (converted locally with pdftotext: `Tp = 0.37 + 0.13 ID`, R2 = 0.93, eight participants).

Repository: `src/eija_studio/resources/web/{index.html,app.css,app.js}`; `src/eija_studio/domain/policy.py` (excursion transitions); `design/layouts/nav-current.json`, `nav-proposed.json`; `design/tasks/canvas-flows.json`, `language-flows.json`, `ia-flows.json`; `docs/hci/design/ai-interaction.md`, `motion-and-performance.md`; `docs/oss/REGISTER.md` (line 16); ADR-003, ADR-008, ADR-011, ADR-013 in `docs/adr/0000-poc-decision-log.md`.

Not opened and therefore not used: JAWS and VoiceOver documentation, the APG menu (as opposed to menu button) pattern, EN 301 549, and the Windows contrast theme documentation.

## 15. Open questions and contradictions

| # | Item | Status |
|---|---|---|
| Q1 | Whether NVDA, JAWS and VoiceOver present the Outline (and, for comparison, the E tree) as specified; whether `aria-disabled` options are found; whether the underscore in `NOT_RUN` is spoken | NOT_RUN; manual passes S1, S4, S7 |
| Q2 | MDN says SVG paint is forced in forced-colour mode; Microsoft says it is not | Resolved for Chromium 154 by measurement (hex not forced); other engines UNVERIFIED |
| Q3 | A region-cycle chord: F6 conflicts with the browser's own focus keys on some platforms (not verified); the design uses skip links (from document start) and palette commands. Task T11 prices the return from another region: 4.15 s by Shift+Tab, 2.75 s by palette (PREDICTION) | Open; test in the formative round; decide before claiming that region reach offsets the 29 tab stops |
| Q4 | Whether an SPA with several views is a "set of web pages" for SC 3.2.6 | UNVERIFIED; treated as applicable |
| Q5 | The 1112 and 752 CSS px breakpoints rest on an assumed 480 px main minimum | Hypothesis; layout aspect |
| Q6 | The Alt+arrow accelerators of the language tree are authored (the diagram pick-up keys went with option E) | Study |
| Q7 | APCA versus WCAG 2.2 for dark text (SYNTHESIS C10) | Open; WCAG 2.2 gates |
| Q8 | Free-text meaning questions in the decision dialog | Decision aspect |
| Q10 | Whether Apply is easily reversible (decides the initial focus of the dialog, section 5.6) | Decision aspect, A7 |
| Q11 | Whether voice-control software reaches the named Outline buttons and menu commands (the picture and its handle are `aria-hidden`) | UNVERIFIED; script S2 |
| Q12 | Whether Data Navigator (MIT) works under the Studio CSP; relevant only if S1 sends the design back towards an in-picture navigation layer (E) | UNVERIFIED; re-evaluate if S1 fails |
| Q13 | Tab traversal of the Outline (10 stops for the excursion, n + m in general) against one stop for E | Formative round with keyboard-only users; revisit trigger in HCI-ADR-0067 |
| Q9 | Chrome 154 focuses scrollable `pre#trace` while axe flags it; other engines untested | The fix (`tabindex="0"`, `role="region"`, label) is cheap; adopt it |
