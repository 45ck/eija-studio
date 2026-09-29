"""Pure result model: classify raw cosmic-ray records and compute scores. No I/O, no cosmic-ray import."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

KILLED, SURVIVED, TIMEOUT, INCOMPETENT, EQUIVALENT, SKIPPED = "killed", "survived", "timeout", "incompetent", "equivalent", "skipped"
STATUSES = (KILLED, SURVIVED, TIMEOUT, INCOMPETENT, EQUIVALENT)  # SKIPPED mutants are dropped before reporting
_COLLECTION_FAILURE = ("error during collection", "errors during collection")  # pytest could not import the mutant


@dataclass(frozen=True)
class Mutant:
    """One mutation of one module and what the selected tests did about it."""

    module: str  # POSIX path relative to the repository root
    operator: str
    occurrence: int
    start: tuple[int, int]
    end: tuple[int, int]
    function: str | None
    status: str
    diff: str
    output: str
    equivalent_reason: str = ""  # set only when a survivor was reclassified as `equivalent` (see equivalents.py)

    @property
    def sort_key(self) -> tuple:
        return (self.module, self.start, self.end, self.operator, self.occurrence)


def classify(record: dict[str, Any]) -> str:
    """Map a cosmic-ray work result to one status.

    `timeout` means the tests hung on the mutant (an infinite loop is a detected fault). `incompetent` means
    the mutant could not be exercised at all (import/collection failure, worker crash): it says nothing about
    the tests and is excluded from the score. Anything not positively classified as killed is not detected.
    """
    result = record.get("result")
    if result is None:
        raise ValueError("work item has no result: cosmic-ray did not finish")
    if result["worker_outcome"] == "skipped":
        return SKIPPED
    if result["worker_outcome"] != "normal":
        return INCOMPETENT
    outcome, output = result["test_outcome"], result.get("output") or ""
    if outcome == "survived":
        return SURVIVED
    if outcome == "incompetent":
        return INCOMPETENT
    if outcome == "killed":
        if output.strip() == "timeout":
            return TIMEOUT
        return INCOMPETENT if any(marker in output for marker in _COLLECTION_FAILURE) else KILLED
    raise ValueError(f"unrecognised test outcome: {outcome!r}")


def score(counts: dict[str, int]) -> float | None:
    """Detected / (detected + survived), rounded down to 4 places; `None` when nothing was assessed.

    Incompetent and equivalent mutants are not assessed: the first could not be run, the second cannot differ.
    Rounding down means a stored threshold never exceeds the measured score. This is a mutation score over
    the curated operator set, not a measure of test quality in general.
    """
    detected = counts.get(KILLED, 0) + counts.get(TIMEOUT, 0)
    assessed = detected + counts.get(SURVIVED, 0)
    return None if assessed == 0 else int(detected / assessed * 10000) / 10000


def tally(mutants: list[Mutant]) -> dict[str, Any]:
    counts = {s: 0 for s in STATUSES}
    for m in mutants:
        counts[m.status] += 1
    return {"total": len(mutants), **counts, "score": score(counts)}
