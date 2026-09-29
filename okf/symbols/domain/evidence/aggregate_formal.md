---
type: Function
title: domain.evidence.aggregate_formal
description: Combine every receipt of one kind.
resource: repo://src/eija_studio/domain/evidence.py#aggregate_formal
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/evidence.py#aggregate_formal
  title: domain/evidence.py
  hash_method: ast-v2
  sha256: 16daaea76989311c9e01de6685422a2dd418a06e38ed31a6927e1cd18674e158
notes_baseline: 12055f086fccacd4ba90ec80a7a1b4f03cda05234f244614fc576230d55146ef
---

# domain.evidence.aggregate_formal

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/evidence`](/modules/domain/evidence.md) |
| Signature | `def aggregate_formal(kind: str, receipts: list[dict[str, Any]], subject: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool], context: Context \| None=None) -> FormalVerdict` |
| Code | `repo://src/eija_studio/domain/evidence.py#aggregate_formal` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Combine every receipt of one kind. No receipt at all is UNKNOWN: absence is visible, never green.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.evidence.FormalVerdict](/symbols/domain/evidence/FormalVerdict.md) - The status of one evidence kind for the current subject, with the receipt that decided it.
* [domain.evidence.combine](/symbols/domain/evidence/combine.md) - The status algebra: authenticated PASS and FAIL never average (CONFLICT); FAIL beats PASS-less states; STALE (a receipt for another subject), then NOT_RUN (a p…
* [domain.formal.Context](/symbols/domain/formal/Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.

## Referenced by

* [application.formal.packet_view](/symbols/application/formal/packet_view.md) - The formal part of the review packet: per-kind claims, blockers, the full evidence list, explanations.
<!-- okf:generated:end links -->
