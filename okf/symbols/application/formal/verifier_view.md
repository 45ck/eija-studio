---
type: Function
title: application.formal.verifier_view
description: 'Every verifier the pack declares, with the status its mode implies before any evidence is read: a kind that is not produced for this pack (``not_run``) is NOT_RUN with the reason, never absent and never a pass.'
resource: repo://src/eija_studio/application/formal.py#verifier_view
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/formal.py#verifier_view
  title: application/formal.py
  hash_method: ast-v2
  sha256: b2b185af4173a8b372ba55f3482c8ad4b28cae1c3dddfe1703412cdc2e2d4358
notes_baseline: 83bc629a2dfefeb5398acf612b34b298030e729f8a9ff0bbd2cac067acc120c9
---

# application.formal.verifier_view

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/formal`](/modules/application/formal.md) |
| Signature | `def verifier_view(pack: Pack) -> list[dict[str, str]]` |
| Code | `repo://src/eija_studio/application/formal.py#verifier_view` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every verifier the pack declares, with the status its mode implies before any evidence is read: a kind that is not
produced for this pack (``not_run``) is NOT_RUN with the reason, never absent and never a pass.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations, and (with a pack) the pack's declared verifiers, so a ki…
<!-- okf:generated:end links -->
