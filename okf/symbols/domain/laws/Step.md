---
type: Class
title: domain.laws.Step
description: One executed transition of a run.
resource: repo://src/eija_studio/domain/laws.py#Step
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/laws.py#Step
  title: domain/laws.py
  hash_method: ast-sig-v1
  sha256: 916eba652a2b2288dfeea83355b0a67baffe49d5e030676d2d246f95c4c0b0a2
notes_baseline: ae5ec9282aa594b59ee67775b28b467537cc121c782fbc289b8b50fd52a91988
---

# domain.laws.Step

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/laws`](/modules/domain/laws.md) |
| Signature | `class Step` |
| Code | `repo://src/eija_studio/domain/laws.py#Step` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
One executed transition of a run.
~~~

## Fields

| Field | Annotation | Default |
|---|---|---|
| `action` | `str` |  |
| `role` | `str` |  |
| `source` | `str` |  |
| `target` | `str` |  |
| `effects` | `tuple[str, ...]` | `()` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.laws.evaluate_run](/symbols/domain/laws/evaluate_run.md) - Violations by one executed run: per-step laws on every step, sequence laws on the whole run.
<!-- okf:generated:end links -->
