# Symbols of domain.formal

# Classes

* [domain.formal.Assessment](Assessment.md) - `class Assessment` in `domain/formal`.
* [domain.formal.Context](Context.md) - What the kernel itself knows about the CURRENT subject, beyond the technical dimensions.
* [domain.formal.Findings](Findings.md) - Collects reasons by severity.
* [domain.formal.FormalArtifact](FormalArtifact.md) - One raw formal artifact from a tool report.
* [domain.formal.KindSpec](KindSpec.md) - One evidence kind: what it claims, how it is checked, what it does not establish.
* [domain.formal.Malformed](Malformed.md) - The artifact does not have the declared typed shape (a structural defect, judged FAIL).

# Constants

* [domain.formal.FORMAL_PRODUCER](FORMAL_PRODUCER.md) - Constant `FORMAL_PRODUCER` in `domain/formal`.
* [domain.formal.LEVEL_RECOMPUTED](LEVEL_RECOMPUTED.md) - Constant `LEVEL_RECOMPUTED` in `domain/formal`.
* [domain.formal.LEVEL_SEALED_TOOL](LEVEL_SEALED_TOOL.md) - Constant `LEVEL_SEALED_TOOL` in `domain/formal`.

# Functions

* [domain.formal.as_records](as_records.md) - Defensive view for display-only helpers: a list of dicts, or nothing.
* [domain.formal.carried_statements](carried_statements.md) - The artifact must carry its own assumptions and limitations (a proof without them is not shown as one).
* [domain.formal.digest](digest.md) - `def digest(container: Any, key: str, where: str) -> str` in `domain/formal`.
* [domain.formal.exact_keys](exact_keys.md) - `def exact_keys(artifact: dict[str, Any], keys: frozenset[str]) -> None` in `domain/formal`.
* [domain.formal.field](field.md) - ``container[key]`` if it is exactly of ``typ`` (``bool`` is not an ``int``); else the artifact is malformed.
* [domain.formal.has_items](has_items.md) - True if the list at ``key`` is not empty (its items may be of any type).
* [domain.formal.not_run_reason](not_run_reason.md) - A NOT_RUN artifact is exactly {protocol, not_run: {reason, prerequisite}}: honest absence, never PASS.
* [domain.formal.records](records.md) - `def records(container: Any, key: str, where: str) -> list[dict[str, Any]]` in `domain/formal`.
* [domain.formal.reported_labels](reported_labels.md) - The tool's own verdict and check labels may LOWER the status, never raise it.
* [domain.formal.source_binding](source_binding.md) - Producer sources named by the tool's report versus the bytes the adapter observes now.
* [domain.formal.strings](strings.md) - `def strings(container: Any, key: str, where: str, minimum: int=1) -> list[str]` in `domain/formal`.
* [domain.formal.text](text.md) - `def text(container: Any, key: str, where: str) -> str` in `domain/formal`.

# Methods

* [domain.formal.Findings.fail](Findings.fail.md) - `def fail(self, why: str) -> None` in `domain/formal`.
* [domain.formal.Findings.result](Findings.result.md) - `def result(self) -> Assessment` in `domain/formal`.
* [domain.formal.Findings.stale](Findings.stale.md) - `def stale(self, why: str) -> None` in `domain/formal`.
* [domain.formal.Findings.unknown](Findings.unknown.md) - `def unknown(self, why: str) -> None` in `domain/formal`.
