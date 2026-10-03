# EIJA next UX pass: focused work and visual change review

## Next pass after ad9394e1 — 3 October

The [published ad9394e1 record](../engineering/2026-10-03-MERGED-IDE-CHECKPOINT.md) contains ten passing browser journeys over identical product bytes, 495 passing JavaScript tests, **22/22 fast sessions PASS** and **18/18 required HCI states captured**. At that checkpoint, unchanged HCI budgets still fail density (50 > 27) and predicted KLM (65.31 > 65 seconds); p95 settled-DOM 825 ms and one focus loss are gaps. Full and release are NOT_RUN on that merge. Subsequent repairs and measurements need their own source-bound record; earlier numeric baselines below retain their historical subjects.

1. Repair the observed focus loss after asking for interpretations, then remeasure that exact path. Inspect the actual high-density states before choosing layout changes: canvas View has 50 visible chunks, pinned Domain/inspector 43 and runtime attempt details 38. Preserve useful context and deliberate opening of owner review; reduce repeated or irrelevant content without hiding necessary evidence or changing the budgets. Use the existing recorder, native controls, Dagre and axe.
2. Finish the reviewer task across S03/S04/S06/S07: inspect a real semantic change, follow exact source, investigate a failed/limited check and return to the same change or attempt. Formal raw-data context and runtime rule return work in the scoped replays; graphical counterexample correspondence is still incomplete and must never be invented from labels.
3. Exercise the complete supported P0 stories in more than one order, including first-use, stale/error, long-label, enlarged-text, keyboard and manual accessibility states. Obtain hands-on review beyond the scripted route and repair consequential findings.
4. Publish the validated integrated checkpoint, reproduce that exact published subject, then capture the usable IDE for the WOW walkthrough, clips and GitHub POC/POF package. Keep the existing `efd33fa7` fresh-clone result labeled as earlier evidence. Live-provider and comparative human claims require their separate observations.

The four personas remain design hypotheses. US13/14 factory coordination and US15 domain refactoring remain planned; the high-fidelity S09 design does not confer working orchestration. Choose external repositories after the first accepted EIJA flow. Reuse existing OSS and adapters before introducing another engine or framework.

**Implementation update, 3 October:** the [new validation checkpoint](2026-10-03-CODE-REVIEW-VALIDATION.md) records the implemented task navigator, paired model comparison, focused evidence and immutable code review. This proposal remains the design rationale. Its earlier density figures are historical; whole-app acceptance is still open.

**2 October 2026 — next build proposal.** This document proposes changes; they are not implemented by this plan. At that proposal checkpoint, density acceptance was **FAIL: 68 > 27** (the earlier captures reviewed below measured 70). The supported product is a model/change workbench with **read-only captured source navigation**; it is not a source-code authoring editor or a working agent factory.

## What to change, and why

The actual `final-recording-4/changes-before-after.png` shows a useful semantic comparison, but the added Save transition fills most of the editor before the next changed transition, related source or evidence becomes visible. The full domain tree remains open beside it. In `evidence-truth.png`, six claim cards, three formal-evidence disclosures, the blocker line, human-evidence callout, review questions, open Problems panel and status bar repeat some of the same facts. The persistent source-review banner is necessary; repeating its full message in several other simultaneously visible places is not.

The generated visual-change concept offers a better focal point: matched baseline/candidate geometry, changed elements, a short change navigator and immediate related evidence. Its illustrative arrows, statuses, source diffs and counts are **not** an implementation specification. The evidence concept's exact-rule investigation is useful, but no suggested authority-policy repair, inferred source behavior or invented runtime trace should be copied from it.

Build a coherent **selected-change → exact source → applicable evidence** loop first. Reduce actual duplicate content and irrelevant task controls while retaining free navigation. Keep the existing six work destinations and reference navigation; an arbitrary smaller tab count is not the proposed solution.

## Concrete hierarchy

