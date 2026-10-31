---
type: Quality Gate
title: nox -s providers_contract
description: Shared contract for codex/claude/opencode/gemini (mocked runner), tree-kill on real processes, HTTP providers (mock transport).
resource: repo://quality/sessions/providers.py#providers_contract
tags:
- gate
- fast
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/providers.py#providers_contract
  title: providers.py
  hash_method: ast-v2
  sha256: 5764c0b0789f3bdb268e1b8ca50422e3f9ddd6e7e9e6ab62c33cce6b031333f5
notes_baseline: e2c5a834f8e5a8c0608e4f5fdf15623686caf3dfa0b66d02979609c3043f1ac8
---

# nox -s providers_contract

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s providers_contract` |
| Tiers | `fast`, `full` |
| Session module | `repo://quality/sessions/providers.py` |
| Code | `repo://quality/sessions/providers.py#providers_contract` |

## Docstring

~~~text
Shared contract for codex/claude/opencode/gemini (mocked runner), tree-kill on real processes, HTTP providers (mock transport).

Needs the ``providers`` extra. Without psutil the reparented-descendant kill tests would SKIP and the gate would
report green without exercising the psutil path, so a missing psutil fails the session instead of passing it.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
