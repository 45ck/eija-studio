---
type: Module
title: interfaces.mcp_server
description: 'MCP (Model Context Protocol) adapter: the agent-facing face of EIJA Studio.'
resource: repo://src/eija_studio/interfaces/mcp_server.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/mcp_server.py
  title: interfaces/mcp_server.py
  hash_method: ast-api-v1
  sha256: 2bbf0a1e2c4cfac7ff7f34d8adbf359da9d0b6e6144ab0ba29ca7fa800653074
notes_baseline: 73edf76ae01fa26d72ebcaa68ef3db27c33c36814c3476d2841593deb7e490e6
---

# interfaces.mcp_server

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/mcp_server.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
MCP (Model Context Protocol) adapter: the agent-facing face of EIJA Studio.

Design in one paragraph. "AI proposes. The kernel checks. The local owner decides." The server exposes
only the operations an agent is allowed to perform: create a case, ask the configured provider for an
UNTRUSTED proposal, read derived views and repository links, dry-run a typed edit, and run the technical runtime verifier. It deliberately has no
tool that selects a meaning, edits the model, approves, applies, discards or previews-with-state. Those
are owner capabilities and stay in the browser Studio (``eija serve``).

The guarantee is ABSENCE, not a role check, in three layers: (1) the tool registry is asserted equal to
``AGENT_TOOLS``; (2) ``AgentSurface`` holds a narrow ``AgentPort`` and never the whole ``Studio``:
the typed surface has no owner method, and the port keeps the ``Studio`` only in a closure, so no chain of
ordinary attribute names (``port._studio.approve``, ``attrgetter``, ``methodcaller``) reaches it (a test walks
every non-dunder attribute path); (3) an AST lint (tests/test_agent_static.py, with a negative control that
only each rule catches) rejects owner-operation and store-write names on any receiver, ``OWNER``, dynamic
attribute access, object-internals dunders, ``operator``/``importlib``/``inspect`` imports, and the ``Studio``
class or instance used outside the port factory. Reaching past the port needs dunder or introspection
access, which layer 3 catches in the common spellings: it is a best-effort lint, not a proof, and the
adapter is not a sandbox. Nothing here "runs as" the AGENT principal: ``Studio.create``,
``propose`` and ``verify`` take no principal, so the kernel cannot tell an MCP caller from any other and the
audit log does not attribute these actions to an agent (kernel follow-up). If a new tool ever needed a
principal, that would be a governance change to ADR-0041, not an implementation detail.

Spend guard: ``--egress-consent`` is a STANDING consent set once at startup, so it covers every
``propose`` call in the session. ``max_provider_calls`` caps how many networked provider calls one
server session may make; the agent cannot change it.

What this module does NOT establish: it is a convenience and a guard rail, not a sandbox. An agent
with the same OS permissions as the owner can still read the workspace directly (see AGENTS.md).

The module is an interface adapter: it may import the application and domain layers and the vendor
SDK; nothing in ``domain`` or ``application`` imports it.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/service`](/modules/application/service.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`domain/transactions`](/modules/domain/transactions.md)
* [`interfaces/agent_config`](/modules/interfaces/agent_config.md)
* [`interfaces/agent_policy`](/modules/interfaces/agent_policy.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.service](/modules/application/service.md) - Module `application/service` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.transactions](/modules/domain/transactions.md) - Open change vocabulary (WBS 1.3): the semantic edits an owner (or a pack meaning) may make to a workflow.
* [interfaces.agent_config](/modules/interfaces/agent_config.md) - Copy-paste MCP client configuration for `eija mcp --print-config <client>`.
* [interfaces.agent_policy](/modules/interfaces/agent_policy.md) - SDK-free policy data for the agent adapter: which persistence operations an agent adapter must never touch.
<!-- okf:generated:end links -->
