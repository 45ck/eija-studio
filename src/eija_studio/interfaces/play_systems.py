"""PlayIDE's systems (ADR-0185): start a new system from a sketch or a template, open one you made before, and save
the work in progress to carry on later.

The server serves one system at a time. Opening another builds a studio for it, on its own workspace, and swaps it
in behind every route; the page then reloads. A system is created only from documents the kernel's pack check
accepts. The draft is the page's work in progress (its plan steps and edited screens), kept in the system's
workspace; it is never the model in force, and on reopening every step is checked by the policy again, like any plan.
"""
from __future__ import annotations

import json
import os
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from eija_studio.application.data_steps import parse_step
from eija_studio.application.describe_system import MAX_DESCRIPTION, describe_documents, described_summary
from eija_studio.application.interop import MAX_CHARS, detect_format, start_from_file
from eija_studio.application.new_system import SKETCH_HELP, sketch_documents, summary, system_id, template_documents
from eija_studio.application.plan import MAX_DRAFT_STEPS, MAX_REQUEST
from eija_studio.domain.models import Contract, DomainError, Workflow
from eija_studio.domain.pack import PACK_FILE, PACKS_ROOT, PackError, load_pack
from eija_studio.domain.screens import parse_screens

BLANK = "blank"
UML = "uml"  # start from a UML file (ADR-0190)
DESCRIBE = "describe"  # start from a description of the app (ADR-0216)
TEMPLATE_FILES = ("pack.json", "data.json", "screens.json", "scenarios.json")


