"""Reproducible checks behind docs/weave/design/agent-interface-and-context-packs.md.

Every check reports MEASURED (it ran; numbers are real for the stated synthetic or repository domain),
PREDICTION (arithmetic on stated assumptions, nothing observed) or NOT_RUN (a prerequisite is missing).
Nothing here shows that the agent interface helps an agent or a person: that needs the evaluation in
section 10 of the design document.

Reuse, not duplication. Ranking (fixed-point personalised PageRank), budgeted selection and the pass^k
estimator are the impact-ranking aspect's reference (graph/bench/impact_math_reference.py); this file
imports them and adds only what is specific to the agent interface: the pack layer, the response
envelope hashing, the replay hash chain, the sample-size arithmetic, the rename probe and the kernel
dry-run example. Hashing follows the identity aspect (graph/schema/identity-vectors.json): "sha256:" +
SHA-256 over ASCII domain tag, NUL and the RFC 8785 subset serialisation.

Stdlib only. The kernel is imported read-only as a reference oracle (rule R9: benches and tests may
import ``eija_studio``; the eventual ``eijagraph`` runtime must not). Output is canonical ASCII JSON
(sorted keys, no timestamps, no wall clock), so two runs on one platform are byte-identical.

    python graph/bench/agent_interface_checks.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import math
import re
import sys
import tokenize
from fractions import Fraction
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

MASK64 = (1 << 64) - 1


def not_run(reason: str) -> dict:
    return {"status": "NOT_RUN", "reason": reason}


def load_reference():
    """The impact-ranking aspect's reference module, or None (checks that need it report NOT_RUN)."""
    path = BENCH / "impact_math_reference.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("impact_math_reference", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("impact_math_reference", module)
    spec.loader.exec_module(module)
    return module


class SplitMix64:
    """Tiny integer PRNG, so seeded samples are identical on every platform and Python version."""

    def __init__(self, seed: int) -> None:
        self.s = seed & MASK64

    def next(self) -> int:
        self.s = (self.s + 0x9E3779B97F4A7C15) & MASK64
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        return z ^ (z >> 31)

    def below(self, n: int) -> int:
        return self.next() % n

    def shuffle(self, items: list) -> list:
        items = list(items)
        for i in range(len(items) - 1, 0, -1):
            j = self.below(i + 1)
            items[i], items[j] = items[j], items[i]
        return items


# ---------------------------------------------------------------------------------------------------
# Canonical bytes: RFC 8785 subset (strings, safe integers, booleans, null; no floats) and dhash.
# ---------------------------------------------------------------------------------------------------
TAG = re.compile(r"eija\.weave\.[a-z0-9.-]+\.v[0-9]+")


def jcs_subset(value) -> str:
    """RFC 8785 for the restricted subset. Keys are ordered by UTF-16 code units (RFC 8785 section 3.2.3)."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        if abs(value) > 2**53 - 1:
            raise ValueError("integer outside the safe range")
        return str(value)
    if isinstance(value, float):
        raise TypeError("floats are not part of the committed subset")
    if isinstance(value, str):
        value.encode("utf-8")  # rejects lone surrogates
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(jcs_subset(v) for v in value) + "]"
    if isinstance(value, dict):
        keys = sorted(value, key=lambda k: k.encode("utf-16-be"))
        return "{" + ",".join(jcs_subset(k) + ":" + jcs_subset(value[k]) for k in keys) + "}"
    raise TypeError(f"unsupported type {type(value).__name__}")


def dhash(tag: str, value) -> str:
    """Identity aspect's convention: 'sha256:' + SHA-256(ascii tag, NUL, JCS bytes). The JSON is self-delimiting."""
    if not TAG.fullmatch(tag):
        raise ValueError(f"bad domain tag {tag!r}")
    return "sha256:" + hashlib.sha256(tag.encode("ascii") + b"\x00" + jcs_subset(value).encode("utf-8")).hexdigest()


