---
type: Module
title: application.ports
description: Application-owned ports.
resource: repo://src/eija_studio/application/ports.py
tags:
- module
- application
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py
  title: application/ports.py
  hash_method: ast-api-v1
  sha256: 7bae93c928e58cb767ab07ade40f7012f9be838f29843f8d5f7ccb629d3b457a
notes_baseline: a535b927b1344fc7ba55f44937bd28586ce1654443ad5223f54fb6aa8a526cac
---

# application.ports

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | application |
| Code | `repo://src/eija_studio/application/ports.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Application-owned ports. Domain/application never depend on vendor or SQL types.
~~~

## Public symbols

* [`EditProposer`](/symbols/application/ports/EditProposer.md) (class) - Offline request resolution only; returns an untrusted transaction and performs no IO or persistence.
* [`FormalEvidenceSource`](/symbols/application/ports/FormalEvidenceSource.md) (class) - Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).
* [`IdentityProvider`](/symbols/application/ports/IdentityProvider.md) (type-alias) - no docstring
* [`ProposalProvider`](/symbols/application/ports/ProposalProvider.md) (class) - no docstring
* [`ProviderResult`](/symbols/application/ports/ProviderResult.md) (class) - no docstring
* [`ReceiptAuthenticator`](/symbols/application/ports/ReceiptAuthenticator.md) (class) - no docstring
* [`Repository`](/symbols/application/ports/Repository.md) (class) - no docstring
* [`SandboxFactory`](/symbols/application/ports/SandboxFactory.md) (type-alias) - no docstring
* [`UnitOfWork`](/symbols/application/ports/UnitOfWork.md) (class) - All mutations on this port commit together or roll back together.

## Internal imports

* [`domain/formal`](/modules/domain/formal.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.formal](/modules/domain/formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [application.edit_proposal](/modules/application/edit_proposal.md) - A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
* [application.ports.EditProposer](/symbols/application/ports/EditProposer.md) - Offline request resolution only; returns an untrusted transaction and performs no IO or persistence.
* [application.ports.FormalEvidenceSource](/symbols/application/ports/FormalEvidenceSource.md) - Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).
* [application.ports.IdentityProvider](/symbols/application/ports/IdentityProvider.md) - Type alias `IdentityProvider` in `application/ports`.
* [application.ports.ProposalProvider](/symbols/application/ports/ProposalProvider.md) - `class ProposalProvider(Protocol)` in `application/ports`.
* [application.ports.ProviderResult](/symbols/application/ports/ProviderResult.md) - `class ProviderResult` in `application/ports`.
* [application.ports.ReceiptAuthenticator](/symbols/application/ports/ReceiptAuthenticator.md) - `class ReceiptAuthenticator(Protocol)` in `application/ports`.
* [application.ports.Repository](/symbols/application/ports/Repository.md) - `class Repository(Protocol)` in `application/ports`.
* [application.ports.SandboxFactory](/symbols/application/ports/SandboxFactory.md) - Type alias `SandboxFactory` in `application/ports`.
* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
<!-- okf:generated:end links -->
