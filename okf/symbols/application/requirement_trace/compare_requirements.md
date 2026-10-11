---
type: Function
title: application.requirement_trace.compare_requirements
description: Compare prose only for existing IDs.
resource: repo://src/eija_studio/application/requirement_trace.py#compare_requirements
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/requirement_trace.py#compare_requirements
  title: application/requirement_trace.py
  hash_method: ast-v2
  sha256: df58cbbe6f1d724e3ffe5157952e91b016171b430b989f04d0aa8427411fd071
notes_baseline: 727c0a3508ac9b743a30b69a42d4a30403634977c5590e8a058a9f4a83cde256
---

# application.requirement_trace.compare_requirements

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/requirement_trace`](/modules/application/requirement_trace.md) |
| Signature | `def compare_requirements(rows: list[dict[str, str]], drafts: Mapping[str, str]) -> list[dict[str, Any]]` |
| Code | `repo://src/eija_studio/application/requirement_trace.py#compare_requirements` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Compare prose only for existing IDs. Unknown IDs never introduce a new executable rule.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.

## Referenced by

* [application.requirement_trace.requirement_review](/symbols/application/requirement_trace/requirement_review.md) - Pinned requirement rows and declared model/law/source/test links with visible gaps.
<!-- okf:generated:end links -->
