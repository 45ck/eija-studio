"""Explicit support levels for the workbench; design visibility is not execution."""
from __future__ import annotations

from typing import Any

from eija_studio.domain.data import data_for
from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import Pack


def capability_map(pack: Pack, model: Workflow) -> dict[str, Any]:
    """The supported constructs, bounded to the current model, with no inferred readiness."""
    data = data_for(pack)
    record = data.record if data else None
    areas = [
        ("requirements", "Requirements and business rules", [
            ("Domain vocabulary and declared boundaries", "checked_design", "DDD terms and their explicit model/source links are inspectable; aggregate invariants and service boundaries are not inferred."),
            ("Requirement prose and declared links", "checked_design", "Acceptance rows can be compared and linked explicitly; prose never becomes policy."),
            ("Typed pack laws", "executable", "Existing law kinds are evaluated by the kernel. An individual proof still needs its own run and scope."),
            ("Arbitrary prose as executable policy", "unsupported", "No inference from requirement wording to authority or behaviour.")]),
        ("data", "Data", [
            (f"Record attributes{': ' + record if record else ''}", "executable" if record else "unsupported", "The generated app validates and stores its one record class." if record else "This pack declares no record data model."),
            ("Other classes and associations", "checked_design", "Drawn and checked for structural agreement; no related records or multiplicity enforcement."),
            ("Action inputs, record updates and migrations", "unsupported", "No general typed action-input/update/migration semantics yet.")]),
        ("behaviour", "Behaviour", [
            ("Flat states, transitions and supported guards", "executable", f"{len(model.states)} states and {len(model.transitions)} transitions in this model; the kernel decides each supported operation."),
            ("Sequence scenarios", "executable", "Fixture actor/action steps are executed against the same kernel."),
            ("Calculations, value conditions and parallel state regions", "unsupported", "Not represented by the current Workflow contract.")]),
        ("collaboration", "Collaboration", [
            ("Local owner capability and optimistic versions", "executable", "Named capabilities and version checks govern the supported local review service; they are not institutional identity."),
            ("Review, replay and exact-subject evidence", "executable", "Existing service contracts bind changes and receipts; source review can still block approval."),
            ("Multi-user identity and distributed collaboration", "unsupported", "One trusted local OS user; no SSO or distributed coordination guarantee.")]),
        ("interfaces", "Interfaces", [
            ("Generated React screens and model-driven navigation", "executable", "React/Mantine renders declared fields and shipped eija.navigation.v1 destinations for create, list, record detail and workflow actions. Create/read are supported; direct record update/delete is unsupported. Eligibility stays with the local service."),
            ("Screen design, presentation map and accessibility checks", "checked_design", "UWE-inspired content/navigation/presentation links come from one generated snapshot. A matching subject does not prove runtime behaviour or complete accessibility; checks retain explicit coverage."),
            ("Arbitrary interaction logic and 3D rendering", "unsupported", "The workbench does not compile arbitrary interaction or game-engine behaviour.")]),
        ("integrations", "Integrations", [
            ("Audit and notification intents", "executable", "Audit rows and outbox intents are recorded atomically; notifications are not delivered."),
            ("API contracts, timer and system actor roles", "checked_design", "Contracts and actor kinds are visible; fixture roles are not authenticated callbacks or elapsed clocks."),
            ("External delivery, retries and connected workflows", "unsupported", "No general provider executor or cross-workflow message delivery.")]),
        ("operations", "Operations", [
            ("Loopback build, SQLite and durable baseline", "executable", "Supported local processes and persistence; activating a model does not edit repository source."),
            ("C4, component and deployment diagrams", "checked_design", "Context, containers and components describe one generated snapshot; declared dependencies are not observed deployments."),
            ("Production deployment, monitoring, cost and rollback", "unsupported", "No production control plane or general migration/rollback contract.")]),
        ("assurance", "Assurance", [
            ("Typed validation, bounded laws and fixture checks", "executable", "Run records distinguish model checks from observed implementation behaviour."),
            ("Source links and acceptance coverage", "checked_design", "Read-only structure and declared links identify subjects; hashes and links do not prove correctness."),
            ("Universal proof and measured human benefit", "unsupported", "No proof for all software; independent evaluation and participant study remain separate.")]),
    ]
    return {"schema": "eija.capabilities.v1", "pack_id": pack.id, "pack_digest": pack.digest,
            "model_hash": model.semantic_hash,
            "levels": {"executable": "Executable in the supported local scope",
                       "checked_design": "Checked design; not runtime behaviour",
                       "unsupported": "Unsupported"},
            "aspects": [{"id": key, "name": name, "constructs": [
                {"name": title, "level": level, "scope": scope} for title, level, scope in constructs]}
                for key, name, constructs in areas],
            "activation": {"supported": "Workflow transactions under unchanged pack identity",
                           "draft_only": ["laws", "vocabulary", "data schema", "screens", "requirement prose"],
                           "reason": "These drafts require separate revision and migration contracts; they are not silently applied."}}
