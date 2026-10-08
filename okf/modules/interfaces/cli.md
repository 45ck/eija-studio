---
type: Module
title: interfaces.cli
description: Module `interfaces/cli` (no module docstring).
resource: repo://src/eija_studio/interfaces/cli.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/cli.py
  title: interfaces/cli.py
  hash_method: ast-api-v1
  sha256: ebfd1f8c63c3f0ddd8455aca7aeb6d5b705767a16a63afb9f574b08f917d2f53
notes_baseline: f1fd2ebe3cc1c7ed299c81b74a59866cb4dae06458db30b71c8930cf9e2cef2e
---

# interfaces.cli

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/cli.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

_The source carries no module docstring._

## Public symbols

_Symbol pages are generated for the domain and application layers only._

## Internal imports

* [`application/compiler`](/modules/application/compiler.md)
* [`application/diagram_catalog`](/modules/application/diagram_catalog.md)
* [`application/scxml`](/modules/application/scxml.md)
* [`application/verifier`](/modules/application/verifier.md)
* [`bootstrap`](/modules/bootstrap.md)
* [`domain/impact`](/modules/domain/impact.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`interfaces/agent_config`](/modules/interfaces/agent_config.md)
* [`interfaces/app_build`](/modules/interfaces/app_build.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.diagram_catalog](/modules/application/diagram_catalog.md) - Named diagram views over a baseline and an optional candidate Workflow.
* [application.scxml](/modules/application/scxml.md) - The workflow state machine as a W3C SCXML statechart (ADR-0160).
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
* [domain.impact](/modules/domain/impact.md) - Module `domain/impact` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [interfaces.agent_config](/modules/interfaces/agent_config.md) - Copy-paste MCP client configuration for `eija mcp --print-config <client>`.
* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
<!-- okf:generated:end links -->
