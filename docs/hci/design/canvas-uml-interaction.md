# Canvas and drag-and-drop UML interaction

Lane `lane/ux-research`, aspect `canvas-uml`. Date 2026-09-29. Status: proposed; the decision record is [HCI-ADR-0061](../../adr/0061-hci-canvas-uml.md). Task flows: [design/tasks/canvas-flows.json](../../../design/tasks/canvas-flows.json). Source ids (`DGM§2.9`, `LAW§2.4`, `V6`) are defined in [../research/SYNTHESIS.md](../research/SYNTHESIS.md) section 1; ids `S1` to `S43` (`S38` is unused; `S24` is split into `S24a` to `S24e`), `M1` to `M3` and `R1` are defined in section 17 of this file. Every number is labelled MEASURED, ESTIMATED, HYPOTHESIS or PREDICTION. Nothing here has been tested on users and no user benefit is claimed.

Revision 3 (2026-09-29, after a second audit): Tidy is labelled a different outcome and gets a same-outcome comparator (T04-move-x5); Tidy R corrected to 5 x 70 ms (4.94 s); T04-kbd and T04-inspector-form added to the stress table (the keyboard MEANING path may be slower than the baseline); toolbar buttons counted as containers; undo coverage counted as one 15-word block; release-1 refusal flow T04-refuse-lite added; the brief deviation is recorded as an owner decision point.

## 0. Decisions first

