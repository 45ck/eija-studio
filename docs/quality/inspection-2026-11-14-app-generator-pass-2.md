# Inspection of the app generator, pass 2, 14 November 2026

A second, deeper pass over the generated app after [pass 1](inspection-2026-11-13-app-generator.md), at the level of the design rather than single lines. Every sector pack (11) was built, served and walked in a real browser: a record created through the page, then each allowed action taken until none was left. All 11 walked without a refusal. The generated service was benchmarked with 5,000 records. The API contract (ADR-0207) was compared with what the server actually answers, route by route and code by code. Newer kernel features were checked against the generator: `UNDECLARED_ROLE` (#258) and `LINKED_LIFECYCLE_CONFLICT` (#257) are policy checks, so a build is refused with `POLICY_BLOCKED` before an app exists; composite states (ADR-0240) are flat in the built app by design.

Checklist, on top of pass 1's:

1. One fact kept in two places (a table copied between the server and the contract).
2. A request that can be lost in transit and cannot be retried safely.
3. A read of shared state outside the transaction that acts on it.
4. A resource a client can hold without limit.
5. Work that grows with the size of the database on every request.

Decision record: [ADR-0251](../adr/0251-app-generator-second-pass.md).

## Defects

| # | Severity | Where | Defect | Fix and regression test |
|---|---|---|---|---|
| H1 | Major | `api_contract.py`, `server.py.tmpl` | The HTTP status of each refusal was kept twice, as the server's `FORBIDDEN`/`INVALID` sets and the contract's `REFUSALS`, and they had drifted: the contract left out 13 codes the app answers (`ACTION_DENIED`, `OPERATION_CONFLICT`, `VALUE_GUARD_DENIED`, `TIMER_NOT_DUE`, `SEPARATION_DENIED`, `LINKED_OBJECT_REFUSED`, `SIGNAL_NOT_ACCEPTED`, `EFFECT_DENIED`, `INVALID_STATE`, `ROLE_CANNOT_START`, `HOST_DENIED`, `INTERNAL_ERROR` and the new `REQUEST_TIMEOUT`), and said a create is refused only 400 or 403 while `ROLE_CANNOT_START` came back 409. | One table, `eija_studio.domain.app_http`, read by both. `ROLE_CANNOT_START` and `SEPARATION_DENIED` are 403 (who is acting), every operation documents 403 and 500. `test_the_server_and_the_contract_read_one_status_table`, `test_every_code_the_app_can_refuse_with_has_a_documented_status`, and the generated HTTP test now checks each refusal's status. |
| H2 | Major | `api_contract.py`, `tests/test_api_contract.py` | `POST /api/signals` (ADR-0242) was missing from the contract, and the drift test's route parser could not see it (`url.path == '/api/signals' and MODEL.receives`), so the test could not fail for it. | The route is documented, with a `Signal` schema, for a model that receives a signal; the parser reads the condition; the drift test runs on library-fines too. |
| H3 | Major | `service.py.tmpl` `create`, `create_object` | A create could not be retried. When its answer was lost the page could only say "review the latest records before trying again", and sending it again made a second record. | An optional `operation_id`, bound to the whole request as the kernel binds an action's: the same request again answers the first record (200, `duplicate: true`), anything else under that id is `OPERATION_CONFLICT`. The page sends one id per draft. `test_a_create_sent_again_after_a_lost_answer_makes_one_record`, `test_an_object_sent_again_after_a_lost_answer_is_stored_once`, and in the generated HTTP test. |
| H4 | Major | `service.py.tmpl` `create`, `receive`, `act` | The record's values, including whether a referenced object exists, were checked before the write lock was taken, on the connection other requests write through. A record could keep the id of an object whose write was then rolled back. `act` read the record's data digest the same way. | Checked inside the write. `test_a_record_cannot_refer_to_an_object_whose_write_rolls_back` |
| H5 | Minor | `server.py.tmpl` | No socket timeout. A client that sent headers promising a body and never sent it held a server thread for ever (still open after 40 s); enough of them exhaust the process. | `timeout = 30`; the request is answered `408 REQUEST_TIMEOUT` and the thread is freed. `test_a_request_that_never_sends_its_body_is_answered_and_its_thread_freed` |
| H6 | Minor | `service.py.tmpl` `records`, `history` | The list ran one query per record and hashed the whole model per record (`semantic_hash` is a property that recomputes); each view scanned every record's audit entries. With 5,000 records: list 0.395 s, view 0.02 s, both growing with the database. | One query, the hash computed once, an index on the audit entry's record (and on `acts.record_id`, `objects.class`). List 0.03 s, view under 0.001 s. `test_the_record_list_is_one_query_and_history_uses_an_index` |
| H7 | Minor | `react-source/controller.js` `cleanValues` | `Number("1e999")` is `Infinity`, which JSON writes as `null`: an optional number was dropped without a word, a required one reported as missing instead of as not a number. | A number the browser cannot hold is sent as typed, and the server refuses it `FIELD_TYPE`. `test_a_number_the_browser_cannot_hold_is_sent_as_typed_not_as_null` |
| H8 | Minor | `server.py.tmpl` | Every page load asked for `/favicon.ico` and logged a 404 in the console of all 11 apps. | `204 No Content`. `test_the_browser_icon_request_is_not_an_error` |

All eight are fixed. The 13 tests in `tests/test_appgen_inspection_pass2.py` were run against `main` first: 10 failed (the other three are statuses `main` already got right, kept as a guard).

## Seeded faults

Two faults were added to `verification/conformance/divergence.py` `CODE` so the harness keeps checking the new behaviour: "a create sent again makes a second record" and "refusals answered with one status". Five existing faults were re-pointed at the changed template lines; "history shows every record's steps" now drops the SQL filter that replaced the loop's check (on its first run it was MISSED because the old check had become redundant).

## Before and after (HTTP, library-loan)

| Request | Before | After |
|---|---|---|
| `GET /favicon.ico` | 404 `NOT_FOUND` | 204 |
| `POST /api/records` twice with one `operation_id` | 201, 201, two records | 201, 200, one record |
| headers promise 50 bytes, body never sent | connection still held after 40 s | `408 REQUEST_TIMEOUT` after 30 s |
| list 5,000 records | 0.395 s | 0.03 s |
| view one record among 5,000 | 0.02 s | under 0.001 s |

## Checked and not defects

* Cross-origin reads: blocked by the browser's same-origin policy, and writes need `Content-Type: application/json`, which a form cannot send without a preflight the app never answers.
* `UNDECLARED_ROLE`, `LINKED_LIFECYCLE_CONFLICT`: refused at build time by the policy, so no app carries them.
* Composite states: flat in the built app by design (ADR-0240).

## Design limits, logged not fixed

* A record made under an earlier model or data model stays stranded (every action refused) until a migration exists; there is no migration path yet.
* Two processes started on one database at the same moment could both try the `ALTER TABLE` migrations; the app is one local process, so this is not reachable from `run.py`.
* Writes are serialised by one lock on one connection, about 1 ms each (SQLite's commit). Enough for a local app; revisit for a shared one.
