"""Rule-language benchmark for the weave lint/compile design (ADR-0095).

Question: which rule language should graph-global rules be written in? The same four rules are written in four
ways and run on the same seeded synthetic graph:

* ``python``  plain Python over dict and set facts
* ``sql``     SQLite: ``NOT EXISTS`` anti-join, ``WITH RECURSIVE ... UNION`` (guarded by ``LIMIT``), ``GROUP BY``
* ``datalog`` a toy semi-naive Datalog evaluator with stratified negation (NOT Souffle: Souffle documents no
              Windows install, https://souffle-lang.github.io/install). It measures expressiveness and the cost of
              a pure-Python evaluation only, never the speed of a real Datalog engine.
* ``shacl``   pySHACL 0.40.1 over an rdflib graph, using SHACL Core for R1 and SHACL-SPARQL for R2 to R4
              (optional; missing packages report NOT_RUN, a run over the time budget reports NOT_RUN).

Rules (each is a real rule from graph/rules/catalogue.json in a simplified form):

* R1 requirement-without-verifier (WV-010): anti-join, no recursion
* R2 transitive-suspect (WV-005): recursion, positive
* R3 requirement-uncovered-transitively (WV-010 variant): recursion, then negation (stratified)
* R4 homonym-in-context (WV-017): self-join with aggregate

Outputs are sorted tuples. The deterministic section of the result file (agreement, sizes, source lines) is
byte-stable for a fixed seed; ``timings_ms`` and ``environment`` are MEASUREMENT of one machine and are kept in a
separate section on purpose. No wall-clock timestamp is written.

Usage (Windows or POSIX)::

    python graph/bench/rule_language_bench.py --out graph/bench/results/rule-language.json

Set TMP and TEMP to a folder inside the checkout before running (the reference PC's system temp is a slow HDD).
To include pySHACL: python -m venv .tmp/venv-rules, install pyshacl==0.40.1 into it and run this file with that interpreter.
Without pyshacl the SHACL column is reported NOT_RUN. The committed result was produced with pyshacl 0.40.1 and rdflib 7.6.0.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import platform
import random
import sqlite3
import statistics
import subprocess
import sys
import time
from collections import defaultdict, deque
from pathlib import Path

SEED = 20260929
RULES = ("R1", "R2", "R3", "R4")
SHACL_TIMEOUT_S = 300


# --------------------------------------------------------------------------------------------- data generator
def make_facts(n: int, seed: int = SEED) -> dict[str, list[tuple[str, ...]]]:
    """Deterministic synthetic facts. ``n`` requirements, 1.5n tests, n modules, n/2 terms."""
    rnd = random.Random(seed)
    reqs = [f"R{i:06d}" for i in range(n)]
    tests = [f"T{i:06d}" for i in range(int(n * 1.5))]
    mods = [f"M{i:06d}" for i in range(n)]
    terms = [f"W{i:06d}" for i in range(max(2, n // 2))]
    refines = {(reqs[i], reqs[rnd.randrange(0, i)]) for i in range(1, n) if rnd.random() < 0.7}
    for _ in range(max(1, n // 100)):  # back edges so cycles exist
        a, b = rnd.randrange(n), rnd.randrange(n)
        if a != b:
            refines.add((reqs[a], reqs[b]))
    verifies = {(t, reqs[rnd.randrange(n)]) for t in tests if rnd.random() < 0.9}
    depends: set[tuple[str, str]] = set()
    for i in range(1, n):
        for _ in range(2):
            j = max(0, i - 1 - int(rnd.expovariate(1 / 20)))
            depends.add((mods[i], mods[j]))
    for _ in range(max(1, n // 50)):  # back edges
        a, b = rnd.randrange(n), rnd.randrange(n)
        if a != b:
            depends.add((mods[a], mods[b]))
    changed = sorted(rnd.sample(mods[int(n * 0.8) : int(n * 0.98)], 3))  # closure covers a fraction of the modules
    contexts = ["Authoring", "Execution", "Assurance", "Governance", "Provider"]
    form_of: list[tuple[str, str]] = []  # (term, "context|form")
    for k, term in enumerate(terms):
        form_of.append((term, f"{contexts[k % 5]}|form{k:06d}"))
    for _ in range(max(1, len(terms) // 100)):  # injected homonyms: two terms share one (context, form) key
        a = rnd.randrange(len(terms))
        b = (a + 5) % len(terms)  # same context (period 5)
        form_of[b] = (terms[b], form_of[a][1])
    return {
        "requirement": [(r,) for r in sorted(reqs)],
        "module": [(m,) for m in sorted(mods)],
        "term": [(t,) for t in sorted(terms)],
        "verifies": sorted(verifies),
        "refines": sorted(refines),
        "depends_on": sorted(depends),
        "changed": [(m,) for m in changed],
        "form_of": sorted(form_of),
    }


# ------------------------------------------------------------------------------------------ python engine
def py_r1(f: dict) -> list[str]:
    verified = {r for _, r in f["verifies"]}
    return sorted(r for (r,) in f["requirement"] if r not in verified)


def py_r2(f: dict) -> list[str]:
    dependents = defaultdict(list)
    for x, y in f["depends_on"]:
        dependents[y].append(x)
    changed = {m for (m,) in f["changed"]}
    seen, queue = set(), deque(sorted(changed))
    while queue:
        y = queue.popleft()
        for x in sorted(dependents[y]):
            if x not in seen:
                seen.add(x)
                queue.append(x)
    return sorted(seen - changed)


def py_r3(f: dict) -> list[str]:
    parents = defaultdict(list)
    for child, parent in f["refines"]:
        parents[child].append(parent)
    covered = {r for _, r in f["verifies"]}
    queue = deque(sorted(covered))
    while queue:
        c = queue.popleft()
        for p in parents[c]:
            if p not in covered:
                covered.add(p)
                queue.append(p)
    return sorted(r for (r,) in f["requirement"] if r not in covered)


def py_r4(f: dict) -> list[str]:
    owners = defaultdict(set)
    for term, key in f["form_of"]:
        owners[key].add(term)
    return sorted(t for ts in owners.values() if len(ts) > 1 for t in ts)


# ----------------------------------------------------------------------------------------------- sql engine
SQL = {
    "R1": "SELECT r.id FROM requirement r WHERE NOT EXISTS (SELECT 1 FROM verifies v WHERE v.req = r.id) ORDER BY 1",
    "R2": """WITH RECURSIVE hit(id) AS (
  SELECT id FROM changed
  UNION
  SELECT d.src FROM depends_on d JOIN hit h ON d.dst = h.id
  LIMIT :guard)
