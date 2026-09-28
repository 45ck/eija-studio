---
type: Bounded Context
title: Provider integration
description: Owns Vendor transport, authentication delegation, limits and response normalization
resource: repo://docs/architecture/ARCHITECTURE.md#provider-integration
tags:
- ddd
- context-map
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#provider-integration
  title: ARCHITECTURE.md
  hash_method: md-table-row-v1
  sha256: 654efaf4bb964c72e1d0851dd63954e61fc8e6f958739d22a63a6af8eca8cd9c
notes_baseline: 13e09060c9aa3e899cd9ec3c09f68962417937fbd5c5611feae807449f913ef6
---

# Provider integration

<!-- okf:generated:begin facts -->
## Owns

Vendor transport, authentication delegation, limits and response normalization

## Published contracts

* [`ProposalProvider`](/symbols/application/ports/ProposalProvider.md)
* [`ProviderResult`](/symbols/application/ports/ProviderResult.md)

## Implementation

* [`adapters/providers.py`](/modules/adapters/providers.md)

Source: context map row `repo://docs/architecture/ARCHITECTURE.md#provider-integration`. These are responsibility boundaries inside a modular monolith, not separately deployed services.
<!-- okf:generated:end facts -->

## Notes

Vendor transport is isolated behind the [ProposalProvider](/symbols/application/ports/ProposalProvider.md) port; nothing in domain or application knows an SDK.

<!-- okf:generated:begin links -->
## Published contracts

* [application.ports.ProposalProvider](/symbols/application/ports/ProposalProvider.md) - `class ProposalProvider(Protocol)` in `application/ports`.
* [application.ports.ProviderResult](/symbols/application/ports/ProviderResult.md) - `class ProviderResult` in `application/ports`.

## Implementing modules

* [adapters.providers](/modules/adapters/providers.md) - Untrusted proposal adapters.
<!-- okf:generated:end links -->
