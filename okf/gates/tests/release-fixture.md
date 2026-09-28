---
type: Quality Gate
title: nox -s release_fixture
description: 'Owner-only release gate: current bytes must match the owner-stamped fixture.'
resource: repo://quality/sessions/tests.py#release_fixture
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/tests.py#release_fixture
  title: tests.py
  hash_method: ast-v2
  sha256: 585844778a85efd5ae113077968e86dbc5b0dab67d7b564469c3593fa4c4c6e2
notes_baseline: aee7f00fc5f773552a15a9b315acd805d9851df53f7ced54efa69bec8b90eb6e
---

# nox -s release_fixture

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s release_fixture` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/tests.py` |
| Code | `repo://quality/sessions/tests.py#release_fixture` |

## Docstring

~~~text
Owner-only release gate: current bytes must match the owner-stamped fixture. Agents never stamp.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
