# Gates defined in quality/sessions/graph.py

# Quality Gates

* [nox -s graph_formal_full](graph-formal-full.md) - ADR-0102: every formal test, the exhaustive enumerations (about 1 minute) and the Alloy certificate models (Glucose, about 25 s).
* [nox -s graph_formal_release](graph-formal-release.md) - ADR-0102 MEASUREMENTS and solver diversity: all formal benchmarks, then the Alloy certificate models on a second SAT backend (SAT4J, about 4 minutes).
* [nox -s graph_formal](graph-formal.md) - ADR-0102: stage-0 self-check of the trusted kernel references, then the fast formal tests (about 15 s).
* [nox -s graph_impact_math_bench](graph-impact-math-bench.md) - ADR-0097 MEASUREMENTS: cost of the reference implementations.
* [nox -s graph_impact_math](graph-impact-math.md) - ADR-0097: hand-verified oracles for impact, ranking, selection, status algebra and confidence statistics (about 10 s).
* [nox -s graph_metamodel_full](graph-metamodel-full.md) - ADR-0089: every metamodel and identity oracle, including byte identity of the bench report across PYTHONHASHSEED values.
* [nox -s graph_metamodel](graph-metamodel.md) - ADR-0089: the generated schemas match metamodel.json, the metamodel tables are coherent, and the fast identity checks hold.
* [nox -s graph_rules_bench](graph-rules-bench.md) - ADR-0095 rule-language benchmark: four engines, four rules, agreement and timings (MEASUREMENT, one machine).
* [nox -s graph_rules](graph-rules.md) - ADR-0095: validate graph/rules/catalogue.json (strata, relations, messages, metamodel agreement) and run its oracles.
