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
  sha256: eee81ba4e1c205ac4b396a1533a6fd1ddbfe3c9e9ec37564e0c38aaf2594b6c5
notes_baseline: 53341beb05a41a251b2e460f72a2a078e0e28d70fbb26b72edeab1daccea67f0
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
* [`application/law_proof`](/modules/application/law_proof.md)
* [`application/scenario_run`](/modules/application/scenario_run.md)
* [`application/scxml`](/modules/application/scxml.md)
* [`application/verifier`](/modules/application/verifier.md)
* [`bootstrap`](/modules/bootstrap.md)
* [`domain/impact`](/modules/domain/impact.md)
* [`domain/models`](/modules/domain/models.md)
* [`domain/policy`](/modules/domain/policy.md)
* [`domain/scenarios`](/modules/domain/scenarios.md)
* [`interfaces/agent_config`](/modules/interfaces/agent_config.md)
* [`interfaces/app_build`](/modules/interfaces/app_build.md)
* [`interfaces/play_systems`](/modules/interfaces/play_systems.md)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Imports

* [application.compiler](/modules/application/compiler.md) - Compiler: model → projections + impacts + obligations + computed review packet.
* [application.diagram_catalog](/modules/application/diagram_catalog.md) - Named diagram views over a baseline and an optional candidate Workflow.
* [application.law_proof](/modules/application/law_proof.md) - Prove a pack's laws over every run the kernel allows (ADR-0166).
* [application.scenario_run](/modules/application/scenario_run.md) - Run a pack's scenarios (its test cases) through the kernel, and record new ones (ADR-0177).
* [application.scxml](/modules/application/scxml.md) - The workflow state machine as a W3C SCXML statechart (ADR-0165).
* [application.verifier](/modules/application/verifier.md) - Bounded synthetic runtime experiments.
* [bootstrap](/modules/bootstrap.md) - The only composition root: wires application ports to concrete adapters.
* [domain.impact](/modules/domain/impact.md) - Module `domain/impact` (no module docstring).
* [domain.models](/modules/domain/models.md) - Module `domain/models` (no module docstring).
* [domain.policy](/modules/domain/policy.md) - Generic policy: coherence with a domain pack's declared action catalog, the pack's laws, and declared effects.
* [domain.scenarios](/modules/domain/scenarios.md) - Scenarios: a pack's test cases, written as stories a person can read and the kernel can run (ADR-0177).
* [interfaces.agent_config](/modules/interfaces/agent_config.md) - Copy-paste MCP client configuration for `eija mcp --print-config <client>`.
* [interfaces.app_build](/modules/interfaces/app_build.md) - `eija build`: write a runnable app generated from a pack's model, then run its kernel conformance tests (ADR-0150).
* [interfaces.play_systems](/modules/interfaces/play_systems.md) - PlayIDE's systems (ADR-0185): start a new system from a sketch or a template, open one you made before, and save the work in progress to carry on later.
<!-- okf:generated:end links -->
