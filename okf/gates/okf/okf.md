---
type: Quality Gate
title: nox -s okf
description: OKF v0.2 conformance, internal links, code-link hashes (STALE), coverage and generator drift.
resource: repo://quality/sessions/okf.py#okf
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/okf.py#okf
  title: okf.py
  hash_method: ast-v1
  sha256: 715797a06dfe6b5f48d93b43b04fe6bc3df1b48745cdcc0b73661e2405cbc9d6
---

# nox -s okf

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s okf` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/okf.py` |
| Code | `repo://quality/sessions/okf.py#okf` |

## Docstring

~~~text
OKF v0.2 conformance, internal links, code-link hashes (STALE), coverage and generator drift.

Fix a STALE or DRIFT finding by reviewing the listed pages and running `python -m quality.okf sync`.
A PASS establishes that the wiki is well-formed and baselined against today's code, not that any
page's prose is correct. Missing tooling reports NOT_RUN (a skipped session), never PASS.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

Same findings without the pytest step: `python -m quality.okf check`. How the checks work and which are stricter than the specification: `repo://docs/knowledge-base.md`.

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
