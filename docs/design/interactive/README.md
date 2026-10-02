# EIJA Studio — interactive design reference

This self-contained local folder connects **ten design surfaces** around an illustrative selected change. **Refinement 5, authored 3 October 2026.** Start with [index.html](index.html), then use Workspace, Source/Evidence routes, edit preview, and **Design states & interaction handoff** disclosure. It has no backend or remote dependency. All earlier frozen artifacts and their browser captures are preserved separately.

**Design only.** Every model, case, source excerpt, witness, runtime result, branch and status is prepared illustration. No request is sent, source is captured, rule is checked, model is committed, agent is started, or evidence is produced. A fixture identity is not a digest or receipt. The Agent role example concerns **Save**, never approval authority. Factory coordination, domain refactoring and source transformation remain planned.

## Open locally

Open `index.html` directly if the local browser permits its external file assets. If local-file restrictions prevent loading, serve this folder with an existing Python runtime:

```powershell
python -m http.server 8767 --bind 127.0.0.1 --directory "."
```

Then open `http://127.0.0.1:8767/` in an authorized disposable browser. Stop that server when finished. Do not use a personal browser profile for acceptance recording; follow the endpoint's browser preflight. No npm install, build step or external service is required. The CSP blocks network connections and form submissions; JavaScript and CSS come from this folder.

## Review the interaction

1. **Changes:** read Save's exact `Owner → Agent` delta. Select Verify in the task inventory to see source endpoint and complete guard entries. The comparison fills the remaining pane. **Focus 100%** centers the selected path at natural text size; pan if the available viewport cannot contain it. Overview is an explicit reduced-scale alternative. Pan/zoom remains synchronized.
2. **Source → Evidence → Return:** contextual entry captures the currently selected item. Ordinary global browsing does not begin a return trail; revisiting its origin by any navigation ends that trail. Destination selection does not overwrite the saved starting item. The separate witness fixture explicitly identifies TR-SELECT; it is not evidence for Save.
3. **Rules & edit preview:** choose Role, Source state, Target state or Guards. These prepared edit fixtures are independent of the open candidate. The larger dialog keeps exact fields/actions visible; its existing item navigator is inside **Exact fields and inventory**, whose summary retains changed/unchanged counts. Close or Escape returns to the invoker. “Show apply outcome” displays an acknowledged-but-unrefreshed illustration; it writes nothing.
4. **State handoff:** choose loading, stale, refusal, missing/unknown or recovery variants without waiting through fabricated progress. Change case to check its independent selection. “Reset design fixtures” resets local presentation only.
5. **Agent factory:** inspect the planned overlap and combined-result contract. There are no operational Start/Merge/Land controls.

Use `Ctrl K` to find a surface. Six frequent destinations are **native navigation buttons**, not an incomplete tablist; **Workspace** exposes all ten surfaces in a native dialog. The left pane contains the current task's complete inventory rather than a second global menu. At compact widths, **Task inventory** explicitly opens that pane. Factory has only planned branch fixtures, not the parked case's change count. Native details/dialogs and buttons retain standard keyboard behavior. The [handoff](HANDOFF.md) lists precise controls, focus, states and evaluation gaps.

## Reuse and provenance

The palette and font stack reuse the actual product `app.css` tokens. The artifact copies these product components **byte for byte** into `assets/`:

| Asset | Reused responsibility |
|---|---|
| `compare.js`, `compare.css` | Snapshot inventory, exact fields, paired rendering, stable geometry and synchronized view controls |
| `canvas.js` | Existing SVG presentation adapter and geometry projection |
| `review.js` | Existing model comparison, including explicit field inventory |
| `dagre.min.js` | Existing pinned Dagre 1.1.8 layout bundle; bundled graphlib 2.2.4 |

No new graph layout, diff, policy interpreter, parser, editor, solver, runtime or orchestration engine is implemented. `design.js` owns local fixtures, navigation, disclosures, selection and illustration-state transitions. Its presentation wrapper moves the existing exact-field/context nodes into one labelled disclosure and calls existing focus/setViewport APIs; it does not calculate layout or infer differences. Compact summary whitespace preserves all array entries; the full raw field table remains available. No generated image is used.

Repository-relative source paths, captured hashes, copied byte identities and sizes are in [asset-manifest.json](asset-manifest.json). The source checkout HEAD was `1ecef1ec31ab158ee9f3e53ed93fbcd53262e828`, with uncommitted US06 comparison changes: **captured hashes identify the actual assets; HEAD alone does not contain or certify them**. The Dagre vendor record is retained at [assets/dagre.VENDOR.json](assets/dagre.VENDOR.json), with [Dagre](assets/dagre.LICENSE.txt) and [graphlib](assets/dagre-graphlib.LICENSE.txt) MIT notices. The [EIJA Apache-2.0 license](assets/EIJA-LICENSE.txt) accompanies the copied product modules. Vendor-record historical statements concern original vendoring, not a new validation of this artifact.

