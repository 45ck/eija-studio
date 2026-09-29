---
type: Quality Gate
title: nox -s audit
description: pip-audit of the measured runtime pins (requirements-tested.txt) against the PyPI advisory database.
resource: repo://quality/sessions/quality.py#audit
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/quality.py#audit
  title: quality.py
  hash_method: ast-v2
  sha256: 93a04efde670c9c54ab8df11aac1c963437c7caa395b825b719a985f3b498c1b
notes_baseline: 82732a96127a2882d95518b747b99660165a463b96b56f5f1e776142895e0869
---

# nox -s audit

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s audit` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/quality.py` |
| Code | `repo://quality/sessions/quality.py#audit` |

## Docstring

~~~text
pip-audit of the measured runtime pins (requirements-tested.txt) against the PyPI advisory database.

Needs network. Without it the session FAILS with a NOT_RUN message: nox turns `session.skip()` into
exit 0, and a success status for an unchecked tree would be PASS by status. Set EIJA_ALLOW_NOT_RUN=1 to
accept the gap explicitly (the session then skips and still prints NOT_RUN). The probe is a TCP connect
to pypi.org:443, so it does not prove the advisory API answers; pip-audit's own network error also fails.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
