---
type: Class
title: domain.laws.PathRequires
description: Every path from the initial state to ``state`` passes through ``via`` (a sequence law).
resource: repo://src/eija_studio/domain/laws.py#PathRequires
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#PathRequires
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: 42c1dd4b9d002028e41830e0fd98542e4b3a50fd2267697f13f078a9655ca96b
notes_baseline: 4067249405b3598bab7acf2d27125728a01190e8b5bdb82770dbab03a8e118c7
---

# domain.laws.PathRequires

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class PathRequires(_Law)` |
| Code | `repo://src/eija_studio/domain/laws.py#PathRequires` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
Every path from the initial state to ``state`` passes through ``via`` (a sequence law).
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `kind` | `Literal['path_requires']` |  |
| `state` | `Name` |  |
| `via` | `Name` |  |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.laws.Name](/symbols/domain/laws/Name.md) - Type alias `Name` in `domain/laws`.

## Referenced by

* [domain.laws.Law](/symbols/domain/laws/Law.md) - Type alias `Law` in `domain/laws`.
* [domain.laws.evaluate_run](/symbols/domain/laws/evaluate_run.md) - Violations by one executed run: per-step laws on every step, sequence laws on the whole run.
<!-- okf:generated:end links -->
