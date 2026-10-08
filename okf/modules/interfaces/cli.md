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
  sha256: 156059e57b54e0c030b8fe2354fc9e42a95d74a348c8eae5de5577695adb3086
notes_baseline: 6c954d83a41bd7d9ae1ca6a492bbfdcc2a820b4f186ac50d128f95ea791221b0
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
* [`interfaces/uml_interop`](/modules/interfaces/uml_interop.md)
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
* [interfaces.uml_interop](/modules/interfaces/uml_interop.md) - `eija uml export` and `eija uml import`: UML interchange from the command line (ADR-0190).
<!-- okf:generated:end links -->
