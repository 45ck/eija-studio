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
  sha256: 6f73a1a3faa64a0a510230bbb4ec8840dd6e171cb05a4611965826de5ac82517
notes_baseline: 788e754c69d5a4454e6e22e51630bdce5f1c070d7abb9db4cbda876fe3e3082f
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
