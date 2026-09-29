---
type: Quality Gate
title: nox -s graph_metamodel
description: 'ADR-0089: the generated schemas match metamodel.json, the metamodel tables are coherent, and the fast identity checks hold.'
resource: repo://quality/sessions/graph.py#graph_metamodel
tags:
- gate
- fast
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/graph.py#graph_metamodel
  title: graph.py
  hash_method: ast-v2
  sha256: cdf88a83c55ff435428b85500b41f622e7076f1de728a91327bfddbcf83688bb
notes_baseline: ff2b99dbc779ff27afb5d440aaf378e6c18306598f5e8dbf5ad13317c987ee49
---

# nox -s graph_metamodel

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s graph_metamodel` |
| Tiers | `fast` |
| Session module | `repo://quality/sessions/graph.py` |
| Code | `repo://quality/sessions/graph.py#graph_metamodel` |

## Docstring

~~~text
ADR-0089: the generated schemas match metamodel.json, the metamodel tables are coherent, and the fast identity checks hold.

Skips the hash-seed subprocess test (about 30 s); `graph_metamodel_full` runs it. Without jsonschema or rfc8785 the affected
tests skip and the output names NOT_RUN.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
