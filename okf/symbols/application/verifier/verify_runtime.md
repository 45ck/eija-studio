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
  hash_method: ast-v1
  sha256: 965a4eb4528fcf9567dc290edea1908cb359c250790f614edbf74089cd33e34a
description_override: Runs the declared actor x state x action matrix against the real runtime in a disposable sandbox and returns the artifact a receipt is built from.
---

# application.verifier.verify_runtime

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`application/verifier`](/modules/application/verifier.md) |
| Signature | `def verify_runtime(model: Workflow, subject: dict, sandbox: SandboxFactory) -> dict` |
| Code | `repo://src/eija_studio/application/verifier.py#verify_runtime` |
| Hash | `ast-v1` over the normalised AST (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

125 cells for a candidate (100 for the baseline), each executed through [execute](/symbols/application/runtime/execute.md) in the sandbox from [SandboxFactory](/symbols/application/ports/SandboxFactory.md), compared with an expected outcome from [ORACLE](/symbols/application/verifier/ORACLE.md).

**Honest limits.** The oracle is hand-written by the same author as the runtime and shares the policy requirements: it is not an independent oracle. The cells are one-step experiments, not a theorem about arbitrary histories. A sandbox observes transaction semantics, not crash durability. See [Bounded runtime matrix](/verification/integration-test.md) and acceptance [AC12](/requirements/ac12.md).

<!-- okf:generated:begin links -->
## Depends on

* [application.ports.SandboxFactory](/symbols/application/ports/SandboxFactory.md) - `SandboxFactory = Callable[[], ContextManager[Repository]]` in `application/ports` (the source has no docstring).
* [application.runtime.execute](/symbols/application/runtime/execute.md) - `def execute(session: UnitOfWork, case_id: str, model: Workflow, command: ExecuteCommand, *, fault=None) -> dict` in `application/runtime` (the source has no d…
* [application.runtime.initialise](/symbols/application/runtime/initialise.md) - `def initialise(session: UnitOfWork, case_id: str, model: Workflow, *, state: str | None=None) -> dict` in `application/runtime` (the source has no docstring).
* [application.verifier.ACTORS](/symbols/application/verifier/ACTORS.md) - `ACTORS = [('teacher-assigned', 'Teacher', True, True), ('teacher-unassigned', 'Teacher', True, False), ('teacher-revoked', 'Teacher', False, True), (…` in `ap…
* [application.verifier.ORACLE](/symbols/application/verifier/ORACLE.md) - `ORACLE = {'Submit': ('Teacher', 'Draft', 'Submitted'), 'Recommend': ('Teacher', 'Submitted', 'Recommended'), 'Approve': ('Registrar', 'Recommended',…` in `app…
* [domain.models.DomainError](/symbols/domain/models/DomainError.md) - Stable error code: never expose provider secrets or arbitrary exception text.
* [domain.models.ExecuteCommand](/symbols/domain/models/ExecuteCommand.md) - `class ExecuteCommand(Contract)` in `domain/models` (the source has no docstring).
* [domain.models.Workflow](/symbols/domain/models/Workflow.md) - `class Workflow(Contract)` in `domain/models` (the source has no docstring).
* [domain.models.fingerprint](/symbols/domain/models/fingerprint.md) - `def fingerprint(value: Any) -> str` in `domain/models` (the source has no docstring).

## Referenced by

* [application.service.Studio.verify](/symbols/application/service/Studio.verify.md) - `def verify(self, case_id: str, expected: int) -> dict` in `application/service` (the source has no docstring).
* [Bounded runtime matrix (integration_test)](/verification/integration-test.md) - Every cell of a declared actor x state x action matrix, run against the real runtime in a disposable sandbox, matched a separately written expected outcome; th…
<!-- okf:generated:end links -->
