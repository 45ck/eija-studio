---
type: Function
title: application.new_system.summary
description: What the new system has, for the form to say before it is created.
resource: repo://src/eija_studio/application/new_system.py#summary
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/new_system.py#summary
  title: application/new_system.py
  hash_method: ast-v2
  sha256: 13ab02dfa057a6bccec184c78a7f68021a854c302586d78e2c730516ffc8b9eb
notes_baseline: ef512717790c99275aa7b67217d16debdcc7808bd6b10da4b5ecbb10bf1ea894
---

# application.new_system.summary

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/new_system`](/modules/application/new_system.md) |
| Signature | `def summary(documents: dict[str, dict[str, Any]]) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/new_system.py#summary` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What the new system has, for the form to say before it is created.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.parse_pack](/symbols/domain/pack/parse_pack.md) - Validate a decoded JSON document as a pack.
<!-- okf:generated:end links -->
