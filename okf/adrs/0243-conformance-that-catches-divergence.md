---
type: Architecture Decision Record
title: 'ADR-0243: Conformance that catches a divergent app by behaviour'
description: The pitch for `eija build` (ADR-0150) is that the generated app's conformance tests prove the app matches its model.
resource: repo://docs/adr/0243-conformance-that-catches-divergence.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0243-conformance-that-catches-divergence.md
  title: 0243-conformance-that-catches-divergence.md
  hash_method: lf-sha256-v1
  sha256: bf0e4fbb467e2b7a3b4f5f02e8211f20ffe6b2785f14ed2af5070ed97fe79953
notes_baseline: 929124cb3d4de4431c32615d93a3fa111a6714a11991b5ea81f328856960bfe7
---

# ADR-0243: Conformance that catches a divergent app by behaviour

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-11-12 |
| Lane | app generation / verification |
| Source | `repo://docs/adr/0243-conformance-that-catches-divergence.md` |

## Decision outcome (verbatim)

> **The harness.** `python -m verification.conformance.divergence` builds, for every shipped pack and two feature variants, real apps that are wrong in exactly one way. It runs each one's generated tests in a fresh process, as `eija build` does. The two families:
>
> * **Model divergence.** The app is built from a model, data model or pack that differs in one element:
>   * a transition is dropped, moved to another source or target, or given another role;
>   * the assignment guard is added or dropped, or a required effect is added or dropped;
>   * a value guard is dropped or flipped;
>   * a time event is dropped or lengthened (ADR-0237);
>   * a received signal is dropped or heard from another sender (ADR-0242);
>   * a step on a linked object is dropped, a linked object starts in another state, or one of its moves leads elsewhere (ADR-0241);
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
* [ADR-0237: Time events on transitions](/adrs/0237-time-events.md) - Issue #93, item 2.
* [ADR-0241: Actions on linked objects](/adrs/0241-actions-on-linked-objects.md) - Issue #93, item 4.
* [ADR-0242: Messages between workflows](/adrs/0242-messages-between-workflows.md) - Issue #93, item 5.

## Referenced by

* [ADR-0249: Fixes from the inspection of the app generator](/adrs/0249-app-generator-inspection-fixes.md) - The 13 November 2026 inspection (record) found ten defects in the generated app and its conformance suite.
<!-- okf:generated:end links -->