SELECT id FROM hit WHERE id NOT IN (SELECT id FROM changed) ORDER BY 1""",
    "R3": """WITH RECURSIVE covered(id) AS (
  SELECT DISTINCT req FROM verifies
  UNION
  SELECT r.parent FROM refines r JOIN covered c ON r.child = c.id
  LIMIT :guard)
SELECT r.id FROM requirement r WHERE r.id NOT IN (SELECT id FROM covered) ORDER BY 1""",
    "R4": """SELECT term FROM form_of WHERE key IN
  (SELECT key FROM form_of GROUP BY key HAVING COUNT(DISTINCT term) > 1) ORDER BY 1""",
}


def sql_load(f: dict) -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    db.executescript(
        """CREATE TABLE requirement(id TEXT PRIMARY KEY);
        CREATE TABLE verifies(test TEXT, req TEXT); CREATE INDEX v_req ON verifies(req);
        CREATE TABLE refines(child TEXT, parent TEXT); CREATE INDEX r_child ON refines(child);
        CREATE TABLE depends_on(src TEXT, dst TEXT); CREATE INDEX d_dst ON depends_on(dst);
        CREATE TABLE changed(id TEXT PRIMARY KEY);
        CREATE TABLE form_of(term TEXT, key TEXT); CREATE INDEX f_key ON form_of(key);"""
    )
    db.executemany("INSERT INTO requirement VALUES (?)", f["requirement"])
    db.executemany("INSERT INTO verifies VALUES (?,?)", f["verifies"])
    db.executemany("INSERT INTO refines VALUES (?,?)", f["refines"])
    db.executemany("INSERT INTO depends_on VALUES (?,?)", f["depends_on"])
    db.executemany("INSERT INTO changed VALUES (?)", f["changed"])
    db.executemany("INSERT INTO form_of VALUES (?,?)", f["form_of"])
    return db


def sql_run(db: sqlite3.Connection, rule: str, guard: int) -> list[str]:
    rows = [r[0] for r in db.execute(SQL[rule], {"guard": guard} if ":guard" in SQL[rule] else {})]
    return rows


# -------------------------------------------------------------------------------------- toy datalog engine
DATALOG = {
    "R1": ["v(R) :- verifies(_, R).", "out(R) :- requirement(R), !v(R)."],
    "R2": [
        "hit(X) :- changed(Y), depends_on(X, Y).",
        "hit(X) :- hit(Y), depends_on(X, Y).",
        "out(X) :- hit(X), !changed(X).",
    ],
    "R3": [
        "cov(R) :- verifies(_, R).",
        "cov(P) :- cov(C), refines(C, P).",
        "out(R) :- requirement(R), !cov(R).",
    ],
    "R4": [
        "dup(K) :- form_of(A, K), form_of(B, K), A != B.",
        "out(T) :- form_of(T, K), dup(K).",
    ],
}
STRATA = {  # relation -> stratum, derived from negation dependencies (checked by `stratify`)
    "R1": [["v"], ["out"]],
    "R2": [["hit"], ["out"]],
    "R3": [["cov"], ["out"]],
    "R4": [["dup"], ["out"]],
}


def _parse(rule: str):
    head, body = rule.rstrip(".").split(":-")
    def atom(text: str):
        text = text.strip()
        if "!=" in text:
            a, b = (x.strip() for x in text.split("!="))
            return ("!=", (a, b), False)
        neg = text.startswith("!")
        text = text.lstrip("!")
        name, args = text.split("(")
        return (name.strip(), tuple(a.strip() for a in args.rstrip(")").split(",")), neg)
    atoms, depth, cur = [], 0, ""
    for ch in body:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            atoms.append(cur)
            cur = ""
        else:
            cur += ch
    atoms.append(cur)
    return atom(head), [atom(a) for a in atoms]


def _isvar(x: str) -> bool:
    return x[0].isupper() or x == "_"


def _match(atoms, rels, env, delta_at=None, delta=None):
    """Backtracking join over positive atoms left to right; negation and inequality checked once bound."""
    if not atoms:
        yield env
        return
    (name, args, neg), rest = atoms[0], atoms[1:]
    if name == "!=":
        if env[args[0]] != env[args[1]]:
            yield from _match(rest, rels, env, delta_at, delta)
        return
    if neg:
        probe = tuple(env[a] if _isvar(a) else a for a in args)
        if probe not in rels[name]:
            yield from _match(rest, rels, env, delta_at, delta)
        return
    source = delta if (delta_at is not None and len(atoms) == delta_at) else rels[name]
    bound = [(i, env[a]) for i, a in enumerate(args) if _isvar(a) and a != "_" and a in env] + [
        (i, a) for i, a in enumerate(args) if not _isvar(a)
    ]
    for tup in source.candidates(name, bound) if hasattr(source, "candidates") else source:
        new = dict(env)
        ok = True
        for i, a in enumerate(args):
            if a == "_":
                continue
            if _isvar(a):
                if a in new and new[a] != tup[i]:
                    ok = False
                    break
                new[a] = tup[i]
            elif a != tup[i]:
                ok = False
                break
        if ok:
            yield from _match(rest, rels, new, delta_at, delta)


class Rel(set):
    """Set of tuples with a lazily built first-bound-column index."""

    def __init__(self, it=()):
        super().__init__(it)
        self._idx: dict[int, dict] = {}
        self._size = -1

    def candidates(self, _name, bound):
        if not bound:
            return list(self)
        col, val = bound[0]
        if self._size != len(self):
            self._idx, self._size = {}, len(self)
        if col not in self._idx:
            idx = defaultdict(list)
            for t in self:
                idx[t[col]].append(t)
            self._idx[col] = idx
        return self._idx[col].get(val, [])


def datalog_run(rule: str, f: dict) -> list[str]:
    rels: dict[str, Rel] = defaultdict(Rel)
    for name, rows in f.items():
        rels[name] = Rel(rows)
    parsed = [_parse(r) for r in DATALOG[rule]]
    for stratum in STRATA[rule]:
        rules = [p for p in parsed if p[0][0] in stratum]
        # naive first pass, then semi-naive: each recursive rule re-evaluated with one atom bound to the delta
        delta: dict[str, Rel] = {s: Rel() for s in stratum}
        for (hname, hargs, _), body in rules:
            for env in _match(body, rels, {}):
                t = tuple(env[a] for a in hargs)
                if t not in rels[hname]:
                    rels[hname].add(t)
                    delta[hname].add(t)
        while any(delta.values()):
            new: dict[str, Rel] = {s: Rel() for s in stratum}
            for (hname, hargs, _), body in rules:
                pos = [i for i, a in enumerate(body) if a[0] in stratum and not a[2]]
                for i in pos:
                    ordered = [body[i], *body[:i], *body[i + 1:]]
                    ordered = sorted(ordered, key=lambda a: a[2] or a[0] == "!=")  # negation and != last
                    for env in _match(ordered, rels, {}, delta_at=len(ordered), delta=delta[body[i][0]]):
                        t = tuple(env[a] for a in hargs)
                        if t not in rels[hname]:
                            new[hname].add(t)
            for name, rows in new.items():
                rels[name] |= rows
            delta = new
    return sorted(t[0] for t in rels["out"])


# ------------------------------------------------------------------------------------------- shacl engine
SHACL_PREFIX = "@prefix sh: <http://www.w3.org/ns/shacl#> . @prefix e: <urn:eija:> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
SHACL = {
    "R1": SHACL_PREFIX
    + """e:S a sh:NodeShape ; sh:targetClass e:Requirement ;
  sh:property [ sh:path [ sh:inversePath e:verifies ] ; sh:minCount 1 ] .""",
    "R2": SHACL_PREFIX
    + """e:S a sh:NodeShape ; sh:targetClass e:Module ;
  sh:sparql [ sh:message "affected" ; sh:select \"\"\"SELECT $this WHERE {
    $this <urn:eija:dependsOn>+ ?y . ?y <urn:eija:changed> true .
    FILTER NOT EXISTS { $this <urn:eija:changed> true } }\"\"\" ] .""",
    "R3": SHACL_PREFIX
    + """e:S a sh:NodeShape ; sh:targetClass e:Requirement ;
  sh:sparql [ sh:message "uncovered" ; sh:select \"\"\"SELECT $this WHERE {
    FILTER NOT EXISTS { ?t <urn:eija:verifies> ?c . ?c <urn:eija:refines>* $this } }\"\"\" ] .""",
    "R4": SHACL_PREFIX
    + """e:S a sh:NodeShape ; sh:targetClass e:Term ;
  sh:sparql [ sh:message "homonym" ; sh:select \"\"\"SELECT $this WHERE {
    $this <urn:eija:formKey> ?k . ?o <urn:eija:formKey> ?k . FILTER(?o != $this) }\"\"\" ] .""",
}


