# EIJA IDE browser evidence — 2 October 2026

Draft implementation checkpoint. This maps browser observations to the acceptance contract; it does not replace focused backend/source/MCP tests, local gates, or human validation. Exact final-tree gate results remain the integrator's responsibility before any release decision. Reproduce this lane using [the browser replay instructions](SELF-DOGFOOD-BROWSER-REPLAY.md).

## Run identity and scope

- Windows primary endpoint; Python and Chromium from the repository environment. Chromium 153.0.8010.12. Dependency pins are the existing `hci` extra; no clean-machine dependency installation was tested in this run.
- Command: `python tests/hci/self_dogfood_replay.py --record --out <new evidence directory>` with the installed Playwright cache configured locally.
- The command owns a fresh temporary workspace, random-port loopback server, and isolated browser context. It uses the connected EIJA checkout read-only and normal source identity. No live provider or personal Chrome profile is involved. Approval/apply POSTs are blocked by the replay and none were attempted.
- `final-recording-4/observations.json` passes all 20 scripted checks, including the real Changes comparison, compact 14px label threshold, and SVG scale 1 within 0.005. The four-view axe audit has zero automatic violations; incomplete contrast checks remain manual-review work. The replay exited 0 and its owned browser, server and temporary workspace closed cleanly.
- `final-recording-4/subject-manifest.json` records base Git HEAD `9898c55f031137448f4de59eb637b04239f09483`, dirty checkout=true, and all 101 captured public source/pack/replay files unchanged across the run. The content SHA-256 is `de2326e3595f4b76526e7cb807e3fc498989ded15a9c2bead1af80be4de34e95`. It includes untracked and vendored source while excluding generated entries; private paths/keys are excluded by policy. The complete SHA-256 file manifest, Python 3.12.10 and installed dependency versions are retained there. HEAD alone is not the tested subject. Final frozen-tree focused-test totals and release-gate results remain **PENDING_INTEGRATOR_RECORD**.
- The unedited browser recording is 52.56 seconds, VP8 at 1600x1100 and 25fps, 5,915,573 bytes. It intentionally includes test pacing and is not performance evidence. `changes-before-after.png`, `semantic-diff-response.json`, `source-code.png` and the readable/reflow screenshots preserve the demonstrated views and their backend oracle.

## Scripted observations

All 20 checks pass in the final recorded run: `ide-entry`, `offline-intent`, `source-navigation`, `canvas-controls`, `checked-edit`, `semantic-diff`, `refused-edit`, `undo-redo`, `reload`, `view-modes`, `workspace-panels`, `keyboard`, `evidence-truth`, `viewport`, `accessibility`, `readability`, `reflow-320`, `axe-observations`, `runtime-errors`, and `owner-boundary`. The raw observations retain the oracle evidence for each; passing these checks does not close the broader acceptance rows below.

## Acceptance evidence map

Statuses below apply to the evidence from this lane alone. `PARTIAL` means an observed subset passed, with the missing acceptance observation named explicitly. `NOT_RUN` means this browser replay did not execute the criterion's decisive oracle.

