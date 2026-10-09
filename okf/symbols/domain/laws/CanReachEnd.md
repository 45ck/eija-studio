---
type: Class
title: domain.laws.CanReachEnd
description: 'From every state a record can get to, some run still reaches one of ``states`` (its ends): no record is left in a dead end or a loop with no way out.'
resource: repo://src/eija_studio/domain/laws.py#CanReachEnd
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#CanReachEnd
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: fc9320f48d60961bfc402cba9ff10869abb4ed553a4ddf543caecd3592d802f8
notes_baseline: 9898be0e95f994768ae9be41ccf2b23fd53f5463406587d7f1a90ef44d1d6866
---

# domain.laws.CanReachEnd

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class CanReachEnd(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#CanReachEnd` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
From every state a record can get to, some run still reaches one of ``states`` (its ends): no record is left
in a dead end or a loop with no way out. A liveness law about the whole table, judged on no single run (ADR-0221).
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['can_reach_end']` |  |
| `states` | `tuple[Name, ...]` | `Field(min_length=1)` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.

## Referenced by

* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
* [domain.laws.stuck_states](/symbols/domain/laws/stuck_states.md) - The states a record can get to from ``initial`` along ``edges`` from which no end of ``law`` can be reached.
<!-- okf:generated:end links -->