| Area | Next implementation | Information and access retained |
|---|---|---|
| Global chrome | One case selector with current revision; one New intent entry; command search; one labelled Layout disclosure for pane controls. Keep undo/redo next to model editing and in History, rather than globally above unrelated evidence/source views. | Model/Source/Intent/Changes/Run/Evidence remain direct destinations. Commands retain keyboard access. The project/snapshot identity and offline/provider state remain readable. No duplicate New intent in explorer and toolbar. |
| Subject and status | One compact subject line and persistent source-review banner. The Evidence destination owns detailed claims; the global status states blocked/eligible and human UNKNOWN without duplicating the full claim inventory. | Full hashes and scope open in one action. Wrong-subject, stale, source-review-required and unknown states remain explicit at every consequential decision. No green overall score. |
| Navigator | In Model, retain the domain explorer. In Changes, offer a case-specific change navigator in that same pane, with changed/added/removed identity and total counts; a labelled switch returns to the domain tree. In Evidence, show the selected check/related rule context instead of every domain category by default. | This is a change of navigation purpose, not a second source of semantics. Restore each task's selection and panel preference. A user can pin the domain explorer. Do not silently replace a pinned navigator or discard its scroll/focus state. |
| Main Changes editor | One selected change, with aligned baseline/candidate diagram detail above its exact field differences. Keep all changed items available in the change navigator; show position/total and a clear “All changes” entry. | No swallowed changes or only-positive summaries. Added/removed elements say “Not present” on the absent side. Unchanged context is visible where needed for direction, but unchanged field rows are available by disclosure. |
| Main Evidence editor | Replace duplicate claim cards and formal summaries with one ledger keyed to actual evidence kind/subject. Each row shows property, status, freshness and scope; expanding a row shows exact assumptions, counterexample and provenance. Put owner review questions in a named “Review this subject” section, opened deliberately. | Show every kind's UNKNOWN/NOT_RUN/PARTIAL/FAIL state before opening details. Source review and human UNKNOWN stay visible. Reviewing is freely accessible, not an automatic next step; all existing owner authority checks remain server-owned. |
| Lower panel | Use Problems for actionable diagnostics while modelling/running; use History when requested. Do not render a second copy of the complete evidence/blocked summary beneath the Evidence editor. Keep a named Problems count/access point and preserve explicit user pinning. | A newly refused operation opens or identifies the relevant exact diagnostic. Errors and blockers remain reachable; success must not silently erase server blockers. Opening history/source and returning restores the current task. |

These changes can reduce **real simultaneously competing tasks**: global commands move to the relevant task; duplicated facts become one authoritative presentation; the explorer navigates the current review rather than unrelated material. No CSS invisibility trick, DOM reparenting for scoring, shortened font, clipped text or selective measurement is part of this design.

## The visual-diff implementation that earns the screen

1. Use `review.js.compare()` over the existing server baseline/candidate snapshots. Produce a complete ordered change inventory, including initial-state, state membership and transition field changes. Selection is a presentation reference `{case, revision, kind, id}`, not a copied model or inferred verdict.
2. Use the **vendored Dagre** runtime for a disposable comparison layout. Match only exact existing identities. Shared coordinates can be computed from the union of known IDs for display, but each side renders only its own snapshot's nodes and transitions. No ghost edge may imply behavior absent from that side; saved model layout must not be rewritten.
3. Default to readable detail around the selected transition and the context needed to understand its endpoints. Label that scope and the number of other changes; provide a real full-model overview and direct model inspection. Never imply that a selected neighborhood proves complete impact. Keep orientation and shared-node positions consistent across the pair, with an independent zoom/pan alternative when sizes differ.
4. Use text/shape plus restrained color for added, removed and changed elements. Show exact before/after role, endpoint, guards and effects beside the selected edge. No generated prose is needed to explain a changed value. At narrow widths stack Before and After in the same order with retained identities; do not shrink labels until illegible.
5. Place “Open bound source” and “Inspect evidence” next to that change. A source peek uses the existing exact-reference API, one file/symbol at a time, with line range, snapshot hash and read-only label. Unresolved bindings say so. Known impact uses only returned references/witnesses and an explicit coverage statement. An affected test/source link does not imply it ran or conforms.

Do not promise a graph animation, hypothetical effect, source-code patch, semantic conflict detector or agent activity the backend cannot supply. The meaningful demonstration is a reviewer selecting one actual rule change, seeing both versions without losing orientation, opening its captured source, and discovering exactly which assurance is missing.

