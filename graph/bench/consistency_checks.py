"""Reproducible checks behind docs/weave/design/consistency-and-sync.md and graph/schema/transformations.md.

Every check reports MEASURED (it ran; the numbers are real for the stated domain) or NOT_RUN with a
reason when a prerequisite (git, the okf lane worktree) is missing. Nothing here proves a property for
all inputs: each check is an exhaustive enumeration of a small domain or a seeded sample, and says which.
These are reference sketches that pin the contracts; they are not the product code (eijagraph.views and
eijagraph.merge come later and must pass the same laws).

Read-only use of the kernel (imports ``eija_studio.domain`` from ``src/``) and of the okf lane's
``quality/okf/pages.py`` (parsed with ``ast``, never imported). Output is canonical ASCII JSON (sorted
keys, integers only, no timestamps), so two runs on one platform are byte-identical. Temp files live in
``.tmp/`` inside the worktree.

    python graph/bench/consistency_checks.py
"""
from __future__ import annotations

import ast
import bisect
import hashlib
import itertools
import json
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from eija_studio.domain.models import DomainError, SemanticTransaction, Transition, Workflow  # noqa: E402
from eija_studio.domain.policy import apply_transaction, baseline, check_policy  # noqa: E402

TMP = ROOT / ".tmp" / "merge_bench"


def not_run(reason: str) -> dict:
    return {"status": "NOT_RUN", "reason": reason}


# --------------------------------------------------------------------------------------------------
# M. Keyed three-way merge: the per-key flat-lattice join.
# --------------------------------------------------------------------------------------------------
Rec = dict[str, str]  # key -> canonical record text; an absent key is an absent record


def merge3(base: Rec, ours: Rec, theirs: Rec) -> tuple[Rec, list[dict]]:
    """Per key: equal sides win; a side equal to base yields to the other; otherwise a conflict.

    Depends only on the three inputs. Iterates over sorted keys, so output order is total.
    """
    merged: Rec = {}
    conflicts: list[dict] = []
    for k in sorted(set(base) | set(ours) | set(theirs)):
        b, o, t = base.get(k), ours.get(k), theirs.get(k)
        if o == t:
            v = o
        elif o == b:
            v = t
        elif t == b:
            v = o
        else:
            conflicts.append({"key": k, "base": b, "ours": o, "theirs": t})
            continue
        if v is not None:
            merged[k] = v
    return merged, conflicts


def _rand_rec(rng: random.Random, keys: list[str]) -> Rec:
    return {k: rng.choice("abc") for k in keys if rng.random() < 0.5}


def _mutate(rng: random.Random, base: Rec, keys: list[str], p: float) -> Rec:
    """A replica derived from base: each key is independently edited (changed, added or removed) with probability p."""
    out = dict(base)
    for k in keys:
        if rng.random() < p:
            v = rng.choice(["a", "b", "c", None])  # None removes
            if v is None:
                out.pop(k, None)
            else:
                out[k] = v
    return out


def keyed_merge_laws(trials: int = 3000, seed: int = 20260929) -> dict:
    """Symmetry, identity, idempotence and associativity of merge3 over a small colliding key space."""
    rng = random.Random(seed)
    keys = [f"k{i}" for i in range(6)]
    c = dict.fromkeys(("symmetric", "identity", "idempotent", "associative_when_defined", "defined_iff_one_change"), 0)
    seen_conflict = seen_defined = 0
    for _ in range(trials):
        b = _rand_rec(rng, keys)
        o, t, u = (_mutate(rng, b, keys, 0.12) for _ in range(3))
        m1, c1 = merge3(b, o, t)
        m2, c2 = merge3(b, t, o)
        swapped = [{"key": x["key"], "base": x["base"], "ours": x["theirs"], "theirs": x["ours"]} for x in c2]
        c["symmetric"] += (m1 == m2 and c1 == swapped)
        mi, ci = merge3(b, o, b)
        c["identity"] += (mi == o and not ci)
        mx, cx = merge3(b, o, o)
        c["idempotent"] += (mx == o and not cx)
        # (o + t) + u  versus  o + (t + u), same base; defined only when no stage conflicts.
        left_i, lc1 = merge3(b, o, t)
        left = merge3(b, left_i, u) if not lc1 else None
        right_i, rc1 = merge3(b, t, u)
        right = merge3(b, o, right_i) if not rc1 else None
        ldef = left is not None and not left[1]
        rdef = right is not None and not right[1]
        c["associative_when_defined"] += (ldef == rdef and (not ldef or (left is not None and right is not None and left[0] == right[0])))
        # Definedness theorem: per key, defined iff at most one distinct value differs from base.
        all_def = all(len({x.get(k) for x in (o, t, u)} - {b.get(k)}) <= 1 for k in set().union(b, o, t, u))
        c["defined_iff_one_change"] += (ldef == all_def and rdef == all_def)
        seen_conflict += (not ldef)
        seen_defined += ldef
    return {"status": "MEASURED", "trials": trials, "seed": seed, "passes": c,
            "trials_defined": seen_defined, "trials_with_conflict": seen_conflict,
            "domain": "6 keys, values a/b/c or absent; base random, three replicas each edit a key with p=0.12; one shared base"}


