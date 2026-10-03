---
type: Function
title: domain.evidence.intact_artifact
description: The raw artifact of an authentic, hash-consistent, known-protocol receipt of this kind, whatever its subject.
resource: repo://src/eija_studio/domain/evidence.py#intact_artifact
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence.py#intact_artifact
  title: domain/evidence.py
  hash_method: ast-v2
  sha256: 3cd48876068592795c592f35aae245fff23d1bbf4c6d4f4205cb0fe7d95029e4
notes_baseline: dfec9116314653c7ff1e1a5038547328982a550d7f17bc9b558ef5b0f6c4b624
---

# domain.evidence.intact_artifact

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `def intact_artifact(receipt: dict[str, Any], kind: str, authenticator: Callable[[dict[str, Any]], bool]) -> dict[str, Any] \| None` |
| Code | `repo://src/eija_studio/domain/evidence.py#intact_artifact` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The raw artifact of an authentic, hash-consistent, known-protocol receipt of this kind, whatever its subject.

For display-only uses (explaining a policy block by a negative control) that must not depend on the
positive proof being about the current subject; never used to decide a status.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.evidence_kinds.KINDS](/symbols/domain/evidence_kinds/KINDS.md) - Constant `KINDS` in `domain/evidence_kinds`.

## Referenced by

* [application.witness_inspection.inspect_verdict](/symbols/application/witness_inspection/inspect_verdict.md) - Project only the deciding receipt, retaining uncertainty and all recorded raw data without writes.
<!-- okf:generated:end links -->
