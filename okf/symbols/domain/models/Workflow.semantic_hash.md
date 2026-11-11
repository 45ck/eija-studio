---
type: Method
title: domain.models.Workflow.semantic_hash
description: 'Order-insensitive fingerprint of the workflow: definition order is non-semantic, identifiers, states, roles and rules are semantic.'
resource: repo://src/eija_studio/domain/models.py#Workflow.semantic_hash
tags:
- symbol
- domain
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Workflow.semantic_hash
  title: domain/models.py
  hash_method: ast-v2
  sha256: 559ae6d9733aea8509ac7c9d5bc8f64d6d0c9646705f17ae430cb56972eca089
description_override: 'Order-insensitive fingerprint of the workflow: definition order is non-semantic, identifiers, states, roles and rules are semantic.'
notes_baseline: eab5996aec1286f9d6c8f0249d81b775b31cb022b17d6aa872cbf610b0f2332e
verified:
- by: process:claude-code
  at: '2026-11-11T13:30:00Z'
  notes_sha256: 09ac2c3c50ca4cfa91f653da45b99c6994824da24586794cf0fe330ea401db71
  sources_sha256: eab5996aec1286f9d6c8f0249d81b775b31cb022b17d6aa872cbf610b0f2332e
---

# domain.models.Workflow.semantic_hash

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`domain/models`](/modules/domain/models.md) |
| Class | [`Workflow`](/symbols/domain/models/Workflow.md) |
| Signature | `def semantic_hash(self) -> str` |
| Code | `repo://src/eija_studio/domain/models.py#Workflow.semantic_hash` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

Sorted states, transitions by id, sorted guards/effects and sorted initiators (when named, ADR-0231) go through [fingerprint](/symbols/domain/models/fingerprint.md). A changed hash makes old [Preview Instances](/language/preview-instance.md) stale (`STALE_INSTANCE`) and invalidates evidence bound to the previous semantic dimension.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
<!-- okf:generated:end links -->
