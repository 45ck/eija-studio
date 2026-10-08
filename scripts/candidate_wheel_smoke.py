#!/usr/bin/env python3
"""Inspect/install an explicit candidate wheel offline; never stamp or relax release checks.

Uses current interpreter dependencies, not a clean-room dependency installation. Run only
in the serial validation slot, with temporary storage outside the source checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

PROBE = (Path(__file__).resolve().parents[1] / "tests/installation/candidate_wheel_probe.py").read_text(encoding="utf-8")


def inspect_wheel(wheel: Path, source: Path) -> str:
    expected = {
        'eija_studio/adapters/edit_proposals.py': source / 'src/eija_studio/adapters/edit_proposals.py',
        'eija_studio/application/edit_proposal.py': source / 'src/eija_studio/application/edit_proposal.py',
        'eija_studio/resources/web/agent-edit.js': source / 'src/eija_studio/resources/web/agent-edit.js',
    }
    for path in sorted((source / 'packs').rglob('*.json')):
        expected['eija_studio/resources/packs/' + path.relative_to(source / 'packs').as_posix()] = path
    with zipfile.ZipFile(wheel) as archive:
        assert archive.testzip() is None, 'Wheel CRC failed'
        for name, path in expected.items():
            assert archive.read(name) == path.read_bytes(), f'Wheel content differs: {name}'
    return hashlib.sha256(expected['eija_studio/resources/web/agent-edit.js'].read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wheel', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True, help='Frozen source used only for byte comparisons')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--scratch-root', type=Path, required=True, help='Existing disposable scratch parent outside source')
    parser.add_argument('--pip-python', default=sys.executable, help='Isolated installer interpreter; runtime dependencies use this process interpreter')
    args = parser.parse_args()
    wheel, source, scratch_root = args.wheel.resolve(), args.source.resolve(), args.scratch_root.resolve()
    assert not scratch_root.is_relative_to(source), 'Installed smoke must be outside the checkout'
    assert not args.out.resolve().is_relative_to(source), 'Write reports outside frozen source'
    report = {'status': 'FAIL', 'mode': 'candidate wheel installed into isolated target; current dependencies reused',
              'wheel_sha256': hashlib.sha256(wheel.read_bytes()).hexdigest(),
              'clean_room_dependency_install': 'NOT_RUN', 'live_provider_calls': 0, 'browser': 'NOT_RUN'}
    try:
        asset_sha = inspect_wheel(wheel, source)
        with tempfile.TemporaryDirectory(prefix='eija-candidate-wheel-', dir=scratch_root) as temporary:
            scratch = Path(temporary)
            installed = scratch / 'installed'
            install = subprocess.run([args.pip_python, '-m', 'pip', 'install', '--no-index', '--no-deps', '--no-compile',
                                      '--target', str(installed), str(wheel)], cwd=scratch, capture_output=True, text=True, timeout=120)
            if install.returncode:
                raise RuntimeError(f'Isolated target install failed with exit {install.returncode}')
            env = os.environ.copy()
            env.update(PYTHONPATH=str(installed), PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1')
            env.pop('EIJA_PACK', None)
            result = subprocess.run([sys.executable, '-c', PROBE, str(installed), str(scratch), asset_sha],
                                    cwd=scratch, env=env, capture_output=True, text=True, timeout=60)
            if result.returncode:
                raise RuntimeError('Installed probe failed: ' + result.stderr[-3000:])
            report.update(json.loads(result.stdout), status='PASS')
    except (AssertionError, KeyError, OSError, RuntimeError, subprocess.SubprocessError, ValueError) as error:
        report['failure'] = f'{type(error).__name__}: {error}'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