def shacl_child(rule: str, n: int) -> None:
    """Run one SHACL rule in this process and print a JSON object (used with a subprocess timeout)."""
    from pyshacl import validate
    from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef

    e = Namespace("urn:eija:")
    f = make_facts(n)
    g = Graph()
    for (r,) in f["requirement"]:
        g.add((e[r], RDF.type, e.Requirement))
    for (m,) in f["module"]:
        g.add((e[m], RDF.type, e.Module))
    for (t,) in f["term"]:
        g.add((e[t], RDF.type, e.Term))
    for t, r in f["verifies"]:
        g.add((e[t], e.verifies, e[r]))
    for c, p in f["refines"]:
        g.add((e[c], e.refines, e[p]))
    for x, y in f["depends_on"]:
        g.add((e[x], e.dependsOn, e[y]))
    for (m,) in f["changed"]:
        g.add((e[m], e.changed, Literal(True, datatype=XSD.boolean)))
    for t, k in f["form_of"]:
        g.add((e[t], e.formKey, Literal(k)))
    shapes = Graph().parse(data=SHACL[rule], format="turtle")
    t0 = time.perf_counter()
    _, rg, _ = validate(g, shacl_graph=shapes, inference="none")
    ms = (time.perf_counter() - t0) * 1000
    sh = Namespace("http://www.w3.org/ns/shacl#")
    focus = sorted(str(o)[len("urn:eija:") :] for o in rg.objects(None, sh.focusNode) if isinstance(o, URIRef))
    print(json.dumps({"violations": focus, "validate_ms": round(ms, 1), "triples": len(g)}))


