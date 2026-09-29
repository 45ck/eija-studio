---
type: Class
title: domain.formal.KindSpec
description: 'One evidence kind: what it claims, how it is checked, what it does not establish.'
resource: repo://src/eija_studio/domain/formal.py#KindSpec
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#KindSpec
  title: domain/formal.py
  hash_method: ast-sig-v1
  sha256: b699f145ebf0a5d612557257a2df58d454383a47c428f04a8898e861db2c45a2
notes_baseline: d00a048b426d6cd715f506dbed53b6cc7ca87fa16e068e449c561bc641d3840e
---

# domain.formal.KindSpec

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `class KindSpec` |
| Code | `repo://src/eija_studio/domain/formal.py#KindSpec` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
One evidence kind: what it claims, how it is checked, what it does not establish.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `str` |  |
| `claim` | `str` |  |
| `method` | `str` |  |
| `protocol` | `str` |  |
| `level` | `str` |  |
| `establishes` | `str` |  |
| `does_not_establish` | `tuple[str, ...]` |  |
| `prerequisites` | `str` |  |
| `check` | `Callable[[dict[str, Any], Context], Assessment]` |  |
| `describe` | `Callable[[dict[str, Any]], dict[str, Any]]` |  |
| `explain` | `Callable[[dict[str, Any], tuple[str, ...]], list[dict[str, Any]]]` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.Assessment](/symbols/domain/formal/Assessment.md) - `class Assessment` in `domain/formal`.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.

## Referenced by

* [domain.evidence_kinds.KINDS](/symbols/domain/evidence_kinds/KINDS.md) - Constant `KINDS` in `domain/evidence_kinds`.
* [domain.formal_bend.SPEC](/symbols/domain/formal_bend/SPEC.md) - Constant `SPEC` in `domain/formal_bend`.
* [domain.formal_bmc.SPEC](/symbols/domain/formal_bmc/SPEC.md) - Constant `SPEC` in `domain/formal_bmc`.
* [domain.formal_smt.SPEC](/symbols/domain/formal_smt/SPEC.md) - Constant `SPEC` in `domain/formal_smt`.
<!-- okf:generated:end links -->
