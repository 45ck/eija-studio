#!/usr/bin/env python
"""ONE live, synthetic proposal call per provider, recorded as evidence. Never runs automatically.

    python scripts/live_provider_smoke.py --provider claude --consent

Sends only the fixed synthetic request "Let teachers sign off excursions." plus the synthetic baseline
workflow. Needs explicit ``--consent`` (egress and possible subscription usage). Status meanings:

    PASS     a live call returned a schema-valid Proposal. Says nothing about interpretation quality.
    FAIL     a call was made and failed (error class recorded; no raw CLI output is kept).
    NOT_RUN  a prerequisite is missing (CLI absent, not signed in, key absent). No claim is made.

Results merge into evidence/live-providers/<date>-<platform>.json keyed by provider, so runs can be done
one at a time. Tokens are never read or printed: sign-in is delegated to each vendor CLI.
"""
from __future__ import annotations
import argparse
import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eija_studio.adapters.providers import PROVIDER_NAMES, create_provider  # noqa: E402
from eija_studio.domain.models import DomainError  # noqa: E402
from eija_studio.domain.policy import baseline  # noqa: E402

REQUEST = "Let teachers sign off excursions."
LIVE_NAMES = tuple(n for n in PROVIDER_NAMES if n != "offline")


def run_smoke(name: str, model: str, timeout: float) -> dict:
    """Return the evidence record for one provider. Makes at most one billable call."""
    provider = create_provider(name, model)
    if hasattr(provider, "timeout"):
        provider.timeout = timeout
    record: dict = {"provider": name, "status": "NOT_RUN", "model_requested": model or "(cli default)"}
    report = provider.doctor()
    record["doctor"] = {k: report[k] for k in ("ready", "cli_version", "login", "login_detail", "required_flags_present", "missing_flags", "reason", "key_present")
                        if k in report}
    if not report.get("ready"):
        record["reason"] = report.get("reason") or report.get("login_detail") or "provider reported not ready"
        return record
    started = time.monotonic()
    try:
        result = provider.propose(REQUEST, baseline())
    except DomainError as error:
        record["latency_s"] = round(time.monotonic() - started, 1)
        record["error_class"] = error.code
        if error.code in ("PROVIDER_AUTH", "PROVIDER_NOT_READY", "PROVIDER_NOT_CONFIGURED"):
            record["reason"] = "Not signed in or no credentials (the CLI/API reported an authentication problem); no claim about the provider"
            return record
        record.update(status="FAIL", schema_valid=False if error.code == "PROVIDER_OUTPUT_INVALID" else None, reason=str(error))
        return record
    record.update(status="PASS", latency_s=round(time.monotonic() - started, 1), schema_valid=True, model=result.model,
                  interpretations=sorted(a.interpretation for a in result.proposal.alternatives), usage=result.usage,
                  note="Schema-valid proposal only; interpretation quality and human comprehension are not measured")
    return record


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--provider", required=True, choices=LIVE_NAMES)
    parser.add_argument("--consent", action="store_true", help="required: acknowledges egress and possible account usage")
    parser.add_argument("--model", default="")
    parser.add_argument("--timeout", type=float, default=150, help="seconds; the owner-authorised ceiling is 180")
    parser.add_argument("--date", default="2026-09-28", help="recorded date, passed in for deterministic files")
    parser.add_argument("--out", type=Path, default=None, help="evidence file (default evidence/live-providers/<date>-<platform>.json)")
    args = parser.parse_args(argv)
    if not args.consent:
        print("Refusing to make a live call without --consent (egress and possible subscription usage).", file=sys.stderr)
        return 2
    if not 1 <= args.timeout <= 180:
        print("--timeout must be between 1 and 180 seconds.", file=sys.stderr)
        return 2
    system = platform.system().lower() or "unknown"
    out = args.out or ROOT / "evidence" / "live-providers" / f"{args.date}-{system}.json"
    document = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    document.update({"recorded_on": args.date, "platform": {"system": platform.system(), "release": platform.release(), "python": platform.python_version()},
                     "latency_note": "latency_s is propose() end to end, including three diagnostic probes (version, help, login status)", "request": REQUEST, "baseline": "synthetic excursion workflow (eija_studio.domain.policy.baseline)"})
    record = run_smoke(args.provider, args.model, args.timeout)
    document.setdefault("results", {})[args.provider] = record
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"provider": args.provider, "status": record["status"], "error_class": record.get("error_class"), "evidence": str(out)}))
    return 0 if record["status"] in ("PASS", "NOT_RUN") else 1


if __name__ == "__main__":
    raise SystemExit(main())
