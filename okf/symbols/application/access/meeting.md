---
type: Function
title: application.access.meeting
description: 'A record''s values that meet every guard over values of these transitions (ADR-0234): {} when they have none, None when no values meet them all.'
resource: repo://src/eija_studio/application/access.py#meeting
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/access.py#meeting
  title: application/access.py
  hash_method: ast-v2
  sha256: 929812237bf6f13bd5b85cc1586abcd22994fae5db3c14747b1842eb1eca26e1
notes_baseline: 274359d514a20e6c4d60c7008ce3f8787de9368858756b006c318aba53420d68
---

# application.access.meeting

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/access`](/modules/application/access.md) |
| Signature | `def meeting(pack: Pack, transitions: list[Transition]) -> dict[str, Any] \| None` |
| Code | `repo://src/eija_studio/application/access.py#meeting` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A record's values that meet every guard over values of these transitions (ADR-0234): {} when they have none,
None when no values meet them all. A cell is about who may act, so it is tried on a record whose values let it.

A guard reads one attribute, so each attribute is solved on its own, among the values that stand for every value
its guards tell apart; a choice attribute only among its declared choices, since a record can hold no other.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.value_guards.points](/symbols/domain/value_guards/points.md) - Values of one attribute that stand for every value its guards can tell apart; None means no value.

## Referenced by

* [application.access.reach](/symbols/application/access/reach.md) - Can a record reach `target` with no step taken by role `without` (or at all, when it is None)?
<!-- okf:generated:end links -->
