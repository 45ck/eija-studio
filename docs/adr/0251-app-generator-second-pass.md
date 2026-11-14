# ADR-0251: One status table, retryable creates and bounded requests in the generated app

* Status: accepted
* Date: 2026-11-14
* Lane: app generator (ADR-0150, ADR-0207, ADR-0249)

## Context and problem statement

The second inspection of the app generator ([record](../quality/inspection-2026-11-14-app-generator-pass-2.md)) found that the API contract and the server kept the status of each refusal in two copies that had drifted, that the signals route was missing from the contract, that a create could not be retried after a lost answer, that values were checked outside the write that used them, that a client could hold a server thread for ever, and that listing and viewing records grew with the database.

## Decision drivers

* The contract must not be able to drift from the server (ADR-0207).
* A request whose answer is lost must be safe to send again, as an action already is (operation ids, ADR-0150).
* A local app must stay answerable whatever one client does.

## Considered options

* One table in `eija_studio.domain.app_http`, read by the generated server and by the contract; an optional operation id on creates; a socket timeout.
* Keep the copies and add a test that compares them.

## Decision outcome

Chosen option: one table. `app_http.REFUSALS` maps each status to its codes, `status_of(code)` answers it, and every code the kernel, the data checks and the app can raise must be in it (a test reads them from the sources). `ROLE_CANNOT_START` and `SEPARATION_DENIED` move from 409 to 403: both are about who is acting. A new `REQUEST_TIMEOUT` (408) answers a request whose body does not arrive within 30 seconds.

Creating a record or a stored object takes an optional `operation_id`. It is bound to the whole request (title, actor, fields, or class, actor, fields), as the kernel binds an action: the same request again returns the first result with status 200 and `duplicate: true`; the id with anything else is `OPERATION_CONFLICT`. An act still requires its id, and the contract now says so. The page sends one id per draft and drops it when the draft or the actor changes.

Values, references and the data digest are checked inside the write. The record list is one query; the model hash is computed once; the audit has an index on the record it belongs to.

### Consequences

* Good: the contract documents every route and code the app answers, and the generated HTTP test checks each refusal's status against the same table.
* Good: a lost create can be retried without a duplicate; a held connection is answered and freed after 30 seconds.
* Bad: the status of `ROLE_CANNOT_START` and `SEPARATION_DENIED` changes for clients of earlier builds; every generated app's files and build subject change, so earlier approved builds are STALE.
* Revisit when: an app is shared by many users, where one write lock and SQLite's commit time matter.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| `http.server` `BaseHTTPRequestHandler.timeout` (standard library) | Used as is | none |
| SQLite expression indexes on `json_extract` (standard library `sqlite3`) | Used as is | none |
| `app_http` status table | A dozen lines of data; no library holds this app's refusal codes | none |
