"""Pure HCI-law formulas. No I/O, no browser, no clock.

Every model here is a *population-average predictive model from laboratory studies*. It ranks
design alternatives and flags outliers; it does NOT measure any real user's speed, and it is not a
usability study. Constants are configurable dataclass fields so a later lane can swap in locally
fitted values.

Sources (checked 2026-09-28):
  * MacKenzie, I. S. (1992). Movement time prediction in human-computer interfaces. Proc. Graphics
    Interface '92, 140-150 -- Shannon formulation ID = log2(D/W + 1).
  * MacKenzie, I. S. & Buxton, W. (1992). Extending Fitts' law to two-dimensional tasks. Proc. CHI
    '92, 219-226 -- "smaller-of" model (W = min(width, height)); mouse regression on a Macintosh II:
    MT = 230 + 166 * log2(A/W + 1) ms, r = .9501.
  * Hick, W. E. (1952) and Hyman, R. (1953): choice reaction time grows with log2(n + 1). Constant
    b ~ 150 ms/bit from Card, Moran & Newell (1983), The Psychology of Human-Computer Interaction.
  * Card, S. K., Moran, T. P. & Newell, A. (1980). The keystroke-level model for user performance
    time with interactive systems. CACM 23(7), 396-410: K 0.28 s (average non-secretary typist), P
    1.10 s, B 0.10 s (press or release), H 0.40 s, M 1.35 s.
  * Miller, G. A. (1956) "The magical number seven, plus or minus two"; Cowan, N. (2001) "The
    magical number 4 in short-term memory" (BBS 24:87-114).
  * Doherty, W. J. & Thadani, A. J. (1982), The economic value of rapid response time (IBM):
    interactions below ~400 ms keep the user and the computer both productive.

Stability contract: this module is reused by other pipelines (for example the UX research lane).
The public names in `__all__` and their docstrings (which state each model's validity limits) are
stable; add new functions rather than changing the meaning of existing ones.
"""
from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

__all__ = [
    "COWAN_LIMIT", "DEFAULT_FITTS", "DEFAULT_HICK", "DEFAULT_KLM", "DOHERTY_MS", "KLM_OPERATORS", "MAX_CHOICES",
    "MAX_ID_BITS", "MILLER_UPPER", "MIN_TARGET_PX", "FittsModel", "HickModel", "KlmTimes", "count_operators",
    "fitts_time", "hick_bits", "hick_time", "iqr", "klm_time", "nearest_edge_distance", "percentile", "shannon_id",
    "smaller_of",
]

MIN_TARGET_PX = 24.0  # WCAG 2.2 SC 2.5.8 Target Size (Minimum), CSS pixels
MAX_ID_BITS = 4.0  # brief: flag Fitts index of difficulty above 4 bits
MAX_CHOICES = 7  # brief: flag Hick choice points above 7 alternatives
DOHERTY_MS = 400.0
MILLER_UPPER = 9  # 7 + 2
COWAN_LIMIT = 4


@dataclass(frozen=True)
class FittsModel:
    """MT = a + b * ID, seconds. Defaults: MacKenzie & Buxton (1992) mouse, smaller-of, Shannon."""

    a: float = 0.230
    b: float = 0.166
    citation: str = "MacKenzie & Buxton 1992 (CHI '92), mouse, smaller-of model, MT = 230 + 166*ID ms"


@dataclass(frozen=True)
class HickModel:
    """T = b * log2(n + 1), seconds. b from Card, Moran & Newell (1983)."""

    b: float = 0.150
    citation: str = "Card, Moran & Newell 1983 (~150 ms/bit); Hick 1952; Hyman 1953"


@dataclass(frozen=True)
class KlmTimes:
    """Standard KLM operator times in seconds (Card, Moran & Newell 1980)."""

    K: float = 0.28
    P: float = 1.10
    B: float = 0.10
    H: float = 0.40
    M: float = 1.35


DEFAULT_FITTS = FittsModel()
DEFAULT_HICK = HickModel()
DEFAULT_KLM = KlmTimes()