def shacl_run(rule: str, n: int) -> dict:
    try:
        import pyshacl  # noqa: F401
    except ImportError:
        return {"status": "NOT_RUN", "reason": "pyshacl not installed"}
    try:
        cp = subprocess.run(
            [sys.executable, __file__, "--shacl-child", rule, str(n)],
            capture_output=True, text=True, timeout=SHACL_TIMEOUT_S, check=False, encoding="utf-8",
        )
    except subprocess.TimeoutExpired:
        return {"status": "NOT_RUN", "reason": f"exceeded {SHACL_TIMEOUT_S} s budget"}
    if cp.returncode != 0:
        return {"status": "NOT_RUN", "reason": "child failed: " + cp.stderr.strip().splitlines()[-1][:200]}
    return {"status": "RAN", **json.loads(cp.stdout.strip().splitlines()[-1])}


# ------------------------------------------------------------------------------------------------ driver
def loc(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))


def source_lines() -> dict:
    py = {"R1": py_r1, "R2": py_r2, "R3": py_r3, "R4": py_r4}
    return {
        "python": {r: loc(inspect.getsource(fn)) for r, fn in py.items()},
        "sql": {r: loc(SQL[r]) for r in RULES},
        "datalog": {r: len(DATALOG[r]) for r in RULES},
        "shacl": {r: loc(SHACL[r].split("\n", 1)[1]) for r in RULES},
        "note": "non-blank, non-comment lines of the rule definition only (no data loading, no driver code)",
    }


