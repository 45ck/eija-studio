---
type: Bounded Context
title: Execution
description: Owns Trusted fixture actor state, preview instances, command replay, committed effect intents
resource: repo://docs/architecture/ARCHITECTURE.md#execution
tags:
- ddd
- context-map
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#execution
  title: ARCHITECTURE.md
  hash_method: md-table-row-v1
  sha256: d5655a652840bcdbd3a01b720c57a358da9b956d7ebf3633befe8a53de641dc4
notes_baseline: 213e1247d4710528d80afabe3af8260299b0c4e245a3ce9396933855aa3599c0
---

# Execution

<!-- okf:generated:begin facts -->
## Owns

Trusted fixture actor state, preview instances, command replay, committed effect intents

## Published contracts

* [`Workflow`](/symbols/domain/models/Workflow.md)
* [`Transition`](/symbols/domain/models/Transition.md)
* [`ExecuteCommand`](/symbols/domain/models/ExecuteCommand.md)
* [`UnitOfWork`](/symbols/application/ports/UnitOfWork.md)

## Implementation

* [`domain/policy.py`](/modules/domain/policy.md)
* [`application/runtime.py`](/modules/application/runtime.md)

Source: context map row `repo://docs/architecture/ARCHITECTURE.md#execution`. These are responsibility boundaries inside a modular monolith, not separately deployed services.
<!-- okf:generated:end facts -->

## Notes

Where protected policy meets runtime: [check_policy](/symbols/domain/policy/check_policy.md) guards the model, [execute](/symbols/application/runtime/execute.md) commits behaviour.

<!-- okf:generated:begin links -->
## Published contracts

* [application.ports.UnitOfWork](/symbols/application/ports/UnitOfWork.md) - All mutations on this port commit together or roll back together.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models`.
* [domain.models.Transition](/symbols/domain/models/Transition.md) - `class Transition(Contract)` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.

## Implementing modules

* [application.runtime](/modules/application/runtime.md) - Generic execution algorithm; domain-specific policy stays in domain.policy.
* [domain.policy](/modules/domain/policy.md) - Protected excursion policy.
<!-- okf:generated:end links -->