# --------------------------------------------------------------------------------------------------
# G. git's line merge versus the keyed merge on line-oriented files.
# --------------------------------------------------------------------------------------------------
def _git_ok() -> bool:
    try:
        return subprocess.run(["git", "--version"], capture_output=True).returncode == 0
    except OSError:
        return False


def _merge_file(d: Path, ours: list[str], base: list[str], theirs: list[str], union: bool = False) -> tuple[int, list[str]]:
    files = {}
    for name, lines in (("o", ours), ("b", base), ("t", theirs)):
        p = d / name
        p.write_bytes(("".join(x + "\n" for x in lines)).encode("utf-8"))
        files[name] = str(p)
    cmd = ["git", "merge-file", "-p"] + (["--union"] if union else []) + [files["o"], files["b"], files["t"]]
    r = subprocess.run(cmd, capture_output=True)
    text = r.stdout.decode("utf-8")
    return r.returncode, text.splitlines()


def predicted_permille(n: int, a: int, b: int, samples: int = 100000, seed: int = 7) -> int:
    """PREDICTION by simulation, no git involved. Model: base keys are n random points; each side adds keys drawn from the
    same distribution; git's line merge conflicts iff the two sides insert into the same gap between base lines (rule
    calibrated by the exhaustive gap-distance run: distance 0 conflicts, distance 1 and more do not). Because random base
    keys leave unequal gaps, P(same gap) for one insertion each is 2/(n+2), not 1/(n+1). Integer permille."""
    rng = random.Random(seed)
    hits = 0
    for _ in range(samples):
        pts = sorted(rng.random() for _ in range(n))
        ga = {bisect.bisect(pts, rng.random()) for _ in range(a)}
        gb = {bisect.bisect(pts, rng.random()) for _ in range(b)}
        hits += bool(ga & gb)
    return round(1000 * hits / samples)


def gap_distance_rule(d: Path, n: int) -> dict:
    """Exhaustive: one insertion on each side at every pair of gaps; which gap distances make git conflict? All distances reported."""
    keys = [f"{10 * (i + 1):05d}" for i in range(n)]
    base = [json.dumps({"id": k}, separators=(",", ":")) for k in keys]

    def with_insert(g: int, tag: str) -> list[str]:
        new = json.dumps({"id": f"{10 * g + 5:05d}", "by": tag}, separators=(",", ":"))
        return sorted(base + [new])

    by_dist: dict[int, list[int]] = {}
    for g1 in range(n + 1):
        for g2 in range(n + 1):
            rc, _ = _merge_file(d, with_insert(g1, "o"), base, with_insert(g2, "t"))
            by_dist.setdefault(abs(g1 - g2), [0, 0])
            by_dist[abs(g1 - g2)][0] += (rc != 0)
            by_dist[abs(g1 - g2)][1] += 1
    return {str(k): {"conflicts": v[0], "pairs": v[1]} for k, v in sorted(by_dist.items())}


