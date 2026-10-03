---
type: Function
title: domain.formal.source_binding
description: Producer sources named by the tool's report versus the bytes the adapter observes now.
resource: repo://src/eija_studio/domain/formal.py#source_binding
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#source_binding
  title: domain/formal.py
  hash_method: ast-v2
  sha256: 3ecc84b74b9aa7036bbf241c3654d57170a0d3e25917b3504aa8047a7174e99b
notes_baseline: 013acc2a26b99a5fced86adf0f2d9afc7405433008fe34645642e37e0f44ba24
---

# domain.formal.source_binding

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `def source_binding(binding: Any, required: tuple[str, ...], f: Findings) -> None` |
| Code | `repo://src/eija_studio/domain/formal.py#source_binding` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Producer sources named by the tool's report versus the bytes the adapter observes now.

``current_sources_sha256_lf`` is observed by the sealed local adapter: attested, not recomputed here.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.Findings](/symbols/domain/formal/Findings.md) - Collects reasons by severity.
* [domain.formal.field](/symbols/domain/formal/field.md) - ``container[key]`` if it is exactly of ``typ`` (``bool`` is not an ``int``); else the artifact is malformed.
<!-- okf:generated:end links -->
