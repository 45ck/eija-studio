---
type: Function
title: domain.evidence.combine
description: 'The status algebra: authenticated PASS and FAIL never average (CONFLICT); FAIL beats PASS-less states; STALE (a receipt for another subject), then NOT_RUN (a prerequisite was missing), then UNKNOWN.'
resource: repo://src/eija_studio/domain/evidence.py#combine
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence.py#combine
  title: domain/evidence.py
  hash_method: ast-v2
  sha256: 4aa3183184160e684c7ee2e558ec380f53c5ca2abfc3d98fdafcf0692827263e
notes_baseline: 6b442a2d549eca510f3e1c52a8b09a7fa0f13445ec83d599fc514134c877f71e
---

# domain.evidence.combine

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `def combine(statuses: list[str]) -> str` |
| Code | `repo://src/eija_studio/domain/evidence.py#combine` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
The status algebra: authenticated PASS and FAIL never average (CONFLICT); FAIL beats PASS-less states;
STALE (a receipt for another subject), then NOT_RUN (a prerequisite was missing), then UNKNOWN.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.evidence.aggregate_formal](/symbols/domain/evidence/aggregate_formal.md) - Combine every receipt of one kind.
* [domain.evidence.aggregate_status](/symbols/domain/evidence/aggregate_status.md) - `def aggregate_status(receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[s…` in `domain/evidence`.
<!-- okf:generated:end links -->
