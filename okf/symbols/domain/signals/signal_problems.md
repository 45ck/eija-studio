---
type: Function
title: domain.signals.signal_problems
description: A signal is named Signal:Name and goes to another workflow; nothing else may take a signal's name.
resource: repo://src/eija_studio/domain/signals.py#signal_problems
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/signals.py#signal_problems
  title: domain/signals.py
  hash_method: ast-v2
  sha256: 6c65c256763ee34bd67432c1c5d40b183aa2dc18e6400fb9d9416456054c4e6b
notes_baseline: f713571f54f08a2ebf4f45654eaa24b39955a6cd7af413970476292a997bbaa8
---

# domain.signals.signal_problems

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/signals`](/modules/domain/signals.md) |
| Signature | `def signal_problems(pack_id: str, catalog: Iterable[Any]) -> list[str]` |
| Code | `repo://src/eija_studio/domain/signals.py#signal_problems` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A signal is named Signal:Name and goes to another workflow; nothing else may take a signal's name.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.signals.SIGNAL](/symbols/domain/signals/SIGNAL.md) - Constant `SIGNAL` in `domain/signals`.
<!-- okf:generated:end links -->
