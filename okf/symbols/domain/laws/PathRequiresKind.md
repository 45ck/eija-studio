---
type: Class
title: domain.laws.PathRequiresKind
description: 'Every path from the initial state to ``state`` includes a step by a role of one of ``role_kinds``, the step entering ``state`` included: a human in the loop before an agent''s work takes effect (a sequence law).'
resource: repo://src/eija_studio/domain/laws.py#PathRequiresKind
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#PathRequiresKind
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: 6d47bc91853cfb45e9ba209edaf9ed1dbfb59b03a08bea2d46cf17f1eb5caa0b
notes_baseline: e920663a7a2ab6070a925a3b97e449af85ea72ad31dfe71ac59455d9a6e29784
---

# domain.laws.PathRequiresKind

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class PathRequiresKind(_KindLaw)` |
| Code | `repo://src/eija_studio/domain/laws.py#PathRequiresKind` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Every path from the initial state to ``state`` includes a step by a role of one of ``role_kinds``, the step
entering ``state`` included: a human in the loop before an agent's work takes effect (a sequence law).
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['path_requires_kind']` |  |
| `state` | `Name` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.

## Referenced by

* [domain.laws.KIND_LAWS](/symbols/domain/laws/KIND_LAWS.md) - Constant `KIND_LAWS` in `domain/laws`.
* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
* [domain.laws.evaluate_run](/symbols/domain/laws/evaluate_run.md) - Violations by one executed run: per-step laws on every step, sequence laws on the whole run.
<!-- okf:generated:end links -->
