---
type: Function
title: application.formal.pack_not_run
description: Why ``kind`` is NOT_RUN for ``pack`` (None when the pack verifies it from the checkout's reports).
resource: repo://src/eija_studio/application/formal.py#pack_not_run
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/formal.py#pack_not_run
  title: application/formal.py
  hash_method: ast-v2
  sha256: 3c1650b2aac16f0ccda83f6952f26c94f5f96d3ba05ae314fd0e5655a5fc2984
notes_baseline: 5eebb651187068ba4a29e2ec2eb5d73bfe4007f348396b347502a5095717dcfe
---

# application.formal.pack_not_run

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/formal`](/modules/application/formal.md) |
| Signature | `def pack_not_run(pack: Pack, kind: str) -> str \| None` |
| Code | `repo://src/eija_studio/application/formal.py#pack_not_run` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Why ``kind`` is NOT_RUN for ``pack`` (None when the pack verifies it from the checkout's reports).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.formal.READS_REPORTS](/symbols/application/formal/READS_REPORTS.md) - Constant `READS_REPORTS` in `application/formal`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.formal.for_pack](/symbols/application/formal/for_pack.md) - Artifacts of a kind this pack does not verify from the reports become one NOT_RUN artifact with the pack's reason.
<!-- okf:generated:end links -->
