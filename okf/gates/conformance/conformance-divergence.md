---
type: Quality Gate
title: nox -s conformance_divergence
description: 'Seeded divergence on one pack and the feature variants: every one caught by behaviour, or refused.'
resource: repo://quality/sessions/conformance.py#conformance_divergence
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/conformance.py#conformance_divergence
  title: conformance.py
  hash_method: ast-v2
  sha256: 115922187772fd6195791353d774cba81b7d694ddefc36ceb51229db752fa507
notes_baseline: 7e0aae44e4883573c35219e13ee2b2fabab6ad743e95876376e4790a1866e7e6
---

# nox -s conformance_divergence

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s conformance_divergence` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/conformance.py` |
| Code | `repo://quality/sessions/conformance.py#conformance_divergence` |

## Docstring

~~~text
Seeded divergence on one pack and the feature variants: every one caught by behaviour, or refused.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
