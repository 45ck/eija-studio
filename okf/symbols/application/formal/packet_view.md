---
type: Function
title: application.formal.packet_view
description: 'The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations.'
resource: repo://src/eija_studio/application/formal.py#packet_view
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/formal.py#packet_view
  title: application/formal.py
  hash_method: ast-v2
  sha256: 1468fc4c1438526a586f6c04a186fd34bc01edd606c3e019b1f1157010eaae97
notes_baseline: 00938f10d93a04b5a28a468330604086aa452a1a942fb1815fd4a8364c82a267
---

# application.formal.packet_view

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/formal`](/modules/application/formal.md) |
| Signature | `def packet_view(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool], context: Context, policy_errors: list[str]) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/formal.py#packet_view` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.formal.BLOCKING](/symbols/application/formal/BLOCKING.md) - Constant `BLOCKING` in `application/formal`.
* [domain.evidence.aggregate_formal](/symbols/domain/evidence/aggregate_formal.md) - Combine every receipt of one kind.
* [domain.evidence_kinds.KINDS](/symbols/domain/evidence_kinds/KINDS.md) - Constant `KINDS` in `domain/evidence_kinds`.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
<!-- okf:generated:end links -->
