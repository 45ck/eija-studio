---
type: Function
title: domain.formal_bend.check
description: '`def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bend`.'
resource: repo://src/eija_studio/domain/formal_bend.py#check
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal_bend.py#check
  title: domain/formal_bend.py
  hash_method: ast-v2
  sha256: a86c2237e5138be193f87431e9a35848cc5f754d1b6ee1deea962d04a957faf0
notes_baseline: 15a3bf0b7a679a28166aac007921e1299de6697aa6fac15d32bba7132f1b2b8a
---

# domain.formal_bend.check

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal_bend`](/modules/domain/formal_bend.md) |
| Signature | `def check(a: dict[str, Any], ctx: Context) -> Assessment` |
| Code | `repo://src/eija_studio/domain/formal_bend.py#check` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.Assessment](/symbols/domain/formal/Assessment.md) - `class Assessment` in `domain/formal`.
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
* [domain.formal.Findings](/symbols/domain/formal/Findings.md) - Collects reasons by severity.
* [domain.formal.carried_statements](/symbols/domain/formal/carried_statements.md) - The artifact must carry its own assumptions and limitations (a proof without them is not shown as one).
* [domain.formal.exact_keys](/symbols/domain/formal/exact_keys.md) - `def exact_keys(artifact: dict[str, Any], keys: frozenset[str]) -> None` in `domain/formal`.
* [domain.formal.field](/symbols/domain/formal/field.md) - ``container[key]`` if it is exactly of ``typ`` (``bool`` is not an ``int``); else the artifact is malformed.
* [domain.formal.reported_labels](/symbols/domain/formal/reported_labels.md) - The tool's own verdict and check labels may LOWER the status, never raise it.
* [domain.formal.text](/symbols/domain/formal/text.md) - `def text(container: Any, key: str, where: str) -> str` in `domain/formal`.
* [domain.formal_bend.KEYS](/symbols/domain/formal_bend/KEYS.md) - Constant `KEYS` in `domain/formal_bend`.

## Referenced by

* [domain.formal_bend.SPEC](/symbols/domain/formal_bend/SPEC.md) - Constant `SPEC` in `domain/formal_bend`.
<!-- okf:generated:end links -->
