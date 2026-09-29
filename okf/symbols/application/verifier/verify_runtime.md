---
type: Function
title: application.verifier.verify_runtime
description: Runs the declared actor x state x action matrix against the real runtime in a disposable sandbox and returns the artifact a receipt is built from.
resource: repo://src/eija_studio/application/verifier.py#verify_runtime
tags:
- symbol
- application
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/application/verifier.py#verify_runtime
  title: application/verifier.py
  hash_method: ast-v2
  sha256: 8452f395c4b9f2584b0f8fe9775d3b147f611951072e44c923ce32ebd6dfde92
description_override: Runs the declared actor x state x action matrix against the real runtime in a disposable sandbox and returns the artifact a receipt is built from.
notes_baseline: 4068a80e4e9f93b8598cf14f45dbfa6f5a17ec66fc09a7d7a7514d7db66ed786
verified:
- by: process:claude-code-integration-phase0
  at: '2026-09-29T04:30:00Z'
  notes_sha256: c279d71ea83dd758ba400cd80b60beab9840befee12261208b61a9114f87b078
  sources_sha256: 69b11e45b44825932c35593230a3bd5de4720cdfec8912cdebfed5959d931fdb
- by: process:eija-wbs-1.3-agent
  at: '2026-09-29T08:20:47Z'
  notes_sha256: ae41a14b066723067fde150de45124d29aab995e31cfc9a3df16d86d2534abad
  sources_sha256: 4068a80e4e9f93b8598cf14f45dbfa6f5a17ec66fc09a7d7a7514d7db66ed786
---

# application.verifier.verify_runtime

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/verifier`](/modules/application/verifier.md) |
| Signature | `def verify_runtime(model: Workflow, subject: dict[str, Any], sandbox: SandboxFactory, pack: Pack \| None=None) -> dict[str, Any]` |
| Code | `repo://src/eija_studio/application/verifier.py#verify_runtime` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

One cell per fixture actor x model state x declared action of the pack (the excursion candidate: 5 x 5 x 5 = 125; the library-loan baseline: 5 x 5 x 6 = 150), each executed through [execute](/symbols/application/runtime/execute.md) in the sandbox from [SandboxFactory](/symbols/application/ports/SandboxFactory.md) and compared with an expected outcome read from the model's transition table and the pack's fixture directory (active, role, assignment guard, typed effect counts).

**Honest limits.** The expectation is computed separately from the runtime's guard evaluation but reads the same model and pack: it checks the runtime against the declared table, not against an independently derived policy. The cells are one-step experiments, not a theorem about arbitrary histories. A sandbox observes transaction semantics, not crash durability. See [Bounded runtime matrix](/verification/integration-test.md) and acceptance [AC12](/requirements/ac12.md).

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.SandboxFactory](/symbols/application/ports/SandboxFactory.md) - Type alias `SandboxFactory` in `application/ports`.
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models`.
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models`.
* [domain.pack.Pack](/symbols/domain/pack/Pack.md) - `class Pack(Contract)` in `domain/pack`.
* [domain.pack.default_pack](/symbols/domain/pack/default_pack.md) - The configured pack (cached per location).

## Referenced by

* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [Bounded runtime matrix (integration_test)](/verification/integration-test.md) - Implemented: Every cell of a declared actor x state x action matrix, run against the real runtime in a sandbox, matched a hand-written oracle that is partly de…
<!-- okf:generated:end links -->
