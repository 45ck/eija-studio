"""Reference semantics for the weave rule system (ADR-0095). Stdlib only; no import from eija_studio.

This module is the executable definition of the parts of the design that must be exact:

* ``fingerprint_v1``   the stable finding identity (rules.md section 6)
* ``rule_verdict`` / ``fold_verdicts``   PASS, FAIL and NOT_RUN semantics (NOT_RUN absorbs PASS, never FAIL)
* ``suppression_status``   suppression expiry without a wall clock, failing closed
* ``build_sarif`` / ``sarif_profile_problems``   the deterministic SARIF 2.1.0 profile and its checker

It is a specification prototype, not the implementation: ``eijagraph.rules`` and ``eijagraph.sarif`` must agree with
it through tests/graph/test_rules_reference.py. Determinism doctrine D-01 to D-24 applies: sorted iteration, no clock,
no locale, explicit UTF-8 and LF.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable, Mapping, Sequence

FINGERPRINT_DOMAIN = "eija.finding.v1"
SAFE_INT = 2**53 - 1
SARIF_VERSION = "2.1.0"
SARIF_SCHEMA_URI = "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json"
PROFILE = "eija-sarif/v1"


# ------------------------------------------------------------------------------------------------ canonical json
def _check_subset(value: Any, path: str = "$") -> None:
    """Strings, safe integers, booleans, null, lists and objects with ASCII identifier keys. No floats (D-02, D-10)."""
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        if abs(value) > SAFE_INT:
            raise ValueError(f"{path}: integer outside the safe range")
        return
    if isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            _check_subset(item, f"{path}[{i}]")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
                raise ValueError(f"{path}: key {key!r} is not an ASCII identifier")
            _check_subset(item, f"{path}.{key}")
        return
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


EFFECTS = ("none", "monotone", "unsafe")


def _overlaps(a: str, b: str) -> bool:
    """True when relation names a and b can hold the same facts: equal, or one is the union view of the other
    (``node`` and ``node.symbol``, ``link`` and ``link.verifies``)."""
    return a == b or a.startswith(b + ".") or b.startswith(a + ".")


def derived_inputs(cat: Mapping[str, Any], name: str) -> tuple[str, ...] | None:
    """Inputs of a derived relation, read from the catalogue ``derivations`` table; None for a base relation.

    Prose entries are resolved conservatively: ``node.<T> ...`` becomes ``node`` (any node type), ``link_status`` becomes
    ``link``, ``node`` and ``ledger``, ``finding`` has no extraction input (it is as complete as the run)."""
    table = cat["derivations"]
    head, _, tail = name.partition(".")
    key = name if name in table else (head + ".<kind>" if tail and head + ".<kind>" in table else None)
    if key is None:
        return None
    if name == "link_status":
        return ("link", "node", "ledger")
    if name == "finding":
        return ()
    out: list[str] = []
    for item in table[key]:
        first = item.split(" ")[0]
        if first.startswith("node.<T>"):
            out.append("node")
        elif "<kind>" in first:
            out.append(first.replace("<kind>", tail))
        else:
            out.append(first)
    return tuple(out)


def read_effect(rule: Mapping[str, Any], incomplete: Iterable[str], cat: Mapping[str, Any]) -> str:
    """How incomplete input relations can distort the findings of one rule: ``none``, ``monotone`` or ``unsafe``.

    ``incomplete`` names base relations whose extractor did not run or ran partially (missing facts, never invented ones).
    A finding is preserved when facts are added only if the rule's violation set is monotone in the incomplete relations.
    Under the declared polarity that holds for a base relation read positively and directly. It fails for a relation read
    negatively (absence findings, anti-joins, ``count < min``: a missing fact can create a finding) and, conservatively,
    for every derived relation (``link_status`` is not monotone in the ledger or in node digests). So:

    * ``none``      no read relation depends on an incomplete one
    * ``monotone``  an incomplete relation is read only positively and directly: a finding seen is real, silence is not
    * ``unsafe``    an incomplete relation is read negatively or through a derived relation: even a finding may be spurious
    """
    bad = list(incomplete)

    def depends(rel: str, seen: frozenset[str] = frozenset()) -> bool:
        if any(_overlaps(rel, b) for b in bad):
            return True
        inputs = derived_inputs(cat, rel)
        if inputs is None or rel in seen:
            return False
        return any(depends(i, seen | {rel}) for i in inputs)

    effect = "none"
    for rel in rule["reads"]["neg"]:
        if depends(rel):
            return "unsafe"
    for rel in rule["reads"]["pos"]:
        if not depends(rel):
            continue
        if derived_inputs(cat, rel) is not None:
            return "unsafe"
        effect = "monotone"
    return effect


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


# ---------------------------------------------------------------------------------------------- suppressions
def suppression_status(supp: Mapping[str, Any], ctx: Mapping[str, Any]) -> str:
    """'active', 'expired' or 'unevaluable'. Only 'active' suppresses (fail closed).

    supp['expires'] is one of
      {'ledger_seq': N}       expires when the ledger has an entry with seq >= N
      {'release': 'vX.Y.Z'}   expires when that release tag exists
      {'until_digest': 'sha256:..', 'subject': id}   expires when the subject digest differs
      {'as_of': 'YYYY-MM-DD'} expires when the explicit as-of input is on or after that date
    ctx supplies ledger_seq_max, releases (a set), digests (a mapping) and as_of (a string or None). No clock is read.
    """
    if not supp.get("justification") or not supp.get("evidence"):
        return "expired"  # WV-045 reports it; it must not suppress
    exp = supp.get("expires")
    if exp is None:
        return "unevaluable"  # every suppression must expire
    if "ledger_seq" in exp:
        return "expired" if ctx.get("ledger_seq_max", 0) >= exp["ledger_seq"] else "active"
    if "release" in exp:
        return "expired" if exp["release"] in ctx.get("releases", set()) else "active"
    if "until_digest" in exp:
        current = ctx.get("digests", {}).get(exp["subject"])
        if current is None:
            return "unevaluable"
        return "active" if current == exp["until_digest"] else "expired"
    if "as_of" in exp:
        as_of = ctx.get("as_of")
        if as_of is None:
            return "unevaluable"
        return "expired" if as_of >= exp["as_of"] else "active"  # ISO dates compare as strings
    return "unevaluable"


# ------------------------------------------------------------------------------------------------ templates
def cardinality_min_sql(scope_view: str, covered_view: str, side: str, peer_view: str | None = None) -> str:
    """The query generated for every cardinality-min rule (WV-010, WV-011, WV-031, WV-037, WV-048 to WV-054, WV-063, ...).

    scope_view    a view with column id: the nodes the obligation applies to (for example node_requirement)
    covered_view  a view with columns link_id, src, dst: the links of the obligated kind whose status is COVERED
    side          'in' counts links that end at the node (dst), 'out' counts links that start at it (src)
    peer_view     optional view with column id: only links whose other end is in this view count (the ``peer`` template
                  parameter, for example node_ui_control). Without it two obligations that differ only in the type of
                  the other end (a transition needs a UI control, a transition needs a symbol) would generate one query.
    The result rows are the violations; zero rows means pass. Parameter :min is the declared minimum."""
    if side not in ("in", "out"):
        raise ValueError("side must be 'in' or 'out'")
    col, other = ("dst", "src") if side == "in" else ("src", "dst")
    for name in (scope_view, covered_view) + ((peer_view,) if peer_view else ()):
        if not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
            raise ValueError(f"unsafe view name {name!r}")
    peer = f" AND c.{other} IN (SELECT id FROM {peer_view})" if peer_view else ""
    return (
        f"SELECT n.id AS node, COUNT(c.link_id) AS count FROM {scope_view} n "
        f"LEFT JOIN {covered_view} c ON c.{col} = n.id{peer} GROUP BY n.id HAVING COUNT(c.link_id) < :min ORDER BY n.id"
    )


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

    descriptors = []
    for r in rules:
        strings = {m["id"]: {"text": _positional(m["text"], r["args"])} for m in r["messages"]}
        descriptors.append(
            {
                "id": r["id"],
                "name": r["name"],
                "shortDescription": {"text": r["why"].split(". ")[0].rstrip(".") + "."},
                "fullDescription": {"text": r["statement"]},
                "helpUri": f"repo://graph/rules/catalogue.json#{r['id']}",
                "messageStrings": dict(sorted(strings.items())),
                "defaultConfiguration": {"level": "none" if r["severity"] == "notrun" else r["severity"]},
                "properties": {"category": r["category"], "stratum": r["stratum"], "soundness": r["soundness"]},
            }
        )

    results: list[dict[str, Any]] = []
    for f in findings:
        rule = by_id[f["rule"]]
        message = next(m for m in rule["messages"] if m["id"] == f["message_id"])
        if message["level"] == "notrun":
            raise ValueError(f"{rule['id']}/{message['id']} is NOT_RUN; pass it in not_run, not in findings")
        args = {k: f["args"][k] for k in rule["args"] if k in f["args"]}
        subjects = [str(f["args"][k]) for k in rule["subjects"]]
        identity = {k: f["args"][k] for k in rule["identity_args"]}
        loc: dict[str, Any] = {}
        if f.get("uri"):
            phys: dict[str, Any] = {"artifactLocation": {"uri": f["uri"], "uriBaseId": "SRCROOT"}}
            if f.get("start_line"):
                phys["region"] = {"startLine": f["start_line"]}
            loc["physicalLocation"] = phys
        if f.get("logical"):
            loc["logicalLocations"] = [{"fullyQualifiedName": i} for i in sorted(f["logical"])]
        result: dict[str, Any] = {
            "ruleId": rule["id"],
            "ruleIndex": index[rule["id"]],
            "kind": "fail",
            "level": message["level"],
            "message": {
                "id": message["id"],
                "arguments": [str(args.get(k, "")) for k in rule["args"]],
                "text": _render(message["text"], {k: args.get(k, "") for k in rule["args"]}),
            },
            "locations": [loc] if loc else [],
            "partialFingerprints": {"eijaFinding/v1": fingerprint_v1(rule["id"], subjects, identity)},
            "suppressions": [],
            "properties": {"witnessKind": rule["witness"]["kind"]},
        }
        if f.get("witness"):
            result["codeFlows"] = [
                {
                    "threadFlows": [
                        {
                            "locations": [
                                {"location": {"logicalLocations": [{"fullyQualifiedName": s["id"]}], "message": {"text": s["text"]}}}
                                for s in f["witness"]
                            ]
                        }
                    ]
                }
            ]
        if f.get("suppression"):
            s = f["suppression"]
            result["suppressions"] = [
                {
                    "kind": "external",
                    "status": "accepted",
                    "justification": s["justification"],
                    "location": {"physicalLocation": {"artifactLocation": {"uri": s.get("evidence", "graph/suppressions.json"), "uriBaseId": "SRCROOT"}}},
                }
            ]
        results.append(result)

    notifications = []
    for n in sorted(not_run, key=lambda x: (x["rule"], x["reason"])):
        rule = by_id[n["rule"]]
        notifications.append(
            {
                "descriptor": {"id": "EIJA-NOTRUN"},
                "associatedRule": {"id": rule["id"]},
                "level": "error",
                "message": {"text": f"NOT_RUN: rule {rule['id']} was not evaluated: {n['reason']}"},
            }
        )
        results.append(
            {
                "ruleId": rule["id"],
                "ruleIndex": index[rule["id"]],
                "kind": "open",
                "message": {"text": f"NOT_RUN: {n['reason']}"},
                "locations": [],
                "partialFingerprints": {"eijaFinding/v1": fingerprint_v1(rule["id"], [rule["id"]], {"notrun": n["reason"]})},
                "suppressions": [],
            }
        )

    def sort_key(r: Mapping[str, Any]) -> tuple[Any, ...]:
        locs = r["locations"]
        phys = locs[0].get("physicalLocation", {}) if locs else {}
        uri = phys.get("artifactLocation", {}).get("uri", "")
        line = phys.get("region", {}).get("startLine", 0)
        return (uri, line, r["ruleId"], r["partialFingerprints"]["eijaFinding/v1"])

    results.sort(key=sort_key)
    run: dict[str, Any] = {
        "tool": {
            "driver": {
                "name": "eija-graph",
                "semanticVersion": tool_version,
                "rules": descriptors,
                "notifications": [
                    {"id": "EIJA-NOTRUN", "name": "NotRun", "shortDescription": {"text": "A prerequisite is missing; the rule was not evaluated. NOT_RUN absorbs PASS."}}
                ],
            }
        },
        "columnKind": "unicodeCodePoints",
        "artifacts": [
            {"location": {"uri": uri, "uriBaseId": "SRCROOT"}, "hashes": {"sha-256": digest}}
            for uri, digest in sorted((artifacts or {}).items())
        ],
        "invocations": [{"executionSuccessful": not notifications, "toolExecutionNotifications": notifications}],
        "results": results,
        "properties": {"eijaProfile": PROFILE},
    }
    if graph_root:
        run["properties"]["graphRoot"] = graph_root
    if verdicts:
        run["properties"]["verdicts"] = dict(sorted(verdicts.items()))
        run["properties"]["verdict"] = fold_verdicts(verdicts.values())
    return {"$schema": SARIF_SCHEMA_URI, "version": SARIF_VERSION, "runs": [run]}


def dumps_sarif(doc: Mapping[str, Any]) -> str:
    """Byte-stable serialisation: sorted keys, two-space indent, ASCII escapes, LF, trailing newline."""
    return json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n"


_ABS = re.compile(r"^(?:[A-Za-z]:[\\/]|/|\\\\)|^[A-Za-z][A-Za-z0-9+.-]*://")


def sarif_profile_problems(doc: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Check a SARIF document against the EIJA determinism profile. Returns sorted (json pointer, problem) pairs."""
    problems: list[tuple[str, str]] = []

    def walk(node: Any, ptr: str) -> None:
        if isinstance(node, Mapping):
            for key, value in node.items():
                child = f"{ptr}/{key}"
                if key in FORBIDDEN_KEYS:
                    problems.append((child, f"forbidden non-deterministic element {key}"))
                if key == "uri" and isinstance(value, str) and _ABS.match(value):
                    problems.append((child, "absolute or scheme-qualified uri; use a relative uri with uriBaseId"))
                if key == "arguments" and ptr.endswith("/invocations/0"):
                    problems.append((child, "invocation.arguments can carry absolute paths"))
                walk(value, child)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{ptr}/{i}")

    walk(doc, "")
    for r_i, run in enumerate(doc.get("runs", [])):
        base = f"/runs/{r_i}"
        results = run.get("results", [])
        if results and run.get("columnKind") != "unicodeCodePoints":
            problems.append((base + "/columnKind", "columnKind must be set explicitly to unicodeCodePoints"))
        ids = [r["id"] for r in run.get("tool", {}).get("driver", {}).get("rules", [])]
        if ids != sorted(ids):
            problems.append((base + "/tool/driver/rules", "rules are not sorted by id"))
        uris = [a["location"]["uri"] for a in run.get("artifacts", [])]
        if uris != sorted(uris):
            problems.append((base + "/artifacts", "artifacts are not sorted by uri"))
        prev: tuple[Any, ...] | None = None
        for i, r in enumerate(results):
            locs = r.get("locations", [])
            phys = locs[0].get("physicalLocation", {}) if locs else {}
            key = (
                phys.get("artifactLocation", {}).get("uri", ""),
                phys.get("region", {}).get("startLine", 0),
                r.get("ruleId", ""),
                r.get("partialFingerprints", {}).get("eijaFinding/v1", ""),
            )
            if prev is not None and key < prev:
                problems.append((f"{base}/results/{i}", "results are not sorted by (uri, line, ruleId, fingerprint)"))
            prev = key
        flags = {("suppressions" in r) for r in results}
        if len(flags) > 1:
            problems.append((base + "/results", "suppressions must be present on all results or none (SARIF 3.27.23)"))
    return sorted(set(problems))


