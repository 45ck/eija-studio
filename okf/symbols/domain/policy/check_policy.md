---
type: Function
title: domain.policy.check_policy
description: Returns the sorted policy error codes of a workflow; an empty list means the model stays inside the protected excursion policy.
resource: repo://src/eija_studio/domain/policy.py#check_policy
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/policy.py#check_policy
  title: domain/policy.py
  hash_method: ast-v1
  sha256: 8761653b64b4d8caba35419d13edf173ec20ad66604b73eade9246ccedeacfcb
description_override: Returns the sorted policy error codes of a workflow; an empty list means the model stays inside the protected excursion policy.
---

# domain.policy.check_policy

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def check_policy(model: Workflow) -> list[str]` |
| Code | `repo://src/eija_studio/domain/policy.py#check_policy` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

**Invariant.** The protected policy is the only definition of what an excursion workflow may look like. Roles, source and target states, mandatory guards and required/forbidden effects of every transition are compared with fixed expectations, so a candidate cannot gain authority by editing the model or by an AI proposal.

* Candidate detection: a workflow with a `Recommend` transition is a *candidate* and must have exactly the five actions and five states; otherwise exactly the four baseline actions and states. Anything else is `UNSUPPORTED_WORKFLOW_SHAPE`.
* `Approve` moves to `Approved` and must be the Registrar's; `Recommend` is the Teacher's and additionally needs the `actor_assigned` guard. A Teacher can never approve: `PROTECTED_AUTHORITY:<action>`.
* `Reject` may start from `Submitted` or `Recommended` (the one owner-selectable parameter, see [apply_transaction](/symbols/domain/policy/apply_transaction.md)); any other source is `UNSUPPORTED_REJECTION_SOURCE`.
* Every transition must carry [FORBIDDEN](/symbols/domain/policy/FORBIDDEN.md) effects and exactly the required effects in [EFFECTS](/symbols/domain/policy/EFFECTS.md).

**What it establishes.** Structural conformance of one model to this policy. **What it does not.** Soundness over the whole transaction grammar (a planned [SMT proof](/verification/smt-proof.md)), or anything about another domain: the policy deliberately rejects arbitrary domains.

Used by [ensure_policy](/symbols/domain/policy/ensure_policy.md), which turns findings into a `POLICY_BLOCKED` error, and by the compiler's review packet.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.BASE_GUARDS](/symbols/domain/models/BASE_GUARDS.md) - `BASE_GUARDS: tuple[Guard, ...] = ('actor_active', 'role_current', 'state_equals', 'expected_version', 'operation_binding')` in `domain/models` (the source has…
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).
* [domain.policy.EFFECTS](/symbols/domain/policy/EFFECTS.md) - `EFFECTS = {'Submit': ('Audit:ExcursionSubmitted',), 'Recommend': ('Audit:ExcursionRecommended', 'Notification:RegistrarQueued'), 'Approve': ('Audit:E…` in `do…
* [domain.policy.FORBIDDEN](/symbols/domain/policy/FORBIDDEN.md) - `FORBIDDEN = ('PaymentCaptured', 'ParentDataExported')` in `domain/policy` (the source has no docstring).

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict, authenticator, active_version: int, scope: str='local-demo') -> dict` in `application/compiler` (the source…
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow) -> None` in `domain/policy` (the source has no docstring).
<!-- okf:generated:end links -->
