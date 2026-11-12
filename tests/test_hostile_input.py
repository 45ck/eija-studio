"""Hostile and malformed input at PlayIDE's edges, and the cost of a plan at the model's limits (ADR-0236).

Each case here was found by fuzzing (docs/engineering/HOSTILE-INPUT.md): a UML file whose escape or number made a reader
raise a bare `ValueError` (a 500 in the IDE, a raw message on the command line), a command-line input that printed a
traceback or a vague error, a saved draft the page could not reopen, and a 64-step plan that replayed every earlier
step for each new one. The fuzz loops are seeded, so a failure here reproduces exactly.
"""
from __future__ import annotations

import contextlib
import json
import random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eija_studio.adapters.system_library import SystemLibrary
from eija_studio.application import plan as plan_module
from eija_studio.application.data_steps import SetRoleKind, apply_data, is_data, set_kinds, split
from eija_studio.application.interop import FORMATS, _READERS, export_model, import_model, mermaid, plantuml, start_from_file
from eija_studio.application.plan import MAX_DRAFT_STEPS, preview_plan
from eija_studio.domain import transactions as transactions_module
from eija_studio.domain.data import data_for
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.domain.policy import apply_structural_all
from eija_studio.domain.transactions import parse_transaction
from eija_studio.interfaces.cli import main
from eija_studio.interfaces.http import create_app
from eija_studio.interfaces.play_systems import StudioHandle, Systems
from kernel_support import harness_studio

ROOT = Path(__file__).resolve().parents[1]
PACKS = [load_pack(p) for p in sorted((ROOT / "packs").iterdir()) if (p / "pack.json").is_file()]
LOAN = load_pack(ROOT / "packs" / "library-loan")
PLANT = "@startuml\n[*] --> A\nA --> B : go\n{}\n@enduml\n"
MERMAID = "```mermaid\nstateDiagram-v2\n[*] --> A\nA --> B : go {}\n```\n"
CLASS = "@startuml\nclass Loan {{\n +a : String {}\n}}\n[*] --> A\nA --> B : go\n@enduml\n"


def _both(fmt: str, text: str) -> None:
    """Import against a pack and start a new system from the file: either works or refuses with a `DomainError`."""
    for run in (lambda: import_model(fmt, text, LOAN, None, data_for(LOAN)), lambda: start_from_file(fmt, text, "H", "h-sys")):
        with contextlib.suppress(DomainError):
            run()


@pytest.mark.parametrize(("fmt", "text"), [
    ("mermaid", MERMAID.format("#99999999999;")),  # a numeric escape beyond Unicode
    ("mermaid", MERMAID.format("#" + "9" * 5000 + ";")),  # more digits than Python converts
    ("plantuml", PLANT.format("B --> C : x<U+FFFFFF>")),  # a code point beyond U+10FFFF
    ("plantuml", PLANT.format("B --> C : x<U+D800>")),  # a lone surrogate
    ("plantuml", CLASS.format("[" + "9" * 5000 + "]")),  # a multiplicity of 5,000 digits
    ("plantuml", CLASS.format("{maxLength = " + "9" * 5000 + "}")),
])
def test_an_escape_or_a_number_no_reader_can_convert_is_read_or_refused_never_a_crash(fmt, text):
    _both(fmt, text)


def test_an_escape_that_is_not_a_character_is_kept_as_written():
    assert plantuml.unescape("a<U+FFFFFF>b<U+00E9>") == "a<U+FFFFFF>bé"
    assert mermaid.unescape("#99999999999;#233;") == "#99999999999;é"


