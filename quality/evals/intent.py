"""Intent eval: does a proposal provider pick the meaning a request asked for? The kernel is the grader (ADR-0229).

Each case in ``packs/intent-evals.json`` is a plain request against one pack and the meaning it asked for. The provider
proposes alternatives; its first alternative is the meaning it would plan. Grading needs no model-as-judge:

* ``correct``     the first alternative is the expected meaning.
* ``substituted`` the request asked for an unsafe (unsupported) change and the provider answered with a supported
                  one instead. This is the #152 failure: a green "the policy allows it" for something nobody asked.
* ``wrong``       any other mismatch.
* ``invalid``     the provider failed or its reply failed validation (fails closed, never repaired).

The planned meaning is then run through the product path (``propose_plan``): the kernel must allow a supported
meaning and refuse an unsupported one. ``kernel_agrees`` records that; a disagreement is a pack or kernel defect,
not a provider score.

Networked providers need ``--allow-network`` and ``--consent`` (AGENTS.md), and ``--max-calls`` caps the number of
billable calls; the run stops when it is reached. Results are evidence for this provider, model and date only.

    python -m quality.evals.intent                                   # offline fixture, no network
    python -m quality.evals.intent --provider openai --model <id> --allow-network --consent --max-calls 40
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from eija_studio.adapters.providers import create_provider
from eija_studio.application.plan import propose_plan
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack, load_pack

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "packs" / "intent-evals.json"  # pack data: lives with the packs, outside the vocabulary gate
HARD_CALL_LIMIT = 200
OUTCOMES = ("correct", "substituted", "wrong", "invalid")


def load_cases(path: Path = CASES) -> list[dict[str, Any]]:
    return list(json.loads(path.read_text(encoding="utf-8"))["cases"])


class _MeaningPlan:
    """A plan proposer that plans exactly one of the pack's meanings, so the kernel judges that meaning as planned."""
    name, live = "intent-eval-meaning", False

    def __init__(self, meaning_id: str):
        self.meaning_id = meaning_id

    def propose(self, request: str, model: Workflow, pack: Pack, *, grows: bool = False) -> dict[str, Any]:
        meaning = pack.meaning(self.meaning_id)
        if meaning is None or not meaning.transactions:
            raise DomainError("PLAN_REQUEST_UNSUPPORTED", "Nothing to plan")
        return {"summary": meaning.label, "meaning": meaning.id,
                "steps": [{"transaction": t.model_dump(mode="json"), "why": "intent eval"} for t in meaning.transactions]}

    def follow_on(self, ripple: dict[str, Any], model: Workflow, pack: Pack) -> dict[str, Any]:
        return {"steps": []}


def kernel_allows(pack: Pack, meaning_id: str) -> bool:
    """True when the kernel accepts the meaning's plan on the pack's model; a meaning with nothing to plan is refused."""
    try:
        return bool(propose_plan(pack.meaning(meaning_id).label, pack.model, pack, _MeaningPlan(meaning_id))["preview"]["legal"])
    except DomainError:
        return False


def grade(pack: Pack, expect: str, picked: str | None) -> str:
    if picked is None:
        return "invalid"
    if picked == expect:
        return "correct"
    asked, answered = pack.meaning(expect), pack.meaning(picked)
    if asked is not None and not asked.supported and asked.id != "unsupported" and answered is not None and answered.supported:
        return "substituted"
    return "wrong"


def run_case(case: dict[str, Any], provider_name: str, model: str, packs: dict[str, Pack]) -> dict[str, Any]:
    pack = packs.setdefault(case["pack"], load_pack(ROOT / "packs" / case["pack"]))
    provider = create_provider(provider_name, model, None, pack)
    picked, error, usage, served = None, None, {}, ""
    try:
        result = provider.propose(case["request"], pack.model)
        picked, usage, served = result.proposal.alternatives[0].interpretation, dict(result.usage), result.model
    except DomainError as e:
        error = e.code
    outcome = grade(pack, case["expect"], picked)
    supported = picked is not None and pack.meaning(picked) is not None and pack.meaning(picked).supported
    row: dict[str, Any] = {"id": case["id"], "kind": case["kind"], "expect": case["expect"], "picked": picked, "outcome": outcome,
                           "error": error, "usage": usage, "served_model": served}
    if picked is not None:
        row["kernel_allows"] = kernel_allows(pack, picked)
        row["kernel_agrees"] = row["kernel_allows"] == supported
    return row


def _tally(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(r["outcome"] for r in rows)
    return {o: counts.get(o, 0) for o in OUTCOMES}


def summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    kinds = sorted({r["kind"] for r in rows})
    tokens: Counter[str] = Counter()
    for r in rows:
        tokens.update({k: v for k, v in r["usage"].items() if isinstance(v, int | float)})
    return {"cases": len(rows), **_tally(rows),
            "by_kind": {k: _tally([r for r in rows if r["kind"] == k]) for k in kinds},
            "kernel_disagreements": [r["id"] for r in rows if r.get("kernel_agrees") is False],
            "usage": dict(tokens)}


def evaluate(provider_name: str = "offline", model: str = "", *, max_calls: int | None = None,
             cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    chosen = cases if cases is not None else load_cases()
    limit = min(max_calls if max_calls is not None else len(chosen), HARD_CALL_LIMIT)
    packs: dict[str, Pack] = {}
    rows = [run_case(case, provider_name, model, packs) for case in chosen[:limit]]
    networked = create_provider(provider_name, model).networked
    return {"scope": "intent-eval", "evidence": "LIVE" if networked else "SYNTHETIC", "provider": provider_name,
            "model": model or None, "ran_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "platform": f"{platform.system()} {platform.machine()} Python {platform.python_version()}",
            "cases_available": len(chosen), "stopped_at_call_limit": limit < len(chosen),
            "summary": summarise(rows), "results": rows}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kernel-graded intent eval for proposal providers (ADR-0229).")
    parser.add_argument("--provider", default="offline")
    parser.add_argument("--model", default="")
    parser.add_argument("--allow-network", action="store_true", help="required for a networked provider")
    parser.add_argument("--consent", action="store_true", help="I accept that requests and the pack model are sent to the vendor and may be billed")
    parser.add_argument("--max-calls", type=int, default=None, help=f"stop after this many provider calls (hard limit {HARD_CALL_LIMIT})")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "evals" / "intent.json")
    args = parser.parse_args(argv)
    if create_provider(args.provider, args.model).networked and not (args.allow_network and args.consent):
        sys.stderr.write("NOT_RUN: a networked provider needs --allow-network and --consent; no call was made.\n")
        return 2
    report = evaluate(args.provider, args.model, max_calls=args.max_calls)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    s = report["summary"]
    sys.stdout.write(f"{report['evidence']} {args.provider} {args.model or ''}: {s['correct']}/{s['cases']} correct, "
                     f"{s['substituted']} substituted, {s['wrong']} wrong, {s['invalid']} invalid -> {args.out}\n")
    return 1 if s["kernel_disagreements"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
