#!/usr/bin/env python3
"""Prove an explicit wheel in a fresh venv outside its source checkout, offline.

Populate --wheelhouse with runtime dependency wheels beforehand. This runner never
downloads dependencies, reuses site-packages, stamps source, or approves.
Run installations only in the serial validation slot.
"""
from __future__ import annotations

import argparse
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_PREFIX = "eija_studio/resources/packs/"


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def authored_package_files(source: Path) -> dict[str, Path]:
    package = source / "src/eija_studio"
    expected = {"eija_studio/" + path.relative_to(package).as_posix(): path
                for path in sorted(package.rglob("*"))
                if is_authored_file(path, package)}
    expected.update({RESOURCE_PREFIX + path.relative_to(source / "packs").as_posix(): path
                     for path in sorted((source / "packs").rglob("*.json"))})
    assert RESOURCE_PREFIX + "default.json" in expected, "Authored default pack pointer is missing"
    return expected


def is_authored_file(path: Path, package: Path) -> bool:
    return (path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
            and (path.suffix == ".py" or "resources" in path.relative_to(package).parts))


def wheel_metadata(archive: zipfile.ZipFile):
    paths = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
    assert len(paths) == 1, "Expected one distribution per wheel"
    return BytesParser().parsebytes(archive.read(paths[0]))


def compare_contents(archive: zipfile.ZipFile, expected: dict[str, Path]) -> dict[str, str]:
    resources = {}
    for name, path in expected.items():
        content = archive.read(name)
        assert content == path.read_bytes(), f"Wheel content differs: {name}"
        resources[name] = digest(content)
    bundled = {name for name in archive.namelist() if name.startswith(RESOURCE_PREFIX) and not name.endswith("/")}
    assert bundled == {name for name in expected if name.startswith(RESOURCE_PREFIX)}, "Retired/extra packs in wheel"
    return resources


def inspect_wheel(wheel: Path, source: Path) -> dict:
    """Bind all authored package and pack bytes, including template/web resources."""
    expected = authored_package_files(source)
    with zipfile.ZipFile(wheel) as archive:
        assert archive.testzip() is None, "Wheel CRC failed"
        metadata = wheel_metadata(archive)
        assert metadata["Name"] == "eija-studio" and metadata["Version"], "Unexpected wheel metadata"
        resources = compare_contents(archive, expected)
    return {"version": metadata["Version"], "requires_dist": metadata.get_all("Requires-Dist", []),
            "resources": resources}


def check_offline_inputs(wheel: Path, wheelhouse: Path) -> None:
    """pip --no-index alone does not prevent direct URL dependencies from doing egress."""
    for candidate in (wheel, *sorted(wheelhouse.glob("*.whl"))):
        with zipfile.ZipFile(candidate) as archive:
            metadata = wheel_metadata(archive)
            assert all("@" not in item for item in metadata.get_all("Requires-Dist", [])), "Direct dependency URLs are not allowed in offline proof"


def clean_environment() -> dict[str, str]:
    """Do not borrow Python paths, pip configuration, or live EIJA provider settings."""
    environment = {key: value for key, value in os.environ.items()
                   if not key.upper().startswith(("PYTHON", "PIP_", "EIJA_")) and key != "VIRTUAL_ENV"}
    environment.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", PIP_CONFIG_FILE=os.devnull)
    return environment


def run_checked(command: list[str], scratch: Path, artifacts: Path, name: str) -> str:
    result = subprocess.run(command, cwd=scratch, env=clean_environment(), capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=240, check=False)
    (artifacts / (name + ".log")).write_text(result.stdout + result.stderr, encoding="utf-8", newline="\n")
    if result.returncode:
        raise RuntimeError(f"{name} failed with exit {result.returncode}; see retained {name}.log")
    return result.stdout


def install_venv(args: argparse.Namespace, scratch: Path, artifacts: Path) -> Path:
    environment = scratch / "fresh environment"
    run_checked([args.python, "-I", "-m", "venv", str(environment)], scratch, artifacts, "create-venv")
    config = (environment / "pyvenv.cfg").read_text(encoding="utf-8").lower()
    assert "include-system-site-packages = false" in config, "Venv inherited system packages"
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    run_checked([str(python), "-I", "-m", "pip", "--isolated", "--disable-pip-version-check", "install", "--no-index", "--no-cache-dir",
                 "--only-binary=:all:", "--find-links", str(args.wheelhouse.resolve()), "--no-compile",
                 "--report", str(artifacts / "pip-install.json"), str(args.wheel.resolve())],
                scratch, artifacts, "install")
    run_checked([str(python), "-I", "-m", "pip", "--isolated", "check"], scratch, artifacts, "pip-check")
    installed = run_checked([str(python), "-I", "-m", "pip", "--isolated", "list", "--format=json"],
                            scratch, artifacts, "installed-packages")
    (artifacts / "installed-packages.json").write_text(installed, encoding="utf-8", newline="\n")
    return python


