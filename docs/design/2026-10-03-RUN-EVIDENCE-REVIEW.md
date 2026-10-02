# Run and Evidence review: truthful attempts, exact subjects

**3 October 2026 — scoped implementation checkpoint; full product acceptance OPEN.** Implementation: **e80efabded0e2b311254ec5efff2f74cc2e54786**. Fast engineering gate: **PASS**; post-demo-repair repeat: **22/22 sessions PASS, exit 0, 259.375 s; 2,380 passed, 206 skipped and two expected failures**. Full gate: **FAIL**; the 35-session run recorded 31 successes, three failures and one skip. Release: **SOURCE_REVIEW_REQUIRED**, exit 2, with its tests passing. The repaired historical demo is **PARTIAL**, with its owner-dependent act unexecuted. This note does not merge the implementation onto main or complete the supported IDE, GitHub POC/POF or human-validation goals. The [earlier Rules record](2026-10-03-RULES-REVIEW.md) retains its own subjects and outcomes.

## What changed

Run now distinguishes the latest attempted action from the last confirmed state and commit. A denial replaces the previous success message; an interrupted or invalid response stays unknown. If the server acknowledges a commit but refreshing the workspace fails, the commit stays confirmed while the view is explicitly unrefreshed. Returning to the same context, resetting a preview, editing the model and changing cases follow distinct retention rules.

