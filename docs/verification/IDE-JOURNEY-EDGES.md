# Independent IDE journey checks

This script extends the [self-dogfood acceptance](../engineering/SELF-DOGFOOD-ACCEPTANCE.md)
and [whole-app stories](../design/WHOLE-APP-STORIES.md) with seven real-browser journeys.
**Status: NOT_RUN when introduced.** A staged script is not execution evidence. The
JSON report and exact source manifest from an actual run determine its status.

Run from the EIJA checkout with the existing `hci` dependencies and isolated
Chromium installed:

```powershell
python tests/hci/ide_journey_edges.py --out reports/ide-journey-edges
```

Use repeated `--story NAME` arguments for a focused rerun. Unselected stories are
reported `NOT_RUN`; the report's `selected_stories` scopes its aggregate result.
Coordinate the serial browser slot and keep source bytes stable during a run.
On Calvin personal endpoints, complete the configured browser-account-router
device preflight before starting browser execution.

| Story | Executed path and independent oracle | Failure or gap detected |
| --- | --- | --- |
| `source-first` | Baseline → declared repository source → Model. Compare every displayed source line, line number, URI and captured hashes with a real source GET, and canvas edges/states with workbench GET. | Source mismatch, wrong baseline, or navigation writing a case. |
| `intent-first-changes` | Offline request → supported meaning → Changes. The added Save transition must be visible; exact case, subject and history GETs remain unchanged by review navigation. | Prompt cannot reach the real change review, or navigation changes semantics. |
| `cross-case-history-source` | Create A/B; give A a different role; preview A's initial meaning; switch from source to B and back to A. Inspect actual case revisions, each history cursor/hash, canvas, inspector and restored history mode. | A candidate/history/selection leaks into B, history becomes editable, or navigation changes either case. Repository source may remain shared only while its actual URI and captured snapshot identity remain explicit. |
| `cancel-unsubmitted-edit` | Change a role selector without submitting. Compare the entire case, evidence subject and semantic history before/after. Use `Cancel draft` if implemented. | No cancellation affordance is `GAP`, even when manual reselection leaves all server state untouched. Escape and manual reselection are documented observations, not invented cancellation support. |
| `stale-second-page` | Two real pages open the same case. B commits through ordinary controls; A attempts its stale edit. Compare GETs before/after rejection, then refresh A. | Lost update, stale write accepted, wrong retained model, or reload cannot recover. |
| `transport-retry` | Abort one real case GET during an explicit refresh. Preserve last valid canvas/selection and exact server state, then retry from the command palette. | Lost working context, phantom success, incorrect mutation, or error presentation remains after successful retry. |
| `keyboard-edit-refusal` | After ordinary fixture setup, use only actual keyboard keys through palette, native selects and buttons for a legal edit and a policy refusal. Compare GET affordances, exact typed transaction, candidate delta, revision/history and refusal codes. | Unreachable controls, unexpected semantic changes, refusal submitted as a real edit, or lost focus. This does not claim keyboard-only setup or human usability. |

The server helper creates its own disposable local workspace with the normal
source identity. `SOURCE_REVIEW_REQUIRED` is expected. It never attaches to a
personal browser profile or an existing owner workspace. All semantic writes use
ordinary UI controls; independent observers issue GET requests only. Approval and
apply requests are intercepted, denied and fail the story. No live inference,
fabricated response body, forced click, DOM model injection, owner decision or
source stamping is used. The sole fault injection aborts a real GET; retry reaches
the real server.

Each story gets a new isolated browser context and continues independently of
other stories. Artifacts include screenshots, request paths/methods, real GET
oracle responses and `observations.json`. These contain synthetic cases and
public captured source; the test-owned session capability is not recorded.
`subject-manifest.json` hashes the source, pack, shared replay helpers and this
script before and after execution. Any captured byte change fails the run. A
missing prerequisite is `NOT_RUN`; a missing product capability is `GAP`; both
remain distinct from a passed journey. A selected `GAP` yields nonzero exit.

These checks establish bounded scripted behavior. They do not measure human
comprehension, prove arbitrary-codebase support, grant owner approval, or close
the full IDE UX acceptance by themselves. Findings belong to the production
owner; the harness must not weaken assertions to hide a product failure.
