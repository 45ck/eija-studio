---
type: Quality Gate
title: nox -s okf_tools
description: 'Tests of the OKF tooling itself: hash normalisation, marker-preserving regeneration, and a negative control per check.'
resource: repo://quality/sessions/okf.py#okf_tools
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/okf.py#okf_tools
  title: okf.py
  hash_method: ast-v1
  sha256: 5beb81a8036a5af9c7884fc4880529ff3d86078e563d10892152e4811c74f31a
---

# nox -s okf_tools

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s okf_tools` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/okf.py` |
| Code | `repo://quality/sessions/okf.py#okf_tools` |

## Docstring

~~~text
Tests of the OKF tooling itself: hash normalisation, marker-preserving regeneration, and a negative control per check.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

Run one file with `nox -s okf_tools -- quality/okf/tests/test_okf_codelink.py`. The tests live outside `tests/` so the kernel suite `pytest -q` needs no extra dependencies.

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
