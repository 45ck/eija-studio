"""Validate graph/rules/catalogue.json and compute its statistics (ADR-0095). Stdlib only.

    python graph/rules/check_catalogue.py            # validate; exit 1 on any error
    python graph/rules/check_catalogue.py --stats    # deterministic JSON statistics (counts, strata, footprints)

The validator is the load-time check of the rule loader in miniature: unknown relations, wrong strata, negation
inside a stratum, messages that use undeclared arguments, unknown mutation operators, rules with no decision entry,
and disagreement with the metamodel (graph/schema/metamodel.json) when it exists. Output is sorted and LF only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
GRAPH = HERE.parent
CATALOGUE = HERE / "catalogue.json"
DECISIONS = HERE / "decisions.jsonl"
METAMODEL = GRAPH / "schema" / "metamodel.json"
BRIEF = GRAPH / "brief.json"

SEVERITY_RANK = {"notrun": 0, "note": 1, "warning": 2, "error": 3}
PHASES = {"P1", "P2", "P3", "P4"}
MATURITY = {"proposed", "experimental", "enforced", "deprecated"}
SOUNDNESS = {"exact", "may", "heuristic"}
CLASSES = {"compile", "lint"}
WITNESS = {"single", "pair", "path", "scope", "diff", "counterexample"}
FIX = {"machine_applicable", "maybe_incorrect", "has_placeholders", "human_only"}
TEMPLATES = {"cardinality-min", "cardinality-max", "acyclic"}
RULE_ID = re.compile(r"^WV-\d{3}$")
PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
NEGATION = re.compile(r"\b(not|no|without|lacks|missing|fewer)\b")

# Rules whose statement uses a negation word but whose negation is over a field or a syntactic property of a row or a
# source object that the rule reads positively (so no relation is read negatively). Reviewed by hand on 2026-09-29; any
# other rule that words a negation must declare a negative read (design section 2.5, 2.6): the closed-world guard and
# the verdict rule depend on the declared polarity being the real one.
ATTRIBUTE_ONLY_NEGATION = {
    "WV-019": "K1 and K2 are attributes of the joined rows",
    "WV-023": "replaced_by is an attribute of the term_meta row",
    "WV-073": "the label is an attribute of the evidence_verdict row",
    "WV-078": "status is an attribute of the adr_meta row",
    "WV-081": "the OSS table rows are an attribute of the adr_meta row",
    "WV-084": "tool, grammar and pins are attributes of the extractor_record row",
    "WV-085": "a syntactic property of the call site (source_call row)",
    "WV-086": "a syntactic property of the call site (source_call row)",
    "WV-089": "compares a recomputed vector with the stored one, both on the committed_file row",
    "WV-090": "properties of one SARIF document",
    "WV-097": "the actor grammar is checked as a pattern (ADR-0094); a declared-actor relation would make this a negative read",
}

# Categories the owner asked for; each must hold at least one active rule.
REQUIRED_COVERAGE = {
    "dangling or stale links": ["link-integrity"],
    "orphans (requirement, term, UI element, test)": ["traceability"],
    "layering and dependency": ["architecture"],
    "naming and vocabulary drift": ["language"],
    "diagram versus model": ["views"],
    "model versus code": ["model-code"],
    "evidence freshness and status lattice": ["evidence"],
    "ADR supersession": ["adr"],
    "determinism violations": ["determinism"],
}

# What each change class dirties (base relations). DESIGN: used only for the footprint statistic.
CHANGE_CLASSES: dict[str, list[str]] = {
    "comment-only edit of a Python function (normalised digest unchanged: early cutoff)": [],
    "body edit of a Python function or method": ["node", "node.symbol", "identifier"],
    "edit of a test function": ["node", "node.test"],
    "add or remove one declared verifies link": ["link", "link.verifies"],
    "edit one term in the registry": ["node", "node.term", "term_form", "term_meta"],
    "edit prose in a document or ADR body": ["node", "node.document", "prose_token", "adr_meta"],
    "edit the UI html or js": ["node", "node.ui_control", "node.ui_field", "node.ui_status", "node.ui_table", "ui_literal"],
    "edit the workflow json": ["node", "node.workflow", "node.state", "node.transition", "node.guard", "node.effect", "node.role"],
    "append one ledger entry": ["ledger", "approved_digest"],
    "edit eijagraph source (static determinism rules)": ["source_call", "node", "node.symbol"],
    "edit the catalogue or a fixture": ["catalogue_rule", "fixture_index", "protected_file"],
}


def load(path: Path = CATALOGUE) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_types() -> tuple[set[str], set[str], dict[str, list[str]], dict[str, Any] | None, str]:
    """(node types incl. supertypes, link kinds, supertype members, metamodel or None, source name)."""
    if METAMODEL.is_file():
        mm = json.loads(METAMODEL.read_text(encoding="utf-8"))
        supers = {k: list(v) for k, v in mm.get("supertypes", {}).items()}
        return set(mm["node_types"]) | set(supers), set(mm["link_types"]), supers, mm, "graph/schema/metamodel.json"
    brief = json.loads(BRIEF.read_text(encoding="utf-8"))
    return {n["id"] for n in brief["node_types"]}, {n["id"] for n in brief["link_types"]}, {}, None, "graph/brief.json"


def relation_stratum(name: str, base: dict[str, int]) -> int | None:
    if name in base:
        return base[name]
    head, _, tail = name.partition(".")
    if tail and head in ("scc", "covered_link", "link_status"):
        return 1
    if tail and head in ("node", "link"):
        return 0
    return None


def validate(cat: dict[str, Any] | None = None) -> list[str]:
    cat = cat or load()
    errors: list[str] = []
    types, kinds, supers, mm, source = load_types()
    rel = {r["name"]: r["stratum"] for r in cat["relations"]}
    rules = cat["rules"]
    ids = [r["id"] for r in rules]
    retired = {x["id"] for x in cat["retired"]}
    ops = cat["mutation_operators"]

    if ids != sorted(ids):
        errors.append("rules are not sorted by id")
    if len(set(ids)) != len(ids):
        errors.append("duplicate rule ids")
    for i in ids:
        if not RULE_ID.match(i):
            errors.append(f"{i}: id does not match WV-NNN")
    for x in cat["retired"]:
        if x["id"] in ids:
            errors.append(f"{x['id']}: retired id is reused")
        if x["merged_into"] not in ids:
            errors.append(f"{x['id']}: merged_into {x['merged_into']} is not an active rule")
    if not (set(rel) >= {"node", "link", "ledger"}):
        errors.append("relations table lacks node, link or ledger")
    for name in cat["categories"]:
        if not any(r["category"] == name for r in rules):
            errors.append(f"category {name} has no rule")

    all_message_ids: Counter[str] = Counter()
    for r in rules:
        rid = r["id"]
        e = errors.append
        for key, allowed in (("category", cat["categories"]), ("kind", cat["kinds"]), ("severity", cat["severities"]), ("tier", cat["tiers"])):
            if r[key] not in allowed:
                e(f"{rid}: {key} {r[key]!r} unknown")
        if r["phase"] not in PHASES:
            e(f"{rid}: phase")
        if r["maturity"] not in MATURITY:
            e(f"{rid}: maturity")
        if r["soundness"] not in SOUNDNESS:
            e(f"{rid}: soundness")
        if r["class"] not in CLASSES:
            e(f"{rid}: class")
        if not (r["implementation"] in ("sql", "python") or r["implementation"].startswith("tool:")):
            e(f"{rid}: implementation {r['implementation']!r}")
        if r["witness"]["kind"] not in WITNESS:
            e(f"{rid}: witness kind")
        if r["implementation"].startswith("tool:") and not r["tool_backed"]:
            e(f"{rid}: tool implementation without tool_backed")
        if r["template"] is not None and r["template"] not in TEMPLATES:
            e(f"{rid}: template")
        if (r["template"] is None) != (r["kind"] != "template"):
            e(f"{rid}: kind template and template field disagree")
        if r["template"] == "cardinality-min":
            peer = r["params"].get("peer")
            if peer is not None:
                if peer not in types:
                    e(f"{rid}: peer node type {peer} is not in {source}")
                if f"node.{peer}" not in r["reads"]["pos"]:
                    e(f"{rid}: peer {peer} is used by the template but node.{peer} is not read")

        # reads and strata
        stratum = 0
        for polarity in ("pos", "neg"):
            for name in r["reads"][polarity]:
                head, _, tail = name.partition(".")
                s = relation_stratum(name, rel)
                if s is None:
                    e(f"{rid}: unknown relation {name}")
                    continue
                if head == "node" and tail and tail not in types:
                    e(f"{rid}: node type {tail} is not in {source}")
                if head in ("link", "scc", "covered_link", "link_status") and tail and tail not in kinds:
                    e(f"{rid}: link kind {tail} is not in {source}")
                stratum = max(stratum, s + (1 if polarity == "neg" else 0))
        if stratum != r["stratum"]:
            e(f"{rid}: stratum {r['stratum']} but the reads give {stratum}")
        if "finding" in r["reads"]["neg"] + r["reads"]["pos"] and r["stratum"] < 3:
            e(f"{rid}: rules over findings must be stratum 3")
        if r["kind"] not in ("meta",) and not r["reads"]["pos"] and not r["reads"]["neg"]:
            e(f"{rid}: reads nothing")

        # messages
        if not r["messages"]:
            e(f"{rid}: no messages")
        levels = [m["level"] for m in r["messages"]]
        for m in r["messages"]:
            all_message_ids[m["id"]] += 1
            if m["level"] not in SEVERITY_RANK:
                e(f"{rid}/{m['id']}: level")
            for ph in PLACEHOLDER.findall(m["text"]):
                if ph not in r["args"]:
                    e(f"{rid}/{m['id']}: placeholder {{{ph}}} is not in args")
        if levels and max(levels, key=SEVERITY_RANK.__getitem__) != r["severity"]:
            e(f"{rid}: severity {r['severity']} is not the highest message level {levels}")
        if not r["subjects"]:
            e(f"{rid}: no subjects (the fingerprint needs them)")
        for a in r["subjects"] + r["identity_args"]:
            if a not in r["args"]:
                e(f"{rid}: {a} is used for identity but is not an arg")
        if len(set(r["args"])) != len(r["args"]):
            e(f"{rid}: duplicate args")

        # mutation matrix
        mu = r["mutations"]
        if not mu["fire"]:
            e(f"{rid}: no fire operator")
        for op in mu["fire"]:
            if op not in ops["fire"]:
                e(f"{rid}: unknown fire operator {op}")
        for op in mu["repair"]:
            if op not in ops["repair"]:
                e(f"{rid}: unknown repair operator {op}")
        for op in mu["benign"]:
            if op not in ops["benign"]:
                e(f"{rid}: unknown benign operator {op}")
        if "RM-REVERT" not in mu["repair"]:
            e(f"{rid}: repair lacks RM-REVERT")
        if r["fix"] is not None:
            if r["fix"].get("applicability") not in FIX or not r["fix"].get("what"):
                e(f"{rid}: fix")
            if r["fix"]["applicability"] not in ("human_only",) and not any(x in ("RM-APPLY-FIX", "RM-REGENERATE", "RM-CANONICALISE", "RM-RENAME-MAP", "RM-SORT") for x in mu["repair"]):
                e(f"{rid}: a fix proposal needs a repair operator that applies it")
        if r["severity"] == "notrun" and r["not_run_when"] and "never" not in r["not_run_when"]:
            e(f"{rid}: a NOT_RUN reporter must not itself depend on a prerequisite")

    # one defect, one rule: two template rules with the same template and parameters generate the same query
    by_params: dict[str, list[str]] = defaultdict(list)
    for r in rules:
        if r["template"] and r["params"]:
            by_params[r["template"] + json.dumps(r["params"], sort_keys=True)].append(r["id"])
    for key, group in sorted(by_params.items()):
        if len(group) > 1:
            errors.append(f"{', '.join(group)}: identical template and params generate one query; merge them or add a distinguishing parameter")

    # declared polarity: a statement that words a negation must read some relation negatively (or be reviewed as attribute-only)
    for r in rules:
        if NEGATION.search(r["statement"]) and not r["reads"]["neg"] and r["id"] not in ATTRIBUTE_ONLY_NEGATION:
            errors.append(f"{r['id']}: the statement words a negation but no relation is read negatively; declare it or add the rule to ATTRIBUTE_ONLY_NEGATION with a reason")
    for rid in sorted(set(ATTRIBUTE_ONLY_NEGATION) - set(ids)):
        errors.append(f"ATTRIBUTE_ONLY_NEGATION names {rid}, which is not an active rule")

    for mid, n in all_message_ids.items():
        if n > 1 and mid != "x":
            errors.append(f"message id {mid} is used {n} times; ids must be unique")

    # governance: every rule has a decision entry with a sequential seq
    decisions = [json.loads(line) for line in DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
    if [d["seq"] for d in decisions] != list(range(1, len(decisions) + 1)):
        errors.append("decisions.jsonl seq is not 1..n")
    have = {d["rule"] for d in decisions}
    for i in ids:
        if i not in have:
            errors.append(f"{i}: no ADR-lite entry in decisions.jsonl")
    for d in decisions:
        if d["rule"] not in ids and d["rule"] not in retired:
            errors.append(f"decisions.jsonl mentions unknown rule {d['rule']}")
    # Promotion gate (content, not presence; WV-093 checks presence). A rule that has left `proposed` needs a checked,
    # rule-specific alternatives entry: the ADR-lite text is otherwise a stub and says nothing about this rule.
    latest = {d["rule"]: d for d in decisions}
    alt_users: Counter[str] = Counter(d["alternatives"] for d in latest.values())
    for r in rules:
        d = latest.get(r["id"])
        if d is None or r["maturity"] in ("proposed", "deprecated"):
            continue
        if not d.get("alternatives_checked"):
            errors.append(f"{r['id']}: maturity {r['maturity']} but its decision entry is a stub (alternatives_checked is not true)")
        elif alt_users[d["alternatives"]] > 1:
            errors.append(f"{r['id']}: maturity {r['maturity']} but its alternatives text is shared with another rule")

    # coverage of the categories the owner asked for
    for label, cats in REQUIRED_COVERAGE.items():
        if sum(1 for r in rules if r["category"] in cats) < 2:
            errors.append(f"required coverage {label!r} has fewer than 2 rules")
    if len(rules) < 40:
        errors.append(f"only {len(rules)} rules; at least 40 are required")

    # banned api list
    apis = [b["api"] for b in cat["banned_apis"]]
    if len(set(apis)) != len(apis):
        errors.append("duplicate banned_apis")

    # metamodel agreement
    if mm is not None:
        by_id = {r["id"]: r for r in rules}
        seen_obligations: set[str] = set()
        for kind, spec in sorted(mm["link_types"].items()):
            for sig in spec["signatures"]:
                for ob in sig.get("obligations", []):
                    rid = ob["rule"]
                    seen_obligations.add(rid)
                    r = by_id.get(rid)
                    if r is None:
                        errors.append(f"metamodel obligation {kind} names {rid}, which is not in the catalogue")
                        continue
                    if r["template"] != "cardinality-min":
                        errors.append(f"{rid}: metamodel says obligation on {kind}; catalogue template is {r['template']}")
                        continue
                    p = r["params"]
                    if (p["scope"].split()[0], p["kind"], p["side"], p["min"]) != (ob["scope"].split()[0], kind, ob["side"], ob["min"]):
                        errors.append(f"{rid}: params {p} disagree with the metamodel obligation {ob} on {kind}")
        for r in rules:
            if r["template"] == "cardinality-min" and (r["metamodel"] or "").startswith("in metamodel") and r["id"] not in seen_obligations:
                errors.append(f"{r['id']}: says it is in the metamodel but no obligation names it")
    return errors


# ----------------------------------------------------------------------------------------------- statistics
def _parents(name: str, supers: dict[str, list[str]]) -> list[str]:
    head, _, tail = name.partition(".")
    out = []
    if tail and head in ("node", "link", "link_status"):
        out.append(head)
    if head == "node" and tail:
        out += ["node." + s for s, members in supers.items() if tail in members]
    return out


def anchored_node_types(mm: dict[str, Any] | None, kind: str) -> set[str] | None:
    """Node types at an anchored end of a link kind, or None when the metamodel is absent (then assume every type)."""
    if mm is None:
        return None
    spec = mm["link_types"][kind]
    supers = mm.get("supertypes", {})
    out: set[str] = set()
    for sig in spec["signatures"]:
        for end in spec.get("anchor_ends", []):
            for t in sig[end]:
                out.update(mm["node_types"] if t == "*" else supers.get(t, [t]))
    return out


def dirty_closure(seeds: list[str], supers: dict[str, list[str]], mm: dict[str, Any] | None, kinds: list[str]) -> set[str]:
    """Relations made dirty by a change, under the derivation table (DESIGN, catalogue 'derivations')."""
    dirty = set(seeds)
    for s in list(dirty):
        dirty.update(_parents(s, supers))
    anchors = {k: anchored_node_types(mm, k) for k in kinds}
    while True:
        before = set(dirty)
        node_types = {d.split(".", 1)[1] for d in dirty if d.startswith("node.")}
        for k in kinds:
            moved = "ledger" in dirty or f"link.{k}" in dirty or (anchors[k] is None and "node" in dirty) or (
                anchors[k] is not None and bool(anchors[k] & node_types))
            if moved:
                dirty.update({f"link_status.{k}", f"covered_link.{k}", "link_status"})
            if f"link.{k}" in dirty:
                dirty.update({f"scc.{k}", "link", "affected"})
        if "link.contains" in dirty or "component_of" in dirty or "link.depends_on" in dirty:
            dirty.update({"component_of"} if "link.contains" in dirty else set())
            dirty.add("component_edge")
        if {"link.realises", "link.exposes"} & dirty:
            dirty.add("exposed_transition")
        if {"link.motivates", "link.supersedes"} & dirty:
            dirty.add("live_motivated")
        if {"evidence_subject", "current_subject", "checker_registry", "evidence_meta"} & dirty:
            dirty.add("evidence_verdict")
        if dirty == before:
            return dirty


def dirty_rules(seeds: list[str], cat: dict[str, Any], supers: dict[str, list[str]], mm: dict[str, Any] | None, kinds: list[str]) -> list[str]:
    """Rules whose read set intersects the dirty relations, plus the stratum-3 rules when any rule is dirty."""
    dirty = dirty_closure(seeds, supers, mm, kinds)
    hit = {r["id"] for r in cat["rules"] if (set(r["reads"]["pos"]) | set(r["reads"]["neg"])) & dirty}
    if hit:
        hit.update(r["id"] for r in cat["rules"] if "finding" in r["reads"]["pos"] + r["reads"]["neg"])
    return sorted(hit)


def stats(cat: dict[str, Any] | None = None) -> dict[str, Any]:
    cat = cat or load()
    _, kinds, supers, mm, source = load_types()
    rules = cat["rules"]

    def count(key: str) -> dict[str, int]:
        return dict(sorted(Counter(r[key] for r in rules).items()))

    decisions = [json.loads(line) for line in DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
    cases = 0
    per_rule_cases = {}
    for r in rules:
        m = r["mutations"]
        n = 1 + len(m["fire"]) + len(m["repair"]) + len(m["benign"])
        per_rule_cases[r["id"]] = n
        cases += n
    fan: dict[str, int] = defaultdict(int)
    for r in rules:
        for name in set(r["reads"]["pos"]) | set(r["reads"]["neg"]):
            fan[name] += 1
    footprints = {}
    for label, seeds in CHANGE_CLASSES.items():
        hit = dirty_rules(seeds, cat, supers, mm, sorted(kinds))
        footprints[label] = {"dirty_rules": len(hit), "of": len(rules), "by_tier": dict(sorted(Counter(next(r["tier"] for r in rules if r["id"] == h) for h in hit).items()))}
    return {
        "source_of_types": source,
        "rules": len(rules),
        "retired": len(cat["retired"]),
        "by_category": count("category"),
        "by_kind": count("kind"),
        "by_severity": count("severity"),
        "by_tier": count("tier"),
        "by_phase": count("phase"),
        "by_stratum": {str(k): v for k, v in sorted(Counter(r["stratum"] for r in rules).items())},
        "by_class": count("class"),
        "by_soundness": count("soundness"),
        "by_implementation": dict(sorted(Counter(r["implementation"].split(":")[0] for r in rules).items())),
        "templates": dict(sorted(Counter(r["template"] for r in rules if r["template"]).items())),
        "with_fix": sum(1 for r in rules if r["fix"]),
        "decision_entries": {
            "total": len(decisions),
            "alternatives_checked": sum(1 for d in decisions if d.get("alternatives_checked")),
            "stub": sum(1 for d in decisions if not d.get("alternatives_checked")),
        },
        "tool_backed": sorted(r["id"] for r in rules if r["tool_backed"]),
        "metamodel_proposals": sorted(r["id"] for r in rules if (r["metamodel"] or "").startswith("proposed")),
        "brief_ids_kept": sum(1 for r in rules if r["brief_id"]),
        "fixture_cases_minimum": cases,
        "fixture_cases_per_rule_max": max(per_rule_cases.values()),
        "relations": len(cat["relations"]),
        "top_read_relations": dict(sorted(fan.items(), key=lambda kv: (-kv[1], kv[0]))[:12]),
        "change_footprints": footprints,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()
    errors = validate()
    if args.stats:
        sys.stdout.write(json.dumps(stats(), indent=2, sort_keys=True) + "\n")
    if errors:
        for line in errors:
            sys.stderr.write(line + "\n")
        sys.stderr.write(f"{len(errors)} error(s)\n")
        return 1
    if not args.stats:
        print(f"catalogue OK: {len(load()['rules'])} rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
