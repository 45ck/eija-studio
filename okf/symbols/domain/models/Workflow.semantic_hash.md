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
  sha256: 1990fd03392fecce24daf35c5db3689d125d00010fcb9d7cae899830f2cf1126
description_override: 'Order-insensitive fingerprint of the workflow: definition order is non-semantic, identifiers, states, roles and rules are semantic.'
notes_baseline: a0bc00921d30ead8ee369828f12cc7909edcee8fea9902b80b608af20b18302c
verified:
- by: process:claude-code
  at: '2026-11-11T13:30:00Z'
  notes_sha256: 09ac2c3c50ca4cfa91f653da45b99c6994824da24586794cf0fe330ea401db71
  sources_sha256: eab5996aec1286f9d6c8f0249d81b775b31cb022b17d6aa872cbf610b0f2332e
- by: process:claude-code
  at: '2026-11-11T22:00:00Z'
  notes_sha256: f64f5f2801fbd3418f505054d7ad87c365301d1d6d73b99ee15a5735df5f7583
  sources_sha256: c9199bd4bb2e922d493c5bae9c4aabdfced54805f28524b40a96d1e44acfdd29
- by: process:claude-code
  at: '2026-11-12T03:40:00Z'
  notes_sha256: 37ffe83169f82f47763b5d6d8e5320acadad43bb46d39cbe66d42123b33b761d
  sources_sha256: a0bc00921d30ead8ee369828f12cc7909edcee8fea9902b80b608af20b18302c
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

Sorted states, transitions by id, sorted guards/effects and sorted initiators (when named, ADR-0231) each transition's sorted value guards (when it has them, ADR-0234) and the composite states sorted by name with sorted children (when there are any, ADR-0238) go through [fingerprint](/symbols/domain/models/fingerprint.md). A changed hash makes old [Preview Instances](/language/preview-instance.md) stale (`STALE_INSTANCE`) and invalidates evidence bound to the previous semantic dimension.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.canonical](/symbols/domain/models/canonical.md) - `def canonical(value: Any) -> str` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
<!-- okf:generated:end links -->
