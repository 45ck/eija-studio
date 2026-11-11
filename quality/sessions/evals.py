"""Evals lane: the kernel-graded intent eval harness (ADR-0229), offline fixture only.

Live runs are never a session. Run them by hand with consent and a call cap:
    python -m quality.evals.intent --provider openai --model <id> --allow-network --consent --max-calls 40
"""
import nox

from quality.tools.suite import run_lane_tests

TESTS = ("tests/test_intent_eval.py",)


@nox.session(python=False, tags=["fast", "full"])
def intent_eval(session: nox.Session) -> None:
    """Grades the offline proposer on packs/intent-evals.json and checks the kernel agrees on every planned meaning."""
    run_lane_tests(session, *TESTS)
