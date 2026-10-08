---
type: Module
title: adapters.self_facts
description: Syntactic facts about EIJA's own review implementation, never a conformance proof.
resource: repo://src/eija_studio/adapters/self_facts.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/self_facts.py
  title: adapters/self_facts.py
  hash_method: ast-api-v1
  sha256: 250c13ce9c2559311daa24d52f22bb39fe23a8b949788e2573b47dd25c152438
notes_baseline: 65b0e9ca9d61715768c228edac824e90a1e8e59435b3e478845d62b8e19024ec
---

# adapters.self_facts

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/self_facts.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Syntactic facts about EIJA's own review implementation, never a conformance proof.

The caller supplies its already filtered, tracked source snapshot. This adapter neither
opens files nor imports or executes target code. It reuses weave's Python AST resolver
and normalisation; the declared reference journey remains a separate domain pack.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`domain/pack`](/modules/domain/pack.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).

## Referenced by

* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
<!-- okf:generated:end links -->
