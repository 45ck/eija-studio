# PlayIDE: 100 small fixes and 200 small polishes (November 2026)

Owner ask, 12 November 2026: "do 100 small fixes and 200 small polishes, quantitative UI/UX, do not change the UI from the original design". So every item here keeps the existing layout, visual language and flows, and every item has a number that moved.

Status: **10 of 100 fixes and 37 of 200 polishes** have landed. Batches ship as small PRs; this file is the running tally.

Labels as in the rest of `docs/hci/`. **MEASURED**: computed by a script run on the real PlayIDE served by `eija serve` (offline provider, synthetic data) in headless Chromium, or computed from the stylesheet. Nothing here is a measurement of people; no usability claim is made.

## What counts

- A **fix** is a defect: something that fails a WCAG 2.2 AA success criterion, an ARIA rule, a keyboard path the UI advertises, or behaviour that is wrong.
- A **polish** is a refinement within the existing design: a contrast ratio raised to AA, a target raised to 24 px, a size raised to the text floor, a duplicate colour folded into a token, a stable width, consistent copy.
- One item is one distinct element or rule. A rule applied to many declarations counts once, and its measure says how many places it covers.

## How it is measured

A harness drives PlayIDE through every diagram tab, the checks popover, a chat plan and its preview, the Review tab with a plan, a paused run, a simulation, the Systems, Review & activate and Requirements dialogs, the Ctrl+K palette and Design + Play, for the `library-loan` and `excursion` packs at 1440x900 and 1280x720. At each stop it records:

- axe-core 4.10 violations (tags wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa, best-practice; `target-size` enabled);
- WCAG 2.2 text contrast from computed colours (opacity and stacked backgrounds blended);
- interactive boxes under 24 x 24 CSS px (SC 2.5.8, inline links exempt);
- controls without an accessible name, fields without a label, buttons without a type;
- keyboard focus with no visible change (focus reached by keyboard so `:focus-visible` applies);
- text under 11 px, clipped text without an ellipsis, broken id references, duplicate ids, horizontal page scroll, overlapping and off-screen controls.

A second script probes behaviour: popover and dialog open/close by keyboard, Escape, focus return, click-outside, tab-list keys, layout toggles and their shortcuts, the run bar's F5/F6/Shift+F5.

Baseline (MEASURED, main at 497bd89): 130 distinct findings on `library-loan` and 153 on `excursion` at 1440x900; 31 of 34 behaviour probes passed. After batch 1: 12 and 16 findings, 34 of 34 probes.

Not fixed on purpose: the chat box is a `textarea` with `role=combobox` for name completion (axe `aria-allowed-role`). Changing the role changes how screen readers announce completion, so it waits for a screen-reader pass. The 13 px plan-step checkboxes sit inside their labels, which are the real targets.


## Fixes

| # | Batch | Where | Change | Measure (before -> after) |
|---|---|---|---|---|
| F001 | 1 | Shell | The page had no level-one heading; the PlayIDE name in the title bar is now the h1 (same look) | axe page-has-heading-one: 1 -> 0 |
| F002 | 1 | Toolbar | Undo/redo and run toolbars sat outside every landmark; the tool bar is now a named region | axe region: 2 nodes -> 0 |
| F003 | 1 | Screen designer | Record-attributes palette was a complementary landmark nested in main; now a labelled section | axe landmark-complementary-is-top-level: 1 -> 0 |
| F004 | 1 | Simulation / Run panel | Scrolling run logs could not be reached by keyboard; both logs now take focus and have a name | axe scrollable-region-focusable: 1 -> 0 (2 logs) |
| F005 | 1 | Requirements dialog | Dialog header was a second banner landmark; it is now a plain header row | axe landmark-no-duplicate-banner and landmark-unique: 2 -> 0 |
| F006 | 1 | Requirements dialog | The tab list held a non-tab Refresh button; Refresh now sits beside the tab list | axe aria-required-children: 1 -> 0 |
| F007 | 1 | Chat plan | Ripple, AI follow-ons and requirements headings skipped from h2 to h4; they now announce as level 3 | axe heading-order: 2 -> 0 |
| F008 | 1 | Command palette | The Ctrl+K search field removed its outline with no replacement; it now shows a 2 px accent underline when focused | focus indicator: none -> 2 px accent (WCAG 2.4.7) |
| F009 | 1 | Diagram tabs | Arrow keys, Home and End did nothing on any tab list; all tab lists now follow the WAI-ARIA tabs pattern | probe: ArrowRight/End move focus 0/2 -> 2/2 |
| F010 | 1 | Diagram tabs | Every tab was its own Tab stop (13 stops to cross the diagram and Systems tabs); now one stop per tab list (roving tabindex) | Tab presses to cross the 11 diagram tabs 11 -> 1 |

## Polishes

