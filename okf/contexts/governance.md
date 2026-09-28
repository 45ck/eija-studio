---
type: Bounded Context
title: Governance
description: Owns Local capabilities, exact-revision acknowledgement, active baseline version
resource: repo://docs/architecture/ARCHITECTURE.md#governance
tags:
- ddd
- context-map
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#governance
  title: ARCHITECTURE.md
  hash_method: md-table-row-v1
  sha256: e73c35e4bb5b7d52c47cf2444d30810d7453b0fb4af9dd766bc3f19c5234c14b
---

# Governance

<!-- okf:generated:begin facts -->
## Owns

Local capabilities, exact-revision acknowledgement, active baseline version

## Published contracts

* [`Principal`](/symbols/domain/models/Principal.md)
* local decision (no public symbol of this name)

## Implementation

* [`domain/models.py`](/modules/domain/models.md)
* [`application/service.py`](/modules/application/service.md)

Source: context map row `repo://docs/architecture/ARCHITECTURE.md#governance`. These are responsibility boundaries inside a modular monolith, not separately deployed services.
<!-- okf:generated:end facts -->

## Notes

Capabilities, exact-revision acknowledgement and the active baseline version. Single local owner only; multi-user operation is out of scope.

<!-- okf:generated:begin links -->
## Published contracts

* [domain.models.Principal](/symbols/domain/models/Principal.md) - `class Principal(Contract)` in `domain/models` (the source has no docstring).

## Implementing modules

* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
<!-- okf:generated:end links -->
