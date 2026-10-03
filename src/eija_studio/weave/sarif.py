# ADAPTED from graph/rules/reference.py (WBS 1.6). Verbatim: canonical_json, fingerprint_v1, rule_verdict, fold_verdicts, exit_code,
# dumps_sarif and the SARIF constants. Split into helpers to meet the complexity budget: _check_subset, build_sarif,
# sarif_profile_problems. tests/weave/test_weave_lift.py proves equal behaviour (same SARIF bytes, same profile problems).
"""Deterministic finding identity, verdict algebra and SARIF 2.1.0 profile (weave lift).

Only the fingerprint, verdict and SARIF part of graph/rules/reference.py is lifted; the read-effect analysis,
suppression expiry and SQL templates stay in the reference module until a rule needs them.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

FINGERPRINT_DOMAIN = "eija.finding.v1"
SAFE_INT = 2**53 - 1
SARIF_VERSION = "2.1.0"
SARIF_SCHEMA_URI = "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json"
PROFILE = "eija-sarif/v1"
EFFECTS = ("none", "monotone", "unsafe")

# ------------------------------------------------------------------------------------------------ canonical json
def _check_mapping(value: Mapping[str, Any], path: str) -> None:
    for key, item in value.items():
        if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ValueError(f"{path}: key {key!r} is not an ASCII identifier")
        _check_subset(item, f"{path}.{key}")


def _check_subset(value: Any, path: str = "$") -> None:
    """Strings, safe integers, booleans, null, lists and objects with ASCII identifier keys. No floats (D-02, D-10)."""
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        if abs(value) > SAFE_INT:
            raise ValueError(f"{path}: integer outside the safe range")
    elif isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            _check_subset(item, f"{path}[{i}]")
    elif isinstance(value, Mapping):
        _check_mapping(value, path)
    else:
        raise ValueError(f"{path}: {type(value).__name__} is not in the canonical subset")


def canonical_json(value: Any) -> str:
    """RFC 8785 subset writer. Equal to JCS for this subset because keys are ASCII, so UTF-16 and code point order agree."""
    _check_subset(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


# ------------------------------------------------------------------------------------------------- fingerprints
def _enc(text: str) -> bytes:
    raw = text.encode("utf-8")
    return len(raw).to_bytes(8, "big") + raw


def fingerprint_v1(rule_id: str, subjects: Sequence[str], identity: Mapping[str, Any] | None = None) -> str:
    """SHA-256 over domain-separated, length-prefixed fields; no line numbers, no message text, no witness, no time.

    subjects   ids of the nodes or links the finding is about; sorted and de-duplicated here
    identity   the rule's identity_args (strings, safe integers, booleans only)
    """
    body = (
        _enc(FINGERPRINT_DOMAIN)
        + _enc(rule_id)
        + _enc(canonical_json(sorted(set(subjects))))
        + _enc(canonical_json(dict(identity or {})))
    )
    return hashlib.sha256(body).hexdigest()


# --------------------------------------------------------------------------------------------------- verdicts
VERDICT_ORDER = {"FAIL": 0, "NOT_RUN": 1, "PASS": 2}


def rule_verdict(gating_findings: int, prerequisites_ok: bool, effect: str = "none") -> str:
    """Verdict of one rule (PASS, FAIL, NOT_RUN).

    prerequisites_ok  False when the rule could not be evaluated at all (tool, grammar or relation missing, rule crashed,
                      suppression expiry unevaluable): NOT_RUN, whatever findings a partial run produced
    effect            ``read_effect`` of the rule for this run

    Soundness. Let F(D) be the finding set of a rule over input D. If F is monotone in the incomplete relations (adding
    facts to them can only add findings; the ``monotone`` effect), then F(partial D) is a subset of F(complete D), so a
    seen finding is real (FAIL is sound) but an empty F(partial D) says nothing (NOT_RUN, never PASS). If F is
    anti-monotone in an incomplete relation (``unsafe``: negation, anti-join, ``count < min``), then F(partial D) can contain
    findings that disappear once the facts arrive, so a finding on partial input is not evidence: NOT_RUN. Whether the
    declared polarity is the real one is checked by tests over exhaustive small worlds, not proved."""
    if effect not in EFFECTS:
        raise ValueError(f"unknown effect {effect!r}")
    if not prerequisites_ok or effect == "unsafe":
        return "NOT_RUN"
    if gating_findings > 0:
        return "FAIL"
    return "PASS" if effect == "none" else "NOT_RUN"


def fold_verdicts(verdicts: Iterable[str]) -> str:
    """Chain minimum over FAIL < NOT_RUN < PASS. Empty input is NOT_RUN: nothing was checked, so nothing passed."""
    items = list(verdicts)
    if not items:
        return "NOT_RUN"
    for v in items:
        if v not in VERDICT_ORDER:
            raise ValueError(f"unknown verdict {v!r}")
    return min(items, key=VERDICT_ORDER.__getitem__)


def exit_code(verdict: str, not_run_accepted: bool = False) -> int:
    """0 PASS, 1 FAIL, 2 NOT_RUN unless explicitly accepted (mirrors the quality lane's audit session, which fails
    with a NOT_RUN message unless EIJA_ALLOW_NOT_RUN=1 records the gap as accepted)."""
    if verdict == "FAIL":
        return 1
    if verdict == "NOT_RUN":
        return 0 if not_run_accepted else 2
    return 0


# ---------------------------------------------------------------------------------------------------- SARIF
_POSITIONAL = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
FORBIDDEN_KEYS = {
    "guid", "correlationGuid", "baselineGuid", "startTimeUtc", "endTimeUtc", "timeUtc", "executionTimeUtc", "asOfTimeUtc",
    "machine", "account", "processId", "commandLine", "workingDirectory", "environmentVariables", "stdin",
    "stdout", "stderr", "stdoutStderr", "revisionId", "addresses", "address", "baselineState", "originalUriBaseIds", "threadId",
}


def _positional(template: str, args: Sequence[str]) -> str:
    def swap(match: re.Match[str]) -> str:
        return "{" + str(list(args).index(match.group(1))) + "}"

    return _POSITIONAL.sub(swap, template)


def _render(template: str, values: Mapping[str, Any]) -> str:
    return _POSITIONAL.sub(lambda m: str(values[m.group(1)]), template)


def _descriptor(r: Mapping[str, Any]) -> dict[str, Any]:
    strings = {m["id"]: {"text": _positional(m["text"], r["args"])} for m in r["messages"]}
    return {
        "id": r["id"],
        "name": r["name"],
        "shortDescription": {"text": r["why"].split(". ")[0].rstrip(".") + "."},
        "fullDescription": {"text": r["statement"]},
        "helpUri": f"repo://graph/rules/catalogue.json#{r['id']}",
        "messageStrings": dict(sorted(strings.items())),
        "defaultConfiguration": {"level": "none" if r["severity"] == "notrun" else r["severity"]},
        "properties": {"category": r["category"], "stratum": r["stratum"], "soundness": r["soundness"]},
    }


def _location(f: Mapping[str, Any]) -> dict[str, Any]:
    loc: dict[str, Any] = {}
    if f.get("uri"):
        phys: dict[str, Any] = {"artifactLocation": {"uri": f["uri"], "uriBaseId": "SRCROOT"}}
        if f.get("start_line"):
            phys["region"] = {"startLine": f["start_line"]}
        loc["physicalLocation"] = phys
    if f.get("logical"):
        loc["logicalLocations"] = [{"fullyQualifiedName": i} for i in sorted(f["logical"])]
    return loc


def _code_flows(witness: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    steps = [{"location": {"logicalLocations": [{"fullyQualifiedName": s["id"]}], "message": {"text": s["text"]}}} for s in witness]
    return [{"threadFlows": [{"locations": steps}]}]


def _suppressions(f: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not f.get("suppression"):
        return []
    s = f["suppression"]
    where = {"physicalLocation": {"artifactLocation": {"uri": s.get("evidence", "graph/suppressions.json"), "uriBaseId": "SRCROOT"}}}
    return [{"kind": "external", "status": "accepted", "justification": s["justification"], "location": where}]


def _message(rule: Mapping[str, Any], message: Mapping[str, Any], all_args: Mapping[str, Any]) -> dict[str, Any]:
    args = {k: all_args[k] for k in rule["args"] if k in all_args}
    return {
        "id": message["id"],
        "arguments": [str(args.get(k, "")) for k in rule["args"]],
        "text": _render(message["text"], {k: args.get(k, "") for k in rule["args"]}),
    }


def _finding_result(rule: Mapping[str, Any], index: int, f: Mapping[str, Any]) -> dict[str, Any]:
    message = next(m for m in rule["messages"] if m["id"] == f["message_id"])
    if message["level"] == "notrun":
        raise ValueError(f"{rule['id']}/{message['id']} is NOT_RUN; pass it in not_run, not in findings")
    subjects = [str(f["args"][k]) for k in rule["subjects"]]
    identity = {k: f["args"][k] for k in rule["identity_args"]}
    loc = _location(f)
    result: dict[str, Any] = {
        "ruleId": rule["id"],
        "ruleIndex": index,
        "kind": "fail",
        "level": message["level"],
        "message": _message(rule, message, f["args"]),
        "locations": [loc] if loc else [],
        "partialFingerprints": {"eijaFinding/v1": fingerprint_v1(rule["id"], subjects, identity)},
        "suppressions": _suppressions(f),
        "properties": {"witnessKind": rule["witness"]["kind"]},
    }
    if f.get("witness"):
        result["codeFlows"] = _code_flows(f["witness"])
    return result


def _not_run_entries(by_id: Mapping[str, Any], index: Mapping[str, int],
                     not_run: Sequence[Mapping[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    notifications: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    for n in sorted(not_run, key=lambda x: (x["rule"], x["reason"])):
        rule = by_id[n["rule"]]
        notifications.append({
            "descriptor": {"id": "EIJA-NOTRUN"},
            "associatedRule": {"id": rule["id"]},
            "level": "error",
            "message": {"text": f"NOT_RUN: rule {rule['id']} was not evaluated: {n['reason']}"},
        })
        results.append({
            "ruleId": rule["id"],
            "ruleIndex": index[rule["id"]],
            "kind": "open",
            "message": {"text": f"NOT_RUN: {n['reason']}"},
            "locations": [],
            "partialFingerprints": {"eijaFinding/v1": fingerprint_v1(rule["id"], [rule["id"]], {"notrun": n["reason"]})},
            "suppressions": [],
        })
    return notifications, results


def _result_key(r: Mapping[str, Any]) -> tuple[Any, ...]:
    locs = r["locations"]
    phys = locs[0].get("physicalLocation", {}) if locs else {}
    uri = phys.get("artifactLocation", {}).get("uri", "")
    line = phys.get("region", {}).get("startLine", 0)
    return (uri, line, r["ruleId"], r["partialFingerprints"]["eijaFinding/v1"])


def _run_properties(graph_root: str | None, verdicts: Mapping[str, str] | None) -> dict[str, Any]:
    props: dict[str, Any] = {"eijaProfile": PROFILE}
    if graph_root:
        props["graphRoot"] = graph_root
    if verdicts:
        props["verdicts"] = dict(sorted(verdicts.items()))
        props["verdict"] = fold_verdicts(verdicts.values())
    return props


def build_sarif(
    catalogue: Mapping[str, Any],
    findings: Sequence[Mapping[str, Any]],
    *,
    not_run: Sequence[Mapping[str, str]] = (),
    artifacts: Mapping[str, str] | None = None,
    graph_root: str | None = None,
    verdicts: Mapping[str, str] | None = None,
    tool_version: str = "0.0.0-design",
) -> dict[str, Any]:
    """Build a SARIF 2.1.0 log in the EIJA determinism profile (rules.md section 7). Pure function of its inputs.

    findings   dicts with rule, message_id, args, uri, start_line (or None), logical (list of ids), witness (list of
               {'id', 'text'}), suppression (None or a dict with justification and evidence)
    not_run    dicts with rule and reason; each becomes a notification and a result of kind 'open'
    verdicts   rule id -> PASS, FAIL or NOT_RUN for every rule evaluated, so that a passing rule leaves a record;
               descriptors are emitted only for rules that have a result
    artifacts  uri -> sha-256 of the LF-folded content, only for referenced files
    """
    by_id = {r["id"]: r for r in catalogue["rules"]}
    used = sorted({f["rule"] for f in findings} | {n["rule"] for n in not_run})
    rules = [by_id[i] for i in used]
    index = {r["id"]: i for i, r in enumerate(rules)}
    results = [_finding_result(by_id[f["rule"]], index[f["rule"]], f) for f in findings]
    notifications, open_results = _not_run_entries(by_id, index, not_run)
    notice = {"id": "EIJA-NOTRUN", "name": "NotRun", "shortDescription": {"text": "A prerequisite is missing; the rule was not evaluated. NOT_RUN absorbs PASS."}}
    run: dict[str, Any] = {
        "tool": {"driver": {"name": "eija-graph", "semanticVersion": tool_version, "rules": [_descriptor(r) for r in rules], "notifications": [notice]}},
        "columnKind": "unicodeCodePoints",
        "artifacts": [{"location": {"uri": uri, "uriBaseId": "SRCROOT"}, "hashes": {"sha-256": digest}} for uri, digest in sorted((artifacts or {}).items())],
        "invocations": [{"executionSuccessful": not notifications, "toolExecutionNotifications": notifications}],
        "results": sorted(results + open_results, key=_result_key),
        "properties": _run_properties(graph_root, verdicts),
    }
    return {"$schema": SARIF_SCHEMA_URI, "version": SARIF_VERSION, "runs": [run]}


def dumps_sarif(doc: Mapping[str, Any]) -> str:
    """Byte-stable serialisation: sorted keys, two-space indent, ASCII escapes, LF, trailing newline."""
    return json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n"


_ABS = re.compile(r"^(?:[A-Za-z]:[\\/]|/|\\\\)|^[A-Za-z][A-Za-z0-9+.-]*://")


def _forbidden_element_problems(key: str, value: Any, ptr: str, child: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if key in FORBIDDEN_KEYS:
        found.append((child, f"forbidden non-deterministic element {key}"))
    if key == "uri" and isinstance(value, str) and _ABS.match(value):
        found.append((child, "absolute or scheme-qualified uri; use a relative uri with uriBaseId"))
    if key == "arguments" and ptr.endswith("/invocations/0"):
        found.append((child, "invocation.arguments can carry absolute paths"))
    return found


def _walk_problems(node: Any, ptr: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(node, Mapping):
        for key, value in node.items():
            child = f"{ptr}/{key}"
            found += _forbidden_element_problems(key, value, ptr, child) + _walk_problems(value, child)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            found += _walk_problems(item, f"{ptr}/{i}")
    return found


def _profile_key(r: Mapping[str, Any]) -> tuple[Any, ...]:
    locs = r.get("locations", [])
    phys = locs[0].get("physicalLocation", {}) if locs else {}
    return (phys.get("artifactLocation", {}).get("uri", ""), phys.get("region", {}).get("startLine", 0),
            r.get("ruleId", ""), r.get("partialFingerprints", {}).get("eijaFinding/v1", ""))


def _result_order_problems(base: str, results: Sequence[Mapping[str, Any]]) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    keys = [_profile_key(r) for r in results]
    prev: tuple[Any, ...] | None = None
    for i, key in enumerate(keys):
        if prev is not None and key < prev:
            found.append((f"{base}/results/{i}", "results are not sorted by (uri, line, ruleId, fingerprint)"))
        prev = key
    return found


def _run_problems(base: str, run: Mapping[str, Any]) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    results = run.get("results", [])
    if results and run.get("columnKind") != "unicodeCodePoints":
        found.append((base + "/columnKind", "columnKind must be set explicitly to unicodeCodePoints"))
    ids = [r["id"] for r in run.get("tool", {}).get("driver", {}).get("rules", [])]
    if ids != sorted(ids):
        found.append((base + "/tool/driver/rules", "rules are not sorted by id"))
    uris = [a["location"]["uri"] for a in run.get("artifacts", [])]
    if uris != sorted(uris):
        found.append((base + "/artifacts", "artifacts are not sorted by uri"))
    found += _result_order_problems(base, results)
    if len({("suppressions" in r) for r in results}) > 1:
        found.append((base + "/results", "suppressions must be present on all results or none (SARIF 3.27.23)"))
    return found


def sarif_profile_problems(doc: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Check a SARIF document against the EIJA determinism profile. Returns sorted (json pointer, problem) pairs."""
    problems = _walk_problems(doc, "")
    for r_i, run in enumerate(doc.get("runs", [])):
        problems += _run_problems(f"/runs/{r_i}", run)
    return sorted(set(problems))
