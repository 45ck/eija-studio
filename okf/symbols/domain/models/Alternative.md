---
type: Class
title: domain.models.Alternative
description: '`class Alternative(Contract)` in `domain/models`.'
resource: repo://src/eija_studio/domain/models.py#Alternative
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/models.py#Alternative
  title: domain/models.py
  hash_method: ast-sig-v1
  sha256: b6771e96505d7b355cfcc07c2a8e56b04dbdd80028e70987f2d3c09dd96edbc8
notes_baseline: 972e90642b43fd9758fd2694e526b9ae99dca75176dcad7c2aee12686d81beb2
---

# domain.models.Alternative

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/models`](/modules/domain/models.md) |
| Signature | `class Alternative(Contract)` |
| Code | `repo://src/eija_studio/domain/models.py#Alternative` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

_The source carries no docstring._

## Fields

| Field | Annotation | Default |
|---|---|---|
| `interpretation` | `str` | `Field(pattern=MEANING_ID)` |
| `explanation` | `str` | `Field(min_length=1, max_length=1600)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Contract](/symbols/domain/models/Contract.md) - `class Contract(BaseModel)` in `domain/models`.
* [domain.models.MEANING_ID](/symbols/domain/models/MEANING_ID.md) - Constant `MEANING_ID` in `domain/models`.

## Referenced by

* [application.diagrams.CONTRACTS](/symbols/application/diagrams/CONTRACTS.md) - Constant `CONTRACTS` in `application/diagrams`.
* [domain.models.Proposal](/symbols/domain/models/Proposal.md) - `class Proposal(Contract)` in `domain/models`.
* [domain.pack.ProposalRule](/symbols/domain/pack/ProposalRule.md) - Offline fixture: when the lower-cased request contains every ``all`` word and at least one ``any`` word.
* [domain.pack.Proposals](/symbols/domain/pack/Proposals.md) - `class Proposals(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
