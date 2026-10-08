---
type: Function
title: application.formal.for_pack
description: Artifacts of a kind this pack does not verify from the reports become one NOT_RUN artifact with the pack's reason.
resource: repo://src/eija_studio/application/formal.py#for_pack
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/formal.py#for_pack
  title: application/formal.py
  hash_method: ast-v2
  sha256: 46266bc8d51a4addfdcb80104839f20654c711ca8794ba2f01e381989a87ad4e
notes_baseline: 8b4c0a65df2592284b0d5569a67bcf20ff7ef5f2b4575cc972cfd873a77baac0
---

# application.formal.for_pack

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/formal`](/modules/application/formal.md) |
| Signature | `def for_pack(items: list[FormalArtifact], pack: Pack \| None) -> list[FormalArtifact]` |
| Code | `repo://src/eija_studio/application/formal.py#for_pack` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Artifacts of a kind this pack does not verify from the reports become one NOT_RUN artifact with the pack's reason.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.formal.pack_not_run](/symbols/application/formal/pack_not_run.md) - Why ``kind`` is NOT_RUN for ``pack`` (None when the pack verifies it from the checkout's reports).
* [domain.evidence_kinds.KINDS](/symbols/domain/evidence_kinds/KINDS.md) - Constant `KINDS` in `domain/evidence_kinds`.
* [domain.formal.FormalArtifact](/symbols/domain/formal/FormalArtifact.md) - One raw formal artifact from a tool report.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.formal.attach](/symbols/application/formal/attach.md) - Sealed receipts for every registered kind the source returned, skipping an exact repeat of the latest one.
<!-- okf:generated:end links -->
