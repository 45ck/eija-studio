---
type: Module
title: domain.signals
description: 'Signals between workflows (issue #93 item 5, ADR-0242): what makes a signal effect well formed.'
resource: repo://src/eija_studio/domain/signals.py
tags:
- module
- domain
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/signals.py
  title: domain/signals.py
  hash_method: ast-api-v1
  sha256: f188991bd783dbd3f5b49016edfcac39edcdf3ef149ab4cba6bdf21d4fec7860
notes_baseline: 04284d702d9da099a058a355eed30e2c92791b983d924fed768440605d631e26
---

# domain.signals

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | domain |
| Code | `repo://src/eija_studio/domain/signals.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Signals between workflows (issue #93 item 5, ADR-0242): what makes a signal effect well formed.

A signal is an effect named `Signal:Name` that one workflow's step writes to its outbox for another workflow of the
system, named by its pack id in `recipient`. The receiving workflow says which signals start a record there
(`Workflow.receives`); the system landscape checks that both ends agree.
~~~

## Public symbols

* [`SIGNAL`](/symbols/domain/signals/SIGNAL.md) (constant) - no docstring
* [`signal_problems`](/symbols/domain/signals/signal_problems.md) (function) - A signal is named Signal:Name and goes to another workflow; nothing else may take a signal's name.
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [domain.pack](/modules/domain/pack.md) - Domain pack: everything domain-specific the kernel needs, as one validated document (WBS 1.1).
* [domain.signals.SIGNAL](/symbols/domain/signals/SIGNAL.md) - Constant `SIGNAL` in `domain/signals`.
* [domain.signals.signal_problems](/symbols/domain/signals/signal_problems.md) - A signal is named Signal:Name and goes to another workflow; nothing else may take a signal's name.
<!-- okf:generated:end links -->
