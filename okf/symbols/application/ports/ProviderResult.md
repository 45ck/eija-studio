---
type: Class
title: application.ports.ProviderResult
description: '`class ProviderResult` in `application/ports` (the source has no docstring).'
resource: repo://src/eija_studio/application/ports.py#ProviderResult
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/ports.py#ProviderResult
  title: application/ports.py
  hash_method: ast-sig-v1
  sha256: c4d048c4468a37042391c07cf3e0100c0eaebcf8df2e802efef9df7189d0f0a8
---

# application.ports.ProviderResult

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/ports`](/modules/application/ports.md) |
| Signature | `class ProviderResult` |
| Code | `repo://src/eija_studio/application/ports.py#ProviderResult` |
| Hash | `ast-sig-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `proposal` | `Proposal` |  |
| `provider` | `str` |  |
| `model` | `str` |  |
| `usage` | `dict[str, Any]` |  |
| `live` | `bool` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Proposal](/symbols/domain/models/Proposal.md) - `class Proposal(Contract)` in `domain/models` (the source has no docstring).

## Referenced by

* [Provider integration](/contexts/provider-integration.md) - Owns Vendor transport, authentication delegation, limits and response normalization
* [application.ports.ProposalProvider](/symbols/application/ports/ProposalProvider.md) - `class ProposalProvider(Protocol)` in `application/ports` (the source has no docstring).
<!-- okf:generated:end links -->