def shannon_id(distance: float, width: float) -> float:
    """Fitts index of difficulty in bits, Shannon form: log2(D / W + 1).

    Establishes a difficulty *rank* for one pointing movement. It does not establish that the
    movement is slow for a given person, and W must already be the smaller-of box dimension.
    """
    if width <= 0:
        raise ValueError("target width must be positive")
    if distance < 0:
        raise ValueError("distance must be non-negative")
    return math.log2(distance / width + 1.0)


def smaller_of(width: float, height: float) -> float:
    """MacKenzie & Buxton (1992): effective 1-D width of a 2-D target is its smaller side."""
    return min(width, height)


def nearest_edge_distance(origin: tuple[float, float], box: tuple[float, float, float, float]) -> float:
    """Distance from `origin` to the closest point of `box` (x, y, w, h); 0 when the origin is inside.

    Sensitivity variant of Fitts's D: a person often stops at the near edge of a wide target, while the
    primary model lands at the centre. It bounds the centre-convention bias; it is not a better model."""
    x, y, w, h = box
    dx = max(x - origin[0], 0.0, origin[0] - (x + w))
    dy = max(y - origin[1], 0.0, origin[1] - (y + h))
    return math.hypot(dx, dy)


def fitts_time(index_of_difficulty: float, model: FittsModel = DEFAULT_FITTS) -> float:
    """Predicted movement time in seconds: a + b * ID."""
    return model.a + model.b * index_of_difficulty


def hick_bits(choices: int) -> float:
    """Decision information in bits for `choices` equally likely alternatives: log2(n + 1)."""
    if choices < 0:
        raise ValueError("choices must be non-negative")
    return math.log2(choices + 1)


def hick_time(choices: int, model: HickModel = DEFAULT_HICK) -> float:
    """Predicted choice time in seconds. Assumes equiprobable, unpractised choices: an upper bound
    for an expert who already knows the answer (Hyman: time follows uncertainty, not raw count)."""
    return model.b * hick_bits(choices)


# --- KLM ------------------------------------------------------------------------------------
KLM_OPERATORS = ("K", "P", "B", "H", "M")


def klm_time(operators: Iterable[str], times: KlmTimes = DEFAULT_KLM) -> float:
    """Sum of standard operator times. Unknown operator symbols raise, so nothing is silently free."""
    table = {"K": times.K, "P": times.P, "B": times.B, "H": times.H, "M": times.M}
    total = 0.0
    for op in operators:
        if op not in table:
            raise ValueError(f"unknown KLM operator {op!r}")
        total += table[op]
    return total


def count_operators(operators: Iterable[str]) -> dict[str, int]:
    """Operator histogram with every standard symbol present (zero counts included)."""
    counts = dict.fromkeys(KLM_OPERATORS, 0)
    for op in operators:
        if op not in counts:
            raise ValueError(f"unknown KLM operator {op!r}")
        counts[op] += 1
    return counts


# --- descriptive statistics -------------------------------------------------------------------
def _nearest_rank(ordered: Sequence[float], q: float) -> float:
    if not 0 <= q <= 100:
        raise ValueError("q must be within 0..100")
    rank = max(1, math.ceil(q / 100.0 * len(ordered)))
    return ordered[rank - 1]


def percentile(values: Sequence[float], q: float) -> float | None:
    """Nearest-rank percentile (q in 0..100). Deterministic, no interpolation, None if empty.

    With few samples p95 is effectively the maximum; the report states the sample count."""
    if not values:
        return None
    return _nearest_rank(sorted(values), q)


def iqr(values: Sequence[float]) -> tuple[float, float, float] | None:
    """(p25, median, p75) by nearest rank, or None if empty. Use this, not one run, to describe a noisy
    wall-clock measurement: the interquartile range shows the spread a single number hides."""
    if not values:
        return None
    ordered = sorted(values)
    return (_nearest_rank(ordered, 25), _nearest_rank(ordered, 50), _nearest_rank(ordered, 75))