The inputs were the repository's `docs/engineering/MISSION.md`, `docs/design/WHOLE-APP-UX.md`, `WHOLE-APP-STORIES.md`, `README.md`, `NEXT-UX-PASS.md`, current modules and actual unsubmitted-role screenshot. The parent team's current gap and density reviews supplied additional interaction constraints. Four personas remain design hypotheses; they are not interviewed segments.

## Verification boundary

At authoring on **3 October 2026**, static and lightweight navigation-check status is recorded in [static-checks.json](static-checks.json). The [navigation regression](checks/navigation-origin.test.cjs) extracts the actual handlers; run with `node --test checks/navigation-origin.test.cjs` and use `DESIGN_JS` to select the prior subject for the counterexample. This is not a browser/layout oracle. **Browser layout, interaction, axe, keyboard focus, reflow, screen-reader behavior and human comprehension were NOT_RUN for refinement 5 at authoring.** Subsequent reviews must remain separate source-bound records. Earlier observations do not accept this revision. No HCI budget is changed or claimed passed.

Parent integration should review this folder, copy it atomically to its final portable destination, then inspect it in a disposable browser after the serialized QA slot becomes free. This artifact does not replace the product or close any story's acceptance.

## Refinement 4: keyboard access and portable evidence

The expanded Run diagnostic and Evidence witness JSON are named, focusable code regions. Use native scrolling keys and Tab to leave them; no key trap or prose tab stops are added. Existing Source scrolling retains its accessible region and shares the visible inset focus indicator. This addresses a serious `scrollable-region-focusable` finding from the earlier refinement 3 Run-at-320px inspection. It has not yet been browser-verified for refinement 4. All nine captured components remain byte-identical to refinement 3.

The retained `checks/stage2-counterexample.log` and `checks/stage3-navigation.log` are **derived public copies** of earlier raw records, not rerun results. The original derivation replaced the machine-specific artifact root with `<design-reference>` (escaped and unescaped variants), removed any UTF-8 BOM, and normalized CRLF to LF. The publication copy additionally removes trailing horizontal whitespace from six blank lines in `checks/stage2-counterexample.log` and six in `checks/stage4-selection-counterexample.log`; no nonblank line or outcome changes. Assertions, counts and durations are unchanged. Raw originals remain in the earlier local frozen artifact; original/derived SHA-256 and transformations are recorded in `asset-manifest.json`. Refinement 4 navigation and raw-code checks retain their subject and log provenance in `asset-manifest.json`. Current refinement 5 checks are recorded in `static-checks.json`; neither establishes rendered scrolling or browser acceptance.

## Refinement 5: prepared edits do not select the parked case

**Explore prepared edit examples** opens independent examples; it does not choose an edit for the currently selected rule. Changing the example updates only the prepared variant and retains keyboard focus on its selector. Opening and closing the preview leaves both parked cases' selections, saved request context and source mappings unchanged. The preview still identifies its own `DESIGN-UNSUBMITTED` subject and selected transition.

The new `checks/prepared-selection.test.cjs` executes actual selection/render/preview handlers. Its same-code counterexample against frozen refinement 4 records three assertion failures, including a parked Save unexpectedly becoming Verify and the source changing from Studio.save to Studio.verify. All eleven current unit checks pass. `checks/stage4-selection-counterexample.log` and `checks/stage5-unit.log` are labelled public log derivatives using the host-root/LF transformations and, for the counterexample only, publication whitespace cleanup described above, with raw and derived hashes in the manifest. No earlier artifact or raw log was modified; browser acceptance for refinement 5 remains pending.

## Publication packaging identity

This publication copy derives from the unchanged [frozen design5 manifest](../assets/interactive-20261003/frozen-design5-manifest.json), SHA-256 `f5a875d080585a76708d3f414b7907522c68b1e9a6857bfaf344f3fe71ea65a0`. Its two public counterexample logs lose only trailing spaces on blank lines; this README and [publication asset manifest](asset-manifest.json) document that derivation. All HTML, JavaScript, CSS and nine copied component/license files remain byte-identical to the QA5 subject. The frozen artifact, raw originals, static-check record and QA5 receipts are unchanged. There is no new browser run or QA6; QA5 remains bound to its original frozen identity.
