"""A build identity binds all generated inputs; an equal workflow alone is insufficient."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from eija_studio.application.build_subject import SUBJECT_FILE, build_subject, checked_build_subject
from eija_studio.domain.models import DomainError, canonical
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces import app_build

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def measured_identity():
    return {"implementation": "fixture-implementation", "trusted_fixture": False}


@pytest.fixture
def identity_provider(measured_identity):
    return lambda: dict(measured_identity)


@pytest.fixture
def generated(identity_provider):
    pack = load_pack(ROOT / "packs/library-loan")
    return app_build.app_files(pack, pack.model, identity_provider=identity_provider)


def changed_json(files, path, mutate):
    result = dict(files)
    document = json.loads(result[path])
    mutate(document)
    result[path] = canonical(document) + "\n"
    return result


def identity_for(files, previous, **changes):
    return build_subject(files, implementation_digest=changes.get("implementation", previous["implementation_digest"]),
                         template_paths=previous["template_paths"])


def test_subject_is_exact_deterministic_and_contains_no_authority(generated):
    files, manifest = generated
    subject = manifest["subject"]
    assert checked_build_subject(files) == subject == json.loads(files[SUBJECT_FILE])
    assert identity_for(dict(reversed(list(files.items()))), subject) == subject
    assert subject["format"] == "eija.build-subject.v1"
    assert SUBJECT_FILE not in subject["payload_paths"]
    assert not {"approved", "trusted_fixture", "receipt", "token"} & subject.keys()


@pytest.mark.parametrize("path,mutate,field", [
    ("app/model.json", lambda d: d["states"].reverse(), "workflow_digest"),
    ("app/pack.json", lambda d: d["pack"].update(description="Different domain description"), "pack_digest"),
    ("app/data.json", lambda d: d["entities"][0].update(description="Changed data meaning"), "data_digest"),
    ("app/screens.json", lambda d: d["screens"][0].update(title="Different screen"), "screens_digest"),
])
def test_each_contract_substitution_changes_subject_even_with_same_workflow(generated, path, mutate, field):
    files, manifest = generated
    previous = manifest["subject"]
    replaced = changed_json(files, path, mutate)
    subject = identity_for(replaced, previous)
    assert subject["model_hash"] == previous["model_hash"]
    assert subject[field] != previous[field]
    assert subject["digest"] != previous["digest"]
    with pytest.raises(DomainError, match="Generated files differ"):
        checked_build_subject(replaced)


def test_template_implementation_and_arbitrary_payload_substitutions_change_subject(generated):
    files, manifest = generated
    previous = manifest["subject"]
    template = files | {"app/web/app.css": files["app/web/app.css"] + "\n/* changed template */\n"}
    template_subject = identity_for(template, previous)
    assert template_subject["templates_digest"] != previous["templates_digest"]
    assert template_subject["digest"] != previous["digest"]
    assert identity_for(files, previous, implementation="other-implementation")["digest"] != previous["digest"]
    extra = files | {"new-executable.py": "raise RuntimeError('different app')\n"}
    assert identity_for(extra, previous)["digest"] != previous["digest"]
    with pytest.raises(DomainError, match="Generated files differ"):
        checked_build_subject(extra)


def test_navigation_substitution_cannot_borrow_the_same_workflow_build(generated):
    files, manifest = generated
    previous = manifest["subject"]
    changed = changed_json(files, "app/navigation.json", lambda d: d["destinations"][0].update(title="Altered records"))
    subject = identity_for(changed, previous)
    assert subject["model_hash"] == previous["model_hash"]
    assert subject["screens_digest"] == previous["screens_digest"]
    assert subject["generated_files_hash"] != previous["generated_files_hash"]
    assert subject["digest"] != previous["digest"]
    with pytest.raises(DomainError, match="Generated files differ"):
        checked_build_subject(changed)


def test_missing_subject_and_cross_pack_contract_are_refused(generated):
    files, manifest = generated
    with pytest.raises(DomainError, match="missing or invalid"):
        checked_build_subject({k: v for k, v in files.items() if k != SUBJECT_FILE})
    other = changed_json(files, "app/screens.json", lambda d: d.update(id="different-pack"))
    with pytest.raises(DomainError, match="same pack"):
        identity_for(other, manifest["subject"])


def test_cached_build_remeasures_templates_and_implementation_without_relabelling_old_snapshot(
        generated, monkeypatch, measured_identity, identity_provider):
    before_files, before_manifest = generated
    pack = load_pack(ROOT / "packs/library-loan")
    real_resources = app_build.resource_files

    class ChangedTemplates:
        def __init__(self, path):
            self.path = path

        def joinpath(self, name):
            return ChangedTemplates(self.path.joinpath(name))

        def read_text(self, **kwargs):
            original = self.path.read_text(**kwargs)
            return original + "\n/* revised */\n" if self.path.name == "app.css.tmpl" else original

    monkeypatch.setattr(app_build, "resource_files", lambda name: ChangedTemplates(real_resources(name)))
    after_files, after_manifest = app_build.app_files(pack, pack.model, identity_provider=identity_provider)
    assert before_manifest["subject"]["digest"] != after_manifest["subject"]["digest"]
    assert before_files["app/web/app.css"] != after_files["app/web/app.css"]
    measured_identity["implementation"] = "changed-implementation"
    _, changed_manifest = app_build.app_files(pack, pack.model, identity_provider=identity_provider)
    assert changed_manifest["subject"]["implementation_digest"] != after_manifest["subject"]["implementation_digest"]
    assert checked_build_subject(before_files) == before_manifest["subject"]


def test_source_changed_during_generation_refuses_mixed_subject():
    pack = load_pack(ROOT / "packs/eija-review-slice")
    observations = iter(({"implementation": "race-before"}, {"implementation": "race-after"}))
    with pytest.raises(DomainError, match="Implementation changed"):
        app_build.app_files(pack, pack.model, identity_provider=lambda: next(observations))


def test_build_stops_before_changed_payload_but_preserves_identical_running_files(generated, tmp_path, monkeypatch, identity_provider):
    files, manifest = generated
    snapshots = []

    def captured(*args, **kwargs):
        snapshots.append(1)
        return dict(files), dict(manifest)

    monkeypatch.setattr(app_build, "app_files", captured)
    pack = load_pack(ROOT / "packs/library-loan")
    out = tmp_path / "app"
    stops = []
    app_build.build_into(out, pack, pack.model, identity_provider, run_tests=False, before_write=lambda: stops.append("initial"))
    original_stat = (out / "app/model.json").stat().st_mtime_ns
    (out / "data").mkdir()
    (out / "data/records.db").write_bytes(b"preserved records")
    app_build.build_into(out, pack, pack.model, identity_provider, run_tests=False, before_write=lambda: stops.append("identical"))
    assert stops == ["initial"] and len(snapshots) == 2
    assert (out / "app/model.json").stat().st_mtime_ns == original_stat
    target = out / "app/web/app.css"
    target.write_bytes(b"tampered while an old process runs")
    app_build.build_into(out, pack, pack.model, identity_provider, run_tests=False,
                         before_write=lambda: stops.append(target.read_text(encoding="utf-8")))
    assert stops[-1] == "tampered while an old process runs" and len(snapshots) == 3
    assert target.read_bytes() == files["app/web/app.css"].encode("utf-8")
    assert (out / "data/records.db").read_bytes() == b"preserved records"


def test_foreign_output_is_refused_before_stopping_current_app(generated, tmp_path, monkeypatch, identity_provider):
    monkeypatch.setattr(app_build, "app_files", lambda *args, **kwargs: generated)
    pack = load_pack(ROOT / "packs/library-loan")
    (tmp_path / "personal.txt").write_text("Leave this alone", encoding="utf-8")
    stops = []
    with pytest.raises(DomainError, match="not empty"):
        app_build.build_into(tmp_path, pack, pack.model, identity_provider, run_tests=False,
                             before_write=lambda: stops.append(True))
    assert stops == [] and (tmp_path / "personal.txt").read_text(encoding="utf-8") == "Leave this alone"


@pytest.mark.parametrize("phase", ["before", "after"])
@pytest.mark.parametrize("mutation", ["payload", "implementation", "rebuilt_subject", "extra_file"])
def test_build_cannot_publish_pass_for_a_subject_changed_around_conformance(
        generated, tmp_path, monkeypatch, phase, mutation, identity_provider, measured_identity):
    files, manifest = generated
    pack = load_pack(ROOT / "packs/library-loan")
    monkeypatch.setattr(app_build, "app_files", lambda *args, **kwargs: (dict(files), dict(manifest)))
    calls = []

    def change_output():
        if mutation == "implementation":
            measured_identity["implementation"] = "different-during-test"
            return
        if mutation == "extra_file":
            (tmp_path / "app/unbound.py").write_text("# an unbound module\n", encoding="utf-8")
            return
        target = tmp_path / "app/web/app.css"
        target.write_bytes(target.read_bytes() + b"\n/* changed during checks */\n")
        if mutation == "rebuilt_subject":
            changed = {path: (tmp_path / path).read_bytes().decode("utf-8") for path in files}
            replacement = identity_for(changed, manifest["subject"])
            (tmp_path / SUBJECT_FILE).write_bytes(canonical(replacement).encode("utf-8"))

    original_write = app_build._write_changed

    def write_then_change(*args):
        hashes = original_write(*args)
        if phase == "before":
            change_output()
        return hashes

    def run_then_change(_out):
        calls.append(True)
        if phase == "after":
            change_output()
        return {"status": "PASS", "detail": "synthetic runner outcome"}

    monkeypatch.setattr(app_build, "_write_changed", write_then_change)
    monkeypatch.setattr(app_build, "conformance", run_then_change)
    result = app_build.build_into(tmp_path, pack, pack.model, identity_provider)
    recorded = json.loads((tmp_path / "BUILD.json").read_text(encoding="utf-8"))
    assert recorded["conformance"] == result["conformance"]
    assert result["conformance"]["status"] == "FAIL"
    assert result["conformance"]["binding"] == "MISMATCH"
    assert result["conformance"]["subject_digest"] == manifest["subject"]["digest"]
    assert bool(calls) is (phase == "after")  # reject pre-existing drift before executing tests


def test_bound_conformance_records_the_exact_checked_subject(generated, tmp_path, monkeypatch, identity_provider):
    files, manifest = generated
    pack = load_pack(ROOT / "packs/library-loan")
    monkeypatch.setattr(app_build, "app_files", lambda *args, **kwargs: (dict(files), dict(manifest)))
    monkeypatch.setattr(app_build, "conformance", lambda _out: {"status": "PASS", "detail": "synthetic runner outcome"})
    result = app_build.build_into(tmp_path, pack, pack.model, identity_provider)
    assert result["conformance"]["status"] == "PASS"
    assert result["conformance"]["subject_digest"] == result["subject"]["digest"]
