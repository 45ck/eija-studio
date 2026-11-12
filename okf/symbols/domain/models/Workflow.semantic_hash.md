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
  sha256: 25de32fdec1f4058437ca03af07b7cb4d16d8d09417ed0e322d34001e8597f7f
description_override: 'Order-insensitive fingerprint of the workflow: definition order is non-semantic, identifiers, states, roles and rules are semantic.'
notes_baseline: a48cf11a554eedd4c94aa895368be1ae7b8caed1aecea07f26b0e8242b257393
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
- by: process:claude-code
  at: '2026-11-12T04:00:08Z'
  notes_sha256: dfd7749be4145ba47169e68f5fb0eddfdc3f192ebc4e31f8acfee71acd406048
  sources_sha256: ec286abdad3950e65157f6f2ae8e5da4fec1147b3ee65940c3f887177db14e1a
- by: process:claude-code
  at: '2026-11-12T04:32:06Z'
  notes_sha256: 51f89c3c239a1c675173761b1821edb93ed3bdeca6abaf657cd077232d21d243
  sources_sha256: a48cf11a554eedd4c94aa895368be1ae7b8caed1aecea07f26b0e8242b257393
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

Sorted states, transitions by id, sorted guards/effects and sorted initiators (when named, ADR-0231) each transition's sorted value guards (when it has them, ADR-0234) and the composite states sorted by name with sorted children (when there are any, ADR-0240), and the linked-object lifecycles sorted by link with sorted moves plus each transition's steps on them (when there are any, ADR-0241), and the received signals as a set (when there are any, ADR-0242) go through [fingerprint](/symbols/domain/models/fingerprint.md). A changed hash makes old [Preview Instances](/language/preview-instance.md) stale (`STALE_INSTANCE`) and invalidates evidence bound to the previous semantic dimension.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.canonical](/symbols/domain/models/canonical.md) - `def canonical(value: Any) -> str` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
<!-- okf:generated:end links -->
