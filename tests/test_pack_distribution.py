"""Bundled packs preserve authoritative bytes and existing pack-resolution boundaries.

The build-hook checks stub setuptools' build step; installed-wheel behavior has a
separate smoke test. Runtime resolution tests do not require setuptools.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from eija_studio.domain import pack as packs

CANONICAL_PACKS = packs.PACKS_ROOT
SETUP = Path(__file__).resolve().parents[1] / "setup.py"


def document(name="excursion"):
    return json.loads((CANONICAL_PACKS / name / "pack.json").read_text(encoding="utf-8"))


def write_pack(root, name="excursion", *, description=None, default=False):
    value = copy.deepcopy(document(name))
    if description is not None:
        value["pack"]["description"] = description
    target = root / name / "pack.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if default:
        (root / "default.json").write_text(json.dumps({"pack": name}) + "\n", encoding="utf-8", newline="\n")
    return target


def tree_bytes(root):
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file()}


@pytest.fixture(autouse=True)
def isolated_pack_registry(monkeypatch):
    monkeypatch.setattr(packs, "_LOADED", {})
    monkeypatch.setattr(packs, "_SOURCES", {})
    monkeypatch.delenv(packs.ENV_PACK, raising=False)


@pytest.fixture
def package_tree(tmp_path):
    package = tmp_path / "src" / "eija_studio"
    package.mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_bytes(b'[project]\nname = "eija-studio"\n')
    return package, package.parents[1] / "packs", package / "resources" / "packs"


def test_checkout_without_generated_resources_uses_repository_packs(package_tree, monkeypatch):
    package, repository, _ = package_tree
    write_pack(repository, description="authoritative checkout", default=True)
    root = packs._packs_root(package)
    assert root == repository
    monkeypatch.setattr(packs, "PACKS_ROOT", root)
    assert packs.default_pack().pack.description == "authoritative checkout"


def test_missing_installed_bundle_refuses_valid_adjacent_packs(tmp_path, monkeypatch):
    package = tmp_path / "installed" / "eija_studio"
    package.mkdir(parents=True)
    adjacent = package.parents[1] / "packs"
    write_pack(adjacent, description="unrelated valid adjacent policy", default=True)
    (tmp_path / "pyproject.toml").write_bytes(b'[project]\nname = "eija-studio"\n')
    before = tree_bytes(tmp_path)
    bundled = package / "resources" / "packs"
    root = packs._packs_root(package)
    assert root == bundled and not bundled.exists()
    monkeypatch.setattr(packs, "PACKS_ROOT", root)
    with pytest.raises(packs.PackError):
        packs.default_pack()
    assert packs.find_pack("excursion") is None
    assert tree_bytes(tmp_path) == before


@pytest.mark.parametrize("metadata", [None, b'[project]\nname = "another-project"\n',
                                     b'[project', b'project = "eija-studio"\n', b'\xff'])
def test_source_looking_layout_requires_valid_matching_metadata(package_tree, monkeypatch, metadata):
    package, adjacent, bundled = package_tree
    write_pack(adjacent, description="must not rescue an unrecognized source layout", default=True)
    marker = package.parents[1] / "pyproject.toml"
    if metadata is None:
        marker.unlink()
    else:
        marker.write_bytes(metadata)
    before = tree_bytes(package.parents[1])
    root = packs._packs_root(package)
    assert root == bundled and not bundled.exists()
    monkeypatch.setattr(packs, "PACKS_ROOT", root)
    with pytest.raises(packs.PackError):
        packs.default_pack()
    assert tree_bytes(package.parents[1]) == before


def test_explicit_override_still_works_when_entire_installed_bundle_is_missing(tmp_path, monkeypatch):
    package = tmp_path / "installed" / "eija_studio"
    package.mkdir(parents=True)
    write_pack(package.parents[1] / "packs", description="unselected adjacent policy", default=True)
    configured = write_pack(tmp_path / "explicit", description="explicit configured policy")
    monkeypatch.setattr(packs, "PACKS_ROOT", packs._packs_root(package))
    monkeypatch.setenv(packs.ENV_PACK, str(configured))
    assert packs.default_location() == configured
    assert packs.default_pack().pack.description == "explicit configured policy"


def test_bundle_wins_over_unrelated_legacy_packs(package_tree, monkeypatch):
    package, legacy, bundled = package_tree
    write_pack(legacy, description="unrelated legacy location", default=True)
    write_pack(bundled, description="installed authoritative bundle", default=True)
    root = packs._packs_root(package)
    assert root == bundled
    monkeypatch.setattr(packs, "PACKS_ROOT", root)
    assert packs.default_pack().pack.description == "installed authoritative bundle"


@pytest.mark.parametrize("defect", ["missing-default", "corrupt-default", "missing-pack", "corrupt-pack"])
def test_incomplete_or_corrupt_bundle_never_falls_back_to_legacy(package_tree, monkeypatch, defect):
    package, legacy, bundled = package_tree
    write_pack(legacy, description="must not rescue broken bundle", default=True)
    pack_file = write_pack(bundled, description="bundled", default=True)
    damaged = bundled / "default.json" if defect.endswith("default") else pack_file
    if defect.startswith("missing"):
        damaged.unlink()
    else:
        damaged.write_text("{broken", encoding="utf-8")
    assert packs._packs_root(package) == bundled
    monkeypatch.setattr(packs, "PACKS_ROOT", packs._packs_root(package))
    before = tree_bytes(bundled)
    with pytest.raises(packs.PackError):
        packs.default_pack()
    assert tree_bytes(bundled) == before


def test_explicit_pack_override_keeps_priority_over_bundle(package_tree, monkeypatch, tmp_path):
    package, _, bundled = package_tree
    write_pack(bundled, description="bundled", default=True)
    custom = write_pack(tmp_path / "custom", description="explicit configured contents")
    monkeypatch.setattr(packs, "PACKS_ROOT", packs._packs_root(package))
    monkeypatch.setenv(packs.ENV_PACK, str(custom))
    assert packs.default_location() == custom
    assert packs.default_pack().pack.description == "explicit configured contents"


@pytest.mark.parametrize("defect", ["missing", "corrupt"])
def test_invalid_explicit_override_never_falls_back_to_bundle(package_tree, monkeypatch, tmp_path, defect):
    package, _, bundled = package_tree
    write_pack(bundled, default=True)
    custom = write_pack(tmp_path / "custom", description="retained original snapshot")
    monkeypatch.setattr(packs, "PACKS_ROOT", packs._packs_root(package))
    monkeypatch.setenv(packs.ENV_PACK, str(custom))
    original = packs.default_pack()
    if defect == "missing":
        custom.unlink()
    else:
        custom.write_text("{broken", encoding="utf-8")
    with pytest.raises(packs.PackError):
        packs.default_pack()
    assert original.pack.description == "retained original snapshot"


def test_identity_lookup_uses_the_same_selected_bundle_root(package_tree, monkeypatch):
    package, legacy, bundled = package_tree
    write_pack(legacy, "library-loan", description="unrelated legacy library")
    write_pack(bundled, "excursion", default=True)
    write_pack(bundled, "library-loan", description="bundled library")
    monkeypatch.setattr(packs, "PACKS_ROOT", packs._packs_root(package))
    assert packs.default_pack().id == "excursion"
    library = packs.find_pack("library-loan")
    assert library is not None and library.pack.description == "bundled library"
    assert packs.find_pack("library-loan", digest=library.digest) is library
    assert packs.find_pack("not-a-bundled-pack") is None


@pytest.fixture
def build_hook(monkeypatch):
    setuptools = pytest.importorskip("setuptools", reason="NOT_RUN: setuptools required only for build-hook checks")
    from setuptools.command.build_py import build_py  # noqa: PLC0415 - optional build dependency

    def forbidden_setup(*args, **kwargs):
        raise AssertionError("Importing setup.py must not execute setup()")

    monkeypatch.setattr(setuptools, "setup", forbidden_setup)
    spec = importlib.util.spec_from_file_location("eija_pack_distribution_test_setup", SETUP)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert issubclass(module.BuildWithPacks, build_py)
    return module, setuptools.Distribution, build_py


def command_for(build_hook, tmp_path, monkeypatch):
    module, distribution, base = build_hook
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.setattr(module, "__file__", str(project / "setup.py"))
    command = module.BuildWithPacks(distribution({"name": "synthetic-pack-build"}))
    command.build_lib = str(tmp_path / "build" / "lib")
    command.editable_mode = False
    calls = []
    monkeypatch.setattr(base, "run", lambda self: calls.append("setuptools-build-step"))
    return command, project, Path(command.build_lib) / "eija_studio" / "resources" / "packs", calls


def test_build_hook_copies_exact_json_bytes_without_changing_sources(build_hook, tmp_path, monkeypatch):
    command, project, generated, calls = command_for(build_hook, tmp_path, monkeypatch)
    source = project / "packs"
    write_pack(source, description="Exact UTF-8 source: café", default=True)
    write_pack(source, "library-loan")
    (source / "notes.txt").write_text("Do not ship unrelated source notes", encoding="utf-8")
    before = tree_bytes(project)
    command.run()
    assert calls == ["setuptools-build-step"]
    expected = {name: data for name, data in tree_bytes(source).items() if name.endswith(".json")}
    assert tree_bytes(generated) == expected
    assert tree_bytes(project) == before
    assert not (project / "src" / "eija_studio" / "resources" / "packs").exists()


def test_rebuild_removes_retired_generated_pack_and_keeps_other_resources(build_hook, tmp_path, monkeypatch):
    command, project, generated, calls = command_for(build_hook, tmp_path, monkeypatch)
    source = project / "packs"
    write_pack(source, default=True)
    retired = write_pack(source, "library-loan")
    command.run()
    assert (generated / "library-loan" / "pack.json").read_bytes() == retired.read_bytes()
    sentinel = generated.parent / "unrelated-resource.txt"
    sentinel.write_bytes(b"retain other build resources")
    retired.unlink()  # Deliberate next source revision, not a build-hook side effect.
    before = tree_bytes(project)
    command.run()
    assert calls == ["setuptools-build-step", "setuptools-build-step"]
    assert tree_bytes(generated) == tree_bytes(source)
    assert not (generated / "library-loan" / "pack.json").exists()
    assert sentinel.read_bytes() == b"retain other build resources"
    assert tree_bytes(project) == before


def test_editable_build_does_not_generate_a_second_pack_source(build_hook, tmp_path, monkeypatch):
    command, project, generated, _ = command_for(build_hook, tmp_path, monkeypatch)
    write_pack(project / "packs", default=True)
    command.editable_mode = True
    before = tree_bytes(project)
    command.run()
    assert not generated.exists()
    assert tree_bytes(project) == before

def test_build_output_inside_authored_packs_is_refused_before_base_writes(build_hook, tmp_path, monkeypatch):
    command, project, _, calls = command_for(build_hook, tmp_path, monkeypatch)
    authored = write_pack(project / "packs", default=True)
    command.build_lib = str(project / "packs" / ".build")
    before = tree_bytes(project)
    _, _, base = build_hook

    def corrupting_base_build(self):
        calls.append("forbidden-base-build")
        authored.write_bytes(b"base build must never reach authored files")

    monkeypatch.setattr(base, "run", corrupting_base_build)
    with pytest.raises(ValueError, match="separate from authored source"):
        command.run()
    assert calls == []
    assert tree_bytes(project) == before