def git_line_merge_vs_keyed(trials: int = 200, n: int = 20, seed: int = 20260929) -> dict:
    """How often does git's textual merge conflict on sorted JSONL sets, append-only ledgers and edits?"""
    if not _git_ok():
        return not_run("git not found")
    TMP.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    def rec(key: str, v: int = 0) -> str:
        return json.dumps({"id": key, "v": v}, sort_keys=True, separators=(",", ":"))

    out: dict[str, Any] = {"status": "MEASURED", "trials_per_scenario": trials, "base_lines": n, "seed": seed}
    with tempfile.TemporaryDirectory(dir=str(TMP)) as td:
        d = Path(td)
        rule = gap_distance_rule(d, min(n, 12))
        out["gap_distance_rule_n12"] = rule
        dstar = max((int(k) for k, v in rule.items() if v["conflicts"] > 0), default=-1)
        out["calibrated_conflict_distance"] = dstar
        out["key_model"] = ("uniform random 32-bit hex keys (hash-like). The predicted 2/(n+2) and the measured permille hold "
                            "only for hash-sorted keys; human-keyed files (REQ-101, REQ-102 appended by two branches) cluster inserts "
                            "and conflict more often")
        # Scenario A: both sides add a and b records to a set sorted by a random (hash-like) key.
        for a, b in ((1, 1), (2, 2), (3, 3)):
            git_conf = keyed_conf = union_equal = clean_total = clean_agree = 0
            for _ in range(trials):
                pool = {f"{rng.getrandbits(32):08x}" for _ in range(n + a + b + 5)}
                ids = sorted(pool)
                rng.shuffle(ids)
                base_ids, add = sorted(ids[:n]), ids[n:n + a + b]
                ours_add, theirs_add = add[:a], add[a:a + b]
                base = [rec(k) for k in base_ids]
                ours = sorted(base + [rec(k) for k in ours_add])
                theirs = sorted(base + [rec(k) for k in theirs_add])
                rc, glines = _merge_file(d, ours, base, theirs)
                git_conf += (rc != 0)
                mk, ck = merge3(dict.fromkeys(base, "x"), dict.fromkeys(ours, "x"), dict.fromkeys(theirs, "x"))
                keyed_conf += bool(ck)
                if rc == 0:
                    clean_total += 1
                    clean_agree += (glines == sorted(mk))
                if (a, b) == (2, 2):  # union is measured once, to bound the number of git processes
                    _, ulines = _merge_file(d, ours, base, theirs, union=True)
                    union_equal += (sorted(set(ulines)) == sorted(set(ours) | set(theirs)))
            out[f"A_sorted_set_adds_{a}x{b}"] = {
                "git_text_conflicts": git_conf, "keyed_conflicts": keyed_conf,
                "git_clean_merges": clean_total, "git_clean_equals_keyed_result": clean_agree,
                "git_union_then_sort_unique_equals_set_union": union_equal if (a, b) == (2, 2) else None,
                "predicted_git_conflicts_permille": predicted_permille(n, a, b),
                "measured_git_conflicts_permille": round(1000 * git_conf / trials)}
        # Scenario B: append-only ledger with sequence numbers; both sides append one entry.
        git_conf = union_dup = 0
        for _ in range(trials):
            base = [json.dumps({"seq": i, "e": f"{rng.getrandbits(32):08x}"}, sort_keys=True, separators=(",", ":")) for i in range(1, n + 1)]
            ours = base + [json.dumps({"seq": n + 1, "e": "ours"}, sort_keys=True, separators=(",", ":"))]
            theirs = base + [json.dumps({"seq": n + 1, "e": "theirs"}, sort_keys=True, separators=(",", ":"))]
            rc, _ = _merge_file(d, ours, base, theirs)
            git_conf += (rc != 0)
            _, ulines = _merge_file(d, ours, base, theirs, union=True)
            seqs = [json.loads(x)["seq"] for x in ulines]
            union_dup += (len(seqs) != len(set(seqs)))
        out["B_append_only_sequence_numbers"] = {"git_text_conflicts": git_conf,
            "git_union_yields_duplicate_seq": union_dup}
        # Scenario C: each side edits one existing record, distinct records i != j.
        conf_adj = tot_adj = conf_far = tot_far = c_clean = c_agree = 0
        for _ in range(trials):
            cids = sorted({f"{rng.getrandbits(32):08x}" for _ in range(n)})
            base = [rec(k) for k in cids]
            i, j = rng.sample(range(len(cids)), 2)
            ours, theirs = list(base), list(base)
            ours[i] = rec(cids[i], 1)
            theirs[j] = rec(cids[j], 2)
            rc, glines = _merge_file(d, ours, base, theirs)
            adjacent = abs(i - j) == 1
            if adjacent:
                tot_adj += 1
                conf_adj += (rc != 0)
            else:
                tot_far += 1
                conf_far += (rc != 0)
            mk, ck = merge3(dict(zip(cids, base)), dict(zip(cids, ours)), dict(zip(cids, theirs)))
            assert not ck
            if rc == 0:
                c_clean += 1
                c_agree += (glines == [mk[k] for k in sorted(mk)])
        out["C_edit_two_distinct_records"] = {"adjacent_pairs": tot_adj, "adjacent_git_conflicts": conf_adj,
            "non_adjacent_pairs": tot_far, "non_adjacent_git_conflicts": conf_far, "keyed_conflicts": 0,
            "git_clean_merges": c_clean, "git_clean_equals_keyed_result": c_agree}
    return out


