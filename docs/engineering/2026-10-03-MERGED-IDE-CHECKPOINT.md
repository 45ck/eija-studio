# Merged IDE checkpoint — 3 October 2026

**Published incremental checkpoint [`ad9394e1`](https://github.com/45ck/eija-studio/commit/ad9394e1d4ae93259ee43ce8448b60c96a826a40); complete IDE, WOW and POC/POF acceptance remain open.** Ten offline browser journeys passed against identical product bytes, and a separate JavaScript run passed 495 tests. This record follows the [mission](MISSION.md), [self-dogfood acceptance](SELF-DOGFOOD-ACCEPTANCE.md) and [whole-app stories](../design/WHOLE-APP-STORIES.md). It remains fixed to this checkpoint as later implementation work continues.

## Tested subject

The browser runs tested an **uncommitted merge** with HEAD `efd33fa7e5ba51f0f21e0382ddb0b0309b08375c` and MERGE_HEAD `d861d454710e16234b5c8fdbf0881fb2d904a52f`. That merge was committed and pushed as **`ad9394e1d4ae93259ee43ce8448b60c96a826a40`**. The publication receipt confirms all **510 committed source/test/tooling files** match the passing fast manifest, with local HEAD, tracking and remote branch equal, zero divergence and clean state at publication. Its product manifest covers **114 files under `src/` and `packs/`**, including vendored assets; every selected browser journey matches those bytes. Each replay records its own helper/source manifest and preserves it during that run; the 114-file comparison is not a claim that every test or packaging file is identical across browser runs.

All ten journeys use disposable offline workspaces and the ordinary source-review-required identity. Browser/server cleanup and captured-source preservation pass. No owner approval or baseline apply, live model call or human study is represented. Candidate model edit is distinct from owner approval/baseline apply and does not rewrite connected source.

The checkpoint is on `work/recovery-provenance-20261003` in [draft PR76](https://github.com/45ck/eija-studio/pull/76), based on the integration branch. PR29 remains the separate upstream integration PR. The predecessor [`efd33fa7`](https://github.com/45ck/eija-studio/commit/efd33fa7e5ba51f0f21e0382ddb0b0309b08375c) has the earlier feasibility proof below. Neither parent alone identifies the tested combined product, and these observations do not validate subsequent commits or assert that main ships this interface.

## Working review loop

An AI-assisted engineer can inspect actual proposal provenance and retained failure state, use the explicitly synthetic bounded edit proposer, compare real model changes and choose whether to persist a candidate edit. A modeller can use checked forms or supported native canvas gestures, inspect the resulting rules/source, and undo. A reviewer can follow exact captured source, inspect formal status/origin/raw data and return to the same check, or follow a runtime refusal to its exact rule and return to the original attempt.

The merge preserves readable before/after labels and unchanged model context, explicit drag feedback, deliberate opening of owner review, and narrow-panel access to formal raw data. Verifying the bounded runtime does not open or fill review questions automatically. These observations support parts of US02–US11; they do not close all those stories.

## Browser and JavaScript observations

| Journey | Result | Retained run |
|---|---|---|
| Formal evidence unavailable / raw return | PASS | `merged-ide-browser-3/formal-unavailable` |
| Recorded formal artifacts / subject context | PASS | `merged-ide-browser-3/formal-recorded` |
| Model/Changes/source/history review | PASS | `merged-ide-browser-4/review` |
| Prospective edit and no-write cancellation | PASS | `merged-ide-browser-4/preview` |
| Native gesture parity | PASS | `merged-ide-browser-4/native-gesture` |
| Source-first investigation and return | PASS | `merged-ide-browser-4/source-first` |
| Combined rule recovery | PASS | `merged-ide-browser-4/rule-recovery` |
| Proposal provenance and failure recovery | PASS | `merged-ide-browser-5/provenance` |
| Bounded offline agent edit / drag / undo | PASS | `merged-ide-browser-5/agent-edit` |
| Runtime refusal, diagnostics and exact return | PASS | `merged-ide-browser-5/runtime` |
| JavaScript regressions, separate execution | **495 PASS, zero FAIL** | `merged-ide-browser-evidence-1/node-final.log` |

The recorded-formal replay checks presentation of retained fixtures; it is not a fresh solver result. Browser assertions, negative controls and individual check counts belong to their replay reports, not one summed story-acceptance score.

Three failed integration attempts remain retained: proposal provenance was initially placed under hidden Changes content; the focused formal raw region clipped at 320 px; and the review helper assumed a tree group remained expanded after the new collapsed default. The first two required product repairs. The third now opens the actual tree group with native input before retaining the original graph assertions. The final selected runs share the repaired product bytes; no budget or source-review requirement was relaxed.

## Gates at ad9394e1

Canonical and expanded HCI use the separately declared `pytest-harness` identity; synthetic owner-flow mechanics there are not normal-source approval, a maintainer decision or human validation. The run used Windows 11, installed headless Chrome **154.0.8037.95**, Playwright **1.63.0**, axe-core **4.12.1**, three pointer repetitions and one keyboard journey. The [checkpoint HCI report](https://github.com/45ck/eija-studio/blob/ad9394e1d4ae93259ee43ce8448b60c96a826a40/docs/hci/REPORT.md) retains the exact UI and instrumentation hashes.

| Gate or observation | Result on the combined subject |
|---|---|
| Required-state capture | **PASS: 18/18** declared states captured and bound to actual subject, screenshots and viewport. This is coverage, not complete UX acceptance. |
| HCI budgets | **14 PASS / two GAP / two FAIL**; budget limits unchanged. |
| Predicted task effort | **FAIL: KLM 65.31 seconds > 65** for the pointer journey; this is a model prediction, not observed user time. |
| Visible-density proxy | **FAIL: 50 > 27** at canvas View, 1440 px (**33 controls + 17 text groups**). Pinned Domain/inspector is 43; runtime attempt details 38. These are actual useful states, not a human memory score. |
| Feedback | **GAP: settled-DOM p95 825 ms**, target 400 ms, limit 4,000 ms; median 95.1 ms. Paint and perceived latency are unmeasured. |
| Keyboard | **GAP: one of 16 activations loses focus to body**, after `ask-interpretations`; two subsequent Tabs reach the next target. The journey completes, but the defect remains open. |
| Automatic accessibility and hygiene | Zero axe violations, measured reflow/target-size failures, stops without a visible focus indicator or JavaScript exceptions. Manual axe incompletes remain for ARIA and contrast; this is not WCAG conformance. |
| Fast, attempt 3 | **PASS: 22/22 sessions**, 277.75 seconds overall; **2,634 tests passed, 210 skipped, two expected failures and 28 warnings** in 189.97 seconds. All 510 recorded source/test/tooling files and original evidence remained unchanged. HCI2 UI and instrumentation hashes match this run exactly. |
| Full / release on this merge | **NOT_RUN**. Earlier parent results do not apply; source review remains required. |

The earlier agent-edit 16 PASS / 2 GAP / 0 FAIL HCI result and the `efd33fa7` gate results describe different subjects and cannot be applied to this merge.

The expanded HCI audit reuses the existing recorder/probe and axe for individual Workspace and Intent disclosures at desktop and 320 px, pinned Domain context, canvas View and refused-attempt details. Its observed views contribute to accessibility and density measurements. Its setup/navigation actions and timings stay outside the canonical task's Fitts, Hick-Hyman, KLM, keyboard and Doherty metrics. It records actual subject/viewport/focus/scroll and screenshot identities, fails missing or unbound required observations, and preserves NOT_RUN coverage. Lower scroll positions, additional widths, individual narrow drawers and formal/source/agent-edit detail density remain unmeasured. Proposal-failure journeys have separate functional replay evidence, outside this density pass.

The first merged gate attempt (`merged-ide-gates-1`) remains retained. Canonical HCI stopped at `verification_ready` because the closed review entry was below the Evidence pane. The diagnostic (`merged-hci-review-diagnostic-1`) observed verified/eligible state without blockers, review closed, focus retained on Verify, empty answers and unchecked boxes. The harness now requires the review entry to be visible after the subsequent explicit native-open action. Product bytes were unchanged by this correction. Fast recorded **2,631 passed, 210 skipped and two expected failures**, with a separate complexity failure for two new HCI audit helpers over the existing budget. The helper repair and second run preserve those budgets; the first failed attempt is not converted to PASS.

Fast attempt 2 (`merged-ide-gates-2/fast.log`) also remains **FAIL**: **2,633 passed, one failed, 210 skipped and two expected failures**; 21 of 22 sessions succeeded. Its remaining Node-backed test still required the closed, below-pane review entry to be visible. The state-specific negative control was updated to allow that closed state and require visibility after actual opening, preserving the other controls. The focused 33-test JavaScript rerun passed. Product and HCI instrumentation bytes stayed unchanged, so HCI2 retains its original subject; the final fast rerun is separate.

## Earlier published feasibility proof

The separate `github-recovery-ux-1` proof passed on **published `efd33fa7`**, in **307.8 seconds**: public GitHub clone, new Python 3.12 environment, editable install and dependency/import checks, installed CLI public-HTTP startup and cleanup, then source-first, native-gesture, proposal-provenance and combined-rule-recovery replays. The clone stayed clean before and after. Existing Windows host, package and browser caches were reused; it is not a new-machine, independent-engineer or cross-platform result.

This proves those installation and replay operations for that predecessor. Repeat feasibility on the later published integrated subject before using it as the final POF artifact.

## Retained evidence identities

These are local run artifact identifiers under `outputs/pof/`; raw logs and videos are not implicitly published by this document. Public release packaging must include a reviewable scoped evidence bundle or stable links, plus the replay instructions.

| Artifact | SHA-256 |
|---|---|
| `merged-ide-browser-evidence-1/summary.json` | `dec2700fa44bc5aaba643f1956dffb3d72d3b24cf24aab7927c41df22df399ce` |
| `merged-ide-browser-evidence-1/node-final.log` | `a259f27d9cb38a6b7e3100dd8e975e52aedbc11dd37b5635a4c5b8be431b0b80` |
| `github-recovery-ux-1/proof.json` | `24c68a1294eebe6a1c77c57e3f40005a74170ef37aa3d36bfdee9f5c9adb0f32` |
| `merged-ide-gates-2/hci/report.json` | `9a9bf83dc6b2d7ba5f8ec948b3a2f8ebf4bb93df2b8b67015c3957ab5d165e4c` |
| `merged-ide-gates-2/hci/trace.json` | `a70f8d80c7c036ca403d19243421e13909241fe564e732473644da02973da8cb` |
| `merged-ide-fast-3/summary.json` | `2ac39d1e68ff6f701290cfcbc85313485e5d760287d2c2b59c057a8f52cf2d44` |
| `merged-ide-fast-3/fast.log` | `6d96422ae6f446e0a5305d8e9200a2492e8e9dff691ad323c41412f2730e1ab2` |
| `merged-ide-publication-1/proof.json` | `f7fd71ddb2f9b37d90779ff6e02c1e3f6ea02bc49e56269e8e1ea4e7c7260657` |

The summary contains the 114 product hashes and each journey's result hash, preserved-subject and cleanup observations. A hash identifies retained bytes; it does not prove their claims correct.

Replay entry points: [agent edit](../../tests/hci/agent_edit_review.md), [proposal provenance](../../tests/hci/proposal_provenance_review.py), [combined rule recovery](../../tests/hci/combined_rule_recovery.py), [source-first review](../../tests/hci/source_first_review.py), [native gesture parity](../../tests/hci/native_gesture_parity.py), and the [HCI method](../hci/README.md). Use the documented prerequisites and the exact published subject intended for reproduction.

## Acceptance needed before the WOW package

The [high-fidelity reference](../design/README.md) specifies ten surfaces, four persona hypotheses, fifteen stories and H01–H10. It remains a design artifact. Current browser observations support a working review loop; whole-app readiness also requires necessary opened/pinned/error states, readable long and dense models, broader viewport/text-size checks, manual accessibility and hands-on use beyond the scripted route. Formal graphical counterexample correspondence remains incomplete. Paint-aware responsiveness and human comprehension cannot be inferred from settled-DOM timing or a density proxy.

Keep source-review-required, UNKNOWN and unsupported semantics visible. Resolve consequential product defects and document applicable gate outcomes, reproduce the final published revision, then capture its actual non-linear tasks for the walkthrough and clips. Retain the original recordings and distinguish fixture activity from live inference. US13/14 factory coordination and US15 domain refactoring remain planned. EIJA is the first validation target; external projects follow the first accepted flow. Reduced comprehension burden, superior V&V and general codebase support remain unproved.
