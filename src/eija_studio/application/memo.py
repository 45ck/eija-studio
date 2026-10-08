"""Ask the kernel the same question of the same frozen model once (ADR-0199).

Building an app's oracle or proving a pack's laws runs `runtime.execute` tens of thousands of times on one unchanged
model, and every run checked the whole model against the policy and hashed it again: over 95 % of the time at the
kernel's limits. A `Workflow` and a `Pack` are frozen after validation, so the same objects always get the same
answer. The answers are kept by the objects' identity, and the memo holds the objects themselves, so an id is never
reused for another object while its entry exists. A copy or an edit is a new object and is asked afresh. The domain's
own functions are unchanged; a refusal still comes from `ensure_policy` itself.
"""
from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from threading import Lock
from typing import Any, TypeVar

from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.pack import Pack

_T = TypeVar("_T")


class IdentityMemo:
    """A small, bounded memo for pure functions of frozen contracts, keyed by the identity of the arguments."""

    def __init__(self, size: int = 128):
        self._size, self._lock = size, Lock()
        self._entries: OrderedDict[tuple[int, ...], tuple[tuple[Any, ...], Any]] = OrderedDict()

    def get(self, args: tuple[Any, ...], compute: Callable[[], _T]) -> _T:
        key = tuple(map(id, args))
        with self._lock:
            hit = self._entries.get(key)
            if hit is not None and all(a is b for a, b in zip(hit[0], args, strict=True)):
                self._entries.move_to_end(key)
                kept: _T = hit[1]
                return kept
        value = compute()
        with self._lock:
            self._entries[key] = (args, value)
            self._entries.move_to_end(key)
            while len(self._entries) > self._size:
                self._entries.popitem(last=False)
        return value


_HASHES, _CONFORMS = IdentityMemo(), IdentityMemo()


def model_hash(model: Workflow) -> str:
    """`model.semantic_hash`, computed once per model object."""
    return _HASHES.get((model,), lambda: model.semantic_hash)


def ensure_conforms(model: Workflow, pack: Pack, ensure: Callable[[Workflow, Pack], None]) -> None:
    """`ensure(model, pack)` (the policy check): a pair it let through is remembered; any other is refused by it again,
    so the error is always the check's own. The check is part of the key, so a different check is asked afresh."""
    def passes() -> bool:
        try:
            ensure(model, pack)
        except DomainError:
            return False
        return True

    if not _CONFORMS.get((model, pack, ensure), passes):
        ensure(model, pack)
