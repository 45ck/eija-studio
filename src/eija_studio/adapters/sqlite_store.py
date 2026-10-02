"""Durable local unit of work. One database transaction owns state + operation + effects."""
from __future__ import annotations
from contextlib import contextmanager, closing
from tempfile import TemporaryDirectory
from typing import Iterator
import json, os, shutil, sqlite3, time
from pathlib import Path
from typing import Literal
from eija_studio.domain.models import Workflow, DomainError, canonical
from eija_studio.domain.pack import Pack, default_pack

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_info(version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS active(id INTEGER PRIMARY KEY CHECK(id=1), version INTEGER NOT NULL, model TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY, version INTEGER NOT NULL, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS actors(id TEXT PRIMARY KEY, role TEXT NOT NULL, active INTEGER NOT NULL, assigned INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS instances(id TEXT PRIMARY KEY, case_id TEXT NOT NULL, model_hash TEXT NOT NULL, state TEXT NOT NULL, version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS operations(id TEXT PRIMARY KEY, binding TEXT NOT NULL, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY, case_id TEXT NOT NULL, operation_id TEXT NOT NULL, kind TEXT NOT NULL, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS pack_info(id INTEGER PRIMARY KEY CHECK(id=1), pack TEXT NOT NULL, digest TEXT NOT NULL);
"""


def fixture_actors(pack: Pack) -> tuple[tuple[str, str, int, int], ...]:
    """The pack's synthetic actor directory as seed rows (id, role, active, assigned)."""
    return tuple((a.id, a.role, int(a.active), int(a.assigned)) for a in pack.fixtures.actors)


class Session:
    def __init__(self, connection: sqlite3.Connection):
        self.db = connection

    def load_case(self, case_id: str) -> dict:
        row = self.db.execute("SELECT body FROM cases WHERE id=?", (case_id,)).fetchone()
        if row is None:
            raise DomainError("NOT_FOUND", "Change Case not found")
        return json.loads(row[0])

    def save_case(self, case: dict, expected: int) -> None:
        case["version"] = expected + 1
        changed = self.db.execute("UPDATE cases SET version=?, body=? WHERE id=? AND version=?",
                                  (case["version"], canonical(case), case["id"], expected)).rowcount
        if changed != 1:
            raise DomainError("STALE_VERSION", "Case changed; reload before acting")

    def insert_case(self, case: dict) -> None:
        self.db.execute("INSERT INTO cases VALUES(?,?,?)", (case["id"], case["version"], canonical(case)))

    def active(self) -> dict:
        row = self.db.execute("SELECT version,model FROM active WHERE id=1").fetchone()
        return {"version": row[0], "model": json.loads(row[1])}

    def set_active(self, model: Workflow, expected: int) -> None:
        n = self.db.execute("UPDATE active SET version=version+1,model=? WHERE id=1 AND version=?", (canonical(model), expected)).rowcount
        if n != 1:
            raise DomainError("STALE_BASELINE", "The local baseline changed; no automatic rebase")

    def event(self, kind: str, body: dict) -> None:
        self.db.execute("INSERT INTO audit(kind,body) VALUES(?,?)", (kind, canonical(body)))

    def actor(self, actor_id: str) -> dict:
        row = self.db.execute("SELECT * FROM actors WHERE id=?", (actor_id,)).fetchone()
        if row is None:
            raise DomainError("UNKNOWN_ACTOR", "Actor is not in the trusted fixture directory")
        return dict(row)

    def create_instance(self, item: dict) -> None:
        self.db.execute("INSERT INTO instances VALUES(:id,:case_id,:model_hash,:state,:version)", item)

    def find_instance(self, instance_id: str, case_id: str) -> dict | None:
        row = self.db.execute("SELECT * FROM instances WHERE id=? AND case_id=?", (instance_id, case_id)).fetchone()
        return dict(row) if row else None

    def update_instance(self, item: dict, expected: int) -> None:
        n = self.db.execute("UPDATE instances SET state=?,version=? WHERE id=? AND version=?",
            (item["state"], item["version"], item["id"], expected)).rowcount
        if n != 1:
            raise DomainError("STALE_VERSION", "Concurrent state update")

    def find_operation(self, operation_id: str) -> dict | None:
        row = self.db.execute("SELECT binding,body FROM operations WHERE id=?", (operation_id,)).fetchone()
        return {"binding": row[0], "result": json.loads(row[1])} if row else None

    def record_operation(self, operation_id: str, binding: str, result: dict) -> None:
        self.db.execute("INSERT INTO operations VALUES(?,?,?)", (operation_id, binding, canonical(result)))

    def enqueue(self, case_id: str, operation_id: str, effect: str, recipient: str) -> None:
        self.db.execute("INSERT INTO outbox VALUES(?,?,?,?,?)", (operation_id + ":" + effect, case_id,
            operation_id, effect, canonical({"recipient": recipient, "fixture_only": True})))

    def observations(self, case_id: str) -> dict:
        events = []
        for row in self.db.execute("SELECT seq,kind,body FROM audit ORDER BY seq"):
            body = json.loads(row[2])
            if body.get("case_id") == case_id:
                events.append({"seq": row[0], "kind": row[1], "body": body})
        return {"events": events, "outbox": [dict(r) for r in self.db.execute("SELECT * FROM outbox WHERE case_id=?", (case_id,))],
            "instances": [dict(r) for r in self.db.execute("SELECT * FROM instances WHERE case_id=?", (case_id,))]}

    def effect_counts(self) -> dict:
        return {t: self.db.execute("SELECT COUNT(*) FROM " + t).fetchone()[0] for t in ("audit", "outbox", "operations")}

Durability = Literal["durable", "ephemeral"]


class SQLiteStore:
    """`durable` flushes every commit (the owner workspace). `ephemeral` is for disposable
    verification sandboxes: identical transaction/atomicity semantics, but no per-commit fsync,
    which costs ~150 ms per write on Windows and made a 125-cell verification take ~40 s."""

    def __init__(self, directory: Path, *, durability: Durability = "durable", pack: Pack | None = None):
        if durability not in ("durable", "ephemeral"):
            raise ValueError("Unknown durability profile")
        self.durability = durability
        self.pack = pack if pack is not None else default_pack()
        self.directory = Path(directory).resolve()
        self.path = self.directory / "studio.sqlite3"
        self._preflight()
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.connection() as db:
            db.executescript(SCHEMA)
            row = db.execute("SELECT version FROM schema_info").fetchone()
            if row and row[0] != 2:
                raise DomainError("SCHEMA_MIGRATION_REQUIRED", "Unsupported database version; source review and explicit migration required")
            if row is None:
                db.execute("INSERT INTO schema_info VALUES(2)")
            self._seed(db)
        try:
            os.chmod(self.directory, 0o700); os.chmod(self.path, 0o600)
        except OSError:
            pass  # Windows ACLs require a separate platform review.

    def _preflight(self) -> None:
        """Refuse incompatible identity before schema, seed, journal settings or permission changes.

        Read-only SQLite may create lock sidecars; it must see committed WAL data so the CLI,
        server and MCP can safely share a workspace. No immutable-mode stale snapshot is used.
        """
        if not self.path.exists():
            return
        try:
            with closing(sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True)) as db:
                versions = db.execute("SELECT version FROM schema_info").fetchall()
                if versions != [(2,)]:
                    raise DomainError("SCHEMA_MIGRATION_REQUIRED", "Workspace lacks a verified pack digest; source review and explicit migration required")
                self._check_pack(db)
        except sqlite3.DatabaseError:
            raise DomainError("SCHEMA_MIGRATION_REQUIRED", "Workspace identity cannot be verified; source review and explicit migration required") from None

    def _check_pack(self, db: sqlite3.Connection) -> None:
        rows = db.execute("SELECT pack,digest FROM pack_info WHERE id=1").fetchall()
        if len(rows) != 1 or not rows[0][1]:
            raise DomainError("SCHEMA_MIGRATION_REQUIRED", "Workspace lacks a verified pack digest; source review and explicit migration required")
        if tuple(rows[0]) != (self.pack.id, self.pack.digest):
            raise DomainError("PACK_MISMATCH", "Workspace pack id or contents differ; use the original pack or an explicitly reviewed migration")

    def _seed(self, db: sqlite3.Connection) -> None:
        """Bind new workspaces to the exact pack before seeding baseline and synthetic actors."""
        db.execute("INSERT OR IGNORE INTO pack_info VALUES(1,?,?)", (self.pack.id, self.pack.digest))
        self._check_pack(db)
        db.execute("INSERT OR IGNORE INTO active VALUES(1,0,?)", (canonical(self.pack.model),))
        db.executemany("INSERT OR IGNORE INTO actors VALUES(?,?,?,?)", fixture_actors(self.pack))

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL" if self.durability == "durable" else "PRAGMA synchronous=OFF")
        return db

    @contextmanager
    def connection(self):
        db = self._connect()
        try:
            with db:
                yield db
        finally:
            db.close()

    @contextmanager
    def transaction(self):
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            yield Session(db)
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def list_cases(self) -> list[dict]:
        with self.connection() as db:
            return [json.loads(r[0]) for r in db.execute("SELECT body FROM cases ORDER BY rowid DESC")]

    def backup(self, target: Path) -> None:
        """SQLite online backup: do not copy the .sqlite3 file without its WAL."""
        with self.connection() as source, closing(sqlite3.connect(target)) as destination:
            source.backup(destination)


SANDBOX_PREFIX = "eija-check-"
STALE_SANDBOX_SECONDS = 3600


def sandbox_factory(workspace: Path, pack: Pack | None = None):
    """Build the application's SandboxFactory for one workspace.

    Sandboxes live in `<workspace>/sandboxes/` (same disk as the workspace, never the system temp
    directory, which may be a slow drive) and use the ephemeral profile: the same unit-of-work
    semantics with no per-commit flush. They hold only synthetic fixture data. A sandbox left behind
    by a killed process is removed by a later call once it is older than STALE_SANDBOX_SECONDS; the
    age threshold keeps a concurrent verification's live sandbox safe."""
    root = Path(workspace).resolve() / "sandboxes"

    @contextmanager
    def sandbox() -> Iterator[SQLiteStore]:
        root.mkdir(mode=0o700, exist_ok=True)  # no parents=True: never recreate a deleted workspace
        _sweep_stale(root)
        # ignore_cleanup_errors: on Windows a transiently locked file (antivirus, indexer) must not
        # mask the verification's own outcome or exception.
        with TemporaryDirectory(prefix=SANDBOX_PREFIX, dir=root, ignore_cleanup_errors=True) as directory:
            yield SQLiteStore(Path(directory), durability="ephemeral", pack=pack)

    return sandbox


def _sweep_stale(root: Path) -> None:
    cutoff = time.time() - STALE_SANDBOX_SECONDS
    for entry in root.glob(SANDBOX_PREFIX + "*"):
        try:
            if entry.is_dir() and entry.stat().st_mtime < cutoff:
                shutil.rmtree(entry, ignore_errors=True)
        except OSError:
            pass
