"""Weave lane gates (ADR-0089 to 0112). One module per lane: each weave aspect adds its sessions below.

Sessions use python=False and sys.executable like the other lanes, keep temp data inside the checkout, and report a
missing optional prerequisite as a skip that the test output names NOT_RUN, never as a pass.
"""
import sys
from pathlib import Path

import nox

PYTHON = sys.executable  # the project environment nox runs in; sessions use python=False
ROOT = Path(__file__).resolve().parents[2]


def _env() -> dict[str, str]:
    """Keep every tool's scratch space inside the checkout: the system TEMP may be a slow HDD."""
    scratch = ROOT / ".tmp"
    scratch.mkdir(exist_ok=True)
    return {"TMP": str(scratch), "TEMP": str(scratch)}


@nox.session(python=False, tags=["fast", "full"])
def graph_rules(session: nox.Session) -> None:
    """ADR-0095: validate graph/rules/catalogue.json (strata, relations, messages, metamodel agreement) and run its oracles.

    The SARIF schema check and the pySHACL cross-check skip (NOT_RUN) when the OASIS schema or pyshacl is absent.
    """
    session.run(PYTHON, "graph/rules/check_catalogue.py", env=_env())
    session.run(
        PYTHON, "-m", "pytest", "-q", "-p", "no:cacheprovider",
        "tests/graph/test_rules_catalogue.py", "tests/graph/test_rules_reference.py", "tests/graph/test_rule_language_bench.py",
        *session.posargs, env=_env(),
    )


@nox.session(python=False, tags=["release"])
def graph_rules_bench(session: nox.Session) -> None:
    """ADR-0095 rule-language benchmark: four engines, four rules, agreement and timings (MEASUREMENT, one machine).

    pySHACL is optional and reported NOT_RUN when missing. Runs serially; the toy Datalog evaluator and pySHACL are slow.
    """
    out = ROOT / "reports" / "graph" / "rule-language.json"
    session.run(PYTHON, "graph/bench/rule_language_bench.py", "--out", str(out), *session.posargs, env=_env())


@nox.session(python=False, tags=["fast"])
def graph_metamodel(session: nox.Session) -> None:
    """ADR-0089: the generated schemas match metamodel.json, the metamodel tables are coherent, and the fast identity checks hold.

    Skips the hash-seed subprocess test (about 30 s); `graph_metamodel_full` runs it. Without jsonschema or rfc8785 the affected
    tests skip and the output names NOT_RUN.
    """
    session.run(PYTHON, "graph/schema/build_schemas.py", "--check", env=_env())
    session.run(
        PYTHON, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/graph/test_metamodel_identity.py",
        "-k", "not hash_seeds", *session.posargs, env=_env(),
    )


@nox.session(python=False, tags=["full"])
def graph_metamodel_full(session: nox.Session) -> None:
    """ADR-0089: every metamodel and identity oracle, including byte identity of the bench report across PYTHONHASHSEED values."""
    session.run(PYTHON, "graph/schema/build_schemas.py", "--check", env=_env())
    session.run(
        PYTHON, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/graph/test_metamodel_identity.py", *session.posargs, env=_env(),
    )

@nox.session(python=False, tags=["fast", "full"])
def graph_impact_math(session: nox.Session) -> None:
    """ADR-0097: hand-verified oracles for impact, ranking, selection, status algebra and confidence statistics (about 10 s).

    Differential checks against graph/formal/eijaref, the kernel and networkx skip as NOT_RUN when that artefact is absent.
    """
    session.run(
        PYTHON, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/graph/test_impact_math_oracles.py", *session.posargs, env=_env(),
    )


@nox.session(python=False, tags=["release"])
def graph_impact_math_bench(session: nox.Session) -> None:
    """ADR-0097 MEASUREMENTS: cost of the reference implementations. The co-change ranking study needs external clones and is run
    by hand (docs/weave/design/impact-ranking-and-confidence.md section 16); it is NOT_RUN here, never a pass.
    """
    session.run(PYTHON, "graph/bench/impact_math_timing.py", *session.posargs, env=_env())



@nox.session(python=False, tags=["fast"])
def graph_formal(session: nox.Session) -> None:
    """ADR-00103: stage-0 self-check of the trusted kernel references, then the fast formal tests (about 15 s).

    Missing Hypothesis, clingo, rfc8785, Java or the pinned Alloy jar make the affected tests skip: the output names NOT_RUN, never a pass.
    """
    session.run(PYTHON, "graph/formal/selfcheck.py", env=_env())
    session.run(
        PYTHON, "-m", "pytest", "-q", "-p", "no:cacheprovider",
        "tests/graph/formal/test_formal_canon.py", "tests/graph/formal/test_formal_crosscheck.py",
        "tests/graph/formal/test_formal_rules_lens_metamodel.py", "tests/graph/formal/test_formal_hash_methods.py",
        "-k", "not alloy", *session.posargs, env=_env(),
    )


@nox.session(python=False, tags=["full"])
def graph_formal_full(session: nox.Session) -> None:
    """ADR-00103: every formal test, the exhaustive enumerations (about 1 minute) and the Alloy certificate models (Glucose, about 25 s).

    Java 17 and the jar pinned in graph/formal/TOOLS.lock are needed for the Alloy commands; without them they are NOT_RUN.
    """
    session.run(PYTHON, "graph/formal/selfcheck.py", "--alloy", env=_env())
    session.run(PYTHON, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/graph/formal", *session.posargs, env=_env())


@nox.session(python=False, tags=["release"])
def graph_formal_release(session: nox.Session) -> None:
    """ADR-00103 MEASUREMENTS and solver diversity: all formal benchmarks, then the Alloy certificate models on a second SAT backend (SAT4J, about 4 minutes).

    A disagreement between the two backends is a FAIL. POSIX byte identity of the report is NOT_RUN until run on Linux or WSL.
    Run serially: one JVM at a time on the shared PC.
    """
    session.run(PYTHON, "graph/bench/formal_checks.py", "--timing", env=_env())
    session.run(PYTHON, "graph/formal/run_alloy.py", "graph/formal/alloy/certificates.als", "--solver", "sat4j", env=_env())
