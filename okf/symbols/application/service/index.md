# Symbols of application.service

# Class

* [application.service.Studio](Studio.md) - The Studio use cases: create, propose, select, edit, verify, approve, apply and execute over a Change Case.

# Functions

* [application.service.now](now.md) - `def now() -> str` in `application/service` (the source has no docstring).

# Methods

* [application.service.Studio.apply](Studio.apply.md) - Applies an approved candidate to the local baseline only if an eligible, authentic, exact-subject decision exists.
* [application.service.Studio.approve](Studio.approve.md) - Seals a local-owner acknowledgement of the exact subject after eligibility, matching subject hash, acknowledged unknowns and correct answers.
* [application.service.Studio.create](Studio.create.md) - `def create(self, request: str) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio.discard](Studio.discard.md) - `def discard(self, case_id: str, expected: int) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio.edit](Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: SemanticTransaction, principal: Principal) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio.execute](Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault=None) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio.export](Studio.export.md) - `def export(self, case_id: str) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio.layout](Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio.propose](Studio.propose.md) - Asks the configured provider for an untrusted interpretation and records the run; networked providers need startup enablement and explicit consent.
* [application.service.Studio.reset_preview](Studio.reset_preview.md) - `def reset_preview(self, case_id: str, expected: int, state: str | None=None) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio.save](Studio.save.md) - `def save(self, case_id: str, expected: int) -> dict` in `application/service` (the source has no docstring).
* [application.service.Studio.select](Studio.select.md) - Records the owner's explicit choice of one supported interpretation and derives the candidate workflow.
* [application.service.Studio.verify](Studio.verify.md) - Runs the runtime matrix in a sandbox and stores a sealed receipt; refuses a source that differs from the release fixture.
* [application.service.Studio.view](Studio.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict` in `application/service` (the source has no docstring).
