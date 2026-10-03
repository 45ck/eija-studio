---
type: Function
title: application.formal.packet_view
description: 'The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations, and (with a pack) the pack''s declared verifiers, so a kind no registered evidence covers (a TLC check) is shown NOT_…'
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
  sha256: eb4bfb4381300e91e1e13b657421fce702dbc9dc3bd450cf268c1b07c6069bf0
notes_baseline: 52a8a1203df4234984af8f369f4c5822338b2a564417771a6665596627fe0e37
---

# application.formal.packet_view

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/formal`](/modules/application/formal.md) |
| Signature | `def packet_view(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool], context: Context, policy_errors: list[str], pack: Pack \| None=None, *, review_context: InspectionContext \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/formal.py#packet_view` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations, and (with a
pack) the pack's declared verifiers, so a kind no registered evidence covers (a TLC check) is shown NOT_RUN too.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [application.formal.BLOCKING](/symbols/application/formal/BLOCKING.md) - Constant `BLOCKING` in `application/formal`.
* [application.formal.verifier_view](/symbols/application/formal/verifier_view.md) - Every verifier the pack declares, with the status its mode implies before any evidence is read: a kind that is not produced for this pack (``not_run``) is NOT_…
* [application.witness_inspection.InspectionContext](/symbols/application/witness_inspection/InspectionContext.md) - The case revision and review scope captured by the compiler, not inferred by a browser.
* [domain.evidence.aggregate_formal](/symbols/domain/evidence/aggregate_formal.md) - Combine every receipt of one kind.
* [domain.evidence_kinds.KINDS](/symbols/domain/evidence_kinds/KINDS.md) - Constant `KINDS` in `domain/evidence_kinds`.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
<!-- okf:generated:end links -->
