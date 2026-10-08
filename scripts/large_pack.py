"""Write a large, valid PlayIDE pack for measuring how the page copes with a big model (ADR-0199).

The pack is a given pack grown by a generated, numbered workflow: extra states reached from its initial state, each left
by a forward action, a skip ahead and sometimes a step back, held by the pack's roles in turn, plus extra classes in
the data model and one screen per generated action. Grown from a pack whose laws only constrain its own states and
actions, the laws still hold, so the kernel, the laws and the build all run on it.

    python scripts/large_pack.py --base packs/<pack> --out .tmp/large-pack

By default it fills the model to the kernel's contract limits (32 states, 64 transitions, 40 classes, 80 screens), so
it is the largest model PlayIDE can be asked to open. It is a fixture for performance checks, not a domain model:
names are numbered, not meaningful.
"""
from __future__ import annotations

import argparse
import json
from itertools import pairwise
from pathlib import Path

GUARDS = ["actor_active", "role_current", "state_equals", "expected_version", "operation_binding"]
# The kernel's contract limits (domain/models.py, data.py, screens.py): a pack at these sizes is the largest PlayIDE opens.
MAX_STATES, MAX_TRANSITIONS, MAX_ENTITIES, MAX_SCREENS = 32, 64, 40, 80


def _edges(start: str, states: int, room: int) -> list[tuple[str, str]]:
    """The chain forward first (so every state is reachable), then skips ahead, then steps back, up to `room` edges."""
    names = [f"Stage{i:03d}" for i in range(1, states + 1)]
    edges = [(start, names[0]), *pairwise(names), (names[-1], start)]
    edges += list(zip(names, names[2:], strict=False))
    edges += [(names[i], names[i - 2]) for i in range(2, len(names), 3)]
    return edges[:room]


def large_pack(base: Path, states: int = MAX_STATES, entities: int = MAX_ENTITIES) -> tuple[dict, dict, dict]:
    """The pack, its data model and its screens, as JSON-ready dicts. Asking for more than the kernel takes is clamped."""
    pack = json.loads((base / "pack.json").read_text(encoding="utf-8"))
    data = json.loads((base / "data.json").read_text(encoding="utf-8"))
    screens = json.loads((base / "screens.json").read_text(encoding="utf-8"))
    model, roles, forbidden = pack["model"], [r["id"] for r in pack["roles"]], list(pack["effects"]["forbidden"])
    if len(model["states"]) >= MAX_STATES:
        raise ValueError(f"{base} already has {len(model['states'])} states, the kernel's limit; there is no room to grow it")
    states = max(1, min(states, MAX_STATES - len(model["states"])))
    entities = max(0, min(entities, MAX_ENTITIES - len(data["entities"])))
    room = min(MAX_TRANSITIONS - len(model["transitions"]), MAX_SCREENS - len(screens["screens"]))
    generated = [{"id": f"TR-GEN{n:04d}", "action": f"Gen{n:04d}", "from_state": a, "to_state": b, "role": roles[n % len(roles)],
                  "guards": list(GUARDS), "required_effects": [f"Audit:Gen{n:04d}"], "forbidden_effects": forbidden}
                 for n, (a, b) in enumerate(_edges(model["initial_state"], states, room), start=1)]
    pack["pack"].update(id="large-generated", name=f"Large generated ({len(model['states']) + states} states)",
                        description=f"A generated fixture for performance checks: {pack['pack']['name']} grown by a numbered workflow.")
    model["id"] = data["id"] = screens["id"] = "large-generated"
    model["states"] += [f"Stage{i:03d}" for i in range(1, states + 1)]
    model["transitions"] += generated
    pack["actions"] += [{"id": t["action"], "guards": list(GUARDS), "required_effects": list(t["required_effects"])} for t in generated]
    pack["effects"]["catalog"] += [{"id": t["required_effects"][0], "kind": "audit"} for t in generated]
    for i in range(1, entities + 1):
        data["entities"].append({"name": f"Thing{i:03d}", "attributes": [
            {"name": f"{kind}{n:02d}", "type": kind, **({"choices": ["A", "B", "C"]} if kind == "choice" else {})}
            for n, kind in enumerate(("text", "number", "date", "boolean", "choice") * 4, start=1)]})
        data["associations"].append({"source": f"Thing{i:03d}", "target": data["record"] if i == 1 else f"Thing{i - 1:03d}",
                                     "role": "of", "source_multiplicity": "0..*", "target_multiplicity": "1"})
    record = next(e for e in data["entities"] if e["name"] == data["record"])
    field = next(a["name"] for a in record["attributes"] if a.get("required"))
    screens["screens"] += [{"use_case": t["action"], "title": t["action"], "fields": [{"attribute": field, "label": field}],
                            "button": t["action"]} for t in generated]
    return pack, data, screens


def write_large_pack(base: Path, out: Path, states: int = MAX_STATES, entities: int = MAX_ENTITIES) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    for name, value in zip(("pack.json", "data.json", "screens.json"), large_pack(base, states, entities), strict=True):
        (out / name).write_text(json.dumps(value, indent=1) + "\n", encoding="utf-8", newline="\n")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--base", type=Path, required=True, help="pack directory to grow (pack.json, data.json, screens.json)")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--states", type=int, default=MAX_STATES, help="extra states (clamped to the kernel limit)")
    parser.add_argument("--entities", type=int, default=MAX_ENTITIES, help="extra classes (clamped to the kernel limit)")
    args = parser.parse_args()
    print(write_large_pack(args.base, args.out, args.states, args.entities))


if __name__ == "__main__":
    main()
