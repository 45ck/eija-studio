# The source-connected IDE on main (8 October 2026)

[PR #78](https://github.com/45ck/eija-studio/pull/78) merged the source-connected IDE onto `main` as merge commit `e0649f70b9cad982e6bd0c9feb84b4cefda0a05f`. Until then the IDE lived only on draft branches: [PR #29](https://github.com/45ck/eija-studio/pull/29) (`integrate/all`) and [PR #76](https://github.com/45ck/eija-studio/pull/76) (`work/recovery-provenance-20261003`). It was a merge commit, not a squash, so the lane PRs those branches already contained (#12, #14, #16, #22, #23, #24, #25) are recorded as merged. #76 was closed as superseded because its base was `integrate/all`.

This record describes what landed and what was checked. It does **not** close full IDE acceptance, the POC/POF package or any human-benefit claim; see [what remains open](#what-remains-open).

## Run it

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: py -3 -m venv .venv; .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,source-analysis]"
eija serve --pack packs/eija-review-slice --repo . --open   # EIJA on its own checkout: read-only, offline
eija serve --open                                            # synthetic excursion example
```

Use **New intent** to start a change case, then move freely between Model, Source, Intent, Changes, Run and Evidence. The offline provider is a deterministic fixture, not a live model. The repository connection never writes to or executes the checkout. While `SOURCE_REVIEW_REQUIRED` is shown, Verify, Approve and Apply are refused (see [#80](https://github.com/45ck/eija-studio/issues/80)).

## What #78 added on top of #29 and #76

| Area | Change |
|---|---|
| Integration | #76 merged with the newer `integrate/all` head (`79ce22f`). In the one conflict (`resources/web/compare.js`), #76's later quiet-label hierarchy and its test were kept: unchanged initial states show only the Initial marker, and Unchanged stays in the accessible name. |
| Linux gate fixes | The vocabulary gate skips gitignored `*.egg-info`. npm shim paths map backslashes to the platform separator; this is a no-op on Windows. |
| Model canvas | Drag handles sit on the routed line's own ends, and the selected transition's label is set beside the line, so the handles no longer cover it. |
| Inspector | Each Change button sits beside its select. The visible text is "Change"; accessible names stay "Change source/target/role". Model references and source bindings render as a plain list. |
| Demos | `assurance_loop` opens the unsupported-interpretations disclosure before highlighting it. The new `ide_walkthrough` scenario drives the self-dogfood IDE. Scenarios can set `CONNECT_REPOSITORY`/`PACK`. Captions and the demo cursor stay visible over modal dialogs. |
| Proof of concept | The [IDE walkthrough record](../demos/2026-10-08-IDE-WALKTHROUGH.md) has a 2:34 real-browser recording (PARTIAL), stills and provenance. |

## Checks on the merged head

These ran on Linux with Python 3.13.16. The browser was Playwright's bundled Chromium 141.0.7390.37 through the `chrome` channel, not Google Chrome. The earlier Windows results recorded on #76 remain bound to their own subject.

| Check | Result |
|---|---|
| `nox -t fast` | 22/22 sessions pass |
| JavaScript (`node --test tests/web/*.test.cjs`) | 503 pass, 0 fail |
| `python scripts/verify_release.py` | 2,672 passed, 172 skipped, 2 xfailed; `source_review: SOURCE_REVIEW_REQUIRED` (expected, not stamped) |
| `nox -t full` | Fails only on `hci`, with 39 tests passing and two budget FAILs: KLM 65.31 > 65 s and density 52 > 27. `metrics` LANE-01 repeats that FAIL. `formal_bend_quick` and `graph_formal_full` are NOT_RUN (no Docker, no Alloy jar). |
| Browser journeys | `native_gesture_parity`, `agent_edit_review`, `prospective_edit_review` and `source_first_review` PASS |
| Demo dry runs | `assurance_loop` and `ide_walkthrough` are PARTIAL: verify, approve and apply are blocked by source review |

Budgets, fixtures, receipts, expected outcomes and `trusted_build.json` were not changed.

## What remains open

- **[#79](https://github.com/45ck/eija-studio/issues/79): re-derive the two HCI limits for the IDE.** The owner chose to reset them. Agents may not raise budgets, so the proposed values (KLM 65.31 s, density 52) wait for a human commit.
- **[#80](https://github.com/45ck/eija-studio/issues/80): owner source review and restamp.** This unblocks verification, approval and apply, and a full-PASS re-recording of the walkthrough.
- The [self-dogfood acceptance contract](SELF-DOGFOOD-ACCEPTANCE.md) (SD01–SD12, UX01–UX08), manual accessibility review, a fresh-clone proof on this exact commit, live-provider validation, a human comprehension study and external-codebase generality all remain open.