![Immediate role refusal in the actual EIJA Run view](https://raw.githubusercontent.com/45ck/eija-studio/e80efabded0e2b311254ec5efff2f74cc2e54786/docs/demos/assets/run-evidence-20261003/denied-before-refresh.png)

*Immediate real role refusal after an earlier successful Propose; persisted state unchanged.*

Evidence presents one subject-bound ledger. Only one exact claim/formal-record pair with compatible kind, status and subject may share a row; mismatches, duplicate kinds, conflicts and unavailable results remain visible. Raw assumptions, bounds and provenance remain inspectable. One global New intent entry and contextual semantic undo/redo in Model and History use the existing server authority and version contracts.

The original browser run reproduced the defect: Propose committed with HTTP 200; the next SelectMeaning attempt received actual HTTP 409 `ROLE_DENIED`, yet Run still displayed “Committed: Propose.” Independent case/runtime observations were unchanged by the denial. That original **FAIL** remains retained.

## Actual product recording

![Real Propose commit followed by SelectMeaning role refusal](https://raw.githubusercontent.com/45ck/eija-studio/0957269149e0270d60881633318404009128376c/pr/29/run-commit-refusal-20261003.gif)

This recording shows the working Run view: the same synthetic Agent commits Propose with HTTP 200, then receives HTTP 409 `ROLE_DENIED` for SelectMeaning. Independently read persisted state is unchanged by the refusal. The recording uses normal source-review-required identity, an offline provider, disposable data and the normal CSP; zero CSP violations, JavaScript errors or forbidden endpoint attempts were recorded. It closes its browser/server and preserves all 115 captured source/replay files.

The adapter reuses the repository's Scene mouse/click path, Take and GIF encoder, loading its recording-only overlay stylesheet from the same origin instead of bypassing CSP. The GIF is **1280×800, 3,878,306 bytes, 15 fps, speed 1**, with **11.02 s** on the encoder timeline (**11.00 s** from ffprobe) and no tail cut. The retained raw video includes the real setup; the GIF starts at the ready Run view. This scripted reference-model clip is not human usability evidence, a general-code execution demo or proof of the full IDE.

## Observed browser results

These runs used normal source-review-required identity, an offline provider and disposable synthetic data. Each captured 115 source/replay files, preserved its captured bytes and closed browser/server. Their subject digests differ because each captures its own runner; the cross-run comparison found 114 common captured files, including all 109 common source/pack files, byte-identical. These are separate executions, not one aggregate story pass count.

| Retained run | Actual result | Scope and limits |
| --- | --- | --- |
| `runtime-evidence-after-3` | **7/7 PASS:** one creation entry at 1440/320 widths; denial after success with independent state nonmutation; aborted transport; invalid response after a real commit; acknowledged commit followed by failed refresh; context/history isolation and keyboard undo/redo; held-request keyboard duplicate prevention. | The 409 denial and induced 503 refresh failure are expected controls. Invalid-response feedback remains unknown even when an independent read establishes the fixture committed. No automatic retry. This is supported model simulation, not execution of arbitrary connected source. |
| `review-workspace-runtime-2` | **9/9 PASS:** selected comparison, independently checked paired graph, exact source roundtrip, evidence focus/error recovery, historical/current subject distinction, self-loop/cross-case context, runtime retention, keyboard/reflow and scoped automated accessibility. | Viewports 1600×1100, 1280×800 and 320×800. Zero automated accessibility violations, **one incomplete check**. This route does not exercise every conflicting ledger packet or all manual/assistive-technology conditions. |
| Separate source-freshness fixture in that workspace run | **3/3 PASS:** captured S1; actual stale rejection retaining S1; explicit S2 refresh and impact. | Fixture removed, real file preserved, browser/server closed. Bounded source-change evidence, not proof of complete impact. |
| `rules-ripple-runtime-2` | **8/8 PASS:** empty inventory; baseline/history to current candidate; Changes inspection; case roundtrip; exact case-wide evidence subject; declared impact references; keyboard at 1440×900 and 1280×800. | Navigation caused no execution or owner decisions. Unknown/ambiguous generated-reference fixtures and human usability were NOT_RUN. The Rules packet is case-wide, not a selected-rule verdict. |

No JavaScript errors or forbidden endpoint attempts were recorded. The workspace error/retry route deliberately produced its own 503. These browser checks did not call real owner verification, approval or apply endpoints, run a live model or establish human comprehension benefit. Ledger implementation and deterministic checks are not browser coverage of every conflicting packet.

### Retained attempts and screenshot correction

`runtime-evidence-after-1` remains **FAIL** after its creation-entry check passed. Re-entering the identical fragment URL returned no navigation response; the shared helper then tried to read response headers. The retained traceback identifies an instrumentation failure before the denial oracle. A narrow entry guard changed the runner, not the product denial contract. Earlier focused DOM failures and their repair remain in the engineering record.

The after-2 JSON assertions for commit-then-refresh-failure remain valid, but its `committed-refresh-failed.png` was overwritten **after manual GET recovery**. It must not illustrate failed refresh. The after-3 runner writes distinct immediate-denial and pre-retry failure filenames, and its seven checks pass again. Before the final browser runs, a separate vocabulary-gate repair changed the generic label “Returned instance” to “Acknowledged instance.” These final runs use that updated application subject; they are not merely a re-caption of after-2. Both earlier passing runs and unsuccessful attempts remain retained with their original identities.

The [integration image manifest](https://github.com/45ck/eija-studio/blob/e80efabded0e2b311254ec5efff2f74cc2e54786/docs/demos/assets/run-evidence-20261003/manifest.json) binds these four original captures to their result, script and source subject. Their bytes match the retained run files. Screenshot selection is not additional browser acceptance.

| Actual capture | Exact context |
| --- | --- |
| [Acknowledged Propose](https://github.com/45ck/eija-studio/blob/e80efabded0e2b311254ec5efff2f74cc2e54786/docs/demos/assets/run-evidence-20261003/allowed-propose.png) | Acknowledged Propose in the isolated candidate runtime; synthetic Agent actor. |
| [Committed, refresh failed — before retry](https://github.com/45ck/eija-studio/blob/e80efabded0e2b311254ec5efff2f74cc2e54786/docs/demos/assets/run-evidence-20261003/committed-refresh-failed-before-retry.png) | Acknowledged commit and last confirmed state retained after a controlled case GET 503, before manual retry. Problems was already expanded in this multi-step run. |
| [Evidence after context recovery](https://github.com/45ck/eija-studio/blob/e80efabded0e2b311254ec5efff2f74cc2e54786/docs/demos/assets/run-evidence-20261003/evidence-focus-error-restore.png) | One Evidence ledger after context recovery; the domain navigator is deliberately pinned and the comparison and inspector selections are distinct. |

## HCI and engineering status

Canonical HCI separately used **pytest-harness identity**, offline synthetic data and Chrome 154.0.8037.58 at 1440×900 with three timing repetitions. It is not the normal-identity browser evidence above or a human study. Its 22 UI asset hashes match the measured integration files. The [source-bound HCI report](https://github.com/45ck/eija-studio/blob/e80efabded0e2b311254ec5efff2f74cc2e54786/docs/hci/REPORT.md) belongs to this code checkpoint; this docs-only publication does not replace main's canonical snapshots or budgets.

| Gate / observation | Result |
| --- | --- |
| Canonical HCI | Completed, exit **1**: **15 PASS, one GAP, two FAIL**. |
| Density proxy | Maximum **48 > 27**, now at the start view; prior checkpoint maximum 52. Run-denied 45, Evidence-verified 44, Rules/impact 38. These are visible DOM grouping counts, not human memory or whole-app acceptance. |
| Modeled pointer journey | **65.31 s > 65 s: FAIL**, unchanged. KLM is a prediction, not observed task time. |
| Settled-DOM timing | Canonical p95 **727.6 ms**, **GAP** against 400 ms, within the unchanged 4000 ms ratchet. The separate full-gate HCI run measured **743.4 ms**. Earlier 733.1 ms and 744.7 ms observations and these shared-machine runs do not establish a controlled speed benefit. |
| Scoped accessibility / focus | Zero axe violations and **0/16** activations losing focus in the canonical route. Incomplete/manual accessibility remains open; the separate workspace browser run has one incomplete check. |
| Fast engineering gate | **22/22 sessions PASS**, exit 0, 231.281 s. Its test session records 2,380 passed, 206 skipped and two expected failures. |
| Full engineering gate | Exit **1**, 1,333.156 s: **35 sessions, 31 success, three FAIL, one skipped**. `demos_dry` used the removed `#new-case` selector; HCI failed density and modeled task time; aggregate metrics failed `LANE-01` because the HCI lane failed. Later targeted demo results do not change this retained full-run result. |
| Historical demo repair | The first targeted rerun **FAIL** reached a collapsed state-flow view; the second **FAIL** attempted an action before reset refresh settled. The repair uses current creation/ledger selectors, opens the state-flow disclosure and waits for current runtime observations. The third rerun exits **0** in 6.609 s, but explicitly reports **PARTIAL**: Act 4 (verify, approve, apply) is **NOT_RUN** because source review is required. The gated ledger selector is therefore not exercised by this run. Post-repair fast repeat: **22/22 sessions PASS, exit 0, 259.375 s; 2,380 passed, 206 skipped and two expected failures**. |
| Full-gate verification scope | Coverage **92.95%**; property tests **172 PASS**; mutation **107 killed, zero survived**, with 22 equivalents excluded. Bounded SMT, runtime BMC and TLA+ checks passed, including their declared negative controls and runtime conformance. These prove the encoded/bounded models and checks, not arbitrary source-code correctness. Generated EIJA laws retain **four NOT_RUN** laws and library-loan retains **two NOT_RUN** laws. |
| Unavailable formal lane | Bend runtime verification **SKIPPED / NOT_RUN** because the Docker daemon was unavailable. The skip is not a pass. |
| Release and fixture restoration | Exit **2**, 531.25 s: **SOURCE_REVIEW_REQUIRED** and `trusted_fixture: false`; test exit **0**, 2,380 passed, 206 skipped, 26 deselected and two expected failures. Live providers were **NOT_TESTED_BY_THIS_SCRIPT**. Original `tests.xml`, `tests.log` and `last-verification.json` bytes were restored and verified. No fixture was stamped or promoted. |

The first gate set is retained separately: fast **FAIL** because “Returned” is reserved pack vocabulary in a generic UI label; full **INTERRUPTED**, with no full result claimed; release **NOT_RUN**. Original evidence bytes were verified unchanged. The one-label repair did not change the vocabulary allowlist or acceptance budgets. The current HCI and completed engineering/release outcomes above come from the second gate set on the repaired label. Neither the later targeted demo repair nor passing individual formal checks relabels the full gate as passing.

## Whole-app acceptance and next work

The [four personas and fifteen stories](WHOLE-APP-STORIES.md) and [ten-surface UX contract](WHOLE-APP-UX.md) remain the scope. This increment supports S06 Evidence, S07 Run and S08 History, with S01 Model/S02 Intent/S10 recovery connections: scoped US02/07/08/09/10/11 and H04/07/08/09 observations. Moving controls or removing repeated rows does not accept an entire story or HCI criterion.

**The ten-surface high-fidelity interaction/recovery handoff is unfinished.** Four populated generated stills cannot stand in for each surface's empty, loading, refused, failed and stale states, exact subject, keyboard order and reflow. Complete those states using the real components and retained observations. Concepts remain illustrative; demo footage must come from the working product.

Next, **US06/S05** needs an inspectable, server-derived pre-submit typed-edit comparison with consequences and a no-write Cancel path; **US07/S06** needs selectable witnesses that navigate only to explicitly mapped model/source identities. Reuse existing policy, comparison and source components. Negative-control traces must keep their own model/control subjects rather than masquerade as candidate failures. Both remain gaps, not accepted capabilities.

Source authoring stays in the engineer's existing editor/agent; connected source is read-only and model edits do not rewrite it. Factory S09 and US13–15, source-transformation adapters, arbitrary-code semantics, live-agent usefulness, clean-checkout whole-product feasibility, owner hands-on acceptance and comparative human validation remain separate work. No result here completes the full IDE/WOW goal.

## Evidence identities

| Retained result | SHA-256 |
| --- | --- |
| `runtime-evidence-before-1` | `37a787207d96f134a089c93b6efeee675cb827d91ae1686ea6515450df95390e` |
| `runtime-evidence-after-1` | `ac5c3887373589d55512909a32c4017e1551f524915b8952ebe4b28a1dc4258b` |
| `runtime-evidence-after-2` | `cffa9b5c47fcc17859a551afb6209b85f498ecaead0686f5b83ae7e82e2386d9` |
| `runtime-evidence-after-3` | `56b5249bb6dc0d117eaee6497b2379ee4ce53b7ce27d366eca249554be6ccd7e` |
| `review-workspace-runtime-2` | `304a6d35f81206006b3b0966d23d8db55bf71ff6bcf427e0664cd0ec46cddb56` |
| `rules-ripple-runtime-2` | `00473f3078f7fa377168e9208ca87fa4ab0e914d3b46b0eeaad8f056ddababe1` |
| Run recording `result.json` | `02ade27077e1e5ec2e54cbe228c52b88084c3601ab7b7943ef2a4d7bb30cb9a2` |
| Run recording GIF bytes | `84c2b39843a62209e9b0929b350d4ced47e1e652ca9e4abe42dad9a9273f11a7` |

Hashes identify the named original bytes, not truth by themselves. Per-run scripts and capture identities remain in the retained receipts and publication manifest. Raw local tracebacks, disposable request identities and private payloads are not reproduced here. The published implementation and media links pin this bounded checkpoint; later increments require new observations.
