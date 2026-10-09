---
type: Function
title: application.describe_system.tests_for
description: 'Test cases for a new system, recorded by the kernel: the way to each end state, and the first step taken by a role that may not take it.'
resource: repo://src/eija_studio/application/describe_system.py#tests_for
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/describe_system.py#tests_for
  title: application/describe_system.py
  hash_method: ast-v2
  sha256: a56e30b61125b41957d49c4dfc013667d7e0d8cde38045b293abe048058929e4
notes_baseline: 37aea50ef04e284a48eb69df26f97cf0ee9e6cbebf99a6cf7a7635dec482ab93
---

# application.describe_system.tests_for

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/describe_system`](/modules/application/describe_system.md) |
| Signature | `def tests_for(pack: Pack, record: str) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/describe_system.py#tests_for` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Test cases for a new system, recorded by the kernel: the way to each end state, and the first step taken by a
role that may not take it. They pin down what the kernel does now, so a later change that alters it shows.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [application.describe_system.describe_documents](/symbols/application/describe_system/describe_documents.md) - The documents of a new system described in `text`, checked by the kernel, and what the describer read.
<!-- okf:generated:end links -->
