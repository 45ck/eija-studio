---
type: Function
title: domain.formal.field
description: '``container[key]`` if it is exactly of ``typ`` (``bool`` is not an ``int``); else the artifact is malformed.'
resource: repo://src/eija_studio/domain/formal.py#field
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#field
  title: domain/formal.py
  hash_method: ast-v2
  sha256: 833f86298c49d858350cd25aff4b7c92e771630897c667f6b1f7cb1730ffd0da
notes_baseline: b744a8f460e365edd2e7b4d70218b4a855396935994e8c89cb4f047103c749fd
---

# domain.formal.field

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `def field(container: Any, key: str, typ: type, where: str) -> Any` |
| Code | `repo://src/eija_studio/domain/formal.py#field` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
``container[key]`` if it is exactly of ``typ`` (``bool`` is not an ``int``); else the artifact is malformed.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.Malformed](/symbols/domain/formal/Malformed.md) - The artifact does not have the declared typed shape (a structural defect, judged FAIL).

## Referenced by

* [domain.formal.digest](/symbols/domain/formal/digest.md) - `def digest(container: Any, key: str, where: str) -> str` in `domain/formal`.
* [domain.formal.has_items](/symbols/domain/formal/has_items.md) - True if the list at ``key`` is not empty (its items may be of any type).
* [domain.formal.records](/symbols/domain/formal/records.md) - `def records(container: Any, key: str, where: str) -> list[dict[str, Any]]` in `domain/formal`.
* [domain.formal.reported_labels](/symbols/domain/formal/reported_labels.md) - The tool's own verdict and check labels may LOWER the status, never raise it.
* [domain.formal.source_binding](/symbols/domain/formal/source_binding.md) - Producer sources named by the tool's report versus the bytes the adapter observes now.
* [domain.formal.strings](/symbols/domain/formal/strings.md) - `def strings(container: Any, key: str, where: str, minimum: int=1) -> list[str]` in `domain/formal`.
* [domain.formal.text](/symbols/domain/formal/text.md) - `def text(container: Any, key: str, where: str) -> str` in `domain/formal`.
* [domain.formal_bend.check](/symbols/domain/formal_bend/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bend`.
* [domain.formal_bmc.check](/symbols/domain/formal_bmc/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_bmc`.
* [domain.formal_smt.check](/symbols/domain/formal_smt/check.md) - `def check(a: dict[str, Any], ctx: Context) -> Assessment` in `domain/formal_smt`.
<!-- okf:generated:end links -->
