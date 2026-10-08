---
type: Quality Gate
title: nox -s pr_status
description: Pull-request states claimed in the roadmap and lane hubs equal GitHub's.
resource: repo://quality/sessions/oss.py#pr_status
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/oss.py#pr_status
  title: oss.py
  hash_method: ast-v2
  sha256: 8d9c6433b2556ad432a879710c83b244739b356402a4295fe1bfff3947969ffa
notes_baseline: 26b7b0d3a56d485726d623c95221abcba289c1f6025b9fe5fe627eb7af679c95
---

# nox -s pr_status

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s pr_status` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/oss.py` |
| Code | `repo://quality/sessions/oss.py#pr_status` |

## Docstring

~~~text
Pull-request states claimed in the roadmap and lane hubs equal GitHub's. NOT_RUN without `gh` and network.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