class StudioHandle:
    """The studio every route uses, which `switch` replaces when another system is opened."""

    def __init__(self, studio: Any):
        object.__setattr__(self, "_current", studio)

    def __getattr__(self, name: str) -> Any:
        return getattr(object.__getattribute__(self, "_current"), name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(object.__getattribute__(self, "_current"), name, value)

    def switch(self, studio: Any) -> None:
        object.__setattr__(self, "_current", studio)


class NewSystem(Contract):
    name: str = Field(default="", max_length=80)  # may be empty only when describing: the describer names it
    template: str = Field(default=BLANK, pattern=r"^[a-z][a-z0-9-]{0,39}$")
    record: str = Field(default="Record", max_length=40)
    sketch: str = Field(default="", max_length=6000)
    uml: str = Field(default="", max_length=MAX_CHARS)  # for template "uml": the file's text
    filename: str = Field(default="", max_length=200)  # for template "uml": its name, which says its format
    description: str = Field(default="", max_length=MAX_DESCRIPTION)  # for template "describe": the app in your words
    check_only: bool = False  # say what would be created, or what is wrong, and write nothing


class OpenSystem(Contract):
    pack: str = Field(min_length=1, max_length=1000)


class DraftStep(Contract):
    transaction: dict[str, Any]
    author: Literal["you", "ai"] = "you"
    round: int | None = Field(default=None, ge=1, le=MAX_DRAFT_STEPS)  # which chat round added it (ADR-0201)
    request: str | None = Field(default=None, max_length=MAX_REQUEST)  # what was asked in that round, in your words


class SavedWork(Contract):
    steps: list[DraftStep] = Field(default_factory=list, max_length=MAX_DRAFT_STEPS)
    accepted: list[bool] = Field(default_factory=list, max_length=MAX_DRAFT_STEPS)
    screens: dict[str, Any] | None = None


def templates() -> list[dict[str, Any]]:
    """The packs that ship with EIJA, each a template a new system can start from."""
    found = []
    for folder in sorted(PACKS_ROOT.iterdir()) if PACKS_ROOT.is_dir() else ():
        if (folder / PACK_FILE).is_file():
            try:
                pack = load_pack(folder)
            except PackError:
                continue
            found.append({"id": pack.id, "name": pack.pack.name, "description": pack.pack.description,
                          "states": len(pack.model.states), "transitions": len(pack.model.transitions),
                          "roles": len(pack.roles), "folder": folder})
    return found


def _documents(folder: Path) -> dict[str, dict[str, Any]]:
    return {name: json.loads((folder / name).read_text(encoding="utf-8")) for name in TEMPLATE_FILES if (folder / name).is_file()}


def new_documents(library: Any, body: NewSystem, describer: Any = None) -> tuple[str, dict[str, dict[str, Any]], dict[str, Any] | None]:
    """The new system's id, its documents checked by the kernel, and for a UML file the import report (what was read,
    kept, filled in or not imported), or for a description what the describer read; `PackError` with every problem
    otherwise."""
    if body.template == DESCRIBE:
        return _described(library, body, describer)
    if not body.name.strip():
        raise PackError(["name: give the system a name"])
    pack_id = system_id(body.name, library.ids())
    if body.template == BLANK:
        return pack_id, sketch_documents(body.name.strip(), body.record.strip() or "Record", body.sketch, pack_id), None
    if body.template == UML:
        return _from_uml(body, pack_id)
    template = next((t for t in templates() if t["id"] == body.template), None)
    if template is None:
        raise DomainError("NOT_FOUND", "No such template")
    return pack_id, template_documents(load_pack(template["folder"]), _documents(template["folder"]), body.name.strip(), pack_id), None


def _from_uml(body: NewSystem, pack_id: str) -> tuple[str, dict[str, dict[str, Any]], dict[str, Any]]:
    if not body.uml.strip():
        raise PackError(["choose a UML file: XMI, PlantUML, Mermaid or draw.io"])
    try:
        fmt = detect_format(body.filename, body.uml)
        documents, report = start_from_file(fmt, body.uml, body.name.strip(), pack_id, body.record.strip() or "Record")
    except DomainError as error:
        raise PackError([error.message]) from None
    return pack_id, documents, report


def _described(library: Any, body: NewSystem, describer: Any) -> tuple[str, dict[str, dict[str, Any]], dict[str, Any]]:
    if describer is None:
        raise DomainError("DESCRIBER_UNAVAILABLE", "No describer is configured")
    documents, reading = describe_documents(body.description, body.name, lambda name: system_id(name, library.ids()), describer)
    return documents["pack.json"]["pack"]["id"], documents, reading


class Systems:
    """The systems home and the system the server has open. `describer` reads a description of an app for "Describe
    your app" (ADR-0216); the offline one unless another is given."""

    def __init__(self, handle: StudioHandle, library: Any, opener: Callable[[Path, Path], Any],
                 pack: Path, workspace: Path, on_switch: Callable[[], Any] = lambda: None, describer: Any = None):
        self.handle, self.library, self.opener, self.on_switch = handle, library, opener, on_switch
        self.describer = describer
        self.lock = threading.Lock()
        self.current = self._entry(handle.pack, Path(pack), Path(workspace))
        self.launched = dict(self.current)
        self.studios: dict[str, Any] = {self._key(pack): object.__getattribute__(handle, "_current")}

    @staticmethod
    def _key(pack: Path) -> str:
        return str(Path(pack).resolve())

    @staticmethod
    def _entry(pack: Any, location: Path, workspace: Path) -> dict[str, Any]:
        return {"id": pack.id, "name": pack.pack.name, "pack": str(Path(location).resolve()), "workspace": str(Path(workspace).resolve())}

    def listing(self) -> dict[str, Any]:
        recent = self._recent()
        shown = {self.current["pack"], *(e["pack"] for e in recent)}
        return {"current": self.current, "recent": recent, "home": str(self.library.home),
                "systems": [s for s in self.library.systems() if s["pack"] not in shown],
                "templates": [{k: v for k, v in t.items() if k != "folder"} for t in templates()], "sketch_help": SKETCH_HELP}

    def _recent(self) -> list[dict[str, Any]]:
        """Recent systems other than the open one, with the one the server started with always among them."""
        recent = [e for e in self.library.recent() if e["pack"] != self.current["pack"]]
        if self.launched["pack"] != self.current["pack"] and self.launched["pack"] not in {e["pack"] for e in recent}:
            recent.append(self.launched)
        return recent

    def open(self, pack: Path, workspace: Path) -> dict[str, Any]:
        """Serve another system: build (or reuse) its studio on its workspace and swap it in."""
        with self.lock:
            key = self._key(pack)
            studio = self.studios.get(key)
            if studio is None:
                studio = self.opener(Path(pack), Path(workspace))
                self.studios[key] = studio
            self.on_switch()  # the running app belongs to the system being left
            self.handle.switch(studio)
            self.current = self._entry(studio.pack, Path(pack), Path(workspace))
            self.library.remember(self.current)
            if self.launched["pack"] != self.current["pack"] and all(e["pack"] != self.launched["pack"] for e in self.library.recent()):
                self.library.remember(self.launched)  # keep the system the server started with one click away
                self.library.remember(self.current)
            return self.current

    def workspace_of(self, pack: str) -> Path:
        """The workspace a known system is opened on: the one it was last opened on, else the folder's own."""
        for entry in [self.launched, *self.library.recent()]:
            if Path(entry["pack"]).resolve() == Path(pack).resolve():
                return Path(entry["workspace"])
        return self.library.workspace(Path(pack))


def register(app, systems: Systems) -> None:
    @app.get("/api/play/systems")
    def play_systems():
        """The system open now, recent ones, the others in the systems home, and the templates to start from."""
        return systems.listing()

    @app.post("/api/play/systems/new")
    def play_new_system(body: NewSystem):
        """Start a new system from a sketch or a template; with `check_only`, only say what it would be."""
        try:
            pack_id, documents, report = new_documents(systems.library, body, systems.describer)
        except PackError as error:
            return {"created": False, "problems": list(error.diagnostics)}
        found: dict[str, Any]
        if body.template == DESCRIBE:
            found = {"system": described_summary(documents), "described": report}
        else:
            found = {"system": summary(documents)} | ({"import": report} if report is not None else {})
        if body.check_only:
            return {"created": False, "problems": []} | found
        folder = systems.library.create(pack_id, documents)
        return {"created": True, "problems": []} | found | {"opened": systems.open(folder, systems.library.workspace(folder))}

    @app.post("/api/play/systems/open")
    def play_open_system(body: OpenSystem):
        """Open a system made before: one in the systems home, one on the recent list, or the one the server started with."""
        if Path(body.pack).resolve() != Path(systems.launched["pack"]) and not systems.library.known(body.pack):
            raise DomainError("NOT_FOUND", "Open a system from the systems home or the recent list")
        return {"opened": systems.open(Path(body.pack), systems.workspace_of(body.pack))}

    def workspace() -> Path:
        return Path(systems.current["workspace"])

    def in_force() -> str:
        """The semantic hash of the model in force on the system open now."""
        with systems.handle.store.transaction() as u:
            return Workflow.model_validate(u.active()["model"]).semantic_hash

    @app.get("/api/play/draft")
    def play_draft():
        """The saved work in progress on the system open now, or null; `moved` when the model in force has changed since."""
        draft = systems.library.read_draft(workspace())
        return {"draft": draft, "system": systems.current, "moved": draft is not None and draft.get("model") != in_force()}

    @app.post("/api/play/draft")
    def play_save_draft(body: SavedWork):
        """Save the work in progress: the plan's steps as typed transactions, and edited screens. Nothing is applied."""
        for step in body.steps:
            parse_step(step.transaction)  # a malformed step is refused here, not on reopening
        if body.screens is not None:
            parse_screens(body.screens, systems.handle.pack.id)
        saved = body.model_dump(mode="json") | {"saved": int(time.time()), "system": systems.current["id"], "model": in_force()}
        systems.library.write_draft(workspace(), saved)
        return {"saved": saved["saved"]}

    @app.post("/api/play/draft/clear")
    def play_clear_draft():
        systems.library.write_draft(workspace(), None)
        return {"cleared": True}


def default_home() -> Path:
    """`$EIJA_SYSTEMS` if set, else `~/PlayIDE`: where systems started in PlayIDE are kept."""
    return Path(os.environ.get("EIJA_SYSTEMS") or Path.home() / "PlayIDE")


def add_parser(subs) -> None:
    new = subs.add_parser("new", help="Start a new system from a sketch or a template, in the systems home (ADR-0185)")
    new.add_argument("name", help="The system's name, for example 'Support desk'")
    new.add_argument("--from", dest="template", default=BLANK, help="The id of a shipped pack to copy (GET /api/play/systems lists them); default blank")
    new.add_argument("--sketch", type=Path, help="For blank: a file with one transition per line, From -> To : Action [Role]")
    new.add_argument("--record", default="Record", help="For blank: the UML class of the record that moves (UpperCamelCase)")
    new.add_argument("--uml", type=Path, help="Start from this UML file (XMI, PlantUML, Mermaid or draw.io); its import report is printed")
    new.add_argument("--systems", type=Path, default=None, help="The systems home (default EIJA_SYSTEMS or ~/PlayIDE)")


def start_system(library: Any, name: str, template: str = BLANK, record: str = "Record", sketch: str = "",
                 uml: Path | None = None) -> tuple[int, dict[str, Any]]:
    """`eija new`: create the system in `library` and say where it is (0), or the problems the kernel's pack check found (2)."""
    body = NewSystem(name=name, template=UML if uml else template, record=record, sketch=sketch,
                     uml=uml.read_text(encoding="utf-8") if uml else "", filename=uml.name if uml else "")
    try:
        pack_id, documents, report = new_documents(library, body)
    except PackError as error:
        return 2, {"created": False, "problems": list(error.diagnostics)}
    folder = library.create(pack_id, documents)
    return 0, {"created": True, "system": summary(documents), "pack": str(folder),
               "serve": f"eija serve --pack {folder} --workspace {library.workspace(folder)}"} | ({"import": report} if report else {})
