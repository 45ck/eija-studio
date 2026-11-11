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
  sha256: 0b854afbd30e49d2c21ab57ab52ca56339d4a484ed7d37ae7331300424e87a30
notes_baseline: 53174f40f703a4cc0b3da0b032c923bc11893cbe61bacfa41349fb9d9f189a6b
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
| `actor` | `str` | `''` |
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.laws.evaluate_run](/symbols/domain/laws/evaluate_run.md) - Violations by one executed run: per-step laws on every step, sequence laws on the whole run.
<!-- okf:generated:end links -->
