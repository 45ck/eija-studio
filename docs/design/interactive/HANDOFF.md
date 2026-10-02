# Interaction/state handoff

## Summary

The design question is whether an engineer can keep **what changed, which subject it belongs to, where it is implemented, and what remains unknown** together while moving freely through the workspace. The strongest moment is exact old/new fields above a paired projection, with explicit source/evidence context nearby. This is an inspectable implementation proposal, not a new product specification or a validation result.

The shell gives project/case identity one global home. Full fixture identity is one disclosure away. The selected element's exact delta remains visible across views. Workspace exposes S01–S10 in one grouped native dialog; six frequent-view shortcuts use native navigation, so auxiliary views never create a tablist without an active panel. The left pane holds task inventory. A separate handoff drawer contains scenario/persona controls; they are not proposed production chrome.

## Refinement 2: observed problem and bounded response

**Observed in the first artifact's retained 1440×900 capture:** global Model/Source/Changes/Evidence/Run destinations appeared in both a long sidebar and top navigation; the changed-item list sat below that menu. Save's selected PREVIEW and SAVED boxes were visible, but the graph continued behind the handoff/footer and the DRAFT box was cropped. The second changed item approached the sidebar's lower edge. This is not evidence that Save's selected endpoints were missing.

**Observed in retained 1280×800 captures:** selected Verify showed 82% Focus while its VERIFIED node was clipped by the outer content boundary. The guard preview showed complete exact values but its multiline whitespace consumed substantial height; the graph was 67% and its route continued behind the dialog footer. Exact field values were visible. Those findings concern layout/comprehension, not model topology correctness.

**Source-supported cause hypothesis:** the old viewport-based height/minimum and fixed preview-summary allowance did not follow actual remaining parent space. Browser rectangle inspection of this revision is still required; the hypothesis is not a new measurement.

This revision changes only presentation: real flex/grid parent sizing; exact fields/context in one disclosure; compact complete array summary; natural-scale selection focus using existing APIs; task inventory above the fold; one complete Workspace menu; concise primary headings and adjacent Source/Evidence limits. Source/unknown boundaries remain visible. Factory inventory contains only explicitly planned branch fixtures. No copied renderer, graph geometry, rule semantics, status authority or HCI budget is modified.

The tradeoff is explicit: **Focus 100% centers rather than promises to fit**. If the available pane is too small, users pan or deliberately choose reduced-scale Overview. The default must never silently shrink labels to claim that everything is readable. Browser review must still establish whether the actual desktop space now shows each selected route and endpoint at natural scale; this revision does not predeclare success.

## Findings implemented in the reference

### Refinement 3: retained QA2 failures

The prior artifact's ordinary global round-trip left an early Save return record alive. Selecting Verify afterward and investigating Source → Evidence could return to Save. A reset-isolated success did not repair that nonlinear route. Global Workspace/frequent-view/command navigation now creates no contextual origin. A contextual action captures the current selection; its Source → Evidence chain retains it; any arrival at the origin view ends the trail without creating a reverse origin. Explicit Return restores the captured selection/focus. Changing an item at a destination does not erase the return record.

QA2 also retained source/guard preview clipping at 1280×800: selected endpoint boxes extended from approximately y320 to y660 while the visible SVG interval was approximately y347–633, at 100% scale. Main Save/Verify comparisons at 1440/1280 and the three 1440 preview variants were observed separately; they do not remove this defect. This revision uses the available 94vh dialog height and moves the duplicate preview item navigator into the existing exact-details disclosure. Its visible summary retains changed/unchanged counts; no values, unknowns, controls or copied renderer bytes are removed or shrunk. Geometry and full selected-path containment still require a new source-bound browser capture.