def example_document(catalogue: Mapping[str, Any]) -> dict[str, Any]:
    """The worked example of graph/schema/examples/wv-example.sarif.json (rules.md section 7). Inputs are literals."""
    sha = lambda text: hashlib.sha256(text.encode("utf-8")).hexdigest()  # noqa: E731
    findings = [
        {
            "rule": "WV-010",
            "message_id": "requirement-not-verified",
            "args": {"node": "repo://docs/verification/ACCEPTANCE_MATRIX.csv#AC01", "kind": "verifies", "side": "in", "min": 1, "count": 0,
                     "links_seen": "link.verifies into AC01: none"},
            "uri": "docs/verification/ACCEPTANCE_MATRIX.csv",
            "start_line": 2,
            "logical": ["repo://docs/verification/ACCEPTANCE_MATRIX.csv#AC01"],
        },
        {
            "rule": "WV-005",
            "message_id": "suspect-link-direct",
            "args": {"link": "repo://graph/links/trace.jsonl#lnk-0007", "target": "repo://src/eija_studio/domain/impact.py#closure",
                     "baseline_digest": "sha256:" + sha("closure-old"), "current_digest": "sha256:" + sha("closure-new"), "path_length": 0},
            "uri": "graph/links/trace.jsonl",
            "start_line": 7,
            "logical": ["repo://graph/links/trace.jsonl#lnk-0007"],
            "witness": [
                {"id": "repo://tests/graph/test_impact_math_oracles.py#test_closure_is_least_fixed_point", "text": "verifier anchored by the link"},
                {"id": "repo://src/eija_studio/domain/impact.py#closure", "text": "target whose ast-v1 digest changed"},
            ],
        },
        {
            "rule": "WV-025",
            "message_id": "dependency-cycle",
            "args": {"members": "repo://src/eija_studio/domain/a.py,repo://src/eija_studio/domain/b.py", "size": 2},
            "uri": "src/eija_studio/domain/a.py",
            "start_line": 1,
            "logical": ["repo://src/eija_studio/domain/a.py", "repo://src/eija_studio/domain/b.py"],
            "suppression": {"justification": "cycle removed by ADR-0123; tracked in the baseline", "evidence": "docs/adr/0123-example.md"},
        },
    ]
    not_run = [{"rule": "WV-065", "reason": "generator eija-diagrams is not installed (pin eija-diagrams==0.0.0 missing)"}]
    return build_sarif(
        catalogue,
        findings,
        not_run=not_run,
        artifacts={
            "docs/verification/ACCEPTANCE_MATRIX.csv": sha("acceptance"),
            "graph/links/trace.jsonl": sha("links"),
            "src/eija_studio/domain/a.py": sha("a"),
        },
        graph_root="sha256:" + sha("example-root"),
        verdicts={"WV-001": "PASS", "WV-005": "FAIL", "WV-010": "FAIL", "WV-025": "PASS", "WV-065": "NOT_RUN"},
    )


if __name__ == "__main__":  # python graph/rules/reference.py > graph/schema/examples/wv-example.sarif.json
    import sys
    from pathlib import Path

    cat = json.loads((Path(__file__).resolve().parent / "catalogue.json").read_text(encoding="utf-8"))
    sys.stdout.buffer.write(dumps_sarif(example_document(cat)).encode("utf-8"))
