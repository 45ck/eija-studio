"""Disposable, explicitly synthetic owner-flow server for browser tests and recordings.

It never stamps source or touches a real owner's workspace. The caller owns the temporary
directory and sends a fresh test capability on stdin; normal HTTP security remains enabled.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import uvicorn

from eija_studio.adapters.system_library import SystemLibrary
from eija_studio.bootstrap import OfflineSystemDescriber, build_studio
from eija_studio.interfaces.http import create_app
from eija_studio.interfaces.play_systems import StudioHandle, Systems
from kernel_support import harness_identity

FIXTURE_MARK = "synthetic-exact-app-browser-test"


def synthetic_studio(workspace: Path, *, synthetic: bool = True):
    """Open only a deliberately marked test workspace using the real services."""
    mark = workspace / "synthetic-fixture.json"
    if not mark.is_file() or json.loads(mark.read_text(encoding="utf-8")).get("identity_source") != FIXTURE_MARK:
        raise RuntimeError("The exact-app test server requires its isolated synthetic fixture marker")
    pack = Path(__file__).resolve().parents[1] / "packs/library-loan"
    studio = build_studio(workspace, pack=pack)
    if synthetic:
        studio.identity_provider = lambda: harness_identity(studio.pack) | {"identity_source": FIXTURE_MARK}
    return studio


def synthetic_app(workspace: Path, token: str, port: int, *, synthetic: bool = True):
    """Use the normal CLI's actual systems services, scoped to the marked scratch workspace."""
    studio = synthetic_studio(workspace, synthetic=synthetic)
    handle = StudioHandle(studio)
    pack = Path(__file__).resolve().parents[1] / "packs/library-loan"
    systems = Systems(handle, SystemLibrary(workspace / "systems"),
                      lambda selected_pack, selected_workspace: build_studio(selected_workspace, pack=selected_pack),
                      pack, workspace, describer=OfflineSystemDescriber())
    return create_app(handle, token, port=port, systems=systems)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--measured-source", action="store_true", help="Keep the normal source-review gate")
    args = parser.parse_args()
    token = sys.stdin.readline().strip()
    if len(token) != 32 or any(character not in "0123456789abcdef" for character in token):
        raise RuntimeError("A fresh synthetic test capability must be supplied on stdin")
    app = synthetic_app(args.workspace, token, args.port, synthetic=not args.measured_source)
    try:
        uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
    finally:
        app.state.play.stop()


if __name__ == "__main__":
    main()
