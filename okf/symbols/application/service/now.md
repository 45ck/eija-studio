---
type: Function
title: application.service.now
description: '`def now() -> str` in `application/service`.'
resource: repo://src/eija_studio/application/service.py#now
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/service.py#now
  title: application/service.py
  hash_method: ast-v2
  sha256: bfb464faa7807e25ce4db44e6eda24c9c71fd82a2695f82ec83d82c8f723fbcb
notes_baseline: 9ffe270073bca6278433bee191ba84095bfd8920da3f19a8357597d196996129
---

# application.service.now

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/service`](/modules/application/service.md) |
| Signature | `def now() -> str` |
| Code | `repo://src/eija_studio/application/service.py#now` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [application.service.Studio.approve](/symbols/application/service/Studio.approve.md) - `def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknow…` in `application/service`.
* [application.service.Studio.create](/symbols/application/service/Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [application.service.Studio.propose](/symbols/application/service/Studio.propose.md) - `def propose(self, case_id: str, expected: int, *, consent: bool=False) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
<!-- okf:generated:end links -->
