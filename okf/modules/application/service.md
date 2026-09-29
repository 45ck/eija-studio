---
type: Module
title: application.service
description: Module `application/service` (no module docstring).
resource: repo://src/eija_studio/application/service.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py
  title: application/service.py
  hash_method: ast-api-v1
  sha256: 7647e6a26939a15d6be4eca8e360c3f1e7cbad5579f061733d337c022fe86f70
notes_baseline: 29aa04116a8048307552fc1c8bc63d5348b12136cfcb6a1ea379995648283ecc
---

# application.service

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/service.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

_The source carries no module docstring._

## Public symbols

* [`Studio`](/symbols/application/service/Studio.md) (class) - no docstring
* [`now`](/symbols/application/service/now.md) (function) - no docstring

## Internal imports

* [`application/compiler`](/modules/application/compiler.md)
* [`application/formal`](/modules/application/formal.md)
* [`application/ports`](/modules/application/ports.md)
* [`application/runtime`](/modules/application/runtime.md)
* [`application/verifier`](/modules/application/verifier.md)
* [`domain/change_case`](/modules/domain/change_case.md)
* [`domain/formal`](/modules/domain/formal.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.ports](/modules/application/ports.md) - Application-owned ports.
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; domain-specific policy stays in domain.policy.
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
* [domain.change_case](/modules/domain/change_case.md) - Module `domain/change_case` (no module docstring).
* [domain.formal](/modules/domain/formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.policy](/modules/domain/policy.md) - Protected excursion policy.

## Referenced by

* [Authoring](/contexts/authoring.md) - Owns Requested intent, alternatives, explicit selection, candidate and edits
* [Governance](/contexts/governance.md) - Owns Local capabilities, exact-revision acknowledgement, active baseline version
* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
* [interfaces.mcp_server](/modules/interfaces/mcp_server.md) - MCP (Model Context Protocol) adapter: the agent-facing face of EIJA Studio.
* [application.service.Studio.apply](/symbols/application/service/Studio.apply.md) - `def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.approve](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknow…` in `application/service`.
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.discard](/symbols/application/service/Studio.discard.md) - `def discard(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.edit](/symbols/application/service/Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.execute](/symbols/application/service/Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] | None=None) -> dict[st…` in `application/service`.
* [application.service.Studio.export](/symbols/application/service/Studio.export.md) - `def export(self, case_id: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [application.service.Studio.layout](/symbols/application/service/Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service`.
* [application.service.Studio.propose](/symbols/application/service/Studio.propose.md) - `def propose(self, case_id: str, expected: int, *, consent: bool=False) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.reset_preview](/symbols/application/service/Studio.reset_preview.md) - `def reset_preview(self, case_id: str, expected: int, state: str | None=None) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.save](/symbols/application/service/Studio.save.md) - `def save(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.select](/symbols/application/service/Studio.select.md) - `def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.view](/symbols/application/service/Studio.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` in `application/service`.
* [application.service.Studio.workflows](/symbols/application/service/Studio.workflows.md) - Baseline and candidate of a case, for read-only projections (diagrams).
* [application.service.now](/symbols/application/service/now.md) - `def now() -> str` in `application/service`.
<!-- okf:generated:end links -->
