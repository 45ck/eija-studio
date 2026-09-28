---
type: Class
title: application.ports.ProposalProvider
description: 'The only door for AI: a provider returns an untrusted Proposal and cannot select meaning, approve or apply.'
resource: repo://src/eija_studio/application/ports.py#ProposalProvider
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#ProposalProvider
  title: application/ports.py
  hash_method: ast-sig-v1
  sha256: 3ea25c091151175504929252f5146fbe03024fbac11d69447d3f5ba1720ecb2b
description_override: 'The only door for AI: a provider returns an untrusted Proposal and cannot select meaning, approve or apply.'
---

# application.ports.ProposalProvider

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class ProposalProvider(Protocol)` |
| Code | `repo://src/eija_studio/application/ports.py#ProposalProvider` |
| Hash | `ast-sig-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `name` | `str` |  |
| `networked` | `bool` |  |

## Protocol members

Structural interface implemented by adapters; not a class to instantiate.

* `def propose(self, request: str, model: Workflow) -> ProviderResult`
* `def doctor(self) -> dict`
<!-- okf:generated:end facts -->

## Notes

Implemented by the offline, OpenRouter and Codex adapters in [adapters.providers](/modules/adapters/providers.md). Networked providers additionally need `--allow-network` and per-request consent.

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.ProviderResult](/symbols/application/ports/ProviderResult.md) - `class ProviderResult` in `application/ports` (the source has no docstring).
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).

## Referenced by

* [Provider integration](/contexts/provider-integration.md) - Owns Vendor transport, authentication delegation, limits and response normalization
* [application.service.Studio](/symbols/application/service/Studio.md) - `class Studio` in `application/service` (the source has no docstring).
<!-- okf:generated:end links -->
