"""Differential check: the exported SCXML chart, run by an independent SCXML engine, agrees with the kernel (ADR-0160).

For every case of the app oracle (`appgen.oracle_cases`: every state x action x fixture actor x expected version, plus
an undeclared action and an unknown actor), the kernel's answer is compared with what python-statemachine (MIT) does
when it runs the exported chart from that state and is sent that action's event:

* COMMITTED: the chart takes the transition to the same state, `version` becomes 1, and `effects` lists the kernel's
  effects in the same order.
* REFUSED: the chart stays in the same state with `version` 0 and no effects. (The engine has no refusal codes; the
  kernel's code is reported beside any disagreement.)

The engine starts a machine in a given state the way a stored record is restored (its state through `start_value`,
its datamodel through `model`). A separate check requires a fresh machine to start in the model's initial state. Replays (`operation_binding`) are not projected.

    python -m verification.scxml.differential [--pack DIR ...] [--out reports/scxml/differential.json]

Exit codes: 0 PASS, 1 FAIL, 3 NOT_RUN (python-statemachine is not installed). NOT_RUN is never reported as PASS.
"""
from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from importlib import metadata
from pathlib import Path
from typing import Any

from eija_studio.application.appgen import oracle_cases
from eija_studio.application.scxml import event_data, scxml_id, to_scxml
from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import Pack, load_pack

try:  # optional (the `xuml` extra): run() reports NOT_RUN when it is missing
    from statemachine.io import load
except ImportError:  # pragma: no cover - exercised only without the extra
    load = None

FORMAT = "eija.scxml-differential.v1"
ROOT = Path(__file__).resolve().parents[2]
ENGINE = "python-statemachine"


def engine_version() -> str | None:
    try:
        return metadata.version(ENGINE)
    except metadata.PackageNotFoundError:
        return None


def say(message: str) -> None:
    sys.stdout.write(message + "\n")
    sys.stdout.flush()


def packs() -> list[Path]:
    return sorted(p for p in (ROOT / "packs").iterdir() if (p / "pack.json").is_file())


def _expected(case: dict[str, Any], model: Workflow) -> dict[str, Any]:
    answer = case["expect"]
    if answer["outcome"] == "COMMITTED":
        return {"state": answer["state"], "version": 1, "effects": list(answer["effects"])}
    return {"state": case["state"], "version": 0, "effects": []}


class Record:
    """A stored record as the engine restores it: its state and its datamodel (`version` 0, no effects yet)."""

    def __init__(self) -> None:
        self.version, self.effects = 0, []


def _observed(chart: Any, case: dict[str, Any], actors: dict[str, dict[str, Any]], names: dict[str, str]) -> dict[str, Any]:
    machine = chart(model=Record(), start_value=scxml_id(case["state"]))
    machine.send(scxml_id(case["action"]), **event_data(actors.get(case["actor"]), case["expected_version"]))
    current = sorted(names.get(s.id, s.id) for s in machine.configuration)
    return {"state": current[0] if len(current) == 1 else current, "version": machine.model.version,
            "effects": list(machine.model.effects)}


def compare(pack: Pack, model: Workflow | None = None, document: str | None = None) -> dict[str, Any]:
    """Run every oracle case on the chart (`document`, by default the export of `model`) and on the kernel."""
    if load is None:
        raise RuntimeError(f"{ENGINE} is not installed")
    model = model if model is not None else pack.model
    document = document if document is not None else to_scxml(pack, model)
    chart = load(document, format="scxml", trusted=False, name="Chart")
    names = {scxml_id(s): s for s in model.states}
    actors = {a.id: a.model_dump() for a in pack.fixtures.actors}
    fresh = chart()
    initial = sorted(names.get(s.id, s.id) for s in fresh.configuration)
    disagreements = []
    if initial != [model.initial_state]:
        disagreements.append({"check": "initial", "expected": model.initial_state, "observed": initial})
    cases = oracle_cases(pack, model)
    for case in cases:
        expected, observed = _expected(case, model), _observed(chart, case, actors, names)
        if expected != observed:
            disagreements.append({"case": {k: case[k] for k in ("state", "action", "actor", "expected_version")},
                                  "kernel": case["expect"], "expected": expected, "observed": observed})
    return {"pack": pack.id, "model_hash": model.semantic_hash,
            "scxml_sha256": sha256(document.encode("utf-8")).hexdigest(), "cases": len(cases),
            "committed": sum(c["expect"]["outcome"] == "COMMITTED" for c in cases),
            "disagreements": disagreements, "status": "FAIL" if disagreements else "PASS"}


def run(locations: list[Path]) -> dict[str, Any]:
    version = engine_version()
    report: dict[str, Any] = {"format": FORMAT, "engine": {"name": ENGINE, "version": version},
                              "oracle": "eija_studio runtime.execute via appgen.oracle_cases", "platform": sys.platform}
    if version is None:
        return report | {"status": "NOT_RUN", "reason": f"{ENGINE} is not installed (pip install -e '.[xuml]')",
                         "packs": []}
    results = [compare(load_pack(location)) for location in locations]
    return report | {"status": "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL", "packs": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m verification.scxml.differential", description=__doc__.split("\n")[0])
    parser.add_argument("--pack", type=Path, action="append", help="Pack directory (default: every pack in packs/)")
    parser.add_argument("--out", type=Path, help="Write the JSON report here")
    args = parser.parse_args(argv)
    report = run(args.pack or packs())
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8", newline="\n")
    for result in report["packs"]:
        say(f"{result['pack']:<20} {result['status']:<5} {result['cases']} cases, "
            f"{result['committed']} commits, {len(result['disagreements'])} disagreements")
    say(f"scxml differential: {report['status']}" + (f" ({report['reason']})" if "reason" in report else ""))
    return {"PASS": 0, "FAIL": 1}.get(report["status"], 3)


if __name__ == "__main__":
    raise SystemExit(main())
