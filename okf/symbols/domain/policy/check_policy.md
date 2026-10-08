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
  sha256: 9ca7b2de18533e6f28abd88a515f3dfa1b5528ed03d39a812e92ad86401135b4
description_override: Returns the sorted policy error codes of a workflow; an empty list means the model stays inside the protected excursion policy.
notes_baseline: 172de13737d848ef5e10c86c3294d9a43774a6b543068e153e34bd957b60b536
verified:
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: e4d9fc5fc96451b56c4bda65da62b3a0c6a0800b09ecd5269faafd16a7a5f6d1
  sources_sha256: 172de13737d848ef5e10c86c3294d9a43774a6b543068e153e34bd957b60b536
---

# domain.policy.check_policy

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/policy`](/modules/domain/policy.md) |
| Signature | `def check_policy(model: Workflow, pack: Pack \| None=None) -> list[str]` |
| Code | `repo://src/eija_studio/domain/policy.py#check_policy` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Sorted, de-duplicated policy codes of ``model`` under the pack (empty means the model conforms).
~~~
<!-- okf:generated:end facts -->

## Notes

**Invariant.** The domain pack is the only definition of what a workflow may look like; this function is generic. It reports:
* `UNSUPPORTED_ACTION` for a transition whose action the pack does not declare;
* `GUARD_POLICY:<action>` / `EFFECT_POLICY:<action>` when a transition's guards or required effects differ from the declared action, or it does not declare every pack-forbidden effect forbidden;
* the code of every broken pack law ([domain.laws](/modules/domain/laws.md)): for the excursion pack `UNSUPPORTED_WORKFLOW_SHAPE`, `PROTECTED_AUTHORITY:<action>`, `PROTECTED_STATE:<action>`, `UNSUPPORTED_REJECTION_SOURCE`.

**What it establishes.** Structural conformance of one model to the pack. For the excursion pack the codes equal the pre-pack hand-written policy on the examples and on all 2572 SMT differential candidates (tests/test_pack.py), and a Z3 proof covers its transaction grammar ([SMT proof](/verification/smt-proof.md)). **What it does not.** That the pack's laws are the right laws.

Used by [ensure_policy](/symbols/domain/policy/ensure_policy.md), which turns findings into a `POLICY_BLOCKED` error with `{codes, refs}`, and by the compiler's review packet.

<!-- okf:generated:begin links -->
## Depends on

* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.policy.declared_codes](/symbols/domain/policy/declared_codes.md) - Every transition must perform a declared action, with exactly its declared guards and required effects, and must declare every pack-forbidden effect forbidden.
* [domain.policy.law_violations](/symbols/domain/policy/law_violations.md) - `def law_violations(model: Workflow, pack: Pack | None=None) -> list[Violation]` in `domain/policy`.

## Referenced by

* [application.appgen.generate](/symbols/application/appgen/generate.md) - Return the per-model files and the build manifest (without file hashes or test results).
* [application.compiler.compile_case](/symbols/application/compiler/compile_case.md) - `def compile_case(case: ChangeCase, identity: dict[str, Any], authenticator: Callable[[dict[str, Any]], bool],…` in `application/compiler`.
* [application.diagrams.policy_violations](/symbols/application/diagrams/policy_violations.md) - Codes `domain.policy.check_policy` reports for `workflow` (empty: the protected policy accepts it).
* [application.law_proof.prove_laws](/symbols/application/law_proof/prove_laws.md) - Every law of the pack, judged on `model` (the pack's own by default), with the evidence for each verdict.
* [application.scxml.to_scxml](/symbols/application/scxml/to_scxml.md) - The model as an SCXML document.
* [application.service.Studio.formal_view](/symbols/application/service/Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [domain.policy.ensure_policy](/symbols/domain/policy/ensure_policy.md) - `def ensure_policy(model: Workflow, pack: Pack | None=None) -> None` in `domain/policy`.
<!-- okf:generated:end links -->
