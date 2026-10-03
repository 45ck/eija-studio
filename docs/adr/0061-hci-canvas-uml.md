# HCI-ADR-0061: Canvas and drag-and-drop UML editing as typed transactions on a generated picture

Template: [template-hci.md](template-hci.md). Full design, task flows and tables: [../hci/design/canvas-uml-interaction.md](../hci/design/canvas-uml-interaction.md) (the "design document") and [../../design/tasks/canvas-flows.json](../../design/tasks/canvas-flows.json). Source ids `S1` to `S43` (`S38` is unused; `S24` is split into `S24a` to `S24e`), `M1` to `M3`, `R1` are defined in section 17 of the design document; the evidence table below repeats the URL for every claim this record leans on.

Revision 3 (2026-09-29, second audit): Tidy is priced as a different outcome with a same-outcome comparator (T04-move-x5); Tidy R is 5 x 70 ms (4.94 s); the T04-kbd stress cell is corrected (current faster); T04-inspector-form and T04-kbd are in the full stress table; toolbar buttons are counted as containers; undo coverage counts as one 15-word block; the deviation from the brief's T04 is an owner decision point; option cells are shortened; an unsourced claim about Mermaid Chart is removed. Revision 2 added option D-lite and the staged decision.

## Status

* Status: proposed. **Owner decision point:** D-lite (release 1 without a MEANING drag) versus D (MEANING drag in release 1). D-lite deviates from the task definition of T04 in `design/brief.json` (see Problem); it needs the owner's sign-off before acceptance.
* Date: 2026-09-29
* Aspect: interaction
* Author / lane: research agent, `lane/ux-research`, aspect `canvas-uml`
* Related: HCI-ADR-0066 (motion and performance, proposed: frame budget, no fetch in the drag loop); [ADR-0000](0000-poc-decision-log.md) ADR-003 (frozen vocabulary), ADR-004 (AI proposal-only), ADR-008 (layout is a separate subject dimension), ADR-012 (no silent rebase), ADR-013 (no build-time framework, DOM text nodes); [ADR-0016](0016-oss-first-adapters-not-engines.md); [ADR-0019](0019-diagrams-generated-from-executable-model.md). Principles P3, P6 to P12 in `docs/hci/research/PRINCIPLES.md`. Invariants I1 to I5 and I10.

## Problem and user goal

* Persona: P2 Domain-model owner (architect), primary. P1 reads the same picture during review. Personas are literature-derived HYPOTHESES.
* Job to be done: when I restructure the model, I want the diagram and the executable model to stay in step, so I do not hand-synchronise (J5); when a rule changes, I want to see what it touches before I commit it (J4).
* Task ids and frequency: T04 "Edit a state diagram by drag and drop" (weekly, HYPOTHESIS). `design/brief.json` defines it as: drag or connect states to emit a typed operation; the kernel accepts or refuses with a reason at the drop target; a non-drag path exists; only frozen-vocabulary operations execute. Variants are in `design/tasks/canvas-flows.json`. Other lanes use the label T04 for different flows (see the model section).
* Problem: the baseline "state view" is five non-focusable cards with no edges; a rule edit is a select plus a button and a layout edit is a select plus two number inputs inside a `<details>`. MEASURED (Chromium 151, real Studio, 1440 by 900, Impact tab, notice box visible): cards end at y = 913 of 900, the edit button starts at y = 938, the layout controls at y = 1102, the page scrolls to 1849, and the first 900 px hold 169 visible words. With the notice box empty (`design/layouts/current-impact.json`) every y is 71 px smaller. There is no picture in which an edit can be made or its effect seen, no undo, and no way to move several nodes except one at a time.
* Out of scope: tree editing, ripple lane, review chapters, palette contents, colour and type values, shell layout (design document section 1); any kernel vocabulary beyond the two typed edits that exist today (ADR-003).

## Evidence

Verified on 2026-09-29. Vendor and library pages were read through a fetch tool that returns a model-written summary, so those rows are at most medium.

