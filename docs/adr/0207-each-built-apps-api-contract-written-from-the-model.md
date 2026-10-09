# ADR-0207: Each built app's API contract, written from the model

* Status: accepted
* Date: 2026-10-09
* Lane: PlayIDE software architecture views (issue #144; follows ADR-0150, ADR-0203 and ADR-0206)

## Context and problem statement

The System lens (ADR-0203) draws each workflow's provided interface as its actions. The Deployment lens (ADR-0206) draws the HTTP routes between the browser and the process. The built app serves them: `GET /api/app`, `GET` and `POST /api/records`, `GET /api/records/{id}`, `POST /api/records/{id}/act` and `GET /api/outbox`. No API contract was shown or exported. A team integrating with a workflow had to read the generated `server.py`.

## Decision drivers

* Write the contract from the same sources the server checks against, so it cannot say more or less than the app does (ADR-0093).
* Use a standard a team's tools already read: OpenAPI 3.1.
* The contract must be checked: against the generated server's routes, against `check_values`, and as valid OpenAPI.

## Considered options

* **Generate an OpenAPI 3.1 document from the pack, the model and the data model (chosen).**
* **Have the generated app serve FastAPI's own OpenAPI.** Rejected: the generated server uses only the standard library on purpose (ADR-0150), and moving it to FastAPI would change every built app.
* **Schemathesis against a running built app.** Not adopted now. It needs a running server per test, and the conformance suite already runs every state × action × actor case against the kernel (ADR-0150). It remains the path for property-based checks over HTTP.

## Decision outcome

Chosen option. `application.api_contract.api_contract(pack, model, data)` is pure, and `POST /api/play/api-contract` returns it for the model on screen.

* The `Fields` schema says what `check_values` accepts for the record class: types, lengths, choices and required attributes, with an empty or null value counted as missing.
* `Action` lists the model's actions, each with the roles that take it. `Actor` lists the pack's fixture directory, which the description says is not authentication.
* The refusals are documented by the status the server sends them with: 400 for a malformed request or a field that breaks the record class, 403 for an actor who may not act, 404 for no such record, and 409 for a step the kernel refuses.

The oracles are in `tests/test_api_contract.py`:

* Every route the generated server answers, read from its `do_GET` and `do_POST`, is in the document, and nothing else is.
* The 400 and 403 codes are the server's own `INVALID` and `FORBIDDEN` sets.
* Every value Hypothesis draws from the `Fields` schema of every shipped pack passes `check_values`. Values the schema refuses are refused by `check_values` too.
* The document validates with `openapi-spec-validator` (the `interop-api` extra). Without that extra, this check is NOT_RUN.

In PlayIDE, the Deployment lens's Python process and the open workflow in the System lens offer **Download the API contract (OpenAPI 3.1)**.

### Consequences

* Good: an integrating team gets a standard contract that is checked against the server and the record class.
* Bad: response bodies are described as objects and arrays, not field by field. The record view's shape is the generated service's, and is not yet a typed contract.
* Bad: the 409 codes are examples. The kernel's full refusal vocabulary is not a closed list the contract can enumerate.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| OpenAPI 3.1 specification (Apache-2.0) | Adopted as the format | — |
| openapi-spec-validator 0.9.0 (Apache-2.0) | Adopted as the oracle, in the `interop-api` extra | — |
| Hypothesis and hypothesis-jsonschema (MPL-2.0, existing `testing` extra) | Adopted to draw values from the schema | — |
| Schemathesis (MIT) | Needs a running server per test; the kernel conformance suite already covers every case | Property-based HTTP checks against a built app |
