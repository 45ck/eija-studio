---
type: Quality Gate
title: nox -s mutation_quick
description: Authority-core mutation run (policy.py, two workers, a few minutes) gated by the ratchet floor.
resource: repo://quality/sessions/mutation.py#mutation_quick
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/mutation.py#mutation_quick
  title: mutation.py
  hash_method: ast-v2
  sha256: 78572eb775d764e0260aa38e0b635d70539b2cfc8eebb3a35e588a6c92bb6cee
notes_baseline: d81626acbe40db790aed3eafd8f15bc3fe1087455e79c0a17188e94c73196cd4
---

# nox -s mutation_quick

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s mutation_quick` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/mutation.py` |
| Code | `repo://quality/sessions/mutation.py#mutation_quick` |

## Docstring

~~~text
Authority-core mutation run (policy.py, two workers, a few minutes) gated by the ratchet floor.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
