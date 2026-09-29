# Information architecture, navigation and command palette

Lane `lane/ux-research`, aspect `ia-navigation`. Date 2026-09-29. Status: proposed. Revision 2 after audit (2026-09-29; changes listed in section 16). Decision record: [HCI-ADR-0057](../../adr/0057-hci-ia-navigation.md). Task flows: [design/tasks/ia-flows.json](../../../design/tasks/ia-flows.json). Layouts: [design/layouts/nav-current.json](../../../design/layouts/nav-current.json) and [nav-proposed.json](../../../design/layouts/nav-proposed.json).

Labels used for every number: **PREDICTION** (model output), **MEASURED** (read from a file or tool that is named), **COUNT** (counted from source files), **ESTIMATED** (reasoned from CSS or from a design), **HYPOTHESIS**, **UNVERIFIED** (not confirmed, not built on). Nothing here measures users of the Studio. No user-benefit claim is made; section 13 is the study that would test one. Source ids S1 to S50 are in section 15. `L1` to `L7` are documents and files written by other lanes in this worktree, listed in section 15.

## 0. Decisions first

| # | Decision | Strongest evidence | Confidence |
|---|---|---|---|
| D1 | Three primary objects get a destination: **Changes** (change cases, including agent runs), **Model** (the ubiquitous-language tree and its lenses) and **Evidence** (claims, gaps, mapping). Agents, states, journeys, requirements, tests and personas are not destinations: agents are rows and a status count, the others are lenses and facets of one selected element. | Engineers seek by searching, browsing and tracing (S42); Linear keeps the human as assignee and the agent as delegate (S44); the persona file calls the agent an actor, not a persona | Medium |
| D2 | The four phase tabs are replaced by the three destinations plus a **scope switch** (Baseline or one case) and a persistent frame: tree sidebar, facet inspector, status bar. Every baseline capability keeps a home (table in section 4.3). | NN/g: tabs suit content the user need not see at the same time (S30); the baseline puts Impact on another tab from Change. Review keeps each operation beside its ripple and counts; claim detail stays one navigation away (4.4) | Medium |
| D3 | The frame is **stable**: top bar 40 px, sidebar 272 px, inspector 360 px, status bar 28 px at 1440x900. Each region has named slots whose position does not change between views. | Hick-Hyman needs stable positions (S1); Jakob's law (S33); WCAG 3.2.3 as guidance only, its applicability to a one-URL app is unclear (S10) | Medium |
| D4 | One **command palette**: Ctrl/Cmd+K, `/` opens it in command mode, a visible trigger in the top bar. It searches the current scope, shows its scope, ranks deterministically, lists blocked commands with the reason, and holds three command classes only (read, propose, job). Owner-only actions appear as **pointer rows** that move focus and never activate. | GitHub, VS Code, JetBrains, Superhuman palettes (S17, S19, S22, S21); class rule aligned with L1 | Medium |
| D5 | **Keyboard first**: APG tree, tablist and combobox patterns, roving tab stops (16 by design), focus that survives a re-render, character-key shortcuts that can be turned off (WCAG 2.1.4, Level A). | S7, S8, S9, S15, S48, S49; baseline defect F4 | Medium |
| D6 | **Deep links** are hash routes `#/scope/view/element?params` built from stable model ids, with `rev` for the exact case revision. No server change. The Decision surface has no URL of its own. A copied link never contains the session token. | GitHub permalinks pin a commit (S36); MDN History and fragment behaviour (S35); baseline server serves `/` only (F8) | Medium |
| D7 | **Wayfinding**: scope chip, breadcrumb path of the selection, tab title with the attention count, click-to-filter roll-up counts, lane counts as scent, and empty or not-found states that name what is missing. | NN/g breadcrumbs, scent, empty states (S39, S31, S40); Claude Code tab title (S23); Storybook status counts that filter the sidebar (S25) | Medium |
| D8 | **Menu budgets** follow the validity range of the laws, not folk numbers: destinations 3, lenses 6, tree siblings at most 12, tree depth at most 4, palette visible rows 8, attention groups 3. | Cockburn et al. fitted n from 2 to 12 (S1); Cowan 3 to 5 chunks held (S6); Miller (S5); NN/g 2 disclosure levels (S4) | Medium |
| D9 | **Predictions are reported as they came out.** On every task that both UIs support, the mouse paths of the proposal are inside the plus or minus 21 percent band. Under the Fitts profile it is slower by 0.36 to 0.39 s on T06 and T14 (PREDICTION, EXTRAPOLATED beyond the calibrated range; 0.00 s with constant P; T14 is a workaround comparator). The keyboard-only review path (T02-kbd, 5.40 s against 3.60 s) overlaps at the base constants and separates in 2 of 6 constant cells. No speed claim is made. The case for D1 to D8 rests on capability, visibility and standards, and is untested. | Section 10 | Medium for the arithmetic, low for any benefit |

What this document does not settle: shell dimensions beyond the interface in section 11, glyphs and colour, the internals of review chapters, the ripple lane, diagrams, the Decision surface and the tree structure itself. Each is another aspect; the assumption made about it is a row in section 11.

## 1. Baseline facts

Read from the repository or measured by another lane. I did not run a browser. Geometry in `nav-current.json` was **copied from the layout lane's Chromium measurement** (L4; the same values are in the layout lane's `design/layouts/current-*.json`, which I compared for the Evidence tab and the tab strip: identical). I first estimated it from the CSS; the estimate was within about 20 px vertically but up to 82 px off horizontally on text-width elements (the connection chip, the tabs, the action buttons), so I replaced it with the measurement. Revision 2 compared every element: 15 are identical to a measured element, 5 are bounding boxes of measured elements, 2 are clipped at the viewport; each element now has a `source` field and the file a provenance `note`. Not reproduced by me. Label: MEASURED, second-hand.

| Id | Fact | Kind | Source |
|---|---|---|---|
| F1 | Four buttons `01 / Change`, `02 / Impact`, `03 / Try`, `04 / Evidence & Decision`, numbered in workflow order. The fourth tab holds two jobs (read evidence, decide). The tab strip has no `role=tablist` and no `aria-selected`: the only ARIA in `index.html` is two `role="status"`, two `aria-label` and one `aria-live`. | COUNT | `index.html`; grep |
| F2 | `app.js` has no `keydown`, `keyup` or `addEventListener` (handlers are assigned as `onclick` and `onsubmit`). The only URL state is the launch token in the fragment, removed by `history.replaceState`. | COUNT | `app.js` |
| F3 | The current tab and the open case are JavaScript variables (`tab`, `current`). A reload returns to the create panel. | source reading | `app.js` |
| F4 | After every load, `cases()` calls `replaceChildren()` on the case list. A focused case button is destroyed and focus falls to the document. | source reading, not run | `app.js` |
| F5 | The tab strip starts at y 552 of 900 (61 percent). Hero and boundary text occupy y 124 to 420. | MEASURED (L4) | `design/layouts/current-change.json` |
| F6 | In the Evidence tab, Approve is at document y 1406 and the document is 1698 px tall; in the Change tab the option buttons are at y about 1162 and the document is 1863 px tall. | MEASURED (L4) | `design/layouts/current-evidence.json`, `current-change.json` |
| F7 | Words in the first viewport at 1440x900: start 126, Change 171, Impact 156, Try 155, Evidence 134. | MEASURED (L4) | `.tmp/current_measure.json` (`wordsVP`) |
| F8 | The server serves `GET /` and `/assets/app.js` and `/assets/app.css` only, with `Cache-Control: no-store` and a CSP without `font-src`. A fragment is never sent to the server. | COUNT | `interfaces/http.py` lines 61 to 63 and 80 to 82 |
| F9 | The launch URL is `http://127.0.0.1:<port>/#<token>`; the token is `secrets.token_urlsafe(32)`, an alphabet without `/`. The token is kept in `sessionStorage`, which is per tab (S34). | COUNT | `interfaces/cli.py` lines 73 to 74; `app.js` |
| F10 | The model API exposes states, transitions (role, guards, effects), journeys as strings, three technical claims and `human_understanding: UNKNOWN`. It has no test, persona or requirement objects. Those ripple rows are therefore "Not analysed" today, not empty. | source reading | `application/compiler.py`; L1 F7, F10 |
| F11 | The fixture domain has states Draft, Submitted, Recommended, Approved, Rejected and transitions TR-SUBMIT, TR-RECOMMEND, TR-APPROVE, TR-REJECT, TR-REVISE with roles Teacher and Registrar. The baseline-to-candidate diff has four operations: ADDED state Recommended, ADDED TR-RECOMMEND, MODIFIED TR-APPROVE and TR-REJECT (source Submitted to Recommended). Layout labels use these real names. | COUNT | `examples/excursion-baseline.json`, `excursion-candidate.json` |
| F12 | Only two typed edits execute (enable recommendation, set rejection source) under a frozen vocabulary; other edits are refused with a reason. | COUNT | ADR-003; `domain/models.py`; L1 F9 |

