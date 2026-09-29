---
type: Quality Gate
title: nox -s providers_doctor
description: Local, offline diagnostic of every CLI provider (version, flags, official login status).
resource: repo://quality/sessions/providers.py#providers_doctor
tags:
- gate
- release
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/providers.py#providers_doctor
  title: providers.py
  hash_method: ast-v2
  sha256: d5246f8a009fe727f58f2b2322becaed6e95d38367d4c2248097447e893fdb95
notes_baseline: c892f7674078cbef3745027bea70fa3f8f5c4c59d2e1d322d2f2425b04501607
---

# nox -s providers_doctor

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s providers_doctor` |
| Tiers | `release` |
| Session module | `repo://quality/sessions/providers.py` |
| Code | `repo://quality/sessions/providers.py#providers_doctor` |

## Docstring

~~~text
Local, offline diagnostic of every CLI provider (version, flags, official login status). A missing CLI or login is NOT_RUN, never PASS.

``READY (login unverified)`` (Gemini) means a call may be attempted; the CLI has no login-status command to confirm it.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