def identity_vector_conformance() -> dict:
    """Does this file's writer reproduce the identity aspect's golden vectors byte for byte?"""
    path = ROOT / "graph" / "schema" / "identity-vectors.json"
    if not path.is_file():
        return not_run("graph/schema/identity-vectors.json not present")
    vectors = json.loads(path.read_text(encoding="utf-8"))
    ok_jcs = ok_hash = 0
    for v in vectors["jcs"]:
        ok_jcs += jcs_subset(v["input"]) == v["jcs"]
        ok_hash += dhash("eija.weave.node.v1", v["input"]) == v["eija.weave.node.v1"]
    rejected = 0
    for bad in (1.0, 2**53, "\ud800"):
        try:
            jcs_subset({"a": bad})
        except (TypeError, ValueError):
            rejected += 1
    return {"status": "MEASURED", "domain": f"{len(vectors['jcs'])} golden vectors in graph/schema/identity-vectors.json",
            "jcs_bytes_equal": [ok_jcs, len(vectors["jcs"])], "node_hash_equal": [ok_hash, len(vectors["jcs"])],
            "must_reject_cases_rejected": [rejected, 3]}


# ---------------------------------------------------------------------------------------------------
# 1. pass^k and pass@k estimators (exact arithmetic; pass^k is the reference's pass_hat_k).
# ---------------------------------------------------------------------------------------------------
def passk_estimator_exactness(n: int = 6) -> dict:
    """For c ~ Binomial(n, q): E[C(c,k)/C(n,k)] = q^k exactly (unbiased pass^k), E[1 - C(n-c,k)/C(n,k)] =
    1 - (1-q)^k (unbiased pass@k), and the plug-in (c/n)^k is biased upward for 0 < q < 1 and k >= 2.
    Exact rational enumeration over a grid of q, so there is no sampling error."""
    ref = load_reference()
    if ref is None:
        return not_run("graph/bench/impact_math_reference.py not present")
    grid = sorted({Fraction(a, b) for b in (2, 3, 5, 10) for a in range(1, b)})
    unbiased_passk = unbiased_passat = True
    plugin_bias = []
    for q in grid:
        pmf = [comb(n, c) * q**c * (1 - q) ** (n - c) for c in range(n + 1)]
        for k in range(1, n + 1):
            unbiased_passk &= sum(p * ref.pass_hat_k(n, c, k) for c, p in enumerate(pmf)) == q**k
            unbiased_passat &= sum(p * (1 - Fraction(comb(n - c, k), comb(n, k))) for c, p in enumerate(pmf)) == 1 - (1 - q) ** k
            if k >= 2:
                plugin_bias.append(sum(p * Fraction(c, n) ** k for c, p in enumerate(pmf)) - q**k)
    q, n8, k4 = Fraction(1, 2), 8, 4
    pmf8 = [comb(n8, c) * q**c * (1 - q) ** (n8 - c) for c in range(n8 + 1)]
    bias = sum(p * Fraction(c, n8) ** k4 for c, p in enumerate(pmf8)) - q**k4
    return {"status": "MEASURED", "domain": f"n={n}, k=1..n, {len(grid)} rational q values, exact Fractions",
            "unbiased_pass_hat_k": bool(unbiased_passk), "unbiased_pass_at_k": bool(unbiased_passat),
            "plugin_p_hat_pow_k_always_above_truth": all(b > 0 for b in plugin_bias),
            "plugin_bias_at_q_1_2_n_8_k_4": str(bias)}


def passk_two_agents() -> dict:
    """Same pass@1, very different pass^k: 10 tasks x n=8 trials each."""
    ref = load_reference()
    if ref is None:
        return not_run("graph/bench/impact_math_reference.py not present")
    n, tasks = 8, 10
    agent_a = [6] * tasks                       # 6 of 8 on every task
    agent_b = [8] * 7 + [4] + [0] * 2           # perfect on 7, coin-flip on 1, never on 2

    def curve(cs):
        return {str(k): str(sum(ref.pass_hat_k(n, c, k) for c in cs) / len(cs)) for k in (1, 2, 4, 8)}
    return {"status": "MEASURED", "domain": "hand-built success counts, exact Fractions",
            "trials_per_task": n, "tasks": tasks, "successes_a": agent_a, "successes_b": agent_b,
            "pass_hat_k_a": curve(agent_a), "pass_hat_k_b": curve(agent_b),
            "total_success_rate_a": str(Fraction(sum(agent_a), n * tasks)),
            "total_success_rate_b": str(Fraction(sum(agent_b), n * tasks))}


