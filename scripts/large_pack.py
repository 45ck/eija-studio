"""Write a large, valid PlayIDE pack for measuring how the page copes with a big model (ADR-0190).

The pack is the library-loan pack grown by a generated case-handling workflow: extra states reached from Requested, each left by two or three generated actions (forward, a skip ahead and sometimes a step back), held by the
three library roles in turn, plus `--entities` extra classes in the data model and one screen per generated action.
The library-loan laws still hold over the generated part, so the kernel, the laws and the build all run on it.

    python scripts/large_pack.py --out .tmp/large-pack

By default it fills the model to the kernel's contract limits (32 states, 64 transitions, 40 classes, 80 screens), so
it is the largest model PlayIDE can be asked to open. It is a fixture for performance checks, not a domain model: names are numbered, not meaningful.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "packs" / "library-loan"
GUARDS = ["actor_active", "role_current", "state_equals", "expected_version", "operation_binding"]
ROLES = ["Librarian", "Clerk", "Member"]
# The kernel's contract limits (domain/models.py, data.py, screens.py): a pack at these sizes is the largest PlayIDE opens.
MAX_STATES, MAX_TRANSITIONS, MAX_ENTITIES, MAX_ATTRIBUTES, MAX_SCREENS = 32, 64, 40, 40, 80


def _transitions(states: int, room: int) -> list[dict]:
    """The chain forward first (so every state is reachable), then skips ahead, then steps back, up to `room` edges."""
    names = [f"Stage{i:03d}" for i in range(1, states + 1)]
    edges = [("Requested", names[0]), *zip(names, names[1:]), (names[-1], "Requested")]
    edges += [(a, b) for a, b in zip(names, names[2:])]
    edges += [(names[i], names[i - 2]) for i in range(2, len(names), 3)]
    edges = edges[:room]
    return [{"id": f"TR-GEN{n:04d}", "action": f"Gen{n:04d}", "from_state": a, "to_state": b, "role": ROLES[n % len(ROLES)],
             "guards": list(GUARDS), "required_effects": [f"Audit:Gen{n:04d}"], "forbidden_effects": ["FineWaivedSilently", "MemberDataShared"]}
            for n, (a, b) in enumerate(edges, start=1)]


def large_pack(states: int = MAX_STATES, entities: int = MAX_ENTITIES) -> tuple[dict, dict, dict]:
    """The pack, its data model and its screens, as JSON-ready dicts. Asking for more than the kernel takes is clamped."""
    pack = json.loads((BASE / "pack.json").read_text(encoding="utf-8"))
    data = json.loads((BASE / "data.json").read_text(encoding="utf-8"))
    screens = json.loads((BASE / "screens.json").read_text(encoding="utf-8"))
    states = max(2, min(states, MAX_STATES - len(pack["model"]["states"])))
    entities = max(0, min(entities, MAX_ENTITIES - len(data["entities"])))
    room = min(MAX_TRANSITIONS - len(pack["model"]["transitions"]), MAX_SCREENS - len(screens["screens"]))
    generated = _transitions(states, room)
    pack["pack"].update(id="large-generated", name=f"Large generated ({len(pack['model']['states']) + states} states)",
                        description="A generated fixture for performance checks: library loan grown by a numbered case workflow.")
    pack["model"]["id"] = "large-generated"
    pack["model"]["states"] += [f"Stage{i:03d}" for i in range(1, states + 1)]
    pack["model"]["transitions"] += generated
    pack["actions"] += [{"id": t["action"], "guards": list(GUARDS), "required_effects": list(t["required_effects"])} for t in generated]
    pack["effects"]["catalog"] += [{"id": t["required_effects"][0], "kind": "audit"} for t in generated]
    data["id"] = "large-generated"
    for i in range(1, entities + 1):
        data["entities"].append({"name": f"Thing{i:03d}", "attributes": [
            {"name": f"{kind}{n:02d}", "type": kind, **({"choices": ["A", "B", "C"]} if kind == "choice" else {})}
            for n, kind in enumerate(("text", "number", "date", "boolean", "choice") * 4, start=1)]})
        target = "Loan" if i == 1 else f"Thing{i - 1:03d}"
        data["associations"].append({"source": f"Thing{i:03d}", "target": target, "role": "of",
                                     "source_multiplicity": "0..*", "target_multiplicity": "1"})
    screens["id"] = "large-generated"
    screens["screens"] += [{"use_case": t["action"], "title": t["action"], "fields": [{"attribute": "itemTitle", "label": "Title"}],
                            "button": t["action"]} for t in generated]
    return pack, data, screens


def write_large_pack(out: Path, states: int = MAX_STATES, entities: int = MAX_ENTITIES) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    for name, value in zip(("pack.json", "data.json", "screens.json"), large_pack(states, entities), strict=True):
        (out / name).write_text(json.dumps(copy.deepcopy(value), indent=1) + "\n", encoding="utf-8", newline="\n")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--states", type=int, default=MAX_STATES, help="extra states (clamped to the kernel limit)")
    parser.add_argument("--entities", type=int, default=MAX_ENTITIES, help="extra classes (clamped to the kernel limit)")
    args = parser.parse_args()
    print(write_large_pack(args.out, args.states, args.entities))


if __name__ == "__main__":
    main()
