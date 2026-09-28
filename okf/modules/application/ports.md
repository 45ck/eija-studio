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
  sha256: be29fd605269558dcf700e3c8c892ebc600d813abe795e331cb9504d043fbdfd
notes_baseline: 70e2a3c117393eb12033b14cc2f844fa9f9c884e9d2ced0b6072da5b3d0b5dfe
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

* [`IdentityProvider`](/symbols/application/ports/IdentityProvider.md) (type-alias) - no docstring
* [`ProposalProvider`](/symbols/application/ports/ProposalProvider.md) (class) - no docstring
* [`ProviderResult`](/symbols/application/ports/ProviderResult.md) (class) - no docstring
* [`ReceiptAuthenticator`](/symbols/application/ports/ReceiptAuthenticator.md) (class) - no docstring
* [`Repository`](/symbols/application/ports/Repository.md) (class) - no docstring
* [`SandboxFactory`](/symbols/application/ports/SandboxFactory.md) (type-alias) - no docstring
* [`UnitOfWork`](/symbols/application/ports/UnitOfWork.md) (class) - All mutations on this port commit together or roll back together.

## Internal imports

* [`domain/models`](/modules/domain/models.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).

## Referenced by

* [adapters.providers](/modules/adapters/providers.md) - Untrusted proposal adapters.
* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; domain-specific policy stays in domain.policy.
* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
* [application.ports.IdentityProvider](/symbols/application/ports/IdentityProvider.md) - Type alias `IdentityProvider` in `application/ports`.
* [application.ports.ProposalProvider](/symbols/application/ports/ProposalProvider.md) - `class ProposalProvider(Protocol)` in `application/ports`.
* [application.ports.ProviderResult](/symbols/application/ports/ProviderResult.md) - `class ProviderResult` in `application/ports`.
* [application.ports.ReceiptAuthenticator](/symbols/application/ports/ReceiptAuthenticator.md) - `class ReceiptAuthenticator(Protocol)` in `application/ports`.
* [application.ports.Repository](/symbols/application/ports/Repository.md) - `class Repository(Protocol)` in `application/ports`.
* [application.ports.SandboxFactory](/symbols/application/ports/SandboxFactory.md) - Type alias `SandboxFactory` in `application/ports`.
* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
<!-- okf:generated:end links -->
