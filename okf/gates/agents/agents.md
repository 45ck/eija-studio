---
type: Quality Gate
title: nox -s agents
description: MCP tools/resources via the SDK's in-memory session and stdio start-up, plus the SDK-free static checks.
resource: repo://quality/sessions/agents.py#agents
tags:
- gate
- full
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://quality/sessions/agents.py#agents
  title: agents.py
  hash_method: ast-v2
  sha256: 8368ba7e61de2bf706f16d59a0bc59eca1c27b4d8a8256aafbc5caf030e79d72
notes_baseline: 346c4ddc108d465e934cb4eac3019227d9b30d94c7dce214429a8c8e1c7cf795
---

# nox -s agents

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Command | `nox -s agents` |
| Tiers | `full` |
| Session module | `repo://quality/sessions/agents.py` |
| Code | `repo://quality/sessions/agents.py#agents` |

## Docstring

~~~text
MCP tools/resources via the SDK's in-memory session and stdio start-up, plus the SDK-free static checks.

The SDK-free checks (owner-operation lint, config snippets, docs and skills drift) always run. The SDK tests
need the `agents` extra; without it the session runs the static checks and then SKIPS with a NOT_RUN reason:
nox reports a plain success as a pass, so a session whose MCP behaviour tests did not run must not end in one.
~~~

Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them).
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