## Implementation sequence and ownership boundaries

| Increment | Likely existing modules | Completion evidence |
|---|---|---|
| 1. Remove duplicate task chrome and evidence presentation | `app.js`, `index.html`, `app.css`, `shell.js`; existing native details/tabs/grid | Information-equivalence checklist mapping every old fact/action to its new location. Real HCI run over all current checkpoints, not a specially emptied layout. Preserve current keyboard, recovery, reflow and case-switch proofs. |
| 2. Selected change and comparison geometry | `review.js`, read-only adapter around `canvas.js`/vendored Dagre | Fixture comparisons for added/removed/changed/unchanged identities, initial state, roles, guards/effects, parallel edges and self-loops. Independent rendered-path/CTM oracle per side; planted wrong endpoint/label must fail. Original baseline/candidate and saved layout remain byte-equivalent. |
| 3. Related source/evidence beside the change | Existing source reader/API and evidence packet rendering | Exact GET oracle for URI/text/range/hashes; missing binding, source failure, stale subject and cross-case tests. Selecting a different change cannot display the previous change's source/evidence as current. |
| 4. Context restoration and full journey | Existing case views, shell layout, command palette and history APIs | Model-first, intent-first, source-first, case/history switch, reset-unsent-fields, refused edit, stale second page, failure/retry and keyboard replay. Zero new mutation on navigation/reset, no owner actions by agents. |

Use native accessible controls, current CSS layout, Dagre and existing Mermaid reference rendering. No new graph engine, framework migration or embedded source editor is needed for these increments. A comparison renderer may reuse geometry, but must have unique SVG marker/element identities for both simultaneous diagrams. Keep model semantics, transaction checks, evidence eligibility and owner authority in their existing server contracts.

## Density decision and acceptance

The earlier 70-item snapshot used to prepare this proposal contains **31 controls + 39 content groups**. A reduction to 27 requires at least 43 fewer counted items; a cosmetic pass cannot achieve that. The strongest plausible reduction is the combined removal of irrelevant global actions, full-tree competition and genuinely duplicate evidence/status. The amount saved is **unmeasured**. Do not assign an optimistic paper count to each new container or claim the target is solved in advance.

After increment 1, run the unchanged probe on the existing states **and** the actual new default/detail/error states needed for the stories, with screenshots showing counted items. Preserve raw/clipped accounting, disabled controls and open/pinned panel observations. Do not move required content below a fold just to escape the viewport count. If a reviewer must open a context panel and that necessary state still exceeds 27, retain the failure and the screenshot; passing an empty/default-only state is insufficient. Stop further decorative work and make that constraint conflict explicit if useful task context cannot coexist with the current limit.

Acceptance requires both the unchanged applicable gates and useful tasks. For the modeller, restore model/case/history selection and correctly distinguish unsent from committed changes. For the AI-assisted engineer, inspect interpretations and unknowns before explicit meaning selection, then inspect every resulting model change before requesting review. For the lead, detect a planted wrong subject/endpoint and identify UNKNOWN coverage without guessing. Factory coordination remains planned and has no acceptance credit here.

Retain browser/version, shipped asset hashes, state, viewport and negative controls for each proof. Inspect 1600×1100, 1280×800 and existing compact probes; require readable normal-scale labels, no new serious/critical axe findings or unintended focus loss, and real pointer/keyboard operation of disclosures. A generated image cannot close any row. A later counterbalanced human task study under the [V&V protocol](../research/2026-10-02-vv-protocol.md) tests comprehension burden; neither a lower chunk count nor a clean browser replay establishes it.

## Read-only inputs

- The retained [HCI report](../hci/REPORT.md) and [integration validation record](../engineering/2026-10-02-VALIDATION-CHECKPOINT.md); earlier captures are named separately in the browser report.
- `docs/design/WHOLE-APP-UX.md`, `WHOLE-APP-STORIES.md`, design README and visual-change/evidence-runtime concept images.
- Actual `work/ide-browser-qa/final-recording-4/changes-before-after.png` and `evidence-truth.png`; these are prior retained captures, not a new run.
- Current `review.js`, shell/evidence presentation and HTML navigation. Backend/source/owner capability boundaries remain as already implemented and tested; this document adds no capability claim.
## Earlier proposed acceptance order — 3 October

