---
type: Function
title: domain.formal.reported_labels
description: The tool's own verdict and check labels may LOWER the status, never raise it.
resource: repo://src/eija_studio/domain/formal.py#reported_labels
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#reported_labels
  title: domain/formal.py
  hash_method: ast-v2
  sha256: 13acba11beaef190b2ffd938f1b6428646686d00546be378879d9e114ba62c6f
notes_baseline: f028676c34e641c7cf4291de659e9d1fa9f7f3e3ba5e013d5bee482388eae360
---

# domain.formal.reported_labels

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `def reported_labels(artifact: dict[str, Any], f: Findings) -> None` |
| Code | `repo://src/eija_studio/domain/formal.py#reported_labels` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The tool's own verdict and check labels may LOWER the status, never raise it.

A PASS label is not evidence (the kernel recomputes from raw content), but a FAIL or an incomplete label
the tool reported about itself (a drift check, a skipped self-test) is never ignored.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.Findings](/symbols/domain/formal/Findings.md) - Collects reasons by severity.
* [domain.formal.field](/symbols/domain/formal/field.md) - ``container[key]`` if it is exactly of ``typ`` (``bool`` is not an ``int``); else the artifact is malformed.
* [domain.formal.records](/symbols/domain/formal/records.md) - `def records(container: Any, key: str, where: str) -> list[dict[str, Any]]` in `domain/formal`.
* [domain.formal.text](/symbols/domain/formal/text.md) - `def text(container: Any, key: str, where: str) -> str` in `domain/formal`.

## Referenced by

* [domain.formal_bend.check](/symbols/domain/formal_bend/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bend`.
* [domain.formal_bmc.check](/symbols/domain/formal_bmc/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bmc`.
* [domain.formal_smt.check](/symbols/domain/formal_smt/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_smt`.
<!-- okf:generated:end links -->
