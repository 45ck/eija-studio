"""A retained build identity cannot label a different installed kernel as that build."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import eija_studio.adapters.identity as measured
from eija_studio.application.build_subject import checked_build_subject
from eija_studio.domain.models import fingerprint
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces import app_build

ROOT = Path(__file__).resolve().parents[1]
INSTALLED_A = {"runtime.py": "synthetic-installed-implementation-A"}
INSTALLED_B = {"runtime.py": "synthetic-installed-implementation-B"}


@pytest.fixture
def retained_build(tmp_path):
    """Only the measured implementation port is synthetic; app generation/startup are real."""
    pack = load_pack(ROOT / "packs/library-loan")
    files, manifest = app_build.app_files(pack, pack.model, identity_provider=lambda: {"implementation": fingerprint(INSTALLED_A)})
    app_build.write(tmp_path, files)
    return tmp_path, files, manifest["subject"]


def start_description(directory, installed):
    # A fresh interpreter executes the generated server's real startup before any route can be served.
    script = ("import json\nfrom unittest.mock import patch\n"
              f"with patch('eija_studio.bootstrap.implementation_manifest', return_value={installed!r}):\n"
              " import app.server\n print(json.dumps(app.server.describe()))\n")
    return subprocess.run([sys.executable, "-c", script], cwd=directory, capture_output=True,  # noqa: S603 - fixed interpreter and test-authored script
                          text=True, encoding="utf-8", timeout=30, check=False)


def test_matching_installed_implementation_can_describe_exact_retained_build(retained_build):
    directory, files, subject = retained_build
    result = start_description(directory, INSTALLED_A)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["subject"] == subject
    assert checked_build_subject(files) == subject


def test_changed_installed_kernel_is_refused_without_relabelling_retained_build(retained_build):
    directory, files, subject = retained_build
    result = start_description(directory, INSTALLED_B)
    assert result.returncode != 0
    assert "BUILD_IMPLEMENTATION_MISMATCH" in result.stderr
    assert result.stdout == ""
    assert subject["implementation_digest"] == fingerprint(INSTALLED_A)
    assert checked_build_subject(files) == subject  # archived identity remains inspectable
    for path, content in files.items():
        assert (directory / path).read_bytes() == content.encode("utf-8")


def test_core_implementation_identity_includes_template_only_changes(tmp_path, monkeypatch):
    kernel = tmp_path / "domain/runtime.py"
    template = tmp_path / "resources/appgen/web/app.css.tmpl"
    kernel.parent.mkdir(parents=True)
    template.parent.mkdir(parents=True)
    kernel.write_text("# unchanged kernel\n", encoding="utf-8")
    template.write_text("body { color: black; }\n", encoding="utf-8")
    monkeypatch.setattr(measured, "PACKAGE", tmp_path)
    before = measured.implementation_files()
    template.write_text("body { color: navy; }\n", encoding="utf-8")
    after = measured.implementation_files()
    assert before["domain/runtime.py"] == after["domain/runtime.py"]
    assert before["resources/appgen/web/app.css.tmpl"] != after["resources/appgen/web/app.css.tmpl"]
    assert fingerprint(before) != fingerprint(after)


@pytest.mark.parametrize("observations,passes", [
    ([INSTALLED_A, INSTALLED_A], True),
    ([INSTALLED_B], False),
    ([INSTALLED_A, INSTALLED_B], False),
])
def test_generated_conformance_requires_same_installed_implementation_before_and_after(retained_build, observations, passes):
    directory, files, subject = retained_build
    script = ("import sys, unittest\nfrom unittest.mock import patch\n"
              f"with patch('eija_studio.bootstrap.implementation_manifest', side_effect={observations!r}):\n"
              " suite = unittest.TestLoader().discover('tests', top_level_dir='.')\n"
              " result = unittest.TextTestRunner().run(suite)\n"
              " sys.exit(0 if result.wasSuccessful() else 1)\n")
    result = subprocess.run([sys.executable, "-c", script], cwd=directory, capture_output=True,  # noqa: S603 - fixed interpreter and test-authored script
                            text=True, encoding="utf-8", timeout=30, check=False)
    assert (result.returncode == 0) is passes, result.stderr
    if not passes:
        assert "BUILD_IMPLEMENTATION_MISMATCH" in result.stderr
    assert checked_build_subject(files) == subject