# ---------------------------------------------------------------------------------------------------
# 2. Number of tasks needed for a paired with/without comparison (PREDICTION: arithmetic on assumptions).
# ---------------------------------------------------------------------------------------------------
def tasks_needed_table() -> dict:
    """Var(mean paired difference) = (sigma_delta^2 + (v0 + v1) / n) / T, where sigma_delta^2 is the variance
    over tasks of the true per-task difference q1_t - q0_t and v_a = E_t[q_a,t (1 - q_a,t)] is the within-task
    Bernoulli variance of arm a. Normal approximation; two-sided alpha = 0.05, power 0.8:
    T >= (z_{0.975} + z_{0.8})^2 * (sigma_delta^2 + (v0 + v1)/n) / delta^2."""
    z = 1.959964 + 0.841621
    delta = 0.10
    v_sum = 0.38  # assumption: base rate 0.5, between-task variance of q = 0.06, so v = 0.25 - 0.06 = 0.19 per arm
    rows = []
    for sigma in (0.05, 0.15, 0.30):
        for n in (1, 3, 5, 10):
            t = math.ceil(z**2 * (sigma**2 + v_sum / n) / delta**2)
            rows.append({"sigma_delta": sigma, "trials_per_task_n": n, "tasks_needed": t})
    mde = []
    for t in (20, 30, 50, 78, 150, 300, 866):
        sigma, n = 0.15, 5
        mde.append({"tasks": t, "trials_per_task_n": n, "sigma_delta": sigma,
                    "minimum_detectable_difference": round(z * math.sqrt((sigma**2 + v_sum / n) / t), 4)})
    return {"status": "PREDICTION", "assumptions": {"delta": delta, "z_sum": round(z, 4), "v0_plus_v1": v_sum,
            "model": "normal approximation; iid trials given task; tasks exchangeable"}, "rows": rows,
            "minimum_detectable_difference_rows": mde}


# ---------------------------------------------------------------------------------------------------
# 3. Context packs: mandatory obligations + the reference's ranking and selection; identity under shuffles.
# ---------------------------------------------------------------------------------------------------
EDGE_TYPES = ("realises", "verifies", "names", "depends_on", "documents")
MANDATORY_EDGE = frozenset({"verifies", "names"})


def synthetic_graph(seed: int = 7, n: int = 300) -> tuple[list[str], list[tuple[str, str, str]], dict[str, int]]:
    rng = SplitMix64(seed)
    nodes = [f"repo://n/{i:03d}" for i in range(n)]
    edges = set()
    for i in range(n):
        for _ in range(1 + rng.below(4)):
            j = rng.below(n)
            if j != i:
                edges.add((nodes[i], EDGE_TYPES[rng.below(len(EDGE_TYPES))], nodes[j]))
    cost = {u: 40 + int(dhash("eija.weave.bench-cost.v1", u)[7:], 16) % 200 for u in nodes}
    return nodes, sorted(edges), cost


def arc_weights(edges) -> dict[tuple[str, str], int]:
    """Default relevance weights of the ranking aspect: forward 2, reverse 1 (each link flows source to target)."""
    w: dict[tuple[str, str], int] = {}
    for a, _, b in edges:
        w[(a, b)] = w.get((a, b), 0) + 2
        w[(b, a)] = w.get((b, a), 0) + 1
    return w