- Exact fields lead the review: `Role: Owner → Agent`, `Source state: PREVIEW → SAVED`, and complete guard arrays. Source and target have distinct labels. Color supplements text/status; it never supplies the only distinction.
- The paired snapshots use existing EIJA comparison and Dagre. Each side renders only its own elements; “removed element” exposes **Not present**. The unchanged inventory stays available. No layout movement is interpreted as semantics.
- Case state owns selection and comparison presentation. Contextual detours retain their original selection until Return or another arrival at the origin; global navigation does not create stale return records. Open source/details and scroll positions are restored on surface revisit where specified by the artifact.
- The selected model's evidence remains NOT_RUN. The separate TR-SELECT witness explicitly names its own transition and does not certify selected Save. Missing source binding is distinct from unavailable transport or unsupported extraction.
- Edit fixtures show the real product's intended preview boundary with existing components, but remain independent prepared snapshots. “Show apply outcome” has deliberately different wording from a real Apply edit; no backend exists.
- Unknown or acknowledged-but-unrefreshed outcomes remain visible outside the preview dialog. Their prepared subject is explicitly **DESIGN-UNSUBMITTED**, independent of the open fixture; no revision 8/9 result is attributed to case B revision 3. The real product requires a case-owned reconciliation record.
- Factory is separate and planned. A missing merged subject cannot be replaced by the current case's evidence. There is no faux landing action or animated agent service.

## Surface states and controls

Each row is available through navigation plus **Design states & interaction handoff → Surface state**. State switching is explicit, not timer-based simulated work. Full interaction testing is pending.

| Surface | Populated controls / subject | Other states and recovery | Keyboard / focus / retained context |
|---|---|---|---|
| **S01 Model** — US02/06/10 | Working fixture, selected rule; existing Canvas; Review an edit; exact rule table with Select action | Loading/stale retain graph. Empty offers Intent or populated fixture. Layout failed replaces the graph with the usable rule table. | Native tree/selection buttons; SVG transition activation; table scroll region. Navigation lands on surface heading. Existing comparison view is separate from this single-model illustration. |
| **S02 Intent** — US03/04/11 | Request textarea, explicit offline identity and model-only scope; two interpretations; Inspect proposed meaning | Loading, failed, unknown preserve the same case's typed request. Explicit controls show the next illustration. No automatic retry or provider progress. | Labelled textarea; native buttons; request correction focuses the textarea. Request survives same-case navigation and case switching. |
| **S03 Changes** — US04/05/07 | Selected delta, complete task inventory, unchanged disclosure, existing paired view; one exact-fields/context disclosure below; adjacent source/evidence | Loading/stale preserve snapshots. Empty explicitly says no differences. Removed fixture omits Save on the After side and shows absence. | Existing arrow-key navigator, graph activation, pan, `+`/`−`, Home. Focus 100% centers at natural scale; Overview may reduce. Compare state retained per case; Source/Evidence return restores selection/view and stable origin focus if still present, otherwise heading. |
| **S04 Source** — US01/05/10 | Exact declared fixture reference, line range, read-only pseudocode, full identity/scope disclosure, return | Loading/stale preserve old excerpt. Missing binding and unsupported states explain no location/coverage; no guessed lookup. Recover illustration is explicit. | Labelled scroll region and line numbers. Arrival heading focus; Return restores selected change. Full content is text, never interpreted HTML. Immutable Code review scope is explained separately; no fabricated Git diff. |
| **S05 Edit preview** — US06/09/11 | Fixed Role/Source/Target/Guards examples for DESIGN-UNSUBMITTED; Open edit preview; copied comparison's captured before/proposed result; Close preview; Show apply outcome | Checking has no verdict; refused has no permission workaround; stale cannot apply. Unknown/acknowledged recovery stays outside the dialog until explicit refresh illustration. The parked open case remains unchanged. | Native modal; first focus Close; Escape same as Close; restores invoker, falling back to heading. All controls are illustration-only. Refactor/source-write actions unavailable and explained. |
| **S06 Evidence** — US07/10/11 | Selected subject, scope, source-review/human unknown, separately scoped witness selector, raw illustrative record, exact rule/Run destinations | Loading/missing/stale do not become PASS. Counterexample is a prepared illustration, distinct from executed evidence. | Native step buttons have pressed state. Raw record disclosure is one action away. Witness points to TR-SELECT, not whatever item happens to be selected. |
| **S07 Run** — US08/11 | Last acknowledged state, latest attempt, captured actor/action, operation diagnostic, rule/evidence routes | Pending/refused/unknown/committed/refresh-failed are distinct prepared outcomes. No automatic retry. No real execution or authority calculation. | Live announcement only for deliberate state changes. Attempt identity separate from last acknowledgement. Audit disclosure defaults closed. |
| **S08 History** — US09/10 | Case-specific timeline and current/historical inspection; return to current comparison | Empty has no fake undo. Loading/stale retain context. Historical identity is explicit and does not inherit current evidence. | Native inspection controls, named current return. No simulated server restore/undo is exposed. Exact production audited Undo/Redo remains an implementation component, not recreated here. |
| **S09 Factory** — US13/14 P1 | Planned branch ownership/base cards, shared abstraction, coverage/authority limits, prepared overlap fields and combined-result contract | Unknown/stale-base/failed-landing variants are contract illustrations only. No actual merged subject exists. Parked case changes are not presented as branch overlap. | No Start/Merge/Approve/Land controls. Contract/overlap actions open native disclosures and focus their summaries. They do not mutate or select an unrelated parked-case element. |
| **S10 Connection/help** — US01/10/11/12 | Scope inventory, exclusions, explicit recovery; help and first-entry routes | Empty, loading, unavailable and partial states preserve prior context. No filesystem/provider access. | Native buttons; one next recovery action. First entry offers model or intent without a wizard. Navigation drawer has a visible Close and Escape return. |

