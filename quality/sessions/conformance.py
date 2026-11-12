"""Conformance-divergence gate (ADR-0241): a generated app that stops matching its model fails its own tests.

`conformance_divergence` builds apps that are wrong in one model element or one seeded code fault, reseals their build
identity so only behaviour can catch them, and runs each app's generated suite. Any divergence the suite misses, other
than a listed equivalence, fails the session. The full tier checks one shipped pack and the two feature variants
(`--core`); the release tier checks every pack. Report: reports/conformance/divergence.json.
"""
import sys

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False


@nox.session(python=False, tags=["full"])
def conformance_divergence(session: nox.Session) -> None:
    """Seeded divergence on one pack and the feature variants: every one caught by behaviour, or refused."""
    session.run(PYTHON, "-m", "verification.conformance.divergence", "--core", *session.posargs)


@nox.session(python=False, tags=["release"])
def conformance_divergence_all(session: nox.Session) -> None:
    """Seeded divergence on every shipped pack and feature variant."""
    session.run(PYTHON, "-m", "verification.conformance.divergence", *session.posargs)
