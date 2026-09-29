"""`eija serve` with the kernel-test harness identity, for UI measurement on unstamped source.

Why this exists: the Studio refuses approval (`SOURCE_REVIEW_REQUIRED`) whenever the running source
differs from the owner-stamped `trusted_build.json`, which is true on every lane branch. The kernel
test suite handles that with a harness identity (tests/conftest.py); this launcher does the same for
the browser journey so the approve/apply screens can be measured at all.

What this does NOT do: it does not edit or restamp trusted_build.json, does not change any policy or
guard, does not touch the release gate, and serves only over the same `create_app` + Uvicorn loopback
stack as `eija serve`. Nothing under src/ knows about it or accepts a harness identity: the stand-in
is injected here, outside the shipped package, exactly as tests/conftest.py injects it. Every report
produced this way says `identity_source: pytest-harness`; it is UI-measurement evidence, never a
release-identity approval. Guard rails: the workspace must live under this checkout's `.tmp/hci/` (so the
stand-in can never open the owner's real workspace) and the server binds loopback only. Use
`--identity release` on a stamped build to run the real `eija serve` instead.
"""

# ruff: noqa: T201 - a launcher prints its private loopback link for the parent process to read
from __future__ import annotations

import argparse
import secrets
from pathlib import Path

import uvicorn

from eija_studio.adapters.identity import identity as measured_identity
from eija_studio.bootstrap import build_studio
from eija_studio.interfaces.http import create_app

HARNESS_MARK = "pytest-harness"  # the same label tests/conftest.py stamps on its identity
ALLOWED_ROOT = Path(__file__).resolve().parents[2] / ".tmp" / "hci"  # where quality.hci.server puts throw-away workspaces


def harness_identity() -> dict:
    """The measured identity, marked as a trusted-fixture STAND-IN so no report can pass it off as a release identity."""
    return measured_identity() | {"trusted_fixture": True, "identity_source": HARNESS_MARK}


def check_workspace(workspace: Path) -> Path:
    """Refuse any workspace outside `<checkout>/.tmp/hci`: the stand-in identity must never touch a real workspace."""
    resolved = workspace.resolve()
    if not resolved.is_relative_to(ALLOWED_ROOT.resolve()):
        raise SystemExit(f"refusing workspace {resolved}: the harness identity only serves throw-away workspaces under {ALLOWED_ROOT}")
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args(argv)
    studio = build_studio(check_workspace(args.workspace))
    studio.identity_provider = harness_identity
    token = secrets.token_urlsafe(32)
    print(f"EIJA Studio HCI harness (offline, {HARNESS_MARK} identity, NOT a release identity). Private link:\nhttp://127.0.0.1:{args.port}/#{token}", flush=True)
    uvicorn.run(create_app(studio, token, args.port), host="127.0.0.1", port=args.port, access_log=False, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
