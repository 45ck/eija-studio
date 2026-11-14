---
type: Module
title: adapters.system_describer
description: 'Offline system describer for PlayIDE''s "Describe your app" start (ADR-0216): a fixed library of app shapes and a small reader for the fields and roles a description names, never an LLM.'
resource: repo://src/eija_studio/adapters/system_describer.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/system_describer.py
  title: adapters/system_describer.py
  hash_method: ast-api-v1
  sha256: fff6ce0ee7ade4ee694a6323b819ea91f3a84c25b90e5a50cf99a51ff3844607
notes_baseline: 3d090836b93977410c15a588d72b11918efd02cd2a2c802b29378dfd4803f9e1
---

# adapters.system_describer

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/system_describer.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Offline system describer for PlayIDE's "Describe your app" start (ADR-0216): a fixed library of app shapes and a
small reader for the fields and roles a description names, never an LLM. Its answer is untrusted, like any proposal;
the application builds the system's documents from it and the kernel's pack check decides whether they are a system.

The reader picks the app shape whose keywords the description uses most (the shapes are data in
`packs/describe-shapes.json`: orders, support tickets, bookings, approvals, loans, hiring, deliveries, publishing and
bugs), else a plain one. Role nouns the
description uses replace the shape's own (a coffee shop's barista for the order flow's staff role). Fields come from
"with …" and "has …" lists: a name with "(a, b, c)" after it is a choice, words such as price or quantity are numbers,
date or deadline are dates, and anything else is text. It says what it read and what it assumed, in words.
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
