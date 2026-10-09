---
type: Function
title: domain.pack.held
description: What a draft holds as its file `name` (see `hold`), or None to read the file from the pack's folder.
resource: repo://src/eija_studio/domain/pack.py#held
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#held
  title: domain/pack.py
  hash_method: ast-v2
  sha256: 46565ab11041cde7e95352269faf18e10bd059a59154abb184300cc2cb648a18
notes_baseline: 79f51066b42708b4fb0b4b43c841b9cd387287865f8e4887a51ff5abf751e157
---

# domain.pack.held

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def held(pack: Pack, name: str) -> Any \| None` |
| Code | `repo://src/eija_studio/domain/pack.py#held` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
What a draft holds as its file `name` (see `hold`), or None to read the file from the pack's folder.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.

## Referenced by

* [domain.data.data_for](/symbols/domain/data/data_for.md) - The data model beside this pack's `pack.json`, if it has one: the one a draft holds (ADR-0202), else `data.json`.
<!-- okf:generated:end links -->
