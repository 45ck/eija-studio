"""Shipped React source and its prebuilt assets must describe the same frontend.

These are artifact-integrity checks; rendered controls, CSP, keyboard use and
refusal/recovery are checked by the real generated-app browser journeys.
"""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from eija_studio.domain.pack import load_pack
from eija_studio.interfaces.app_build import app_files
from eija_studio.bootstrap import source_identity

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src/eija_studio/resources/appgen"
SOURCE = APP / "react-source"


def test_prebuilt_react_assets_match_every_authored_input_and_locked_dependency():
    manifest = json.loads((SOURCE / "build-manifest.json").read_text(encoding="utf-8"))
    package = json.loads((SOURCE / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((SOURCE / "package-lock.json").read_text(encoding="utf-8"))
    assert manifest["format"] == "eija.react-frontend.v1"
    assert {"react", "react-dom", "@mantine/core", "@mantine/hooks"} <= package["dependencies"].keys()
    assert manifest["dependencies"] == package["dependencies"] == lock["packages"][""]["dependencies"]
    for name, digest in manifest["sources"].items():
        assert sha256((SOURCE / name).read_bytes()).hexdigest() == digest, name
    for name, digest in manifest["outputs"].items():
        assert sha256((APP / "web" / (name + ".tmpl")).read_bytes()).hexdigest() == digest, name


def test_generated_export_contains_the_authored_react_build_without_node_modules():
    pack = load_pack(ROOT / "packs/library-loan")
    files, _ = app_files(pack, pack.model, identity_provider=source_identity)
    manifest = json.loads(files["frontend/build-manifest.json"])
    for name, digest in manifest["sources"].items():
        assert sha256(files[f"frontend/{name}"].encode()).hexdigest() == digest, name
    assert not any("node_modules" in name.split("/") for name in files)
    assert manifest["runtime"]["node_required"] is False
    assert manifest["runtime"]["network_required"] is False