| Claim | Source URL | Source type | Confidence | Verified on |
|---|---|---|---|---|
| SC 2.5.7 (AA): dragging must be achievable by a single pointer without dragging; keyboard alone does not satisfy it; click-then-click, buttons, menus, text fields are accepted | https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html | standard | high | 2026-09-29 |
| SC 2.5.8: targets at least 24 by 24 CSS px, spacing exception | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | standard | high | 2026-09-29 |
| SC 2.5.2: up-event completion needs abort or undo | https://www.w3.org/WAI/WCAG22/Understanding/pointer-cancellation.html | standard | high | 2026-09-29 |
| SC 1.4.1 and 1.4.11: colour not the only cue; 3:1 for UI components and focus indicators | https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html and https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html | standard | high | 2026-09-29 |
| Composite widget = one tab stop, roving focus (examples: radio group, tablist, menu, grid, toolbar, tree); `role="group"` as container is a fit by analogy | https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/ | official guidance | high for the pattern, UNVERIFIED for the fit | 2026-09-29 |
| ARIA Graphics Module is a Recommendation (2018-10-02); AT support not tested; `aria-grabbed` deprecated | https://www.w3.org/TR/graphics-aria-1.0/ and https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-grabbed | standard; documentation | high for status, UNVERIFIED for support | 2026-09-29 |
| GLSP: typed operations (`CreateEdge`, `ReconnectEdge`, `ChangeBounds`); server validates; edge hints (static, or dynamic via `RequestCheckEdgeAction`); `ChangeBounds` is graphical only; server command stack | https://www.eclipse.dev/glsp/documentation/protocol/ | official documentation | medium | 2026-09-29 |
| GLSP validation runs on the server because only it knows the model | https://www.eclipse.dev/glsp/documentation/validation/ | official documentation | medium | 2026-09-29 |
| draw.io: connectors from hover arrows with valid-target outline; Alt suspends grid snapping | https://www.drawio.com/docs/manual/connectors/ and https://www.drawio.com/docs/reference/shortcuts/modifier-shortcuts-in-diagrams/ | official documentation | medium | 2026-09-29 |
| draw.io: regenerating a Mermaid diagram keeps styles and labels, resets positions, sizes and connector paths | https://www.drawio.com/blog/mermaid-diagrams | first-party blog | high | 2026-09-29 |
| FigJam: Tidy up arranges objects into a grid; connector ends can be dragged to another object | https://help.figma.com/hc/en-us/articles/1500004362321-Guide-to-FigJam | official documentation | high | 2026-09-29 |
| Figma: Control suspends snapping; a guide appears; no threshold documented | https://help.figma.com/hc/en-us/articles/360039956914-Adjust-alignment-rotation-and-position | official documentation | high | 2026-09-29 |
| tldraw: Tab reading order, Ctrl/Cmd+arrows to nearest shape, live-region "description, type, n of total" | https://tldraw.dev/sdk-features/accessibility | official documentation | high | 2026-09-29 |
| dnd-kit keyboard sensor: Space/Enter, arrows, Escape; `role="button"`, `aria-roledescription`, instructions, live region | https://dndkit.com/guides/accessibility | library documentation | medium | 2026-09-29 |
| Atlassian: drag should not be the only way; move actions in a menu | https://atlassian.design/components/pragmatic-drag-and-drop/design-guidelines | vendor design guidance | medium | 2026-09-29 |
| Snap-and-go: stop at aligned positions instead of warping; up to 138% (1D) and 231% (2D) faster than no snapping; slightly slower than traditional snapping | https://doi.org/10.1145/1054972.1055014 (abstract via https://api.openalex.org/works/doi:10.1145/1054972.1055014) | peer-reviewed, abstract only | medium | 2026-09-29 |
| Snap-dragging uses automatically placed guiding lines | https://doi.org/10.1145/15922.15912 (abstract via OpenAlex) | peer-reviewed, abstract only | medium | 2026-09-29 |
| Feedforward bridges Norman's Gulf of Execution | https://doi.org/10.1145/2470654.2466255 (abstract via OpenAlex) | peer-reviewed, abstract only | medium | 2026-09-29 |
| Amulet command objects allow selective undo of any earlier operation | https://doi.org/10.1145/238386.238526 (abstract via OpenAlex) | peer-reviewed, abstract only | medium | 2026-09-29 |
| Shneiderman: permit easy reversal; offer informative feedback | https://www.cs.umd.edu/users/ben/goldenrules.html | author site | high | 2026-09-29 |
| Claude Code rewind lists what it does not restore | https://code.claude.com/docs/en/checkpointing | vendor documentation | high | 2026-09-29 |
| Response-time classes 0.1 s, 1 s, 10 s | https://www.nngroup.com/articles/response-times-3-important-limits/ | practitioner research | high as a convention | 2026-09-29 |
| KLM operators: K 0.12 / 0.20 (55 wpm) / 0.28 (design point) / 1.2 s; P 1.1; B 0.1; H 0.4; M 0.6 to 1.35 with 1.2 recommended | https://web.eecs.umich.edu/~kieras/docs/GOMS/KLM.pdf (TLS check failed in WebFetch; downloaded with `curl -k`, text read locally) | first-party author document | high for the numbers | 2026-09-29 |
| KLM: 21% RMS error; expert, error-free routine tasks only | https://en.wikipedia.org/wiki/Keystroke-level_model | secondary | medium | 2026-09-29 |
| Menu pointing Tp = 0.37 + 0.13 ID s, R2 = 0.93, 8 participants; used here for 2D pointing and drags (extrapolation) | https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf (text read locally) | peer-reviewed paper | high for the fit, low for the extrapolation | 2026-09-29 |
| Cognitive Dimensions definitions | https://www.cl.cam.ac.uk/~afb21/CognitiveDimensions/CDtutorial.pdf | tutorial by the authors | high | 2026-09-29 |
| CSP: `worker-src` falls back to `child-src`, `script-src`, `default-src`; `style-src` blocks style attributes, `<style>`, `cssText` but not `element.style.prop` | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/worker-src and https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/style-src | documentation | high | 2026-09-29 |
| MEASURED: under the Studio CSP, SVG presentation and `transform` attributes apply, `element.style` works, `setAttribute("style")` and SVG `<style>` are blocked, a blob worker is blocked, a same-origin worker constructs (execution not tested) | local `.tmp/canvas-uml/measure.py`, Chromium 151.0.7922.34 | measurement | high for this browser only | 2026-09-29 |
| MEASURED: edit POST p50 19.5 ms, layout POST p50 18.2 ms, case GET p50 23.8 ms, n = 20; p95 indicative only | local `.tmp/canvas-uml/latency.py` | measurement | high at p50 for this machine | 2026-09-29 |
| Library facts: elkjs 0.12.0 "EPL-2.0 OR GPL-3.0-or-later"; tldraw and Excalidraw need React; maxGraph needs a bundler; JointJS core MPL-2.0, key parts paid | https://registry.npmjs.org/elkjs/latest (same path for the others), https://github.com/maxGraph/maxGraph, https://tldraw.dev/community/license, https://github.com/clientIO/joint, https://github.com/dagrejs/dagre, https://js.cytoscape.org/ | registry; repositories | high for registry fields, medium for pages | 2026-09-29 |
| MEASURED sizes: `elk.bundled.js` 1,609,707 B (466,995 gzip); `cytoscape.min.js` 435,503 B (136,441); `dagre.min.js` 48,956 B (17,091); independent re-run within 35 B gzip | files from https://cdn.jsdelivr.net/npm/, `gzip -9` locally | measurement | high | 2026-09-29 |
| ASF: EPL-2.0 category B, GPL category X (context only; EIJA is not an ASF product) | https://www.apache.org/legal/resolved.html | policy page | medium; not legal advice | 2026-09-29 |
| **Against:** dragging is slower and more error-prone than pointing | https://doi.org/10.1145/108844.108868 (abstract via OpenAlex) | peer-reviewed, abstract only | medium | 2026-09-29 |
| **Against:** Structurizr says re-parenting is generally not easy via a UI (argues for models as code) | https://docs.structurizr.com/as-code | vendor documentation | medium | 2026-09-29 |
| **Against (own model):** no MEANING edit has a robust speed advantage; the keyboard MEANING path may be slower than the baseline; Tidy's large gain prices a different outcome | this record, Quantitative model | model output | n/a | 2026-09-29 |

