---
type: Class
title: application.memo.IdentityMemo
description: A small, bounded memo for pure functions of frozen contracts, keyed by the identity of the arguments.
resource: repo://src/eija_studio/application/memo.py#IdentityMemo
tags:
- symbol
- application
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/memo.py#IdentityMemo
  title: application/memo.py
  hash_method: ast-sig-v1
  sha256: b27fa06e463614616fe1f09503f1ac5f35c8d9bc45316f949de0e4383b6e6dce
notes_baseline: f31cf7f9f5774f143a06d6466cd36e66831eda8321b92fedc50566baf1ea53ac
---

# application.memo.IdentityMemo

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`application/memo`](/modules/application/memo.md) |
| Signature | `class IdentityMemo` |
| Code | `repo://src/eija_studio/application/memo.py#IdentityMemo` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A small, bounded memo for pure functions of frozen contracts, keyed by the identity of the arguments.
~~~

## Methods

* [`get`](/symbols/application/memo/IdentityMemo.get.md) - `def get(self, args: tuple[Any, ...], compute: Callable[[], _T]) -> _T`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.memo.IdentityMemo.get](/symbols/application/memo/IdentityMemo.get.md) - `def get(self, args: tuple[Any, ...], compute: Callable[[], _T]) -> _T` in `application/memo`.
<!-- okf:generated:end links -->
