---
type: Quality Gate
title: nox -s hci_docs
description: 'Drift check (no browser): snapshot == derive(committed trace, current laws + budgets); REPORT.md == render(snapshot).'
resource: repo://quality/sessions/hci.py#hci_docs
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/hci.py#hci_docs
  title: hci.py
  hash_method: ast-v2
  sha256: 6f503ffe84f2ce08938d05476afa00abfea0255720cce79a39ad17feaa584c8b
notes_baseline: e9763db316bd6d28cf9d351790917c497a1b620b2798bb2ce66787cd498e9bca
---

# nox -s hci_docs

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s hci_docs` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/hci.py` |
| Code | `repo://quality/sessions/hci.py#hci_docs` |

## Docstring

~~~text
Drift check (no browser): snapshot == derive(committed trace, current laws + budgets); REPORT.md == render(snapshot).
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