## Quantitative model

* Model and formula: KLM, total = sum of operators. Pointing MT = a + b x ID, ID = log2(D/W + 1), D centre to centre, W the smaller side. All results **PREDICTION**.
* Inputs and sources: M 1.35 s; K 0.20 s (Kieras 55 wpm; chord = 2); B 0.10 s per press or release; H 0.40 s; a = 0.37 s, b = 0.13 s/bit (Cockburn et al. 2007, menu pointing; extrapolated). R = 70 ms per kernel commit (MEASURED: POST plus two GETs, 67 ms); five sequential commits = 350 ms. Geometry profile **D** (headline: current MEASURED with the notice box, proposed from design document appendix B.2) and profile **L** (cross-check: `design/layouts/current-impact.json`, `design/layouts/proposed-canvas.json`). Popup rows ESTIMATED 22 px. Pointer starts at (720, 450). Flows: `design/tasks/canvas-flows.json`. Band plus or minus 21%.
* Result for the current design (PREDICTION, s): T04 reconnect 5.62 (4.44 to 6.80); T04-move 8.68 (6.86 to 10.51); five nodes by form (T04-tidy and T04-move-x5 current) 24.50 (19.36 to 29.65); T04-kbd 2.62 (2.07 to 3.17); T04-move-kbd 6.77 (5.35 to 8.19); T04-undo 5.62 (a repeat edit: the baseline has no undo).
* Result for the proposed design (PREDICTION, s): T04 drag 3.04; T04-click 3.24; **T04-lite 3.20 (2.53 to 3.87)**; **T04-inspector 3.39 (2.68 to 4.10)**; T04-inspector-form 5.13; T04-move 3.18 (2.51 to 3.85); **T04-move-x5 15.90 (12.56 to 19.24) with one M per node, 10.50 (8.30 to 12.71) planned once**; T04-tidy 4.94 (3.90 to 5.98), batch 4.66; T04-kbd 2.22 (1.75 to 2.69); T04-move-kbd 3.82; T04-undo 2.22; T04-refuse-lite 4.48 and T04-refuse 4.29 (no current equivalent). Revision 1 gave T04-tidy 3.49 s (omitted the preview M); revision 2 gave 4.84 s (R = 250 ms, inconsistent with the 70 ms rule).
* **Tidy prices a different outcome.** The current five-node flow places nodes where the user chose; Tidy applies an algorithmic layout the user accepts. Its speed matters only when the result is acceptable, and layout quality is UNKNOWN. The same-outcome comparator is T04-move-x5.

