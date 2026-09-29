---
type: Quality Gate
title: nox -s graph_rules_bench
description: 'ADR-0095 rule-language benchmark: four engines, four rules, agreement and timings (MEASUREMENT, one machine).'
resource: repo://quality/sessions/graph.py#graph_rules_bench
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/graph.py#graph_rules_bench
  title: graph.py
  hash_method: ast-v2
  sha256: b0b12fd6721affc07fe7863bcc1b1e4e8ca3413b6de470010c616a070feafe77
notes_baseline: a3f7ec06aa97c84c58daf5e6582db443bee395b6fde56a182c93618c883ed0da
---

# nox -s graph_rules_bench

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s graph_rules_bench` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/graph.py` |
| Code | `repo://quality/sessions/graph.py#graph_rules_bench` |

## Docstring

~~~text
ADR-0095 rule-language benchmark: four engines, four rules, agreement and timings (MEASUREMENT, one machine).

pySHACL is optional and reported NOT_RUN when missing. Runs serially; the toy Datalog evaluator and pySHACL are slow.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
