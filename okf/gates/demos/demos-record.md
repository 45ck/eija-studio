---
type: Quality Gate
title: nox -s demos_record
description: 'Maintainer-only: record the scenarios (slow, needs Chrome and a free display/CPU).'
resource: repo://quality/sessions/demos.py#demos_record
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/demos.py#demos_record
  title: demos.py
  hash_method: ast-v2
  sha256: 26ed1430afe9177bfdb652e251719469915ffea6b8a70ed900c6cc38e60aa338
notes_baseline: aa11992386e249ead156528a16665c443369ee5bd79d3ee097d6630680a11412
---

# nox -s demos_record

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s demos_record` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/demos.py` |
| Code | `repo://quality/sessions/demos.py#demos_record` |

## Docstring

~~~text
Maintainer-only: record the scenarios (slow, needs Chrome and a free display/CPU).
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
