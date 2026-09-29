"""Stage-0 self-check of the weave's trusted kernel: runs the law suites on the reference implementations and on
deliberately wrong ones, without pytest, without eijagraph and without any sibling file.

    python graph/formal/selfcheck.py            # fast (seconds): exit 0 PASS, 1 FAIL, 2 NOT_RUN
    python graph/formal/selfcheck.py --alloy    # also the pinned Alloy certificate models (about 25 s; NOT_RUN when absent)

Why it exists (design document section 3.6): the weave verifies its own links, so its own checker must not be the
only thing that reports on its own health. This script imports only ``eijaref`` (stdlib) and reports through its own
channel: a failing suite cannot be masked by the machinery it is judging. A suite that PASSES a wrong implementation
is itself a FAIL (it cannot fail, so it proves nothing).

Output: canonical ASCII JSON, sorted keys, no timestamps.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from eijaref import canon, closure, order, status, suites  # noqa: E402


def _suite(name: str, good: list, controls: list) -> dict:
    """good: violations lists from implementations that must pass; controls: (label, violations) that must FAIL."""
    ok_good = all(v == [] for v in good)
    ok_controls = all(v != [] for _, v in controls)
    return {"name": name, "reference_passes": ok_good, "wrong_implementations_caught": ok_controls,
            "verdict": "PASS" if ok_good and ok_controls else "FAIL"}


def run(with_alloy: bool = False) -> dict:
    results = [
        _suite("closure (all 3-node graphs)", [suites.suite_closure(lambda g, r: closure.lfp_kleene(g, r)),
                                               suites.suite_closure(lambda g, r: closure.warshall_closure(g, r))],
               [("one-hop closure", suites.suite_closure(suites.wrong_closure_one_hop))]),
        _suite("scc labels and topological order (all 3-node graphs)",
               [suites.suite_order(order.scc_labels, order.lexicographic_topological_order)],
               [("insertion-order labels", suites.suite_order(suites.wrong_scc_nx_style, order.lexicographic_topological_order))]),
        _suite("canonical serialisation", [suites.suite_canon(canon.dumps)],
               [("python json.dumps", suites.suite_canon(suites.wrong_dumps_python_json))]),
        _suite("status algebra", [suites.suite_status(status.join, status.meet, status.claim_status)],
               [("vacuous empty gate", suites.suite_status(status.join, suites.wrong_status_vacuous, status.claim_status)),
                ("NOT_RUN skipped", suites.suite_status(status.join, status.leaky_meet, status.claim_status))]),
        _suite("link status laws", [suites.suite_link_status(suites.link_status_ref)],
               [("any-ack clears", suites.suite_link_status(suites.wrong_link_status_any_ack)),
                ("unresolved is covered", suites.suite_link_status(suites.wrong_link_status_unresolved_covered))]),
    ]
    laws = status.check_laws()
    results.append({"name": "join laws (6 values, 216 triples)", "verdict": "PASS" if all(laws.values()) else "FAIL"})
    tools = {"alloy": {"verdict": "NOT_RUN", "reason": "not requested (--alloy)"}}
    if with_alloy:
        import run_alloy
        tools["alloy"] = run_alloy.run(Path(__file__).resolve().parent / "alloy" / "certificates.als")
        tools["alloy"] = {k: tools["alloy"][k] for k in ("verdict", "sentinel", "reason") if k in tools["alloy"]}
    verdicts = [r["verdict"] for r in results] + ([tools["alloy"]["verdict"]] if with_alloy else [])
    overall = "FAIL" if "FAIL" in verdicts else "NOT_RUN" if "NOT_RUN" in verdicts else "PASS"
    scope = "fast tier and Alloy certificate models" if with_alloy else "fast tier only: the Alloy models were not requested and are not covered by this verdict"
    return {"schema": "eija.weave.formal-selfcheck.v1", "verdict": overall, "scope": scope, "suites": results, "tools": tools}


def main(argv: list[str]) -> int:
    report = run("--alloy" in argv)
    sys.stdout.buffer.write((json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii"))
    return {"PASS": 0, "FAIL": 1, "NOT_RUN": 2}[report["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
