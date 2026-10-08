---
type: Class
title: domain.pack.ProposalRule
description: 'Offline fixture: when the lower-cased request contains every ``all`` word and at least one ``any`` word.'
resource: repo://src/eija_studio/domain/pack.py#ProposalRule
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#ProposalRule
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: 2af129662b67023f5c23cf4e2191647363a47477116bee86f3d7a5dd39907184
notes_baseline: bf398275753bde62a1842cff806c66889e4fbc427b34df561d7ef968ef4dfb48
---

# domain.pack.ProposalRule

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class ProposalRule(Contract)` |
| Code | `repo://src/eija_studio/domain/pack.py#ProposalRule` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Offline fixture: when the lower-cased request contains every ``all`` word and at least one ``any`` word.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `all` | `tuple[str, ...]` | `()` |
| `any` | `tuple[str, ...]` | `()` |
| `alternatives` | `tuple[Alternative, ...]` | `Field(min_length=1, max_length=4)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Alternative](/symbols/domain/models/Alternative.md) - `class Alternative(Contract)` in `domain/models`.
* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.

## Referenced by

* [domain.pack.Proposals](/symbols/domain/pack/Proposals.md) - `class Proposals(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
