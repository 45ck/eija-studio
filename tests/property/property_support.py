"""Test-side composition and observation helpers for the property suite.

``bootstrap.build_studio`` is the production composition root and always opens the durable profile.
Property tests run thousands of short transactions, so they compose the same adapters with the
``ephemeral`` store profile, which the store documents as having identical transaction/atomicity
semantics without the per-commit flush. Nothing here is imported by the package.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator

from eija_studio.adapters.identity import identity as measured_identity
from eija_studio.adapters.providers import OfflineProvider
from eija_studio.adapters.receipts import ReceiptSigner
from eija_studio.adapters.sqlite_store import SQLiteStore
from eija_studio.application.service import Studio
from eija_studio.bootstrap import sandbox_factory
from eija_studio.domain.models import OWNER

REQUEST = "Let teachers sign off excursions."
ROOT = Path(__file__).resolve().parents[2]

# Example-count multiplier per Hypothesis profile (see conftest.py). Tests state their own baseline
# budget and scale it, so "deep" means the same thing everywhere: ten times the ci budget.
SCALE = {"ci": 1, "deep": 10}


def examples(base: int) -> int:
    """``base`` examples under the ci profile, more under deep."""
    return base * SCALE[os.environ.get("EIJA_HYPOTHESIS_PROFILE", "ci")]


# Outcome histogram of the stateful differential test (Committed / Replayed / refusal codes), reported
# in reports/testing/property.json so a green run shows which behaviours the walks actually reached.
OUTCOMES: Counter[str] = Counter()
MAIN_OUTCOMES: dict[str, int] = {}  # snapshot after the un-mutated differential run (the mutant runs also count in OUTCOMES)


@contextmanager
def scratch_directory() -> Iterator[Path]:
    """A throw-away workspace inside the checkout (the system temp directory may be a slow disk)."""
    root = ROOT / ".tmp"
    root.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="prop-", dir=root))
    try:
        yield directory
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def harness_identity() -> dict:
    """Behavioural tests exercise the source under test; release-fixture identity is a separate gate."""
    return measured_identity() | {"trusted_fixture": True}


def ephemeral_studio(directory: Path) -> Studio:
    """Studio wired like ``build_studio(..., provider="offline")`` but on the ephemeral store profile."""
    store = SQLiteStore(directory, durability="ephemeral")
    return Studio(store, OfflineProvider(), ReceiptSigner(store.directory), harness_identity,
                  sandbox_factory(store.directory))


def selected_case(studio: Studio) -> dict:
    """A Change Case in PREVIEW with the supported "recommend only" meaning selected by the owner."""
    case = studio.create(REQUEST)
    case = studio.propose(case["id"], case["version"])
    return studio.select(case["id"], case["version"], "recommend_only", OWNER)


def set_actor(studio: Studio, actor_id: str, column: str, value: object) -> None:
    """Change the trusted synthetic directory, as an external assignment feed would.

    The kernel deliberately has no write API for actors (ADR-011), so this goes to the adapter's table.
    """
    if column not in {"role", "active", "assigned"}:
        raise ValueError(column)
    with studio.store.transaction() as u:
        changed = u.db.execute(f"UPDATE actors SET {column}=? WHERE id=?", (value, actor_id)).rowcount
    if changed != 1:
        raise LookupError(actor_id)