## 2. Primary objects and where they live

| Object | What it is (source) | Surface | Reached by | Budget |
|---|---|---|---|---|
| Change case | Aggregate linking request, alternatives, candidate, receipts, decision (ARCHITECTURE.md). Parallel agent proposals are parallel cases (L1 F6) | **Changes** destination: inbox rows grouped by whose turn; Review view per case | Top-bar tab, `g c`, status-bar attention count, palette, deep link | Groups: Needs you, Working, Ended (3) |
| Agent run | A proposal is a view over a case (L1 A3); the agent has no goals the UI serves and no authority | A row in Changes with a lane label and state word; a count in the status bar; the composer opened by Ask AI. **Not a destination** | Same as change case | none |
| Language and DDD structure | Ubiquitous-language terms in context, aggregate, entity or value, term (REQ dossier §5 #1; persona P2) | **Model** destination: the tree is the sidebar spine in every view | Sidebar, palette, breadcrumb | Depth at most 4; siblings at most 12 |
| State, transition | Workflow definition (F11) | Model, lens States (diagram, rule table, Run preview mode) | Lens tab, tree selection, lane row | 1 lens |
| Journey | Kernel journeys (strings today, F10) | Model, lens Journeys | Lens, lane row | 1 lens |
| Requirement, test, persona | Model kinds the kernel does not analyse today (F10) | Model lenses Requirements, Tests, Personas; facet rows in the inspector lane | Lens, lane row, palette prefix | 3 lenses |
| Evidence | Receipts and claims with bound, per subject dimension | **Evidence** destination: Claims (default) and Mapping; counts in the status bar on every view | Top-bar tab, `g e`, status-bar count, lane row | 2 views |
| Concept-to-code mapping | Concept, symbol, last check, drift (SYNTHESIS S20) | Evidence, view Mapping; lane row Code | Segmented control, lane row | 1 view |
| Decision (approve, apply) | Local decision bound to the exact revision (ARCHITECTURE.md) | The **Decision surface**: opened only by a user activation of Decide... in the Review header | Button in Review | 1 surface |

Why agents are not a destination: L1 D2 already specifies one inbox row per agent run, grouped by turn (Claude Code and Gerrit precedents, S23, S24). That inbox is the Changes home. A separate Agents page would create a second list of the same objects. Cursor's Agents Window consolidates agents in one sidebar (S43); the Studio's equivalent is the Changes list.

Why tests, personas, requirements are lenses and facets: a review asks how they relate to one selected element (facet lane, S27), and a QA engineer asks for all of one kind (lens). Both are served by one model and one selection (Ilograph's perspective switch over one set of resources, S29).

## 3. The frame and its stable slots

```
top bar 40   EIJA Studio  Changes  Model  Evidence    Case 4f3a r3 v        [Search or run...  Ctrl K]        offline
+-----------------+-----------------------------------------------+------------------------+
| Filter model    | Let teachers sign off excursions    [Decide...]| Recommended  state     |  title 32 | action slot
| Excursion       | Excursion > Recommended                        | Persona       n        |  crumb / lens tabs
|   Draft         | Core  n                                        | Requirement   n        |
|   Submitted     |   ADDED    state Recommended   n n n UNKNOWN  | State         n        |
|   Recommended + |   ADDED    action Recommend    n n n UNKNOWN  | Journey       n        |
|   Approved      | Follows from core  n                           | Test          n        |
|   Rejected      |   MODIFIED action Approve      n n n UNKNOWN  | Code          n        |
|   Teacher       |   MODIFIED action Reject       n n n UNKNOWN  | Evidence      n        |
|   Registrar     | Other  n                                       | Not analysed  n items  |
|   Audit effects | n formatting-only edits hidden, show           | Ask AI...   Source view|
+-----------------+-----------------------------------------------+------------------------+
status 28   n UNKNOWN  n FAIL  n CONFLICT  n STALE  n NOT_RUN  n PASS     n need you, n running   Run verification   VERIFIED
```

Sketch of the Review view at 1440x900. `n` stands for a count the kernel supplies; no invented figures. Row text uses the real fixture names (F11). Widths: sidebar 272, main 808, inspector 360.

| Slot (id prefix) | Region | Geometry at 1440x900 | Holds | Stays constant across views |
|---|---|---|---|---|
| `tb-dest-*` | Top bar | 40 px tall, x 128 to 384 | Three destination links, `aria-current` on the active one | Position, order, labels |
| `tb-scope` | Top bar | 320 x 28 | Scope: `Baseline v{n}` or `Case {id} r{n}`, a menu of Baseline and open cases | Position |
| `tb-palette` | Top bar | 400 x 28 | The palette trigger: "Search or run..." and the key | Position |
| `tb-provider` | Top bar | 120 x 28 | Provider and egress state (offline, or "egress on") | Position |
| `sb-filter`, `sb-row-*` | Sidebar | 272 wide; rows 28 tall | Language tree with three filter modes; one status glyph per row; change mark in Review | Same tree in every view; only marks change |
| `main-title`, `main-action` | Main header | title 608 x 32; action 152 x 32 at x 912 | Case title (Review), request field (New change), element name (Model). **The primary action slot**: Decide... (Review), Run verification (Evidence), New change... (Changes), Run preview (Model, States) | The slot and its position |
| `main-crumb`, `main-lens-*`, `main-seg-*` | Main sub-header | y 84, 32 tall | Location path of the selection; lens tablist (Model) or Claims and Mapping (Evidence) | Position |
| `main-group-*`, `main-row-*` | Main list | rows 40 tall from y 156 | Chapters and operations (Review); inbox rows (Changes); claims (Evidence); element rows (Model lists) | Row anatomy per view |
| `insp-*` | Inspector | 360 wide | Facet lane in a fixed order: Persona, Requirement, State, Journey, Test, Code, Evidence; then Not analysed; Ask AI...; Source view; owner controls (Edit..., Clear by decision...) when they apply | Order and position |
| `st-*` | Status bar | 28 tall | Counts by evidence status, UNKNOWN first and PASS last; attention count; job control; case stage | Position; counts are buttons that filter |

Rules:

1. **Slots do not move.** A view changes the content of a slot, never its place (WCAG 3.2.3, S10). This is also the condition under which Hick-Hyman applies to an expert (S1).
2. **Chrome recedes.** Regions are separated by one hairline, not by cards. Bare text controls (status counts, scope, Source view) carry no border. Container counts are in section 12.
3. **Inspector and sidebar collapse.** Ctrl/Cmd+B toggles the sidebar (S19). The inspector toggles from the palette and from a header button. Below 1280 px wide the inspector is hidden by default and opens over the list column, not over the tree; the minimum main width is 560 px (ASSUMPTION for the layout aspect, section 11).
4. **The decision surface replaces the main and inspector regions**, keeps the top bar and status bar, and is left with Esc. It is the Stripe FocusView idea (a blocking mode for a start-to-finish task, S26) without a new elevation.

## 4. Destinations, lenses and views

### 4.1 What each destination is

| Destination | Default view | Sidebar | Main | Inspector | Primary action |
|---|---|---|---|---|---|
| Changes | Inbox: Needs you, Working, Ended (L1 D2 row anatomy); first Needs you row focused | Tree of the baseline (scope Baseline), no row selected. Selecting a node filters the inbox to cases whose diff touches that element; a line above the list names the filter with a clear control; the element goes in the URL (`#/changes/<element>`); a C0 filter, nothing else | Groups and rows; a case opens as Review | Summary of the focused row | New change... |
| Changes, case open (Review) | Chapters Core, Follows from core, Other with typed operations labelled ADDED, MODIFIED, REMOVED; first operation selected | Tree with change marks; filter mode "changed only" | Operation rows with ripple counts; "n formatting-only edits hidden" | Facet lane of the selected operation | Decide... |
| Model | Language lens for the selection, or the whole context | Tree | Lens content: Language, States, Journeys, Requirements, Tests, Personas | Facet lane | Run preview (States) |
| Evidence | Claims for the selection scope, with counts by status and the four-slot coverage row (owned by the evidence aspect) | Tree with status glyphs | Claim rows; Mapping table | Selected claim: bound, covered, assumed, NOT covered | Run verification |
| Decision surface | Exact revision, every UNKNOWN, questions, acknowledge, Approve, then separately Apply | Collapsed | Owner decision content (decision aspect) | Collapsed | none in the palette |

Lens switch and Claims or Mapping are **in-page tabs** (a `tablist`, APG S48). Destinations are **links** with `aria-current` and a different look (underline) so the two are not mixed (S30).

### 4.2 Selection drives everything

One selection, one id (the selection bus, interface I-N1 of L3). The tree, the lane, the lenses, the canvas and the lists subscribe to it. Selecting in any of them updates the others in the same frame and calls `history.replaceState`. Element ids are stable model ids (`Recommended`, `TR-REJECT`), never row indexes. With nothing selected, a lens shows the whole context. This is REQ dossier decision 1 (one tree, one selection, everything else a facet) and Jama's "selected item plus neighbours" (S27).

### 4.3 Where each baseline capability goes

| Baseline | Proposal | Change of steps |
|---|---|---|
| Case list (aside) | Changes inbox and the scope menu | grouped by turn |
| `01 / Change`: request, Ask for interpretations, alternatives, Select this meaning, typed edit, Save, Discard | Changes home (New change...); Review of a DRAFT or PROPOSED case shows the alternatives as rows (BLOCKED ones stay listed with the reason); typed edit is an owner control in the inspector; Save and Discard in the case header menu | select-all and the New case click disappear |
| `02 / Impact`: state flow, rule table, impact summary, layout-only edit | Review ripple lane (impact) and Model, States lens (flow, table, layout) | ripple is beside the change |
| `03 / Try`: runtime preview, actor, actions, audit | Model, States lens, mode Run preview; observations appear in Evidence | mode, not a tab |
| `04 / Evidence & Decision`: claims, UNKNOWN box, questions, Approve, Apply, Export | Evidence, Claims (with the UNKNOWN count always in the status bar); Decision surface via Decide...; Export in the case header menu | evidence and decision are separate places; the Decision surface shows every UNKNOWN itself, so it does not depend on the Evidence destination (4.4) |
| Check provider connection | `tb-provider` chip opens the provider check | one step |
| Hero, boundary and footer text | Removed from the primary viewport. The synthetic-domain and single-owner statement moves to the shortcuts and about sheet and to the first-run empty state | words leave the first screen |

### 4.4 What Review shows together, and what is one step away

| Visible together in Review at 1440x900 (`nav-proposed.json`, view `review`) | One navigation away |
|---|---|
| Operation rows with ADDED or MODIFIED, ripple counts and an UNKNOWN count per row; chapter counts | Claim detail: bound, covered, assumed, NOT covered (Evidence destination, or the Evidence lane row) |
| Facet lane of the selected operation: a count and a gap glyph per kind, "Not analysed" on its own line | Lens content (States diagram, Journeys) in Model |
| Status roll-up: six counts, UNKNOWN first | The Decision surface (Decide...), which lists every UNKNOWN itself |

The NN/g tabs test (S30) is met for change and ripple and only partly for evidence: the counts travel with the change, the claims do not. Evidence and Decision stay apart because the Decision surface is a blocking owner step with its own UNKNOWN list (P2, I1), not because evidence may be out of sight when deciding. Whether reviewers need claim detail beside the operation is study question 9 (section 14).

## 5. Scope switch

The scope answers "what am I looking at: the applied model or a candidate?". It is the first datum of wayfinding and the root of the breadcrumb, as the branch is in a code host.

| Scope | Views available | Notes |
|---|---|---|
| `base` (Baseline v{n}) | Model, Changes | Evidence for the baseline is whatever receipts the kernel returns; a claim with none reads UNKNOWN or NOT_RUN. Whether the kernel returns receipts for an applied baseline is an open question (section 14) |
| `case/<id>` | Review, Model, Evidence, Decision | Candidate model; `rev` names the case revision |

Switching scope keeps the selected element id when it exists in the target scope and says so when it does not.

## 6. Command palette

### 6.1 Invocation and shape

| Item | Design | Source |
|---|---|---|
| Open | Ctrl/Cmd+K anywhere (a modifier chord: unconditional). Click on the top-bar trigger. `/` when focus is not in a text field opens the palette in **command mode** (a character key: switchable, section 7). | GitHub opens its palette with Ctrl+K or Cmd+K (S17); `>` is command mode in GitHub (S17), while GitHub's `/` prefix searches files and repositories, so `/` for commands is L1's choice, not a GitHub convention; the VS Code `>` prefix is UNVERIFIED (not on the page opened, S19) |
| Command mode prefixes | A leading `/` or `>` restricts results to commands. Slash aliases from L1: `/agents`, `/propose`, `/ask`, `/why`, `/unknowns`, `/verify`, `/stop`, `/source`, `/history` | L1 slash table |
| Dialog | Modal dialog (APG, S9) containing a combobox with a listbox popup (S8): DOM focus stays in the input, `aria-activedescendant` marks the option. Tab wraps inside. Esc closes and focus returns to the invoker. | S8, S9 |
| Scope line | First row of the dialog states the scope: "Searching case 4f3a r3, selection Reject: n elements, n commands". Backspace on an empty query widens it: selection subtree, then scope, then all scopes. | GitHub shows the location at the top left and scopes suggestions to it (S17) |
| Rows | One line: kind word, name, path, status glyph and word, shortcut or slash alias. 32 px tall, at most 8 visible. "n of N" is announced in a live region. | Superhuman shows the shortcut in results (S21); JetBrains matches synonyms (S22). A Zed precedent from the DEV dossier was not re-opened: UNVERIFIED, not relied on |
| Empty query | "Recent" (at most 3, this session only) then "For the selection" (at most 5). No frequency learning and no telemetry in v1. | HYPOTHESIS |

### 6.2 Ranking (deterministic)

1. Exact id or name, 2. name prefix, 3. word prefix, 4. in-order subsequence (fuzzy), 5. synonym from a shipped table (for example "sign off" finds the Approve action element). Within a rank: selection subtree first, then recently visited, then element kinds before commands (commands first in command mode), then alphabetical. Superhuman lists fuzzy matching, synonyms and context filtering as principles (S21); JetBrains matches synonyms (S22). The synonym table is data, reviewable in a diff.

### 6.3 Command classes (the safety rule)

The classes are those of the AI-interaction aspect (L1 section 3). The palette registry accepts three:

| Class | Meaning | Examples in the palette |
|---|---|---|
| C0 read | Navigate, view, filter, copy a link, open a source view. Changes no model and no evidence | Go to Model; Show States; Filter to UNKNOWN; Copy link to this view |
| C1 propose | Opens the composer. Marked "provider call". Per-request consent (I8) is inside the composer, never in the palette | Ask AI to propose at selection... |
| C2 job | Starts or stops a kernel check that writes evidence but decides nothing | Run verification; Stop; Run preview |

Everything else is **absent** from the registry: approve, apply, take, refuse, undo, discard, clear suspect, select meaning, typed edits, layout changes. Typing one of these shows a single **pointer row**: "Approve is an owner action in the Decision surface: go to Decide..." Activating a pointer row moves focus to that control (or navigates to the view that holds it) and does nothing else. A pointer row never opens the Decision surface; only a user activation of the Decide... button does (L1 layer L3).

Registry contract (interface for every aspect that contributes commands):

```
register({ id, name, alias?, class: "C0" | "C1" | "C2",
           available(selection, scope) -> { state: "enabled" | "blocked" | "ai", reason? },
           run(context) })
pointer({ match, label, focusTarget })    // moves focus only
```

`register` throws for any other class. The test (section 13) walks the registry and the source of every handler.

A domain collision to design out: the fixture has an action element named **Approve** (the registrar's transition). Element results are navigation, shown with a kind word ("action") and a different row style from commands; no command row is ever named Approve or Apply.

### 6.4 Command inventory (34)

| Group | Commands | Class | Alias or key |
|---|---|---|---|
| Go (5) | Go to Changes, Go to Model, Go to Evidence, Switch scope..., Go to first Needs you item | C0 | `g c`, `g m`, `g e`, `g s`; `/agents` |
| Show (9) | Show Language, States, Journeys, Requirements, Tests, Personas; Show Claims; Show Mapping; Define term... (content aspect, L7) | C0 | none; lens keys 1 to 6 only while the lens tablist has focus |
| Filter (7) | Filter to UNKNOWN, FAIL, CONFLICT, STALE, NOT_RUN, changed only; Clear filter | C0 | `/unknowns` for the first |
| Run (3) | Run verification, Stop, Run preview | C2 | `/verify`, `/stop` |
| Ask (3) | Ask AI to propose at selection..., Ask AI a question..., Explain refusal | C1, C1, C0 | `/propose`, `/ask`, `/why` |
| View (7) | Toggle sidebar, Toggle inspector, Copy link to this view, Show source, Show history, Show keyboard shortcuts, Character shortcuts on or off | C0 | Ctrl/Cmd+B; `/source`, `/history`; `?` |

Names are verb first, one to four words (a design rule of this document; the Raycast and VS Code naming rules cited in the DEV dossier were not re-opened: UNVERIFIED, not relied on). The 34 commands sit in six groups; the palette never shows all 34 unfiltered at once (8 rows).

### 6.5 States, empty and failure

| Situation | What the palette shows |
|---|---|
| Command available | Plain row |
| Command blocked | The row stays listed with the word BLOCKED and the kernel reason, for example "no candidate" or "UNSUPPORTED_EDIT (ADR-003)". Nothing is silently hidden. |
| AI command | Row carries "provider call"; when egress is off the reason says so |
| No match | "No match in case 4f3a r3 (41 elements and 34 commands searched). Backspace widens the scope." The count is the real number searched. It never says the thing does not exist. |
| Kernel or API error | The error code and message the kernel returned |

### 6.6 Latency classes

Palette open is the **direct** class (limit 100 ms, target 50 ms). Results after a keystroke are the **view** class (limit 1000 ms, target 200 ms). Both come from the motion aspect (L2). The index is built from the last case payload on the client; no request is made per keystroke (design; unmeasured, UNVERIFIED).

### 6.6a Why not chat-first

A conversation as the primary navigation was considered (option E in the ADR). Navigation must be deterministic and work offline, and every provider call needs a startup flag and per-request consent (I8), so the palette stays a local index with a separate, marked AI command. This is a design reason, not a finding about users.

## 7. Keyboard model

| Key | Action | Modifier or character | Precedent |
|---|---|---|---|
| Ctrl/Cmd+K | Open palette | modifier | GitHub (S17) |
| `/` | Open palette in command mode | character | L1; GitHub uses `/` or `S` to focus search (S18) |
| `?` | Shortcut sheet, searchable | character | GitHub `?` dialog (S18) |
| `g` then `c`, `m`, `e`, `s` | Go to Changes, Model, Evidence, scope menu | character sequence | GitHub `g` then `c`, `i`, `p` (S18) |
| Ctrl/Cmd+B | Toggle sidebar | modifier | VS Code (S19) |
| Esc | Close the palette or a menu; leave the Decision surface. Nothing else. | none | APG dialog (S9) |
| Arrows, Home, End, Enter, type-ahead | Tree navigation, expand, collapse, open | none | APG tree (S7) |
| Left, Right, Home, End | Lens and Claims or Mapping tabs, automatic activation | none | APG tabs (S48) |
| Up, Down, Enter | Rows in Changes, Review, Evidence lists | none | APG listbox idea (S8) |
| F2 | Rename in the tree | none | HYPOTHESIS: language aspect convention; the APG tree defines no rename key |

**WCAG 2.1.4 (Level A, S15).** Single character shortcuts (`/`, `?`, `g` sequences, lens digits) must have a way to turn off, or remap, or be active only on focus. Design: they are inactive while any text field or the composer has focus; the shortcut sheet and the palette command "Character shortcuts on or off" turn them all off; the choice is stored in `localStorage` inside try and catch and the default is on. The modifier chords (Ctrl/Cmd+K, Ctrl/Cmd+B) are outside the criterion. If character shortcuts are off, the palette still reaches everything, so nothing depends on them (WCAG 2.1.1, S16).

**Conflicts to test.** Ctrl+K and Ctrl+B are used by browsers or extensions in some configurations. The plan is one smoke test per browser (one Chromium at a time on this PC), not a claim. Ctrl+Shift+P, the VS Code key, is not used because browsers reserve it in some configurations (UNVERIFIED).

**Tab stops (COUNT from the design).** 16: skip link 1; top bar 4 (destinations as one roving group, scope, palette, provider); sidebar 2 (filter, tree as one roving group); main 3 (action, view tablist when present, list as one roving group); inspector 3 (lane as one roving group, Ask AI, Source view; plus Edit... when the selection has a typed edit); status bar 3 (counts as one toolbar, attention, job). Roving groups follow the tree, tabs and toolbar patterns (S7, S48, S49).

**Focus rules.** (1) A re-render never destroys the focused element; focus is restored by stable id (baseline defect F4). (2) After navigating, focus moves to the first row of the main list (Changes: first Needs you row) and the change is announced in the existing polite live region. (3) The palette is a modal dialog and returns focus. (4) Sticky top and status bars must not hide a focused element: `scroll-padding` of 40 px top and 28 px bottom (WCAG 2.4.11, S12).

### 7.1 Familiar conventions reused, and where this design departs

Jakob's law: users prefer a product to work like the ones they already know (S33). It is only as good as the reference set; this one is developer tools I chose (GitHub, VS Code, Linear, Storybook, Gerrit, Claude Code), and it is untested with the Studio's users.

| Convention | Reference | Use here | Departure |
|---|---|---|---|
| Ctrl/Cmd+K opens a palette with a location and prefixes | GitHub (S17) | Same key, scope line, `>` prefix (`/` means commands here, unlike GitHub) | Owner actions are pointer rows; a search states what it searched |
| `g` then a letter goes to a section; `?` lists shortcuts | GitHub (S18) | `g c`, `g m`, `g e`, `g s`; `?` | Switchable for WCAG 2.1.4 |
| Ctrl/Cmd+B toggles the side bar | VS Code (S19) | Same | none |
| Named regions, status bar | VS Code (S19) | Top bar, sidebar, main, inspector, status bar | The status bar holds evidence counts that filter |
| Status counts that filter the sidebar | Storybook testing widget (S25) | Roll-up buttons | Six evidence statuses, UNKNOWN first, PASS last |
| Attention list: whose turn | Gerrit, Claude Code agent view (a terminal UI in research preview) (S24, S23) | Needs you, Working, Ended; tab-title count | No AI in an approving slot |
| Tree with arrow keys, type-ahead | APG (S7) | Language tree | Status glyph and change mark per row |
| Location path | Code hosts; NN/g (S39) | Breadcrumb of the selection | Hierarchy of the model, not of files |

Not adopted: an activity bar of icons (icon-only controls need labels), editor tabs that hold many open views (option D in the ADR), Ctrl+Shift+P (browser conflicts, UNVERIFIED), any auto-approve or "allowed" mode.

## 8. Deep links and history

### 8.1 Grammar

```
route    = "#/" [ "changes" [ "/" element ] ]    ; element filters the inbox
         | "#/" scope "/" view [ "/" element ] [ "?" params ]
scope    = "base" | "case/" case-id
view     = "review"                       ; case scope only
         | "model/" lens                  ; lens = language | states | journeys | requirements | tests | personas
         | "evidence/" ( "claims" | "mapping" )
element  = stable model id, percent-encoded
params   = rev=<n>                        ; case revision the link was made from
         | f=<unknown|fail|conflict|stale|notrun|changed>   ; tree and list filter
         | fm=<highlight|path|flat>                            ; filter mode of the language aspect, default path
         | mode=run                       ; Model, States: Run preview
```

Examples (ids from the fixture, case id a placeholder):

| Link | Meaning |
|---|---|
| `#/` | Changes inbox, first Needs you row focused |
| `#/case/<case-id>/review?rev=3` | Review of revision 3 |
| `#/case/<case-id>/model/states/TR-REJECT?rev=3` | The Reject transition in the States lens |
| `#/case/<case-id>/evidence/claims?f=unknown` | Claims filtered to UNKNOWN |
| `#/base/model/language/Recommended` | The term Recommended in the baseline |

### 8.2 Rules

| Rule | Reason |
|---|---|
| Hash routes, not path routes. The server serves `/` only (F8); a path route would need a fallback route in `http.py` and a test, a security-relevant change. A fragment is not sent to the server. | F8; no server change |
| A hash starting `#/` is a route; anything else is the launch token. The token alphabet has no `/` (F9). After the token is read it is replaced with `#/` (the baseline replaces it with an empty fragment). | Disambiguation without a server change |
| Push a history entry when scope, destination, view, lens or an opened case changes; replace it when only the selection or a filter changes. Assigning a different `location.hash` creates an entry and fires `hashchange`; assigning the same value does not; `pushState` fires no `hashchange` (S35). One `hashchange` handler renders; in-memory entries use `pushState` and a `popstate` handler. | Back and Forward step through places, not through every arrow key |
| **The Decision surface has no URL.** Decide... pushes an in-memory history entry at the Review URL; Back closes it; a reload lands on Review with Decide... focused. | Opening it needs a user activation of the button (L1); a link cannot open it |
| A link states the revision it was made from. If the case is now at a later revision the page says "This link names revision 3; the case is at revision 5" and offers revision 5. No silent rebase (I7, ADR-012). GitHub pins a link to a commit while a branch link moves (S36); `rev` is that idea, and a link without `rev` moves. | Honest staleness |
| Unknown element id: "No element X in case 4f3a r5. This change REMOVED it" when the diff says so, otherwise "not found". Unknown case: "Case not found." | Named, never blank (S40, S41) |
| `Copy link to this view` builds `origin + pathname + hash` and never includes the token. | The token is a credential |
| Filter and scoping mode are in the URL, so "the gaps list" can be shared. Palette state, expansion state and scroll are not. | Shareable answers |
| `document.title` is `<selection> · <scope> · EIJA Studio`, prefixed `n need you · ` when n is above 0 (99+ above 99). | Claude Code agent view puts the awaiting-input count in its terminal tab title (S23; a terminal, research preview) |

### 8.3 The token problem for a second tab (open, not decided)

`sessionStorage` is per tab, and a new tab or window starts with an empty one (S34; a page opened with an opener may start with a copy, but ordinary links open without an opener in current browsers, UNVERIFIED). A pasted deep link in a new tab therefore has no token and the API answers `SESSION_REQUIRED`. Options for the security lane, none tested: (a) the user opens the launch link, then pastes the route; (b) a same-origin handoff between tabs; (c) keep the state as it is and say so in the sheet. This design does not put the token in a link. Deep links work today for reload, Back and Forward in the same tab.

## 9. Wayfinding and information scent

| Cue | Where | Rule | Source |
|---|---|---|---|
| Current destination | Top bar | Underline plus bold plus `aria-current`; at least two indicators | NN/g tabs (S30) |
| Scope | Top bar | Always visible; the root of the path | code-host branch analogy; GitHub palette location (S17) |
| Location path | Main sub-header | Hierarchy, not history: Context > Aggregate > Entity > Term; the last item is not a link; helpful most when a deep link lands here | NN/g breadcrumbs (S39) |
| Whose turn | Status bar count, Changes groups, tab title | "n need you, n running"; a turn word per row | Gerrit "Your turn" (S24); Claude Code groups and title (S23) |
| Roll-up | Status bar | Counts by status, UNKNOWN first, PASS last; each is a button that filters the tree and list (click again to clear) | Storybook's testing widget: pressing the failure count filters the sidebar (S25) |
| Scent on rows | Tree, lists, lane | One status glyph per row; counts and kinds beside each lane row; ADDED, MODIFIED, REMOVED on operation rows; labels of one or two words | Scent is the estimate of value before the click (S31); label rules (S30); DOORS Next admins hide per-row icons to cut clutter (REQ dossier §2.2) |
| Gaps | Lane | A required link that is missing is drawn as a gap glyph with the word; "Not analysed" is a separate line and never drawn like "unaffected" | Jama's missing-link mark (S27); P1 |
| Empty states | Every list | Name what is missing in domain words and give one verb-first action: "No change cases yet. Review the sample change." | NN/g and Primer empty states (S40, S41) |
| Where did I come from | Esc, Back | Esc closes overlays and the Decision surface only; Back returns to the previous place | History rules, section 8 |

**Filter scoping (Notion precedent).** Notion offers three explicit modes when filtering sub-items (parents only, parents and sub-items, sub-items only; S28). The tree filter uses the three named modes of the language aspect (L6): Highlight, Path (matches with their ancestors, the default) and Flat (matches only), plus its fuzzy toggle. The mode is visible next to the filter and in the URL.

## 10. Quantitative model

Everything in this section is a **PREDICTION**. KLM covers expert, error-free, routine tasks and not reading, learning or errors; its RMS error is about 21 percent (S2). Constants are population and device specific.

### 10.1 Menu budgets from the validity range of the laws

Hick-Hyman for practised users with stable item positions: T = 0.24 + 0.08 log2(n) s, R2 0.98, fitted on menus of 2, 4, 8 and 12 items with eight participants. Search of unfamiliar or moving items: T = 0.30 + 0.08 n s, R2 0.99 (S1). Hick-Hyman applies to stable positions; typed search is not modelled. The palette row below is the empty-query list or a visual scan of results, not typed search.

| Menu | n | Expert T (s) | Novice T (s) | Limit source |
|---|---|---|---|---|
| Destinations | 3 | 0.37 | 0.54 | baseline has 4 tabs: 0.40 and 0.62 |
| Lenses | 6 | 0.45 | 0.78 | S1 range |
| Attention groups | 3 | 0.37 | 0.54 | chunk limit |
| Palette rows visible | 8 | 0.48 | 0.94 | S1 range |
| Tree siblings, maximum | 12 | 0.53 | 1.26 | top of the fitted range |

**Reading.** Going from 4 baseline tabs to 3 destinations saves 0.033 s for an expert and 0.08 s for a novice. That is far inside the band and is **not** a reason for the change. What the laws contribute is a cap: keep every menu inside 2 to 12 items so the model applies. A flat list of 64 commands is outside the fitted range and no time is predicted for it; the palette avoids the case by search and by 6 groups. Miller's absolute-judgment span is about 6 to 7 categories and memory span about 7 chunks; Cowan finds 3 to 5 chunks when rehearsal and grouping are blocked (S5, S6). The limit is about what must be **held in mind**, not about visible items, so it caps the review summary (at most 4 top-level chunks, the review aspect) and not the length of a tree.

### 10.2 KLM flows

Method. Flows are in `design/tasks/ia-flows.json`; every total can be recomputed by hand from that file and the layouts (my script is untracked scratch in `.tmp/`). M 1.35 (the top of Kieras's 0.6 to 1.35 s range; he recommends 1.2), K 0.20 (average skilled typist, 55 wpm), P 1.10 without geometry, H 0.40, B 0.10 (Kieras S50, a tutorial by a KLM author based on Card, Moran and Newell 1983; the book was not opened). Kieras counts B once for a press and once for a release; these flows use one B per click on both sides, so a delta understates by 0.1 s per extra click on the side with more clicks (T02: -1.40 would be -1.50), R 200 ms for a view change and 300 ms for a local API round trip (the motion aspect's class targets; unmeasured). With geometry, P is Fitts in the Shannon form MT = 0.37 + 0.13 log2(D/W + 1) s, D the centre-to-centre distance, W the smaller side (Cockburn et al. use the same form and constants for menu pointing, R2 0.93, S1; the smaller-side rule is my assumption). The constants were calibrated on vertical pointing down a 16-item menu of 130x22 px items with a mouse by 8 right-handed graduate CS students, so D up to about 340 px and ID up to about 4.0 bits (derived from the item size; distances are not stated in the paper). 22 of the 34 Fitts terms in these flows have D above 350 px and 11 have ID above 4.0 (COUNT): the Fitts columns below are **EXTRAPOLATED** and the constant-P columns are the primary result. The pointer starts at (720, 450), the same origin the canvas lane uses. One M opens each cognitive unit and one precedes each variable string, the same rule on both sides. Provider, verification and fixture waits are excluded because they are the same on both sides. Content steps owned by other aspects (consent checkbox, questions, Approve, Apply) are identical constant-P steps on both sides.

| Task | Current, const P | Current, Fitts P | Proposed, const P | Proposed, Fitts P | Delta const | Delta Fitts |
|---|---|---|---|---|---|---|
| T01 create case, choose meaning | 18.90 | 18.08 | 17.50 | 17.29 | -1.40 (-7%) | -0.79 (-4%) |
| T02 review by meaning (mouse) | 5.60 | 4.96 | 4.20 | 3.86 | -1.40 (-25%) | -1.10 (-22%) |
| T02-kbd review by meaning (keyboard) | 5.40 | 5.40 | 3.60 | 3.60 | -1.80 (-33%) | -1.80 (-33%) |
| T03 see the ripple | 4.30 | 3.93 | 4.10 | 3.62 | -0.20 (-5%) | -0.31 (-8%) |
| T04 edit state, non-dragging path | 8.20 | 7.83 | 6.60 | 6.60 | -1.60 (-20%) | -1.23 (-16%) |
| T05 edit the language tree | not supported | not supported | 9.20 | 8.66 | | |
| T06 run and read evidence | 5.30 | 4.56 | 5.30 | 4.93 | 0.00 (0%) | +0.36 (+8%) |
| T07 inspect a counterexample | not supported | not supported | 6.10 | 5.84 | | |
| T08 approve and apply | 18.65 | 18.16 | 18.45 | 18.24 | -0.20 (-1%) | +0.07 (0%) |
| T09 find anything (workaround comparator) | 6.30 | 5.93 | 5.30 | 5.30 | -1.00 (-16%) | -0.63 (-11%) |
| T10 first run (steps, not a time claim; workaround comparator) | 13.45 | 12.40 | 4.10 | 3.89 | -9.35 | -8.51 |
| T11 resolve a stale item | not supported | not supported | 12.20 | 11.88 | | |
| T12 map a concept to code | not supported | not supported | 5.50 | 5.14 | | |
| T13 ask AI at an element | not supported | not supported | 14.30 | 13.70 | | |
| T14 find gaps (workaround comparator) | 4.10 | 3.61 | 4.10 | 4.00 | 0.00 (0%) | +0.39 (+11%) |

Seconds. "Not supported" is an empty current flow, not zero seconds (`design/brief.json` marks T13 partial because whole-request interpretations exist; the element-scoped path is absent). **Workaround comparator**: `design/brief.json` marks T09, T10 and T14 absent in the baseline; their current flows (find-in-page on one tab, the create panel, scanning claim cards) do not reach the same outcome, so those deltas are not like-for-like costs. T10 is a novice task, KLM does not apply, and the useful figure is the step count: 5 point-and-click pairs in the baseline against 1 in the proposal, which needs an application feature (UNVERIFIED, T10 assumptions).

**Worked example, T02 with constant P.** Current: M 1.35 + P 1.10 + B 0.10 + R 0.30 (open the case) + P 1.10 + B 0.10 + R 0.20 (Impact tab) + M 1.35 = 5.60 s. Proposed: M 1.35 + P 1.10 + B 0.10 + R 0.30 + M 1.35 = 4.20 s. With Fitts: current P1 D 616 px, W 85, ID 3.05, 0.77 s; P2 D 430 px, W 50, ID 3.26, 0.79 s, total 4.96 s; proposed P D 278 px, W 40, ID 2.99, 0.76 s, total 3.86 s. **T02-kbd.** Current: H 0.40 + M 1.35 + 3 Tab 0.60 + Enter 0.20 + R 0.30 + 4 Tab 0.80 + Enter 0.20 + R 0.20 + M 1.35 = 5.40 s (the second run of Tabs exists because the case list is rebuilt and the focused button is destroyed, F4; I assume Tab resumes at the removal point, 4 Tabs; if the browser restarts from the document start it is 6 Tabs and 5.80 s; UNVERIFIED, not run). Proposed: H 0.40 + M 1.35 + Enter 0.20 + R 0.30 + M 1.35 = 3.60 s.

**Where the proposal is not faster.** T06 and T14 are slower by 0.36 s and 0.39 s under the Fitts profile and equal under constant P (0.00 s). Both Fitts deltas are extrapolated (T06 proposal terms D 577 and 653 px, ID 3.95 and 4.42; T14 D 788 px, ID 4.86), and T14 is a workaround comparator: the Evidence tab and the roll-up count are farther from the pointer than the baseline's tab strip (T14: D 788 px, W 28, ID 4.86, 1.00 s, against the baseline's tab at ID 1.95, 0.62 s). T08 is deliberately not shortened (PRINCIPLES P2; LAW section 3).

**Which differences are outside the band.** A difference counts only if the two plus or minus 21 percent intervals do not overlap. Over a grid of K 0.12, 0.20, 0.28 s, P constant or Fitts, and with or without one extra M in the current flow (12 cells per task), the cells that separate are: T02 6 (all need the extra M in the current flow), T02-kbd 8 (2 of 6 without the extra M), T04 2, T09 1, T10 12 (invalid for novices), all others 0. At the base constants only T10 separates, and KLM does not apply to it. The keyboard-only path leans on a design rule (Changes home focuses the first Needs you row, unverified) and on an unverified focus behaviour. This is the honest reading: the IA change is not justified by speed.

### 10.3 Tree or palette

Per level of an expert tree walk with fan-out 8: Hick 0.24 + 0.08 log2(8) = 0.48 s, plus P 1.10 and B 0.10, so 1.68 s (novice search: 0.94 + 1.20 = 2.14 s). Landauer and Nachbar found expert menu selection well described by Hick-Hyman and Fitts components in series (S1). A palette lookup by a user who knows the name: M 1.35 + H 0.40 + Ctrl+K 0.40 + 6 typed characters 1.20 + Enter 0.20 + R 0.10 = 3.65 s (3.25 s with hands already on the keyboard).

| Depth of a known target | Tree, expert (s) | Tree, novice (s) | Palette (s) |
|---|---|---|---|
| 1 | 3.03 | 3.49 | 3.65 |
| 2 | 4.71 | 5.63 | 3.65 |
| 3 | 6.39 | 7.77 | 3.65 |
| 4 | 8.07 | 9.91 | 3.65 |

**Reading.** The tree is as fast as the palette at depth 1 and slower beyond, if the user knows the name. The palette does not beat a visible control (M 1.35 + P 1.10 + B 0.10 = 2.55 s against 2.75 s for a typed 4-character command, dossier DEV §2.12). The tree earns its place as context and for browsing, not for speed. Validity: expert, stable positions, names known, error-free; the band is plus or minus 21 percent; expansion state that shifts positions weakens the expert row.

### 10.4 Keyboard-only reach (COUNT and PREDICTION)

To reach the Evidence view by keyboard from load: baseline 8 Tab presses to the fourth tab plus Enter (9 keys, 1.8 s, Tab order read from `index.html` and `app.js`, not run); proposal `g e` (2 keys, 0.4 s) or Ctrl+K, `ev`, Enter (5 keys, 1.0 s) when character shortcuts are off.

### 10.5 Limits

Expert, error-free, routine only. No reading time, no learning, no errors, no discoverability (the palette is invisible to a novice; the trigger in the top bar and the shortcut hints address that, untested). Constants are from 1980 laboratory tasks and an eight-participant menu study. The M count is a judgement. Geometry for the proposal is a design, not a build; geometry for the baseline is a measurement by another lane that I did not reproduce. **Sensitivity to the shell.** The layout lane's drafts (L4, `proposed-review.json`) use the same three destinations and status ids but a 296 px tree, a 752 px main and a 392 px inspector, and put the decision entry in the inspector. Re-running the Fitts terms of my flows on that geometry (ids mapped by hand, flows with an unmapped slot skipped) changes every total by 0.00 to 0.07 s (PREDICTION), so the shell dimensions do not matter at this precision. Fitts models one-dimensional pointing and was calibrated on vertical menu movements of at most about 340 px (10.2); every 2D or longer term here is extrapolated; the top-bar and status-bar edge advantage for the mouse (S38) is not credited, which is conservative for the proposal.

## 11. Interfaces and assumptions

| Id | Aspect | This design assumes | If it changes |
|---|---|---|---|
| A1 | Layout and shell | Regions and sizes of section 3 at 1440x900; sidebar 272, inspector 360; below 1280 px the inspector is hidden; minimum main width 560 | Slot positions in `nav-proposed.json` are re-derived; the flows are recomputed by the executable model |
| A2 | Status and colour | Six evidence status words with a glyph each; UNKNOWN first and PASS last in the roll-up; a glyph on every tree row; contrast computed by the token aspect | Words alone carry the meaning until glyphs exist; contrast stays UNKNOWN |
| A3 | Type | Navigation uses at most three sizes (title, base, meta) | The nav counts in section 12 are recomputed |
| A4 | Review | Chapters Core, Follows from core, Other (the review aspect's names, L5); operation rows with ripple counts; "n formatting-only edits hidden"; Viewed marks (review aspect) | Only the row anatomy changes |
| A5 | Ripple lane | Seven rows in the order Persona, Requirement, State, Journey, Test, Code, Evidence, each with a count and a gap glyph; "Not analysed" listed apart | Navigation needs each row to be one focusable target |
| A6 | Language and tree | Tree depth at most 4, siblings at most 12; ids are stable model ids; rename is a typed request (refused today under ADR-003) | Depth and fan-out budgets move with the tree design |
| A7 | Canvas | Selection bus with model ids (L3 I-N1) is provided here. **The canvas asked for edit commands in the palette (L3 I-P1: `canvas.tidy`, `canvas.reconnect-source`, ...). This design declines: typed edits and layout changes are owner-only, are not palette commands, and appear as pointer rows** | The canvas fallback in L3 applies: the keyboard path uses canvas keys and inspector controls |
| A8 | AI interaction | Classes C0 to C4, palette classes C0 to C2, `/` command mode, inbox row anatomy, status-bar and tab-title count (L1). I put the attention count in the status bar as L1 asks, and dropped the top-bar chip | Slash aliases are renamed |
| A9 | Motion | Latency classes of L2 | R values and targets change |
| A10 | Decision | The surface has no URL; opened only by the Decide... button; owns its layout | The T08 flow is recomputed |
| A11 | Security | No server change; the token stays out of links; a second-tab handoff is an open question | Section 8.3 |
| A12 | Kernel | Element ids are stable; the diff lists ADDED, MODIFIED, REMOVED; the payload carries what the index needs | The palette index falls back to names |
| A13 | Layout lane drafts (L4) | Same three destinations and the same status-bar ids as this design; tree 296 px, main 752, inspector 392; `Review decision` button in the inspector; a palette mock that lists `Set rejection source` and `Rename term` as rows | Sizes: no effect at this precision (section 10.5). Rows: under this design they are pointer rows and the rename row is BLOCKED with its reason (ADR-003) |
| A14 | Review aspect (L5) | Assumes a 48 px navigation rail and no tree on the Review screen; the evidence rail holds the Decide entry; chapters Core, Follows from core, Other; ripple strip with `?` for unmodelled kinds | This design keeps the tree as the persistent sidebar because one selection must be shared (D2); the sidebar collapses with Ctrl/Cmd+B if the layout needs the width. The Decide entry position (main header or rail) changes T08 by 0.03 s; the rule "one primary action per view in a fixed slot" stays. Recorded as option F in the ADR: main width on Review 1000 px with the rail against 808 px here and 752 px in the layout lane (COUNT); rejected as the default, kept as the collapsed state |
| A15 | Language aspect (L6) | Tree in a 400 px left rail, filter modes Highlight, Path, Flat, `Move to` and the palette as the non-drag path emitting the same operation | Width: see A13. Filter names adopted. **Palette emitting an operation conflicts with L1 and with this design (pointer rows); the non-drag path stays the `Move to` picker and the inspector** |
| A16 | Content aspect (L7) | Screens SH, HOME, TREE, REVIEW, EVID, DECIDE, PAL; HOME has one primary action (open the sample); `Define <term>` in the palette; word budget per screen | HOME is this design's Changes home; `Define term...` is a C0 command (added). The 20-word persistent shell budget is checked against the frame here (top bar and status bar words: 34 counted) and is a deviation to reconcile |

## 12. Anti-slop counts for navigation

COUNT from `design/layouts/nav-proposed.json`, filtered by the `view` field (revision 2: one file, four views; the file's `views` block carries the same numbers), and MEASURED by L4 for the baseline. Every visible token counts, including each count placeholder `n`, because it renders as one number. The launch view is Changes; Model and Evidence lay out only the shell and their tab strips, so their counts are partial.

| Item | Baseline | Proposal | Target | Note |
|---|---|---|---|---|
| Words in the first viewport | 171 (Change tab, MEASURED by L4) | launch view (Changes) 90; Review 133; Model 91 and Evidence 58 partial (COUNT, PREDICTION for a build; `n` placeholders 16 and 32 of these) | about 120 | Launch view under budget. Review 11 percent over; the excess is level-0 content that P1 and P4 require (counts by state, operations). Recorded as a deviation in the ADR |
| Containers (regions, chips, inputs, filled buttons, selected fills) | not counted by me | launch view 9 (4 regions, 2 inputs, 1 chip, 1 button, 1 selected fill); Review 11 (4, 2, 1, 2 buttons, 2 selected fills); Model 10 and Evidence 9 partial | about 12 | Review at budget |
| Nested depth | | 2 | at most 3 | region, list, row |
| Eyebrow labels | 10 (dossier count) | 0 | at most 1 | chapter headings are section labels |
| Smallest interactive side | 18 px (native checkboxes `egress` and `acknowledge`; the label is 25 px tall; MEASURED by L4); 34 px among the navigation elements | 24 px (`main-crumb` ancestor links; the show link in `main-hidden`); 28 px in the launch view; bare text buttons 28 px tall | at least 24 | WCAG 2.5.8 (S13); at the minimum, no margin |
| Elevations | 0 | 1 (palette dialog) | at most 2 | no shadow, one border |
| Font sizes for navigation | | at most 3 by design | 6 for the viewport | whole-viewport count belongs to the type aspect: UNKNOWN |

## 13. Validation plan

Nothing below has been run.

**Prototype checks (one Chromium at a time; 1440x900 and 1280x720).** (1) Recompute every flow from the JSON with the executable model and compare to section 10. (2) Static test: the palette registry accepts only C0, C1, C2 and no handler references `/approve`, `/apply`, `/select`, `/edit`, `/layout`, `/discard`, `/save`; each pointer row moves focus only. (3) Deep-link round trip: for every route in section 8.1, load it fresh and compare the rendered state with the state that produced it; Back and Forward; unknown id; stale `rev`; a token never beginning with `/`. (4) Focus test: after opening a case, `document.activeElement` is the first row; a re-render keeps the focused element; tab stops per page at most 16. (5) Target-size scan: every interactive element at least 24 by 24 CSS px. (6) CSP smoke test: `hashchange`, `pushState` and `popstate` run under the current CSP (UNVERIFIED). (7) Latency probe p95 of at least 30 trials: palette open at most 100 ms; results after a keystroke at most 200 ms (target). (8) Character-shortcut toggle disables `/`, `?` and `g` sequences, verified with a keyboard-only session.

**Tree test (NN/g method, S32).** Text-only hierarchy of the three destinations, six lenses and the tree levels; goals T02, T03, T06, T09, T11, T12, T14. Measure first-click success, directness and time. Pass criteria fixed in advance (HYPOTHESIS): first-click success at least 80 percent on each task with at least 12 participants; a task below 60 percent is relabelled and retested. NN/g gives no minimum sample; formative rounds of about 5 find problems and do not estimate prevalence (LAW section 2.10).

**Within-subject study arm (protocol inline; the study aspect owns the full protocol).** Baseline Studio against the proposal, counterbalanced, engineers, excursion-workflow tasks T02, T03, T06, T09, T14, keyboard-only cohort included. Measures: time to first evidence, wrong-destination clicks, focus-loss events, UNKNOWN misread as PASS from the roll-up (target zero), SEQ per task, SUS overall, Raw TLX, and rubber-stamp indicators (time from opening the Decision surface to Approve; UNKNOWN items opened). Stop and redesign if any participant misreads a roll-up count as approval readiness on a seeded UNKNOWN, or reaches Approve by any route other than Decide.... Results: none yet.

## 14. Open questions and risks

| # | Question | Effect | Owner |
|---|---|---|---|
| 1 | Does the kernel return receipts for an applied baseline, so Evidence in scope `base` is meaningful? | Evidence in Baseline scope reads UNKNOWN or is hidden | kernel lane |
| 2 | Second-tab token handoff (section 8.3) | Deep links across tabs need the launch link | security lane |
| 3 | Does "Changes home focuses the first Needs you row" cause wrong-case opens? | The T02-kbd advantage depends on it | study |
| 4 | F2 for rename and `g` sequences may collide with browser or extension keys | Keymap changes | prototype |
| 5 | The empty-state action "Review the sample change" needs an application feature (offline fixture from the UI) | T10 proposed flow is not buildable today | application |
| 6 | Is the palette discoverable enough for the ICP without training? | Visible trigger and hints are the only mitigation | study |
| 7 | Three lanes want typed-operation commands in the palette (canvas L3 I-P1, language L6 D6, the layout lane's palette mock) and L1 forbids them. Resolved here in favour of L1 with pointer rows | Integrator must confirm; if the palette may stage an edit with a preview and a separate commit, the registry needs a fourth class and the static test changes | integrator |
| 8 | The status bar is far from the pointer; the predicted cost is 0.36 to 0.39 s on T06 and T14 under the extrapolated Fitts profile (0.00 s with constant P) | May move the roll-up to the sidebar top (0.02 s difference, PREDICTION) | layout |
| 9 | Do reviewers need claim detail beside an operation, or are the counts in Review enough before Decide...? | If detail is needed, the Evidence lane row expands in place (disclosure level 1) instead of navigating | study |

## 15. Sources (all opened on 2026-09-29)

Summaries are model-written by WebFetch; nothing is quoted beyond a few words. The Cockburn PDF was read locally as text.

| Id | URL | Type |
|---|---|---|
| S1 | https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf | peer-reviewed paper (CHI 2007) |
| S2 | https://en.wikipedia.org/wiki/Keystroke-level_model | secondary; 21 percent RMS error, validity (constants now from S50) |
| S3 | https://www.nngroup.com/articles/response-times-3-important-limits/ | practitioner (0.1, 1, 10 s) |
| S4 | https://www.nngroup.com/articles/progressive-disclosure/ | practitioner, 2006 |
| S5 | https://psychclassics.yorku.ca/Miller/ | primary paper, 1956 |
| S6 | https://pmc.ncbi.nlm.nih.gov/articles/PMC2864034/ | review, Cowan |
| S7 | https://www.w3.org/WAI/ARIA/apg/patterns/treeview/ | W3C practice guide |
| S8 | https://www.w3.org/WAI/ARIA/apg/patterns/combobox/ | W3C practice guide |
| S9 | https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ | W3C practice guide |
| S10 | https://www.w3.org/WAI/WCAG22/Understanding/consistent-navigation.html | standard, 3.2.3 AA (scope: a set of web pages; guidance only here) |
| S11 | https://www.w3.org/WAI/WCAG22/Understanding/multiple-ways.html | standard, 2.4.5 AA (scope: a set of web pages, process steps exempt; an AJAX app at one URL is one web page; guidance only here) |
| S12 | https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html | standard, 2.4.11 AA |
| S13 | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | standard, 2.5.8 AA |
| S14 | https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html | standard, 2.5.7 AA |
| S15 | https://www.w3.org/WAI/WCAG22/Understanding/character-key-shortcuts.html | standard, 2.1.4 A |
| S16 | https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html | standard, 2.1.1 A |
| S17 | https://docs.github.com/en/get-started/accessibility/github-command-palette | official documentation |
| S18 | https://docs.github.com/en/get-started/accessibility/keyboard-shortcuts | official documentation |
| S19 | https://code.visualstudio.com/docs/getstarted/userinterface | official documentation |
| S20 | https://linear.app/docs/search | official documentation |
| S21 | https://blog.superhuman.com/how-to-build-a-remarkable-command-palette/ | first-party blog |
| S22 | https://www.jetbrains.com/help/idea/searching-everywhere.html | official documentation |
| S23 | https://code.claude.com/docs/en/agent-view | official documentation |
| S24 | https://gerrit-review.googlesource.com/Documentation/user-attention-set.html | official documentation |
| S25 | https://storybook.js.org/docs/writing-tests/integrations/vitest-addon | official documentation |
| S26 | https://docs.stripe.com/stripe-apps/design | official documentation |
| S27 | https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability/trace-view.html | official documentation |
| S28 | https://www.notion.com/help/tasks-and-dependencies | official documentation |
| S29 | https://www.ilograph.com/features.html | vendor page |
| S30 | https://www.nngroup.com/articles/tabs-used-right/ | practitioner, 2024-08-02 |
| S31 | https://www.nngroup.com/articles/information-scent/ | practitioner, 2020-02-02 |
| S32 | https://www.nngroup.com/articles/tree-testing/ | practitioner, 2023-08-06 |
| S33 | https://lawsofux.com/jakobs-law/ | practitioner summary |
| S34 | https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage | reference documentation |
| S35 | https://developer.mozilla.org/en-US/docs/Web/API/History/pushState | reference documentation |
| S36 | https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files | official documentation |
| S37 | https://www.nngroup.com/articles/ten-usability-heuristics/ | practitioner |
| S38 | https://www.nngroup.com/articles/fitts-law/ | practitioner |
| S39 | https://www.nngroup.com/articles/breadcrumbs/ | practitioner, 2018-12-23 |
| S40 | https://www.nngroup.com/articles/empty-state-interface-design/ | practitioner, 2021-09-19 |
| S41 | https://primer.style/product/ui-patterns/empty-states/ | design-system documentation |
| S42 | https://arxiv.org/abs/1703.01897 | peer-reviewed interview study, 2017 (abstract read) |
| S43 | https://cursor.com/blog/cursor-3 | vendor blog |
| S44 | https://linear.app/docs/assigning-issues | official documentation |
| S45 | https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/hidden | reference documentation |
| S46 | https://github.com/primer/behaviors | repository page (MIT) |
| S47 | https://github.com/chakra-ui/zag/discussions/2309 | forum |
| S48 | https://www.w3.org/WAI/ARIA/apg/patterns/tabs/ | W3C practice guide |
| S49 | https://www.w3.org/WAI/ARIA/apg/patterns/toolbar/ | W3C practice guide |
| S50 | https://web.eecs.umich.edu/~kieras/docs/GOMS/KLM.pdf | tutorial by a KLM author (Kieras), based on Card, Moran and Newell 1983; operator times |

Other lanes (read in this worktree on 2026-09-29; written in parallel, all proposed): L1 `docs/hci/design/ai-interaction.md` and `docs/adr/0064-hci-ai-interaction.md`; L2 `docs/hci/design/motion-and-performance.md`; L3 `docs/hci/design/canvas-uml-interaction.md`; L4 the layout lane: `design/layouts/current-*.json` (Chromium measurement of the baseline), `design/layouts/proposed-*.json` (its shell drafts) and the scratch `.tmp/current_measure.json` (untracked, gitignored; the method is that lane's to publish); L5 `docs/hci/design/evidence-and-change-review.md` and `docs/adr/0063-hci-evidence-change-review.md`; L6 `docs/hci/design/language-and-ddd-tree.md` and `docs/adr/0062-hci-language-ddd-tree.md`; L7 `docs/hci/design/content-and-onboarding.md` and `docs/adr/0065-hci-content-onboarding.md`. Repository files: `index.html`, `app.css`, `app.js`, `interfaces/http.py`, `interfaces/cli.py`, `examples/excursion-*.json`, `docs/architecture/ARCHITECTURE.md`, `AGENTS.md`, ADR-003 and ADR-013 in `docs/adr/0000-poc-decision-log.md`. Research dossiers cited by id: REQ, DEV, LAW, SYNTHESIS in `docs/hci/research/` (not re-opened unless a URL is listed above).

Not verified: the Linear page opened (S20) does not state the command menu shortcut; I did not rely on Ctrl+K for Linear. The VS Code Quick Open prefixes `>` and `:`, the Zed key-beside-command precedent and the Raycast and VS Code naming rules are UNVERIFIED (not on an opened page) and nothing rests on them. Ctrl+Shift+P conflicts, `F2` as a rename convention, per-browser Ctrl+K and Ctrl+B conflicts, palette performance, and every effect on users are UNVERIFIED.

## 16. Revision 2 (after audit, 2026-09-29)

| Audit finding | Verified? | Change |
|---|---|---|
| Co-visibility argument contradicts itself (B rejected for what C also does) | Yes | Section 4.4 states what Review shows together and what is one step away; D2 and 4.3 reworded; the ADR drops "evidence apart from decision" as a reason against B and says the tabs test is only partly met |
| Flows say `nav-current.json` is estimated from CSS | Yes (15 of 15 tasks) | Assumption replaced in every task; `nav-current.json` has a provenance note and a per-element `source` field (15 copied, 5 bounding boxes, 2 clipped) |
| WCAG 2.4.5 and 3.2.3 scope | Yes: the Understanding page counts a one-URL AJAX app as one web page | Guidance, not a conformance claim; three routes rest on Borg et al. (S42) |
| Fitts constants extrapolated | Yes: 16 items of 130x22 px, 8 right-handed graduate CS students (S1, read locally) | Calibration range in 10.2 and 10.5; Fitts columns marked EXTRAPOLATED; constant-P deltas reported beside T06 and T14 |
| T09, T10, T14 are not like-for-like | Yes (`design/brief.json`: absent; T13 partial) | Marked workaround comparators in the table, the flows and the ADR |
| One layout mixes views; launch view not counted; `n` counted; 28 px claim | Mostly. One point disputed: `n` renders as one number, so counting it as a word is correct; the convention is now stated and the `n` share reported | `nav-proposed.json` keeps one file (file ownership) with a `view` field per element and a `views` block; the Changes launch view is laid out (90 words, 9 containers); smallest target 24 px |
| Unopened sources (Zed, Raycast and VS Code naming, VS Code prefixes); KLM from Wikipedia | Yes: the VS Code page lists only `?` | Marked UNVERIFIED and not relied on; KLM constants re-sourced to Kieras (S50), which also shows a click is B twice (0.2 s); the effect on deltas is stated |
| "You decide" vs "Needs you"; `T02-kbd` id | Yes | "Needs you" throughout; `variant_of: "T02"` |
| Tree selection in Changes undefined; rail option missing | Yes, with one correction: the layout lane (HCI-ADR-0058) keeps a 296 px tree sidebar in every view at 1440 and uses a rail only below 960 px; only the review aspect assumes a 48 px rail with no tree | Tree selection in Changes filters the inbox (4.1, 8.1); option F added to the ADR with main widths 1000 / 808 / 752 px |
