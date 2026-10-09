---
type: Function
title: application.sequences.record_name
description: 'The record lifeline''s name and its class: `loan : Loan` when the pack has a data model.'
resource: repo://src/eija_studio/application/sequences.py#record_name
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/sequences.py#record_name
  title: application/sequences.py
  hash_method: ast-v2
  sha256: f6e9e1395dd3de9f2f3b302f353771a9e831216475633591462110d757328f6e
notes_baseline: f179a653faeb56af93f8465e0b4078d57ee301655874f595ea93c11c507fcce1
---

# application.sequences.record_name

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/sequences`](/modules/application/sequences.md) |
| Signature | `def record_name(pack: Pack) -> tuple[str, str]` |
| Code | `repo://src/eija_studio/application/sequences.py#record_name` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The record lifeline's name and its class: `loan : Loan` when the pack has a data model.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.sequences.check_sequences](/symbols/application/sequences/check_sequences.md) - Every scenario drawn as a sequence and checked by the kernel on `model`; with `base` (the model in force) also on it, for the change.
<!-- okf:generated:end links -->