# --------------------------------------------------------------------------------------------------
# I. Invariants that a clean keyed merge does not preserve (I-confluence, Bailis et al. 2015).
# --------------------------------------------------------------------------------------------------
def _wf_to_map(w: Workflow) -> Rec:
    m: Rec = {"initial_state": w.initial_state}
    for s in w.states:
        m[f"state:{s}"] = s
    for t in w.transitions:
        m[f"transition:{t.id}"] = json.dumps(t.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return m


def _map_to_wf(m: Rec) -> Workflow:
    states = tuple(sorted(v for k, v in m.items() if k.startswith("state:")))
    trans = tuple(Transition(**json.loads(v)) for k, v in sorted(m.items()) if k.startswith("transition:"))
    return Workflow(initial_state=m["initial_state"], states=states, transitions=trans)


def _extra(id_: str, action: str, src: str, dst: str) -> Transition:
    from eija_studio.domain.models import BASE_GUARDS
    return Transition(id=id_, action=action, from_state=src, to_state=dst, role="Teacher", guards=BASE_GUARDS,
                      required_effects=("Audit:X",), forbidden_effects=("PaymentCaptured",))


def _with(w: Workflow, states: Iterable[str] | None = None, add: Iterable[Transition] = (),
          drop_actions: Iterable[str] = ()) -> Workflow:
    drop = set(drop_actions)
    trans = tuple(t for t in w.transitions if t.action not in drop) + tuple(add)
    return Workflow(states=tuple(states) if states is not None else w.states, transitions=trans)


def _structure_errors(w: Workflow) -> list[str]:
    """Structural (constructor) errors of a workflow, recomputed by revalidating its own dump. Empty means valid."""
    try:
        Workflow.model_validate(w.model_dump(mode="json"))
        return []
    except ValueError as e:  # pydantic ValidationError is a ValueError
        return sorted(x["msg"] for x in e.errors()) if hasattr(e, "errors") else [str(e)]  # type: ignore[attr-defined]


def non_confluent_invariants() -> dict:
    """Which invariants survive a clean keyed merge of two structurally valid workflows?

    Two levels are kept apart, because they are different sets:
    * structural errors: what the ``Workflow`` constructor rejects (unique action, no dangling state). Both sides
      are constructed workflows, so they are structurally valid; the flags are computed, not assumed.
    * policy findings: what ``check_policy`` reports. On these scenarios BOTH sides already carry policy findings
      (they add an unsupported action), so the invariants tested here are structural, and the policy set difference
      is reported only when the merged workflow is structurally valid.
    A merged workflow that fails the constructor has no policy findings to compare: the run is a structural-error
    illustration of M8, not a set difference of ``Finding`` objects.
    """
    base = baseline()
    scenarios: dict[str, tuple[Workflow, Workflow]] = {}
    # 1. Uniqueness with a chosen value: both add an "Escalate" action under different transition ids.
    scenarios["unique_action_specific_value"] = (
        _with(base, add=[_extra("TR-ESC-A", "Escalate", "Draft", "Submitted")]),
        _with(base, add=[_extra("TR-ESC-B", "Escalate", "Submitted", "Approved")]))
    # 2. Foreign key with delete: ours removes state Rejected and its transitions, theirs adds a use of it.
    scenarios["foreign_key_delete_vs_insert"] = (
        _with(base, states=("Draft", "Submitted", "Approved"), drop_actions=("Reject", "Revise")),
        _with(base, add=[_extra("TR-ESC", "Escalate", "Submitted", "Rejected")]))
    # 3. Foreign key with inserts only: both add an unused state (control, expected I-confluent).
    scenarios["control_insert_only"] = (
        _with(base, states=base.states + ("Held",)),
        _with(base, states=base.states + ("Closed",)))
    out: dict[str, Any] = {"status": "MEASURED", "scenarios": {}}
    for name, (o, t) in scenarios.items():
        merged, conflicts = merge3(_wf_to_map(base), _wf_to_map(o), _wf_to_map(t))
        merged_errors: list[str] = []
        emergent_policy: list[str] = []
        try:
            mw: Workflow | None = _map_to_wf(merged)
        except ValueError as e:
            mw = None
            merged_errors = sorted(x["msg"] for x in e.errors()) if hasattr(e, "errors") else [str(e)]  # type: ignore[attr-defined]
        if mw is not None:
            emergent_policy = sorted(set(check_policy(mw)) - (set(check_policy(o)) | set(check_policy(t))))
        out["scenarios"][name] = {
            "ours_structure_errors": _structure_errors(o), "theirs_structure_errors": _structure_errors(t),
            "ours_policy_findings": len(check_policy(o)), "theirs_policy_findings": len(check_policy(t)),
            "keyed_merge_conflicts": len(conflicts),
            "merged_structure": "valid" if mw is not None else "invalid",
            "emergent_structure_errors": merged_errors,
            "emergent_policy_findings_when_merged_valid": emergent_policy}
    return out


# --------------------------------------------------------------------------------------------------
# L. Lens laws for a state-view edit translator over the kernel's real transaction alphabet.
# --------------------------------------------------------------------------------------------------
Edge = tuple[str, str, str]  # (action, from_state, to_state); role and id are annotations, not identity


def get_view(w: Workflow) -> tuple[frozenset[str], frozenset[Edge]]:
    return frozenset(w.states), frozenset((t.action, t.from_state, t.to_state) for t in w.transitions)


def sem(w: Workflow) -> str:
    return w.semantic_hash


# A view edit is a tuple. ("add_edge", action, src, dst) | ("retarget", action, new_src) | ("move", node, x, y)
# | anything else is outside the alphabet.
def apply_view_edit(view: tuple[frozenset[str], frozenset[Edge]], edit: tuple) -> tuple[frozenset[str], frozenset[Edge]] | None:
    states, edges = view
    if edit[0] == "add_edge":
        _, action, src, dst = edit
        return states | {src, dst}, edges | {(action, src, dst)}
    if edit[0] == "retarget":
        _, action, new_src = edit
        old = [e for e in edges if e[0] == action]
        if len(old) != 1 or new_src not in states:
            return None
        return states, (edges - {old[0]}) | {(action, new_src, old[0][2])}
    if edit[0] == "move":
        return view
    return None


def translate(model: Workflow, edit: tuple) -> tuple[str, Any]:
    """('Accepted', (transactions, layout_changes)) or ('Rejected', code). Never raises, never applies."""
    try:
        kind = edit[0]
        if kind == "move":
            _, node, x, y = edit
            if node not in model.states:
                return "Rejected", "UNKNOWN_NODE"
            return "Accepted", ((), ((node, x, y),))
        if kind == "add_edge":
            _, action, src, dst = edit
            if (action, src, dst) in get_view(model)[1]:
                return "Accepted", ((), ())  # no-op: GetPut
            if (action, src, dst) == ("Recommend", "Submitted", "Recommended"):
                return "Accepted", (("enable_recommendation",), ())
            return "Rejected", "UNSUPPORTED_EDIT"
        if kind == "retarget":
            _, action, new_src = edit
            if action != "Reject":
                return "Rejected", "UNSUPPORTED_EDIT"
            if new_src not in ("Submitted", "Recommended"):
                return "Rejected", "UNSUPPORTED_REJECTION_SOURCE"
            cur = next((t.from_state for t in model.transitions if t.action == "Reject"), None)
            if cur == new_src:
                return "Accepted", ((), ())
            txs = ("set_rejection_source:" + new_src,)
            try:
                put(model, txs)  # dry run: an Accepted proposal must be applicable (law L9)
            except DomainError as err:
                return "Rejected", err.code  # e.g. MEANING_REQUIRED before enable_recommendation
            return "Accepted", (txs, ())
        return "Rejected", "UNSUPPORTED_EDIT"
    except (ValueError, TypeError, IndexError):
        return "Rejected", "MALFORMED_EDIT"


def put(model: Workflow, txs: tuple[str, ...]) -> Workflow:
    """The only put: the kernel's apply_transaction. Raises DomainError on refusal."""
    for tx in txs:
        if tx == "enable_recommendation":
            model = apply_transaction(model, SemanticTransaction(kind="enable_recommendation"))
        else:
            src = tx.split(":", 1)[1]
            model = apply_transaction(model, SemanticTransaction(kind="set_rejection_source", rejection_source=src))
    return model


_PRIORITY = {"add_edge": 0, "retarget": 1, "move": 2}
# Declared amendment classes: which actions a transaction kind may rewire beyond the drawn edit (kernel apply_transaction).
AMENDMENT_POLICY: dict[str, set[str]] = {"enable_recommendation": {"Approve", "Reject"}, "set_rejection_source": set()}


def translate_batch(model: Workflow, edits: list[tuple], tr=None) -> tuple[str, Any]:
    """Dependency order (semantic before layout; enabling before dependent), then a total tiebreak."""
    tr = tr or translate
    # L6: two different edits of one slot do not commute and have no dependency order; refuse, never pick a winner.
    slots: dict[Any, tuple] = {}
    for e in edits:
        try:
            slot = ("node", e[1]) if e[0] == "move" else ("edge", e[1]) if e[0] in ("add_edge", "retarget") else None
        except (IndexError, TypeError):
            slot = None
        if slot is not None:
            if slot in slots and slots[slot] != e:
                return "Rejected", "CONFLICTING_EDITS"
            slots[slot] = e
    ordered = sorted(edits, key=lambda e: (_PRIORITY.get(e[0], 9), json.dumps(e)))
    txs: list[str] = []
    layout: list[tuple] = []
    cur = model
    for e in ordered:
        kind, res = tr(cur, e)
        if kind == "Rejected":
            return "Rejected", res
        t, l = res
        try:
            cur = put(cur, t)
        except DomainError as err:
            return "Rejected", err.code
        txs += list(t)
        layout += list(l)
    return "Accepted", (tuple(txs), tuple(sorted(layout)))


def safe_put(m: Workflow, txs: tuple[str, ...]) -> Workflow | None:
    try:
        return put(m, txs)
    except DomainError:
        return None


def lens_laws_on_kernel_alphabet(tr=None) -> dict:
    tr = tr or translate
    base = baseline()
    cand = apply_transaction(base, SemanticTransaction(kind="enable_recommendation"))
    bases = {"baseline": base, "candidate": cand}
    alphabet = [("add_edge", "Recommend", "Submitted", "Recommended"),
                ("retarget", "Reject", "Submitted"), ("retarget", "Reject", "Recommended"),
                ("move", "Draft", 10, 20), ("move", "Nowhere", 1, 1),
                ("add_edge", "Escalate", "Draft", "Approved"), ("retarget", "Approve", "Draft"),
                ("delete_state", "Draft"), (), ("move", "Draft")]
    r: dict[str, Any] = {"status": "MEASURED", "bases": sorted(bases), "alphabet_size": len(alphabet)}

    # L7 totality: every edit gives Accepted or Rejected with a code; nothing raises.
    total = 0
    accepted_pairs = []
    for bn, m in bases.items():
        for e in alphabet:
            kind, res = tr(m, e)
            assert kind in ("Accepted", "Rejected")
            total += 1
            if kind == "Accepted":
                accepted_pairs.append((bn, m, e, res))
    r["L7_totality_pairs_checked"] = total
    # L9 applicability: every Accepted proposal applies through the kernel put without a refusal.
    r["L9_accepted_apply_cleanly"] = {"accepted": len(accepted_pairs),
        "pass": sum(safe_put(m, res[0]) is not None for _, m, _, res in accepted_pairs)}

    # L1 GetPut: an edit that asks for what the view already shows yields no transactions and no change.
    noops = [("add_edge", "Recommend", "Submitted", "Recommended"), ("retarget", "Reject", "Recommended"),
             ("retarget", "Reject", "Submitted")]
    getput_ok = getput_n = 0
    for m in bases.values():
        for e in noops:
            applied = apply_view_edit(get_view(m), e)
            if applied is None or applied != get_view(m):
                continue  # the edit is not a no-op on this base
            kind, res = tr(m, e)
            getput_n += 1
            after = safe_put(m, res[0]) if kind == "Accepted" else None
            getput_ok += (kind == "Accepted" and res == ((), ()) and after is not None and sem(after) == sem(m))
    r["L1_getput"] = {"noop_pairs": getput_n, "pass": getput_ok}

    # L2 PutGet modulo layout and declared amendments. Classical PutGet (get(put(a, c)) = a) fails by design when the
    # kernel completes an edit: the amendment alpha is the symmetric difference between the picture the user drew
    # (the intended view) and get(put(...)). The law: after = (intended - alpha_removed) + alpha_added exactly, alpha is
    # reported, and alpha only touches the actions the transaction kind is declared to rewire; empty alpha otherwise.
    putget_n = putget_ok = 0
    amendments: dict[str, dict] = {}
    for bn, m, e, (txs, layout) in accepted_pairs:
        if e[0] == "move":
            continue
        intended = apply_view_edit(get_view(m), e)
        if intended is None:
            continue
        applied_model = safe_put(m, txs)
        putget_n += 1
        if applied_model is None:
            continue  # counted by L9; a proposal that cannot apply passes nothing
        view, after = get_view(m), get_view(applied_model)
        added = (after[1] - view[1]) - (intended[1] - view[1])
        removed = (view[1] - after[1]) - (view[1] - intended[1])
        states = (after[0] - view[0]) - (intended[0] - view[0])
        allowed = set().union(*(AMENDMENT_POLICY.get(t.split(":", 1)[0], set()) for t in txs)) if txs else set()
        exact = after[1] == (intended[1] - removed) | added
        bounded = all(edge[0] in allowed for edge in added | removed) and not states
        putget_ok += exact and bounded
        if txs:
            amendments[f"{bn}:{'/'.join(map(str, e))}"] = {
                "amended_edges_added": sorted(list(x) for x in added),
                "amended_edges_removed": sorted(list(x) for x in removed),
                "amended_states_added": sorted(states)}
    r["L2_putget_modulo_amendments"] = {"pairs": putget_n, "pass": putget_ok}
    r["L2_amendments_reported_to_human"] = {k: amendments[k] for k in sorted(amendments)}

    # L3 conditional PutPut: two edits of the same slot; the second overrides the first.
    pp_n = pp_ok = 0
    for m in bases.values():
        for e1, e2 in itertools.product([("retarget", "Reject", "Submitted"), ("retarget", "Reject", "Recommended")], repeat=2):
            try:
                k1, r1 = tr(m, e1)
                m1 = safe_put(m, r1[0]) if k1 == "Accepted" else None
                k2, r2 = tr(m1, e2) if m1 is not None else ("Rejected", ((), ()))
                lhs = safe_put(m1, r2[0]) if (m1 is not None and k2 == "Accepted") else None
                k3, r3 = tr(m, e2)
                rhs = safe_put(m, r3[0]) if k3 == "Accepted" else None
            except (DomainError, TypeError, ValueError):
                continue
            if lhs is None or rhs is None:
                continue
            pp_n += 1
            pp_ok += (sem(lhs) == sem(rhs))
    r["L3_conditional_putput"] = {"pairs": pp_n, "pass": pp_ok}

    # L4 layout independence: a move never changes the semantic hash; the layout complement carries it.
    mv_n = mv_ok = 0
    for m in bases.values():
        for s in m.states:
            kind, res = tr(m, ("move", s, 5, 6))
            mv_n += 1
            mv_ok += (kind == "Accepted" and res[0] == () and res[1] == ((s, 5, 6),))
    r["L4_layout_independence"] = {"pairs": mv_n, "pass": mv_ok}

    # L5 order: permutation invariance of the batch translator, and how often naive input-order application fails.
    batch_edits = [("add_edge", "Recommend", "Submitted", "Recommended"), ("retarget", "Reject", "Recommended"),
                   ("move", "Draft", 1, 2)]
    results = set()
    naive_fail = naive_total = 0
    for perm in itertools.permutations(batch_edits):
        kind, res = translate_batch(base, list(perm), tr)
        results.add(json.dumps([kind, res], sort_keys=True))
        cur, failed = base, False
        for e in perm:
            k, rs = tr(cur, e)
            try:
                cur = put(cur, rs[0]) if k == "Accepted" else cur
                failed |= (k == "Rejected")
            except DomainError:
                failed = True
                break
        naive_total += 1
        naive_fail += failed
    r["L5_order"] = {"permutations": naive_total, "distinct_batch_translator_results": len(results),
                     "naive_input_order_failures": naive_fail}

    # L2b PutGetPut-shaped stability (Foster et al. discuss the PutGetPut weakening of Mu et al. as the standard
    # relaxation of PutGet): replaying an accepted edit on its own result is a no-op. Non-vacuous under amendments,
    # because the result already contains the kernel's completion of the edit.
    pgp_n = pgp_ok = 0
    for bn, m, e, (txs, layout) in accepted_pairs:
        if e[0] == "move":
            continue
        after_m = safe_put(m, txs)
        if after_m is None:
            continue
        pgp_n += 1
        k2, r2 = tr(after_m, e)
        pgp_ok += (k2 == "Accepted" and r2 == ((), ()))
    r["L2b_putgetput_replay_is_noop"] = {"pairs": pgp_n, "pass": pgp_ok}

    # L6 non-commutation is typed: two different edits of one slot are refused in a batch, never silently ordered.
    l6 = [([("retarget", "Reject", "Submitted"), ("retarget", "Reject", "Recommended")], "Rejected"),
          ([("move", "Draft", 1, 2), ("move", "Draft", 3, 4)], "Rejected"),
          ([("move", "Draft", 1, 2), ("move", "Draft", 1, 2)], "Accepted"),  # identical duplicates are one edit
          ([("move", "Draft", 1, 2), ("move", "Submitted", 3, 4)], "Accepted")]  # disjoint slots commute
    r["L6_typed_non_commutation"] = {"pairs": len(l6), "pass": sum(translate_batch(cand, b, tr)[0] == want for b, want in l6),
                                     "domain": "4 hand-written fixture batches on the candidate base; no negative oracle"}

    # L10 identity by id: an edit of an existing element names it by id; an unknown id or a label variant is refused.
    l10 = [("move", "Nowhere", 1, 1), ("move", "draft", 1, 1), ("move", "Draft ", 1, 1)]
    r["L10_identity_by_id"] = {"pairs": len(l10) * len(bases), "pass": sum(
        tr(m, e) == ("Rejected", "UNKNOWN_NODE") for m in bases.values() for e in l10)}

    # L8 no authority and purity: translate never mutates the model (frozen contracts) and returns only proposals.
    before = [sem(m) for m in bases.values()]
    for m in bases.values():
        for e in alphabet:
            tr(m, e)
    r["L8_purity_semantic_hashes_unchanged"] = before == [sem(m) for m in bases.values()]
    return r


def _law_failures(r: dict) -> list[str]:
    """Names of laws in a lens-law report that did not fully hold."""
    bad = []
    for k, v in r.items():
        if isinstance(v, dict) and "pass" in v:
            n = v.get("noop_pairs", v.get("pairs", v.get("accepted")))
            if v["pass"] != n:
                bad.append(k)
    if r.get("L8_purity_semantic_hashes_unchanged") is False:
        bad.append("L8_purity_semantic_hashes_unchanged")
    if r["L5_order"]["distinct_batch_translator_results"] != 1:
        bad.append("L5_order")
    return sorted(bad)


def lens_negative_controls() -> dict:
    """The law suite must fail on deliberately broken translators (negative oracle), and pass on the reference."""

    def bad_getput(m: Workflow, e: tuple) -> tuple[str, Any]:  # emits a transaction for a no-op edit
        kind, res = translate(m, e)
        if kind == "Accepted" and res == ((), ()) and e[0] == "add_edge":
            return "Accepted", (("enable_recommendation",), ())
        return kind, res

    def bad_putget(m: Workflow, e: tuple) -> tuple[str, Any]:  # retargets the wrong slot
        if e == ("retarget", "Reject", "Recommended"):
            return translate(m, ("retarget", "Reject", "Submitted"))
        return translate(m, e)

    def bad_layout(m: Workflow, e: tuple) -> tuple[str, Any]:  # leaks a layout move into the semantic model
        if e[:1] == ("move",) and len(e) == 4 and e[1] in m.states:
            return "Accepted", (("enable_recommendation",), ((e[1], e[2], e[3]),))
        return translate(m, e)

    def bad_unapplicable(m: Workflow, e: tuple) -> tuple[str, Any]:  # skips the dry run: accepts what the kernel refuses
        if e[:1] == ("retarget",) and len(e) == 3 and e[2] == "Recommended":
            return "Accepted", (("set_rejection_source:Recommended",), ())
        return translate(m, e)

    out: dict[str, Any] = {"status": "MEASURED", "reference_failures": _law_failures(lens_laws_on_kernel_alphabet(translate))}
    for name, fn in (("bad_getput", bad_getput), ("bad_putget", bad_putget), ("bad_layout", bad_layout),
                     ("bad_unapplicable", bad_unapplicable)):
        out[name + "_detected_by"] = _law_failures(lens_laws_on_kernel_alphabet(fn))
    return out


# --------------------------------------------------------------------------------------------------
# C. Complement preservation of the okf lane's generated-block rewriter (read-only, via ast).
# --------------------------------------------------------------------------------------------------
def okf_complement_preservation() -> dict:
    src_path = ROOT.parent / "okf" / "quality" / "okf" / "pages.py"
    if not src_path.exists():
        return not_run("okf lane worktree not found next to this worktree")
    src = src_path.read_bytes().decode("utf-8")
    tree = ast.parse(src)
    keep = [n for n in tree.body
            if (isinstance(n, ast.Assign) and any(getattr(t, "id", None) == "_BLOCK" for t in n.targets))
            or (isinstance(n, ast.FunctionDef) and n.name in ("block", "render_body"))]
    if len(keep) != 3:
        return not_run("okf pages.py does not define _BLOCK, block and render_body in the expected shape")
    ns: dict[str, Any] = {"re": re, "PageSpec": object}
    exec(compile("from __future__ import annotations\n" + ast.unparse(ast.Module(body=list[ast.stmt](keep), type_ignores=[])), "okf_pages_subset", "exec"), ns)

    class Spec:
        title = "T"
        seed = ""

    blocks = {"facts": "F1", "links": "L1"}

    def page(notes: str) -> str:
        return ("# T\n\n<!-- okf:generated:begin facts -->\nOLD\n<!-- okf:generated:end facts -->\n\n## Notes\n\n"
                + notes + "\n\n<!-- okf:generated:begin links -->\nX\n<!-- okf:generated:end links -->\n")

    res: dict[str, Any] = {"status": "MEASURED", "pages_py_sha256_of_okf_working_copy": hashlib.sha256(src.encode("utf-8")).hexdigest(),
                           "note": "digest of the okf worktree's working copy at run time; it moves whenever the okf lane edits the file, "
                                   "so it is not stable across time (compare the committed blob id instead)", "cases": {}}
    for name, notes in (("plain_notes", "one\n\ntwo"), ("three_blank_lines_in_prose", "a\n\n\n\nb"),
                        ("three_blank_lines_in_fence", "```\na\n\n\n\nb\n```")):
        out = ns["render_body"](Spec(), blocks, page(notes))
        again = ns["render_body"](Spec(), blocks, out)
        res["cases"][name] = {"human_text_preserved": notes in out, "idempotent": out == again,
                              "generated_regions_replaced": "F1" in out and "OLD" not in out}
    return res


CHECKS: dict[str, Any] = {
    "keyed_merge_laws": keyed_merge_laws,
    "git_line_merge_vs_keyed": git_line_merge_vs_keyed,
    "non_confluent_invariants": non_confluent_invariants,
    "lens_laws_on_kernel_alphabet": lens_laws_on_kernel_alphabet,
    "lens_negative_controls": lens_negative_controls,
    "okf_complement_preservation": okf_complement_preservation,
}


def report(names: list[str] | None = None) -> dict:
    return {"schema": "eija.weave.consistency-checks.v1", **{n: CHECKS[n]() for n in sorted(names or CHECKS)}}


if __name__ == "__main__":
    wanted = sys.argv[1:] or None
    unknown = [n for n in (wanted or []) if n not in CHECKS]
    if unknown:
        sys.exit("unknown check(s): " + ", ".join(unknown) + "; choose from " + ", ".join(sorted(CHECKS)))
    sys.stdout.buffer.write((json.dumps(report(wanted), sort_keys=True, indent=1, ensure_ascii=True) + "\n").encode("ascii"))