Arithmetic for T04 (profile D):

| Op | Current | s | Proposed (stage-2 drag) | s |
|---|---|---|---|---|
| M | locate control below the fold | 1.35 | know where the handle is | 1.35 |
| K | one wheel notch | 0.20 | | |
| P | D 425, W 44, ID 3.41 | 0.814 | D 175, W 24, ID 3.05 | 0.766 |
| B | click (2) / press | 0.20 | press | 0.10 |
| M | choose the value | 1.35 | | |
| P | D 44, W 22, ID 1.58 (ESTIMATED) | 0.576 | drag D 203, W 56, ID 2.21 | 0.657 |
| B | click (2) / release | 0.20 | release | 0.10 |
| P | D 183, W 49, ID 2.24 | 0.662 | | |
| B | click (2) | 0.20 | | |
| R | reload | 0.07 | reload | 0.07 |
| Total | | 5.622 | | 3.043 |

* Decision flips inside the band? Tested on every task: flat P = 1.1 s, Kieras design point (M 1.2, K 0.28), doubled drag slope, current one M fewer, proposed one M more (full table: design document section 11.2; profile L in the same section).

| Task | Base separate? | Current one M fewer | Proposed one M more | Robust |
|---|---|---|---|---|
| T04, T04-click, T04-lite, T04-inspector | yes | 4.27 vs 3.04 to 3.39: overlap | 5.62 vs 4.39 to 4.74: overlap | **no** |
| T04-inspector-form | no | 4.27 vs 5.13: overlap | 5.62 vs 6.48: overlap | no |
| T04-kbd | no | 1.27 vs 2.22: **separate, current faster** | 2.62 vs 3.57: overlap | no; possibly slower |
| T04-move | yes | 7.33 vs 3.18: separate | 8.68 vs 4.53: separate | **yes** |
| T04-move-x5, one M per node | yes (by 0.12 s) | 23.15 vs 15.90: overlap | 24.50 vs 17.25: overlap | no |
| T04-move-x5, planned once | yes | 23.15 vs 10.50: separate | 24.50 vs 11.85: separate | **yes** |
| T04-move-kbd | yes | 5.42 vs 3.82: overlap | 6.77 vs 5.17: overlap | no |
| T04-tidy | yes | 23.15 vs 4.94: separate | 24.50 vs 6.29: separate | yes, but a different outcome |
| T04-undo | yes | 4.27 vs 2.22: separate | 5.62 vs 3.57: separate | yes, but prices a workaround |

  **Speed claims that survive:** moving one node (T04-move), and arranging several nodes by drag if the user plans once. No MEANING edit has one; the four MEANING paths differ by 0.35 s at most. The keyboard MEANING path is possibly slower than a keyboard-savvy baseline user (and its flows are asymmetric: the proposed flow assumes the edge is already selected; two arrow keys to reach it give 2.62 s, equal to the baseline).