## Shared state and interaction ownership

| State | Prototype owner | Product integration requirement |
|---|---|---|
| Active case/revision, selected model element | In-memory, fixture key; independent per case | Server case/model remains authority. Same ID in a different subject cannot inherit source/evidence applicability. |
| Compare pan/zoom and selected item | Existing `EijaCompare` state; kept per case | Also bind to exact revision; resetting after semantic change must be deliberate and tested. |
| Surface scroll and opened disclosures | Local presentation cache | Preserve useful context; no semantic persistence or extra server version. |
| Request text | Per-case local illustration | Preserve through failure; distinguish whether request was accepted or merely sent. |
| Edit preview | Native dialog + prepared snapshots | Real `/edit/preview` result, origin subject guard, one captured `/edit` expected version, stale/cancel/unknown handling remain the implemented authority boundary. |
| Evidence/source navigation | Explicit fixture binding | Exact source digest/line identity and evidence subject from backend; unresolved stays unresolved. |
| Recovery state | Explicit prepared subject DESIGN-UNSUBMITTED; retained outside dialog | Real unknown/acknowledged reconciliation must be owned by the exact case and guard executable mutation paths outside transient dialog/notice. |
| Factory | No operational state | Future worktree/merge/authority contract and actual combined-result checks are prerequisites. |

The artifact has no asynchronous API or persistence. Selecting a fixture state is not a concurrency test, and closing a dialog here cannot prove a product command was cancelled. Its purpose is to make intended transitions inspectable before implementation/evaluation.

## Responsive and accessibility handoff

- **1440×900 target:** 228px task inventory, central paired review, 265px context. Exact selected fields lead. Graph space is allocated from the actual remaining flex pane; exact fields/context have a native disclosure. Desired layout, not observed acceptance of refinement 2.
- **1280×800 target:** 205px task inventory, 225px context, compact header; retain 14px main text and natural graph scale. Focus 100% centers, not auto-shrinks. Inspect actual selected endpoint/route containment; pan and explicit Overview remain available when space is insufficient.
- **Below 1050px:** adjacent context gives way to primary Source/Evidence destinations; selection ribbon remains. It does not remove scope/unknowns from those destination views.
- **720px and narrower:** task inventory is a deliberate drawer with Close/Escape; Workspace remains a complete native dialog; source/review regions scroll; comparison stacks Before/After. At 320px the diagram can be two-dimensional and vertically scrollable, but surrounding controls, exact fields, warning and recovery action must be reachable. No compact graph-above-fold acceptance is claimed.
- **Keyboard:** native navigation, labelled fields and scroll regions, skip link, focusable destination heading, native modal behavior, existing comparison shortcuts. No custom tree/tab widget is introduced for the shell.
- **Reduced motion:** no animated transition or fake completion timer is required for meaning. Actual forced-colour, text enlargement, screen-reader behavior, target geometry, focus restoration, drawer interaction and clipping need browser/manual evaluation.

