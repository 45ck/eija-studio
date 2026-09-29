---
type: Quality Gate
title: nox -s hci_snapshot_fresh
description: 'Release tier: the committed HCI evidence must describe the CURRENT UI bytes (strict drift check, no browser).'
resource: repo://quality/sessions/hci.py#hci_snapshot_fresh
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/hci.py#hci_snapshot_fresh
  title: hci.py
  hash_method: ast-v2
  sha256: 74d1f59836610a99f2e9b1b6d14295dc350ed9b45ae30d35cee1f50f848f8beb
notes_baseline: 03401f28fc9459ebba8f12f7d1b648611774347f0da1500e4411581e2cea8471
---

# nox -s hci_snapshot_fresh

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s hci_snapshot_fresh` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/hci.py` |
| Code | `repo://quality/sessions/hci.py#hci_snapshot_fresh` |

## Docstring

~~~text
Release tier: the committed HCI evidence must describe the CURRENT UI bytes (strict drift check, no browser).

The fast `hci_docs` gate only notes a stale UI hash, because the visual lane legitimately changes the UI first
and refreshes evidence after; a release must not ship evidence about UI bytes that no longer exist.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