The strongest next working benefit is a complete reviewer task: understand a
specific change, follow its exact source and applicable evidence, detect a seeded
harmful change or unsupported claim, and recover without losing context. Prioritize
that usable loop; lower comprehension burden still needs observed human decisions.
Keep the existing four personas, fifteen stories, ten screens and H01–H10 in
[the story matrix](WHOLE-APP-STORIES.md) and [whole-app contract](WHOLE-APP-UX.md).
This sequence is engineering work, not a wizard users must follow.

| Order | User benefit / mapping | Next acceptance |
| --- | --- | --- |
| 1 | Historical baseline; all personas/H01–10 | At that checkpoint, preserve canonical1 and corrected canonical2, both FAIL. The corrected count is 56 > 27, KLM 65.31 > 65 s and p95 747.6 ms GAP. Close real UX/gate failures, new JavaScript line-identity repair and post-refactor checks without relaxing budgets. |
| 2 | Reviewer/lead and AI engineer can judge a change; US01/02/04/05/07/10/11, S10/S01/S03/S04/S06 | Complete source-first and review-first journeys through all changes, exact source, property/bounds/unknowns and available counterexamples. Check wrong fields/arrows/subjects, missing bindings, stale capture, failed refresh and cross-case return. Include populated/opened/pinned context. |
| 3 | Modeller and AI engineer can change, try and recover; US03/06/08/09 plus US02/10/11, S02/S05/S07/S08 | Complete intent or typed-edit entry, supported consequence preview, authoritative redraw/evidence invalidation, allowed/refused runtime actions and history recovery. Preserve unsent work on failure; cancel makes no mutation; stale and duplicate requests cannot silently apply. |
| 4 | All core personas can use and reproduce the supported IDE; US01–US12, S01–S08/S10 | Complete pointer/keyboard tasks and applicable empty/loading/error/stale variants at desktop, enlarged text and existing reflow sizes. Resolve manual accessibility/incomplete findings; measure paint-aware feedback separately. Reproduce the final published checkout with an independent engineer, then record the actual working product and limits. |
| 5 | Factory operator can inspect and land a bounded combined result; US13/14, S09 with S03/S04/S06/S08 | Reuse Git/worktree/agent tools. Prove ownership, known overlap witnesses, fresh base and actual merged-result verification plus authorized landing/recovery. Separate branch passes or agent cards are insufficient. |
| 6 | Modeller can use one explicit domain refactor; US15, S05/S03/S04/S06 | Choose one supported rename/split/merge adapter, inspect deterministic model/source/test effects and correspondence, test conformance and refusal. Unsupported transformations remain unavailable. |

Accessibility, subject truth and recovery apply in each increment, not only step
4. S09 and US13–US15 remain planned expansion; source authoring stays in the existing
editor/agent. Reuse the OSS register and current components before adding tools.

Observe representative reviewers, AI-assisted engineers and modellers on the real
loop while closing it. Predeclare matched seeded changes, correct decisions,
false alarms, completion/errors/effort and comparison conditions against existing
review practice; report sample and limitations. Factory personas remain hypotheses
until the coordination task exists. EIJA is first; select external repositories
after the first accepted flow and record actual language/semantic coverage.
Universal codebase correctness, general factory safety and reduced comprehension
burden remain unproved. A useful demo and reproducible proof should say so plainly.

At that earlier checkpoint, the corrected density maximum was Rules & ripple: 31 controls + 25 text-parent
groups, not the paired Changes layout. Inspect that actual state before simplifying
it. Source inspection suggests repeated state-card/rule-table facts and contextual
transition-edit discovery as candidates; the trace lacks a screenshot and named
text-group inventory, so these are hypotheses for task review. Preserve impact
coverage, exact subject, blockers and stable navigation. KLM's fixed pointer costs
require an actually evaluated equivalent task path; cosmetic changes alone cannot
close the 65.31-second failure.