No density score is claimed. Repetition is removed where it does not support the task; important unknowns, complete changes and direct navigation remain. This design does not change the stored 27-chunk budget, KLM threshold, latency targets, or any instrument.

## Evidence versus assumptions

**Observed inputs:** current product component source; existing ten-surface specification and fifteen stories; actual repaired unsubmitted-role screenshot; parent-held gap/density analyses. The already integrated product's tests and browser observations apply to their original subjects only.

**Design hypotheses:** exact field-first presentation plus adjacent source/evidence reduces review memory burden; task-grouped navigation is easier to scan than ten equal top-level buttons; progressive identities retain trust without dominating the main task. None is a measured human outcome.

**At authoring, 3 October 2026, not performed for refinement 5:** browser run/capture, axe, human task study, accessibility conformance, live-agent use, repository conformance, performance benchmark, factory operation or product acceptance. Subsequent reviews are separate source-bound records. Earlier retained captures motivate changes but do not verify this revision. The actual-handler Node regression is a separate, limited navigation check, not visual evidence.

## Review questions and next evidence

1. From Save, can a reviewer state **which role changes** and **whether the proposed edit is already submitted**? Negative control: the same endpoints/labels with a reversed role delta must be noticed.
2. From Verify, can the reviewer distinguish **source moved to SAVED** from **target moved**, and identify the exact removed guard entry? Negative controls: wrong arrow endpoint, omitted guard, or reversed Before/After must fail the independent comparison oracle.
3. Can the reviewer open source, discover a missing binding, inspect an inapplicable witness and return without attributing another subject's result to the selection? Negative control: same element ID on a different case/revision.
4. Can an interrupted edit retain an acknowledged/unknown outcome after the dialog closes, while the engineer still finds a safe next action? Prototype inspection can assess wording; only real browser/server fault tests establish product behavior.
5. Does the declared desktop/reflow layout expose exact deltas before scrolling, and are all critical context, recovery controls and keyboard return points visible? Preserve contrary captures and fix the design; do not clip content or shrink type to satisfy a score.

Recommended next handoff: **wireframe-critic** for this inspectable layout, then **usability-test-planner** to freeze equivalent persona tasks and independent answers using the existing V&V protocol. Existing HCI instruments should measure real integrated interactions after implementation; no new parallel formula or automatic acceptance is proposed.

## Refinement 4: raw-record keyboard contract

Only the two authored JSON preformatted blocks use `pre.exact-record[tabindex="0"][role="region"]`. Run is named **Latest attempt identity and diagnostic JSON**; Evidence is named **Illustrative witness record and assumptions JSON**. Both retain literal data and native arrow/Page/Tab behavior. The focus outline is inset so the pane cannot clip it. No general prose gains a tab stop. The already-focusable Source region retains its behavior. The original selected-source, return-trail and comparison-framing fixes remain unchanged.

Next browser check: open the actual Run Attempt details disclosure, resize to 320px, Tab to the named raw region, scroll with real keys, then leave without a trap. Repeat the Evidence exact record and read-only Source where content overflows. Run axe in these opened states and retain incomplete findings separately. Prior eight functional groups and ten framing observations belong to refinement 3, not this authored revision.

## Refinement 5: independent prepared-selection contract

The `#edit-kind` change handler changes only `variant`, rerenders S05 and focuses the replacement selector. It never calls the open-case `setSelection`. The context action is labelled **Explore prepared edit examples** so it makes no selected-rule matching promise. Existing `openPreview()` supplies its own `DESIGN-UNSUBMITTED` r8 and variant transition to the copied comparison component, with no case-selection callback. No copied asset changes.

Browser regression to retain: case A Save → global Rules → choose Verify source example → open/close preview → global Changes remains Save → Source remains Studio.save. Repeat case B and verify its explicit missing binding remains missing. Include independent request/selection context for both cases and return-focus behavior. The previous origin, framing and raw-scroller checks remain required; their earlier observations do not accept refinement 5.
