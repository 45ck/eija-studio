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
  sha256: 848fa179384be96180b66c5b23ab497f60f195d839e0541d00da22ccbf8b4c63
notes_baseline: 152dd850884b548a201955725cd8dc8285b1458766e5a7142c8c614ab841503d
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
* [`GeneratedApps`](/symbols/application/ports/GeneratedApps.md) (class) - Capture exact generated artifacts and observe the existing local conformance checker.
* [`GeneratedSnapshot`](/symbols/application/ports/GeneratedSnapshot.md) (type-alias) - no docstring
* [`GeneratedSubjectValidator`](/symbols/application/ports/GeneratedSubjectValidator.md) (type-alias) - no docstring
* [`IdentityProvider`](/symbols/application/ports/IdentityProvider.md) (type-alias) - no docstring
* [`PlanProposer`](/symbols/application/ports/PlanProposer.md) (class) - Turns a chat request into {summary, meaning, steps: [{transaction, why}]}.
* [`ProposalProvider`](/symbols/application/ports/ProposalProvider.md) (class) - no docstring
* [`ProviderResult`](/symbols/application/ports/ProviderResult.md) (class) - no docstring
* [`ReceiptAuthenticator`](/symbols/application/ports/ReceiptAuthenticator.md) (class) - no docstring
* [`Repository`](/symbols/application/ports/Repository.md) (class) - no docstring
* [`SandboxFactory`](/symbols/application/ports/SandboxFactory.md) (type-alias) - no docstring
* [`SystemDescriber`](/symbols/application/ports/SystemDescriber.md) (class) - Turns a description of an app into {name, record, sketch, fields, reading} for "Describe your app" (ADR-0216).
* [`UnitOfWork`](/symbols/application/ports/UnitOfWork.md) (class) - All mutations on this port commit together or roll back together.

## Internal imports

* [`domain/formal`](/modules/domain/formal.md)
* [`domain/generated_app`](/modules/domain/generated_app.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/transactions`](/modules/domain/transactions.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.formal](/modules/domain/formal.md) - Primitives for per-kind admissibility of formal evidence (ADR-0145, ADR-0146).
* [domain.generated_app](/modules/domain/generated_app.md) - Versioned exact generated-app selection and evidence contracts; no authority is implied by a hash.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.

## Referenced by

* [adapters.generated_apps](/modules/adapters/generated_apps.md) - Retain exact selected app bytes and run their existing generated unittest checker locally.
* [application.describe_system](/modules/application/describe_system.md) - Describe your app (ADR-0216): a new system from one description, like starting an app in Lovable or Replit.
* [application.edit_proposal](/modules/application/edit_proposal.md) - A read-only offline proposal over one captured candidate; owner edits keep their existing boundary.
* [application.formal](/modules/application/formal.md) - Formal evidence in the application layer: seal what an adapter collected, and build the packet view.
* [application.generated_app](/modules/application/generated_app.md) - Shared generation and exact-app evidence operations for the existing kernel and checker.
* [application.plan](/modules/application/plan.md) - Plan mode for the PlayIDE chat (ADR-0156): an AI proposes a change as numbered typed steps; the person accepts or rejects each one and sees what the accepted o…
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; the domain (policy, laws, typed effects) comes from the pack.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [application.service_views](/modules/application/service_views.md) - Read-only Studio projections over the same case, pack and exact-app evidence.
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
* [application.ports.EditProposer](/symbols/application/ports/EditProposer.md) - Offline request resolution only; returns an untrusted transaction and performs no IO or persistence.
* [application.ports.FormalEvidenceSource](/symbols/application/ports/FormalEvidenceSource.md) - Where formal artifacts come from (Docker, Java, z3 or saved reports are adapter prerequisites).
* [application.ports.GeneratedApps](/symbols/application/ports/GeneratedApps.md) - Capture exact generated artifacts and observe the existing local conformance checker.
* [application.ports.GeneratedSnapshot](/symbols/application/ports/GeneratedSnapshot.md) - Type alias `GeneratedSnapshot` in `application/ports`.
* [application.ports.GeneratedSubjectValidator](/symbols/application/ports/GeneratedSubjectValidator.md) - Type alias `GeneratedSubjectValidator` in `application/ports`.
* [application.ports.IdentityProvider](/symbols/application/ports/IdentityProvider.md) - Type alias `IdentityProvider` in `application/ports`.
* [application.ports.PlanProposer](/symbols/application/ports/PlanProposer.md) - Turns a chat request into {summary, meaning, steps: [{transaction, why}]}.
* [application.ports.ProposalProvider](/symbols/application/ports/ProposalProvider.md) - `class ProposalProvider(Protocol)` in `application/ports`.
* [application.ports.ProviderResult](/symbols/application/ports/ProviderResult.md) - `class ProviderResult` in `application/ports`.
* [application.ports.ReceiptAuthenticator](/symbols/application/ports/ReceiptAuthenticator.md) - `class ReceiptAuthenticator(Protocol)` in `application/ports`.
* [application.ports.Repository](/symbols/application/ports/Repository.md) - `class Repository(Protocol)` in `application/ports`.
* [application.ports.SandboxFactory](/symbols/application/ports/SandboxFactory.md) - Type alias `SandboxFactory` in `application/ports`.
* [application.ports.SystemDescriber](/symbols/application/ports/SystemDescriber.md) - Turns a description of an app into {name, record, sketch, fields, reading} for "Describe your app" (ADR-0216).
* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
<!-- okf:generated:end links -->