| ID | Browser-lane status | Actual observation and remaining requirement |
|---|---|---|
| SD01 | PARTIAL | A new disposable workspace and server reach the connected IDE through the documented integrated command. The scoped source/dependency manifest is retained. A fresh machine/install and setup timing remain unmeasured here. |
| SD02 | PARTIAL | Source navigation opens a captured read-only symbol with scope and identity. All 101 public source/pack/replay byte identities match before/after. Adapter inventory reconciliation and adversarial root/exclusion tests require the integrator's repository-adapter evidence; this manifest has its own explicit scope/exclusions. |
| SD03 | NOT_RUN | Browser replay does not compare repeated canonical extraction or independently annotate symbols/plant false references. Include current deterministic extractor tests separately. |
| SD04 | PARTIAL | ChangeCase resolves to actual source lines with method/range/digest metadata; Repository shows `Conformance: NOT_RUN`. Missing/dynamic/unresolved cases and all displayed links are not exhaustively exercised. |
| SD05 | PARTIAL | Selecting the optional saved meaning renders SAVED, and history/current role labels agree with the selected models. No deliberately false endpoint was injected into the renderer oracle. |
| SD06 | PARTIAL | Safe Save-role change increments revision and changes semantic identity; unsafe Approve-role change returns `REFERENCE_AUTHORITY:Approve` without an edit POST or state/version change. This run covers the self-review pack, not every supported pack or an independent affordance enumeration. |
| SD07 | PARTIAL | Canvas/panel presentation changes preserve semantic identity; reload restores the saved candidate. A stale-version race was not sent by this browser replay; add backend/HTTP stale-command evidence. |
| SD08 | NOT_RUN | No MCP client run or before/after agent-read snapshot comparison in this browser replay. The browser owner-boundary observation is not evidence of MCP authority boundaries. |
| SD09 | NOT_RUN | Impact view is reachable, but independent witness-path enumeration is not executed here. Include the bounded graph/impact tests separately. |
| SD10 | PARTIAL | Semantic identity changes with an accepted edit and restores on undo/redo. Source-review and human-unknown states remain visible; verification refuses the changed source. Adversarial model/source/tool identity substitutions require focused evidence tests. |
| SD11 | PARTIAL | Actual browser/server journey covers intent, source, semantic editing/refusal, history/reload, panels, keyboard, scale and evidence. Broader non-linear journeys and the unexecuted UX observations below remain. |
| SD12 | PARTIAL | Changed implementation visibly retains `SOURCE_REVIEW_REQUIRED`; verify refuses, approval/apply stay disabled, human understanding remains `UNKNOWN`. Link/generation/release verification results are pending the integrator. |
| UX01 | PARTIAL | A model-first case traverses source, intent, history, evidence and back while retaining the current candidate. Independent source-first and agent-change-first starts and cross-case selection isolation were not run here. |
| UX02 | PARTIAL | Desktop screenshots at 1600x1100 and 1280x800 are readable; panels reclaim space; compact controls reflow. The Inspector toggle contrast defect is fixed and the integrated audit has zero automatic violations. A broader long-label/empty/error-state sweep is absent. |
| UX03 | PARTIAL | Default 100%, Overview, zoom/pan and the optional saved branch are observed. Overview intentionally shrinks labels. The 320x568 scale defect is fixed and the font-size/matrix regression passes; the short viewport shows only a small clipped portion of the graph. Other packs/layout stress cases remain separate. |
| UX04 | PARTIAL | Legal/illegal edits, exact semantic undo/redo, read-only history/baseline, and reload recovery work. Cancel, stale browser commands, transport failure and retry are not all exercised. |
| UX05 | PARTIAL | Current candidate/revision survives baseline/history previews and reload; historical Owner and current Agent role are distinguished. Cross-case switches and deliberately substituted stale evidence need separate tests. |
| UX06 | PARTIAL | Command palette focus/Escape, tab/tree arrows, Enter selection, splitter keyboard control, source-region focus and 25 real Tab stops are observed. A complete source/edit/refusal journey using only the keyboard was not performed. |
| UX07 | PARTIAL | This recording intentionally adds pacing and is not latency evidence. The separately retained HCI refresh3 measures median settled DOM 86.5ms and first-feedback p95 4.7ms, with settled p95 836.8ms. It remains synthetic/instrumented, excludes perceived paint latency, and does not complete the double-activation/failure/retry acceptance sweep. |
| UX08 | PARTIAL | Manual inspection found and retained real defects beyond a simple happy path; fixes were verified instead of hiding them through forced clicks or edited footage. Broader hands-on use and an owner's product acceptance remain unobserved; no human comprehension study is claimed. |

## Counterexamples and accessibility limits

- `final-recording-1/failure.png` and its JSON retain the compact zero-width workspace: hidden sidebars removed grid auto-placement slots. The explicit grid-position fix restored navigation at both compact heights; `final-recording-2/reflow-320-800.png` shows the corrected view.
- `final-recording-2/reflow-320-568.png` retains a second manual finding: the toolbar reported 100% while a very short canvas shrank text. In recording3, the exact viewport fix passes the 14px minimum rendered label threshold and actual screen-matrix scale 1 within 0.005 at both compact sizes. Short viewports necessarily show a limited part of the graph; do not call this a complete mobile IDE usability result.
- `final-recording-3/axe.json` retains a serious automatic `color-contrast` failure for `#toggle-inspector` in Intent, Evidence and Repository: foreground `#647992` on background `#101d2d`, ratio 3.79:1, required 4.5:1 for 13px text. The repaired color `#849bb7` measures 5.951:1 in the UI owner's focused browser check. The integrated `final-recording-4/axe.json` confirms zero automatic violations in all four views. It still contains incomplete color-contrast findings for 19 Model targets and two targets in each other view; these are **REVIEW_REQUIRED**, not WCAG conformance.
- `manual-a11y-1/observations.json` preserves actual computed styles and 25 Tab focus stops. Sample contrast ratios are 12.803:1 for state labels, 6.897:1 for state metadata, and 11.412:1 for edge labels against their actual fill/halo. These samples do not resolve every incomplete axe target or interaction state.
- Screen-reader use, forced colors, reduced motion, live-model usefulness, human comprehension, external repositories and held-out generality are **NOT_RUN**.