def test_an_xmi_bound_written_with_a_digit_int_refuses_and_a_draw_io_position_that_is_not_a_number():
    xmi, _ = export_model("xmi", LOAN, None, data_for(LOAN))
    assert 'value="1"' in xmi
    _both("xmi", xmi.replace('value="1"', 'value="²"', 1))  # str.isdigit accepts "²"; int does not
    drawio, _ = export_model("drawio", LOAN, None, data_for(LOAN))
    for bad in ("1e", "--10", "nan", "inf", "1e400"):
        # Positions only order what was drawn: an unreadable one counts as 0 and the drawing still reads back unchanged.
        report = import_model("drawio", drawio.replace('<mxGeometry x="', f'<mxGeometry x="{bad}'), LOAN, None, data_for(LOAN))
        assert report["status"] == "CLEAN", bad


_JUNK = ["\x00", "﻿", "<", ">", "&", "&amp;", "]]>", "\n", "-->", ":", "[", "]", '"', "{", "}", "|", "é", "@enduml",
         "@startuml", "state", "class", "<|--", "0..*", "\r\n", "<!DOCTYPE x>", "&#0;", "--", "1" * 40, "#99999999;", "<U+FFFFFF>",
         'x="1e"', "²"]


def _mutate(rng: random.Random, text: str) -> str:
    chars = list(text)
    for _ in range(rng.randint(1, 8)):
        at = rng.randrange(len(chars) + 1)
        roll = rng.random()
        if roll < 0.4:
            chars[at:at] = list(rng.choice(_JUNK))
        elif roll < 0.7 and chars:
            del chars[at:at + rng.randint(1, 30)]
        elif chars:
            a, b = sorted((rng.randrange(len(chars)), rng.randrange(len(chars))))
            chars[at:at] = chars[a:b][:200]
    return "".join(chars)


@pytest.mark.parametrize("fmt", FORMATS)
def test_a_mutated_export_is_read_or_refused_by_every_reader_never_a_crash(fmt):
    """Seeded mutation fuzz straight at the readers, under the net in `parse_file`, so a new crash is seen here."""
    rng = random.Random(f"hostile-{fmt}")  # noqa: S311 - a seeded fuzz, not a secret
    exports = [export_model(fmt, pack, None, data_for(pack))[0] for pack in PACKS]
    for _ in range(150):
        text = _mutate(rng, rng.choice(exports))
        with contextlib.suppress(DomainError):
            _READERS[fmt](text)


def test_a_reader_crash_reaches_the_person_as_a_refusal(monkeypatch):
    def broken(_text):
        raise ValueError("an unexpected reader failure")

    monkeypatch.setitem(_READERS, "plantuml", broken)
    with pytest.raises(DomainError) as refused:
        import_model("plantuml", PLANT.format(""), LOAN, None, data_for(LOAN))
    assert refused.value.code == "IMPORT_INVALID" and "unexpected" not in refused.value.message


# --- the plan check: each step is applied once, and the verdicts are the replay's -----------------------------------

def _replayed(model, pack, transactions, accepted):
    """The reference: what `_statuses` did before ADR-0236, replaying every kept step for each new one."""
    kept, out = [], []
    for tx, keep in zip(transactions, accepted, strict=True):
        if not keep:
            out.append("rejected")
            continue
        try:
            steps = [*kept, tx]
            structural, data_steps = split(steps)
            if isinstance(tx, SetRoleKind):
                set_kinds(pack, [tx])
            elif is_data(tx):
                apply_data(data_for(pack), data_steps)
            else:
                apply_structural_all(model, structural, pack)
            kept.append(tx)
            out.append("applies")
        except DomainError as error:
            out.append(error.code)
    return out