* Baseline label reconciliation: HCI-ADR-0066's T04 is the numeric-field layout edit (10.17 s vs 3.85 s flat-P; its "6.3 s" is the difference). It corresponds to T04-move here (9.67 s vs 3.82 s flat-P). The layout lane's T04 adds navigation and uses R = 300 ms. The integrator should rename the three T04s.
* Validity limits: KLM and Fitts cover expert, error-free, routine pointing, not learning, reading a refusal, mode errors, drag errors or discoverability. Drag times use pointing constants and are lower bounds. Cockburn's constants (8 participants, vertical menu items) are extrapolated to 2D pointing and drags; that uncertainty is outside the band. Its 0.37 s intercept follows a menu-button click, so separate B operators may double-count a little; the flat-P row bounds this. The M count is analyst judgement (hence the one-M stresses). R is one machine, n = 20. The 0.1 s, 1 s, 10 s classes are conventions. No result shows that users will find the canvas pleasant or decide better.
* Deliberate deviations from the model: the confirmation before a drop that would clear a recorded decision costs one keypress and stays (undo cannot restore a cleared decision; P11, ADR-008). The Tidy ghost preview costs one M and stays for the same reason. Approve and apply are not on the canvas (P2).

## Options considered

| Option | What it is and who does it (source) | Advantages | Drawbacks | Verdict |
|---|---|---|---|---|
| A: baseline | select plus Apply; select plus number fields; static cards (repository, MEASURED) | works; keyboard-reachable; only legal values | below the fold; no picture of positions; no undo; 24.5 s for five nodes | kept as the non-drag path and degraded mode |
| B: canvas SDK (tldraw, Excalidraw, maxGraph, JointJS, Cytoscape.js) | free-form editors: https://tldraw.dev/sdk-features/accessibility, https://www.drawio.com/docs/manual/connectors/; licences https://tldraw.dev/community/license, https://github.com/maxGraph/maxGraph, https://github.com/clientIO/joint | mature drag, zoom, hit-testing | React or bundler (fails ADR-013); tldraw not OSI; JointJS key parts paid; each owns a second model; 0.4 to 47 MB | rejected |
| C: read-only generated diagram plus forms | Structurizr https://docs.structurizr.com/as-code; one-way Mermaid rendering | simplest; no drag accessibility problem | no direct manipulation; layout stays a form | rejected as target; kept as degraded mode |
| D: custom SVG, every gesture a typed request, including a MEANING drag with drop-target refusal | GLSP protocol shape https://www.eclipse.dev/glsp/documentation/protocol/; FigJam connector drag https://help.figma.com/hc/en-us/articles/1500004362321-Guide-to-FigJam | meets ADR-013 and CSP; one model; matches brief T04 literally | D-lite's cost plus handle, drop ghost, drop refusal UI; LAYOUT-vs-MEANING misidentification risk; drag errors; no robust speed gain | not chosen for release 1; stage-2 study arm (H-C4) |
| **D-lite**: custom SVG, drag for LAYOUT only; MEANING by select-edge-then-click, inspector, keyboard, palette | draw.io snapping https://www.drawio.com/docs/reference/shortcuts/modifier-shortcuts-in-diagrams/; FigJam Tidy up (URL above); WCAG 2.5.7 https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html; Atlassian menus https://atlassian.design/components/pragmatic-drag-and-drop/design-guidelines | drag where the model predicts a gain (T04-move); the 2.5.7 path is the primary path; no handle or drop-refusal UI | no direct manipulation of meaning; deviates from brief T04 (refusal on click, not at a drop target); handle expectation unmeasured; code size UNKNOWN | **chosen for release 1, subject to owner sign-off** |
| E: text-first (edit Mermaid or PlantUML) | draw.io resets layout on re-edit https://www.drawio.com/blog/mermaid-diagrams | familiar to some developers | contradicts ADR-0019 (model is the source); round trips lose layout | rejected; text is a read-only export |

D-lite versus D: D-lite removes the handle, the drag path for meaning (press, drag, drop, abort, drop refusal) and the replacement-edge ghost; both need I-K1, I-K3, I-K4, I-K5, the log, Tidy, snapping and the accessible twin. "Fewer gesture classes to teach" is analyst judgement, not evidence. The owner may choose D outright.

## Decision

