---
type: Quality Gate
title: nox -s graph_rules
description: 'ADR-0095: validate graph/rules/catalogue.json (strata, relations, messages, metamodel agreement) and run its oracles.'
resource: repo://quality/sessions/graph.py#graph_rules
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/graph.py#graph_rules
  title: graph.py
  hash_method: ast-v2
  sha256: 50eec6a011df64191334e33f2820a90004133e4b37cb48db8aa59844b12703d1
notes_baseline: c454020efd196e23316d35dbd973eb4c17f81de021d5dfefc2a4068e8d8b2896
---

# nox -s graph_rules

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s graph_rules` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/graph.py` |
| Code | `repo://quality/sessions/graph.py#graph_rules` |

## Docstring

~~~text
ADR-0095: validate graph/rules/catalogue.json (strata, relations, messages, metamodel agreement) and run its oracles.

The SARIF schema check and the pySHACL cross-check skip (NOT_RUN) when the OASIS schema or pyshacl is absent.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