def _random_step(rng: random.Random, pack) -> dict:
    model = pack.model
    states, transitions = list(model.states), [t.id for t in model.transitions]
    actions, roles = [a.id for a in pack.actions], [r.id for r in pack.roles]
    kind = rng.choice(["add_state", "rename_state", "remove_state", "set_initial", "add_transition", "retarget_transition",
                       "remove_transition", "set_role", "set_effects"])
    fresh = f"S{rng.randrange(4)}"
    return {
        "add_state": lambda: {"kind": kind, "state": rng.choice([*states, fresh])},
        "rename_state": lambda: {"kind": kind, "state": rng.choice([*states, fresh]), "to": rng.choice([*states, fresh])},
        "remove_state": lambda: {"kind": kind, "state": rng.choice([*states, fresh])},
        "set_initial": lambda: {"kind": kind, "state": rng.choice([*states, fresh])},
        "add_transition": lambda: {"kind": kind, "id": f"T-{rng.randrange(3)}", "action": rng.choice(actions),
                                   "from_state": rng.choice([*states, fresh]), "to_state": rng.choice([*states, fresh]),
                                   "role": rng.choice(roles)},
        "retarget_transition": lambda: {"kind": kind, "transition": rng.choice([*transitions, "T-0"]),
                                        "end": rng.choice(["source", "target"]), "state": rng.choice([*states, fresh])},
        "remove_transition": lambda: {"kind": kind, "transition": rng.choice([*transitions, "T-0"])},
        "set_role": lambda: {"kind": kind, "transition": rng.choice(transitions), "role": rng.choice(roles)},
        "set_effects": lambda: {"kind": kind, "transition": rng.choice(transitions), "required_effects": []},
    }[kind]()


def test_each_step_of_a_plan_gets_the_verdict_replaying_the_steps_before_it_gives():
    rng = random.Random("plan-differential")  # noqa: S311 - a seeded fuzz, not a secret
    compared = 0
    for _ in range(400):
        pack = rng.choice(PACKS)
        steps = [parse_transaction(_random_step(rng, pack)) for _ in range(rng.randint(1, 8))]
        accepted = [rng.random() < 0.8 for _ in steps]
        statuses = preview_plan(pack.model, pack, steps, accepted)["steps"]
        assert [s.get("code", s["status"]) for s in statuses] == _replayed(pack.model, pack, steps, accepted)
        compared += 1
    assert compared == 400