Chosen option: "D-lite for release 1, with the MEANING drag of option D as a pre-registered study arm (stage 2)", because the model supports drag where it is robust (moving nodes) and not where it is not (every MEANING edit overlaps under the one-M stress), because the MEANING drag adds error-proneness and a LAYOUT-versus-MEANING misidentification risk for an edit with two legal values, because WCAG 2.5.7 already forces the non-drag path that D-lite makes primary, and because option B fails ADR-013, the licence test or the one-model rule. GLSP documents the split this needs: typed operations validated by the server, layout operations separate from model operations, a server-side command stack. **The choice does not rest on a speed advantage for any MEANING edit, nor on Tidy's 4.94 s, which prices a different outcome.** It deviates from the brief's T04 definition (drop-target refusal) and is proposed pending the owner's decision (Status).

Concrete behaviour (D1 to D13 in the design document):

1. **D1 Projection and typed requests.** The canvas is drawn from the model. A gesture sends one typed request (`LayoutChange` or `SemanticTransaction`) or nothing. Without kernel affordances the canvas is read-only.
2. **D2 Gesture classes.** VIEW, LAYOUT (keeps domain evidence, clears the decision), MEANING (evidence STALE, clears the decision), outcome REFUSED; each with word tag, glyph, stroke style and live-region sentence; colour never alone.
3. **D3 Ghost and policy feedback.** Tier 1: kernel affordance map (legal targets, refusal codes), no round trip. Tier 2: kernel consequence summaries delivered with the case; no fetch in a drag loop or hover; very large models fall back to one event-driven dry run per target entry. An illegal click or drop shows the kernel code and one sentence at the target.
4. **D4 Snapping.** 8-unit grid, alignment guides, stop-not-warp, capture 6 px (HYPOTHESIS), Alt or Option suspends, clamp 0..2000.
5. **D5 Connectors.** Release 1: selecting the Reject edge arms its source end and outlines legal states; no drag handle. Stage 2: a 24 by 24 handle on the Reject source end only. Connect is disabled with `UNSUPPORTED_WORKFLOW_SHAPE`.
6. **D6 Auto-layout.** Deterministic layered placement for nodes without a stored position; explicit Tidy with ghost preview and Apply as one undoable LAYOUT batch; dagre fallback; elkjs deferred.
7. **D7 Undo and redo.** Append-only transaction log; undo is an inverse transaction; coverage in three labelled lines (15 words in total); refusals are "not recorded" lines; a drop that would clear a recorded decision asks for one confirmation.
8. **D8 Non-drag paths.** Node: numeric fields, keyboard lift mode. Meaning: select-edge-then-click (primary), inspector segmented control, keyboard move-source mode, palette. Escape aborts.
9. **D9 Accessibility semantics.** One tab stop, roving focus, `role="button"` with `aria-roledescription`, one polite live region, rule table as accessible twin; Graphics ARIA roles not relied on; container role tested.
10. **D10 Implementation rules.** `createElementNS`, attributes and classes, `element.style` only via CSSOM, Pointer Events; no `<style>`, no `setAttribute("style")`, no blob worker; a new script file needs an `/assets` allowlist entry.
11. **D11 OSS.** No canvas SDK; a custom-module row for `docs/oss/REGISTER.md` is drafted in design document section 10.
12. **D12 Timing.** Feedback in the 0.1 s class; commit 43 to 67 ms at p50 (MEASURED, n = 20); PENDING state for slower disks.
13. **D13 Staging.** Release 1 = D-lite. The MEANING drag is promoted only if H-C4 holds (drag beats the click arm by more than the band, misidentification at most 1 of 12, every refusal recovered within 30 s), or when connector creation becomes executable.

Invariants and principles: **AI proposes, the kernel checks, the owner decides** (I1): no gesture applies or approves; AI proposals appear as dashed `PROPOSED` ghosts with no accept control. **Generated from the model** (I2, P3): DOM equals render(model, layout). **UNKNOWN visible** (I3): never drawn as unaffected. **Providers and agents never approve or apply** (I4): log, undo, palette and canvas keys contain no approve or apply. **Untrusted text through text nodes** (I5, ADR-013). **No user-benefit claim** (I10).

Interfaces this decision depends on (design document section 1): kernel affordance map with consequence summaries, batch layout, layout history, refusal refs; `/assets` allowlist; tokens; selection bus; palette commands; change overlay; shell layout; density deviation I-D1. Conflicts with `design/layouts/proposed-canvas.json` are in design document appendix B.3; in particular `handle-reject-source` must stay behind a stage-2 flag because three stage-2 flows reference it.

