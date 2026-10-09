---
type: Class
title: domain.pack.PackError
description: A pack that cannot be used.
resource: repo://src/eija_studio/domain/pack.py#PackError
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#PackError
  title: domain/pack.py
  hash_method: ast-sig-v1
  sha256: f89a9c91009526fb0da0c61c3ac21251b2dc78f698fa2bf95a2f4ea0b950c6d3
notes_baseline: 1e9625dae1da5e47e4b10a56d54eceff332eb4acce0cebf280d011d5967476a0
---

# domain.pack.PackError

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `class PackError(DomainError)` |
| Code | `repo://src/eija_studio/domain/pack.py#PackError` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
A pack that cannot be used. ``diagnostics`` is sorted and never empty.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.

## Referenced by

* [application.law_proof.with_laws](/symbols/application/law_proof/with_laws.md) - The pack with its law file replaced by `laws` (a draft edited in PlayIDE), checked as the pack loader checks it.
* [application.new_system.parse_sketch](/symbols/application/new_system/parse_sketch.md) - The transitions, extra actions and extra roles of a sketch, or `PackError` naming each bad line.
* [application.new_system.sketch_documents](/symbols/application/new_system/sketch_documents.md) - `pack.json` and `data.json` for a system started from a sketch, checked by the kernel's pack check.
* [domain.pack.default_location](/symbols/domain/pack/default_location.md) - ``$EIJA_PACK`` if set, else the pack named by ``packs/default.json``.
* [domain.pack.find_pack](/symbols/domain/pack/find_pack.md) - Resolve a loaded snapshot by digest, or an unambiguous id after refreshing its sources.
* [domain.pack.parse_pack](/symbols/domain/pack/parse_pack.md) - Validate a decoded JSON document as a pack.
<!-- okf:generated:end links -->