def test_a_full_plan_applies_each_step_once_not_once_per_later_step(monkeypatch):
    calls = []
    real = transactions_module.apply_structural
    monkeypatch.setattr(transactions_module, "apply_structural", lambda *a: calls.append(1) or real(*a))
    monkeypatch.setattr("eija_studio.domain.policy.apply_structural", transactions_module.apply_structural)
    pack = LOAN
    steps = [parse_transaction({"kind": "set_role", "transition": t.id, "role": t.role}) for t in pack.model.transitions]
    steps = (steps * (MAX_DRAFT_STEPS // len(steps) + 1))[:MAX_DRAFT_STEPS]
    result = preview_plan(pack.model, pack, steps, [True] * len(steps))
    assert result["legal"] and all(s["status"] == "applies" for s in result["steps"])
    # One application per step in the step-by-step check, plus the whole plan once more through the policy.
    assert len(calls) <= 2 * MAX_DRAFT_STEPS, len(calls)
    assert plan_module._Applied  # the cursor the check uses


# --- the command line: a stable code and a sentence, never a traceback --------------------------------------------

def _cli(capsys, *argv) -> tuple[int, dict]:
    code = main(list(argv))
    return code, json.loads(capsys.readouterr().out)


@pytest.mark.parametrize(("content", "error"), [
    (b"\xff\xfe\x00garbage", "NOT_UTF8"),
    (b"{", "INVALID_JSON"),
    (b"[]", "SCHEMA_INVALID"),
    (b'{"id": 1}', "SCHEMA_INVALID"),
    (b"[" * 100_000 + b"]" * 100_000, "INVALID_JSON"),
])
def test_a_bad_workflow_file_is_named_by_what_is_wrong_with_it(tmp_path, capsys, content, error):
    bad = tmp_path / "workflow.json"
    bad.write_bytes(content)
    code, report = _cli(capsys, "scxml", "--workflow", str(bad))
    assert code == 2 and report["error"] == error, report
    assert "garbage" not in json.dumps(report)  # the file's content is never echoed


def test_a_schema_failure_names_the_fields_but_not_their_values(tmp_path, capsys):
    bad = tmp_path / "workflow.json"
    bad.write_text(json.dumps({"id": "secret-value-1234567890" * 3, "states": "not-a-list"}), encoding="utf-8")
    code, report = _cli(capsys, "laws", "--workflow", str(bad))
    assert code == 2 and report["error"] == "SCHEMA_INVALID"
    fields = {f["field"] for f in report["details"]["fields"]}
    assert "states" in fields and "secret-value" not in json.dumps(report)


def test_a_missing_file_or_a_folder_is_named(tmp_path, capsys):
    assert _cli(capsys, "uml", "import", str(tmp_path / "nope.puml"))[1] == {
        "error": "FILE_NOT_FOUND", "message": f"No such file: {tmp_path / 'nope.puml'}"}
    assert _cli(capsys, "scxml", "--workflow", str(tmp_path))[1]["error"] == "NOT_A_FILE"


@pytest.mark.parametrize(("content", "error"), [(b"[]", "SCHEMA_INVALID"), (b"null", "SCHEMA_INVALID"),
                                                (b"[" * 100_000 + b"]" * 100_000, "INPUT_TOO_DEEP")])
def test_check_export_refuses_a_file_that_is_not_an_export_object(tmp_path, capsys, content, error):
    bad = tmp_path / "export.json"
    bad.write_bytes(content)
    code, report = _cli(capsys, "check-export", str(bad))
    assert code == 2 and report["error"] == error


# --- a saved draft on disk that cannot be reopened -------------------------------------------------------------------

SESSION = "synthetic-hostile-input-test"
HEADERS = {"Authorization": "Bearer " + SESSION, "Origin": "http://127.0.0.1:8765"}


@pytest.mark.parametrize("stored", [
    {"steps": "abc"},
    {"steps": [{"transaction": "not-an-object"}]},
    {"steps": [], "accepted": [1, 2]},
    {"steps": [], "screens": ["not", "an", "object"]},
    {"steps": [], "saved": "yesterday"},
])
def test_a_saved_draft_in_another_shape_is_set_aside_not_reopened(tmp_path, stored):
    launched = PACKS_ROOT / "library-loan"
    studio = harness_studio(tmp_path / "workspace", pack=launched)
    handle = StudioHandle(studio)
    systems = Systems(handle, SystemLibrary(tmp_path / "home"), lambda pack, workspace: harness_studio(workspace, pack=pack),
                      launched, tmp_path / "workspace")
    app = create_app(handle, SESSION, systems=systems)
    try:
        client = TestClient(app, base_url=HEADERS["Origin"])
        draft = tmp_path / "workspace" / "draft.json"
        draft.write_text(json.dumps(stored), encoding="utf-8")
        body = client.get("/api/play/draft", headers=HEADERS).json()
        assert body["draft"] is None and body["set_aside"] is True
        assert not draft.exists() and json.loads((tmp_path / "workspace" / "draft.unreadable.json").read_text()) == stored
        # The next Save writes a fresh draft, and the set-aside one is still there.
        assert client.post("/api/play/draft", json={"steps": []}, headers=HEADERS).status_code == 200
        assert client.get("/api/play/draft", headers=HEADERS).json()["draft"]["steps"] == []
        assert (tmp_path / "workspace" / "draft.unreadable.json").is_file()
        # A second unreadable draft is set aside beside the first, never over it.
        draft.write_text(json.dumps({"steps": "second"}), encoding="utf-8")
        assert client.get("/api/play/draft", headers=HEADERS).json()["set_aside"] is True
        assert json.loads((tmp_path / "workspace" / "draft.unreadable.json").read_text()) == stored
        assert json.loads((tmp_path / "workspace" / "draft.unreadable-2.json").read_text()) == {"steps": "second"}
    finally:
        app.state.play.stop()
