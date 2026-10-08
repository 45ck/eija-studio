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
  sha256: 513f9c9bdbe5a51097931c16bc79f61900a7aeb38e973ba2e327e5dee6dc3d9e
notes_baseline: ada7e6966e37bc92e2303f0c38560abbb25108b281b70fda8716450c84471c76
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