## Supplemental engineering evidence supplied by the repair lane

The repair lane reports these concrete executions; merge them with the final frozen-tree gate record instead of treating the browser-only map as the whole project's test coverage. `.tmp/codex-e2e/repair-focused.log` records 237 passing repository/source/diagram/HTTP/policy/mutation tests. `.tmp/codex-e2e/repair-gates.log` records 98 property passes with six existing expected failures, 94 OKF passes with two skips, and API PERF01–06 passes. API timing is not browser timing.

| Acceptance rows | Executed controls named by the repair lane | Limit |
|---|---|---|
| SD02–03 | `test_repository_connection::test_equal_inputs_repeat_without_writing_target`; `test_missing_binding_fails_actual_weave_lint` | Positive repeatability and a planted missing binding; final combined source subject must still be recorded. |
| SD02–04 | `test_repository_source::test_source_is_exact_captured_bytes_with_ast_location_and_no_target_write`; `test_declared_file_binding_is_a_file_only_preview_not_a_claimed_symbol` | Exact captured source and file-versus-symbol distinction; not universal language or behavioral conformance. |
| SD08 | `test_repository_source::test_mcp_source_is_read_only_narrow_and_returns_same_bound_payload` | Narrow MCP source surface only; the full tool/authority matrix needs its own current run. |
| SD09 | Property `test_closure_is_reachability` and four closure mutants | Independent bounded graph oracle and seeded faults; unknown real dependencies remain outside the graph. |
| SD10 | Property `test_stale_subject_dimension_makes_receipt_stale` and `ignores_subject` mutant | Evidence subject substitutions and fault sensitivity; not a human understanding result. |

The repair lane confirms that a deliberately false rendered-endpoint control for SD05 is absent. Existing broader MCP/affordance/history test names are not enough to infer their current execution: the 237-test selection does not include all of them. The final full-gate record remains pending the integrating agent.

## Release decision boundary

`hci-refresh-3/` preserves the actual raw `report.json`, `trace.json` and `REPORT.md`, copied and SHA-256 checked before another collection can overwrite them. Its budget status is **16 PASS, 1 GAP and 1 FAIL**: the visibility/chunk proxy is **70 against the allowed budget 27**. The remaining GAP is settled DOM p95 836.8ms against the 400ms target, within the existing 4000ms ratchet. Axe reports zero critical/serious/moderate/minor violations; focus loss is zero of 15 activations. Color-contrast incompletes remain. The earlier `hci-refresh-2/` retains the historical contrast failure and 15 PASS, 2 GAP, 1 FAIL result. HCI uses the explicit `pytest-harness` identity and Chrome 154.0.8037.58, unlike the ordinary source-review identity and isolated Chromium 153.0.8010.12 in this lane. Synthetic harness approval is not owner approval.

Source-connected functional evidence is available and the normal-identity replay passes all 20 checks. Full SD/UX acceptance, applicable local gates and maintainer source review remain separate decisions. This report supports a **draft implementation checkpoint, not a release decision**. It does not claim the full acceptance contract is closed, nor that passing a scripted recording proves better engineering outcomes. Keep the raw failed runs and the final current-subject observations together. The HCI budget failure remains explicit despite the successful normal-identity replay.

## Retained run artifacts

The local run bundle retains `final-recording-4/observations.json`, `subject-manifest.json`, `semantic-diff-response.json`, `axe.json`, `accessibility-snapshot.txt`, screenshots, and the unedited video. These are local execution artifacts, not an assertion that every raw file is distributed in this repository. The source manifest captures the dirty working-tree bytes rather than equating them with the base commit. The separately archived HCI report is also available through [the generated HCI report](../hci/REPORT.md), whose current revision may be newer than this dated checkpoint.

| Identity | SHA-256 |
|---|---|
| Captured source/pack/replay content | `de2326e3595f4b76526e7cb807e3fc498989ded15a9c2bead1af80be4de34e95` |
| Self-review pack | `e0c4b2783c1e30238870be7d65ac680adb41ed1bd4745affed0135f723019f1d` |
| Replay script | `113a1f0b272d401e31697b6d6d9c6f599f2dfebc207092508113a1047e77c798` |
| Archived HCI refresh3 report JSON | `680962b8c387e597bfa2b3a51909b3063cd83dcb2e7eb7079e935fd248b80d70` |
