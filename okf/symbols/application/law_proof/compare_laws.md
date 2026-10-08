---
type: Function
title: application.law_proof.compare_laws
description: Which laws a draft adds, removes or changes.
resource: repo://src/eija_studio/application/law_proof.py#compare_laws
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/law_proof.py#compare_laws
  title: application/law_proof.py
  hash_method: ast-v2
  sha256: 40e0518f4628e96106561ea273b6f9dbfbd97fb71531f5440c6bd243f3e413d3
notes_baseline: 177c3e3e92e4a4e9a1e174ae1c956a36a3715a1829606606c1630eb2fb763143
---

# application.law_proof.compare_laws

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/law_proof`](/modules/application/law_proof.md) |
| Signature | `def compare_laws(before: Pack, after: Pack) -> dict[str, list[str]]` |
| Code | `repo://src/eija_studio/application/law_proof.py#compare_laws` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Which laws a draft adds, removes or changes. Removing or changing a law can loosen what the kernel refuses.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
<!-- okf:generated:end links -->