def med(fn, reps: int = 3) -> float:
    xs = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        xs.append((time.perf_counter() - t) * 1000)
    return round(statistics.median(xs), 2)


def digest(rows: list[str]) -> str:
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()[:16]


def run(sizes: list[int], shacl_max: int) -> dict:
    agreement, timings = {}, {}
    for n in sizes:
        f = make_facts(n)
        db = sql_load(f)
        guard = n * 2 + 10
        out, tm = {}, {}
        for r, py in zip(RULES, (py_r1, py_r2, py_r3, py_r4), strict=False):
            res = {"python": py(f), "sql": sql_run(db, r, guard)}
            tm[r] = {"python": med(lambda py=py: py(f)), "sql": med(lambda r=r: sql_run(db, r, guard))}
            if n <= 100000:  # the toy evaluator is the slowest engine; above this size it would report NOT_RUN
                res["datalog"] = datalog_run(r, f)
                tm[r]["datalog"] = med(lambda r=r: datalog_run(r, f), reps=1)
            if n <= shacl_max:
                sh = shacl_run(r, n)
                if sh["status"] == "RAN":
                    res["shacl"] = sh["violations"]
                    tm[r]["shacl_validate"] = sh["validate_ms"]
                else:
                    tm[r]["shacl"] = sh
            out[r] = res
        agreement[str(n)] = {
            r: {
                "count": len(out[r]["python"]),
                "sha256_16": digest(out[r]["python"]),
                "engines_run": sorted(out[r]),
                "engines_identical": len({tuple(v) for v in out[r].values()}) == 1,
                "engines_not_run": sorted({"python", "sql", "datalog", "shacl"} - set(out[r])),
            }
            for r in RULES
        }
        timings[str(n)] = tm
    return {"agreement": agreement, "timings_ms": timings}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", nargs="+", type=int, default=[200, 1000, 2000, 10000, 100000])
    ap.add_argument("--shacl-max", type=int, default=2000)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--shacl-child", nargs=2, metavar=("RULE", "N"))
    a = ap.parse_args()
    if a.shacl_child:
        shacl_child(a.shacl_child[0], int(a.shacl_child[1]))
        return 0
    body = run(a.sizes, a.shacl_max)
    try:
        import pyshacl
        import rdflib
        shacl_env = {"pyshacl": pyshacl.__version__, "rdflib": rdflib.__version__}
    except ImportError:
        shacl_env = "not installed"
    result = {
        "schema": "eija.weave.bench.rule-language/v1",
        "label": "MEASUREMENT for timings (one machine); deterministic sections are byte-stable for a fixed seed",
        "seed": SEED,
        "rules": {
            "R1": "requirement without verifier (anti-join)",
            "R2": "transitive suspect (positive recursion)",
            "R3": "requirement not covered through refinement chain (recursion then negation)",
            "R4": "homonym in context (self-join and aggregate)",
        },
        "source_lines": source_lines(),
        "agreement": body["agreement"],
        "timings_ms": body["timings_ms"],
        "environment": {
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
            "platform": platform.platform(),
            "shacl": shacl_env,
            "shacl_budget_s": SHACL_TIMEOUT_S,
        },
    }
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text, encoding="utf-8", newline="\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
