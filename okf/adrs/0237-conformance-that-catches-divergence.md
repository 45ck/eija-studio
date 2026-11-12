---
type: Architecture Decision Record
title: 'ADR-0237: Conformance that catches a divergent app by behaviour'
description: The pitch for `eija build` (ADR-0150) is that the generated app's conformance tests prove the app matches its model.
resource: repo://docs/adr/0237-conformance-that-catches-divergence.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0237-conformance-that-catches-divergence.md
  title: 0237-conformance-that-catches-divergence.md
  hash_method: lf-sha256-v1
  sha256: 317592c49820175c7e355336a4d3ef839588cd284bf62994c54b49b71ecbc2a0
notes_baseline: 8a4bb227107da6c0c86a38daba68040174b6beca04895271b3a8ac47d51d9fc9
---

# ADR-0237: Conformance that catches a divergent app by behaviour

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-12 |
| Lane | app generation / verification |
| Source | `repo://docs/adr/0237-conformance-that-catches-divergence.md` |

## Decision outcome (verbatim)

> **The harness.** `python -m verification.conformance.divergence` builds, for every shipped pack and two feature variants, real apps that are wrong in exactly one way. It runs each one's generated tests in a fresh process, as `eija build` does. The two families:
>
> * **Model divergence.** The app is built from a model, data model or pack that differs in one element:
>   * a transition is dropped, moved to another source or target, or given another role;
>   * the assignment guard is added or dropped, or a required effect is added or dropped;
>   * a value guard is dropped or flipped;
>   * the initial state is moved, or an initiator is added or dropped;
>   * an effect's kind or recipient is changed;
>   * a fixture actor's active or assigned flag is flipped;
>   * an attribute is dropped, retyped, made required or optional, given a shorter limit, or loses a choice;
>   * a built association is dropped, unbuilt or given another multiplicity;
>   * a separation-of-duties law is dropped.
>
>   The app keeps the reviewed oracle and tests. Only the identity fields (model hash, data and screens digests) are pointed at the divergent app, and the build identity is resealed, so only behaviour can fail the suite.
> * **Code divergence.** One of 23 seeded faults in `app/service.py` or `app/server.py`, resealed the same way. A fault in code a subject's app never reaches is not applicable to it, not missed. For example, a fault in the value-guard check applies only to a model with value guards.
>
> Each divergence ends up CAUGHT, REFUSED (no app is built: the model is invalid or the protected policy refuses it), EQUIVALENT, or MISSED. Only one kind of divergence may be EQUIVALENT: dropping a forbidden effect. The kernel performs only required effects, and the policy checks forbidden ones at build time. Any MISSED divergence fails the check. For each law, the harness also runs the law proof on every model divergence, and every divergence the proof finds BROKEN must be CAUGHT or REFUSED.
>
> The two feature variants exist only in the harness, so the shipped packs keep their bytes:
>

## Sections

* Context and problem statement
* Decision drivers
* Decision outcome

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://tests/test_appgen.py`
* `repo://tests/test_conformance_divergence.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Related decisions

* [ADR-0033: Mutation analysis with cosmic-ray, run natively on Windows](/adrs/0033-mutation-tool-selection.md) - The kernel test suite (88 tests at the start of this lane) passes, but a green suite says nothing about whether it would notice a wrong guard, a swapped role o…
* [ADR-0150: Build runnable apps from the model, checked against the kernel as oracle](/adrs/0150-build-apps-from-the-model-with-a-kernel-oracle.md) - The owner's goal, stated on 8 October 2026, is "UML you can trust to build apps".
* [ADR-0165: Executable UML on the EIJA kernel: one interpreter, a closed action vocabulary, SCXML as the standard cross-check](/adrs/0165-executable-uml-on-the-eija-kernel.md) - PlayIDE draws six UML views (state machine, class, use case, screens, component, sequence) over one model (ADR-0093), and `eija build` turns the model into a r…
* [ADR-0232: One action from several states](/adrs/0232-one-action-from-several-states.md) - Issue #148: `Workflow.coherent` refused a second transition with the same action, so each action labelled exactly one transition.
<!-- okf:generated:end links -->
