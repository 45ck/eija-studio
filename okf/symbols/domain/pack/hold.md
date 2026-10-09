---
type: Function
title: domain.pack.hold
description: A draft of `pack` that holds `content` in memory as its file `name` beside `pack.json` (such as a draft data model for `data.json`, ADR-0202).
resource: repo://src/eija_studio/domain/pack.py#hold
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#hold
  title: domain/pack.py
  hash_method: ast-v2
  sha256: 91176045322b3bbdc3041b7f190be56bacdbdd1ad7e9d4348fad4d0d857d5e4e
notes_baseline: 18faf2ff711701d490d1045578376bd5878163e114d870ad3adce18974e2e30d
---

# domain.pack.hold

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def hold(pack: Pack, name: str, content: Any) -> Pack` |
| Code | `repo://src/eija_studio/domain/pack.py#hold` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A draft of `pack` that holds `content` in memory as its file `name` beside `pack.json` (such as a draft data
model for `data.json`, ADR-0202). The pack document and its digest are the same; nothing is written, and the
other files are still read from where `pack` was read.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.data_steps.draft_pack](/symbols/application/data_steps/draft_pack.md) - `pack` as these plan steps would have it, held in memory: on a system the person started (`grows`), the actions and roles they name are declared (ADR-0201) and…
<!-- okf:generated:end links -->
