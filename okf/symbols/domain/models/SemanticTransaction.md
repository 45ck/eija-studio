---
type: Class
title: domain.models.SemanticTransaction
description: 'One typed business-meaning edit: enable recommendation or set the registrar rejection source.'
resource: repo://src/eija_studio/domain/models.py#SemanticTransaction
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#SemanticTransaction
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: 7d70a888f1a198ac3b8ffc197dc001c643f1ae22ed9af154a3046b82d14acfcf
description_override: 'One typed business-meaning edit: enable recommendation or set the registrar rejection source.'
notes_baseline: 6e702f86b1f5452281fdc9268c22c00f0944ba4c010e792aca26b71675bef728
verified:
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: 448cfc6039aadb8c51542e6886ed1a8fe21f8503b21cb1d20ec0de761da2558a
  sources_sha256: 6e702f86b1f5452281fdc9268c22c00f0944ba4c010e792aca26b71675bef728
---

# domain.models.SemanticTransaction

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class SemanticTransaction(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#SemanticTransaction` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
DEPRECATED closed vocabulary, superseded by the open one in ``domain.transactions`` (WBS 1.3).

Kept for one caller only: verification/bend/bend_generate.py, whose bytes the committed Bend proof binds
(changing them turns that evidence non-PASS until Docker regenerates it, WBS 1.4). ``policy.apply_transaction``
reads it as "apply the pack's first supported meaning". The service, HTTP, pack meanings and stored cases never
accept it: a stored case holding one is refused with ``CASE_SCHEMA_OLD``.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['enable_recommendation']` |  |
<!-- okf:generated:end facts -->

## Notes

**Deprecated.** The closed pre-pack vocabulary. The open vocabulary is the discriminated union in `domain/transactions.py` ([Semantic Transaction](/language/semantic-transaction.md)). This class survives only because `verification/bend/bend_generate.py` builds one and the committed Bend proof binds that file's bytes; `policy.apply_transaction` reads it as "apply the pack's first supported meaning". The service, HTTP, pack meanings and stored cases never accept it. WBS 1.4 removes it.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [Authoring](/contexts/authoring.md) - Owns Requested intent, alternatives, explicit selection, candidate and edits
* [Semantic Transaction](/language/semantic-transaction.md) - One typed business-meaning edit.
* [domain.policy.apply_transaction](/symbols/domain/policy/apply_transaction.md) - Apply one transaction (policy-checked).
<!-- okf:generated:end links -->
