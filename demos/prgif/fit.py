"""Pure logic that fits a recording into the PR-STANDARD media limits. No ffmpeg, no files: unit-testable.

Two independent decisions:

* **Timing.** A recording longer than the time limit is played faster (up to `max_speedup`), so the whole
  story still fits. Only when even that is not enough is the tail cut, and the caller is told so.
* **Size.** Candidate (fps, width) pairs are tried from the highest to the lowest quality until one encodes
  under the byte limit. After each measured attempt, candidates predicted to be too large are skipped, using
  the rough model `bytes ~ fps * width^2` anchored on the latest measurement. The model only orders and
  prunes attempts; every accepted result is a measured file size, never a prediction.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from itertools import product

MAX_WIDTH = 1280
MAX_SECONDS = 20.0
MAX_BYTES = 5_000_000  # decimal megabytes: conservative against any "5 MB" reading
MIN_WIDTH = 480
FPS_LADDER: tuple[int, ...] = (15, 12, 10, 8, 6)
WIDTH_STEP = 0.85
MAX_SPEEDUP = 2.0
PREDICTION_SLACK = 1.15  # the size model is rough: only skip a candidate that is clearly too large


@dataclass(frozen=True)
class Limits:
    max_width: int = MAX_WIDTH
    max_seconds: float = MAX_SECONDS
    max_bytes: int = MAX_BYTES
    min_width: int = MIN_WIDTH
    max_speedup: float = MAX_SPEEDUP


@dataclass(frozen=True)
class Timing:
    """How the source timeline maps to the GIF: `speed` > 1 plays faster; `cut` means the tail was dropped."""

    speed: float
    output_seconds: float
    cut: bool


@dataclass(frozen=True, order=True)
class Candidate:
    fps: int
    width: int

    @property
    def cost(self) -> float:
        return float(self.fps * self.width * self.width)


@dataclass
class FitResult:
    chosen: Candidate
    size: int
    attempts: list[tuple[Candidate, int]] = field(default_factory=list)


class DoesNotFitError(ValueError):
    """Even the smallest candidate was over the byte limit. Carries every measured attempt."""

    def __init__(self, attempts: list[tuple[Candidate, int]], max_bytes: int) -> None:
        tried = ", ".join(f"{c.fps}fps/{c.width}px={size}B" for c, size in attempts)
        super().__init__(f"no candidate fits {max_bytes} bytes (tried {tried}); shorten the recording")
        self.attempts = attempts


def plan_timing(duration_s: float, limits: Limits = Limits()) -> Timing:
    if duration_s <= 0:
        raise ValueError(f"recording has no duration ({duration_s})")
    if duration_s <= limits.max_seconds:
        return Timing(speed=1.0, output_seconds=duration_s, cut=False)
    speed = duration_s / limits.max_seconds
    if speed <= limits.max_speedup:
        return Timing(speed=speed, output_seconds=limits.max_seconds, cut=False)
    return Timing(speed=limits.max_speedup, output_seconds=limits.max_seconds, cut=True)


def _even(value: float) -> int:
    return max(2, int(value) // 2 * 2)


def widths(source_width: int, limits: Limits = Limits()) -> list[int]:
    """Descending widths from the source (never upscaled, at most `max_width`) down to `min_width`."""
    top = _even(min(source_width, limits.max_width))
    floor = min(top, _even(limits.min_width))
    found = [top]
    while (nxt := _even(found[-1] * WIDTH_STEP)) > floor:
        found.append(nxt)
    if found[-1] != floor:
        found.append(floor)
    return found


def candidates(source_width: int, limits: Limits = Limits(),
               fps_ladder: Sequence[int] = FPS_LADDER) -> list[Candidate]:
    """Every (fps, width) pair, most expensive (best quality) first; ties prefer the wider frame."""
    pairs = {Candidate(fps, width) for fps, width in product(fps_ladder, widths(source_width, limits))}
    return sorted(pairs, key=lambda c: (c.cost, c.width), reverse=True)


def predicted_size(anchor: tuple[Candidate, int], candidate: Candidate) -> float:
    measured, size = anchor
    return size * candidate.cost / measured.cost


def fit(encode: Callable[[Candidate], int], ladder: Sequence[Candidate], max_bytes: int) -> FitResult:
    """Encode candidates in order until one is at most `max_bytes`. The last candidate is always tried."""
    if not ladder:
        raise ValueError("no candidates to try")
    attempts: list[tuple[Candidate, int]] = []
    for index, candidate in enumerate(ladder):
        is_last = index == len(ladder) - 1
        if attempts and not is_last and predicted_size(attempts[-1], candidate) > max_bytes * PREDICTION_SLACK:
            continue
        size = encode(candidate)
        attempts.append((candidate, size))
        if size <= max_bytes:
            return FitResult(chosen=candidate, size=size, attempts=attempts)
    raise DoesNotFitError(attempts, max_bytes)
