---
type: Module
title: interfaces.uml_interop
description: '`eija uml export` and `eija uml import`: UML interchange from the command line (ADR-0190).'
resource: repo://src/eija_studio/interfaces/uml_interop.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/uml_interop.py
  title: interfaces/uml_interop.py
  hash_method: ast-api-v1
  sha256: 4a010cce7817db14c0be12d45745e9b154503d3e7a186b492bb250d73b17a9bd
notes_baseline: 1582610b43b3e25dec3f14fbf57daeb58c0149a474643fd32c1a88564369fecf
---

# interfaces.uml_interop

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/uml_interop.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
`eija uml export` and `eija uml import`: UML interchange from the command line (ADR-0190).

Export prints the file (or writes `--out`) and lists on stderr what no UML file carries. Like `eija render`, a model
the protected policy refuses is still written, but it is named on stderr and the command exits 2. Import prints the JSON report
and, with `--out-dir`, writes the candidate `workflow.json` and `data.json` so they can go through `eija laws`,
`eija render` and `eija build`. Neither command changes a pack: keeping an import is an owner's decision.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`domain/data`](/modules/domain/data.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/pack`](/modules/domain/pack.md)
* [`domain/policy`](/modules/domain/policy.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [domain.data](/modules/domain/data.md) - The data model of a pack, shown as a UML class diagram (ADR-0153): entities, typed attributes and associations.
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.

## Referenced by

* [interfaces.cli](/modules/interfaces/cli.md) - Module `interfaces/cli` (no module docstring).
<!-- okf:generated:end links -->
