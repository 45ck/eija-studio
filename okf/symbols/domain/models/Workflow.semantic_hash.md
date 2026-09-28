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
  sha256: 8320b3ba427e12549b9120c151630a677b0596d84ff486bc11afa8f53b340786
description_override: 'Order-insensitive fingerprint of the workflow: definition order is non-semantic, identifiers, states, roles and rules are semantic.'
notes_baseline: 870f5e36162952709a48b7bb1c919a06b468ea6145b26789815e62a00eddb606
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

Sorted states, transitions by id and sorted guards/effects go through [fingerprint](/symbols/domain/models/fingerprint.md). A changed hash makes old [Preview Instances](/language/preview-instance.md) stale (`STALE_INSTANCE`) and invalidates evidence bound to the previous semantic dimension.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
<!-- okf:generated:end links -->