## Anti-slop rubric check

PREDICTIONS for the excursion model, counted by hand; the slop-budget script was not run. UNKNOWN is not a pass.

| Item | Target | Result | Value | MEASURED or PREDICTION |
|---|---|---|---|---|
| No decorative gradient, glassmorphism or blur | 0 | pass | 0; ghost is a dashed stroke | PREDICTION |
| No card inside card | nesting depth at most 3 | pass | depth 2 (pane, node) | PREDICTION |
| Containers per primary viewport | at most about 12 | **fail without deviation** | 10 at rest in the canvas region (pane, 5 nodes, 4 bordered toolbar buttons), 11 with Tidy Apply, 13 with the inspector options; plus one per extra state. Deviation requested (I-D1): count diagram nodes as content marks | PREDICTION |
| No emoji, no icon-per-bullet | 0 | pass | glyphs are SVG paths with a visible word | PREDICTION |
| No generic hero plus three-feature grid | 0 | not applicable | canvas region only | not applicable |
| No default gradient or unexamined font stack | rationale present | not applicable | no colour or font chosen here | not applicable |
| No placeholder or fake data; every number sourced | 0 unsourced | UNKNOWN | real excursion states and kernel codes; one ESTIMATED number without a source (module size 25 to 45 KB); HYPOTHESES labelled (6 px, 4 px, 4 s, 8 units) | not applicable |
| Prose blocks of 8 or more words | about 30 words per viewport | pass (hand count) | 0 at rest; refusal 12, consequence 11, mode 8, confirmation 8, layout-history 9, MEANING undo coverage 15 (three lines counted as one block); largest simultaneous set 20, worst case 26 | PREDICTION |
| Visible chrome words | at most about 120 | pass for the canvas region | 14 at rest; 17 during a Tidy preview; baseline MEASURED 169 in the first 900 px | PREDICTION; baseline MEASURED |
| Distinct font sizes | at most 6 | pass | 3 | PREDICTION |
| Type families | 2 plus monospace | pass | none added | PREDICTION |
| Elevations | at most 2 | pass | 0 | PREDICTION |
| Accent hues | 1 plus status hues | pass | accent marks MEANING; LAYOUT neutral | PREDICTION |
| Eyebrow labels | at most 1 | pass | 0 | PREDICTION |
| Disclosure depth | at most 2 | pass | refusal and status at level 0; log drawer level 1 | PREDICTION |
| Colour never the only carrier | 0 violations | pass by design, UNKNOWN until simulated | word, glyph and stroke pattern per class | PREDICTION |

## Accessibility check

| Check | Standard | Result | Evidence |
|---|---|---|---|
| Text contrast computed | SC 1.4.3 | UNKNOWN | token values do not exist yet (I-T1) |
| Non-text contrast | SC 1.4.11: 3:1 | UNKNOWN | roles named; values pending |
| Colour not the only cue | SC 1.4.1 | pass by design; CVD pending | word, glyph, stroke pattern; refused targets dotted with a cross |
| Target size | SC 2.5.8 | pass by design | edge hit stroke 24 px, stage-2 handle 24 by 24, toolbar 28 to 32 px high, inspector options 140 by 32, nodes 112 by 48 or larger |
| Dragging has a non-dragging path | SC 2.5.7 | pass by design | node: numeric fields; meaning: select-edge-then-click, inspector control |
| Keyboard, visible focus, reading order | SC 2.1.1, 2.1.2, 2.4.7 | pass by design; untested | one tab stop, roving focus; Tab and Escape leave; mode line names exit keys |
| Pointer cancellation | SC 2.5.2 | pass by design | commit on up event; Escape or release off target aborts |
| Text spacing and reflow | SC 1.4.12, 1.4.10 | UNKNOWN | 1.4.10 exempts two-dimensional diagrams; SVG text spacing not evaluated |
| Reduced motion | `prefers-reduced-motion` | pass by design | revert and Tidy movement become instant |
| Name, role, state, position in set | APG composite widget; dnd-kit pattern | UNKNOWN | names carry "n of total"; real screen readers UNVERIFIED; `group`, `toolbar`, `application` compared in the test plan |
| APCA Lc (advisory) | not a gate | not computed | no colour values yet |

## Validation plan

