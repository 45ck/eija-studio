# Re-inspection of the pull requests merged from 11 November 2026, 13 November 2026

A Fagan-style inspection of what went in fast under auto-merge: #217 (hosted CI) through #252. Each merged diff was
read against its pull request, its ADR and its tests, every Codex review finding on #217 to #231 was checked against the
code, and the features were tried together, since each PR was reviewed alone. The companion log for open PRs and the
Codex threads on #232 to #248 is [inspection-2026-11-13-pull-requests.md](inspection-2026-11-13-pull-requests.md).
Severity: **major** changes behaviour a user or client can see; **minor** is wording, naming or a doc slip.

## What was inspected

| Work product | Result |
|---|---|
| #217 hosted CI (ADR-0228) | Workflows match the ADR. One minor stale comment, M5. |
| #219 OpenAI provider, intent eval, live chat plan mode (ADR-0229, ADR-0230) | Both Codex findings (negative call cap, offline provenance for exact phrases) are fixed in 58e8a5a, though their threads were left open on GitHub. No new defect. |
| #223 initiators (ADR-0231) | Both Codex findings fixed (hash order, creation-only initiators drawn). One major defect, M4: UML exports drop initiators silently. |
| #227 one action from several states (ADR-0232) | Both Codex findings fixed. One major defect, M1, introduced by the later #232 and #245. |
| #228 separation of duties (ADR-0233) | No Codex findings; no defect found. |
| #229 value guards (ADR-0234), #230 built associations (ADR-0235), #231 docs | All five Codex findings fixed with tests. Value guards also take part in M1. |
| #232 to #248 kernel items, V&V and hardening | Feature interactions tried: two defects, M2 (#245) and M3 (#237 against the built app). |
| #252 operation id on actions | Correct. |

## Defect log

| ID | Severity | Location | Defect | Status |
|---|---|---|---|---|
| M1 | major | `src/eija_studio/domain/transactions.py`, `_add_transition` | ADR-0232 lets one action leave several states. Adding another source declared the new transition from the pack's action catalog, which has no time event, value guard or step on a linked object. For an action that carries one (`EscalateStale after(2 days)` in refund-desk, `OpenWindow / target.lock` in ai-ops, any `[amount > 500]`), the new transition differed from its siblings and the edit was refused as "The edit would make the workflow incoherent". Drawing a second arrow for such an action in PlayIDE, or importing one from UML, failed with no reason. #232 and #245 broke #227 here. | Fixed: another source copies what the action's transitions share; a different target or role is refused and named. |
| M2 | major | `src/eija_studio/domain/models.py` (`Workflow.objects`), built app `LIFECYCLES` | Two links to one class (`target` and `canary`, both `Microservice`) could declare different lifecycles. An object has one state, so the built app started every object in the first lifecycle's initial state. The build then failed 8 of its own conformance tests (`LINKED_OBJECT_REFUSED` where the kernel committed) with no named cause, although the kernel and PlayIDE accepted the model. | Fixed: the policy refuses it as `LINKED_LIFECYCLE_CONFLICT:<class>`, so PlayIDE, `eija build` and the runtime name it. Links to one class with the same lifecycle are still allowed. |
| M3 | minor | `src/eija_studio/resources/appgen/server.py.tmpl`, `POST /api/records/{id}/act` | ADR-0238 made the kernel read `expected_version: 1.0` as the JSON integer its contract allows, but the built app's handler kept its own `isinstance(int)` check and answered `400 BAD_REQUEST`. | Fixed: a whole float is read as an int; `0.5`, `"0"` and `true` are still refused. |
| M4 | major | `src/eija_studio/application/interop/model.py`, `_guards_not_carried` | A UML export of a model that names who may start a record wrote nothing about it and did not list it as not carried, unlike value guards, time events, composites, lifecycles and signals. A round trip through another tool lost the rule without warning. | Fixed: every format lists `who may start a record: ‹roles› (ADR-0231)` under `not_carried`. |
| M5 | minor | `.github/workflows/test.yml` | The header still said hosted CI is unavailable and manual-only (ADR-0017), contradicting ADR-0228. | Fixed: it says what the workflow runs and points to `quality.yml`. |

All five are fixed in one pull request, with `tests/test_merged_pr_inspection.py` as the regression suite.

## Checked and found correct

- The kernel's signal delivery binds the record's values but does not store them; the built app stores them. That is what ADR-0242 says.
- The app oracle's ordinary cases wait the longest time event and put linked objects where a run of the record leaves them, so value, timer and linked cases on a transition that also has the other features are not vacuous.
- SCXML hoisting of a timed action onto a composite still checks `elapsed` per leaf, as the kernel does.
- `keyed` diffs an action from several states by source, so diagrams and ripple see each one.
- The intent eval refuses a negative call cap before any call, and grades a supported pick for an off-topic request as wrong rather than substituted, by design.

## Before and after

`tests/test_merged_pr_inspection.py` on `main` (22298bc) and on this branch:

```text
before: 11 failed, 1 passed
  FAILED test_m1_a_timed_action_can_leave_another_state
  FAILED test_m1_an_action_on_a_linked_object_can_leave_another_state
  FAILED test_m1_a_value_guarded_action_can_leave_another_state
  FAILED test_m1_an_action_whose_guards_were_edited_can_leave_another_state
  FAILED test_m1_another_source_with_a_different_target_is_refused_and_named
  FAILED test_m2_two_links_to_one_class_may_not_declare_different_lifecycles
  FAILED test_m3_the_built_app_reads_a_whole_float_version_as_a_json_integer
  FAILED test_m4_an_export_lists_who_may_start_a_record_as_not_carried[plantuml|mermaid|xmi|drawio]
after:  12 passed
```

**M1**, adding a second source to an existing action:

```text
before  refund-desk  EscalateStale after(2 days) from Requested  -> REFUSED EDIT_INVALID The edit would make the workflow incoherent
        ai-ops       OpenWindow / target.lock from Opened        -> REFUSED EDIT_INVALID The edit would make the workflow incoherent
after   refund-desk  EscalateStale from Requested -> OK; sources ('AwaitingApproval', 'Requested')
        ai-ops       OpenWindow from Opened      -> OK; sources ('Scheduled', 'Opened')
```

**M2**, ai-ops with a second link `canary` to `Microservice` and a `Cold`/`Warm` lifecycle:

```text
before  model accepted; eija build -> conformance FAIL (failures=8)
        AssertionError: {'outcome': 'REFUSED', 'code': 'LINKED_OBJECT_REFUSED'} != {'outcome': 'COMMITTED', ...}
after   check_policy -> ['LINKED_LIFECYCLE_CONFLICT:Microservice']; eija build -> POLICY_BLOCKED, no app written
```

**M3**, `POST /api/records/{id}/act` with `"expected_version": 0.0` on a built library-loan app:

```text
before  400 {"code": "BAD_REQUEST", "message": "expected_version must be an integer"}
after   200 {"committed": true, ...}     (0.5, "0" and true: still 400 BAD_REQUEST)
```

**M4**, export of library-loan with `initiators: ["Clerk"]`:

```text
before  plantuml/mermaid/xmi/drawio: initiators in file False, listed as not carried False
after   plantuml/mermaid/xmi/drawio: not_carried includes "who may start a record: Clerk (ADR-0231)"
```
