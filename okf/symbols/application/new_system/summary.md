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
  sha256: 2e2077e2f9b4d939bcafdfafa62f05a74442504509608f968cdca4482c94e8c3
notes_baseline: 498c96c8d251dee575c9b479bf39950e176b9b6e5847f18ad37d50e56e09df86
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

## Referenced by

* [application.describe_system.described_summary](/symbols/application/describe_system/described_summary.md) - What a described system has in every view, for the form to say before it is created.
<!-- okf:generated:end links -->
