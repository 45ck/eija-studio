---
type: Function
title: domain.formal.not_run_reason
description: 'A NOT_RUN artifact is exactly {protocol, not_run: {reason, prerequisite}}: honest absence, never PASS.'
resource: repo://src/eija_studio/domain/formal.py#not_run_reason
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/formal.py#not_run_reason
  title: domain/formal.py
  hash_method: ast-v2
  sha256: 5128c4647d64c5bd63027cc9b1b14ebc1e60aa759cf644d820a398b266e54581
notes_baseline: 669ffb83f1e115e6b3b5c5fd569c943ec0043cf8322dae9e2abf6a3fd41b248e
---

# domain.formal.not_run_reason

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/formal`](/modules/domain/formal.md) |
| Signature | `def not_run_reason(artifact: dict[str, Any]) -> Assessment` |
| Code | `repo://src/eija_studio/domain/formal.py#not_run_reason` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
A NOT_RUN artifact is exactly {protocol, not_run: {reason, prerequisite}}: honest absence, never PASS.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.formal.Assessment](/symbols/domain/formal/Assessment.md) - `class Assessment` in `domain/formal`.
* [domain.formal.Malformed](/symbols/domain/formal/Malformed.md) - The artifact does not have the declared typed shape (a structural defect, judged FAIL).
* [domain.formal.text](/symbols/domain/formal/text.md) - `def text(container: Any, key: str, where: str) -> str` in `domain/formal`.
<!-- okf:generated:end links -->