* Prototype measurements (one browser at a time, 1440x900 and 1280x720): pointer-move to ghost paint p95 at most 100 ms over a scripted 5 s drag; commit round trip p95 within HCI-ADR-0066's commit class (warn 300 ms, fail 1000 ms) with at least 30 trials, on C: and D:; no request inside the drag frame loop; CSP smoke with zero violations; every interactive element at least 24 by 24 CSS px; G2, G3a, G3 reachable by keyboard only and by click only; every refused target maps to a section 6 code; DOM equals render(model, layout) on 5 fixtures; slop counts within design document section 13 or a recorded deviation; contrast and CVD once tokens exist; flows recomputed from real geometry.
* Pass criteria, fixed before running: the numbers above, and no verdict in the decision-flip table changes with real geometry.
* User-study protocol reference: design document section 15.
  * Design: within-subject, current Studio versus proposed canvas, counterbalanced. Reconnect arms: form, inspector control, select-edge-then-click, drag handle, keyboard.
  * Participants: at least 12 for a comparative claim; formative rounds of about 5; a keyboard-only cohort and a screen-reader cohort.
  * Tasks: T04 (all arms), T04-move, T04-move-x5 (target positions fixed on a sketch), T04-tidy (with an acceptability rating of the result), T04-undo, T04-refuse-lite; T04-refuse in the drag arm.
  * Measures: time on task; errors; refused attempts and recovery time; class misidentification; UNKNOWN or STALE misread as current (target zero); skipped decision confirmations; SEQ; SUS; Raw NASA-TLX.
  * Analysis: pre-registered H-C1 (click paths and drag differ by less than the band), H-C2 (node drag beats the form on T04-move and T04-move-x5; Tidy time reported only for participants who keep its result), H-C3 (misidentification at most 1 of 12 per arm), H-C4 (promotion of the MEANING drag); effect sizes with intervals.
  * Stop criteria: 2 or more of 12 misclassify LAYOUT and MEANING on seeded gestures; any approval with an unread UNKNOWN; any refusal not recovered within 30 s.
* Status of results: none. **No user-benefit claim is made until results exist.**

## Consequences

* Good: a picture in which the owner acts on what they see; drag for positions; a non-drag primary path for meaning; refusal reasons at the point of error; layout stored apart from meaning; one typed request path for pointer, keyboard, inspector and palette; undo that says what it does not restore; no dependency that fails ADR-013, the CSP or the licence.
* Bad: about 25 to 45 KB (ESTIMATED, no source) of new script; three kernel additions and one allowlist change first; only two edits are executable, so release 1 moves nodes and changes one edge end; the owner's drag-and-drop request and the brief's drop-target refusal are met for positions only; the keyboard MEANING path may be slower than the baseline; error-proneness rises against the select box; the canvas region uses most of the container budget.
* Cognitive Dimensions impact (analyst judgement; design document section 14): repetition viscosity falls; knock-on visible before commit; hidden dependencies visible for drawn edges; secondary notation kept by id; error-proneness rises, mitigated by refusal, outlines and undo; hard mental operations shift from coordinates to keyboard modes.
* Security and repository impact: CSP unchanged; `/assets` allowlist grows by `canvas.js` or the code lives in `app.js` (I-S1); browser asset change requires source review (ARCHITECTURE.md); no new network path; kernel additions need a regression test and an ADR (AGENTS.md).
* Licence check: no third-party code or asset included. Evaluated: maxGraph Apache-2.0, Cytoscape.js MIT, dagre MIT, JointJS core MPL-2.0, Excalidraw MIT, tldraw source-available with production key, elkjs "EPL-2.0 OR GPL-3.0-or-later". Not legal advice.
* Revisit when: the owner chooses D; the study meets H-C4 or breaks a stop criterion; Tidy results are rejected by most participants; the kernel vocabulary grows beyond a few executable edit kinds; a model exceeds about 30 nodes; p95 commit latency exceeds 100 ms (30 trials or more); a screen-reader test fails; a cited source changes.

## Definition of ready

- [x] Persona, task ids and frequency stated (with the brief's T04 definition)
- [x] Each evidence row has a URL, type, confidence and date; rows argue against the decision (three)
- [x] Model outputs labelled PREDICTION with constants and band; validity limits; decision-flip test on every task
- [x] At least three options including the baseline, each with a source URL
- [x] Rubric table complete (UNKNOWN not counted as pass)
- [x] Accessibility table complete
- [x] Validation plan with pass criteria fixed in advance, study reference, stop criteria
- [x] No claim of user benefit without a study
- [ ] Owner decision on D-lite versus D (deviation from brief T04)
