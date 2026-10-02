"""Pack identity regressions: current file bytes, explicit snapshots and immutable reopen rejection."""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from eija_studio.adapters.sqlite_store import SQLiteStore
from eija_studio.domain import pack as packs
from eija_studio.domain.models import DomainError

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def document():
    return json.loads((ROOT / "packs" / "excursion" / "pack.json").read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def isolated_registry(monkeypatch, tmp_path):
    monkeypatch.setattr(packs, "_LOADED", {})
    monkeypatch.setattr(packs, "_SOURCES", {})
    monkeypatch.setattr(packs, "PACKS_ROOT", tmp_path / "repository-packs")


def write_pack(path, document):
    path.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    return packs.load_pack(path)


def workspace_bytes(directory):
    # Read-only SQLite is allowed to create shared-memory locks and an empty WAL.
    # Every persisted DB byte and every nonempty WAL remains part of the oracle.
    paths = [path for path in directory.rglob("*") if path.is_file() and not path.name.endswith("-shm")]
    return {path.relative_to(directory).as_posix(): body for path in paths
            if (body := path.read_bytes()) or not path.name.endswith("-wal")}


def test_default_pack_reads_changed_contents_even_with_identical_size_and_mtime(tmp_path, monkeypatch, document):
    path = tmp_path / "pack.json"
    document["pack"]["description"] = "first revision"
    first = write_pack(path, document)
    monkeypatch.setenv(packs.ENV_PACK, str(path))
    assert packs.default_pack() is first
    before = path.stat()
    document["pack"]["description"] = "other revision"
    path.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert path.stat().st_size == before.st_size
    current = packs.default_pack()
    assert current.digest != first.digest
    assert current.pack.description == "other revision"
    assert first.pack.description == "first revision"


@pytest.mark.parametrize("replace_with", [None, "{broken"])
def test_default_pack_never_returns_cached_success_for_missing_or_invalid_file(tmp_path, monkeypatch, document, replace_with):
    path = tmp_path / "pack.json"
    write_pack(path, document)
    monkeypatch.setenv(packs.ENV_PACK, str(path))
    packs.default_pack()
    if replace_with is None:
        path.unlink()
    else:
        path.write_text(replace_with, encoding="utf-8")
    with pytest.raises(packs.PackError):
        packs.default_pack()


def test_same_id_variants_require_digest_and_preserve_both_snapshots(tmp_path, document):
    first = write_pack(tmp_path / "first.json", document)
    document["laws"].pop()
    other = write_pack(tmp_path / "other.json", document)
    assert first.id == other.id and first.model == other.model
    assert first.digest != other.digest
    with pytest.raises(DomainError) as caught:
        packs.find_pack(first.id)
    assert caught.value.code == "PACK_IDENTITY_REQUIRED"
    with pytest.raises(DomainError) as caught:
        packs.meaning_ids(first.id)
    assert caught.value.code == "PACK_IDENTITY_REQUIRED"
    assert packs.find_pack(first.id, digest=first.digest) == first
    assert packs.find_pack(other.id, digest=other.digest) == other
    assert packs.find_pack(first.id, digest="0" * 64) is None
    assert packs.meaning_ids(first.id, digest=first.digest) == frozenset(m.id for m in first.meanings)


def test_id_lookup_refreshes_its_source_before_selecting_a_pack(tmp_path, document):
    path = tmp_path / "pack.json"
    first = write_pack(path, document)
    document["laws"].pop()
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(DomainError) as caught:
        packs.find_pack(first.id)
    assert caught.value.code == "PACK_IDENTITY_REQUIRED"
    assert packs.find_pack(first.id, digest=first.digest) is first


def test_identical_contents_at_two_paths_are_not_ambiguous(tmp_path, document):
    first = write_pack(tmp_path / "first.json", document)
    second = write_pack(tmp_path / "second.json", document)
    assert second.digest == first.digest
    assert packs.find_pack(first.id) == first


def test_repository_pack_cannot_be_shadowed_by_same_id_custom_variant(tmp_path, document):
    repository = packs.PACKS_ROOT / document["pack"]["id"]
    repository.mkdir(parents=True)
    write_pack(repository / "pack.json", document)
    document["laws"].pop()
    custom = write_pack(tmp_path / "custom.json", document)
    with pytest.raises(DomainError) as caught:
        packs.find_pack(custom.id)
    assert caught.value.code == "PACK_IDENTITY_REQUIRED"


def test_new_workspace_persists_full_digest_and_reopens_unchanged(tmp_path, document):
    pack = packs.parse_pack(document)
    directory = tmp_path / "workspace"
    store = SQLiteStore(directory, durability="ephemeral", pack=pack)
    with store.transaction() as session:
        session.event("retained", {"case_id": "example"})
    before = workspace_bytes(directory)
    reopened = SQLiteStore(directory, durability="ephemeral", pack=packs.parse_pack(document))
    with reopened.connection() as db:
        assert tuple(db.execute("SELECT pack,digest FROM pack_info WHERE id=1").fetchone()) == (pack.id, pack.digest)
        assert db.execute("SELECT version FROM schema_info").fetchone()[0] == 2
        assert db.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 1
    assert workspace_bytes(directory) == before


@pytest.mark.parametrize("change", ["laws", "actors", "id"])
def test_reopen_mismatch_rejects_before_workspace_mutation(tmp_path, document, change):
    directory = tmp_path / "workspace"
    original = packs.parse_pack(document)
    SQLiteStore(directory, durability="ephemeral", pack=original)
    before = workspace_bytes(directory)
    if change == "laws":
        document["laws"].pop()
    elif change == "actors":
        document["fixtures"]["actors"].append({**document["fixtures"]["actors"][0], "id": "extra-actor"})
    else:
        document["pack"]["id"] = document["model"]["id"] = "other-domain"
    with pytest.raises(DomainError) as caught:
        SQLiteStore(directory, pack=packs.parse_pack(document))
    assert caught.value.code == "PACK_MISMATCH"
    assert workspace_bytes(directory) == before
    SQLiteStore(directory, durability="ephemeral", pack=original)


@pytest.mark.parametrize("version", [1, 2, 99])
def test_legacy_or_unprovable_workspace_requires_explicit_migration_without_writes(tmp_path, document, version):
    directory = tmp_path / "workspace"
    directory.mkdir()
    pack = packs.parse_pack(document)
    path = directory / "studio.sqlite3"
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("CREATE TABLE schema_info(version INTEGER NOT NULL)")
        db.execute("INSERT INTO schema_info VALUES(?)", (version,))
        db.execute("CREATE TABLE pack_info(id INTEGER PRIMARY KEY, pack TEXT NOT NULL)")
        db.execute("INSERT INTO pack_info VALUES(1,?)", (pack.id,))
        db.execute("CREATE TABLE retained(body TEXT)")
        db.execute("INSERT INTO retained VALUES('original workspace data')")
    before = workspace_bytes(directory)
    with pytest.raises(DomainError) as caught:
        SQLiteStore(directory, pack=pack)
    assert caught.value.code == "SCHEMA_MIGRATION_REQUIRED"
    assert "source review" in caught.value.message and "migration" in caught.value.message
    assert workspace_bytes(directory) == before


def test_missing_persisted_digest_is_not_silently_rebound(tmp_path, document):
    directory = tmp_path / "workspace"
    pack = packs.parse_pack(document)
    store = SQLiteStore(directory, durability="ephemeral", pack=pack)
    with store.connection() as db:
        db.execute("DELETE FROM pack_info")
    before = workspace_bytes(directory)
    with pytest.raises(DomainError) as caught:
        SQLiteStore(directory, pack=pack)
    assert caught.value.code == "SCHEMA_MIGRATION_REQUIRED"
    assert workspace_bytes(directory) == before


def test_pack_mismatch_committed_only_in_wal_is_detected_without_data_writes(tmp_path, document):
    directory = tmp_path / "workspace"
    pack = packs.parse_pack(document)
    store = SQLiteStore(directory, durability="ephemeral", pack=pack)
    with store.connection() as db:
        db.execute("UPDATE pack_info SET digest=?", ("f" * 64,))
        db.commit()
        before = workspace_bytes(directory)
        with pytest.raises(DomainError) as caught:
            SQLiteStore(directory, pack=pack)
        assert caught.value.code == "PACK_MISMATCH"
        assert workspace_bytes(directory) == before
    with pytest.raises(DomainError) as caught:
        SQLiteStore(directory, pack=pack)
    assert caught.value.code == "PACK_MISMATCH"


def test_concurrent_constructor_reopens_valid_workspace_with_committed_wal(tmp_path, document):
    directory = tmp_path / "workspace"
    pack = packs.parse_pack(document)
    first = SQLiteStore(directory, durability="ephemeral", pack=pack)
    with first.connection() as db:
        db.execute("INSERT INTO audit(kind,body) VALUES('retained','{}')")
        db.commit()
        assert (directory / "studio.sqlite3-wal").stat().st_size > 0
        second = SQLiteStore(directory, durability="ephemeral", pack=pack)
        with second.connection() as concurrent:
            assert concurrent.execute("SELECT COUNT(*) FROM audit WHERE kind='retained'").fetchone()[0] == 1
            assert tuple(concurrent.execute("SELECT pack,digest FROM pack_info").fetchone()) == (pack.id, pack.digest)
