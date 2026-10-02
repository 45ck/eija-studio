from __future__ import annotations
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Callable
from uuid import uuid4
import time
from pydantic import ValidationError
from eija_studio.domain.models import Workflow, Principal, LayoutChange, ExecuteCommand, DomainError, fingerprint
from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.pack import Pack, default_pack
from eija_studio.domain.policy import apply_transaction, apply_transactions, check_policy, meaning_options
from eija_studio.domain.affordance import affordances as affordance_map, dry_run
from eija_studio.domain.transactions import Transaction
from eija_studio.domain.formal import Context
from .ports import ProposalProvider, Repository, ReceiptAuthenticator, IdentityProvider, SandboxFactory, UnitOfWork, FormalEvidenceSource
from .formal import attach as attach_formal, packet_view, what_if_model
from .compiler import compile_case, subject_for
from .verifier import verify_runtime
from .runtime import initialise, execute
from .repository import RepositorySource
from .history import command_event, history_view, replay


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_case(body: dict[str, Any]) -> ChangeCase:
    """A stored case; one written in the closed pre-pack transaction vocabulary is refused, never migrated silently."""
    try:
        return ChangeCase.model_validate(body)
    except ValidationError as error:
        if any(e.get("loc", ())[:1] in (("transactions",), ("redo_transactions",)) for e in error.errors()):
            raise DomainError("CASE_SCHEMA_OLD", "This case was written by an older kernel; create a new Change Case") from None
        raise


