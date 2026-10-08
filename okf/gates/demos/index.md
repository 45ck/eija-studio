# Gates defined in quality/sessions/demos.py

# Quality Gates

* [nox -s demos_dry](demos-dry.md) - Every non-blocked scenario still works against the real Studio (no video).
* [nox -s demos_record](demos-record.md) - Maintainer-only: record the scenarios (slow, needs Chrome and a free display/CPU).
* [nox -s demos_registry](demos-registry.md) - Catalogue matches the code, REGISTRY.md is fresh, manifests are well formed.
* [nox -s demos_typecheck](demos-typecheck.md) - mypy over the demos package (the shared mypy config names only eija_studio).
