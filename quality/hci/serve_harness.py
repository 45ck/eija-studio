"""`eija serve` with the kernel-test harness identity, for UI measurement on unstamped source.

Why this exists: the Studio refuses approval (`SOURCE_REVIEW_REQUIRED`) whenever the running source
differs from the owner-stamped `trusted_build.json`, which is true on every lane branch. The kernel
test suite handles that with a harness identity (tests/conftest.py); this launcher does the same for
the browser journey so the approve/apply screens can be measured at all.

What this does NOT do: it does not edit or restamp trusted_build.json, does not change any policy or
guard, does not touch the release gate, and serves only over the same `create_app` + Uvicorn loopback
stack as `eija serve`. Every report produced this way says `identity_source: pytest-harness`; it is
UI-measurement evidence, never a release-identity approval. Use `--identity release` on a stamped
build to run the real `eija serve` instead.
"""
from __future__ import annotations

import argparse
import secrets
from pathlib import Path

HARNESS_MARK = "pytest-harness"  # must equal tests/conftest.py HARNESS_MARK; tests/hci asserts it


def harness_identity() -> dict:
    """Same shape as tests/conftest.py `harness_identity`: the measured identity marked as a test fixture.

    Establishes only that the UI can be driven to approve/apply on unstamped source. It is NOT a release identity."""
    from eija_studio.adapters.identity import identity as measured_identity

    return measured_identity() | {"trusted_fixture": True, "identity_source": HARNESS_MARK}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args(argv)
    import uvicorn
    from eija_studio.bootstrap import build_studio
    from eija_studio.interfaces.http import create_app

    studio = build_studio(args.workspace)
    studio.identity_provider = harness_identity
    token = secrets.token_urlsafe(32)
    print("EIJA Studio HCI harness (offline, pytest-harness identity; approvals here are NOT release approvals). Private link:\n"
          f"http://127.0.0.1:{args.port}/#{token}", flush=True)
    uvicorn.run(create_app(studio, token, args.port), host="127.0.0.1", port=args.port, access_log=False, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
