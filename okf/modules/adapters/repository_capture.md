---
type: Module
title: adapters.repository_capture
description: Bounded repository reads adapted to the existing deterministic Weave engine.
resource: repo://src/eija_studio/adapters/repository_capture.py
tags:
- module
- adapters
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/adapters/repository_capture.py
  title: adapters/repository_capture.py
  hash_method: ast-api-v1
  sha256: 11adb0063e9c4a8de5776baf9291fc44df313c516363ed6cf57fc9be25ce6eb6
notes_baseline: 7a6d91d35efd2efa5b5e3e377103ecade00d833563a5e4649fbeef6093c35595
---

# adapters.repository_capture

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | adapters |
| Code | `repo://src/eija_studio/adapters/repository_capture.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Bounded repository reads adapted to the existing deterministic Weave engine.

Only tracked, non-ignored, permitted text files enter a temporary mirror. Weave never
receives the original checkout, so a declared binding cannot bypass those exclusions.
Git metadata commands do not run project code, hooks, filters, or external diff tools.
The trusted-local-user assumption still applies: this is not an OS security sandbox.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [adapters.repository](/modules/adapters/repository.md) - Repository analysis and bounded source navigation over captured checkout bytes.
<!-- okf:generated:end links -->
