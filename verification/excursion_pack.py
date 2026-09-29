"""The excursion pack as the hand-written formal models see it.

The SMT, BMC, Bend and TLA+ models under verification/ encode THIS pack by hand (WBS 1.4 generates them from a
pack and keeps these as negative controls until equivalence gates pass). Their constants therefore come from
packs/excursion, never from generic kernel code.
"""
from __future__ import annotations

from eija_studio.domain.models import SemanticTransaction
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.domain.policy import apply_transaction, effects_table, forbidden_effects

PACK = load_pack(PACKS_ROOT / "excursion")
EFFECTS: dict[str, tuple[str, ...]] = effects_table(PACK)
FORBIDDEN: tuple[str, ...] = forbidden_effects(PACK)
# (id, role, active, assigned): as integers for the SQLite seed rows, as booleans for the runtime matrix.
FIXTURE_ACTORS: tuple[tuple[str, str, int, int], ...] = tuple(
    (a.id, a.role, int(a.active), int(a.assigned)) for a in PACK.fixtures.actors)
ACTORS: tuple[tuple[str, str, bool, bool], ...] = tuple((a.id, a.role, a.active, a.assigned) for a in PACK.fixtures.actors)


def _oracle() -> dict[str, tuple[str, str, str]]:
    """(role, source, target) per declared action, read from the recommendation candidate's table."""
    candidate = apply_transaction(PACK.model, SemanticTransaction(kind="enable_recommendation"), PACK)
    by = {t.action: t for t in candidate.transitions}
    return {a.id: (by[a.id].role, by[a.id].from_state, by[a.id].to_state) for a in PACK.actions}


ORACLE: dict[str, tuple[str, str, str]] = _oracle()
