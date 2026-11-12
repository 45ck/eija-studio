---
type: Quality Gate
title: nox -s conformance_divergence_all
description: Seeded divergence on every shipped pack and feature variant.
resource: repo://quality/sessions/conformance.py#conformance_divergence_all
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/conformance.py#conformance_divergence_all
  title: conformance.py
  hash_method: ast-v2
  sha256: 09af86de23d5016023c7d5928b640929ea83df21a3d0fa4e0206a67d21dc212c
notes_baseline: 324c31ba6ab7610d18939d15ed89f40c2a7c101821df1941b01cbf64a860a575
---

# nox -s conformance_divergence_all

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s conformance_divergence_all` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/conformance.py` |
| Code | `repo://quality/sessions/conformance.py#conformance_divergence_all` |

## Docstring

~~~text
Seeded divergence on every shipped pack and feature variant.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
