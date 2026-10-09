"""Where a person's own systems live on disk (ADR-0185): one folder per system under a systems home, the recent list,
and the saved draft of the work in progress.

A system folder is an ordinary pack folder (`pack.json`, `data.json`, `screens.json`) with its own workspace,
`.eija/`, beside them, so its change cases, history and draft stay with it. Every write is whole-file and atomic
(written beside, then renamed), with LF line endings. Nothing here decides what a system means: the caller checks
the documents with the kernel before they are written.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import PACK_FILE, PACK_ID

RECENT_FILE = "recent.json"
DRAFT_FILE = "draft.json"
WORKSPACE = ".eija"
MAX_RECENT = 12


def _write_json(path: Path, document: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as out:
            out.write(json.dumps(document, indent=2, ensure_ascii=False) + "\n")
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def _is_pack(location: str | Path) -> bool:
    """A pack folder (with `pack.json`) or a pack file."""
    path = Path(location)
    return (path / PACK_FILE).is_file() if path.is_dir() else path.is_file()


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


class SystemLibrary:
    """The systems home: `<home>/<id>/pack.json` for each system, and `<home>/recent.json`."""

    def __init__(self, home: Path):
        self.home = Path(home).expanduser().resolve()

    def ids(self) -> set[str]:
        return {path.name for path in self.home.iterdir() if path.is_dir()} if self.home.is_dir() else set()

    def systems(self) -> list[dict[str, Any]]:
        """The systems in the home, most recently changed first."""
        found = []
        for folder in (self.home.iterdir() if self.home.is_dir() else ()):
            pack = _read_json(folder / PACK_FILE) if folder.is_dir() else None
            if isinstance(pack, dict) and isinstance(pack.get("pack"), dict):
                info = pack["pack"]
                found.append({"id": str(info.get("id", folder.name)), "name": str(info.get("name", folder.name)),
                              "pack": str(folder), "workspace": str(folder / WORKSPACE),
                              "changed": (folder / PACK_FILE).stat().st_mtime})
        return sorted(found, key=lambda s: -s["changed"])

    def create(self, pack_id: str, documents: dict[str, dict[str, Any]]) -> Path:
        """Write a new system's checked documents into `<home>/<pack_id>/`; never over an existing folder."""
        if not re.fullmatch(PACK_ID, pack_id):
            raise DomainError("SYSTEM_ID_INVALID", "A system id is lower-case letters, digits and hyphens")
        folder = self.home / pack_id
        if folder.exists():
            raise DomainError("SYSTEM_EXISTS", f"A system called {pack_id} already exists in {self.home}")
        self.home.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(dir=self.home, prefix=f".{pack_id}."))
        try:
            for name, document in documents.items():
                _write_json(staging / name, document)
            staging.rename(folder)
        except BaseException:
            shutil.rmtree(staging, ignore_errors=True)
            raise
        return folder

    @staticmethod
    def workspace(folder: Path) -> Path:
        """A system folder's own workspace."""
        return Path(folder) / WORKSPACE

    @staticmethod
    def read_draft(workspace: Path) -> dict[str, Any] | None:
        """The draft saved in a system's workspace, if any."""
        found = _read_json(Path(workspace) / DRAFT_FILE)
        return found if isinstance(found, dict) else None

    @staticmethod
    def write_draft(workspace: Path, draft: dict[str, Any] | None) -> None:
        """Save the draft into the system's workspace, or clear it."""
        path = Path(workspace) / DRAFT_FILE
        if draft is None:
            path.unlink(missing_ok=True)
        else:
            _write_json(path, draft)

    def contains(self, pack: Path) -> bool:
        pack = Path(pack).resolve()
        return pack.parent == self.home and (pack / PACK_FILE).is_file()

    def known(self, pack: str | Path) -> bool:
        """A system the person may open by path: one in the home, or one on the recent list."""
        resolved = Path(pack).resolve()
        return self.contains(resolved) or any(Path(e["pack"]).resolve() == resolved for e in self.recent())

    def recent(self) -> list[dict[str, Any]]:
        """Systems opened before, newest first; entries whose pack is gone are left out."""
        entries = _read_json(self.home / RECENT_FILE)
        if not isinstance(entries, list):
            return []
        keep = [e for e in entries if isinstance(e, dict) and all(isinstance(e.get(k), str) for k in ("pack", "workspace", "name"))]
        return [e for e in keep if _is_pack(e["pack"])][:MAX_RECENT]

    def remember(self, entry: dict[str, Any]) -> None:
        """Put a just-opened system at the top of the recent list."""
        entry = {k: entry[k] for k in ("id", "name", "pack", "workspace")} | {"opened": int(time.time())}
        others = [e for e in self.recent() if Path(e["pack"]) != Path(entry["pack"])]
        _write_json(self.home / RECENT_FILE, [entry, *others][:MAX_RECENT])