def ppr_float(nodes, arcs, seeds, iters=78, alpha=0.2) -> dict[str, float]:
    """The obvious float power iteration over `arcs` in the given order; used only to test whether float bit
    differences change what a pack selects. Same iteration count and teleport as the integer reference."""
    out: dict[str, list[tuple[str, float]]] = {u: [] for u in nodes}
    for (u, v), w in arcs:
        out[u].append((v, float(w)))
    seed_p = {u: 1.0 / len(seeds) for u in seeds}
    x = dict.fromkeys(nodes, 0.0)
    x.update(seed_p)
    for _ in range(iters):
        y = dict.fromkeys(nodes, 0.0)
        tele = 0.0
        for u in nodes:
            if x[u] == 0.0:
                continue
            cont = x[u] * (1 - alpha)
            tele += x[u] - cont
            tot = sum(w for _, w in out[u])
            if tot:
                for v, w in out[u]:
                    y[v] += cont * w / tot
            else:
                tele += cont
        for s in seeds:
            y[s] += tele * seed_p[s]
        x = y
    return x


def build_pack(nodes, edges, cost, seeds, budget, ranker="int") -> dict:
    """Mandatory obligations first (seeds and one-hop neighbours over MANDATORY_EDGE), then the reference's
    budgeted selection over the rest of the two-hop neighbourhood. Nothing is dropped silently."""
    ref = load_reference()
    adj: dict[str, set[str]] = {u: set() for u in nodes}
    mand: dict[str, set[str]] = {u: set() for u in nodes}
    for a, t, b in edges:
        adj[a].add(b)
        adj[b].add(a)
        if t in MANDATORY_EDGE:
            mand[a].add(b)
            mand[b].add(a)
    seed_set = set(seeds)
    mandatory = set(seed_set)
    for s in seed_set:
        mandatory |= mand[s]
    hop1 = set().union(*(adj[s] for s in seed_set)) | seed_set
    hop2 = set().union(*(adj[u] for u in hop1)) | hop1
    weights = arc_weights(edges)
    if ranker == "int":
        score = ref.ppr_int(nodes, weights, dict.fromkeys(seed_set, 1))["ppm"]
    else:  # float, arc order = dict insertion order
        fl = ppr_float(nodes, list(weights.items()), sorted(seed_set))
        score = {u: int(fl[u] * 1_000_000 + 0.5) for u in nodes}
    candidates = {u: (score[u], cost[u]) for u in hop2 - mandatory if score[u] > 0}
    sel = ref.select_context({u: cost[u] for u in mandatory}, candidates, budget)
    if sel["status"] != "OK":
        return {"error": "BUDGET_TOO_SMALL", "needed": sel["needed"], "budget": budget}
    chosen = set(sel["chosen"])
    items = [{"id": u, "role": "mandatory", "cost": cost[u], "score_ppm": score[u]}
             for u in sorted(mandatory, key=lambda u: (u not in seed_set, u))]
    items += [{"id": u, "role": "ranked", "cost": cost[u], "score_ppm": score[u]}
              for u in sorted(chosen, key=lambda u: (-score[u], u))]
    omitted = sorted((hop2 - mandatory) - chosen)
    return {"seeds": sorted(seed_set), "budget": budget, "spent": sum(i["cost"] for i in items), "items": items,
            "omitted_count": len(omitted), "complete": not omitted}


