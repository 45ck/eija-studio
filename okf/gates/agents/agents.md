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
  sha256: c1a2df9f9869496133d69651247881b5f63a3836b5b828016c2035b9e2c2449b
notes_baseline: 856861aaf2086399587816059ba14f104272b11f369e7835575bd56dff478308
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