def runtime_identity(python: Path, scratch: Path, artifacts: Path, source: Path, version: str) -> dict:
    probe = """import importlib.metadata,json,pathlib,site,sys,eija_studio
p=pathlib.Path(eija_studio.__file__).resolve()
assert sys.prefix != sys.base_prefix and not site.ENABLE_USER_SITE
assert p.is_relative_to(pathlib.Path(sys.prefix).resolve())
assert not any(pathlib.Path(x).resolve().is_relative_to(pathlib.Path(sys.argv[1])) for x in sys.path if x)
assert importlib.metadata.version('eija-studio') == sys.argv[2] == eija_studio.__version__
print(json.dumps({'python':sys.version,'prefix':sys.prefix,'package':str(p.parent),'system_site_packages':False}))
"""
    output = run_checked([str(python), "-I", "-c", probe, str(source), version], scratch, artifacts, "identity")
    return json.loads(output)


def exercise(python: Path, scratch: Path, artifacts: Path, args: argparse.Namespace, wheel: dict) -> dict:
    identity = runtime_identity(python, scratch, artifacts, args.source.resolve(), wheel["version"])
    fixture = ROOT / "tests/installation" / (args.mode + "_wheel_probe.py")
    payload = fixture.read_bytes()
    (artifacts / "probe.py").write_bytes(payload)
    if args.mode == "release":
        provision_samples(args.source.resolve(), scratch, artifacts)
    asset = wheel["resources"]["eija_studio/resources/web/agent-edit.js"]
    output = run_checked([str(python), "-I", "-c", payload.decode("utf-8"), str(Path(identity["package"]).parent),
                          str(scratch), asset], scratch, artifacts, "application-probe")
    return {**json.loads(output), "runtime": identity, "probe_sha256": digest(payload)}


def provision_samples(source: Path, scratch: Path, artifacts: Path) -> None:
    inputs = json.loads((ROOT / "tests/installation/release_wheel_inputs.json").read_text(encoding="utf-8"))
    manifest = []
    for name, path in inputs.items():
        sample, destination = (source / path).resolve(), (scratch / name).resolve()
        assert sample.is_relative_to(source) and destination.is_relative_to(scratch), "Fixture paths must remain bounded"
        content = sample.read_bytes()
        destination.write_bytes(content)
        manifest.append({"source": path, "destination": name, "sha256": digest(content),
                         "provision": "explicit copied fixture; not wheel content"})
    (artifacts / "sample-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")


def arguments(mode: str, argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wheel', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True, help='Source snapshot used for byte comparisons only')
    parser.add_argument('--out', type=Path, required=True, help='New report path outside source; failures are retained')
    parser.add_argument('--scratch-root', type=Path, required=True, help='Existing disposable parent outside source')
    parser.add_argument('--wheelhouse', type=Path, required=True, help='Local runtime dependency wheels; no network fallback')
    parser.add_argument('--python', '--pip-python', default=sys.executable, help='Base Python used only to create a new venv')
    args = parser.parse_args(argv)
    args.mode = mode
    return args


def output_paths(args: argparse.Namespace) -> tuple[Path, Path]:
    source, scratch = args.source.resolve(), args.scratch_root.resolve()
    report = args.out.resolve()
    assert scratch.is_dir() and not scratch.is_relative_to(source), 'Scratch parent must exist outside source'
    assert not report.is_relative_to(source), 'Write reports outside frozen source'
    artifacts = report.parent / (report.stem + '-artifacts')
    assert not report.exists() and not artifacts.exists(), 'Use new report paths to retain previous runs'
    artifacts.mkdir(parents=True)
    return scratch, artifacts


def main(mode: str = 'candidate', argv: list[str] | None = None) -> int:
    args = arguments(mode, argv)
    scratch_root, artifacts = output_paths(args)
    report = {'status': 'FAIL', 'mode': mode + ' wheel; fresh isolated venv; offline dependency installation',
              'clean_room_dependency_install': 'NOT_RUN', 'live_provider_calls': 0, 'browser': 'NOT_RUN',
              'artifacts': str(artifacts), 'platform': platform.platform(), 'source': str(args.source.resolve()),
              'wheelhouse': str(args.wheelhouse.resolve()), 'runner_sha256': digest(Path(__file__).read_bytes()),
              'pack_provision': 'wheel bundle; source parity required', 'wheel_content_check': 'NOT_RUN'}
    try:
        assert args.wheelhouse.is_dir(), 'A local dependency wheelhouse is required'
        check_offline_inputs(args.wheel.resolve(), args.wheelhouse.resolve())
        report['wheel_sha256'] = digest(args.wheel.read_bytes())
        wheel = inspect_wheel(args.wheel, args.source.resolve())
        report['wheel_content_check'] = 'PASS'
        (artifacts / 'wheel-manifest.json').write_text(json.dumps(wheel, indent=2) + '\n', encoding='utf-8', newline='\n')
        with tempfile.TemporaryDirectory(prefix='eija installed proof ', dir=scratch_root) as temporary:
            scratch = Path(temporary)
            report['clean_room_dependency_install'] = 'FAIL'
            python = install_venv(args, scratch, artifacts)
            report['clean_room_dependency_install'] = 'PASS'
            report.update(exercise(python, scratch, artifacts, args, wheel), status='PASS')
    except (AssertionError, KeyError, OSError, RuntimeError, subprocess.SubprocessError, ValueError, zipfile.BadZipFile) as error:
        report['failure'] = f'{type(error).__name__}: {error}'
    args.out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
