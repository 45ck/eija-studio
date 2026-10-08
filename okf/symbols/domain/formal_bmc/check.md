---
type: Function
title: domain.formal_bmc.check
description: '`def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bmc`.'
resource: repo://src/eija_studio/domain/formal_bmc.py#check
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal_bmc.py#check
  title: domain/formal_bmc.py
  hash_method: ast-v2
  sha256: 7a03bbe1c0488c409b0a189695bd76390bf54f7766eb113ef950ad29a15cd3cd
notes_baseline: 6ef8ad15ad95193ef82f2be98177ca1b509ddf4812d815631621116f19b12fb4
---

# domain.formal_bmc.check

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal_bmc`](/modules/domain/formal_bmc.md) |
| Signature | `def check(a: dict[str, Any], ctx: Context) -> Assessment` |
| Code | `repo://src/eija_studio/domain/formal_bmc.py#check` |
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
* [domain.formal_bmc.KEYS](/symbols/domain/formal_bmc/KEYS.md) - Constant `KEYS` in `domain/formal_bmc`.

## Referenced by

* [domain.formal_bmc.SPEC](/symbols/domain/formal_bmc/SPEC.md) - Constant `SPEC` in `domain/formal_bmc`.
<!-- okf:generated:end links -->
