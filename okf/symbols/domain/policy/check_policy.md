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
  hash_method: ast-v2
  sha256: 228e5d92eb7d7b3724d0e5fa681689a13ce9e856eaff4c5287b09930b30b510d
description_override: Returns the sorted policy error codes of a workflow; an empty list means the model stays inside the protected excursion policy.
notes_baseline: f259ee95657957c18bba38a4bb459a633a66198276d2941a63108c5028ca8856
---

# domain.policy.check_policy

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def check_policy(model: Workflow) -> list[str]` |
| Code | `repo://src/eija_studio/domain/policy.py#check_policy` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

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

* [domain.models.BASE_GUARDS](/symbols/domain/models/BASE_GUARDS.md) - Constant `BASE_GUARDS` in `domain/models`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.policy.EFFECTS](/symbols/domain/policy/EFFECTS.md) - Constant `EFFECTS` in `domain/policy`.
* [domain.policy.FORBIDDEN](/symbols/domain/policy/FORBIDDEN.md) - Constant `FORBIDDEN` in `domain/policy`.

## Referenced by

* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.diagrams.policy_violations](/symbols/application/diagrams/policy_violations.md) - Codes `domain.policy.check_policy` reports for `workflow` (empty: the protected policy accepts it).
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow) -> None` in `domain/policy`.
<!-- okf:generated:end links -->