| # | Decision | Confidence | Evidence |
|---|---|---|---|
| D1 | The canvas is a projection of the executable model. A gesture emits exactly one typed request or nothing. The kernel accepts or refuses; the picture is redrawn from the accepted model. The client holds no copy of the policy. Without kernel-supplied affordances the canvas is read-only. | Medium | S10 (GLSP: server validates, server command stack), DGM§3.1, AGENTS.md ("no second interpreter"), section 2 |
| D2 | Every gesture belongs to one of three classes with distinct word, glyph and ghost: **VIEW** (nothing recorded), **LAYOUT** (`LayoutChange`; keeps domain evidence, clears the recorded decision), **MEANING** (`SemanticTransaction`; makes exact-subject evidence STALE, clears the decision). A fourth outcome, **REFUSED**, changes nothing. | Medium | S10 (ChangeBounds is graphical only), ADR-008, `service.py`, section 4 |
| D3 | Ghost preview and policy feedback use two tiers, both kernel outputs: an **affordance map** (legal targets and refusal codes) and **consequence summaries** for each legal drop or click target, precomputed per model version and delivered with the case, so neither the drag loop nor a hover performs a **fetch**. Models too large to precompute fall back to an event-driven dry run on target entry, outside the frame loop. An illegal drop is refused at the target with the kernel code and one sentence. Legal and illegal cues never rely on colour. | Medium | S10 (static hints plus dynamic server check), S20 (feedforward), S15, M3 |
| D4 | Snapping: 8-unit grid and alignment guides to other nodes' edges and centres, **stop-not-warp**, capture 6 screen px (HYPOTHESIS), Alt/Option suspends, world clamped to the kernel bounds 0..2000 with a visible limit line. | Low to medium | S18, S21, S12, S8 |
| D5 | Connector creation is **capability-gated**. Today the only executable connector edit is changing the Reject source end, which has two legal values. A Connect tool is listed but disabled with the kernel's reason until the kernel advertises an executable connector kind. | Medium | `policy.py`, `service.py`, S7, S13, S10 (ReconnectEdge, edge check) |
| D6 | Auto-layout: a deterministic layered placement, computed and never stored, places only nodes without a stored position. **Tidy** is an explicit, previewed, undoable LAYOUT batch. Built-in engine first; dagre (MIT, 49 KB) if needed; elkjs deferred (1.6 MB, EPL-2.0 OR GPL-3.0-or-later). | Low to medium | S14, S13, S29, M2b size table |
| D7 | Undo and redo are the **transaction log**: append-only, undo is an inverse transaction, every undo lists what it does not restore in short labelled lines (section 8), refusals are shown as "not recorded". A drop that would clear a recorded decision asks for confirmation first. | Medium | S16, S22, S10, S27, ADR-012 |
| D8 | Non-drag paths for every drag: click-then-click and inspector controls (single pointer, WCAG 2.5.7), keyboard lift mode, palette commands. Keyboard alone does not satisfy 2.5.7. Escape aborts a drag (2.5.2). | High for the standard | S1, S24b, S25, S26 |
| D9 | Accessibility semantics: one tab stop with roving focus, `role="button"` plus `aria-roledescription` on nodes and edges, polite live region, and the existing rule table kept as the accessible twin. ARIA Graphics roles are not relied upon. | Low: assistive-technology behaviour is UNVERIFIED | S3, S4, S5, S25 |
| D10 | Custom SVG built with `createElementNS`, geometry and paint as attributes, classes from `app.css`, `element.style` only through the CSSOM, Pointer Events. No `<style>` element, no `setAttribute("style")`, no blob worker. A new script file needs an `/assets` allowlist change. | High for the CSP facts (MEASURED, one browser) | M2, S39, S40 |
| D11 | No canvas SDK is adopted. Each candidate fails at least one hard constraint or would own a second model. | Medium | section 12, S28 to S37 |
| D12 | Feedback timing follows the 0.1 s and 1 s classes; a commit round trip on this PC is about 43 ms (one POST plus one GET) to 67 ms (the baseline's POST plus two GETs) at p50 (MEASURED, n = 20 each), so no optimistic state is needed here; a PENDING state is specified for slower machines. | Medium | S15, M3 |
| D13 | **Staging (option D-lite first).** Release 1: LAYOUT drag with snapping, Tidy, and MEANING edits by selecting the edge and then clicking a legal state, using the inspector segmented control, the keyboard or the palette. There is **no MEANING drag handle** in release 1. The MEANING drag (G3, the rest of option D) is built only as a study arm and is promoted when the promotion criteria in section 15 are met or when the kernel vocabulary makes connector creation executable. Reason: the drag is not predicted to be faster in any robust way, it adds the LAYOUT-versus-MEANING misidentification risk and a drop-target refusal UI, and WCAG 2.5.7 requires the non-drag path anyway. The owner may override this; the added cost is listed in HCI-ADR-0061 option D. | Medium | section 11.2, S1, S19, section 14 |

**Headline prediction (PREDICTION, KLM plus Fitts, band plus or minus 21%; every row survives or fails the stress tests of section 11.2).**

| Task | Current (s) | Proposed (s) | Robust? |
|---|---|---|---|
| Move one node (T04-move) | 8.68 | 3.18 | yes: separable in every stress row |
| Place five nodes where the user chooses, one drag each (T04-move-x5, same outcome as the form) | 24.50 | 15.90 (one M per node); 10.50 (one M for the whole plan) | 15.90: **no** (overlaps in 4 of 5 stress rows and in the layout-file geometry); 10.50: yes |
| Tidy five nodes (T04-tidy, five POSTs): **different outcome** (algorithm places, user accepts) | 24.50 | 4.94 | separable, but prices a different outcome; valid only when the algorithmic layout is acceptable (UNKNOWN) |
| Change the Reject source by drag (T04) | 5.62 | 3.04 | **no**: bands overlap with one M fewer for the current flow |
| The same by click-then-click on the handle (T04-click) | 5.62 | 3.24 | **no** |
| The same by selecting the edge, then a state (T04-lite) | 5.62 | 3.20 | **no** |
| Move one node by keyboard (T04-move-kbd) | 6.77 | 3.82 | **no** |
| Keyboard-only source change (T04-kbd) | 2.62 | 2.22 | **no**; with one M fewer the **current** flow is faster (1.27 vs 2.22, separable) |

Only moving one node (T04-move) carries a clean speed claim. Arranging five nodes by hand is faster only if the user plans the arrangement once (10.50 s); with one decision per node, as the baseline flow is charged, the claim does not survive the stress rows. Tidy (4.94 s) is fast because it does a different job: it replaces manual arrangement only when its result is acceptable, which is UNKNOWN. No speed claim is made for any MEANING edit: dragging the Reject source end, clicking the handle, and selecting the edge then a state differ by 0.2 s or less, far inside the band, and the keyboard path may be slower than the baseline for a keyboard-savvy user. Speed is therefore not the reason to build the MEANING drag; directness, visible refusal reasons and layout persistence are, and they need a study. This is why decision D13 stages the MEANING drag behind the study.

**Deviation from the brief.** `design/brief.json` defines T04 as "drag or connect states to emit a typed operation; the kernel accepts or refuses with a reason at the drop target". Release 1 (D13) ships no MEANING drag and no drop-target refusal: refusal appears on a click instead. This is a deviation from the brief's task definition and is an **owner decision point** (HCI-ADR-0061, Status). The promotion path is H-C4 (section 15).

**What this document does not settle.** Tree editing (T05), ripple (T03), review chapters (T02), palette contents (T09), status glyphs and colour values, and the shell layout. Where the canvas depends on them the assumption is listed in section 1 as an interface.

## 1. Interfaces to other aspects and to the kernel

Nothing below is guessed silently. Each row is an assumption the owning aspect must confirm or change.

| Id | Interface | Owner | What the canvas assumes | If it changes |
|---|---|---|---|---|
| I-K1 | Affordance map in the case payload | kernel (new) | For each editable end: legal targets, and for each refused target a code from `policy.py` | Without it the canvas is read-only (D1) |
| I-K2 | Consequence summary per legal drop, in the case payload next to I-K1; and, for models above about 64 legal (handle, target) pairs (HYPOTHESIS), a dry run `POST /api/cases/{id}/edit/check` | kernel (new) | Pure: runs `check_policy` and `apply_transaction`, returns `{accepted, errors[], changed[], clears{decision, exact_subject_evidence}}`; both functions are already pure | Ghost shows tier 1 only; consequence chips are absent |
| I-K3 | Batch layout `POST /api/cases/{id}/layout` with `changes[]`, atomic | kernel (new) | Tidy commits as one transaction; today five POSTs (PREDICTION 350 ms, 5 x 70 ms) | Tidy is five requests and five log entries |
| I-K4 | Layout changes recorded in the transaction log with before and after | kernel (new) | Today only `SemanticTransaction` is stored (`case.transactions`); layout keeps the latest value only | Layout undo works within a session only and says so |
| I-K5 | Refusal payload `{code, message, refs[]}` with element ids | kernel (small) | `DomainError` already carries code and message; refs are new | Refusal shows at the pointer, not on the offending element |
| I-S1 | `/assets` allowlist gains `canvas.js` | security-boundary aspect | `http.py` allows only `app.js` and `app.css` today | Canvas code must live inside `app.js` |
| I-T1 | Tokens | tokens aspect | Roles named in section 5.4; values are theirs | Contrast becomes UNKNOWN until values exist |
| I-N1 | Selection bus | navigation aspect | One selected model id shared by tree, lane, canvas; canvas element ids are model ids (`Recommended`, `TR-REJECT`) | Selection stays local to the canvas |
| I-P1 | Palette commands | palette aspect | `canvas.tidy`, `canvas.undo`, `canvas.redo`, `canvas.move-node`, `canvas.reconnect-source`; no approve or apply (I4) | Keyboard path uses canvas keys only |
| I-R1 | Change overlay | review aspect | The dry-run projection can be drawn as ADDED / MODIFIED / REMOVED on the canvas | No overlay |
| I-L1 | Shell layout | layout aspect | Canvas pane at least 720 by 520 CSS px at 1440 by 900; toolbar inside its top edge; inspector docked at its right | Appendix B geometry is re-derived |
| I-D1 | Density metric | density aspect | Diagram nodes count as content marks, not chrome containers (deviation request, section 13) | Canvas exceeds the container budget above about 10 nodes |

## 2. What the kernel executes today (read from source, 2026-09-29)

| Fact | Source in repo |
|---|---|
| Workflow has 5 states (Draft, Submitted, Recommended, Approved, Rejected) and 5 transitions (Submit, Recommend, Approve, Reject, Revise) after the recommendation meaning is selected; the baseline has 4 states | `domain/policy.py` `baseline()`, `apply_transaction()` |
| `SemanticTransaction.kind` is `enable_recommendation` or `set_rejection_source`; after selection `edit()` accepts only `set_rejection_source` (`UNSUPPORTED_EDIT` otherwise); the source is `Submitted` or `Recommended` | `domain/models.py`, `application/service.py` |
| `enable_recommendation` is reachable only through meaning selection from a proposal (`select()`); it cannot be replaced silently (`CASE_ALREADY_SELECTED`) | `application/service.py` |
| `LayoutChange` is `{node, x, y}`, x and y integers 0..2000, node must be a workflow state (`UNKNOWN_NODE`); the layout is `dict[node] -> {x, y}`; edges have no stored layout | `domain/models.py`, `service.layout()` |
| Any edit or layout change sets `decision = None`, moves the stage to `PREVIEW`, and, if a decision existed, records `DecisionInvalidated` with reason "semantic edit" or "exact presentation changed" | `service.edit()`, `service.layout()` |
| Technical evidence dimensions are semantic, implementation, policy, environment, harness; presentation is excluded from receipt applicability but included in the decision subject; a receipt with a different technical subject is `STALE` | `domain/evidence.py`, `compiler.subject_for()`, ARCHITECTURE.md |
| Policy refusal codes: `UNSUPPORTED_WORKFLOW_SHAPE`, `UNSUPPORTED_ACTION`, `PROTECTED_AUTHORITY:<action>`, `PROTECTED_STATE:<action>`, `UNSUPPORTED_REJECTION_SOURCE`, `GUARD_POLICY:<action>`, `EFFECT_POLICY:<action>`; service and HTTP codes: `MEANING_REQUIRED`, `STALE_VERSION`, `CASE_CLOSED`, `POLICY_BLOCKED`, `CONTRACT_REJECTED` (422) | `domain/policy.py`, `service.py`, `interfaces/http.py` |
| Impact closure per changed action is a fixed chain: rule, runtime, state-view, journey, obligation, receipt, review-packet, local-decision | `domain/impact.py` |
| Baseline state view: five `div` cards in a flex row, not focusable, no edges; layout is edited through a select plus two number inputs inside a `<details>` | `resources/web/app.js`, `index.html` |

Consequence: **the drag editor would execute exactly two kinds of request today**, a node move (LAYOUT) and a Reject-source reconnect with two legal values (MEANING). Every other gesture is a visible refusal. The design must not imply general model editing (SYNTHESIS section 5).

## 3. Gesture map

Pointer gestures, the typed request each becomes, what the ghost shows, and the non-drag path. "Kernel" means the request goes to the existing endpoint; refusals come from the codes in section 2.

| # | Gesture | Class | Typed request | Ghost while dragging | Outcome on accept | Non-drag path |
|---|---|---|---|---|---|---|
| G1 | Pan, zoom, select, hover, focus | VIEW | none | none | nothing recorded; per-viewer view state may go to `localStorage` inside try/catch | keyboard arrows, `+`, `-`, `0` |
| G2 | Drag a node body | LAYOUT | `LayoutChange{node, x, y}` | dashed outline of the node at the snapped position; alignment guides; tag `LAYOUT` | node moves; log entry; decision cleared | inspector position fields; keyboard lift mode |
| G3a | **Stage 1.** Click the Reject edge (its source end is armed, legal states are outlined), then click a legal state | MEANING | `SemanticTransaction{set_rejection_source, rejection_source: <state>}` | none while pointing; legal targets outlined and labelled, illegal targets dotted with a cross; tag `MEANING`; precomputed consequence chips on hover or focus of a legal target | edge redrawn from the accepted model; log entry; decision cleared; evidence STALE | this is the non-drag path; inspector segmented control; keyboard move-source mode; palette |
| G3 | **Stage 2 (study arm, D13).** Drag the **tail handle** of the Reject edge onto a state | MEANING | `SemanticTransaction{set_rejection_source, rejection_source: <state>}` | legal targets outlined and labelled, illegal targets dotted with a cross; dashed replacement edge from the pointer; tag `MEANING`; precomputed consequence chips (dry run only for large models) | edge redrawn from the accepted model; log entry; decision cleared; evidence STALE | G3a; inspector segmented control; keyboard move-source mode; palette |
| G4 | Drag any other edge end (stage 2 only; in stage 1 no end is draggable) | REFUSED | none sent; the affordance map already says why | no handle is drawn; pressing on the end shows the refusal sentence (`PROTECTED_STATE:<action>`) | nothing changes | inspector shows the same reason as text |
| G5 | Hover a node, drag from an arrow handle to another node (connector creation) | REFUSED today | would be `add_transition`; not in the frozen vocabulary | not offered: the Connect tool is disabled with `UNSUPPORTED_WORKFLOW_SHAPE` | nothing | none needed |
| G6 | Drop a palette shape (new state) onto the canvas | REFUSED today | `add_state`; not in the vocabulary | not offered; the Recommended state exists only through meaning selection in the Change view (`enable_recommendation`) | nothing | none needed |
| G7 | Delete or rename a state or edge (Delete, F2, double-click) | REFUSED today | none | none | announced refusal with `PROTECTED_STATE` or `UNSUPPORTED_WORKFLOW_SHAPE` | none needed |
| G8 | Tidy (button, palette) | LAYOUT | `LayoutChange[]` in one batch (I-K3) | dashed target positions for every node in scope with a short line from each current position; tag `LAYOUT`; Apply and Cancel appear beside the button | all positions change in one log entry | Enter applies, Escape cancels |
| G9 | Undo, redo | as the undone entry | inverse `SemanticTransaction` or `LayoutChange` | none | new log entry `UNDO of #n` | Ctrl/Cmd+Z, Ctrl/Cmd+Shift+Z |

**Read-only states.** Before a meaning is selected there is no candidate (`MEANING_REQUIRED`); the canvas shows the baseline workflow with a `BASELINE` tag and no handles. After `APPLIED` or `DISCARDED` (`CASE_CLOSED`) the canvas is read-only and the log is frozen.

**Effects of each class (derived from code, not run).**

| | Decision | Receipts | Preview instance | Stage | Log |
|---|---|---|---|---|---|
| VIEW | unchanged | unchanged | unchanged | unchanged | none |
| LAYOUT | cleared; renew exact-presentation approval | kept and still applicable (presentation is not a technical dimension) | unchanged | to PREVIEW | entry with before and after positions |
| MEANING | cleared | kept as originals; recomputed applicability gives STALE for the old subject | stale; the baseline UI drops it | to PREVIEW | `SemanticTransaction` appended |
| REFUSED | unchanged | unchanged | unchanged | unchanged | session-only line "not recorded" |

Whether undoing a MEANING edit makes an older receipt applicable again follows from `assess_receipt` (same semantic hash gives the same verdict) but was not executed; a kernel test must confirm before the undo text says so (UNKNOWN until then).

## 4. Making layout-only visibly different from meaning

The rule (P3, ADR-008): a picture edit that does not change meaning must never look like one that does. Three redundant channels, none of them colour alone (WCAG 1.4.1, S24c).

| Channel | VIEW | LAYOUT | MEANING | REFUSED |
|---|---|---|---|---|
| Word tag at the pointer and in the log | none | `LAYOUT` | `MEANING` | `REFUSED` plus the code |
| Ghost outline | none | dashed, neutral, same shape as the node | solid outline on the drop target plus a dashed replacement edge | dotted outline on the target with a cross glyph |
| Consequence line (transient, at most 12 words) | none | "Position only. Decision cleared." | "MODIFIED Reject starts at Submitted (was Recommended). Decision cleared. Evidence STALE." | kernel sentence from section 6 |
| Log glyph and verb | none | outlined square with an offset arrow; "Moved" | filled diamond; "Changed" | crossed circle; "Refused" |
| Live-region text | none | "Moved Rejected to 176, 372. Layout only." | "Reject now starts at Submitted. Meaning change." | "Refused. Reject can start only at Submitted or Recommended." |
| Cursor | grab | move | crosshair | not-allowed |

Accent hue marks MEANING and is neutral for LAYOUT, but the word and shape carry the meaning. Whether users tell the two classes apart is not known; it is a primary study measure (section 15).

## 5. Ghost preview, snapping and connectors

### 5.1 Ghost preview and policy feedback (D3)

Feedforward shows what will happen before the action is committed (S20 reframes feedforward as a way across Norman's gulf of execution; the abstract read gives no effect size). GLSP splits validation into static type hints on the client for immediate feedback and a dynamic server check when the answer needs model knowledge (S10). EIJA has no client-side policy, so both tiers are kernel outputs:

| Tier | Content | Source | Latency | Used for |
|---|---|---|---|---|
| 1 Affordance map | per handle: legal targets; per refused target: a code | I-K1, precomputed per model version (5 states, so a few dozen entries) | 0 round trips, inside the 0.1 s class | which targets to outline, which to dot; refusal sentence on hover |
| 2 Consequence summary | accepted or not; changed elements; whether the decision and exact-subject evidence would be cleared | I-K2: precomputed with tier 1 for every legal (handle, target) pair; for large models a dry run requested when the pointer **enters** a legal target (an event, not per frame), one in flight, cached by (case version, request) | precomputed: 0 round trips; dry run: no dry-run endpoint exists, so the edit POST is a **proxy** for its cost (MEASURED p50 19.5 ms, p95 21.9 ms, n = 20 and p95 is then the second-largest sample, indicative only; M3); shown as "checking" if it exceeds 100 ms | consequence chips, MODIFIED label, evidence effects |

A refused drop is cancelled, the handle returns to its origin, and the refusal sentence stays for four seconds or until the next gesture (HYPOTHESIS). The refusal text names the kernel code in monospace so a report can cite it.

### 5.2 Snapping and alignment guides (D4)

| Item | Decision | Basis |
|---|---|---|
| Grid | 8 world units, snap on | draw.io and Figma snap to grids and objects; both let the modifier suspend snapping (S8: Alt for draw.io; S12: Control for Figma) |
| Guides | thin line to another node's left, centre, right, top, middle or bottom edge while within capture; no distance labels in v1 | Bier and Stone 1986 use automatically placed guiding lines to help precise placement (S21); Figma shows a guide when snapping occurs (S12) |
| Behaviour | **stop, not warp**: the ghost holds at the aligned position while the pointer moves inside the capture zone, then continues | Baudisch et al. 2005: stopping at aligned positions instead of warping removes the need to deactivate snapping; reported 138% (1D) and 231% (2D) faster alignment than no snapping in their studies, and slightly slower than warp snapping (S18) |
| Capture radius | 6 screen px | HYPOTHESIS. Figma documents no threshold (S12). Calibrate against the T04-move task |
| Suspend | hold Alt or Option | draw.io precedent (S8); Baudisch shows a modifier is not needed but exceptions remain |
| Bounds | positions clamp to 0..2000 in world units; a limit line and the words "limit 2000" appear at the edge | kernel contract `LayoutChange` (`ge=0, le=2000`); a 422 `CONTRACT_REJECTED` must never be the first the user hears of it |
| Result | ghost shows raw pointer position (thin cross) and snapped position (dashed outline) | keeps the difference visible |

### 5.3 Connector creation and reconnection (D5)

| Situation | Behaviour |
|---|---|
| Reconnect the Reject source (today's only executable connector edit) | **Stage 1:** selecting the Reject edge arms its source end; legal states are outlined (G3a). No handle is drawn. **Stage 2 (study arm):** the tail of the Reject edge carries a visible dot with a 24 by 24 hit area (WCAG 2.5.8, S2). Pressing it starts G3. Legal targets get a 2 px solid outline and the word `starts here`; refused targets get a dotted outline and a cross. FigJam also reconnects by dragging a connector's start or end point (S13). |
| Other edge ends | No handle is drawn (nothing to grab that would only refuse). A press on the end shows why (G4). This keeps the refusal count low without hiding the fact that the end is locked. |
| Create a connector | Draw.io creates connectors by hovering a shape and dragging from a direction arrow, and outlines the valid target while dragging (S7). EIJA copies that pattern only for connector kinds the kernel lists as executable. Today none is, so the Connect tool appears in the toolbar and the palette **disabled, with the reason** (`UNSUPPORTED_WORKFLOW_SHAPE`). When a kind appears: hover arrow, drag, tier-1 outlines, tier-2 check (GLSP `RequestCheckEdgeAction` analogue, S10), release creates a `CreateEdge`-style typed request. |
| Routing | Derived, never stored (the kernel stores positions of states only). Forward edges are straight; the Reject edge is orthogonal; the Revise back-edge runs under the row. No manual waypoints; draw.io's waypoint editing (S7) is deliberately absent because the kernel has nowhere to store waypoints. |

### 5.4 Token roles the canvas needs (values belong to the tokens aspect)

`canvas.surface`, `canvas.node.fill`, `canvas.node.stroke`, `canvas.edge`, `canvas.focus` (at least 3:1 against adjacent colours, WCAG 1.4.11, S24d), `canvas.ghost.stroke`, `canvas.meaning.accent`, `canvas.layout.neutral`, `canvas.legal`, `canvas.refused`, `canvas.guide`, plus the status roles for the one glyph slot on each node (top right, 16 px). Dashed and dotted patterns are strokes, not colours. Contrast is UNKNOWN until values exist.

## 6. Refusal catalogue

The sentence is ours; the code is the kernel's. The kernel should return both (I-K5). Sentences are content decisions to be checked in the study.

| Kernel code | Sentence at the drop or click target | Words |
|---|---|---|
| `UNSUPPORTED_REJECTION_SOURCE` | Reject can start only at Submitted or Recommended. | 8 |
| `PROTECTED_STATE:<action>` | `<action>` goes from `<from>` to `<to>`: protected policy. | 8 |
| `PROTECTED_AUTHORITY:<action>` | Who may perform `<action>` is protected policy. | 7 |
| `GUARD_POLICY:<action>`, `EFFECT_POLICY:<action>` | Guards and effects of `<action>` are protected policy. | 8 |
| `UNSUPPORTED_WORKFLOW_SHAPE`, `UNSUPPORTED_ACTION` | States and actions are fixed (ADR-003). Adding or removing one is unsupported. | 12 |
| `UNSUPPORTED_EDIT` | After a meaning is selected, only the rejection source can be edited. | 12 |
| `MEANING_REQUIRED` | Choose a supported meaning in Change before editing. | 8 |
| `CASE_ALREADY_SELECTED` | The selected meaning cannot be silently replaced. | 7 |
| `STALE_VERSION` (409) | The case changed elsewhere. Reload before editing. The drop is reverted. | 11 |
| `CASE_CLOSED` | This case is closed. Create a new Change Case. | 9 |
| `UNKNOWN_NODE` | Only workflow states have a position. | 6 |
| `CONTRACT_REJECTED` (422) | Position must be 0 to 2000. (The clamp in section 5.2 prevents this.) | 6 |
| `AUTHORITY_REQUIRED` (403) | This session may not make this edit. | 7 |

Word counts are by hand (`<action>` counted as one word). The longest sentence is 12 words; section 13 uses the maximum.

## 7. Auto-layout (D6)

| Question | Decision | Basis |
|---|---|---|
| When does automatic layout run? | Only for nodes with no stored position. Stored positions always win. Nothing re-lays out implicitly. | draw.io resets geometry when a Mermaid diagram regenerates (S14); Structurizr and FigJam offer layout as a separate command (DGM§2.8, S13) |
| Where are defaults stored? | Nowhere. They are a pure function of the model, so the same model always draws the same picture (I2). Only owner-made positions are stored (`LayoutChange`). | ADR-008, ADR-0019 |
| Which algorithm first? | A built-in deterministic layered placement: layer = longest path from the initial state over forward edges; back edges (Revise) ignored for layering; order inside a layer follows the model's `states` order. It reproduces the Appendix B picture for the excursion model. | 5 states and 5 transitions today; a custom pass of a few dozen lines avoids a dependency |
| When a library? | If the built-in pass gives visibly worse results on a model with more than about 30 nodes, adopt `@dagrejs/dagre` (MIT, `dist/dagre.min.js` 48,956 B raw, 17,091 B gzip, MEASURED). elkjs only if ports, orthogonal routing or hierarchy are required and the licence review passes. Layout **quality** was not compared: UNKNOWN. | S35, S28, M2b |
| What does Tidy do? | Scope: selection or all. Shows the ghost of every target position, then Apply or Cancel. On Apply it is one LAYOUT batch (I-K3) and one undo step. It renews the exact-presentation approval and keeps domain evidence. | FigJam Tidy up arranges selected objects (S13); yEd and Structurizr precedents (DGM§2.8, 2.10) |
| Interactive mode | ELK's `interactive` option keeps existing positions and modifies the layout as little as possible (S29). Not used in v1; recorded as the route if elkjs is adopted. | S29 |
| Choice offered to the user | One command, one algorithm, until a second algorithm exists. A menu of one is not shown. | Hick-Hyman does not apply to a single choice; no evidence for a second algorithm here |

Mental-map preservation is the reason to keep stored positions stable. The primary papers (Misue et al. 1995; Purchase et al. 2006) were not opened with an abstract; only a 2013 title on the effect of mental-map preservation was found. The claim that stable layout helps orientation is therefore carried by the Cognitive Dimensions definition of secondary notation (S17) and by the observed loss in draw.io (S14), not by a cited experiment: UNVERIFIED as an effect.

## 8. Undo and redo as the transaction log (D7)

| Item | Decision | Basis |
|---|---|---|
| Model | Append-only log of typed transactions. Undo appends an inverse transaction (`UNDO of #7`); redo appends the original again. Nothing is deleted or rewritten. | ADR-012 retains originals; GLSP keeps a server command stack with undo and redo actions (S10); Amulet command objects support selective undo of any earlier operation (S22) |
| Entry | `#seq`, class glyph and word, verb phrase, request arguments, before and after values, time, outcome, coverage string | P11 |
| What is logged | MEANING and LAYOUT transactions. Refusals appear as "not recorded" lines for the session only. VIEW gestures are not logged. | kernel stores only accepted transactions today |
| Shown where | A drawer under the canvas listing entries newest first; the same component is reused by the review aspect for the list of typed operations of an agent change (I-R1) | one component, two uses |
| Confirm before | A drop or Tidy when a decision exists (stage APPROVED): "This clears the recorded decision for revision N." (8 words). One extra keypress. Otherwise commit on release and offer Undo. | Shneiderman rule 6 easy reversal (S16); a cleared decision cannot be restored by undo |
| Coverage lines for MEANING undo (three labelled lines, at most 7 words each) | "Restores: Reject starts at Recommended." (5) / "Not restored: owner decision, approve again." (6) / "Not undone here: Apply." (4). The three lines are shown together and count as **one 15-word block** in the prose budget (section 13). The earlier 36-word string is withdrawn: it exceeded the prose budget, and its clause about evidence receipts stated something not yet executed (section 3, last paragraph). Evidence status after an undo is shown by the kernel-recomputed status glyphs, not by a sentence. | Claude Code lists what rewind does not track (S27) |
| Coverage lines for LAYOUT undo | "Restores: position of Rejected." (4) / "Not restored: owner decision, renew presentation approval." (7) | ADR-008 |
| After reload | MEANING entries are restored from `case.transactions`. LAYOUT undo needs I-K4; until then the button says "Layout history is not recorded before this page load" (9 words, shown on demand). | kernel stores latest layout only |
| Closed case | Undo and redo disabled with the reason (`CASE_CLOSED`) | `service.py` |
| Authority | Undo never approves, applies or re-approves; no palette or keyboard path from the log reaches approve or apply | I4 |
| Keys | Ctrl/Cmd+Z, Ctrl/Cmd+Shift+Z; not intercepted while a text field has focus | native text undo must keep working |

## 9. Keyboard and non-drag alternatives (D8, D9)

### 9.1 What WCAG requires

SC 2.5.7 (Level AA) requires that functionality using a dragging movement can be achieved by a **single pointer without dragging**; the Understanding page states that a keyboard-only alternative does not satisfy it, and lists click-then-click, adjacent buttons, pop-up menus after a click and text fields as accepted alternatives (S1). Keyboard operation is separately required by 2.1.1. The design therefore ships both:

| Path | Satisfies | Steps for G3 (reconnect Reject source) |
|---|---|---|
| Drag (pointer), stage 2 only | usability | press tail handle, move, release on a legal state |
| Click-then-click (stage 1 primary path, G3a) | 2.5.7 | click the Reject edge (its source end is armed, legal targets outlined, status line names the mode), click a legal state; Escape or a click on empty canvas disarms. In stage 2 the same works from the tail handle |
| Inspector segmented control | 2.5.7, screen readers | select the Reject edge; choose `Submitted` or `Recommended` (two toggle buttons, refused options stay listed with the reason as a description) |
| Keyboard move-source mode | 2.1.1 | see 9.2 |
| Palette command | 2.1.1 | `canvas.reconnect-source Submitted`, shown enabled or blocked with reason (I-P1) |
| Numeric position fields | 2.5.7 for G2 (node drag, which stays in stage 1) | x and y inputs in the inspector, kept from the baseline |

Atlassian's drag-and-drop guidance likewise says drag should never be the only way and recommends move actions in a menu (S26).

### 9.2 Keyboard model

The canvas is one composite widget with one tab stop and roving focus, as the APG keyboard guidance describes (S3). Tab and Shift+Tab leave it; Escape cancels the current mode. Escape and Tab are standard ways out, so no notice is required by 2.1.2 (S24e), but the mode line states them anyway.

| Key | In navigate mode | In lift or move-source mode |
|---|---|---|
| Arrow keys | move focus to the nearest node or edge in that direction | move the ghost by 8 units (lift) or cycle the **legal** targets (move-source) |
| Shift+Arrow | none | move 32 units (lift only) |
| Space or Enter | lift the focused node; on a selected edge with an editable end, start move-source | drop and commit |
| Escape | none (focus stays) | cancel; the ghost disappears, nothing is sent (2.5.2 abort, S24b) |
| Delete, F2 | refusal announced (G7) | not applicable |
| `+`, `-`, `0` | zoom, fit | not applicable |
| Ctrl/Cmd+Z, Ctrl/Cmd+Shift+Z | undo, redo | not applicable |

The pick-up, move, drop and cancel keys follow the pattern of the dnd-kit keyboard sensor (Space or Enter, arrows, Space or Enter, Escape) (S25); its nodes carry `role="button"`, `aria-roledescription` and an instruction element referenced by `aria-describedby`. The reading-order and nearest-neighbour navigation follows the tldraw design, which uses Tab for reading order and Ctrl/Cmd+arrows for the nearest shape (S9); EIJA uses plain arrows because the canvas is a composite widget and Tab must leave it.

**Mode error.** Lift mode and navigate mode share the arrow keys. The mode is written in a status line inside the canvas ("Moving Rejected. Arrows move, Enter drops, Esc cancels", 8 words) and announced. Mode errors are not measured; the keyboard cohort in the study looks for them.

### 9.3 Assistive-technology semantics (D9)

| Element | Role and name | State |
|---|---|---|
| Canvas | `role="group"`, name "State diagram, 5 states, 5 transitions" (fit by analogy: the APG keyboard page lists radio group, tablist, menu, grid, toolbar and tree as composite examples, not `group`; the AT test plan evaluates `group`, `toolbar` and `application` variants) | none |
| Node | `role="button"`, `aria-roledescription="state"`, name "Recommended, state, 3 of 5" | `aria-pressed` for selection |
| Edge | `role="button"`, `aria-roledescription="transition"`, name "Reject, Registrar, from Recommended to Rejected" | `aria-pressed` |
| Status line and outcomes | one polite live region (`role="status"`, S4) | announces selection, mode, accepted, refused |
| Rule table (baseline strength, kept) | native `<table>` with the same selection | the accessible twin: every state and transition is readable and editable through the inspector without the canvas |

The tldraw announcement pattern is "description, type, n of total" in a live region (S9). The WAI-ARIA Graphics Module is a W3C Recommendation of 2018-10-02 and defines `graphics-document`, `graphics-object` and `graphics-symbol` (S5); no assistive-technology support was tested, so those roles are **not relied upon**: UNVERIFIED. `aria-grabbed` and `aria-dropeffect` are deprecated and are not used (S6).

Reduced motion: the only animation is the revert of a refused drop and the Tidy move, both replaced by an instant jump when `prefers-reduced-motion` is set; motion never carries meaning.

## 10. Implementation constraints (D10)

**MEASURED (M2).** Chromium 151.0.7922.34 headless, the real Studio server, its real CSP (`default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; ...`), 2026-09-29. Script injected with the page's own DOM APIs.

| Test | Result | Consequence |
|---|---|---|
| SVG `fill`, `stroke`, `stroke-width`, `stroke-dasharray`, `transform`, `marker-end`, `fill="url(#pattern)"` set as attributes with `setAttribute` | applied, no violation | geometry and paint may be attributes |
| `element.style.opacity`, `element.style.transform`, `style.setProperty` | applied, no violation | CSSOM is a legal fallback for dynamic values |
| `setAttribute("style", ...)` on an SVG element | blocked (`style-src-attr`), value ignored | never used |
| `<style>` element inside the SVG | blocked (`style-src-elem`) | all class rules live in `app.css` |
| `new Worker("/assets/app.js")` | constructed, no violation; **execution under the CSP not tested** (construction succeeds even if the later script load fails) | MDN's fallback rule (S39) implies a same-origin worker file is allowed by `script-src 'self'` once the allowlist serves it; the design does not depend on a worker |
| `new Worker(blob:...)` | violation `worker-src blob:` | no inline or blob workers |

MDN documents the same: `worker-src` falls back to `child-src`, then `script-src`, then `default-src` (S39), and `style-src` blocks style attributes and `<style>` but not `element.style.prop` (S40). This narrows SYNTHESIS C15 for one browser; Firefox and Safari were not tested, and Lit and adopted stylesheets were not tested.

**Rules.**

1. Build nodes and edges with `document.createElementNS("http://www.w3.org/2000/svg", ...)`; labels through `textContent` only (ADR-013, I5). State names are model text and are untrusted.
2. Geometry and paint as attributes; states (`data-state`, `data-class`) select class rules in `app.css`; ghost dashes are a class.
3. Pointer Events with `setPointerCapture` for mouse, touch and pen; `touch-action: none` on the canvas as a class rule; drag begins after 4 px of movement (HYPOTHESIS) so a click is not a drag.
4. Commit on the up event; Escape or release on a refused target aborts (2.5.2 option 2, S24b).
5. `expected_version` is sent with every request as the baseline does; a `STALE_VERSION` reverts the ghost.
6. The canvas module is new script. It needs the allowlist entry I-S1 or must live in `app.js`. The baseline is 10,561 B of JavaScript and 7,156 B of CSS (MEASURED, `wc -c`, 2026-09-29). A canvas module is ESTIMATED at 25 to 45 KB unminified; that number has no source and must be replaced by a measurement.
7. `docs/oss/REGISTER.md` row for the integrator: capability "Canvas editor for the generated state diagram"; OSS checked: maxGraph, Cytoscape.js, tldraw, Excalidraw, JointJS, elkjs, dagre (section 12); EIJA custom glue: `canvas.js` (about 25 to 45 KB, ESTIMATED); why custom: no candidate meets ADR-013, the CSP and the licence together without owning a second model; replacement path: dagre for layout when models exceed about 30 nodes, or an SVG editor that passes the CSP smoke test.

## 11. Quantitative model (PREDICTION)

**Formulas and constants.** KLM: total is the sum of operators. M 1.35 s (the Card, Moran and Newell value; Kieras recommends 1.2 s within a range of 0.6 to 1.35 s, S43), K 0.20 s per key (a chord counts two; S43 gives 0.20 s for an average skilled typist at 55 wpm and 0.28 s as its design point for the typical user), B 0.10 s per press or release (a click is two B), H 0.40 s (S23, S43, LAW§2.4). Pointing: MT = 0.37 + 0.13 x ID seconds, ID = log2(D/W + 1) bits, mouse, from Cockburn, Gutwin and Greenberg 2007 (R2 = 0.93, 8 participants, menu-item pointing; S24a); W is the smaller side of the target (an assumption from LAW§2.1). **Extrapolation:** these constants were fitted on vertical menu-item pointing and are applied here to free two-dimensional pointing over 45 to 430 px and to drags; the KLM band below does not include any uncertainty for that step. Cockburn's 0.37 s intercept was fitted on selection after a menu-button click, so charging separate B operators beside it may double-count a small click component; the flat-P stress row (P = 1.1 s, no Cockburn constants) bounds that effect. R is system response. Pointer starts at the viewport centre (720, 450). Band: plus or minus 21% (KLM RMS error, S23).

**Geometry, two profiles.**

| Profile | Current | Proposed | Use |
|---|---|---|---|
| D (headline) | MEASURED with Playwright and Chromium 151, real Studio, offline fixture, 1440 by 900, Impact tab, **immediately after selecting the recommendation meaning, so the notice box "Meaning selected. The local baseline has not changed." is visible** (M1; the tabs sit at y = 623 here and y = 552 in the layout-file page, a 71 px difference that I attribute to the `#notice` element, which `app.css` styles only when non-empty; inferred from `app.js` and `app.css`, not isolated by a run). The state cards then end at y = 913 and the edit control starts at y = 938 of 900. | Appendix B.2, the design's own intent | numbers in sections 0, 11.1 and 14 |
| L (cross-check) | `design/layouts/current-impact.json`, notice box empty (case reopened from the list), every y value 71 px smaller: the edit control straddles the fold (y = 867, 33 px visible) and no scroll is charged, which favours the baseline | `design/layouts/proposed-canvas.json` (layout lane, nodes 112 by 48, handle 24 by 24 at 46 px from the pointer start) | 11.2 last table; the P ops of `canvas-flows.json` that carry a `layout` key use these ids |

Native `<select>` popup rows are not measurable and use ESTIMATED 22 px rows. Elements that exist in neither layout file (snap zone, Apply button, inspector segmented option, edge hit stroke) are ESTIMATED and marked in the flow notes.

**Kernel round trip.** MEASURED (M3, n = 20 each, this PC, C: drive, loopback): edit POST p50 19.5 ms, p95 21.9 ms; layout POST p50 18.2 ms, p95 44.3 ms, max 58.8 ms; case GET p50 23.8 ms, p95 26.6 ms. With n = 20 the p95 is effectively the second-largest sample, so every p95 here is **indicative only**; HCI-ADR-0066 asks for at least 30 trials and a rerun is deferred. The baseline `command()` issues the POST plus two GETs, so R = 70 ms is used for every commit (19.5 + 23.8 + 23.8 = 67 ms rounded up). The lower figure of 43 ms in D12 is one POST plus one GET (19.5 + 23.8), the cost if a commit needed only one reload; the cases-list GET was not timed and is assumed equal to the case GET. Adding the three p95 values gives 44.3 + 26.6 + 26.6 = 98 ms for layout plus reload; a sum of p95s is not the p95 of the sum, so this is an **upper-bound heuristic**, not a percentile. It sits on the 0.1 s boundary, so a PENDING state is kept in the design (D12). The five sequential Tidy commits are charged 5 x 70 = 350 ms by the same rule as every other commit. The motion aspect's proposed HCI-ADR-0066 gives commit actions a warn target of 300 ms and a fail limit of 1000 ms, which this stays under. The AGENTS.md note says D: is a slow HDD; this workspace was on C:.

### 11.1 Results (profile D, base constants)

| Task | Current (s) | Proposed (s) | Bands (plus or minus 21%) | Separable in the base case | Robust (11.2) | Flat P = 1.1 s |
|---|---|---|---|---|---|---|
| T04 reconnect Reject source by drag (stage 2) | 5.62 | 3.04 | 4.44 to 6.80 vs 2.40 to 3.68 | yes | **no** | 6.87 vs 3.82 |
| T04-click click-then-click on the handle (stage 2) | 5.62 | 3.24 | 4.44 to 6.80 vs 2.56 to 3.92 | yes | **no** | 6.87 vs 4.02 |
| T04-lite select edge, click a state (stage 1) | 5.62 | 3.20 | 4.44 to 6.80 vs 2.53 to 3.87 | yes | **no** | 6.87 vs 4.02 |
| T04-inspector segmented control (stage 1) | 5.62 | 3.39 | 4.44 to 6.80 vs 2.68 to 4.10 | yes | **no** | 6.87 vs 4.02 |
| T04-inspector-form select plus Apply, as the layout lane draws it | 5.62 | 5.13 | 4.44 to 6.80 vs 4.05 to 6.21 | **no** | no | 6.87 vs 6.62 |
| T04-kbd keyboard only | 2.62 | 2.22 | 2.07 to 3.17 vs 1.75 to 2.69 | **no** | no | 2.62 vs 2.22 |
| T04-move move a node | 8.68 | 3.18 | 6.86 to 10.51 vs 2.51 to 3.85 | yes | **yes** | 9.67 vs 3.82 |
| T04-move-kbd move a node, keyboard only | 6.77 | 3.82 | 5.35 to 8.19 vs 3.02 to 4.62 | yes | **no** | 6.77 vs 3.82 |
| T04-move-x5 place five nodes by hand, one M per node (same outcome as the form) | 24.50 | 15.90 | 19.36 to 29.65 vs 12.56 to 19.24 | yes (by 0.12 s) | **no** | 24.50 vs 19.10 (overlap) |
| T04-move-x5, one M for the whole plan (sensitivity, not in the JSON) | 24.50 | 10.50 | 19.36 to 29.65 vs 8.30 to 12.71 | yes | **yes** | 24.50 vs 13.70 |
| T04-tidy tidy five nodes, five POSTs (different outcome, see below) | 24.50 | 4.94 | 19.36 to 29.65 vs 3.90 to 5.98 | yes | yes, but prices a different outcome | 24.50 vs 5.65 |
| T04-tidy-batch one atomic batch (I-K3 built; different outcome) | 24.50 | 4.66 | 19.36 to 29.65 vs 3.68 to 5.64 | yes | yes, but prices a different outcome | 24.50 vs 5.37 |
| T04-undo undo the last edit | 5.62 | 2.22 | 4.44 to 6.80 vs 1.75 to 2.69 | yes, but the baseline has no undo (row prices a repeat edit) | yes except under both stresses | 6.87 vs 2.22 |
| T04-refuse cost of one refused drag (stage 2) | none | 4.29 | 3.39 to 5.19 | not comparable | n/a | 5.10 |
| T04-refuse-lite cost of one refused click (stage 1, release 1) | none | 4.48 | 3.54 to 5.42 | not comparable | n/a | 5.30 |

All values PREDICTION. The T04-tidy proposed flow charges one M for reading the ghost preview before Apply (revision 1 omitted it and gave 3.49 s) and R = 350 ms for five sequential commits (5 x 70 ms, the rule used for every other commit; revision 2 charged 250 ms and gave 4.84 s); with one atomic batch it is 4.66 s. Full operator lists with D, W and ID per pointing operation are in `design/tasks/canvas-flows.json`.

**Tidy prices a different outcome.** The current T04-tidy flow charges five rounds of deciding and typing coordinates the user chose. Tidy applies an algorithmic arrangement the user only accepts. It replaces manual arrangement only when that arrangement is acceptable, and layout quality is UNKNOWN (section 16). The same-outcome comparator is T04-move-x5: five drags, 15.90 s with one M per node (as the baseline is charged) or 10.50 s if the user plans once while seeing the picture. Like T04-undo, the Tidy row prices a workaround, not a like-for-like task.

### 11.2 Arithmetic and stress tests

Arithmetic for T04 (headline geometry):

| Op | Current flow | s | Proposed flow | s |
|---|---|---|---|---|
| M | locate the control below the fold (MEASURED y = 938 of 900) | 1.35 | know where the tail handle is | 1.35 |
| K | one wheel notch (100 px ESTIMATED) | 0.20 | | |
| P | to `diagram-source`: D = 425, W = 44, ID = 3.41 | 0.814 | to handle: D = 175, W = 24, ID = 3.05 | 0.766 |
| B B | click | 0.20 | B press | 0.10 |
| M | choose the value | 1.35 | | |
| P | to option: D = 44, W = 22 (ESTIMATED), ID = 1.58 | 0.576 | drag to Submitted: D = 203, W = 56, ID = 2.21 | 0.657 |
| B B | click | 0.20 | B release | 0.10 |
| P | to Apply: D = 183, W = 49, ID = 2.24 | 0.662 | | |
| B B | click | 0.20 | | |
| R | reload | 0.07 | reload | 0.07 |
| Total | | **5.62** | | **3.04** |

Check of the sum: current 1.35 + 0.20 + 0.814 + 0.20 + 1.35 + 0.576 + 0.20 + 0.662 + 0.20 + 0.07 = 5.622 s. Proposed 1.35 + 0.766 + 0.10 + 0.657 + 0.10 + 0.07 = 3.043 s.

HCI-ADR-0066 (proposed, motion aspect) defines its own T04 as the numeric-field layout edit: current 10.17 s with a flat 1.1 s pointing operator, proposed 3.85 s (drag, flat P, R = 100 ms). Its "6.3 s" is the **difference** 10.17 - 3.85 = 6.32 s, not a baseline; that task corresponds to this record's T04-move (9.67 s flat-P current, 3.82 s flat-P proposed), so the two records agree within rounding of R. The layout lane's own T04 flow (`layout-model.md` section 11) adds navigation to the canvas and uses R = 300 ms. Three lanes therefore use the label T04 for three different flows; the integrator should rename them.

**Stress tests (profile D).** Each row applies one variation to the base case. A cell is "sep" if the plus or minus 21% bands do not overlap. A task is **robust** only if it is separable in every cell. The two M stresses charge the current flow one M fewer (the expert already knows the value) and the proposed flow one M more (reading a preview or a refusal), because the M count is analyst judgement.

| Task | base | flat P | Kieras (M 1.2, K 0.28) | drag slope x 2 | current one M fewer | proposed one M more | Robust |
|---|---|---|---|---|---|---|---|
| T04 | 5.62 / 3.04 sep | 6.87 / 3.82 sep | 5.40 / 2.89 sep | 5.62 / 3.33 sep | 4.27 / 3.04 **overlap** | 5.62 / 4.39 **overlap** | no |
| T04-click | 5.62 / 3.24 sep | 6.87 / 4.02 sep | 5.40 / 3.09 sep | n/a | 4.27 / 3.24 **overlap** | 5.62 / 4.59 **overlap** | no |
| T04-lite | 5.62 / 3.20 sep | 6.87 / 4.02 sep | 5.40 / 3.05 sep | n/a | 4.27 / 3.20 **overlap** | 5.62 / 4.55 **overlap** | no |
| T04-inspector | 5.62 / 3.39 sep | 6.87 / 4.02 sep | 5.40 / 3.24 sep | n/a | 4.27 / 3.39 **overlap** | 5.62 / 4.74 **overlap** | no |
| T04-inspector-form | 5.62 / 5.13 **overlap** | 6.87 / 6.62 **overlap** | 5.40 / 4.98 **overlap** | n/a | 4.27 / 5.13 **overlap** | 5.62 / 6.48 **overlap** | no (no separation anywhere) |
| T04-kbd | 2.62 / 2.22 **overlap** | n/a (no P) | 2.95 / 2.39 **overlap** | n/a | 1.27 / 2.22 sep, **current faster** | 2.62 / 3.57 **overlap** | no; possibly slower than the baseline |
| T04-move | 8.68 / 3.18 sep | 9.67 / 3.82 sep | 9.42 / 3.03 sep | 8.68 / 3.70 sep | 7.33 / 3.18 sep | 8.68 / 4.53 sep | **yes** |
| T04-move-x5 (one M per node) | 24.50 / 15.90 sep | 24.50 / 19.10 **overlap** | 30.71 / 15.15 sep | 24.50 / 18.48 **overlap** | 23.15 / 15.90 **overlap** | 24.50 / 17.25 **overlap** | no |
| T04-move-x5 (one M in total) | 24.50 / 10.50 sep | 24.50 / 13.70 sep | 30.71 / 10.35 sep | 24.50 / 13.08 sep | 23.15 / 10.50 sep | 24.50 / 11.85 sep | yes |
| T04-move-kbd | 6.77 / 3.82 sep | 6.77 / 3.82 sep | 8.07 / 4.63 sep | n/a | 5.42 / 3.82 **overlap** | 6.77 / 5.17 **overlap** | no |
| T04-tidy | 24.50 / 4.94 sep | 24.50 / 5.65 sep | 30.71 / 4.64 sep | n/a | 23.15 / 4.94 sep | 24.50 / 6.29 sep | yes, but a different outcome |
| T04-undo | 5.62 / 2.22 sep | 6.87 / 2.22 sep | 5.40 / 2.23 sep | n/a | 4.27 / 2.22 sep | 5.62 / 3.57 sep | yes (fails only with both stresses together: 4.27 vs 3.57); prices a workaround |

Revision 1 applied this test to T04, T04-move and T04-tidy only and labelled T04-click and T04-move-kbd as separable without qualification; both overlap under the one-M-fewer row, like T04. Revision 2 omitted T04-kbd and T04-inspector-form from this table and misreported T04-kbd under the one-M-fewer stress as an overlap: the bands separate with the **current** flow faster (1.27 s, band 1.00 to 1.54, against 2.22 s, band 1.75 to 2.69). The T04-kbd flows are also asymmetric (the current flow assumes ArrowDown on a closed select; the proposed flow assumes the edge is already selected; two arrow keys to reach it make the proposed flow 2.62 s). **The keyboard MEANING path has no predicted advantage and possibly a disadvantage.** It exists for WCAG 2.1.1, not for speed.

**Speed claims that survive:** T04-move (one node) and T04-move-x5 if the user plans the arrangement once. T04-tidy and T04-undo separate in every row but price a different outcome or a workaround. T04-inspector-form, the layout lane's select plus Apply, is not distinguishable from the baseline in any row, so the segmented control of section 9.1 is the option with a predicted advantage over the form (about 1.7 s, PREDICTION, not robust).

**Geometry cross-check (profile L, base constants).** Current = `current-impact.json`, proposed = `proposed-canvas.json`; the current flow charges no scroll for T04 and one wheel notch fewer for T04-move; the keyboard move needs 240 units (9 keys).

| Task | Current (s) | Proposed (s) | Bands | Same verdict as profile D? |
|---|---|---|---|---|
| T04 | 5.43 | 2.88 | 4.29 to 6.57 vs 2.27 to 3.48 | yes (overlap with one M fewer: 4.08 vs 2.88) |
| T04-click | 5.43 | 3.08 | 4.29 to 6.57 vs 2.43 to 3.72 | yes |
| T04-lite | 5.43 | 3.26 | 4.29 to 6.57 vs 2.57 to 3.94 | yes |
| T04-inspector | 5.43 | 3.40 | 4.29 to 6.57 vs 2.68 to 4.11 | yes |
| T04-inspector-form | 5.43 | 5.14 | 4.29 to 6.57 vs 4.06 to 6.22 | yes (no separation) |
| T04-move | 8.50 | 3.26 | 6.71 to 10.28 vs 2.58 to 3.94 | yes, robust |
| T04-move-kbd | 6.77 | 4.22 | 5.35 to 8.19 vs 3.33 to 5.11 | yes (overlap with one M fewer) |
| T04-move-x5 (one M per node) | 24.50 | 16.30 | 19.36 to 29.65 vs 12.88 to 19.72 | overlap here as well; not robust in either profile |
| T04-tidy | 24.50 | 5.04 | 19.36 to 29.65 vs 3.98 to 6.10 | yes (different outcome) |
| T04-undo | 5.43 | 2.22 | 4.29 to 6.57 vs 1.75 to 2.69 | yes; marginal overlap with one M more (4.29 vs 4.32) |
| T04-refuse | none | 4.15 | 3.28 to 5.02 | not comparable |
| T04-refuse-lite | none | 4.47 | 3.53 to 5.41 | not comparable |

Totals differ from the headline by at most 0.4 s (T04-move-kbd, from the longer keyboard travel) and no verdict changes. The proposed T04 is favoured in profile L by geometry: the handle lies 46 px from the assumed pointer start, which is why the flat-P row is the fairer comparison.

### 11.3 Target sizes and drop zones (Fitts, D and W from Appendix B.2)

| Choice | W | ID (bits) | MT (s) | Difference |
|---|---|---|---|---|
| Handle hit area 24 px versus 12 px at D = 175 | 24 / 12 | 3.05 / 3.96 | 0.767 / 0.885 | +0.118 s for the smaller handle |
| Drop anywhere on the node (W = 56) versus on a small port (W = 24) at D = 203 | 56 / 24 | 2.21 / 3.24 | 0.657 / 0.791 | +0.134 s for the port |
| Snap capture zone 12 px versus 24 px at D = 176 | 12 / 24 | 3.97 / 3.06 | 0.886 / 0.768 | +0.118 s for the smaller zone |

The 24 px hit area also meets WCAG 2.5.8 for the handle (S2). Differences of about 0.1 s are far inside the KLM band and are not decisions on their own; they support the sizes because the standard already requires them.

### 11.4 Validity limits

KLM and Fitts describe expert, error-free, routine pointing; they do not model reading a refusal, learning where a handle is, mode errors, or drag error rates. MacKenzie, Sellen and Buxton 1991 found shorter movement times and lower error rates for pointing than for dragging with a mouse, trackball and stylus, and a lower index of performance for dragging (S19); no constants were read, so drag times here use pointing constants and are lower bounds (the sensitivity row doubles the slope as a stress test, not as a source). Cockburn's constants come from menu-item pointing with 8 participants and one mouse setup and are applied to 2D pointing and drags (an extrapolation whose uncertainty is not in the band). K = 0.20 s is one of four typist-skill values in Kieras 2001 (S43); with its design point (M 1.2, K 0.28) no verdict changes (section 11.2). Kernel round-trip times are one machine and n = 20. The 0.1 s, 1 s and 10 s classes are conventions (S15), not thresholds of this UI. **None of this shows that users will find the canvas pleasant or make better decisions.**

## 12. OSS decision matrix (D11)

Hard constraints from the repository: **C1** no build-time framework, browser code runs from plain files (ADR-013); **C2** strict CSP (section 10); **C3** licence compatible with an Apache-2.0 project (ADR-0015); **C4** accessibility: nodes and edges can be focused, named and operated by keyboard; **C5** size: the shipped Studio is 17.7 KB of JavaScript and CSS today (MEASURED), so any large dependency needs a reason; **C6** no second model: the library must not become a parallel source of workflow truth (AGENTS.md: do not create parallel rule/state/journey sources). C6 is my inference from that rule.

Sizes are MEASURED unless stated: files fetched from jsDelivr on 2026-09-29 and compressed locally with `gzip -9` (M2b). Unpacked package sizes come from the npm registry (S37). "Pass", "fail" and "unknown" apply to the constraint; nothing is scored or weighted.

| Candidate | Role | C1 no bundler | C2 CSP | C3 licence | C4 a11y | C5 size | C6 second model | Verdict |
|---|---|---|---|---|---|---|---|---|
| maxGraph 0.24.0 (S31, S37) | renderer and editor | **fail**: README says direct use in a page is not supported; needs a bundler | unknown (not tested) | pass, Apache-2.0 | unknown (undocumented on the pages read) | 7.1 MB unpacked; bundle size of a tree-shaken build not measured | fail: owns a graph model | eliminated by C1 |
| Cytoscape.js 3.34.3 (S34, S37) | graph model, canvas renderer, drag built in | pass: `cytoscape.min.js` | unknown | pass, MIT | **unknown to fail**: docs are silent; renderer described as canvas in DGM§2.12, so nodes would not be DOM elements (inference) | 435,503 B raw, 136,441 B gzip; `cytoscape-edgehandles` 28,538 B raw, 7,069 B gzip | fail: owns a graph | not adopted; keep for large read-only graphs if ever needed |
| tldraw SDK 5.4.2 (S33, S37) | infinite canvas SDK | **fail**: React peer dependency | unknown | **fail**: source-available, development-only by default, production key or watermark; not OSI | pass on documentation: best documented keyboard and announcement design (S9) | 14.9 MB unpacked (`tldraw`) | fail: owns a store | eliminated by C1 and C3; its accessibility design is adopted as a pattern |
| Excalidraw 0.18.1 (S36, S37) | whiteboard component | **fail**: React peer dependency | unknown; fonts load from a CDN unless self-hosted (DGM§2.4) | pass, MIT | unknown (GitHub page silent) | 46.8 MB unpacked | fail: scene model | eliminated by C1 |
| JointJS core 4.3.3 (S32, S37) | SVG diagram library | unknown: repository does not state script-tag use on the page read; older 3.7.7 depends on jQuery, lodash, Backbone | unknown | pass, MPL-2.0 (file-level copyleft) | unknown (no a11y documentation on the page read) | 6.2 MB unpacked | fail: owns a graph | eliminated: inspector, stencil, toolbar and advanced layouts are in the paid JointJS+ |
| elkjs 0.12.0 (S28, S37) | layout engine only | pass: `elk.bundled.js` or `elk-api.js` plus a worker | worker path works with `script-src 'self'` given an allowlist entry (S39, M2) | pass with review: **EPL-2.0 OR GPL-3.0-or-later** (registry); the ASF treats EPL-2.0 as category B for binary inclusion in ASF products (S30), which is not legal advice for EIJA | not applicable (no rendering) | **1,609,707 B raw, 466,995 B gzip** (`elk.bundled.js`); worker 1,595,334 B raw | pass (positions only) | deferred (D6) |
| dagre (`@dagrejs/dagre` 3.1.1) (S35, S37) | layered layout only | pass: `dist/dagre.min.js` | pass (plain script, no workers) | pass, MIT | not applicable | **48,956 B raw, 17,091 B gzip** | pass (positions only) | fallback layout engine if the built-in pass is not enough |
| Custom SVG plus built-in layered placement | renderer, interaction, layout | pass | pass (MEASURED, section 10) | pass | pass if built as specified; AT behaviour UNVERIFIED | ESTIMATED 25 to 45 KB unminified | pass: the kernel model is the only model | **chosen** |

GLSP and Sirius Web are not candidates (Java or React stacks, DGM§2.9); their **protocol shape** is adopted (S10). The cost of the choice is maintenance of hit-testing, routing, snapping and accessibility code by this project; that cost is not estimated.

## 13. Anti-slop and density for the canvas region (PREDICTION from the design; the slop-budget script was not run)

| Item | Target | Value at rest for the excursion model | Note |
|---|---|---|---|
| Visible words in the canvas region | about 120 for the whole viewport | 14 at rest, recounted from Appendix B.2: 5 state names, 5 action names, 4 toolbar labels (Tidy, Undo, Redo, Connect disabled); 17 while a Tidy preview shows Apply and a node is near the limit ("limit 2000") | whole viewport depends on other aspects; baseline MEASURED 169 in the first 900 px |
| Prose blocks of 8 or more words (budget: about 30 words in total per viewport) | about 30 | **0 at rest. Transient, counted by hand: longest refusal 12 words, consequence line 11, mode line 8, decision confirmation 8, layout-history notice 9, MEANING undo coverage 15 (three labelled lines shown together count as one block), LAYOUT undo coverage 11.** Largest simultaneous set: refusal (12) plus mode line (8) = 20; worst case if the MEANING undo coverage (15) is still visible when an armed edge shows its consequence line (11) = 26 | within budget only after the earlier 36-word coverage string was cut to 15 words (section 8); splitting it into lines does not by itself satisfy the budget, which is a total and the refusal catalogue was cut to 12 words at most (section 6). The audit rejected the earlier "transient, so not counted" argument: the rubric does not exempt transient text, so transient strings are counted here. Live-region text is not visible and is not counted |
| Bordered or filled containers in the canvas region | about 12 for the viewport | **10 at rest**: the pane, 5 nodes and 4 bordered toolbar buttons (Tidy, Undo, Redo, Connect disabled; Appendix B.2); 11 while the Tidy Apply button shows; 13 with the two inspector options of the segmented control (outside the pane, same viewport) | the canvas region alone uses most of the budget of about 12 before any other aspect adds anything, and grows by one per state. Deviation request I-D1: count diagram nodes as content marks. Alternative: draw toolbar buttons as unbordered text buttons (enforced by a class rule and by the slop-budget script counting any border or background fill), which gives 6 at rest; that trades a weaker button affordance and is not chosen here. Without a deviation this is a fail at 5 states with the inspector open, and at scale |
| Nesting depth | at most 3 | 2 (pane, node) | |
| Font sizes in the region | at most 6 | 3: node label, edge label, transient tag and status | |
| Elevations | at most 2 | 0 in the canvas; ghost has no shadow | |
| Gradient, blur, glassmorphism | 0 | 0 | ghost is a dashed stroke |
| Emoji or icon-per-bullet | 0 | 0 | glyphs are SVG paths with visible words next to them |
| Colour as sole carrier | 0 | 0 by design: every class has a word and a stroke pattern | to be verified with CVD simulation once tokens exist |

## 14. Cognitive Dimensions of Notations

Definitions from the Green and Blackwell tutorial (S17). Ratings are **analyst judgement** from the baseline files and this design, not measurements. Concern: L low, M medium, H high. The last column says what would confirm or refute the rating.

| Dimension | Baseline (select, number fields, state cards) | Proposed canvas | Design response and how to check |
|---|---|---|---|
| Viscosity: repetition | H: five nodes need five passes through the form (PREDICTION 24.5 s) | L to M: five drags (PREDICTION 15.9 s with one decision per node, 10.5 s planned once; only the latter robust) or one Tidy (4.9 s with five POSTs, 4.7 s with one batch; a different outcome, useful only when the algorithmic layout is acceptable; section 11.1) | Tidy and multi-select; T04-tidy in the study |
| Viscosity: knock-on | M: an edit clears the decision and stales evidence; the consequence is a count | M: unchanged in the kernel, but visible before commit in the ghost chips | dry run lists changed elements; count of silent knock-ons must be zero |
| Visibility | H: edit controls sit below the fold at 1440 by 900 (MEASURED y = 938, 1102); relationships exist only as text lines in cards | L for 5 states; M above about 30 nodes | one view of the whole model; finder for large models; measure first-click time to a named edge |
| Premature commitment | M: selecting a meaning cannot be replaced without discarding the case | M to L: the ghost of a candidate meaning can be shown before selection (I-R1) | preview before select; not built by the canvas alone |
| Hidden dependencies | M: impact is a count plus JSON | L for drawn edges; M for the kernel's mapped closure, whose envelope says it is not every real-world consequence | show mapped consequences with UNKNOWN kept separate (ripple aspect) |
| Role-expressiveness | M: all states look alike | L: initial, terminal and current states drawn distinctly; edge label shows action; role in the inspector | check that users name initial and terminal states in the first-click test |
| Error-proneness | L: the select offers only legal values | **M: rises**: in stage 2 free dragging invites illegal drops; in stage 1 (select the edge, click a state) only clicks on refused states can err, and the armed edge shows legal targets first, so the rise is smaller (analyst judgement) | refusal at the target with code and reason, tier-1 outlines, undo; count refused attempts per task and per stage |
| Secondary notation | H: positions are numbers with no picture | L: positions stored by id apart from meaning; M because edge routing and annotations are not stored | layout file has only ids and coordinates; no free text notes in v1 |
| Abstraction | L (none) | M: no grouping or composite states offered | out of scope while the vocabulary is frozen |
| Closeness of mapping | M: "State-view edit: Reject starts at" is a form for a picture concept | stage 2: L (drag the start of the arrow); stage 1: M to L (select the arrow, then click the state it should start at) | first-click and think-aloud; compare the two stages in the study arm |
| Consistency | M: two editors, one typed command (a strength) | L: canvas, inspector, keyboard and palette emit the same request | regression test: same request from each path |
| Diffuseness | H: long explanatory text | L | word count per viewport |
| Hard mental operations | H: compute coordinates without seeing positions | M: two modes on the keyboard, three gesture classes | mode line; measure mode errors and class misidentification |
| Progressive evaluation | M: apply, then re-verify | L: consequence chips before commit; verification stays a separate job | dry run before drop |
| Provisionality | M | M: ghost and dashed `PROPOSED` styling exist, but the kernel accepts only complete valid states, so nothing can be sketched | do not imply free sketching |

## 15. Validation plan (protocol only; nothing has been run)

**Prototype measurements** (one Chromium at a time, 1440 by 900 and 1280 by 720). Pass criteria fixed before running:

| Check | Pass |
|---|---|
| Pointer-move to ghost paint, p95, scripted 5 s drag; no fetch inside the frame loop (consistent with HCI-ADR-0066 item 7) | at most 100 ms; zero requests during the drag except one event-driven dry run per target entry in the large-model fallback |
| Commit round trip (POST plus reload), p95, **at least 30 trials** (the n = 20 measurement in M3 is indicative only) | within the commit class of HCI-ADR-0066 (warn 300 ms, fail 1000 ms; proposed there); also report whether it stays under 100 ms, on C: and separately on D: |
| CSP smoke on the real canvas | zero violations during all gestures |
| Every interactive element | at least 24 by 24 CSS px, or spacing exception documented |
| Every G3a, G3 and G2 outcome | reachable with keyboard only and with click-then-click only (automated) |
| Affordance map | every refused target has a code from section 6; none is `CONTRACT_REJECTED` |
| DOM equals render(model, layout) | regeneration test passes for 5 fixtures |
| Words, containers, font sizes in the canvas region | within section 13 values or a recorded deviation |
| Contrast and CVD for ghost, guides, handles | computed once tokens exist; UNKNOWN before |

**User study.** Within-subject, current Studio versus the proposed canvas, excursion workflow, tasks T04 (arms: form, inspector control, select-edge-then-click, drag handle, keyboard), T04-move, T04-move-x5 (target positions given on a printed sketch so the outcome is fixed), T04-tidy (with an acceptability rating of the Tidy result: would the participant keep it, 1 to 7), T04-undo, T04-refuse-lite and, in the drag arm only, T04-refuse. Counterbalanced order; at least 12 participants for a comparative claim, formative rounds of about 5 to find problems (LAW§2.10); a keyboard-only cohort and a screen-reader cohort. Measures: time on task; error count; refused attempts per task and recovery time; **class misidentification** (after each gesture, "did this change meaning or only layout?"); UNKNOWN or STALE evidence misread as current (target zero); confirmation skipped on a decision-clearing drop; SEQ per task; SUS and Raw TLX with intervals. Hypotheses pre-registered before the run: H-C1 stage-1 click paths (T04-lite, T04-inspector) and the drag (T04) differ by less than the KLM band on the reconnect task; H-C2 node drag reduces time on T04-move and T04-move-x5 by more than the band, and Tidy reduces time on T04-tidy by more than the band **for participants who keep the Tidy result** (Tidy time is reported separately from acceptability, never pooled); H-C3 class misidentification is at most 1 of 12 participants in each arm; **H-C4 (promotion of the MEANING drag, decision D13): the drag arm reduces time on the reconnect task against the click arm by more than the KLM band, with class misidentification at most 1 of 12 and every refusal recovered within 30 s; if not, the MEANING drag is not built.** The arms of the reconnect task are: form (baseline), inspector control, select-edge-then-click (stage 1), drag handle (stage 2). **Stop and redesign** if 2 or more of 12 participants misclassify LAYOUT and MEANING on seeded gestures, if any participant approves with an unread UNKNOWN on a seeded item, or if the refusal path leaves any participant unable to recover within 30 s. No result exists.

## 16. Open questions and UNVERIFIED items

| Item | Status |
|---|---|
| Screen-reader behaviour of `role="button"` with `aria-roledescription` on SVG groups; graphics roles; the canvas container as `group`, `toolbar` or `application` | UNVERIFIED; test the three container variants with at least two reader and browser pairs |
| Firefox and Safari behaviour for the CSP results in section 10 | UNVERIFIED; one Chromium only |
| Whether undoing a MEANING edit re-applies an older receipt | derived from `assess_receipt`, not executed; kernel test required |
| Capture radius 6 px, drag threshold 4 px, refusal display 4 s, snap grid 8 | HYPOTHESES to calibrate |
| Layout quality of the built-in pass versus dagre and elkjs | UNKNOWN, not compared; the Tidy speed figure is only relevant when the result is acceptable |
| Whether a user arranging five nodes decides once or per node (T04-move-x5: 10.50 s versus 15.90 s) | UNKNOWN; only the once-planned case is robust against the form |
| Keyboard MEANING path (T04-kbd) against a keyboard-savvy baseline user | PREDICTION says possibly slower; the keyboard cohort measures it |
| Brief T04 asks for drag with refusal at the drop target; release 1 ships neither for MEANING | owner decision (HCI-ADR-0061 Status) |
| Effect of mental-map preservation on users | UNVERIFIED as a cited effect (section 7) |
| Whether users want drag editing of a model with two executable edits | unknown; the study is the test, and the value may be small until the vocabulary grows |
| Legal review of elkjs (EPL-2.0 OR GPL-3.0-or-later) in an Apache-2.0 project | not done; only needed if elkjs is adopted |
| Millisecond behaviour on the D: HDD | not measured |
| Latency with n of at least 30 (M3 used 20) | deferred: needs the Studio server and one browser run |
| Whether the MEANING drag (stage 2) beats the click paths | unknown; study arm and H-C4 |
| Cross-lane conflicts with `design/layouts/proposed-canvas.json` (B.3) | for the integrator |

## 17. Sources (all opened 2026-09-29)

| Id | URL | Used for | Type | Confidence |
|---|---|---|---|---|
| S1 | https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html | 2.5.7 needs a single-pointer non-dragging path; keyboard alone does not satisfy it | standard | high |
| S2 | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | 2.5.8: 24 by 24 CSS px, spacing exception | standard | high |
| S3 | https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/ | composite widget, single tab stop, roving tabindex | official guidance | high |
| S4 | https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html | 4.1.3, `role="status"` | standard | high |
| S5 | https://www.w3.org/TR/graphics-aria-1.0/ | Graphics Module Recommendation 2018-10-02 | standard | high |
| S6 | https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-grabbed | `aria-grabbed` deprecated | documentation | high |
| S7 | https://www.drawio.com/docs/manual/connectors/ | hover-arrow connector creation, valid-target outline | official docs | medium (page silent on endpoint dragging) |
| S8 | https://www.drawio.com/docs/reference/shortcuts/modifier-shortcuts-in-diagrams/ | Alt suspends grid snapping | official docs | high |
| S9 | https://tldraw.dev/sdk-features/accessibility | Tab reading order, Ctrl/Cmd+arrows, live-region announcement | official docs | high |
| S10 | https://www.eclipse.dev/glsp/documentation/protocol/ and https://eclipse.dev/glsp/documentation/protocol/ | edge check, ReconnectEdge, ChangeBounds graphical only, server command stack, static hints plus dynamic check | official docs | medium (page summarised by a fetch tool) |
| S11 | https://www.eclipse.dev/glsp/documentation/validation/ | validation is server-side | official docs | medium |
| S12 | https://help.figma.com/hc/en-us/articles/360039956914-Adjust-alignment-rotation-and-position | Control suspends snapping; guide shown; no documented threshold | official docs | high |
| S13 | https://help.figma.com/hc/en-us/articles/1500004362321-Guide-to-FigJam | Tidy up, drag connector end to reconnect | official docs | high |
| S14 | https://www.drawio.com/blog/mermaid-diagrams | regeneration resets positions and connector paths | official blog | high |
| S15 | https://www.nngroup.com/articles/response-times-3-important-limits/ | 0.1, 1, 10 s | practitioner research | high as convention |
| S16 | https://www.cs.umd.edu/users/ben/goldenrules.html | golden rules incl. easy reversal, informative feedback | author site | high |
| S17 | https://www.cl.cam.ac.uk/~afb21/CognitiveDimensions/CDtutorial.pdf | dimension definitions | tutorial by the framework authors | high |
| S18 | https://doi.org/10.1145/1054972.1055014 (abstract read at https://api.openalex.org/works/doi:10.1145/1054972.1055014) | snap-and-go | peer-reviewed paper, abstract only | medium |
| S19 | https://doi.org/10.1145/108844.108868 (abstract via OpenAlex) | pointing vs dragging | peer-reviewed paper, abstract only | medium |
| S20 | https://doi.org/10.1145/2470654.2466255 (abstract via OpenAlex) | feedforward | peer-reviewed paper, abstract only | medium |
| S21 | https://doi.org/10.1145/15922.15912 (abstract via OpenAlex) | snap-dragging | peer-reviewed paper, abstract only | medium |
| S22 | https://doi.org/10.1145/238386.238526 (abstract via OpenAlex) | command objects, selective undo | peer-reviewed paper, abstract only | medium |
| S23 | https://en.wikipedia.org/wiki/Keystroke-level_model | KLM operators, 21% error, scope | secondary | medium |
| S43 | Kieras, "Using the Keystroke-Level Model to Estimate Execution Times", 2001, https://web.eecs.umich.edu/~kieras/docs/GOMS/KLM.pdf (WebFetch could not verify the server certificate; the PDF was downloaded with `curl -k` and its text read locally, 2026-09-29) | K by typist skill (0.12, 0.20, 0.28, 1.2 s), P 1.1 s average, B 0.1, H 0.4, M 0.6 to 1.35 s with 1.2 recommended, BB = click | first-party author document (university) | high for the numbers; the TLS check was skipped for the download |
| S24a | Cockburn, Gutwin, Greenberg, CHI 2007, https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf (text read locally from the PDF) | Tp = 0.37 + 0.13 ID, R2 = 0.93 | peer-reviewed paper | high |
| S24b | https://www.w3.org/WAI/WCAG22/Understanding/pointer-cancellation.html | 2.5.2 abort or undo | standard | high |
| S24c | https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html | 1.4.1 | standard | high |
| S24d | https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html | 1.4.11: 3:1, focus indicators | standard | high |
| S24e | https://www.w3.org/WAI/WCAG22/Understanding/no-keyboard-trap.html | 2.1.2 | standard | high |
| S25 | https://dndkit.com/guides/accessibility | keyboard sensor keys, roles, live region | library documentation | medium |
| S26 | https://atlassian.design/components/pragmatic-drag-and-drop/design-guidelines | non-drag move menus | vendor design guidance | medium |
| S27 | https://code.claude.com/docs/en/checkpointing | rewind lists what it does not restore | vendor documentation | high |
| S28 | https://github.com/kieler/elkjs | elkjs usage, algorithms | repository | medium |
| S29 | https://eclipse.dev/elk/reference/options/org-eclipse-elk-interactive.html | interactive mode | official docs | medium |
| S30 | https://www.apache.org/legal/resolved.html | ASF category B for EPL-2.0 | policy page | medium; not legal advice for this project |
| S31 | https://github.com/maxGraph/maxGraph | bundler required, Apache-2.0 | repository | high |
| S32 | https://github.com/clientIO/joint | MPL-2.0, JointJS+ paid plugins | repository | medium |
| S33 | https://tldraw.dev/community/license | licence terms | official | high |
| S34 | https://js.cytoscape.org/ | drag built in, 3.34.3 | official | medium |
| S35 | https://github.com/dagrejs/dagre | MIT, dist/dagre.min.js | repository | medium |
| S36 | https://github.com/excalidraw/excalidraw | MIT, React | repository | high |
| S37 | https://registry.npmjs.org/<package>/latest for elkjs, cytoscape, @maxgraph/core, @joint/core, jointjs, dagre, @dagrejs/dagre, tldraw, @excalidraw/excalidraw, cytoscape-edgehandles | version, licence field, unpacked size, peer dependencies | registry metadata | high for the fields |
| S39 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/worker-src | worker-src fallback | documentation | high |
| S40 | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/style-src | what style-src blocks | documentation | high |
| S41 | https://www.w3.org/WAI/WCAG22/Understanding/reflow.html | 1.4.10 exempts diagrams | standard | high |
| S42 | https://docs.structurizr.com/as-code | re-parenting is generally not easy via a UI; automatic and manual layout in a browser editor | vendor documentation | medium |
| M1 | Local measurement, `.tmp/canvas-uml/measure.py`, Chromium 151.0.7922.34 headless, Studio 0.2.0 from this worktree, offline provider, 2026-09-29 | current geometry | MEASURED | one browser, one viewport pair |
| M2 | same script, CSP smoke section | CSP results in section 10 | MEASURED | Chromium only |
| M2b | `curl` from https://cdn.jsdelivr.net/npm/<pkg>@<version>/<file> then `wc -c` and `gzip -9 -c \| wc -c`, 2026-09-29 | library file sizes | MEASURED | gzip level differs from CDN Brotli; an independent re-run gave the same raw sizes and gzip sizes about 30 B lower (gzip build difference, immaterial) |
| M3 | `.tmp/canvas-uml/latency.py`, 20 iterations each, this PC, C: drive, loopback | commit and read latency | MEASURED | one machine |
| R1 | repository files read: `domain/policy.py`, `domain/models.py`, `domain/evidence.py`, `domain/impact.py`, `application/service.py`, `application/compiler.py`, `interfaces/http.py`, `resources/web/*`, ARCHITECTURE.md, ADR-0000, ADR-0019 | kernel facts in section 2 | primary | high |

Research dossiers used as leads, not as sources for numbers: `diagramming-and-uml-tools.md` (DGM), `hci-laws-and-quantitative-models.md` (LAW), `SYNTHESIS.md`, `PRINCIPLES.md`. Abstract-only papers (S18 to S22) are cited for what the abstract states, nothing more.

## Appendix A. Gesture state machine

```text
idle --press on node (stage 1) or handle (stage 2)--> armed --move > 4 px--> dragging
armed --release--> click (select; a selected edge arms its source end; stage 2: a handle click arms it too)
dragging --move--> dragging   (ghost, guides, tier-1 outlines and precomputed tier-2 chips; no fetch in the loop)
dragging --Escape | release outside any legal target--> cancelled   (nothing sent)
dragging --release on legal target--> confirming   (only if a decision exists)
dragging --release on legal target--> pending      (no decision exists)
confirming --Enter--> pending   |   confirming --Escape--> cancelled
pending --kernel accepts--> committed   (redraw from model; log entry; announce)
pending --kernel refuses--> refused     (revert ghost; refusal sentence; not recorded)
```

## Appendix B. Geometry

### B.1 Current Impact tab (MEASURED, M1; page coordinates, 1440 by 900, viewport height 900; measured with the notice box visible, immediately after selecting the meaning. Without it every y value is 71 px smaller: `design/layouts/current-impact.json` has the cards at y = 749 and the edit control at y = 867, see section 11)

| Element | x | y | w | h | Note |
|---|---|---|---|---|---|
| tab `02 / Impact` | 403 | 623 | 98 | 50 | |
| state cards Draft, Submitted, Recommended, Approved, Rejected | 322, 507, 737, 931, 1076 | 820 | 175, 220, 185, 135, 145 | 93 | straddle the fold (bottom 913) |
| `#diagram-source` select | 546 | 940 | 142 | 44 | below the fold |
| `Apply state-view edit` | 702 | 938 | 186 | 49 | below the fold |
| `Layout-only change` summary | 322 | 1045 | 1041 | 41 | below the fold |
| `#layout-node`, `#layout-x`, `#layout-y`, `Save layout` (disclosure open) | 373, 553, 674, 773 | 1104 | 142, 85, 85, 117 | 44 to 49 | below the fold |
| page scroll height | | | | 1849 | 1920 at 1280 by 720 |

Visible words in the first 900 px of the Impact tab (my counting script, layout disclosure closed): 169 at 1440 by 900, 141 at 1280 by 720 (MEASURED; text nodes whose bounding box intersects the viewport, hidden nodes excluded).

### B.2 Proposed canvas (assumption; `eija.layout.v1` excerpt for the layout aspect to adopt or replace)

```json
{
  "schema": "eija.layout.v1",
  "ui": "proposed",
  "screen": "canvas-state-diagram",
  "viewport": {"w": 1440, "h": 900},
  "elements": [
    {"id": "canvas-pane", "role": "canvas", "x": 320, "y": 120, "w": 752, "h": 520, "label": "State diagram", "importance": 1.0, "words": 14},
    {"id": "tool-tidy", "role": "button", "x": 332, "y": 128, "w": 72, "h": 32, "label": "Tidy", "importance": 0.4, "words": 1},
    {"id": "tool-tidy-apply", "role": "button", "x": 412, "y": 128, "w": 72, "h": 32, "label": "Apply", "importance": 0.4, "words": 1},
    {"id": "tool-undo", "role": "button", "x": 492, "y": 128, "w": 72, "h": 32, "label": "Undo", "importance": 0.4, "words": 1},
    {"id": "tool-redo", "role": "button", "x": 572, "y": 128, "w": 72, "h": 32, "label": "Redo", "importance": 0.3, "words": 1},
    {"id": "tool-connect", "role": "button", "x": 652, "y": 128, "w": 72, "h": 32, "label": "Connect (disabled)", "importance": 0.1, "words": 1},
    {"id": "node-Draft", "role": "chip", "x": 344, "y": 224, "w": 120, "h": 56, "label": "Draft", "importance": 0.6, "words": 1},
    {"id": "node-Submitted", "role": "chip", "x": 520, "y": 224, "w": 120, "h": 56, "label": "Submitted", "importance": 0.8, "words": 1},
    {"id": "node-Recommended", "role": "chip", "x": 696, "y": 224, "w": 120, "h": 56, "label": "Recommended", "importance": 0.8, "words": 1},
    {"id": "node-Approved", "role": "chip", "x": 872, "y": 224, "w": 120, "h": 56, "label": "Approved", "importance": 0.6, "words": 1},
    {"id": "node-Rejected", "role": "chip", "x": 872, "y": 344, "w": 120, "h": 56, "label": "Rejected", "importance": 0.6, "words": 1},
    {"id": "handle-Reject-source", "role": "button", "x": 768, "y": 274, "w": 24, "h": 24, "label": "Reject starts here", "importance": 0.9, "words": 0},
    {"id": "inspector-opt-Submitted", "role": "button", "x": 1104, "y": 240, "w": 140, "h": 32, "label": "Submitted", "importance": 0.7, "words": 1},
    {"id": "inspector-opt-Recommended", "role": "button", "x": 1252, "y": 240, "w": 140, "h": 32, "label": "Recommended", "importance": 0.7, "words": 1}
  ]
}
```

Importance values are my judgement. The pointer start (720, 450) and the pane, toolbar and inspector positions are assumptions from I-L1. The built-in layered placement of section 7 yields the node coordinates above for the excursion model (four layers at a pitch of 176 units, nodes 120 by 56, 56 units of gap, Rejected under Approved).

`tool-tidy-apply` is drawn only while a Tidy preview is showing, so it is not in the word count at rest (14 = 5 states, 5 actions, Tidy, Undo, Redo, Connect). The four toolbar buttons are bordered and **count as containers** (section 13: 10 at rest in the canvas region). `tool-connect` is disabled with the reason `UNSUPPORTED_WORKFLOW_SHAPE` (D5). The ids here are this design's own; the layout lane's ids are in `design/layouts/proposed-canvas.json` and the P ops of `canvas-flows.json` use those wherever they exist. `canvas-flows.json` cannot use `canvas-*.json` layouts because none exists: the layout lane's file is named `proposed-canvas.json`, and this record does not own files under `design/layouts/`.

### B.3 Conflicts with the layout lane draft (`design/layouts/proposed-canvas.json`), for the integrator

| Item in the layout lane draft | Conflict with this design | Suggested resolution |
|---|---|---|
| `handle-approve-source` ("Approve starts here", 24 by 24) | D5 and G4: only the Reject source end is editable; the kernel refuses moving the Approve source (`PROTECTED_STATE:Approve`). A drawn handle for an edit that always refuses breaks the "no handle that only refuses" rule | remove it; show the lock reason in the inspector |
| `tool-connect` enabled (Connect, 88 by 28) | D5: Connect is listed **disabled** with the kernel's reason until an executable connector kind exists | draw it disabled |
| `handle-reject-source` | present in stage 2 only (D13); stage 1 arms the source end when the edge is selected | **do not delete it**: keep it behind a stage-2 flag. `canvas-flows.json` tasks T04, T04-click and T04-refuse reference it and cannot be recomputed from layout files without it; release-1 tasks (T04-lite, T04-inspector, T04-refuse-lite) use only `edge-reject-label` and nodes |
| `insp-source` select plus `insp-source-apply` | D8 specifies a segmented control (one click commits); the form costs a predicted 5.13 s against 3.39 s and is not distinguishable from the baseline (section 11.1) | use the segmented control, or record a deviation |
| toolbar: Select, Connect, Tidy, Fit; no Undo, Redo or Apply | D6, D7 need Undo, Redo and the Tidy Apply and Cancel | add them, or bind them to the palette and keys only and record the discoverability cost |
| canvas 752 by 756, nodes 112 by 48 | this design assumed 120 by 56 nodes; both meet 2.5.8 | none; the layout lane's values are used in the cross-check |
