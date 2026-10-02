# Prospective edit review: inspect the captured change

**3 October 2026 — implementation [ca95f46](https://github.com/45ck/eija-studio/commit/ca95f468206fec706f7a274788faf872877ac4a1).** Engineers can inspect a server-derived model comparison before submitting a typed edit, close it without writing, or explicitly apply its captured transaction. Scoped browser checks and fast engineering gates pass. Full gate **FAILS: 32 successful sessions, two failed, one skipped**; HCI and aggregate metrics remain blockers. Release exits **2: SOURCE_REVIEW_REQUIRED**, although its tests exit 0. Full US06, whole-app IDE/WOW and GitHub POC/POF acceptance remain open. The [earlier Run/Evidence record](2026-10-03-RUN-EVIDENCE-REVIEW.md) retains its own subjects and results.

## Working interaction

![Real Owner to Agent preview followed by Close](https://raw.githubusercontent.com/45ck/eija-studio/8633d7d8e950cc407b458382b5b03ec60be35f30/pr/29/prospective-edit-close-20261003.gif)

*Real product recording: inspect Save's Owner → Agent preview, then Close. Zero edit POSTs; the authoritative case, packet, history and runtime remain unchanged, including revision 2 and its semantic hash. This clip demonstrates preview and cancellation only.*

The 14.87 s encoded GIF is 960×600 at 15 fps, original speed, with no tail cut. Real UI setup is retained in the raw recording before this segment. It uses a disposable offline fixture, normal source-review identity and normal CSP; the recording-only same-origin cursor adapter adds no invented product labels. Duration is media length, not a latency measurement. GIF SHA-256: `3f885ec73446485dbee5ccb56e6523694a386939b2581249ed4eee279e978037` (4,479,499 bytes). The [earlier Run commit/refusal recording](https://raw.githubusercontent.com/45ck/eija-studio/0957269149e0270d60881633318404009128376c/pr/29/run-commit-refusal-20261003.gif) retains its earlier e80efab subject and scope.

The preview captures one case revision and returns its exact current/proposed models, semantic hashes and transaction. Changed old/new values lead the comparison. Close preview or Escape discards only the unsent interaction. Apply edit sends that transaction and captured version to the existing route, which repeats authority, lifecycle, history and policy checks. A concurrent change can invalidate the preview immediately.

The read-only adapter reuses the existing history replay, interpreter and policy; it grants no capability, reserves no revision and adds no alternative semantics. Refusals return no candidate or candidate hash. Existing policy-only edit-check HTTP/MCP behavior stays intact. [ADR-0149](https://github.com/45ck/eija-studio/blob/ca95f468206fec706f7a274788faf872877ac4a1/docs/adr/0149-read-only-edit-preview.md) records this boundary and reuse.

After submission, the comparison consistently describes **captured** snapshots. The top outcome states whether no write has been sent, submission is active, the edit was acknowledged, refused, or its outcome is unknown. Acknowledged edits survive failed refresh; unknown acknowledgements never imply no commit. A case-owned reconciliation notice remains after closing, further semantic edits are blocked until authoritative refresh, and GET recovery does not retry the write. Late replies cannot replace a closed or newer context.

| Actual capture | Exact context |
| --- | --- |
| [Unsubmitted role still](https://github.com/45ck/eija-studio/blob/ca95f468206fec706f7a274788faf872877ac4a1/docs/demos/assets/prospective-edit-20261003/unsubmitted-role.png) | Unsubmitted server preview: Save role Owner to Agent; no edit sent. |
| [Source endpoint preview](https://github.com/45ck/eija-studio/blob/ca95f468206fec706f7a274788faf872877ac4a1/docs/demos/assets/prospective-edit-20261003/unsubmitted-source.png) | Unsubmitted server preview: Verify source PREVIEW to SAVED at 1280 by 800. |
| [Acknowledged edit, before recovery](https://github.com/45ck/eija-studio/blob/ca95f468206fec706f7a274788faf872877ac4a1/docs/demos/assets/prospective-edit-20261003/acknowledged-edit-before-close-and-retry.png) | Edit acknowledged once; controlled workspace GET failure; Apply disabled before Close and recovery. |
| [Unknown acknowledgement](https://github.com/45ck/eija-studio/blob/ca95f468206fec706f7a274788faf872877ac4a1/docs/demos/assets/prospective-edit-20261003/unknown-edit-before-close.png) | Controlled lost acknowledgement; outcome unknown; no automatic write retry. |

The [four-still capture manifest](https://github.com/45ck/eija-studio/blob/ca95f468206fec706f7a274788faf872877ac4a1/docs/demos/assets/prospective-edit-20261003/manifest.json) binds those PNG bytes to preview-5's result, script and 117 captured source/replay files. The separately recorded GIF has the same 117-file source subject; its own wire, before/after and cleanup receipts retain the preview/Close outcome. Captured source matches this implementation commit. Product captures do not establish human usability or complete consequences of arbitrary source edits.

## Current browser and engineering evidence

The five product browser runs below used normal-source-review identity, normal CSP, an offline provider and isolated synthetic fixtures. Each run preserves its captured subject; differing runner inventories give the runs different subject hashes. These are separate scoped executions, not a count of accepted user stories. Canonical HCI uses the separate `pytest-harness` identity described in its engineering row.

| Final run | Result and scope |
| --- | --- |
| `us06-prospective-edit-5` | **5 PASS:** no-write Close/Escape; exact complete candidate on explicit keyboard Apply; late success/failure replies; acknowledged edit plus failed refresh; unknown acknowledgement and GET-only reconciliation. |
| `us06-journey-edges-5` | **7 PASS:** source/intent entry, cross-case historical/source context, no-write cancellation, actual two-page stale-version refusal, explicit retry and keyboard refusal. |
| `us06-runtime-evidence-4` | **7 PASS:** creation entry, refusal after success, transport/invalid-response uncertainty, acknowledged commit plus failed refresh, context/history isolation and duplicate prevention. |
| `us06-rules-ripple-4` | **8 PASS:** baseline/current/history navigation, exact case-wide evidence subject, declared impact destinations and keyboard/viewports. |
| `us06-review-workspace-3` | **9 PASS**, plus a separate **3-check freshness fixture PASS**: paired comparison, exact source/evidence/history context and responsive/keyboard review. Zero automated accessibility violations; **one incomplete check**. |

Expected candidates come from independent complete-model edits and actual server responses/GETs. Painted graph and changed-value geometry oracles retain their negative controls. Both changed values are initially visible at 1440×900 and 1280×800 without scrolling; the 320×800 probe checks desktop-created preview reflow, not complete mobile authoring. Narrow chooser wrapping remains a known issue. Four runs explicitly record browser/server closure; the edge schema records normal exit/context cleanup without separate closure flags.

[Compact browser receipts](https://github.com/45ck/eija-studio/blob/ca95f468206fec706f7a274788faf872877ac4a1/docs/demos/assets/prospective-edit-20261003/browser-receipts.json) retain the check names, subjects and result digests; their SHA-256 is `3eb374fece03f3abd6f1f18504998a982443d6642926789de19ca534b6bd8b6a`. The [replay guide](https://github.com/45ck/eija-studio/blob/ca95f468206fec706f7a274788faf872877ac4a1/tests/hci/prospective_edit_review.md) specifies setup, oracles and limits.

| Engineering observation | Actual result |
| --- | --- |
| JavaScript | **288/288 PASS**. |
| Fast gate, Windows / Python 3.12.10 | **22/22 sessions PASS**, 363.688 s. Test session: **2,404 passed, 206 skipped, two expected failures**; pytest duration 259.08 s. |
| Repository-query relocation checks | Separate focused run: **169 passed, one warning, 48.88 s**, covering dispatch/source/freshness, interface/preview boundaries and the real maintainability budget. Five static sessions passed separately. |
| Canonical HCI | Separate identity: `pytest-harness`, a kernel-test stand-in, never a release identity. **15 PASS, one GAP, two FAIL**. Density **48 > 27**; modeled pointer KLM **65.31 s > 65 s**. Settled-DOM p95 **914.2 ms**, GAP against 400 ms within the unchanged 4000 ms ratchet. All 22 UI asset hashes match. |
| Full gate | **FAIL**, exit 1, 1481.391 s: **32 successful / two failed / one skipped** of 35 sessions. Failed: `hci`, `metrics`. `formal_bend_quick` is **NOT_RUN**, Docker daemon unavailable. Its fresh HCI probe measured p95 **909.5 ms**, distinct from the canonical 914.2 ms above; density/KLM failures persist. |
| Full-run metrics | **19 PASS / one FAIL / one NOT_RUN**. LANE-01 fails the HCI aggregate. COV-01 was NOT_RUN when metrics collected; the later coverage session separately passed. Module MI-01 now **20.289 >= 20**. |
| Full-run coverage | **2,404 passed, 206 skipped, two expected failures, 28 warnings**, 222.15 s. Coverage **93.03%**, above the unchanged 78% threshold. This does not turn the failed full gate into a pass. |
| Full-run demo dry-run | Session succeeds, but scenario is **PARTIAL**: Act 4 verification/approval/apply is **NOT_RUN**, `SOURCE_REVIEW_REQUIRED`. No trusted-flow acceptance. |
| Release | Exit **2**, **SOURCE_REVIEW_REQUIRED**, 562.328 s. Tests exit **0**: **2,404 passed, 206 skipped, 26 deselected, two expected failures, 25 warnings**, 558.04 s. `trusted_fixture=false`; live providers **NOT_TESTED_BY_THIS_SCRIPT**. No fixture stamping or trusted-source promotion; the original three evidence files were restored byte for byte. |

Full/release continuation is bound to gate head `27cc455fee58dc19d3f0d8c049be16f9a3775dae`, whose Git tree `b9bf6349d6b3b21b61d69a8405873a4e62cd6a70` is identical to implementation ca95f46. The ancestry merge changed no source bytes; tree identity is a source binding, not a correctness or release result.

KLM is a prediction; DOM timing/grouping counts do not measure perceived latency, human memory or comprehension benefit. Independent review of the preview, selector scoping, repository-query relocation and lifecycle wording found no remaining material issue within those reviewed deltas. The reviewer did not execute tests or accept full US06.

## Retained failures and limits

| Earlier record | Retained outcome and bounded correction |
| --- | --- |
| Preview-1 / edges-1 / Rules-1 | Preview-1 keeps its five passes and cleanup warnings; edges-1 keeps six PASS/one failed hidden-inspector observation; Rules-1 keeps three passes before a comparison-selector collision. Real completion waits, explicit inspector navigation and ordinary-comparison host scoping preserve expected data, geometry and negative controls. |
| Source-1 bootstrap | The invocation that failed to import `quality` remains an instrumentation failure, separate from the later completed run. |
| Recording take-1 | A recorder assertion wrongly required `expected_version` in the read-only preview request; that field belongs to the mutating edit contract. Its actual first-take body/status were not retained. Corrected take-2 records HTTP 200 and the exact transaction-only request before asserting it, retaining complete candidate/no-write oracles. Product bytes were unchanged; the failed take remains retained. |
| Gate-1 | Fast **21/22 sessions**: one failed test, 2,400 passed. Module MI-01 was **19.644 < 20** while per-function complexity passed. Existing read-only repository dispatch moved into its existing module; no threshold or policy change. Full/release **NOT_RUN**. |
| Gate-2 / pre-wording captures | Fast passed **22/22**, but actual acknowledged/unknown screenshots exposed a **P2**: “Uncommitted edit preview” / “current candidate” contradicted the true outcome. Guards and disabled Apply were correct. Neutral captured-snapshot captions resolve the reviewed defect; new final runs above exercise the changed bytes. Full **INTERRUPTED** for repair; release **NOT_RUN**; original three evidence files restored exactly. |
| Earlier HCI timings | Gate-1 p95 **848.3 ms**, gate-2 **818.2 ms**; each retained 15/1/2 and the same density/KLM failures. Later timing changes do not establish a controlled speed benefit. |

This increment supports **US06/S05** typed-edit review and **US09–11** recovery, keyboard use and honest feedback. Full form/canvas-gesture parity, long/multiple-field pixel coverage, manual accessibility and complete normal/refused/stale/recovery acceptance remain open. The [four personas/fifteen stories](WHOLE-APP-STORIES.md), [ten-surface contract](WHOLE-APP-UX.md) and human validation remain the larger target. Connected source stays read-only; selectable witnesses, factory coordination and general source transformations remain separate work. Evolving design references are illustrative and are not publication or product-acceptance evidence here.

A separate source-only inspection flags keyboard scrolling of the raw Evidence packet (`#packet`) and error JSON (`#error-json`) when their disclosures are open and overflowing: neither has an explicit named, focusable-region contract. This is next product UX debt, not a new observed browser or axe failure; the scoped runs did not explicitly open those panes for their accessibility scans. Run's `#trace` already has named focusable-region markup, but actual key-driven scrolling under overflow remains unexercised. The next targeted check must establish real overflow, visible keyboard focus and scrolling at desktop and narrow widths while preserving the exact diagnostic text.

Next implementation work is US01/02: consolidate duplicated case pickers while preserving context, and give the raw packet/error regions an explicit keyboard contract. Preparatory patches remain outside this committed checkpoint. US07's exact-subject witness remains pending; the whole-IDE goal remains open.