| # | Batch | Where | Change | Measure (before -> after) |
|---|---|---|---|---|
| P001 | 1 | Chat | Suggestion chips ("Add a state", ...) use the accent ink | text contrast 3.82:1 -> 5.44:1 (WCAG 1.4.3 AA) |
| P002 | 1 | Permissions | Transition names in the permission grid use the accent ink | text contrast 4.27:1 -> 6.08:1 |
| P003 | 1 | Permissions | Role column heads use the accent ink | text contrast 4.27:1 -> 6.08:1 |
| P004 | 1 | Review | "Low" risk pill uses the accent ink | text contrast 3.82:1 -> 5.44:1 |
| P005 | 1 | Chat / Review | "You" author pill uses the accent ink | text contrast 3.82:1 -> 5.44:1 |
| P006 | 1 | Status bar | "Previewing a plan" chip green darkened one step (same hue) | white text contrast 4.04:1 -> 5.08:1 |
| P007 | 1 | Status bar | Passing score chip uses the same darker green | white text contrast 4.04:1 -> 5.08:1 |
| P008 | 1 | Chat ripple | "~" and "⚠" marks in the ripple list use the warn ink | glyph contrast 3.89:1 -> 5.23:1 on hover wash |
| P009 | 1 | Checks | Failing check mark uses the warn ink | glyph contrast 3.40:1 -> 5.92:1 |
| P010 | 1 | What's missing | To-do mark uses the warn ink | glyph contrast 4.59:1 -> 5.62:1 on the page ground |
| P011 | 1 | Theme | Four near-identical warn inks (#8a5a00, #8a5a08, #8a5a0a, #8a5a12) replaced by one --warn token | distinct warn text colours 4 -> 1 (16 declarations) |
| P012 | 1 | Permissions | "assigned only" / "new" tags: text raised to the 11.2 px floor | font size 10.56 px -> 11.2 px |
| P013 | 1 | Title bar | Source status pill ("Source review required"): text raised to the 11.2 px floor | font size 10.88 px -> 11.2 px |
| P014 | 1 | Review & activate | Effect card counts: text raised to the 11.2 px floor | font size 10.88 px -> 11.2 px |
| P015 | 1 | Command palette | Kind tags (Command, State, Ask): text raised to the 11.2 px floor | font size 10.88 px -> 11.2 px |
| P016 | 1 | Components (C4) | Eyebrow label: text raised to the 11.2 px floor | font size 10.88 px -> 11.2 px |
| P017 | 1 | Components (C4) | "Open" drill-in hint on system nodes: text raised to the 11.2 px floor | font size 10.56 px -> 11.2 px |
| P018 | 1 | Review | Risk and change pills (High/Medium/Low, added/changed): text raised to the 11.2 px floor | font size 10.88 px -> 11.2 px |
| P019 | 1 | Screens flow | Role caption above each screen: text raised to the 11.2 px floor | font size 10.88 px -> 11.2 px |
| P020 | 1 | Screens flow | "+N more" overflow note: text raised to the 11.2 px floor | font size 10.88 px -> 11.2 px |
| P021 | 1 | Sequences | Scenario tags in the sequence list: text raised to the 11.2 px floor | font size 10.88 px -> 11.2 px |
| P022 | 1 | Chat / Activation | AI / You author pills: text raised to the 11.2 px floor | font size 10.88 px -> 11.2 px |
| P023 | 1 | Laws / Tests | "Show what it governs" and "Show on diagram" buttons: target raised to the 24 px minimum (WCAG 2.5.8) | target 152x23 -> 152x24 px |
| P024 | 1 | What's missing | Row heads ("State machine ready"): target raised to the 24 px minimum (WCAG 2.5.8) | target 247x22 -> 247x24 px |
| P025 | 1 | Screens palette | "On screen" chip buttons: target raised to the 24 px minimum (WCAG 2.5.8) | target 76x21 -> 76x24 px |
| P026 | 1 | Screen designer | Field move buttons (↑ ↓) and remove: target raised to the 24 px minimum (WCAG 2.5.8) | target 30x23 -> 30x24 px |
| P027 | 1 | Review | "Show me" buttons on review items: target raised to the 24 px minimum (WCAG 2.5.8) | target 75x21 -> 75x24 px |
| P028 | 1 | Chat plan | "Show me" buttons on plan steps: target raised to the 24 px minimum (WCAG 2.5.8) | target 70x21 -> 70x24 px |
| P029 | 1 | Chat ripple | Ripple list rows (each opens the changed view): target raised to the 24 px minimum (WCAG 2.5.8) | target 333x21 -> 333x24 px |
| P030 | 1 | Permissions | Role column-head buttons: target raised to the 24 px minimum (WCAG 2.5.8) | target 56x16 -> 56x24 px |
| P031 | 1 | Permissions | Transition buttons in the grid: target raised to the 24 px minimum (WCAG 2.5.8) | target 144x17 -> 144x24 px |
| P032 | 1 | Run panel | Trace steps and record links in the run panel: target raised to the 24 px minimum (WCAG 2.5.8) | target 312x17 -> 312x24 px |
| P033 | 1 | What's missing | "Update the tests" fix button: target raised to the 24 px minimum (WCAG 2.5.8) | target 121x23 -> 121x24 px |
| P034 | 1 | Review & activate | "Exact app and checker identities" disclosure: target raised to the 24 px minimum (WCAG 2.5.8) | target 804x15 -> 804x24 px |
| P035 | 1 | Review & activate | "Revision identities" and effect-group disclosures: target raised to the 24 px minimum (WCAG 2.5.8) | target 804x20 -> 804x24 px |
| P036 | 1 | Screen designer | "Accessibility (WCAG 2.2 AA)" disclosure: target raised to the 24 px minimum (WCAG 2.5.8) | target 546x16 -> 546x24 px |
| P037 | 1 | Shell | Pane splitters (left, chat, bottom panel, local app) grab 3 px either side of the 5 px line; the drawn line is unchanged | grab width 5 px -> 11 px (x4 splitters) |
