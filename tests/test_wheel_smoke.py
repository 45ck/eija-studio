"""Negative controls for the explicit installation proof, without installing packages."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import zipfile

import pytest

from scripts import candidate_wheel_smoke as smoke


def wheel_fixture(tmp_path, *, changed=None, extra=None, requirement="", version="9.8.7"):
    source = tmp_path / "source"
    authored = {"src/eija_studio/__init__.py": b"__version__ = '9.8.7'\n",
                "src/eija_studio/resources/web/agent-edit.js": b"// candidate asset\n",
                "src/eija_studio/resources/appgen/view.tmpl": b"template bytes\n",
                "packs/default.json": b'{"pack":"fixture"}',
                "packs/fixture/pack.json": b'{"synthetic":"pack"}'}
    archive_files = {}
    for name, content in authored.items():
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        installed = name.removeprefix("src/") if name.startswith("src/") else "eija_studio/resources/" + name
        archive_files[installed] = b"wrong bytes" if changed == installed else content
    if extra:
        archive_files[extra] = b"retired pack"
    wheel = tmp_path / "candidate.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        for name, content in archive_files.items():
            archive.writestr(name, content)
        metadata = f"Name: eija-studio\nVersion: {version}\n"
        if requirement:
            metadata += f"Requires-Dist: {requirement}\n"
        archive.writestr("eija_studio.dist-info/METADATA", metadata)
    return wheel, source


def test_wheel_version_and_resource_manifest_come_from_candidate(tmp_path):
    wheel, source = wheel_fixture(tmp_path)
    result = smoke.inspect_wheel(wheel, source)
    assert result["version"] == "9.8.7"
    assert result["resources"]["eija_studio/resources/appgen/view.tmpl"] == smoke.digest(b"template bytes\n")
    assert result["resources"]["eija_studio/resources/packs/default.json"] == smoke.digest(b'{"pack":"fixture"}')


@pytest.mark.parametrize("changed", ["eija_studio/__init__.py", "eija_studio/resources/appgen/view.tmpl",
                                     "eija_studio/resources/packs/fixture/pack.json"])
def test_stale_code_template_or_pack_wheel_is_refused(tmp_path, changed):
    wheel, source = wheel_fixture(tmp_path, changed=changed)
    with pytest.raises(AssertionError, match="Wheel content differs"):
        smoke.inspect_wheel(wheel, source)


def test_retired_pack_in_wheel_is_refused(tmp_path):
    wheel, source = wheel_fixture(tmp_path, extra="eija_studio/resources/packs/retired/pack.json")
    with pytest.raises(AssertionError, match="Retired/extra"):
        smoke.inspect_wheel(wheel, source)


def test_offline_flag_cannot_hide_direct_dependency_egress(tmp_path):
    wheel, _ = wheel_fixture(tmp_path, requirement="example @ https://invalid.example/dependency.whl")
    wheelhouse = tmp_path / "dependency wheels"
    wheelhouse.mkdir()
    with pytest.raises(AssertionError, match="Direct dependency URLs"):
        smoke.check_offline_inputs(wheel, wheelhouse)


def test_runtime_environment_drops_checkout_paths_and_live_provider_settings(monkeypatch):
    monkeypatch.setenv("PYTHONPATH", "source-checkout")
    monkeypatch.setenv("PYTHONHOME", "borrowed-python")
    monkeypatch.setenv("EIJA_PROVIDER", "live-provider")
    monkeypatch.setenv("EIJA_PACK", "unrelated-policy")
    monkeypatch.setenv("PIP_EXTRA_INDEX_URL", "https://invalid.example")
    monkeypatch.setenv("VIRTUAL_ENV", "inherited-venv")
    result = smoke.clean_environment()
    assert not {"PYTHONPATH", "PYTHONHOME", "EIJA_PROVIDER", "EIJA_PACK", "PIP_EXTRA_INDEX_URL", "VIRTUAL_ENV"} & result.keys()
    assert result["PYTHONNOUSERSITE"] == "1"


def test_proof_cannot_write_inside_checkout_or_replace_previous_results(tmp_path):
    source, scratch = tmp_path / "source", tmp_path / "outside"
    source.mkdir()
    scratch.mkdir()
    args = argparse.Namespace(source=source, scratch_root=source, out=scratch / "report.json")
    with pytest.raises(AssertionError, match="outside source"):
        smoke.output_paths(args)
    args.scratch_root, args.out = scratch, source / "report.json"
    with pytest.raises(AssertionError, match="outside frozen"):
        smoke.output_paths(args)
    args.out = scratch / "report.json"
    args.out.write_text("prior failure", encoding="utf-8")
    with pytest.raises(AssertionError, match="retain previous"):
        smoke.output_paths(args)
    assert args.out.read_text(encoding="utf-8") == "prior failure"


def test_install_failure_stays_fail_and_retains_report(tmp_path, monkeypatch):
    wheel, source = wheel_fixture(tmp_path)
    scratch, wheelhouse = tmp_path / "outside", tmp_path / "wheels"
    scratch.mkdir()
    wheelhouse.mkdir()
    output = scratch / "failed-install.json"

    def failed_install(*args):
        raise RuntimeError("missing dependency wheel; no network fallback")

    monkeypatch.setattr(smoke, "install_venv", failed_install)
    status = smoke.main(argv=["--wheel", str(wheel), "--source", str(source), "--out", str(output),
                              "--scratch-root", str(scratch), "--wheelhouse", str(wheelhouse)])
    report = json.loads(output.read_text(encoding="utf-8"))
    assert status == 1 and report["status"] == "FAIL"
    assert report["clean_room_dependency_install"] == "FAIL"
    assert "no network fallback" in report["failure"]
    assert (scratch / "failed-install-artifacts/wheel-manifest.json").is_file()


@pytest.mark.parametrize("inheritance", ["false", "true"])
def test_venv_install_keeps_dependencies_enabled_and_rejects_inheritance(tmp_path, monkeypatch, inheritance):
    args = argparse.Namespace(python="base-python", wheelhouse=tmp_path / "wheels", wheel=tmp_path / "app.whl")
    commands = []

    def run(command, scratch, artifacts, name):
        commands.append(command)
        if name == "create-venv":
            environment = Path(command[-1])
            environment.mkdir()
            (environment / "pyvenv.cfg").write_text(f"include-system-site-packages = {inheritance}\n", encoding="utf-8")
        return "[]"

    monkeypatch.setattr(smoke, "run_checked", run)
    if inheritance == "true":
        with pytest.raises(AssertionError, match="inherited system packages"):
            smoke.install_venv(args, tmp_path, tmp_path)
        assert len(commands) == 1
        return
    python = smoke.install_venv(args, tmp_path, tmp_path)
    assert "fresh environment" in str(python)
    install = next(command for command in commands if "install" in command)
    assert {"--no-index", "--no-cache-dir", "--only-binary=:all:", "--report", "-I"} <= set(install)
    assert "--no-deps" not in install and "--target" not in install
    assert not any("--system-site-packages" in command for command in commands)