class Studio:
    def __init__(self, store: Repository, provider: ProposalProvider, signer: ReceiptAuthenticator, identity_provider: IdentityProvider, sandbox: SandboxFactory, *, allow_network: bool = False,
                 formal: FormalEvidenceSource | None = None, pack: Pack | None = None,
                 repository: RepositorySource | None = None):
        self.pack = pack if pack is not None else default_pack()  # the domain: laws, meanings, fixtures
        self.formal = formal  # optional: without it the formal kinds stay UNKNOWN in the packet, never green
        self.store, self.provider, self.signer = store, provider, signer
        self.identity_provider, self.sandbox = identity_provider, sandbox
        self.allow_network, self._provider_lock = allow_network, Lock()
        self.repository = repository

    def workbench(self) -> dict[str, Any]:
        """Current pack declarations and baseline, with separately labelled read-only repository facts."""
        with self.store.transaction() as u:
            active = u.active()
        return {"pack": {"id": self.pack.id, "name": self.pack.pack.name, "version": self.pack.pack.version,
                         "digest": self.pack.digest},
                "language": self.pack.language.model_dump(mode="json"),
                "roles": [role.model_dump(mode="json") for role in self.pack.roles],
                "laws": [law.model_dump(mode="json") for law in self.pack.laws],
                "model": active["model"], "baseline_version": active["version"],
                "connection": self.repository.snapshot() if self.repository is not None else None,
                "source_review_required": not self.identity_provider()["trusted_fixture"]}

    def repository_impact(self, term: str, *, expected_source_hash: str | None = None) -> dict[str, Any]:
        """Known repository links only. This neither edits the repository nor grants evidence or authority."""
        if self.repository is None:
            return {"status": "unconfigured", "reason": "Start with --repo PATH to inspect a local repository"}
        return self.repository.impact(term, expected_source_hash=expected_source_hash)

    def repository_source(self, reference: str, *, expected_source_hash: str | None = None) -> dict[str, Any]:
        """Bounded source view from the configured repository's captured nodes; no arbitrary path or execution."""
        if self.repository is None:
            return {"status": "unconfigured", "reason": "Start with --repo PATH to inspect a local repository"}
        return self.repository.read_source(reference, expected_source_hash=expected_source_hash)

    def repository_freshness(self, expected_source_hash: str) -> dict[str, Any]:
        """Observe captured byte identity; this grants no source conformance, evidence or owner authority."""
        if self.repository is None:
            return {"status": "unconfigured", "reason": "Start with --repo PATH to inspect a local repository"}
        return self.repository.freshness(expected_source_hash=expected_source_hash)

    @staticmethod
    def _case(u: UnitOfWork, case_id: str, expected: int | None = None, editable: bool = False) -> ChangeCase:
        c = _parse_case(u.load_case(case_id))
        if expected is not None:
            c.at_version(expected)
        if editable:
            c.require_editable()
        return c

    @staticmethod
    def _save(u: UnitOfWork, before: ChangeCase, changes: dict[str, Any]) -> dict[str, Any]:
        # Full revalidation; model_copy(update=...) would bypass field validators.
        c = ChangeCase.model_validate(before.model_dump(mode="json") | changes)
        body = c.model_dump(mode="json")
        u.save_case(body, before.version)
        return body

    def create(self, request: str) -> dict[str, Any]:
        if not isinstance(request, str) or not request.strip() or len(request) > 6000:
            raise DomainError("INVALID_REQUEST", "Provide 1–6000 characters of synthetic request text")
        with self.store.transaction() as u:
            active = u.active()
            case = ChangeCase(id=uuid4().hex, version=0, stage="DRAFT", request=request,
                baseline_version=active["version"], baseline=Workflow.model_validate(active["model"]), candidate=None,
                proposal=None, provider_run=None, selected_meaning=None, selected_by=None, transactions=(), layout={},
                receipts=(), decision=None, created_at=now())
            body = case.model_dump(mode="json")
            u.insert_case(body)
            u.event("CaseCreated", {"case_id": case.id, "request_hash": fingerprint(request)})
        return body

    def propose(self, case_id: str, expected: int, *, consent: bool = False) -> dict[str, Any]:
        with self.store.transaction() as u:
            case = self._case(u, case_id, expected, editable=True)
            if case.candidate is not None:
                raise DomainError("CASE_ALREADY_SELECTED", "Create a new case to reinterpret a selected meaning")
        if self.provider.networked and not (self.allow_network and consent):
            raise DomainError("EGRESS_CONSENT_REQUIRED", "Enable network at startup and explicitly consent to sending the request and synthetic model")
        if not self._provider_lock.acquire(blocking=False):
            raise DomainError("PROVIDER_BUSY", "One proposal is already running; no duplicate call was made")
        attempt_id = uuid4().hex
        try:
            with self.store.transaction() as u:
                u.event("ProviderCallStarted", {"case_id": case_id, "attempt_id": attempt_id,
                    "provider": self.provider.name, "request_hash": fingerprint(case.request), "egress": self.provider.networked})
            start = time.monotonic()
            result = self.provider.propose(case.request, case.baseline)
            self._known_meanings(result.proposal)
            run = {"id": attempt_id, "provider": result.provider, "model": result.model, "live": result.live,
                "usage": result.usage, "elapsed_seconds": round(time.monotonic() - start, 3), "timestamp": now(),
                "request_hash": fingerprint(case.request), "egress": self.provider.networked,
                "semantics": "Untrusted language interpretation; no authority or evidence"}
            with self.store.transaction() as u:
                current = self._case(u, case_id, expected, editable=True)
                if current.candidate is not None:
                    raise DomainError("CASE_ALREADY_SELECTED", "Create a new case to reinterpret meaning after candidate selection")
                body = self._save(u, current, {"proposal": result.proposal.model_dump(mode="json"), "provider_run": run, "stage": "PROPOSED"})
                u.event("ProposalReceived", {"case_id": case_id, "run": run})
            return body
        except DomainError as error:
            with self.store.transaction() as u:
                u.event("ProviderCallNotAccepted", {"case_id": case_id, "attempt_id": attempt_id,
                    "error_code": error.code, "billing": "UNKNOWN for a started network request"})
            raise
        finally:
            self._provider_lock.release()

    def _known_meanings(self, proposal: Any) -> None:
        """Fail closed on a proposal naming a meaning this studio's pack does not model (every provider, not only the parsers)."""
        known = {m.id for m in self.pack.meanings}
        if any(a.interpretation not in known for a in proposal.alternatives):
            raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider named a meaning the domain pack does not model; no repair")

    def select(self, case_id: str, expected: int, interpretation: str, principal: Principal) -> dict[str, Any]:
        principal.require("select")
        with self.store.transaction() as u:
            case = self._case(u, case_id, expected, editable=True)
            if case.candidate is not None:
                raise DomainError("CASE_ALREADY_SELECTED", "The selected meaning cannot be silently replaced")
            if case.proposal is None or interpretation not in {a.interpretation for a in case.proposal.alternatives}:
                raise DomainError("INTERPRETATION_MISSING", "Choose one of the proposed interpretations")
            meaning = self.pack.meaning(interpretation)
            if meaning is None:
                raise DomainError("MEANING_UNSUPPORTED", "This meaning is not modelled by the domain pack")
            if not meaning.supported:
                raise DomainError("MEANING_UNSUPPORTED", meaning.consequences[0])
            candidate = apply_transactions(case.baseline, meaning.transactions, self.pack)
            txs = [tx.model_dump(mode="json") for tx in meaning.transactions]
            body = self._save(u, case, {"selected_meaning": interpretation, "selected_by": principal.id,
                "transactions": txs, "candidate": candidate.model_dump(mode="json"), "stage": "PREVIEW"})
            u.event("MeaningSelected", {"case_id": case_id, "by": principal.id, "transactions": txs})
        return body

    def edit(self, case_id: str, expected: int, tx: Transaction, principal: Principal) -> dict[str, Any]:
        principal.require("edit")
        with self.store.transaction() as u:
            case = self._case(u, case_id, expected, editable=True)
            replay(case, self.pack)
            model = apply_transaction(case.executable(), tx, self.pack)
            return self._semantic_save(u, case, model, (*case.transactions, tx), (), tx, principal,
                                       "SemanticEdited", "semantic edit", case.redo_transactions)

    def undo(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]:
        """Undo the last owner semantic edit; the selected meaning remains an indivisible protected prefix."""
        principal.require("edit")
        with self.store.transaction() as u:
            case = self._case(u, case_id, expected, editable=True)
            history = replay(case, self.pack)
            if len(case.transactions) == history.initial_count:
                raise DomainError("NOTHING_TO_UNDO", "The original meaning selection cannot be undone; no owner edits remain")
            tx = case.transactions[-1]
            return self._semantic_save(u, case, history.models[-2], case.transactions[:-1],
                                       (*case.redo_transactions, tx), tx, principal, "SemanticUndone", "semantic undo")

    def redo(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]:
        """Reapply the next undone typed command through the same interpreter and policy checks."""
        principal.require("edit")
        with self.store.transaction() as u:
            case = self._case(u, case_id, expected, editable=True)
            history = replay(case, self.pack)
            if not case.redo_transactions:
                raise DomainError("NOTHING_TO_REDO", "No undone semantic edit remains on this branch")
            tx = case.redo_transactions[-1]
            return self._semantic_save(u, case, history.redo_models[0], (*case.transactions, tx),
                                       case.redo_transactions[:-1], tx, principal, "SemanticRedone", "semantic redo")

    def _semantic_save(self, u: UnitOfWork, case: ChangeCase, model: Workflow,
                       transactions: tuple[Transaction, ...], redo: tuple[Transaction, ...],
                       tx: Transaction, principal: Principal, kind: str, reason: str,
                       discarded_redo: tuple[Transaction, ...] = ()) -> dict[str, Any]:
        if case.decision:
            u.event("DecisionInvalidated", {"case_id": case.id, "old_decision": case.decision, "reason": reason})
        body = self._save(u, case, {"candidate": model.model_dump(mode="json"),
            "transactions": [item.model_dump(mode="json") for item in transactions],
            "redo_transactions": [item.model_dump(mode="json") for item in redo], "decision": None, "stage": "PREVIEW"})
        u.event(kind, command_event(case, model, tx, principal.id, now(), discarded_redo))
        return body

    def history(self, case_id: str) -> dict[str, Any]:
        """Reconstructed semantic revisions and append-only command audit; never changes the case."""
        with self.store.transaction() as u:
            case = self._case(u, case_id)
            return history_view(case, self.pack, u.observations(case_id)["events"])

    def _working(self, case_id: str) -> Workflow:
        """The model an edit would change: the candidate once a meaning is selected, else the baseline. Read-only."""
        with self.store.transaction() as u:
            case = self._case(u, case_id)
        return case.candidate if case.candidate is not None else case.baseline

    def edit_check(self, case_id: str, tx: Transaction) -> dict[str, Any]:
        """Dry-run one edit: {legal, codes, refs}. No authority is needed because nothing is written."""
        return dry_run(self._working(case_id), tx, self.pack)

    def affordances(self, case_id: str) -> dict[str, Any]:
        """Which single edits of the case's working model the kernel would accept (read-only)."""
        model = self._working(case_id)
        return {"pack": self.pack.id, "semantic_hash": model.semantic_hash, "affordances": affordance_map(model, self.pack)}

    def layout(self, case_id: str, expected: int, change: LayoutChange, principal: Principal) -> dict[str, Any]:
        principal.require("edit")
        with self.store.transaction() as u:
            case = self._case(u, case_id, expected, editable=True)
            if change.node not in case.executable().states:
                raise DomainError("UNKNOWN_NODE", "Layout node is not a workflow state")
            layout = dict(case.layout) | {change.node: {"x": change.x, "y": change.y}}
            if case.decision:
                u.event("DecisionInvalidated", {"case_id": case_id, "old_decision": case.decision, "reason": "exact presentation changed"})
            return self._save(u, case, {"layout": layout, "decision": None, "stage": "PREVIEW"})

    def save(self, case_id: str, expected: int) -> dict[str, Any]:
        with self.store.transaction() as u:
            case = self._case(u, case_id, expected, editable=True)
            case.executable()
            return self._save(u, case, {"stage": "SAVED", "decision": None})

    def verify(self, case_id: str, expected: int) -> dict[str, Any]:
        with self.store.transaction() as u:
            case = self._case(u, case_id, expected, editable=True)
        model = case.executable()
        identity = self.identity_provider()
        if not identity["trusted_fixture"]:
            raise DomainError("SOURCE_REVIEW_REQUIRED", "Implementation differs from the shipped release fixture")
        subject = subject_for(model, case.layout, identity)
        receipt = self.signer.seal(verify_runtime(model, subject, self.sandbox, self.pack))
        # Formal artifacts are collected outside any transaction (a tool run may be slow), then sealed and appended with the runtime receipt.
        formal = attach_formal(self.formal, case.baseline, model, subject, list(case.receipts), self.signer.seal, now(), lambda: uuid4().hex,
                               self.pack)
        with self.store.transaction() as u:
            current = self._case(u, case_id, expected, editable=True)
            return self._save(u, current, {"receipts": list(current.receipts) + [receipt, *formal], "decision": None, "stage": "VERIFIED"})

    def approve(self, case_id: str, expected: int, subject_hash: str, answers: dict[str, str], acknowledge_unknowns: bool,
                principal: Principal, scope: str = "local-demo") -> dict[str, Any]:
        principal.require("approve")
        with self.store.transaction() as u:
            case = self._case(u, case_id, expected, editable=True)
            packet = compile_case(case, self.identity_provider(), self.signer.authentic, u.active()["version"], scope, self.pack)
            if not packet["eligible"]:
                raise DomainError("GATE_BLOCKED", ", ".join(packet["blockers"]))
            if packet["subject_hash"] != subject_hash:
                raise DomainError("SUBJECT_CHANGED", "The exact review subject has changed")
            if not acknowledge_unknowns:
                raise DomainError("UNKNOWNS_NOT_ACKNOWLEDGED", "Acknowledge the local/synthetic/human-unknown scope")
            expected_answers = {q["id"]: q["expected"] for q in packet["questions"]}
            if answers != expected_answers:
                raise DomainError("MEANING_CHECK_FAILED", "Critical consequences were not correctly acknowledged")
            decision = self.signer.seal({"by": principal.id, "case_id": case.id, "scope": scope, "subject_hash": subject_hash,
                "baseline_version": case.baseline_version, "time": now(), "answers": answers,
                "human_understanding": "UNKNOWN", "kind": "local-owner-acknowledgement"})
            body = self._save(u, case, {"decision": decision, "stage": "APPROVED"})
            u.event("LocalDecision", {"case_id": case_id, "decision": decision})
            return body

    def apply(self, case_id: str, expected: int, principal: Principal) -> dict[str, Any]:
        principal.require("apply")
        with self.store.transaction() as u:
            case = self._case(u, case_id, expected, editable=True)
            packet = compile_case(case, self.identity_provider(), self.signer.authentic, u.active()["version"], pack=self.pack)
            decision = case.decision
            if not packet["eligible"] or case.stage != "APPROVED" or not decision:
                raise DomainError("GATE_BLOCKED", "A current eligible exact-subject decision is required")
            if not self.signer.authentic(decision) or decision["subject_hash"] != packet["subject_hash"] or decision["scope"] != "local-demo":
                raise DomainError("STALE_DECISION", "Decision is invalid or no longer matches the exact subject")
            u.set_active(case.executable(), case.baseline_version)
            body = self._save(u, case, {"stage": "APPLIED"})
            u.event("AppliedToLocalBaseline", {"case_id": case_id, "by": principal.id, "subject": packet["subject"]})
            return body

    def discard(self, case_id: str, expected: int) -> dict[str, Any]:
        with self.store.transaction() as u:
            case = self._case(u, case_id, expected, editable=True)
            u.event("CaseDiscarded", {"case_id": case_id})
            return self._save(u, case, {"stage": "DISCARDED", "decision": None})

    def reset_preview(self, case_id: str, expected: int, state: str | None = None) -> dict[str, Any]:
        with self.store.transaction() as u:
            case = self._case(u, case_id, expected, editable=True)
            return initialise(u, case_id, case.executable(), state=state, pack=self.pack)

    def execute(self, case_id: str, command: ExecuteCommand, fault: Callable[[str], None] | None = None) -> dict[str, Any]:
        with self.store.transaction() as u:
            case = self._case(u, case_id, editable=True)
            result = execute(u, case_id, case.executable(), command, fault=fault, pack=self.pack)
        return result

    def view(self, case_id: str, scope: str = "local-demo") -> dict[str, Any]:
        with self.store.transaction() as u:
            case = self._case(u, case_id)
            packet = compile_case(case, self.identity_provider(), self.signer.authentic, u.active()["version"], scope, self.pack)
            observations = u.observations(case_id)
        # Formal evidence is read (files, no database) after the transaction has ended.
        packet = packet | {"blocked_meanings": self._blocked_meanings(case)}
        return {"case": case.model_dump(mode="json"), "packet": packet, "options": meaning_options(self.pack),
                "pack": {"id": self.pack.id, "name": self.pack.pack.name, "version": self.pack.pack.version}, "observations": observations}

    def _blocked_meanings(self, case: ChangeCase) -> list[dict[str, Any]]:
        """For each proposed interpretation the policy refuses: what it would do to the model, the policy errors, and the formal
        negative-control counterexamples that explain them. Empty once a meaning is selected or without a formal source."""
        if case.candidate is not None or case.proposal is None or self.formal is None:
            return []
        found = []
        for alternative in case.proposal.alternatives:
            model = what_if_model(case.baseline, alternative.interpretation, self.pack)
            meaning = self.pack.meaning(alternative.interpretation)
            if model is not None and meaning is not None:
                found.append({"interpretation": alternative.interpretation, "label": meaning.label,
                              "policy_errors": check_policy(model, self.pack), "explanations": self.formal_view(model)["explanations"]})
        return found

    def formal_view(self, model: Workflow) -> dict[str, Any]:
        """Formal evidence for a bare workflow (``eija compile``): collected and sealed in memory, never stored, never a decision."""
        subject, base = subject_for(model, {}, self.identity_provider()), self.pack.model
        receipts = attach_formal(self.formal, base, model, subject, [], self.signer.seal, now(), lambda: uuid4().hex, self.pack)
        return packet_view(receipts, subject, self.signer.authentic, Context(model.semantic_hash, base.semantic_hash),
                           check_policy(model, self.pack), self.pack)

    def workflows(self, case_id: str) -> tuple[Workflow, Workflow | None]:
        """Baseline and candidate of a case, for read-only projections (diagrams). No authority, no writes."""
        with self.store.transaction() as u:
            case = self._case(u, case_id)
        return case.baseline, case.candidate

    def export(self, case_id: str) -> dict[str, Any]:
        content = self.view(case_id)
        return {"format": "eija.change-case.export.v1", "payload_hash": fingerprint(content), "payload": content,
                "verification_boundary": "Payload hash detects corruption. Local signatures require the originating workspace key; exports cannot confer fresh authority."}
