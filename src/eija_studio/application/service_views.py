"""Read-only Studio projections over the same case, pack and exact-app evidence.

The command service owns authority, signed decisions and all writes. These inherited
views preserve its public API while keeping projections and source navigation together.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from pydantic import ValidationError
from eija_studio.domain.affordance import affordances as affordance_map, dry_run
from eija_studio.domain.change_case import ChangeCase
from eija_studio.domain.generated_app import GeneratedAppActivation
from eija_studio.domain.models import DomainError, Workflow, fingerprint
from eija_studio.domain.pack import Pack
from eija_studio.domain.policy import check_policy, meaning_options
from eija_studio.domain.transactions import Transaction
from .formal import what_if_model
from .history import history_view
from .ports import FormalEvidenceSource, IdentityProvider, ReceiptAuthenticator, Repository, UnitOfWork
from .repository import (RepositoryChangeSource, RepositorySource, compare_repository_changes,
                         read_repository_change_file, read_repository_freshness, read_repository_impact,
                         read_repository_source)


class StudioViews(ABC):
    """Projection half of Studio; callbacks use the command service's case and review checks."""

    store: Repository
    pack: Pack
    formal: FormalEvidenceSource | None
    identity_provider: IdentityProvider
    repository: RepositorySource | None
    repository_changes: RepositoryChangeSource | None
    signer: ReceiptAuthenticator

    @staticmethod
    @abstractmethod
    def _case(u: UnitOfWork, case_id: str, expected: int | None = None, editable: bool = False) -> ChangeCase: ...

    @abstractmethod
    def _compile(self, case: ChangeCase, active_version: int, scope: str = "local-demo") -> dict[str, Any]: ...

    @abstractmethod
    def _decision_matches(self, case: ChangeCase, packet: dict[str, Any]) -> bool: ...

    @abstractmethod
    def formal_view(self, model: Workflow) -> dict[str, Any]: ...

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
                "source_review_required": not self.identity_provider()["trusted_fixture"],
                "identity_source": self.identity_provider().get("identity_source", "measured-local-source"),
                "active_app_build": self.active_app_build(active)}

    def repository_impact(self, term: str, *, expected_source_hash: str | None = None) -> dict[str, Any]:
        """Known repository links only. This neither edits the repository nor grants evidence or authority."""
        return read_repository_impact(self.repository, term, expected_source_hash=expected_source_hash)

    def repository_source(self, reference: str, *, expected_source_hash: str | None = None) -> dict[str, Any]:
        """Bounded source view from the configured repository's captured nodes; no arbitrary path or execution."""
        return read_repository_source(self.repository, reference, expected_source_hash=expected_source_hash)

    def repository_freshness(self, expected_source_hash: str) -> dict[str, Any]:
        """Observe captured byte identity; this grants no source conformance, evidence or owner authority."""
        return read_repository_freshness(self.repository, expected_source_hash)

    def repository_change(self, base: str, head: str) -> dict[str, Any]:
        """Compare immutable source revisions; this grants no model or repository write authority."""
        return compare_repository_changes(self.repository_changes, base, head)

    def repository_change_file(self, base: str, head: str, path: str,
                               reference: str | None = None) -> dict[str, Any]:
        """Read bounded historical text and syntax; live source identity remains separate."""
        return read_repository_change_file(self.repository_changes, base, head, path, reference)

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

    def view(self, case_id: str, scope: str = "local-demo") -> dict[str, Any]:
        with self.store.transaction() as u:
            case = self._case(u, case_id)
            packet = self._compile(case, u.active()["version"], scope)
            observations = u.observations(case_id)
        # Formal evidence is read (files, no database) after the transaction has ended.
        packet = packet | {"blocked_meanings": self._blocked_meanings(case)}
        return {"case": case.model_dump(mode="json"), "packet": packet, "options": meaning_options(self.pack),
                "pack": {"id": self.pack.id, "name": self.pack.pack.name, "version": self.pack.pack.version}, "observations": observations}

    def active_app_build(self, active: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Read the atomically associated case and remeasure its exact approved generated application."""
        with self.store.transaction() as u:
            active = u.active() if active is None else active
            recorded = active.get("app_build")
            if recorded is None:
                return None
            try:
                association = GeneratedAppActivation.model_validate(recorded).model_dump(mode="json")
                case = self._case(u, association["case_id"])
                if case.stage != "APPLIED" or case.app_build is None:
                    raise DomainError("ACTIVE_APP_INVALID", "Active app association lacks an applied exact-app case")
                case.executable()
            except (ValidationError, DomainError):
                return {"binding": None, "subject": None, "freshness": "UNAVAILABLE", "conformance": {"status": "UNKNOWN"},
                        "limitations": ["The recorded active generated-app association is invalid or its case is unavailable."]}
        packet = self._compile(case, active["version"])
        view: dict[str, Any] = packet["app_build"]
        valid = self._approved_association(case, active, association, packet)
        with self.store.transaction() as u:
            still_active = u.active() == active
        return association | view | {"freshness": "CURRENT" if valid and still_active else "STALE"}

    def _approved_association(self, case: ChangeCase, active: dict[str, Any],
                              association: dict[str, Any], packet: dict[str, Any]) -> bool:
        """The stored association must match both the active model and the current signed review."""
        return bool(self._association_matches(case, active, association) and
                    self._decision_matches(case, packet) and packet["eligible"] and
                    association["subject_hash"] == packet["subject_hash"])

    @staticmethod
    def _association_matches(case: ChangeCase, active: dict[str, Any], association: dict[str, Any]) -> bool:
        if case.stage != "APPLIED" or case.app_build is None:
            return False
        return bool(association["case_id"] == case.id and association["binding"] == case.app_build.model_dump(mode="json") and
                association["baseline_version"] == active["version"] == case.baseline_version + 1 and
                case.executable().model_dump(mode="json") == active["model"])

    def build_approval(self, subject: dict[str, Any]) -> dict[str, Any]:
        """An unreviewed preview may run, but cannot inherit approval from a matching workflow alone."""
        active = self.active_app_build()
        if active is None or active["subject"] != subject:
            return {"status": "UNREVIEWED", "subject_digest": subject["digest"]}
        return {"status": "ACTIVE_APPROVED" if active["freshness"] == "CURRENT" else "STALE",
                "case_id": active["case_id"], "subject_digest": subject["digest"]}

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

    def workflows(self, case_id: str) -> tuple[Workflow, Workflow | None]:
        """Baseline and candidate of a case, for read-only projections (diagrams). No authority, no writes."""
        with self.store.transaction() as u:
            case = self._case(u, case_id)
        return case.baseline, case.candidate

    def export(self, case_id: str) -> dict[str, Any]:
        content = self.view(case_id)
        return {"format": "eija.change-case.export.v1", "payload_hash": fingerprint(content), "payload": content,
                "verification_boundary": "Payload hash detects corruption. Local signatures require the originating workspace key; exports cannot confer fresh authority."}
