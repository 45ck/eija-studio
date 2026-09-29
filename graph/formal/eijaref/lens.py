"""Law checker for asymmetric lenses with a partial put, plus the paper's three counterexample lenses.

Definitions (Foster, Greenwald, Moore, Pierce, Schmitt, "Combinators for bidirectional tree
transformations", TOPLAS 2007, section 3): a lens has get: C -> A and put: A x C -> C.
GetPut  put(get c, c) = c.            PutGet  get(put(a, c)) = a.
PutPut  put(a', put(a, c)) = put(a', c)        (optional; with GetPut and PutGet: "very well behaved").
The paper states the laws "if both operations are defined"; EIJA's put can refuse (``translate`` returns
``Rejected``), so the checker below makes the definedness explicit. ``put`` returns ``REJECTED`` or a new source.

    GetPut   for every source c:                   put(get c, c) is Accepted(c)
    PutGet   for every (a, c) with put(a, c) = c': get(c') == a        (compared by eq_view: layout may be ignored)
    PutPut   for every (a, a', c) where put(a, c) = c1, put(a', c1) = c2 and put(a', c) = c3 are all
             accepted:                             c2 == c3

The suite is a MEASUREMENT on the supplied finite domain. It is validated by the paper's own examples,
which must trip exactly the laws the paper says they trip.
"""
from __future__ import annotations

from itertools import product
from typing import Any, Callable, Iterable

REJECTED = object()


def check_lens_laws(sources: Iterable[Any], views: Iterable[Any], get: Callable[[Any], Any],
                    put: Callable[[Any, Any], Any], eq_view: Callable[[Any, Any], bool] = lambda a, b: a == b,
                    limit: int = 3) -> dict[str, list]:
    srcs, vws = list(sources), list(views)
    bad: dict[str, list] = {"GetPut": [], "PutGet": [], "PutPut": []}
    for c in srcs:
        r = put(get(c), c)
        if r is REJECTED or r != c:
            bad["GetPut"].append((c, "rejected" if r is REJECTED else r))
    for a, c in product(vws, srcs):
        r = put(a, c)
        if r is not REJECTED and not eq_view(get(r), a):
            bad["PutGet"].append((a, c, r))
    for a, a2, c in product(vws, vws, srcs):
        c1 = put(a, c)
        if c1 is REJECTED:
            continue
        c2, c3 = put(a2, c1), put(a2, c)
        if c2 is not REJECTED and c3 is not REJECTED and c2 != c3:
            bad["PutPut"].append((a, a2, c, c2, c3))
    return {k: v[:limit] for k, v in bad.items()}


# Foster et al. section 3, the three counterexamples (source: the paper text, opened 2026-09-29).
def lens_putget_not_getput():
    """C = string x int, A = string. get (s, n) = s; put(s', (s, n)) = (s', 0): put has a side effect on n."""
    return (lambda c: c[0]), (lambda a, c: (a, 0))


def lens_getput_not_putget():
    """C = string, A = string x int. get s = (s, 0); put((s', n), s) = s': the int of the view is dropped."""
    return (lambda c: (c, 0)), (lambda a, c: a[0])


def lens_well_behaved_not_putput():
    """C = string x int (data, version), A = string. put overwrites the data and bumps the version if it changed."""
    return (lambda c: c[0]), (lambda a, c: c if a == c[0] else (a, c[1] + 1))


PAPER_CONTROLS = {
    # name: (constructor, domain, expected set of violated laws)
    "putget_not_getput": (lens_putget_not_getput, "pair_source_str_view", {"GetPut"}),
    "getput_not_putget": (lens_getput_not_putget, "str_source_pair_view", {"PutGet"}),
    "well_behaved_not_putput": (lens_well_behaved_not_putput, "pair_source_str_view", {"PutPut"}),
}

STRS = ("a", "b")
PAIRS = tuple(product(STRS, (0, 1, 2)))
DOMAINS = {"pair_source_str_view": (PAIRS, STRS), "str_source_pair_view": (STRS, PAIRS)}


def run_paper_controls() -> dict[str, dict]:
    out = {}
    for name, (ctor, dom, expected) in sorted(PAPER_CONTROLS.items()):
        get, put = ctor()
        srcs, views = DOMAINS[dom]
        bad = check_lens_laws(srcs, views, get, put)
        violated = {k for k, v in bad.items() if v}
        out[name] = {"violated": sorted(violated), "expected": sorted(expected), "agrees": violated == expected}
    return out
