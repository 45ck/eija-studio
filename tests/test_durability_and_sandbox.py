"""Pins the durability split introduced for Windows: the owner workspace is always durable, only
disposable verification sandboxes are ephemeral, and production wiring uses the measured identity."""
import os
import time

import pytest
from eija_studio.adapters import identity as identity_adapter
from eija_studio.adapters.sqlite_store import SANDBOX_PREFIX, STALE_SANDBOX_SECONDS, SQLiteStore, sandbox_factory
from eija_studio.bootstrap import build_studio

FULL, OFF = 2, 0


def synchronous(store: SQLiteStore) -> int:
    with store.transaction() as session:
        return session.db.execute("PRAGMA synchronous").fetchone()[0]


def test_owner_workspace_is_durable(tmp_path):
    studio = build_studio(tmp_path / "workspace")
    assert studio.store.durability == "durable"
    assert synchronous(studio.store) == FULL


def test_sandbox_is_ephemeral_beside_workspace_and_removed(tmp_path):
    workspace = SQLiteStore(tmp_path / "workspace")
    with sandbox_factory(workspace.directory)() as sandbox:
        assert sandbox.durability == "ephemeral"
        assert synchronous(sandbox) == OFF
        assert sandbox.directory.parent == workspace.directory / "sandboxes"
        assert sandbox.directory.name.startswith(SANDBOX_PREFIX)
        location = sandbox.directory
    assert not location.exists()


def test_stale_crash_leftovers_are_swept_but_fresh_ones_kept(tmp_path):
    workspace = SQLiteStore(tmp_path / "workspace")
    root = workspace.directory / "sandboxes"
    root.mkdir()
    stale, fresh = root / (SANDBOX_PREFIX + "stale"), root / (SANDBOX_PREFIX + "fresh")
    stale.mkdir()
    fresh.mkdir()
    old = time.time() - STALE_SANDBOX_SECONDS - 60
    os.utime(stale, (old, old))
    with sandbox_factory(workspace.directory)():
        pass
    assert not stale.exists() and fresh.exists()


def test_sandbox_factory_does_not_recreate_a_missing_workspace(tmp_path):
    with pytest.raises(FileNotFoundError):
        with sandbox_factory(tmp_path / "missing")():
            pass


def test_unknown_durability_profile_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        SQLiteStore(tmp_path / "workspace", durability="fast")


def test_production_wiring_uses_measured_identity(tmp_path):
    studio = build_studio(tmp_path / "workspace")
    assert studio.identity_provider.func is identity_adapter.identity  # bound to the studio's pack
    assert "identity_source" not in studio.identity_provider()


def test_receipt_discloses_non_durable_sandbox(studio, verified):
    receipt = studio.view(verified["id"])["case"]["receipts"][-1]
    assert any("non-durable sandbox" in item for item in receipt["artifact"]["limitations"])