def context_pack_determinism(shuffles: int = 40) -> dict:
    ref = load_reference()
    if ref is None:
        return not_run("graph/bench/impact_math_reference.py not present")
    nodes, edges, cost = synthetic_graph()
    seeds = [nodes[3], nodes[101], nodes[250]]
    budget = 2400
    pack_hashes, float_items = set(), set()
    rng = SplitMix64(99)
    first = None
    for _ in range(shuffles):
        n2, e2 = rng.shuffle(nodes), rng.shuffle(edges)
        pack = build_pack(n2, e2, cost, seeds, budget)
        first = first or pack
        pack_hashes.add(dhash("eija.weave.pack.v1", pack))
        fp = build_pack(n2, e2, cost, seeds, budget, ranker="float")
        float_items.add(tuple(it["id"] for it in fp["items"]))
    content = {u: dhash("eija.weave.bench-content.v1", u) for u in nodes}
    pack_ids = [it["id"] for it in first["items"]]
    victim = pack_ids[len(pack_ids) // 2]
    content2 = dict(content)
    content2[victim] = dhash("eija.weave.bench-content.v1", [victim, "edited"])
    changed = [u for u in pack_ids if content[u] != content2[u]]
    small = build_pack(nodes, edges, cost, seeds, 100)
    return {"status": "MEASURED", "domain": f"synthetic graph {len(nodes)} nodes / {len(edges)} typed edges, seed 7; {shuffles} shuffles of node and edge order; ranking and selection from the impact-ranking reference",
            "distinct_packs": len(pack_hashes),
            "distinct_item_sequences_if_the_ranking_were_float": len(float_items),
            "pack_items": len(pack_ids), "pack_spent_of_budget": [first["spent"], budget], "pack_complete": first["complete"],
            "omitted_count": first["omitted_count"], "verify_flags_only_changed_item": changed == [victim],
            "budget_too_small_reports_needed_cost": small.get("error") == "BUDGET_TOO_SMALL" and small["needed"] > 100}


# ---------------------------------------------------------------------------------------------------
# 4. Replay log: hash chain, tamper detection, key-order independence, domain separation.
# ---------------------------------------------------------------------------------------------------
GENESIS = "sha256:" + "0" * 64
EVENT_TAG = "eija.weave.agent-run-event.v1"


def event_hash(prev: str, event: dict) -> str:
    return dhash(EVENT_TAG, {"prev": prev, "event": event})


def chain_head(events: list[dict]) -> tuple[str, list[str]]:
    prev, hashes = GENESIS, []
    for e in events:
        prev = event_hash(prev, e)
        hashes.append(prev)
    return prev, hashes


def verify_chain(events: list[dict], recorded: list[str], head: str) -> int | None:
    """Index of the first event whose recorded hash disagrees, -1 for a head or length mismatch, None if valid."""
    prev = GENESIS
    for i, e in enumerate(events):
        prev = event_hash(prev, e)
        if i >= len(recorded) or recorded[i] != prev:
            return i
    return None if (prev == head and len(recorded) == len(events)) else -1


def run_log_chain(length: int = 200) -> dict:
    rng = SplitMix64(5)
    kinds = ("tool_call", "tool_result", "model_message", "file_edit", "proposal")
    events = []
    for i in range(length):
        events.append({"seq": i, "kind": kinds[rng.below(len(kinds))], "sha256": dhash("eija.weave.bench-blob.v1", i),
                       "note": ["ascii", "\U0001F600 astral", "\uff5e bmp"][rng.below(3)],
                       "\U0001F600": i, "\uff5e": i + 1})
    head, hashes = chain_head(events)
    edit_detected = 0
    for i in range(length):
        bad = [dict(e) for e in events]
        bad[i]["seq"] = bad[i]["seq"] + 1000
        edit_detected += verify_chain(bad, hashes, head) == i
    swap_detected = sum(verify_chain([*events[:i], events[i + 1], events[i], *events[i + 2:]], hashes, head) == i
                        for i in range(length - 1))
    trunc = verify_chain(events[:-1], hashes, head) == -1
    same_head = chain_head([dict(reversed(list(e.items()))) for e in events])[0] == head
    naive = hashlib.sha256(b"a" + b"bc").hexdigest() == hashlib.sha256(b"ab" + b"c").hexdigest()
    sep = dhash("eija.weave.bench-domain.v1", ["a", "bc"]) == dhash("eija.weave.bench-domain.v1", ["ab", "c"])
    cross = dhash("eija.weave.node.v1", {"k": 1}) == dhash("eija.weave.edge.v1", {"k": 1})
    order = jcs_subset({"\U0001F600": 1, "\uff5e": 2})
    return {"status": "MEASURED", "domain": f"synthetic {length}-event chain incl. astral and BMP keys",
            "single_field_edits_detected_at_the_edited_index": [edit_detected, length],
            "adjacent_swaps_detected": [swap_detected, length - 1], "truncation_detected": trunc,
            "dict_key_order_does_not_change_head": same_head,
            "naive_concatenation_collides": naive, "json_structured_domain_hash_collides": sep,
            "same_record_under_two_domain_tags_collides": cross,
            "jcs_orders_astral_before_fullwidth_tilde": order.index("\U0001F600") < order.index("\uff5e"),
            "python_sorted_by_code_point_disagrees": sorted(["\U0001F600", "\uff5e"]) == ["\uff5e", "\U0001F600"]}


def replay_of_tool_calls() -> dict:
    """A toy pure tool (impact via the kernel closure) recorded then replayed against the same and a drifted snapshot."""
    from eija_studio.domain.impact import closure
    nodes, edges, _ = synthetic_graph(seed=11, n=120)

    def snapshot(es):
        g: dict[str, list[str]] = {}
        for a, _, b in es:
            g.setdefault(a, []).append(b)
        return g, dhash("eija.weave.bench-root.v1", sorted([list(e) for e in es]))
    g, root = snapshot(edges)
    calls = [{"roots": [nodes[i]], "budget": 25} for i in range(0, 120, 3)]

    def run(g, root, c):
        r = closure(g, c["roots"], c["budget"])
        return {"graph_root": root, "affected": r["affected"], "complete": r["complete"], "frontier": r["frontier"]}
    recorded = [dhash("eija.weave.mcp-response.v1", run(g, root, c)) for c in calls]
    same = sum(dhash("eija.weave.mcp-response.v1", run(g, root, c)) == rec for c, rec in zip(calls, recorded, strict=False))
    g2, root2 = snapshot(edges[:-1])
    differ_with_root = sum(dhash("eija.weave.mcp-response.v1", run(g2, root2, c)) != rec for c, rec in zip(calls, recorded, strict=False))
    differ_content = sum(run(g2, root, c) != run(g, root, c) for c in calls)
    return {"status": "MEASURED", "domain": "40 recorded closure calls on a 120-node synthetic graph, kernel impact.closure as the tool",
            "replay_same_snapshot_equal": [same, len(calls)],
            "graph_root_changes_when_one_edge_is_removed": root != root2,
            "responses_that_differ_after_drift_because_they_carry_graph_root": differ_with_root,
            "responses_whose_affected_set_actually_changed": differ_content}


def sqlite_instruction_budget() -> dict:
    """A deterministic resource limit for a free-form read-only query: SQLite VM instructions counted by
    Connection.set_progress_handler, not seconds. Same query, same data, same SQLite: same count?"""
    import sqlite3
    nodes, edges, _ = synthetic_graph(seed=7, n=300)
    query = ("WITH RECURSIVE r(id) AS (SELECT ? UNION SELECT e.dst FROM edge e JOIN r ON e.src = r.id) "
             "SELECT id FROM r ORDER BY id")

    def run(edge_order, limit=None):
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE edge(src TEXT, type TEXT, dst TEXT)")
        con.execute("CREATE INDEX ix ON edge(src)")
        con.executemany("INSERT INTO edge VALUES (?,?,?)", edge_order)
        calls = [0]

        def cb():
            calls[0] += 1
            return 1 if limit is not None and calls[0] >= limit else 0
        con.set_progress_handler(cb, 100)
        try:
            con.execute(query, (nodes[0],)).fetchall()
            aborted = False
        except sqlite3.DatabaseError:
            aborted = True
        con.close()
        return calls[0], aborted
    same_order = {run(edges)[0] for _ in range(5)}
    rng = SplitMix64(1)
    shuffled = {run(rng.shuffle(edges))[0] for _ in range(10)}
    full_calls = run(edges)[0]
    aborted = run(edges, limit=max(1, full_calls // 2))[1]
    return {"status": "MEASURED", "domain": "recursive-CTE reachability on the 300-node synthetic graph, handler every 100 VM instructions, sqlite3 " + sqlite3.sqlite_version,
            "handler_calls_same_insertion_order_5_runs_distinct": len(same_order),
            "handler_calls_10_shuffled_insertion_orders_distinct": len(shuffled),
            "aborts_when_half_the_budget_is_allowed": aborted}


# ---------------------------------------------------------------------------------------------------
# 5. Free-form text replace versus syntax-aware candidates, on this repository's src/.
# ---------------------------------------------------------------------------------------------------
def rename_probe(names=("closure", "fingerprint", "receipt", "impact", "verify", "approve")) -> dict:
    files = sorted((ROOT / "src" / "eija_studio").rglob("*.py"), key=lambda p: p.as_posix())
    tree = dhash("eija.weave.bench-tree.v1", [[p.relative_to(ROOT).as_posix(), p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")] for p in files])
    rows = {}
    for name in names:
        pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])")
        text = code = attr = 0
        for p in files:
            src = p.read_bytes().decode("utf-8").replace("\r\n", "\n")
            text += len(pat.findall(src))
            prev = None
            for tok in tokenize.generate_tokens(io.StringIO(src).readline):
                if tok.type == tokenize.NAME and tok.string == name:
                    code += 1
                    attr += prev is not None and prev.type == tokenize.OP and prev.string == "."
                if tok.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.COMMENT):
                    prev = tok
        rows[name] = {"word_boundary_text_matches": text, "code_name_tokens": code,
                      "in_strings_docstrings_comments": text - code, "code_tokens_after_dot": attr}
    return {"status": "MEASURED", "domain": f"{len(files)} files under src/eija_studio, CRLF folded; source tree hash {tree[7:23]}",
            "note": "A NAME token is a syntactic candidate, not a resolved reference; attribute names on other objects are still false candidates. Resolution needs scope and type information (LibCST metadata, SCIP).",
            "rows": rows}


# ---------------------------------------------------------------------------------------------------
# 6. The kernel's pure transaction dry run, as the worked example for `txn_dry_run`.
# ---------------------------------------------------------------------------------------------------
def kernel_dry_run_example() -> dict:
    from eija_studio.domain.impact import model_impact
    from eija_studio.domain.models import DomainError
    from eija_studio.domain.policy import apply_transaction, baseline, demo_candidate
    from eija_studio.domain.transactions import RetargetTransition
    base = baseline()
    out = {"baseline_semantic_hash": base.semantic_hash[:16], "baseline_actions": [t.action for t in base.transitions]}
    cand = demo_candidate()
    reject = next(t for t in base.transitions if t.action == "Reject")

    def retarget(state: str) -> RetargetTransition:
        return RetargetTransition(kind="retarget_transition", transition=reject.id, end="source", state=state)
    imp = model_impact(base, cand)
    out["enable_recommendation"] = {"verdict": "ACCEPTED", "candidate_semantic_hash": cand.semantic_hash[:16],
                                    "changed_actions": imp["changed_actions"], "closure_size": len(imp["affected"]),
                                    "complete": imp["complete"]}
    try:  # the drag: the rejection transition's source moved to the initial state
        apply_transaction(base, retarget(base.initial_state))
        out["drag_reject_source_to_initial"] = {"verdict": "ACCEPTED"}
    except DomainError as e:
        out["drag_reject_source_to_initial"] = {"verdict": "REJECTED", "code": e.code, "codes": (e.details or {}).get("codes")}
    cand2 = apply_transaction(cand, retarget(base.transitions[0].to_state))
    out["retarget_reject_source_after_meaning"] = {"verdict": "ACCEPTED", "changed_actions": model_impact(cand, cand2)["changed_actions"]}
    out["input_model_unchanged"] = base.semantic_hash[:16] == out["baseline_semantic_hash"]
    return {"status": "MEASURED", "domain": "kernel domain functions apply_transaction and model_impact on policy.baseline()", **out}


def run_all() -> dict:
    return {"schema": "eija.weave.agent-interface-checks.v1",
            "python_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
            "identity_vector_conformance": identity_vector_conformance(),
            "passk_estimator_exactness": passk_estimator_exactness(),
            "passk_two_agents": passk_two_agents(),
            "tasks_needed_table": tasks_needed_table(),
            "context_pack_determinism": context_pack_determinism(),
            "run_log_chain": run_log_chain(),
            "replay_of_tool_calls": replay_of_tool_calls(),
            "sqlite_instruction_budget": sqlite_instruction_budget(),
            "rename_probe": rename_probe(),
            "kernel_dry_run_example": kernel_dry_run_example()}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    sys.stdout.write(json.dumps(run_all(), sort_keys=True, indent=1, ensure_ascii=True) + "\n")
