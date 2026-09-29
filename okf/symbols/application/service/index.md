# Symbols of application.service

# Classes

* [application.service.Studio](Studio.md) - The Studio use cases: create, propose, select, edit, verify, approve, apply and execute over a Change Case.

# Functions

* [application.service.now](now.md) - `def now() -> str` in `application/service`.

# Methods

* [application.service.Studio.affordances](Studio.affordances.md) - Which single edits of the case's working model the kernel would accept (read-only).
* [application.service.Studio.apply](Studio.apply.md) - Applies an approved candidate to the local baseline only if an eligible, authentic, exact-subject decision exists.
* [application.service.Studio.approve](Studio.approve.md) - Seals a local-owner acknowledgement of the exact subject after eligibility, matching subject hash, acknowledged unknowns and correct answers.
* [application.service.Studio.create](Studio.create.md) - `def create(self, request: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.discard](Studio.discard.md) - `def discard(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.edit](Studio.edit.md) - `def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.edit_check](Studio.edit_check.md) - Dry-run one edit: {legal, codes, refs}.
* [application.service.Studio.execute](Studio.execute.md) - `def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] | None=None) -> dict[st…` in `application/service`.
* [application.service.Studio.export](Studio.export.md) - `def export(self, case_id: str) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.formal_view](Studio.formal_view.md) - Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision.
* [application.service.Studio.layout](Studio.layout.md) - `def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.propose](Studio.propose.md) - Asks the configured provider for an untrusted interpretation and records the run; networked providers need startup enablement and explicit consent.
* [application.service.Studio.reset_preview](Studio.reset_preview.md) - `def reset_preview(self, case_id: str, expected: int, state: str | None=None) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.save](Studio.save.md) - `def save(self, case_id: str, expected: int) -> dict[str, Any]` in `application/service`.
* [application.service.Studio.select](Studio.select.md) - Records the owner's explicit choice of one supported interpretation and derives the candidate workflow.
* [application.service.Studio.verify](Studio.verify.md) - Runs the runtime matrix in a sandbox and stores a sealed receipt; refuses a source that differs from the release fixture.
* [application.service.Studio.view](Studio.view.md) - `def view(self, case_id: str, scope: str='local-demo') -> dict[str, Any]` in `application/service`.
* [application.service.Studio.workflows](Studio.workflows.md) - Baseline and candidate of a case, for read-only projections (diagrams).
