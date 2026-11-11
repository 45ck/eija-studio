---
type: Class
title: domain.laws.DistinctActors
description: 'Separation of duties (issue #149, ADR-0233): on one record, no single actor takes two different ``actions``, such as raising a request and approving it.'
resource: repo://src/eija_studio/domain/laws.py#DistinctActors
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#DistinctActors
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: ced6ebe2627bddbdd2bd3482cd6543b17500d45c93f46cd2bd2fe454ca7d74d4
notes_baseline: eb7fb5990e33c2e6e1d05f98a8c69632eaf7e2442314d30321cf020dbdc78759
---

# domain.laws.DistinctActors

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class DistinctActors(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#DistinctActors` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Separation of duties (issue #149, ADR-0233): on one record, no single actor takes two different ``actions``,
such as raising a request and approving it. About who acted, not which role: an actor whose role changes between
steps is still the same actor. The kernel refuses the second step at commit time (``SEPARATION_DENIED``); the
table cannot break it, so the policy never reports it. Repeating the same action (resubmitting) is allowed.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['distinct_actors']` |  |
| `actions` | `tuple[Name, ...]` | `Field(min_length=2, max_length=8)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.

## Referenced by

* [application.runtime.check_separation](/symbols/application/runtime/check_separation.md) - Refuse an actor who already took another action of a separation law on this record.
* [application.runtime.separations](/symbols/application/runtime/separations.md) - The pack's separation-of-duties laws in force on ``model`` that name ``action`` (issue #149, ADR-0233).
* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
* [domain.laws.separation_breach](/symbols/domain/laws/separation_breach.md) - The other listed action ``actor`` already took on this record, if taking ``action`` now breaks ``law``.
<!-- okf:generated:end links -->
