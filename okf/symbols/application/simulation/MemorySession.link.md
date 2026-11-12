---
type: Method
title: application.simulation.MemorySession.link
description: Link a record to an object, setting the object's state if given or the object is new (ADR-0241).
resource: repo://src/eija_studio/application/simulation.py#MemorySession.link
tags:
- symbol
- application
- method
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/simulation.py#MemorySession.link
  title: application/simulation.py
  hash_method: ast-v2
  sha256: 2706e2adb53a12c2c3eae482bef56418e8f92aff466afd43cf20dc9f16c0041b
notes_baseline: d4aba946c42f45a3502d6a6c94f3bd8e947b7d0c8269fbd8c59e044df06a8acb
---

# application.simulation.MemorySession.link

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | method |
| Module | [`application/simulation`](/modules/application/simulation.md) |
| Class | [`MemorySession`](/symbols/application/simulation/MemorySession.md) |
| Signature | `def link(self, instance_id: str, link: str, key: str, state: str \| None=None) -> None` |
| Code | `repo://src/eija_studio/application/simulation.py#MemorySession.link` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Link a record to an object, setting the object's state if given or the object is new (ADR-0241).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
